"""Regression tests for the 4.4 scanner additions."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import lint
import lint_andrew

AVOID_LIST = ("delve tapestry landscape vibrant pivotal crucial foster bolster garner underscore nuanced "
              "multifaceted intricate meticulous leverage harness illuminate realm robust holistic seamless "
              "streamlined nestled renowned groundbreaking comprehensive moreover furthermore additionally "
              "encompassing cultivating showcasing embodies epitomizes spearheading interplay indelible "
              "endeavor advent").split()


def categories(text, **options):
    findings, _ = lint.check(text, **options)
    return [f.category for f in findings]


class AdditionTests(unittest.TestCase):
    def test_every_word_on_the_stated_avoid_list_is_a_candidate(self):
        for word in AVOID_LIST:
            findings, _ = lint.check(f"The team will {word} the plan next week.")
            self.assertTrue(any(word in f.rule for f in findings), word)
        findings, _ = lint.check("On the one hand, the pilot worked.")
        self.assertIn("empty-phrase", [f.category for f in findings])

    def test_ordinary_business_reply_stays_clean(self):
        text = ("Hi Dana,\n\nNot yet. I'll send it Friday. Tuesday works for the review, and I can't make Thursday.\n\n"
                "The limit applies per account, not per user. The plan covers three regions, and the data shows "
                "a 12% drop in retries during the pilot. Our analysis covers 410 requests. Of course the price "
                "depends on volume.\n\nNot the first time. We saw the same failure in March and April.\n\n"
                "Thanks,\nAndrew\n")
        self.assertEqual(lint_andrew.check_andrew(text, genre="email")[0], [])

    def test_staged_contrast_across_sentences(self):
        text = "This does not mean every option is equal. It means nobody checks. Not the technology. The people."
        findings, _ = lint.check(text)
        self.assertEqual([f.rule.split(":")[0] for f in findings], ["split pivot", "fragment pivot"])

    def test_draft_artifacts_are_read_through_quotes_but_not_code(self):
        text = ('Dear [Your Name], see [TK: launch date] and "[Insert quote here]".\n'
                "Source: [docs](https://example.test/a?utm_source=chatgpt.com) contentReference[oaicite:0]{index=0}.\n"
                "Zero​width.\n")
        self.assertEqual(categories(text), ["draft-artifact"] * 6)
        clean = ("See [Your account](https://example.test) and [Name][ref].\n\n[Name]: https://example.test\n"
                 "`[Your Name]`\n```\n[Insert text] turn0search3\n```\n")
        self.assertEqual(categories(clean), [])
        source = Path(__file__).resolve().parents[1] / "references" / "preservation.md"
        if source.exists():  # the skill's own gap examples live inside code spans
            self.assertNotIn("draft-artifact", categories(source.read_text(encoding="utf-8"), genre="docs"))

    def test_new_review_families_and_their_gates(self):
        text = ("To be honest, the market wants growth. She was featured in Forbes, Wired, and TechCrunch. "
                "Importantly, we saw various issues, numerous delays and a range of bugs (and, increasingly, outages).")
        self.assertEqual(categories(text), ["banned-phrase", "abstract-actor", "borrowed-authority",
                                            "announcement", "vague-quantity", "hedging"])
        self.assertEqual(categories("We saw various issues and numerous delays. The team decides on Friday."), [])
        self.assertEqual(categories("- **Speed:** Speed improved.\n"), ["formatting-bullet"])

    def test_docs_genre_keeps_literal_technical_terms(self):
        text = "The robust estimator is comprehensive. We leverage the paradigm to streamline builds."
        self.assertEqual(len(categories(text)), 5)
        self.assertEqual(categories(text, genre="docs"), [])
        self.assertEqual(categories("We delve into a rich tapestry.", genre="docs").count("stock-vocab"), 2)

    def test_connective_paragraph_openers_need_a_cluster(self):
        body = "the team reviewed the plan and agreed the budget would hold."
        text = "\n\n".join(f"{word}, {body}" for word in ("However", "Moreover", "Overall")) + f"\n\nThe {body}"
        self.assertIn("transition-density", categories(text))
        self.assertNotIn("transition-density", categories(f"However, {body}\n\nThe {body}\n\nThe {body}"))

    def test_business_length_diagnostic_is_a_note_not_a_finding(self):
        short = " ".join(["The export failed on the second retry. We fixed the queue. It works now."] * 10)
        findings, cadence = lint_andrew.check_andrew(short, genre="email", formality="business")
        self.assertTrue(any("17 to 24" in note for note in cadence.notes))
        self.assertFalse(any("17 to 24" in f.rule for f in findings))
        _, casual = lint_andrew.check_andrew(short, genre="email", formality="natural")
        self.assertFalse(any("17 to 24" in note for note in casual.notes))
        _, brief = lint_andrew.check_andrew("Tuesday works. I'll send the file that morning.", genre="email")
        self.assertFalse(any("17 to 24" in note for note in brief.notes))

    def test_cli_still_reports_json_and_exits_zero(self):
        data = "Great question! Dear [Your Name], here is the plan.".encode()
        for script in ("lint.py", "lint_andrew.py"):
            result = subprocess.run([sys.executable, str(SCRIPTS / script), "--json"], input=data,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(result.returncode, 0, result.stderr)
            found = [f["category"] for f in json.loads(result.stdout)["findings"]]
            self.assertIn("draft-artifact", found)


if __name__ == "__main__":
    unittest.main()
