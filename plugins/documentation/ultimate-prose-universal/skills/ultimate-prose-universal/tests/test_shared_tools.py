"""Regression tests for the clarity-derived tools shared by both prose skills."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import fidelity_check  # noqa: E402
import prose_stats  # noqa: E402

SOURCE = ("Our internal test suggests startup may be about 12% faster on Pixel 8. "
          "The sample was 40 cold launches, and we have not tested older devices. "
          "Mina thinks the cache change caused most of the gain.")
FAITHFUL = ("Startup is about 12% faster on Pixel 8 in our internal test of 40 cold launches, "
            "which suggests the change may help; we haven't tested older devices. "
            "Mina thinks the cache change drove most of the gain.")
INFLATED = ("Startup is now 12% faster on Pixel 9, thanks to the cache change, "
            "which caused most of the gain across all devices.")


def run(script, *args, data=b""):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], input=data,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class FidelityTests(unittest.TestCase):
    def test_faithful_rewrite_keeps_hard_anchors_and_qualifiers(self):
        result = fidelity_check.compare(SOURCE, FAITHFUL)
        self.assertEqual(result["dropped"], {})
        self.assertNotIn("numbers", result["added"])
        self.assertNotIn("names", result["added"], "sentence-initial Startup is not a new name")

    def test_inflated_rewrite_reports_lost_scope_and_new_facts(self):
        result = fidelity_check.compare(SOURCE, INFLATED)
        self.assertIn("40", result["dropped"]["numbers"])
        self.assertIn("may", result["dropped"]["hedge"])
        self.assertIn("suggests", result["dropped"]["evidential"])
        self.assertIn("thinks", result["dropped"]["attribution"])
        self.assertIn("Mina", result["dropped"]["names"])
        self.assertIn("negation", result["dropped"])
        self.assertIn("9", result["added"]["numbers"])
        self.assertIn("all", result["added"]["absolute"])

    def test_quantity_words_and_units_normalize(self):
        result = fidelity_check.compare("Latency fell twelve percent to 280 ms.",
                                        "Latency fell 12% to 280ms.")
        self.assertEqual(result["dropped"], {})
        self.assertEqual(result["added"], {})

    def test_about_counts_only_before_a_quantity(self):
        quiet = fidelity_check.compare("We talked about pricing on Tuesday.",
                                       "We discussed pricing on Tuesday.")
        self.assertNotIn("approximation", quiet["dropped"])
        loud = fidelity_check.compare("It costs about $40.", "It costs $40.")
        self.assertIn("about", loud["dropped"]["approximation"])

    def test_family_swaps_are_quiet_and_net_changes_are_reported(self):
        source = "About 12% of users may churn if pricing changes. Dana thinks the pilot worked on 16 Oct."
        swap = "Roughly 12% of users might churn if pricing changes. Dana believes the pilot worked on 16 October."
        result = fidelity_check.compare(source, swap)
        self.assertEqual((result["dropped"], result["added"]), ({}, {}))
        firmer = "12% of users churn when pricing changes. The pilot worked on 16 October."
        result = fidelity_check.compare(source, firmer)
        self.assertEqual(set(result["dropped"]), {"hedge", "approximation", "condition", "attribution", "names"})
        self.assertEqual(result["added"], {})

    def test_new_promises_and_causes_are_reported(self):
        source = "The pilot finished in May 2026. We plan to ship in June. Retries fell and refunds stayed flat."
        rewrite = "The pilot finished in May 2026. We'll ship in June because retries fell, so refunds stayed flat."
        result = fidelity_check.compare(source, rewrite)
        self.assertEqual(result["added"]["commitment"], {"will": 1})
        self.assertEqual(result["added"]["causation"], {"because": 1})
        same = fidelity_check.compare("We will ship because tests passed.", "We'll ship, because tests passed.")
        self.assertEqual((same["dropped"], same["added"]), ({}, {}))

    def test_summary_mode_lists_only_additions(self):
        cut = "Startup is 12% faster on Pixel 8 and will be on every device."
        full = fidelity_check.compare(SOURCE, cut)
        self.assertIn("40", full["dropped"]["numbers"])
        summary = fidelity_check.compare(SOURCE, cut, mode="summary")
        self.assertEqual(summary["dropped"], {})
        self.assertEqual(set(summary["added"]), {"absolute", "commitment"})
        with self.assertRaises(ValueError):
            fidelity_check.compare("a", "b", mode="other")
        with tempfile.TemporaryDirectory() as folder:
            source, short = Path(folder) / "s.txt", Path(folder) / "c.txt"
            source.write_text(SOURCE, encoding="utf-8")
            short.write_text("Startup is about 12% faster on Pixel 8 in our internal test.", encoding="utf-8")
            self.assertEqual(run("fidelity_check.py", str(source), str(short), "--strict").returncode, 1)
            result = run("fidelity_check.py", str(source), str(short), "--mode", "summary", "--strict", "--json")
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual((payload["mode"], payload["dropped"], payload["added"]), ("summary", {}, {}))
            text = run("fidelity_check.py", str(source), str(short), "--mode", "summary").stdout.decode()
            self.assertIn("Summary mode", text)

    def test_code_links_quotes_and_dates_are_anchors(self):
        source = ('Run `keys verify --env staging` by Thursday at 2 p.m. and email ops@example.com. '
                  'The note said "do not revoke first".')
        rewrite = 'Run `keys verify` by Friday and email the ops team. The note warned against revoking first.'
        result = fidelity_check.compare(source, rewrite)
        self.assertIn("keys verify --env staging", result["dropped"]["code"])
        self.assertIn("ops@example.com", result["dropped"]["links"])
        self.assertIn("thursday", result["dropped"]["dates"])
        self.assertIn("friday", result["added"]["dates"])
        self.assertIn("do not revoke first", result["dropped"]["quotes"])

    def test_cli_strict_json_and_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            source, good, bad = (Path(folder) / n for n in ("s.txt", "g.txt", "b.txt"))
            source.write_text(SOURCE, encoding="utf-8")
            good.write_text(FAITHFUL, encoding="utf-8")
            bad.write_text(INFLATED, encoding="utf-8")
            before = source.read_bytes()
            self.assertEqual(run("fidelity_check.py", str(source), str(good), "--strict").returncode, 0)
            strict = run("fidelity_check.py", str(source), str(bad), "--strict", "--json")
            self.assertEqual(strict.returncode, 1)
            payload = json.loads(strict.stdout)
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(run("fidelity_check.py", str(source), str(bad)).returncode, 0)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(run("fidelity_check.py", "-", "-").returncode, 2)
            self.assertEqual(run("fidelity_check.py", str(source), "/missing.txt").returncode, 2)
            self.assertEqual(run("fidelity_check.py", "-", str(good), data=b"  ").returncode, 2)


class ProseStatsTests(unittest.TestCase):
    def test_headings_lists_code_and_quotes_are_handled(self):
        text = ('# A Heading That Should Not Count\n\n'
                'The cache change cut cold starts in the pilot.\n\n'
                '- First item without punctuation\n- Second item\n\n'
                '```\nstudies show this is crucial\n```\n\n'
                'The reviewer wrote "studies show this is crucial" in the margin.\n')
        stats = prose_stats.analyze(text)
        units = [u for p in prose_stats.structure(text) for u in p["units"]]
        self.assertNotIn("A Heading That Should Not Count", " ".join(units))
        self.assertIn("First item without punctuation", units)
        self.assertEqual(stats["look_here"]["vague_attribution"], [])
        self.assertEqual(stats["look_here"]["importance_without_mechanism"], [])
        quoted = prose_stats.analyze(text, include_quotes=True)
        self.assertTrue(quoted["look_here"]["vague_attribution"])

    def test_importance_needs_a_mechanism_nearby(self):
        bare = prose_stats.analyze("This update is transformative for every team.")
        self.assertTrue(bare["look_here"]["importance_without_mechanism"])
        backed = prose_stats.analyze("This update is important because retries no longer duplicate orders.")
        self.assertFalse(backed["look_here"]["importance_without_mechanism"])
        stats = prose_stats.analyze("The effect was statistically significant in the 2024 cohort only.")
        self.assertFalse(stats["look_here"]["importance_without_mechanism"])

    def test_kickers_flourishes_and_actors(self):
        text = ("Teams want to reuse the approval machinery they already have for every new agent. "
                "That instinct backfires. The bug was an authorization flaw wearing the costume of "
                "a performance fix. The data tells us to slow down.")
        look = prose_stats.analyze(text)["look_here"]
        self.assertEqual(look["demonstrative_kickers"], ["That instinct backfires."])
        self.assertEqual(look["metaphor_flourishes"], ["wearing the costume of"])
        self.assertEqual(look["abstract_actors"], ["The data tells"])
        self.assertFalse(prose_stats.analyze("That works for me.")["look_here"]["demonstrative_kickers"])

    def test_model_register_reports_only_a_cluster(self):
        filler = " ".join(["The review covered the release notes and the rollout plan in detail."] * 14)
        few = prose_stats.analyze(filler + " The load-bearing check is a backstop.")
        self.assertEqual(few["look_here"]["model_register_cluster"], [])
        many = prose_stats.analyze(filler + " The load-bearing check is a backstop and a tripwire, "
                                   "byte-identical to the papered over version.")
        self.assertGreaterEqual(len(many["look_here"]["model_register_cluster"]), 4)
        short = prose_stats.analyze("The load-bearing backstop tripwire was byte-identical and papered over.")
        self.assertEqual(short["look_here"]["model_register_cluster"], [])

    def test_no_score_and_compare_cli(self):
        with tempfile.TemporaryDirectory() as folder:
            before, after = Path(folder) / "before.md", Path(folder) / "after.md"
            before.write_text("At its core, this is a crucial shift. Experts agree.", encoding="utf-8")
            after.write_text("Retries no longer create duplicate orders in the pilot.", encoding="utf-8")
            data = after.read_bytes()
            result = run("prose_stats.py", str(after), "--compare", str(before), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue({"size", "measurements", "look_here", "earlier"} <= set(payload))
            self.assertFalse(any("score" in key for key in payload["measurements"]))
            self.assertTrue(payload["earlier"]["look_here"]["stock_openers"])
            text = run("prose_stats.py", str(after), "--compare", str(before))
            self.assertIn("->", text.stdout.decode())
            self.assertIn("No composite score", text.stdout.decode())
            self.assertEqual(after.read_bytes(), data)
        self.assertEqual(run("prose_stats.py", "-", data=b"   ").returncode, 2)
        self.assertEqual(run("prose_stats.py", "/missing.md").returncode, 2)


class PackageTests(unittest.TestCase):
    def test_package_validator_passes(self):
        result = run("validate_package.py")
        self.assertEqual(result.returncode, 0, result.stdout.decode() + result.stderr.decode())


if __name__ == "__main__":
    unittest.main()
