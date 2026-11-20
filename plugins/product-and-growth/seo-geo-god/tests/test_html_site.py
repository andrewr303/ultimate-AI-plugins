"""WP02: PageDoc extraction, Markdown, directives, URL mapping, build traversal, page/site rules,
duplicates, link graph, redirect maps and the site-good / site-bad fixtures."""
from __future__ import annotations

import calendar
import json
import os
import re
import sys
import unittest
from typing import Any, Dict, List, Optional
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_html_site
import helpers  # noqa: E402
from seo_geo_lib import directives, hreflang, htmlparse, perf, sitemaps, sitescan  # noqa: E402
from seo_geo_lib.findings import dedupe, sort_findings  # noqa: E402

BASE = "https://example.com"
TODAY = helpers.TODAY
PARA = ("Widgets need a dry shelf, a soft cloth and a little patience. Wipe the housing gently and store "
        "the widget away from direct sunlight so the finish stays clean.")
WP02_OWNERS = ("sitescan", "sitemaps", "hreflang", "perf")


def setUpModule() -> None:
    helpers.block_network()


# ----------------------------------------------------------------------------------------- builders

def page(path: str = "/", *, title: Any = None, head: str = "", body: Optional[str] = None, lang: Optional[str] = "en",
         canonical: Any = "self", description: Any = True, og: bool = True, viewport: bool = True,
         h1: str = "Widget care") -> str:
    """A page that passes every WP02 page rule unless a parameter changes it."""
    url = BASE + path
    out = ["<!doctype html>", "<html%s>" % (' lang="%s"' % lang if lang else ""), "<head>", '<meta charset="utf-8">']
    if viewport:
        out.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    if title is not False:
        out.append("<title>%s</title>" % (title if title is not None else "Widget care notes for %s" % path))
    if description is True:
        out.append('<meta name="description" content="Care notes for the synthetic page %s.">' % path)
    elif description:
        out.append('<meta name="description" content="%s">' % description)
    canon = url if canonical == "self" else canonical
    if canon is not None:
        out.append('<link rel="canonical" href="%s">' % canon)
    if og:
        out.append('<meta property="og:title" content="Widget care">')
        out.append('<meta property="og:image" content="%s/assets/hero.png">' % BASE)
        out.append('<meta property="og:url" content="%s">' % (canon if canon and "://" in canon else url))
    out.append(head)
    out.append("</head><body>")
    out.append(body if body is not None else "<main><h1>%s</h1><p>%s</p><p><a href=\"/\">Home</a></p></main>"
               % (h1, PARA))
    out.append("</body></html>")
    return "\n".join(out)


def rel_for(path: str) -> str:
    return "index.html" if path == "/" else path.strip("/") + "/index.html"


def build(pages: Dict[str, str], extra: Optional[Dict[str, Any]] = None, *, base_url: Optional[str] = BASE,
          url_style: str = "directory", **kw: Any) -> sitescan.BuiltSite:
    """Scan a temporary build made from {url path: html} plus extra {rel path: content}."""
    files: Dict[str, Any] = {rel_for(p): html for p, html in pages.items()}
    files.update(extra or {})
    with helpers.temp_dir() as root:
        helpers.write_tree(root, files)
        return sitescan.scan_build(str(root), base_url=base_url, url_style=url_style, **kw)


def pages_rules(site: sitescan.BuiltSite, **kw: Any) -> List[Any]:
    kw.setdefault("today", TODAY)
    return sitescan.check_pages(site, **kw)


def ids(findings: List[Any]) -> List[str]:
    return helpers.rule_ids(findings)


def audit(site: sitescan.BuiltSite, *, expect_indexable: bool = True, profile: str = "default") -> List[Any]:
    """Every WP02 check composed the way audit-build composes them."""
    parsed = sitemaps.load_sitemaps(site.root, sitemaps.discover(site.root, site.robots_txt) + site.sitemap_paths) \
        if site.root else []
    listed = {u["loc"] for sm in parsed for u in sm["urls"] if u.get("loc")}
    out = sitescan.check_pages(site, expect_indexable=expect_indexable, profile=profile, today=TODAY,
                               sitemap_urls=listed)
    out += sitescan.check_duplicates(site)
    out += sitescan.check_links(site, sitescan.link_graph(site), sitemap_urls=listed)
    inputs = sitescan.sitemap_inputs(site)
    out += sitemaps.check_sitemaps(parsed, base_url=site.base_url, site_urls=inputs["site_urls"],
                                   indexable=inputs["indexable"], today=TODAY, profile=profile)
    hin = sitescan.hreflang_inputs(site)
    alternates = {u["loc"]: u["alternates"] for sm in parsed for u in sm["urls"] if u.get("alternates")}
    out += hreflang.check_hreflang(hin["pages"], canonical_of=hin["canonical_of"], noindex_of=hin["noindex_of"],
                                   sitemap_alternates=alternates)
    for key in sorted(site.pages):
        out += perf.check_static(site.pages[key], url=key, file=site.files.get(key))
    return sort_findings(dedupe(out))


# ----------------------------------------------------------------------------------------- PageDoc

class PageDocTests(unittest.TestCase):
    def test_title_inside_svg_or_body_is_ignored(self) -> None:
        doc = htmlparse.parse_html("<html><head><title> Real  title </title></head><body><svg><title>Icon</title>"
                                   "</svg><title>Body title</title></body></html>")
        self.assertEqual(doc.titles, ["Real title"])
        only_svg = htmlparse.parse_html("<html><head></head><body><svg><title>Icon</title></svg><p>x</p></body></html>")
        self.assertEqual(only_svg.titles, [])

    def test_rel_tokens_are_case_insensitive(self) -> None:
        doc = htmlparse.parse_html(
            '<head><link REL="Canonical" href="https://example.com/a/"><link rel="ALTERNATE" HREFLANG="de" '
            'href="https://example.com/de/"><link rel="Alternate" type="Text/Markdown" href="/a.md"></head>'
            '<body><a href="/x/" rel="NoFollow Ugc">x</a></body>')
        self.assertEqual(doc.canonicals, [("https://example.com/a/", 1)])
        self.assertEqual([(c, h) for c, h, _ in doc.hreflang], [("de", "https://example.com/de/")])
        self.assertEqual(doc.alternates[0]["type"], "text/markdown")
        self.assertTrue(doc.links[0]["nofollow"])
        self.assertEqual(doc.links[0]["rel"], ["nofollow", "ugc"])

    def test_canonical_and_hreflang_in_body_are_ignored(self) -> None:
        doc = htmlparse.parse_html('<head><title>t</title></head><body><p>text</p><link rel="canonical" href="/x/">'
                                   '<link rel="alternate" hreflang="fr" href="/fr/"></body>')
        self.assertEqual(doc.canonicals, [])
        self.assertEqual(doc.hreflang, [])
        self.assertEqual(len(doc.link_tags), 2)

    def test_alt_absent_is_none_and_empty_is_empty_string(self) -> None:
        doc = htmlparse.parse_html('<body><img src="a.png"><img src="b.png" alt=""><img src="c.png" alt="A cloth">'
                                   '</body>')
        self.assertEqual([i["alt"] for i in doc.images], [None, "", "A cloth"])

    def test_meta_keys_are_lower_cased_and_refresh_recorded(self) -> None:
        doc = htmlparse.parse_html('<head><meta NAME="Description" content="One"><meta name="description" '
                                   'content="Two"><meta property="OG:Title" content="T"><meta http-equiv="Refresh" '
                                   'content="0; url=/new/"><meta charset="utf-8"></head>')
        self.assertEqual(doc.meta["description"], ["One", "Two"])
        self.assertEqual(doc.meta["og:title"], ["T"])
        self.assertEqual(doc.meta_refresh, "0; url=/new/")
        self.assertEqual(doc.meta["charset"], ["utf-8"])

    def test_jsonld_type_is_trimmed_and_lower_cased(self) -> None:
        doc = htmlparse.parse_html('<head>\n<script type=" Application/LD+JSON ">{"@type": "Thing"}</script>\n'
                                   '<script type="application/json">{"@type": "Ignored"}</script></head>')
        self.assertEqual(doc.jsonld, [{"raw": '{"@type": "Thing"}', "line": 2}])
        self.assertEqual(len(doc.scripts), 1)

    def test_jsonld_types_walker(self) -> None:
        blocks = [{"raw": '{"@context": "https://schema.org", "@graph": [{"@type": "Organization"}, '
                          '{"@type": ["WebSite", "https://schema.org/Thing"]}]}'},
                  {"raw": '[{"@type": " Article "}, {"nested": {"@type": "Person"}}]'},
                  {"raw": '{"@type": "Broken",}'}]
        self.assertEqual(htmlparse.jsonld_types(blocks),
                         ["<invalid-json-ld>", "Article", "Organization", "Person", "Thing", "WebSite"])
        deep = {"raw": "[" * 300 + "]" * 300}
        self.assertEqual(htmlparse.jsonld_types([deep]), ["<invalid-json-ld>"])

    def test_scripts_and_inline_cap(self) -> None:
        doc = htmlparse.parse_html('<head><script src="/a.js" async></script><script type="module" src="/m.js">'
                                   '</script></head><body><script>%s</script></body>' % ("x" * 25000))
        head_a, head_m, inline = doc.scripts
        self.assertTrue(head_a["async"] and head_a["in_head"] and not head_a["defer"])
        self.assertTrue(head_m["module"])
        self.assertFalse(inline["in_head"])
        self.assertEqual(len(inline["inline_text"]), 20000)
        self.assertEqual(inline["length"], 25000)

    def test_main_text_visible_text_and_word_counts(self) -> None:
        doc = htmlparse.parse_html("<body><nav>Menu items</nav><main><h1>Title</h1><p>Main words here</p></main>"
                                   "<footer>Footer text</footer><script>var hidden = 1;</script></body>")
        self.assertEqual(doc.main_text, "Title Main words here")
        self.assertIn("Menu items", doc.visible_text)
        self.assertNotIn("hidden", doc.visible_text)
        self.assertEqual(doc.word_count, 4)
        no_main = htmlparse.parse_html("<body><header>Head</header><p>Body text</p><aside>Side</aside></body>")
        self.assertEqual(no_main.main_text, "Body text")
        self.assertEqual(htmlparse.count_words("ウィジェット care"), 7)

    def test_headings_ignore_noscript_and_template(self) -> None:
        doc = htmlparse.parse_html("<body><h1>One</h1>\n<noscript><h2>No</h2></noscript><template><h3>T</h3>"
                                   "</template>\n<h2>Two <span>parts</span></h2></body>")
        self.assertEqual(doc.headings, [(1, "One", 1), (2, "Two parts", 3)])

    def test_app_root_noscript_and_widget_counts(self) -> None:
        doc = htmlparse.parse_html('<body><div id="root"><p>Loading...</p></div><noscript>Enable JavaScript to use '
                                   'this.</noscript><div onclick="x()">Go</div><input id="q"><label for="q">Q</label>'
                                   '<input id="r"><input aria-label="named"></body>')
        self.assertEqual(doc.app_root_text_len, 10)
        self.assertEqual(doc.noscript_text_len, len("Enable JavaScript to use this."))
        self.assertEqual(doc.onclick_divs, 1)
        self.assertEqual(doc.unlabeled_inputs, 1)

    def test_microdata_and_rdfa_flags(self) -> None:
        self.assertTrue(htmlparse.parse_html('<div itemscope itemtype="https://schema.org/Thing"></div>').has_microdata)
        self.assertTrue(htmlparse.parse_html('<div vocab="https://schema.org/" typeof="Thing"></div>').has_rdfa)
        plain = htmlparse.parse_html('<meta property="og:title" content="x"><p>x</p>')
        self.assertFalse(plain.has_microdata or plain.has_rdfa)

    def test_extract_links(self) -> None:
        html = ('<head><base href="https://example.com/docs/"></head><body><a href="a/#x">A</a><a href="/b/">B</a>'
                '<a href="a/">dup</a><a href="#top">frag</a><a href="mailto:x@example.com">m</a>'
                '<a href="javascript:void(0)">j</a><a href="https://example.org/c">C</a><a>none</a></body>')
        self.assertEqual(htmlparse.extract_links(html, "https://example.com/start/"),
                         ["https://example.com/docs/a/", "https://example.com/b/", "https://example.org/c"])

    def test_images_viewport_guess_and_lazy_kinds(self) -> None:
        doc = htmlparse.parse_html('<body><img src="/logo.png" alt="logo" width="80" height="40">'
                                   '<img src="/hero.jpg" alt="hero" loading="lazy" width="1200" height="600">'
                                   '<img data-src="/b.jpg" class="lazyload" alt="b"></body>')
        logo, hero, lazy = doc.images
        self.assertFalse(logo["in_first_viewport_guess"])
        self.assertTrue(hero["in_first_viewport_guess"])
        self.assertEqual((hero["lazy"], lazy["lazy"]), ("native", "js"))

    def test_seeded_random_markup_never_raises(self) -> None:
        rng = helpers.seeded_random()
        parts = ["<", ">", "</", "/>", "<!--", "-->", "<![CDATA[", "]]>", "<!DOCTYPE", "<?xml", "&", "&amp;", "&#x110000;",
                 '"', "'", "=", " ", "\n", "<script>", "</script>", "<title>", "<svg>", "<div id=root>", "<a href=",
                 "<img alt", "<h1>", "</h2>", "<noscript>", "<template>", "<p>", "<li>", "<table>", "x", "\u202e", "#",
                 "```", "~~~", "---", "+++", "[a](", ")", "!["]
        for _ in range(200):
            text = "".join(rng.choice(parts) for _ in range(rng.randint(0, 60)))
            doc = htmlparse.parse_html(text)
            self.assertIsInstance(doc.visible_text, str)
            self.assertIsInstance(htmlparse.parse_markdown(text, path="x.mdx").word_count, int)

    def test_malformed_markup_never_raises(self) -> None:
        doc = htmlparse.parse_html("<html><head><title>Open<body><p>Unclosed <div><a href='/x'>x</b></html><<<>>")
        self.assertIsInstance(doc, htmlparse.PageDoc)
        self.assertEqual(htmlparse.parse_html("").titles, [])


# ----------------------------------------------------------------------------------------- Markdown

class MarkdownTests(unittest.TestCase):
    def test_yaml_frontmatter_scalars(self) -> None:
        doc = htmlparse.parse_markdown('---\ntitle: "FM title"\ndescription: Short desc\ncanonical_url: '
                                       'https://example.com/a/\nlang: de\nnoindex: true\ntags: [a, b]\n---\n# H1\n',
                                       path="a.md")
        self.assertEqual(doc.titles, ["FM title"])
        self.assertEqual(doc.meta["description"], ["Short desc"])
        self.assertEqual(doc.meta["robots"], ["noindex"])
        self.assertEqual(doc.canonicals, [("https://example.com/a/", 4)])
        self.assertEqual((doc.lang, doc.kind), ("de", "markdown"))

    def test_toml_frontmatter_and_h1_title_fallback(self) -> None:
        doc = htmlparse.parse_markdown('+++\ntitle = "Toml title"\n+++\nBody\n')
        self.assertEqual(doc.titles, ["Toml title"])
        self.assertEqual(htmlparse.parse_markdown("Intro\n\n# First heading\n").titles, ["First heading"])
        self.assertEqual(htmlparse.parse_markdown("---\ntitle: x\nno closing fence\n").titles, [])

    def test_backtick_and_tilde_fences_with_longer_closers(self) -> None:
        md = ("# One\n````\n# not a heading\n```\nstill code\n````\n## Two\n~~~\n# no\n```\n~~~~\n"
              "#hashtag is not a heading\n### Three\n")
        doc = htmlparse.parse_markdown(md)
        self.assertEqual([(lvl, t) for lvl, t, _ in doc.headings], [(1, "One"), (2, "Two"), (3, "Three")])
        self.assertNotIn("still code", doc.visible_text)
        self.assertIn("#hashtag is not a heading", doc.visible_text)

    def test_unclosed_fence_hides_the_rest(self) -> None:
        doc = htmlparse.parse_markdown("# Kept\n~~~python\n# hidden\ntext\n")
        self.assertEqual([t for _, t, _ in doc.headings], ["Kept"])
        self.assertNotIn("hidden", doc.visible_text)

    def test_backtick_info_string_with_backtick_is_not_a_fence(self) -> None:
        doc = htmlparse.parse_markdown("``` a`b\n# Visible\n")
        self.assertEqual([t for _, t, _ in doc.headings], ["Visible"])

    def test_links_images_and_mdx_lines(self) -> None:
        md = ('import Chart from "./Chart"\n<Chart data={x} />\n# Title\nSee [the guide](/guide/ "Guide") and '
              '<https://example.org/x>.\n![A cloth](/cloth.png)\nexport const meta = {}\n')
        doc = htmlparse.parse_markdown(md, path="post.mdx")
        self.assertEqual([l["href"] for l in doc.links], ["/guide/", "https://example.org/x"])
        self.assertEqual([(i["src"], i["alt"]) for i in doc.images], [("/cloth.png", "A cloth")])
        self.assertNotIn("import", doc.visible_text)
        self.assertNotIn("Chart", doc.visible_text)


# ----------------------------------------------------------------------------------------- directives

class DirectivesTests(unittest.TestCase):
    def test_parameter_values_bind_before_tokens(self) -> None:
        parsed = directives.parse_robots_values(["max-image-preview: none"])
        self.assertEqual(parsed["tokens"], set())
        self.assertEqual(parsed["params"], {"max-image-preview": "none"})
        self.assertFalse(parsed["noindex"] or parsed["nofollow"])
        none = directives.parse_robots_values(["NONE"])
        self.assertTrue(none["noindex"] and none["nofollow"])

    def test_max_snippet_zero_means_nosnippet(self) -> None:
        self.assertTrue(directives.parse_robots_values(["max-snippet:0"])["nosnippet"])
        self.assertFalse(directives.parse_robots_values(["max-snippet: -1"])["nosnippet"])
        self.assertEqual(directives.parse_robots_values(["max-snippet: 30"])["max_snippet"], 30)

    def test_unavailable_after_dates_with_commas(self) -> None:
        for value, year in (("unavailable_after: Wednesday, 01-Jan-25 00:00:00 GMT, noindex", 2025),
                            ("unavailable_after: Wed, 01 Jan 2025 00:00:00 GMT", 2025),
                            ("unavailable_after: 2027-01-01T10:00:00+02:00, nofollow", 2027)):
            parsed = directives.parse_robots_values([value])
            self.assertEqual(directives.parse_date(parsed["unavailable_after"]).year, year, value)
        self.assertIn("noindex", directives.parse_robots_values(
            ["unavailable_after: Wednesday, 01-Jan-25 00:00:00 GMT, noindex"])["tokens"])
        self.assertIsNone(directives.parse_date("next tuesday"))

    def test_parse_date_forms_match_on_every_python(self) -> None:
        cases = {"2025-01-01": "2025-01-01T00:00:00+00:00", "2025-01-01T10:00:00+0200": "2025-01-01T10:00:00+02:00",
                 "2025-01-01 10:00:00.5Z": "2025-01-01T10:00:00+00:00", "2025-01-01T10:00-05:00": "2025-01-01T10:00:00-05:00",
                 "25 Jun 2010 15:00:00 PST": "2010-06-25T15:00:00-08:00"}
        for value, iso in cases.items():
            self.assertEqual(directives.parse_date(value).isoformat(), iso, value)
        for value in ("2025-02-30", "2025-01-01T25:00", "2025-01-01T10:00:00+2400", "", "garbage", "2025-01-01 PST"):
            self.assertIsNone(directives.parse_date(value), value)

    def test_most_restrictive_value_wins_and_conflicts_are_reported(self) -> None:
        parsed = directives.parse_robots_values(["max-snippet: 50", "max-snippet: 20, max-image-preview: large",
                                                 "max-image-preview: none"])
        self.assertEqual(parsed["params"], {"max-snippet": "20", "max-image-preview": "none"})
        self.assertEqual(parsed["conflicts"], ["max-image-preview: large vs none", "max-snippet: 50 vs 20"])
        both = directives.parse_robots_values(["index, follow", "noindex"])
        self.assertTrue(both["noindex"])
        self.assertIn("index vs noindex", both["conflicts"])

    def test_x_robots_agent_prefixes(self) -> None:
        groups = directives.parse_x_robots(["googlebot: noindex, bingbot: nofollow\nmax-snippet: 20", "noarchive"])
        self.assertEqual(sorted(groups), ["*", "bingbot", "googlebot"])
        self.assertTrue(groups["googlebot"]["noindex"])
        self.assertEqual(groups["*"]["params"], {"max-snippet": "20"})
        self.assertIn("noarchive", groups["*"]["tokens"])
        self.assertTrue(directives.effective({}, groups, "googlebot")["noindex"])
        bing = directives.effective({}, groups, "bingbot")
        self.assertFalse(bing["noindex"])
        self.assertTrue(bing["nofollow"])

    def test_effective_combines_meta_and_header_sources(self) -> None:
        meta = {"robots": ["max-snippet: 50"], "googlebot": ["max-snippet: 20"], "bingbot": ["noindex"]}
        eff = directives.effective(meta, directives.parse_x_robots(["noindex"]), "googlebot")
        self.assertEqual(eff["params"]["max-snippet"], "20")
        self.assertEqual(eff["sources"], ["meta:robots", "meta:googlebot", "header:*"])
        self.assertEqual(eff["noindex_sources"], ["header:*"])
        self.assertTrue(eff["header_noindex"])
        self.assertFalse(directives.effective({"bingbot": ["noindex"]}, None, "googlebot")["noindex"])
        self.assertEqual(directives.effective({"robots": ["noarchive, nocache"]})["ignored"], ["noarchive", "nocache"])

    def test_bing_ai_preferences(self) -> None:
        meta = {"bingbot": ["ai-training: disallow"], "robots": ["ai-grounding: disallow"]}
        header = directives.parse_x_robots(["bingbot: ai-grounding: disallowextended"])
        self.assertEqual(directives.bing_ai(meta, header), {"ai-training": "disallow",
                                                            "ai-grounding": "disallowextended"})
        self.assertEqual(directives.bing_ai({"bingbot": ["ai-training: allow"]}, {}),
                         {"ai-training": None, "ai-grounding": None})


# ----------------------------------------------------------------------------------------- URL mapping

class UrlMappingTests(unittest.TestCase):
    def test_styles(self) -> None:
        cases = {
            "directory": {"index.html": "/", "x/index.html": "/x/", "x.html": "/x.html", "a/b.htm": "/a/b.htm"},
            "clean": {"index.html": "/", "x/index.html": "/x", "x.html": "/x", "a/b.htm": "/a/b"},
            "preserve": {"index.html": "/index.html", "x/index.html": "/x/index.html", "x.html": "/x.html"},
        }
        for style, mapping in cases.items():
            for rel, path in mapping.items():
                self.assertEqual(sitescan.url_for(rel, None, style), path, (style, rel))
                self.assertEqual(sitescan.url_for(rel, BASE + "/", style), BASE + path, (style, rel))
        self.assertEqual(sitescan.url_for("my page/ü.html", BASE, "directory"), BASE + "/my%20page/%C3%BC.html")
        with self.assertRaises(ValueError):
            sitescan.url_for("x.html", None, "pretty")

    def test_base_url_validation(self) -> None:
        for bad in ("example.com", "ftp://example.com", "https://user@example.com", "https://example.com/?q=1"):
            with helpers.temp_dir() as root, self.assertRaises(ValueError):
                sitescan.scan_build(str(root), base_url=bad)

    def test_normalize_url_is_shared_across_modules(self) -> None:
        samples = ["HTTPS://Example.COM:443/a%7Eb/?q=1#frag", "http://example.com:80", "/rel/path/", "https://[::1]:8080/x",
                   "https://example.com/caf%C3%A9/", "https://example.com/a b"]
        for url in samples:
            n = sitescan.normalize_url(url)
            self.assertEqual(n, sitemaps.normalize_url(url))
            self.assertEqual(n, hreflang.normalize_url(url))
        self.assertEqual(sitescan.normalize_url("HTTPS://Example.COM:443/a%7Eb/?q=1#frag"), "https://example.com/a~b/?q=1")
        self.assertTrue(sitescan.same_ignoring_slash("https://example.com/a", "https://EXAMPLE.com/a/"))
        self.assertFalse(sitescan.same_ignoring_slash("https://example.com/a", "https://example.com/b/"))

    def test_launch_host_heuristic_is_shared(self) -> None:
        hosts = {"localhost": "local host", "app.local": "local host", "127.0.0.1": "local or private address",
                 "10.1.2.3": "local or private address", "my-site.vercel.app": "preview host",
                 "staging.example.com": "staging host", "example-preview.example.com": "staging host",
                 "review.example.com": None,
                 "dev-01.example.com": "staging host", "www.example.com": None, "example.com": None,
                 "devices.example.com": None}
        for host, expected in hosts.items():
            self.assertEqual(sitescan.launch_host_problem(host, "example.com"), expected, host)
            self.assertEqual(sitemaps.launch_host_problem(host, "example.com"), expected, host)
        self.assertIsNone(sitescan.launch_host_problem("my-site.vercel.app", "other.vercel.app"))


# ----------------------------------------------------------------------------------------- traversal

class TraversalTests(unittest.TestCase):
    def test_reads_pages_and_host_files_and_skips_hidden_dirs(self) -> None:
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {
                "index.html": page("/"), "a/index.html": page("/a/"), "404.html": page("/404.html"),
                ".git/HEAD.html": "<html></html>", "node_modules/pkg/index.html": "<html></html>",
                ".env": "SECRET_TOKEN=do-not-read", "robots.txt": "User-agent: *\nAllow: /\n",
                "llms.txt": "# Site\n", "sitemap.xml": "<urlset/>", "sitemap-news.xml.gz": b"\x1f\x8b",
                "_headers": "/a/*\n  X-Robots-Tag: noindex\n", "_redirects": "/old/ /a/ 301\n",
                "vercel.json": json.dumps({"redirects": [{"source": "/v-old", "destination": "/a/"}]}),
                "assets/app.js": "1;"})
            opened: List[str] = []
            real_open = os.open

            def spy(path: Any, *args: Any, **kwargs: Any) -> int:
                opened.append(str(path))
                return real_open(path, *args, **kwargs)

            with mock.patch.object(os, "open", spy):
                site = sitescan.scan_build(str(root), base_url=BASE)
        self.assertEqual(sorted(site.pages), [BASE + "/", BASE + "/a/"])
        self.assertEqual(site.not_found_page, "404.html")
        self.assertIsNotNone(site.not_found_doc)
        self.assertEqual(site.robots_txt, "User-agent: *\nAllow: /\n")
        self.assertEqual(site.llms_txt, "# Site\n")
        self.assertEqual(site.sitemap_paths, ["sitemap-news.xml.gz", "sitemap.xml"])
        self.assertEqual(site.headers[BASE + "/a/"], {"x-robots-tag": "noindex"})
        self.assertEqual([r["from"] for r in site.redirects], ["/old/", "/v-old"])
        self.assertEqual(site.redirects[1]["status"], 308)
        self.assertEqual(sorted(site.config_files), ["_headers", "_redirects", "vercel.json"])
        self.assertIn("/assets/app.js", site.assets)
        self.assertFalse(any(".env" in p or ".git" in p or "node_modules" in p for p in opened), opened)
        self.assertNotIn("/.env", site.assets)
        self.assertEqual(site.skipped, [])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlinks_are_skipped_and_reported(self) -> None:
        with helpers.temp_dir() as outside, helpers.temp_dir() as root:
            helpers.write_tree(outside, {"secret.html": "<title>outside</title>", "dir/index.html": "<p>x</p>"})
            helpers.write_tree(root, {"index.html": page("/")})
            os.symlink(str(outside / "secret.html"), str(root / "linked.html"))
            os.symlink(str(outside / "dir"), str(root / "linked-dir"))
            site = sitescan.scan_build(str(root), base_url=BASE)
            self.assertEqual(sorted(site.pages), [BASE + "/"])
            self.assertEqual(sorted((s["path"], s["reason"]) for s in site.skipped),
                             [("linked-dir", "symlink"), ("linked.html", "symlink")])
            os.symlink(str(root), str(outside / "root-link"))
            with self.assertRaises(ValueError):
                sitescan.scan_build(str(outside / "root-link"))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "mkfifo unavailable")
    def test_special_files_are_never_opened(self) -> None:
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {"index.html": page("/")})
            os.mkfifo(str(root / "pipe.html"))
            site = sitescan.scan_build(str(root), base_url=BASE)
        self.assertEqual(site.skipped, [{"path": "pipe.html", "reason": "special file"}])

    def test_oversized_file_is_reported_not_read(self) -> None:
        big = "<html><body>" + "x" * (5 * 1024 * 1024) + "</body></html>"
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {"index.html": page("/"), "huge/index.html": big})
            site = sitescan.scan_build(str(root), base_url=BASE)
        self.assertEqual(list(site.pages), [BASE + "/"])
        self.assertEqual(site.skipped[0]["path"], "huge/index.html")
        self.assertEqual(site.skipped[0]["reason"], "too_large")
        found = helpers.findings_for(pages_rules(site), "HTTP005")
        self.assertEqual([f.file for f in found], ["huge/index.html"])
        small_cap = build({"/": page("/"), "/mid/": page("/mid/", body="<p>%s</p>" % ("y" * 3000))},
                          max_file_bytes=2000)
        self.assertEqual([(s["path"], s["reason"]) for s in small_cap.skipped], [("mid/index.html", "too_large")])
        self.assertEqual(helpers.findings_for(pages_rules(small_cap), "HTTP005"), [])

    def test_max_pages_and_url_collisions(self) -> None:
        site = build({"/": page("/"), "/a/": page("/a/"), "/b/": page("/b/")}, max_pages=2)
        self.assertEqual(len(site.pages), 2)
        self.assertIn("max_pages 2 reached; 1 pages not scanned", site.skipped[-1]["reason"])
        clean = build({}, {"x.html": page("/x"), "x/index.html": page("/x")}, url_style="clean")
        self.assertEqual(list(clean.pages), [BASE + "/x"])
        self.assertTrue(clean.skipped[0]["reason"].startswith("url collision"))

    def test_errors_for_bad_roots(self) -> None:
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {"file.txt": "x"})
            with self.assertRaises(NotADirectoryError):
                sitescan.scan_build(str(root / "file.txt"))
            with self.assertRaises(ValueError):
                sitescan.scan_build(str(root), url_style="pretty")

    def test_charset_decoding(self) -> None:
        latin = '<html><head><meta charset="iso-8859-1"><title>Caf\xe9</title></head></html>'.encode("latin-1")
        self.assertIn("Café", sitescan.decode_html(latin))
        self.assertEqual(sitescan.decode_html(b"\xef\xbb\xbf<p>x</p>"), "<p>x</p>")
        self.assertEqual(sitescan.decode_html(b'<meta charset="no-such-codec"><p>\xff</p>'),
                         '<meta charset="no-such-codec"><p>�</p>')

    def test_host_config_parsers(self) -> None:
        rules = sitescan.parse_headers_file("# comment\n/docs/*\n  X-Robots-Tag: noindex\n  ! X-Old\n/x\n  Link: <a>\n")
        self.assertEqual([(r["pattern"], r["headers"], r["source"]) for r in rules],
                         [("/docs/*", [("x-robots-tag", "noindex")], "_headers:2"), ("/x", [("link", "<a>")], "_headers:5")])
        reds, rws = sitescan.parse_redirects_file("/a /b\n/c /d 302!\n/* /index.html 200\n# x\n/e /f 404\n")
        self.assertEqual([(r["from"], r["status"], r["force"]) for r in reds], [("/a", 301, False), ("/c", 302, True)])
        self.assertEqual([r["source"] for r in rws], ["_redirects:3"])


# ----------------------------------------------------------------------------------------- page rules

class IndexingRuleTests(unittest.TestCase):
    def test_idx001_severity_depends_on_expect_indexable(self) -> None:
        site = build({"/": page("/"), "/n/": page("/n/", head='<meta name="robots" content="noindex">')})
        default = helpers.findings_for(pages_rules(site), "IDX001")
        strict = helpers.findings_for(pages_rules(site, expect_indexable=True), "IDX001")
        self.assertEqual([(f.severity, f.file) for f in default], [("warning", "n/index.html")])
        self.assertEqual([f.severity for f in strict], ["error"])
        self.assertNotIn("CANON001", ids(pages_rules(build({"/n/": page("/n/", canonical=None,
                         head='<meta name="robots" content="noindex">')}))))

    def test_idx002_idx003_conflicts_and_ignored_directives(self) -> None:
        site = build({"/c/": page("/c/", head='<meta name="robots" content="noindex"><meta name="googlebot" '
                                             'content="index, noarchive, nositelinkssearchbox">'),
                      "/ok/": page("/ok/", head='<meta name="robots" content="index, follow">')})
        found = pages_rules(site)
        self.assertEqual([f.file for f in helpers.findings_for(found, "IDX002")], ["c/index.html"])
        self.assertEqual(helpers.findings_for(found, "IDX003")[0].evidence["observed"],
                         ["noarchive", "nositelinkssearchbox"])

    def test_idx004_header_config_noindex(self) -> None:
        site = build({"/": page("/"), "/private/": page("/private/")}, {"_headers": "/private/*\n  X-Robots-Tag: noindex\n"})
        found = pages_rules(site)
        self.assertEqual([f.file for f in helpers.findings_for(found, "IDX004")], ["private/index.html"])
        self.assertEqual(helpers.findings_for(found, "IDX001")[0].evidence["observed"], ["header:*"])
        vercel = build({"/": page("/")}, {"vercel.json": json.dumps({"headers": [{"source": "/(.*)", "headers": [
            {"key": "X-Robots-Tag", "value": "googlebot: noindex"}]}]})})
        self.assertIn("IDX004", ids(pages_rules(vercel)))
        bing_only = build({"/": page("/")}, {"_headers": "/*\n  X-Robots-Tag: bingbot: noindex\n"})
        self.assertNotIn("IDX001", ids(pages_rules(bing_only)))

    def test_idx005_unavailable_after_boundary(self) -> None:
        def run(value: str) -> List[str]:
            return ids(pages_rules(build({"/": page("/", head='<meta name="robots" content="unavailable_after: %s">'
                                                          % value)})))
        self.assertIn("IDX005", run("2026-10-31"))
        self.assertNotIn("IDX005", run("2026-11-01"))
        self.assertNotIn("IDX005", run("2027-01-01"))


class CanonicalRuleTests(unittest.TestCase):
    def test_canon001_missing_and_header_canonical(self) -> None:
        self.assertIn("CANON001", ids(pages_rules(build({"/": page("/", canonical=None)}))))
        header = build({"/": page("/", canonical=None)}, {"_headers": '/\n  Link: <https://example.com/>; rel="canonical"\n'})
        self.assertNotIn("CANON001", ids(pages_rules(header)))
        both = build({"/": page("/")}, {"_headers": '/\n  Link: <https://example.com/>; rel="canonical"\n'})
        self.assertEqual(helpers.findings_for(pages_rules(both), "CANON002")[0].evidence["observed"],
                         [BASE + "/", BASE + "/"])

    def test_canon002_multiple(self) -> None:
        site = build({"/": page("/", head='<link rel="canonical" href="https://example.com/other/">')})
        self.assertEqual(len(helpers.findings_for(pages_rules(site), "CANON002")), 1)

    def test_canon003_invalid_forms(self) -> None:
        for href, reason in (("/rel/", "is relative"), ("https://example.com/x/#top", "contains a fragment"),
                             ("https://user:pw@example.com/", "contains credentials"),
                             ("ftp://example.com/", "is not an absolute http(s) URL"), ("", "is empty"),
                             ("https://example.com/a b", "contains spaces or control characters"),
                             ("https://example.com:99999/", "is malformed")):
            found = helpers.findings_for(pages_rules(build({"/": page("/", canonical=href)})), "CANON003")
            self.assertEqual(len(found), 1, href)
            self.assertIn(reason, found[0].message, href)
        self.assertEqual(helpers.findings_for(pages_rules(build({"/": page("/")})), "CANON003"), [])

    def test_canon004_target_state_and_canon005(self) -> None:
        site = build({"/": page("/"), "/a/": page("/a/", canonical=BASE + "/missing/"),
                      "/b/": page("/b/", canonical=BASE + "/n/"),
                      "/n/": page("/n/", head='<meta name="robots" content="noindex">'),
                      "/c/": page("/c/", canonical=BASE + "/old/"), "/d/": page("/d/", canonical=BASE + "/"),
                      "/e/": page("/e/", canonical=BASE + "/"), "/f/": page("/f/", canonical=BASE + "/file.pdf"),
                      "/g/": page("/g/", canonical="https://example.org/syndicated/")},
                     {"_redirects": "/old/ /a/ 301\n", "file.pdf": b"%PDF"})
        found = sitescan.check_duplicates(site)
        reasons = {f.file: f.evidence["reason"] for f in helpers.findings_for(found, "CANON004")}
        self.assertEqual(reasons, {"a/index.html": "missing from the site", "b/index.html": "noindex",
                                   "c/index.html": "redirects"})
        other = {f.file: f.evidence["pages_sharing_target"] for f in helpers.findings_for(found, "CANON005")}
        self.assertEqual(other, {"d/index.html": 2, "e/index.html": 2, "f/index.html": 1, "g/index.html": 1})

    def test_canon006_pagination_and_canon008_trailing_slash(self) -> None:
        site = build({"/blog/": page("/blog/"), "/blog/page/2/": page("/blog/page/2/", canonical=BASE + "/blog/"),
                      "/blog/page/1/": page("/blog/page/1/", canonical=BASE + "/blog/"),
                      "/x/": page("/x/", canonical=BASE + "/x")})
        found = pages_rules(site)
        self.assertEqual([f.file for f in helpers.findings_for(found, "CANON006")], ["blog/page/2/index.html"])
        self.assertEqual([f.file for f in helpers.findings_for(found, "CANON008")], ["x/index.html"])
        dup = sitescan.check_duplicates(site)
        self.assertEqual([f.file for f in helpers.findings_for(dup, "CANON005")], ["blog/page/1/index.html"])


class MetadataRuleTests(unittest.TestCase):
    def rules_for(self, **kw: Any) -> List[str]:
        return ids(pages_rules(build({"/": page("/", **kw)})))

    def test_clean_page_has_no_findings(self) -> None:
        self.assertEqual(pages_rules(build({"/": page("/")}), expect_indexable=True), [])

    def test_meta001_meta007_titles(self) -> None:
        self.assertIn("META001", self.rules_for(title=False))
        self.assertIn("META001", self.rules_for(title="   "))
        self.assertIn("META007", self.rules_for(head="<title>Second</title>"))

    def test_meta002_placeholder_titles(self) -> None:
        for title in ("Create Next App", "Vite + React", "Home", "{{ page.title }}", "%PAGE_TITLE%", "Untitled"):
            self.assertIn("META002", self.rules_for(title=title), title)
        self.assertNotIn("META002", self.rules_for(title="Home care routines for widgets"))

    def test_meta004_meta008_meta009_meta010_meta013(self) -> None:
        self.assertIn("META004", self.rules_for(description=False))
        self.assertIn("META004", self.rules_for(description=" "))
        self.assertIn("META008", self.rules_for(lang=None))
        self.assertIn("META009", self.rules_for(viewport=False))
        self.assertIn("META009", self.rules_for(viewport=False, head='<meta name="viewport" content="width=1024">'))
        self.assertNotIn("META009", self.rules_for(viewport=False, head='<meta name="viewport" content="initial-scale=1">'))
        self.assertIn("META010", self.rules_for(og=False))
        self.assertIn("META013", self.rules_for(head='<meta name="keywords" content="widgets">'))

    def test_meta011_title_length_boundary(self) -> None:
        self.assertNotIn("META011", self.rules_for(title="t" * 60))
        found = helpers.findings_for(pages_rules(build({"/": page("/", title="t" * 61)})), "META011")
        self.assertEqual((found[0].severity, found[0].confidence), ("info", "low"))

    def test_thresholds_come_from_the_data_file(self) -> None:
        limits = json.loads((helpers.DATA_DIR / "thresholds.json").read_text(encoding="utf-8"))
        limits["title_hint_chars"] = 10
        with mock.patch.object(sitescan, "thresholds", return_value=limits):
            self.assertIn("META011", self.rules_for(title="t" * 11))
        self.assertNotIn("META011", self.rules_for(title="t" * 11))

    def test_meta012_obsolete_year_window(self) -> None:
        self.assertIn("META012", self.rules_for(title="Best widgets 2025"))
        self.assertIn("META012", self.rules_for(h1="Widget guide 2021"))
        for title in ("Best widgets 2026", "Widgets 2020 archive", "Since 2021, widgets", "2024 vs 2026 widgets",
                      "Widget model 12021"):
            self.assertNotIn("META012", self.rules_for(title=title), title)

    def test_meta014_og_url(self) -> None:
        self.assertIn("META014", self.rules_for(head='<meta property="og:url" content="https://example.com/other/">',
                                                og=False))
        self.assertNotIn("META014", self.rules_for(head='<meta property="og:url" content="https://example.com">',
                                                   og=False))

    def test_noindex_and_refresh_pages_skip_search_facing_rules(self) -> None:
        noindex = self.rules_for(title=False, description=False, og=False, canonical=None,
                                 head='<meta name="robots" content="noindex">')
        self.assertEqual(noindex, ["IDX001"])
        refresh = self.rules_for(title=False, head='<meta http-equiv="refresh" content="0; url=/new/">')
        self.assertEqual(refresh, ["SPAM002"])
        timed = self.rules_for(head='<meta http-equiv="refresh" content="300">')
        self.assertEqual(timed, [])


class HeadingRuleTests(unittest.TestCase):
    def test_hdg001_hdg002(self) -> None:
        found = ids(pages_rules(build({"/": page("/", body="<h2>Sub</h2><h4>Deep</h4><p>%s</p>" % PARA)})))
        self.assertIn("HDG001", found)
        self.assertIn("HDG002", found)
        self.assertNotIn("HDG002", ids(pages_rules(build({"/": page("/", body="<h1>a</h1><h2>b</h2><h2>c</h2><h3>d"
                                                                            "</h3><h2>e</h2>")}))))

    def test_hdg003_word_boundary(self) -> None:
        def run(words: int) -> List[str]:
            return ids(pages_rules(build({"/": page("/", body="<p>%s</p>" % " ".join(["word"] * words))})))
        self.assertIn("HDG003", run(300))
        self.assertNotIn("HDG003", run(299))


class RenderingRuleTests(unittest.TestCase):
    def run_body(self, body: str, head: str = "") -> List[Any]:
        return pages_rules(build({"/": page("/", body=body, head=head)}))

    def test_wordpress_like_app_root_with_content_is_not_csr(self) -> None:
        body = '<div id="app"><main><h1>Widgets</h1><p>%s</p></main></div><script src="/a.js"></script>' % PARA
        self.assertNotIn("REND001", ids(self.run_body(body)))

    def test_empty_root_is_csr(self) -> None:
        found = helpers.findings_for(self.run_body('<div id="root"></div><script type="module" src="/a.js"></script>'),
                                     "REND001")
        self.assertEqual(found[0].evidence["root_text_chars"], 0)

    def test_loading_root_is_csr(self) -> None:
        self.assertIn("REND001", ids(self.run_body('<div id="__next"><p>Loading...</p></div>')))

    def test_decompose_order_nested_script_and_style_do_not_count(self) -> None:
        body = ('<div id="root"><script>var t="%s";</script><style>.a{color:red}/*%s*/</style></div>'
                % ("x" * 400, "y" * 400))
        self.assertIn("REND001", ids(self.run_body(body)))
        with_text = ('<div id="root"><script>var t=1;</script><style>.a{}</style><h1>Widgets</h1><p>%s</p></div>'
                     % PARA)
        self.assertNotIn("REND001", ids(self.run_body(with_text)))

    def test_root_text_and_page_word_boundaries(self) -> None:
        self.assertIn("REND001", ids(self.run_body('<div id="root">%s</div>' % ("a" * 50))))
        self.assertNotIn("REND001", ids(self.run_body('<div id="root">%s</div>' % ("a" * 51))))
        many = '<div id="root"></div><main><h1>x</h1><p>%s</p></main>' % " ".join(["word"] * 200)
        self.assertNotIn("REND001", ids(self.run_body(many)))

    def test_no_root_thin_text_with_scripts(self) -> None:
        found = helpers.findings_for(self.run_body("<p>Hi</p>", head='<script src="/bundle.js" defer></script>'),
                                     "REND001")
        self.assertEqual(found[0].confidence, "medium")
        self.assertNotIn("REND001", ids(self.run_body("<p>Hi</p>")))

    def test_rend002_inline_script_boundary(self) -> None:
        visible = len(htmlparse.parse_html(page("/", body="<h1>Dash</h1><p>Rows appear below.</p>")).visible_text)
        size = max(2000, 5 * visible)

        def run(n: int) -> List[str]:
            return ids(self.run_body("<h1>Dash</h1><p>Rows appear below.</p><script>%s</script>" % ("x" * n)))
        self.assertIn("REND002", run(size))
        self.assertNotIn("REND002", run(size - 1))

    def test_rend003_noscript_boundary(self) -> None:
        def run(n: int) -> List[str]:
            return ids(self.run_body("<noscript>%s</noscript><p>Hi</p>" % ("n" * n)))
        self.assertIn("REND003", run(200))
        self.assertNotIn("REND003", run(199))

    def test_rend004_hash_routes(self) -> None:
        found = helpers.findings_for(self.run_body('<h1>x</h1><a href="#/settings">S</a><a href="#!/a">A</a>'
                                                   '<a href="#top">Top</a>'), "REND004")
        self.assertEqual(found[0].evidence["observed"], ["#/settings", "#!/a"])

    def test_rend005_spa_fallbacks(self) -> None:
        for extra, source in (({"200.html": "<div id=root></div>"}, "200.html"),
                              ({"_redirects": "/*  /index.html  200\n"}, "_redirects:1"),
                              ({"vercel.json": json.dumps({"rewrites": [{"source": "/(.*)",
                                                                         "destination": "/index.html"}]})},
                               "vercel.json:rewrites[0]")):
            site = build({"/": page("/")}, extra)
            self.assertEqual(site.spa_fallback, source)
            self.assertIn("REND005", ids(pages_rules(site)))
        narrow = build({"/": page("/")}, {"_redirects": "/app/*  /app/index.html  200\n"})
        self.assertIsNone(narrow.spa_fallback)


class ImageLinkSpamRuleTests(unittest.TestCase):
    def run_body(self, body: str, head: str = "", **kw: Any) -> List[Any]:
        return pages_rules(build({"/": page("/", body="<h1>x</h1><p>%s</p>%s" % (PARA, body), head=head)}, **kw))

    def test_img001_missing_alt_skips_decorative(self) -> None:
        found = helpers.findings_for(self.run_body('<img src="/a.png"><img src="/b.png" alt=""><img src="/c.png" '
                                                   'role="presentation"><img src="/d.png" aria-hidden="true">'), "IMG001")
        self.assertEqual(found[0].evidence["observed"], ["/a.png"])

    def test_img002_filename_and_keyword_list_alts(self) -> None:
        for alt in ("IMG_1234.jpg", "dsc 0042", "widget-red-large-cheap", "widget, cloth, shelf, care, cheap"):
            self.assertIn("IMG002", ids(self.run_body('<img src="/a.png" alt="%s">' % alt)), alt)
        for alt in ("A widget on a shelf", "Red, blue, green, white and black widgets in a row."):
            self.assertNotIn("IMG002", ids(self.run_body('<img src="/a.png" alt="%s">' % alt)), alt)

    def test_link004_non_crawlable_links(self) -> None:
        found = helpers.findings_for(self.run_body('<a href="javascript:void(0)">m</a><a onclick="go()">g</a>'
                                                   '<a href="#" onclick="x()">h</a><a href="#top">t</a><a name="n">n</a>'
                                                   '<span role="link">s</span>'), "LINK004")
        self.assertEqual(found[0].evidence["count"], 3)

    def test_spam001_history_manipulation(self) -> None:
        trap = "<script>history.pushState({}, '', location.href); window.onpopstate = function () {};</script>"
        load = "<script>document.addEventListener('DOMContentLoaded', function(){history.pushState({}, '', '/x');});</script>"
        bare = "<script>history.pushState({}, '', '/x');</script>"
        click = ("<script>document.querySelector('a').addEventListener('click', function(){history.pushState({}, '', "
                 "'/x');});</script>")
        for body in (trap, load, bare):
            self.assertIn("SPAM001", ids(self.run_body(body)), body)
        self.assertNotIn("SPAM001", ids(self.run_body(click)))
        self.assertNotIn("SPAM001", ids(self.run_body('<script src="/router.js"></script>')))

    def test_local002_retired_business_profile_features(self) -> None:
        self.assertIn("LOCAL002", ids(self.run_body('<a href="https://widgets.business.site/">old site</a>')))
        self.assertIn("LOCAL002", ids(self.run_body("<p>Chat with us on Google any time.</p>")))
        self.assertNotIn("LOCAL002", ids(self.run_body('<a href="https://example.org/business/">business</a>')))

    def test_agent005_markdown_alternate(self) -> None:
        head = '<link rel="alternate" type="text/markdown" href="/index.md">'
        self.assertIn("AGENT005", ids(self.run_body("", head=head)))
        self.assertNotIn("AGENT005", ids(pages_rules(build({"/": page("/", head=head)}, {"index.md": "# x\n"}))))
        self.assertNotIn("AGENT005", ids(self.run_body("", head='<link rel="alternate" type="text/markdown" '
                                                                 'href="https://docs.example.org/x.md">')))
        self.assertIn("AGENT005", ids(self.run_body("", head='<link rel="alternate" href="/notes.md">')))

    def test_http005_html_size_boundary(self) -> None:
        limit = 2097152
        for size, expected in ((limit, False), (limit + 1, True)):
            html = page("/")
            html = html.replace("</body>", "<!--%s--></body>" % ("p" * (size - len(html.encode("utf-8")) - 7)))
            self.assertEqual(len(html.encode("utf-8")), size)
            found = ids(pages_rules(build({"/": html})))
            self.assertEqual("HTTP005" in found, expected, size)

    def test_http007_mixed_content(self) -> None:
        body = '<img src="http://cdn.example.net/a.png" alt="a" width="1" height="1"><script src="http://x.test/a.js">' \
               '</script>'
        found = helpers.findings_for(self.run_body(body), "HTTP007")
        self.assertEqual(found[0].evidence["observed"], ["http://cdn.example.net/a.png", "http://x.test/a.js"])
        plain = pages_rules(build({"/": page("/", body=body)}, base_url="http://example.com"))
        self.assertEqual([f.key for f in helpers.findings_for(plain, "HTTP007")], ["plain-http"])
        self.assertNotIn("HTTP007", ids(pages_rules(build({"/": page("/", body=body)}, base_url=None))))


class LaunchRuleTests(unittest.TestCase):
    def test_launch003_staging_urls(self) -> None:
        head = ('<meta property="og:url" content="https://staging.example.com/">'
                '<link rel="alternate" hreflang="en" href="http://localhost:3000/">'
                '<script type="application/ld+json">{"url": "https://my-site.vercel.app/"}</script>')
        found = helpers.findings_for(pages_rules(build({"/": page("/", og=False, head=head)})), "LAUNCH003")
        self.assertEqual(sorted(h["where"] for h in found[0].evidence["observed"]), ["hreflang", "json-ld", "og:url"])
        preview = build({"/": page("/", canonical="https://my-site.vercel.app/")}, base_url="https://my-site.vercel.app")
        self.assertNotIn("LAUNCH003", ids(pages_rules(preview)))

    def test_launch004_sitewide_blocks(self) -> None:
        robots = build({"/": page("/")}, {"robots.txt": "User-agent: *\nDisallow: /\n"})
        found = helpers.findings_for(pages_rules(robots), "LAUNCH004")
        self.assertEqual((found[0].file, found[0].severity), ("robots.txt", "error"))
        noindex = build({"/": page("/", head='<meta name="robots" content="noindex">'),
                         "/a/": page("/a/", head='<meta name="robots" content="none">')})
        self.assertIn("LAUNCH004", ids(pages_rules(noindex)))
        for robots_txt in ("User-agent: *\nDisallow: /admin/\n", "User-agent: Googlebot\nDisallow: /\n",
                           "User-agent: *\nDisallow: /\nAllow: /public/\n"):
            self.assertNotIn("LAUNCH004", ids(pages_rules(build({"/": page("/")}, {"robots.txt": robots_txt}))))
        single = build({"/": page("/", head='<meta name="robots" content="noindex">')})
        self.assertNotIn("LAUNCH004", ids(pages_rules(single)))

    def test_launch001_and_launch005_only_with_launch_profile(self) -> None:
        site = build({"/": page("/")})
        self.assertEqual(ids(pages_rules(site)), [])
        found = pages_rules(site, profile="launch")
        self.assertEqual(ids(found), ["LAUNCH001", "LAUNCH005"])
        self.assertEqual(helpers.findings_for(found, "LAUNCH001")[0].evidence["missing"], ["Organization/WebSite JSON-LD"])
        org = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization"}</script>'
        good = build({"/": page("/", head=org)}, {"404.html": page("/404.html", head='<meta name="robots" '
                                                                                 'content="noindex">')})
        self.assertEqual(pages_rules(good, profile="launch"), [])
        indexable_404 = build({"/": page("/", head=org)}, {"404.html": page("/404.html")})
        found = helpers.findings_for(pages_rules(indexable_404, profile="launch", sitemap_urls={BASE + "/404.html"}),
                                     "LAUNCH005")
        self.assertEqual(found[0].evidence["observed"], ["listed in the sitemap", "no noindex (indexable if the host "
                                                         "serves it with status 200)"])
        self.assertIn("LAUNCH001", ids(pages_rules(build({"/a/": page("/a/")}), profile="launch")))


class LiveFetchTests(unittest.TestCase):
    def records(self) -> List[Dict[str, Any]]:
        html = {"content-type": "text/html; charset=utf-8"}
        return [
            {"url": BASE + "/", "status": 200, "headers": html, "text": page("/")},
            {"url": BASE + "/gone/", "status": 404, "headers": html, "text": "<p>gone</p>"},
            {"url": BASE + "/blocked/", "status": 403, "headers": html, "text": "<p>no</p>"},
            {"url": BASE + "/final/", "requested_url": BASE + "/start/", "status": 200, "headers": html,
             "text": page("/final/"), "redirect_chain": [{"url": BASE + "/start/", "status": 301},
                                                         {"url": BASE + "/middle/", "status": 302}]},
            {"url": BASE + "/moved/", "status": 200, "headers": html, "text": page("/moved/"),
             "redirect_chain": [{"url": BASE + "/was/", "status": 301}]},
            {"url": "http://example.com/plain/", "status": 200, "headers": html, "text": page("/plain/")},
            {"url": BASE + "/robots.txt", "status": 200, "headers": {"Content-Type": "text/plain"},
             "text": "User-agent: *\nAllow: /\n"},
            {"url": BASE + "/llms.txt", "status": 404, "headers": {}, "text": "missing"},
            {"url": BASE + "/data.json", "status": 200, "headers": {"content-type": "application/json"}, "text": "{}"},
        ]

    def test_site_from_fetches(self) -> None:
        site = sitescan.site_from_fetches(self.records(), base_url=BASE)
        self.assertEqual(sorted(site.pages), ["http://example.com/plain/", BASE + "/", BASE + "/final/", BASE + "/moved/"])
        self.assertEqual(site.robots_txt, "User-agent: *\nAllow: /\n")
        self.assertIsNone(site.llms_txt)
        self.assertEqual(site.status[BASE + "/start/"], 301)
        self.assertEqual(site.redirects[0]["to"], BASE + "/final/")

    def test_http_rules_on_live_records(self) -> None:
        found = pages_rules(sitescan.site_from_fetches(self.records(), base_url=BASE))
        self.assertEqual([f.url for f in helpers.findings_for(found, "HTTP001")], [BASE + "/gone/"])
        self.assertEqual([f.url for f in helpers.findings_for(found, "HTTP008")], [BASE + "/blocked/"])
        self.assertEqual([f.url for f in helpers.findings_for(found, "HTTP002")], [BASE + "/start/"])
        self.assertEqual([f.url for f in helpers.findings_for(found, "HTTP003")], [BASE + "/start/"])
        plain = [f for f in helpers.findings_for(found, "HTTP007") if f.key == "plain-http"]
        self.assertEqual([f.url for f in plain], ["http://example.com/plain/"])
        self.assertNotIn("IDX004", ids(found))

    def test_unfollowed_redirect_uses_redirect_target(self) -> None:
        records = [{"url": BASE + "/out/", "status": 302, "headers": {}, "text": None,
                    "redirect_chain": [{"url": BASE + "/out/", "status": 302}],
                    "redirect_target": "https://example.org/landing/"}]
        site = sitescan.site_from_fetches(records, base_url=BASE)
        self.assertEqual(site.redirects[0]["to"], "https://example.org/landing/")
        self.assertEqual(ids(pages_rules(site)), ["HTTP003"])

    def test_live_crawl_does_not_call_unfetched_targets_broken(self) -> None:
        records = [{"url": BASE + "/", "status": 200, "headers": {"content-type": "text/html"},
                    "text": page("/", body='<h1>x</h1><p>%s</p><a href="/unfetched/">u</a><a href="/gone/">g</a>' % PARA)},
                   {"url": BASE + "/gone/", "status": 410, "headers": {}, "text": ""}]
        site = sitescan.site_from_fetches(records, base_url=BASE)
        graph = sitescan.link_graph(site)
        self.assertEqual([b["target"] for b in graph["broken"]], [BASE + "/gone/"])


# ----------------------------------------------------------------------------------------- duplicates

class DuplicateTests(unittest.TestCase):
    def test_duplicate_titles_and_descriptions(self) -> None:
        site = build({"/a/": page("/a/", title="Same", description="Same text."),
                      "/b/": page("/b/", title="same ", description="Same  text."),
                      "/c/": page("/c/", title="Same", head='<meta name="robots" content="noindex">'),
                      "/d/": page("/d/", title="Unique")})
        found = sitescan.check_duplicates(site)
        title = helpers.findings_for(found, "META003")
        self.assertEqual((title[0].affected, list(title[0].sample)), (2, [BASE + "/a/", BASE + "/b/"]))
        self.assertEqual(len(helpers.findings_for(found, "META005")), 1)

    def test_reciprocal_hreflang_pairs_in_different_languages_are_suppressed(self) -> None:
        alt = ('<link rel="alternate" hreflang="en" href="https://example.com/en/">'
               '<link rel="alternate" hreflang="de" href="https://example.com/de/">')
        site = build({"/en/": page("/en/", title="Widgets", head=alt),
                      "/de/": page("/de/", title="Widgets", head=alt, lang="de")})
        self.assertNotIn("META003", ids(sitescan.check_duplicates(site)))
        same_lang = ('<link rel="alternate" hreflang="en-GB" href="https://example.com/en/">'
                     '<link rel="alternate" hreflang="en-US" href="https://example.com/us/">')
        site = build({"/en/": page("/en/", title="Widgets", head=same_lang),
                      "/us/": page("/us/", title="Widgets", head=same_lang)})
        self.assertIn("META003", ids(sitescan.check_duplicates(site)))

    def test_paginated_and_canonicalized_pages_are_not_duplicates(self) -> None:
        site = build({"/blog/": page("/blog/", title="Blog"), "/blog/page/2/": page("/blog/page/2/", title="Blog"),
                      "/copy/": page("/copy/", title="Blog", canonical=BASE + "/blog/")})
        self.assertNotIn("META003", ids(sitescan.check_duplicates(site)))


# ----------------------------------------------------------------------------------------- link graph

class LinkGraphTests(unittest.TestCase):
    def site(self) -> sitescan.BuiltSite:
        def links(*hrefs: str) -> str:
            return "<main><h1>x</h1><p>%s</p>%s</main>" % (PARA, "".join('<a href="%s">Page %s</a>' % (h, h)
                                                                          for h in hrefs))
        return build({"/": page("/", body=links("/a/", "/b/", "/missing/", "/404.html", "/file.pdf", "/old/",
                                                "mailto:x@example.com", "https://example.org/")),
                      "/a/": page("/a/", body=links("/c/", "/")), "/b/": page("/b/", body=links("/a/")),
                      "/c/": page("/c/", body=links("/d/")), "/d/": page("/d/", body=links("/e/")),
                      "/e/": page("/e/", body=links("/")), "/orphan/": page("/orphan/")},
                     {"404.html": page("/404.html"), "file.pdf": b"%PDF", "_redirects": "/old/ /b/ 301\n"})

    def test_graph_depth_orphans_broken_redirected(self) -> None:
        graph = sitescan.link_graph(self.site())
        self.assertEqual(graph["home"], BASE + "/")
        depth = {k[len(BASE):]: v for k, v in graph["depth"].items()}
        self.assertEqual(depth, {"/": 0, "/a/": 1, "/b/": 1, "/c/": 2, "/d/": 3, "/e/": 4, "/orphan/": None})
        self.assertEqual(graph["orphans"], [BASE + "/orphan/"])
        self.assertEqual(sorted(b["href"] for b in graph["broken"]), ["/404.html", "/missing/"])
        self.assertEqual([r["href"] for r in graph["redirected"]], ["/old/"])
        self.assertEqual(graph["inlinks"][BASE + "/b/"], 1)
        self.assertEqual(graph["depth_histogram"]["unreachable"], 1)

    def test_link_rules(self) -> None:
        site = self.site()
        graph = sitescan.link_graph(site)
        found = sitescan.check_links(site, graph, sitemap_urls={BASE + "/orphan/", BASE + "/a/"})
        self.assertEqual(ids(found), ["LINK001", "LINK002", "LINK003", "LINK006"])
        self.assertEqual([f.url for f in helpers.findings_for(found, "LINK003")], [BASE + "/e/"])
        self.assertEqual([f.url for f in helpers.findings_for(found, "LINK002")], [BASE + "/orphan/"])
        self.assertNotIn("LINK002", ids(sitescan.check_links(site, graph)))

    def test_link005_generic_anchor_share_and_link007(self) -> None:
        def run(generic: int, total: int, nofollow: bool = False) -> List[str]:
            anchors = ['<a href="/p%d/">%s</a>' % (i, "read more" if i < generic else "Widget page %d" % i)
                       for i in range(total)]
            if nofollow:
                anchors.append('<a href="/p0/" rel="nofollow">Widget page zero</a>')
            pages = {"/": page("/", body="<h1>x</h1>%s" % "".join(anchors))}
            pages.update({"/p%d/" % i: page("/p%d/" % i, body="<main><h1>x</h1><p>%s</p></main>" % PARA)
                          for i in range(total)})
            site = build(pages)
            return ids(sitescan.check_links(site, sitescan.link_graph(site)))
        self.assertIn("LINK005", run(3, 10))
        self.assertNotIn("LINK005", run(2, 10))
        self.assertNotIn("LINK005", run(9, 9))
        self.assertIn("LINK007", run(0, 2, nofollow=True))


# ----------------------------------------------------------------------------------------- redirect maps

class RedirectMapTests(unittest.TestCase):
    F = ("redirects",)

    def builds(self) -> Any:
        old = sitescan.scan_build(str(helpers.fixture("redirects", "old-build")), base_url=BASE)
        new = sitescan.scan_build(str(helpers.fixture("redirects", "new-build")), base_url=BASE)
        return old, new

    def test_parse_redirect_map(self) -> None:
        entries = sitescan.parse_redirect_map(str(helpers.fixture("redirects", "map-bad.csv")))
        self.assertEqual(len(entries), 13)
        errors = {e["line"]: e["error"] for e in entries if e["error"]}
        self.assertEqual(sorted(errors), [12, 13, 14])
        self.assertIsNone(entries[0]["error"])
        self.assertEqual(entries[0]["status"], 301)
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {"m.csv": "﻿/a/,/b/\n#x,y\n\n/c/,/d/,\n".encode("utf-8")})
            plain = sitescan.parse_redirect_map(str(root / "m.csv"))
        self.assertEqual([(e["old"], e["new"], e["status"], e["error"]) for e in plain],
                         [("/a/", "/b/", None, None), ("/c/", "/d/", None, None)])

    def test_bad_map_triggers_every_redirect_rule(self) -> None:
        old, new = self.builds()
        found = sitescan.check_redirects(sitescan.parse_redirect_map(str(helpers.fixture("redirects", "map-bad.csv"))),
                                         old_site=old, new_site=new)
        self.assertEqual(ids(found), ["REDIR001", "REDIR002", "REDIR003", "REDIR004", "REDIR005", "REDIR006",
                                      "REDIR007"])
        self.assertEqual(len(helpers.findings_for(found, "REDIR007")), 4)
        self.assertEqual(sorted(f.url for f in helpers.findings_for(found, "REDIR006")), [BASE + "/c/", BASE + "/d/"])
        self.assertEqual(helpers.findings_for(found, "REDIR003")[0].url, "/b/")
        self.assertEqual(helpers.findings_for(found, "REDIR005")[0].affected, 3)

    def test_good_map_is_clean_and_builds_are_optional(self) -> None:
        old, new = self.builds()
        good = sitescan.parse_redirect_map(str(helpers.fixture("redirects", "map-good.csv")))
        self.assertEqual(sitescan.check_redirects(good, old_site=old, new_site=new), [])
        bad = sitescan.parse_redirect_map(str(helpers.fixture("redirects", "map-bad.csv")))
        self.assertEqual(ids(sitescan.check_redirects(bad)), ["REDIR001", "REDIR002", "REDIR004", "REDIR005",
                                                              "REDIR007"])

    def test_redir005_home_count_boundary(self) -> None:
        two = [{"line": i, "old": "/x%d/" % i, "new": "/", "status": 301, "error": None} for i in range(2)]
        self.assertEqual(sitescan.check_redirects(two), [])
        three = two + [{"line": 9, "old": "/x9/", "new": "https://example.com/", "status": 301, "error": None}]
        self.assertEqual(ids(sitescan.check_redirects(three)), ["REDIR005"])
        diluted = three + [{"line": 20 + i, "old": "/y%d/" % i, "new": "/z%d/" % i, "status": 301, "error": None}
                           for i in range(20)]
        self.assertEqual(sitescan.check_redirects(diluted), [])


# ----------------------------------------------------------------------------------------- records

class PageRecordTests(unittest.TestCase):
    def test_page_record_shape(self) -> None:
        html = page("/a/", head='<meta name="robots" content="max-snippet: 20, noarchive">'
                               '<link rel="alternate" hreflang="DE" href="/de/a/">',
                    body='<main><h1>Head</h1><h2>Sub</h2><p>%s</p><a href="/b/">b</a><a href="https://example.org/">o'
                         '</a><a href="#x">f</a></main>' % PARA)
        doc = htmlparse.parse_html(html, url=BASE + "/a/")
        rec = sitescan.page_record(BASE + "/a/", doc, status=200, headers={"X-Robots-Tag": "googlebot: noindex"})
        self.assertEqual(rec["canonical"], BASE + "/a/")
        self.assertEqual(rec["robots"], ["max-snippet:20", "noarchive"])
        self.assertEqual(rec["x_robots"], {"googlebot": ["noindex"]})
        self.assertEqual((rec["h1"], rec["h2"], rec["internal_links"]), ("Head", ["Sub"], 1))
        self.assertEqual(rec["hreflang"], [["de", BASE + "/de/a/"]])
        self.assertTrue(rec["noindex"])
        self.assertEqual(rec["og"]["og:url"], BASE + "/a/")
        again = sitescan.page_record(BASE + "/a/", htmlparse.parse_html(html, url=BASE + "/a/"))
        self.assertEqual(again["content_hash"], rec["content_hash"])
        self.assertIsNone(again["x_robots"])

    def test_build_time(self) -> None:
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {"index.html": page("/")})
            stamp = calendar.timegm((2026, 10, 31, 0, 0, 0))
            os.utime(str(root / "index.html"), (stamp, stamp))
            site = sitescan.scan_build(str(root), base_url=BASE)
            self.assertEqual(sitescan.build_time(site), "2026-10-31T00:00:00Z")
        self.assertIsNone(sitescan.build_time(sitescan.site_from_fetches([], base_url=BASE)))


# ----------------------------------------------------------------------------------------- fixtures

class SiteFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.expected = json.loads(helpers.read_fixture("site-bad", "EXPECTED_RULES.json"))
        cls.catalog = helpers.catalog()

    def scan(self, name: str) -> sitescan.BuiltSite:
        return sitescan.scan_build(str(helpers.fixture(name)), base_url=BASE)

    def test_site_good_has_no_errors_or_warnings(self) -> None:
        for profile in ("default", "launch"):
            found = audit(self.scan("site-good"), expect_indexable=True, profile=profile)
            serious = [(f.rule, f.file, f.message) for f in found if f.severity in ("error", "warning")]
            self.assertEqual(serious, [], profile)
        no_base = sitescan.scan_build(str(helpers.fixture("site-good")), base_url=None)
        self.assertEqual([f.rule for f in audit(no_base, profile="launch") if f.severity != "info"], [])

    def test_site_bad_emits_every_module_rule(self) -> None:
        opts = self.expected["options"]
        site = sitescan.scan_build(str(helpers.fixture("site-bad")), base_url=opts["base_url"],
                                   url_style=opts["url_style"])
        found = audit(site, expect_indexable=opts["expect_indexable"], profile=opts["profile"])
        missing = sorted(set(self.expected["module_rules"]) - set(ids(found)))
        self.assertEqual(missing, [])
        default = ids(audit(self.scan("site-bad"), expect_indexable=True))
        self.assertEqual(sorted(set(self.expected["launch_profile_only"]) & set(default)), [])
        self.assertTrue(all(f.file or f.url for f in found))

    def test_planned_rules_are_never_emitted(self) -> None:
        planned = {r.id for r in self.catalog.all() if r.status != "v1"}
        found = audit(self.scan("site-bad"), profile="launch")
        self.assertEqual(sorted(planned & set(ids(found))), [])

    def test_site_bad_output_is_deterministic(self) -> None:
        first = [(f.fingerprint(), f.severity, f.message) for f in audit(self.scan("site-bad"))]
        second = [(f.fingerprint(), f.severity, f.message) for f in audit(self.scan("site-bad"))]
        self.assertEqual(first, second)
        self.assertEqual(len({fp for fp, _, _ in first}), len(first))

    def test_expected_rules_contract(self) -> None:
        exp = self.expected
        wp02_v1 = {r.id for r in self.catalog.all() if r.owner in WP02_OWNERS and r.status == "v1"}
        for key in ("module_rules", "integration_rules", "launch_profile_only", "integration_possible"):
            values = exp[key]
            self.assertEqual(values, sorted(set(values)), key)
            for rid in values:
                self.assertIn(rid, self.catalog, rid)
                self.assertEqual(self.catalog.get(rid).status, "v1", rid)
        self.assertTrue(set(exp["module_rules"]) <= wp02_v1)
        self.assertTrue(set(exp["module_rules"]) <= set(exp["integration_rules"]))
        self.assertTrue(set(exp["launch_profile_only"]) <= set(exp["module_rules"]))
        self.assertFalse(set(exp["integration_possible"]) & set(exp["integration_rules"]))
        covered = set(exp["module_rules"]) | set(exp["module_fixture_rules"])
        self.assertEqual(sorted(wp02_v1 - covered), [])
        self.assertTrue(set(exp["module_fixture_rules"]) <= wp02_v1)

    def test_site_bad_carries_inputs_for_other_packages(self) -> None:
        robots = helpers.read_fixture("site-bad", "robots.txt")
        self.assertIn("User-agent: GPTBot", robots)
        self.assertIn("Content-Signal:", robots)
        self.assertIn("<lastmod>2030-01-01</lastmod>", helpers.read_fixture("site-bad", "sitemap.xml"))
        schema = helpers.read_fixture("site-bad", "schema", "index.html")
        self.assertIn("[REPLACE:", schema)
        self.assertIn("</script", schema.split('type="application/ld+json">', 1)[1].split("</script>\n", 1)[0])
        content = helpers.read_fixture("site-bad", "content", "index.html")
        self.assertIn("TODO:", content)
        self.assertTrue("​" in content and "‮" in content)
        self.assertFalse(helpers.read_fixture("site-bad", "llms.txt").lstrip().startswith("#"))
        self.assertTrue(helpers.read_fixture("site-good", "llms.txt").startswith("# "))

    def test_fixture_hosts_are_reserved_names(self) -> None:
        for name in ("site-good", "site-bad", "sitemaps", "redirects", "lighthouse"):
            for path in sorted(helpers.fixture(name).rglob("*")):
                if not path.is_file():
                    continue
                text = path.read_bytes().decode("utf-8", "replace")
                for host in re.findall(r"https?://(?:[^/@\s\"'<>]*@)?([A-Za-z0-9.-]+)", text):
                    host = host.lower().rstrip(".")
                    ok = (host in ("localhost", "127.0.0.1", "www.sitemaps.org", "www.google.com", "www.w3.org",
                                   "schema.org") or host.endswith(".test") or
                          any(host == d or host.endswith("." + d) for d in ("example.com", "example.org",
                                                                             "example.net")))
                    self.assertTrue(ok, "%s: %s" % (path, host))


if __name__ == "__main__":
    unittest.main()
