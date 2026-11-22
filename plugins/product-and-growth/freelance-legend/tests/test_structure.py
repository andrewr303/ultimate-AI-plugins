"""Structural checks for the freelance-legend plugin package.

Run from the plugin root:  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
FRONTMATTER = re.compile(r"\A---\nname: ([a-z0-9-]+)\ndescription: \"(.+?)\"\n---\n", re.S)
REL_LINK = re.compile(r"`((?:\.\./)+[\w./-]+\.(?:md|txt|py))`")
EXPECTED = {
    "freelance-legend", "job-scanner", "job-vetting", "proposal-writer", "pricing-scoping",
    "client-communications", "interview-prep", "contracts-scope", "profile-optimizer", "case-studies",
    "portfolio-website", "cold-outreach", "pipeline-tracker",
}


class StructureTests(unittest.TestCase):
    def test_manifests_parse_and_agree(self):
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        generic = json.loads((ROOT / "plugin.json").read_text())
        self.assertEqual(claude["name"], "freelance-legend")
        self.assertEqual(claude["name"], generic["name"])
        self.assertEqual(claude["version"], generic["version"])

    def test_expected_skills_present(self):
        self.assertEqual({p.name for p in SKILLS}, EXPECTED)

    def test_frontmatter(self):
        for skill in SKILLS:
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            m = FRONTMATTER.match(text)
            self.assertIsNotNone(m, f"{skill.name}: bad frontmatter")
            self.assertEqual(m.group(1), skill.name)
            desc = m.group(2)
            self.assertLessEqual(len(desc), 1024, f"{skill.name}: description too long")
            self.assertRegex(desc, r"\bUse (?:for|when)\b", f"{skill.name}: no trigger cases")
            self.assertRegex(desc, r"\bNot (?:for|legal)\b", f"{skill.name}: no negative cases")

    def test_relative_references_resolve(self):
        for md in list((ROOT / "skills").rglob("*.md")) + list((ROOT / "agents").glob("*.md")):
            for ref in REL_LINK.findall(md.read_text(encoding="utf-8")):
                self.assertTrue((md.parent / ref).resolve().exists(), f"{md.relative_to(ROOT)} -> {ref}")

    def test_public_package_ships_only_fixture_profile_and_seeds(self):
        for name in ("andrew-profile.md", "scanner-seed-ids.txt"):
            self.assertFalse((ROOT / "references" / name).exists(), name)
        self.assertIn("Fictional", (ROOT / "examples" / "profile.example.md").read_text())
        seed = (ROOT / "examples" / "scanner-seed.example.txt").read_text()
        self.assertRegex(seed, r"(?m)^fixture-")
        self.assertFalse((ROOT / "research" / "2026-11-04" / "source-material").exists())

    def test_agent_frontmatter(self):
        for agent in (ROOT / "agents").glob("*.md"):
            text = agent.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\nname: "), agent.name)
            self.assertIn("\ndescription: ", text.split("---")[1])


if __name__ == "__main__":
    unittest.main()
