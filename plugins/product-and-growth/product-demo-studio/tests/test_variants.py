"""Campaign timing, portable output and interrupted-publication regressions."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / 'scripts'))
import variants


class VariantSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = self.root / 'source'
        shutil.copytree(PLUGIN / 'examples/tandem', self.base, ignore=shutil.ignore_patterns('campaign-jobs'))
        self.job = json.loads((self.base / 'promo-vertical.json').read_text())
        self.manifest = json.loads((self.base / 'experiment-manifest.json').read_text())
        self.manifest['experiments'] = self.manifest['experiments'][:1]
        self.out = self.root / 'jobs'

    def materialize(self):
        return variants.materialize(self.job, self.base, self.manifest, self.out, use='video')

    def result(self):
        return json.loads((self.out / (self.manifest['experiments'][0]['id'] + '.json')).read_text())

    def with_audio(self, role='narration'):
        self.job['audio'] = [{'path': 'score.wav', 'role': role, 'gainDb': 0, 'start': 0,
                              'duration': 12, 'rightsId': 'tandem-original'}]

    def test_success_is_an_independent_portable_project(self):
        original = copy.deepcopy(self.job)
        rows = self.materialize()
        self.assertEqual(len(rows), 1)
        self.assertEqual(self.result()['captions'], self.job['captions'])
        self.assertEqual(self.job, original)
        self.assertEqual((self.out / 'fixture/product.js').read_bytes(), (self.base / 'fixture/product.js').read_bytes())
        self.assertTrue((self.out / 'capture/result.png').is_file())
        self.assertEqual(json.loads((self.out / 'render-jobs.json').read_text()), rows)
        self.assertEqual(list(self.root.glob('.pds-variants-*')), [])

    def test_local_evidence_sources_are_copied_without_requiring_source_hash_entries(self):
        evidence_path = self.base / self.job['evidence']
        evidence = json.loads(evidence_path.read_text())
        proof = self.base / 'review-notes.txt'
        proof.write_text('Local source evidence')
        evidence['claims'][0]['sources'].append({'type': 'documentation', 'path': proof.name})
        evidence_path.write_text(json.dumps(evidence))
        self.materialize()
        self.assertEqual((self.out / proof.name).read_text(), 'Local source evidence')

    def test_symlink_source_escape_is_rejected_before_output(self):
        external = self.root / 'outside.ttf'
        external.write_text('Do not copy')
        link = self.base / 'outside.ttf'
        try:
            link.symlink_to(external)
        except OSError:
            self.skipTest('Host cannot create symlinks')
        self.job['font'] = link.name
        with self.assertRaisesRegex(ValueError, 'escapes|invalid'):
            self.materialize()
        self.assertFalse(self.out.exists())

    def test_existing_empty_directory_is_published(self):
        self.out.mkdir()
        self.materialize()
        self.assertTrue((self.out / 'render-jobs.json').is_file())

    def test_populated_directory_is_preserved(self):
        self.out.mkdir()
        sentinel = self.out / 'notes.txt'
        sentinel.write_text('Keep this')
        with self.assertRaisesRegex(ValueError, 'empty directory'):
            self.materialize()
        self.assertEqual(sentinel.read_text(), 'Keep this')
        self.assertEqual(list(self.out.iterdir()), [sentinel])

    def test_output_symlink_and_symlink_ancestor_are_rejected(self):
        external = self.root / 'external'
        external.mkdir()
        for target in [self.out, self.root / 'linked-parent']:
            try:
                target.symlink_to(external, target_is_directory=True)
            except OSError:
                self.skipTest('Host cannot create symlinks')
            self.out = target if target.name == 'jobs' else target / 'jobs'
            with self.assertRaisesRegex(ValueError, 'symlink'):
                self.materialize()
        self.assertEqual(list(external.iterdir()), [])

    def test_source_cannot_be_output(self):
        self.out = self.base
        with self.assertRaisesRegex(ValueError, 'differ from the source'):
            self.materialize()

    def test_audio_duration_changes_require_authored_jobs(self):
        for role in ['narration', 'music', 'sfx']:
            for duration in [6, 18]:
                with self.subTest(role=role, duration=duration):
                    self.with_audio(role)
                    self.manifest['experiments'][0]['duration'] = duration
                    with self.assertRaisesRegex(ValueError, 'Cannot automatically change duration with audio'):
                        self.materialize()
                    self.assertFalse(self.out.exists())

    def test_preserved_source_audio_duration_change_is_rejected(self):
        self.job.update(renderer='footage', visualMode='recorded', source={
            'path': 'capture/tandem-workflow.webm', 'start': 0, 'audioPolicy': 'preserve'})
        self.manifest['experiments'][0]['duration'] = 6
        with self.assertRaisesRegex(ValueError, 'Cannot automatically change duration with audio'):
            self.materialize()
        self.assertFalse(self.out.exists())

    def test_unchanged_audio_timing_is_preserved(self):
        self.with_audio()
        self.materialize()
        self.assertEqual(self.result()['audio'], self.job['audio'])
        self.assertEqual(self.result()['captions'], self.job['captions'])

    def test_silent_variant_scales_captions_and_review_points_and_rebinds_config(self):
        self.job['reviewPoints'] = [{'time': 9, 'label': 'Proof'}]
        self.job['configHash'] = hashlib.sha256(json.dumps(self.job, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        self.manifest['experiments'][0]['duration'] = 6
        self.materialize()
        result = self.result()
        self.assertEqual(result['captions'][0]['start'], 0.25)
        self.assertEqual(result['captions'][0]['end'], 1.35)
        self.assertEqual(result['reviewPoints'], [{'time': 4.5, 'label': 'Proof'}])
        payload = {key: value for key, value in result.items() if key != 'configHash'}
        self.assertEqual(result['configHash'], hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest())
        self.assertNotEqual(result['configHash'], self.job['configHash'])

    def test_reserved_and_asset_job_filename_collisions_fail_before_writing(self):
        self.manifest['experiments'][0]['id'] = 'render-jobs'
        with self.assertRaisesRegex(ValueError, 'filename collision'):
            self.materialize()
        self.assertFalse(self.out.exists())
        self.manifest['experiments'][0]['id'] = 'one-job'
        self.job['font'] = 'one-job.json'
        (self.base / 'one-job.json').write_text('A supplied asset')
        with self.assertRaisesRegex(ValueError, 'filename collision'):
            self.materialize()
        self.assertFalse(self.out.exists())

    def test_case_insensitive_and_file_directory_collisions_fail(self):
        self.job['font'] = 'RENDER-JOBS.JSON'
        (self.base / self.job['font']).write_text('An asset')
        with self.assertRaisesRegex(ValueError, 'filename collision'):
            self.materialize()
        self.job['font'] = 'render-jobs.json/font.ttf'
        (self.base / 'render-jobs.json').mkdir()
        (self.base / self.job['font']).write_text('An asset')
        with self.assertRaisesRegex(ValueError, 'file/directory collision'):
            self.materialize()
        self.assertFalse(self.out.exists())

    def test_copy_failure_leaves_absent_or_empty_output_and_no_partial_files(self):
        for existing in [False, True]:
            with self.subTest(existing=existing):
                if existing:
                    self.out.mkdir()
                with patch.object(variants.shutil, 'copy2', side_effect=OSError('disk full')):
                    with self.assertRaisesRegex(OSError, 'disk full'):
                        self.materialize()
                self.assertEqual(self.out.exists(), existing)
                if existing:
                    self.assertEqual(list(self.out.iterdir()), [])
                    self.out.rmdir()
                self.assertEqual(list(self.root.glob('.pds-variants-*')), [])

    def test_publication_failure_restores_existing_empty_output(self):
        self.out.mkdir()
        with patch.object(variants.Path, 'rename', side_effect=OSError('rename denied')):
            with self.assertRaisesRegex(OSError, 'rename denied'):
                self.materialize()
        self.assertTrue(self.out.is_dir())
        self.assertEqual(list(self.out.iterdir()), [])
        self.assertEqual(list(self.root.glob('.pds-variants-*')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
