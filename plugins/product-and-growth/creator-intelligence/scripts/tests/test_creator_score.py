import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from creator_score import Dimension, WEIGHTS, baseline_confidence, outlier_report, score_creator  # noqa: E402


def posts(values, age=200):
    return [{"id": f"p{i}", "views": v, "age_hours": age} for i, v in enumerate(values)]


class OutlierTests(unittest.TestCase):
    def test_median_not_mean_so_one_viral_post_does_not_hide_itself(self):
        data = posts([100] * 11 + [10_000])
        report = outlier_report(data)
        self.assertEqual(report["baseline"], 100)
        self.assertEqual(report["posts"][0]["lift"], 100)
        self.assertEqual(report["posts"][0]["label"], "huge")

    def test_labels_follow_thresholds(self):
        report = outlier_report(posts([100] * 10 + [160, 250, 600]))
        labels = {p["id"]: p["label"] for p in report["posts"]}
        self.assertEqual(labels["p10"], "mild")
        self.assertEqual(labels["p11"], "strong")
        self.assertEqual(labels["p12"], "huge")
        self.assertIsNone(labels["p0"])

    def test_young_posts_are_excluded_from_baseline(self):
        data = posts([100] * 12) + [{"id": "new", "views": 5, "age_hours": 5}]
        report = outlier_report(data)
        self.assertEqual(report["baseline"], 100)
        self.assertEqual(report["excluded_too_young"], 1)

    def test_confidence_scales_with_sample_size(self):
        self.assertEqual(baseline_confidence(9), "low")
        self.assertEqual(baseline_confidence(12), "medium")
        self.assertEqual(baseline_confidence(25), "high")

    def test_no_settled_posts_gives_low_confidence_and_no_baseline(self):
        report = outlier_report([{"id": "x", "views": 1, "age_hours": 1}])
        self.assertIsNone(report["baseline"])
        self.assertEqual(report["confidence"], "low")


def full(score, conf="high"):
    return {k: Dimension(score, conf) for k in WEIGHTS}


class ScoreTests(unittest.TestCase):
    def test_weights_sum_to_100(self):
        self.assertEqual(sum(WEIGHTS.values()), 100)

    def test_uniform_scores_return_that_score(self):
        result = score_creator(full(80))
        self.assertEqual(result["score"], 80.0)
        self.assertEqual(result["confidence"], "high")
        self.assertEqual(result["band"], [75.0, 85.0])

    def test_gate_rejects_regardless_of_score(self):
        result = score_creator(full(95), gates=["G2"])
        self.assertEqual(result["verdict"], "reject")
        self.assertIsNone(result["score"])

    def test_missing_dimension_is_renormalised_not_zeroed_and_confidence_capped_low(self):
        dims = full(80)
        dims["audience_fit"] = Dimension(None)
        result = score_creator(dims)
        self.assertEqual(result["score"], 80.0)
        self.assertEqual(result["confidence"], "low")
        self.assertEqual(result["missing"], ["audience_fit"])

    def test_authenticity_floor_caps_total(self):
        dims = full(95)
        dims["authenticity"] = Dimension(30, "high")
        result = score_creator(dims)
        self.assertEqual(result["score"], 60)
        self.assertEqual(result["floor_capped_by"], ["authenticity"])

    def test_overall_confidence_is_the_weakest_present_dimension(self):
        dims = full(70)
        dims["reach"] = Dimension(70, "medium")
        self.assertEqual(score_creator(dims)["confidence"], "medium")

    def test_nothing_scorable_is_rejected_for_insufficient_data(self):
        result = score_creator({k: Dimension(None) for k in WEIGHTS})
        self.assertEqual(result["verdict"], "reject")
        self.assertIn("G3", result["gates"])

    def test_invalid_inputs_raise(self):
        with self.assertRaises(ValueError):
            score_creator({"charisma": Dimension(50)})
        with self.assertRaises(ValueError):
            score_creator({"reach": Dimension(120)})
        with self.assertRaises(ValueError):
            score_creator(full(50), gates=["G9"])



class InputGuardTests(unittest.TestCase):
    def test_huge_integer_is_invalid_not_an_overflow(self):
        with self.assertRaises(ValueError):
            score_creator({"reach": Dimension(10**400)})
        with self.assertRaises(ValueError):
            outlier_report([{"id": "a", "views": 10**400, "age_hours": 100}])
        with self.assertRaises(ValueError):
            baseline_confidence(10**400)

    def test_non_finite_and_unsafe_ids_are_rejected(self):
        for bad in (float("nan"), float("inf"), -float("inf"), 2**53, 10**400, 1.5, True):
            with self.subTest(id=bad), self.assertRaises(ValueError):
                outlier_report([{"id": bad, "views": 1, "age_hours": 100}])

    def test_prototype_key_metrics_are_rejected(self):
        for metric in ("__proto__", "constructor", "prototype"):
            with self.subTest(metric=metric), self.assertRaises(ValueError):
                outlier_report([{"id": "a", metric: 1, "age_hours": 100}], metric)


if __name__ == "__main__":
    unittest.main()


class CliTests(unittest.TestCase):
    def run_cli(self, text):
        import subprocess
        script = Path(__file__).resolve().parents[1] / "creator_score.py"
        return subprocess.run([sys.executable, "-I", "-B", str(script)], input=text,
                              capture_output=True, text=True)

    def test_malformed_input_exits_2_without_traceback(self):
        for bad in ("nope", "{}", '{"dimensions":{"niche_fit":{"score":"x"}}}',
                    '{"dimensions":{"niche_fit":{"score":80}},"gates":"G1"}'):
            r = self.run_cli(bad)
            self.assertEqual(r.returncode, 2, bad)
            self.assertNotIn("Traceback", r.stderr)

    def test_valid_input_exits_0(self):
        r = self.run_cli('{"posts":[{"id":"a","views":10,"age_hours":100}]}')
        self.assertEqual(r.returncode, 0)
