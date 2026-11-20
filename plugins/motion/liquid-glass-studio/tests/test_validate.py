"""Regression tests for scripts/validate_plugin.py and scripts/package_plugin.py.

Every test builds a small fixture package in a temporary directory, so the
tests do not depend on the state of the real plugin files.
Run: python3 -m unittest discover -s tests -p "test_*.py"
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PACKAGE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from package_plugin import package_plugin  # noqa: E402
from validate_plugin import main as validate_main  # noqa: E402
from validate_plugin import validate_archive, validate_directory  # noqa: E402

SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

FILES = {
    "plugin.json": json.dumps({
        "$schema": SCHEMA,
        "name": "fixture-glass",
        "version": "1.0.0",
        "description": "Fixture plugin for validator tests.",
        "extensions": {"com.openai": {"interface": {
            "displayName": "Fixture Glass",
            "shortDescription": "Fixture glass plugin",
            "longDescription": "A fixture used by the validator tests.",
            "developerName": "Test Author",
            "category": "Developer Tools",
            "capabilities": [],
            "logo": "./assets/icon.svg",
            "defaultPrompt": ["Review this glass UI."],
        }}},
    }, indent=2),
    ".claude-plugin/plugin.json": json.dumps({
        "name": "fixture-glass", "version": "1.0.0", "description": "Fixture plugin for validator tests.",
    }),
    "assets/icon.svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>\n',
    "README.md": (
        "# Fixture Glass\n\n"
        "See [optics](references/optics.md#snell-refraction) and [the skill](skills/glass-web/SKILL.md).\n"
        "External links are not checked: [W3C](https://www.w3.org/WAI/).\n"
        "Directories resolve too: [skills](skills/).\n\n"
        "```md\n[ignored](missing.md) with an em dash \u2014 and the word robust inside a fence\n```\n\n"
        "Inline code is ignored: `[x](nope.md)` and `seamless`.\n"
    ),
    "NOTICE.md": "# Notice\n\nOriginal text, MIT license.\n",
    "references/optics.md": (
        "# Optics\n\n## Snell refraction\n\nBending follows Snell's law.\n\n"
        "## The `displacement` map\n\nSee [above](#snell-refraction) and [this one](#the-displacement-map).\n\n"
        "## Snell refraction\n\nA duplicate heading gets a suffix: [dup](#snell-refraction-1).\n\n"
        "Pick a landscape or portrait frame.\n\n"
        'A source README says "a robust engine" in its own words.\n'
    ),
    "skills/glass-web/SKILL.md": (
        "---\nname: glass-web\ndescription: Build web liquid glass style surfaces with fallbacks.\n---\n\n"
        "# Glass web\n\nRead [optics](../../references/optics.md).\n"
    ),
    "skills/glass-web/agents/openai.yaml": (
        "interface:\n  display_name: Glass Web\n  short_description: Web glass surfaces\n"
        "  default_prompt: Use $glass-web to build the glass toolbar.\npolicy:\n  allow_implicit_invocation: true\n"
    ),
    "docs/agents.md": "# Briefs\n\nNo frontmatter needed here. See [the reviewer](../agents/glass-reviewer.md).\n",
    "agents/glass-reviewer.md": "---\nname: glass-reviewer\ndescription: Review glass UI.\n---\n\nReview it.\n",
    "commands/glass.md": "---\ndescription: Start a glass task.\n---\n\nRoute the request.\n",
    "templates/glass-spec.md": "# Glass spec\n\n| Field | Value |\n| --- | --- |\n",
    "examples/glass-lab/README.md": "# Lab\n\nOpen index.html.\n",
    "examples/glass-lab/index.html": "<!doctype html><title>lab</title>\n",
    "research/skills-survey/sources/sources.jsonl": '{"id": "S1", "url": "https://example.org"}\n\n{"id": "S2"}\n',
    "research/skills-survey/artifacts/candidates.json": '{"candidates": []}\n',
    "research/skills-survey/outputs/research-decision-report.md": (
        "# Report\n\nResearch prose is exempt \u2014 a robust, seamless survey.\n"
    ),
    "scripts/tool.py": "print('hi')\n",
}


def build_fixture(root: Path, files=None):
    for relative, content in (files or FILES).items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root


def messages(result, level="errors"):
    return [f"{item['path']}: {item['message']}" for item in result[level]]


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lgs-validate-")
        self.addCleanup(self.tmp.cleanup)
        self.root = build_fixture(Path(self.tmp.name) / "fixture-glass")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def edit_json(self, relative, change):
        path = self.root / relative
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data))

    def assertFails(self, fragment, path_fragment=None):
        result = validate_directory(self.root)
        self.assertFalse(result["ok"], "expected a failure")
        found = [m for m in messages(result) if fragment in m and (path_fragment is None or path_fragment in m)]
        self.assertTrue(found, f"no error containing {fragment!r}; got {messages(result)}")
        return result

    # -- good fixture -----------------------------------------------------
    def test_good_fixture_passes_with_expected_warnings(self):
        result = validate_directory(self.root)
        self.assertTrue(result["ok"], messages(result))
        warnings = " | ".join(messages(result, "warnings"))
        self.assertIn("'landscape'", warnings)
        self.assertIn("inside a quotation", warnings)
        self.assertEqual(result["stats"]["skills"], 1)
        self.assertEqual(result["stats"]["agents"], 1)
        self.assertEqual(result["stats"]["commands"], 1)
        self.assertEqual(result["stats"]["research_records"], 2)

    # -- manifests --------------------------------------------------------
    def test_schema_url_required(self):
        self.edit_json("plugin.json", lambda d: d.update({"$schema": "https://example.org/schema.json"}))
        self.assertFails("$schema")

    def test_strict_semver(self):
        for bad in ("1.0", "01.0.0", "v1.0.0", "1.0.0-"):
            with self.subTest(version=bad):
                self.edit_json("plugin.json", lambda d, v=bad: d.update({"version": v}))
                self.assertFails("strict SemVer")
        self.edit_json("plugin.json", lambda d: d.update({"version": "1.2.3-beta.1+build.5"}))
        self.edit_json(".claude-plugin/plugin.json", lambda d: d.update({"version": "1.2.3-beta.1+build.5"}))
        self.assertTrue(validate_directory(self.root)["ok"])

    def test_bad_name(self):
        self.edit_json("plugin.json", lambda d: d.update({"name": "Fixture_Glass"}))
        self.assertFails("name must be")

    def test_short_description_limit(self):
        self.edit_json("plugin.json", lambda d: d["extensions"]["com.openai"]["interface"].update(
            {"shortDescription": "x" * 31}))
        self.assertFails("shortDescription is 31 characters")

    def test_interface_fields_and_logo(self):
        self.edit_json("plugin.json", lambda d: d["extensions"]["com.openai"]["interface"].pop("displayName"))
        self.assertFails("interface.displayName")
        build_fixture(self.root)
        (self.root / "assets/icon.svg").unlink()
        self.assertFails("interface.logo file is missing")

    def test_logo_cannot_escape(self):
        self.edit_json("plugin.json", lambda d: d["extensions"]["com.openai"]["interface"].update(
            {"logo": "../outside.svg"}))
        self.assertFails("escapes the package")

    def test_claude_manifest_identity(self):
        self.edit_json(".claude-plugin/plugin.json", lambda d: d.update({"version": "1.0.1"}))
        self.assertFails("version", ".claude-plugin/plugin.json")
        (self.root / ".claude-plugin/plugin.json").unlink()
        self.assertFails(".claude-plugin/plugin.json is missing")

    def test_duplicate_json_keys(self):
        self.write(".claude-plugin/plugin.json", '{"name": "fixture-glass", "name": "x", "version": "1.0.0"}')
        self.assertFails("duplicate key")

    # -- skills, briefs, commands -------------------------------------------
    def test_skill_name_must_match_directory(self):
        self.write("skills/glass-web/SKILL.md", "---\nname: glass-webs\ndescription: x\n---\n")
        self.assertFails("must equal directory name")

    def test_skill_needs_frontmatter(self):
        self.write("skills/glass-web/SKILL.md", "# No frontmatter\n")
        self.assertFails("must start with YAML frontmatter")

    def test_skill_description_limit(self):
        self.write("skills/glass-web/SKILL.md", "---\nname: glass-web\ndescription: " + "a" * 1025 + "\n---\n")
        self.assertFails("description is 1025 characters")

    def test_openai_yaml_fields(self):
        self.write("skills/glass-web/agents/openai.yaml",
                   "interface:\n  display_name: Glass Web\n  short_description: Web\npolicy:\n  allow_implicit_invocation: 'yes'\n")
        result = self.assertFails("interface.default_prompt")
        self.assertIn("allow_implicit_invocation", " ".join(messages(result)))
        (self.root / "skills/glass-web/agents/openai.yaml").unlink()
        self.assertFails("openai.yaml is missing")

    def test_openai_yaml_parse_error(self):
        self.write("skills/glass-web/agents/openai.yaml", "interface: [unclosed\n")
        self.assertFails("invalid YAML")

    def test_agent_brief_frontmatter(self):
        self.write("agents/glass-reviewer.md", "---\ndescription: Review glass UI.\n---\n")
        self.assertFails("needs a nonblank name")
        self.write("agents/glass-reviewer.md", "---\nname: other\ndescription: Review.\n---\n")
        self.assertFails("should equal file name")

    def test_agents_readme_is_an_error(self):
        # Claude Code loads every agents/*.md as an agent, README included.
        self.write("agents/README.md", "# Briefs\n\nNo frontmatter here.\n")
        self.assertFails("loads every agents/*.md file as an agent", "agents/README.md")

    def test_docs_is_prose_gated(self):
        self.write("docs/agents.md", "# Briefs\n\nA robust set \u2014 of briefs.\n")
        result = self.assertFails("banned word 'robust'", "docs/agents.md")
        self.assertTrue(any("dash" in m and "docs/agents.md" in m for m in messages(result)), messages(result))

    def test_command_needs_description(self):
        self.write("commands/glass.md", "---\nargument-hint: '[target]'\n---\nBody\n")
        self.assertFails("command frontmatter needs a nonblank description")

    # -- links ------------------------------------------------------------
    def test_missing_link_target(self):
        self.write("NOTICE.md", "# Notice\n\nSee [gone](references/gone.md).\n")
        self.assertFails("link target does not exist: references/gone.md")

    def test_missing_anchor(self):
        self.write("NOTICE.md", "# Notice\n\nSee [optics](references/optics.md#no-such-heading).\n")
        self.assertFails("anchor not found")

    def test_same_file_anchor(self):
        self.write("NOTICE.md", "# Notice\n\n[top](#notice) and [bad](#nowhere).\n")
        result = self.assertFails("anchor not found: #nowhere")
        self.assertNotIn("#notice", " ".join(messages(result)))

    def test_link_cannot_escape_or_be_absolute(self):
        self.write("NOTICE.md", "# Notice\n\n[up](../../etc/passwd) [abs](/etc/passwd)\n")
        result = self.assertFails("escapes the package")
        self.assertIn("must be relative", " ".join(messages(result)))

    def test_reference_style_definition(self):
        self.write("NOTICE.md", "# Notice\n\nSee [spec][s].\n\n[s]: references/missing.md\n")
        self.assertFails("references/missing.md")

    # -- prose gate -------------------------------------------------------
    def test_em_and_en_dash_fail_outside_code(self):
        self.write("references/optics.md", "# Optics\n\nBlur \u2014 then tint.\n")
        self.assertFails("em dash")
        self.write("references/optics.md", "# Optics\n\nPages 3\u20135.\n")
        self.assertFails("en dash")

    def test_banned_word_fails_whole_word_case_insensitive(self):
        self.write("skills/glass-web/SKILL.md",
                   "---\nname: glass-web\ndescription: A Robust glass skill.\n---\n")
        self.assertFails("banned word 'Robust'")
        self.write("skills/glass-web/SKILL.md",
                   "---\nname: glass-web\ndescription: Words like unrobust and robusta are fine.\n---\n")
        result = validate_directory(self.root)
        self.assertTrue(result["ok"], messages(result))

    def test_banned_word_in_each_prose_location(self):
        for relative in ("agents/glass-reviewer.md", "commands/glass.md", "templates/glass-spec.md",
                         "examples/glass-lab/README.md", "docs/agents.md", "README.md", "NOTICE.md"):
            with self.subTest(path=relative):
                build_fixture(self.root)
                path = self.root / relative
                path.write_text(path.read_text() + "\nWe delve into it.\n")
                self.assertFails("banned word 'delve'", relative)

    def test_additionally_only_as_opener(self):
        self.write("NOTICE.md", "# Notice\n\nIt also adds blur, additionally tint.\n")
        self.assertTrue(validate_directory(self.root)["ok"])
        self.write("NOTICE.md", "# Notice\n\nIt adds blur. Additionally, it tints.\n")
        self.assertFails("sentence opener")

    def test_leverage_is_warning(self):
        self.write("NOTICE.md", "# Notice\n\nUse leverage carefully.\n")
        result = validate_directory(self.root)
        self.assertTrue(result["ok"], messages(result))
        self.assertTrue(any("'leverage'" in m for m in messages(result, "warnings")))

    def test_research_is_exempt_but_jsonl_must_parse(self):
        result = validate_directory(self.root)
        self.assertTrue(result["ok"], messages(result))  # report.md has an em dash and banned words
        self.write("research/skills-survey/sources/sources.jsonl", '{"id": "S1"}\n{broken\n')
        result = self.assertFails("invalid JSONL record")
        self.assertIn(2, [e["line"] for e in result["errors"]])
        build_fixture(self.root)
        self.write("research/skills-survey/artifacts/candidates.json", "{nope")
        self.assertFails("invalid JSON")

    def test_symlink_rejected(self):
        os.symlink(self.root / "NOTICE.md", self.root / "references/link.md")
        self.assertFails("symlinks are not allowed")

    def test_excluded_folders_ignored(self):
        self.write("examples/glass-lab/node_modules/pkg/README.md", "A robust package \u2014 [x](missing.md)\n")
        self.assertTrue(validate_directory(self.root)["ok"])

    # -- CLI --------------------------------------------------------------
    def run_cli(self, *args):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = validate_main(list(args))
        return code, buffer.getvalue()

    def test_cli_json_and_exit_codes(self):
        code, out = self.run_cli(str(self.root), "--json")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["ok"])
        self.write("NOTICE.md", "# Notice\n\nA pivotal note.\n")
        code, out = self.run_cli(str(self.root))
        self.assertEqual(code, 1)
        self.assertIn("FAIL", out)
        self.assertIn("NOTICE.md:3", out)
        code, out = self.run_cli(str(self.root / "missing"), "--json")
        self.assertEqual(code, 2)
        self.assertIn("fatal", json.loads(out))

    def test_cli_subprocess(self):
        process = subprocess.run([sys.executable, str(SCRIPTS / "validate_plugin.py"), str(self.root), "--json"],
                                 capture_output=True, text=True, check=False)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)


class ArchiveAndPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="lgs-package-")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.root = build_fixture(self.work / "fixture-glass")

    def make_zip(self, entries):
        path = self.work / "test.zip"
        with zipfile.ZipFile(path, "w") as bundle:
            for name, data, mode in entries:
                info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = mode << 16
                bundle.writestr(info, data)
        return path

    def test_package_is_deterministic_and_valid(self):
        (self.root / "scripts/__pycache__").mkdir()
        (self.root / "scripts/__pycache__/tool.cpython-313.pyc").write_bytes(b"\0")
        (self.root / ".DS_Store").write_bytes(b"\0")
        (self.root / "examples/glass-lab/node_modules").mkdir()
        (self.root / "examples/glass-lab/node_modules/x.js").write_text("x")
        (self.root / "scripts/tool.py").chmod(0o755)
        first = package_plugin(self.root, self.work / "out/a.zip")
        second = package_plugin(self.root, self.work / "out/b.zip")
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first["sha256"], hashlib.sha256((self.work / "out/a.zip").read_bytes()).hexdigest())
        with zipfile.ZipFile(self.work / "out/a.zip") as bundle:
            names = bundle.namelist()
            self.assertEqual(names, sorted(names))
            self.assertTrue(all(n.startswith("fixture-glass/") for n in names))
            self.assertIn("fixture-glass/research/skills-survey/artifacts/candidates.json", names)
            self.assertFalse([n for n in names if "__pycache__" in n or ".DS_Store" in n or "node_modules" in n])
            self.assertTrue(all(i.date_time == (2020, 1, 1, 0, 0, 0) for i in bundle.infolist()))
            mode = bundle.getinfo("fixture-glass/scripts/tool.py").external_attr >> 16
            self.assertEqual(stat.S_IMODE(mode), 0o755)
        self.assertTrue(validate_archive(self.work / "out/a.zip")["ok"])

    def test_package_refuses_invalid_tree_and_output_inside(self):
        with self.assertRaises(ValueError):
            package_plugin(self.root, self.root / "dist/x.zip")
        (self.root / "NOTICE.md").write_text("# Notice\n\nA vibrant note.\n")
        process = subprocess.run([sys.executable, str(SCRIPTS / "package_plugin.py"), str(self.root),
                                  "--output", str(self.work / "bad.zip")], capture_output=True, text=True, check=False)
        self.assertEqual(process.returncode, 1, process.stderr)
        self.assertFalse((self.work / "bad.zip").exists())

    def test_package_cli_prints_sha(self):
        process = subprocess.run([sys.executable, str(SCRIPTS / "package_plugin.py"), str(self.root),
                                  "--output", str(self.work / "cli.zip")], capture_output=True, text=True, check=False)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        digest = hashlib.sha256((self.work / "cli.zip").read_bytes()).hexdigest()
        self.assertEqual(process.stdout.split()[0], digest)

    def test_archive_rejects_traversal_absolute_and_symlink(self):
        regular = stat.S_IFREG | 0o644
        cases = {
            "path traversal": [("fixture-glass/../evil.txt", b"x", regular)],
            "absolute": [("/etc/evil.txt", b"x", regular)],
            "symlink member": [("fixture-glass/link", b"/etc/passwd", stat.S_IFLNK | 0o777)],
        }
        for label, entries in cases.items():
            with self.subTest(case=label):
                path = self.make_zip([("fixture-glass/plugin.json", b"{}", regular)] + entries)
                result = validate_archive(path)
                self.assertFalse(result["ok"])
                self.assertIn(label, json.dumps(result))

    def test_archive_size_cap(self):
        path = self.make_zip([("fixture-glass/plugin.json", b"x" * 2048, stat.S_IFREG | 0o644)])
        result = validate_archive(path, max_bytes=1024)
        self.assertFalse(result["ok"])
        self.assertIn("exceeds the cap", json.dumps(result))

    def test_archive_reruns_directory_checks(self):
        package_plugin(self.root, self.work / "good.zip")
        with zipfile.ZipFile(self.work / "good.zip") as source, \
                zipfile.ZipFile(self.work / "bad.zip", "w") as target:
            for info in source.infolist():
                data = source.read(info)
                if info.filename.endswith("NOTICE.md"):
                    data = "# Notice\n\nBlur \u2014 tint.\n".encode()
                target.writestr(info, data)
        result = validate_archive(self.work / "bad.zip")
        self.assertFalse(result["ok"])
        self.assertIn("em dash", json.dumps(result))

    def test_archive_cli_exit_codes(self):
        package_plugin(self.root, self.work / "good.zip")
        buffer = io.StringIO()
        with redirect_stdout(buffer), redirect_stderr(buffer):
            self.assertEqual(validate_main(["--archive", str(self.work / "good.zip")]), 0)
            (self.work / "junk.zip").write_bytes(b"not a zip")
            self.assertEqual(validate_main(["--archive", str(self.work / "junk.zip")]), 2)


if __name__ == "__main__":
    unittest.main()
