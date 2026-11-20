"""Portable behavior checks for the packaged read-only evidence collector."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("inspect_project.py")
SPEC = importlib.util.spec_from_file_location("inspect_project", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InspectProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def test_actual_node_and_extension_evidence_without_values_or_execution(self):
        package = {"scripts": {"start": "node -e 'throw Error(42)'", "test": "SECRET_COMMAND"},
                   "dependencies": {"react": "18", "electron": "40", "private-token": "SECRET"},
                   "workspaces": ["packages/*"]}
        self.write("package.json", json.dumps(package))
        self.write("extension/manifest.json", json.dumps({"manifest_version": 3,
                   "name": "Clipper", "background": {"service_worker": "worker.js"},
                   "permissions": ["nativeMessaging", "activeTab"]}))
        result = MODULE.inspect(self.root)
        self.assertTrue(result["complete"])
        by_kind = {row["kind"]: row for row in result["evidence"]}
        self.assertEqual(by_kind["node-package"], {"path": "package.json", "kind": "node-package",
                         "script_names": ["start", "test"], "frameworks": ["electron", "react"],
                         "has_workspaces": True})
        self.assertEqual(by_kind["browser-extension"], {"path": "extension/manifest.json",
                         "kind": "browser-extension", "manifest_version": 3,
                         "has_background": True, "native_messaging": True})
        self.assertNotIn("SECRET", json.dumps(result))
        self.assertEqual(result["warnings"], [])

    def test_skips_dependencies_hidden_paths_and_symlinks(self):
        self.write("node_modules/fake/package.json", "{broken")
        self.write("vendor/manifest.json", "{broken")
        self.write(".hidden/package.json", "{broken")
        self.write("real/Package.swift", "// evidence marker only")
        try:
            (self.root / "linked-file.json").symlink_to(self.root / "real/Package.swift")
            (self.root / "loop").symlink_to(self.root, target_is_directory=True)
            (self.root / "manifest.json").symlink_to(self.root / "node_modules/fake/package.json")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this platform")
        result = MODULE.inspect(self.root)
        self.assertEqual(result["evidence"], [{"path": "real/Package.swift", "kind": "swift-package"}])
        self.assertEqual(result["warnings"], [])
        self.assertLess(result["visited_entries"], 15)

    def test_invalid_nonobject_and_oversize_json_warn_and_continue(self):
        self.write("bad/package.json", "{")
        self.write("array/package.json", "[]")
        self.write("large/package.json", " " * (512 * 1024 + 1))
        self.write("ok/Package.swift", "")
        result = MODULE.inspect(self.root)
        self.assertEqual(result["evidence"], [{"path": "ok/Package.swift", "kind": "swift-package"}])
        self.assertEqual(len(result["warnings"]), 3)
        self.assertTrue(any("JSON exceeds size limit" in x for x in result["warnings"]))
        self.assertTrue(any("JSONDecodeError" in x for x in result["warnings"]))
        self.assertTrue(any("ValueError" in x for x in result["warnings"]))

    def test_deeply_nested_untrusted_json_warns_instead_of_crashing(self):
        self.write("package.json", "[" * 20000 + "0" + "]" * 20000)
        result = MODULE.inspect(self.root)
        self.assertEqual(result["evidence"], [])
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("RecursionError", result["warnings"][0])

    def test_entry_budget_stops_and_reports_incomplete(self):
        for index in range(8):
            self.write(f"file-{index}", "")
        result = MODULE.inspect(self.root, budget=3)
        self.assertFalse(result["complete"])
        self.assertEqual(result["visited_entries"], 4)
        self.assertTrue(any("entry budget reached" in x for x in result["warnings"]))

    def test_depth_budget_and_invalid_root(self):
        self.write("/".join(["nested"] * 10) + "/Package.swift", "")
        result = MODULE.inspect(self.root)
        self.assertFalse(result["complete"])
        self.assertEqual(result["evidence"], [])
        with self.assertRaisesRegex(ValueError, "existing directory"):
            MODULE.inspect(self.root / "missing")


if __name__ == "__main__":
    unittest.main()
