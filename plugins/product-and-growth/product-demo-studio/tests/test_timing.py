"""Timing contracts: reject unsafe alignment, preserve source media, measure generated audio."""
from __future__ import annotations

from array import array
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "timing.py"
SPEC = importlib.util.spec_from_file_location("studio_timing", SCRIPT)
timing = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(timing)


class CaptionTimingTests(unittest.TestCase):
    def test_multiline_crlf_bom_and_adjacent_cues(self):
        source = "\ufeff1\r\n00:00:00,100 --> 00:00:00,500\r\nFirst line\r\nSecond line\r\n\r\n2\r\n00:00:00,500 --> 00:00:01,000\r\nResult\r\n"
        report = timing.caption_report(source, 1, 24)
        self.assertEqual(report["captions"][0], {"start": .1, "end": .5, "text": "First line\nSecond line"})
        self.assertEqual(report["frameMap"][0]["firstFrame"], 3)
        self.assertEqual(report["frameMap"][0]["endFrameExclusive"], 12)
        self.assertEqual(report["frameMap"][1]["firstFrame"], 12)
        self.assertEqual(report["totalFramesCoveringDuration"], 24)

    def test_overlap_and_unordered_times_rejected(self):
        for next_times in ("00:00:00,400 --> 00:00:00,800", "00:00:00,000 --> 00:00:00,100"):
            with self.subTest(next_times=next_times), self.assertRaisesRegex(ValueError, "unordered or overlaps"):
                timing.caption_report("1\n00:00:00,200 --> 00:00:00,500\nOne\n\n2\n" + next_times + "\nTwo", 1)

    def test_invalid_boundaries_rejected(self):
        bad = [
            ("00:00:01,000 --> 00:00:01,000", "end must be after"),
            ("00:00:01,000 --> 00:00:02,000", "declared duration"),
            ("00:60:00,000 --> 01:00:01,000", "invalid minute"),
            ("00:00:00,001 --> 00:00:00,002", "shorter than"),
        ]
        for times, message in bad:
            with self.subTest(times=times), self.assertRaisesRegex(ValueError, message):
                timing.caption_report("1\n" + times + "\nWords", 1)

    def test_duplicate_ids_and_unknown_placement_rejected(self):
        with self.assertRaisesRegex(ValueError, "indices must increase"):
            timing.caption_report("1\n00:00:00,000 --> 00:00:00,500\nA\n\n1\n00:00:00,500 --> 00:00:01,000\nB", 1)
        with self.assertRaisesRegex(ValueError, "placement settings"):
            timing.caption_report("1\n00:00:00,000 --> 00:00:00,500 X1:20\nWords", 1)

    def test_empty_caption_and_empty_document_rejected(self):
        for source in ("", "1\n00:00:00,000 --> 00:00:00,500\n "):
            with self.subTest(source=source), self.assertRaises(ValueError):
                timing.caption_report(source, 1)

    def test_frame_rounding_has_exclusive_end_and_handles_float_noise(self):
        self.assertEqual(timing.frame_boundary(.1, 24), 3)
        self.assertEqual(timing.frame_boundary(Fraction(1, 24), 24), 1)
        self.assertEqual(timing.frame_boundary(.04166666666666667, 24), 1)
        self.assertEqual(timing.frame_boundary(.041668, 24), 2)
        self.assertEqual(timing.frame_boundary(1.001, 24), 25)


class WordTimingTests(unittest.TestCase):
    def test_supplied_words_source_and_pause_map_preserved(self):
        payload = {"source": {"kind": "human-marked", "audioSha256": "a" * 64},
                   "words": [{"start": .1, "end": .3, "word": "Open"},
                             {"start": .5, "end": .8, "text": "Tandem."}]}
        report = timing.word_report(payload, 1, 24)
        self.assertEqual(report["declaredSource"], payload["source"])
        self.assertEqual(report["words"][0]["text"], "Open")
        self.assertEqual(report["pauseWindows"][0]["duration"], .2)
        self.assertEqual(report["timingAuthority"], "supplied-word-timestamps")
        self.assertTrue(any("not independently verified" in text for text in report["warnings"]))

    def test_short_word_is_retained_as_subframe_not_invented_alignment(self):
        report = timing.word_report([{"start": .01, "end": .02, "text": "a"}], 1, 24)
        self.assertEqual(report["words"], [{"start": .01, "end": .02, "text": "a"}])
        self.assertTrue(report["frameMap"][0]["subframe"])
        self.assertEqual(report["frameMap"][0]["frameCount"], 0)

    def test_invalid_word_timing_rejected(self):
        cases = [
            [{"start": -.1, "end": .2, "text": "negative"}],
            [{"start": 0, "end": 1.1, "text": "outside"}],
            [{"start": 0, "end": .5, "text": "first"}, {"start": .4, "end": .7, "text": "overlap"}],
            [{"start": True, "end": .2, "text": "boolean"}],
            [{"start": "0.1", "end": .2, "text": "string"}],
            [{"start": float("nan"), "end": .2, "text": "nan"}],
            [{"start": 0, "end": .2, "text": "one", "word": "two"}],
        ]
        for entries in cases:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                timing.word_report(entries, 1)

    def test_duration_fps_and_missing_words_rejected(self):
        for payload, duration, fps in [([], 1, 24), ({}, 1, 24), ([], 0, 24), ([], 1, 0), ([], 1, 240)]:
            with self.subTest(payload=payload, duration=duration, fps=fps), self.assertRaises(ValueError):
                timing.word_report(payload, duration, fps)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg and ffprobe unavailable")
class AudioMeasurementTests(unittest.TestCase):
    @staticmethod
    def fixture(path, mode, duration=4.5):
        rate = 22050
        samples = array("h")
        for index in range(round(duration * rate)):
            seconds = index / rate
            if mode == "silence":
                value = 0
            else:
                value = .05 * math.sin(2 * math.pi * 440 * seconds)
                if mode == "transients":
                    # Original damped impulses on a half-second grid; no copied music.
                    phase = seconds % .5
                    if seconds >= .5 and phase < .04:
                        value += .65 * math.exp(-phase * 95) * math.cos(2 * math.pi * 800 * phase)
            samples.append(max(-32768, min(32767, round(value * 32767))))
        if sys.byteorder != "little":
            samples.byteswap()
        with wave.open(str(path), "wb") as target:
            target.setnchannels(1)
            target.setsampwidth(2)
            target.setframerate(rate)
            target.writeframes(samples.tobytes())

    def test_generated_transient_grid_measured_and_input_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transients.wav"
            self.fixture(path, "transients")
            before = path.read_bytes()
            report = timing.analyze_audio(path, 24)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(before).hexdigest())
            self.assertAlmostEqual(report["duration"], 4.5, places=4)
            self.assertEqual(report["totalFramesCoveringDuration"], 108)
            self.assertIsNotNone(report["loudness"]["integratedLufs"])
            self.assertIsNotNone(report["loudness"]["truePeakDbtp"])
            self.assertAlmostEqual(report["beatAnalysis"]["candidateBpm"], 120, delta=4)
            self.assertGreaterEqual(report["beatAnalysis"]["confidence"], .6)
            self.assertTrue(any(abs(item["time"] - 1.5) <= .04 for item in report["onsetCandidates"]))
            self.assertTrue(report["envelope"])

    def test_steady_sine_does_not_gain_fabricated_beat_grid(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sine.wav"
            self.fixture(path, "sine", 1.2)
            report = timing.analyze_audio(path)
            self.assertIsNone(report["beatAnalysis"]["candidateBpm"])
            self.assertEqual(report["beatAnalysis"]["beatCandidates"], [])

    def test_silence_reports_no_bpm_and_no_meaningful_loudness(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "silence.wav"
            self.fixture(path, "silence", .5)
            report = timing.analyze_audio(path)
            self.assertIsNone(report["beatAnalysis"]["candidateBpm"])
            self.assertFalse(report["loudness"]["measurementMeaningful"])
            self.assertIsNone(report["decodedMono"]["peakDbfs"])
            self.assertIsNone(report["loudness"]["truePeakDbtp"])


class CliSafetyTests(unittest.TestCase):
    def test_source_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json"
            path.write_text("[]")
            with self.assertRaisesRegex(ValueError, "never overwritten"):
                timing.write_report(path, {"new": "report"}, path)
            self.assertEqual(path.read_text(), "[]")

    def test_valid_cli_output_is_atomic_portable_and_caption_schema_compatible(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "my captions.srt"
            output = Path(directory) / "reports" / "captions.json"
            source.write_text("1\n00:00:00,000 --> 00:00:00,500\nTry the workflow.\n")
            result = subprocess.run([sys.executable, str(SCRIPT), "captions", "--input", str(source),
                                     "--output", str(output), "--duration", "1", "--fps", "24"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text())
            self.assertEqual(set(report["captions"][0]), {"start", "end", "text"})
            self.assertNotIn(str(Path(directory)), output.read_text())
            self.assertFalse(list(output.parent.glob(".timing-*")))

    def test_nonfinite_json_rejected_and_no_report_written(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "words.json"
            output = Path(directory) / "result.json"
            source.write_text('[{"start": NaN, "end": 0.5, "text": "bad"}]')
            result = subprocess.run([sys.executable, str(SCRIPT), "words", "--input", str(source),
                                     "--output", str(output), "--duration", "1"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("non-finite", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
