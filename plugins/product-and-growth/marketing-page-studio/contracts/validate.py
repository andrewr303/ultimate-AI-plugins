#!/usr/bin/env python3
"""Validate versioned production contracts locally, with optional evidence/file checks.

Dependencies: Python 3.10+ and jsonschema>=4. No network or schema downloading.
CLI emits one JSON object and returns 0 on pass, 1 on invalid data, 2 on setup errors.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from typing import Any

ROOT = Path(__file__).resolve().parent
VERSION = '1.0.0'


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()
PATH_FIELDS = {'path', 'logoPath', 'brandPath', 'evidencePath', 'storyboardPath', 'captureManifestPath', 'narrationPath', 'captionsPath', 'soundtrackPath', 'jobPath', 'posterPath', 'outputPath', 'renderPath', 'template', 'outputDir', 'evidence', 'font', 'project', 'entry'}
PATH_ARRAYS = {'resourcePaths', 'evidence'}


def safe_relative(value: str) -> bool:
    """Paths are normalized forward-slash project paths, never URL/drive/traversal."""
    return bool(value and not value.startswith(('/', '\\')) and '\\' not in value and ':' not in value and '\x00' not in value and '..' not in PurePosixPath(value).parts)


def _walk(value: Any, path: str = '$'):
    if isinstance(value, dict):
        for key, item in value.items():
            yield path + '.' + key, key, item
            yield from _walk(item, path + '.' + key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from _walk(item, f'{path}[{i}]')


def validate(schema_name: str, data: Any, *, project_root: Path | None = None,
             evidence: dict | None = None, use: str = 'internal',
             check_files: bool = False, captures: dict | None = None) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    def error(path, message, code='semantic'):
        errors.append({'path': path, 'code': code, 'message': message})
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return {'ok': False, 'schema': schema_name, 'errors': [{'path':'$', 'code':'dependency', 'message':'Install jsonschema>=4: python -m pip install jsonschema'}], 'warnings':[]}
    schema_path = ROOT / 'schemas' / (schema_name + '.schema.json')
    if not re.fullmatch('[a-z][a-z0-9-]*', schema_name) or not schema_path.is_file():
        return {'ok': False, 'schema': schema_name, 'errors': [{'path':'$', 'code':'schema', 'message':'Unknown bundled schema name'}], 'warnings':[]}
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    for e in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data), key=lambda x: '/'.join(map(str,x.absolute_path))):
        path = '$' + ''.join(f'[{x}]' if isinstance(x,int) else '.'+str(x) for x in e.absolute_path)
        error(path, e.message, 'schema')
    if errors:
        return {'ok':False, 'schema':schema_name, 'id':data.get('id') if isinstance(data,dict) else None, 'errors':errors, 'warnings':warnings}
    # Defend portable paths in every contract, including nested provenance records.
    for path,key,value in _walk(data):
        paths = []
        if key in PATH_FIELDS and isinstance(value,str): paths = [(path,value)]
        if key in PATH_ARRAYS and isinstance(value,list): paths += [(f'{path}[{i}]',v) for i,v in enumerate(value) if isinstance(v,str)]
        if key == 'sourceHashes' and isinstance(value,dict): paths += [(path+'.'+p,p) for p in value]
        if key == 'assets' and isinstance(value,list) and schema_name == 'render-job':
            paths += [(f'{path}[{i}]',v) for i,v in enumerate(value) if isinstance(v,str)]
        for pp,p in paths:
            if not safe_relative(p):error(pp,'Use a relative forward-slash path inside the production project, without parent traversal.', 'path')
        if key in ('url','baseUrl') and isinstance(value,str):
            parsed = urlsplit(value)
            if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
                error(path,'Evidence and capture URLs must be HTTP(S), with a hostname and without embedded credentials.','url')
        if key == 'source' and isinstance(value,dict) and 'type' in value:
            if not value.get('path') and not value.get('url'):error(path,'Provenance needs a path or URL.')
            if value.get('type') == 'repository' and not value.get('revision'):error(path,'Repository provenance requires a product revision.')
    # Stable IDs are unique within each record collection.
    for path,key,value in _walk(data):
        if isinstance(value,list) and value and all(isinstance(x,dict) and 'id' in x for x in value):
            seen=set()
            for i,item in enumerate(value):
                if item['id'] in seen:error(f'{path}[{i}].id','Duplicate stable ID: '+item['id'],'duplicate-id')
                seen.add(item['id'])
    if project_root and evidence is None and schema_name in ('campaign-brief','storyboard','render-job','export-variants'):
        rel = data.get('evidencePath', data.get('evidence','product-evidence.json'))
        if safe_relative(rel):
            ep = (project_root.resolve()/rel).resolve()
            if ep.is_relative_to(project_root.resolve()) and ep.is_file():
                try:
                    candidate = json.loads(ep.read_text(encoding='utf-8'))
                    result = validate('product-evidence',candidate,project_root=project_root,check_files=check_files)
                    if result['ok']:
                        evidence = candidate
                    else:
                        error('$.evidencePath','Product evidence is invalid: '+json.dumps(result['errors']),'evidence')
                except (OSError,ValueError) as exc:
                    error('$.evidencePath','Cannot read product evidence: '+str(exc),'evidence')
            else:
                error('$.evidencePath','Missing product-evidence.json or declared evidencePath in the project root.','evidence')
    if schema_name == 'product-evidence':
        for i,c in enumerate(data['claims']):
            if c['status'] == 'verified' and not c['sources']:error(f'$.claims[{i}].sources','Verified claims need supporting evidence.','evidence')
            for s in c['sources']:
                if check_files and project_root and s.get('path') and safe_relative(s['path']):
                    source_path=(project_root.resolve()/s['path']).resolve()
                    if not source_path.is_relative_to(project_root.resolve()):
                        error(f'$.claims[{i}].sources','Local evidence source escapes the project through a symlink: '+s['path'],'path')
                    elif not source_path.is_file():
                        error(f'$.claims[{i}].sources','Missing local evidence source: '+s['path'],'file')
                if not s.get('path') and not s.get('url'):
                    error(f'$.claims[{i}].sources','Each evidence source requires a path or URL.','evidence')
            if c['status'] == 'verified':
                for s in c['sources']:
                    if s.get('type') in ('repository','capture') and s.get('revision') != data['product']['revision']:
                        error(f'$.claims[{i}].sources','Verified product source must name the current product revision.','evidence')
            if c['status'] == 'unsupported' and set(c['allowedUses']) - {'internal'}:error(f'$.claims[{i}].allowedUses','Unsupported claims may appear only in internal planning.','evidence')
    if schema_name == 'capture-manifest' and project_root:
        rights_path=(project_root.resolve()/'asset-manifest.json').resolve()
        if not rights_path.is_relative_to(project_root.resolve()):
            error('$.assets','Rights manifest path escapes the project through a symlink.','path')
        elif rights_path.is_file():
            try:
                rights=json.loads(rights_path.read_text(encoding='utf-8'))
                rights_report=validate('asset-manifest',rights)
                if not rights_report['ok']:
                    error('$.assets','Asset rights manifest is invalid: '+json.dumps(rights_report['errors']),'rights')
                else:
                    by_id={a['id']:a for a in rights['assets']}
                    if rights['productRevision'] != data['productRevision']:error('$.productRevision','Capture and rights manifest revisions differ.','rights')
                    for i,a in enumerate(data['assets']):
                        record=by_id.get(a['id'])
                        if a['rightsId'] != rights['id']:error(f'$.assets[{i}].rightsId','rightsId must identify the owning asset-manifest document.','rights')
                        if record is None:error(f'$.assets[{i}]','No rights record with the same captured asset id.','rights')
                        elif record['path'] != a['path'] or record['sha256'] != a['sha256']:error(f'$.assets[{i}]','Rights record path/hash does not match the captured asset.','rights')
            except (OSError,ValueError) as exc:
                error('$.assets','Cannot read asset rights manifest: '+str(exc),'rights')
        elif check_files:
            error('$.assets','Missing asset-manifest.json for captured asset rights.','rights')
    if schema_name == 'capture-job':
        requirements={'goto':'value','click':'selector','fill':'selector','select':'selector','press':'value','wait-for':'selector','screenshot':'path'}
        recording=False
        for i,s in enumerate(data['steps']):
            required=requirements.get(s['action'])
            if 'holdMs' in s and s['action'] != 'wait-for':error(f'$.steps[{i}].holdMs','A settled reading hold is permitted only after a wait-for action.')
            if required and not s.get(required):error(f'$.steps[{i}]',f"Action {s['action']} requires {required}.")
            if s['action'] in ('fill','select') and 'value' not in s:error(f'$.steps[{i}]','Fill/select requires a value.')
            if s['action']=='start-recording':
                if recording:error(f'$.steps[{i}]','Recording is already active.')
                recording=True
            if s['action']=='stop-recording':
                if not recording:error(f'$.steps[{i}]','Stop recording has no matching start.')
                recording=False
        if recording:error('$.steps','Recording must be stopped explicitly.')
        if data['mode']=='illustrative' and not data['syntheticData']:warnings.append({'path':'$.syntheticData','message':'Confirm illustrative data is safe and clearly labeled.'})
    if schema_name == 'interactive-demo':
        ids={s['id'] for s in data['states']}
        if data['initialState'] not in ids:error('$.initialState','Initial state is not declared.')
        graph={s:set() for s in ids}
        for i,t in enumerate(data['transitions']):
            if t['from'] not in ids or t['to'] not in ids:error(f'$.transitions[{i}]','Transition references an undeclared state.')
            else:graph[t['from']].add(t['to'])
        reached={data['initialState']};queue=list(reached)
        while queue:
            n=queue.pop()
            for nxt in graph.get(n,()):
                if nxt not in reached:reached.add(nxt);queue.append(nxt)
        for state in ids-reached:error('$.states','Unreachable state: '+state)
        if data['mode'] in ('replay','illustrative') and not any(x in data['label'].lower() for x in ('sample','replay','illustrat','simulat','demo')):error('$.label','Label a simulated/replayed surface so visitors understand its mode.')
    if captures:
        capture_report = validate('capture-manifest',captures)
        if not capture_report['ok']:
            error('$.captures','Supplied capture manifest is invalid: '+json.dumps(capture_report['errors']),'evidence')
            captures = None
    if schema_name == 'storyboard':
        previous_end=0
        safe=data['safeZone']
        if safe['width']<=0 or safe['height']<=0 or safe['x']+safe['width']>data['width'] or safe['y']+safe['height']>data['height']:error('$.safeZone','Safe zone must fit inside the composition.')
        asset_ids={a['id'] for a in captures['assets']} if captures else None
        for i,shot in enumerate(data['shots']):
            if shot['startFrame'] != previous_end:error(f'$.shots[{i}].startFrame','Shots must be contiguous and ordered; use explicit transition shots for holds.')
            previous_end=shot['startFrame']+shot['durationFrames']
            if shot['readingHoldFrames']>shot['durationFrames']:error(f'$.shots[{i}].readingHoldFrames','Reading hold exceeds the shot duration.')
            bounds=shot.get('captionBounds')
            if bounds and not (bounds['x']>=safe['x'] and bounds['y']>=safe['y'] and bounds['x']+bounds['width']<=safe['x']+safe['width'] and bounds['y']+bounds['height']<=safe['y']+safe['height']):error(f'$.shots[{i}].captionBounds','Caption bounds must fit inside the safe zone.')
            if asset_ids is not None:
                for aid in shot['assetIds']:
                    if aid not in asset_ids:error(f'$.shots[{i}].assetIds','Unknown capture asset: '+aid)
            if 'cursor' in shot:
                for xkey,ykey in [('x','y'),('targetX','targetY')]:
                    if shot['cursor'][xkey]>=data['width'] or shot['cursor'][ykey]>=data['height']:error(f'$.shots[{i}].cursor','Cursor point lies outside the composition.')
    if schema_name == 'render-job':
        if 'configHash' in data:
            payload = {k:v for k,v in data.items() if k != 'configHash'}
            canonical = json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
            if hashlib.sha256(canonical).hexdigest() != data['configHash']:
                error('$.configHash','Config SHA-256 mismatch. Hash canonical JSON with configHash omitted.','hash')
        if data['width']%2 or data['height']%2:error('$.width','Encoded yuv420 dimensions must be even.')
        safe = data.get('safeZone')
        if safe and (safe['width']<=0 or safe['height']<=0 or safe['x']+safe['width']>data['width'] or safe['y']+safe['height']>data['height']):
            error('$.safeZone','Safe zone must have positive area and fit inside the composition.')
        for i,c in enumerate(data['captions']):
            if c['start']>=c['end'] or c['end']>data['duration']:error(f'$.captions[{i}]','Caption start must precede end and stay inside the render duration.')
        for i,a in enumerate(data['audio']):
            if a.get('start',0)>=data['duration']:error(f'$.audio[{i}].start','Audio starts after the render ends.')
            if a.get('duration') and a['start']+a['duration']>data['duration']:error(f'$.audio[{i}]','Audio extends beyond the render duration.')
        if data['renderer']=='footage' and not data.get('source'):error('$.source','Footage adapter requires a source video.')
    if schema_name in ('export-variants','experiment-manifest'):
        entries=data.get('variants',data.get('experiments',[]))
        pairs=set()
        hook_ids={h['id'] for h in data.get('hooks',[])}
        body_ids={b['id'] for b in data.get('bodies',[])}
        if schema_name=='experiment-manifest':
            for field in ('text','angle','hypothesis'):
                vals=[h[field].strip().casefold() for h in data['hooks']]
                if len(set(vals))!=len(vals):error('$.hooks','Hooks must have distinct '+field+'; cosmetic duplicates are not separate hypotheses.')
        for i,v in enumerate(entries):
            prefix='$.variants' if schema_name=='export-variants' else '$.experiments'
            a,b=map(int,v['aspectRatio'].split(':'))
            if 'width' in v and v['width']*b != v['height']*a:error(f'{prefix}[{i}].aspectRatio','Composition dimensions do not match the declared aspect ratio.')
            pair=(v['hookId'],v['bodyId'],v['aspectRatio'])
            if pair in pairs:error(f'{prefix}[{i}]','Duplicate hook/body/aspect combination.')
            pairs.add(pair)
            if hook_ids and v['hookId'] not in hook_ids:error(f'{prefix}[{i}].hookId','Unknown hook.')
            if body_ids and v['bodyId'] not in body_ids:error(f'{prefix}[{i}].bodyId','Unknown body.')
    if schema_name=='asset-manifest':
        for i,a in enumerate(data['assets']):
            if a['permission']=='unknown' and a['redistributable']:error(f'$.assets[{i}]','Unknown rights cannot be marked redistributable.','rights')
    if schema_name=='qa-results':
        for i,c in enumerate(data['checks']):
            if c['status']=='pass' and not c['evidence']:error(f'$.checks[{i}].evidence','A pass needs an evidence artifact; use untested for unexecuted checks.','evidence')
    # Contextual claim check: publish only supported, permitted claims.
    if evidence:
        evidence_report = validate('product-evidence',evidence,project_root=project_root,check_files=check_files)
        if not evidence_report['ok']:
            error('$.evidencePath','Supplied product evidence is invalid: '+json.dumps(evidence_report['errors']),'evidence')
            evidence = None
    if evidence:
        expected_revision = data.get('productRevision')
        if expected_revision and evidence.get('product',{}).get('revision') != expected_revision:
            error('$.productRevision','Product revision differs from the evidence revision.','evidence')
        available={c['id']:c for c in evidence.get('claims',[])}
        claims=[]
        for p,k,v in _walk(data):
            if k in ('claims','claimIds') and isinstance(v,list):claims.extend((p,c) for c in v if isinstance(c,str))
        for p,cid in claims:
            c=available.get(cid)
            if c is None:error(p,'Unknown claim ID: '+cid,'evidence')
            elif use != 'internal' and use not in c.get('allowedUses',[]):error(p,'Claim not authorized for '+use+': '+cid,'evidence')
            elif c['status']=='unsupported' and use!='internal':error(p,'Unsupported claim cannot be published: '+cid,'evidence')
    # Optional filesystem verification binds current local inputs to their recorded hashes.
    if project_root:
        project_root=project_root.resolve()
        def resolve_local(p):
            if not safe_relative(p):return None
            q=(project_root/p).resolve()
            if not q.is_relative_to(project_root):error('$','Path escapes the project through a symlink: '+p,'path');return None
            return q
        for p,key,value in _walk(data):
            if key=='sourceHashes':
                for rel,expected in value.items():
                    q=resolve_local(rel)
                    if q is None:continue
                    if not q.is_file():error(p,'Missing source file: '+rel,'file')
                    elif file_sha256(q)!=expected:error(p,'Source SHA-256 mismatch: '+rel,'hash')
        if check_files:
            assets=data.get('assets',[]) if schema_name in ('capture-manifest','asset-manifest') else []
            for a in assets:
                q=resolve_local(a['path'])
                if q is None:continue
                if not q.is_file():error('$.assets','Missing asset: '+a['path'],'file')
                elif file_sha256(q)!=a['sha256']:error('$.assets','Asset SHA-256 mismatch: '+a['path'],'hash')
            for p,key,value in _walk(data):
                if key in {'brandPath','evidencePath','storyboardPath','captureManifestPath','narrationPath','soundtrackPath','template','evidence','font'} and isinstance(value,str):
                    q=resolve_local(value)
                    if q is not None and not q.is_file():error(p,'Missing referenced input: '+value,'file')
            if schema_name == 'render-job':
                inputs=[a['path'] for a in data['audio']]
                if data.get('source'):inputs.append(data['source']['path'])
                for rel in inputs:
                    q=resolve_local(rel)
                    if q is not None and not q.is_file():error('$','Missing renderer input: '+rel,'file')
    elif check_files:error('$','--check-files requires --root.','usage')
    return {'ok':not errors,'schema':schema_name,'id':data.get('id'),'errors':errors,'warnings':warnings}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema',required=True,help='Bundled schema name, e.g. campaign-brief')
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--root',type=Path,help='Production project root for hash and optional input file checks')
    parser.add_argument('--check-files',action='store_true')
    parser.add_argument('--evidence',type=Path)
    parser.add_argument('--captures',type=Path)
    parser.add_argument('--use',choices=['internal','website','video','ads'],default='internal')
    args=parser.parse_args(argv)
    try:
        data=json.loads(args.input.read_text(encoding='utf-8'))
        evidence=json.loads(args.evidence.read_text(encoding='utf-8')) if args.evidence else None
        captures=json.loads(args.captures.read_text(encoding='utf-8')) if args.captures else None
        report=validate(args.schema,data,project_root=args.root,evidence=evidence,use=args.use,check_files=args.check_files,captures=captures)
    except (OSError,ValueError) as exc:
        print(json.dumps({'ok':False,'errors':[{'path':'$','code':'input','message':str(exc)}],'warnings':[]}));return 2
    print(json.dumps(report,indent=2))
    return 0 if report['ok'] else 1

if __name__=='__main__':
    raise SystemExit(main())
