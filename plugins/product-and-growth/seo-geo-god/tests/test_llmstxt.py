"""Tests for seo_geo_lib.llmstxt (WP03): llmstxt.org v2 parsing, AGENT001-003/009, drafting."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_llmstxt
import helpers  # noqa: E402
from seo_geo_lib import llmstxt as L  # noqa: E402

CAT = helpers.catalog()
BASE = "https://example.com"
SITE = {"https://example.com/docs/present/", "https://example.com/docs/getting-started",
        "https://example.com/docs/webhooks.html", "https://example.com/docs/api/", "https://example.com/changelog/"}


def setUpModule():
    helpers.block_network()


def parsed(name):
    return L.parse_llms(helpers.read_fixture("llms", name + ".txt"))


def ids(findings):
    return helpers.rule_ids(findings)


class ParseTests(unittest.TestCase):
    def test_valid_v2_structure(self):
        p = parsed("valid")
        self.assertEqual((p["h1"], p["h1_line"]), ("Example Docs", 1))
        self.assertTrue(p["summary"].startswith("Example Docs describes a synthetic invoicing API"))
        self.assertIn("Markdown versions", p["details"])
        self.assertEqual([s["title"] for s in p["sections"]], ["Guides", "Reference", "Optional"])
        self.assertTrue(p["has_optional"])
        self.assertEqual((p["errors"], p["notes"]), ([], []))
        links = p["sections"][0]["links"]
        self.assertEqual(links[0], {"title": "Getting started", "url": "https://example.com/docs/getting-started.md",
                                    "notes": "Create a sandbox account", "line": 13})
        self.assertEqual((links[1]["title"], links[1]["notes"]), ("Webhooks [beta]", None))

    def test_heading_inside_code_fence_is_ignored(self):
        p = L.parse_llms("# Title\n\n````md\n# fake\n```\n## also fake\n````\n\n"
                         "## Real\n\n- [a](https://example.com/a)\n")
        self.assertEqual(p["errors"], [])
        self.assertEqual([s["title"] for s in p["sections"]], ["Real"])
        self.assertNotIn("unclosed code fence", p["notes"])
        unclosed = L.parse_llms("# Title\n\n```\n## hidden\n")
        self.assertIn("unclosed code fence", unclosed["notes"])
        self.assertEqual(unclosed["sections"], [])

    def test_h1_is_the_only_requirement(self):
        p = L.parse_llms("# Only a title\n")
        self.assertEqual(p["errors"], [])
        self.assertIn("no blockquote summary after the H1 (recommended)", p["notes"])
        self.assertIn("no H2 sections with link lists", p["notes"])
        self.assertEqual(ids(L.check_llms(p, CAT)), [])

    def test_missing_h1(self):
        p = parsed("no-h1")
        self.assertIn("missing H1 title (the only required element)", p["errors"])
        self.assertIsNone(p["h1"])
        self.assertEqual(L.parse_llms("")["errors"], ["missing H1 title (the only required element)"])

    def test_hashtag_and_deep_indent_are_not_headings(self):
        self.assertIn("missing H1 title (the only required element)", L.parse_llms("#hashtag\n")["errors"])
        self.assertIn("missing H1 title (the only required element)", L.parse_llms("    # code\n")["errors"])
        self.assertEqual(L.parse_llms("   # Indented title #\n")["h1"], "Indented title")

    def test_h1_must_come_first_and_be_unique(self):
        p = parsed("h1-late")
        self.assertEqual(p["h1"], "Example Docs")
        self.assertTrue(any("content before the H1" in e for e in p["errors"]))
        self.assertTrue(any("more than one H1" in e for e in p["errors"]))
        self.assertEqual(L.parse_llms("#\n")["errors"], ["line 1: the H1 is empty"])

    def test_blockquote_only_directly_after_h1(self):
        p = L.parse_llms("# T\n\nIntro text.\n\n> not a summary\n")
        self.assertIsNone(p["summary"])
        self.assertIn("> not a summary", p["details"])
        p = L.parse_llms("# T\n> line one\n> line two\n")
        self.assertEqual(p["summary"], "line one line two")

    def test_bom_crlf_and_list_markers(self):
        p = L.parse_llms("\ufeff# T\r\n\r\n## S\r\n* [a](https://example.com/a): n\r\n"
                         "+ [b](<https://example.com/b c>)\r\n")
        self.assertEqual(p["h1"], "T")
        self.assertEqual([(x["url"], x["notes"]) for x in p["sections"][0]["links"]],
                         [("https://example.com/a", "n"), ("https://example.com/b c", None)])

    def test_section_notes_and_prose(self):
        p = parsed("no-summary")
        self.assertIn("no blockquote summary after the H1 (recommended)", p["notes"])
        self.assertTrue(any("has no links" in n for n in p["notes"]))
        self.assertEqual(p["sections"][0]["prose"], 1)

    def test_served_as_html_detection(self):
        p = parsed("soft-404")
        self.assertTrue(p["is_html"])
        self.assertIn("content looks like an HTML page, not Markdown (soft 404?)", p["errors"])
        self.assertTrue(L.looks_like_html("\ufeff  <HTML><body></body></html>"))
        self.assertFalse(L.looks_like_html("# Title\n<html> in prose\n"))

    def test_template_example_validates(self):
        path = helpers.TEMPLATES_DIR / "llms.txt.example"
        if not path.is_file():
            self.skipTest("templates/llms.txt.example not present yet")
        p = L.parse_llms(path.read_text(encoding="utf-8"))
        self.assertEqual(p["errors"], [])
        self.assertTrue(p["h1"] and p["summary"] and p["has_optional"])
        found = L.check_llms(p, CAT, base_url=BASE)
        self.assertEqual(ids(found), [])

    def test_hostile_input_bounded(self):
        rng = helpers.seeded_random()
        pool = "#> -[]()\\:`~\n\r *+abc\u2028<"
        for _ in range(200):
            text = "".join(rng.choice(pool) for _ in range(rng.randint(0, 400)))
            L.check_llms(L.parse_llms(text), CAT, base_url=BASE, site_urls=SITE)
        long_label = "# T\n## S\n- [" + "\\[" * 20000 + "](https://example.com/x)\n"
        self.assertEqual(len(L.parse_llms(long_label)["sections"][0]["links"]), 1)


class CheckTests(unittest.TestCase):
    def test_agent001_absent(self):
        found = L.check_llms(None, CAT, present=False)
        self.assertEqual(ids(found), ["AGENT001"])
        self.assertEqual((found[0].severity, found[0].file), ("info", "llms.txt"))
        self.assertIn("Google Search ignores it", found[0].message)
        self.assertEqual(CAT.get("AGENT001").evidence_class, "D")
        self.assertEqual(ids(L.check_llms(parsed("valid"), CAT)), [])

    def test_agent002_structure(self):
        found = L.check_llms(parsed("no-h1"), CAT)
        self.assertEqual(ids(found), ["AGENT002"])
        self.assertEqual(found[0].severity, "warning")
        late = L.check_llms(parsed("h1-late"), CAT)
        self.assertEqual(late[0].line, 1)
        self.assertIn("+1 more", late[0].message)
        html = L.check_llms(parsed("soft-404"), CAT)
        self.assertIn("HTML page", html[0].message)

    def test_agent003_links(self):
        found = L.check_llms(parsed("links"), CAT, base_url=BASE, site_urls=SITE)
        self.assertEqual(ids(found), ["AGENT003"])
        problems = {(x["line"], x["problem"]) for x in found[0].evidence["links"]}
        self.assertEqual(problems, {(7, "relative URL (use an absolute URL)"), (8, "non-http(s) URL"),
                                    (9, "list item is not a Markdown link"), (10, "not found in the site")})
        self.assertEqual(found[0].line, 7)

    def test_agent003_without_site_list_checks_shape_only(self):
        found = L.check_llms(parsed("links"), CAT)
        problems = {x["problem"] for x in found[0].evidence["links"]}
        self.assertNotIn("not found in the site", problems)
        self.assertIn("relative URL (use an absolute URL)", problems)

    def test_markdown_mirrors_resolve_to_pages(self):
        found = L.check_llms(parsed("valid"), CAT, base_url=BASE, site_urls=SITE)
        self.assertEqual(found, [])
        p = L.parse_llms("# T\n## S\n- [x](https://example.com/nothing.md)\n- [y](<https://example.com/a b>)\n"
                         "- [z](https://example.com/a b)\n")
        problems = [x["problem"] for x in L.check_llms(p, CAT, base_url=BASE, site_urls=SITE)[0].evidence["links"]]
        self.assertEqual(problems, ["not found in the site", "URL contains whitespace",
                                    "list item is not a Markdown link"])

    def test_site_comparison_ignores_case_slash_fragment_and_default_port(self):
        p = L.parse_llms("# T\n## S\n- [a](HTTPS://Example.COM:443/docs/present#top)\n"
                         "- [b](https://example.com/docs/getting-started/)\n")
        self.assertEqual(L.check_llms(p, CAT, base_url=BASE, site_urls=SITE), [])

    def test_agent009_llms_full(self):
        found = L.check_llms(parsed("valid"), CAT, full_present=True, file="dist/llms.txt")
        self.assertEqual(ids(found), ["AGENT009"])
        self.assertEqual(found[0].file, "dist/llms-full.txt")
        live = L.check_llms(None, CAT, present=False, full_present=True, url="https://example.com/llms.txt")
        self.assertEqual(ids(live), ["AGENT001", "AGENT009"])
        self.assertEqual(live[1].url, "https://example.com/llms-full.txt")
        self.assertEqual(CAT.get("AGENT009").evidence_class, "D")

    def test_owner_and_schema(self):
        found = (L.check_llms(parsed("links"), CAT, base_url=BASE, site_urls=SITE) +
                 L.check_llms(parsed("no-h1"), CAT) + L.check_llms(None, CAT, present=False, full_present=True))
        for f in found:
            self.assertEqual((CAT.get(f.rule).owner, CAT.get(f.rule).status), ("llmstxt", "v1"))
            self.assertEqual(helpers.validate_schema(f.to_dict(CAT), "finding.schema.json"), [], f.rule)


class DraftTests(unittest.TestCase):
    PAGES = [
        {"url": "https://example.com/docs/b", "title": "B [beta] \\ notes", "description": "", "section": ""},
        {"url": "https://example.com/", "title": "Home", "description": "Synthetic\nhome  page", "section": ""},
        {"url": "https://example.com/docs/a", "title": "", "description": "Alpha docs"},
        {"url": "https://example.com/blog/post", "title": "Post", "description": "A post"},
        {"url": "https://example.com/docs/a", "title": "", "description": ""},
        {"url": "https://example.com/private", "title": "Hidden", "description": "", "noindex": True},
        {"url": "https://example.com/optional/x", "title": "Opt dir", "description": ""},
        {"url": "https://example.com/guide (v2)", "title": "Guide", "description": "", "section": "Guides"},
    ]

    def draft(self, **kw):
        kw.setdefault("title", "Example Site")
        return L.draft_llms(list(self.PAGES), **kw)

    def test_escaping_and_no_invented_text(self):
        text = self.draft()
        self.assertIn("- [B \\[beta\\] \\\\ notes](https://example.com/docs/b)\n", text)
        self.assertIn("- [/docs/a](https://example.com/docs/a): Alpha docs\n", text)
        self.assertIn("- [Home](https://example.com/): Synthetic home page\n", text)
        self.assertIn("- [Opt dir](https://example.com/optional/x)\n", text)
        self.assertEqual(text.count("(https://example.com/docs/a)"), 1)
        self.assertNotIn("Hidden", text)
        self.assertNotIn("\n> ", text)
        self.assertIn("(https://example.com/guide%20%28v2%29)", text)

    def test_grouping_and_order(self):
        text = self.draft()
        headings = [line for line in text.splitlines() if line.startswith("#")]
        self.assertEqual(headings, ["# Example Site", "## Pages", "## Blog", "## Docs", "## Guides",
                                    "## Optional pages"])
        docs = text.split("## Docs\n\n", 1)[1].split("\n\n", 1)[0].splitlines()
        self.assertEqual(docs, ["- [/docs/a](https://example.com/docs/a): Alpha docs",
                                "- [B \\[beta\\] \\\\ notes](https://example.com/docs/b)"])

    def test_optional_prefixes_and_summary(self):
        text = self.draft(summary="  A synthetic\nsite ", optional_urls=["/blog/", "https://example.com/optional/"])
        self.assertTrue(text.startswith("# Example Site\n\n> A synthetic site\n\n## Pages\n"))
        self.assertTrue(text.endswith("## Optional\n\n- [Post](https://example.com/blog/post): A post\n"
                                      "- [Opt dir](https://example.com/optional/x)\n"))
        self.assertNotIn("## Blog", text)

    def test_deterministic_and_round_trips(self):
        first, second = self.draft(), L.draft_llms(list(reversed(self.PAGES)), title="Example Site")
        self.assertEqual(first, second)
        p = L.parse_llms(first)
        self.assertEqual(p["errors"], [])
        labels = [x["title"] for s in p["sections"] for x in s["links"]]
        self.assertIn("B [beta] \\ notes", labels)
        self.assertEqual(ids(L.check_llms(p, CAT, base_url=BASE)), [])

    def test_max_entries_and_title_required(self):
        text = self.draft(max_entries=2)
        self.assertEqual(text.count("\n- ["), 2)
        with self.assertRaises(ValueError):
            L.draft_llms([], title="  \n ")
        self.assertEqual(L.draft_llms([], title="T"), "# T\n")


if __name__ == "__main__":
    unittest.main()
