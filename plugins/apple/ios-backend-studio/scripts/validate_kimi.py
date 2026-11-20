#!/usr/bin/env python3
"""Statically check this skills-only package against Kimi Code 2.x discovery.

Python 3.10+; standard library only. Does not install a plugin, edit host settings,
load a provider, or execute model/project code.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import unquote, urlsplit

MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
MAX_FILES = 10000
PLUGIN_NAME = re.compile(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*(?:@[A-Za-z0-9_-]+)?\Z')
NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SEMVER = re.compile(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z')
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^)\s]+)(?:\s+["\'][^\n]*["\'])?\s*\)')


class CompatibilityError(ValueError):
    """An input does not satisfy this package's Kimi contract."""


def _no_symlink_components(path: Path) -> None:
    for component in (path, *path.parents):
        if component.is_symlink():
            raise CompatibilityError(f'Symlink path is not supported: {component}')


def _read_regular(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise CompatibilityError(f'Nonregular input is not supported: {path}')
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise CompatibilityError(f'Input exceeds file-size bound: {path}')
    return data


def _inventory(root: Path) -> dict[Path, bytes]:
    """Snapshot ordinary files without following directory or file links."""
    _no_symlink_components(root)
    if not root.is_dir():
        raise CompatibilityError(f'Expected a directory: {root}')
    result: dict[Path, bytes] = {}
    folded: set[str] = set()
    total = 0
    entries = 0
    def walk_error(error: OSError) -> None:
        raise CompatibilityError(f'Cannot inspect source directory: {error.filename}') from error
    for current, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        here = Path(current)
        dirs.sort()
        entries += len(dirs) + len(names)
        if entries > MAX_FILES:
            raise CompatibilityError('Package exceeds inspection entry-count bound')
        for name in dirs:
            item = here / name
            if not stat.S_ISDIR(item.lstat().st_mode):
                raise CompatibilityError(f'Symlink or non-directory input: {item}')
        for name in sorted(names):
            item = here / name
            if not stat.S_ISREG(item.lstat().st_mode):
                raise CompatibilityError(f'Symlink or nonregular input: {item}')
            relative = item.relative_to(root)
            normalized = str(relative).casefold()
            if normalized in folded:
                raise CompatibilityError(f'Case-colliding input path: {relative}')
            folded.add(normalized)
            data = _read_regular(item)
            total += len(data)
            if total > MAX_TOTAL_BYTES or len(result) >= MAX_FILES:
                raise CompatibilityError('Package exceeds inspection size or entry-count bound')
            result[relative] = data
    return result


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise CompatibilityError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def _json_object(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data.decode('utf-8'), object_pairs_hook=_unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CompatibilityError(f'Invalid JSON in {label}: {exc}') from exc
    if not isinstance(value, dict):
        raise CompatibilityError(f'{label} must contain a JSON object')
    return value


def _identity(manifest: dict) -> tuple[str, str, str]:
    name = manifest.get('name')
    version = manifest.get('version')
    description = manifest.get('description', '')
    if not isinstance(name, str) or len(name) > 64 or not PLUGIN_NAME.fullmatch(name):
        raise CompatibilityError('Manifest name must match Kimi plugin-id syntax')
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise CompatibilityError('Manifest version must be semantic version text')
    if not isinstance(description, str):
        raise CompatibilityError('Manifest description must be text')
    return name, version, description


def _skill_metadata(data: bytes, label: str) -> tuple[str, str]:
    """Check this package's simple single-line Agent Skills metadata."""
    try:
        text = data.decode('utf-8')
    except UnicodeError as exc:
        raise CompatibilityError(f'Invalid UTF-8 skill: {label}') from exc
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise CompatibilityError(f'Missing skill frontmatter: {label}')
    try:
        end = lines.index('---', 1)
    except ValueError as exc:
        raise CompatibilityError(f'Unclosed skill frontmatter: {label}') from exc
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'(name|description):\s*(.+)', line)
        if not match:
            # Ancillary YAML fields are outside this small discovery contract.
            continue
        key, value = match.groups()
        if key in metadata:
            raise CompatibilityError(f'Duplicate {key} in skill metadata: {label}')
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise CompatibilityError(f'Unsupported quoted skill metadata: {label}') from exc
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1].replace("''", "'")
        elif value.startswith(('|', '>', '&', '*', '!', '[', '{')) or value in {'true', 'false', 'null', '~'}:
            raise CompatibilityError(f'Unsupported non-string skill metadata: {label}')
        if not isinstance(value, str):
            raise CompatibilityError(f'Skill {key} must be text: {label}')
        metadata[key] = value
    name = metadata.get('name', '')
    description = metadata.get('description', '')
    if len(name) > 64 or not NAME.fullmatch(name):
        raise CompatibilityError(f'Invalid skill name: {label}')
    if not description.strip() or len(description) > 1024:
        raise CompatibilityError(f'Invalid skill description: {label}')
    return name, description


def _local_links(root: Path, files: dict[Path, bytes]) -> None:
    for relative, data in files.items():
        if relative.suffix.casefold() != '.md':
            continue
        try:
            text = data.decode('utf-8')
        except UnicodeError as exc:
            raise CompatibilityError(f'Invalid Markdown UTF-8: {relative}') from exc
        for match in LINK.finditer(text):
            target = match.group(1).strip('<>')
            try:
                parsed = urlsplit(target)
            except ValueError as exc:
                raise CompatibilityError(f'Invalid Markdown link: {relative}: {target}') from exc
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = (root / relative.parent / unquote(parsed.path)).resolve()
            if not path.is_relative_to(root):
                raise CompatibilityError(f'Markdown link escapes plugin: {relative}: {target}')
            if not path.exists():
                raise CompatibilityError(f'Broken local Markdown link: {relative}: {target}')


def validate_kimi(directory: str | Path, expected_skills: int | None = None) -> list[str]:
    """Return static errors for the iOS package's Kimi skills-only profile.

    Supports current native metadata, skill roots and optional session-start
    skill instructions. This is not a validator for arbitrary MCP/hook plugins.
    """
    errors: list[str] = []
    try:
        root = Path(directory).absolute()
        _no_symlink_components(root)
        root = root.resolve()
        files = _inventory(root)
        primary = Path('kimi.plugin.json')
        fallback = Path('.kimi-plugin/plugin.json')
        manifest_path = primary if primary in files else fallback
        if manifest_path not in files:
            return ['No current Kimi manifest at kimi.plugin.json or .kimi-plugin/plugin.json']
        if primary in files and fallback in files:
            errors.append('Two Kimi manifests would shadow each other; retain one authoritative manifest')
        manifest = _json_object(files[manifest_path], str(manifest_path))
        name, version, description = _identity(manifest)
        unsupported = {'tools', 'apps', 'inject', 'configFile', 'config_file', 'bootstrap', 'runtime'}
        declared_unsupported = sorted(set(manifest) & unsupported)
        if declared_unsupported:
            errors.append('Unsupported current Kimi runtime fields: ' + ', '.join(declared_unsupported))
        allowed = {'$schema', 'name', 'version', 'description', 'keywords', 'author', 'homepage', 'license',
                   'interface', 'skills', 'sessionStart', 'skillInstructions'}
        extra = sorted(set(manifest) - allowed - unsupported)
        if extra:
            errors.append('Fields outside this skills-only Kimi profile: ' + ', '.join(extra))
        if '$schema' in manifest and manifest['$schema'] != 'https://kimi.com/schemas/kimi.plugin.schema.json':
            errors.append('Unexpected Kimi schema identifier')
        for field in ('homepage', 'license', 'skillInstructions'):
            if field in manifest and not isinstance(manifest[field], str):
                errors.append(f'Kimi {field} must be text')
        if 'keywords' in manifest and (not isinstance(manifest['keywords'], list) or any(not isinstance(x, str) for x in manifest['keywords'])):
            errors.append('Kimi keywords must be a string array')
        if 'author' in manifest and not isinstance(manifest['author'], (str, dict)):
            errors.append('Kimi author must be text or an object')
        if 'interface' in manifest:
            interface = manifest['interface']
            if not isinstance(interface, dict) or any(not isinstance(v, str) for v in interface.values()):
                errors.append('Kimi interface fields must be text')
        if Path('plugin.json') in files:
            portable = _json_object(files[Path('plugin.json')], 'portable plugin.json')
            for field, value in (('name', name), ('version', version), ('description', description)):
                if portable.get(field, '') != value:
                    errors.append(f'Kimi {field} differs from portable plugin.json')
        raw = manifest.get('skills')
        roots = [raw] if isinstance(raw, str) else raw
        if not isinstance(roots, list) or not roots or any(not isinstance(x, str) for x in roots):
            errors.append('Kimi skills must explicitly declare a nonempty ./ path or path array')
            roots = []
        seen_roots: set[Path] = set()
        found: dict[str, Path] = {}
        for entry in roots:
            if not entry.startswith('./'):
                errors.append(f'Kimi skills path must start with ./: {entry}')
                continue
            folder = (root / entry).resolve()
            if not folder.is_relative_to(root):
                errors.append(f'Kimi skills path escapes plugin: {entry}')
                continue
            if not folder.is_dir():
                errors.append(f'Kimi skills path is not a directory: {entry}')
                continue
            if folder in seen_roots:
                errors.append(f'Duplicate Kimi skill root: {entry}')
                continue
            seen_roots.add(folder)
            for skill_dir in sorted(folder.iterdir()):
                if skill_dir.is_file() and skill_dir.suffix.casefold() == '.md':
                    errors.append(f'Flat skill file is outside this directory-form package profile: {skill_dir.relative_to(root)}')
                    continue
                skill_file = skill_dir / 'SKILL.md'
                if not skill_dir.is_dir() or not skill_file.is_file():
                    continue
                relative = skill_file.relative_to(root)
                skill_name, _ = _skill_metadata(files[relative], str(relative))
                if skill_name != skill_dir.name:
                    errors.append(f'Skill name differs from its directory: {relative}')
                key = skill_name.casefold()
                if key in found:
                    errors.append(f'Duplicate Kimi skill name: {skill_name}')
                found[key] = relative
        if not found:
            errors.append('Kimi manifest discovers no directory-form skills')
        if expected_skills is not None and len(found) != expected_skills:
            errors.append(f'Expected {expected_skills} Kimi skills, found {len(found)}')
        if 'sessionStart' in manifest:
            start = manifest['sessionStart']
            if not isinstance(start, dict) or set(start) != {'skill'} or not isinstance(start.get('skill'), str):
                errors.append('Kimi sessionStart must name one declared skill')
            elif start['skill'].casefold() not in found:
                errors.append('Kimi sessionStart skill was not discovered')
        for required in (f'skills/{name}/SKILL.md',
                         'references/operating-contract.md', 'LICENSE'):
            if Path(required) not in files:
                errors.append(f'Missing shared support file: {required}')
        _local_links(root, files)
    except (CompatibilityError, OSError, ValueError) as exc:
        errors.append(str(exc))
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--expected-skills', type=int, help='Require an explicit discovered-skill count')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    if args.expected_skills is not None and args.expected_skills < 1:
        parser.error('--expected-skills must be positive')
    errors = validate_kimi(args.root, args.expected_skills)
    if args.json:
        print(json.dumps({'valid': not errors, 'host_contract': 'kimi-code-2.x-skills',
                          'expected_skills': args.expected_skills, 'runtime_tested': False,
                          'errors': errors}, indent=2))
    elif errors:
        for error in errors:
            print(f'Kimi compatibility: {error}', file=sys.stderr)
    else:
        print('Kimi Code 2.x static compatibility passed.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
