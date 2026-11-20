"""Offline tests for the package validator, the deterministic ZIP builder and the shipped manifests.

Synthetic plugin trees are built in temporary directories, so these tests do not depend on the
rest of the real plugin tree being complete. Nothing here touches the network.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
import socket
import stat
import sys
import tempfile
import unittest
import warnings
import xml.etree.ElementTree as ElementTree
import zipfile
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
REAL_ROOT = TESTS_DIR.parent
sys.path.insert(0, str(REAL_ROOT / "scripts"))
sys.path.insert(0, str(TESTS_DIR))

import package_plugin as packager  # noqa: E402
import validate_plugin as vp  # noqa: E402

_SAVED_SOCKET = {}


def _deny_network(*args, **kwargs):
    raise RuntimeError("network access is blocked in tests")


def setUpModule():
    try:
        import helpers  # tests/helpers.py: shared network sentinel
    except ImportError:
        helpers = None
    block = getattr(helpers, "block_network", None)
    if callable(block):
        block()
        return
    for owner, name in ((socket.socket, "connect"), (socket.socket, "connect_ex"),
                        (socket, "create_connection"), (socket, "getaddrinfo")):
        _SAVED_SOCKET[(owner, name)] = getattr(owner, name)
        setattr(owner, name, _deny_network)


def tearDownModule():
    for (owner, name), value in _SAVED_SOCKET.items():
        setattr(owner, name, value)
    _SAVED_SOCKET.clear()


OWNED_FILES = ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "LICENSE",
               "assets/icon.svg") + tuple(vp.LICENSE_FILES)
LICENSE_SHA256 = {
    "licenses/claude-seo-MIT.txt": "a42b3b0253cecea9af810c5207a67b0be8c9a0cfbf52b9302c3d26b063e7a86b",
    "licenses/geo-seo-claude-MIT.txt": "7bb0e4a490394cd2e1beab4d5886fd9cab237527144cc931170e4f29cf1872cc",
    "licenses/open-seo-mcp-skills-MIT.txt": "2df13980592521711925f0cf7acccc27167f6b825e774f19bbe07fae0c9f9436",
    "licenses/eGEOagents-MIT.txt": "443031081d42bc750db2a1fb173e5b42f408203a8c13c4382181b95cdd665800",
    "licenses/notfair-plugin-MIT.txt": "4fef0720a8c3a7182a7a44bf211a357fa1388d8acec87110c014e02e956dc248",
    "licenses/geoptimize-MIT.txt": "b132b6ecfe2dd5be23807d9c7148f0ce8cc367b231eeca478331044e14ec442e",
    "licenses/aaron-marketing-skills-Apache-2.0.txt": "664cd12e1c315650bf14cb1385359d13d4724ac03940ac10918390ef78e4f5e7",
}
COPYRIGHT_LINES = {
    "LICENSE": "Copyright (c) 2026 SEO-GEO-god contributors",
    "licenses/claude-seo-MIT.txt": "Copyright (c) 2026 agricidaniel",
    "licenses/geo-seo-claude-MIT.txt": "Copyright (c) 2026 Zubair Trabzada",
    "licenses/open-seo-mcp-skills-MIT.txt": "Copyright (c) 2026 Ryze AI",
    "licenses/eGEOagents-MIT.txt": "Copyright (c) 2025 Vera Badias",
    "licenses/notfair-plugin-MIT.txt": "Copyright (c) 2026 Toprank Contributors",
    "licenses/geoptimize-MIT.txt": "Copyright (c) 2026 Te-Shu Wang",
    "licenses/aaron-marketing-skills-Apache-2.0.txt": "Copyright 2024 Aaron He Zhu",
}


def skill_text(name, description=None):
    description = description or f"Synthetic {name} for validator tests. Not for real sites (use the other skill)."
    return (f'---\nname: {name}\ndescription: "{description}"\n---\n\n# {name}\n\n'
            f"Read [the fact](../../references/facts.md#f-t-1) and the [rules](#rules).\n\n## Rules\n\n- Synthetic rule.\n")


def openai_text(name):
    return (f'interface:\n  display_name: "{name.title()}"\n  short_description: "Synthetic skill"\n'
            f'  default_prompt: "Use ${name} to run the synthetic task."\npolicy:\n  allow_implicit_invocation: true\n')


SCENARIOS = {"status": vp.SCENARIO_STATUS, "cases": [
    {"id": "alpha", "prompt": "Fix the synthetic thing.", "expected_skills": ["alpha-skill"], "acceptance": "Routes to alpha."},
    {"id": "no-skill", "prompt": "Run a paid ads campaign.", "expected_skills": [], "acceptance": "No skill applies."},
]}
SYNTHETIC_FILES = {
    "README.md": ("# Demo plugin\n\nSee [skills](skills/), [alpha](skills/alpha-skill/SKILL.md), [notice](NOTICE.md#attribution), "
                  "[release](CHANGELOG.md#100--2026-11-01), [fact](references/facts.md#f-t-1), "
                  "[parser](<references/facts.md#the-robotstxt-parser>), [site](https://example.com/), "
                  "[mail](mailto:team@example.com) and ![icon](assets/icon.svg \"Icon\").\n\n[ref]: VALIDATION.md#validation\n"),
    "NOTICE.md": "# Notice\n\n## Attribution\n\nSee [the MIT text](licenses/claude-seo-MIT.txt).\n",
    "CHANGELOG.md": "# Changelog\n\n## 1.0.0 \u2014 2026-11-01\n\n- Initial synthetic release.\n",
    "VALIDATION.md": "# Validation\n\nBack to [the README](README.md#demo-plugin).\n",
    "references/facts.md": ("# Facts\n\n| ID | Fact |\n| --- | --- |\n| <a id=\"f-t-1\"></a>F-T-1 | Synthetic fact. |\n\n"
                            "## The `robots.txt` parser\n\nBack to [the parser](#the-robotstxt-parser) and [facts](#facts).\n"),
    "skills/alpha-skill/SKILL.md": skill_text("alpha-skill"),
    "skills/alpha-skill/agents/openai.yaml": openai_text("alpha-skill"),
    "skills/beta-skill/SKILL.md": skill_text("beta-skill"),
    "skills/beta-skill/agents/openai.yaml": openai_text("beta-skill"),
    "agents/README.md": "# Agents\n\n- [Alpha agent](alpha-agent.md)\n",
    "agents/alpha-agent.md": ('---\nname: alpha-agent\ndescription: "Read-only synthetic reviewer."\ntools: Read, Grep, Glob, Bash\n'
                              "---\n\n# Alpha agent\n\nLoads [alpha](../skills/alpha-skill/SKILL.md).\n"),
    "data/rules.json": json.dumps({"as_of": "2026-11-01", "rules": []}),
    "schemas/finding.schema.json": json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}),
    "templates/project.example.json": json.dumps({"schema_version": 1}),
    "tests/skill-scenarios.json": json.dumps(SCENARIOS),
    "scripts/tool.py": "from __future__ import annotations\n",
}


def build_plugin(root):
    root = Path(root)
    for rel in OWNED_FILES:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REAL_ROOT / rel).read_bytes())
    for rel, text in SYNTHETIC_FILES.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


class TempTree(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="seo-geo-god-package-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.root = build_plugin(self.work / "seo-geo-god")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def change_json(self, rel, change):
        path = self.root / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def assertValid(self, root=None):
        result = vp.validate_directory(root or self.root)
        self.assertTrue(result["ok"], json.dumps(result["errors"], indent=1))
        return result

    def assertRejected(self, fragment, root=None):
        result = vp.validate_directory(root or self.root)
        self.assertFalse(result["ok"], result)
        self.assertIn(fragment, json.dumps(result["errors"]))
        return result


class RestrictedYamlTests(unittest.TestCase):
    def test_scalar_styles_and_types(self):
        cases = {
            '"Use \\"quotes\\" and \\u00e9"': ('Use "quotes" and \u00e9', True),
            "'It''s fine'": ("It's fine", True),
            '"value" # trailing comment': ("value", True),
            "plain words, with commas": ("plain words, with commas", False),
            "plain # comment": ("plain", False),
            "true": (True, False), "False": (False, False), "null": (None, False), "~": (None, False),
            "": (None, False), "42": (42, False), "-1.5": (-1.5, False), "[CHAT, 'CODEX']": (["CHAT", "CODEX"], False),
            "[]": ([], False), "C#-style": ("C#-style", False),
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(vp.scalar(text), expected)

    def test_scalar_rejects_unsupported_syntax(self):
        for text in (">", ">-", "|", '"unterminated', "'unterminated", '"bad \\x41 escape"', "{a: 1}", "&anchor value",
                     "*alias", "!tag value", "@reserved", "`tick", "- item", "key: value inside", "[nested, [list]]",
                     "[unclosed", '"a" trailing'):
            with self.subTest(text=text):
                with self.assertRaises(vp.YamlSubsetError):
                    vp.scalar(text)

    def test_one_level_mapping(self):
        data, quoted = vp.parse_mapping('# comment\nname: demo\n\ndescription: "One line."\n', depth=1)
        self.assertEqual(data, {"name": "demo", "description": "One line."})
        self.assertEqual(quoted, {"name": False, "description": True})
        for text, fragment in (("name: a\nname: b\n", "duplicate key"),
                               ('description: "a"\n  continued\n', "unexpected indentation"),
                               ("description: >\n  folded\n", "block scalars"),
                               ("- item\n", "expected 'key: value'"),
                               ("key:value\n", "expected 'key: value'"),
                               ("parent:\n  child: x\n", "unexpected indentation")):
            with self.subTest(text=text):
                with self.assertRaisesRegex(vp.YamlSubsetError, fragment):
                    vp.parse_mapping(text, depth=1)

    def test_two_level_mapping(self):
        text = 'interface:\n  display_name: "A"\n  short_description: B\npolicy:\n    allow_implicit_invocation: false\n    products: [CODEX]\n'
        data, _ = vp.parse_mapping(text.replace("\n", "\r\n"), depth=2)
        self.assertEqual(data, {"interface": {"display_name": "A", "short_description": "B"},
                                "policy": {"allow_implicit_invocation": False, "products": ["CODEX"]}})
        for text, fragment in (("interface:\n  icons:\n    small: a.svg\n", "nesting deeper"),
                               ("interface:\n  - item\n", "expected 'key: value'"),
                               ("interface:\n  a: 1\n    b: 2\n", "inconsistent indentation"),
                               ("interface:\n\ta: 1\n", "tab indentation"),
                               ("interface:\n  a: 1\n  a: 2\n", "duplicate key interface.a"),
                               ("  a: 1\n", "unexpected indentation"),
                               ("---\ninterface:\n", "expected 'key: value'")):
            with self.subTest(text=text):
                with self.assertRaisesRegex(vp.YamlSubsetError, fragment):
                    vp.parse_mapping(text, depth=2)

    def test_split_frontmatter(self):
        self.assertEqual(vp.split_frontmatter("---\nname: a\n---\nbody\n"), ("name: a", "body\n"))
        self.assertEqual(vp.split_frontmatter("---\r\nname: a\r\n---\r\nbody"), ("name: a\r", "body"))
        self.assertEqual(vp.split_frontmatter("# no frontmatter\n"), (None, "# no frontmatter\n"))
        self.assertEqual(vp.split_frontmatter("---\nname: a\nnever closed\n")[0], None)
        self.assertEqual(vp.split_frontmatter("\ufeff---\nname: a\n---\n")[0], None)


class MarkdownAnchorTests(unittest.TestCase):
    def test_github_style_slugs(self):
        cases = {
            "Before you change anything": "before-you-change-anything",
            "1.0.0 \u2014 2026-11-01": "100--2026-11-01",
            "The `robots.txt` parser": "the-robotstxt-parser",
            "`__init__` and __bold__ and *em*": "__init__-and-bold-and-em",
            "Q&amp;A: what's new?": "qa-whats-new",
            "\u00dcn\u00efcode Stra\u00dfe": "\u00fcn\u00efcode-stra\u00dfe",
            "[Linked](x.md) heading": "linked-heading",
            "snake_case_name": "snake_case_name",
            "Use `SG audit-build` (offline)": "use-sg-audit-build-offline",
            "F-T-18 \u00b7 Googlebot": "f-t-18--googlebot",
        }
        for heading, slug in cases.items():
            with self.subTest(heading=heading):
                self.assertEqual(vp.github_slug(heading), slug)

    def test_duplicate_headings_get_github_suffixes(self):
        anchors = vp.markdown_anchors("# A\n\n## A\n\n### A-1\n\n## Closing ##\n")
        self.assertTrue({"a", "a-1", "a-1-1", "closing"} <= anchors)

    def test_anchors_ignore_code_comments_and_frontmatter(self):
        text = ("---\ntitle: x\n---\n\n#hashtag is not a heading\n\n```md\n# Not a heading\n<a id=\"in-code\"></a>\n```\n\n"
                "~~~~\n```\n# Still code\n~~~~\n\n<!-- <a id=\"in-comment\"></a> -->\n\nSetext title\n============\n\n"
                "<a id=\"f-t-18\"></a> and <span name='named'></span>\n\n# Real\n")
        anchors = vp.markdown_anchors(text)
        self.assertTrue({"setext-title", "f-t-18", "named", "real"} <= anchors)
        for absent in ("hashtag-is-not-a-heading", "not-a-heading", "in-code", "still-code", "in-comment", "title-x"):
            self.assertNotIn(absent, anchors)

    def test_list_item_before_rule_is_not_setext(self):
        self.assertNotIn("item", vp.markdown_anchors("- item\n---\n"))


class ValidatorTests(TempTree):
    def test_valid_synthetic_package(self):
        result = self.assertValid()
        self.assertEqual(result["scope"], "offline structural and integrity checks; no host installation or factual verification")
        stats = result["stats"]
        self.assertEqual((stats["skills"], stats["agent_briefs"], stats["data_files"], stats["schema_files"],
                          stats["scenario_cases"]), (2, 1, 1, 1, 2))
        self.assertGreaterEqual(stats["links_checked"], 15)
        self.assertEqual(stats["files"], len(vp.package_files(self.root)))

    def test_missing_directory(self):
        self.assertRejected("package directory does not exist", self.work / "absent")

    def test_manifest_schema_name_and_semver(self):
        for change, fragment in ((lambda d: d.update({"$schema": "https://example.invalid/schema"}), "schema declaration"),
                                 (lambda d: d.pop("$schema"), "schema declaration"),
                                 (lambda d: d.update(name="Bad_Name"), "invalid plugin name"),
                                 (lambda d: d.update(name="bad--name"), "invalid plugin name"),
                                 (lambda d: d.update(version="01.2.3"), "strict SemVer"),
                                 (lambda d: d.update(version=1), "strict SemVer"),
                                 (lambda d: d.update(description=""), "description must be a nonblank string"),
                                 (lambda d: d.update(description="x" * 301), "description exceeds 300"),
                                 (lambda d: d.update(keywords="seo"), "keywords must be an array"),
                                 (lambda d: d.update(author="someone"), "author must be an object"),
                                 (lambda d: d.update(extensions=[]), "extensions and extensions.com.openai must be objects")):
            with self.subTest(fragment=fragment):
                original = (self.root / "plugin.json").read_text(encoding="utf-8")
                self.change_json("plugin.json", change)
                self.assertRejected(fragment)
                (self.root / "plugin.json").write_text(original, encoding="utf-8")
        self.change_json("plugin.json", lambda d: d.update(description="x" * 300))
        self.assertValid()

    def test_manifest_interface_rules(self):
        def interface(change):
            def apply(data):
                change(data["extensions"]["com.openai"]["interface"])
            self.change_json("plugin.json", apply)
            self.change_json(".codex-plugin/plugin.json", lambda d: change(d["interface"]))
        for change, fragment in ((lambda i: i.update(shortDescription="x" * 31), "exceeds 30 characters"),
                                 (lambda i: i.pop("displayName"), "displayName must be a nonblank string"),
                                 (lambda i: i.update(category="Marketing"), "category"),
                                 (lambda i: i.update(category={"wrong": True}), "category"),
                                 (lambda i: i.update(defaultPrompt=["a", "b", "c", "d"]), "defaultPrompt must be"),
                                 (lambda i: i.update(defaultPrompt=[]), "defaultPrompt must be"),
                                 (lambda i: i.update(capabilities=[""]), "capabilities must be"),
                                 (lambda i: i.update(brandColor="red"), "brandColor"),
                                 (lambda i: i.update(logo="./assets/missing.svg"), "missing local file: ./assets/missing.svg"),
                                 (lambda i: i.update(logo="https://example.com/icon.svg"), "contained relative local path"),
                                 (lambda i: i.update(composerIcon="../outside.svg"), "path escapes package"),
                                 (lambda i: i.update(logo="http://[::1/icon.svg"), "invalid local path")):
            with self.subTest(fragment=fragment):
                saved = {rel: (self.root / rel).read_text(encoding="utf-8") for rel in ("plugin.json", ".codex-plugin/plugin.json")}
                interface(change)
                self.assertRejected(fragment)
                for rel, text in saved.items():
                    (self.root / rel).write_text(text, encoding="utf-8")
        interface(lambda i: i.update(shortDescription="x" * 30, defaultPrompt="One prompt."))
        self.assertValid()

    def test_overlay_identity_agreement(self):
        for overlay in vp.OVERLAYS:
            for key, value in (("version", "0.0.1"), ("name", "other-name"), ("license", "Apache-2.0")):
                with self.subTest(overlay=overlay, key=key):
                    original = (self.root / overlay).read_text(encoding="utf-8")
                    self.change_json(overlay, lambda d: d.update({key: value}))
                    self.assertRejected(f"{key} disagrees with portable manifest")
                    (self.root / overlay).write_text(original, encoding="utf-8")
        self.change_json(".claude-plugin/plugin.json", lambda d: d.pop("name"))
        self.assertRejected("name disagrees")

    def test_overlays_are_required_objects(self):
        (self.root / ".claude-plugin/plugin.json").write_text("[]", encoding="utf-8")
        self.assertRejected("compatibility manifest must be a JSON object")
        (self.root / ".claude-plugin/plugin.json").unlink()
        self.assertRejected("required file is missing")

    def test_codex_interface_and_skills_path(self):
        self.change_json(".codex-plugin/plugin.json", lambda d: d["interface"].update(displayName="Different"))
        self.assertRejected("interface disagrees with plugin.json")
        self.change_json(".codex-plugin/plugin.json", lambda d: d["interface"].update(displayName="SEO-GEO-god"))
        self.assertValid()
        for value in (None, "./references", "../skills", 3, "skills\x00"):
            with self.subTest(skills=value):
                self.change_json(".codex-plugin/plugin.json", lambda d: d.update(skills=value))
                self.assertRejected("skills must point to ./skills")
        self.change_json(".codex-plugin/plugin.json", lambda d: d.update(skills="skills"))
        self.assertValid()
        self.change_json(".codex-plugin/plugin.json", lambda d: d.pop("interface"))
        self.assertRejected("interface must be an object")

    def test_forbidden_manifest_keys(self):
        for rel in ("plugin.json",) + vp.OVERLAYS:
            for key in vp.FORBIDDEN_KEYS:
                with self.subTest(manifest=rel, key=key):
                    original = (self.root / rel).read_text(encoding="utf-8")
                    self.change_json(rel, lambda d: d.update({key: {}}))
                    self.assertRejected(f"forbidden manifest key: {key}")
                    (self.root / rel).write_text(original, encoding="utf-8")

    def test_portable_root_rejects_host_specific_fields(self):
        for key in ("skills", "interface"):
            with self.subTest(key=key):
                original = (self.root / "plugin.json").read_text(encoding="utf-8")
                self.change_json("plugin.json", lambda d: d.update({key: "./skills"}))
                self.assertRejected(f"{key} is not a portable root manifest field")
                (self.root / "plugin.json").write_text(original, encoding="utf-8")

    def test_forbidden_paths(self):
        for rel, is_dir in (("hooks", True), ("hooks", False), (".mcp.json", False), ("bin", True)):
            with self.subTest(path=rel, directory=is_dir):
                path = self.root / rel
                if is_dir:
                    path.mkdir()
                    (path / "hooks.json").write_text("{}", encoding="utf-8")
                else:
                    path.write_text("{}", encoding="utf-8")
                self.assertRejected("forbidden path")
                if is_dir:
                    (path / "hooks.json").unlink()
                    path.rmdir()
                else:
                    path.unlink()
        self.write("templates/opt-in/claude-code-hook.example.json", "{}")
        self.write("tests/fixtures/stack/next/src/hooks/use-thing.ts", "export {};\n")
        self.assertValid()

    def test_required_files(self):
        for rel in vp.REQUIRED_FILES + tuple(vp.LICENSE_FILES):
            with self.subTest(rel=rel):
                path = self.root / rel
                original = path.read_bytes()
                path.unlink()
                self.assertRejected("required file is missing")
                path.write_bytes(original)

    def test_license_texts(self):
        self.write("licenses/claude-seo-MIT.txt", "Some other text\n")
        self.assertRejected("license text does not contain 'MIT License'")
        self.write("licenses/claude-seo-MIT.txt", (REAL_ROOT / "licenses/claude-seo-MIT.txt").read_text(encoding="utf-8"))
        self.write("licenses/aaron-marketing-skills-Apache-2.0.txt", "MIT License\n")
        self.assertRejected("license text does not contain 'Apache License'")
        self.write("licenses/aaron-marketing-skills-Apache-2.0.txt", "Apache License\n")
        self.write("LICENSE", "All rights reserved.\n")
        self.assertRejected("LICENSE must contain the MIT license text")

    def test_skill_name_mismatch(self):
        self.write("skills/alpha-skill/SKILL.md", skill_text("mismatched"))
        self.assertRejected("name must match its directory")

    def test_skill_name_format(self):
        for name in ("Bad_Skill", "x" * 65):
            with self.subTest(name=name):
                self.write(f"skills/{name}/SKILL.md", skill_text(name))
                self.write(f"skills/{name}/agents/openai.yaml", openai_text("bad"))
                self.assertRejected("kebab-case and at most 64 characters")
                for rel in ("SKILL.md", "agents/openai.yaml"):
                    (self.root / "skills" / name / rel).unlink()
                (self.root / "skills" / name / "agents").rmdir()
                (self.root / "skills" / name).rmdir()
        name = "x" * 64
        self.write(f"skills/{name}/SKILL.md", skill_text(name))
        self.write(f"skills/{name}/agents/openai.yaml", openai_text("long"))
        self.assertValid()

    def test_skill_frontmatter_keys(self):
        path = self.root / "skills/alpha-skill/SKILL.md"
        original = path.read_text(encoding="utf-8")
        for text, fragment in ((original.replace("---\n\n#", "license: MIT\n---\n\n#", 1), "exactly name and description; found description, license, name"),
                               (original.replace('description: "', 'summary: "', 1), "exactly name and description"),
                               ("# No frontmatter\n", "must start with a --- frontmatter block"),
                               (original.replace("name: alpha-skill", "name: alpha-skill\nname: again"), "duplicate key")):
            with self.subTest(fragment=fragment):
                path.write_text(text, encoding="utf-8")
                self.assertRejected(fragment)
        path.write_text(original, encoding="utf-8")
        self.assertValid()

    def test_skill_description_rules(self):
        path = self.root / "skills/alpha-skill/SKILL.md"
        base = "---\nname: alpha-skill\ndescription: {}\n---\n\n# Alpha\n"
        for value, fragment in ((">\n  Folded description.", "block scalars"),
                                ("|\n  Literal description.", "block scalars"),
                                ("Plain unquoted description.", "one-line quoted string"),
                                ('""', "description must be a nonblank string"),
                                ('"' + "x" * 1025 + '"', "description exceeds 1024"),
                                ('"multi\n  line"', "unterminated")):
            with self.subTest(value=value[:20]):
                path.write_text(base.format(value), encoding="utf-8")
                self.assertRejected(fragment)
        for value in ('"' + "x" * 1024 + '"', "'Single quoted description.'"):
            with self.subTest(value=value[:20]):
                path.write_text(base.format(value), encoding="utf-8")
                self.assertValid()

    def test_skill_requires_openai_yaml(self):
        (self.root / "skills/beta-skill/agents/openai.yaml").unlink()
        self.assertRejected("skill is missing agents/openai.yaml")

    def test_openai_yaml_subset(self):
        path = self.root / "skills/alpha-skill/agents/openai.yaml"
        good = openai_text("alpha-skill")
        for text, fragment in ((good + "dependencies:\n  tools: x\n", "unsupported top-level key: dependencies"),
                               (good.replace("policy:", "  brand: x\npolicy:"), "unsupported interface key: brand"),
                               (good + "  permissions: all\n", "unsupported policy key: permissions"),
                               (good.replace("true", '"true"'), "allow_implicit_invocation must be boolean"),
                               (good + "  products: [chatgpt]\n", "products must list CHAT, CODEX or HERMES"),
                               (good.replace('  display_name: "Alpha-Skill"\n', ""), "interface.display_name is required"),
                               (good.replace('"Synthetic skill"', '""'), "interface.short_description is required"),
                               (good.replace('"Use $alpha-skill to run the synthetic task."', "42"), "default_prompt must be one nonblank string"),
                               (good.replace('"Synthetic skill"', "|\n    multi"), "block scalars"),
                               (good.replace("  display_name", "\tdisplay_name"), "tab indentation"),
                               ("interface: flat\n", "interface must be a mapping"),
                               (good.replace("policy:\n", "policy: none\n").replace("  allow_implicit_invocation: true\n", ""), "policy must be a mapping"),
                               ("interface:\n  icons:\n    small: x.svg\n", "nesting deeper"),
                               (good.replace("policy:", "  brand_color: blue\npolicy:"), "invalid interface.brand_color")):
            with self.subTest(fragment=fragment):
                path.write_text(text, encoding="utf-8")
                self.assertRejected(fragment)
        path.write_text(good.replace("true", "null") + "  products: [CODEX, CHAT]\n", encoding="utf-8")
        self.assertValid()

    def test_openai_icon_paths_are_relative_to_skill(self):
        path = self.root / "skills/alpha-skill/agents/openai.yaml"
        path.write_text(openai_text("alpha-skill").replace("policy:", "  icon_small: assets/small.svg\npolicy:"), encoding="utf-8")
        self.assertRejected("missing local file: assets/small.svg")
        self.write("skills/alpha-skill/assets/small.svg", "<svg xmlns=\"http://www.w3.org/2000/svg\"/>\n")
        self.assertValid()

    def test_skill_layout(self):
        self.write("skills/alpha-skill/nested/SKILL.md", skill_text("nested"))
        self.assertRejected("one directory below skills/")
        (self.root / "skills/alpha-skill/nested/SKILL.md").unlink()
        self.write("skills/.hidden-skill/SKILL.md", skill_text(".hidden-skill"))
        self.write("skills/.hidden-skill/agents/openai.yaml", openai_text("hidden"))
        self.assertRejected("hidden skill directory is not portable")

    def test_package_without_skills(self):
        for rel in ("skills/alpha-skill", "skills/beta-skill"):
            for path in sorted((self.root / rel).rglob("*"), reverse=True):
                path.rmdir() if path.is_dir() else path.unlink()
            (self.root / rel).rmdir()
        self.change_json("tests/skill-scenarios.json", lambda d: d["cases"][0].update(expected_skills=[]))
        self.assertRejected("package contains no skills")

    def test_agent_brief_frontmatter(self):
        path = self.root / "agents/alpha-agent.md"
        original = path.read_text(encoding="utf-8")
        for text, fragment in ((original.replace('description: "Read-only synthetic reviewer."\n', ""), "description must be a nonblank string"),
                               (original.replace("name: alpha-agent", "name: other-agent"), "name must match"),
                               (original.replace("tools:", "model: opus\ntools:"), "unsupported agent frontmatter key: model"),
                               (original.replace("tools: Read, Grep, Glob, Bash", 'tools: ""'), "tools must be"),
                               (original.replace("tools: Read, Grep, Glob, Bash", "tools: Read, , Bash"), "tools must be"),
                               (original.replace("tools: Read, Grep, Glob, Bash", "tools: 3"), "tools must be"),
                               ("# No frontmatter\n", "must start with a --- frontmatter block")):
            with self.subTest(fragment=fragment):
                path.write_text(text, encoding="utf-8")
                self.assertRejected(fragment)
        for tools in ("[Read, Grep]", "Read, Bash(git:*)"):
            with self.subTest(tools=tools):
                path.write_text(original.replace("Read, Grep, Glob, Bash", tools), encoding="utf-8")
                self.assertValid()
        path.write_text(original.replace("tools: Read, Grep, Glob, Bash\n", ""), encoding="utf-8")
        self.assertValid()

    def test_broken_local_link(self):
        self.write("references/broken.md", "[Missing](absent.md)\n")
        result = self.assertRejected("line 1: missing local file: absent.md")
        self.assertEqual(result["errors"][0]["path"], "references/broken.md")

    def test_missing_anchor(self):
        self.write("references/broken.md", "\n\n[Missing anchor](facts.md#does-not-exist)\n")
        self.assertRejected("line 3: missing local anchor: facts.md#does-not-exist")
        self.write("references/broken.md", "[Upper case](facts.md#F-T-1)\n")
        self.assertRejected("missing local anchor")
        self.write("references/broken.md", "[Explicit](facts.md#f-t-1) and [encoded](facts.md#the%2Drobotstxt%2Dparser)\n")
        self.assertValid()

    def test_same_file_anchor(self):
        path = self.write("references/local.md", "# Present\n\n[Here](#present)\n")
        self.assertValid()
        path.write_text("# Present\n\n[Missing](#absent)\n", encoding="utf-8")
        self.assertRejected("missing local anchor: #absent")

    def test_anchor_only_checked_for_markdown_targets(self):
        self.write("references/code.md", "[Line](../scripts/tool.py#L1)\n")
        self.assertValid()

    def test_links_cannot_escape_root(self):
        (self.work / "outside.md").write_text("# Outside\n", encoding="utf-8")
        self.write("references/broken.md", "[Outside](../../outside.md)\n")
        self.assertRejected("link escapes package")

    def test_unsafe_links(self):
        for link, fragment in (("file:///etc/passwd", "unsupported link scheme"),
                               ("javascript:alert(1)", "unsupported link scheme"),
                               ("/README.md", "unsafe local link"),
                               ("..\\\\README.md", "unsafe local link"),
                               ("<>", "empty link destination")):
            with self.subTest(link=link):
                self.write("references/broken.md", f"[Bad]({link})\n")
                self.assertRejected(fragment)

    def test_reference_definitions_are_checked(self):
        self.write("references/defs.md", "[Text][x]\n\n[x]: missing.md\n")
        self.assertRejected("missing local file: missing.md")
        self.write("references/defs.md", "Note.[^1]\n\n[^1]: Footnote text, not a link.\n\n[x]: <facts.md#facts>\n")
        self.assertValid()

    def test_example_code_and_comments_are_not_links(self):
        self.write("references/code.md", ("`[code](missing.md)`\n\n```md\n[example](missing.md)\n```\n\n"
                                          "````\n```\n[nested](missing.md)\n````\n\n   ~~~\n   [tilde](missing.md)\n   ~~~\n\n"
                                          "<!-- [comment](missing.md)\n[still comment](missing.md) -->\n\n"
                                          "\\[escaped\\](missing.md)\n"))
        self.assertValid()

    def test_frontmatter_is_not_scanned_for_links(self):
        self.write("references/front.md", "---\nsee: \"[x](missing.md)\"\n---\n\n# Front\n")
        self.assertValid()

    def test_fixture_markdown_is_not_link_checked(self):
        self.write("tests/fixtures/content/broken-links.md", "[Missing](absent.md) and [anchor](#nowhere)\n")
        self.assertValid()

    def test_excluded_directories_are_ignored(self):
        self.write(".seo-geo-god/reports/report.md", "[Missing](absent.md)\n")
        self.write(".pytest_cache/README.md", "[Missing](absent.md)\n")
        (self.root / "scripts/__pycache__").mkdir()
        (self.root / "scripts/__pycache__/tool.cpython-313.pyc").write_bytes(b"\x00cache")
        (self.root / "scripts/stale.pyc").write_bytes(b"\x00cache")
        (self.root / ".DS_Store").write_bytes(b"\x00")
        result = self.assertValid()
        self.assertNotIn("scripts/stale.pyc", vp.package_files(self.root))
        self.assertEqual(result["stats"]["files"], len(OWNED_FILES) + len(SYNTHETIC_FILES))

    def test_data_files(self):
        cases = (('{"rules": []}', "as_of must be an ISO date"),
                 ('{"as_of": "2026-13-01"}', "as_of must be an ISO date"),
                 ('{"as_of": "2026-11-1"}', "as_of must be an ISO date"),
                 ('{"as_of": 20261101}', "as_of must be an ISO date"),
                 ("[]", "data file must be a JSON object"),
                 ("{", "invalid JSON"),
                 ('{"as_of": "2026-11-01", "as_of": "2026-11-02"}', "duplicate key: as_of"),
                 ("[" * 100000 + "]" * 100000, "invalid JSON"))
        for text, fragment in cases:
            with self.subTest(text=text[:30]):
                self.write("data/extra.json", text)
                self.assertRejected(fragment)
        self.write("data/extra.json", '{"as_of": "2026-11-01"}')
        self.assertValid()

    def test_schema_files(self):
        for text, fragment in (("{", "invalid JSON"), ('{"type": "object"}', "must declare $schema"),
                               ("[]", "schema file must be a JSON object"),
                               ('{"$schema": "https://json-schema.org/draft/2020-12/schema", "as_of": "soon"}', "as_of must be an ISO date")):
            with self.subTest(text=text):
                self.write("schemas/extra.schema.json", text)
                self.assertRejected(fragment)

    def test_template_and_example_json_must_parse(self):
        for rel in ("templates/jsonld/article.json", "examples/audit.json"):
            with self.subTest(rel=rel):
                path = self.write(rel, "{not json")
                self.assertRejected("invalid JSON")
                path.write_text('{"@context": "https://schema.org"}', encoding="utf-8")
                self.assertValid()

    def test_file_size_cap(self):
        path = self.root / "assets/large.bin"
        path.write_bytes(b"a" * vp.MAX_FILE_BYTES)
        self.assertValid()
        path.write_bytes(b"a" * (vp.MAX_FILE_BYTES + 1))
        self.assertRejected("file exceeds the 2 MiB size cap")

    def test_directory_symlink_and_file_symlink(self):
        (self.work / "outside.md").write_text("# Outside\n", encoding="utf-8")
        link = self.root / "references/unsafe.md"
        link.symlink_to(self.work / "outside.md")
        self.assertRejected("symlinks are not permitted")
        link.unlink()
        (self.root / "linked-dir").symlink_to(self.work, target_is_directory=True)
        self.assertRejected("symlinks are not permitted")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "os.mkfifo is not available on this platform")
    def test_special_files_rejected(self):
        os.mkfifo(self.root / "references/pipe")
        self.assertRejected("only regular files and directories are permitted")


class ScenarioTests(TempTree):
    def change_scenarios(self, change):
        self.change_json("tests/skill-scenarios.json", change)

    def test_missing_scenarios_file(self):
        (self.root / "tests/skill-scenarios.json").unlink()
        self.assertRejected("skill scenarios must be a JSON object")

    def test_status_does_not_claim_host_execution(self):
        for status in (None, "agent-host execution passed", ["reviewer fixtures"]):
            with self.subTest(status=status):
                self.change_scenarios(lambda d: d.update(status=status))
                self.assertRejected("without claiming agent-host execution")

    def test_cases_are_typed(self):
        for cases in (None, {}, []):
            with self.subTest(cases=cases):
                self.change_scenarios(lambda d: d.update(cases=cases))
                self.assertRejected("nonempty cases array")
        self.change_scenarios(lambda d: d.update(cases=["not an object"]))
        self.assertRejected("scenario 1 must be an object")

    def test_ids_are_unique_and_fields_nonblank(self):
        self.change_scenarios(lambda d: d["cases"].append(dict(d["cases"][0])))
        self.assertRejected("scenario 3 has missing or duplicate id")
        self.change_scenarios(lambda d: d["cases"].pop())
        for field in ("id", "prompt", "acceptance"):
            for value in (None, " ", ["wrong type"]):
                with self.subTest(field=field, value=value):
                    self.change_scenarios(lambda d: d["cases"][0].update({field: value}))
                    self.assertRejected("missing or duplicate id" if field == "id" else f"needs nonblank {field}")
                    self.change_scenarios(lambda d: d["cases"][0].update({field: "valid"}))
        self.assertValid()

    def test_expected_skills_reference_real_skills(self):
        for expected in (None, "alpha-skill", ["does-not-exist"], [{"wrong": "type"}]):
            with self.subTest(expected=expected):
                self.change_scenarios(lambda d: d["cases"][0].update(expected_skills=expected))
                self.assertRejected("expected_skills must be an array of existing skill names")
        self.change_scenarios(lambda d: d["cases"][0].update(expected_skills=["alpha-skill", "alpha-skill"]))
        self.assertRejected("repeats an expected skill")
        self.change_scenarios(lambda d: d["cases"][0].update(expected_skills=["beta-skill", "alpha-skill"]))
        self.assertValid()


class ArchiveTests(TempTree):
    def zip_tree(self, path, prefix, extra=()):
        with zipfile.ZipFile(path, "w") as bundle:
            for directory in sorted({str(Path(rel).parent) for rel in vp.package_files(self.root)} - {"."}):
                if prefix:
                    bundle.writestr(f"{prefix}{directory}/", "")
            for rel in vp.package_files(self.root):
                bundle.write(self.root / rel, f"{prefix}{rel}")
            for name, data in extra:
                bundle.writestr(name, data)
        return path

    def unsafe_zip(self, names, expected, mode=None):
        path = self.work / "unsafe.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(path, "w") as bundle:
                for name in names:
                    entry = zipfile.ZipInfo(name)
                    if mode is not None:
                        entry.create_system = 3
                        entry.external_attr = mode << 16
                    bundle.writestr(entry, "{}")
        result = vp.validate_archive(path)
        self.assertFalse(result["ok"], result)
        self.assertIn(expected, json.dumps(result["errors"]))
        return result

    def test_unsafe_member_paths(self):
        for name in ("../escape", "/escape", "C:\\escape", "plugin/../escape", "plugin//double", "plugin/./dot", "c:/drive"):
            with self.subTest(name=name):
                self.unsafe_zip([name, "plugin/plugin.json"], "unsafe archive path")

    def test_symlink_and_special_members(self):
        self.unsafe_zip(["plugin/plugin.json", "plugin/link"], "nonregular archive member", stat.S_IFLNK | 0o777)
        self.unsafe_zip(["plugin/plugin.json", "plugin/pipe"], "nonregular archive member", stat.S_IFIFO | 0o644)

    def test_duplicate_members(self):
        self.unsafe_zip(["plugin/plugin.json", "plugin/plugin.json"], "duplicate archive member: plugin/plugin.json")
        self.unsafe_zip(["plugin/plugin.json", "plugin/README.md", "plugin/readme.md"], "case-insensitive duplicate archive member")

    def test_wrapper_rules(self):
        self.unsafe_zip(["one/plugin.json", "two/plugin.json"], "one plugin with at most one wrapper")
        self.unsafe_zip(["outer/seo-geo-god/plugin.json"], "nested under extra wrapper directories")
        self.unsafe_zip(["plugin.json", "other/plugin.json"], "multiple plugin roots")

    def test_excluded_members(self):
        for name in ("plugin/scripts/__pycache__/x.cpython-313.pyc", "plugin/scripts/x.pyc", "plugin/.seo-geo-god/a.json",
                     "plugin/.git/config", "plugin/.DS_Store"):
            with self.subTest(name=name):
                self.unsafe_zip(["plugin/plugin.json", name], "excluded path in archive")

    def test_member_and_size_limits(self):
        with mock.patch.object(vp, "MAX_MEMBERS", 1):
            self.unsafe_zip(["plugin/plugin.json", "plugin/README.md"], "too many members")
        with mock.patch.object(vp, "MAX_ARCHIVE_BYTES", 3):
            self.unsafe_zip(["plugin/plugin.json", "plugin/README.md"], "uncompressed archive exceeds")

    def test_not_a_zip(self):
        path = self.work / "broken.zip"
        path.write_bytes(b"not a zip archive")
        result = vp.validate_archive(path)
        self.assertFalse(result["ok"])
        self.assertIn("cannot read archive", json.dumps(result["errors"]))
        self.assertFalse(vp.validate_archive(self.work / "missing.zip")["ok"])

    def test_wrapped_archive_with_directory_entries(self):
        result = vp.validate_archive(self.zip_tree(self.work / "wrapped.zip", "seo-geo-god/"))
        self.assertTrue(result["ok"], result)
        self.assertGreater(result["stats"]["archive_members"], len(vp.package_files(self.root)))

    def test_direct_root_archive(self):
        result = vp.validate_archive(self.zip_tree(self.work / "direct.zip", ""))
        self.assertTrue(result["ok"], result)

    def test_wrapper_must_equal_plugin_name(self):
        result = vp.validate_archive(self.zip_tree(self.work / "renamed.zip", "other-name/"))
        self.assertFalse(result["ok"])
        self.assertIn("must equal the plugin name", json.dumps(result["errors"]))

    def test_archive_content_is_fully_validated(self):
        path = self.zip_tree(self.work / "hooks.zip", "seo-geo-god/", extra=[("seo-geo-god/hooks/hooks.json", "{}")])
        result = vp.validate_archive(path)
        self.assertFalse(result["ok"])
        self.assertIn("forbidden path", json.dumps(result["errors"]))


class PackagerTests(TempTree):
    def add_junk(self):
        (self.root / "scripts/__pycache__").mkdir()
        (self.root / "scripts/__pycache__/tool.cpython-313.pyc").write_bytes(b"cache")
        (self.root / "scripts/stale.pyc").write_bytes(b"cache")
        self.write(".seo-geo-god/reports/audit.json", "{}")
        self.write(".pytest_cache/v/cache/lastfailed", "{}")
        (self.root / ".DS_Store").write_bytes(b"\x00")

    def test_deterministic_archive_and_exclusions(self):
        self.add_junk()
        first, second = self.work / "out/one.zip", self.work / "out/two.zip"
        result = packager.package_plugin(self.root, first)
        packager.package_plugin(self.root, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(result["sha256"], hashlib.sha256(first.read_bytes()).hexdigest())
        self.assertEqual(result["size_bytes"], first.stat().st_size)
        self.assertTrue(vp.validate_archive(first)["ok"])
        with zipfile.ZipFile(first) as bundle:
            infos = bundle.infolist()
        names = [info.filename for info in infos]
        self.assertEqual(names, sorted(names))
        self.assertEqual(names, ["seo-geo-god/" + rel for rel in vp.package_files(self.root)])
        for info in infos:
            self.assertEqual(info.date_time, (2020, 1, 1, 0, 0, 0))
            self.assertEqual(info.external_attr >> 16, stat.S_IFREG | 0o644)
            self.assertEqual(info.compress_type, zipfile.ZIP_DEFLATED)
        for marker in ("__pycache__", ".pyc", ".seo-geo-god/", ".pytest_cache", ".DS_Store"):
            self.assertFalse(any(marker in name for name in names), marker)
        for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "plugin.json", "LICENSE"):
            self.assertIn("seo-geo-god/" + rel, names)
        self.assertEqual(sorted(p.name for p in (self.work / "out").iterdir()), ["one.zip", "two.zip"])

    def test_replaces_existing_output(self):
        output = self.work / "existing.zip"
        output.write_bytes(b"stale")
        packager.package_plugin(self.root, output)
        self.assertTrue(vp.validate_archive(output)["ok"])

    def test_refuses_output_inside_plugin_dir(self):
        for output in (self.root / "output.zip", self.root / "nested/deeper/output.zip", self.root):
            with self.subTest(output=output):
                with self.assertRaisesRegex(ValueError, "outside the plugin directory"):
                    packager.package_plugin(self.root, output)
        self.assertFalse((self.root / "output.zip").exists())
        self.assertFalse((self.root / "nested").exists())

    def test_stops_on_invalid_source(self):
        self.write("references/broken.md", "[Missing](absent.md)\n")
        output = self.work / "dist/must-not-exist.zip"
        with self.assertRaisesRegex(ValueError, "missing local file"):
            packager.package_plugin(self.root, output)
        self.assertFalse(output.exists())

    def test_failed_archive_validation_leaves_no_files(self):
        output = self.work / "dist/never.zip"
        failure = {"ok": False, "scope": vp.SCOPE, "errors": [{"path": "x", "message": "synthetic failure"}], "stats": {}}
        with mock.patch.object(packager, "validate_archive", return_value=failure):
            with self.assertRaisesRegex(ValueError, "synthetic failure"):
                packager.package_plugin(self.root, output)
        self.assertEqual(list((self.work / "dist").iterdir()), [])

    def test_command_line_entry_points(self):
        output = self.work / "cli.zip"
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = packager.main([str(self.root), "--output", str(output)])
        self.assertEqual(code, 0, stdout.getvalue())
        self.assertTrue(json.loads(stdout.getvalue())["ok"])
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = packager.main([str(self.root), "--output", str(self.root / "inside.zip")])
        self.assertEqual(code, 1)
        self.assertIn("outside the plugin directory", json.loads(stdout.getvalue())["error"])
        for argv, expected in (([str(self.root)], 0), (["--archive", str(output)], 0), ([str(self.work / "absent")], 1)):
            with self.subTest(argv=argv):
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    code = vp.main(argv)
                self.assertEqual(code, expected)
                self.assertEqual(json.loads(stdout.getvalue())["ok"], expected == 0)


def python_files():
    files = []
    for top in ("scripts", "tests"):
        for path in sorted((REAL_ROOT / top).rglob("*.py")):
            relative = path.relative_to(REAL_ROOT)
            if vp.excluded(relative) or relative.parts[:2] == ("tests", "fixtures"):
                continue
            files.append(path)
    return files


def imported_modules(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.module.split(".")[0]


class RealTreeTests(unittest.TestCase):
    FORBIDDEN_MODULES = {"subprocess", "pickle", "tomllib", "yaml", "requests", "bs4", "lxml"}

    def parsed(self):
        for path in python_files():
            yield path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 9))

    def test_python_files_use_python_39_syntax(self):
        files = python_files()
        self.assertIn(REAL_ROOT / "scripts/validate_plugin.py", files)
        for path in files:
            with self.subTest(path=path.relative_to(REAL_ROOT).as_posix()):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 9))

    def test_annotated_modules_postpone_evaluation(self):
        for path, tree in self.parsed():
            annotated = any(isinstance(node, ast.AnnAssign) or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and (node.returns is not None or any(a.annotation is not None for a in
                                 node.args.args + node.args.kwonlyargs + node.args.posonlyargs))
                            for node in ast.walk(tree))
            future = any(isinstance(node, ast.ImportFrom) and node.module == "__future__"
                         and any(alias.name == "annotations" for alias in node.names) for node in tree.body)
            with self.subTest(path=path.relative_to(REAL_ROOT).as_posix()):
                self.assertTrue(future or not annotated, "annotations need `from __future__ import annotations` for Python 3.9")

    def test_no_forbidden_modules_or_dynamic_execution(self):
        for path, tree in self.parsed():
            with self.subTest(path=path.relative_to(REAL_ROOT).as_posix()):
                self.assertFalse(set(imported_modules(tree)) & self.FORBIDDEN_MODULES)
                calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
                self.assertFalse(calls & {"eval", "exec", "__import__"})

    @unittest.skipUnless(hasattr(sys, "stdlib_module_names"), "sys.stdlib_module_names needs Python 3.10+")
    def test_no_third_party_imports(self):
        local = {"seo_geo_lib", "tests", "helpers"}  # helpers: tests/helpers.py contract
        for top in ("scripts", "tests"):
            local.update(path.stem for path in (REAL_ROOT / top).glob("*.py"))
        allowed = set(sys.stdlib_module_names) | local | {"__future__"}
        for path, tree in self.parsed():
            with self.subTest(path=path.relative_to(REAL_ROOT).as_posix()):
                self.assertEqual(sorted(set(imported_modules(tree)) - allowed), [])

    def test_manifests_follow_blueprint(self):
        portable = json.loads((REAL_ROOT / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((REAL_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((REAL_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        keywords = ["seo", "geo", "generative-engine-optimization", "ai-search", "structured-data", "core-web-vitals", "coding-agents"]
        self.assertEqual(set(portable), {"$schema", "name", "version", "description", "author", "license", "keywords", "extensions"})
        self.assertEqual(set(claude), {"name", "version", "description", "author", "keywords", "license", "agents"})
        self.assertEqual(set(codex), {"name", "version", "description", "author", "license", "keywords", "interface", "skills"})
        interface = portable["extensions"]["com.openai"]["interface"]
        for data in (portable, claude, codex):
            self.assertEqual((data["name"], data["version"], data["license"], data["keywords"]), ("seo-geo-god", "1.0.1", "MIT", keywords))
            self.assertEqual(data["description"], portable["description"])
        self.assertLessEqual(len(portable["description"]), 300)
        self.assertEqual(codex["interface"], interface)
        self.assertEqual(codex["skills"], "./skills")
        for data in (portable, claude, codex):
            self.assertEqual(data["author"], {"name": "Andrew Rodriguez"})
        briefs = sorted("./agents/" + p.name for p in (REAL_ROOT / "agents").glob("*.md") if p.name != "README.md")
        self.assertEqual(claude["agents"], briefs)
        self.assertEqual((interface["displayName"], interface["category"], interface["capabilities"]), ("SEO-GEO-god", "Developer Tools", []))
        self.assertLessEqual(len(interface["shortDescription"]), 30)
        self.assertEqual((interface["logo"], interface["composerIcon"]), ("./assets/icon.svg", "./assets/icon.svg"))
        self.assertTrue(1 <= len(interface["defaultPrompt"]) <= 3)
        text = json.dumps([portable, claude, codex]).lower()
        for word in ("guarantee", "generated by"):
            self.assertNotIn(word, text)

    def test_license_files(self):
        self.assertEqual(sorted(p.name for p in (REAL_ROOT / "licenses").iterdir()), sorted(Path(rel).name for rel in vp.LICENSE_FILES))
        for rel, digest in LICENSE_SHA256.items():
            with self.subTest(rel=rel):
                self.assertEqual(hashlib.sha256((REAL_ROOT / rel).read_bytes()).hexdigest(), digest, "license text must stay verbatim")
        for rel, line in COPYRIGHT_LINES.items():
            with self.subTest(rel=rel):
                self.assertIn(line, (REAL_ROOT / rel).read_text(encoding="utf-8"))
        self.assertTrue((REAL_ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License\n\nCopyright (c) 2026 SEO-GEO-god contributors\n"))

    def test_icon_is_a_small_inert_svg(self):
        raw = (REAL_ROOT / "assets/icon.svg").read_text(encoding="utf-8")
        self.assertLess(len(raw.encode("utf-8")), 2048)
        self.assertNotIn("<!DOCTYPE", raw.upper())
        self.assertNotIn("<!ENTITY", raw.upper())
        root = ElementTree.fromstring(raw)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        for element in root.iter():
            tag = element.tag.split("}")[-1]
            self.assertNotIn(tag, {"script", "foreignObject", "image", "text", "a", "style", "use"})
            for attribute in element.attrib:
                name = attribute.split("}")[-1].lower()
                self.assertFalse(name.startswith("on") or name == "href", attribute)

    @unittest.skipUnless((REAL_ROOT / "skills/seo-geo-god/SKILL.md").is_file() and (REAL_ROOT / "scripts/seo_geo_lib/cli.py").is_file(),
                         "real plugin tree incomplete: skills/seo-geo-god/SKILL.md and scripts/seo_geo_lib/cli.py are written by other work packages")
    def test_real_plugin_root_validates(self):
        result = vp.validate_directory(REAL_ROOT)
        self.assertTrue(result["ok"], json.dumps(result["errors"], indent=1))
        self.assertEqual(result["stats"]["skills"], 24)
        self.assertEqual(result["stats"]["agent_briefs"], 6)


if __name__ == "__main__":
    unittest.main()
