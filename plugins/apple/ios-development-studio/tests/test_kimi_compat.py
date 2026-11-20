"""Kimi Code 2.x manifest/discovery regression checks; no host or provider calls."""
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
SPEC = importlib.util.spec_from_file_location('validate_kimi', ROOT / 'scripts/validate_kimi.py')
kimi = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kimi)


class KimiCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / 'plugin'
        self.root.mkdir()
        self.identity = {'name': 'ios-development-studio', 'version': '1.1.0', 'description': 'iOS workflows'}
        self.write('plugin.json', json.dumps(self.identity))
        self.manifest = {**self.identity, 'skills': './skills/'}
        self.save_manifest()
        self.skill('skills/ios-development', 'ios-development')
        self.skill('skills/ios-testing', 'ios-testing')
        for name in ('skills/ios-development/references/operating-contract.md', 'scripts/project_probe.py',
                     'scripts/route.py', 'LICENSE', 'THIRD_PARTY_NOTICES.md', 'docs/source-map.md'):
            self.write(name, 'Support content\n')

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value, encoding='utf-8')
        return p

    def skill(self, directory, name):
        return self.write(directory + '/SKILL.md', f'---\nname: {name}\ndescription: Use for the requested iOS workflow.\n---\n\n# Workflow\n')

    def save_manifest(self):
        self.write('kimi.plugin.json', json.dumps(self.manifest))

    def errors(self):
        return kimi.validate_kimi(self.root, expected_skills=2)

    def test_current_canonical_package_discovers_all_26_without_changes(self):
        before = {p.relative_to(ROOT): p.read_bytes() for p in ROOT.rglob('*') if p.is_file()}
        self.assertEqual(kimi.validate_kimi(ROOT, expected_skills=26), [])
        after = {p.relative_to(ROOT): p.read_bytes() for p in ROOT.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_minimal_current_native_manifest_and_source_are_valid(self):
        self.assertEqual(self.errors(), [])
        self.assertNotIn('tools', self.manifest)
        self.assertNotIn('inject', self.manifest)

    def test_documented_hidden_manifest_path_is_supported(self):
        data = (self.root / 'kimi.plugin.json').read_text()
        (self.root / 'kimi.plugin.json').unlink()
        self.write('.kimi-plugin/plugin.json', data)
        self.assertEqual(self.errors(), [])

    def test_shadowed_manifests_are_reported(self):
        self.write('.kimi-plugin/plugin.json', json.dumps(self.manifest))
        self.assertTrue(any('shadow' in error for error in self.errors()))

    def test_portable_manifest_alone_is_not_current_kimi_installation(self):
        (self.root / 'kimi.plugin.json').unlink()
        self.assertTrue(any('No current Kimi manifest' in error for error in self.errors()))

    def test_identity_version_and_description_stay_synchronized(self):
        for field, value in [('name', 'another-plugin'), ('version', '1.2.0'), ('description', 'Changed')]:
            with self.subTest(field=field):
                self.manifest = {**self.identity, 'skills': './skills/', field: value}
                self.save_manifest()
                self.assertTrue(any(f'{field} differs' in error for error in self.errors()))

    def test_old_python_runtime_fields_are_rejected_even_when_empty(self):
        for field in ('tools', 'apps', 'inject', 'configFile', 'config_file', 'bootstrap', 'runtime'):
            with self.subTest(field=field):
                self.manifest = {**self.identity, 'skills': './skills/', field: []}
                self.save_manifest()
                self.assertTrue(any('Unsupported current Kimi runtime fields' in error for error in self.errors()))

    def test_current_display_metadata_and_skill_instructions_are_supported(self):
        self.manifest.update({'$schema': 'https://kimi.com/schemas/kimi.plugin.schema.json',
                              'keywords': ['ios', 'swift'], 'author': {'name': 'Maintainer'},
                              'license': 'MIT', 'homepage': 'https://example.com/',
                              'interface': {'displayName': 'iOS Development Studio', 'shortDescription': 'iOS workflows'},
                              'skillInstructions': 'Use the project deployment target.',
                              'sessionStart': {'skill': 'ios-development'}})
        self.save_manifest()
        self.assertEqual(self.errors(), [])

    def test_manifest_capabilities_outside_this_profile_are_explicit(self):
        self.manifest['hooks'] = []
        self.save_manifest()
        self.assertTrue(any('outside this skills-only Kimi profile' in error for error in self.errors()))

    def test_skill_roots_accept_a_contained_path_array(self):
        self.manifest['skills'] = ['./skills/']
        self.save_manifest()
        self.assertEqual(self.errors(), [])

    def test_invalid_skill_root_types_do_not_crash(self):
        for value in (None, [], {}, [True], 42):
            with self.subTest(value=value):
                self.manifest['skills'] = value
                self.save_manifest()
                self.assertTrue(any('explicitly declare' in error for error in self.errors()))

    def test_skill_path_requires_dot_slash_and_existing_directory(self):
        for value, message in [('skills/', 'start with ./'), ('./absent', 'not a directory'),
                               ('./LICENSE', 'not a directory')]:
            with self.subTest(value=value):
                self.manifest['skills'] = value
                self.save_manifest()
                self.assertTrue(any(message in error for error in self.errors()))

    def test_escaping_skill_root_is_rejected(self):
        outside = self.parent / 'outside'
        outside.mkdir()
        self.manifest['skills'] = './../outside'
        self.save_manifest()
        self.assertTrue(any('escapes plugin' in error for error in self.errors()))

    def test_duplicate_resolved_roots_are_rejected(self):
        self.manifest['skills'] = ['./skills', './skills/']
        self.save_manifest()
        self.assertTrue(any('Duplicate Kimi skill root' in error for error in self.errors()))

    def test_duplicate_skill_names_across_roots_are_rejected(self):
        self.skill('another/ios-testing', 'ios-testing')
        self.manifest['skills'] = ['./skills/', './another/']
        self.save_manifest()
        self.assertTrue(any('Duplicate Kimi skill name' in error for error in self.errors()))

    def test_stray_flat_skill_is_not_silently_missed_by_count(self):
        self.write('skills/extra.md', 'Another skill')
        self.assertTrue(any('Flat skill file' in error for error in self.errors()))

    def test_session_start_must_name_a_discovered_skill(self):
        for value in ({'skill': 'missing'}, {'skill': 1}, 'ios-development'):
            with self.subTest(value=value):
                self.manifest['sessionStart'] = value
                self.save_manifest()
                self.assertTrue(any('sessionStart' in error for error in self.errors()))

    def test_required_directory_metadata_and_unique_keys_are_checked(self):
        p = self.root / 'skills/ios-testing/SKILL.md'
        for body in ('# Missing frontmatter', '---\nname: ios-testing\n---\n',
                     '---\nname: ios-testing\nname: ios-testing\ndescription: Valid\n---\n'):
            with self.subTest(body=body):
                p.write_text(body)
                self.assertTrue(self.errors())

    def test_skill_name_matches_directory_and_description_limits(self):
        self.skill('skills/ios-testing', 'wrong-name')
        self.assertTrue(any('differs from its directory' in error for error in self.errors()))
        self.write('skills/ios-testing/SKILL.md', '---\nname: ios-testing\ndescription: ' + 'x' * 1025 + '\n---\n')
        self.assertTrue(any('description' in error for error in self.errors()))

    def test_malformed_json_utf8_and_types_return_errors(self):
        for data in (b'{bad', b'[]', b'\xff', b'{"name":"one","name":"two"}'):
            with self.subTest(data=data):
                (self.root / 'kimi.plugin.json').write_bytes(data)
                self.assertTrue(self.errors())

    def test_missing_shared_support_and_broken_relative_links(self):
        (self.root / 'docs/source-map.md').unlink()
        self.assertTrue(any('Missing shared support file' in error for error in self.errors()))
        self.write('docs/source-map.md', '[Missing](missing.md)')
        self.assertTrue(any('Broken local Markdown link' in error for error in self.errors()))

    def test_escaping_markdown_link_is_rejected_even_if_target_exists(self):
        (self.parent / 'outside.md').write_text('Outside')
        self.write('README.md', '[Outside](../outside.md)')
        self.assertTrue(any('escapes' in error for error in self.errors()))

    def test_external_and_anchor_references_do_not_make_network_calls(self):
        self.write('README.md', '[Online](https://example.invalid/reference)\n[Anchor](#local)')
        self.assertEqual(self.errors(), [])

    @unittest.skipUnless(hasattr(os, 'symlink'), 'Requires symlink support')
    def test_symlinked_root_or_files_are_rejected(self):
        linked = self.parent / 'linked'
        linked.symlink_to(self.root, target_is_directory=True)
        self.assertTrue(kimi.validate_kimi(linked))
        (self.root / 'linked.md').symlink_to(self.root / 'docs/source-map.md')
        self.assertTrue(any('Symlink' in error for error in self.errors()))

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'Requires POSIX FIFO support')
    def test_special_file_is_rejected_without_blocking(self):
        os.mkfifo(self.root / 'blocked.md')
        result = subprocess.run([sys.executable, '-S', str(ROOT / 'scripts/validate_kimi.py'), str(self.root),
                                 '--expected-skills', '2', '--json'], capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['valid'])

    def test_expected_discovery_count_is_enforced(self):
        self.assertTrue(any('Expected 26' in error for error in kimi.validate_kimi(self.root, 26)))

    def test_cli_works_with_only_standard_library(self):
        result = subprocess.run([sys.executable, '-S', str(ROOT / 'scripts/validate_kimi.py'), str(self.root),
                                 '--expected-skills', '2', '--json'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        self.assertTrue(data['valid'])
        self.assertFalse(data['runtime_tested'])
        self.assertEqual(data['host_contract'], 'kimi-code-2.x-skills')


if __name__ == '__main__':
    unittest.main()
