#!/usr/bin/env python3
"""Check local bibliography, citation and claim-record integrity without network access.

This validates references and record structure, never factual truth, legal
clearance, API availability, or whether recorded execution actually happened.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata
from urllib.parse import urlsplit

MAX_FILE = 10 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024
MAX_ENTRIES = 10000
CITATION = re.compile(r'\bsrc_[A-Za-z0-9][A-Za-z0-9_]*\b')
SOURCES = Path('research/sources/sources.jsonl')
CLAIMS = Path('research/artifacts/claim_ledger.jsonl')


def _read(root: Path, path: Path) -> str:
    if not path.resolve().is_relative_to(root):
        raise ValueError(f'Outside-root reference input: {path.name}')
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError(f'Symlink reference input: {path.name}')
        if item == root:
            break
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError(f'Nonregular reference input: {path.name}')
        data = stream.read(MAX_FILE + 1)
    if len(data) > MAX_FILE:
        raise ValueError(f'Oversized reference input: {path.name}')
    return data.decode('utf-8')


def _unique(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def _records(root: Path, relative: Path) -> list[dict]:
    result = []
    for number, line in enumerate(_read(root, root / relative).splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line, object_pairs_hook=_unique)
        if not isinstance(record, dict):
            raise ValueError(f'{relative}:{number}: record must be an object')
        result.append(record)
    return result


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_references(directory: str | Path) -> list[str]:
    """Return structural diagnostics; an empty list is not a factual verdict."""
    errors: list[str] = []
    try:
        root = Path(directory).absolute()
        if root.is_symlink() or not root.is_dir():
            return ['Reference root must be a real directory']
        root = root.resolve()
        if not (root / SOURCES).exists():
            return [f'Missing source registry: {SOURCES}']
        sources: dict[str, dict] = {}
        for record in _records(root, SOURCES):
            identity = record.get('id')
            if not _text(identity):
                errors.append('Source record requires a nonblank id')
                continue
            if identity in sources:
                errors.append(f'Duplicate source id: {identity}')
            sources[identity] = record
            for field in ('url', 'org', 'type'):
                if not _text(record.get(field)):
                    errors.append(f'{identity}: source {field} must be nonblank text')
            if not isinstance(record.get('quality_rating'), str) or record['quality_rating'] not in {'A', 'B', 'C', 'D', 'E'}:
                errors.append(f'{identity}: source quality_rating must be A–E')
            if _text(record.get('url')) and not urlsplit(record['url']).scheme:
                errors.append(f'{identity}: source URL must identify a URI scheme')
        if not sources:
            errors.append('Source registry is empty')
        if (root / CLAIMS).exists():
            claims: set[str] = set()
            for record in _records(root, CLAIMS):
                identity = record.get('claim_id')
                if not _text(identity):
                    errors.append('Claim record requires a nonblank claim_id')
                    continue
                if identity in claims:
                    errors.append(f'Duplicate claim id: {identity}')
                claims.add(identity)
                if not _text(record.get('text')):
                    errors.append(f'{identity}: claim text must be nonblank')
                ids = record.get('source_ids')
                if not isinstance(ids, list) or not ids or any(not _text(item) for item in ids):
                    errors.append(f'{identity}: source_ids must be a nonempty text array')
                    continue
                missing = [item for item in ids if item not in sources]
                errors.extend(f'{identity}: unregistered source id {item}' for item in missing)
                if not missing and record.get('review_status') == 'manually_supported' and record.get('claim_type') != 'executable':
                    orgs = {unicodedata.normalize('NFKC', sources[item].get('org', '')).strip().casefold()
                            for item in ids if isinstance(sources[item].get('org'), str)}
                    orgs.discard('')
                    if len(orgs) < 2:
                        errors.append(f'{identity}: manually_supported record needs independent underlying author identities; case variants count once')
        entries = total = 0
        for current, dirs, names in os.walk(root, followlinks=False):
            here = Path(current)
            dirs[:] = sorted(d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.venv'})
            for name in dirs:
                if (here / name).is_symlink():
                    raise ValueError(f'Symlink reference directory: {name}')
            entries += len(dirs) + len(names)
            if entries > MAX_ENTRIES:
                raise ValueError('Reference inspection exceeds entry-count bound')
            for name in sorted(names):
                path = here / name
                if path.suffix.casefold() != '.md':
                    continue
                text = _read(root, path)
                total += len(text.encode('utf-8'))
                if total > MAX_TOTAL:
                    raise ValueError('Reference inspection exceeds size bound')
                for identity in sorted(set(CITATION.findall(text)) - sources.keys()):
                    errors.append(f'{path.relative_to(root)}: unregistered source citation {identity}')
    except (OSError, ValueError, UnicodeError) as exc:
        errors.append(str(exc))
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    errors = validate_references(args.root)
    if args.json:
        print(json.dumps({'valid': not errors, 'scope': 'reference_integrity_only',
                          'factual_verification': False, 'errors': errors}, indent=2))
    elif errors:
        for error in errors:
            print(f'Reference integrity: {error}', file=sys.stderr)
    else:
        print('Reference integrity checks passed; factual verification is outside this check.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
