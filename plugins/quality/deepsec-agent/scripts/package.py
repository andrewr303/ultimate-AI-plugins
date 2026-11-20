#!/usr/bin/env python3
"""Build a deterministic local plugin ZIP without dependency or state files."""
import argparse
import hashlib
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
destination = args.out.resolve()
if destination.is_relative_to(root):
    parser.error('--out must be outside the plugin directory')
destination.parent.mkdir(parents=True, exist_ok=True)
excluded = {'node_modules', '__pycache__', '.git', '.deepsec', '.deepsec-host.json'}
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for source in sorted(root.rglob('*')):
        relative = source.relative_to(root)
        if any(part in excluded or part.startswith('.env') for part in relative.parts):
            continue
        if relative.parts[:2] == ('examples', 'reports'):
            continue
        if source.is_symlink():
            raise SystemExit('Refusing a symlink in plugin package')
        if not source.is_file():
            continue
        info = zipfile.ZipInfo('deepsec-agent/' + relative.as_posix(), (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = (0o100644 << 16)
        archive.writestr(info, source.read_bytes())
print(str(destination))
print('sha256 ' + hashlib.sha256(destination.read_bytes()).hexdigest())
