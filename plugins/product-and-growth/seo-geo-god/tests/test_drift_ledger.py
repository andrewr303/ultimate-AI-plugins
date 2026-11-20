"""WP06: drift snapshots and DRIFT001-020, audit-history diff, observation ledger and statistics."""
from __future__ import annotations

import copy
import json
import os
import sys
import unittest
from datetime import date
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_drift_ledger
import helpers  # noqa: E402
from seo_geo_lib import drift, ledger  # noqa: E402
from seo_geo_lib.findings import Result, make  # noqa: E402

NOW = helpers.NOW
BASE = "https://example.com"


def setUpModule() -> None:
    helpers.block_network()


def load_fixture(name):
    return json.loads(helpers.read_fixture("drift", name))


def record(path, **kw):
    rec = {"url": BASE + path, "status": 200, "title": "Title", "meta_description": "Description.",
           "canonical": BASE + path, "robots": [], "x_robots": None, "h1": "Heading", "h2": ["A"], "hreflang": [],
           "jsonld_types": ["WebPage"], "og": {"og:title": "T"}, "word_count": 400, "internal_links": 10,
           "content_hash": "a" * 64, "noindex": False}
    rec.update(kw)
    return rec


def snap(records, *, type_="build-dir", base_url=BASE, version="1.0.0", robots=None):
    return drift.snapshot(records, source={"type": type_, "path": "dist", "base_url": base_url, "profile": "default"},
                          tool_version=version, now=NOW, robots_txt=robots)


def pair(before, after):
    """Compare one page changed from `before` fields to `after` fields; returns rule ids (sorted)."""
    data, found = drift.compare(snap([record("/p/", **before)]), snap([record("/p/", **after)]))
    return sorted(f.rule for f in found), found, data


class NormalizeUrlTests(unittest.TestCase):
    def test_scheme_host_port_query_fragment_and_slash(self):
        self.assertEqual(drift.normalize_url("HTTPS://Example.COM:443/Blog/Post/?utm_source=x&b=2&a=1#top"),
                         "https://example.com/Blog/Post?a=1&b=2")

    def test_root_keeps_slash_and_empty_path_becomes_root(self):
        self.assertEqual(drift.normalize_url("https://example.com"), "https://example.com/")
        self.assertEqual(drift.normalize_url("https://example.com/"), "https://example.com/")

    def test_non_default_port_kept_default_http_port_dropped(self):
        self.assertEqual(drift.normalize_url("http://example.com:8080/a/"), "http://example.com:8080/a")
        self.assertEqual(drift.normalize_url("http://example.com:80/a"), "http://example.com/a")
        self.assertEqual(drift.normalize_url("https://example.com:80/a"), "https://example.com:80/a")

    def test_all_utm_parameters_dropped_case_insensitively(self):
        self.assertEqual(drift.normalize_url("https://example.com/?UTM_Medium=x&utm_campaign=y&id=3"),
                         "https://example.com/?id=3")

    def test_userinfo_dropped_and_blank_values_kept(self):
        self.assertEqual(drift.normalize_url("https://user:pw@example.com/a?x="), "https://example.com/a?x=")

    def test_path_only_urls_stay_path_only(self):
        self.assertEqual(drift.normalize_url("/blog/"), "/blog")
        self.assertEqual(drift.normalize_url("/"), "/")

    def test_equivalent_spellings_share_one_key(self):
        a = drift.normalize_url("https://EXAMPLE.com/docs/?b=1&a=2")
        b = drift.normalize_url("https://example.com/docs?a=2&b=1&utm_term=z")
        self.assertEqual(a, b)


class SnapshotTests(unittest.TestCase):
    def test_pages_keyed_by_normalized_url_with_known_fields_only(self):
        doc = snap([record("/b/", extra="dropped"), record("/a/")])
        self.assertEqual(doc["schema"], drift.SNAPSHOT_SCHEMA)
        self.assertEqual(list(doc["pages"]), [BASE + "/a", BASE + "/b"])
        self.assertEqual(sorted(doc["pages"][BASE + "/a"]), sorted(drift.RECORD_FIELDS))
        self.assertNotIn("extra", doc["pages"][BASE + "/b"])
        self.assertEqual(doc["created"], NOW)
        json.dumps(doc)

    def test_missing_fields_become_null(self):
        doc = drift.snapshot([{"url": BASE + "/x/"}], source={"type": "live"}, tool_version="1.0.0", now=NOW)
        self.assertIsNone(doc["pages"][BASE + "/x"]["canonical"])
        self.assertIsNone(doc["robots_sha256"])

    def test_url_collision_keeps_first_and_is_reported(self):
        doc = snap([record("/a/", title="first"), record("/a", title="second")])
        self.assertEqual(doc["pages"][BASE + "/a"]["title"], "first")
        self.assertEqual(doc["url_collisions"], [BASE + "/a"])

    def test_robots_hash_ignores_line_ending_style(self):
        lf = snap([], robots="User-agent: *\nDisallow: /x\n")
        crlf = snap([], robots="User-agent: *\r\nDisallow: /x\r\n")
        self.assertEqual(lf["robots_sha256"], crlf["robots_sha256"])
        self.assertNotEqual(lf["robots_sha256"], snap([], robots="User-agent: *\n")["robots_sha256"])

    def test_invalid_inputs_refused(self):
        with self.assertRaises(ValueError):
            drift.snapshot([record("/a/")], source={}, tool_version="1.0.0", now=NOW)
        with self.assertRaises(ValueError):
            drift.snapshot([{"title": "no url"}], source={"type": "live"}, tool_version="1.0.0", now=NOW)


class DriftFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = load_fixture("EXPECTED.json")
        cls.data, cls.found = drift.compare(load_fixture("baseline.json"), load_fixture("current.json"))

    def test_each_fixture_page_triggers_exactly_its_rule(self):
        by_url = {}
        for f in self.found:
            if f.rule != "DRIFT019":
                by_url.setdefault(drift.normalize_url(f.url), []).append(f.rule)
        for url, rule in self.expected["pages"].items():
            with self.subTest(url=url):
                self.assertEqual(by_url.get(url, []), [rule] if rule else [])

    def test_every_drift_rule_except_the_gate_is_covered(self):
        self.assertEqual(helpers.rule_ids(self.found), ["DRIFT%03d" % i for i in range(1, 20)])

    def test_deltas_summary_and_robots_diff(self):
        deltas = self.data["deltas"]
        self.assertTrue(self.data["comparable"])
        self.assertEqual(deltas["summary"], {"added": 1, "removed": 1, "changed": 18, "unchanged": 1})
        self.assertTrue(deltas["robots"]["changed"])
        self.assertIn("+Disallow: /drafts/", deltas["robots"]["diff"])

    def test_site_level_robots_finding_uses_base_url(self):
        robots = helpers.findings_for(self.found, "DRIFT019")
        self.assertEqual(len(robots), 1)
        self.assertEqual(robots[0].url, BASE)
        self.assertEqual(robots[0].evidence["state"], "changed")
        self.assertEqual(robots[0].affected, 20)

    def test_retired_type_removal_is_info_and_other_removal_error(self):
        sev = {drift.normalize_url(f.url): f.severity for f in helpers.findings_for(self.found, "DRIFT010")}
        self.assertEqual(sev[BASE + "/retired-removed"], "info")
        self.assertEqual(sev[BASE + "/types-removed"], "error")

    def test_findings_match_the_finding_schema_and_catalog(self):
        cat = helpers.catalog()
        for f in self.found:
            with self.subTest(rule=f.rule, url=f.url):
                self.assertEqual(helpers.validate_schema(f.to_dict(cat), "finding.schema.json"), [])
                self.assertEqual(cat.get(f.rule).owner, "drift")

    def test_fingerprints_are_stable_across_runs(self):
        _, again = drift.compare(load_fixture("baseline.json"), load_fixture("current.json"))
        self.assertEqual(sorted(f.fingerprint() for f in again), sorted(f.fingerprint() for f in self.found))

    def test_other_origin_fixture_is_withheld(self):
        data, found = drift.compare(load_fixture("baseline.json"), load_fixture("current-other-origin.json"))
        self.assertEqual([f.rule for f in found], ["DRIFT020"])
        self.assertFalse(data["comparable"])
        self.assertIsNone(data["deltas"])
        self.assertIn("base URL differs", data["reasons"][0])

    def test_identical_snapshots_have_no_findings(self):
        base = load_fixture("baseline.json")
        data, found = drift.compare(base, copy.deepcopy(base))
        self.assertEqual(found, [])
        self.assertEqual(data["deltas"]["summary"]["unchanged"], 20)
        self.assertFalse(data["deltas"]["robots"]["changed"])


class ComparabilityGateTests(unittest.TestCase):
    def gate(self, baseline, current):
        data, found = drift.compare(baseline, current)
        return data, [f.rule for f in found]

    def test_major_version_differs(self):
        data, rules = self.gate(snap([record("/a/")]), snap([record("/a/", title="New")], version="2.0.0"))
        self.assertEqual(rules, ["DRIFT020"])
        self.assertIsNone(data["deltas"])
        self.assertIn("tool major version", data["reasons"][0])

    def test_minor_version_difference_is_comparable(self):
        data, rules = self.gate(snap([record("/a/")]), snap([record("/a/", title="New")], version="1.4.2"))
        self.assertTrue(data["comparable"])
        self.assertEqual(rules, ["DRIFT008"])

    def test_source_type_differs(self):
        data, rules = self.gate(snap([record("/a/")]), snap([record("/a/")], type_="live"))
        self.assertEqual(rules, ["DRIFT020"])
        self.assertIn("source type differs", data["reasons"][0])

    def test_base_url_differs_including_missing(self):
        _, rules = self.gate(snap([record("/a/")]), snap([record("/a/")], base_url=None))
        self.assertEqual(rules, ["DRIFT020"])

    def test_base_url_spelling_variants_are_the_same(self):
        _, rules = self.gate(snap([record("/a/")]), snap([record("/a/")], base_url="HTTPS://EXAMPLE.COM/"))
        self.assertEqual(rules, [])

    def test_schema_differs_and_reasons_accumulate(self):
        other = snap([record("/a/")], type_="live", version="3.0.0")
        other["schema"] = "seo-geo-god.snapshot/2"
        data, rules = self.gate(snap([record("/a/")]), other)
        self.assertEqual(rules, ["DRIFT020"])
        self.assertEqual(len(data["reasons"]), 3)

    def test_gate_finding_is_site_level(self):
        _, found = drift.compare(snap([record("/a/"), record("/b/")]), snap([record("/a/")], version="2.0.0"))
        self.assertEqual(found[0].url, BASE)
        self.assertEqual(found[0].affected, 2)

    def test_non_snapshot_input_refused(self):
        with self.assertRaises(ValueError):
            drift.compare({"pages": []}, snap([]))
        with self.assertRaises(ValueError):
            drift.compare(snap([]), {"source": {}, "pages": {"x": "not an object"}})


class DriftRuleBoundaryTests(unittest.TestCase):
    def test_drift001_status_transitions(self):
        self.assertEqual(pair({"status": 200}, {"status": 500})[0], ["DRIFT001"])
        self.assertEqual(pair({"status": 204}, {"status": 410})[0], ["DRIFT001"])
        self.assertEqual(pair({"status": 200}, {"status": 301})[0], [])
        self.assertEqual(pair({"status": 301}, {"status": 404})[0], [])
        self.assertEqual(pair({"status": None}, {"status": 404})[0], [])

    def test_drift002_from_tokens_when_flag_absent(self):
        rules, _, _ = pair({"noindex": None}, {"noindex": None, "x_robots": {"googlebot": ["noindex"]}})
        self.assertEqual(rules, ["DRIFT002"])
        rules, _, _ = pair({"noindex": None}, {"noindex": None, "robots": ["none"]})
        self.assertEqual(rules, ["DRIFT002", "DRIFT013"])

    def test_noindex_removed_is_a_delta_without_finding(self):
        rules, _, data = pair({"robots": ["noindex"], "noindex": True}, {"robots": [], "noindex": False})
        self.assertEqual(rules, [])
        self.assertEqual(data["deltas"]["pages"][0]["changes"]["noindex"], {"before": True, "after": False})

    def test_drift003_and_drift004_canonical(self):
        self.assertEqual(pair({}, {"canonical": BASE + "/p"})[0], ["DRIFT003"])
        self.assertEqual(pair({}, {"canonical": "HTTPS://EXAMPLE.COM/p/"})[0], [])
        self.assertEqual(pair({}, {"canonical": None})[0], ["DRIFT004"])
        self.assertEqual(pair({"canonical": None}, {"canonical": BASE + "/p/"})[0], [])

    def test_drift005_and_drift008_title(self):
        self.assertEqual(pair({"title": "Pricing"}, {"title": None})[0], ["DRIFT005"])
        self.assertEqual(pair({"title": "Pricing"}, {"title": "  "})[0], ["DRIFT005"])
        self.assertEqual(pair({"title": "Pricing"}, {"title": "Plans"})[0], ["DRIFT008"])
        self.assertEqual(pair({"title": "Pricing  plans"}, {"title": " Pricing plans "})[0], [])
        self.assertEqual(pair({"title": None}, {"title": "Pricing"})[0], [])

    def test_drift006_and_drift007_h1_similarity_boundary(self):
        self.assertEqual(pair({"h1": "Send invoices"}, {"h1": None})[0], ["DRIFT006"])
        self.assertEqual(pair({"h1": "abcd"}, {"h1": "abef"})[0], [])  # ratio exactly 0.5: not below
        self.assertEqual(pair({"h1": "abcd"}, {"h1": "aefg"})[0], ["DRIFT007"])
        self.assertEqual(pair({"h1": "Send Invoices"}, {"h1": "send invoices"})[0], [])
        _, found, _ = pair({"h1": "abcd"}, {"h1": "wxyz"})
        self.assertEqual(found[0].evidence["similarity"], 0.0)

    def test_drift009_description_changed_or_removed_not_added(self):
        self.assertEqual(pair({}, {"meta_description": "Other."})[0], ["DRIFT009"])
        _, found, _ = pair({}, {"meta_description": None})
        self.assertIn("removed", found[0].message)
        self.assertEqual(pair({"meta_description": None}, {"meta_description": "New."})[0], [])

    def test_drift010_mixed_removal_stays_error(self):
        _, found, _ = pair({"jsonld_types": ["FAQPage", "Article"]}, {"jsonld_types": []})
        self.assertEqual(found[0].severity, "error")
        self.assertEqual(found[0].evidence["retired_types"], ["FAQPage"])

    def test_drift010_schema_org_prefixes_are_normalized(self):
        rules, found, _ = pair({"jsonld_types": ["https://schema.org/HowTo"]}, {"jsonld_types": []})
        self.assertEqual((rules, found[0].severity), (["DRIFT010"], "info"))
        self.assertEqual(pair({"jsonld_types": ["schema.org/Article"]}, {"jsonld_types": ["Article"]})[0], [])

    def test_retired_types_come_from_structured_data_json(self):
        self.assertTrue({"FAQPage", "HowTo", "SpecialAnnouncement"} <= drift.retired_types())
        self.assertNotIn("WebSite", drift.retired_types())  # only its SearchAction feature was retired

    def test_drift011_types_added(self):
        self.assertEqual(pair({"jsonld_types": []}, {"jsonld_types": ["Product"]})[0], ["DRIFT011"])

    def test_drift012_hreflang_set_compared_as_a_set(self):
        a = [["en", BASE + "/p/"], ["de", BASE + "/de/p/"]]
        self.assertEqual(pair({"hreflang": a}, {"hreflang": list(reversed(a))})[0], [])
        self.assertEqual(pair({"hreflang": a}, {"hreflang": [["EN", "https://EXAMPLE.com/p/"],
                                                             ["de", BASE + "/de/p/"]]})[0], [])
        self.assertEqual(pair({"hreflang": a}, {"hreflang": a[:1]})[0], ["DRIFT012"])

    def test_drift013_directives_other_than_noindex(self):
        self.assertEqual(pair({}, {"robots": ["nosnippet"]})[0], ["DRIFT013"])
        self.assertEqual(pair({}, {"x_robots": {"*": ["noarchive"]}})[0], ["DRIFT013"])
        self.assertEqual(pair({}, {"robots": ["index", "follow"]})[0], [])
        self.assertEqual(pair({}, {"robots": ["noindex"], "noindex": True})[0], ["DRIFT002"])
        self.assertEqual(pair({"robots": ["max-snippet:50"]}, {"robots": ["MAX-SNIPPET:50"]})[0], [])

    def test_drift014_only_when_all_og_tags_removed(self):
        og = {"og:title": "T", "og:image": BASE + "/i.png"}
        self.assertEqual(pair({"og": og}, {"og": {"og:title": "T"}})[0], [])
        self.assertEqual(pair({"og": og}, {"og": {}})[0], ["DRIFT014"])
        self.assertEqual(pair({"og": og}, {"og": None})[0], ["DRIFT014"])

    def test_drift015_word_drop_boundary(self):
        self.assertEqual(pair({"word_count": 800}, {"word_count": 400})[0], [])  # exactly 50%
        self.assertEqual(pair({"word_count": 800}, {"word_count": 399})[0], ["DRIFT015"])
        self.assertEqual(pair({"word_count": 0}, {"word_count": 0})[0], [])
        self.assertEqual(pair({"word_count": 800}, {"word_count": None})[0], [])

    def test_drift016_link_drop_boundary(self):
        self.assertEqual(pair({"internal_links": 10}, {"internal_links": 5})[0], [])
        self.assertEqual(pair({"internal_links": 10}, {"internal_links": 4})[0], ["DRIFT016"])
        self.assertEqual(pair({"internal_links": 10}, {"internal_links": 20})[0], [])

    def test_drift017_needs_both_hashes(self):
        self.assertEqual(pair({}, {"content_hash": "b" * 64})[0], ["DRIFT017"])
        self.assertEqual(pair({}, {"content_hash": None})[0], [])

    def test_h2_change_is_recorded_without_a_rule(self):
        rules, _, data = pair({"h2": ["A", "B"]}, {"h2": ["A"]})
        self.assertEqual(rules, [])
        self.assertIn("h2", data["deltas"]["pages"][0]["changes"])

    def test_drift019_robots_added_and_removed(self):
        _, found = drift.compare(snap([record("/a/")]), snap([record("/a/")], robots="User-agent: *\n"))
        self.assertEqual([(f.rule, f.evidence["state"]) for f in found], [("DRIFT019", "added")])
        _, found = drift.compare(snap([record("/a/")], robots="User-agent: *\n"), snap([record("/a/")]))
        self.assertEqual([(f.rule, f.evidence["state"]) for f in found], [("DRIFT019", "removed")])

    def test_threshold_override_from_thresholds_json(self):
        patched = dict(drift.thresholds())
        patched["drift"] = {"word_drop_pct": 70}
        with mock.patch.object(drift, "thresholds", return_value=patched):
            self.assertEqual(pair({"word_count": 800}, {"word_count": 300})[0], [])
            self.assertEqual(pair({"word_count": 800}, {"word_count": 200})[0], ["DRIFT015"])


def envelope(findings, *, command="audit-build", base_url=BASE, path="dist", rules_version=None, checks=None):
    result = Result(command=command, target={"type": "build-dir", "path": path, "base_url": base_url,
                                             "profile": "default"},
                    findings=list(findings), checks_run=list(checks or ["pages", "jsonld", "robots"]))
    env = result.to_envelope(helpers.catalog(), now=NOW)
    if rules_version:
        env["rules_version"] = rules_version
    return json.loads(json.dumps(env))


class CompareFindingsTests(unittest.TestCase):
    def setUp(self):
        self.a = make("IDX001", "noindex on page", url=BASE + "/a/", key="noindex")
        self.b = make("SD006", "placeholder", url=BASE + "/b/", key="placeholder")
        self.c = make("CANON002", "two canonicals", url=BASE + "/c/", key="count")

    def test_added_no_longer_observed_and_persisting(self):
        diff = drift.compare_findings(envelope([self.a, self.b]), envelope([self.b, self.c]))
        self.assertEqual([x["rule"] for x in diff["added"]], ["CANON002"])
        self.assertEqual([x["rule"] for x in diff["no_longer_observed"]], ["IDX001"])
        self.assertEqual([x["rule"] for x in diff["persisting"]], ["SD006"])
        self.assertEqual(diff["counts"], {"added": 1, "no_longer_observed": 1, "persisting": 1})
        self.assertFalse(diff["no_longer_observed"][0]["check_not_run"])
        self.assertIn("not proof of a fix", diff["note"])

    def test_absent_because_check_did_not_run(self):
        diff = drift.compare_findings(envelope([self.a, self.b]), envelope([], checks=["jsonld"]))
        flags = {x["rule"]: x["check_not_run"] for x in diff["no_longer_observed"]}
        self.assertEqual(flags, {"IDX001": True, "SD006": False})

    def test_severity_change_on_persisting_finding(self):
        hotter = make("IDX001", "noindex on page", url=BASE + "/a/", key="noindex", severity="error")
        diff = drift.compare_findings(envelope([self.a]), envelope([hotter]))
        self.assertEqual(diff["persisting"][0]["severity_before"], "warning")

    def test_checkout_path_ignored_when_base_url_matches(self):
        diff = drift.compare_findings(envelope([self.a]), envelope([self.a], path="./dist"))
        self.assertEqual(diff["counts"]["persisting"], 1)

    def test_refusals(self):
        old = envelope([self.a])
        with self.assertRaisesRegex(ValueError, "command differs"):
            drift.compare_findings(old, envelope([self.a], command="audit-url"))
        with self.assertRaisesRegex(ValueError, "target differs"):
            drift.compare_findings(old, envelope([self.a], base_url="https://example.org"))
        with self.assertRaisesRegex(ValueError, "rules major version"):
            drift.compare_findings(old, envelope([self.a], rules_version="2027.1.0"))
        broken = envelope([self.a])
        broken["error"] = "boom"
        with self.assertRaisesRegex(ValueError, "recorded an error"):
            drift.compare_findings(old, broken)
        with self.assertRaisesRegex(ValueError, "not a seo-geo-god result envelope"):
            drift.compare_findings(old, {"findings": []})

    def test_minor_rules_version_change_is_allowed(self):
        diff = drift.compare_findings(envelope([self.a]), envelope([self.a], rules_version="2026.12.1"))
        self.assertEqual(diff["counts"]["persisting"], 1)


PANEL = {"kind": "panel", "surface": "perplexity", "query": "how to send a recurring invoice",
         "query_class": "informational", "holdout": False, "status": "valid_present",
         "cited_urls": ["https://example.com/guides/recurring-invoices/"],
         "cited_statement": "Recurring invoices repeat on a schedule you set.", "locale": "en-US", "device": "mobile",
         "logged_in": False, "model_label": None}
METRIC = {"kind": "metric", "source": "gsc", "metric": "clicks", "value": 120, "window": "2026-10-01:2026-10-28",
          "segment": "page=/guides/"}
EXPERIMENT = {"kind": "experiment", "hypothesis": "Answer-first rewrite raises the citation rate",
              "change": "content/guides/recurring-invoices.md section s03",
              "target_urls": ["https://example.com/guides/recurring-invoices/"],
              "control_urls": ["https://example.com/guides/payment-reminders/"], "deployed_at": "2026-10-04",
              "metric": "citation_rate", "baseline_ref": "panel reads 2026-09-20 and 2026-09-27",
              "readback_days": [7, 14, 28, 56], "decision": None, "note": None}


class LedgerFileTests(unittest.TestCase):
    def test_init_creates_meta_and_observations_exclusively(self):
        with helpers.temp_dir() as tmp:
            target = str(tmp / "ledger")
            meta = ledger.init(target, now=NOW)
            self.assertEqual(meta["schema"], ledger.LEDGER_SCHEMA)
            self.assertEqual(json.loads((tmp / "ledger" / "ledger.json").read_text())["created"], NOW)
            self.assertEqual((tmp / "ledger" / "observations.jsonl").read_text(), "")
            with self.assertRaises(FileExistsError):
                ledger.init(target, now=NOW)
            self.assertEqual(ledger.load(target), [])

    def test_init_refuses_symlinked_directory_and_bad_timestamp(self):
        with helpers.temp_dir() as tmp:
            (tmp / "real").mkdir()
            os.symlink(str(tmp / "real"), str(tmp / "link"))
            with self.assertRaises(ValueError):
                ledger.init(str(tmp / "link"), now=NOW)
            with self.assertRaises(ValueError):
                ledger.init(str(tmp / "new"), now="yesterday")

    def test_record_load_and_stored_fields(self):
        with helpers.temp_dir() as tmp:
            ledger.init(str(tmp), now=NOW)
            stored = ledger.record(str(tmp), PANEL, now=NOW)
            self.assertRegex(stored["id"], r"^[0-9a-f]{16}$")
            self.assertEqual(stored["id"], ledger.identity(PANEL))
            self.assertEqual((stored["recorded_at"], stored["v"]), (NOW, 1))
            self.assertEqual(ledger.load(str(tmp)), [stored])
            self.assertEqual(helpers.validate_schema(stored, "ledger.schema.json"), [])

    def test_duplicate_observation_refused_but_repeated_sample_accepted(self):
        with helpers.temp_dir() as tmp:
            ledger.init(str(tmp), now=NOW)
            ledger.record(str(tmp), PANEL, now=NOW)
            with self.assertRaisesRegex(ValueError, "duplicates"):
                ledger.record(str(tmp), dict(PANEL), now="2026-11-02T00:00:00Z")
            ledger.record(str(tmp), dict(PANEL, sample=2), now=NOW)
            ledger.record(str(tmp), dict(PANEL, observed_at="2026-11-01T10:00:00Z"), now=NOW)
            self.assertEqual(len(ledger.load(str(tmp))), 3)

    def test_record_many_is_all_or_nothing(self):
        with helpers.temp_dir() as tmp:
            ledger.init(str(tmp), now=NOW)
            with self.assertRaisesRegex(ValueError, "observation 2 is invalid"):
                ledger.record_many(str(tmp), [PANEL, dict(PANEL, status="maybe")], now=NOW)
            with self.assertRaisesRegex(ValueError, "observation 2 duplicates"):
                ledger.record_many(str(tmp), [PANEL, dict(PANEL)], now=NOW)
            self.assertEqual(ledger.load(str(tmp)), [])
            self.assertEqual(len(ledger.record_many(str(tmp), [PANEL, METRIC, EXPERIMENT], now=NOW)), 3)

    def test_uninitialized_or_corrupt_ledger_refused(self):
        with helpers.temp_dir() as tmp:
            with self.assertRaises(ValueError):
                ledger.record(str(tmp), PANEL, now=NOW)
            ledger.init(str(tmp / "l"), now=NOW)
            with open(str(tmp / "l" / "observations.jsonl"), "a", encoding="utf-8") as fh:
                fh.write("{not json\n")
            with self.assertRaisesRegex(ValueError, "line 1"):
                ledger.load(str(tmp / "l"))

    def test_record_needs_iso_timestamp(self):
        with helpers.temp_dir() as tmp:
            ledger.init(str(tmp), now=NOW)
            with self.assertRaises(ValueError):
                ledger.record(str(tmp), PANEL, now="today")


class ObservationValidationTests(unittest.TestCase):
    def problems(self, base, **changes):
        obs = dict(base)
        for key, value in changes.items():
            if value is KeyError:
                obs.pop(key, None)
            else:
                obs[key] = value
        return ledger.validate_observation(obs)

    def test_valid_examples_pass_both_validators(self):
        for obs in (PANEL, METRIC, EXPERIMENT, {"kind": "panel", "surface": "claude", "query": "q",
                                                 "query_class": "other", "status": "empty"}):
            with self.subTest(kind=obs["kind"]):
                self.assertEqual(ledger.validate_observation(obs), [])
                self.assertEqual(helpers.validate_schema(obs, "ledger.schema.json"), [])

    def test_invalid_examples_fail_both_validators(self):
        cases = {
            "unknown field": dict(PANEL, mood="happy"),
            "personal data": dict(PANEL, email="someone@example.com"),
            "missing required": {k: v for k, v in PANEL.items() if k != "surface"},
            "bad status": dict(PANEL, status="cited"),
            "userinfo url": dict(PANEL, cited_urls=["https://user@example.com/"]),
            "long statement": dict(PANEL, cited_statement="x" * 301),
            "bad window": dict(METRIC, window="2026-10-28"),
            "bad metric source": dict(METRIC, source="semrush"),
            "non-finite value": dict(METRIC, value="12"),
            "bad readback days": dict(EXPERIMENT, readback_days=[0, 7]),
            "bad decision": dict(EXPERIMENT, decision="ship"),
            "bad deployed_at": dict(EXPERIMENT, deployed_at="2026/10/04"),
            "empty target urls are fine but not a string": dict(EXPERIMENT, target_urls="https://example.com/"),
        }
        for label, obs in cases.items():
            with self.subTest(case=label):
                self.assertNotEqual(ledger.validate_observation(obs), [])
                self.assertNotEqual(helpers.validate_schema(obs, "ledger.schema.json"), [])

    def test_python_only_semantic_checks(self):
        self.assertIn("personal data", self.problems(PANEL, user_agent="x")[0])
        self.assertTrue(self.problems(PANEL, status="error"))  # error sample with cited_urls
        self.assertEqual(self.problems(PANEL, status="error", cited_urls=[]), [])
        self.assertTrue(self.problems(METRIC, window="2026-10-28:2026-10-01"))
        self.assertTrue(self.problems(METRIC, window="2026-02-30:2026-03-01"))
        self.assertTrue(self.problems(PANEL, id="abc"))
        self.assertTrue(self.problems(PANEL, surface="   "))
        self.assertTrue(self.problems(EXPERIMENT, readback_days=[7, 7]))
        self.assertTrue(self.problems(PANEL, sample=0))
        self.assertTrue(self.problems(PANEL, holdout="no"))
        self.assertEqual(ledger.validate_observation([PANEL]), ["observation must be a JSON object"])
        self.assertIn("kind must be", ledger.validate_observation({"kind": "note"})[0])

    def test_identity_ignores_stored_fields(self):
        stored = dict(PANEL, id="0" * 16, recorded_at=NOW, v=1)
        self.assertEqual(ledger.identity(stored), ledger.identity(PANEL))
        self.assertNotEqual(ledger.identity(dict(PANEL, sample=2)), ledger.identity(PANEL))


def panel(status, **kw):
    obs = dict(PANEL, status=status, cited_urls=[] if status != "valid_present" else PANEL["cited_urls"])
    obs.update(kw)
    obs.setdefault("recorded_at", NOW)
    obs.setdefault("id", ledger.identity(obs))
    return obs


class SummaryAndStatsTests(unittest.TestCase):
    def test_wilson_reference_values(self):
        lo, hi = ledger.wilson(3, 10)
        self.assertEqual((round(lo, 4), round(hi, 4)), (0.1078, 0.6032))
        self.assertEqual(ledger.wilson(0, 10)[0], 0.0)
        self.assertEqual(ledger.wilson(10, 10)[1], 1.0)
        lo, hi = ledger.wilson(1, 1)
        self.assertTrue(0 < lo < 1 and hi == 1.0)
        for k, n in ((0, 0), (4, 3), (-1, 3)):
            with self.assertRaises(ValueError):
                ledger.wilson(k, n)

    def test_two_proportion_z(self):
        out = ledger.two_proportion_z(30, 100, 10, 100)
        self.assertAlmostEqual(out["z"], 3.5355, places=3)
        self.assertAlmostEqual(out["p_value"], 0.000407, places=5)
        self.assertAlmostEqual(out["diff"], 0.2)
        same = ledger.two_proportion_z(5, 10, 5, 10)
        self.assertEqual((same["z"], same["p_value"]), (0.0, 1.0))
        self.assertEqual(ledger.two_proportion_z(0, 10, 0, 20)["z"], 0.0)
        with self.assertRaises(ValueError):
            ledger.two_proportion_z(1, 0, 1, 1)

    def test_denominators_exclude_empty_and_error(self):
        obs = ([panel("valid_present", sample=i) for i in range(1, 4)] +
               [panel("valid_absent", sample=i) for i in range(1, 8)] +
               [panel("empty", sample=1), panel("empty", sample=2), panel("error", sample=1)])
        out = ledger.summary(obs, by=("surface",))
        group = out["groups"][0]
        self.assertEqual(group["group"], {"surface": "perplexity"})
        self.assertEqual((group["samples"], group["n"], group["empty"], group["error"]), (13, 10, 2, 1))
        self.assertEqual((group["rate"], group["ci95"]), (0.3, [0.1078, 0.6032]))
        self.assertEqual(group["result"], "computed")
        self.assertNotIn("warning", group)
        self.assertEqual(out["totals"]["n"], 10)
        self.assertIn("excluded", out["note"])

    def test_no_computable_result_and_failed_read_warning(self):
        obs = [panel("empty", sample=1), panel("error", sample=2), panel("valid_absent", surface="claude")]
        out = ledger.summary(obs, by=("surface",))
        groups = {g["group"]["surface"]: g for g in out["groups"]}
        self.assertEqual(groups["perplexity"]["result"], "no computable result")
        self.assertIsNone(groups["perplexity"]["rate"])
        self.assertIsNone(groups["perplexity"]["ci95"])
        self.assertIn("failed measurement", groups["perplexity"]["warning"])
        self.assertEqual(groups["claude"]["rate"], 0.0)
        half = ledger.summary([panel("empty", sample=1), panel("valid_absent", sample=2)], by=("surface",))
        self.assertNotIn("warning", half["groups"][0])  # exactly half is not "more than half"

    def test_grouping_window_and_metrics(self):
        obs = [panel("valid_present", query_class="branded", observed_at="2026-10-05"),
               panel("valid_absent", query_class="generic", observed_at="2026-10-20"),
               panel("valid_present", query_class="generic", recorded_at="2026-11-01T00:00:00Z"),
               dict(METRIC, id="m1", recorded_at=NOW), dict(METRIC, id="m2", recorded_at=NOW, value=90,
                                                             window="2026-09-01:2026-09-28")]
        out = ledger.summary(obs)
        self.assertEqual([g["group"] for g in out["groups"]],
                         [{"surface": "perplexity", "query_class": "branded"},
                          {"surface": "perplexity", "query_class": "generic"}])
        windowed = ledger.summary(obs, by=("query_class",), window=("2026-10-01", "2026-10-31"))
        self.assertEqual(windowed["totals"]["samples"], 2)
        self.assertEqual(windowed["metrics"], [])
        self.assertEqual([s["value"] for s in out["metrics"][0]["series"]], [90, 120])
        with self.assertRaises(ValueError):
            ledger.summary(obs, by=("email",))
        with self.assertRaises(ValueError):
            ledger.summary(obs, window=("2026-10-31", "2026-10-01"))

    def test_holdout_grouping(self):
        obs = [panel("valid_present"), panel("valid_absent", holdout=True)]
        groups = ledger.summary(obs, by=("holdout",))["groups"]
        self.assertEqual([(g["group"]["holdout"], g["rate"]) for g in groups], [(False, 1.0), (True, 0.0)])


class ExperimentStatusTests(unittest.TestCase):
    def status(self, today, *items):
        stored = [dict(o, id="e%d" % i, recorded_at="2026-10-0%dT00:00:00Z" % (i + 1)) for i, o in enumerate(items)]
        return ledger.experiments_status(stored, today=today)

    def test_due_dates_and_states_while_reading(self):
        (exp,) = self.status(date(2026, 11, 1), EXPERIMENT)
        self.assertEqual([(r["days"], r["date"], r["status"]) for r in exp["readbacks"]],
                         [(7, "2026-10-11", "passed"), (14, "2026-10-18", "passed"), (28, "2026-11-01", "due"),
                          (56, "2026-11-29", "upcoming")])
        self.assertEqual((exp["state"], exp["next_readback"], exp["decision"]), ("reading", "2026-11-01", None))

    def test_not_deployed_yet_and_default_readbacks(self):
        future = {k: v for k, v in EXPERIMENT.items() if k != "readback_days"}
        future["deployed_at"] = "2026-11-05"
        (exp,) = self.status(date(2026, 11, 1), future)
        self.assertEqual(exp["state"], "not_deployed_yet")
        self.assertEqual([r["date"] for r in exp["readbacks"]], ["2026-11-12", "2026-11-19", "2026-12-03",
                                                                  "2026-12-31"])

    def test_decision_due_then_decided_by_a_later_record(self):
        keyed = dict(EXPERIMENT, experiment_id="exp-1")
        (exp,) = self.status(date(2027, 1, 1), keyed)
        self.assertEqual((exp["state"], exp["next_readback"]), ("decision_due", None))
        (exp,) = self.status(date(2027, 1, 1), keyed, dict(keyed, decision="keep_testing", note="mixed reads"))
        self.assertEqual((exp["state"], exp["decision"], exp["records"], exp["key"]),
                         ("decided", "keep_testing", 2, "exp-1"))

    def test_custom_readbacks_and_ordering(self):
        early = dict(EXPERIMENT, deployed_at="2026-09-01", hypothesis="Earlier", readback_days=[30])
        out = self.status(date(2026, 11, 1), EXPERIMENT, early)
        self.assertEqual([e["hypothesis"] for e in out], ["Earlier", EXPERIMENT["hypothesis"]])
        self.assertEqual(out[0]["readbacks"], [{"days": 30, "date": "2026-10-01", "status": "passed"}])

    def test_end_to_end_through_the_ledger(self):
        with helpers.temp_dir() as tmp:
            ledger.init(str(tmp), now=NOW)
            ledger.record_many(str(tmp), [EXPERIMENT, PANEL], now=NOW)
            out = ledger.experiments_status(ledger.load(str(tmp)), today=helpers.TODAY)
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0]["readbacks"][2]["status"], "due")


if __name__ == "__main__":
    unittest.main()
