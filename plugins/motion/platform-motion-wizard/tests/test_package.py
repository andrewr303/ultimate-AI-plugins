"""Offline regression checks for this package's validator and ZIP builder."""
from __future__ import annotations

import hashlib
import json
import shutil
import stat
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE_ROOT / "scripts"))
from package_plugin import package_plugin
from validate_plugin import validate_archive, validate_directory


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="motion-package-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.root = self.work / "platform-motion-wizard"
        shutil.copytree(SOURCE_ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))

    def assertRejected(self, fragment):
        result = validate_directory(self.root)
        self.assertFalse(result["ok"], result)
        self.assertIn(fragment, json.dumps(result))

    def change_manifest(self, change):
        path = self.root / "plugin.json"
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def change_first_claim(self, change):
        path = self.root / "research/artifacts/claim_ledger.jsonl"
        claims = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        change(claims[0])
        path.write_text("\n".join(json.dumps(claim) for claim in claims) + "\n")

    def change_scenarios(self, change):
        path = self.root / "tests/skill-scenarios.json"
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def test_valid_complete_package(self):
        result = validate_directory(self.root)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["stats"]["skills"], len(list((self.root / "skills").glob("*/SKILL.md"))))

    def test_original_source_bytes(self):
        expected = {
            "polish-platform-motion/SKILL.md": "472f6743e32a33bf5a4bf9088914dc0803023fd4fc1a3b27dfca9772fa255567",
            "polish-platform-motion/agents/openai.yaml": "b3719b2d3ca3ee9b0ec9ec285f0278ef4c3d5e98b3a91c7e1df198c4f1f54efe",
            "polish-platform-motion/assets/icon.svg": "fbb6c7314886573cd56c3f86884a65afe3b5f4ce4bf1ee6baeeeb1fa50aea7a4",
            "polish-platform-motion/references/image-transcript.md": "343e3d7cece582bcef97e298f9c5496418319270d5d4e31b047b722d665fb6ad",
        }
        manifest = json.loads((self.root / "provenance/original-files.json").read_text())
        self.assertEqual({r["source_path"] for r in manifest["files"]}, set(expected))
        for record in manifest["files"]:
            self.assertEqual(record["sha256"], expected[record["source_path"]])
            raw = (self.root / record["preserved_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record["sha256"])

    def test_skill_name_mismatch(self):
        path = self.root / "skills/motion-review/SKILL.md"
        path.write_text(path.read_text().replace("name: motion-review", "name: mismatched"))
        self.assertRejected("skill name must match")

    def test_broken_local_link(self):
        path = self.root / "references/broken.md"
        path.write_text("[Missing](absent.md)\n")
        self.assertRejected("missing local file")

    def test_broken_anchor(self):
        (self.root / "references/broken.md").write_text("[Missing anchor](performance.md#does-not-exist)\n")
        self.assertRejected("missing local anchor")

    def test_same_file_anchor(self):
        path = self.root / "references/local-anchor.md"
        path.write_text("# Present\n\n[Here](#present)\n")
        self.assertTrue(validate_directory(self.root)["ok"])
        path.write_text("# Present\n\n[Missing](#absent)\n")
        self.assertRejected("missing local anchor")

    def test_links_cannot_escape_root(self):
        (self.work / "outside.md").write_text("# Outside\n")
        (self.root / "references/broken.md").write_text("[Outside](../../outside.md)\n")
        self.assertRejected("reference escapes package")

    def test_example_code_is_not_a_link(self):
        (self.root / "references/code.md").write_text("`[code](missing.md)`\n\n```md\n[example](missing.md)\n```\n")
        self.assertTrue(validate_directory(self.root)["ok"])

    def test_bad_agent_policy(self):
        path = self.root / "skills/motion-review/agents/openai.yaml"
        path.write_text('interface:\n  display_name: Review\n  short_description: Review motion\npolicy:\n  allow_implicit_invocation: "false"\n  products: [chatgpt]\n  permissions: all\n')
        result = validate_directory(self.root)
        messages = json.dumps(result)
        self.assertFalse(result["ok"])
        for expected in ("unknown policy", "must be boolean", "CHAT, CODEX, HERMES"):
            self.assertIn(expected, messages)

    def test_asset_path_is_relative_to_skill(self):
        path = self.root / "skills/motion-review/agents/openai.yaml"
        path.write_text("interface:\n  display_name: Review\n  short_description: Review motion\n  icon_small: assets/missing.svg\n")
        self.assertRejected("missing local file")

    def test_changed_preserved_bytes(self):
        path = self.root / "skills/polish-platform-motion/SKILL.md"
        path.write_bytes(path.read_bytes() + b"\nchanged\n")
        self.assertRejected("preserved bytes changed")

    def test_manifest_schema(self):
        self.change_manifest(lambda data: data.update({"$schema": "https://example.invalid/schema"}))
        self.assertRejected("schema declaration")

    def test_manifest_semver(self):
        self.change_manifest(lambda data: data.update(version="01.2.3"))
        self.assertRejected("strict SemVer")

    def test_metadata_types_report_error_instead_of_crashing(self):
        self.change_manifest(lambda data: data["extensions"]["com.openai"]["interface"].update(category={"wrong": True}))
        self.assertRejected("unsupported interface category")

    def test_subtitle_limit(self):
        self.change_manifest(lambda data: data["extensions"]["com.openai"]["interface"].update(shortDescription="x" * 31))
        self.assertRejected("exceeds 30")

    def test_compatibility_identity(self):
        path = self.root / ".claude-plugin/plugin.json"
        data = json.loads(path.read_text())
        data["version"] = "0.0.1"
        path.write_text(json.dumps(data))
        self.assertRejected("version disagrees")

    def test_unregistered_research_source(self):
        path = self.root / "research/artifacts/claim_ledger.jsonl"
        claims = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        claims[0]["source_ids"] = ["unregistered"]
        path.write_text("\n".join(json.dumps(x) for x in claims) + "\n")
        self.assertRejected("unregistered or missing source_ids")

    def test_malformed_ledger_types_do_not_crash(self):
        path = self.root / "research/sources/sources.jsonl"
        sources = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        sources[0]["quality_rating"] = ["A"]
        sources[0]["org"] = ["wrong-type"]
        path.write_text("\n".join(json.dumps(x) for x in sources) + "\n")
        path = self.root / "research/artifacts/claim_ledger.jsonl"
        claims = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        claims[0]["risk"] = ["normal"]
        claims[0]["source_ids"] = [sources[0]["id"]]
        path.write_text("\n".join(json.dumps(x) for x in claims) + "\n")
        self.assertRejected("invalid quality_rating")

    def test_research_status_is_required_and_typed(self):
        for status in (None, "supported", ["manually_supported"], {"status": "manually_supported"}):
            with self.subTest(status=status):
                self.change_first_claim(lambda claim: claim.update(review_status=status))
                self.assertRejected("invalid or missing review_status")
        self.change_first_claim(lambda claim: claim.pop("review_status"))
        self.assertRejected("invalid or missing review_status")

    def test_numeric_legal_and_causal_claims_require_high_risk(self):
        for claim_type in ("numeric", "legal", "causal"):
            with self.subTest(claim_type=claim_type):
                self.change_first_claim(lambda claim: claim.update(claim_type=claim_type, risk="normal"))
                self.assertRejected("requires high risk")

    def test_supported_executable_claim_requires_confirmed_proof(self):
        proof = {"script": "tests/example.py", "output": "A recorded result", "env": "Python", "verdict": "confirmed"}
        self.change_first_claim(lambda claim: claim.update(claim_type="executable", execution_proof=proof))
        self.assertTrue(validate_directory(self.root)["ok"])
        for verdict in ("partial", "refuted"):
            with self.subTest(verdict=verdict):
                self.change_first_claim(lambda claim: claim["execution_proof"].update(verdict=verdict))
                self.assertRejected("requires confirmed execution_proof")

    def test_unresolved_and_refuted_execution_proofs_remain_explicit(self):
        for status, verdict in (("unresolved", "partial"), ("refuted", "refuted")):
            with self.subTest(status=status):
                self.change_first_claim(lambda claim: claim.update(
                    claim_type="executable", review_status=status,
                    execution_proof={"script": "tests/example.py", "output": "A recorded result", "env": "Python", "verdict": verdict}
                ))
                self.assertTrue(validate_directory(self.root)["ok"])

    def test_unresolved_single_source_claim_is_retained(self):
        self.change_first_claim(lambda claim: claim.update(
            review_status="unresolved", source_ids=claim["source_ids"][:1]
        ))
        self.assertTrue(validate_directory(self.root)["ok"])
        self.change_first_claim(lambda claim: claim.update(review_status="manually_supported"))
        self.assertRejected("lacks independent source organizations")

    def test_scenario_ids_must_be_unique(self):
        self.change_scenarios(lambda data: data["cases"].append(data["cases"][0]))
        self.assertRejected("missing or duplicate id")

    def test_scenario_required_fields_are_typed(self):
        for field in ("id", "prompt", "acceptance"):
            for value in (None, " ", ["wrong type"]):
                with self.subTest(field=field, value=value):
                    self.change_scenarios(lambda data: data["cases"][0].update({field: value}))
                    self.assertRejected("missing or duplicate id" if field == "id" else f"needs nonblank {field}")
                    self.change_scenarios(lambda data: data["cases"][0].update({field: "valid"}))

    def test_scenario_expected_skills_reference_real_skills(self):
        for expected in (None, "motion-web", ["does-not-exist"], [{"wrong": "type"}]):
            with self.subTest(expected=expected):
                self.change_scenarios(lambda data: data["cases"][0].update(expected_skills=expected))
                self.assertRejected("expected_skills must be an array of existing skill names")
        self.change_scenarios(lambda data: data["cases"][0].update(expected_skills=[]))
        self.assertTrue(validate_directory(self.root)["ok"])

    def test_scenario_repeated_expected_skill(self):
        self.change_scenarios(lambda data: data["cases"][0].update(expected_skills=["motion-web", "motion-web"]))
        self.assertRejected("repeats an expected skill")

    def test_scenario_status_does_not_claim_host_execution(self):
        for status in (None, "agent-host execution passed", ["reviewer fixtures"]):
            with self.subTest(status=status):
                self.change_scenarios(lambda data: data.update(status=status))
                self.assertRejected("without claiming agent-host execution")

    def test_scenario_collection_and_cases_are_typed(self):
        for cases in (None, {}, [], ["not an object"]):
            with self.subTest(cases=cases):
                self.change_scenarios(lambda data: data.update(cases=cases))
                self.assertRejected("must be an object" if cases == ["not an object"] else "nonempty cases array")

    def test_directory_symlink(self):
        (self.root / "references/unsafe.md").symlink_to(self.work / "outside.md")
        self.assertRejected("symlinks are not permitted")

    def unsafe_zip(self, name, expected, mode=None, extra=None):
        path = self.work / "unsafe.zip"
        with zipfile.ZipFile(path, "w") as bundle:
            entry = zipfile.ZipInfo(name)
            if mode is not None:
                entry.create_system = 3
                entry.external_attr = mode << 16
            bundle.writestr(entry, "target")
            if extra:
                bundle.writestr(extra, "{}")
        result = validate_archive(path)
        self.assertFalse(result["ok"], result)
        self.assertIn(expected, json.dumps(result))

    def test_zip_traversal(self):
        self.unsafe_zip("../escape", "unsafe archive path")

    def test_zip_absolute(self):
        self.unsafe_zip("/escape", "unsafe archive path")

    def test_zip_windows_path(self):
        self.unsafe_zip("C:\\escape", "unsafe archive path")

    def test_zip_symlink(self):
        self.unsafe_zip("plugin/link", "nonregular archive member", stat.S_IFLNK | 0o777)

    def test_zip_multiple_wrappers(self):
        self.unsafe_zip("one/plugin.json", "one plugin with at most one wrapper", extra="two/plugin.json")

    def test_zip_duplicate_name(self):
        path = self.work / "duplicate.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(path, "w") as bundle:
                bundle.writestr("plugin/plugin.json", "{}")
                bundle.writestr("plugin/plugin.json", "{}")
        result = validate_archive(path)
        self.assertFalse(result["ok"])
        self.assertIn("duplicate archive member", json.dumps(result))

    def test_deterministic_archive_and_exclusions(self):
        cache = self.root / "scripts/__pycache__"
        cache.mkdir(exist_ok=True)
        (cache / "junk.pyc").write_bytes(b"cache")
        first, second = self.work / "one.zip", self.work / "two.zip"
        package_plugin(self.root, first)
        package_plugin(self.root, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertTrue(validate_archive(first)["ok"])
        with zipfile.ZipFile(first) as bundle:
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in bundle.namelist()))
            self.assertTrue(all(name.startswith("platform-motion-wizard/") for name in bundle.namelist()))
            self.assertIn("platform-motion-wizard/.claude-plugin/plugin.json", bundle.namelist())

    def test_direct_root_archive_accepts_compatibility_manifest(self):
        output = self.work / "direct-root.zip"
        with zipfile.ZipFile(output, "w") as bundle:
            for path in self.root.rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    bundle.write(path, path.relative_to(self.root).as_posix())
        result = validate_archive(output)
        self.assertTrue(result["ok"], result)

    def test_packaging_rejects_inside_output(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            package_plugin(self.root, self.root / "output.zip")

    def test_packaging_stops_on_invalid_source(self):
        (self.root / "references/broken.md").write_text("[Missing](absent.md)\n")
        output = self.work / "must-not-exist.zip"
        with self.assertRaises(ValueError):
            package_plugin(self.root, output)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
