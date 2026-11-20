"""Tests for seo_geo_lib.jsonld (WP04): extraction, structure, Google feature checks, templates, data."""
from __future__ import annotations

import ast
import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_jsonld
import helpers  # noqa: E402
from seo_geo_lib import findings as F  # noqa: E402
from seo_geo_lib import jsonld as J  # noqa: E402

CAT = helpers.catalog()
CTX = "https://schema.org"
PAGE = "https://example.com/page/"
TEMPLATE_NAMES = ["article.json", "breadcrumb.json", "local-business.json", "organization-website.graph.json",
                  "product-merchant.json", "profile-page.json", "software-application.json", "video.json"]


def setUpModule():
    helpers.block_network()


def tearDownModule():
    assert helpers.network_attempts() == [], helpers.network_attempts()


def html(*blocks, head=""):
    body = "".join('<script type="application/ld+json">%s</script>\n' % (b if isinstance(b, str) else json.dumps(b))
                   for b in blocks)
    return "<!doctype html>\n<html><head>\n%s%s</head><body><p>x</p></body></html>\n" % (head, body)


def lint(*blocks, url=PAGE, filename="page.html", **kw):
    return J.lint_text(html(*blocks), CAT, filename=filename, url=url, **kw)[1]


def ids(found):
    return helpers.rule_ids(found)


def only(found, rule):
    return helpers.findings_for(found, rule)


def fixture_lint(name, url=PAGE, **kw):
    return J.lint_text(helpers.read_fixture("jsonld", name), CAT, filename="tests/fixtures/jsonld/" + name, url=url,
                       **kw)


def entity(**props):
    out = {"@context": CTX}
    out.update(props)
    return out


class ExtractTests(unittest.TestCase):
    def test_blocks_lines_and_indexes(self):
        text = ('<html>\n<head>\n<script type="application/ld+json">\n{"@type": "A"}\n</script>\n'
                '<script src="app.js"></script>\n<script type="application/ld+json">[]</script>\n')
        blocks = J.extract_blocks(text, filename="a.html")
        self.assertEqual([(b["index"], b["line"], b["content_line"]) for b in blocks], [(1, 3, 3), (2, 7, 7)])
        self.assertEqual(blocks[0]["raw"], '\n{"@type": "A"}\n')
        self.assertEqual([b["skipped"] for b in blocks], [None, None])
        self.assertTrue(all(b["closed"] for b in blocks))

    def test_regular_scripts_and_comments_are_ignored(self):
        blocks = J.extract_blocks(helpers.read_fixture("jsonld", "valid-article.html"), filename="v.html")
        self.assertEqual(len(blocks), 1)
        self.assertIn('"@graph"', blocks[0]["raw"])

    def test_mime_type_variants(self):
        accepted = ['type=" Application/LD+JSON "', "type='application/ld+json'", "type=application/ld+json",
                    'type="application/ld+json; charset=utf-8"', 'TYPE="application/ld+json"']
        for attr in accepted:
            with self.subTest(attr=attr):
                self.assertEqual(len(J.extract_blocks("<script %s>{}</script>" % attr)), 1)
        for attr in ('type="application/json"', 'type="text/javascript"', 'data-type="application/ld+json"', ""):
            with self.subTest(attr=attr):
                self.assertEqual(J.extract_blocks("<script %s>{}</script>" % attr), [])

    def test_quoted_gt_inside_attribute(self):
        blocks = J.extract_blocks('<script data-x="a>b" type="application/ld+json">{"a": 1}</script>')
        self.assertEqual(blocks[0]["raw"], '{"a": 1}')

    def test_closing_tag_rules(self):
        blocks = J.extract_blocks('<script type="application/ld+json">{"a": "</scripted>"}</script >tail')
        self.assertEqual(blocks[0]["raw"], '{"a": "</scripted>"}')
        unclosed = J.extract_blocks('<script type="application/ld+json">{"a": 1}')
        self.assertEqual((unclosed[0]["raw"], unclosed[0]["closed"]), ('{"a": 1}', False))
        self.assertEqual(J.extract_blocks('<script type="application/ld+json" data-x="never closed'), [])

    def test_html_self_closing_is_not_self_closing(self):
        blocks = J.extract_blocks('<script type="application/ld+json" />{"a": 1}</script>', filename="a.html")
        self.assertEqual(blocks[0]["raw"], '{"a": 1}')

    def test_json_file_is_one_block(self):
        blocks = J.extract_blocks('{"@type": "Thing"}', filename="templates/jsonld/x.json")
        self.assertEqual([(b["index"], b["line"], b["raw"]) for b in blocks], [(1, 1, '{"@type": "Thing"}')])

    def test_block_cap(self):
        text = '<script type="application/ld+json">{}</script>' * (J.MAX_BLOCKS + 5)
        self.assertEqual(len(J.extract_blocks(text)), J.MAX_BLOCKS)
        self.assertTrue(J.lint_text(text, CAT, filename="a.html")[0]["truncated"])

    def test_redos_pathological_inputs_are_fast(self):
        n = 100_000
        cases = {
            "unterminated attribute": '<script type="application/ld+json" data-x="' + "a" * n,
            "repeated openers": "<script " * (n // 8),
            "repeated single quotes": "<script type=application/ld+json a='" * (n // 38),
            "attribute soup": '<script type="application/ld+json" ' + ' a=b c="d" ' * (n // 11) + ">{}</script>",
            "repeated closers": '<script type="application/ld+json">' + "</script" * (n // 8),
            "repeated comments": "<!--" * (n // 4),
            "braces in component": "<script type=\"application/ld+json\" x={" + "{" * n,
            "long json string": '<script type="application/ld+json">{"a": "' + "\\" * n + "</script>",
        }
        for label, text in sorted(cases.items()):
            for name in ("page.html", "Page.tsx"):
                with self.subTest(case=label, file=name):
                    start = time.perf_counter()
                    J.extract_blocks(text, filename=name)
                    J.lint_text(text, CAT, filename=name)
                    self.assertLess(time.perf_counter() - start, 1.0)


class TemplateSkipTests(unittest.TestCase):
    SOURCES = {
        "Page.tsx": '<script type="application/ld+json">{jsonLd}</script>',
        "Page.vue": '<script type="application/ld+json">{"name": "{{ title }}"}</script>',
        "Page.astro": '<script type="application/ld+json">{schema}</script>',
        "product.liquid": '<script type="application/ld+json">{"name": {{ product.title | json }}}</script>',
    }

    def test_component_files_skip_template_expressions(self):
        for name, text in sorted(self.SOURCES.items()):
            with self.subTest(file=name):
                found = J.lint_text(text, CAT, filename=name)[1]
                self.assertEqual(ids(found), ["SD019"])
                self.assertEqual(only(found, "SD019")[0].severity, "info")
                self.assertEqual(J.extract_blocks(text, filename=name)[0]["skipped"], J.SKIP_TEMPLATE)

    def test_same_text_in_html_is_validated(self):
        for name, text in sorted(self.SOURCES.items()):
            with self.subTest(file=name):
                self.assertIsNone(J.extract_blocks(text, filename="page.html")[0]["skipped"])
                found = J.lint_text(text, CAT, filename="page.html")[1]
                self.assertNotIn("SD019", ids(found))
                self.assertTrue({"SD001", "SD003"} & set(ids(found)))

    def test_each_marker(self):
        for marker in ("{{ x }}", "{% if x %}", "{@html x}", "${x}", "<?php echo $x; ?>", "<?= $x ?>", "<%= x %>"):
            text = '<script type="application/ld+json">{"name": "%s"}</script>' % marker
            with self.subTest(marker=marker):
                self.assertEqual(J.extract_blocks(text, filename="t.njk")[0]["skipped"], J.SKIP_TEMPLATE)
                self.assertIsNone(J.extract_blocks(text, filename="t.html")[0]["skipped"])
        for ext in J.COMPONENT_EXTS:
            with self.subTest(ext=ext):
                self.assertEqual(J.extract_blocks(self.SOURCES["Page.astro"], filename="x" + ext)[0]["skipped"],
                                 J.SKIP_TEMPLATE)

    def test_literal_json_in_component_is_validated(self):
        text = '<script type="application/ld+json">{"@context": "https://schema.org", "@type": "WebSite", ' \
               '"name": "{brace} inside a string", "url": "https://example.com/"}</script>'
        self.assertIsNone(J.extract_blocks(text, filename="Head.astro")[0]["skipped"])
        self.assertEqual(J.lint_text(text, CAT, filename="Head.astro", url=PAGE)[1], [])

    def test_template_mode_override(self):
        text = self.SOURCES["Page.vue"]
        self.assertEqual(ids(J.lint_text(text, CAT, filename="layout.html", template_mode=True)[1]), ["SD019"])
        self.assertEqual(ids(J.lint_text(text, CAT, filename="Page.vue", template_mode=False)[1]), ["SD003", "SD004"])

    def test_self_closing_jsx_does_not_swallow_the_file(self):
        text = helpers.read_fixture("jsonld", "Seo.tsx")
        blocks = J.extract_blocks(text, filename="Seo.tsx")
        self.assertEqual(len(blocks), 1)
        self.assertTrue(blocks[0]["self_closing"])
        self.assertEqual(blocks[0]["raw"], "")
        self.assertEqual(blocks[0]["line"], 5)


class ParseTests(unittest.TestCase):
    def test_valid_and_errors(self):
        self.assertEqual(J.parse_block('{"a": [1, 2]}'), ({"a": [1, 2]}, None))
        self.assertEqual(J.parse_block('\ufeff{"a": 1}')[0], {"a": 1})
        for raw in ('{"a": 1,}', "", "   ", '{"a": NaN}', "{'a': 1}", '{"a": 1} trailing'):
            with self.subTest(raw=raw):
                data, err = J.parse_block(raw)
                self.assertIsNone(data)
                self.assertTrue(err)

    def test_size_cap(self):
        self.assertIn("larger than 10 bytes", J.parse_block('{"a": "0123456789"}', max_bytes=10)[1])
        self.assertIsNone(J.parse_block('{"a": "é"}', max_bytes=12)[1])
        self.assertIsNotNone(J.parse_block('{"a": "éé"}', max_bytes=12)[1])

    def test_depth_limit(self):
        self.assertIsNone(J.parse_block("[" * 64 + "]" * 64)[1])
        self.assertIn("64", J.parse_block("[" * 65 + "]" * 65)[1])
        self.assertIsNotNone(J.parse_block("[" * 10_000)[1])
        found = lint("[" * 10_000)
        self.assertEqual(ids(found), ["SD001"])

    def test_syntax_error_line_is_absolute(self):
        text = '<html>\n<script type="application/ld+json">\n{\n  "a": 1,\n}\n</script>'
        found = J.lint_text(text, CAT, filename="a.html")[1]
        self.assertEqual([f.rule for f in found], ["SD001"])
        self.assertIn(found[0].line, (4, 5))  # comma line (3.13+) or closing-brace line (3.9-3.12)
        self.assertEqual(found[0].evidence["block"], 1)


INVALID_SHAPES = [
    ("null root", None, "SD002", "$"),
    ("number root", 42, "SD002", "$"),
    ("string root", "Thing", "SD002", "$"),
    ("boolean root", True, "SD002", "$"),
    ("nested array at root", [[{"@context": CTX, "@type": "Thing"}]], "SD002", "$[0]"),
    ("number in root array", [1], "SD002", "$[0]"),
    ("null in root array", [None], "SD002", "$[0]"),
    ("string graph", {"@context": CTX, "@graph": "x"}, "SD002", "$.@graph"),
    ("null graph member", {"@context": CTX, "@graph": [None]}, "SD002", "$.@graph[0]"),
    ("number graph member", {"@context": CTX, "@graph": [{"@type": "A"}, 42]}, "SD002", "$.@graph[1]"),
    ("nested array in graph", {"@context": CTX, "@graph": [[{"@type": "A"}]]}, "SD002", "$.@graph[0]"),
    ("no context", {"@type": "Thing"}, "SD003", "$"),
    ("empty context", {"@context": "", "@type": "Thing"}, "SD003", "$"),
    ("null context", {"@context": None, "@type": "Thing"}, "SD003", "$"),
    ("null context resets inheritance", {"@context": CTX, "@graph": [{"@context": None, "@type": "Thing"}]},
     "SD003", "$.@graph[0]"),
    ("graph without context", {"@graph": [{"@type": "Thing"}]}, "SD003", "$.@graph[0]"),
    ("no type", {"@context": CTX, "name": "x"}, "SD004", "$"),
    ("empty type", {"@context": CTX, "@type": ""}, "SD004", "$"),
    ("null type", {"@context": CTX, "@type": None}, "SD004", "$"),
    ("graph member without type", {"@context": CTX, "@graph": [{"name": "x"}]}, "SD004", "$.@graph[0]"),
    ("nested graph inherits, needs type", {"@context": CTX, "@graph": [{"@type": "A", "@graph": [{"name": "y"}]}]},
     "SD004", "$.@graph[0].@graph[0]"),
    ("number context", {"@context": 5, "@type": "Thing"}, "SD005", "$"),
    ("empty array context", {"@context": [], "@type": "Thing"}, "SD005", "$"),
    ("array context with number", {"@context": [CTX, 5], "@type": "Thing"}, "SD005", "$"),
    ("blank string context", {"@context": "  ", "@type": "Thing"}, "SD005", "$"),
    ("number type", {"@context": CTX, "@type": 5}, "SD005", "$"),
    ("empty array type", {"@context": CTX, "@type": []}, "SD005", "$"),
    ("array type with blank", {"@context": CTX, "@type": ["Thing", ""]}, "SD005", "$"),
    ("object type not coerced", {"@context": CTX, "@type": {"toString": {}}}, "SD005", "$"),
    ("blank string type", {"@context": CTX, "@type": "   "}, "SD005", "$"),
]

VALID_SHAPES = [
    ("string context", {"@context": CTX, "@type": "Thing"}),
    ("vocab context", {"@context": {"@vocab": "https://schema.org/"}, "@type": "Thing"}),
    ("context array", {"@context": [CTX, {"ex": "https://example.com/ns#"}, None], "@type": "Thing"}),
    ("empty graph", {"@context": CTX, "@graph": []}),
    ("graph inherits context", {"@context": CTX, "@graph": [{"@type": "A"}, {"@type": "B"}]}),
    ("root array", [{"@context": CTX, "@type": "A"}, {"@context": CTX, "@type": "B"}]),
    ("empty root array", []),
    ("type array", {"@context": CTX, "@type": ["Product", "Car"]}),
    ("named graph container", {"@context": CTX, "@id": "https://example.com/#g", "@graph": [{"@type": "A"}]}),
    ("typed graph wrapper", {"@context": CTX, "@type": "WebPage", "@graph": [{"@type": "Thing"}]}),
    ("single-object graph", {"@context": CTX, "@graph": {"@type": "Thing"}}),
    ("nested property objects need nothing", {"@context": CTX, "@type": "Article", "author": {"name": "x"}}),
    ("member context overrides", {"@context": None, "@graph": [{"@context": CTX, "@type": "Thing"}]}),
]


class StructuralTests(unittest.TestCase):
    def test_matrix_sizes(self):
        self.assertGreaterEqual(len(INVALID_SHAPES), 19)
        self.assertGreaterEqual(len(VALID_SHAPES), 7)

    def test_invalid_shapes(self):
        for label, data, rule, path in INVALID_SHAPES:
            with self.subTest(case=label):
                diags = J.structural(data, block=2, line=4)
                self.assertIn((rule, path), [(d["rule"], d["path"]) for d in diags], diags)
                self.assertTrue(all(d["block"] == 2 and d["line"] == 4 and d["message"] for d in diags))

    def test_valid_shapes(self):
        for label, data in VALID_SHAPES:
            with self.subTest(case=label):
                self.assertEqual(J.structural(data), [])

    def test_invalid_shapes_through_lint(self):
        for label, data, rule, _path in INVALID_SHAPES:
            with self.subTest(case=label):
                found = lint(json.dumps(data))
                self.assertIn(rule, ids(found))
                self.assertEqual(only(found, rule)[0].severity, CAT.get(rule).severity)

    def test_null_context_resets_inheritance(self):
        diags = J.structural({"@context": CTX, "@graph": [{"@type": "A"}, {"@context": None, "@type": "B"}]})
        self.assertEqual([(d["rule"], d["path"]) for d in diags], [("SD003", "$.@graph[1]")])
        self.assertIn("null", diags[0]["message"])

    def test_deep_python_structures_do_not_raise(self):
        deep = {"@context": CTX, "@type": "A"}
        for _ in range(300):
            deep = {"@context": CTX, "@graph": [deep]}
        self.assertIn("SD002", [d["rule"] for d in J.structural(deep)])
        wide = {"@context": CTX, "@graph": [{"@type": "A"} for _ in range(J.NODE_CAP + 5)]}
        self.assertEqual([d["kind"] for d in J.structural(wide)], ["limit"])
        self.assertIsInstance(J.entities(deep), list)


class EntitiesTests(unittest.TestCase):
    def test_flattening_paths_and_primary(self):
        data = {"@context": CTX, "@graph": [
            {"@type": "WebPage", "@id": "https://example.com/p/#webpage",
             "mainEntity": {"@type": "Product", "name": "W", "offers": {"@type": "Offer"}}},
            {"@type": "Organization", "@id": "https://example.com/#organization"}]}
        recs = J.entities(data)
        self.assertEqual([(r["path"], r["types"], r["top_level"], r["primary"]) for r in recs], [
            ("$.@graph[0]", ["WebPage"], True, True),
            ("$.@graph[0].mainEntity", ["Product"], False, True),
            ("$.@graph[0].mainEntity.offers", ["Offer"], False, False),
            ("$.@graph[1]", ["Organization"], True, True)])
        self.assertEqual(recs[3]["id"], "https://example.com/#organization")
        self.assertEqual(recs[1]["context"], CTX)

    def test_type_normalization(self):
        recs = J.entities({"@context": CTX, "@type": ["https://schema.org/Product", "schema:Car", "Product"]})
        self.assertEqual(recs[0]["types"], ["Car", "Product"])

    def test_root_array_and_container(self):
        self.assertEqual([r["path"] for r in J.entities([entity(**{"@type": "A"}), entity(**{"@type": "B"})])],
                         ["$[0]", "$[1]"])
        self.assertEqual(J.entities({"@context": CTX, "@graph": []}), [])


class PlaceholderTests(unittest.TestCase):
    def org(self, **props):
        base = {"@type": "Organization", "name": "Example Widgets", "description": "d", "url": "https://example.com/",
                "logo": "https://example.com/l.png"}
        base.update(props)
        return entity(**base)

    def test_tokens(self):
        for value in ("[REPLACE: name]", "[fill in]", "[Insert name]", "[TODO]", "[ todo: later ]", "[Business Name]",
                      "[City]", "[Your company]", "Lorem Ipsum dolor", "REPLACE_ME", "REPLACE", "YOUR_API_KEY",
                      "https://yourdomain.test/x"):
            with self.subTest(value=value):
                found = lint(self.org(alternateName=value))
                self.assertEqual(ids(found), ["SD006"])
                self.assertEqual(only(found, "SD006")[0].priority, None)
                self.assertEqual(only(found, "SD006")[0].evidence["paths"], ["$.alternateName"])

    def test_non_tokens(self):
        for value in ("Replacement parts", "replace the filter yearly", "Your order ships in two days",
                      "todo lists for teams", "Lorem", "[Remastered] edition", "YOURS truly", "MY_REPLACEMENT"):
            with self.subTest(value=value):
                self.assertEqual(lint(self.org(alternateName=value)), [])

    def test_example_com_urls(self):
        org = self.org(url="https://example.com/", logo="https://cdn.example.com/l.png")
        self.assertEqual(lint(org, url="https://example.com/a/"), [])
        self.assertEqual(lint(org, url="https://shop.example.com/a/"), [])
        on_other = only(lint(org, url="https://widgets.test/a/"), "SD006")
        self.assertEqual((len(on_other), on_other[0].evidence["count"], on_other[0].confidence), (1, 2, "high"))
        unknown = only(lint(org, url=None), "SD006")
        self.assertEqual(unknown[0].confidence, "medium")
        named = self.org(name="See example.com for details", url="https://widgets.test/",
                         logo="https://widgets.test/l.png")
        self.assertEqual(lint(named, url="https://widgets.test/a/"), [])

    def test_fixture_and_malformed_block(self):
        found = fixture_lint("placeholders.html", url="https://widgets.test/")[1]
        sd006 = only(found, "SD006")
        self.assertEqual(len(sd006), 1)
        self.assertEqual(sd006[0].evidence["count"], 5)
        bad = lint('{"@context": "https://schema.org", "name": "[REPLACE: x]",}')
        self.assertEqual(ids(bad), ["SD001", "SD006"])


class NoRichResultTests(unittest.TestCase):
    def test_fixture_types_are_info_only(self):
        found = fixture_lint("deprecated.html")[1]
        sd007 = only(found, "SD007")
        self.assertEqual(sorted(f.evidence["type"] for f in sd007),
                         ["ClaimReview", "FAQPage", "HowTo", "Occupation", "SpecialAnnouncement", "WebSite"])
        self.assertTrue(all(f.severity == "info" for f in sd007))
        self.assertNotIn("error", {f.severity for f in found})
        self.assertNotIn("warning", {f.severity for f in found})
        claim = [f for f in sd007 if f.evidence["type"] == "ClaimReview"][0]
        self.assertIn("phased out", claim.message)
        faq = [f for f in sd007 if f.evidence["type"] == "FAQPage"][0]
        self.assertEqual((faq.evidence["since"], faq.evidence["fact"]), ("2026-05-07", "F-T-02"))

    def test_website_only_flagged_for_search_action(self):
        site = {"@type": "WebSite", "name": "W", "url": "https://example.com/"}
        self.assertEqual(lint(entity(**site)), [])
        self.assertEqual(lint(entity(potentialAction={"@type": "ReadAction"}, **site)), [])
        flagged = lint(entity(potentialAction=[{"@type": "ReadAction"}, {"@type": "SearchAction"}], **site))
        self.assertEqual(ids(flagged), ["SD007"])

    def test_kept_types_are_not_flagged(self):
        for t in ("Course", "Quiz", "Vehicle", "Book", "VideoObject", "QAPage"):
            with self.subTest(type=t):
                self.assertNotIn("SD007", ids(lint(entity(**{"@type": t, "name": "x"}))))

    def test_nested_and_deduplicated(self):
        page = entity(**{"@type": "WebPage", "mainEntity": {"@type": "FAQPage"}})
        found = lint(page, entity(**{"@type": "FAQPage"}))
        self.assertEqual(len(F.dedupe(only(found, "SD007"))), 1)

    def test_non_schema_vocabulary_ignored(self):
        self.assertEqual(lint({"@context": "https://vocab.example.org/", "@type": "FAQPage"}), [])

    def test_severity_cap_holds(self):
        self.assertEqual(CAT.severity_for("SD007", profile="launch", expect_indexable=True), "info")


class RequiredPropertyTests(unittest.TestCase):
    def test_article_and_organization_never_sd008(self):
        for t in ("Article", "NewsArticle", "BlogPosting", "TechArticle", "Organization", "Corporation", "NGO"):
            with self.subTest(type=t):
                found = lint(entity(**{"@type": t}))
                self.assertNotIn("SD008", ids(found))
                self.assertEqual({f.severity for f in found}, {"info"})

    def test_local_business_address(self):
        found = lint(entity(**{"@type": "LocalBusiness", "name": "Shop"}))
        sd008 = only(found, "SD008")
        self.assertEqual((len(sd008), sd008[0].evidence["missing"], sd008[0].severity), (1, ["address"], "warning"))
        self.assertEqual(only(lint(entity(**{"@type": "Restaurant"})), "SD008")[0].evidence["missing"],
                         ["address", "name"])
        ok = entity(**{"@type": "Dentist", "name": "Shop", "address": {"@type": "PostalAddress", "streetAddress": "1"}})
        self.assertNotIn("SD008", ids(lint(ok)))

    def test_breadcrumb_items(self):
        def crumbs(*items):
            return entity(**{"@type": "BreadcrumbList", "itemListElement": list(items)})
        good = crumbs({"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"},
                      {"@type": "ListItem", "position": 2, "item": {"@id": "https://example.com/b/", "name": "B"}},
                      {"@type": "ListItem", "position": 3, "name": "Here"})
        self.assertEqual(lint(good), [])
        middle = crumbs({"@type": "ListItem", "position": 1, "name": "Home"}, {"@type": "ListItem", "position": 2,
                                                                                "name": "Here"})
        self.assertEqual(only(lint(middle), "SD008")[0].evidence["missing"], ["itemListElement[:-1].item"])
        single = crumbs({"@type": "ListItem", "position": 1, "name": "Home"})
        self.assertEqual(lint(single), [])
        nameless = crumbs({"@type": "ListItem", "position": 1, "item": "https://example.com/"})
        self.assertIn("itemListElement[].name|item.name", only(lint(nameless), "SD008")[0].evidence["missing"])
        self.assertIn("itemListElement", only(lint(crumbs()), "SD008")[0].evidence["missing"])

    def test_event_and_job_posting(self):
        event = entity(**{"@type": "MusicEvent", "name": "Gig", "startDate": "2026-12-01", "location": {"name": "Hall"}})
        self.assertEqual(only(lint(event), "SD008")[0].evidence["missing"], ["location.address"])
        job = {"@type": "JobPosting", "title": "Tech", "description": "d", "datePosted": "2026-10-01",
               "hiringOrganization": {"@type": "Organization", "name": "W"}, "employmentType": "FULL_TIME",
               "validThrough": "2026-12-01"}
        self.assertEqual(only(lint(entity(**job)), "SD008")[0].evidence["missing"],
                         ["jobLocation or applicantLocationRequirements"])
        remote = dict(job, applicantLocationRequirements={"@type": "Country", "name": "US"})
        self.assertEqual(lint(entity(**remote)), [])

    def test_product_snippet_and_merchant_listing(self):
        bare = only(lint(entity(**{"@type": "Product", "name": "W"})), "SD008")
        self.assertEqual([f.evidence["missing"] for f in bare], [["review or aggregateRating or offers"]])
        reviewed = entity(**{"@type": "Product", "name": "W", "review": {
            "@type": "Review", "author": {"@type": "Person", "name": "A"}, "reviewRating": {"ratingValue": 4},
            "datePublished": "2026-10-01"}})
        self.assertEqual(lint(reviewed), [])
        offer = {"@type": "Offer", "price": "19.99", "priceCurrency": "USD", "availability": "https://schema.org/InStock"}
        merchant = entity(**{"@type": "Product", "name": "W", "description": "d", "brand": {"name": "B"},
                             "offers": offer})
        found = only(lint(merchant), "SD008")
        self.assertEqual([(f.evidence["feature"], f.evidence["missing"], f.confidence) for f in found],
                         [("Merchant listing", ["image"], "medium")])
        self.assertEqual(lint(merchant, merchant=False), [])
        self.assertEqual(only(lint(merchant, merchant=True), "SD008")[0].confidence, "high")
        strict = only(lint(entity(**{"@type": "Product", "name": "W", "image": "https://example.com/w.png",
                                     "review": reviewed["review"]}), merchant=True), "SD008")
        self.assertEqual(strict[0].evidence["missing"], ["offers"])

    def test_software_app_and_profile_page(self):
        app = entity(**{"@type": "MobileApplication", "name": "A", "offers": {"@type": "Offer", "price": 0},
                        "applicationCategory": "GameApplication", "operatingSystem": "Android"})
        self.assertEqual(only(lint(app), "SD008")[0].evidence["missing"], ["aggregateRating or review"])
        no_price = entity(**{"@type": "SoftwareApplication", "name": "A", "applicationCategory": "x",
                             "operatingSystem": "y", "review": {"@type": "Review", "author": "A",
                                                                "reviewRating": {"ratingValue": 5}}})
        self.assertEqual(only(lint(no_price), "SD008")[0].evidence["missing"], ["offers.price"])
        profile = {"@type": "ProfilePage", "dateCreated": "2026-01-01", "dateModified": "2026-02-01"}
        self.assertEqual(lint(entity(mainEntity={"@type": "Person", "alternateName": "sam"}, **profile)), [])
        self.assertEqual(only(lint(entity(mainEntity={"@type": "Person"}, **profile)), "SD008")[0].evidence["missing"],
                         ["mainEntity.name or mainEntity.alternateName"])

    def test_nested_reviews(self):
        product = entity(**{"@type": "Product", "name": "W", "review": {"@type": "Review",
                                                                          "reviewRating": {"ratingValue": 4}}})
        nested = only(lint(product), "SD008")
        self.assertEqual([(f.evidence["path"], f.evidence["missing"]) for f in nested], [("$.review", ["author"])])
        top = entity(**{"@type": "Review", "author": "A", "reviewRating": {"ratingValue": 4}, "datePublished": "2026-01-01"})
        self.assertEqual(only(lint(top), "SD008")[0].evidence["missing"], ["itemReviewed", "itemReviewed.name"])

    def test_reference_resolution(self):
        graph = {"@context": CTX, "@graph": [
            {"@type": "Person", "@id": "https://example.com/#sam", "name": "Sam"},
            {"@type": "Article", "headline": "H", "datePublished": "2026-01-01", "dateModified": "2026-01-02",
             "image": "https://example.com/i.png", "author": {"@id": "https://example.com/#sam"}}]}
        self.assertEqual(lint(graph), [])
        dangling = json.loads(json.dumps(graph))
        dangling["@graph"][1]["author"] = {"@id": "https://example.com/#nobody"}
        self.assertEqual(only(lint(dangling), "SD009")[0].evidence["missing"], ["author.name"])

    def test_recommended_never_asks_for_ratings(self):
        shop = entity(**{"@type": "LocalBusiness", "name": "S", "address": {"streetAddress": "1"}})
        missing = [m for f in only(lint(shop), "SD009") for m in f.evidence["missing"]]
        self.assertIn("geo", missing)
        self.assertFalse({"aggregateRating", "review"} & set(missing))
        self.assertTrue(all(f.severity == "info" for f in only(lint(shop), "SD009")))

    def test_nested_non_feature_nodes_are_not_nudged(self):
        article = entity(**{"@type": "Article", "headline": "H", "datePublished": "2026-01-01",
                            "dateModified": "2026-01-02", "image": "https://example.com/i.png",
                            "author": {"@type": "Organization", "name": "W"}, "publisher": {"@type": "Organization"}})
        self.assertEqual(lint(article), [])


class SelfServingTests(unittest.TestCase):
    def shop(self, **props):
        base = {"@type": "LocalBusiness", "name": "S", "address": {"streetAddress": "1"}, "description": "d",
                "logo": "https://widgets.test/l.png", "telephone": "1", "geo": {"latitude": 1, "longitude": 1},
                "openingHoursSpecification": [{"opens": "09:00"}], "url": "https://widgets.test/"}
        base.update(props)
        return entity(**base)

    RATING = {"@type": "AggregateRating", "ratingValue": 4.5, "reviewCount": 10}

    def test_fixture_own_site(self):
        found = fixture_lint("local-self-serving.html", url="https://example.com/shop/")[1]
        sd010 = only(found, "SD010")
        self.assertEqual((len(sd010), sd010[0].confidence, sd010[0].severity), (1, "high", "warning"))
        self.assertIn("SD008", ids(found))

    def test_host_comparison(self):
        rated = self.shop(aggregateRating=self.RATING)
        self.assertEqual(only(lint(rated, url="https://www.widgets.test/x/"), "SD010")[0].confidence, "high")
        self.assertEqual(only(lint(rated, url="https://shop.widgets.test/x/"), "SD010")[0].confidence, "high")
        self.assertEqual(lint(rated, url="https://reviews.example.org/x/"), [])
        self.assertEqual(only(lint(rated, url=None), "SD010")[0].confidence, "low")
        no_url = self.shop(aggregateRating=self.RATING, url=None)
        del no_url["url"]
        self.assertEqual(only(lint(no_url, url="https://widgets.test/"), "SD010")[0].confidence, "medium")

    def test_review_site_fixture(self):
        self.assertEqual(fixture_lint("review-site.html", url="https://reviews.example.org/diner/")[1], [])
        self.assertEqual(ids(fixture_lint("review-site.html", url=None)[1]), ["SD010"])

    def test_organization_and_item_reviewed(self):
        org = entity(**{"@type": "Organization", "url": "https://example.com/", "review": [{"@type": "Review"}]})
        self.assertIn("SD010", ids(lint(org)))
        review = entity(**{"@type": "Review", "author": "A", "reviewRating": {"ratingValue": 5},
                           "itemReviewed": {"@type": "Store", "name": "S", "url": "https://example.com/"}})
        self.assertIn("SD010", ids(lint(review)))
        product = entity(**{"@type": "Product", "name": "W", "aggregateRating": self.RATING})
        self.assertNotIn("SD010", ids(lint(product)))
        self.assertNotIn("SD010", ids(lint(self.shop(aggregateRating=None))))


class RatingTests(unittest.TestCase):
    def check(self, **rating):
        product = entity(**{"@type": "Product", "name": "W", "aggregateRating": dict({"@type": "AggregateRating"},
                                                                                      **rating)})
        return only(lint(product), "SD011")

    def test_invalid(self):
        cases = [dict(ratingValue=4, ratingCount=0), dict(ratingValue=4, reviewCount="0"),
                 dict(ratingValue=4, ratingCount="many"), dict(ratingValue="great", ratingCount=3),
                 dict(ratingValue=6, ratingCount=3), dict(ratingValue=0.99, ratingCount=3),
                 dict(ratingValue="120%", ratingCount=3), dict(ratingValue="11/10", ratingCount=3),
                 dict(ratingValue=3, bestRating=1, worstRating=5, ratingCount=3), dict(ratingValue=4, ratingCount=1.5),
                 dict(ratingValue=4, ratingCount=True), dict(ratingValue=4, ratingCount=-2)]
        for case in cases:
            with self.subTest(case=case):
                found = self.check(**case)
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0].severity, "error")

    def test_valid_and_boundaries(self):
        cases = [dict(ratingValue=5, ratingCount=1), dict(ratingValue=1, reviewCount=1), dict(ratingValue="4.5",
                 ratingCount="1,234"), dict(ratingValue=8, bestRating=10, ratingCount=2),
                 dict(ratingValue=0, worstRating=0, ratingCount=2), dict(ratingValue="60%", ratingCount=2),
                 dict(ratingValue="6 / 10", ratingCount=2), dict(ratingValue="[REPLACE: rating]", ratingCount=2),
                 dict(ratingValue=4, ratingCount=2.0)]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(self.check(**case), [])

    def test_missing_counts_is_required_not_invalid(self):
        product = entity(**{"@type": "Product", "name": "W", "aggregateRating": {"@type": "AggregateRating",
                                                                                 "ratingValue": 4}})
        found = lint(product)
        self.assertEqual(ids(found), ["SD008"])
        self.assertEqual(only(found, "SD008")[0].evidence["missing"], ["ratingCount or reviewCount"])

    def test_fixture(self):
        found = fixture_lint("product-bad.html")[1]
        self.assertEqual(ids(found), ["SD008", "SD011", "SD017"])
        self.assertIn("ratingCount is 0", only(found, "SD011")[0].message)


class BreakoutTests(unittest.TestCase):
    def test_markers(self):
        cases = {"</scripted>": "high", "<!-- x": "high", "<script>": "high", "<b>bold</b>": "medium",
                 "a < b": "medium"}
        for value, confidence in sorted(cases.items()):
            with self.subTest(value=value):
                found = only(lint(entity(**{"@type": "WebPage", "name": value})), "SD012")
                self.assertEqual((len(found), found[0].confidence, found[0].severity), (1, confidence, "error"))

    def test_escaped_is_clean(self):
        self.assertEqual(lint('{"@context": "https://schema.org", "@type": "WebPage", "name": "a \\u003c/script> b"}'),
                         [])
        self.assertEqual(lint(entity(**{"@type": "WebPage", "name": "a > b"})), [])

    def test_fixture_cut_by_closing_tag(self):
        found = fixture_lint("breakout.html")[1]
        self.assertEqual(ids(found), ["SD001", "SD012"])
        by_block = {f.evidence["block"]: f for f in only(found, "SD012")}
        self.assertEqual(sorted(by_block), [1, 2])
        self.assertEqual(by_block[1].confidence, "high")
        self.assertIn("inside a JSON string", by_block[2].evidence["markers"][-1])


class UrlAndDateTests(unittest.TestCase):
    def org(self, **props):
        base = {"@type": "Organization", "name": "W", "description": "d", "url": "https://example.com/",
                "logo": "https://example.com/l.png"}
        base.update(props)
        return entity(**base)

    def test_urls(self):
        bad = {"/logo.png": "relative", "logo.png": "relative", "//cdn.example.com/l.png": "protocol-relative",
               "data:image/png;base64,AAAA": "non-http scheme data:", "": "empty", "https:///nohost": "malformed"}
        for value, problem in sorted(bad.items()):
            with self.subTest(value=value):
                found = only(lint(self.org(logo=value)), "SD013")
                self.assertEqual((len(found), found[0].evidence["problems"]), (1, [problem]))
        for value in ("https://example.com/l.png", "http://example.com/l.png", "HTTPS://EXAMPLE.COM/L.PNG"):
            with self.subTest(value=value):
                self.assertEqual(lint(self.org(logo=value)), [])

    def test_ids_and_lists(self):
        self.assertEqual(only(lint(self.org(**{"@id": "#org"})), "SD013")[0].evidence["property"], "@id")
        for value in ("_:b0", "urn:uuid:6e8bc430-9c3a-11d9-9669-0800200c9a66", "https://example.com/#org"):
            with self.subTest(value=value):
                self.assertEqual(lint(self.org(**{"@id": value})), [])
        found = only(fixture_lint("values.html")[1], "SD013")
        self.assertEqual(sorted(f.evidence["property"] for f in found), ["logo", "sameAs"])
        self.assertEqual([f.evidence["values"] for f in found if f.evidence["property"] == "sameAs"],
                         [["examplewidgets"]])
        self.assertEqual(lint(self.org(url="[REPLACE: home page URL]"), url=PAGE)[0].rule, "SD006")
        self.assertEqual(lint({"@context": "https://vocab.example.org/", "@type": "Thing", "url": "/x"}), [])

    def test_dates(self):
        good = ["2026-11-01", "2026-11", "2026", "2026-11-01T09:00:00Z", "2026-11-01T09:00:00.123+01:00",
                "2026-11-01T09:00+0100", "2024-02-29", "2026-11-01T23:59:60Z"]
        bad = ["01/11/2026", "November 1, 2026", "2026-13-01", "2026-02-30", "2026-11-01 09:00", "2026-11-01T25:00",
               "2026-11-01T09:00:00+15:00", "2026-1-1", 20261101, True]
        for value in good:
            with self.subTest(value=value):
                self.assertEqual(lint(self.org(foundingDate=value)), [])
        for value in bad:
            with self.subTest(value=value):
                found = only(lint(self.org(foundingDate=value)), "SD014")
                self.assertEqual((len(found), found[0].severity), (1, "warning"))
        self.assertEqual(only(fixture_lint("values.html")[1], "SD014")[0].evidence["values"], ["01/11/2026"])
        self.assertEqual(lint(self.org(foundingDate=None)), [])


class IdConflictTests(unittest.TestCase):
    ID = "https://example.com/#organization"

    def test_within_page(self):
        org = {"@type": "Organization", "@id": self.ID, "name": "W", "description": "d", "url": "https://example.com/",
               "logo": "https://example.com/l.png"}
        person = {"@type": "Person", "@id": self.ID, "name": "Sam"}
        found = only(lint({"@context": CTX, "@graph": [org, person]}), "SD015")
        self.assertEqual((len(found), found[0].evidence["id"], len(found[0].evidence["variants"])), (1, self.ID, 2))
        renamed = dict(org, name="Other")
        self.assertIn("SD015", ids(lint(entity(**org), entity(**renamed))))
        subtype = dict(org, **{"@type": "Store", "address": {"streetAddress": "1"}})
        self.assertNotIn("SD015", ids(lint({"@context": CTX, "@graph": [org, subtype]})))
        ref = {"@type": "WebSite", "name": "W", "url": "https://example.com/", "publisher": {"@id": self.ID}}
        self.assertEqual(lint({"@context": CTX, "@graph": [org, ref]}), [])
        self.assertEqual(lint(entity(**org), entity(**org)), [])

    def site(self, *names):
        out = {}
        for name in names:
            summary = fixture_lint("site/%s.html" % name, url="https://example.com/%s/" % name)[0]
            out["https://example.com/%s/" % name] = summary["entities"]
        return out

    def test_across_pages(self):
        found = J.lint_entities_site(self.site("a", "b", "c"), CAT)
        self.assertEqual(len(found), 1)
        f = found[0]
        self.assertEqual((f.rule, f.affected, f.url), ("SD015", 3, "https://example.com/a/"))
        self.assertEqual(list(f.sample), ["https://example.com/a/", "https://example.com/b/", "https://example.com/c/"])
        self.assertEqual(sorted(v["pages"] for v in f.evidence["variants"]), [1, 2])
        self.assertEqual(f.evidence["id"], self.ID)

    def test_consistent_pages_and_single_page(self):
        self.assertEqual(J.lint_entities_site(self.site("a", "c"), CAT), [])
        page = {"https://example.com/x/": J.entities({"@context": CTX, "@graph": [
            {"@type": "Organization", "@id": self.ID, "name": "W"}, {"@type": "Person", "@id": self.ID, "name": "S"}]})}
        self.assertEqual(J.lint_entities_site(page, CAT), [])
        self.assertEqual(J.lint_entities_site({}, CAT), [])

    def test_entity_records_input(self):
        pages = {"https://example.com/1/": J.entities(entity(**{"@type": "Organization", "@id": self.ID, "name": "W"})),
                 "https://example.com/2/": J.entities(entity(**{"@type": "Organization", "@id": self.ID, "name": "Z"}))}
        found = J.lint_entities_site(pages, CAT)
        self.assertEqual([f.affected for f in found], [2])


class MerchantOfferTests(unittest.TestCase):
    def product(self, offers, **kw):
        return entity(**dict({"@type": "Product", "name": "W", "description": "d", "image": "https://example.com/w.png",
                              "brand": {"name": "B"}, "offers": offers}, **kw))

    def offer(self, **props):
        return dict({"@type": "Offer", "availability": "https://schema.org/InStock"}, **props)

    def test_invalid_offers(self):
        cases = [dict(price=0, priceCurrency="USD"), dict(price="0.00", priceCurrency="USD"),
                 dict(price="19,99", priceCurrency="EUR"), dict(price="$19.99", priceCurrency="USD"),
                 dict(priceCurrency="USD"), dict(price=19.99), dict(price=19.99, priceCurrency="usd"),
                 dict(price=-1, priceCurrency="USD")]
        for case in cases:
            with self.subTest(case=case):
                found = only(lint(self.product(self.offer(**case))), "SD017")
                self.assertEqual((len(found), found[0].severity, found[0].confidence), (1, "warning", "medium"))

    def test_valid_offers(self):
        cases = [dict(price=19.99, priceCurrency="USD"), dict(price="0.01", priceCurrency="GBP"),
                 dict(priceSpecification={"@type": "UnitPriceSpecification", "price": 5, "priceCurrency": "EUR"}),
                 dict(price="[REPLACE: price]", priceCurrency="[REPLACE: currency]")]
        for case in cases:
            with self.subTest(case=case):
                self.assertNotIn("SD017", ids(lint(self.product(self.offer(**case)))))

    def test_modes_and_aggregate_offer(self):
        bad = self.product(self.offer(price=0, priceCurrency="USD"))
        self.assertEqual(lint(bad, merchant=False), [])
        self.assertEqual(only(lint(bad, merchant=True), "SD017")[0].confidence, "high")
        aggregate = self.product({"@type": "AggregateOffer", "lowPrice": 0, "priceCurrency": "USD"})
        self.assertNotIn("SD017", ids(lint(aggregate)))
        missing = only(lint(self.product({"@type": "AggregateOffer", "priceCurrency": "USD"})), "SD008")
        self.assertEqual(missing[0].evidence["missing"], ["lowPrice"])
        multi = only(lint(self.product([self.offer(price=1, priceCurrency="USD"), self.offer(price=0)])), "SD017")
        self.assertEqual(multi[0].evidence["problems"], ["offer 2 price 0 is not above 0", "offer 2 has no priceCurrency"])


class TemplateSourceTests(unittest.TestCase):
    def test_unsafe_and_safe_stringify(self):
        unsafe = fixture_lint("Seo.tsx")[1]
        self.assertEqual(ids(unsafe), ["SD018", "SD019"])
        self.assertEqual((only(unsafe, "SD018")[0].line, only(unsafe, "SD018")[0].severity), (6, "warning"))
        self.assertEqual(ids(fixture_lint("SeoSafe.tsx")[1]), ["SD019"])
        self.assertEqual(ids(fixture_lint("Schema.astro")[1]), ["SD019"])
        vue = fixture_lint("Product.vue")[1]
        self.assertEqual(ids(vue), ["SD018", "SD019"])
        self.assertEqual(len(only(vue, "SD018")), 1)

    def test_escape_variants(self):
        base = '<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: %s }} />'
        for expr in ('JSON.stringify(d).replace(/</g, "\\\\u003c")', "JSON.stringify(d).replaceAll('<', '\\\\x3c')",
                     'JSON.stringify(d).replace(/[<>&]/g, esc)'):
            with self.subTest(expr=expr):
                self.assertNotIn("SD018", ids(J.lint_text(base % expr, CAT, filename="A.jsx")[1]))
        self.assertIn("SD018", ids(J.lint_text(base % "JSON.stringify(d)", CAT, filename="A.jsx")[1]))
        self.assertEqual(J.lint_text(base % "safeJsonLd(d)", CAT, filename="A.jsx")[1][0].rule, "SD019")

    def test_html_files_are_not_scanned_for_sd018(self):
        text = '<script>var s = {type: "application/ld+json", text: JSON.stringify(d)};</script>'
        self.assertEqual(J.lint_text(text, CAT, filename="page.html")[1], [])

    def test_liquid_versus_html(self):
        self.assertEqual(ids(fixture_lint("product.liquid")[1]), ["SD019"])
        self.assertIn("SD001", ids(fixture_lint("product-as-html.html")[1]))


class FormatTests(unittest.TestCase):
    def test_microdata_and_rdfa(self):
        found = fixture_lint("microdata-only.html")[1]
        self.assertEqual(ids(found), ["SD020"])
        self.assertEqual((found[0].severity, found[0].evidence), ("info", {"microdata": True, "rdfa": False}))
        rdfa = '<html><body vocab="https://schema.org/"><div typeof="Product"></div></body></html>'
        self.assertEqual(J.lint_text(rdfa, CAT, filename="r.html")[1][0].evidence, {"microdata": False, "rdfa": True})

    def test_negatives(self):
        mixed = html(entity(**{"@type": "WebSite", "name": "W", "url": "https://example.com/"}),
                     head='<div itemscope itemtype="https://schema.org/Thing"></div>')
        self.assertEqual(J.lint_text(mixed, CAT, filename="m.html", url=PAGE)[1], [])
        plain = '<html><head><meta property="og:title" content="x"></head><script>if (typeof x === "y") {}</script></html>'
        self.assertEqual(J.lint_text(plain, CAT, filename="p.html")[1], [])
        self.assertEqual(J.lint_text("<div itemscope></div>", CAT, filename="a.html", markup={"microdata": False,
                                                                                            "rdfa": False})[1], [])
        flagged = J.lint_text("<p>x</p>", CAT, filename="a.html", markup={"microdata": True})[1]
        self.assertEqual(ids(flagged), ["SD020"])
        self.assertEqual(J.lint_text('{"@context": "https://schema.org", "@type": "Thing"}', CAT, filename="a.json")[1],
                         [])


class LintTextTests(unittest.TestCase):
    EXPECTED = {
        "valid-article.html": [],
        "deprecated.html": ["SD007"],
        "local-self-serving.html": ["SD008", "SD009", "SD010"],
        "product-bad.html": ["SD008", "SD011", "SD017"],
        "breakout.html": ["SD001", "SD012"],
        "values.html": ["SD013", "SD014"],
        "microdata-only.html": ["SD020"],
        "Seo.tsx": ["SD018", "SD019"],
        "product.liquid": ["SD019"],
    }

    def test_fixture_rule_sets(self):
        for name, expected in sorted(self.EXPECTED.items()):
            with self.subTest(fixture=name):
                self.assertEqual(ids(fixture_lint(name, url="https://example.com/shop/")[1]), expected)

    def test_summary(self):
        summary, found = fixture_lint("valid-article.html")
        self.assertEqual(found, [])
        self.assertEqual({k: summary[k] for k in ("blocks", "parsed", "invalid", "skipped", "truncated")},
                         {"blocks": 1, "parsed": 1, "invalid": 0, "skipped": 0, "truncated": False})
        self.assertEqual(summary["types"], ["BlogPosting", "Organization", "Person"])
        self.assertEqual([e["id"] for e in summary["entities"]], ["https://example.com/#organization",
                                                                  "https://example.com/authors/sam/#person",
                                                                  "https://example.com/blog/hinge/#article"])
        broken = J.lint_text(helpers.read_fixture("jsonld", "breakout.html"), CAT, filename="b.html")[0]
        self.assertEqual((broken["parsed"], broken["invalid"]), (1, 1))
        self.assertEqual(J.lint_text("", CAT)[0]["blocks"], 0)

    def test_findings_shape_and_determinism(self):
        names = sorted(self.EXPECTED) + ["placeholders.html", "review-site.html"]
        first = [f.to_dict(CAT) for n in names for f in fixture_lint(n)[1]]
        second = [f.to_dict(CAT) for n in names for f in fixture_lint(n)[1]]
        self.assertEqual(first, second)
        for item in first:
            with self.subTest(rule=item["rule"], id=item["id"]):
                rule = CAT.get(item["rule"])
                self.assertEqual((rule.owner, rule.status), ("jsonld", "v1"))
                self.assertEqual(item["severity"], CAT.severity_for(item["rule"]))
                self.assertTrue(item["file"].startswith("tests/fixtures/jsonld/"))
                self.assertEqual(helpers.validate_schema(item, "finding.schema.json"), [])
        for n in names:
            fps = [f.fingerprint() for f in fixture_lint(n)[1]]
            self.assertEqual(len(fps), len(set(fps)), n)

    def test_every_v1_rule_is_exercised(self):
        names = sorted(self.EXPECTED) + ["placeholders.html", "Product.vue"]
        seen = {f.rule for n in names for f in fixture_lint(n, url="https://example.com/shop/")[1]}
        seen |= {"SD002", "SD003", "SD004", "SD005"} & set(ids(lint(None, {"@type": "A"}, {"@context": CTX},
                                                                     {"@context": 5, "@type": "A"})))
        seen.add(J.lint_entities_site(IdConflictTests().site("a", "b"), CAT)[0].rule)
        v1 = {r.id for r in CAT.all() if r.owner == "jsonld" and r.status == "v1"}
        self.assertEqual(v1 - seen, set())
        self.assertNotIn("SD016", seen)

    def test_catalog_default_and_registry_override(self):
        text = html(entity(**{"@type": "FAQPage"}))
        self.assertEqual(ids(J.lint_text(text)[1]), ["SD007"])
        registry = json.loads(json.dumps(J.load_registry()))
        registry["no_rich_result"] = []
        self.assertEqual(J.lint_text(text, CAT, registry=registry)[1], [])


class TemplatesTests(unittest.TestCase):
    DIR = helpers.TEMPLATES_DIR / "jsonld"

    def test_exact_file_set(self):
        self.assertEqual(sorted(p.name for p in self.DIR.iterdir()), TEMPLATE_NAMES)

    def test_each_template_yields_only_sd006(self):
        for name in TEMPLATE_NAMES:
            text = (self.DIR / name).read_text(encoding="utf-8")
            for url in (None, "https://example.com/x/", "https://widgets.test/x/"):
                with self.subTest(template=name, url=url):
                    found = J.lint_text(text, CAT, filename="templates/jsonld/" + name, url=url)[1]
                    self.assertEqual(ids(found), ["SD006"])
            for profile_merchant in (True, False):
                with self.subTest(template=name, merchant=profile_merchant):
                    found = J.lint_text(text, CAT, filename="templates/jsonld/" + name, merchant=profile_merchant)[1]
                    self.assertEqual(ids(found), ["SD006"])

    def test_values_are_tokens_and_no_ratings(self):
        allowed_literal_keys = {"@context", "@type", "unitCode", "position"}

        def walk(value, key, name):
            if isinstance(value, dict):
                self.assertFalse({"aggregateRating", "reviewRating", "ratingValue"} & set(value), name)
                for k, v in value.items():
                    walk(v, k, name)
            elif isinstance(value, list):
                for v in value:
                    walk(v, key, name)
            elif key not in allowed_literal_keys:
                ok = isinstance(value, str) and (value.startswith("[REPLACE: ") or value.startswith("https://example.com/#"))
                self.assertTrue(ok, "%s: %s=%r" % (name, key, value))

        for name in TEMPLATE_NAMES:
            data = json.loads((self.DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(data["@context"], "https://schema.org")
            walk(data, None, name)
        graph = json.loads((self.DIR / "organization-website.graph.json").read_text(encoding="utf-8"))
        self.assertEqual([n["@id"] for n in graph["@graph"]], ["https://example.com/#organization",
                                                               "https://example.com/#website"])
        product = json.loads((self.DIR / "product-merchant.json").read_text(encoding="utf-8"))
        self.assertTrue({"shippingDetails", "hasMerchantReturnPolicy"} <= set(product["offers"]))
        video = json.loads((self.DIR / "video.json").read_text(encoding="utf-8"))
        self.assertEqual(video["hasPart"][0]["@type"], "Clip")


class DataTests(unittest.TestCase):
    DATA = json.loads((helpers.DATA_DIR / "structured-data.json").read_text(encoding="utf-8"))

    def feature(self, name):
        return [f for f in self.DATA["features"] if f["feature"] == name][0]

    def test_header(self):
        self.assertEqual(self.DATA["as_of"], "2026-11-01")
        self.assertEqual((self.DATA["schema_org"]["version"], self.DATA["schema_org"]["released"]), ("30.1", "2026-09-16"))
        self.assertEqual(self.DATA["gallery"]["count"], len(self.DATA["gallery"]["cards"]))
        self.assertEqual(self.DATA["gallery"]["count"], 25)
        self.assertEqual(self.DATA["formats"]["recommended"], "JSON-LD")

    def test_no_rich_result_seed(self):
        rows = {(e["type"], e["since"]) for e in self.DATA["no_rich_result"]}
        self.assertEqual(rows, {("FAQPage", "2026-05-07"), ("HowTo", "2023-09-14"), ("SpecialAnnouncement", "2025-07-31"),
                                ("ClaimReview", None), ("Occupation", "2025-09-09"), ("WebSite", "2024-11-21")})
        types = {e["type"] for e in self.DATA["no_rich_result"]}
        self.assertFalse(types & {"Course", "Quiz", "Vehicle", "Book"})
        for entry in self.DATA["no_rich_result"]:
            with self.subTest(type=entry["type"]):
                self.assertTrue(entry["source_url"].startswith("https://"))
                self.assertRegex(entry["fact"], r"^F-T-\d{2}$")
                self.assertIn(entry["status"], ("retired", "phasing_out"))

    def test_features(self):
        self.assertEqual(self.feature("Article")["required"], [])
        self.assertEqual(self.feature("Organization")["required"], [])
        self.assertEqual(self.feature("Local business")["required"], ["address", "name"])
        self.assertEqual(self.feature("Breadcrumb")["devices"], ["desktop"])
        self.assertTrue(self.feature("Event")["regions"])
        for f in self.DATA["features"]:
            with self.subTest(feature=f["feature"]):
                self.assertIn(f["status"], ("supported", "limited", "phasing_out"))
                self.assertTrue(f["source_url"].startswith("https://developers.google.com/search/"))
                offer_rec = set(f.get("offer_recommended") or ())
                for p in f.get("nudge") or ():
                    self.assertTrue(p in f["recommended"] or (p.startswith("offers.") and p[7:] in offer_rec), p)
                self.assertFalse({p.split(".")[0] for p in f.get("nudge") or ()} & set(self.DATA["never_nudge"]))

    def test_lists(self):
        self.assertEqual(set(self.DATA["never_nudge"]), {"aggregateRating", "review"})
        self.assertTrue({"Organization", "LocalBusiness"} <= set(self.DATA["self_serving_review_types"]))
        self.assertIn("Restaurant", J._default_reg().self_serving)
        self.assertNotIn("SocialMediaPosting", J._default_reg().expand(["Article"]))
        for key in ("url_properties", "date_properties"):
            self.assertEqual(self.DATA[key], sorted(set(self.DATA[key])))
        dates = [t["date"] for t in self.DATA["timeline"]]
        self.assertEqual(dates, sorted(dates))

    def test_fact_ids_exist_when_registry_present(self):
        facts = helpers.REFERENCES_DIR / "current-facts.md"
        if not facts.is_file():
            self.skipTest("references/current-facts.md not written yet")
        text = facts.read_text(encoding="utf-8")
        cited = {e["fact"] for e in self.DATA["no_rich_result"]} | {f["fact"] for f in self.DATA["features"]}
        for fact in sorted(cited):
            with self.subTest(fact=fact):
                self.assertIn('<a id="%s"></a>' % fact.lower(), text)


class SafetyTests(unittest.TestCase):
    def test_python39_syntax_and_imports(self):
        for path in (helpers.SCRIPTS_DIR / "seo_geo_lib" / "jsonld.py", helpers.PLUGIN_ROOT / "tests" / "test_jsonld.py"):
            with self.subTest(file=path.name):
                helpers.parse_py39(path)
        tree = ast.parse((helpers.SCRIPTS_DIR / "seo_geo_lib" / "jsonld.py").read_text(encoding="utf-8"))
        local = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level:
                local.update([node.module] if node.module else [a.name for a in node.names])
            elif isinstance(node, ast.Import):
                self.assertFalse({a.name.split(".")[0] for a in node.names} & {"subprocess", "socket", "pickle"})
        self.assertEqual(local - {"findings", "rulesdb"}, set())

    def test_untrusted_strings_are_bounded(self):
        long_name = "x" * 5000
        found = lint(entity(**{"@type": "Organization", "@id": "https://example.com/#o", "logo": "/" + long_name}))
        for f in found:
            self.assertLessEqual(len(json.dumps(f.to_dict(CAT))), 4000)
        summary = J.lint_text(html(entity(**{"@type": "Thing", "@id": "https://example.com/#t", "name": long_name})),
                              CAT, filename="a.html")[0]
        self.assertLessEqual(len(summary["entities"][0]["name"]), 200)


if __name__ == "__main__":
    unittest.main()
