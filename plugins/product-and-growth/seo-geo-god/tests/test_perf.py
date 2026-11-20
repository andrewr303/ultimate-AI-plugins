"""WP02: static performance signals (PERF001-007), CWV ratings, Lighthouse / PSI / CrUX readers and field
findings (PERF008-009)."""
from __future__ import annotations

import json
import os
import sys
import unittest
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_perf
import helpers  # noqa: E402
from seo_geo_lib import htmlparse, perf  # noqa: E402


def setUpModule() -> None:
    helpers.block_network()


def lighthouse(name: str) -> Dict[str, Any]:
    return json.loads(helpers.read_fixture("lighthouse", name))


def static(body: str, head: str = "") -> List[Any]:
    doc = htmlparse.parse_html("<html lang=\"en\"><head><title>t</title>%s</head><body>%s</body></html>" % (head, body),
                               path="index.html", url="https://example.com/")
    return perf.check_static(doc)


def ids(findings: List[Any]) -> List[str]:
    return helpers.rule_ids(findings)


HERO = '<img src="/hero.jpg" alt="Hero" width="1200" height="600" fetchpriority="high">'


class StaticSignalTests(unittest.TestCase):
    def test_clean_page_has_no_signals(self) -> None:
        self.assertEqual(static("<h1>Widgets</h1>" + HERO, head='<script src="/a.js" defer></script>'), [])

    def test_perf001_dimensions(self) -> None:
        found = helpers.findings_for(static('<img src="/a.png" alt="a"><img src="/b.png" alt="b" width="10">'
                                            '<img src="data:image/png;base64,AAAA" alt="c">'), "PERF001")
        self.assertEqual(found[0].evidence["observed"], ["/a.png", "/b.png"])
        for img in ('<img src="/a.png" alt="a" width="10" height="10">', '<img src="/a.png" alt="a" style="aspect-ratio: 4 / 3">',
                    '<img src="/a.png" alt="a" style="width: 10px; height: 20px">'):
            self.assertNotIn("PERF001", ids(static(img)), img)

    def test_perf002_lazy_lcp_candidate(self) -> None:
        native = helpers.findings_for(static('<img src="/hero.jpg" alt="h" width="1200" height="600" loading="lazy" '
                                             'fetchpriority="high">'), "PERF002")
        self.assertEqual(native[0].evidence["lazy"], "native")
        js = helpers.findings_for(static('<img src="/hero.jpg" data-src="/hero-big.jpg" alt="h" width="1200" height="600" '
                                         'fetchpriority="high">'), "PERF002")
        self.assertEqual(js[0].evidence["lazy"], "js")
        later = "<p>%s</p>" % " ".join(["word"] * 150)
        self.assertNotIn("PERF002", ids(static(later + '<img src="/x.jpg" alt="x" width="800" height="400" loading="lazy">')))
        early = "<p>%s</p>" % " ".join(["word"] * 149)
        self.assertIn("PERF002", ids(static(early + '<img src="/x.jpg" alt="x" width="800" height="400" loading="lazy">')))

    def test_small_icons_and_navigation_images_are_not_lcp_candidates(self) -> None:
        for img in ('<img src="/i.png" alt="i" width="199" height="199" loading="lazy">',
                    '<img src="/logo.png" alt="Logo" width="400" height="300" loading="lazy">',
                    '<nav><img src="/n.png" alt="n" width="400" height="300" loading="lazy"></nav>'):
            self.assertEqual(ids(static(img)), [], img)
        self.assertIn("PERF002", ids(static('<img src="/w.png" alt="w" width="200" height="100" loading="lazy">')))

    def test_perf003_priority_hint_or_preload(self) -> None:
        plain = '<img src="/hero.jpg" alt="h" width="1200" height="600">'
        self.assertEqual(ids(static(plain)), ["PERF003"])
        self.assertEqual(static(plain, head='<link rel="preload" as="image" href="/hero.jpg">'), [])
        self.assertEqual(static(plain, head='<link rel="preload" as="image" imagesrcset="/hero.jpg 1x, /hero2.jpg 2x">'),
                         [])
        self.assertEqual(ids(static(plain, head='<link rel="preload" as="font" href="/hero.jpg">')), ["PERF003"])

    def test_perf004_render_blocking_head_scripts(self) -> None:
        found = helpers.findings_for(static(HERO, head='<script src="/a.js"></script><script src="/b.js" async></script>'
                                            '<script src="/c.js" defer></script><script type="module" src="/d.js"></script>'
                                            '<script type="text/plain" src="/e.txt"></script><script>inline()</script>'),
                                     "PERF004")
        self.assertEqual(found[0].evidence["observed"], ["/a.js"])
        self.assertEqual(static(HERO + '<script src="/body.js"></script>'), [])

    def test_perf005_unload_handlers(self) -> None:
        body_attr = htmlparse.parse_html('<html><body onbeforeunload="return 1"><p>x</p></body></html>')
        self.assertEqual(ids(perf.check_static(body_attr)), ["PERF005"])
        self.assertIn("PERF005", ids(static(HERO + "<script>window.addEventListener('unload', send);</script>")))
        self.assertIn("PERF005", ids(static(HERO + "<script>window.onbeforeunload = function () {};</script>")))
        self.assertEqual(static(HERO + "<script>window.addEventListener('pagehide', send);</script>"), [])

    def test_perf006_prerender(self) -> None:
        self.assertEqual(ids(static(HERO, head='<link rel="prerender" href="/next/">')), ["PERF006"])
        self.assertEqual(static(HERO, head='<link rel="prefetch" href="/next/">'), [])

    def test_perf007_heavy_html_boundary(self) -> None:
        limit = 1048576
        for size, expected in ((limit, False), (limit + 1, True)):
            shell = "<html><head><title>t</title></head><body>%s%s</body></html>"
            pad = size - len((shell % (HERO, "")).encode("utf-8")) - len("<!---->")
            doc = htmlparse.parse_html(shell % (HERO, "<!--%s-->" % ("p" * pad)))
            self.assertEqual(doc.raw_size, size)
            self.assertEqual("PERF007" in ids(perf.check_static(doc)), expected, size)

    def test_location_defaults_and_overrides(self) -> None:
        doc = htmlparse.parse_html('<img src="/a.png" alt="a">', path="a/index.html", url="https://example.com/a/")
        found = perf.check_static(doc)
        self.assertEqual((found[0].file, found[0].url), ("a/index.html", "https://example.com/a/"))
        moved = perf.check_static(doc, url="https://example.com/b/", file="b/index.html")
        self.assertEqual((moved[0].file, moved[0].url), ("b/index.html", "https://example.com/b/"))

    def test_site_bad_home_page_signals(self) -> None:
        doc = htmlparse.parse_html(helpers.read_fixture("site-bad", "index.html"), path="index.html")
        self.assertEqual(ids(perf.check_static(doc)), ["PERF001", "PERF002", "PERF003", "PERF004", "PERF005", "PERF006"])


class RatingTests(unittest.TestCase):
    def test_thresholds(self) -> None:
        cases = [("lcp", 2500, "good"), ("lcp_ms", 2501, "needs-improvement"), ("largest_contentful_paint", 4000,
                                                                                "needs-improvement"),
                 ("LCP", 4001, "poor"), ("inp", 200, "good"), ("inp", 201, "needs-improvement"), ("inp", 500,
                                                                                               "needs-improvement"),
                 ("interaction_to_next_paint", 501, "poor"), ("cls", 0.1, "good"), ("cls", "0.10", "good"),
                 ("cls", 0.1001, "needs-improvement"), ("cumulative_layout_shift", 0.25, "needs-improvement"),
                 ("cls", 0.2501, "poor"), ("fcp", 1800, "good"), ("ttfb", 1801, "poor"),
                 ("experimental_time_to_first_byte", 800, "good")]
        for metric, value, expected in cases:
            self.assertEqual(perf.rate(metric, value), expected, (metric, value))

    def test_unknown_and_retired_metrics_raise(self) -> None:
        for metric in ("fid", "first_input_delay", "tbt", ""):
            with self.assertRaises(ValueError):
                perf.rate(metric, 1)

    def test_thresholds_come_from_data_file(self) -> None:
        cwv = json.loads((helpers.DATA_DIR / "thresholds.json").read_text(encoding="utf-8"))["cwv"]
        self.assertEqual(perf.rate("lcp", cwv["lcp_ms"][0]), "good")
        self.assertEqual(perf.rate("lcp", cwv["lcp_ms"][1] + 1), "poor")


class LighthouseReaderTests(unittest.TestCase):
    def test_raw_lhr(self) -> None:
        lab = perf.read_lighthouse(lighthouse("lhr-mobile.json"))
        self.assertEqual((lab["source"], lab["kind"], lab["form_factor"]), ("lighthouse", "lab", "mobile"))
        self.assertEqual(lab["categories"], {"accessibility": 90, "performance": 62})
        self.assertEqual(lab["null_categories"], ["seo"])
        self.assertEqual(lab["metrics"], {"lcp_ms": 3120, "cls": 0.12, "fcp_ms": 1500, "tbt_ms": 410, "si_ms": 2800,
                                          "ttfb_ms": 640})
        self.assertEqual(lab["ratings"], {"lcp_ms": "needs-improvement", "cls": "needs-improvement", "fcp_ms": "good",
                                          "ttfb_ms": "good"})
        self.assertIsNone(lab["agentic"])
        self.assertIsNone(lab["field"])
        self.assertEqual((lab["lighthouse_version"], lab["final_url"]), ("13.0.0", "https://example.com/"))

    def test_psi_response_with_field_data_and_cls_units(self) -> None:
        summary = perf.read_lighthouse(lighthouse("psi-with-field.json"))
        self.assertEqual(summary["source"], "psi")
        self.assertEqual(summary["metrics"]["cls"], 0.12)
        field = summary["field"]
        self.assertEqual(field["metrics"], {"lcp_ms": 4500, "inp_ms": 180, "cls": 0.12, "fcp_ms": 1700})
        self.assertEqual(field["ratings"]["lcp_ms"], "poor")
        self.assertEqual((field["kind"], field["url"], field["overall"]), ("field", "https://example.com/", "SLOW"))

    def test_agentic_category_pass_ratio(self) -> None:
        lab = perf.read_lighthouse(lighthouse("lhr-agentic.json"))
        agentic = lab["agentic"]
        self.assertEqual((agentic["category"], agentic["passed"], agentic["counted"], agentic["display"]),
                         ("agentic-browsing", 2, 5, "2/5"))
        self.assertIn("not Google Search", agentic["note"])
        self.assertIn("agentic-browsing", lab["null_categories"])

    def test_invalid_inputs(self) -> None:
        for data in ([], {"lighthouseResult": {}}, {"foo": 1}):
            with self.assertRaises(ValueError):
                perf.read_lighthouse(data)  # type: ignore[arg-type]

    def test_non_numeric_values_are_skipped(self) -> None:
        lab = perf.read_lighthouse({"categories": {"performance": {"score": "n/a"}},
                                    "audits": {"largest-contentful-paint": {"numericValue": "NaN"}}})
        self.assertEqual((lab["categories"], lab["null_categories"], lab["metrics"]), ({}, ["performance"], {}))


class CruxReaderTests(unittest.TestCase):
    def test_record_with_string_cls_and_unrated_metrics(self) -> None:
        field = perf.read_crux(lighthouse("crux-record.json"))
        self.assertEqual(field["metrics"], {"cls": 0.05, "ttfb_ms": 900, "inp_ms": 180, "lcp_ms": 2600})
        self.assertEqual(field["ratings"]["lcp_ms"], "needs-improvement")
        self.assertEqual(field["histograms"]["lcp_ms"], {"good": 0.71, "needs-improvement": 0.2, "poor": 0.09})
        self.assertEqual(field["unrated"], ["largest_contentful_paint_soft_navigation", "round_trip_time"])
        self.assertEqual(field["experimental"], ["largest_contentful_paint_soft_navigation"])
        self.assertEqual((field["url"], field["form_factor"]), ("https://example.com", "PHONE"))

    def test_history_uses_latest_non_null_p75(self) -> None:
        field = perf.read_crux(lighthouse("crux-history.json"))
        self.assertEqual(field["metrics"], {"cls": 0.3, "lcp_ms": 4200})

    def test_fid_is_never_rated(self) -> None:
        field = perf.read_crux({"record": {"metrics": {"first_input_delay": {"percentiles": {"p75": 300}}}}})
        self.assertEqual((field["metrics"], field["unrated"]), ({}, ["first_input_delay"]))
        self.assertEqual(perf.check_field(field), [])

    def test_invalid_records(self) -> None:
        for data in ([], {"record": {"key": {}}}, {"metrics": []}):
            with self.assertRaises(ValueError):
                perf.read_crux(data)  # type: ignore[arg-type]


class FieldFindingTests(unittest.TestCase):
    def test_perf008_per_core_web_vital(self) -> None:
        found = perf.check_field(perf.read_crux(lighthouse("crux-record.json")))
        self.assertEqual([(f.rule, f.evidence["metric"], f.evidence["rating"]) for f in found],
                         [("PERF008", "lcp_ms", "needs-improvement")])
        self.assertEqual(found[0].evidence["thresholds"], [2500, 4000])
        history = perf.check_field(perf.read_crux(lighthouse("crux-history.json")))
        self.assertEqual(sorted(f.evidence["metric"] for f in history), ["cls", "lcp_ms"])

    def test_boundary_values_are_good(self) -> None:
        self.assertEqual(perf.check_field(perf.read_crux(lighthouse("crux-good.json"))), [])

    def test_psi_field_wins_over_lab(self) -> None:
        found = perf.check_field(perf.read_lighthouse(lighthouse("psi-with-field.json")))
        self.assertEqual(sorted(f.evidence["metric"] for f in found), ["cls", "lcp_ms"])
        self.assertEqual(ids(found), ["PERF008"])

    def test_perf009_lab_only(self) -> None:
        lab = perf.read_lighthouse(lighthouse("lhr-mobile.json"))
        found = perf.check_field(lab)
        self.assertEqual([(f.rule, f.severity, f.url) for f in found], [("PERF009", "info", "https://example.com/")])
        self.assertEqual(ids(perf.check_field({"lab": lab, "field": None})), ["PERF009"])
        combined = perf.check_field({"lab": lab, "field": perf.read_crux(lighthouse("crux-record.json"))})
        self.assertEqual(ids(combined), ["PERF008"])
        self.assertEqual(perf.check_field({}), [])

    def test_field_without_core_web_vitals_falls_back_to_lab_notice(self) -> None:
        lab = perf.read_lighthouse(lighthouse("lhr-mobile.json"))
        ttfb_only = perf.read_crux({"record": {"metrics": {"experimental_time_to_first_byte": {"percentiles": {"p75": 2000}}}}})
        self.assertEqual(ids(perf.check_field({"lab": lab, "field": ttfb_only})), ["PERF009"])
        self.assertEqual(perf.check_field(ttfb_only), [])


if __name__ == "__main__":
    unittest.main()
