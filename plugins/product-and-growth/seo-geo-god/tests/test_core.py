"""WP01 core tests: findings, catalog, scores, gates, renderers, output writing, data files."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_core
import helpers  # noqa: E402
from seo_geo_lib import DATA_DIR, FACTS_AS_OF, findings, report, rulesdb
from seo_geo_lib.findings import Finding, Result, compute_scores, dedupe, gate_tripped, make, sort_findings, truncate


def setUpModule() -> None:
    helpers.block_network()


CAT = rulesdb.RuleCatalog.load()


def _ranges(spec: str) -> list:
    out = []
    for part in spec.split():
        fam, lo, hi = re.match(r"^([A-Z]+)(\d{3})(?:-(\d{3}))?$", part).groups()
        out += ["%s%03d" % (fam, n) for n in range(int(lo), int(hi or lo) + 1)]
    return out


BLUEPRINT_IDS = _ranges(
    "CRAWL001-009 IDX001-005 CANON001-008 HTTP001-008 META001-014 HDG001-003 SD001-020 SMAP001-011 HREF001-008 "
    "LINK001-007 REND001-005 PERF001-009 IMG001-004 VID001 CONT001-010 CITE001-003 PSEO001-003 AI001-015 "
    "AGENT001-006 AGENT008-009 SPAM001-003 LOCAL001-002 LAUNCH001-005 DRIFT001-020 REDIR001-007 FID001-010")
PLANNED = {"HTTP006", "SD016", "IMG003", "IMG004", "VID001", "CONT006", "PSEO002", "PSEO003", "AGENT006", "SPAM003",
           "LOCAL001", "LAUNCH002"}
FACT_IDS = {"F-AI-%02d" % i for i in range(1, 41)} | {"F-T-%02d" % i for i in range(1, 54)}
REFERENCE_FILES = {
    "current-facts.md", "framework-recipes.md", "robots-and-directives.md", "cwv-and-performance.md",
    "structured-data-matrix.md", "international.md", "migrations.md", "programmatic-seo.md", "ci-recipes.md",
    "ai-crawlers.md", "ai-surfaces.md", "agent-readiness.md", "citability-and-rewrite.md", "measurement-protocol.md",
    "geo-research-evidence.md", "content-quality-rubrics.md", "keyword-and-content-strategy.md", "local-seo.md",
    "ecommerce-seo.md", "connectors.md", "search-policies.md", "scoring-and-prioritization.md",
    "recommendation-contract.md", "safety-and-honesty.md", "cli-reference.md", "rule-catalog.md"}
ENVELOPE_KEYS = {"tool", "version", "schema_version", "command", "generated_at", "facts_as_of", "rules_version", "mode",
                 "target", "summary", "coverage", "scores", "findings", "data", "limitations", "untrusted_fields",
                 "error"}
WP01_PY = ["scripts/seo_geo_lib/__init__.py", "scripts/seo_geo_lib/findings.py", "scripts/seo_geo_lib/rulesdb.py",
           "scripts/seo_geo_lib/report.py", "scripts/seo_geo_lib/fetch.py", "scripts/seo_geo_lib/stack.py",
           "tests/helpers.py", "tests/test_core.py", "tests/test_fetch.py", "tests/test_stack.py"]


def f(rule: str, **kw) -> Finding:
    kw.setdefault("message", "synthetic finding")
    return make(rule, kw.pop("message"), catalog=CAT, **kw)


class FingerprintTest(unittest.TestCase):
    def test_formula_matches_blueprint(self) -> None:
        x = f("CANON002", file="dist/a/index.html", url="https://example.com/a/", key="canonical-count")
        raw = "CANON002|dist/a/index.html|https://example.com/a/|canonical-count"
        self.assertEqual(x.fingerprint(), "SG-" + hashlib.sha1(raw.encode()).hexdigest()[:12])
        self.assertRegex(x.fingerprint(), r"^SG-[0-9a-f]{12}$")

    def test_stable_across_line_message_and_evidence_changes(self) -> None:
        a = f("CANON002", file="a.html", key="k", line=3, message="one", evidence={"n": 1})
        b = f("CANON002", file="a.html", key="k", line=99, message="two", evidence={"n": 2})
        self.assertEqual(a.fingerprint(), b.fingerprint())

    def test_identity_fields_change_fingerprint(self) -> None:
        base = f("CANON002", file="a.html", url="https://example.com/", key="k")
        for other in (f("CANON001", file="a.html", url="https://example.com/", key="k"),
                      f("CANON002", file="b.html", url="https://example.com/", key="k"),
                      f("CANON002", file="a.html", url="https://example.com/x", key="k"),
                      f("CANON002", file="a.html", url="https://example.com/", key="k2")):
            self.assertNotEqual(base.fingerprint(), other.fingerprint())

    def test_findings_are_hashable(self) -> None:
        a = f("META004", url="https://example.com/", evidence={"x": [1]})
        self.assertEqual(len({a, a}), 1)


class MakeTest(unittest.TestCase):
    def test_defaults_from_catalog_and_override(self) -> None:
        self.assertEqual(f("IDX001").severity, "warning")
        self.assertEqual(f("IDX001", severity="error").severity, "error")
        self.assertEqual(f("IDX001").effective_priority(CAT), "P0")

    def test_invalid_inputs(self) -> None:
        with self.assertRaises(KeyError):
            f("NOPE001")
        with self.assertRaises(ValueError):
            f("IDX001", severity="fatal")
        with self.assertRaises(ValueError):
            f("IDX001", confidence="certain")
        with self.assertRaises(ValueError):
            f("IDX001", priority="P9")
        with self.assertRaises(TypeError):
            f("IDX001", colour="red")

    def test_normalization(self) -> None:
        x = f("IMG001", file="dist\\img\\a.html", line=0, sample=["u1", "u1", "u2"], affected=1,
              evidence={"src": "x" * 500})
        self.assertEqual(x.file, "dist/img/a.html")
        self.assertIsNone(x.line)
        self.assertEqual(x.sample, ("u1", "u2"))
        self.assertEqual(x.affected, 2)
        self.assertEqual(len(x.evidence["src"]), 200)
        self.assertTrue(x.evidence["src"].endswith("\u2026"))
        many = f("IMG001", sample=["s%d" % i for i in range(30)])
        self.assertEqual(len(many.sample), findings.SAMPLE_LIMIT)
        self.assertEqual(many.affected, 30)

    def test_default_catalog_used(self) -> None:
        self.assertEqual(make("CANON002", "m").severity, "error")


class TruncateTest(unittest.TestCase):
    def test_strings_lists_dicts(self) -> None:
        self.assertEqual(truncate("abc", 200), "abc")
        self.assertEqual(len(truncate("a" * 201)), 200)
        self.assertEqual(truncate("a" * 200), "a" * 200)
        nested = truncate({"k" * 300: ["v" * 300] * 25})
        key = next(iter(nested))
        self.assertEqual(len(key), 200)
        self.assertEqual(len(nested[key]), 21)
        self.assertTrue(nested[key][-1].startswith("\u2026 (+5 more)"))

    def test_non_json_values(self) -> None:
        self.assertEqual(truncate(float("nan")), "nan")
        self.assertEqual(truncate({"b", "a"}), ["a", "b"])
        self.assertEqual(truncate((1, 2)), [1, 2])
        self.assertEqual(truncate(Path("x/y")), "x/y")
        deep: dict = {}
        node = deep
        for _ in range(20):
            node["n"] = {}
            node = node["n"]
        json.dumps(truncate(deep))  # bounded depth, serializable


class DedupeSortTest(unittest.TestCase):
    def test_dedupe_merges_scope(self) -> None:
        a = f("META003", key="title:Home", sample=["https://example.com/a"], affected=1)
        b = f("META003", key="title:Home", sample=["https://example.com/b"], affected=1, severity="error")
        c = f("META003", key="title:About", sample=["https://example.com/c"])
        out = dedupe([a, b, c])
        self.assertEqual(len(out), 2)
        merged = out[0]
        self.assertEqual(merged.sample, ("https://example.com/a", "https://example.com/b"))
        self.assertEqual(merged.affected, 2)
        self.assertEqual(merged.severity, "error")
        self.assertEqual(dedupe(out), out)

    def test_dedupe_keeps_larger_affected_and_priority(self) -> None:
        a = f("LINK005", key="site", affected=40)
        b = findings.escalate(f("LINK005", key="site", affected=3), CAT)
        out = dedupe([a, b])
        self.assertEqual(out[0].affected, 40)
        self.assertIsNone(out[0].priority)  # LINK005 is not a blocker, so escalate() kept it unchanged

    def test_sort_order(self) -> None:
        items = [
            f("META004", url="https://example.com/b"),                    # P2 info
            f("CANON002", url="https://example.com/z"),                   # P1 error
            f("CANON001", url="https://example.com/a"),                   # P2 warning
            f("IDX001", url="https://example.com/x"),                     # P0 warning
            findings.escalate(f("REND001", url="https://example.com/"), CAT),  # P0 error
            f("CANON002", file="a.html", line=9), f("CANON002", file="a.html", line=2, key="2"),
        ]
        order = [(x.rule, x.file, x.line) for x in sort_findings(items, CAT)]
        self.assertEqual(order, [("REND001", None, None), ("IDX001", None, None), ("CANON002", None, None),
                                 ("CANON002", "a.html", 2), ("CANON002", "a.html", 9), ("CANON001", None, None),
                                 ("META004", None, None)])
        self.assertEqual(sort_findings(list(reversed(items)), CAT), sort_findings(items, CAT))

    def test_escalate_only_blockers(self) -> None:
        self.assertEqual(findings.escalate(f("CONT004"), CAT).priority, "P0")
        self.assertIsNone(findings.escalate(f("CANON002"), CAT).priority)


class GateTest(unittest.TestCase):
    def test_semantics(self) -> None:
        info, warn, err = f("META004"), f("CANON001"), f("CANON002")
        self.assertFalse(gate_tripped([], "info"))
        self.assertTrue(gate_tripped([err], "error"))
        self.assertFalse(gate_tripped([warn, info], "error"))
        self.assertTrue(gate_tripped([warn], "warning"))
        self.assertFalse(gate_tripped([info], "warning"))
        self.assertTrue(gate_tripped([info], "info"))
        self.assertFalse(gate_tripped([err], "never"))
        with self.assertRaises(ValueError):
            gate_tripped([err], "fatal")


class EnvelopeTest(unittest.TestCase):
    def build(self, found, checks=("pages",), scores=None, **kw):
        res = Result(command="audit-build", target={"type": "build-dir", "path": "dist", "base_url": "https://example.com"},
                     findings=list(found), checks_run=list(checks), **kw)
        return res.to_envelope(CAT, now=helpers.NOW, scores=scores)

    def test_keys_and_summary(self) -> None:
        env = self.build([f("CANON002", key="a"), f("CANON002", key="a"), f("META004")], summary={"pages": 3},
                         checks_skipped=[{"check": "http", "reason": "offline build"}], not_measured=["indexing"],
                         limitations=["Local HTML cannot establish HTTP status."], data={"pages": 3})
        self.assertEqual(set(env), ENVELOPE_KEYS)
        self.assertEqual(env["tool"], "seo-geo-god")
        self.assertEqual(env["schema_version"], "1.0")
        self.assertEqual(env["generated_at"], helpers.NOW)
        self.assertEqual(env["facts_as_of"], "2026-11-01")
        self.assertEqual(env["rules_version"], "2026.11.0")
        self.assertEqual(env["summary"], {"error": 1, "warning": 0, "info": 1, "pages": 3})
        self.assertEqual(len(env["findings"]), 2)
        self.assertIsNone(env["scores"])
        self.assertEqual(env["untrusted_fields"], sorted(env["untrusted_fields"]))
        self.assertIn("findings[].evidence", env["untrusted_fields"])
        self.assertEqual(helpers.validate_schema(env, "result.schema.json"), [])
        for item in env["findings"]:
            self.assertEqual(helpers.validate_schema(item, "finding.schema.json"), [])
            self.assertEqual(item["as_of"], FACTS_AS_OF)

    def test_finding_dict_fields(self) -> None:
        d = f("CANON002", file="dist/a.html", url="https://example.com/a", line=14, key="k",
              evidence={"observed": ["https://example.com/a", "https://example.com/b"]}).to_dict(CAT)
        self.assertEqual(d["title"], "Multiple canonical links")
        self.assertEqual((d["category"], d["priority"], d["evidence_class"]), ("crawl_index", "P1", "A"))
        self.assertEqual(d["scope"], {"affected": 1, "sample": []})
        self.assertIn("fact:F-T-21", d["refs"])

    def test_via_proxy_and_errors(self) -> None:
        self.assertNotIn("via_proxy", self.build([]))
        env = self.build([], via_proxy=True, error="network disabled: pass --live to fetch")
        self.assertTrue(env["via_proxy"])
        self.assertEqual(helpers.validate_schema(env, "result.schema.json"), [])

    def test_scores_option(self) -> None:
        env = self.build([f("META002")], checks=("pages", "jsonld", "sitemaps"), scores="both")
        self.assertEqual(set(env["scores"]["profiles"]), {"seo", "geo"})
        self.assertIn("not a ranking", env["scores"]["note"])
        self.assertEqual(helpers.validate_schema(env, "result.schema.json"), [])
        self.assertEqual(set(self.build([], scores="geo")["scores"]["profiles"]), {"geo"})
        self.assertIsNone(self.build([], scores="none")["scores"])
        with self.assertRaises(ValueError):
            self.build([], scores="all")

    def test_schema_rejects_bad_finding(self) -> None:
        d = f("CANON002").to_dict(CAT)
        d["severity"] = "fatal"
        d["id"] = "SG-xyz"
        problems = helpers.validate_schema(d, "finding.schema.json")
        self.assertTrue(any("severity" in p for p in problems) and any(".id" in p for p in problems))


class ScoreTest(unittest.TestCase):
    def cat_score(self, found, checks=("pages",), profile="seo", cid="crawl_index"):
        return compute_scores(found, list(checks), CAT, profile)["categories"][cid]

    def test_null_below_70_percent_and_boundary(self) -> None:
        low = compute_scores([], ["jsonld"], CAT, "seo")
        self.assertIsNone(low["overall"])
        self.assertEqual(low["overall_reason"], "measured weight 8% < 70%")
        self.assertEqual(low["measured_weight"], 0.08)
        exact = ["launch", "duplicates", "sitemaps", "links", "content", "llms"]  # 22+12+10+10+8+8 = 70
        at = compute_scores([], exact, CAT, "seo")
        self.assertEqual((at["overall"], at["measured_weight"], at["overall_reason"]), (100, 0.7, None))
        below = compute_scores([], exact[:-1], CAT, "seo")
        self.assertIsNone(below["overall"])
        self.assertIn("62%", below["overall_reason"])

    def test_unmeasured_category_is_null_even_with_findings(self) -> None:
        cats = compute_scores([f("SD001")], ["pages"], CAT, "seo")["categories"]
        self.assertEqual(cats["structured_data"], {"score": None, "measured": False})
        self.assertNotIn("monitoring", cats)
        self.assertNotIn("fidelity", cats)

    def test_class_factors(self) -> None:
        self.assertEqual(self.cat_score([f("META009")], cid="metadata")["score"], 96)     # A warning: 4
        self.assertEqual(self.cat_score([f("META002")], cid="metadata")["score"], 98)     # C warning: 2
        self.assertEqual(self.cat_score([f("CANON002")])["score"], 88)                    # A error: 12
        self.assertEqual(self.cat_score([f("CANON008")])["score"], 100)                   # info: 0
        d_rule = f("AGENT001", severity="warning")
        self.assertEqual(self.cat_score([d_rule], checks=("llms",), cid="ai_access")["score"], 100)  # D: 0

    def test_scope_multipliers(self) -> None:
        self.assertEqual(self.cat_score([f("CANON001", affected=1)])["score"], 96)
        self.assertEqual(self.cat_score([f("CANON001", affected=2)])["score"], 94)
        self.assertEqual(self.cat_score([f("CANON001", affected=9)])["score"], 94)
        self.assertEqual(self.cat_score([f("CANON001", affected=10)])["score"], 92)
        self.assertEqual(self.cat_score([f("CRAWL009")], checks=("robots",))["score"], 92)  # site-scope rule

    def test_root_cause_dedup_and_max_severity(self) -> None:
        two = [f("CANON001", url="https://example.com/a"), f("CANON001", url="https://example.com/b")]
        self.assertEqual(self.cat_score(two)["score"], 94)  # one rule, 2 pages: 4 x 1.5
        mixed = [f("IDX001", url="https://example.com/a"), f("IDX001", url="https://example.com/b", severity="error")]
        self.assertEqual(self.cat_score(mixed)["score"], 82)  # error 12 x 1.5
        many = [f("CANON002"), f("CANON003"), f("HTTP001"), f("CANON004"), f("REDIR002"), f("REDIR003"),
                f("REDIR006"), f("LAUNCH003"), f("LAUNCH004"), f("CRAWL004")]
        floored = self.cat_score(many, checks=("pages", "robots"))
        self.assertEqual(floored["score"], 0)
        self.assertEqual(floored["rules_triggered"], sorted({x.rule for x in many}))

    def test_overall_weighted_mean_and_profiles(self) -> None:
        checks = ["pages", "duplicates", "links", "robots", "sitemaps", "hreflang", "jsonld", "content", "perf", "llms"]
        clean = compute_scores([], checks, CAT, "seo")
        self.assertEqual((clean["overall"], clean["measured_weight"]), (100, 1.0))
        seo = compute_scores([f("CONT004")], checks, CAT, "seo")
        geo = compute_scores([f("CONT004")], checks, CAT, "geo")
        self.assertEqual(seo["categories"]["content"]["score"], 88)
        self.assertEqual(seo["overall"], round((100 * 92 + 88 * 8) / 100))
        self.assertEqual(geo["overall"], round((100 * 80 + 88 * 20) / 100))
        with self.assertRaises(ValueError):
            compute_scores([], checks, CAT, "both")


class CatalogIntegrityTest(unittest.TestCase):
    def test_no_problems_and_every_blueprint_id(self) -> None:
        self.assertEqual(CAT.problems(), [])
        ids = [r.id for r in CAT.all()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sorted(ids), sorted(BLUEPRINT_IDS))
        self.assertEqual(len(ids), 198)
        self.assertNotIn("AGENT007", CAT)
        self.assertEqual({r.id for r in CAT.all() if r.status == "planned"}, PLANNED)

    def test_raw_entries_complete(self) -> None:
        raw = json.loads((DATA_DIR / "rules.json").read_text(encoding="utf-8"))
        self.assertEqual(raw["schema"], "seo-geo-god.rules/1")
        self.assertEqual(raw["as_of"], "2026-11-01")
        self.assertEqual(raw["rules_version"], "2026.11.0")
        required = {"id", "title", "category", "severity", "priority", "evidence_class", "effort", "impact", "status",
                    "owner", "fix_hint", "refs"}
        for entry in raw["rules"]:
            self.assertTrue(required <= set(entry), entry["id"])
            self.assertRegex(entry["id"], r"^[A-Z]{2,6}\d{3}$")
            self.assertLessEqual(len(entry["fix_hint"]), 200, entry["id"])
            self.assertNotRegex(entry["fix_hint"].lower(), r"guarantee")
            fam = entry["id"].rstrip("0123456789")
            self.assertIn(fam, raw["categories"][entry["category"]]["families"], entry["id"])
            if entry["effort"] is None:
                self.assertTrue(entry["id"].startswith("DRIFT"))

    def test_refs_point_to_known_facts_and_references(self) -> None:
        facts_md = helpers.REFERENCES_DIR / "current-facts.md"
        anchors = set(re.findall(r'<a id="(f-[a-z]+-\d{2})"', facts_md.read_text(encoding="utf-8"))) \
            if facts_md.is_file() else None
        for rule in CAT.all():
            for ref in rule.refs:
                if ref.startswith("fact:"):
                    self.assertIn(ref[5:], FACT_IDS, rule.id)
                    if anchors:
                        self.assertIn(ref[5:].lower(), anchors, "%s cites %s missing from current-facts.md" % (rule.id, ref))
                elif ref.startswith("references/"):
                    self.assertIn(ref.split("/", 1)[1].split("#")[0], REFERENCE_FILES, rule.id)
                else:
                    self.assertTrue(ref.startswith("https://"), ref)

    def test_weights_penalties_blockers(self) -> None:
        weights = {c: (m["weights"]["seo"], m["weights"]["geo"]) for c, m in CAT.categories.items() if m["scored"]}
        self.assertEqual(weights, {"crawl_index": (22, 15), "rendering": (12, 15), "metadata": (12, 5),
                                   "structured_data": (8, 8), "discovery": (10, 5), "architecture": (10, 7),
                                   "performance_media": (10, 5), "content": (8, 20), "ai_access": (8, 20)})
        self.assertEqual(CAT.penalties["class_factor"], {"A": 1, "B": 1, "C": 0.5, "D": 0})
        self.assertEqual((CAT.penalties["error"], CAT.penalties["warning"], CAT.penalties["info"]), (12, 4, 0))
        self.assertEqual(CAT.penalties["scope"], [[1, 1.0], [2, 1.5], [10, 2.0]])
        self.assertEqual(CAT.blockers, frozenset({"CRAWL004", "IDX001", "AI004", "LAUNCH003", "LAUNCH004", "REND001",
                                                  "SD012", "CONT004", "CONT010", "HTTP001"}))
        for check, cats in CAT.checks.items():
            self.assertTrue(set(cats) <= set(CAT.categories), check)

    def test_escalations(self) -> None:
        self.assertEqual(CAT.severity_for("IDX001"), "warning")
        self.assertEqual(CAT.severity_for("IDX001", expect_indexable=True), "error")
        self.assertEqual(CAT.severity_for("CRAWL001", profile="launch"), "warning")
        self.assertEqual(CAT.severity_for("SMAP001", profile="launch"), "warning")
        self.assertEqual(CAT.severity_for("SMAP001"), "info")
        self.assertEqual(CAT.severity_for("SD007", profile="launch"), "info")

    def test_catalog_load_errors(self) -> None:
        with self.assertRaises(ValueError):
            rulesdb.RuleCatalog({"rules": [{"id": "X"}]})
        entry = CAT.get("CANON002").to_dict()
        with self.assertRaises(ValueError):
            rulesdb.RuleCatalog({"rules": [entry, entry]})
        with self.assertRaises(KeyError):
            CAT.get("ZZZ999")
        broken = rulesdb.RuleCatalog({"schema": "x", "as_of": "soon", "rules": [dict(entry, severity="fatal",
                                                                                    refs=["wiki"])]})
        problems = broken.problems()
        self.assertTrue(any("severity" in p for p in problems) and any("refs" in p for p in problems))

    def test_rule_dataclass(self) -> None:
        rule = CAT.get("CANON002")
        self.assertEqual(rule.family, "CANON")
        self.assertEqual(rule.to_dict()["refs"], list(rule.refs))
        self.assertEqual(rulesdb.default_catalog().get("CANON002"), rule)


class DataFileTest(unittest.TestCase):
    def test_thresholds(self) -> None:
        th = rulesdb.thresholds()
        self.assertEqual(th["as_of"], "2026-11-01")
        self.assertEqual(th["cwv"]["lcp_ms"], [2500, 4000])
        self.assertEqual(th["cwv"]["inp_ms"], [200, 500])
        self.assertEqual(th["cwv"]["cls"], [0.1, 0.25])
        self.assertEqual((th["cwv"]["fcp_ms"], th["cwv"]["ttfb_ms"]), ([1800, 3000], [800, 1800]))
        self.assertEqual((th["googlebot_html_bytes"], th["robots_max_bytes"]), (2097152, 512000))
        self.assertEqual(th["sitemap"], {"source": th["sitemap"]["source"], "max_urls": 50000, "max_bytes": 52428800,
                                         "image_per_url": 1000, "news_max": 1000})
        self.assertEqual(th["indexnow"]["key_regex"], "^[A-Za-z0-9-]{8,128}$")
        self.assertEqual((th["fidelity"]["min_ratio"], th["fidelity"]["max_ratio"], th["fidelity"]["min_words"]),
                         (0.8, 1.6, 20))
        self.assertEqual(th["csr"]["root_text_max"], 50)
        self.assertEqual(th["gsc"]["striking"], [5, 20, 100])
        self.assertEqual(th["pseo"], {"source": "heuristic", "near_dup": 0.85, "shingle": 5})
        self.assertEqual(th["title_hint_chars"], 60)
        for key, value in th.items():
            if isinstance(value, dict) and key != "sources":
                self.assertIn("source", value, key)
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                self.assertIn(key, th["sources"], key)
        self.assertIn("heuristic", th["gsc"]["default_ctr_curve"]["source"])
        th["cwv"]["lcp_ms"] = [1, 2]
        self.assertEqual(rulesdb.thresholds()["cwv"]["lcp_ms"], [2500, 4000])

    def test_load_data_guards(self) -> None:
        self.assertEqual(rulesdb.load_data("rules")["schema"], "seo-geo-god.rules/1")
        for bad in ("../rules", "rules.json", "", "Rules"):
            with self.assertRaises(ValueError):
                rulesdb.load_data(bad)

    def test_json_guards(self) -> None:
        with self.assertRaises(ValueError):
            rulesdb.loads_json("[" * 300 + "]" * 300)
        self.assertIsInstance(rulesdb.loads_json("[" * 256 + "]" * 256), list)  # boundary: exactly 256 allowed
        self.assertEqual(rulesdb.loads_json('{"a": "%s"}' % ("[" * 400))["a"], "[" * 400)
        self.assertEqual(rulesdb.loads_json(b'\xef\xbb\xbf{"a": 1}'), {"a": 1})
        for bad in ('{"a": NaN}', '[Infinity]', b"\xff\xfe", "{"):
            with self.assertRaises(ValueError):
                rulesdb.loads_json(bad)
        with helpers.temp_dir() as d:
            p = d / "big.json"
            p.write_text("[" + "1," * 1000 + "1]", encoding="utf-8")
            with self.assertRaises(ValueError):
                rulesdb.read_json(p, max_bytes=100)
            self.assertEqual(len(rulesdb.read_json(p)), 1001)

    def test_freshness_statuses(self) -> None:
        today = date(2026, 11, 1)
        with helpers.temp_dir() as d:
            for name, age in (("fresh", 0), ("edge90", 90), ("aging", 91), ("edge180", 180), ("stale", 181)):
                (d / (name + ".json")).write_text(json.dumps({"as_of": (today - timedelta(days=age)).isoformat()}))
            (d / "noasof.json").write_text("{}")
            (d / "broken.json").write_text("{")
            (d / "notes.txt").write_text("ignored")
            with mock.patch.object(rulesdb, "DATA_DIR", d):
                rows = {r["file"]: r for r in rulesdb.freshness(today)}
        status = {k: v["status"] for k, v in rows.items()}
        self.assertEqual(status, {"data/aging.json": "aging", "data/broken.json": "unknown", "data/edge180.json": "aging",
                                  "data/edge90.json": "fresh", "data/fresh.json": "fresh", "data/noasof.json": "unknown",
                                  "data/stale.json": "stale"})
        self.assertEqual(rows["data/stale.json"]["age_days"], 181)
        self.assertIn("error", rows["data/broken.json"])
        self.assertEqual(list(rows), sorted(rows))

    def test_own_data_files_fresh(self) -> None:
        rows = {r["file"]: r for r in rulesdb.freshness(helpers.TODAY)}
        for name in ("data/rules.json", "data/thresholds.json"):
            self.assertEqual((rows[name]["status"], rows[name]["as_of"]), ("fresh", "2026-11-01"))
        later = {r["file"]: r["status"] for r in rulesdb.freshness(helpers.TODAY + timedelta(days=181))}
        self.assertEqual(later["data/rules.json"], "stale")

    def test_schemas_files(self) -> None:
        for name in ("finding.schema.json", "result.schema.json"):
            doc = json.loads((helpers.SCHEMAS_DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(doc["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(doc["as_of"], "2026-11-01")


class RenderTest(unittest.TestCase):
    def sample_env(self, extra=()):
        found = [f("CANON002", file="dist/a/index.html", url="https://example.com/a/", line=14, key="c",
                   evidence={"observed": ["https://example.com/a", "https://example.com/b"]}),
                 f("META004", url="https://example.com/b/"), f("AI004", file="dist/robots.txt", line=2)] + list(extra)
        res = Result(command="audit-build", target={"type": "build-dir", "path": "dist", "base_url": "https://example.com"},
                     findings=found, checks_run=["pages", "robots"],
                     checks_skipped=[{"check": "http", "reason": "offline build: HTTP status not observable"}])
        return res.to_envelope(CAT, now=helpers.NOW, scores="seo")

    def test_json_format(self) -> None:
        env = self.sample_env([f("META002", url="https://example.com/c", evidence={"t": "a\u2028b\u202ec\x85"})])
        text = report.render(env, "json", CAT)
        self.assertTrue(text.endswith("}\n"))
        self.assertEqual(json.loads(text), env)
        for ch in ("\u2028", "\u202e", "\x85"):
            self.assertNotIn(ch, text)
        self.assertIn("\\u202e", text)
        self.assertEqual(text, json.dumps(env, indent=2, sort_keys=True, ensure_ascii=False)
                         .replace("\u2028", "\\u2028").replace("\u202e", "\\u202e").replace("\x85", "\\u0085") + "\n")

    def test_sarif_shape(self) -> None:
        abs_file = os.path.join(os.getcwd(), "dist", "abs", "index.html")
        env = self.sample_env([f("LINK001", file=abs_file, line=3)])
        sarif = json.loads(report.render(env, "sarif", CAT))
        self.assertEqual(sarif["$schema"], "https://json.schemastore.org/sarif-2.1.0.json")
        self.assertEqual(sarif["version"], "2.1.0")
        run = sarif["runs"][0]
        driver = run["tool"]["driver"]
        self.assertEqual((driver["name"], driver["semanticVersion"]), ("seo-geo-god", "1.0.1"))
        rule_ids = [r["id"] for r in driver["rules"]]
        self.assertEqual(rule_ids, sorted({x["rule"] for x in env["findings"]}))
        for r in driver["rules"]:
            self.assertEqual(set(r) - {"helpUri"}, {"id", "name", "shortDescription", "fullDescription",
                                                    "defaultConfiguration", "properties"})
            self.assertEqual(set(r["properties"]), {"category", "priority", "evidenceClass", "tags"})
        canon = next(r for r in driver["rules"] if r["id"] == "CANON002")
        self.assertTrue(canon["helpUri"].startswith("https://developers.google.com/"))
        levels = {res["ruleId"]: res["level"] for res in run["results"]}
        self.assertEqual((levels["CANON002"], levels["META004"], levels["AI004"]), ("error", "note", "error"))
        for res in run["results"]:
            self.assertEqual(rule_ids[res["ruleIndex"]], res["ruleId"])
            self.assertRegex(res["partialFingerprints"]["seoGeoGod/v1"], r"^SG-[0-9a-f]{12}$")
            self.assertEqual(set(res["properties"]), {"priority", "url", "confidence", "evidence"})
            uri = res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
            self.assertFalse(uri.startswith("/"), uri)
        by_rule = {res["ruleId"]: res for res in run["results"]}
        loc = by_rule["CANON002"]["locations"][0]["physicalLocation"]
        self.assertEqual(loc, {"artifactLocation": {"uri": "dist/a/index.html"}, "region": {"startLine": 14}})
        self.assertEqual(by_rule["LINK001"]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
                         "dist/abs/index.html")
        self.assertEqual(by_rule["META004"]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
                         "https://example.com/b/")
        inv = run["invocations"][0]
        self.assertTrue(inv["executionSuccessful"])
        self.assertIn("skipped http", inv["toolExecutionNotifications"][0]["message"]["text"])
        self.assertEqual(run["properties"], {"factsAsOf": "2026-11-01", "rulesVersion": "2026.11.0", "mode": "offline"})

    def test_markdown_structure(self) -> None:
        md = report.render(self.sample_env(), "md", CAT)
        self.assertLess(md.index("## Coverage and limitations"), md.index("## Findings"))
        self.assertIn("Skipped http: offline build: HTTP status not observable", md)
        self.assertIn("not measured", md)
        self.assertIn("not a ranking, traffic or citation prediction", md)
        self.assertLess(md.index("### P0"), md.index("### P1"))
        self.assertLess(md.index("### P1"), md.index("### P2"))
        self.assertIn("| Priority | Rule | Severity | Where | Finding | Fix |", md)
        self.assertTrue(md.rstrip().endswith(report.UNTRUSTED_FOOTER))
        self.assertIn("`dist/a/index.html:14`", md)

    def test_markdown_escaping(self) -> None:
        hostile = 'Title <script>alert(1)</script> | `tick` [x](javascript:alert(1)) <img src=x onerror="a()">\n# H'
        env = self.sample_env([f("META002", url="https://example.com/h", message=hostile,
                                 evidence={"title": hostile + "\u202e"})])
        md = report.render(env, "md", CAT)
        self.assertNotIn("<", md)
        self.assertNotIn("\u202e", md)
        self.assertNotRegex(md, r"<[^>]*\son\w+=")
        row = next(line for line in md.splitlines() if "META002" in line and line.startswith("| P"))
        self.assertEqual(len(re.findall(r"(?<!\\)\|", row)), 7)
        self.assertIn("\\`tick\\`", row)
        self.assertIn("\\[x\\]", row)

    def test_markdown_property_hostile_titles(self) -> None:
        rnd = helpers.seeded_random()
        alphabet = list("<>|`*_[]()&#!\\\n\r\t\"'=/ abcSCRIPTonerror") + ["\u202e", "\u200b", "\u2028", "<script", "onload="]
        for _ in range(200):
            text = "".join(rnd.choice(alphabet) for _ in range(rnd.randint(1, 60)))
            env = self.sample_env([f("META002", url="https://example.com/p" + text, message=text, evidence={"v": text})])
            md = report.to_markdown(env)
            self.assertNotIn("<", md)
            self.assertNotRegex(md, "[\u202e\u200b\u2028]")
            for line in md.splitlines():
                if line.startswith("| P") and "META002" in line:
                    self.assertEqual(len(re.findall(r"(?<!\\)\|", line.replace("\\\\", ""))), 7, line)

    def test_text_format(self) -> None:
        env = self.sample_env([f("META002", url="https://example.com/n", message="line1\nline2")])
        lines = report.render(env, "text", CAT).splitlines()
        self.assertEqual(len(lines), len(env["findings"]) + 1)
        self.assertTrue(lines[0].startswith("ERROR "))
        self.assertIn("WARNING META002 https://example.com/n \u2014 line1 line2", lines)
        self.assertIn("error(s)", lines[-1])

    def test_render_rejects_unknown_format(self) -> None:
        with self.assertRaises(ValueError):
            report.render(self.sample_env(), "html", CAT)

    def test_error_envelope_renders(self) -> None:
        res = Result(command="audit-url", target={"type": "url", "url": "https://example.com/"}, mode="live",
                     error="network disabled: pass --live to fetch")
        env = res.to_envelope(CAT, now=helpers.NOW)
        self.assertIn("**Error:** network disabled", report.to_markdown(env))
        self.assertFalse(json.loads(report.render(env, "sarif", CAT))["runs"][0]["invocations"][0]["executionSuccessful"])
        self.assertIn("error: network disabled", report.to_text(env))

    def test_resolve_now(self) -> None:
        self.assertEqual(report.resolve_now("2026-11-01T00:00:00Z"), "2026-11-01T00:00:00Z")
        with mock.patch.dict(os.environ, {"SEO_GEO_GOD_NOW": "2026-11-01T12:30:00+01:00"}):
            self.assertEqual(report.resolve_now(), "2026-11-01T12:30:00+01:00")
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertRegex(report.resolve_now(), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        with self.assertRaises(ValueError):
            report.resolve_now("yesterday")


class WriteOutputTest(unittest.TestCase):
    def test_exclusive_create_and_force(self) -> None:
        with helpers.temp_dir() as d:
            target = d / "reports" / "out.json"
            report.write_output("one\n", str(target))
            self.assertEqual(target.read_text(encoding="utf-8"), "one\n")
            with self.assertRaises(report.OutputRefused):
                report.write_output("two\n", str(target))
            self.assertEqual(target.read_text(encoding="utf-8"), "one\n")
            report.write_output("three\n", str(target), force=True)
            self.assertEqual(target.read_text(encoding="utf-8"), "three\n")

    def test_refuses_inside_audited_dir(self) -> None:
        with helpers.temp_dir() as d:
            build = d / "dist"
            (build / "sub").mkdir(parents=True)
            for path in (build / "report.json", build / "sub" / "r.md", d / "dist" / ".." / "dist" / "x.json", build):
                with self.assertRaises(report.OutputRefused):
                    report.write_output("x", str(path), forbid_under=[str(build)])
            link = d / "alias"
            os.symlink(build, link)
            with self.assertRaises(report.OutputRefused):
                report.write_output("x", str(link / "r.json"), forbid_under=[str(build)])
            report.write_output("ok", str(d / "dist-report.json"), forbid_under=[str(build)])
            self.assertTrue((d / "dist-report.json").is_file())
            self.assertEqual(list(build.rglob("*.json")), [])

    def test_refuses_non_regular_targets(self) -> None:
        with helpers.temp_dir() as d:
            (d / "real.txt").write_text("keep", encoding="utf-8")
            os.symlink(d / "real.txt", d / "link.txt")
            with self.assertRaises(report.OutputRefused):
                report.write_output("x", str(d / "link.txt"), force=True)
            self.assertEqual((d / "real.txt").read_text(encoding="utf-8"), "keep")
            (d / "adir").mkdir()
            with self.assertRaises(report.OutputRefused):
                report.write_output("x", str(d / "adir"), force=True)

    def test_stdout(self) -> None:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            report.write_output("to stdout\n", None)
            report.write_output("dash\n", "-")
        self.assertEqual(buf.getvalue(), "to stdout\ndash\n")


class SyntaxTest(unittest.TestCase):
    def test_wp01_files_parse_as_python39(self) -> None:
        for rel in WP01_PY:
            helpers.parse_py39(helpers.PLUGIN_ROOT / rel)

    def test_no_network_attempts(self) -> None:
        self.assertEqual(helpers.network_attempts(), [])


if __name__ == "__main__":
    unittest.main()
