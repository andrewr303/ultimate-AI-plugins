"""Capture boundary tests; browser workflow is exercised by web.py verify."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import json
import os
import sys

spec = importlib.util.spec_from_file_location("studio_capture", Path(__file__).resolve().parents[1] / "scripts" / "capture.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class CaptureContractTests(unittest.TestCase):
    def job(self):
        return {"schemaVersion": "1.0.0", "id": "tandem-triage", "productRevision": "fixture-1",
                "baseUrl": "http://127.0.0.1:8000/app.html", "viewport": {"width": 1200, "height": 800, "deviceScaleFactor": 1},
                "steps": [{"id": "inbox", "action": "screenshot", "path": "screenshots/inbox.png"}],
                "outputDir": "screenshots", "mode": "actual", "syntheticData": True, "claims": []}

    def test_relative_screenshots_cannot_escape_capture_directory(self):
        for path in ("../private.png", "/tmp/p.png", "sub/../../p.png", "sub\\p.png", "C:/p.png", "./p.png"):
            with self.subTest(path=path), self.assertRaises(capture.CaptureError):
                capture.safe_asset_path(path)
        self.assertEqual(capture.safe_asset_path("screenshots/inbox.png"), "screenshots/inbox.png")

    def test_url_cannot_read_local_files_or_embed_credentials(self):
        for url in ("file:///etc/passwd", "javascript:alert(1)", "http://user:secret@localhost/app", "data:text/html,hi"):
            with self.subTest(url=url), self.assertRaises(capture.CaptureError):
                capture.check_url(url)

    def test_unimplemented_commands_are_rejected_before_browser_launch(self):
        job = self.job()
        job["steps"] = [{"id": "bad", "action": "evaluate", "value": "fetch('https://example.test')"}]
        with self.assertRaisesRegex(capture.CaptureError, "unsupported action"):
            capture.validate_job(job)

    def test_duplicate_output_names_are_not_silently_overwritten(self):
        job = self.job()
        job["steps"] *= 2
        with self.assertRaisesRegex(capture.CaptureError, "duplicate"):
            capture.validate_job(job)

    def test_excessive_resolution_and_wait_are_reported(self):
        job = self.job()
        job["viewport"] = {"width": 7680, "height": 4320, "deviceScaleFactor": 3}
        with self.assertRaisesRegex(capture.CaptureError, "megapixels"):
            capture.validate_job(job)
        job = self.job()
        job["steps"] = [{"id": "wait", "action": "wait-for", "selector": "body", "timeoutMs": 120001}]
        with self.assertRaisesRegex(capture.CaptureError, "120000"):
            capture.validate_job(job)

    def test_typed_content_is_not_in_persisted_step_plan(self):
        # URL query values can contain credentials and must never enter manifest provenance.
        self.assertEqual(capture.display_url("https://example.test/private?token=secret#auth"), "https://example.test/private")

    def test_reading_hold_is_bounded_and_only_follows_a_visible_condition(self):
        job = self.job()
        job['steps'][0]['holdMs'] = 1000
        with self.assertRaisesRegex(capture.CaptureError, 'only supported on wait-for'):
            capture.validate_job(job)
        job = self.job()
        job['steps'].insert(0, {'id':'read','action':'wait-for','selector':'body','holdMs':10001})
        with self.assertRaisesRegex(capture.CaptureError, '10000'):
            capture.validate_job(job)

    def test_missing_browser_is_actionable(self):
        with self.assertRaisesRegex(capture.CaptureError, "browser executable"):
            capture.choose_browser("/no/such/browser")

    def test_missing_revision_and_wrong_schema_are_not_guessed(self):
        job = self.job()
        del job["productRevision"]
        with self.assertRaisesRegex(capture.CaptureError, "productRevision"):
            capture.validate_job(job)
        job = self.job()
        job["schemaVersion"] = "0.2"
        with self.assertRaisesRegex(capture.CaptureError, "schemaVersion"):
            capture.validate_job(job)

    def test_root_handoff_does_not_replace_another_job(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = capture.canonical_manifest_path(root, self.job())
            self.assertEqual(path, root / "capture-manifest.json")
            path.write_text(json.dumps({"id": "another-job"}))
            with self.assertRaisesRegex(capture.CaptureError, "different job"):
                capture.canonical_manifest_path(root, self.job())
            path.write_text(json.dumps({"id": self.job()["id"]}))
            self.assertEqual(capture.canonical_manifest_path(root, self.job()), path)

    def test_studio_browser_precedes_legacy_environment(self):
        # Executable resolution is shared with every capture command; use the
        # running interpreter as an existing path without launching a browser.
        with patch.dict(os.environ, {"STUDIO_BROWSER": sys.executable, "BROWSER_EXECUTABLE": "/missing/legacy"}):
            self.assertEqual(capture.choose_browser(), sys.executable)
        with patch.dict(os.environ, {"STUDIO_BROWSER": "/missing/studio"}):
            self.assertEqual(capture.choose_browser(sys.executable), sys.executable)


if __name__ == "__main__":
    unittest.main()
