#!/usr/bin/env python3
"""Bounded read-only iOS project inventory. Never executes project configuration."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import sys

MAX_FILES = 20000
MAX_BYTES = 1024 * 1024
SKIP_DIRS = {'.git', 'node_modules', 'Pods', 'Carthage', 'DerivedData', '.build', 'build', 'dist', '__pycache__', '.venv', 'vendor'}
SETTINGS = ('IPHONEOS_DEPLOYMENT_TARGET', 'SWIFT_VERSION', 'SWIFT_STRICT_CONCURRENCY', 'SWIFT_DEFAULT_ACTOR_ISOLATION', 'SWIFT_APPROACHABLE_CONCURRENCY', 'SDKROOT', 'SUPPORTED_PLATFORMS')
FRAMEWORKS = ('SwiftUI', 'UIKit', 'CoreData', 'SwiftData', 'XCTest', 'Testing', 'WidgetKit', 'AppIntents', 'CloudKit', 'Nuke', 'NukeUI', 'ExyteChat')
TOOLS = ('xcodebuild', 'xcrun', 'swift', 'asc', 'eas', 'node', 'python3')


def read_small(path: Path, root: Path, warnings: list[str]) -> str | None:
    try:
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            warnings.append(f'Skipped link or outside-root file: {path.relative_to(root)}')
            return None
        # Nonblocking open avoids hanging on a named pipe; fstat checks the
        # opened object itself. Never follow a final-component symlink.
        flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
        with os.fdopen(os.open(path, flags), 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                warnings.append(f'Skipped nonregular file: {path.relative_to(root)}')
                return None
            # Read at most the bound even if the file grows after inspection.
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            warnings.append(f'Skipped oversized file: {path.relative_to(root)}')
            return None
        return data.decode('utf-8-sig')
    except (OSError, UnicodeError, ValueError) as exc:
        warnings.append(f'Could not read {path.name}: {type(exc).__name__}')
        return None


def probe(project: str | Path, limit: int = MAX_FILES) -> dict:
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('Project path must be an existing directory')
    if not 1 <= limit <= MAX_FILES:
        raise ValueError(f'File limit must be between 1 and {MAX_FILES}')
    report = {'format_version': 1, 'project': str(root), 'host': platform.system(),
              'stack': 'unknown', 'signals': [], 'projects': [], 'workspaces': [],
              'settings_candidates': [], 'package_pins': [], 'framework_imports': {},
              'tools_on_path': {tool: bool(shutil.which(tool)) for tool in TOOLS},
              'scanned_files': 0, 'truncated': False, 'warnings': [],
              'limitations': ['Static candidates only; does not evaluate xcconfig includes, target inheritance, conditional build settings, Swift manifests, or dynamic app configuration.',
                              'Tool presence is not proof of installation health, authentication, selected Xcode, build compatibility, or runtime success.']}
    native = expo_runtime = react_native = eas = False
    for current, dirs, names in os.walk(root, followlinks=False):
        here = Path(current)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.env') and not (here / d).is_symlink())
        for d in dirs:
            rel = str((here / d).relative_to(root))
            if d.endswith('.xcodeproj'):
                report['projects'].append(rel)
                native = True
            elif d.endswith('.xcworkspace'):
                report['workspaces'].append(rel)
        for name in sorted(names):
            if report['scanned_files'] >= limit:
                report['truncated'] = True
                break
            report['scanned_files'] += 1
            p = here / name
            if p.is_symlink():
                continue
            selected = name in {'Package.swift', 'Package.resolved', 'package.json', 'project.pbxproj', 'eas.json'} or name.endswith(('.xcconfig', '.swift'))
            if not selected:
                continue
            rel = str(p.relative_to(root))
            if name == 'eas.json':
                eas = True
                report['signals'].append({'kind': 'eas_config', 'path': rel})
                continue
            text = read_small(p, root, report['warnings'])
            if text is None:
                continue
            if name == 'package.json':
                try:
                    data = json.loads(text)
                    if not isinstance(data, dict):
                        raise ValueError('expected object')
                    deps: dict = {}
                    for group in ('dependencies', 'devDependencies'):
                        value = data.get(group, {})
                        if not isinstance(value, dict):
                            raise ValueError('dependency group must be object')
                        deps.update(value)
                    for dep in ('expo', 'react-native'):
                        if dep in deps:
                            report['signals'].append({'kind': 'runtime_dependency', 'name': dep, 'path': rel})
                    expo_runtime |= 'expo' in deps
                    react_native |= 'react-native' in deps
                except (ValueError, TypeError):
                    report['warnings'].append(f'Invalid package JSON: {rel}')
            elif name == 'Package.resolved':
                try:
                    data = json.loads(text)
                    if not isinstance(data, dict):
                        raise ValueError('expected object')
                    nested = data.get('object', {})
                    if not isinstance(nested, dict):
                        raise ValueError('invalid legacy object')
                    pins = data.get('pins', nested.get('pins', []))
                    if not isinstance(pins, list):
                        raise ValueError('pins must be list')
                    for pin in pins[:500]:
                        if not isinstance(pin, dict) or not isinstance(pin.get('state', {}), dict):
                            raise ValueError('invalid pin')
                        state = pin.get('state', {})
                        # Omit repository URLs, which can contain embedded credentials.
                        identity = pin.get('identity', pin.get('package'))
                        report['package_pins'].append({'identity': identity if isinstance(identity, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,150}', identity) else '(unrecognized)',
                                                      'version': state.get('version') if isinstance(state.get('version'), str) and re.fullmatch(r'[A-Za-z0-9.+_-]{1,100}', state['version']) else None,
                                                      'revision': state.get('revision') if isinstance(state.get('revision'), str) and re.fullmatch(r'[a-fA-F0-9]{7,64}', state['revision']) else None,
                                                      'path': rel})
                except (ValueError, TypeError, AttributeError):
                    report['warnings'].append(f'Invalid resolved-package JSON: {rel}')
            elif name == 'Package.swift':
                native = True
                tools = re.search(r'^\s*//\s*swift-tools-version:\s*([0-9.]+)', text, re.M)
                report['signals'].append({'kind': 'swift_manifest', 'path': rel, 'tools_version_candidate': tools.group(1) if tools else None})
            elif name == 'project.pbxproj' or name.endswith('.xcconfig'):
                for setting in SETTINGS:
                    pattern = r'(?m)^\s*' + re.escape(setting) + r'(?:\[[^\]\n]+\])*\s*=\s*([^;\n]+)'
                    for match in re.finditer(pattern, text):
                        value = match.group(1).strip().strip('"')
                        # Only report simple setting values, not expansion or executable text.
                        if re.fullmatch(r'[A-Za-z0-9_. +,-]{1,100}', value):
                            report['settings_candidates'].append({'setting': setting, 'value': value, 'path': rel})
            if name.endswith('.swift'):
                for framework in FRAMEWORKS:
                    if re.search(r'(?m)^\s*(?:@\w+\s+)?import\s+' + framework + r'\b', text):
                        bucket = report['framework_imports'].setdefault(framework, {'count': 0, 'sample_paths': []})
                        bucket['count'] += 1
                        if len(bucket['sample_paths']) < 5:
                            bucket['sample_paths'].append(rel)
        if report['truncated']:
            report['warnings'].append('Scan bound reached; narrow the project path for complete discovery.')
            break
    if expo_runtime:
        report['stack'] = 'expo-with-native' if native else 'expo'
    elif react_native:
        report['stack'] = 'react-native-with-native' if native else 'react-native'
    elif native:
        report['stack'] = 'native-swift'
    if eas:
        report['limitations'].append('EAS config alone does not imply an Expo runtime or authorize cloud use.')
    if platform.system() != 'Darwin':
        report['limitations'].append('This host cannot establish local Xcode, Apple simulator or physical-device validation.')
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', nargs='?', default='.')
    parser.add_argument('--max-files', type=int, default=MAX_FILES)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(probe(args.project, args.max_files), indent=2))
    except (ValueError, OSError) as exc:
        print(f'project_probe: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
