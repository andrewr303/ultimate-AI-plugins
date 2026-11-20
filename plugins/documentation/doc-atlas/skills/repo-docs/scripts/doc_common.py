"""Bounded, read-only filesystem helpers. No networking or subprocesses."""
from __future__ import annotations
import os
from pathlib import Path

MAX_FILES = 5000
MAX_BYTES = 1_048_576
SKIP_DIRS = {'.git', '.hg', '.svn', 'node_modules', 'vendor', 'dist', 'build',
             'out', 'coverage', '.next', '.nuxt', '.astro', '.cache', '__pycache__',
             '.venv', 'venv', 'target', 'site-packages', '.tox'}
SECRET_NAMES = {'credentials', 'credentials.json', 'secrets', 'secrets.json',
                'secrets.yaml', 'secrets.yml', '.npmrc', '.pypirc', '.netrc',
                'id_rsa', 'id_ed25519', 'id_ecdsa', '.aws', '.ssh', '.gnupg', '.azure',
                '.secrets', 'secrets.toml', 'service-account.json'}
SECRET_SUFFIXES = {'.pem', '.key', '.p12', '.pfx', '.keystore'}

class InputFailure(Exception):
    pass


def secret_name(name: str) -> bool:
    lower = name.lower()
    return (lower.startswith('.env') or lower in SECRET_NAMES or
            Path(lower).suffix in SECRET_SUFFIXES)


def root_path(value: str) -> Path:
    p = Path(value).absolute()
    if p.is_symlink():
        raise InputFailure('repository root must not be a symlink')
    if not p.is_dir():
        raise InputFailure('repository root is not a readable directory')
    return p.resolve()


def contained(root: Path, path: Path) -> Path:
    """Reject all symlink components, sensitive names, and lexical/root escapes."""
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(root)
    except ValueError as exc:
        raise InputFailure('path escapes repository root') from exc
    cursor = root
    for part in relative.parts:
        if secret_name(part):
            raise InputFailure('sensitive path is excluded')
        if part.lower() in SKIP_DIRS:
            raise InputFailure('dependency, build, or metadata directory is excluded')
        cursor = cursor / part
        if cursor.is_symlink():
            raise InputFailure('symlink path is excluded')
    try:
        absolute.resolve().relative_to(root)
    except ValueError as exc:
        raise InputFailure('resolved path escapes repository root') from exc
    return absolute


def read_text(root: Path, path: Path, max_bytes: int = MAX_BYTES) -> str:
    path = contained(root, path)
    try:
        with path.open('rb') as stream:
            data = stream.read(max_bytes + 1)
    except OSError as exc:
        raise InputFailure('file could not be read') from exc
    if len(data) > max_bytes:
        raise InputFailure('file exceeds byte limit')
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise InputFailure('file is not UTF-8 text') from exc


def inventory(root: Path, max_files: int = MAX_FILES) -> tuple[list[Path], dict]:
    files: list[Path] = []
    stats = {'files_seen': 0, 'excluded_entries': 0, 'truncated': False,
             'read_failures': 0}
    stack = [root]
    while stack:
        folder = stack.pop()
        try:
            with os.scandir(folder) as scan:
                # Bound directory reads as well as the returned file inventory.
                entries = []
                for entry in scan:
                    stats['files_seen'] += 1
                    if stats['files_seen'] > max_files:
                        stats['truncated'] = True
                        return files, stats
                    entries.append(entry)
        except OSError:
            stats['read_failures'] += 1
            continue
        for entry in sorted(entries, key=lambda e: e.name):
            try:
                if entry.is_symlink() or secret_name(entry.name):
                    stats['excluded_entries'] += 1
                elif entry.is_dir(follow_symlinks=False):
                    if entry.name.lower() in SKIP_DIRS:
                        stats['excluded_entries'] += 1
                    else:
                        stack.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    files.append(Path(entry.path))
            except OSError:
                stats['read_failures'] += 1
    return sorted(files), stats
