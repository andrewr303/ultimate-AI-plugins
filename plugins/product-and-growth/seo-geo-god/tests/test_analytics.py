"""WP06: export loaders, Search Console analyses, referrer and bot classification, gaps planner,
project validation, the search-updates ledger and the AI referrer registry."""
from __future__ import annotations

import copy
import json
import os
import re
import sys
import unittest
from datetime import date
from unittest import mock
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_analytics
import helpers  # noqa: E402
from seo_geo_lib import analytics as an  # noqa: E402
from seo_geo_lib import rulesdb  # noqa: E402

FIX = helpers.fixture("analytics")


def setUpModule() -> None:
    helpers.block_network()


def path(*parts):
    return str(FIX.joinpath(*parts))


def rows(name, dims=None):
    return an.load_rows(path("gsc", name), dimensions=dims)


def row(query=None, page=None, clicks=0, impressions=100, position=5.0):
    out = {"clicks": clicks, "impressions": impressions, "position": position,
           "ctr": clicks / impressions if impressions else 0.0}
    if query is not None:
        out["query"] = query
    if page is not None:
        out["page"] = page
    return out


def write(tmp, name, content):
    target = tmp / name
    if isinstance(content, bytes):
        target.write_bytes(content)
    else:
        target.write_text(content, encoding="utf-8")
    return str(target)


class LoadRowsTests(unittest.TestCase):
    def test_search_console_ui_csv(self):
        cur = rows("queries-cur.csv")
        first = cur[0]
        self.assertEqual(first, {"query": "invoice template", "clicks": 120, "impressions": 1234, "ctr": 0.0972,
                                 "position": 4.0})
        self.assertEqual(len(cur), 6)

    def test_localized_semicolon_csv_with_decimal_commas(self):
        de = rows("queries-de.csv")
        self.assertEqual(de[0], {"query": "invoice template", "clicks": 1234, "impressions": 45678, "ctr": 0.027,
                                 "position": 3.4})
        self.assertEqual(de[1]["position"], 12.25)

    def test_search_analytics_api_json_with_dimensions(self):
        qp = rows("query-page.json", ["query", "page"])
        self.assertEqual(qp[0]["query"], "invoice template")
        self.assertEqual(qp[0]["page"], "https://example.com/templates/")
        self.assertEqual((qp[0]["clicks"], qp[0]["impressions"], qp[0]["position"]), (100, 3000, 4.0))
        with self.assertRaisesRegex(ValueError, "--dimensions"):
            rows("query-page.json")
        with self.assertRaisesRegex(ValueError, "--dimensions"):
            rows("query-page.json", ["query"])
        with self.assertRaisesRegex(ValueError, "unknown dimension"):
            rows("query-page.json", ["query", "url"])

    def test_api_json_variants(self):
        with helpers.temp_dir() as tmp:
            empty = write(tmp, "empty.json", '{"responseAggregationType": "auto"}')
            self.assertEqual(an.load_rows(empty), [])
            sa = write(tmp, "sa.json", json.dumps({"rows": [{"keys": ["IMAGE_RESULT"], "clicks": 1,
                                                              "impressions": 2, "ctr": 0.5, "position": 1.5}]}))
            self.assertEqual(an.load_rows(sa, dimensions=["searchAppearance"])[0]["search_appearance"],
                             "IMAGE_RESULT")
            generic = write(tmp, "list.json", json.dumps([{"Query": "a", "Clicks": "3", "Impressions": "30"}]))
            self.assertEqual(an.load_rows(generic)[0], {"query": "a", "clicks": 3, "impressions": 30, "ctr": 0.1})
            bad = write(tmp, "bad.json", '{"rows": "nope"}')
            with self.assertRaises(ValueError):
                an.load_rows(bad)

    def test_ga4_export_with_comment_preamble(self):
        ga4 = an.load_rows(path("ga4", "sessions.csv"))
        self.assertEqual(ga4[0], {"source_medium": "chatgpt.com / referral", "landing_page": "/guides/send-invoice/",
                                  "sessions": 40, "source": "chatgpt.com", "medium": "referral"})
        self.assertEqual(len(ga4), 10)

    def test_ctr_forms_and_derived_ctr(self):
        with helpers.temp_dir() as tmp:
            csv_path = write(tmp, "q.csv", "Query,Clicks,Impressions,CTR,Position\na,5,100,0.05,3\nb,5,100,5,3\n"
                                           "c,5,100,,3\nd,0,0,,9\nGrand total,10,300,,\n")
            got = {r["query"]: r["ctr"] for r in an.load_rows(csv_path)}
            self.assertEqual(got, {"a": 0.05, "b": 0.05, "c": 0.05, "d": 0.0})

    def test_utf16_export_is_decoded(self):
        with helpers.temp_dir() as tmp:
            target = write(tmp, "u16.csv", "Query,Clicks,Impressions\nä,1,2\n".encode("utf-16"))
            self.assertEqual(an.load_rows(target)[0]["query"], "ä")

    def test_refusals(self):
        with helpers.temp_dir() as tmp:
            env = write(tmp, ".env", "Query,Clicks\na,1\n")
            with self.assertRaisesRegex(ValueError, "environment"):
                an.load_rows(env)
            with self.assertRaisesRegex(ValueError, "regular file"):
                an.load_rows(str(tmp))
            big = write(tmp, "big.csv", "Query,Clicks\n" + "a,1\n" * 100)
            with self.assertRaisesRegex(ValueError, "limit"):
                an.load_rows(big, max_bytes=50)
            unknown = write(tmp, "unknown.csv", "foo,bar\n1,2\n")
            with self.assertRaisesRegex(ValueError, "no recognised columns"):
                an.load_rows(unknown)
            garbage = write(tmp, "garbage.csv", "Query,Clicks\na,many\n")
            with self.assertRaisesRegex(ValueError, "line 2 clicks"):
                an.load_rows(garbage)
            with self.assertRaisesRegex(ValueError, "no page column"):
                an.load_rows(path("gsc", "queries-cur.csv"), dimensions=["page"])
            with self.assertRaises(ValueError):
                an.load_rows(write(tmp, "blank.csv", "\n# only a comment\n"))


class MoversDecayTests(unittest.TestCase):
    def test_movers_from_fixtures(self):
        out = an.movers(rows("queries-cur.csv"), rows("queries-prev.csv"))
        self.assertEqual(out["min_delta"], 2.0)  # from data/thresholds.json
        self.assertEqual([r["query"] for r in out["winners"]], ["invoice template"])  # exactly 2 positions
        self.assertEqual(out["winners"][0]["position_change"], 2.0)
        self.assertEqual([r["query"] for r in out["losers"]], ["free invoice generator", "recurring invoices"])
        self.assertEqual([r["clicks_change"] for r in out["losers"]], [-110, -20])  # most clicks lost first
        self.assertEqual([r["query"] for r in out["new"]], ["late payment reminder"])
        self.assertEqual([r["query"] for r in out["lost"]], ["invoice number format"])
        listed = {r["query"] for k in ("winners", "losers", "new", "lost") for r in out[k]}
        self.assertNotIn("tiny query", listed)  # below min_impressions in both periods
        self.assertNotIn("invoice software", listed)  # moved 1.5 positions

    def test_movers_thresholds_and_aggregation(self):
        out = an.movers(rows("queries-cur.csv"), rows("queries-prev.csv"), min_delta=1.5)
        self.assertIn("invoice software", [r["query"] for r in out["winners"]])
        cur = [row("a", clicks=10, impressions=100, position=2.0), row("a", clicks=0, impressions=300, position=6.0)]
        prev = [row("a", clicks=10, impressions=400, position=8.0)]
        (win,) = an.movers(cur, prev)["winners"]
        self.assertEqual((win["position_cur"], win["clicks_cur"], win["impressions_cur"]), (5.0, 10, 400))
        with self.assertRaisesRegex(ValueError, "needs a page column"):
            an.movers(rows("queries-cur.csv"), rows("queries-prev.csv"), key="page")

    def test_decay_from_fixtures_and_boundaries(self):
        out = an.decay(rows("pages-cur.csv"), rows("pages-prev.csv"))
        self.assertEqual([(urlsplit(r["page"]).path, r["drop_pct"]) for r in out],
                         [("/guides/invoices/", 40.0), ("/features/", 100.0), ("/blog/old/", 40.0)])
        features = out[1]
        self.assertTrue(features["missing_in_current"])
        pages = {urlsplit(r["page"]).path for r in out}
        self.assertNotIn("/exact/", pages)  # exactly 30% is not "more than 30%"
        self.assertNotIn("/blog/tiny/", pages)  # 9 previous clicks < 10
        self.assertNotIn("/pricing/", pages)  # 28%
        looser = an.decay(rows("pages-cur.csv"), rows("pages-prev.csv"), drop_pct=25.0, min_prev_clicks=5)
        self.assertEqual(len(looser), 6)


class CtrStrikingTests(unittest.TestCase):
    def test_fixed_threshold_positive_negative_boundary(self):
        data = [row("flag", clicks=19, impressions=1000, position=3.0),
                row("at-ctr", clicks=20, impressions=1000, position=3.0),
                row("few", clicks=1, impressions=199, position=3.0),
                row("edge-pos", clicks=3, impressions=200, position=5.0),
                row("deep", clicks=1, impressions=1000, position=5.1)]
        out = an.ctr_anomalies(data)
        self.assertEqual([r["query"] for r in out], ["flag", "edge-pos"])
        self.assertEqual(out[0]["basis"], "fixed threshold")

    def test_curve_based_anomalies(self):
        curve = {3: 0.10}
        data = [row("low", clicks=40, impressions=1000, position=3.0),
                row("half", clicks=50, impressions=1000, position=3.0),
                row("nocurve", clicks=0, impressions=1000, position=4.0)]
        out = an.ctr_anomalies(data, curve=curve)
        self.assertEqual([r["query"] for r in out], ["low"])
        self.assertEqual((out[0]["expected_ctr"], out[0]["ratio"], out[0]["clicks_below_curve_estimate"]),
                         (0.1, 0.4, 60.0))

    def test_site_and_default_ctr_curves(self):
        data = [row(clicks=10, impressions=100, position=2.5), row(clicks=30, impressions=100, position=1.4),
                row(clicks=1, impressions=99, position=4.0), row(clicks=2, impressions=200, position=14.0),
                row(clicks=0, impressions=500, position=25.0), row(clicks=5, impressions=0, position=1.0)]
        self.assertEqual(an.site_ctr_curve(data), {1: 0.3, 3: 0.1, "11-20": 0.01})
        self.assertEqual(an.site_ctr_curve(data, min_impressions=50), {1: 0.3, 3: 0.1, 4: 0.0101, "11-20": 0.01})
        default = an.default_ctr_curve()
        self.assertEqual(default[3], 0.11)
        self.assertEqual(default["11-20"], 0.01)
        self.assertNotIn("source", default)

    def test_striking_distance_boundaries(self):
        data = [row("lo", impressions=100, position=5.0), row("hi", impressions=150, position=20.0),
                row("above", impressions=500, position=4.9), row("below", impressions=500, position=20.1),
                row("few", impressions=99, position=10.0)]
        self.assertEqual([r["query"] for r in an.striking_distance(data)], ["hi", "lo"])
        self.assertEqual([r["query"] for r in an.striking_distance(data, low=4.0, min_impressions=50)],
                         ["above", "hi", "lo", "few"])


class QueryPageTests(unittest.TestCase):
    def test_cannibalization_winner_and_serp_domination(self):
        out = an.cannibalization(rows("query-page.json", ["query", "page"]))
        self.assertEqual([r["query"] for r in out], ["invoice template", "invoice app", "billing tool"])
        template, app, billing = out
        self.assertEqual((template["winner"], template["serp_domination"]), ("https://example.com/templates/", False))
        self.assertEqual(template["losers"], ["https://example.com/blog/invoice-template/"])
        self.assertTrue(app["serp_domination"])
        self.assertTrue(app["action"].startswith("monitor"))
        self.assertEqual(billing["winner"], "https://example.com/b/")  # same position, more clicks

    def test_serp_domination_boundaries(self):
        def dominated(p1, p2):
            data = [row("q", "https://example.com/1", clicks=5, impressions=100, position=p1),
                    row("q", "https://example.com/2", clicks=5, impressions=100, position=p2)]
            return an.cannibalization(data)[0]["serp_domination"]
        self.assertTrue(dominated(3.0, 5.0))  # spread exactly 2, max exactly 5
        self.assertFalse(dominated(3.0, 5.1))
        self.assertFalse(dominated(1.0, 3.5))
        self.assertEqual(an.cannibalization([row("q", "https://example.com/1", impressions=60),
                                             row("q", "https://example.com/2", impressions=39)]), [])

    def test_optional_threshold_keys_are_read_when_present(self):
        patched = an.thresholds()
        patched["gsc"].update(serp_domination={"max_spread": 1.0}, movers_min_impressions=2000)
        data = [row("q", "https://example.com/1", clicks=5, impressions=100, position=2.0),
                row("q", "https://example.com/2", clicks=5, impressions=100, position=3.5)]
        with mock.patch.object(an, "thresholds", return_value=patched):
            self.assertFalse(an.cannibalization(data)[0]["serp_domination"])
            out = an.movers(rows("queries-cur.csv"), rows("queries-prev.csv"))
            self.assertEqual((out["winners"], [r["query"] for r in out["losers"]]), ([], ["free invoice generator"]))
        self.assertTrue(an.cannibalization(data)[0]["serp_domination"])

    def test_branded_split_is_impression_weighted(self):
        data = [row("Example Co login", clicks=50, impressions=100, position=1.0),
                row("example co pricing", clicks=10, impressions=300, position=3.0),
                row("invoice template", clicks=5, impressions=500, position=8.0)]
        out = an.branded_split(data, ["Example Co", " "])
        self.assertEqual(out["brand_terms"], ["example co"])
        self.assertEqual(out["branded"], {"queries": 2, "clicks": 60, "impressions": 400, "ctr": 0.15,
                                          "position": 2.5})
        self.assertEqual(out["non_branded"]["position"], 8.0)
        with self.assertRaises(ValueError):
            an.branded_split(data, ["  "])

    def test_planner_buckets_from_fixture(self):
        out = an.planner_buckets(rows("planner.json", ["query", "page"]))
        b = out["buckets"]
        self.assertEqual(out["counts"], {"A": 1, "B": 1, "C": 1, "D": 1, "E": 1})
        self.assertEqual(b["A"][0]["query"], "how to send an invoice")
        self.assertEqual((b["A"][0]["click_potential_90d"], b["A"][0]["click_potential_monthly"]), (90.0, 30.0))
        self.assertEqual(b["B"][0]["query"], "invoice for photographers")
        self.assertEqual((b["C"][0]["query"], b["C"][0]["refresh_target"]),
                         ("invoice template", "https://example.com/templates/"))
        self.assertEqual(b["C"][0]["click_potential_90d"], 450.0)
        self.assertEqual(b["D"], [{"parent": "how to send an invoice", "page": "https://example.com/guides/send-invoice/",
                                   "related": ["send invoice email"]}])
        self.assertEqual(b["E"][0]["query"], "invoice generator")
        self.assertEqual((out["target_ctr"], out["target_position"]), (0.11, 3))
        self.assertIn("heuristic default", out["curve_source"])
        self.assertTrue(any("not a forecast" in n for n in out["notes"]))

    def test_planner_units_for_a_28_day_export(self):
        data = [row("send invoice", "https://example.com/s/", clicks=10, impressions=500, position=9.0)]
        out = an.planner_buckets(data, days=28)
        (a,) = out["buckets"]["A"]
        self.assertEqual(a["click_potential_window"], 45.0)  # 500 x 0.11 - 10
        self.assertEqual(a["click_potential_90d"], round(45.0 * 90 / 28, 1))
        self.assertEqual(a["click_potential_monthly"], round(45.0 * 30 / 28, 1))
        self.assertAlmostEqual(out["thresholds"]["a_min_impressions"], 100 * 28 / 90)
        ninety = an.planner_buckets(data, days=90)["buckets"]["A"][0]
        self.assertEqual(ninety["click_potential_monthly"], round(ninety["click_potential_90d"] / 3, 1))
        with self.assertRaises(ValueError):
            an.planner_buckets(data, days=0)

    def test_planner_boundaries_and_precedence(self):
        def bucket_of(data, **kw):
            out = an.planner_buckets(data, **kw)["buckets"]
            return sorted(k for k, v in out.items() if v)
        self.assertEqual(bucket_of([row("q", "https://example.com/p", impressions=50, position=20.1)]), ["B"])
        self.assertEqual(bucket_of([row("q", "https://example.com/p", impressions=50, position=20.0)]), [])
        self.assertEqual(bucket_of([row("q", "https://example.com/p", impressions=49, position=30.0)]), [])
        self.assertEqual(bucket_of([row("q", "https://example.com/p", impressions=100, position=5.0)]), ["A"])
        self.assertEqual(bucket_of([row("q", "https://example.com/p", impressions=99, position=5.0)]), [])
        # position 6 qualifies for A and C; C (CTR underperformer) wins
        self.assertEqual(bucket_of([row("q", "https://example.com/p", clicks=1, impressions=600, position=6.0)]),
                         ["C"])
        # two pages under position 20 with >= 20 impressions each: E only, never A
        split = [row("q", "https://example.com/1", impressions=20, position=8.0),
                 row("q", "https://example.com/2", impressions=200, position=9.0)]
        self.assertEqual(bucket_of(split), ["E"])
        split[0]["impressions"] = 19
        self.assertEqual(bucket_of(split), ["A"])

    def test_planner_with_site_curve(self):
        data = [row("q", "https://example.com/p", clicks=10, impressions=500, position=9.0)]
        out = an.planner_buckets(data, curve={3: 0.2, 9: 0.03})
        self.assertEqual((out["target_ctr"], out["curve_source"]), (0.2, "site-calibrated"))
        self.assertEqual(out["buckets"]["A"][0]["click_potential_window"], 90.0)

    def test_aio_recovery_filter_and_boundaries(self):
        out = an.aio_recovery(rows("queries-cur.csv"), rows("queries-prev.csv"))
        self.assertEqual([r["query"] for r in out], ["free invoice generator", "recurring invoices"])
        self.assertTrue(all(r["ai_overview_observed"] == "unknown" for r in out))
        prev = [row("q", clicks=100, impressions=1000)]
        self.assertEqual(an.aio_recovery([row("q", clicks=80, impressions=1000)], prev), [])  # exactly -20%
        self.assertEqual(len(an.aio_recovery([row("q", clicks=79, impressions=1000)], prev)), 1)
        self.assertEqual(an.aio_recovery([row("q", clicks=50, impressions=900)], prev), [])  # impressions -10%
        self.assertEqual(len(an.aio_recovery([row("q", clicks=50, impressions=901)], prev)), 1)
        self.assertEqual(an.aio_recovery([row("q", clicks=1, impressions=99)], [row("q", clicks=50, impressions=99)]),
                         [])


class ReferrerBotTests(unittest.TestCase):
    def test_ga4_referrals(self):
        out = an.classify_referrers(path("ga4", "sessions.csv"))
        self.assertEqual((out["input"], out["unit"], out["total"], out["ai"]), ("ga4", "sessions", 896, 76))
        self.assertEqual(out["matched_by"], {"referrer_or_source": 72, "utm_source": 0, "ai_assistant_channel": 4})
        self.assertEqual([(p["product"], p["sessions"]) for p in out["by_product"]][:2],
                         [("ChatGPT", 50), ("Perplexity", 15)])
        self.assertEqual(out["by_landing_page"][0], {"landing_page": "/guides/send-invoice/", "sessions": 52})
        self.assertIn("floor", " ".join(out["notes"]))
        self.assertEqual(out["ga4_channel"]["medium"], "ai-assistant")

    def test_ga4_channel_group_column_and_missing_columns(self):
        with helpers.temp_dir() as tmp:
            target = write(tmp, "ch.csv", "Session source,Session medium,Session default channel group,Sessions\n"
                                          "app.example.net,referral,AI Assistant,7\ngoogle,organic,Organic Search,9\n")
            out = an.classify_referrers(target)
            self.assertEqual((out["ai"], out["matched_by"]["ai_assistant_channel"]), (7, 7))
            no_source = write(tmp, "pages.csv", "Page,Clicks\n/a,1\n")
            with self.assertRaises(ValueError):
                an.classify_referrers(no_source)

    def test_access_log_referrals(self):
        out = an.classify_referrers(path("logs", "access.log"), log=True)
        self.assertEqual((out["unit"], out["total"], out["ai"], out["unparsed_lines"]), ("hits", 15, 3, 1))
        self.assertEqual(out["matched_by"]["utm_source"], 1)
        self.assertEqual(out["by_landing_page"], [{"landing_page": "/guides/send-invoice/", "hits": 2},
                                                  {"landing_page": "/pricing/", "hits": 1}])
        dumped = json.dumps(out)
        self.assertNotIn("203.0.113", dumped)  # no IP addresses in the output
        self.assertNotIn("id=42", dumped)  # query strings stripped from landing paths

    def test_registry_regex_matches_every_host_and_nothing_else(self):
        reg = rulesdb.load_data("ai-referrers")
        pattern = re.compile(reg["ga4_regex"])
        for host in [h["host"] for h in reg["hosts"]] + ["www.perplexity.ai", "labs.chatgpt.com"]:
            with self.subTest(host=host):
                self.assertTrue(pattern.match(host))
        for host in ("google.com", "www.google.com", "bing.com", "example.com", "notchatgpt.com",
                     "chatgpt.com.example.net", "google"):
            with self.subTest(host=host):
                self.assertIsNone(pattern.match(host))

    def test_bot_hits_are_labelled_claimed(self):
        out = an.classify_bots(path("logs", "access.log"))
        self.assertEqual(out["label"], an.CLAIMED)
        self.assertEqual((out["lines"], out["parsed"], out["unparsed"], out["matched_hits"], out["unmatched_hits"]),
                         (16, 14, 2, 9, 5))
        tokens = {r["token"]: r for r in out["by_token"]}
        self.assertEqual(tokens["Googlebot"]["statuses"], {"2xx": 1, "4xx": 1})
        self.assertEqual(tokens["PerplexityBot"]["statuses"], {"5xx": 1})
        self.assertIn("GoogleOther-Image", tokens)  # longest token wins over GoogleOther
        self.assertNotIn("GoogleOther", tokens)
        self.assertEqual(tokens["GPTBot"]["ip_list_url"], "https://openai.com/gptbot.json")
        for r in out["by_token"] + out["by_class"]:
            self.assertEqual(r["label"], "claimed (unverified)")
        self.assertEqual({c["class"]: c["hits"] for c in out["by_class"]}, {"INDEX": 3, "MIXED": 3, "TRAIN": 2,
                                                                          "USER": 1})
        self.assertIn("claim", out["note"])

    def test_control_tokens_are_never_matched(self):
        reg = {"crawlers": [{"token": "Google-Extended", "class": "CONTROL", "ua_substring": None},
                            {"token": "Example-Bot", "class": "INDEX", "ua_substring": "Example-Bot"}]}
        with helpers.temp_dir() as tmp:
            log = write(tmp, "a.log", '192.0.2.1 - - [01/Nov/2026:00:00:00 +0000] "GET / HTTP/1.1" 200 1 "-" '
                                      '"Google-Extended Example-Bot/2"\n')
            out = an.classify_bots(log, crawler_registry=reg)
            self.assertEqual([r["token"] for r in out["by_token"]], ["Example-Bot"])


class GapsPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = json.loads(helpers.read_fixture("analytics", "tracker", "project.json"))

    def test_plan_reason_codes_and_one_rewrite_per_page(self):
        out = an.plan_citation_gaps(path("tracker", "tracker.csv"), self.project, root=path("tracker", "site"))
        self.assertEqual([p["page_id"] for p in out["pages"]], ["guide", "templates"])
        guide = out["pages"][0]
        self.assertEqual(guide["query_id"], "q-send")
        self.assertEqual(guide["other_gaps"], [{"query": "send invoice by email", "query_id": "q-email"}])
        self.assertEqual(guide["cited_sources"], ["https://example.org/a", "https://example.net/b",
                                                  "https://example.org/c"])  # duplicate row merged
        self.assertEqual([u["reason"] for u in out["unmatched"]],
                         ["query_not_in_project", "no_target_page", "page_has_no_source", "source_not_found"])
        self.assertEqual([s["reason"] for s in out["skipped"]], ["holdout_query", "tracker_error"])
        self.assertEqual((out["cited"], out["gaps"]), (1, 8))
        self.assertEqual([r["query_id"] for r in out["remeasure"]], ["q-send", "q-email", "q-template"])
        self.assertIn("never copy", out["note"])

    def test_without_root_sources_are_not_checked(self):
        out = an.plan_citation_gaps(path("tracker", "tracker.csv"), self.project)
        self.assertIn("reminders", [p["page_id"] for p in out["pages"]])
        self.assertTrue(out["source_check"].startswith("not checked"))

    def test_source_paths_outside_root_are_not_found(self):
        project = copy.deepcopy(self.project)
        project["pages"][0]["source_path"] = "../tracker.csv"
        out = an.plan_citation_gaps(path("tracker", "tracker.csv"), project, root=path("tracker", "site"))
        self.assertIn(("q-send", "source_not_found"), [(u.get("query_id"), u["reason"]) for u in out["unmatched"]])

    def test_json_tracker_and_tracker_errors(self):
        out = an.plan_citation_gaps(path("tracker", "tracker.json"), self.project, root=path("tracker", "site"))
        self.assertEqual([p["page_id"] for p in out["pages"]], ["templates"])
        self.assertEqual(out["skipped"], [{"query": "late fee calculator", "reason": "tracker_error",
                                           "detail": "rate limited"}])
        self.assertEqual(out["cited"], 1)

    def test_tracker_and_project_refusals(self):
        with helpers.temp_dir() as tmp:
            no_cited = write(tmp, "t.csv", "query,sources\na,\n")
            with self.assertRaisesRegex(ValueError, "cited column"):
                an.plan_citation_gaps(no_cited, self.project)
        broken = copy.deepcopy(self.project)
        broken["guardrails"]["no_fabricated_proof"] = False
        with self.assertRaisesRegex(ValueError, "project validate"):
            an.plan_citation_gaps(path("tracker", "tracker.csv"), broken)

    def test_normalize_query_and_cited_values(self):
        self.assertEqual(an.normalize_query("  How to   send an Invoice?! "), "how to send an invoice")
        self.assertEqual(an.normalize_query("¿Qué es net 30?"), "¿qué es net 30")
        rows_ = an.load_tracker(path("tracker", "tracker.csv"))
        self.assertEqual([r["cited"] for r in rows_[:6]], [False, False, False, True, False, False])
        self.assertEqual(rows_[0]["sources"], ["https://example.org/a", "https://example.net/b"])


class ProjectValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = json.loads(helpers.read_fixture("analytics", "tracker", "project.json"))

    def problems(self, mutate):
        project = copy.deepcopy(self.valid)
        mutate(project)
        return an.validate_project(project)

    def assertProblem(self, mutate, text):
        found = self.problems(mutate)
        self.assertTrue(any(text in p for p in found), "%r not in %r" % (text, found))

    def test_valid_fixture_and_template_placeholders(self):
        self.assertEqual(an.validate_project(self.valid), [])
        template = helpers.TEMPLATES_DIR / "project.example.json"
        if not template.is_file():
            self.skipTest("templates/project.example.json is written by another package")
        found = an.validate_project(json.loads(template.read_text(encoding="utf-8")))
        self.assertTrue(any("unfilled placeholder" in p for p in found))
        self.assertFalse(any("guardrails" in p for p in found))  # the template keeps all four guardrails true

    def test_secret_like_keys_and_values_rejected(self):
        self.assertProblem(lambda p: p["measurement"].update(api_key="x"), "secret-like key")
        self.assertProblem(lambda p: p["project"].update(gsc_token="x"), "secret-like key")
        self.assertProblem(lambda p: p["measurement"].update(note="sk-" + "a" * 30), "looks like a credential")

    def test_guardrails_required_and_true(self):
        self.assertProblem(lambda p: p["guardrails"].pop("no_auto_publish_visible_copy"),
                           "guardrails.no_auto_publish_visible_copy must be true")
        self.assertProblem(lambda p: p["guardrails"].update(no_fabricated_proof="true"),
                           "guardrails.no_fabricated_proof must be true")
        self.assertProblem(lambda p: p.pop("guardrails"), "guardrails.no_duplicate_query_owners")

    def test_url_and_domain_consistency(self):
        self.assertProblem(lambda p: p["project"].update(canonical_url="https://example.org/"),
                           "canonical_url host must equal")
        self.assertProblem(lambda p: p["pages"][0].update(url="https://example.net/x/"), "does not match")
        self.assertProblem(lambda p: p["pages"][0].update(url="https://user:pw@example.com/x/"), "userinfo")
        self.assertProblem(lambda p: p["pages"][0].update(url="/relative/"), "absolute http(s) URL")
        self.assertProblem(lambda p: p["project"].update(repository="ftp://example.net/repo"), "repository")

    def test_duplicates_and_owners(self):
        self.assertProblem(lambda p: p["pages"].append(dict(p["pages"][0])), "duplicate page id")
        self.assertProblem(lambda p: p["pages"].append(dict(p["pages"][0], id="copy",
                                                            url="https://example.com/guides/send-invoice")),
                           "share the same active URL")
        self.assertProblem(lambda p: p["queries"].append(dict(p["queries"][0])), "duplicate query id")
        self.assertProblem(lambda p: p["queries"].append(dict(p["queries"][0], id="q2", target_page="templates",
                                                              intent="other-intent")),
                           "give the same text")
        self.assertProblem(lambda p: p["queries"].append(dict(p["queries"][0], id="q3", text="new text",
                                                              target_page="templates")),
                           "give the same intent")

    def test_experiment_labels_allow_competing_owners(self):
        def both_experiments(p):
            p["queries"][0]["experiment"] = "exp-1"
            p["queries"].append(dict(p["queries"][0], id="q3", text="new text", target_page="templates"))
        self.assertEqual(self.problems(both_experiments), [])
        self.assertEqual(self.problems(lambda p: p["queries"].append(
            dict(p["queries"][0], id="q4", text="another text"))), [])  # same intent, same page: one owner

    def test_field_level_problems(self):
        self.assertProblem(lambda p: p.update(schema_version=2), "schema_version must be 1")
        self.assertProblem(lambda p: p["project"].pop("language"), "project.language is required")
        self.assertProblem(lambda p: p["queries"][0].update({"class": "seo"}), "class must be one of")
        self.assertProblem(lambda p: p["queries"][0].update(target_page="nowhere"), "is not a page id")
        self.assertProblem(lambda p: p["queries"][0].update(holdout="yes"), "holdout must be true or false")
        self.assertProblem(lambda p: p["pages"][0].update(status="live"), "status must be")
        self.assertProblem(lambda p: p["measurement"].update(engines=[]), "measurement.engines")
        self.assertProblem(lambda p: p["measurement"].pop("cadence"), "measurement.cadence")
        self.assertProblem(lambda p: p.update(pages=[]), "pages must be a non-empty list")
        self.assertEqual(an.validate_project([]), ["project file must be a JSON object"])


GOOGLE_OR_MICROSOFT = re.compile(r"(^|\.)(google\.com|blog\.google|web\.dev|developer\.chrome\.com|bing\.com|"
                                 r"microsoft\.com)$")


class UpdatesLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = rulesdb.load_data("search-updates")

    def test_filters_by_date_prefix_and_kind(self):
        out = an.updates(since="2026-09", kind="spam", today=helpers.TODAY)
        self.assertEqual([u["name"] for u in out["updates"]], ["September 2026 spam update"])
        core = an.updates(since="2026", kind="core", today=helpers.TODAY)
        self.assertEqual([u["date"] for u in core["updates"]], ["2026-03-27", "2026-05-21"])
        everything = an.updates(today=helpers.TODAY)
        self.assertEqual(everything["count"], len(self.doc["updates"]))
        dates = [u["date"] for u in everything["updates"]]
        self.assertEqual(dates, sorted(dates))
        self.assertNotIn("unverified", everything)
        self.assertGreater(everything["unverified_count"], 0)
        self.assertEqual(len(an.updates(today=helpers.TODAY, include_unverified=True)["unverified"]),
                         everything["unverified_count"])

    def test_freshness_states_and_upcoming(self):
        self.assertEqual(an.updates(today=date(2026, 11, 1))["freshness"]["status"], "fresh")
        self.assertEqual(an.updates(today=date(2027, 3, 1))["freshness"]["status"], "aging")
        stale = an.updates(today=date(2027, 6, 1))["freshness"]
        self.assertEqual((stale["status"], stale["age_days"]), ("stale", 212))
        self.assertIn(self.doc["source_of_truth"], stale["warning"])
        upcoming = an.updates(today=date(2027, 2, 1))["upcoming"]
        self.assertEqual([u["date"] for u in upcoming], ["2027-02-01", "2027-03-01", "2027-09-30"])

    def test_invalid_filters(self):
        for since in ("2026-9", "26", "2026-09-01T00:00"):
            with self.assertRaises(ValueError):
                an.updates(since=since, today=helpers.TODAY)
        with self.assertRaises(ValueError):
            an.updates(kind="algorithm", today=helpers.TODAY)

    def test_every_entry_cites_a_google_or_microsoft_url(self):
        self.assertEqual(self.doc["as_of"], "2026-11-01")
        self.assertIn("status.search.google.com", self.doc["source_of_truth"])
        for entry in self.doc["updates"] + self.doc["scheduled"]:
            with self.subTest(entry=entry["name"]):
                host = urlsplit(entry["source"]).hostname or ""
                self.assertTrue(entry["source"].startswith("https://") and GOOGLE_OR_MICROSOFT.search(host))
                self.assertIn(entry["kind"], an.UPDATE_KINDS)
        for entry in self.doc["updates"]:
            date.fromisoformat(entry["date"])
            if entry["kind"] in ("core", "spam", "discover"):
                self.assertEqual(entry["source"], self.doc["source_of_truth"])

    def test_dashboard_seed_and_unverified_shape(self):
        ranking = [(u["date"], u["kind"]) for u in self.doc["updates"] if u["kind"] in ("core", "spam", "discover")]
        self.assertEqual(len(ranking), 18)  # research table: March 2024 to September 2026
        self.assertIn(("2026-09-24", "spam"), ranking)
        for entry in self.doc["unverified"]:
            with self.subTest(claim=entry["claim"][:40]):
                self.assertEqual(sorted(entry), ["claim", "date", "sources", "status"])
                self.assertIsInstance(entry["sources"], list)
                self.assertTrue(entry["status"])

    def test_fact_ids_exist_in_the_registry(self):
        facts = helpers.REFERENCES_DIR / "current-facts.md"
        if not facts.is_file():
            self.skipTest("references/current-facts.md is written by another package")
        known = set(re.findall(r'<a id="(f-(?:ai|t)-\d{2})"></a>', facts.read_text(encoding="utf-8")))
        cited = set()
        for name in ("search-updates.json", "ai-referrers.json"):
            cited |= {f.lower() for f in re.findall(r"F-(?:AI|T)-\d{2}", (helpers.DATA_DIR / name).read_text())}
        self.assertEqual(sorted(cited - known), [])


class ReferrerRegistryTests(unittest.TestCase):
    def test_registry_shape(self):
        reg = rulesdb.load_data("ai-referrers")
        self.assertEqual(reg["as_of"], "2026-11-01")
        hosts = [h["host"] for h in reg["hosts"]]
        self.assertEqual(len(hosts), len(set(hosts)))
        self.assertTrue(all(h["product"] and h["label"] for h in reg["hosts"]))
        self.assertEqual(reg["utm_sources"], ["chatgpt.com"])
        self.assertEqual((reg["ga4_channel"]["fact"], reg["ga4_channel"]["medium"]), ("F-AI-30", "ai-assistant"))
        notes = " ".join(reg["notes"])
        self.assertIn("Organic Search", notes)
        self.assertIn("floor", notes)
        self.assertEqual({h["host"] for h in reg["hosts"] if h["mixed_search"]}, {"you.com", "phind.com", "kagi.com"})


if __name__ == "__main__":
    unittest.main()
