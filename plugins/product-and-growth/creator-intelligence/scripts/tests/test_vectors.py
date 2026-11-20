"""Assert every shared golden vector against the Python reference.

The TypeScript suite (test/vectors.test.ts) asserts the same files, so the two
implementations cannot drift apart without one suite failing.
"""
import json
import math
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import build_vectors  # noqa: E402

VECTORS = SCRIPTS.parent / "vectors"


def load(name):
    return json.loads((VECTORS / name).read_text(encoding="utf-8"))


def same(actual, expected, tol=1e-9):
    if isinstance(expected, bool) or expected is None or isinstance(expected, str):
        return actual == expected and type(actual) is type(expected)
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool) and math.isclose(actual, expected, rel_tol=0, abs_tol=tol)
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(same(a, e, tol) for a, e in zip(actual, expected))
    if isinstance(expected, dict):
        return isinstance(actual, dict) and list(actual) == list(expected) and all(same(actual[k], expected[k], tol) for k in expected)
    raise TypeError(f"unexpected vector value {expected!r}")


RUNNERS = {
    "decode": lambda x: build_vectors.cr.decode(x),
    "extract": lambda x: build_vectors.cr.extract(x),
    "registrable_domain": lambda x: build_vectors.cr.registrable_domain(x),
    "is_roster_page": lambda x: build_vectors.cr.is_roster_page(**x),
    "classify": build_vectors._classify,
    "baseline_confidence": lambda x: build_vectors.cs.baseline_confidence(x),
    "outlier_report": build_vectors._outlier,
    "score_creator": build_vectors._score,
}


class VectorTests(unittest.TestCase):
    def check_file(self, name):
        data = load(name)
        tol = data.get("tolerance", 1e-9)
        count = 0
        for section, vectors in data.items():
            if not isinstance(vectors, list):
                continue
            for v in vectors:
                count += 1
                with self.subTest(section=section, id=v["id"]):
                    if v.get("throws"):
                        with self.assertRaises((TypeError, ValueError)):
                            RUNNERS[section](v["input"])
                    else:
                        actual = json.loads(json.dumps(RUNNERS[section](v["input"])))
                        self.assertTrue(same(actual, v["expected"], tol), f"{actual!r} != {v['expected']!r}")
        self.assertGreater(count, 50)

    def test_contact_rule_vectors(self):
        self.check_file("contact-rules.vectors.json")

    def test_creator_score_vectors(self):
        self.check_file("creator-score.vectors.json")

    def test_vector_files_are_current(self):
        self.assertEqual(build_vectors.main(["build_vectors.py", "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
