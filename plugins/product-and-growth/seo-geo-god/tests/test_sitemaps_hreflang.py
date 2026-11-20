"""WP02: sitemap parsing and checks (SMAP001-011), IndexNow payloads, hreflang codes and clusters
(HREF001-008, CANON007)."""
from __future__ import annotations

import os
import sys
import time
import unittest
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_sitemaps_hreflang
import helpers  # noqa: E402
from seo_geo_lib import hreflang, htmlparse, sitemaps, sitescan  # noqa: E402

BASE = "https://example.com"
TODAY = helpers.TODAY
NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
IMG_NS = 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'


def setUpModule() -> None:
    helpers.block_network()


def fixture_bytes(name: str) -> bytes:
    return helpers.read_fixture("sitemaps", name, binary=True)


def parse_fixture(name: str, **kw: Any) -> Dict[str, Any]:
    return sitemaps.parse_sitemap(fixture_bytes(name), source=name, **kw)


def urlset(entries: Sequence[str], extra_ns: str = "") -> bytes:
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset %s %s>%s</urlset>' % (NS, extra_ns, "".join(entries))
            ).encode("utf-8")


def url_entry(loc: str, lastmod: Optional[str] = None, inner: str = "") -> str:
    return "<url><loc>%s</loc>%s%s</url>" % (loc, "<lastmod>%s</lastmod>" % lastmod if lastmod else "", inner)


def check(parsed: List[Dict[str, Any]], **kw: Any) -> List[Any]:
    kw.setdefault("base_url", BASE)
    kw.setdefault("today", TODAY)
    return sitemaps.check_sitemaps(parsed, **kw)


def ids(findings: List[Any]) -> List[str]:
    return helpers.rule_ids(findings)


# ----------------------------------------------------------------------------------------- parsing

class ParseSitemapTests(unittest.TestCase):
    def test_urlset_with_images_and_alternates(self) -> None:
        sm = parse_fixture("urlset.xml")
        self.assertEqual((sm["kind"], sm["errors"], sm["notes"]), ("urlset", [], []))
        self.assertEqual([u["loc"] for u in sm["urls"]], [BASE + "/", BASE + "/de/", BASE + "/about/"])
        first = sm["urls"][0]
        self.assertEqual(first["images"], [BASE + "/assets/hero.png"])
        self.assertEqual(first["alternates"], [("en", BASE + "/"), ("de", BASE + "/de/")])
        self.assertEqual(sm["urls"][1]["lastmod"], "2026-10-21T08:15:00+02:00")

    def test_sitemap_index(self) -> None:
        sm = parse_fixture("index.xml")
        self.assertEqual(sm["kind"], "sitemapindex")
        self.assertEqual(sm["sitemaps"], [{"loc": BASE + "/urlset.xml", "lastmod": "2026-10-21"},
                                          {"loc": BASE + "/missing.xml", "lastmod": None}])

    def test_text_sitemaps(self) -> None:
        good = parse_fixture("text.txt")
        self.assertEqual((good["kind"], good["errors"]), ("text", []))
        self.assertEqual([u["loc"] for u in good["urls"]], [BASE + "/", BASE + "/about/", BASE + "/de/"])
        bad = parse_fixture("text-bad.txt")
        self.assertEqual(bad["kind"], "text")
        self.assertEqual(bad["errors"], ["line 2 is not an absolute http(s) URL", "line 3 is not an absolute http(s) URL"])
        only_bad = sitemaps.parse_sitemap(b"/a/\nnot a url\n", source="x.txt")
        self.assertEqual(only_bad["kind"], "invalid")

    def test_feed_is_accepted(self) -> None:
        sm = parse_fixture("feed.xml")
        self.assertEqual(sm["kind"], "feed")
        self.assertEqual([u["loc"] for u in sm["urls"]], [BASE + "/", BASE + "/blog/first-post/"])

    def test_doctype_and_entity_are_refused_before_parsing(self) -> None:
        for name in ("doctype.xml", "entity-lower.xml"):
            sm = parse_fixture(name)
            self.assertEqual((sm["kind"], sm["urls"]), ("invalid", []), name)
            self.assertEqual(sm["errors"], ["DOCTYPE or ENTITY declaration refused"], name)
        inline = sitemaps.parse_sitemap(b'<urlset %s><!ENTITY x "y"><url><loc>a</loc></url></urlset>'
                                        % NS.encode(), source="x.xml")
        self.assertEqual(inline["kind"], "invalid")

    def test_malformed_wrong_root_namespace_and_encoding(self) -> None:
        self.assertTrue(parse_fixture("malformed.xml")["errors"][0].startswith("XML parse error"))
        self.assertEqual(parse_fixture("wrong-root.xml")["errors"], ["unexpected root element <html>"])
        no_ns = parse_fixture("no-namespace.xml")
        self.assertEqual((no_ns["kind"], no_ns["notes"]), ("urlset", ["root element is not in the sitemaps.org namespace"]))
        self.assertEqual(parse_fixture("latin1.xml")["errors"], ["not UTF-8"])

    def test_gzip_is_decompressed_and_bounded(self) -> None:
        data = helpers.gzip_bytes(fixture_bytes("urlset.xml"))
        sm = sitemaps.parse_sitemap(data, source="sitemap.xml.gz")
        self.assertEqual((sm["kind"], len(sm["urls"])), ("urlset", 3))
        self.assertEqual(sm["size"], len(fixture_bytes("urlset.xml")))
        bomb = helpers.gzip_bytes(b"<" + b" " * (40 * 1024 * 1024))
        started = time.monotonic()
        capped = sitemaps.parse_sitemap(bomb, source="bomb.xml.gz", max_bytes=1024 * 1024)
        self.assertLess(time.monotonic() - started, 5.0)
        self.assertTrue(capped["too_large"])
        self.assertEqual(capped["size"], 1024 * 1024 + 1)
        self.assertEqual(capped["urls"], [])
        broken = sitemaps.parse_sitemap(b"\x1f\x8bnot gzip", source="x.gz")
        self.assertTrue(broken["errors"][0].startswith("gzip error"))

    def test_uncompressed_size_cap(self) -> None:
        sm = sitemaps.parse_sitemap(urlset([url_entry(BASE + "/")]), source="s.xml", max_bytes=50)
        self.assertTrue(sm["too_large"])
        self.assertEqual(sm["urls"], [])

    def test_image_removed_tags(self) -> None:
        entry = parse_fixture("images-removed.xml")["urls"][0]
        self.assertEqual(entry["images"], [BASE + "/a.png"])
        self.assertEqual(entry["image_removed_tags"], ["title", "license"])


class DiscoverAndLoadTests(unittest.TestCase):
    def test_discover_from_robots_and_common_names(self) -> None:
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {"sitemap.xml": "<urlset/>", "maps/posts.xml": "<urlset/>", "sitemap.txt": "x"})
            robots = ("User-agent: *\nSitemap: https://example.com/maps/posts.xml # posts\n"
                      "sitemap: https://cdn.example.net/remote.xml\nSitemap: /sitemap.xml\n")
            self.assertEqual(sitemaps.discover(str(root), robots),
                             ["maps/posts.xml", "sitemap.xml", "sitemap.txt", "https://cdn.example.net/remote.xml"])
            self.assertEqual(sitemaps.discover(str(root), None), ["sitemap.xml", "sitemap.txt"])
        self.assertEqual(sitemaps.discover("", "Sitemap: https://example.com/s.xml"), ["https://example.com/s.xml"])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_load_skips_symlinks_and_escapes(self) -> None:
        with helpers.temp_dir() as outside, helpers.temp_dir() as root:
            helpers.write_tree(outside, {"secret.xml": urlset([url_entry(BASE + "/secret/")]).decode()})
            helpers.write_tree(root, {"sitemap.xml": urlset([url_entry(BASE + "/")]).decode()})
            os.symlink(str(outside / "secret.xml"), str(root / "linked.xml"))
            self.assertEqual(sitemaps.discover(str(root), "Sitemap: https://example.com/linked.xml"),
                             ["sitemap.xml", "https://example.com/linked.xml"])
            loaded = sitemaps.load_sitemaps(str(root), ["sitemap.xml", "linked.xml", "../outside.xml", "sitemap.xml",
                                                        "https://example.com/linked.xml"])
        self.assertEqual([sm["source"] for sm in loaded], ["sitemap.xml"])

    def test_load_reports_oversized_and_unreadable(self) -> None:
        with helpers.temp_dir() as root:
            helpers.write_tree(root, {"big.xml": "x" * 200, "dir.xml/inner": "x"})
            loaded = sitemaps.load_sitemaps(str(root), ["big.xml", "dir.xml"], max_bytes=100)
        self.assertEqual([(sm["source"], sm["too_large"]) for sm in loaded], [("big.xml", True), ("dir.xml", False)])
        self.assertTrue(loaded[1]["errors"][0].startswith("unreadable"))


# ----------------------------------------------------------------------------------------- checks

class CheckSitemapTests(unittest.TestCase):
    def test_smap001_none_found_and_launch_escalation(self) -> None:
        found = check([])
        self.assertEqual([(f.rule, f.severity, f.url) for f in found], [("SMAP001", "info", BASE + "/")])
        self.assertEqual(check([], profile="launch")[0].severity, "warning")

    def test_smap002_url_count_boundary(self) -> None:
        def text_sitemap(n: int) -> Dict[str, Any]:
            body = "\n".join("%s/p/%d/" % (BASE, i) for i in range(n)).encode()
            return sitemaps.parse_sitemap(body, source="sitemap.txt")
        self.assertNotIn("SMAP002", ids(check([text_sitemap(50000)])))
        found = helpers.findings_for(check([text_sitemap(50001)]), "SMAP002")
        self.assertEqual(found[0].evidence["entries"], 50001)

    def test_smap002_size_limit_is_not_reported_as_invalid(self) -> None:
        big = sitemaps.parse_sitemap(urlset([url_entry(BASE + "/")]), source="s.xml", max_bytes=10)
        self.assertEqual(ids(check([big])), ["SMAP002"])

    def test_smap003_invalid_sitemaps(self) -> None:
        parsed = [parse_fixture(n) for n in ("doctype.xml", "malformed.xml", "wrong-root.xml", "latin1.xml")]
        found = helpers.findings_for(check(parsed), "SMAP003")
        self.assertEqual([f.file for f in found], ["doctype.xml", "latin1.xml", "malformed.xml", "wrong-root.xml"])
        self.assertNotIn("SMAP003", ids(check([parse_fixture("no-namespace.xml")])))

    def test_smap004_loc_problems(self) -> None:
        sm = sitemaps.parse_sitemap(urlset([url_entry("/relative/"), url_entry("https://example.org/x/"),
                                            url_entry("ftp://example.com/f"), url_entry("https://u@example.com/"),
                                            url_entry(BASE + "/ok/"), url_entry("https://WWW.example.com/")]),
                                    source="s.xml")
        found = helpers.findings_for(check([sm]), "SMAP004")
        self.assertEqual(found[0].affected, 5)
        no_base = helpers.findings_for(sitemaps.check_sitemaps([sm], base_url=None, today=TODAY), "SMAP004")
        self.assertEqual(no_base[0].affected, 3)

    def test_smap005_lastmod_formats(self) -> None:
        found = helpers.findings_for(check([parse_fixture("lastmod.xml")]), "SMAP005")
        self.assertEqual(found[0].evidence["observed"], ["2026/10/01", "2026-10-01T10:20:30", "01-10-2026", "2026-13-01"])
        valid = sitemaps.parse_sitemap(urlset([url_entry(BASE + "/a/", v) for v in (
            "2026", "2026-10", "2026-10-01", "2026-10-01T10:20Z", "2026-10-01T10:20:30.123456+05:30")]), source="v.xml")
        self.assertNotIn("SMAP005", ids(check([valid])))

    def test_smap006_uniform_future_and_build_time(self) -> None:
        self.assertIn("all 3 entries share one lastmod",
                      helpers.findings_for(check([parse_fixture("uniform.xml")]), "SMAP006")[0].evidence["observed"])
        two = sitemaps.parse_sitemap(urlset([url_entry(BASE + "/a/", "2026-10-01"), url_entry(BASE + "/b/", "2026-10-01")]),
                                     source="two.xml")
        self.assertNotIn("SMAP006", ids(check([two])))
        tomorrow = sitemaps.parse_sitemap(urlset([url_entry(BASE + "/a/", "2026-11-02"), url_entry(BASE + "/b/", "2026-09-01")]),
                                          source="t.xml")
        self.assertNotIn("SMAP006", ids(check([tomorrow])))
        future = sitemaps.parse_sitemap(urlset([url_entry(BASE + "/a/", "2026-11-03"), url_entry(BASE + "/b/", "2026-09-01")]),
                                        source="f.xml")
        self.assertEqual(helpers.findings_for(check([future]), "SMAP006")[0].evidence["observed"],
                         ["1 lastmod values are in the future"])
        built = sitemaps.parse_sitemap(urlset([url_entry(BASE + "/a/", "2026-10-30T12:00:00Z"),
                                               url_entry(BASE + "/b/", "2026-10-30T12:00:30Z"),
                                               url_entry(BASE + "/c/", "2026-05-01")]), source="b.xml")
        reasons = helpers.findings_for(check([built], build_time="2026-10-30T12:00:10Z"), "SMAP006")[0]
        self.assertEqual(reasons.evidence["observed"], ["2 lastmod values equal the build time"])
        self.assertNotIn("SMAP006", ids(check([built], build_time="2026-10-29T00:00:00Z")))

    def test_smap007_priority_and_changefreq(self) -> None:
        found = helpers.findings_for(check([parse_fixture("uniform.xml")]), "SMAP007")
        self.assertEqual(found[0].evidence["entries"], 2)
        self.assertNotIn("SMAP007", ids(check([parse_fixture("urlset.xml")])))

    def test_smap010_removed_tags_and_image_count_boundary(self) -> None:
        found = helpers.findings_for(check([parse_fixture("images-removed.xml")]), "SMAP010")
        self.assertEqual(found[0].evidence["removed_tags"], ["license", "title"])

        def images(n: int) -> Dict[str, Any]:
            inner = "".join("<image:image><image:loc>%s/i/%d.png</image:loc></image:image>" % (BASE, i) for i in range(n))
            return sitemaps.parse_sitemap(urlset([url_entry(BASE + "/g/", inner=inner)], IMG_NS), source="g.xml")
        self.assertNotIn("SMAP010", ids(check([images(1000)])))
        self.assertIn("SMAP010", ids(check([images(1001)])))

    def test_smap011_index_child_missing(self) -> None:
        parsed = [parse_fixture("index.xml"), dict(parse_fixture("urlset.xml"), source="urlset.xml")]
        found = helpers.findings_for(check(parsed), "SMAP011")
        self.assertEqual([f.evidence["observed"] for f in found], [BASE + "/missing.xml"])

    def test_launch003_for_staging_locs(self) -> None:
        sm = sitemaps.parse_sitemap(urlset([url_entry("http://localhost:3000/"), url_entry("https://staging.example.com/"),
                                            url_entry(BASE + "/")]), source="s.xml")
        found = helpers.findings_for(check([sm]), "LAUNCH003")
        self.assertEqual(found[0].affected, 2)
        self.assertNotIn("SMAP004", ids(check([sm])))

    def test_smap008_and_smap009_parity_with_the_build(self) -> None:
        reasons = {BASE + "/noindex/": "noindex", BASE + "/old/": "redirects",
                   BASE + "/copy/": "canonicalized to https://example.com/", BASE + "/gone/": "missing"}

        def indexable(url: str) -> Union[bool, str]:
            return reasons.get(url, True)
        site_urls = {BASE + "/", BASE + "/unlisted/", BASE + "/noindex/", BASE + "/copy/", BASE + "/slash"}
        sm = sitemaps.parse_sitemap(urlset([url_entry(u) for u in (BASE + "/", BASE + "/noindex/", BASE + "/old/",
                                                                    BASE + "/copy/", BASE + "/gone/", BASE + "/slash/")]),
                                    source="s.xml")
        found = check([sm], site_urls=site_urls, indexable=indexable)
        parity = {f.evidence["reason"]: f.affected for f in helpers.findings_for(found, "SMAP008")}
        self.assertEqual(parity, {"canonicalized": 1, "missing": 1, "noindex": 1, "redirects": 2})
        unlisted = helpers.findings_for(found, "SMAP009")
        self.assertEqual(list(unlisted[0].sample), [BASE + "/unlisted/"])
        clean = check([sm], site_urls={BASE + "/"}, indexable=lambda u: True)
        self.assertNotIn("SMAP009", ids(clean))

    def test_parity_with_a_real_build(self) -> None:
        def page(path: str, head: str = "") -> str:
            return ('<html lang="en"><head><title>%s</title><link rel="canonical" href="%s%s">%s</head><body><h1>x</h1>'
                    '</body></html>' % (path, BASE, path, head))
        files = {"index.html": page("/"), "a/index.html": page("/a/"),
                 "n/index.html": page("/n/", '<meta name="robots" content="noindex">'),
                 "c/index.html": '<html><head><link rel="canonical" href="%s/a/"></head></html>' % BASE,
                 "_redirects": "/old/ /a/ 301\n",
                 "sitemap.xml": urlset([url_entry(BASE + p) for p in ("/", "/n/", "/c/", "/old/", "/gone/")]).decode()}
        with helpers.temp_dir() as root:
            helpers.write_tree(root, files)
            site = sitescan.scan_build(str(root), base_url=BASE)
            parsed = sitemaps.load_sitemaps(site.root, site.sitemap_paths)
        inputs = sitescan.sitemap_inputs(site)
        self.assertEqual(inputs["indexable"](BASE + "/"), True)
        self.assertEqual(inputs["indexable"](BASE + "/c/"), "canonicalized to %s/a/" % BASE)
        self.assertEqual(inputs["indexable"]("/n/"), "noindex")
        found = check(parsed, **inputs)
        parity = {f.evidence["reason"] for f in helpers.findings_for(found, "SMAP008")}
        self.assertEqual(parity, {"canonicalized", "missing", "noindex", "redirects"})
        self.assertEqual(list(helpers.findings_for(found, "SMAP009")[0].sample), [BASE + "/a/"])

    def test_site_bad_sitemaps(self) -> None:
        root = str(helpers.fixture("site-bad"))
        site = sitescan.scan_build(root, base_url=BASE)
        paths = sitemaps.discover(root, site.robots_txt) + site.sitemap_paths
        parsed = sitemaps.load_sitemaps(root, paths)
        self.assertEqual([p["source"] for p in parsed], ["sitemap-broken.xml", "sitemap.xml", "sitemap_index.xml"])
        found = ids(check(parsed, **sitescan.sitemap_inputs(site)))
        for rule in ("SMAP003", "SMAP004", "SMAP005", "SMAP006", "SMAP007", "SMAP008", "SMAP009", "SMAP010", "SMAP011",
                     "LAUNCH003"):
            self.assertIn(rule, found)

    def test_site_good_sitemap_is_clean(self) -> None:
        root = str(helpers.fixture("site-good"))
        site = sitescan.scan_build(root, base_url=BASE)
        parsed = sitemaps.load_sitemaps(root, sitemaps.discover(root, site.robots_txt) + site.sitemap_paths)
        self.assertEqual(check(parsed, **sitescan.sitemap_inputs(site)), [])


# ----------------------------------------------------------------------------------------- IndexNow

class IndexNowTests(unittest.TestCase):
    KEY = "a1b2c3d4e5f6"

    def test_valid_payload(self) -> None:
        payload = sitemaps.indexnow_payload([BASE + "/a/", BASE + "/b/", BASE + "/a/", " "], host="Example.com",
                                            key=self.KEY, key_location=BASE + "/%s.txt" % self.KEY)
        self.assertEqual(payload, {"host": "example.com", "key": self.KEY, "keyLocation": BASE + "/%s.txt" % self.KEY,
                                   "urlList": [BASE + "/a/", BASE + "/b/"]})
        self.assertNotIn("keyLocation", sitemaps.indexnow_payload([BASE + "/"], host="example.com", key=self.KEY,
                                                                  key_location=None))

    def test_rejections(self) -> None:
        cases = [
            dict(urls=[BASE + "/"], host="example.com", key="short", key_location=None),
            dict(urls=[BASE + "/"], host="example.com", key="bad_key_with_underscore", key_location=None),
            dict(urls=[BASE + "/"], host="example.com", key="k" * 129, key_location=None),
            dict(urls=["https://example.org/"], host="example.com", key=self.KEY, key_location=None),
            dict(urls=[BASE + "/"], host="example.com/path", key=self.KEY, key_location=None),
            dict(urls=[BASE + "/"], host="example.com", key=self.KEY, key_location="https://example.org/k.txt"),
            dict(urls=[BASE + "/"], host="example.com", key=self.KEY, key_location=BASE + "/key.json"),
            dict(urls=[BASE + "/a/"], host="example.com", key=self.KEY, key_location=BASE + "/b/key.txt"),
            dict(urls=[], host="example.com", key=self.KEY, key_location=None),
            dict(urls=["ftp://example.com/"], host="example.com", key=self.KEY, key_location=None),
        ]
        for case in cases:
            urls = case.pop("urls")
            with self.assertRaises(ValueError, msg=repr(case)):
                sitemaps.indexnow_payload(urls, **case)

    def test_url_limit_boundary(self) -> None:
        urls = ["%s/p/%d/" % (BASE, i) for i in range(10001)]
        self.assertEqual(len(sitemaps.indexnow_payload(urls[:10000], host="example.com", key=self.KEY,
                                                       key_location=None)["urlList"]), 10000)
        with self.assertRaises(ValueError):
            sitemaps.indexnow_payload(urls, host="example.com", key=self.KEY, key_location=None)


# ----------------------------------------------------------------------------------------- hreflang

def hpage(url: str, alts: Sequence[Tuple[str, str]], lang: Optional[str] = "en", head: str = "") -> htmlparse.PageDoc:
    links = "".join('<link rel="alternate" hreflang="%s" href="%s">' % (c, h) for c, h in alts)
    lang_attr = ' lang="%s"' % lang if lang else ""
    return htmlparse.parse_html("<html%s><head>%s%s</head><body><p>x</p></body></html>" % (lang_attr, links, head),
                                path=url.split("://", 1)[1].split("/", 1)[1] + "index.html", url=url)


EN, DE, FR, XD = BASE + "/en/", BASE + "/de/", BASE + "/fr/", BASE + "/"
FULL = [("en", EN), ("de", DE), ("x-default", XD)]


def run(pages: Dict[str, Any], **kw: Any) -> List[Any]:
    return hreflang.check_hreflang(pages, **kw)


class HreflangCodeTests(unittest.TestCase):
    def test_valid_codes(self) -> None:
        for code in ("en", "en-GB", "zh-Hant", "zh-Hans-US", "x-default", "X-Default", "pt-br", "DE-at", "eu", "uk"):
            self.assertIsNone(hreflang.code_problem(code), code)

    def test_invalid_codes(self) -> None:
        cases = {"en-UK": "use GB", "es-419": "numeric region", "EU": "reserved", "UN": "reserved",
                 "en_US": "hyphen", "GB": "region, not a language", "UK": "uk means Ukrainian", "eng": "two-letter",
                 "xx": "not an ISO 639-1", "en-XX": "alpha-2", "en-GB-x": "too many", "": "empty", "e1": "two-letter",
                 "en-USA": "alpha-2"}
        for code, fragment in cases.items():
            problem = hreflang.code_problem(code)
            self.assertIsNotNone(problem, code)
            self.assertIn(fragment, problem, code)


class HreflangClusterTests(unittest.TestCase):
    def test_reciprocal_cluster_is_clean(self) -> None:
        pages = {EN: hpage(EN, FULL), DE: hpage(DE, FULL, lang="de"), XD: hpage(XD, FULL)}
        self.assertEqual(run(pages, canonical_of=lambda u: u, noindex_of=lambda u: False), [])
        cluster = hreflang.clusters(pages)
        self.assertEqual(len(cluster), 1)
        self.assertEqual(cluster[0]["pages"], [XD, DE, EN])
        self.assertEqual(cluster[0]["x_default"], XD)
        self.assertEqual(cluster[0]["matrix"][EN]["de"], DE)

    def test_one_way_link_is_href003(self) -> None:
        pages = {EN: hpage(EN, FULL), DE: hpage(DE, [("de", DE), ("x-default", XD)], lang="de")}
        found = run(pages)
        self.assertEqual([(f.rule, f.url) for f in found if f.rule == "HREF003"], [("HREF003", EN)])

    def test_return_link_with_a_different_code_is_href003(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("de", DE)]), DE: hpage(DE, [("de", DE), ("fr", EN)], lang="de")}
        found = helpers.findings_for(run(pages), "HREF003")
        self.assertEqual([f.url for f in found], [EN])
        self.assertTrue(found[0].key.startswith("return-code:"))
        self.assertEqual((found[0].evidence["observed"], found[0].evidence["expected"]), (["fr"], "en"))

    def test_missing_self_reference_is_href002(self) -> None:
        pages = {EN: hpage(EN, [("de", DE)]), DE: hpage(DE, [("de", DE), ("en", EN)], lang="de")}
        found = run(pages)
        self.assertEqual([f.url for f in helpers.findings_for(found, "HREF002")], [EN])
        self.assertEqual(helpers.findings_for(found, "HREF003"), [])

    def test_relative_url_is_href005(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("de", "/de/")]), DE: hpage(DE, [("de", DE), ("en", EN)], lang="de")}
        found = run(pages)
        self.assertEqual([f.evidence["observed"] for f in helpers.findings_for(found, "HREF005")], ["/de/"])
        self.assertEqual(helpers.findings_for(found, "HREF003"), [])

    def test_target_noindex_noncanonical_and_missing_is_href006(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("de", DE), ("fr", FR), ("es", BASE + "/es/"), ("it", "https://example.org/it/")]),
                 DE: hpage(DE, [("de", DE), ("en", EN)], lang="de"), FR: hpage(FR, [("fr", FR), ("en", EN)], lang="fr")}
        found = run(pages, noindex_of=lambda u: u == DE, canonical_of=lambda u: EN if u == FR else u)
        reasons = sorted(f.evidence["reason"] for f in helpers.findings_for(found, "HREF006") if f.url == EN)
        self.assertEqual(reasons, ["canonicalized to %s" % EN, "missing", "noindex"])
        self.assertEqual(ids(run(pages)), ["HREF004", "HREF006"])

    def test_duplicate_code_is_href007(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("de", DE), ("DE", BASE + "/de-alt/"), ("de", DE)])}
        found = helpers.findings_for(run(pages), "HREF007")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].evidence["observed"], [DE, BASE + "/de-alt/"])

    def test_html_lang_mismatch_is_href008(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("de", DE)]), DE: hpage(DE, [("de", DE), ("en", EN)], lang="fr")}
        self.assertEqual([f.url for f in helpers.findings_for(run(pages), "HREF008")], [DE])
        regional = {EN: hpage(EN, [("en-GB", EN)], lang="en-US")}
        self.assertEqual(helpers.findings_for(run(regional), "HREF008"), [])

    def test_invalid_code_is_href001_and_not_used_for_clusters(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("en-UK", BASE + "/uk/"), ("es-419", BASE + "/la/")])}
        found = run(pages)
        self.assertEqual(sorted(f.evidence["observed"] for f in helpers.findings_for(found, "HREF001")), ["en-UK", "es-419"])
        self.assertEqual(ids(found), ["HREF001", "HREF004"])

    def test_x_default_reported_once_per_cluster(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("de", DE)]), DE: hpage(DE, [("de", DE), ("en", EN)], lang="de"),
                 FR: hpage(FR, [("fr", FR)], lang="fr")}
        found = helpers.findings_for(run(pages), "HREF004")
        self.assertEqual([(f.url, f.affected) for f in found], [(DE, 2), (FR, 1)])

    def test_canon007_cross_language_canonical(self) -> None:
        pages = {EN: hpage(EN, [("en", EN), ("de", DE)]), DE: hpage(DE, [("de", DE), ("en", EN)], lang="de")}
        found = run(pages, canonical_of=lambda u: EN)
        self.assertEqual([f.url for f in helpers.findings_for(found, "CANON007")], [DE])
        gb, us = BASE + "/en-gb/", BASE + "/en-us/"
        same = {gb: hpage(gb, [("en-GB", gb), ("en-US", us)], lang="en-GB"),
                us: hpage(us, [("en-US", us), ("en-GB", gb)], lang="en-US")}
        self.assertEqual(helpers.findings_for(run(same, canonical_of=lambda u: us), "CANON007"), [])

    def test_sitemap_alternates_count_as_declarations(self) -> None:
        pages = {EN: hpage(EN, []), DE: hpage(DE, [], lang="de")}
        alternates = {EN: [("en", EN), ("de", DE), ("x-default", EN)], DE: [("de", DE), ("en", EN), ("x-default", EN)]}
        self.assertEqual(run(pages, sitemap_alternates=alternates), [])
        one_way = {EN: [("en", EN), ("de", DE)], DE: [("de", DE)]}
        self.assertIn("HREF003", ids(run(pages, sitemap_alternates=one_way)))

    def test_base_href_resolves_relative_targets(self) -> None:
        doc = hpage(EN, [("en", "en/"), ("de", "de/")], head='<base href="https://example.com/">')
        pages = {EN: doc, DE: hpage(DE, [("de", DE), ("en", EN)], lang="de")}
        self.assertEqual(sorted(f.rule for f in run(pages)), ["HREF004", "HREF005", "HREF005"])

    def test_site_bad_hreflang(self) -> None:
        site = sitescan.scan_build(str(helpers.fixture("site-bad")), base_url=BASE)
        inputs = sitescan.hreflang_inputs(site)
        found = run(inputs["pages"], canonical_of=inputs["canonical_of"], noindex_of=inputs["noindex_of"])
        self.assertEqual(ids(found), ["CANON007", "HREF001", "HREF002", "HREF003", "HREF004", "HREF005", "HREF006",
                                      "HREF007", "HREF008"])
        self.assertTrue(all(f.file for f in found))

    def test_site_good_hreflang_is_clean(self) -> None:
        for base in (BASE, None):
            site = sitescan.scan_build(str(helpers.fixture("site-good")), base_url=base)
            inputs = sitescan.hreflang_inputs(site)
            self.assertIn(BASE + "/de/", inputs["pages"])
            self.assertEqual(run(inputs["pages"], canonical_of=inputs["canonical_of"],
                                 noindex_of=inputs["noindex_of"]), [], base)

    def test_without_base_url_the_declared_origin_is_used(self) -> None:
        site = sitescan.scan_build(str(helpers.fixture("site-bad")), base_url=None)
        inputs = sitescan.hreflang_inputs(site)
        self.assertEqual(inputs["canonical_of"](DE), EN)
        self.assertTrue(inputs["noindex_of"](BASE + "/noindex-page/"))
        found = run(inputs["pages"], canonical_of=inputs["canonical_of"], noindex_of=inputs["noindex_of"])
        self.assertIn("CANON007", ids(found))


if __name__ == "__main__":
    unittest.main()
