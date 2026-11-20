"""Behavior tests for the plugin's bounded, offline documentation helpers."""
from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/repo-docs/scripts'
sys.path.insert(0, str(SCRIPTS))
from doc_common import InputFailure, contained, inventory, root_path
import docs_check
import repo_inspect


class Helpers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def check(self, content, extra=None):
        self.write('README.md', content)
        for path, body in (extra or {}).items():
            self.write(path, body)
        return docs_check.run(self.root, None, 5000)

    def codes(self, result):
        return {f['code'] for f in result['findings']}

    def unresolved(self, result):
        return {f['code'] for f in result['unresolved']}

    def test_unmatched_leading_thematic_break_does_not_hide_broken_link(self):
        result, status = self.check('---\n# Title\n\n[broken](missing.md)\n')
        self.assertEqual(status, 1)
        self.assertIn('missing-local-file', self.codes(result))
        self.assertNotIn('unclosed-frontmatter', self.codes(result))

    def test_unclosed_mapping_frontmatter_errors_and_keeps_scanning(self):
        result, status = self.check('---\ntitle: Example\n\n[broken](missing.md)\n')
        self.assertEqual(status, 1)
        self.assertEqual(self.codes(result), {'unclosed-frontmatter', 'missing-local-file'})

    def test_paired_thematic_breaks_do_not_hide_markdown(self):
        result, status = self.check('---\n# Title\n\n[broken](missing.md)\n\n---\n')
        self.assertEqual(status, 1)
        self.assertEqual(self.codes(result), {'missing-local-file'})
        self.assertNotIn('frontmatter-not-validated', self.unresolved(result))

    def test_paired_mapping_frontmatter_is_scoped_and_body_still_checked(self):
        result, status = self.check('---\ntitle: "[metadata](not-a-document-link.md)"\ndescription: Demo\n---\n# Title\n\n[broken](missing.md)\n')
        self.assertEqual(status, 1)
        self.assertEqual(len(result['findings']), 1)
        self.assertEqual(result['findings'][0]['line'], 7)
        self.assertEqual(self.codes(result), {'missing-local-file'})
        self.assertIn('frontmatter-not-validated', self.unresolved(result))

    def test_thematic_break_and_valid_links_are_not_frontmatter_failure(self):
        result, status = self.check('---\n\n# Title\n\n[title](#title)\n')
        self.assertEqual(status, 0, result)
        self.assertEqual(result['findings'], [])

    def test_valid_local_files_fragments_duplicates_percent_and_reference(self):
        result, status = self.check('# Top\n\n[Top](#top)\n[second](#same-1)\n\n## Same\n\n## Same\n\n[space](docs/hello%20world.md#caf%C3%A9)\n![Diagram](image.png)\n[guide][ref]\n[ref]: docs/hello%20world.md "Guide"\n', {'docs/hello world.md': '# Café\n', 'image.png': 'image'})
        self.assertEqual(status, 0, result)
        self.assertEqual(result['findings'], [])

    def test_missing_local_file_and_anchor(self):
        result, status = self.check('# Title\n\n[bad](missing.md)\n[anchor](#missing)\n')
        self.assertEqual(status, 1)
        self.assertEqual(self.codes(result), {'missing-local-file', 'missing-heading-fragment'})

    def test_fences_inline_code_comments_and_indented_code_are_ignored(self):
        result, status = self.check('# Title\n\n```md\n[bad](missing.md)\n![ ](bad.png)\n```\n\n`[bad](missing.md)`\n\n<!-- [bad](missing.md) -->\n\n    [bad](missing.md)\n\n~~~md\n[bad](missing.md)\n~~~\n')
        self.assertEqual(status, 0, result)
        self.assertEqual(result['findings'], [])

    def test_longer_fence_contains_triple_backticks(self):
        result, status = self.check('# Title\n\n````md\n```\n[bad](missing.md)\n```\n````\n')
        self.assertEqual(status, 0, result)

    def test_unclosed_fence(self):
        result, status = self.check('# Title\n\n```bash\necho hi\n')
        self.assertEqual(status, 1)
        self.assertIn('unclosed-fence', self.codes(result))

    def test_unknown_full_and_collapsed_references(self):
        result, status = self.check('# Title\n\n[text][unknown]\n[missing][]\n')
        self.assertEqual(status, 1)
        self.assertEqual(len(result['findings']), 2)
        self.assertEqual(self.codes(result), {'unknown-reference'})

    def test_prose_brackets_do_not_create_unknown_reference_errors(self):
        result, status = self.check('# Title\n\nUse array[index] and [optional] text.\n')
        self.assertEqual(status, 0, result)

    def test_missing_alt_but_code_label_is_meaningful(self):
        result, status = self.check('# Title\n\n![](image.png)\n![`graph`](image.png)\n', {'image.png': 'image'})
        self.assertEqual(status, 1)
        self.assertEqual([f['code'] for f in result['findings']], ['missing-image-alt'])

    def test_escaped_markdown_does_not_become_link(self):
        result, status = self.check('# Title\n\n\\[bad](missing.md)\n')
        self.assertEqual(status, 0, result)

    def test_balanced_parentheses_and_angle_destination(self):
        result, status = self.check('# Title\n\n[one](docs/a(b).md)\n[two](<docs/space name.md> "Title")\n', {'docs/a(b).md': '# A\n', 'docs/space name.md': '# Space\n'})
        self.assertEqual(status, 0, result)

    def test_framework_mdx_remote_query_extensionless_are_unresolved(self):
        result, status = self.check('# Title\n\n[route](/guide)\n[query](README.md?q=1)\n[extless](guide)\n[web](https://example.com#x)\n[mdx](guide.mdx#hi)\n', {'guide.mdx': 'export const X = 1\n'})
        self.assertEqual(status, 0, result)
        self.assertTrue({'framework-route-or-query', 'extensionless-route', 'remote-or-scheme-link', 'unsupported-fragment', 'mdx-requires-renderer'} <= self.unresolved(result))

    def test_html_custom_anchors_do_not_cause_false_missing_anchor(self):
        result, status = self.check('# Title\n\n<a id="custom"></a>\n[custom](#custom)\n')
        self.assertEqual(status, 0, result)
        self.assertIn('custom-renderer-fragment', self.unresolved(result))

    def test_heading_hierarchy_is_warning(self):
        result, status = self.check('# Title\n\n### Deep\n')
        self.assertEqual(status, 0)
        self.assertEqual(result['findings'][0]['severity'], 'warning')

    def test_root_escape_and_sensitive_links_are_errors(self):
        result, status = self.check('# Title\n\n[out](../outside.md)\n[secret](.env)\n[win](C:\\secret.md)\n[unc](\\\\server\\secret.md)\n')
        self.assertEqual(status, 1)
        self.assertEqual(self.codes(result), {'excluded-destination', 'outside-root'})

    def test_sensitive_and_vendor_targets_are_not_read(self):
        result, status = self.check('# Title\n\n[secret](.env)\n[vendor](node_modules/pkg/README.md#x)\n[escape](../outside)\n', {'.env': 'PRIVATE', 'node_modules/pkg/README.md': '# X\n'})
        self.assertEqual(status, 1)
        self.assertEqual(len(result['findings']), 3)
        self.assertEqual(self.codes(result), {'excluded-destination'})
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_encoded_escape_and_null(self):
        result, status = self.check('# Title\n\n[out](%2e%2e/outside.md)\n[null](file%00.md)\n')
        self.assertEqual(status, 1)
        self.assertEqual(self.codes(result), {'excluded-destination', 'invalid-destination'})

    def test_symlink_target_is_excluded(self):
        outside = Path(self.temp.name).parent / (Path(self.temp.name).name + '-secret.md')
        outside.write_text('never read', encoding='utf-8')
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        (self.root/'link.md').symlink_to(outside)
        result, status = self.check('# Title\n\n[link](link.md)\n')
        self.assertEqual(status, 1)
        self.assertIn('excluded-destination', self.codes(result))

    def test_bad_utf8_and_oversized_documents_return_read_failure(self):
        (self.root/'bad.md').write_bytes(b'\xff')
        result, status = docs_check.run(self.root, None, 5000)
        self.assertEqual(status, 2)
        self.assertTrue(result['failures'])
        (self.root/'bad.md').write_bytes(b'a' * 1_048_577)
        result, status = docs_check.run(self.root, None, 5000)
        self.assertEqual(status, 2)

    def test_bounded_inventory_and_missing_flags(self):
        for i in range(8):
            self.write(f'{i}.md', '# Title\n')
        files, stats = inventory(self.root, 2)
        self.assertTrue(stats['truncated'])
        self.assertLessEqual(len(files), 2)
        result, status = repo_inspect.inspect(self.root, 2)
        self.assertEqual(status, 0)
        self.assertTrue(result['limits']['truncated'])

    def test_inspect_stack_detection_nested_manifests_and_no_script_bodies(self):
        self.write('package.json', json.dumps({'name': 'demo', 'scripts': {'docs:build': 'DO-NOT-PRINT-SECRET'}, 'dependencies': {'@astrojs/starlight': '^0.1.0'}}))
        self.write('docs/package.json', json.dumps({'devDependencies': {'vitepress': '^1.0.0'}}))
        self.write('docs/.vitepress/config.ts', 'DO-NOT-PRINT-CONFIG')
        self.write('README.md', '# DO-NOT-PRINT-README\n')
        self.write('.env', 'DO-NOT-PRINT-ENV')
        self.write('node_modules/private/package.json', '{invalid')
        result, status = repo_inspect.inspect(self.root)
        self.assertEqual(status, 0)
        self.assertEqual({s['name'] for s in result['stacks']}, {'starlight', 'vitepress'})
        self.assertFalse(result['missing']['readme'])
        self.assertNotIn('DO-NOT-PRINT', json.dumps(result))
        self.assertEqual(result['manifests'][0]['script_names'] if result['manifests'][0]['path'] == 'package.json' else result['manifests'][1]['script_names'], ['docs:build'])

    def test_invalid_manifest_and_invalid_root_are_failures(self):
        self.write('package.json', '{')
        result, status = repo_inspect.inspect(self.root)
        self.assertEqual(status, 2)
        with self.assertRaises(InputFailure):
            root_path(str(self.root/'missing'))
        with self.assertRaises(InputFailure):
            contained(self.root, self.root/'..'/'outside.md')

    def test_cli_exit_codes_and_read_only(self):
        readme = self.write('README.md', '# Title\n\n[bad](missing.md)\n')
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        run = subprocess.run([sys.executable, str(SCRIPTS/'docs_check.py'), '--root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)['status'], 'errors')
        invalid = subprocess.run([sys.executable, str(SCRIPTS/'docs_check.py'), '--root', str(self.root), '--path', '../outside.md'], capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

if __name__ == '__main__':
    unittest.main()
