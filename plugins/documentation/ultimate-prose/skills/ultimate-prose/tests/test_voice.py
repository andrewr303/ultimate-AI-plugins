"""Regression tests for the 4.5 voice calibration of the Andrew overlay.

Every text here is synthetic; none reproduces a sent message.
"""
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import lint_andrew

SIGN = "\n\nBest regards,\nAndrew Rodriguez\n"


def cats(text, **options):
    findings, _ = lint_andrew.check_andrew(text, **options)
    return [f.category for f in findings]


def notes(text, **options):
    return lint_andrew.check_andrew(text, **options)[1].notes


class VoiceCalibrationTests(unittest.TestCase):
    def test_quick_replies_in_his_form_are_clean(self):
        for body in ("Yes that works, I'll send the revised file Thursday morning.",
                     "Sounds good! I figured it wouldn't be needed but it's good to have just in case.",
                     "Confirmed.", "Awesome, thank you!",
                     "It should be good to go, but that's really up to Dana."):
            self.assertEqual(cats(body + SIGN, genre="email"), [], body)

    def test_ordinary_email_close_and_single_emphasis_are_his_voice(self):
        body = ("Hi Dana,\n\nThe migration is on track, and I think we're in good shape for Friday's review. "
                "I actually finished the export early, so I'm really just waiting on the test data.\n\n"
                "Let me know if you need anything from me before then.")
        self.assertEqual(cats(body + SIGN, genre="email"), [])
        self.assertIn("banned-phrase", cats(body + SIGN, genre="email", formality="executive"))
        self.assertIn("banned-phrase", cats(body, genre="generic"))
        stacked = body.replace("so I'm really just", "so I'm really, really, truly just")
        found = cats(stacked + SIGN, genre="email")
        self.assertIn("andrew-intensifier-budget", found)
        self.assertIn("intensifier", found)
        twice = body.replace("I think", "I actually think")
        self.assertIn("andrew-marker-density", cats(twice + SIGN, genre="email"))

    def test_agreement_is_not_a_certainty_claim(self):
        self.assertEqual(cats("I agree 100%, that makes sense." + SIGN, genre="email"), [])
        self.assertEqual(cats("I would definitely recommend sending the links too." + SIGN, genre="email"), [])
        self.assertIn("andrew-certainty", cats("The model is 100% accurate." + SIGN, genre="email"))
        self.assertIn("andrew-certainty", cats("This will clearly work." + SIGN, genre="email"))
        self.assertIn("andrew-certainty",
                      cats("I would definitely recommend it." + SIGN, genre="email", formality="executive"))

    def test_casual_register_keeps_his_own_markers(self):
        post = ("Agree 100%. As a solo founder+engineer I've been testing this lately and it's clearly the "
                "best option right now (which still surprises me lol). Definitely excited to try the new release!")
        self.assertEqual(cats(post, genre="tweet", formality="natural"), [])
        business = cats(post + SIGN, genre="email")
        self.assertIn("andrew-plus-join", business)
        self.assertIn("andrew-casual-residue", business)
        self.assertIn("andrew-certainty", business)

    def test_first_person_openers_are_judged_as_a_share(self):
        plain = ("I merged the fix this morning. The export now keeps its labels. I also reran the March case. "
                 "The totals match the ledger. Dana still needs to deploy it. The staging site is unchanged. "
                 "I'll send the notes after lunch. The review can start Thursday.")
        self.assertNotIn("andrew-i-opener", cats(plain + SIGN, genre="email"))
        heavy = ("I merged the fix this morning. I reran the March case. I checked the totals. I updated the notes. "
                 "I asked Dana to deploy it. I will send the summary after lunch. The review can start Thursday.")
        self.assertIn("andrew-i-opener", cats(heavy + SIGN, genre="email"))
        self.assertNotIn("andrew-i-opener", cats("I merged it. I reran it. I sent it." + SIGN, genre="email"))

    def test_semicolons_and_long_paragraphs_flag_a_departure(self):
        one = "The export is fixed; the labels are back. I reran the March case and the totals match the ledger."
        self.assertNotIn("andrew-semicolon", cats(one + SIGN, genre="email"))
        many = ("The export is fixed; the labels are back; the totals match. "
                "I reran the March case; nothing else changed.")
        self.assertIn("andrew-semicolon", cats(many + SIGN, genre="email"))
        self.assertNotIn("andrew-semicolon", cats(many, genre="docs"))
        six = " ".join(f"Step {n} finished without errors." for n in range(1, 7))
        self.assertNotIn("andrew-long-paragraph", cats(six + SIGN, genre="email"))
        eight = " ".join(f"Step {n} finished without errors." for n in range(1, 9))
        self.assertIn("andrew-long-paragraph", cats(eight + SIGN, genre="email"))

    def test_missing_email_sign_off_is_a_note_not_a_finding(self):
        body = "Yes that works, I'll send the revised file Thursday morning."
        self.assertTrue(any("Best regards" in note for note in notes(body, genre="email")))
        self.assertEqual(cats(body, genre="email"), [])
        self.assertFalse(any("Best regards" in note for note in notes(body + SIGN, genre="email")))
        self.assertFalse(any("Best regards" in note for note in notes(body + "\n\nThanks,\nAndrew Rodriguez", genre="email")))
        self.assertFalse(any("Best regards" in note for note in notes(body, genre="tweet", formality="natural")))
        self.assertFalse(any("Best regards" in note for note in notes(body, genre="email", formality="natural")))


if __name__ == "__main__":
    unittest.main()
