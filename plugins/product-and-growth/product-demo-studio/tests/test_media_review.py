"""Authored review points and caption boundaries bind to decoded final frames."""
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / 'scripts'))
import media


class ReviewSampling(unittest.TestCase):
    def test_authored_off_grid_points_merge_on_presented_frame(self):
        samples = media.review_samples(3, 12, 36, {'reviewPoints': [
            {'time': 1.04, 'label': 'Result ready'},
            {'time': 1.08, 'label': 'Read the result'},
            {'time': 2.999, 'label': 'CTA hold'},
        ]})
        by_frame = {sample['frame']: sample for sample in samples}
        self.assertEqual(by_frame[12]['time'], 1)
        self.assertEqual(by_frame[12]['labels'], ['Result ready', 'Read the result'])
        self.assertIn('CTA hold', by_frame[35]['labels'])
        self.assertEqual([sample['frame'] for sample in samples], [0, 9, 12, 18, 27, 35])

    def test_non_grid_caption_boundaries_include_neighbours_and_midpoint(self):
        samples = media.review_samples(3, 12, 36, {'captions': [
            {'start': 1.01, 'end': 1.98, 'text': 'A caption'},
        ]})
        by_frame = {sample['frame']: sample for sample in samples}
        self.assertIn('caption-1:before-start', by_frame[12]['labels'])
        self.assertIn('caption-1:start', by_frame[13]['labels'])
        self.assertIn('caption-1:after-start', by_frame[14]['labels'])
        self.assertIn('caption-1:midpoint', by_frame[17]['labels'])
        self.assertIn('caption-1:before-end', by_frame[23]['labels'])
        self.assertIn('caption-1:end', by_frame[24]['labels'])
        self.assertIn('caption-1:after-end', by_frame[25]['labels'])

    def test_one_frame_clip_deduplicates_and_has_no_unavailable_caption_neighbours(self):
        samples = media.review_samples(.05, 20, 1, {'captions': [
            {'start': 0, 'end': .05, 'text': 'One frame'},
        ]})
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0]['frame'], 0)
        self.assertIn('opening', samples[0]['labels'])
        self.assertIn('ending', samples[0]['labels'])
        self.assertNotIn('caption-1:end', samples[0]['labels'])
        self.assertNotIn('caption-1:before-start', samples[0]['labels'])

    def test_invalid_review_inputs_fail_before_extraction(self):
        invalid = [
            {'time': -1, 'label': 'Wrong'}, {'time': 3, 'label': 'End is outside'},
            {'time': math.nan, 'label': 'Not a time'}, {'time': math.inf, 'label': 'Infinite'},
            {'time': True, 'label': 'Boolean'}, {'time': 1, 'label': ' '},
            {'time': 1, 'label': 'x' * 81}, {'time': 1, 'label': 'Wrong keys', 'path': '../out'},
        ]
        for point in invalid:
            with self.subTest(point=point), self.assertRaises(ValueError):
                media.review_samples(3, 12, 36, {'reviewPoints': [point]})
        for duration, fps, frames in [(0, 12, 1), (3, 0, 36), (math.nan, 12, 36), (3, 12, 0)]:
            with self.subTest(parameters=(duration, fps, frames)), self.assertRaises(ValueError):
                media.review_samples(duration, fps, frames)

    def test_sample_budget_rejects_rather_than_dropping_required_frames(self):
        captions = [{'start': .1 + i * 1.7, 'end': .6 + i * 1.7, 'text': str(i)} for i in range(100)]
        with self.assertRaisesRegex(ValueError, 'exceeds 512'):
            media.review_samples(180, 60, 10800, {'captions': captions})


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg and ffprobe required')
class EncodedReview(unittest.TestCase):
    def test_exact_decoded_colours_and_cli_job_review_points(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            colours = [(240, 40, 40), (40, 220, 40), (40, 40, 240)]
            for frame in range(12):
                Image.new('RGB', (96, 64), colours[frame // 4]).save(root / f'{frame:03d}.png')
            video = root / 'video.mp4'
            media.run(['ffmpeg', '-v', 'error', '-framerate', '12', '-i', root / '%03d.png',
                       '-frames:v', '12', '-c:v', 'libx264', '-crf', '0', '-pix_fmt', 'yuv420p', '-y', video])
            job = {'width': 96, 'height': 64, 'fps': 12, 'duration': 1, 'audio': [],
                   'reviewPoints': [{'time': 4 / 12, 'label': 'Result <ready> / ../'},
                                    {'time': 8 / 12, 'label': 'CTA'}],
                   'captions': [{'start': 4 / 12, 'end': 8 / 12, 'text': 'Middle scene'}]}
            job_file = root / 'job.json'
            job_file.write_text(json.dumps(job))
            review_dir = root / 'review'
            result = subprocess.run([sys.executable, str(PLUGIN / 'scripts/media.py'), 'inspect', str(video),
                                     '--job', str(job_file), '--review-dir', str(review_dir)],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'passed')
            self.assertEqual(report['visualReview']['status'], 'required')
            by_frame = {item['frame']: item for item in report['reviewFrames']}
            self.assertIn('Result <ready> / ../', by_frame[4]['labels'])
            self.assertIn('caption-1:before-start', by_frame[3]['labels'])
            self.assertIn('caption-1:end', by_frame[8]['labels'])
            for frame, sample in by_frame.items():
                self.assertEqual(sample['time'], frame / 12)
                with Image.open(review_dir / sample['path']) as image:
                    pixel = image.convert('RGB').getpixel((48, 32))
                expected = colours[frame // 4]
                self.assertLess(max(abs(actual - wanted) for actual, wanted in zip(pixel, expected)), 8)
                self.assertEqual(sample['sha256'], media.digest(review_dir / sample['path']))
            self.assertEqual(report['reviewSheets'][0]['path'], 'contact-sheet.jpg')
            self.assertEqual(report['reviewSheets'][0]['sha256'], media.digest(review_dir / 'contact-sheet.jpg'))
            self.assertEqual(len(list(review_dir.glob('*.png'))), len(report['reviewFrames']))
            self.assertFalse(list(review_dir.glob('.review-*')))
            job['reviewPoints'] = [{'time': 1, 'label': 'Outside the clip'}]
            job_file.write_text(json.dumps(job))
            rejected_dir = root / 'rejected-review'
            rejected = subprocess.run([sys.executable, str(PLUGIN / 'scripts/media.py'), 'inspect', str(video),
                                       '--job', str(job_file), '--review-dir', str(rejected_dir)],
                                      text=True, capture_output=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertIn('inside the video duration', json.loads(rejected.stderr)['error'])
            self.assertFalse(rejected_dir.exists())

    def test_many_authored_points_paginate_contact_sheets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=red:s=96x64:r=12:d=3',
                       '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-y', root / 'video.mp4'])
            expected = {'width': 96, 'height': 64, 'fps': 12, 'duration': 3, 'audio': [],
                        'reviewPoints': [{'time': frame / 12, 'label': f'Point {frame}'} for frame in range(32)]}
            report = media.inspect(root / 'video.mp4', expected, root / 'review')
            self.assertEqual(len(report['reviewSheets']), 2)
            self.assertEqual(report['reviewSheets'][1]['path'], 'contact-sheet-002.jpg')
            for sheet in report['reviewSheets']:
                with Image.open(root / 'review' / sheet['path']) as image:
                    self.assertLessEqual(image.height, 420 * 8)


if __name__ == '__main__':
    unittest.main(verbosity=2)
