"""Regression cases for bibliography structure and citation integrity only."""
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
SPEC = importlib.util.spec_from_file_location('reference_integrity', ROOT / 'scripts/validate_references.py')
refs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refs)


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = [self.source('src_apple', 'Apple'), self.source('src_other', 'Independent publisher')]
        self.save_sources()
        self.write('references/card.md', 'Read src_apple and src_other.\n')
        self.claim = {'claim_id': 'clm_example', 'text': 'A narrow design observation.',
                      'risk': 'normal', 'claim_type': 'descriptive', 'source_ids': ['src_apple', 'src_other'],
                      'review_status': 'manually_supported'}
        self.save_claim()

    def source(self, identity, org):
        return {'id': identity, 'org': org, 'url': 'https://example.invalid/reference',
                'type': 'official_docs', 'quality_rating': 'A'}

    def write(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def save_sources(self):
        return self.write('research/sources/sources.jsonl', ''.join(json.dumps(s) + '\n' for s in self.sources))

    def save_claim(self):
        return self.write('research/artifacts/claim_ledger.jsonl', json.dumps(self.claim) + '\n')

    def test_registered_claim_and_card_citations_preserve_input(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(refs.validate_references(self.root), [])
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_registry_and_unregistered_card_or_claim_ids_fail(self):
        registry = self.save_sources()
        registry.unlink()
        self.assertIn('Missing source registry', '\n'.join(refs.validate_references(self.root)))
        self.save_sources()
        self.write('references/card.md', 'Read src_missing.\n')
        self.claim['source_ids'] = ['src_unknown']
        self.save_claim()
        errors = '\n'.join(refs.validate_references(self.root))
        self.assertIn('src_missing', errors)
        self.assertIn('src_unknown', errors)

    def test_duplicate_records_and_json_keys_fail(self):
        self.sources.append(self.sources[0])
        self.save_sources()
        self.assertIn('Duplicate source id', '\n'.join(refs.validate_references(self.root)))
        self.write('research/sources/sources.jsonl', '{"id":"one","id":"two"}\n')
        self.assertIn('Duplicate JSON key', '\n'.join(refs.validate_references(self.root)))
        self.sources.pop()
        self.save_sources()
        self.write('research/artifacts/claim_ledger.jsonl', (json.dumps(self.claim) + '\n') * 2)
        self.assertIn('Duplicate claim id', '\n'.join(refs.validate_references(self.root)))

    def test_org_case_variants_are_one_underlying_author(self):
        self.sources[1]['org'] = ' apple '
        self.save_sources()
        self.assertIn('case variants count once', '\n'.join(refs.validate_references(self.root)))
        self.claim['review_status'] = 'unresolved'
        self.save_claim()
        self.assertEqual(refs.validate_references(self.root), [])

    def test_malformed_record_types_and_missing_metadata_are_diagnostics(self):
        for value in ([], {'id': 'src_apple', 'quality_rating': 'Z'}, {'id': 1}):
            self.write('research/sources/sources.jsonl', json.dumps(value) + '\n')
            self.assertTrue(refs.validate_references(self.root))
        self.save_sources()
        self.claim['source_ids'] = [None]
        self.save_claim()
        self.assertIn('source_ids', '\n'.join(refs.validate_references(self.root)))

    @unittest.skipUnless(hasattr(os, 'symlink'), 'Symlink support required')
    def test_linked_reference_input_is_rejected(self):
        target = self.root / 'references/card.md'
        linked = self.root / 'references/linked.md'
        linked.symlink_to(target)
        self.assertIn('Symlink', '\n'.join(refs.validate_references(self.root)))

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO support required')
    def test_nonregular_reference_does_not_block(self):
        os.mkfifo(self.root / 'references/blocked.md')
        result = subprocess.run([sys.executable, '-S', str(ROOT / 'scripts/validate_references.py'),
                                 str(self.root), '--json'], capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Nonregular', result.stdout)

    def test_cli_reports_integrity_without_a_factual_verdict(self):
        result = subprocess.run([sys.executable, '-S', str(ROOT / 'scripts/validate_references.py'),
                                 str(self.root), '--json'], capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        self.assertTrue(output['valid'])
        self.assertEqual(output['scope'], 'reference_integrity_only')
        self.assertFalse(output['factual_verification'])


if __name__ == '__main__':
    unittest.main()
