"""Tests for seo_geo_lib.robots (WP03): RFC 9309 parsing and matching, AI access rules, registry, access check."""
from __future__ import annotations

import functools
import os
import sys
import time
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_robots
import helpers  # noqa: E402
from seo_geo_lib import fetch as fetchmod  # noqa: E402
from seo_geo_lib import robots as R  # noqa: E402
from seo_geo_lib.findings import dedupe  # noqa: E402

CAT = helpers.catalog()
REG = R.load_registry()
PUBLIC = "93.184.215.14"


def setUpModule():
    helpers.block_network()


def fx(name):
    return R.parse_robots(helpers.read_fixture("robots", name + ".txt"))


def ids(findings):
    return helpers.rule_ids(findings)


def only(findings, rule):
    return helpers.findings_for(findings, rule)


def check(text, **kw):
    return R.check_robots(R.parse_robots(text), CAT, **kw)


def entry(token):
    return next(e for e in REG["crawlers"] if e["token"] == token)


def shape(rb):
    """Comparable structure of a parse (line numbers kept: comments never add lines)."""
    return ([(g.agents, [(d, p, n) for d, p, n in g.rules], [s["value"] for s in g.signals]) for g in rb.groups],
            rb.sitemaps, [u[0].lower() for u in rb.unknown], [o[1] for o in rb.orphans], [m[1] for m in rb.malformed])


# ----------------------------------------------------------------------------- parsing

class ParseTests(unittest.TestCase):
    def test_consecutive_user_agents_share_one_group(self):
        rb = fx("rfc9309")
        self.assertEqual(rb.groups[0].agents, ["ExampleBot", "OtherBot"])
        self.assertEqual([d for d, _p, _n in rb.groups[0].rules], ["disallow", "allow"])
        self.assertEqual(len(rb.groups), 4)
        self.assertEqual(rb.sitemaps, ["https://example.com/sitemap.xml"])

    def test_user_agent_after_rules_starts_new_group(self):
        rb = R.parse_robots("User-agent: a\nDisallow: /x\nUser-agent: b\nDisallow: /y\n")
        self.assertEqual([g.agents for g in rb.groups], [["a"], ["b"]])

    def test_non_rule_lines_do_not_end_agent_collection(self):
        rb = R.parse_robots("User-agent: a\nCrawl-delay: 3\nUser-agent: b\nDisallow: /y\n")
        self.assertEqual([g.agents for g in rb.groups], [["a", "b"]])

    def test_split_only_on_cr_lf_crlf(self):
        rb = R.parse_robots("User-agent: *\rDisallow: /a\r\nDisallow: /b\nDisallow: /c")
        self.assertEqual([p for _d, p, _n in rb.groups[0].rules], ["/a", "/b", "/c"])
        self.assertEqual([n for _d, _p, n in rb.groups[0].rules], [2, 3, 4])

    def test_unicode_line_separators_inside_comment_stay_comment(self):
        for sep in ("\u2028", "\u2029", "\x85", "\x0b", "\x0c"):
            rb = R.parse_robots("User-agent: *\nDisallow: /a # note%sDisallow: /\n" % sep)
            self.assertEqual([p for _d, p, _n in rb.groups[0].rules], ["/a"], repr(sep))
            self.assertTrue(R.is_allowed(rb, "anybot", "/b"))

    def test_bom_is_stripped(self):
        rb = R.parse_robots("\ufeffUser-agent: *\nDisallow: /x\n")
        self.assertEqual(rb.groups[0].agents, ["*"])
        self.assertEqual(rb.unknown, [])

    def test_field_names_case_insensitive_and_whitespace_tolerant(self):
        rb = R.parse_robots("USER-AGENT :  Foo  \nDISALLOW:/x\n  allow : /x/y  \n")
        self.assertEqual(rb.groups[0].agents, ["Foo"])
        self.assertEqual(rb.groups[0].rules, [("disallow", "/x", 2), ("allow", "/x/y", 3)])

    def test_unknown_fields_orphans_and_malformed_lines(self):
        rb = R.parse_robots("Disallow: /early\nUser-agent: *\nCrawl-delay: 5\nHost: example.com\nDisalow: /typo\n"
                            "no separator here\nUser-agent:\nContent-Signal: search=yes\n")
        self.assertEqual(rb.orphans, [("Disallow: /early", 1)])
        self.assertEqual([u[0].lower() for u in rb.unknown], ["crawl-delay", "host"])
        self.assertEqual([m[1] for m in rb.malformed], [5, 6, 7])
        self.assertTrue(any("misspelling of disallow" in e for e in rb.errors))
        self.assertEqual(len(rb.groups[0].signals), 1)

    def test_content_signal_before_any_group_is_orphan(self):
        rb = R.parse_robots("Content-Signal: search=yes\nUser-agent: *\nAllow: /\n")
        self.assertEqual(rb.orphans, [("Content-Signal: search=yes", 1)])
        self.assertEqual(rb.groups[0].signals, [])

    def test_size_cutoff_drops_tail_and_partial_line(self):
        limit = 512000
        head = "User-agent: *\n"
        filler = "".join("Disallow: /p%06d-long-path-segment\n" % i for i in range(16000))
        text = head + filler + "Disallow: /\n"
        self.assertGreater(len(text.encode()), limit)
        rb = R.parse_robots(text)
        self.assertTrue(rb.truncated)
        self.assertEqual(rb.size, len(text.encode()))
        paths = [p for _d, p, _n in rb.groups[0].rules]
        self.assertNotIn("/", paths)
        self.assertTrue(all(p.endswith("-long-path-segment") for p in paths))
        self.assertTrue(R.is_allowed(rb, "anybot", "/zzz"))
        self.assertIn("CRAWL002", ids(R.check_robots(rb, CAT)))

    def test_size_exactly_at_limit_is_not_truncated(self):
        base = "User-agent: *\nDisallow: /x\n"
        rb = R.parse_robots(base + "#" * (100 - len(base)), max_bytes=100)
        self.assertFalse(rb.truncated)
        rb = R.parse_robots(base + "#" * (101 - len(base)), max_bytes=100)
        self.assertTrue(rb.truncated)
        self.assertEqual(rb.groups[0].rules, [("disallow", "/x", 2)])

    def test_cloudflare_marker_and_range(self):
        rb = fx("cloudflare-managed")
        self.assertTrue(rb.cloudflare_managed)
        self.assertEqual(rb.managed_range, (1, 12))
        self.assertFalse(fx("clean").cloudflare_managed)
        self.assertIn(R._CF_MARKER, [m.lower() for m in REG["cloudflare_managed"]["markers"]])

    def test_html_detected(self):
        self.assertTrue(R.parse_robots("<!DOCTYPE html><html><body>404</body></html>").looks_html)
        self.assertFalse(fx("clean").looks_html)

    def test_summary_is_json_ready(self):
        summary = R.robots_summary(fx("ai-policy"))
        self.assertTrue(summary["present"])
        self.assertIn("crawl-delay", summary["unknown_fields"])
        self.assertEqual(R.robots_summary(None), {"present": False})


class FuzzTests(unittest.TestCase):
    ALPHABET = "ab #:*$/\u2028\u2029xyz=\t"

    def test_parse_invariant_under_trailing_comments(self):
        rng = helpers.seeded_random()
        base_text = helpers.read_fixture("robots", "ai-policy.txt")
        base_lines = base_text.split("\n")
        expected = shape(R.parse_robots(base_text))
        for _ in range(200):
            lines = []
            for line in base_lines:
                if rng.random() < 0.6:
                    junk = "".join(rng.choice(self.ALPHABET) for _ in range(rng.randint(0, 12)))
                    line = line + rng.choice(("", " ", "\t")) + "#" + junk
                lines.append(line)
            got = shape(R.parse_robots("\n".join(lines)))
            self.assertEqual(got, expected)

    def test_random_input_never_crashes(self):
        rng = helpers.seeded_random()
        pool = "User-agent: *\nDisallow:Allow:Sitemap:Content-Signal:#$/\r\n\u2028\ufeff\x00\u00e9%2F=,ai-train=no"
        for _ in range(200):
            text = "".join(rng.choice(pool) for _ in range(rng.randint(0, 300)))
            rb = R.parse_robots(text)
            R.check_robots(rb, CAT)
            R.access_table(rb, paths=("/", "/a?b=c"))
            R.is_allowed(rb, "Googlebot", text[:50])


# ----------------------------------------------------------------------------- matching

class MatchTests(unittest.TestCase):
    def setUp(self):
        self.rb = fx("rfc9309")

    def test_union_of_groups_naming_the_token(self):
        self.assertFalse(R.is_allowed(self.rb, "ExampleBot", "/private/x"))
        self.assertFalse(R.is_allowed(self.rb, "ExampleBot", "/second-group/x"))
        self.assertTrue(R.is_allowed(self.rb, "OtherBot", "/second-group/x"))
        self.assertEqual(len(R.rules_for(self.rb, "examplebot")), 3)

    def test_token_match_is_case_insensitive_product_token(self):
        for token in ("EXAMPLEBOT", "examplebot", "ExampleBot/2.1 (+https://example.com/bot)"):
            self.assertFalse(R.is_allowed(self.rb, token, "/private/x"), token)

    def test_named_group_replaces_star(self):
        self.assertTrue(R.is_allowed(self.rb, "ExampleBot", "/tmp/x"))
        self.assertFalse(R.is_allowed(self.rb, "UnlistedBot", "/tmp/x"))

    def test_longest_match_wins(self):
        self.assertTrue(R.is_allowed(self.rb, "ExampleBot", "/private/public-page.html"))
        self.assertFalse(R.is_allowed(self.rb, "ExampleBot", "/private/public-page.htm"))

    def test_allow_wins_ties(self):
        rb = R.parse_robots("User-agent: *\nDisallow: /page\nAllow: /page\n")
        self.assertTrue(R.is_allowed(rb, "x", "/page"))
        rb = R.parse_robots("User-agent: *\nAllow: /page\nDisallow: /page\n")
        self.assertTrue(R.is_allowed(rb, "x", "/page"))

    def test_wildcard_and_end_anchor(self):
        self.assertFalse(R.is_allowed(self.rb, "x", "/docs/file.pdf"))
        self.assertTrue(R.is_allowed(self.rb, "x", "/docs/file.pdf?download=1"))
        self.assertTrue(R.is_allowed(self.rb, "x", "/tmp/ok"))
        self.assertFalse(R.is_allowed(self.rb, "x", "/tmp/ok2"))
        self.assertTrue(R.is_allowed(self.rb, "StrictBot", "/"))
        self.assertFalse(R.is_allowed(self.rb, "StrictBot", "/a"))
        rb = R.parse_robots("User-agent: *\nDisallow: /*/edit*\nDisallow: /a$b\n")
        self.assertFalse(R.is_allowed(rb, "x", "/post/12/edit?x=1"))
        self.assertTrue(R.is_allowed(rb, "x", "/post/12/view"))
        self.assertFalse(R.is_allowed(rb, "x", "/a$b/c"))
        self.assertTrue(R.is_allowed(rb, "x", "/a"))

    def test_matcher_edge_patterns(self):
        cases = [("/", "/", True), ("/*", "/anything", True), ("*", "/x", True), ("/a*b*c", "/aXbYc", True),
                 ("/a*b*c", "/aXcYb", False), ("/a*$", "/abc", True), ("/x$", "/x", True), ("/x$", "/xy", False),
                 ("/*.php$", "/index.php", True), ("/*.php$", "/index.php5", False), ("/ab*ab$", "/ab", False),
                 ("/ab*ab$", "/abab", True), ("$", "/", False), ("/fish*", "/Fish", False)]
        for pattern, path, expected in cases:
            self.assertEqual(R._matches(R._norm_pattern(pattern), R._norm_path(path)), expected, (pattern, path))

    def test_empty_disallow_is_ignored(self):
        rb = R.parse_robots("User-agent: *\nDisallow:\n")
        self.assertEqual(R.rules_for(rb, "x"), [])
        self.assertTrue(R.is_allowed(rb, "x", "/anything"))

    def test_no_group_or_no_file_allows_everything(self):
        rb = R.parse_robots("User-agent: OnlyBot\nDisallow: /\n")
        self.assertIsNone(R.rules_for(rb, "OtherBot"))
        self.assertTrue(R.is_allowed(rb, "OtherBot", "/x"))
        self.assertTrue(R.is_allowed(None, "OtherBot", "/x"))

    def test_robots_txt_itself_always_allowed(self):
        rb = fx("block-all")
        self.assertTrue(R.is_allowed(rb, "Googlebot", "/robots.txt"))
        self.assertFalse(R.is_allowed(rb, "Googlebot", "/robots.txt.bak"))

    def test_percent_encoding_normalized(self):
        rb = R.parse_robots("User-agent: *\nDisallow: /caf\u00e9\nDisallow: /%7euser\nDisallow: /a%2fb\n")
        for path in ("/caf\u00e9/menu", "/caf%c3%a9/menu", "/CAF%C3%A9".lower()):
            self.assertFalse(R.is_allowed(rb, "x", path), path)
        self.assertFalse(R.is_allowed(rb, "x", "/~user/page"))
        self.assertTrue(R.is_allowed(rb, "x", "/a/b"))
        self.assertFalse(R.is_allowed(rb, "x", "/a%2Fb"))

    def test_absolute_url_input_keeps_query(self):
        self.assertFalse(R.is_allowed(self.rb, "x", "https://example.com/file.pdf"))
        self.assertTrue(R.is_allowed(self.rb, "x", "https://example.com/file.pdf?x=1"))

    def test_policy_token_never_falls_back_to_star(self):
        rb = fx("block-all")
        self.assertIsNone(R.rules_for(rb, "__usage_ai-training"))
        self.assertTrue(R.is_allowed(rb, "__usage_ai-training", "/"))
        rb = fx("ai-policy")
        self.assertEqual(R.rules_for(rb, "__usage_ai-training"), [("disallow", "/"), ("allow", "/press/")])
        self.assertTrue(R.is_allowed(rb, "__usage_ai-training", "/press/kit.pdf"))
        self.assertFalse(R.is_allowed(rb, "__usage_ai-training", "/blog/"))

    def test_crawler_fallback_group(self):
        rb = R.parse_robots("User-agent: *\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /\n")
        self.assertFalse(R.is_allowed(rb, "Applebot", "/x"))
        self.assertTrue(R.is_allowed(rb, "Applebot", "/x", fallback="Googlebot"))
        star_only = R.parse_robots("User-agent: *\nDisallow: /\n")
        self.assertFalse(R.is_allowed(star_only, "Applebot", "/x", fallback="Googlebot"))

    def test_allow_predicate_for_our_crawler(self):
        allowed = R.allow_predicate("User-agent: seo-geo-god\nDisallow: /private/\n")
        self.assertFalse(allowed("https://example.com/private/a"))
        self.assertTrue(allowed("https://example.com/public"))

    def test_pathological_pattern_is_fast(self):
        rb = R.parse_robots("User-agent: *\nDisallow: /" + "*a" * 3000 + "$\n")
        path = "/" + "a" * 4000 + "b"
        start = time.perf_counter()
        for _ in range(20):
            R.is_allowed(rb, "x", path)
        self.assertLess(time.perf_counter() - start, 1.0)


# ----------------------------------------------------------------------------- Content-Signal

class ContentSignalTests(unittest.TestCase):
    def test_valid_values(self):
        out = R.parse_content_signal("search=yes, ai-train=no")
        self.assertEqual((out["search"], out["ai-train"], out["ai-input"]), ("yes", "no", None))
        self.assertFalse(out["malformed"])
        self.assertEqual(out["unknown"], [])

    def test_case_and_spacing_and_use_parameter(self):
        out = R.parse_content_signal("Search = Yes ,AI-Input=NO, use=reference")
        self.assertEqual((out["search"], out["ai-input"], out["use"]), ("yes", "no", "reference"))
        self.assertFalse(out["malformed"])

    def test_unknown_key_is_reported_not_malformed(self):
        out = R.parse_content_signal("search=yes, ai-personalization=no")
        self.assertEqual(out["unknown"], ["ai-personalization"])
        self.assertFalse(out["malformed"])

    def test_malformed_variants(self):
        for value in ("", "search", "search=", "ai-train=maybe", "use=forever", "search=yes,", "search=yes, search=no",
                      "=yes"):
            self.assertTrue(R.parse_content_signal(value)["malformed"], value)
        self.assertFalse(R.parse_content_signal("search=yes, search=yes")["malformed"])

    def test_keys_come_from_registry(self):
        out = R.parse_content_signal("search=yes")
        self.assertEqual(set(REG["content_signals"]["keys"]) | set(REG["content_signals"]["testing_keys"]),
                         {k for k in out if k not in ("unknown", "malformed", "problems")})


# ----------------------------------------------------------------------------- registry

class RegistryTests(unittest.TestCase):
    SEED = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "OAI-AdsBot", "ClaudeBot", "Claude-User", "Claude-SearchBot",
            "PerplexityBot", "Perplexity-User", "Googlebot", "Google-Extended", "GoogleOther", "Google-CloudVertexBot",
            "Google-Agent", "Google-GeminiNotebook", "Applebot", "Applebot-Extended", "bingbot", "meta-externalagent",
            "meta-webindexer", "meta-externalfetcher", "meta-externalads", "facebookexternalhit", "Amazonbot",
            "Amzn-SearchBot", "Amzn-User", "DuckAssistBot", "MistralAI-User", "MistralAI-Index", "MistralAI-Training",
            "CCBot", "Bytespider", "cohere-ai", "cohere-training-data-crawler", "anthropic-ai", "Claude-Web"]

    def test_schema_validates(self):
        self.assertEqual(helpers.validate_schema(REG, "ai-crawlers.schema.json"), [])
        self.assertEqual(REG["as_of"], "2026-11-01")
        self.assertEqual(REG["recheck_by"], ["2026-12-15", "2027-02-01", "2027-03-01", "2027-09-30"])

    def test_schema_rejects_missing_provenance(self):
        broken = R.load_registry()
        del broken["crawlers"][0]["source_label"]
        broken["crawlers"][1]["verified_on"] = "soon"
        problems = helpers.validate_schema(broken, "ai-crawlers.schema.json")
        self.assertTrue(any("source_label" in p for p in problems))
        self.assertTrue(any("verified_on" in p for p in problems))

    def test_seed_tokens_present_and_unique(self):
        tokens = [e["token"] for e in REG["crawlers"]]
        self.assertEqual(len({t.lower() for t in tokens}), len(tokens))
        for token in self.SEED:
            self.assertIn(token, tokens)
        self.assertEqual([p["token"] for p in REG["policy_tokens"]], ["__usage_ai-training"])

    def test_every_entry_has_provenance(self):
        for e in REG["crawlers"]:
            self.assertEqual(e["verified_on"], "2026-11-01", e["token"])
            self.assertIn(e["source_label"], ("V", "S", "3P", "SR"), e["token"])
            self.assertIn("source_url", e)
            if e["source_url"] is None:
                self.assertTrue(e["needs_verification"] and e["source_url_note"], e["token"])
            else:
                self.assertTrue(e["source_url"].startswith("https://"), e["token"])
            if e["source_label"] in ("3P", "SR"):
                self.assertTrue(e["needs_verification"], e["token"])
            else:
                self.assertFalse(e["needs_verification"], e["token"])
                self.assertIsNotNone(e["source_url"], e["token"])

    def test_google_extended_never_lists_ai_overviews_or_ai_mode(self):
        ge = entry("Google-Extended")
        self.assertEqual((ge["class"], ge["ua_substring"], ge["block_rule"]), ("CONTROL", None, "AI002"))
        for surface in ge["visibility_surfaces"]:
            self.assertNotIn("ai overview", surface.lower())
            self.assertNotIn("ai mode", surface.lower())
        self.assertIn("AI Overviews", entry("Googlebot")["visibility_surfaces"])

    def test_control_tokens_have_no_user_agent(self):
        for e in REG["crawlers"]:
            if e["class"] == "CONTROL":
                self.assertIsNone(e["ua_substring"], e["token"])
            else:
                self.assertEqual(e["ua_substring"], e["token"])

    def test_block_rule_consistent_with_class(self):
        for e in REG["crawlers"]:
            if e["token"] in ("Googlebot", "bingbot"):
                self.assertEqual(e["block_rule"], "AI004")
            elif e["class"] in ("USER", "AGENT") and e["honors_robots"] in ("no", "partial"):
                self.assertEqual(e["block_rule"], "AI003", e["token"])
            elif e["class"] in ("TRAIN", "CONTROL", "CORPUS"):
                self.assertEqual(e["block_rule"], "AI002", e["token"])
            elif e["block_rule"] == "AI001":
                self.assertTrue(e["visibility_surfaces"], e["token"])
            if e["block_rule"] == "AI003":
                self.assertIn(e["honors_robots"], ("no", "partial"), e["token"])

    def test_documented_behaviour_rows(self):
        self.assertEqual(entry("ClaudeBot")["crawl_delay"], "honored")
        self.assertEqual(entry("Applebot")["fallback"], "Googlebot")
        self.assertEqual(entry("Applebot")["crawl_delay"], "ignored")
        self.assertEqual(entry("Perplexity-User")["honors_robots"], "no")
        self.assertIs(entry("PerplexityBot")["training"], False)
        self.assertEqual(entry("CCBot")["rdns"], "*.crawl.commoncrawl.org")
        self.assertIn("legacy token (3P)", entry("anthropic-ai")["notes"])

    def test_policy_token_semantics(self):
        p = REG["policy_tokens"][0]
        self.assertIs(p["star_matches"], False)
        honored = {h["vendor"]: h["from"] for h in p["honored_by"]}
        self.assertEqual(honored["Microsoft Bing"], "2027-02-01")
        self.assertEqual(honored["Google"], "early 2027")
        self.assertEqual({h["label"] for h in p["honored_by"] if h["vendor"] == "OpenAI"}, {"SR"})

    def test_claims_map_to_registry_tokens(self):
        tokens = {e["token"] for e in REG["crawlers"]}
        pairs = {(c["check_token"], c["not_token"]) for c in REG["claims"]}
        for c in REG["claims"]:
            self.assertIn(c["check_token"], tokens)
            self.assertIn(c["not_token"], tokens)
        for pair in [("OAI-SearchBot", "GPTBot"), ("Googlebot", "Google-Extended"), ("Claude-SearchBot", "ClaudeBot"),
                     ("Applebot", "Applebot-Extended")]:
            self.assertIn(pair, pairs)

    def test_classes_cover_entries_and_load_returns_copy(self):
        self.assertTrue({e["class"] for e in REG["crawlers"]} <= set(REG["classes"]))
        copy_ = R.load_registry()
        copy_["crawlers"].clear()
        self.assertTrue(R.load_registry()["crawlers"])


# ----------------------------------------------------------------------------- check_robots rules

class CrawlRuleTests(unittest.TestCase):
    def test_crawl001_missing_file_and_launch_escalation(self):
        found = R.check_robots(None, CAT)
        self.assertEqual(ids(found), ["CRAWL001"])
        self.assertEqual(found[0].severity, "info")
        self.assertEqual(R.check_robots(None, CAT, profile="launch")[0].severity, "warning")
        self.assertNotIn("CRAWL001", ids(check("")))

    def test_crawl002_oversize(self):
        self.assertEqual(only(check("User-agent: *\nDisallow: /x\n" + "#" * 600000), "CRAWL002")[0].severity, "error")
        self.assertNotIn("CRAWL002", ids(check("User-agent: *\nDisallow: /x\n")))

    def test_crawl003_unsupported_fields(self):
        found = only(R.check_robots(fx("ai-policy"), CAT), "CRAWL003")
        self.assertEqual(sorted(f.evidence["field"] for f in found), ["crawl-delay", "noindex"])
        delay = next(f for f in found if f.evidence["field"] == "crawl-delay")
        self.assertIn("Anthropic", delay.message)
        self.assertNotIn("CRAWL003", ids(check("User-agent: *\nContent-Signal: search=yes\nAllow: /\n")))

    def test_crawl004_all_blocked(self):
        found = only(R.check_robots(fx("block-all"), CAT), "CRAWL004")
        self.assertEqual((len(found), found[0].severity, found[0].line), (1, "error", 2))
        self.assertNotIn("CRAWL004", ids(R.check_robots(fx("allowlist"), CAT)))
        self.assertNotIn("CRAWL004", ids(check("User-agent: *\nDisallow: /\nAllow: /public/\n")))
        self.assertIn("CRAWL004", ids(check("User-agent: *\nDisallow: /*\n\nUser-agent: Foo\nDisallow: /\n")))
        self.assertIn("CRAWL004", ids(check("User-agent: *\nDisallow: /\nAllow: /robots.txt\n")))

    def test_crawl005_assets(self):
        probe = only(R.check_robots(fx("assets"), CAT), "CRAWL005")
        self.assertEqual((len(probe), probe[0].confidence), (1, "medium"))
        self.assertTrue(probe[0].evidence["probe_paths"])
        given = only(R.check_robots(fx("assets"), CAT, asset_paths=["/assets/app.css", "/assets/public/a.css",
                                                                    "/img/logo.png"]), "CRAWL005")
        self.assertEqual(given[0].confidence, "high")
        self.assertEqual(given[0].evidence["blocked"], ["/assets/app.css"])
        self.assertEqual(only(R.check_robots(fx("assets"), CAT, asset_paths=["/assets/public/a.css"]), "CRAWL005"), [])
        self.assertNotIn("CRAWL005", ids(R.check_robots(fx("clean"), CAT)))
        self.assertNotIn("CRAWL005", ids(R.check_robots(fx("block-all"), CAT)))

    def test_crawl006_sitemap_lines(self):
        self.assertEqual(only(R.check_robots(fx("block-all"), CAT), "CRAWL006")[0].key, "sitemap-missing")
        invalid = only(R.check_robots(fx("ai-policy"), CAT), "CRAWL006")
        self.assertEqual((invalid[0].key, invalid[0].line), ("sitemap-invalid", 31))
        self.assertNotIn("CRAWL006", ids(check("User-agent: *\nAllow: /\nSitemap: http://example.com/s.xml\n")))
        self.assertIn("CRAWL006", ids(check("User-agent: *\nAllow: /\nSitemap: ftp://example.com/s.xml\n")))

    def test_crawl007_encoding(self):
        found = only(R.check_robots(fx("ai-policy"), CAT), "CRAWL007")
        self.assertEqual((len(found), found[0].line), (1, 7))
        self.assertIn("CRAWL007", ids(check("User-agent: *\nDisallow: /my page\n")))
        self.assertNotIn("CRAWL007", ids(check("User-agent: *\nDisallow: /caf%C3%A9/\n")))

    def test_crawl008_noindex_blocked(self):
        rb = fx("rfc9309")
        found = R.check_blocked_noindex(rb, ["https://example.com/tmp/page", "https://example.com/ok", "/x.pdf"], CAT)
        self.assertEqual([(f.url, f.file) for f in found], [(None, "/x.pdf"), ("https://example.com/tmp/page", None)])
        self.assertEqual(found[1].evidence["blocked_for"], ["Googlebot", "bingbot"])
        self.assertEqual(found[0].severity, "warning")
        rb = R.parse_robots("User-agent: Googlebot\nDisallow: /a/\n")
        self.assertEqual(R.check_blocked_noindex(rb, ["/a/1"], CAT)[0].evidence["blocked_for"], ["Googlebot"])
        self.assertEqual(R.check_blocked_noindex(None, ["/a/1"], CAT), [])

    def test_crawl009_malformed(self):
        found = only(R.check_robots(fx("ai-policy"), CAT), "CRAWL009")
        self.assertEqual((found[0].line, found[0].severity), (2, "warning"))
        self.assertIn("CRAWL009", ids(check("User-agent: *\nDisalow: /x\n")))
        self.assertIn("CRAWL009", ids(check("User-agent: *\nDisallow: private\n")))
        html = only(check("<!DOCTYPE html>\n<html><body>Not found</body></html>\n"), "CRAWL009")
        self.assertIn("HTML", html[0].message)
        self.assertNotIn("CRAWL009", ids(check("User-agent: *\nDisallow: *.pdf$\n")))


class AIRuleTests(unittest.TestCase):
    def setUp(self):
        self.policy = R.check_robots(fx("ai-policy"), CAT)

    def keys(self, findings, rule):
        return sorted(f.key for f in only(findings, rule))

    def test_ai001_named_block_of_ai_search(self):
        self.assertEqual(self.keys(self.policy, "AI001"), ["token:perplexitybot"])
        self.assertEqual(only(self.policy, "AI001")[0].severity, "warning")
        self.assertNotIn("AI001", ids(check("User-agent: PerplexityBot\nDisallow: /blog/\n")))
        self.assertNotIn("AI001", ids(check("User-agent: PerplexityBot\nAllow: /\n")))
        unknown = only(check("User-agent: MistralAI-Index\nDisallow: /\n"), "AI001")
        self.assertIn("does not describe", unknown[0].message)

    def test_ai001_applebot_follows_googlebot_group(self):
        found = check("User-agent: Googlebot\nDisallow: /\n")
        self.assertEqual(self.keys(found, "AI001"), ["token:applebot"])
        self.assertIn("follows the Googlebot group", only(found, "AI001")[0].message)
        self.assertEqual(self.keys(found, "AI004"), ["token:googlebot"])
        self.assertNotIn("AI001", ids(check("User-agent: Googlebot\nDisallow: /\n\nUser-agent: Applebot\nAllow: /\n")))

    def test_ai002_training_blocks(self):
        self.assertEqual(self.keys(self.policy, "AI002"),
                         ["token:claudebot", "token:google-extended", "token:gptbot"])
        ge = next(f for f in only(self.policy, "AI002") if f.key == "token:google-extended")
        self.assertNotIn("AI Overviews", ge.message)
        self.assertNotIn("AI Mode", ge.message)
        self.assertIn("Gemini Apps grounding", ge.message)
        self.assertEqual(ge.severity, "info")
        self.assertNotIn("AI002", ids(check("User-agent: GPTBot\nDisallow: /private/\n")))
        corpus = only(check("User-agent: CCBot\nDisallow: /\n"), "AI002")
        self.assertIn("corpus", corpus[0].message)

    def test_ai003_user_triggered_fetchers(self):
        self.assertEqual(self.keys(self.policy, "AI003"), ["token:perplexity-user"])
        self.assertEqual(self.keys(check("User-agent: Google-Agent\nDisallow: /cart/\n"), "AI003"),
                         ["token:google-agent"])
        self.assertNotIn("AI003", ids(check("User-agent: ChatGPT-User\nAllow: /\n")))
        claude_user = check("User-agent: Claude-User\nDisallow: /\n")
        self.assertEqual((ids(claude_user)), ["AI001", "CRAWL006"])

    def test_ai004_googlebot_and_bingbot(self):
        found = R.check_robots(fx("block-all"), CAT)
        self.assertEqual(self.keys(found, "AI004"), ["token:bingbot", "token:googlebot"])
        self.assertEqual(only(found, "AI004")[0].severity, "error")
        self.assertIn("by the * group", only(found, "AI004")[0].message)
        self.assertEqual(self.keys(check("User-agent: bingbot\nDisallow: /\n"), "AI004"), ["token:bingbot"])
        self.assertNotIn("AI004", ids(check("User-agent: Googlebot\nDisallow: /private/\n")))
        self.assertNotIn("AI004", ids(check("User-agent: Googlebot\nDisallow: /\nAllow: /$\n")))

    def test_ai005_malformed_content_signal(self):
        found = only(self.policy, "AI005")
        self.assertEqual((len(found), found[0].line), (1, 20))
        self.assertEqual(found[0].evidence["unknown_keys"], ["foo"])
        self.assertIn("AI005", ids(check("User-agent: *\nContent-Signal: ai-retrieval=yes\nAllow: /\n")))
        self.assertNotIn("AI005", ids(check("User-agent: *\nContent-Signal: search=yes, ai-input=no\nAllow: /\n")))

    def test_ai006_named_groups_lack_signal(self):
        found = only(self.policy, "AI006")
        self.assertEqual(len(found[0].evidence["groups"]), 3)
        repeated = ("User-agent: *\nContent-Signal: ai-train=no\nAllow: /\n\n"
                    "User-agent: GPTBot\nContent-Signal: ai-train=no\nDisallow: /\n")
        self.assertNotIn("AI006", ids(check(repeated)))
        self.assertNotIn("AI006", ids(check("User-agent: GPTBot\nDisallow: /\n")))
        self.assertNotIn("AI006", ids(check("User-agent: *\nContent-Signal: ai-train=no\nAllow: /\n\n"
                                            "User-agent: __usage_ai-training\nDisallow: /\n")))

    def test_ai007_shared_training_token(self):
        found = only(self.policy, "AI007")
        self.assertEqual(found[0].evidence["preference"], "mixed by path")
        full = only(check("User-agent: __usage_ai-training\nDisallow: /\n"), "AI007")
        self.assertEqual(full[0].evidence["preference"], "against AI training")
        self.assertIn("Microsoft Bing: 2027-02-01", full[0].evidence["honored_by"])
        self.assertIn("not access control", full[0].message)
        self.assertNotIn("AI007", ids(R.check_robots(fx("clean"), CAT)))

    def test_ai008_star_assumed_training_preference(self):
        self.assertIn("AI008", ids(R.check_robots(fx("cloudflare-managed"), CAT)))
        commented = check("# Block AI training crawlers\nUser-agent: *\nDisallow: /\n")
        self.assertIn("AI008", ids(commented))
        far = check("# Block AI training crawlers\n\n\n\n\n\nUser-agent: *\nDisallow: /\n")
        self.assertNotIn("AI008", ids(far))
        self.assertNotIn("AI008", ids(R.check_robots(fx("ai-policy"), CAT)))
        self.assertNotIn("AI008", ids(R.check_robots(fx("clean"), CAT)))

    def test_ai009_cloudflare_managed(self):
        found = only(R.check_robots(fx("cloudflare-managed"), CAT), "AI009")
        self.assertEqual((found[0].severity, found[0].line), ("warning", 1))
        self.assertEqual(found[0].evidence["disallowed_in_block"], ["CCBot", "GPTBot"])
        self.assertNotIn("AI009", ids(R.check_robots(fx("clean"), CAT)))

    def test_ai014_star_only_block(self):
        found = only(R.check_robots(fx("allowlist"), CAT), "AI014")
        tokens = found[0].evidence["tokens"]
        self.assertIn("OAI-SearchBot", tokens)
        self.assertIn("PerplexityBot", tokens)
        self.assertNotIn("Applebot", tokens)
        self.assertNotIn("AI014", ids(R.check_robots(fx("block-all"), CAT)))
        explicit = ("User-agent: *\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /\n\n" +
                    "".join("User-agent: %s\n" % t for t in tokens) + "Allow: /\n")
        self.assertNotIn("AI014", ids(check(explicit)))

    def test_clean_file_has_no_findings(self):
        self.assertEqual(R.check_robots(fx("clean"), CAT), [])
        self.assertEqual(R.check_robots(fx("rfc9309"), CAT), [])

    def test_location_owner_and_determinism(self):
        default = R.check_robots(fx("ai-policy"), CAT)
        self.assertTrue(all(f.file == "robots.txt" and f.url is None for f in default))
        live = R.check_robots(fx("ai-policy"), CAT, url="https://example.com/robots.txt")
        self.assertTrue(all(f.file is None and f.url == "https://example.com/robots.txt" for f in live))
        built = R.check_robots(fx("ai-policy"), CAT, file="dist/robots.txt")
        self.assertTrue(all(f.file == "dist/robots.txt" for f in built))
        again = R.check_robots(fx("ai-policy"), CAT)
        self.assertEqual([f.fingerprint() for f in default], [f.fingerprint() for f in again])
        self.assertEqual(len(dedupe(default)), len(default))
        for f in default + R.check_robots(fx("cloudflare-managed"), CAT) + R.check_robots(fx("allowlist"), CAT):
            rule = CAT.get(f.rule)
            self.assertEqual((rule.owner, rule.status), ("robots", "v1"), f.rule)
            self.assertLessEqual(len(f.message), 300, f.rule)

    def test_policy_templates_parse_cleanly(self):
        folder = helpers.TEMPLATES_DIR / "robots"
        files = sorted(folder.glob("*.txt")) if folder.is_dir() else []
        if not files:
            self.skipTest("templates/robots/ not present yet")
        for path in files:
            rb = R.parse_robots(path.read_text(encoding="utf-8"))
            self.assertEqual((rb.orphans, rb.malformed, rb.unknown, rb.errors), ([], [], [], []), path.name)
            found = ids(R.check_robots(rb, CAT))
            for rule in ("CRAWL004", "CRAWL009", "AI004", "AI005", "AI014"):
                self.assertNotIn(rule, found, path.name)
            for token in ("Googlebot", "bingbot"):
                self.assertTrue(R.is_allowed(rb, token, "/"), (path.name, token))
        search_only = folder / "search-only-no-training.txt"
        if search_only.is_file():
            rb = R.parse_robots(search_only.read_text(encoding="utf-8"))
            for token in ("OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User", "PerplexityBot",
                          "Perplexity-User"):
                self.assertTrue(R.is_allowed(rb, token, "/"), token)
            for token in ("GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended", "meta-externalagent", "CCBot",
                          "MistralAI-Training", "__usage_ai-training"):
                self.assertFalse(R.is_allowed(rb, token, "/"), token)

    def test_findings_validate_against_schema(self):
        for f in R.check_robots(fx("ai-policy"), CAT) + R.check_robots(fx("block-all"), CAT):
            self.assertEqual(helpers.validate_schema(f.to_dict(CAT), "finding.schema.json"), [], f.rule)


# ----------------------------------------------------------------------------- access table

class AccessTableTests(unittest.TestCase):
    def test_rows_carry_provenance_and_impacts(self):
        rows = R.access_table(fx("ai-policy"))
        by = {r["token"]: r for r in rows}
        for r in rows:
            for key in ("token", "vendor", "class", "allowed", "group", "visibility_impact", "training_impact",
                        "honors_robots", "verify", "source_url", "verified_on", "needs_verification"):
                self.assertIn(key, r)
        self.assertEqual((by["GPTBot"]["group"], by["GPTBot"]["allowed"]), ("named", {"/": False}))
        self.assertEqual(by["GPTBot"]["training_impact"], "preference against OpenAI training stated")
        self.assertEqual(by["PerplexityBot"]["visibility_impact"], "excluded from Perplexity search answers")
        self.assertEqual(by["Googlebot"]["group"], "*")
        self.assertTrue(by["Googlebot"]["visibility_impact"].startswith("eligible for Google Search"))
        self.assertEqual(by["Perplexity-User"]["honors_robots"], "no")
        self.assertTrue(by["Bytespider"]["needs_verification"])

    def test_google_extended_row_never_claims_ai_overviews(self):
        for text in (helpers.read_fixture("robots", "ai-policy.txt"), "User-agent: Google-Extended\nAllow: /\n"):
            row = next(r for r in R.access_table(R.parse_robots(text)) if r["token"] == "Google-Extended")
            self.assertNotIn("AI Overviews", row["visibility_impact"])
            self.assertNotIn("AI Mode", row["visibility_impact"])

    def test_policy_row_and_star(self):
        row = next(r for r in R.access_table(fx("block-all")) if r["token"] == "__usage_ai-training")
        self.assertEqual(row["group"], "none")
        self.assertTrue(row["training_impact"].startswith("no preference expressed"))
        row = next(r for r in R.access_table(fx("ai-policy"), paths=("/", "/press/a")) if r["class"] == "CONTROL"
                   and r["token"] == "__usage_ai-training")
        self.assertEqual(row["allowed"], {"/": False, "/press/a": True})
        self.assertTrue(row["training_impact"].startswith("mixed by path"))

    def test_class_filters(self):
        rb = fx("ai-policy")
        self.assertEqual({r["class"] for r in R.access_table(rb, classes="training")}, {"TRAIN", "CONTROL", "CORPUS"})
        self.assertEqual({r["class"] for r in R.access_table(rb, classes="search")}, {"INDEX", "MIXED"})
        self.assertEqual({r["class"] for r in R.access_table(rb, classes=["USER"])}, {"USER"})
        self.assertNotIn("ADS", {r["class"] for r in R.access_table(rb, classes="ai")})
        self.assertEqual(len(R.access_table(rb, classes="all")), len(R.access_table(rb)))
        with self.assertRaises(ValueError):
            R.access_table(rb, classes="robots")

    def test_unknown_agents_and_fallback_rows(self):
        rb = R.parse_robots("User-agent: *\nDisallow: /\n\nUser-agent: Googlebot\nAllow: /\n\n"
                            "User-agent: ExampleScraper\nDisallow: /\n")
        rows = {r["token"]: r for r in R.access_table(rb)}
        self.assertFalse(rows["ExampleScraper"]["in_registry"])
        self.assertTrue(rows["ExampleScraper"]["blocks_site"])
        self.assertEqual(rows["Applebot"]["group"], "fallback:Googlebot")
        self.assertEqual(rows["Applebot"]["allowed"], {"/": True})
        self.assertNotIn("ExampleScraper", {r["token"] for r in R.access_table(rb, classes="ai")})

    def test_no_robots_file(self):
        rows = R.access_table(None, paths=("/", "/x"))
        self.assertTrue(all(r["group"] == "none" and all(r["allowed"].values()) for r in rows))


# ----------------------------------------------------------------------------- page directives

class PageDirectiveTests(unittest.TestCase):
    URL = "https://example.com/a/"

    def run_one(self, entry_):
        return R.check_page_ai_directives({self.URL: entry_}, CAT)

    def test_ai010_snippet_controls(self):
        found = self.run_one({"google": {"tokens": ["nosnippet"], "nosnippet": True, "max_snippet": None}})
        self.assertEqual(ids(found), ["AI010"])
        self.assertIn("AI Overviews", found[0].message)
        self.assertEqual(found[0].url, self.URL)
        self.assertEqual(ids(self.run_one({"google": {"max_snippet": 50}})), ["AI010"])
        self.assertIn("max-snippet:50", self.run_one({"google": {"max_snippet": 50}})[0].message)
        self.assertEqual(ids(self.run_one({"google": {"params": {"max-snippet": "0"}}})), ["AI010"])
        self.assertEqual(ids(self.run_one({"google": {"max_snippet": -1}})), [])
        self.assertEqual(ids(self.run_one({"data_nosnippet": 2})), ["AI010"])
        self.assertEqual(ids(self.run_one({"google": {"nosnippet": True, "noindex": True}})), [])
        self.assertEqual(ids(self.run_one({"tokens": ["nosnippet"]})), ["AI010"])
        self.assertEqual(self.run_one({"google": {"tokens": ["max-snippet:30"]}})[0].evidence["max_snippet"], 30)

    def test_ai011_noarchive_nocache(self):
        found = self.run_one({"google": {"tokens": ["noarchive"]}, "bingbot": {"tokens": ["nocache"]}})
        self.assertEqual(ids(found), ["AI011"])
        self.assertEqual(found[0].evidence["directives"], ["noarchive", "nocache"])
        self.assertIn("2027-03-01", found[0].message)
        self.assertEqual(ids(self.run_one({"google": {"tokens": ["noindex", "nofollow"]}})), [])

    def test_ai012_bing_ai_directives(self):
        found = self.run_one({"bing_ai": {"ai-training": "disallow", "ai-grounding": None}})
        self.assertEqual(ids(found), ["AI012"])
        self.assertIn("2027-02-01", found[0].message)
        self.assertEqual(ids(self.run_one({"bing_ai": {"ai-training": None, "ai-grounding": None}})), [])

    def test_accepts_directives_module_output(self):
        try:
            from seo_geo_lib import directives
        except ImportError:
            self.skipTest("directives.py (WP02) not present")
        meta = {"robots": ["max-snippet:40, noarchive"], "bingbot": ["ai-grounding:disallowextended"]}
        xrobots = directives.parse_x_robots(["bingbot: nocache"])
        found = self.run_one({"google": directives.effective(meta, xrobots, "googlebot"),
                              "bingbot": directives.effective(meta, xrobots, "bingbot"),
                              "bing_ai": directives.bing_ai(meta, xrobots)})
        self.assertEqual(ids(found), ["AI010", "AI011", "AI012"])
        self.assertEqual(only(found, "AI010")[0].evidence["max_snippet"], 40)
        self.assertEqual(only(found, "AI011")[0].evidence["directives"], ["noarchive", "nocache"])
        self.assertEqual(only(found, "AI012")[0].evidence["bing_ai"], {"ai-grounding": "disallowextended"})

    def test_file_location_and_order(self):
        found = R.check_page_ai_directives({"dist/b.html": {"tokens": ["noarchive"]},
                                            "dist/a.html": {"tokens": ["noarchive"]}}, CAT)
        self.assertEqual([f.file for f in found], ["dist/a.html", "dist/b.html"])
        self.assertTrue(all(f.url is None for f in found))


# ----------------------------------------------------------------------------- live access check (fakes only)

def resp(status=200, body="", ctype="text/plain", headers=None, error_kind=None, url=None):
    h = {"content-type": ctype}
    h.update(headers or {})
    return SimpleNamespace(status=status, headers=h, text=body, content_type=ctype, error=None if not error_kind
                           else "fake " + error_kind, error_kind=error_kind, url=url)


class FakeFetch:
    def __init__(self, routes, default=None):
        self.routes, self.default = routes, default or resp(404, "nf", "text/html")
        self.calls = []

    def __call__(self, url, accept=None, max_bytes=None):
        self.calls.append((url, accept))
        path = url.split("://", 1)[1].split("/", 1)
        key = "/" + (path[1] if len(path) > 1 else "")
        route = self.routes.get((key, accept)) or self.routes.get(key) or self.default
        return route

    def paths(self):
        return ["/" + u.split("://", 1)[1].split("/", 1)[1] for u, _a in self.calls]


ORIGIN = "https://example.com"
GOOD_ROBOTS = "User-agent: *\nContent-Signal: search=yes, ai-train=no\nAllow: /\n\nSitemap: https://example.com/s.xml\n"


class AccessCheckTests(unittest.TestCase):
    def run_check(self, routes, **kw):
        fake = FakeFetch(routes)
        data, found = R.access_check(ORIGIN, fetch=fake, catalog=CAT, **kw)
        return fake, data, found

    def test_robots_5xx_is_ai015_and_limits_probes(self):
        fake, data, found = self.run_check({"/robots.txt": resp(503, "down")})
        self.assertEqual(ids(found), ["AI015"])
        self.assertEqual(found[0].severity, "error")
        self.assertIn("12 hours", found[0].message)
        self.assertEqual(data["robots"]["outcome"], "unreachable")
        self.assertEqual(sorted(set(fake.paths())), ["/", "/robots.txt"])
        self.assertTrue(any(s["path"] == "/llms.txt" for s in data["skipped"]))

    def test_robots_unreachable_and_429(self):
        for route in (resp(None, "", error_kind="timeout"), resp(429, "slow down")):
            _fake, data, found = self.run_check({"/robots.txt": route})
            self.assertIn("AI015", ids(found))

    def test_robots_404_is_no_restrictions(self):
        fake, data, found = self.run_check({"/robots.txt": resp(404, "nf", "text/html")})
        self.assertEqual(data["robots"]["outcome"], "no-restrictions")
        self.assertEqual(ids(found), ["CRAWL001"])
        self.assertIn("/llms.txt", fake.paths())

    def test_robots_redirect_loop_is_treated_as_not_found(self):
        fake, data, found = self.run_check({"/robots.txt": resp(None, "", error_kind="too_many_redirects")})
        self.assertEqual(data["robots"]["outcome"], "too-many-redirects")
        self.assertEqual(ids(found), ["CRAWL001"])
        self.assertEqual(found[0].confidence, "medium")
        self.assertIn("/llms.txt", fake.paths())

    def test_refused_origin_stops(self):
        fake, data, found = self.run_check({"/robots.txt": resp(None, "", error_kind="url_refused")})
        self.assertEqual((found, len(fake.calls)), ([], 1))
        self.assertIn("refused", data["error"])

    def test_invalid_origin(self):
        with self.assertRaises(ValueError):
            R.access_check("ftp://example.com", fetch=FakeFetch({}), catalog=CAT)

    def test_clean_site(self):
        routes = {"/robots.txt": resp(200, GOOD_ROBOTS), "/": resp(200, "<html></html>", "text/html"),
                  "/llms.txt": resp(200, "# Example\n", "text/plain")}
        fake, data, found = self.run_check(routes)
        self.assertEqual(found, [])
        self.assertFalse(data["not_found_probe"]["soft_404"])
        self.assertTrue(data["llms"]["present"])
        self.assertEqual(len(data["well_known"]), 4)
        self.assertEqual(data["requests"], len(fake.calls))

    def test_http004_soft_404_probe(self):
        fake = FakeFetch({"/robots.txt": resp(200, GOOD_ROBOTS)}, default=resp(200, "<html>app</html>", "text/html"))
        data, found = R.access_check(ORIGIN, fetch=fake, catalog=CAT)
        self.assertIn("HTTP004", ids(found))
        self.assertTrue(data["not_found_probe"]["soft_404"])
        self.assertIn("AGENT004", ids(found))
        agent8 = only(found, "AGENT008")
        self.assertEqual(len(agent8), 1)
        self.assertIn("catch-all", agent8[0].message)
        probe = only(found, "HTTP004")[0].url
        data2, found2 = R.access_check(ORIGIN, fetch=FakeFetch({"/robots.txt": resp(200, GOOD_ROBOTS)},
                                                               default=resp(200, "x", "text/html")), catalog=CAT)
        self.assertEqual(only(found2, "HTTP004")[0].url, probe)

    def test_agent004_llms_served_as_html(self):
        routes = {"/robots.txt": resp(200, GOOD_ROBOTS),
                  "/llms.txt": resp(200, "<!doctype html><title>x</title>", "text/plain")}
        _fake, data, found = self.run_check(routes)
        self.assertEqual(ids(found), ["AGENT004"])
        self.assertTrue(data["llms"]["served_as_html"])

    def test_llms_check_callback(self):
        seen = []
        routes = {"/robots.txt": resp(200, GOOD_ROBOTS), "/llms.txt": resp(200, "# Title\n", "text/markdown")}
        self.run_check(routes, llms_check=lambda text: seen.append(text) or [])
        self.assertEqual(seen, ["# Title\n"])

    def test_ai013_markdown_header_contradiction(self):
        md = resp(200, "# Home", "text/markdown",
                  {"content-signal": "ai-train=yes, search=yes, ai-input=yes", "vary": "Accept"})
        routes = {"/robots.txt": resp(200, GOOD_ROBOTS), ("/", "text/markdown"): md,
                  "/": resp(200, "<html></html>", "text/html")}
        _fake, data, found = self.run_check(routes)
        self.assertEqual(ids(found), ["AI013"])
        self.assertEqual(found[0].evidence["conflicts"][0]["key"], "ai-train")
        self.assertTrue(data["markdown"]["served_markdown"] and data["markdown"]["vary_accept"])
        self.assertEqual(data["contradictions"], ["markdown"])
        agree = dict(routes)
        agree[("/", "text/markdown")] = resp(200, "# Home", "text/markdown", {"content-signal": "ai-train=no"})
        self.assertEqual(self.run_check(agree)[2], [])

    def test_ai013_from_shared_token_and_training_groups(self):
        md = resp(200, "# Home", "text/markdown", {"content-signal": "ai-train=yes"})
        for robots_text in ("User-agent: __usage_ai-training\nDisallow: /\n",
                            "User-agent: GPTBot\nUser-agent: ClaudeBot\nDisallow: /\n"):
            routes = {"/robots.txt": resp(200, robots_text), ("/", "text/markdown"): md}
            found = self.run_check(routes)[2]
            self.assertIn("AI013", ids(found), robots_text)
        routes = {"/robots.txt": resp(200, "User-agent: *\nAllow: /\n"), ("/", "text/markdown"): md}
        self.assertNotIn("AI013", ids(self.run_check(routes)[2]))

    def test_ai009_live_and_dedupe_with_robots_findings(self):
        routes = {"/robots.txt": resp(200, helpers.read_fixture("robots", "cloudflare-managed.txt"))}
        _fake, data, found = self.run_check(routes)
        self.assertEqual(ids(found), ["AI009"])
        self.assertTrue(data["robots"]["cloudflare_managed"])
        _fake, _data, full = self.run_check(routes, robots_findings=True)
        self.assertGreater(len(ids(full)), 1)
        merged = dedupe(found + full)
        self.assertEqual(len(only(merged, "AI009")), 1)

    def test_agent008_well_known(self):
        routes = {"/robots.txt": resp(200, GOOD_ROBOTS),
                  "/.well-known/api-catalog": resp(200, "{not json", "application/linkset+json"),
                  "/.well-known/agent-card.json": resp(200, '{"name": "x"}', "application/json"),
                  "/.well-known/oauth-protected-resource": resp(200, "<html></html>", "text/html")}
        _fake, data, found = self.run_check(routes)
        self.assertEqual(ids(found), ["AGENT008"])
        self.assertEqual(found[0].evidence["documents"], ["/.well-known/api-catalog (invalid-json)",
                                                          "/.well-known/oauth-protected-resource (html)"])
        outcomes = {w["path"]: w["outcome"] for w in data["well_known"]}
        self.assertEqual(outcomes["/.well-known/agent-card.json"], "json")
        self.assertEqual(outcomes["/.well-known/oauth-authorization-server"], "absent")
        fake, data, _found = self.run_check({"/robots.txt": resp(200, GOOD_ROBOTS)}, probe_well_known=False)
        self.assertNotIn("well_known", data)

    def test_our_crawler_respects_robots(self):
        robots = "User-agent: seo-geo-god\nDisallow: /llms.txt\nDisallow: /.well-known/\n"
        fake, data, _found = self.run_check({"/robots.txt": resp(200, robots)})
        self.assertNotIn("/llms.txt", fake.paths())
        self.assertFalse(any(p.startswith("/.well-known/") for p in fake.paths()))
        self.assertEqual({s["path"] for s in data["skipped"]} & {"/llms.txt"}, {"/llms.txt"})
        fake, _data, _found = self.run_check({"/robots.txt": resp(200, robots)}, ignore_robots=True)
        self.assertIn("/llms.txt", fake.paths())

    def test_with_real_fetch_and_fake_transport(self):
        before = len(helpers.network_attempts())
        transport = helpers.FakeTransport(default=(404, {"Content-Type": "text/html"}, b"nf"))
        transport.add("https://example.com/robots.txt", 503, {"Content-Type": "text/plain"}, b"down")
        transport.add("https://example.com/", 200, {"Content-Type": "text/html"}, b"<html></html>")
        resolver = helpers.FakeResolver({"example.com": [PUBLIC]})
        fetch = functools.partial(fetchmod.fetch, transport=transport, resolver=resolver,
                                  clock=helpers.FakeClock())
        data, found = R.access_check(ORIGIN, fetch=fetch, catalog=CAT)
        self.assertEqual(ids(found), ["AI015"])
        self.assertEqual(transport.urls, ["https://example.com/robots.txt", "https://example.com/",
                                          "https://example.com/"])
        self.assertEqual(len(helpers.network_attempts()), before)


if __name__ == "__main__":
    unittest.main()
