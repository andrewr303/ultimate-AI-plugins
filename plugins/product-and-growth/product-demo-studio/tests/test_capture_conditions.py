"""Declarative readiness validation and real-browser capture receipts."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("capture_conditions", ROOT / "scripts" / "capture.py")
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)


def job(url="http://127.0.0.1:8000"):
    return {"schemaVersion": "1.0.0", "id": "readiness", "productRevision": "fixture-1", "baseUrl": url,
            "viewport": {"width": 640, "height": 480, "deviceScaleFactor": 1}, "outputDir": "capture",
            "mode": "actual", "syntheticData": True, "claims": [],
            "steps": [{"id": "ready", "action": "wait-for", "selector": "#result", "timeoutMs": 1000},
                      {"id": "result", "action": "screenshot", "path": "capture/result.png"}]}


class ReadinessContractTests(unittest.TestCase):
    def test_supported_conditions_and_legacy_wait(self):
        schema = json.loads((ROOT / "contracts" / "schemas" / "capture-job.schema.json").read_text())
        for condition in [None, {"type": "state", "state": "hidden"},
                          {"type": "text", "value": ""},
                          {"type": "attribute", "name": "aria-busy", "value": "false"}]:
            with self.subTest(condition=condition):
                doc = job()
                if condition is not None:
                    doc["steps"][0]["condition"] = condition
                capture.validate_job(doc)
                self.assertEqual(list(Draft202012Validator(schema).iter_errors(doc)), [])

    def test_invalid_condition_shapes_fail_runner_and_schema(self):
        schema = json.loads((ROOT / "contracts" / "schemas" / "capture-job.schema.json").read_text())
        cases = [None, {}, [], {"type": "evaluate", "value": "window.ready"},
                 {"type": "state", "state": "enabled"}, {"type": "state", "state": "hidden", "value": "x"},
                 {"type": "text"}, {"type": "text", "value": 1},
                 {"type": "text", "value": "x" * 10001}, {"type": "text", "value": "x", "regex": True},
                 {"type": "attribute", "name": "data-state"},
                 {"type": "attribute", "name": "bad name", "value": "ready"},
                 {"type": "attribute", "name": "data-state\n", "value": "ready"},
                 {"type": "attribute", "name": "a" * 201, "value": "ready"}]
        for condition in cases:
            with self.subTest(condition=repr(condition)[:100]):
                doc = job()
                doc["steps"][0]["condition"] = condition
                with self.assertRaises(capture.CaptureError):
                    capture.validate_job(doc)
                self.assertTrue(list(Draft202012Validator(schema).iter_errors(doc)))

    def test_conditions_cannot_be_attached_to_other_actions(self):
        schema = json.loads((ROOT / "contracts" / "schemas" / "capture-job.schema.json").read_text())
        for action in sorted(capture.ACTIONS - {"wait-for"}):
            with self.subTest(action=action):
                doc = job()
                doc["steps"][0].update(action=action, condition={"type": "text", "value": "Ready"})
                with self.assertRaisesRegex(capture.CaptureError, "only supported on wait-for"):
                    capture.validate_job(doc)
                self.assertTrue(list(Draft202012Validator(schema).iter_errors(doc)))


PAGE = b"""<!doctype html><title>Readiness fixture</title>
<button id="run" onclick="setTimeout(()=>document.querySelector('#result').textContent='Ready private-example',150);
setTimeout(()=>document.querySelector('#result').setAttribute('data-state','complete-private'),300);
setTimeout(()=>document.querySelector('#busy').hidden=true,450)">Run</button>
<p id="result" data-state="stale-private">Stale private-example</p><p id="busy">Processing</p>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, *args):
        pass


@unittest.skipUnless(importlib.util.find_spec("playwright") and capture.choose_browser(),
                     "Playwright and a system Chromium are required for browser readiness tests")
class BrowserReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_delayed_text_attribute_and_hidden_conditions_and_private_receipt(self):
        doc = job(self.url)
        doc["steps"] = [
            {"id": "run", "action": "click", "selector": "#run"},
            {"id": "text", "action": "wait-for", "selector": "#result", "timeoutMs": 2000,
             "condition": {"type": "text", "value": "Ready private-example"}},
            {"id": "attribute", "action": "wait-for", "selector": "#result", "timeoutMs": 2000,
             "condition": {"type": "attribute", "name": "data-state", "value": "complete-private"}},
            {"id": "hidden", "action": "wait-for", "selector": "#busy", "timeoutMs": 2000,
             "condition": {"type": "state", "state": "hidden"}},
            {"id": "result", "action": "screenshot", "path": "capture/result.png"}]
        with tempfile.TemporaryDirectory() as directory:
            manifest, path = capture.run_capture(doc, directory)
            self.assertTrue(path.is_file())
            self.assertEqual(len(manifest["assets"]), 1)
            raw = (Path(directory) / "capture" / "capture-report.json").read_text()
            report = json.loads(raw)
            conditions = [item["condition"] for item in report["actions"] if "condition" in item]
            self.assertEqual(conditions, [{"type": kind, "outcome": "passed"} for kind in ("text", "attribute", "state")])
            for private in ("private-example", "data-state", "complete-private", "stale-private"):
                self.assertNotIn(private, raw)

    def test_text_and_attribute_mismatches_fail_without_leaking_assertion_contents(self):
        for condition in [{"type": "text", "value": "expected-private"},
                          {"type": "attribute", "name": "data-state", "value": "expected-private"}]:
            with self.subTest(condition=condition["type"]), tempfile.TemporaryDirectory() as directory:
                doc = job(self.url)
                doc["steps"][0].update(condition=condition, timeoutMs=100)
                with self.assertRaisesRegex(capture.CaptureError, "condition was not satisfied within 100 ms") as raised:
                    capture.run_capture(doc, directory)
                raw = (Path(directory) / "capture" / "capture-report.json").read_text()
                self.assertEqual(json.loads(raw)["actions"][-1]["condition"],
                                 {"type": condition["type"], "outcome": "failed"})
                self.assertFalse((Path(directory) / "capture-manifest.json").exists())
                self.assertFalse((Path(directory) / "capture" / "result.png").exists())
                for private in ("expected-private", "Stale private-example", "data-state", "stale-private"):
                    self.assertNotIn(private, raw + str(raised.exception))

    def test_legacy_visibility_and_reading_hold_remain_supported(self):
        doc = job(self.url)
        doc["steps"][0]["holdMs"] = 100
        with tempfile.TemporaryDirectory() as directory:
            capture.run_capture(doc, directory)
            report = json.loads((Path(directory) / "capture" / "capture-report.json").read_text())
            self.assertEqual(report["actions"][0]["condition"], {"type": "state", "outcome": "passed"})


if __name__ == "__main__":
    unittest.main()
