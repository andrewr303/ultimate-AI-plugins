"""Tests for seo_geo_lib.sections and seo_geo_lib.fidelity (WP05): byte-exact Markdown sections and
the deterministic rewrite fidelity gate (FID001-FID010)."""
from __future__ import annotations

import json
import os
import re
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_*
import helpers  # noqa: E402
from seo_geo_lib import fidelity as F  # noqa: E402
from seo_geo_lib import sections as S  # noqa: E402

CAT = helpers.catalog()
LS = chr(0x2028)  # LINE SEPARATOR: must never act as a line break
BOM = chr(0xFEFF)
CONTENT = helpers.fixture("content")


def setUpModule():
    helpers.block_network()


def markdown_fixtures():
    """Every Markdown file under tests/fixtures/ (content, site-good, site-bad, ...)."""
    return sorted(p for p in helpers.FIXTURES.rglob("*.md") if p.is_file())


def split(text):
    raw, body = S.split_frontmatter(text)
    return raw, body, S.split_sections(body)


def variants(text):
    """The text plus CRLF and lone-CR line-ending variants."""
    lf = text.replace("\r\n", "\n")
    return [text, lf.replace("\n", "\r\n"), lf.replace("\n", "\r")]


class RoundTripTests(unittest.TestCase):
    def test_every_markdown_fixture_round_trips_byte_exactly(self):
        files = markdown_fixtures()
        self.assertGreaterEqual(len(files), 10)
        for path in files:
            for text in variants(path.read_text(encoding="utf-8")):
                with self.subTest(path=path.name, crlf="\r\n" in text, cr="\r" in text):
                    raw, body, secs = split(text)
                    self.assertEqual(raw + body, text)
                    self.assertEqual(S.join_sections(secs), body)
                    self.assertEqual([s.id for s in secs], ["s%02d" % i for i in range(len(secs))])

    def test_empty_body_has_no_sections(self):
        self.assertEqual(S.split_sections(""), [])
        self.assertEqual(S.join_sections([]), "")

    def test_whitespace_only_preamble_is_kept(self):
        secs = S.split_sections("  \n\t\n# A\nbody\n")
        self.assertEqual([(s.id, s.level, s.heading, s.text) for s in secs],
                         [("s00", 0, "", "  \n\t\n"), ("s01", 1, "A", "# A\nbody\n")])

    def test_no_preamble_when_text_starts_with_heading(self):
        secs = S.split_sections("# A\none\n## B\ntwo")
        self.assertEqual([(s.id, s.level, s.heading) for s in secs], [("s00", 1, "A"), ("s01", 2, "B")])
        self.assertEqual(secs[1].text, "## B\ntwo")

    def test_setext_and_hashtag_are_not_headings(self):
        body = "Title\n=====\n\nSub\n---\n\n#hashtag\n####### seven\n"
        secs = S.split_sections(body)
        self.assertEqual(len(secs), 1)
        self.assertEqual(secs[0].level, 0)

    def test_heading_rules(self):
        self.assertEqual(S.heading_of("# C#\n"), (1, "C#"))
        self.assertEqual(S.heading_of("## Prices ##\n"), (2, "Prices"))
        self.assertEqual(S.heading_of("#\tTabbed\r\n"), (1, "Tabbed"))
        self.assertEqual(S.heading_of("###### six"), (6, "six"))
        for line in ("#", "#   ", "####### seven", "#hashtag", " # indented", "\t# tab-indented"):
            with self.subTest(line=line):
                self.assertEqual(S.heading_of(line), (0, ""))

    def test_fences_with_longer_closers(self):
        body = "````\n```\n# not a heading\n```\n## still fenced\n````\n# Real\nx\n"
        secs = S.split_sections(body)
        self.assertEqual([s.heading for s in secs], ["", "Real"])
        self.assertEqual(S.join_sections(secs), body)

    def test_tilde_fence_needs_same_char_and_length(self):
        body = "~~~~\n~~~\n```\n# inside\n~~~~~\n# After\n"
        self.assertEqual([s.heading for s in S.split_sections(body)], ["", "After"])

    def test_fence_with_info_string_does_not_close(self):
        body = "```\n```js\n# inside\n```\n# After\n"
        self.assertEqual([s.heading for s in S.split_sections(body)], ["", "After"])

    def test_unclosed_fence_runs_to_end(self):
        secs = S.split_sections("# A\n```\n# hidden\n## hidden too\n")
        self.assertEqual([s.heading for s in secs], ["A"])

    def test_crlf_headings_and_lone_cr(self):
        crlf = "intro\r\n# One\r\nbody\r\n## Two\r\n"
        secs = S.split_sections(crlf)
        self.assertEqual([s.heading for s in secs], ["", "One", "Two"])
        self.assertTrue(secs[1].text.endswith("\r\n"))
        self.assertEqual(S.join_sections(secs), crlf)
        cr = "intro\r# One\rbody\r"
        self.assertEqual([s.heading for s in S.split_sections(cr)], ["", "One"])

    def test_line_separator_is_not_a_line_break(self):
        body = "intro" + LS + "# not a heading\n# Real\n"
        secs = S.split_sections(body)
        self.assertEqual([s.heading for s in secs], ["", "Real"])
        self.assertEqual(S.lines(body), ["intro" + LS + "# not a heading\n", "# Real\n"])

    def test_word_count(self):
        sec = S.split_sections("# Hinge care\nWipe the pin, twice.\n")[0]
        self.assertEqual(sec.word_count, len(re.findall(r"\w+", sec.text)))
        self.assertEqual(sec.word_count, 6)

    def test_fixture_structure(self):
        _, _, secs = split(helpers.read_fixture("content", "guide.md"))
        self.assertEqual([(s.id, s.level, s.heading) for s in secs],
                         [("s00", 0, ""), ("s01", 1, "Widget care guide"), ("s02", 2, "Cleaning"),
                          ("s03", 2, "Prices"), ("s04", 3, "Footnotes in C#"), ("s05", 2, "Trailing whitespace")])
        edge = S.split_sections(helpers.read_fixture("content", "edge-cases.md"))
        self.assertEqual([(s.level, s.heading) for s in edge],
                         [(0, ""), (1, "C#"), (1, "Tab after the hashes still makes a heading"), (2, "Closing hashes")])
        self.assertTrue(edge[-1].text.endswith("# so this is not a heading\n"))

    def test_seeded_random_documents_round_trip(self):
        rnd = helpers.seeded_random()
        pieces = ["# H", "## Sub ##", "#tag", "####### x", "```", "````", "~~~", "~~~~~", "```js", "Title", "===",
                  "---", "text with words", "", "  ", "\t", "# C#", LS + "# glued", "| a | b |", "> quote", "#"]
        endings = ["\n", "\r\n", "\r"]
        for _ in range(200):
            body = "".join(rnd.choice(pieces) + rnd.choice(endings) for _ in range(rnd.randint(0, 30)))
            if rnd.random() < 0.3:
                body = body.rstrip("\r\n")
            secs = S.split_sections(body)
            self.assertEqual(S.join_sections(secs), body)
            self.assertEqual([s.id for s in secs], ["s%02d" % i for i in range(len(secs))])
            for s in secs[1:]:
                self.assertEqual(S.heading_of(S.lines(s.text)[0]), (s.level, s.heading))
            for s in secs:
                self.assertEqual(s.word_count, len(re.findall(r"\w+", s.text)))


class FrontmatterTests(unittest.TestCase):
    def test_yaml_and_toml_are_lossless(self):
        for name, delim in (("guide.md", "---"), ("toml-note.md", "+++")):
            text = helpers.read_fixture("content", name)
            raw, body = S.split_frontmatter(text)
            self.assertTrue(raw.startswith(delim))
            self.assertTrue(raw.rstrip("\r\n").endswith(delim))
            self.assertEqual(raw + body, text)

    def test_cases(self):
        cases = [
            ("---\na: 1\n---\nbody\n", "---\na: 1\n---\n"),
            ("---\n---\nbody", "---\n---\n"),
            ("---\na: 1\n---", "---\na: 1\n---"),
            ("+++\ntitle = 'x'\n+++\r\nbody", "+++\ntitle = 'x'\n+++\r\n"),
            ("---\r\na: 1\r\n---\r\nbody", "---\r\na: 1\r\n---\r\n"),
            (BOM + "---\na: 1\n---\nbody", BOM + "---\na: 1\n---\n"),
            ("---\na: 1\n----\nbody\n", ""),
            ("---\na: 1\n+++\nbody\n", ""),
            ("---\nno closing delimiter\n", ""),
            ("text\n---\na: 1\n---\n", ""),
            (" ---\na: 1\n---\n", ""),
        ]
        for text, raw in cases:
            with self.subTest(text=text):
                got_raw, body = S.split_frontmatter(text)
                self.assertEqual(got_raw, raw)
                self.assertEqual(got_raw + body, text)

    def test_seeded_random_frontmatter_invariant(self):
        rnd = helpers.seeded_random()
        parts = ["---", "+++", "a: 1", "title = 'x'", "", "----", "# H", "text"]
        for _ in range(200):
            text = "".join(rnd.choice(parts) + rnd.choice(["\n", "\r\n"]) for _ in range(rnd.randint(0, 8)))
            raw, body = S.split_frontmatter(text)
            self.assertEqual(raw + body, text)
            self.assertTrue(raw == "" or raw.startswith(("---", "+++")))


class ReplaceAndDiffTests(unittest.TestCase):
    BODY = "Intro.\n\n# Hinges\nOld text.\n\n## Care\nWipe it.\n"

    def test_replace_section_keeps_other_bytes(self):
        secs = S.split_sections(self.BODY)
        new = S.replace_section(secs, "s02", "## Care\nWipe the pin with a dry cloth.\n")
        self.assertEqual(S.join_sections(new), "Intro.\n\n# Hinges\nOld text.\n\n## Care\nWipe the pin with a dry cloth.\n")
        self.assertEqual([s.id for s in new], ["s00", "s01", "s02"])
        self.assertEqual(new[2].word_count, 8)
        self.assertEqual(secs[2].text, "## Care\nWipe it.\n")  # original list untouched

    def test_replace_without_heading_keeps_metadata(self):
        secs = S.replace_section(S.split_sections(self.BODY), "s00", "Better intro.\n\n")
        self.assertEqual((secs[0].level, secs[0].heading), (0, ""))

    def test_replace_unknown_id_raises_key_error(self):
        secs = S.split_sections(self.BODY)
        with self.assertRaises(KeyError):
            S.replace_section(secs, "s09", "x")
        with self.assertRaises(KeyError):
            S.get_section(secs, "nope")
        self.assertEqual(S.get_section(secs, "s01").heading, "Hinges")

    def test_section_table_lines(self):
        rows = S.section_table(S.split_sections(self.BODY), first_line=5)
        self.assertEqual([(r["id"], r["start_line"]) for r in rows], [("s00", 5), ("s01", 7), ("s02", 10)])
        self.assertEqual(set(rows[0]), {"id", "heading", "level", "word_count", "start_line"})

    def test_clean_rewrite(self):
        original = "## Care\nWipe it.\n\n"
        cases = [
            ("```markdown\n## Care\nWipe the pin.\n```", "## Care\nWipe the pin.\n\n"),
            ("~~~\n## Care\nWipe the pin.\n~~~\n", "## Care\nWipe the pin.\n\n"),
            ("\n\n## Care\nWipe the pin.   \n", "## Care\nWipe the pin.\n\n"),
            ("```\n## Care\n```\nmore\n", "```\n## Care\n```\nmore\n\n"),
        ]
        for rewritten, expected in cases:
            with self.subTest(rewritten=rewritten):
                self.assertEqual(S.clean_rewrite(original, rewritten), expected)
        self.assertEqual(S.clean_rewrite("\n\nIntro\n", "Better intro"), "\n\nBetter intro\n")
        code_only = "```bash\nrun\n```\n"
        self.assertEqual(S.clean_rewrite(code_only, "```bash\nrun --fast\n```"), "```bash\nrun --fast\n```\n")
        self.assertEqual(S.clean_rewrite("  \n", "anything"), "  \n")

    def test_clean_rewrite_keeps_joins_byte_exact(self):
        secs = S.split_sections(self.BODY)
        cleaned = S.clean_rewrite(secs[1].text, "```\n# Hinges\nNew text.\n```")
        joined = S.join_sections(S.replace_section(secs, "s01", cleaned))
        self.assertEqual(joined, "Intro.\n\n# Hinges\nNew text.\n\n## Care\nWipe it.\n")

    def test_unified_diff(self):
        self.assertEqual(S.unified("same\n", "same\n", "a.md"), "")
        diff = S.unified("a\nb\n", "a\nc\n", "docs/page.md")
        self.assertTrue(diff.startswith("--- a/docs/page.md\n+++ b/docs/page.md\n"))
        self.assertIn("-b\n+c\n", diff)
        tail = S.unified("a\nb", "a\nc", "x.md")
        self.assertIn("\\ No newline at end of file\n", tail)
        self.assertTrue(tail.endswith("\n"))


ORIGINAL = """## Hinge test

The hinge test opens and closes the lid until the pin wears out. See the
[protocol](https://example.org/protocol) and <https://example.org/raw.csv>.
It costs $1,185 and passed 40% of runs in 2025; this is one snapshot.

| Model | Cycles |
| --- | --- |
| A | 12 |

```bash
bench --runs 999 https://example.org/inside-code
```
"""


def violations(original, rewrite, **kw):
    return F.check_fidelity(original, rewrite, **kw)["violations"]


class FidelityTests(unittest.TestCase):
    def test_identical_rewrite_passes(self):
        result = F.check_fidelity(ORIGINAL, ORIGINAL)
        self.assertEqual((result["passed"], result["violations"]), (True, []))
        stats = result["stats"]
        self.assertEqual(stats["links"], {"original": 2, "rewrite": 2})
        self.assertEqual(stats["table_rows"], {"original": 3, "rewrite": 3})
        self.assertEqual(stats["code_blocks"], {"original": 1, "rewrite": 1})
        self.assertEqual((stats["min_ratio"], stats["max_ratio"], stats["min_words"]), (0.8, 1.6, 20))
        self.assertEqual(stats["ratio"], 1.0)

    def test_every_fixture_is_faithful_to_itself(self):
        for path in sorted(CONTENT.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertTrue(F.check_fidelity(text, text)["passed"])

    def test_heading_changed(self):
        rewrite = ORIGINAL.replace("## Hinge test", "## How the hinge test works")
        self.assertEqual(violations(ORIGINAL, rewrite), ["heading_changed"])
        added = ORIGINAL.replace("| Model", "### Results\n\n| Model", 1)
        self.assertIn("heading_changed", violations(ORIGINAL, added))

    def test_heading_check_skipped_without_original_heading(self):
        body = "Plain intro paragraph with enough words to read naturally here.\n"
        self.assertEqual(violations(body, "# New heading\n" + body), [])

    def test_html_headings_compared(self):
        a = "<h2>Hinge test</h2><p>Text.</p>"
        self.assertEqual(violations(a, "<h2>Hinge tests</h2><p>Text.</p>"), ["heading_changed"])
        self.assertEqual(violations(a, "<h2>Hinge test</h2><p>Better text.</p>"), [])

    def test_links_removed_and_added(self):
        rewrite = (ORIGINAL.replace("[protocol](https://example.org/protocol)", "protocol")
                   .replace("<https://example.org/raw.csv>", "[raw](https://example.org/raw.csv) and "
                            "https://example.net/new."))
        self.assertEqual(violations(ORIGINAL, rewrite),
                         ["link_removed:https://example.org/protocol", "link_added:https://example.net/new"])

    def test_link_kinds_extracted(self):
        text = ('See [a](https://example.com/a "Title"), ![img](/img/b.png), <https://example.com/c>, '
                'https://example.com/d.; <a href="https://example.com/e">e</a> <a href=\'/f\'>f</a> '
                '[ref][1] and [x](<https://example.com/g>)\n\n[1]: https://example.com/h "Ref"\n')
        self.assertEqual(F.extract_links(text), {
            "https://example.com/a", "/img/b.png", "https://example.com/c", "https://example.com/d",
            "https://example.com/e", "/f", "https://example.com/g", "https://example.com/h"})

    def test_reference_definition_removed(self):
        a = "Read the [guide][g].\n\n[g]: https://example.com/guide\n"
        b = "Read the guide.\n"
        self.assertEqual(violations(a, b), ["link_removed:https://example.com/guide"])

    def test_numbers_removed_and_added_with_normalization(self):
        rewrite = ORIGINAL.replace("$1,185", "about $1,200").replace("40%", "forty percent")
        self.assertEqual(violations(ORIGINAL, rewrite),
                         ["number_removed:1185", "number_removed:40%", "number_added:1200"])
        self.assertEqual(F.extract_numbers("$1,185 and 40% and 3.5 and " + chr(0x20AC) + "7"), {"1185", "40%", "3.5", "7"})

    def test_numbers_in_code_and_urls_are_ignored(self):
        rewrite = ORIGINAL.replace("It costs", "The test costs")
        self.assertEqual(violations(ORIGINAL, rewrite), [])
        _, rest = F.split_code(ORIGINAL)
        nums = F.extract_numbers(rest)
        self.assertNotIn("999", nums)
        self.assertEqual(nums, {"1185", "40%", "2025", "12"})

    def test_numbers_sorted_as_strings(self):
        a = "Runs: 194 and 47 passed, with enough surrounding words to stay above the length floor here."
        b = "Runs passed, with enough surrounding words to stay above the length floor here today."
        self.assertEqual([v for v in violations(a, b) if v.startswith("number_removed")],
                         ["number_removed:194", "number_removed:47"])

    def test_table_rows_decreased(self):
        rewrite = ORIGINAL.replace("| A | 12 |\n", "")
        self.assertEqual(violations(ORIGINAL, rewrite), ["number_removed:12", "table_rows_decreased"])
        more = ORIGINAL.replace("| A | 12 |\n", "| A | 12 |\n| B | 12 |\n")
        self.assertEqual(violations(ORIGINAL, more), [])
        html_a = "<table><tr><td>A</td></tr><tr><td>B</td></tr></table>"
        self.assertEqual(violations(html_a, "<table><tr><td>A</td></tr></table>"), ["table_rows_decreased"])

    def test_code_block_changed(self):
        rewrite = ORIGINAL.replace("--runs 999", "--runs 998")
        self.assertEqual(violations(ORIGINAL, rewrite), ["code_block_changed"])
        moved = ORIGINAL.replace("```bash", "Run this:\n\n```bash")
        self.assertEqual(violations(ORIGINAL, moved), [])
        self.assertEqual(violations("<pre>a = 1</pre> text", "<pre>a = 2</pre> text"), ["code_block_changed"])

    def test_length_bounds(self):
        twenty = " ".join("w%d" % i for i in range(20))
        self.assertEqual(F.check_fidelity(twenty, " ".join(twenty.split()[:16]))["violations"], [])  # ratio 0.8
        self.assertEqual(violations(twenty, " ".join(twenty.split()[:15])), ["too_short"])
        self.assertEqual(violations(twenty, twenty + " " + " ".join("x%d" % i for i in range(12))), [])  # 1.6
        self.assertEqual(violations(twenty, twenty + " " + " ".join("x%d" % i for i in range(13))), ["too_long"])
        nineteen = " ".join(twenty.split()[:19])
        result = F.check_fidelity(nineteen, "w0")
        self.assertEqual((result["violations"], result["stats"]["ratio_checked"]), ([], False))
        self.assertEqual(violations(twenty, " ".join(twenty.split()[:15]), min_ratio=0.7), [])
        self.assertEqual(violations(twenty, twenty + " x y z", max_ratio=1.1), ["too_long"])
        self.assertEqual(violations(nineteen, "w0", min_words=5), ["too_short"])

    def test_superlatives(self):
        base = "The hinge lasts for many cycles in normal use and in lab tests with a slow motor rig."
        self.assertEqual(violations(base, base.replace("The hinge", "The best hinge")), ["superlative_added:best"])
        self.assertEqual(violations(base, base + " Follow best practices."), [])
        self.assertEqual(violations("The best hinge " + base, "The best hinge really " + base), [])
        self.assertEqual(violations(base, base.replace("lasts", "is leading to fewer repairs and lasts")), [])
        self.assertEqual(violations(base, base + " It is stellar.", superlatives=["stellar"]),
                         ["superlative_added:stellar"])
        self.assertEqual(violations(base, base.replace("The hinge", "The best hinge"), superlatives=[]), [])

    def test_caveats(self):
        base = ("The hinge figure comes from one snapshot of a bench test and results may vary in homes, "
                "so treat it as an estimate.")
        self.assertEqual(violations(base, base.replace("one snapshot of ", "")), ["caveat_removed:one snapshot"])
        self.assertEqual(violations(base, base.replace("results may vary", "Results May Vary")), [])
        self.assertEqual(violations(base, base.replace("as an estimate", "as fact"), caveats=["as an estimate"]),
                         ["caveat_removed:as an estimate"])

    def test_violation_order(self):
        a = ("## Hinge\n\nSee [a](https://example.com/a). It cost $5 in 2025 and results may vary.\n\n"
             "| x |\n| y |\n\n```\ncode\n```\n" + " ".join("w%d" % i for i in range(30)) + "\n")
        b = ("## Hinges\n\nSee [b](https://example.com/b). The best one cost $6 in 2025.\n\n| x |\n\n```\ncode2\n```\n")
        self.assertEqual(violations(a, b), [
            "heading_changed", "link_removed:https://example.com/a", "link_added:https://example.com/b",
            "number_removed:5", "number_added:6", "table_rows_decreased", "code_block_changed", "too_short",
            "superlative_added:best", "caveat_removed:results may vary"])

    def test_defaults_come_from_thresholds_json(self):
        limits = json.loads((helpers.DATA_DIR / "thresholds.json").read_text(encoding="utf-8"))["fidelity"]
        stats = F.check_fidelity("a", "a")["stats"]
        self.assertEqual((stats["min_ratio"], stats["max_ratio"], stats["min_words"]),
                         (limits["min_ratio"], limits["max_ratio"], limits["min_words"]))


class FidelityScaleTests(unittest.TestCase):
    def test_many_links_stay_linear(self):
        page = "\n".join("Line %d with [link](https://example.com/%d) and 40%% of $5." % (i, i) for i in range(4000))
        start = time.perf_counter()
        result = F.check_fidelity(page, page.replace("https://example.com/7)", "https://example.net/7)"))
        self.assertLess(time.perf_counter() - start, 10.0)
        self.assertEqual(result["violations"], ["link_removed:https://example.com/7", "link_added:https://example.net/7"])


class WholePageNegativeTests(unittest.TestCase):
    """Synthetic whole-page rewrites that lose substance must be rejected (eGEOagents lesson)."""

    EXPECTED = {
        "page-rewrite-drops-date": ["number_removed:10", "number_removed:2026"],
        "page-rewrite-drops-source": ["link_removed:https://example.org/labs/hinge-2025.csv",
                                      "link_removed:https://example.org/labs/hinge-protocol"],
        "page-rewrite-drops-row": ["number_removed:15", "number_removed:24000", "number_removed:4",
                                   "table_rows_decreased"],
        "page-rewrite-hype": ["superlative_added:best", "superlative_added:industry-leading",
                              "superlative_added:most reliable", "superlative_added:ultimate",
                              "caveat_removed:not a guarantee", "caveat_removed:one snapshot",
                              "caveat_removed:results may vary"],
    }

    def setUp(self):
        self.original = helpers.read_fixture("content", "fidelity", "original.md")

    def test_faithful_rewrite_passes(self):
        result = F.check_fidelity(self.original, helpers.read_fixture("content", "fidelity", "rewrite-faithful.md"))
        self.assertEqual((result["passed"], result["violations"]), (True, []))

    def test_every_negative_is_rejected(self):
        names = sorted(p.stem for p in (CONTENT / "fidelity").glob("page-rewrite-*.md"))
        self.assertEqual(names, sorted(self.EXPECTED))
        for name in names:
            with self.subTest(name=name):
                result = F.check_fidelity(self.original, helpers.read_fixture("content", "fidelity", name + ".md"))
                self.assertFalse(result["passed"])
                self.assertEqual(result["violations"], self.EXPECTED[name])


class FindingMappingTests(unittest.TestCase):
    def test_rule_for_every_code(self):
        self.assertEqual({F.rule_for(code) for code in F.VIOLATION_RULES}, {"FID%03d" % i for i in range(1, 11)})
        self.assertEqual(F.rule_for("link_removed:https://example.com/a"), "FID002")
        self.assertEqual(F.rule_for("too_long"), "FID008")
        with self.assertRaises(KeyError):
            F.rule_for("made_up:1")
        for rid in F.VIOLATION_RULES.values():
            rule = CAT.get(rid)
            self.assertEqual((rule.owner, rule.status, rule.severity), ("fidelity", "v1", "error"))

    def test_findings_from_result(self):
        original = helpers.read_fixture("content", "fidelity", "original.md")
        result = F.check_fidelity(original, helpers.read_fixture("content", "fidelity", "page-rewrite-drops-row.md"))
        findings = F.fidelity_findings(result, file="docs/hinge.md", catalog=CAT)
        self.assertEqual([f.rule for f in findings], ["FID004", "FID004", "FID004", "FID006"])
        self.assertEqual(len({f.fingerprint() for f in findings}), 4)
        for f in findings:
            self.assertEqual((f.severity, f.file), ("error", "docs/hinge.md"))
            self.assertEqual(helpers.validate_schema(f.to_dict(CAT), "finding.schema.json"), [])
        self.assertEqual(F.fidelity_findings({"passed": True, "violations": []}), [])

    def test_length_finding_carries_ratio(self):
        twenty = " ".join("w%d" % i for i in range(20))
        result = F.check_fidelity(twenty, "w0 w1")
        (finding,) = F.fidelity_findings(result)
        self.assertEqual(finding.rule, "FID008")
        self.assertEqual(finding.evidence["allowed"], [0.8, 1.6])
        self.assertEqual(finding.evidence["ratio"], 0.1)


if __name__ == "__main__":
    unittest.main()
