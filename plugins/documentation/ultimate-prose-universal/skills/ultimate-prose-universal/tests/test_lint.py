"""Boundary and CLI tests for the optional advisory scanner."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lint.py"
sys.path.insert(0, str(SCRIPT.parent))
import lint


class ScannerTests(unittest.TestCase):
    def run_cli(self, *args, data=b""):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=data,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_protected_sources_and_exact_unicode_positions(self):
        text = ('> This changes everything.\r\nLazy quotation continuation.\r\n\r\n'
                '```txt\r\nThis changes everything.\r\n```\r\n'
                '`This changes everything` “This changes everything.”\r\n'
                '«This changes everything.» 「This changes everything.」\r\n'
                'Café 🐈: This changes everything.\r\n')
        masked = lint.mask_sources(text)
        self.assertEqual(len(masked), len(text))
        self.assertEqual([(i, c) for i, c in enumerate(masked) if c in "\r\n"],
                         [(i, c) for i, c in enumerate(text) if c in "\r\n"])
        findings = lint.check(text)
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.offset_start, text.rindex("This changes everything"))
        self.assertEqual(finding.line, 9)
        self.assertEqual(finding.column, 9)
        self.assertEqual(text[finding.offset_start:finding.offset_end], finding.snippet)
        self.assertEqual(lint.check("First line.\rThis changes everything.")[0].line, 2)

    def test_include_quotes_keeps_code_and_technical_tokens_protected(self):
        text = ('"This changes everything."\n> This changes everything.\n\n'
                '`This changes everything`\n> ```txt\n> This changes everything.\n> ```\n'
                'https://example.test/“world” a.b@example.test /srv/“data” ./“data” C:\\“data”\\file\n')
        findings = lint.check(text, include_quotes=True, straight_quotes=True)
        self.assertEqual([f.rule_id for f in findings], ["claim-scope", "claim-scope"])

    def test_single_quotes_contractions_and_unclosed_fences(self):
        text = "'This changes everything.' ‘This changes everything.’ It's a draft.\n"
        self.assertFalse(lint.check(text))
        self.assertEqual(len(lint.check(text, include_quotes=True)), 2)
        for fence in ("```", "~~~~"):
            self.assertFalse(lint.check(fence + "\nThis changes everything.\n"))

    def test_masks_cannot_join_a_signal_or_duplicate(self):
        text = 'This changes `source` everything.\nThis changes "source" everything.\n'
        self.assertFalse(lint.check(text))
        self.assertFalse(lint.check('The draft is ready today. "Quoted source." The draft is ready today.'))

    def test_small_contextual_signals_are_advisory(self):
        text = ("In today's world, we need a plan. The uncomfortable truth is we need more time. "
                "The world's best system is guaranteed to work. Only time will tell.")
        findings = lint.check(text)
        self.assertEqual(len(findings), 5)
        self.assertTrue(all(f.severity == "REVIEW" and not f.convention for f in findings))
        self.assertIn("cannot judge", findings[2].message)

    def test_no_vocabulary_typography_or_cultural_defaults(self):
        text = ("Robust standard errors matter. Leverage rose. Moreover, it’s a useful framework — "
                "a critical one. Fuck, that was hard. Hello, dear friend.\n"
                "The question remains open. Can you meet? Approved. Ship it.")
        self.assertFalse(lint.check(text, genre="email", tone="warm, bold, playful"))
        self.assertFalse(lint.check("The sun rises. The sun rises."))  # short repetition can be deliberate

    def test_repeated_framing_and_adjacent_duplicate(self):
        text = ("The key takeaway is timing. The key takeaway is staffing.\n"
                "The report will arrive tomorrow. The report will arrive tomorrow.")
        findings = lint.check(text)
        self.assertEqual([f.rule_id for f in findings], ["repeated-framing", "adjacent-duplicate"])
        self.assertEqual(findings[1].snippet, "The report will arrive tomorrow.")
        self.assertFalse(lint.check("The key takeaway is timing."))

    def test_strict_only_applies_to_selected_conventions(self):
        text = "This changes everything. It’s ready — send it."
        normal = self.run_cli("--strict", data=text.encode())
        self.assertEqual(normal.returncode, 0)
        for option in ("--straight-quotes", "--no-em-dash"):
            selected = self.run_cli(option, "--strict", "--json", data=text.encode())
            self.assertEqual(selected.returncode, 1)
            findings = json.loads(selected.stdout)["findings"]
            self.assertTrue(all(f["severity"] == "REVIEW" for f in findings))
            self.assertTrue(any(f["convention"] for f in findings))
            self.assertEqual(self.run_cli(option, data=text.encode()).returncode, 0)

    def test_json_context_and_file_are_preserved(self):
        data = "Café 🐈\r\nThis changes everything.\r\n".encode()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "draft.txt"
            path.write_bytes(data)
            result = self.run_cli(str(path), "--json", "--genre", "fiction", "--tone", "dry and lyrical")
            self.assertEqual(path.read_bytes(), data)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["context"]["tone"], "dry and lyrical")
        self.assertEqual(payload["context"]["genre"], "fiction")
        self.assertEqual(payload["findings"][0]["offset_start"], data.decode().index("This"))
        self.assertEqual(set(payload), {"schema_version", "context", "findings"})

    def test_attribution_actor_and_residue_constructions(self):
        text = ("Studies show founders sleep less. The data tells us to wait. "
                "Here's the revised version of the memo.")
        self.assertEqual([f.rule_id for f in lint.check(text)],
                         ["vague-attribution", "abstract-actor", "assistant-residue"])
        cited = ("Studies show founders sleep less (Lee, 2024). "
                 'Research suggests the same in [the survey](https://example.test/s). '
                 "The data shows a 12% drop.")
        self.assertFalse(lint.check(cited))
        self.assertFalse(lint.check('The memo quoted "experts say" as a cliché.'))

    def test_earned_devices_are_not_findings(self):
        for text in ("Before reopening traffic, verify the certificate, the DNS record, and the health check.",
                     "At dusk, the blue pigment almost disappears. Step sideways and the silver ground "
                     "catches the room's light, returning the river a piece at a time.",
                     "The limit applies per account, not per user."):
            with self.subTest(text=text):
                self.assertFalse(lint.check(text))

    def test_cli_help_errors_and_empty_input(self):
        self.assertEqual(self.run_cli("--help").returncode, 0)
        self.assertEqual(self.run_cli("-").returncode, 0)
        plain, detect = self.run_cli(), self.run_cli("--detect")
        self.assertEqual(plain.stdout, detect.stdout)
        for args, data in ((["--genre", "unknown"], b""), (["--json", "--detect"], b""),
                           (["/missing/file.txt"], b""), ([], b"\xff")):
            result = self.run_cli(*args, data=data)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn(b"Traceback", result.stderr)

    def rules(self, text, **options):
        return [f.rule_id for f in lint.check(text, **options)]

    def test_staged_constructions_and_their_ordinary_counterparts(self):
        text = ("Great question! Here's the thing. Not the technology. The people.\n\n"
                "This does not mean every option is equal. It means nobody checks. I'm not saying docs "
                "don't matter. This shows the importance of testing.\n\n"
                "As of my last knowledge update, the figures are not publicly available.\n\n"
                "The future looks bright.")
        self.assertEqual(self.rules(text), [
            "assistant-residue", "staged-insight", "staged-contrast", "staged-contrast", "unprompted-rebuttal",
            "explained-example", "knowledge-gap", "knowledge-gap", "stock-closer"])
        ordinary = ("Not yet. I'll send it Friday. No problem on the invoice.\n\n"
                    "The limit applies per account, not per person. It's not ready, so it's staying in staging. "
                    "This isn't about blame; I just need the date. Of course, the price depends on volume. "
                    "Certainly the cache helps. Not the first time. We saw the same failure in March and April.\n\n"
                    "The future looks bright for the pilot, but only if testing passes.")
        self.assertFalse(lint.check(ordinary, genre="email"))

    def test_contrast_frames_are_reported_only_when_repeated(self):
        self.assertFalse(lint.check("This isn't just a dashboard; the export also feeds payroll."))
        text = "This isn't just a dashboard. It's not a tool, it's a movement.\n\nIt isn't only a chart."
        findings = lint.check(text)
        self.assertEqual([f.rule_id for f in findings], ["repeated-contrast"])
        self.assertTrue(findings[0].snippet.startswith("It's not a tool"))

    def test_draft_artifacts_are_read_through_quotes_and_links_but_not_code(self):
        text = ('Dear [Your Name], see [TK: launch date] and "[Insert quote here]".\n'
                "Source: [the docs](https://example.test/a?utm_source=chatgpt.com) "
                "contentReference[oaicite:0]{index=0} turn0search3.\nZero\u200bwidth.\n")
        self.assertEqual(self.rules(text), ["open-placeholder", "open-placeholder", "open-placeholder",
                                            "tool-artifact", "tool-artifact", "tool-artifact", "tool-artifact"])
        clean = ("See [Your account](https://example.test) and [Name][ref].\n\n[Name]: https://example.test\n"
                 "`[Your Name]`\n```\n[Insert text] turn0search3 utm_source=chatgpt\n```\nRegular text.\n")
        self.assertFalse(lint.check(clean))
        self.assertFalse(lint.check("\ufeffStarts with a byte order mark."))
        self.assertEqual(self.rules("A stray\ufeff mark."), ["tool-artifact"])

    def test_front_matter_comments_and_ignore_regions_are_protected(self):
        text = ("---\ntitle: This changes everything\n---\n\n"
                "<!-- prose:ignore-start supplied brief -->\nThis changes everything.\n<!-- prose:ignore-end -->\n"
                "<!-- This changes everything -->\nThis changes everything.\n")
        findings = lint.check(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 9)
        self.assertEqual(len(lint.mask_sources(text)), len(text))
        # An unclosed block or region hides nothing.
        self.assertEqual(len(lint.check("---\nThis changes everything.\n")), 1)
        self.assertEqual(len(lint.check("<!-- prose:ignore-start -->\nThis changes everything.\n")), 1)

    def test_label_echo_and_selected_avoid_terms(self):
        text = "- **Performance:** Performance has improved.\n- **Security:** We added encryption.\n"
        findings = lint.check(text)
        self.assertEqual([f.rule_id for f in findings], ["label-echo"])
        text = "We leveraged it. Delving deeper, at its core it’s a tapestry. Leverage ratios rose in `leverage.py`."
        self.assertFalse(lint.check(text))
        found = lint.check(text, avoid=("leverage", "delve", "at its core"))
        self.assertEqual([f.snippet for f in found], ["leveraged", "Delving", "at its core", "Leverage"])
        self.assertTrue(all(f.convention for f in found))
        self.assertEqual([m[0] for m in lint.term_pattern("it's fine").finditer("It’s fine. it's  fine")],
                         ["It’s fine", "it's  fine"])
        with tempfile.TemporaryDirectory() as folder:
            terms = Path(folder) / "avoid.txt"
            terms.write_text("# house list\nleverage\ndeep dive  # phrase\n", encoding="utf-8")
            data = "A deep-dive into leverage.".encode()
            strict = self.run_cli("--avoid-file", str(terms), "--avoid", "tapestry, realm", "--strict", "--json", data=data)
            self.assertEqual(strict.returncode, 1)
            payload = json.loads(strict.stdout)
            self.assertEqual([f["snippet"] for f in payload["findings"]], ["deep-dive", "leverage"])
            self.assertEqual(payload["context"]["conventions"], ["avoid-term"])
            self.assertEqual(self.run_cli("--avoid-file", str(Path(folder) / "missing.txt")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
