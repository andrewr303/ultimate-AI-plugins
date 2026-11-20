#!/usr/bin/env python3
"""Read-only repository documentation inventory; emits metadata, never file bodies."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from doc_common import InputFailure, MAX_FILES, inventory, read_text, root_path

STACK_DEPS = {'@astrojs/starlight': 'starlight', '@docusaurus/core': 'docusaurus',
              'vitepress': 'vitepress', 'nextra': 'nextra',
              'fumadocs-core': 'fumadocs', 'fumadocs-ui': 'fumadocs',
              'vitepress-theme-demoblock': 'vitepress'}
CONFIG_MARKERS = {'mkdocs.yml': 'mkdocs', 'mkdocs.yaml': 'mkdocs',
                  'book.toml': 'mdbook', 'docs.json': 'mintlify',
                  'mint.json': 'mintlify', '.readthedocs.yaml': 'readthedocs',
                  '.readthedocs.yml': 'readthedocs'}


def inspect(root: Path, max_files: int = MAX_FILES) -> tuple[dict, int]:
    files, limits = inventory(root, max_files)
    paths = [p.relative_to(root).as_posix() for p in files]
    stacks: list[dict] = []
    manifests: list[dict] = []
    configs: list[str] = []
    failures: list[dict] = []
    docs = [s for s in paths if Path(s).suffix.lower() in {'.md', '.mdx', '.markdown', '.rst'}]
    for p, relative in zip(files, paths):
        name = p.name.lower()
        stack = CONFIG_MARKERS.get(name)
        if name.startswith('docusaurus.config.'):
            stack = 'docusaurus'
        if p.parent.name == '.vitepress' and name.startswith('config.'):
            stack = 'vitepress'
        if stack:
            configs.append(relative)
            stacks.append({'name': stack, 'evidence': relative, 'kind': 'config-marker'})
        if name != 'package.json':
            continue
        try:
            data = json.loads(read_text(root, p))
            if not isinstance(data, dict):
                raise ValueError('manifest is not an object')
            info = {'path': relative}
            for key in ('name', 'version', 'packageManager'):
                if isinstance(data.get(key), str):
                    info[key] = data[key][:200]
            scripts = data.get('scripts', {})
            info['script_names'] = sorted(scripts) if isinstance(scripts, dict) else []
            detected = {}
            for key in ('dependencies', 'devDependencies', 'peerDependencies'):
                deps = data.get(key, {})
                if isinstance(deps, dict):
                    for dep, version in deps.items():
                        if dep in STACK_DEPS and isinstance(version, str):
                            detected[dep] = version[:120]
                            stacks.append({'name': STACK_DEPS[dep], 'evidence': relative,
                                           'kind': 'dependency', 'package': dep,
                                           'version_range': version[:120]})
            info['documentation_dependencies'] = detected
            manifests.append(info)
        except (InputFailure, ValueError, json.JSONDecodeError):
            failures.append({'path': relative, 'reason': 'manifest unreadable, oversized, or invalid JSON'})
    readme = [p for p in docs if Path(p).name.lower().startswith('readme.')]
    result = {'tool': 'repo_inspect', 'schema_version': 1,
              'scope': 'Bounded read-only inventory. Markers suggest stacks; they do not prove configured features.',
              'limits': limits, 'stacks': stacks, 'manifests': manifests,
              'documentation_files': docs[:250], 'documentation_file_count': len(docs),
              'config_files': configs,
              'extension_counts': dict(sorted(Counter(Path(p).suffix.lower() or '[none]' for p in paths).items())),
              'missing': {'readme': not bool(readme), 'docs_directory': not any(p.startswith(('docs/', 'doc/', 'documentation/')) for p in paths),
                          'detected_site_stack': not bool(stacks)},
              'unsupported': ['Configuration content and runtime behavior are not evaluated.',
                              'Secrets, environment files, symlinks, dependencies and build directories are excluded.'],
              'failures': failures}
    if len(docs) > 250:
        result['unsupported'].append('Documentation path display capped at 250 entries.')
    if limits['truncated']:
        result['unsupported'].append('Traversal limit reached; inventory is incomplete.')
    return result, 2 if failures or limits['read_failures'] else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.', help='Repository directory (never modified).')
    parser.add_argument('--max-files', type=int, default=MAX_FILES, help='Maximum scanned entries, 1..50000.')
    args = parser.parse_args()
    if not 1 <= args.max_files <= 50000:
        parser.error('--max-files must be between 1 and 50000')
    try:
        result, status = inspect(root_path(args.root), args.max_files)
    except InputFailure as exc:
        print(json.dumps({'tool': 'repo_inspect', 'failure': str(exc)}))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return status

if __name__ == '__main__':
    sys.exit(main())
