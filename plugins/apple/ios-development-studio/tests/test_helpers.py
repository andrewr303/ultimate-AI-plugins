"""Behavioral checks for original read-only tools; no Apple toolchain required."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe_module = load_script('project_probe')
route_module = load_script('route')


class ProjectProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, data):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(data)
        return p

    def test_native_settings_are_candidates_and_probe_never_writes(self):
        self.write('App.xcodeproj/project.pbxproj', 'SWIFT_VERSION = 5.0;\nIPHONEOS_DEPLOYMENT_TARGET = 16.0;\nSWIFT_STRICT_CONCURRENCY = complete;')
        self.write('App/Screen.swift', 'import SwiftUI\nimport CoreData\n')
        self.write('package.json', '{"private":true}')
        self.write('eas.json', '{"build":{}}')
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = probe_module.probe(self.root)
        self.assertEqual(result['stack'], 'native-swift')
        self.assertEqual(result['framework_imports']['SwiftUI']['count'], 1)
        self.assertIn({'setting':'SWIFT_VERSION','value':'5.0','path':'App.xcodeproj/project.pbxproj'}, result['settings_candidates'])
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertTrue(any('static' in s.casefold() for s in result['limitations']))

    def test_expo_dependency_and_native_signal_can_coexist(self):
        self.write('package.json', '{"dependencies":{"expo":"~55.0.0","react-native":"0.80.0"}}')
        self.write('ios/App.xcodeproj/project.pbxproj', 'SWIFT_VERSION = 5.0;')
        self.assertEqual(probe_module.probe(self.root)['stack'], 'expo-with-native')

    def test_config_key_or_eas_wrapper_does_not_adopt_expo(self):
        self.write('package.json', '{"private":true,"expo":{"name":"Tooling wrapper"}}')
        self.write('eas.json', '{}')
        self.assertEqual(probe_module.probe(self.root)['stack'], 'unknown')

    def test_bare_react_native_is_not_expo(self):
        self.write('package.json', '{"dependencies":{"react-native":"0.80.0"}}')
        self.assertEqual(probe_module.probe(self.root)['stack'], 'react-native')

    def test_does_not_evaluate_swift_or_dynamic_javascript(self):
        marker = self.root / 'executed'
        self.write('Package.swift', '// swift-tools-version: 6.0\n// import data\nprint("never run")')
        self.write('app.config.js', f'require("fs").writeFileSync({json.dumps(str(marker))}, "bad")')
        result = probe_module.probe(self.root)
        self.assertFalse(marker.exists())
        self.assertEqual(result['signals'][0]['tools_version_candidate'], '6.0')

    def test_skips_links_dependencies_and_oversized_inputs(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / 'Secret.swift'
            external.write_text('import Nuke\n')
            (self.root / 'linked.swift').symlink_to(external)
            (self.root / 'linked-dir').symlink_to(Path(outside), target_is_directory=True)
            self.write('node_modules/hidden.swift', 'import NukeUI\n')
            self.write('Huge.swift', 'import ExyteChat\n' + 'x' * probe_module.MAX_BYTES)
            result = probe_module.probe(self.root)
            self.assertEqual(result['framework_imports'], {})
            self.assertTrue(any('oversized' in w for w in result['warnings']))

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO fixture requires a POSIX host')
    def test_named_pipe_is_skipped_without_blocking(self):
        os.mkfifo(self.root / 'Blocked.swift')
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/project_probe.py'), str(self.root)],
                                capture_output=True, text=True, timeout=3, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report['framework_imports'], {})
        self.assertTrue(any('nonregular' in w for w in report['warnings']))

    def test_lockfile_formats_and_no_credential_urls(self):
        sensitive_url = 'https://person:private-value@example.invalid/private.git'
        self.write('Package.resolved', json.dumps({'version': 2,'pins':[{'identity':'nuke','location':sensitive_url,'state':{'version':'13.0.0','revision':'a' * 40}}]}))
        self.write('nested/Package.resolved', json.dumps({'object':{'pins':[{'package':'Chat','repositoryURL':sensitive_url,'state':{'version':'2.0.0','revision':'b' * 40}}]},'version':1}))
        result = probe_module.probe(self.root)
        self.assertEqual(len(result['package_pins']), 2)
        self.assertNotIn('private-value', json.dumps(result))
        self.assertEqual(result['package_pins'][0]['identity'], 'nuke')

    def test_malformed_json_and_types_do_not_crash(self):
        self.write('package.json', '{bad')
        self.write('Package.resolved', '{"pins":[null]}')
        result = probe_module.probe(self.root)
        self.assertEqual(len(result['warnings']), 2)
        self.write('package.json', '{"dependencies":[]}')
        self.write('Package.resolved', '[]')
        self.assertEqual(len(probe_module.probe(self.root)['warnings']), 2)

    def test_scan_bounds_and_missing_path(self):
        self.write('a.swift', 'import SwiftUI')
        self.write('b.swift', 'import UIKit')
        result = probe_module.probe(self.root, limit=1)
        self.assertTrue(result['truncated'])
        self.assertEqual(result['scanned_files'], 1)
        with self.assertRaises(ValueError):
            probe_module.probe(self.root / 'absent')
        with self.assertRaises(ValueError):
            probe_module.probe(self.root, limit=0)

    def test_never_prints_arbitrary_dependency_or_setting_values(self):
        self.write('package.json', '{"dependencies":{"expo":"https://person:private-value@example.invalid"}}')
        self.write('x.xcconfig', 'SWIFT_VERSION = $(sensitive);\nPRODUCT_BUNDLE_IDENTIFIER = private.internal.app;')
        result = probe_module.probe(self.root)
        rendered = json.dumps(result)
        self.assertNotIn('private-value', rendered)
        self.assertNotIn('sensitive', rendered)
        self.assertNotIn('private.internal.app', rendered)
        self.assertEqual(result['settings_candidates'], [])


class RoutingTests(unittest.TestCase):
    def test_fixture_routes(self):
        fixtures = json.loads((ROOT / 'tests/fixtures/routing.json').read_text())
        for fixture in fixtures:
            with self.subTest(request=fixture['request']):
                result = route_module.suggest(fixture['request'], fixture['stack'])
                self.assertEqual(result['primary'], fixture['primary'])
                if fixture.get('supporting_contains'):
                    self.assertIn(fixture['supporting_contains'], result['supporting'])

    def test_rejects_empty_or_oversized_request_and_invalid_stack(self):
        for request, stack in [('', 'auto'), ('x' * 20001, 'native'), ('test', 'invalid')]:
            with self.assertRaises(ValueError):
                route_module.suggest(request, stack)

    def test_no_actions_are_executed(self):
        result = route_module.suggest('Prepare this iOS app release', 'native')
        self.assertEqual(result['primary'], 'ios-release')
        self.assertIn('does not', result['limitation'])
        self.assertIn('authorize', result['limitation'])


if __name__ == '__main__':
    unittest.main()
