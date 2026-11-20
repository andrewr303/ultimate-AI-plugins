#!/usr/bin/env python3
"""Materialize a canonical experiment manifest into independent render-job projects. No invented hooks."""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath

from render import resolve

RATIOS = {'9:16': (1080, 1920), '16:9': (1920, 1080), '1:1': (1080, 1080), '4:5': (1080, 1350)}


def output_path(value, base):
    """Check the lexical path before resolving it, including existing ancestors."""
    raw = Path(value)
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    if any(path.is_symlink() for path in (raw, *raw.parents)):
        raise ValueError('Variant output and its ancestors must not be symlinks')
    out = Path(os.path.abspath(raw))
    if out == Path(base).resolve():
        raise ValueError('Variant output must differ from the source project')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError('Variant output must be absent or an empty directory; existing files are never overwritten')
    return out


def check_collisions(paths):
    """Keep output portable on case-insensitive filesystems as well."""
    seen = {}
    for path, kind in paths:
        key = PurePosixPath(path).as_posix().casefold()
        if key in seen:
            raise ValueError(f'Variant output filename collision: {path} ({kind}; already {seen[key]})')
        seen[key] = kind
    for path in seen:
        if any(parent.as_posix().casefold() in seen for parent in PurePosixPath(path).parents if parent.as_posix() != '.'):
            raise ValueError(f'Variant output file/directory collision: {path}')


def materialize(job, base, manifest, out, limit=None, use="ads"):
    base = Path(base).resolve()
    out = output_path(out, base)
    if limit is not None and limit < 1:
        raise ValueError('limit must be positive')
    validator = Path(__file__).resolve().parents[1] / 'contracts' / 'validate.py'
    if not validator.is_file():
        raise ValueError('Bundled contracts validator missing; reinstall the plugin')
    spec = importlib.util.spec_from_file_location('variant_contracts', validator)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for schema, data in [('render-job', job), ('experiment-manifest', manifest)]:
        report = mod.validate(schema, data)
        if not report['ok']:
            raise ValueError('Invalid ' + schema + ': ' + json.dumps(report['errors']))
    ids = [x['id'] for x in manifest['experiments']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate experiment IDs')
    if any(not re.fullmatch('[a-z][a-z0-9._-]*', x) for x in ids):
        raise ValueError('Experiment IDs must be safe portable identifiers')
    hooks = {x['id']: x for x in manifest['hooks']}
    bodies = {x['id']: x for x in manifest['bodies']}
    if manifest['productRevision'] != job['productRevision']:
        raise ValueError('Experiment and render job revisions differ')
    for experiment in manifest['experiments']:
        if experiment['hookId'] not in hooks or experiment['bodyId'] not in bodies:
            raise ValueError('Unknown hook or body ID')
    evidence = json.loads(resolve(base, job['evidence']).read_text()) if job.get('evidence') else None
    prepared = []
    for experiment in manifest['experiments'][:limit]:
        if experiment['aspectRatio'] not in RATIOS:
            raise ValueError('Unsupported authored aspect ratio: ' + experiment['aspectRatio'])
        variant = copy.deepcopy(job)
        body = bodies[experiment['bodyId']]
        variant.update(
            id=experiment['id'], hook=hooks[experiment['hookId']]['text'], promise=body['proof'],
            body='before-after' if 'before' in body['approach'].lower() or 'before' in experiment['bodyId'] else
                 ('review' if any(word in body['approach'].lower() for word in ['review', 'edit', 'human']) else 'context'),
            placement=experiment['placement'], width=RATIOS[experiment['aspectRatio']][0],
            height=RATIOS[experiment['aspectRatio']][1], duration=experiment['duration'],
            cta=experiment['cta'], claimIds=body['claims'], campaignId=manifest['campaignId'])
        factor = variant['duration'] / job['duration']
        if factor != 1:
            if job.get('audio') or job.get('source', {}).get('audioPolicy') == 'preserve':
                raise ValueError('Cannot automatically change duration with audio: author a separate job with aligned audio, captions and review points')
            for caption in variant.get('captions', []):
                caption['start'] = round(caption['start'] * factor, 4)
                caption['end'] = round(caption['end'] * factor, 4)
            for point in variant.get('reviewPoints', []):
                point['time'] = round(point['time'] * factor, 4)
        if 'configHash' in variant:
            payload = {k: v for k, v in variant.items() if k != 'configHash'}
            variant['configHash'] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
        report = mod.validate('render-job', variant, project_root=base, evidence=evidence, use=use, check_files=True)
        if not report['ok']:
            raise ValueError('Variant contract invalid: ' + json.dumps(report['errors']))
        prepared.append(variant)

    # Resolve every source and filename before creating any destination artifacts.
    references = set()
    for variant in prepared:
        references.update(filter(None, [variant.get('evidence'), variant.get('template'), variant.get('font'),
                                       variant.get('source', {}).get('path')]))
        references.update(audio['path'] for audio in variant.get('audio', []))
        references.update(variant.get('sourceHashes', {}))
    if evidence is None:
        evidence = json.loads(resolve(base, 'product-evidence.json').read_text())
        references.add('product-evidence.json')
    if evidence:
        references.update(source['path'] for claim in evidence['claims'] for source in claim['sources'] if source.get('path'))
    if (base / 'asset-manifest.json').is_file():
        rights_path = resolve(base, 'asset-manifest.json')
        rights = json.loads(rights_path.read_text())
        references.add('asset-manifest.json')
        references.update(asset['path'] for asset in rights['assets'])
        references.update(asset['source']['path'] for asset in rights['assets'] if asset.get('source', {}).get('path'))
    sources = [(PurePosixPath(rel).as_posix(), resolve(base, rel)) for rel in sorted(references)]
    generated = [(variant['id'] + '.json', 'render job') for variant in prepared]
    generated += [('experiment-manifest.json', 'experiment manifest'), ('render-jobs.json', 'render index')]
    check_collisions([(rel, 'source asset') for rel, _ in sources] + generated)
    rows = [{'id': variant['id'], 'job': variant['id'] + '.json', 'status': 'planned'} for variant in prepared]
    result = copy.deepcopy(manifest)
    for experiment in result['experiments']:
        experiment['status'] = 'planned'

    out.parent.mkdir(parents=True, exist_ok=True)
    output_path(out, base)
    with tempfile.TemporaryDirectory(prefix='.pds-variants-', dir=out.parent) as temp:
        stage = Path(temp) / 'project'
        stage.mkdir()
        for rel, source in sources:
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        for variant in prepared:
            (stage / (variant['id'] + '.json')).write_text(json.dumps(variant, indent=2) + '\n', encoding='utf-8')
        (stage / 'experiment-manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        (stage / 'render-jobs.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
        for variant in prepared:
            report = mod.validate('render-job', variant, project_root=stage, evidence=evidence, use=use, check_files=True)
            if not report['ok']:
                raise ValueError('Staged variant contract invalid: ' + json.dumps(report['errors']))
        # Recheck after staging: a newly populated output must also be preserved.
        output_path(out, base)
        existed = out.exists()
        mode = out.stat().st_mode & 0o777 if existed else None
        try:
            if existed:
                out.rmdir()  # Refuses to remove a concurrently populated directory.
            stage.rename(out)
        except OSError:
            if existed and not out.exists():
                out.mkdir(mode=mode)
            raise
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--use', choices=['video', 'ads'], default='ads')
    args = parser.parse_args()
    try:
        job_path = Path(args.job).resolve()
        rows = materialize(json.loads(job_path.read_text()), job_path.parent,
                           json.loads(Path(args.manifest).read_text()), args.output, args.limit, args.use)
        print(json.dumps({'jobs': len(rows), 'output': args.output}))
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}), file=sys.stderr)
        sys.exit(2)
