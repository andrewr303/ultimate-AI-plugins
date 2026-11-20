"""SEO-GEO-god command line (WP11): the section 4.6 argparse surface, composing every module.

Offline by default. Only audit-url, access-check, robots --url and drift snapshot --url use the
network, only with --live, and only through the SSRF-guarded ``fetch`` module; without --live they
exit 3 before any socket is created. Exit codes: 0 completed, 1 gate tripped, 2 usage or input
error, 3 refused by safety policy, 4 internal error (the envelope with ``error`` is still printed).
The full report is written before a gate exits 1.
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import os
import posixpath
import re
import stat
import sys
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

from . import SCHEMAS_DIR, TOOL_NAME, VERSION
from . import (analytics, content, directives, drift, fetch, fidelity, hreflang, htmlparse, jsonld, ledger, llmstxt,
               perf, report, robots, rulesdb, sections, sitemaps, sitescan, stack)
from .findings import FAIL_ON, SEVERITY_ORDER, Finding, Result, escalate, gate_tripped
from .report import EXIT_GATE, EXIT_INTERNAL, EXIT_OK, EXIT_REFUSED, EXIT_USAGE
from .rulesdb import RuleCatalog

PROFILES = ("default", "launch", "programmatic", "local", "ecommerce", "geo")
SCORE_CHOICES = ("none", "seo", "geo", "both")
AUDIT_COMMANDS = frozenset({"audit-build", "audit-page", "audit-url"})
CRAWLER_CLASSES = ("TRAIN", "INDEX", "USER", "AGENT", "ADS", "MIXED", "CONTROL", "PREVIEW", "CORPUS")
UPDATE_KINDS = ("core", "spam", "policy", "documentation", "structured-data", "ai-control")
GSC_SUBCOMMANDS = ("movers", "decay", "ctr", "striking", "cannibalization", "brand", "buckets", "aio-recovery")
HTML_EXTS = (".html", ".htm")
MD_EXTS = (".md", ".mdx", ".markdown")
JSONLD_EXTS = HTML_EXTS + jsonld.COMPONENT_EXTS + (".jsonld", ".json")
MAX_INPUT = 5_242_880
MAX_EXPORT = 52_428_800
MAX_LIVE_SITEMAPS = 10
SITEMAP_BYTES = fetch.MAX_BYTES_LIMIT
ASSET_EXT = re.compile(r"\.(?:css|js|mjs|png|jpe?g|gif|webp|avif|svg|ico|woff2?)$", re.I)
NOSNIPPET_ATTR = re.compile(r"<[a-zA-Z][^>]*?\sdata-nosnippet\b", re.I)
OFFLINE_LIMITATION = ("Local HTML cannot establish HTTP status, X-Robots-Tag from the server, robots.txt access, "
                      "or actual indexing.")
LIVE_LIMITATION = ("A bounded crawl with the seo-geo-god user agent; search engines and AI crawlers may receive "
                   "different responses (user agent, location, bot management).")
EXPORT_LIMITATION = "Analyses of user-provided exports: heuristic readings of past data, not forecasts."
NOT_MEASURED = ["field Core Web Vitals", "indexing status", "rendered DOM after JavaScript", "AI citations"]
# audit-page sees one file: rules that need the rest of the build, or (for Markdown) the HTML layout, are skipped.
PAGE_BUILD_RULES = frozenset({"AGENT005", "CANON004"})
MARKDOWN_LAYOUT_RULES = frozenset({"CANON001", "META008", "META009", "META010", "META014", "LAUNCH001"})
NETWORK_DISABLED = "network disabled: pass --live to fetch %s (only sites you own or are authorized to test)"
# Test seam: unit tests install fakes here (FakeTransport, FakeResolver, FakeClock); production leaves None.
HOOKS: Dict[str, Any] = {"transport": None, "resolver": None, "sleep": None, "clock": None}


class CliError(Exception):
    """An error with an exit code (2 usage/input, 3 refused)."""
    code = EXIT_USAGE


class UsageError(CliError):
    code = EXIT_USAGE


class Refused(CliError):
    code = EXIT_REFUSED


@dataclass
class Ctx:
    args: argparse.Namespace
    cat: RuleCatalog
    now: str
    today: date


@dataclass
class Outcome:
    """What a command produced. `raw` replaces the rendered report for the formats in `raw_formats`."""
    result: Result
    audited: List[str] = field(default_factory=list)   # --output may not land inside these directories
    gate: bool = False                                 # command-specific gate (fidelity failed)
    gate_reason: str = ""
    raw: Optional[str] = None
    raw_formats: Tuple[str, ...] = ()
    report_to_stdout: bool = False                     # --output named the command's artifact instead


# ----------------------------------------------------------------------------- small helpers

def _disp(path: str) -> str:
    return path.replace(os.sep, "/") if os.sep != "/" else path


def _join(base: str, rel: str) -> str:
    b = _disp(base).rstrip("/")
    return rel if b in ("", ".") else posixpath.normpath(posixpath.join(b, rel))


def _origin(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return "%s://%s" % (parts.scheme.lower(), parts.netloc.lower())


def _read_bytes(path: str, limit: int = MAX_INPUT, what: str = "input") -> bytes:
    """Read a regular file (or stdin for "-") with a size cap; never reads .env files."""
    if path == "-":
        stream = getattr(sys.stdin, "buffer", None)
        data = stream.read(limit + 1) if stream is not None else sys.stdin.read(limit + 1).encode("utf-8")
    else:
        if os.path.basename(path).lower().startswith(".env"):
            raise Refused("refusing to read %s: .env files may hold secrets" % path)
        try:
            st = os.stat(path)
        except FileNotFoundError:
            raise UsageError("%s not found: %s" % (what, path)) from None
        if stat.S_ISDIR(st.st_mode):
            raise UsageError("%s is a directory: %s" % (what, path))
        if not stat.S_ISREG(st.st_mode):
            raise UsageError("%s is not a regular file: %s" % (what, path))
        if st.st_size > limit:
            raise UsageError("%s %s is %d bytes; the limit is %d" % (what, path, st.st_size, limit))
        with open(path, "rb") as fh:
            data = fh.read(limit + 1)
    if len(data) > limit:
        raise UsageError("%s %s exceeds %d bytes" % (what, path, limit))
    return data


def _read_text(path: str, limit: int = MAX_INPUT, what: str = "input") -> str:
    data = _read_bytes(path, limit, what)
    if path.lower().endswith(HTML_EXTS) or data.lstrip()[:1] == b"<":
        return sitescan.decode_html(data)
    return data.decode("utf-8-sig", "replace")


def _read_json(path: str, limit: int = MAX_EXPORT, what: str = "JSON input") -> Any:
    try:
        return rulesdb.loads_json(_read_bytes(path, limit, what))
    except ValueError as exc:
        raise UsageError("%s %s is not valid JSON: %s" % (what, path, exc)) from None


def _kind(path: str, text: str) -> str:
    low = path.lower()
    if low.endswith(MD_EXTS):
        return "markdown"
    if low.endswith(HTML_EXTS) or text.lstrip()[:1] == "<":
        return "html"
    return "markdown"


def _walk(root: str, exts: Tuple[str, ...], recursive: bool = True) -> List[str]:
    """Relative paths of regular files under root: sorted, no symlinks, dot entries or node_modules."""
    real = os.path.realpath(root)
    out: List[str] = []
    for cur, dirs, files in os.walk(real):
        dirs[:] = sorted(d for d in dirs if recursive and not d.startswith(".") and d != "node_modules"
                         and not os.path.islink(os.path.join(cur, d)))
        for name in sorted(files):
            full = os.path.join(cur, name)
            if name.startswith(".") or not name.lower().endswith(exts) or os.path.islink(full):
                continue
            try:
                if not stat.S_ISREG(os.lstat(full).st_mode) or not os.path.realpath(full).startswith(real + os.sep):
                    continue
            except OSError:
                continue
            out.append(_disp(os.path.relpath(full, real)))
    return sorted(out)


def _inputs(paths: Sequence[str], exts: Tuple[str, ...], recursive: bool) -> List[str]:
    out: List[str] = []
    for p in paths:
        if os.path.isdir(p):
            if os.path.islink(p):
                raise Refused("refusing to walk a symlinked directory: %s" % p)
            out.extend(_join(p, rel) for rel in _walk(p, exts, recursive))
        elif os.path.exists(p):
            out.append(_disp(p))
        else:
            raise UsageError("input not found: %s" % p)
    return list(dict.fromkeys(out))


def _scan(directory: str, base_url: Optional[str], url_style: str = "directory", max_pages: int = 5000,
          max_file_bytes: int = MAX_INPUT) -> sitescan.BuiltSite:
    if not os.path.isdir(directory):
        raise UsageError("build directory not found: %s" % directory)
    if max_pages < 1 or max_file_bytes < 1:
        raise UsageError("--max-pages and --max-file-bytes must be positive")
    return sitescan.scan_build(directory, base_url=base_url, url_style=url_style, max_pages=max_pages,
                               max_file_bytes=max_file_bytes)


def _page_text(site: sitescan.BuiltSite, key: str, cap: int) -> str:
    """Raw HTML of a scanned page, re-read without following symlinks (same cap as the scan)."""
    full = os.path.join(site.root or "", site.files[key])
    fd = os.open(full, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as fh:
        if not stat.S_ISREG(os.fstat(fh.fileno()).st_mode):
            raise OSError("not a regular file: %s" % site.files[key])
        data = fh.read(cap + 1)
    return sitescan.decode_html(data[:cap])


def _prefix(findings: Iterable[Finding], base: str) -> List[Finding]:
    """Make module-relative file paths relative to the working directory (as given on the command line)."""
    out = []
    for f in findings:
        if f.file and "://" not in f.file and not os.path.isabs(f.file):
            f = dataclasses.replace(f, file=_join(base, f.file))
        out.append(f)
    return out


def _site_urls(site: sitescan.BuiltSite) -> Set[str]:
    base = (site.base_url or "").rstrip("/")
    urls = set(site.pages)
    urls.update(base + a if base else a for a in site.assets)
    return urls


def _first(values: Sequence[str]) -> str:
    return next((v for v in values if v and v.strip()), "")


def _finalize(findings: Iterable[Finding], cat: RuleCatalog, *, profile: str = "default",
              expect_indexable: bool = False, home: Optional[str] = None) -> List[Finding]:
    """Catalog escalations (profiles, --expect-indexable, caps) and P0 blocker escalation (section 4.2)."""
    caps = cat.escalations.get("caps", {})
    out = []
    for f in findings:
        rule = cat.get(f.rule)
        if rule.status != "v1":
            continue   # planned rules are catalogued, never emitted
        sev = f.severity
        if sev == rule.severity:
            sev = cat.severity_for(f.rule, profile=profile, expect_indexable=expect_indexable)
        cap = caps.get(f.rule)
        if cap and SEVERITY_ORDER[sev] > SEVERITY_ORDER[cap]:
            sev = cap
        if sev != f.severity:
            f = dataclasses.replace(f, severity=sev)
        if f.rule in cat.blockers:
            if f.rule == "IDX001":
                applies = expect_indexable
            elif f.rule in ("REND001", "HTTP001"):
                applies = home is not None and (f.url or "").rstrip("/") == home.rstrip("/")
            else:
                applies = True
            if applies:
                f = escalate(f, cat)
        out.append(f)
    return out


def _robots_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{"token": r["token"], "class": r["class"], "group": r["group"], "allowed": r["allowed"],
             "blocks_site": r["blocks_site"]} for r in rows]


def _sitemap_summary(parsed: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{"source": p.get("source"), "kind": p.get("kind"), "urls": len(p.get("urls") or []),
             "sitemaps": len(p.get("sitemaps") or []), "errors": len(p.get("errors") or []), "size": p.get("size")}
            for p in parsed]


def _skip(check: str, reason: str) -> Dict[str, str]:
    return {"check": check, "reason": reason}


# ----------------------------------------------------------------------------- site audit (audit-build, audit-url)

def _audit_site(ctx: Ctx, site: sitescan.BuiltSite, parsed: List[Dict[str, Any]], *, profile: str,
                expect_indexable: bool, text_of: Callable[[str], Optional[str]], live: bool,
                full_present: bool) -> Tuple[List[Finding], List[str], List[Dict[str, str]], Dict[str, Any]]:
    """Run every module check on a BuiltSite in the section 4.5 order."""
    cat, today = ctx.cat, ctx.today
    out: List[Finding] = []
    run: List[str] = []
    skipped: List[Dict[str, str]] = []
    data: Dict[str, Any] = {}
    origin = _origin(site.base_url) if site.base_url else None
    listed = {u["loc"] for sm in parsed for u in sm.get("urls") or [] if u.get("loc")}
    # pages, duplicates, links
    out += sitescan.check_pages(site, cat, expect_indexable=expect_indexable, profile=profile, today=today,
                                sitemap_urls=listed)
    run.append("pages")
    out += sitescan.check_duplicates(site, cat)
    run.append("duplicates")
    graph = sitescan.link_graph(site)
    out += sitescan.check_links(site, graph, cat, sitemap_urls=listed)
    run.append("links")
    data["link_graph"] = {"nodes": len(graph["nodes"]), "edges": len(graph["edges"]), "home": graph["home"],
                          "orphans": len(graph["orphans"]), "orphan_sample": graph["orphans"][:10],
                          "broken": len(graph["broken"]), "redirected": len(graph["redirected"]),
                          "nofollow": len(graph["nofollow"]), "depth_histogram": graph["depth_histogram"],
                          "anchors": {k: graph["anchors"][k] for k in ("total", "generic")}}
    # robots
    rob = robots.parse_robots(site.robots_txt) if site.robots_txt is not None else None
    assets = sorted(a for a in site.assets if ASSET_EXT.search(a))[:200]
    robots_loc: Dict[str, Any] = {"url": origin + "/robots.txt"} if live and origin else {"file": "robots.txt"}
    out += robots.check_robots(rob, cat, asset_paths=assets, profile=profile, **robots_loc)
    for f in robots.check_blocked_noindex(rob, [k for k in sorted(site.pages) if sitescan.is_noindex(site, k)], cat):
        if f.file in site.pages:   # without a base URL page keys are URL paths, not files
            f = dataclasses.replace(f, url=f.file, file=site.files.get(f.file) if site.root else None)
        out.append(f)
    run.append("robots")
    data["robots"] = {"present": rob is not None, "summary": robots.robots_summary(rob),
                      "access": _robots_rows(robots.access_table(rob))}
    # one read per page: directive inputs (ai-directives), JSON-LD and content findings are collected here
    # and appended in the section 4.5 order below; raw HTML is not kept in memory between pages
    per_url: Dict[str, Dict[str, Any]] = {}
    entities: Dict[str, Any] = {}
    types: Set[str] = set()
    main_texts: Dict[str, str] = {}
    pairs: List[Dict[str, str]] = []
    citable: Dict[str, Any] = {}
    jsonld_found: List[Finding] = []
    content_found: List[Finding] = []
    merchant = True if profile == "ecommerce" else None
    for key in sorted(site.pages):
        doc = site.pages[key]
        text = text_of(key) or ""
        file = site.files.get(key) if site.root else None
        xr_value = site.headers.get(key, {}).get("x-robots-tag")
        xr = directives.parse_x_robots([xr_value]) if xr_value else {}
        per_url[key] = {"file": file, "google": sitescan.page_directives(site, key),
                        "bingbot": sitescan.page_directives(site, key, "bingbot"),
                        "bing_ai": directives.bing_ai(doc.meta, xr),
                        "data_nosnippet": len(NOSNIPPET_ATTR.findall(text))}
        summary, found = jsonld.lint_text(text, cat, filename=file or "", url=key if "://" in key else None,
                                          markup={"microdata": doc.has_microdata, "rdfa": doc.has_rdfa},
                                          merchant=merchant)
        jsonld_found += found
        entities[key] = summary["entities"]
        types.update(summary["types"])
        content_found += content.check_text(text, cat, kind="html", file=file, url=key, today=today)
        visible = not sitescan.is_noindex(site, key) and not doc.meta_refresh
        if visible:
            main_texts[key] = doc.main_text
            pairs.append({"url": key, "title": doc.titles[0] if doc.titles else "",
                          "description": _first(doc.meta.get("description", []))})
        if profile == "geo" and visible and doc.word_count >= 150:
            c = content.citability(content.blocks_from_html(text), year=today.year)
            citable[key] = {k: c.get(k) for k in ("mean_all", "mean_top5", "coverage_70")}
            citable[key]["passages"] = len(c.get("passages") or [])
    out += robots.check_page_ai_directives(per_url, cat)
    run.append("ai-directives")
    # sitemaps, hreflang
    inputs = sitescan.sitemap_inputs(site)
    out += sitemaps.check_sitemaps(parsed, cat, base_url=site.base_url, site_urls=inputs["site_urls"],
                                   indexable=inputs["indexable"], today=today, profile=profile)
    run.append("sitemaps")
    data["sitemaps"] = _sitemap_summary(parsed)
    hin = sitescan.hreflang_inputs(site)
    alternates = {u["loc"]: u["alternates"] for sm in parsed for u in sm.get("urls") or [] if u.get("alternates")}
    out += hreflang.check_hreflang(hin["pages"], cat, canonical_of=hin["canonical_of"], noindex_of=hin["noindex_of"],
                                   sitemap_alternates=alternates)
    run.append("hreflang")
    data["hreflang"] = {"clusters": len(hreflang.clusters(hin["pages"], sitemap_alternates=alternates))}
    # jsonld, content (+ pseo, citability)
    out += jsonld_found
    out += jsonld.lint_entities_site(entities, cat)
    run.append("jsonld")
    data["jsonld"] = {"pages_with_jsonld": sum(1 for k in site.pages if site.pages[k].jsonld),
                      "types": sorted(types)}
    out += content_found
    site_text = content.check_site_text(main_texts, pairs, cat, base_url=(origin + "/") if origin else None)
    out += [f for f in site_text if f.rule != "PSEO001"]
    run.append("content")
    if profile == "programmatic":
        out += [f for f in site_text if f.rule == "PSEO001"]
        run.append("pseo")
    else:
        skipped.append(_skip("pseo", "near-duplicate page analysis runs with --profile programmatic"))
    if profile == "geo":
        run.append("citability")
        data["citability"] = citable
    # perf, llms, launch
    for key in sorted(site.pages):
        out += perf.check_static(site.pages[key], cat, url=key, file=site.files.get(key) if site.root else None)
    run.append("perf")
    parsed_llms = llmstxt.parse_llms(site.llms_txt) if site.llms_txt is not None else None
    llms_loc: Dict[str, Any] = {"url": origin + "/llms.txt"} if live and origin else {"file": "llms.txt"}
    out += llmstxt.check_llms(parsed_llms, cat, base_url=site.base_url, site_urls=_site_urls(site),
                              present=site.llms_txt is not None, full_present=full_present, **llms_loc)
    run.append("llms")
    data["llms"] = {"present": site.llms_txt is not None, "full_present": full_present}
    if profile == "launch":
        run.append("launch")
    home = None
    if site.pages:
        home = graph["home"] if graph.get("home") else None
    findings = _finalize(out, cat, profile=profile, expect_indexable=expect_indexable, home=home)
    return findings, run, skipped, data


def _build_sitemaps(site: sitescan.BuiltSite) -> List[Dict[str, Any]]:
    if not site.root:
        return []
    return sitemaps.load_sitemaps(site.root, sitemaps.discover(site.root, site.robots_txt) + site.sitemap_paths)


def cmd_audit_build(ctx: Ctx) -> Outcome:
    a = ctx.args
    site = _scan(a.dir, a.base_url, a.url_style, a.max_pages, a.max_file_bytes)
    full = os.path.join(site.root or "", "llms-full.txt")
    full_present = os.path.isfile(full) and not os.path.islink(full)
    findings, run, skipped, data = _audit_site(
        ctx, site, _build_sitemaps(site), profile=a.profile, expect_indexable=a.expect_indexable,
        text_of=lambda key: _page_text(site, key, a.max_file_bytes), live=False, full_present=full_present)
    skipped.insert(0, _skip("http", "offline build: HTTP status codes and server response headers are not "
                                    "observable (host header files such as _headers are applied where present)"))
    if not site.redirects:
        skipped.append(_skip("redirects", "no redirect config (_redirects, vercel.json) in the build; server "
                                          "redirects are not observable offline"))
    skipped.append(_skip("access", "live AI-access checks (robots.txt status, CDN blocks, response headers) need "
                                   "access-check --live"))
    if a.profile != "launch":
        skipped.append(_skip("launch", "launch checks LAUNCH001 and LAUNCH005 run with --profile launch"))
    data.update(pages=len(site.pages), skipped=site.skipped[:50], profile=a.profile)
    res = Result(command="audit-build", target={"type": "build-dir", "path": _disp(a.dir), "base_url": site.base_url,
                                               "profile": a.profile},
                 findings=_prefix(findings, a.dir), checks_run=run, checks_skipped=skipped,
                 not_measured=list(NOT_MEASURED), limitations=[OFFLINE_LIMITATION], data=data,
                 summary={"pages": len(site.pages), "files_skipped": len(site.skipped)})
    return Outcome(result=res, audited=[a.dir])


def cmd_audit_page(ctx: Ctx) -> Outcome:
    a = ctx.args
    display = "stdin" if a.file == "-" else _disp(a.file)
    text = _read_text(a.file)
    kind = _kind(a.file, text)
    if a.url and not re.match(r"(?i)^https?://[^/\s?#]+", a.url):
        raise UsageError("--url must be an absolute http(s) URL")
    doc = htmlparse.parse_html(text, path=display, url=a.url) if kind == "html" else \
        htmlparse.parse_markdown(text, path=display)
    doc.raw_size = doc.raw_size or len(text.encode("utf-8"))
    key = a.url or "/"
    root = os.path.dirname(os.path.abspath(a.file)) if a.file != "-" else os.getcwd()
    site = sitescan.BuiltSite(root=root, base_url=_origin(a.url) if a.url else None, url_style="preserve",
                              pages={key: doc}, files={key: display})
    cat = ctx.cat
    out = sitescan.check_pages(site, cat, expect_indexable=a.expect_indexable, today=ctx.today)
    run = ["pages"]
    if kind == "html":
        out += robots.check_page_ai_directives({key: {
            "file": display, "google": sitescan.page_directives(site, key),
            "bingbot": sitescan.page_directives(site, key, "bingbot"), "bing_ai": directives.bing_ai(doc.meta, {}),
            "data_nosnippet": len(NOSNIPPET_ATTR.findall(text))}}, cat)
        run.append("ai-directives")
    summary, found = jsonld.lint_text(text, cat, filename=display, url=a.url,
                                      markup={"microdata": doc.has_microdata, "rdfa": doc.has_rdfa})
    out += found
    run.append("jsonld")
    out += content.check_text(text, cat, kind=kind, file=display, url=a.url, today=ctx.today)
    run.append("content")
    if kind == "html":
        out += perf.check_static(doc, cat, url=a.url, file=display)
        run.append("perf")
    if not a.url:
        out = [dataclasses.replace(f, url=None) if f.url == "/" else f for f in out]
    drop = PAGE_BUILD_RULES | (MARKDOWN_LAYOUT_RULES if kind != "html" else frozenset())
    out = [f for f in out if f.rule not in drop]
    findings = _finalize(out, cat, expect_indexable=a.expect_indexable, home=a.url if a.url and
                         urllib.parse.urlsplit(a.url).path in ("", "/") else None)
    data = {"kind": kind, "title": doc.titles[0] if doc.titles else None,
            "description": _first(doc.meta.get("description", [])) or None,
            "canonical": doc.canonicals[0][0] if doc.canonicals else None, "lang": doc.lang,
            "word_count": doc.word_count, "headings": len(doc.headings), "links": len(doc.links),
            "images": len(doc.images), "jsonld_types": summary["types"]}
    skipped = [_skip("http", "single file: HTTP status and server headers are not observable"),
               _skip("links", "single file: the internal link graph, link targets and Markdown alternates need a "
                              "build directory (audit-build)")]
    if kind != "html":
        skipped.append(_skip("perf", "Markdown source: static performance signals need built HTML"))
        skipped.append(_skip("layout", "Markdown source: canonical, lang, viewport and Open Graph tags come from "
                                       "the layout; audit the built HTML for them"))
    res = Result(command="audit-page", target={"type": "file", "path": display, "url": a.url},
                 findings=findings, checks_run=run, checks_skipped=skipped, not_measured=list(NOT_MEASURED),
                 limitations=[OFFLINE_LIMITATION], data=data, summary={"pages": 1, "files_skipped": 0})
    return Outcome(result=res)


# ----------------------------------------------------------------------------- live commands

def _require_live(args: argparse.Namespace, url: str) -> None:
    if not getattr(args, "live", False):
        raise Refused(NETWORK_DISABLED % url)


def _allow(args: argparse.Namespace) -> FrozenSet[str]:
    try:
        return fetch.parse_allow_local(getattr(args, "allow_local", None) or ())
    except ValueError as exc:
        raise UsageError(str(exc)) from None


def _live_kw(args: argparse.Namespace) -> Dict[str, Any]:
    return {"via_proxy": bool(getattr(args, "via_proxy", False)), "transport": HOOKS["transport"],
            "resolver": HOOKS["resolver"]}


def _check_start(url: str, allow: FrozenSet[str]) -> None:
    try:
        fetch.check_url(url, allow_local=allow)
    except fetch.FetchRefused as exc:
        raise Refused("refused by the fetch safety policy: %s" % exc.reason) from None


def _crawl_live(ctx: Ctx, start: str, *, max_pages: int, delay: Optional[float], ignore_robots: bool
                ) -> Tuple[sitescan.BuiltSite, Dict[str, str], List[Dict[str, Any]], Dict[str, Any]]:
    """Robots gate, bounded same-origin crawl, then sitemaps and llms.txt; returns (site, texts, parsed, data)."""
    a = ctx.args
    allow = _allow(a)
    kw = _live_kw(a)
    _check_start(start, allow)
    if not 1 <= max_pages <= fetch.CRAWL_MAX_PAGES:
        raise UsageError("--max-pages must be between 1 and %d" % fetch.CRAWL_MAX_PAGES)
    if delay is not None and delay < 0:
        raise UsageError("--delay must be >= 0")
    if ignore_robots:
        pred: Optional[Callable[[str], bool]] = None
        rinfo: Dict[str, Any] = {"outcome": "ignored (--ignore-robots with --allow-local)"}
    else:
        pred, rinfo = fetch.robots_gate(start, parse=robots.allow_predicate, allow_local=allow,
                                        clock=HOOKS["clock"], **kw)
        if rinfo.get("outcome") == "refused":
            raise Refused("refused by the fetch safety policy: %s" % rinfo.get("error"))
    stats: Dict[str, Any] = {}
    results = fetch.crawl(start, max_pages=max_pages, delay=delay, allow_local=allow, robots_allowed=pred,
                          extract_links=htmlparse.extract_links, stats=stats, sleep=HOOKS["sleep"],
                          clock=HOOKS["clock"], **kw)
    first = results[0] if results else None
    if first is not None and first.refused:
        raise Refused("refused by the fetch safety policy: %s" % first.error)
    origin = _origin(first.url) if first is not None and first.status is not None else _origin(start)
    site = sitescan.site_from_fetches([r.as_record() for r in results], base_url=origin)
    texts = {r.url: r.text for r in results if r.text is not None}
    if rinfo.get("outcome") == "parsed":
        site.robots_txt = rinfo.get("text") or ""
    pause = HOOKS["sleep"] or time.sleep
    wait = (0.2 if any(urllib.parse.urlsplit(origin).netloc == h for h in allow) else 1.0) if delay is None else delay
    extra: List[Dict[str, Any]] = []

    def get(url: str, accept: str, max_bytes: int) -> Optional[fetch.FetchResult]:
        if _origin(url) != origin or (pred is not None and not pred(url)) or len(extra) >= MAX_LIVE_SITEMAPS + 2:
            return None
        if wait:
            pause(wait)
        res = fetch.fetch(url, accept=accept, max_bytes=max_bytes, allow_local=allow, clock=HOOKS["clock"], **kw)
        extra.append({"url": res.url, "status": res.status, "error_kind": res.error_kind})
        return res

    candidates = robots.parse_robots(site.robots_txt).sitemaps if site.robots_txt else []
    queue = [u for u in candidates if _origin(u) == origin] or [origin + "/sitemap.xml"]
    parsed: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    while queue and len(parsed) < MAX_LIVE_SITEMAPS:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        res = get(u, "application/xml,text/xml;q=0.9,text/plain;q=0.5,*/*;q=0.1", SITEMAP_BYTES)
        if res is None or not res.ok or res.body is None:
            continue
        p = sitemaps.parse_sitemap(res.body, source=res.url)
        parsed.append(p)
        queue.extend(s["loc"] for s in p.get("sitemaps") or [] if s.get("loc"))
    res = get(origin + "/llms.txt", robots.TEXT_ACCEPT, 1_048_576)
    if res is not None and res.ok and res.text is not None and not llmstxt.looks_like_html(res.text):
        site.llms_txt = res.text
    data = {"robots_gate": {k: v for k, v in rinfo.items() if k != "text"},
            "crawl": {k: (v[:50] if isinstance(v, list) else v) for k, v in stats.items()},
            "fetched": len(results), "extra_requests": extra,
            "statuses": {r.url: r.status for r in results[:200]},
            "redirect_chains": [{"from": r.requested_url, "chain": r.redirect_chain, "to": r.url,
                                 "unfollowed_target": r.redirect_target} for r in results if r.redirect_chain][:50],
            "errors": [{"url": r.url, "error_kind": r.error_kind, "error": r.error} for r in results if r.error][:50]}
    data["via_proxy"] = any(r.via_proxy for r in results)
    return site, texts, parsed, data


def _live_result(res: Result, data: Dict[str, Any]) -> Result:
    res.mode = "live"
    res.limitations.append(LIVE_LIMITATION)
    if data.get("via_proxy"):
        res.via_proxy = True
        res.limitations.append(fetch.PROXY_LIMITATION)
    return res


def cmd_audit_url(ctx: Ctx) -> Outcome:
    a = ctx.args
    _require_live(a, a.url)
    if a.ignore_robots and not a.allow_local:
        raise Refused("--ignore-robots is accepted only with --allow-local (your own development server)")
    site, texts, parsed, live = _crawl_live(ctx, a.url, max_pages=a.max_pages, delay=a.delay,
                                            ignore_robots=a.ignore_robots)
    findings, run, skipped, data = _audit_site(ctx, site, parsed, profile=a.profile,
                                               expect_indexable=a.expect_indexable, text_of=texts.get, live=True,
                                               full_present=False)
    run += ["http", "redirects"]
    skipped.append(_skip("access", "Cloudflare blocks, Content-Signal headers and probes run in access-check --live"))
    data.update(live, pages=len(site.pages), profile=a.profile)
    res = Result(command="audit-url", target={"type": "url", "url": fetch.redact_url(a.url),
                                             "base_url": site.base_url, "profile": a.profile},
                 findings=findings, checks_run=run, checks_skipped=skipped,
                 not_measured=["field Core Web Vitals", "indexing status", "rendered DOM after JavaScript",
                               "AI citations"], data=data,
                 summary={"pages": len(site.pages), "files_skipped": len(site.skipped)})
    return Outcome(result=_live_result(res, live))


def cmd_access_check(ctx: Ctx) -> Outcome:
    a = ctx.args
    _require_live(a, a.origin)
    allow = _allow(a)
    _check_start(a.origin, allow)
    kw = _live_kw(a)
    parts = urllib.parse.urlsplit(a.origin.strip())
    if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
        raise UsageError("ORIGIN must be an absolute http(s) URL")
    base = _origin(a.origin.strip())
    proxied: List[bool] = []

    def get(url: str, accept: str = robots.HTML_ACCEPT, max_bytes: int = 65536) -> fetch.FetchResult:
        res = fetch.fetch(url, accept=accept, max_bytes=max_bytes, allow_local=allow, clock=HOOKS["clock"], **kw)
        proxied.append(res.via_proxy)
        return res

    def llms_check(text: str) -> List[Finding]:
        return llmstxt.check_llms(llmstxt.parse_llms(text), ctx.cat, base_url=base, url=base + "/llms.txt")

    data, found = robots.access_check(base, fetch=get, catalog=ctx.cat, llms_check=llms_check, robots_findings=True)
    if (data.get("robots") or {}).get("outcome") == "refused":
        raise Refused(data.get("error") or "refused by the fetch safety policy")
    data["via_proxy"] = any(proxied)
    res = Result(command="access-check", target={"type": "origin", "url": base},
                 findings=_finalize(found, ctx.cat), checks_run=["access", "robots", "llms"],
                 not_measured=["what AI products actually crawl or cite", "bot verification by IP or reverse DNS"],
                 data=data)
    return Outcome(result=_live_result(res, data))


# ----------------------------------------------------------------------------- robots, jsonld, sitemap, hreflang, links

def cmd_robots(ctx: Ctx) -> Outcome:
    a = ctx.args
    if bool(a.file) == bool(a.url):
        raise UsageError("give a robots.txt FILE or --url URL --live")
    paths = a.path or ["/"]
    data: Dict[str, Any] = {}
    if a.url:
        _require_live(a, a.url)
        allow = _allow(a)
        _check_start(a.url, allow)
        target = _origin(a.url) + "/robots.txt"
        res = fetch.fetch(target, accept="text/plain,*/*;q=0.1", max_bytes=1_048_576, allow_local=allow,
                          clock=HOOKS["clock"], **_live_kw(a))
        if res.refused:
            raise Refused("refused by the fetch safety policy: %s" % res.error)
        data["fetch"] = {"url": res.url, "status": res.status, "error_kind": res.error_kind}
        if res.ok:
            rob: Optional[robots.RobotsTxt] = robots.parse_robots(res.text or "")
        elif res.error is None and res.status is not None and 400 <= res.status < 500 and res.status != 429:
            rob = None
        else:
            raise UsageError("robots.txt could not be read (%s); run access-check --live for status details" % (
                "HTTP %s" % res.status if res.status else res.error_kind))
        found = robots.check_robots(rob, ctx.cat, url=target)
        result = Result(command="robots", target={"type": "url", "url": target}, mode="live", via_proxy=res.via_proxy)
        if res.via_proxy:
            result.limitations.append(fetch.PROXY_LIMITATION)
    else:
        rob = robots.parse_robots(_read_text(a.file, MAX_INPUT, "robots.txt"))
        found = robots.check_robots(rob, ctx.cat, file=_disp(a.file))
        result = Result(command="robots", target={"type": "robots-file", "path": _disp(a.file)})
    try:
        rows = robots.access_table(rob, paths=paths, classes=a.bots)
    except ValueError as exc:
        raise UsageError(str(exc)) from None
    data.update(summary=robots.robots_summary(rob), bots=a.bots, paths=paths, rows=rows)
    result.findings = _finalize(found, ctx.cat)
    result.checks_run = ["robots"]
    result.data = data
    result.limitations.append("robots.txt is a request to crawlers, not access control; a CDN or WAF can still "
                              "block or allow bots regardless of this file.")
    return Outcome(result=result)


def cmd_jsonld(ctx: Ctx) -> Outcome:
    a = ctx.args
    files = _inputs(a.paths, JSONLD_EXTS, a.recursive)
    out: List[Finding] = []
    rows: List[Dict[str, Any]] = []
    entities: Dict[str, Any] = {}
    explicit = {_disp(p) for p in a.paths if not os.path.isdir(p)}
    for path in files:
        text = _read_text(path, MAX_INPUT, "file")
        if path.lower().endswith(".json") and path not in explicit and '"@context"' not in text:
            continue   # in directory walks, plain .json files count only when they look like JSON-LD
        summary, found = jsonld.lint_text(text, ctx.cat, filename=path, url=a.url)
        out += found
        entities[a.url or path] = summary["entities"]
        rows.append({"path": path, "blocks": summary["blocks"], "parsed": summary["parsed"],
                     "skipped": summary["skipped"], "invalid": summary["invalid"], "types": summary["types"],
                     "findings": len(found)})
    if len(entities) > 1:
        out += jsonld.lint_entities_site(entities, ctx.cat)
    res = Result(command="jsonld", target={"type": "paths", "path": ", ".join(_disp(p) for p in a.paths), "url": a.url},
                 findings=_finalize(out, ctx.cat), checks_run=["jsonld"], data={"files": rows},
                 not_measured=["Google rich-result eligibility (use the Rich Results Test)"],
                 limitations=["Syntax and structure checks only; valid markup is never a rich-result guarantee."])
    return Outcome(result=res, audited=[p for p in a.paths if os.path.isdir(p)])


def _local_sitemaps(path: str) -> Tuple[str, List[Dict[str, Any]]]:
    if os.path.isdir(path):
        root = path
        rtxt = os.path.join(path, "robots.txt")
        robots_text = _read_text(rtxt, MAX_INPUT, "robots.txt") if os.path.isfile(rtxt) else None
        rels = sitemaps.discover(path, robots_text) + [r for r in _walk(path, (".xml", ".gz"), True)
                                                       if sitescan.SITEMAP_NAME.search(r.rsplit("/", 1)[-1])]
        return root, sitemaps.load_sitemaps(root, rels)
    if not os.path.isfile(path):
        raise UsageError("sitemap not found: %s" % path)
    root = os.path.dirname(path) or "."
    parsed = sitemaps.load_sitemaps(root, [os.path.basename(path)])
    known = {p["source"] for p in parsed}
    for p in list(parsed):   # one level of local sitemap-index children
        for child in p.get("sitemaps") or []:
            rel = urllib.parse.unquote(urllib.parse.urlsplit(child.get("loc") or "").path).lstrip("/")
            if rel and rel not in known and os.path.isfile(os.path.join(root, rel)):
                known.add(rel)
                parsed += sitemaps.load_sitemaps(root, [rel])
    return root, parsed


def cmd_sitemap(ctx: Ctx) -> Outcome:
    a = ctx.args
    root, parsed = _local_sitemaps(a.path)
    kw: Dict[str, Any] = {}
    if a.build_dir:
        site = _scan(a.build_dir, a.base_url)
        kw = sitescan.sitemap_inputs(site)
    found = sitemaps.check_sitemaps(parsed, ctx.cat, base_url=a.base_url, today=ctx.today, **kw)
    res = Result(command="sitemap", target={"type": "sitemap", "path": _disp(a.path), "build_dir": a.build_dir,
                                           "base_url": a.base_url},
                 findings=_prefix(_finalize(found, ctx.cat), root), checks_run=["sitemaps"],
                 data={"sitemaps": _sitemap_summary(parsed), "parsed": [
                     {"source": p.get("source"), "errors": p.get("errors"), "notes": p.get("notes"),
                      "sitemaps": p.get("sitemaps"), "sample": [u.get("loc") for u in (p.get("urls") or [])[:20]]}
                     for p in parsed]})
    if not a.build_dir:
        res.checks_skipped.append(_skip("parity", "pass --build-dir to compare sitemap URLs with the built pages"))
    return Outcome(result=res, audited=[a.path] if os.path.isdir(a.path) else [])


def cmd_hreflang(ctx: Ctx) -> Outcome:
    a = ctx.args
    site = _scan(a.dir, a.base_url, a.url_style)
    parsed = _build_sitemaps(site)
    hin = sitescan.hreflang_inputs(site)
    alternates = {u["loc"]: u["alternates"] for sm in parsed for u in sm.get("urls") or [] if u.get("alternates")}
    found = hreflang.check_hreflang(hin["pages"], ctx.cat, canonical_of=hin["canonical_of"],
                                    noindex_of=hin["noindex_of"], sitemap_alternates=alternates)
    groups = hreflang.clusters(hin["pages"], sitemap_alternates=alternates)
    res = Result(command="hreflang", target={"type": "build-dir", "path": _disp(a.dir), "base_url": site.base_url},
                 findings=_prefix(_finalize(found, ctx.cat), a.dir), checks_run=["hreflang"],
                 data={"pages": len(site.pages), "clusters": groups[:50], "cluster_count": len(groups)})
    return Outcome(result=res, audited=[a.dir])


def cmd_links(ctx: Ctx) -> Outcome:
    a = ctx.args
    site = _scan(a.dir, a.base_url)
    listed = {u["loc"] for sm in _build_sitemaps(site) for u in sm.get("urls") or [] if u.get("loc")}
    graph = sitescan.link_graph(site)
    found = sitescan.check_links(site, graph, ctx.cat, sitemap_urls=listed)
    if a.graph_out:
        report.write_output(report.dump_json(graph), a.graph_out, force=a.force, forbid_under=[a.dir])
    data = {"pages": len(site.pages), "edges": len(graph["edges"]), "home": graph["home"],
            "orphans": graph["orphans"][:100], "depth_histogram": graph["depth_histogram"],
            "broken": graph["broken"][:100], "redirected": len(graph["redirected"]), "nofollow": len(graph["nofollow"]),
            "anchors": graph["anchors"], "graph_out": _disp(a.graph_out) if a.graph_out else None}
    res = Result(command="links", target={"type": "build-dir", "path": _disp(a.dir), "base_url": site.base_url},
                 findings=_prefix(_finalize(found, ctx.cat), a.dir), checks_run=["links"], data=data)
    return Outcome(result=res, audited=[a.dir])


def _map_key(url: str) -> str:
    parts = urllib.parse.urlsplit(sitescan.normalize_url(url) if "://" in url else url)
    return (parts.path or "/") + ("?" + parts.query if parts.query else "")


def cmd_redirects(ctx: Ctx) -> Outcome:
    a = ctx.args
    _read_bytes(a.map, 10 * 1024 * 1024, "redirect map")   # existence, type and size checks
    entries = sitescan.parse_redirect_map(a.map)
    old = _scan(a.old_build, a.base_url) if a.old_build else None
    new = _scan(a.new_build, a.base_url) if a.new_build else None
    found = sitescan.check_redirects(entries, ctx.cat, old_site=old, new_site=new)
    mapping = {_map_key(e["old"]): e for e in entries if not e.get("error")}
    chains = []
    for e in [x for x in entries if not x.get("error")][:500]:
        hops, cur, seen = [e["old"]], e, {_map_key(e["old"])}
        while _map_key(cur["new"]) in mapping and _map_key(cur["new"]) not in seen and len(hops) < 20:
            seen.add(_map_key(cur["new"]))
            cur = mapping[_map_key(cur["new"])]
            hops.append(cur["old"])
        loop = _map_key(cur["new"]) in seen
        chains.append({"from": e["old"], "to": cur["new"], "hops": len(hops), "loop": loop})
    res = Result(command="redirects", target={"type": "redirect-map", "path": _disp(a.map), "base_url": a.base_url},
                 findings=_finalize(found, ctx.cat), checks_run=["redirects"],
                 data={"entries": len(entries), "errors": sum(1 for e in entries if e.get("error")), "chains": chains})
    if not (old and new):
        res.checks_skipped.append(_skip("coverage", "pass --old-build and --new-build to check destinations and "
                                                    "unmapped old URLs"))
    return Outcome(result=res, audited=[d for d in (a.old_build, a.new_build) if d])


def cmd_perf(ctx: Ctx) -> Outcome:
    a = ctx.args
    if not (a.path or a.lighthouse or a.crux):
        raise UsageError("give a PATH, --lighthouse FILE or --crux FILE")
    out: List[Finding] = []
    data: Dict[str, Any] = {}
    audited: List[str] = []
    if a.path:
        if os.path.isdir(a.path):
            site = _scan(a.path, None)
            for key in sorted(site.pages):
                out += _prefix(perf.check_static(site.pages[key], ctx.cat, url=None, file=site.files[key]), a.path)
            data["static"] = {"pages": len(site.pages)}
            audited.append(a.path)
        else:
            doc = htmlparse.parse_html(_read_text(a.path), path=_disp(a.path))
            doc.raw_size = len(_read_bytes(a.path))
            out += perf.check_static(doc, ctx.cat, file=_disp(a.path))
            data["static"] = {"pages": 1}
    lab = field_ = None
    try:
        if a.lighthouse:
            lab = perf.read_lighthouse(_read_json(a.lighthouse, MAX_EXPORT, "Lighthouse JSON"))
            data["lab"] = lab
        if a.crux:
            field_ = perf.read_crux(_read_json(a.crux, MAX_EXPORT, "CrUX JSON"))
            data["field"] = field_
    except ValueError as exc:
        raise UsageError(str(exc)) from None
    if lab is not None and field_ is not None:
        out += perf.check_field({"field": field_, "lab": lab}, ctx.cat)
    elif lab is not None or field_ is not None:
        out += perf.check_field(lab if lab is not None else field_, ctx.cat)
    res = Result(command="perf", target={"type": "perf", "path": _disp(a.path or a.lighthouse or a.crux),
                                        "lighthouse": a.lighthouse, "crux": a.crux},
                 findings=_finalize(out, ctx.cat), checks_run=["perf"], data=data,
                 not_measured=[] if field_ is not None else ["field Core Web Vitals"],
                 limitations=["Static HTML signals are risks, not measurements; lab data is not field data."])
    return Outcome(result=res, audited=audited)


# ----------------------------------------------------------------------------- llms.txt and indexnow

def cmd_llms_validate(ctx: Ctx) -> Outcome:
    a = ctx.args
    text = _read_text(a.file, MAX_INPUT, "llms.txt")
    parsed = llmstxt.parse_llms(text)
    site_urls = None
    folder = a.build_dir or os.path.dirname(a.file) or "."
    if a.build_dir:
        site_urls = _site_urls(_scan(a.build_dir, a.base_url))
    full = os.path.join(folder, "llms-full.txt")
    found = llmstxt.check_llms(parsed, ctx.cat, base_url=a.base_url, site_urls=site_urls, present=True,
                               full_present=os.path.isfile(full) and not os.path.islink(full), file=_disp(a.file))
    res = Result(command="llms-txt validate", target={"type": "file", "path": _disp(a.file), "base_url": a.base_url},
                 findings=_finalize(found, ctx.cat), checks_run=["llms"], data=parsed,
                 limitations=["llms.txt is optional; Google Search ignores it and no AI search vendor documents "
                              "using it (as of 2026-11-01)."])
    if not a.build_dir:
        res.checks_skipped.append(_skip("site-links", "pass --build-dir to check that linked pages exist"))
    return Outcome(result=res, audited=[a.build_dir] if a.build_dir else [])


def _indexable_pages(site: sitescan.BuiltSite) -> List[str]:
    ok = sitescan.sitemap_inputs(site)["indexable"]
    return [k for k in sorted(site.pages) if ok(k) is True]


def cmd_llms_draft(ctx: Ctx) -> Outcome:
    a = ctx.args
    site = _scan(a.dir, a.base_url)
    keep = set(_indexable_pages(site))
    pages = [{"url": k, "title": site.pages[k].titles[0] if site.pages[k].titles else "",
              "description": _first(site.pages[k].meta.get("description", [])), "noindex": k not in keep}
             for k in sorted(site.pages)]
    try:
        text = llmstxt.draft_llms(pages, title=a.title, summary=a.summary, optional_urls=a.optional_prefix or ())
    except ValueError as exc:
        raise UsageError(str(exc)) from None
    written = None
    if a.output:
        report.write_output(text, a.output, force=a.force, forbid_under=[a.dir])
        written = _disp(a.output)
    res = Result(command="llms-txt draft",
                 target={"type": "build-dir", "path": _disp(a.dir), "base_url": site.base_url},
                 data={"text": text, "pages": len(keep), "written": written},
                 limitations=["Labels and notes come only from existing titles and descriptions; review before "
                              "publishing (owner approval)."])
    return Outcome(result=res, raw=text, raw_formats=("text",), report_to_stdout=True)


def cmd_indexnow(ctx: Ctx) -> Outcome:
    a = ctx.args
    if bool(a.build_dir) == bool(a.urls_file):
        raise UsageError("give exactly one of --build-dir DIR or --urls-file FILE")
    if bool(a.key) == bool(a.key_file):
        raise UsageError("give exactly one of --key K or --key-file F")
    if a.build_dir:
        if not a.base_url:
            raise UsageError("--build-dir needs --base-url")
        urls = _indexable_pages(_scan(a.build_dir, a.base_url))
    else:
        lines = _read_text(a.urls_file, MAX_EXPORT, "URL list").splitlines()
        urls = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    key = a.key or _first(_read_text(a.key_file, 1024, "key file").splitlines()).strip()
    host = urllib.parse.urlsplit(a.base_url or (urls[0] if urls else "")).hostname or ""
    try:
        payload = sitemaps.indexnow_payload(urls, host=host, key=key, key_location=a.key_location)
    except ValueError as exc:
        raise UsageError(str(exc)) from None
    check: Dict[str, Any] = {"checked": False}
    if a.build_dir:
        rel = (urllib.parse.urlsplit(a.key_location).path if a.key_location else "/%s.txt" % key)
        prefix = urllib.parse.urlsplit(a.base_url).path.rstrip("/")
        rel = rel[len(prefix):] if prefix and rel.startswith(prefix) else rel
        path = os.path.join(a.build_dir, urllib.parse.unquote(rel).lstrip("/"))
        if not os.path.realpath(path).startswith(os.path.realpath(a.build_dir) + os.sep):
            raise Refused("--key-location path escapes the build directory")
        present = os.path.isfile(path) and not os.path.islink(path)
        matches = present and _first(_read_text(path, 1024, "key file").splitlines()).strip() == key
        check = {"checked": True, "expected": _join(a.build_dir, rel.lstrip("/")), "present": present,
                 "matches": bool(matches)}
    res = Result(command="indexnow", target={"type": "indexnow", "url": "https://%s/" % host if host else None},
                 data={"payload": payload, "urls": len(payload["urlList"]), "key_file": check, "sent": False,
                       "note": "Payload prepared only; nothing was sent. Submitting it is an external action that "
                               "needs owner approval. Google does not use IndexNow."})
    return Outcome(result=res, audited=[a.build_dir] if a.build_dir else [])


# ----------------------------------------------------------------------------- content commands

def cmd_citability(ctx: Ctx) -> Outcome:
    a = ctx.args
    if a.top < 1:
        raise UsageError("--top must be at least 1")
    text = _read_text(a.file)
    kind = _kind(a.file, text)
    blocks = content.blocks_from_html(text) if kind == "html" else content.blocks_from_markdown(text)
    data = content.citability(blocks, query=a.query, year=ctx.today.year, top=a.top)
    res = Result(command="citability", target={"type": "file", "path": _disp(a.file), "query": a.query},
                 checks_run=["citability"], data=data,
                 limitations=["Citability scores are a heuristic (evidence class C) for editing priorities; they "
                              "do not predict whether any AI product will cite the page."])
    return Outcome(result=res)


def cmd_content_lint(ctx: Ctx) -> Outcome:
    a = ctx.args
    files = _inputs(a.paths, HTML_EXTS + MD_EXTS, a.recursive)
    out: List[Finding] = []
    rows = []
    for path in files:
        text = _read_text(path, MAX_INPUT, "file")
        kind = _kind(path, text)
        found = content.check_text(text, ctx.cat, kind=kind, file=path, today=ctx.today)
        out += found
        rows.append({"path": path, "kind": kind, "findings": len(found),
                     "metrics": content.lint_metrics(text, kind=kind, today=ctx.today)})
    res = Result(command="content-lint", target={"type": "paths", "path": ", ".join(_disp(p) for p in a.paths)},
                 findings=_finalize(out, ctx.cat), checks_run=["content"], data={"files": rows},
                 limitations=["Phrase lists are style signals, not AI detection."])
    return Outcome(result=res, audited=[p for p in a.paths if os.path.isdir(p)])


def _sections(path: str) -> Tuple[str, str, List[sections.Section]]:
    text = _read_text(path)
    fm, body = sections.split_frontmatter(text)
    return text, fm, sections.split_sections(body)


def _section(secs: Sequence[sections.Section], sid: str) -> sections.Section:
    try:
        return sections.get_section(secs, sid)
    except KeyError:
        raise UsageError("unknown section id %r (run sections list)" % sid) from None


def cmd_sections_list(ctx: Ctx) -> Outcome:
    a = ctx.args
    _text, fm, secs = _sections(a.file)
    rows = sections.section_table(secs, first_line=len(sections.lines(fm)) + 1)
    res = Result(command="sections list", target={"type": "file", "path": _disp(a.file)},
                 data={"frontmatter": bool(fm), "sections": rows})
    return Outcome(result=res)


def cmd_sections_show(ctx: Ctx) -> Outcome:
    a = ctx.args
    _text, _fm, secs = _sections(a.file)
    sec = _section(secs, a.id)
    written = None
    if a.output:
        _not_same(a.output, a.file)
        report.write_output(sec.text, a.output, force=a.force)
        written = _disp(a.output)
    res = Result(command="sections show", target={"type": "file", "path": _disp(a.file)},
                 data={"id": sec.id, "heading": sec.heading, "level": sec.level, "word_count": sec.word_count,
                       "text": sec.text, "written": written})
    return Outcome(result=res, raw=sec.text, raw_formats=("text",), report_to_stdout=True)


def _not_same(output: str, source: str) -> None:
    if os.path.exists(output) and os.path.realpath(output) == os.path.realpath(source):
        raise Refused("refusing to edit %s in place; write to a new file" % source)


def cmd_sections_replace(ctx: Ctx) -> Outcome:
    a = ctx.args
    text, fm, secs = _sections(a.file)
    sec = _section(secs, a.id)
    new = sections.clean_rewrite(sec.text, _read_text(getattr(a, "with"), MAX_INPUT, "replacement"))
    full = fm + sections.join_sections(sections.replace_section(secs, a.id, new))
    diff = sections.unified(text, full, _disp(a.file))
    data: Dict[str, Any] = {"id": a.id, "changed": full != text}
    if a.output:
        _not_same(a.output, a.file)
        report.write_output(full, a.output, force=a.force)
        data["written"] = _disp(a.output)
    else:
        data["diff"] = diff
    res = Result(command="sections replace", target={"type": "file", "path": _disp(a.file)}, data=data,
                 limitations=["The source file is never edited in place; review the diff and run fidelity."])
    return Outcome(result=res, raw=diff, raw_formats=("text",), report_to_stdout=True)


def cmd_fidelity(ctx: Ctx) -> Outcome:
    a = ctx.args
    result = fidelity.check_fidelity(_read_text(a.original), _read_text(a.rewrite), min_ratio=a.min_ratio,
                                     max_ratio=a.max_ratio)
    found = fidelity.fidelity_findings(result, file=_disp(a.rewrite), catalog=ctx.cat)
    res = Result(command="fidelity", target={"type": "rewrite", "path": _disp(a.rewrite),
                                            "original": _disp(a.original)},
                 findings=_finalize(found, ctx.cat), checks_run=["fidelity"], data=result)
    return Outcome(result=res, gate=not result["passed"],
                   gate_reason="rewrite failed the fidelity check (%d violation(s))" % len(result["violations"]))


# ----------------------------------------------------------------------------- drift and ledger

def _records(site: sitescan.BuiltSite) -> List[Dict[str, Any]]:
    return [sitescan.page_record(k, site.pages[k], status=site.status.get(k), headers=site.headers.get(k))
            for k in sorted(site.pages)]


def cmd_drift_snapshot(ctx: Ctx) -> Outcome:
    a = ctx.args
    if bool(a.dir) == bool(a.url):
        raise UsageError("give a build DIR or --url URL --live")
    if not a.output:
        raise UsageError("drift snapshot needs --output FILE")
    if a.url:
        _require_live(a, a.url)
        site, _texts, _parsed, live = _crawl_live(ctx, a.url, max_pages=a.max_pages, delay=a.delay,
                                                  ignore_robots=False)
        source = {"type": "live", "url": fetch.redact_url(a.url), "base_url": a.base_url or site.base_url,
                  "profile": "default"}
        audited: List[str] = []
    else:
        site = _scan(a.dir, a.base_url)
        live = {}
        source = {"type": "build-dir", "path": _disp(a.dir), "base_url": site.base_url, "profile": "default"}
        audited = [a.dir]
    snap = drift.snapshot(_records(site), source=source, tool_version=VERSION, now=ctx.now, robots_txt=site.robots_txt)
    report.write_output(report.dump_json(snap), a.output, force=a.force, forbid_under=audited)
    res = Result(command="drift snapshot", target=dict(source),
                 data={"written": _disp(a.output), "pages": len(snap.get("pages") or {}), "crawl": live or None})
    if a.url:
        _live_result(res, live)
    return Outcome(result=res, audited=audited, report_to_stdout=True)


def cmd_drift_compare(ctx: Ctx) -> Outcome:
    a = ctx.args
    baseline = _read_json(a.baseline, MAX_EXPORT, "baseline snapshot")
    if os.path.isdir(a.current):
        src = baseline.get("source") if isinstance(baseline, dict) else None
        base = a.base_url or (src.get("base_url") if isinstance(src, dict) else None)
        site = _scan(a.current, base)
        current = drift.snapshot(_records(site), source={"type": "build-dir", "path": _disp(a.current),
                                                          "base_url": site.base_url, "profile": "default"},
                                 tool_version=VERSION, now=ctx.now, robots_txt=site.robots_txt)
    else:
        current = _read_json(a.current, MAX_EXPORT, "current snapshot")
    try:
        data, found = drift.compare(baseline, current, ctx.cat)
    except (TypeError, AttributeError) as exc:
        raise UsageError("not a seo-geo-god snapshot: %s" % exc) from None
    res = Result(command="drift compare", target={"type": "drift", "path": _disp(a.current),
                                                 "baseline": _disp(a.baseline)},
                 findings=_finalize(found, ctx.cat), checks_run=["drift"], data=data)
    return Outcome(result=res, audited=[a.current] if os.path.isdir(a.current) else [])


def cmd_drift_findings(ctx: Ctx) -> Outcome:
    a = ctx.args
    data = drift.compare_findings(_read_json(a.old, MAX_EXPORT, "report"), _read_json(a.new, MAX_EXPORT, "report"),
                                  ctx.cat)
    res = Result(command="drift findings", target={"type": "reports", "path": _disp(a.new), "old": _disp(a.old)},
                 data=data)
    return Outcome(result=res)


def cmd_ledger_init(ctx: Ctx) -> Outcome:
    a = ctx.args
    meta = ledger.init(a.dir, now=ctx.now)
    return Outcome(result=Result(command="ledger init", target={"type": "ledger", "path": _disp(a.dir)}, data=meta))


def cmd_ledger_record(ctx: Ctx) -> Outcome:
    a = ctx.args
    raw = _read_bytes(getattr(a, "json"), MAX_INPUT, "observation JSON").decode("utf-8-sig", "replace")
    try:
        doc = rulesdb.loads_json(raw)
        items = doc if isinstance(doc, list) else [doc]
    except ValueError:
        try:
            items = [rulesdb.loads_json(line) for line in raw.splitlines() if line.strip()]
        except ValueError as exc:
            raise UsageError("observation input is not JSON or JSON Lines: %s" % exc) from None
    stored = ledger.record_many(a.dir, items, now=ctx.now)
    return Outcome(result=Result(command="ledger record", target={"type": "ledger", "path": _disp(a.dir)},
                                 data={"recorded": len(stored), "ids": [s["id"] for s in stored]}))


def cmd_ledger_summary(ctx: Ctx) -> Outcome:
    a = ctx.args
    window = None
    if a.window:
        parts = a.window.split(":")
        if len(parts) != 2:
            raise UsageError("--window must be START:END (YYYY-MM-DD:YYYY-MM-DD)")
        window = (parts[0], parts[1])
    by = [b.strip() for b in a.by.split(",") if b.strip()]
    data = ledger.summary(ledger.load(a.dir), by=by, window=window)
    return Outcome(result=Result(command="ledger summary", target={"type": "ledger", "path": _disp(a.dir)}, data=data,
                                 limitations=["Rates describe the recorded samples only; empty and error samples are "
                                              "excluded from denominators."]))


def cmd_ledger_status(ctx: Ctx) -> Outcome:
    a = ctx.args
    rows = ledger.experiments_status(ledger.load(a.dir), today=ctx.today)
    return Outcome(result=Result(command="ledger status", target={"type": "ledger", "path": _disp(a.dir)},
                                 data={"experiments": rows, "today": ctx.today.isoformat()}))


# ----------------------------------------------------------------------------- exports (gsc, referrers, gaps, project)

def _rows(path: str, dims: Optional[str]) -> List[Dict[str, Any]]:
    _read_bytes(path, MAX_EXPORT, "export")   # existence, type and size checks (and never .env)
    return analytics.load_rows(path, dimensions=[d.strip() for d in dims.split(",")] if dims else None)


def cmd_gsc(ctx: Ctx) -> Outcome:
    a = ctx.args
    sub = a.gsc_sub
    cur = _rows(a.current, a.dimensions)
    needs_prev = sub in ("movers", "decay", "aio-recovery")
    if needs_prev and not a.previous:
        raise UsageError("gsc %s needs CURRENT and PREVIOUS exports" % sub)
    prev = _rows(a.previous, a.dimensions) if a.previous else None
    curve = analytics.site_ctr_curve(cur) if getattr(a, "calibrate", False) else None
    if sub == "movers":
        data: Any = analytics.movers(cur, prev, key=a.key or "query", min_delta=a.min_delta,
                                     min_impressions=a.min_impressions)
    elif sub == "decay":
        data = analytics.decay(cur, prev, key=a.key or "page", drop_pct=a.drop_pct, min_prev_clicks=a.min_prev_clicks)
    elif sub == "ctr":
        data = analytics.ctr_anomalies(cur, max_position=a.max_position, max_ctr=a.max_ctr,
                                       min_impressions=a.min_impressions, curve=curve)
    elif sub == "striking":
        data = analytics.striking_distance(cur, low=a.low, high=a.high, min_impressions=a.min_impressions)
    elif sub == "cannibalization":
        data = analytics.cannibalization(cur, min_impressions=a.min_impressions)
    elif sub == "brand":
        if not a.brand_terms:
            raise UsageError("gsc brand needs --brand-terms TERM ...")
        data = analytics.branded_split(cur, a.brand_terms)
    elif sub == "buckets":
        data = analytics.planner_buckets(cur, curve=curve, days=a.days)
    else:
        data = analytics.aio_recovery(cur, prev, key=a.key or "query", min_impressions=a.min_impressions)
    payload = data if isinstance(data, dict) else {"rows": data, "count": len(data)}
    if curve is not None:
        payload = dict(payload, calibrated_curve={str(k): v for k, v in curve.items()})
    res = Result(command="gsc " + sub, target={"type": "export", "path": _disp(a.current),
                                             "previous": _disp(a.previous) if a.previous else None},
                 data=payload, limitations=[EXPORT_LIMITATION])
    return Outcome(result=res)


def cmd_referrers(ctx: Ctx) -> Outcome:
    a = ctx.args
    _read_bytes(a.file, MAX_EXPORT, "export")
    data = analytics.classify_bots(a.file) if a.bots else analytics.classify_referrers(a.file, log=a.log)
    limits = ["Counts from one export; missing referrers land in Direct, so AI referral counts are a floor."]
    if a.bots:
        limits = ["User-agent strings are claims; counts are claimed (unverified) until checked by IP or reverse DNS."]
    return Outcome(result=Result(command="referrers", target={"type": "export", "path": _disp(a.file)}, data=data,
                                 limitations=limits))


def cmd_gaps_plan(ctx: Ctx) -> Outcome:
    a = ctx.args
    project = _read_json(a.project, MAX_INPUT, "project file")
    _read_bytes(a.tracker, MAX_EXPORT, "tracker")
    data = analytics.plan_citation_gaps(a.tracker, project, root=a.repo_root)
    return Outcome(result=Result(command="gaps plan", target={"type": "tracker", "path": _disp(a.tracker),
                                                             "project": _disp(a.project)}, data=data))


def cmd_project_validate(ctx: Ctx) -> Outcome:
    a = ctx.args
    problems = analytics.validate_project(_read_json(a.file, MAX_INPUT, "project file"))
    return Outcome(result=Result(command="project validate", target={"type": "file", "path": _disp(a.file)},
                                 data={"valid": not problems, "problems": problems}))


# ----------------------------------------------------------------------------- reference data commands

def cmd_stack(ctx: Ctx) -> Outcome:
    a = ctx.args
    if not os.path.isdir(a.root):
        raise UsageError("not a directory: %s" % a.root)
    data = stack.detect_stack(a.root)
    return Outcome(result=Result(command="stack", target={"type": "repo", "path": _disp(a.root)}, data=data,
                                 limitations=["Detection reads configuration files only; verify the installed "
                                              "framework version before applying a recipe."]))


def cmd_updates(ctx: Ctx) -> Outcome:
    a = ctx.args
    data = analytics.updates(since=a.since, kind=a.kind, today=ctx.today, include_unverified=a.unverified)
    return Outcome(result=Result(command="updates", target={"type": "data", "path": "data/search-updates.json"},
                                 data=data))


def cmd_crawlers(ctx: Ctx) -> Outcome:
    a = ctx.args
    reg = robots.load_registry()
    rows = [c for c in reg["crawlers"] if a.klass is None or c["class"] == a.klass]
    data: Dict[str, Any] = {"as_of": reg.get("as_of"), "recheck_by": reg.get("recheck_by"), "class": a.klass,
                            "crawlers": rows, "claims": reg.get("claims")}
    if a.klass in (None, "CONTROL"):
        data["policy_tokens"] = reg.get("policy_tokens")
    return Outcome(result=Result(command="crawlers", target={"type": "data", "path": "data/ai-crawlers.json"},
                                 data=data, limitations=["A user-agent token is a claim; verify crawlers by "
                                                         "published IP lists or reverse DNS where offered."]))


_CLASS_TEXT = {"A": "A (official engine or standards documentation)", "B": "B (deterministic spec or structure check)",
               "C": "C (heuristic; thresholds are ours)", "D": "D (experimental; never penalizes a score)"}


def _ref_link(ref: str) -> str:
    if ref.startswith("fact:"):
        fid = ref[5:]
        return "[%s](current-facts.md#%s)" % (fid, fid.lower())
    if ref.startswith("rule:"):
        rid = ref[5:]
        return "[%s](#%s)" % (rid, rid.lower())
    if ref.startswith("https://"):
        return "<%s>" % ref
    if ref.startswith("references/"):
        rel = ref[len("references/"):]
        return "[%s](%s)" % (report.md_escape(rel), rel)
    return "[%s](../%s)" % (report.md_escape(ref), ref)


def rule_catalog_markdown(cat: RuleCatalog, rules: Optional[Sequence[rulesdb.Rule]] = None) -> str:
    """references/rule-catalog.md: one anchored section per rule, grouped by category (generated)."""
    chosen = list(cat.all() if rules is None else rules)
    esc = report.md_escape
    lines = ["# Rule catalog", "",
             "Generated by `SG rules --format md` from `data/rules.json` (rules version %s, as of %s). Do not edit "
             "this file by hand: change the catalog, then regenerate it. `tests/test_cli.py` checks that the two "
             "match." % (cat.rules_version, cat.as_of), "",
             "As of %s. Severities, priorities and weights are opinionated defaults. Evidence classes: A official "
             "engine or standards documentation, B deterministic spec or structure check, C heuristic (our own "
             "thresholds), D experimental (never penalizes a score). Rules with status `planned` are catalogued "
             "but never emitted. Scores and priorities are explained in "
             "[scoring-and-prioritization.md](scoring-and-prioritization.md)." % cat.as_of, "",
             "Priority: P0 fix now (blocks indexing, AI access or rich-result validity site-wide, or ships staging "
             "artifacts), P1 this sprint, P2 backlog, P3 optional. Scope `site` means a site-wide rule, which always "
             "takes the largest scope multiplier in scores.", "",
             "## Categories", "", "| Category | Title | Rule families | SEO weight | GEO weight | Scored | Rules |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for cid, meta in cat.categories.items():
        count = sum(1 for r in chosen if r.category == cid)
        lines.append("| `%s` | %s | %s | %s | %s | %s | %d |" % (
            cid, esc(meta.get("title")), esc(", ".join(meta.get("families") or [])), meta["weights"]["seo"],
            meta["weights"]["geo"], "yes" if meta.get("scored", True) else "no", count))
    for cid, meta in cat.categories.items():
        group = [r for r in chosen if r.category == cid]
        if not group:
            continue
        lines += ["", "## %s (`%s`)" % (esc(meta.get("title")), cid)]
        for r in group:
            lines += ["", '<a id="%s"></a>' % r.id.lower(), "", "### %s: %s" % (r.id, esc(r.title)), "",
                      "| Field | Value |", "| --- | --- |",
                      "| Severity | %s |" % r.severity, "| Priority | %s |" % r.priority,
                      "| Evidence class | %s |" % _CLASS_TEXT.get(r.evidence_class, r.evidence_class),
                      "| Effort / impact | %s / %s |" % (r.effort or "n/a", r.impact),
                      "| Scope | %s |" % r.scope, "| Status | %s |" % r.status,
                      "| Checked by | `%s` |" % r.owner, "",
                      "- **Fix:** %s" % esc(r.fix_hint)]
            if r.notes:
                lines.append("- **Notes:** %s" % esc(r.notes))
            lines.append("- **References:** %s" % ", ".join(_ref_link(x) for x in r.refs))
    return "\n".join(lines) + "\n"


def cmd_rules(ctx: Ctx) -> Outcome:
    a = ctx.args
    cat = ctx.cat
    if a.category and a.category not in cat.categories:
        raise UsageError("unknown category %r; choose from %s" % (a.category, ", ".join(cat.categories)))
    rules = [r for r in cat.all() if (a.category is None or r.category == a.category)
             and (a.status is None or r.status == a.status)]
    data = {"rules_version": cat.rules_version, "as_of": cat.as_of, "count": len(rules),
            "categories": cat.categories, "penalties": cat.penalties, "blockers": sorted(cat.blockers),
            "rules": [r.to_dict() for r in rules]}
    return Outcome(result=Result(command="rules", target={"type": "data", "path": "data/rules.json"}, data=data),
                   raw=rule_catalog_markdown(cat, rules), raw_formats=("md",))


def cmd_doctor(ctx: Ctx) -> Outcome:
    cat = ctx.cat
    py_ok = sys.version_info >= (3, 9)
    fresh = rulesdb.freshness(ctx.today)
    problems = cat.problems()
    schemas = []
    for p in sorted(SCHEMAS_DIR.glob("*.json")):
        try:
            rulesdb.read_json(p)
            schemas.append({"file": "schemas/" + p.name, "ok": True})
        except (OSError, ValueError):
            schemas.append({"file": "schemas/" + p.name, "ok": False})
    warnings = []
    if not py_ok:
        warnings.append("Python 3.9 or newer is required")
    for row in fresh:
        if row["status"] in ("aging", "stale", "unknown"):
            warnings.append("%s is %s (as_of %s); re-verify facts against primary sources" % (
                row["file"], row["status"], row["as_of"]))
    if problems:
        warnings.append("rule catalog has %d integrity problem(s)" % len(problems))
    warnings += ["%s does not parse" % s["file"] for s in schemas if not s["ok"]]
    cwd = os.getcwd()
    data = {"ok": py_ok and not problems and all(s["ok"] for s in schemas)
            and not any(r["status"] in ("stale", "unknown") for r in fresh),
            "python": {"version": "%d.%d.%d" % sys.version_info[:3], "minimum": "3.9", "ok": py_ok},
            "tool_version": VERSION, "today": ctx.today.isoformat(), "data": fresh,
            "catalog": {"rules": len(cat), "v1": sum(1 for r in cat.all() if r.status == "v1"),
                        "planned": sum(1 for r in cat.all() if r.status == "planned"),
                        "rules_version": cat.rules_version, "problems": problems},
            "schemas": schemas, "output": {"cwd_writable": os.access(cwd, os.W_OK)},
            "network": "offline by default; only --live commands fetch, through the SSRF-guarded client",
            "warnings": warnings}
    if warnings and not ctx.args.quiet:
        for w in warnings:
            sys.stderr.write("%s: warning: %s\n" % (TOOL_NAME, w))
    return Outcome(result=Result(command="doctor", target={"type": "install"}, data=data))


# ----------------------------------------------------------------------------- parser

def _common() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(add_help=False)
    g = p.add_argument_group("global options")
    g.add_argument("--format", choices=report.FORMATS, default="json", help="output format (default json)")
    g.add_argument("--output", metavar="FILE", help="write to FILE (exclusive create; see --force)")
    g.add_argument("--force", action="store_true", help="allow --output to overwrite an existing file")
    g.add_argument("--fail-on", choices=FAIL_ON, default="never", help="exit 1 at or above this severity")
    g.add_argument("--scores", choices=SCORE_CHOICES, default=None, help="add readiness scores (audit commands)")
    g.add_argument("--now", metavar="ISO8601", help="timestamp for generated_at (or env SEO_GEO_GOD_NOW)")
    g.add_argument("--today", metavar="YYYY-MM-DD", help="date for date-dependent checks")
    g.add_argument("--quiet", action="store_true", help="suppress notes and warnings on stderr")
    return p


def build_parser() -> argparse.ArgumentParser:
    """The full CLI parser (section 4.6)."""
    parser = argparse.ArgumentParser(
        prog="seo_geo.py", description="SEO-GEO-god: offline-first SEO and GEO audit CLI (standard library only).",
        epilog="Exit codes: 0 completed, 1 gate tripped, 2 usage or input error, 3 refused by safety policy, "
               "4 internal error. Network access only with --live.")
    parser.add_argument("--version", action="version", version="%s %s" % (TOOL_NAME, VERSION))
    top = parser.add_subparsers(dest="command", metavar="COMMAND")
    top.required = True
    common = _common()

    def leaf(group: Any, name: str, full: str, handler: Callable[[Ctx], Outcome], text: str) -> argparse.ArgumentParser:
        p = group.add_parser(name, help=text, description=text, parents=[common])
        p.set_defaults(handler=handler, command_name=full)
        return p

    def grouped(name: str, text: str) -> Any:
        p = top.add_parser(name, help=text, description=text)
        sub = p.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
        sub.required = True
        return sub

    def profile(p: argparse.ArgumentParser) -> None:
        p.add_argument("--profile", choices=PROFILES, default="default")

    def live(p: argparse.ArgumentParser, *, crawl: bool = False) -> None:
        p.add_argument("--live", action="store_true", help="allow network access (required)")
        p.add_argument("--allow-local", action="append", metavar="HOST:PORT", help="permit your own local server")
        p.add_argument("--via-proxy", action="store_true", help="use HTTPS_PROXY/HTTP_PROXY (no DNS pinning)")
        if crawl:
            p.add_argument("--max-pages", type=int, default=fetch.CRAWL_DEFAULT_PAGES, metavar="N")
            p.add_argument("--delay", type=float, default=None, metavar="S")

    p = leaf(top, "stack", "stack", cmd_stack, "detect framework, build output and SEO surfaces (read-only)")
    p.add_argument("root", nargs="?", default=".", metavar="ROOT")
    p = leaf(top, "audit-build", "audit-build", cmd_audit_build, "audit a static build directory (main CI command)")
    p.add_argument("dir", metavar="DIR")
    p.add_argument("--base-url", metavar="URL")
    p.add_argument("--url-style", choices=sitescan.URL_STYLES, default="directory")
    p.add_argument("--expect-indexable", action="store_true")
    profile(p)
    p.add_argument("--max-pages", type=int, default=5000, metavar="N")
    p.add_argument("--max-file-bytes", type=int, default=MAX_INPUT, metavar="N")
    p = leaf(top, "audit-page", "audit-page", cmd_audit_page, "audit one HTML or Markdown file (or - for stdin)")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--url", metavar="URL")
    p.add_argument("--expect-indexable", action="store_true")
    p = leaf(top, "audit-url", "audit-url", cmd_audit_url, "bounded same-origin live crawl (needs --live)")
    p.add_argument("url", metavar="URL")
    live(p, crawl=True)
    p.add_argument("--ignore-robots", action="store_true", help="only with --allow-local (your dev server)")
    p.add_argument("--expect-indexable", action="store_true")
    profile(p)
    p = leaf(top, "access-check", "access-check", cmd_access_check, "live AI-access checks for one origin")
    p.add_argument("origin", metavar="ORIGIN")
    live(p)
    p = leaf(top, "robots", "robots", cmd_robots, "robots.txt crawler access table and checks")
    p.add_argument("file", nargs="?", metavar="FILE")
    p.add_argument("--url", metavar="URL")
    live(p)
    p.add_argument("--bots", choices=("all", "ai", "search", "user", "training"), default="all")
    p.add_argument("--path", action="append", metavar="PATH")
    p = leaf(top, "jsonld", "jsonld", cmd_jsonld, "lint JSON-LD in HTML, component templates and .jsonld files")
    p.add_argument("paths", nargs="+", metavar="PATH")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--url", metavar="URL")
    p = leaf(top, "sitemap", "sitemap", cmd_sitemap, "parse and check sitemaps (file or directory)")
    p.add_argument("path", metavar="PATH")
    p.add_argument("--build-dir", metavar="DIR")
    p.add_argument("--base-url", metavar="URL")
    p = leaf(top, "hreflang", "hreflang", cmd_hreflang, "hreflang clusters and reciprocity")
    p.add_argument("dir", metavar="DIR")
    p.add_argument("--base-url", metavar="URL", required=True)
    p.add_argument("--url-style", choices=sitescan.URL_STYLES, default="directory")
    p = leaf(top, "links", "links", cmd_links, "internal link graph: orphans, depth, broken links")
    p.add_argument("dir", metavar="DIR")
    p.add_argument("--base-url", metavar="URL")
    p.add_argument("--graph-out", metavar="FILE")
    p = leaf(top, "redirects", "redirects", cmd_redirects, "validate a redirect map (old_url,new_url[,status])")
    p.add_argument("map", metavar="MAP.csv")
    p.add_argument("--old-build", metavar="DIR")
    p.add_argument("--new-build", metavar="DIR")
    p.add_argument("--base-url", metavar="URL")
    p = leaf(top, "perf", "perf", cmd_perf, "static performance signals and Lighthouse/CrUX summaries")
    p.add_argument("path", nargs="?", metavar="PATH")
    p.add_argument("--lighthouse", metavar="FILE")
    p.add_argument("--crux", metavar="FILE")
    g = grouped("llms-txt", "validate or draft llms.txt")
    p = leaf(g, "validate", "llms-txt validate", cmd_llms_validate, "validate an llms.txt file")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--build-dir", metavar="DIR")
    p.add_argument("--base-url", metavar="URL")
    p = leaf(g, "draft", "llms-txt draft", cmd_llms_draft, "draft llms.txt from a build (never invents text)")
    p.add_argument("dir", metavar="DIR")
    p.add_argument("--base-url", metavar="URL", required=True)
    p.add_argument("--title", metavar="T", required=True)
    p.add_argument("--summary", metavar="S")
    p.add_argument("--optional-prefix", action="append", metavar="PATH")
    p = leaf(top, "indexnow", "indexnow", cmd_indexnow, "prepare an IndexNow payload (never sends it)")
    p.add_argument("--build-dir", metavar="DIR")
    p.add_argument("--urls-file", metavar="FILE")
    p.add_argument("--base-url", metavar="URL")
    p.add_argument("--key", metavar="K")
    p.add_argument("--key-file", metavar="F")
    p.add_argument("--key-location", metavar="URL")
    p = leaf(top, "citability", "citability", cmd_citability, "passage citability heuristics for one file")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--query", metavar="Q")
    p.add_argument("--top", type=int, default=5, metavar="N")
    p = leaf(top, "content-lint", "content-lint", cmd_content_lint, "content checks for HTML, Markdown and MDX")
    p.add_argument("paths", nargs="+", metavar="PATH")
    p.add_argument("--recursive", action="store_true")
    g = grouped("sections", "list, show or replace Markdown sections (never edits in place)")
    p = leaf(g, "list", "sections list", cmd_sections_list, "list sections with ids")
    p.add_argument("file", metavar="FILE")
    p = leaf(g, "show", "sections show", cmd_sections_show, "show one section (--output writes its text)")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--id", required=True, metavar="ID")
    p = leaf(g, "replace", "sections replace", cmd_sections_replace, "replace one section; diff or --output FILE")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--id", required=True, metavar="ID")
    p.add_argument("--with", required=True, metavar="NEW", help="file holding the new section text (- for stdin)")
    p.add_argument("--diff", action="store_true", help="print a unified diff (default without --output)")
    p = leaf(top, "fidelity", "fidelity", cmd_fidelity, "check a rewrite against its original (exit 1 on failure)")
    p.add_argument("original", metavar="ORIGINAL")
    p.add_argument("rewrite", metavar="REWRITE")
    p.add_argument("--min-ratio", type=float, metavar="F")
    p.add_argument("--max-ratio", type=float, metavar="F")
    g = grouped("drift", "snapshots, drift comparison and audit history")
    p = leaf(g, "snapshot", "drift snapshot", cmd_drift_snapshot, "write a snapshot of a build or live site")
    p.add_argument("dir", nargs="?", metavar="DIR")
    p.add_argument("--url", metavar="URL")
    live(p, crawl=True)
    p.add_argument("--base-url", metavar="URL")
    p = leaf(g, "compare", "drift compare", cmd_drift_compare, "compare a baseline snapshot with a snapshot or build")
    p.add_argument("baseline", metavar="BASELINE")
    p.add_argument("current", metavar="CURRENT")
    p.add_argument("--base-url", metavar="URL")
    p = leaf(g, "findings", "drift findings", cmd_drift_findings, "diff two result envelopes")
    p.add_argument("old", metavar="OLD.json")
    p.add_argument("new", metavar="NEW.json")
    g = grouped("ledger", "append-only observation ledger")
    p = leaf(g, "init", "ledger init", cmd_ledger_init, "create a ledger directory")
    p.add_argument("dir", metavar="DIR")
    p = leaf(g, "record", "ledger record", cmd_ledger_record, "append observations from JSON (- for stdin)")
    p.add_argument("dir", metavar="DIR")
    p.add_argument("--json", required=True, metavar="FILE")
    p = leaf(g, "summary", "ledger summary", cmd_ledger_summary, "rates with Wilson 95%% intervals")
    p.add_argument("dir", metavar="DIR")
    p.add_argument("--by", default="surface,query_class", metavar="FIELDS")
    p.add_argument("--window", metavar="START:END")
    p = leaf(g, "status", "ledger status", cmd_ledger_status, "experiments and read-back dates")
    p.add_argument("dir", metavar="DIR")
    g = grouped("gsc", "offline Search Console export analyses")
    for name in GSC_SUBCOMMANDS:
        p = leaf(g, name, "gsc " + name, cmd_gsc, "gsc %s analysis of exported rows" % name)
        p.set_defaults(gsc_sub=name)
        p.add_argument("current", metavar="CURRENT")
        p.add_argument("previous", nargs="?", metavar="PREVIOUS")
        p.add_argument("--dimensions", metavar="DIMS", help="API JSON key order, e.g. query,page")
        p.add_argument("--key", choices=("query", "page"))
        p.add_argument("--brand-terms", nargs="+", metavar="T")
        p.add_argument("--calibrate", action="store_true", help="use the site-calibrated CTR curve")
        p.add_argument("--min-impressions", type=int, metavar="N")
        p.add_argument("--min-delta", type=float, metavar="F")
        p.add_argument("--drop-pct", type=float, metavar="F")
        p.add_argument("--min-prev-clicks", type=int, metavar="N")
        p.add_argument("--max-position", type=float, metavar="F")
        p.add_argument("--max-ctr", type=float, metavar="F")
        p.add_argument("--low", type=float, metavar="F")
        p.add_argument("--high", type=float, metavar="F")
        p.add_argument("--days", type=int, default=90, metavar="N")
    p = leaf(top, "referrers", "referrers", cmd_referrers, "AI referral or claimed bot counts from an export or log")
    p.add_argument("file", metavar="FILE")
    p.add_argument("--log", action="store_true")
    p.add_argument("--bots", action="store_true")
    g = grouped("gaps", "citation-gap planning")
    p = leaf(g, "plan", "gaps plan", cmd_gaps_plan, "plan one rewrite per page from a citation tracker")
    p.add_argument("tracker", metavar="TRACKER")
    p.add_argument("--project", required=True, metavar="FILE")
    p.add_argument("--repo-root", metavar="DIR", help="check project source paths against this repository")
    g = grouped("project", "project contract")
    p = leaf(g, "validate", "project validate", cmd_project_validate, "validate a project contract file")
    p.add_argument("file", metavar="FILE")
    p = leaf(top, "updates", "updates", cmd_updates, "dated search-engine update and documentation ledger")
    p.add_argument("--since", metavar="YYYY[-MM[-DD]]")
    p.add_argument("--kind", choices=UPDATE_KINDS)
    p.add_argument("--unverified", action="store_true")
    p = leaf(top, "crawlers", "crawlers", cmd_crawlers, "AI crawler and agent registry")
    p.add_argument("--class", dest="klass", choices=CRAWLER_CLASSES, metavar="CLASS")
    p = leaf(top, "rules", "rules", cmd_rules, "rule catalog (--format md generates references/rule-catalog.md)")
    p.add_argument("--category", metavar="C")
    p.add_argument("--status", choices=rulesdb.STATUSES)
    leaf(top, "doctor", "doctor", cmd_doctor, "Python version, data freshness and catalog integrity")
    return parser


def command_names() -> List[str]:
    """Sorted leaf command strings, e.g. "audit-build", "gsc movers", "llms-txt validate"."""
    names: List[str] = []

    def walk(p: argparse.ArgumentParser, prefix: str) -> None:
        for action in p._actions:   # argparse keeps sub-parsers here; there is no public accessor
            if isinstance(action, argparse._SubParsersAction):
                for name, child in action.choices.items():
                    full = (prefix + " " + name).strip()
                    if any(isinstance(x, argparse._SubParsersAction) for x in child._actions):
                        walk(child, full)
                    else:
                        names.append(full)

    walk(build_parser(), "")
    return sorted(names)


# ----------------------------------------------------------------------------- main

def _today(args: argparse.Namespace, now: str) -> date:
    if args.today:
        try:
            return date.fromisoformat(args.today)
        except ValueError:
            raise ValueError("--today must be YYYY-MM-DD") from None
    if args.now or os.environ.get("SEO_GEO_GOD_NOW"):
        return date.fromisoformat(now[:10])
    return date.today()


def _appendix(env: Dict[str, Any], fmt: str) -> str:
    """Data section for md/text output of data commands (JSON in a fence; <, > and & escaped)."""
    if not env.get("data"):
        return ""
    body = report.dump_json(env["data"]).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    if fmt == "text":
        return body
    runs = [len(m) for m in re.findall(r"`+", body)]
    fence = "`" * max(3, max(runs or [0]) + 1)
    return "\n## Data\n\n%sjson\n%s%s\n" % (fence, body, fence)


def _render(ctx: Ctx, out: Outcome) -> Tuple[str, Dict[str, Any]]:
    a = ctx.args
    scores = None
    if a.command_name in AUDIT_COMMANDS:
        scores = a.scores or ("geo" if getattr(a, "profile", None) == "geo" else None)
    env = out.result.to_envelope(ctx.cat, now=ctx.now, scores=scores)
    if out.raw is not None and a.format in out.raw_formats:
        return out.raw, env
    text = report.render(env, a.format, ctx.cat)
    if a.format in ("md", "text") and a.command_name not in AUDIT_COMMANDS:
        extra = _appendix(env, a.format)
        if a.format == "md" and extra:
            footer = "\n---\n\n%s\n" % report.UNTRUSTED_FOOTER
            text = text[: -len(footer)] + extra + footer if text.endswith(footer) else text + extra
        else:
            text = extra + text
    return text, env


def _error_text(command: str, fmt: str, message: str, now: str, cat: Optional[RuleCatalog]) -> str:
    res = Result(command=command, target={}, error=message)
    try:
        env = res.to_envelope(cat or rulesdb.default_catalog(), now=now)
        return report.render(env, fmt if fmt in report.FORMATS else "json", cat)
    except Exception:   # the catalog itself is broken: fall back to a minimal JSON envelope
        return json.dumps({"tool": TOOL_NAME, "version": VERSION, "command": command, "error": message},
                          sort_keys=True) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the CLI; returns the exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    except SystemExit as exc:   # --help / --version (0) or an argparse usage error (2)
        return exc.code if isinstance(exc.code, int) else (EXIT_OK if exc.code is None else EXIT_USAGE)
    command, fmt = args.command_name, args.format
    now = "1970-01-01T00:00:00Z"
    cat: Optional[RuleCatalog] = None
    try:
        now = report.resolve_now(args.now)
        ctx = Ctx(args=args, cat=rulesdb.default_catalog(), now=now, today=_today(args, now))
        cat = ctx.cat
        if args.scores not in (None, "none") and command not in AUDIT_COMMANDS:
            raise UsageError("--scores applies to audit-build, audit-page and audit-url only")
        out = args.handler(ctx)
        text, env = _render(ctx, out)
        report.write_output(text, None if out.report_to_stdout else args.output, force=args.force,
                            forbid_under=out.audited)
        final = out.result.final_findings(cat)
        if out.gate or gate_tripped(final, args.fail_on):
            if not args.quiet:
                reason = out.gate_reason if out.gate else "findings at or above --fail-on %s (%d error, %d warning, " \
                    "%d info)" % (args.fail_on, env["summary"]["error"], env["summary"]["warning"],
                                  env["summary"]["info"])
                sys.stderr.write("%s: gate tripped: %s\n" % (TOOL_NAME, reason))
            return EXIT_GATE
        return EXIT_OK
    except CliError as exc:
        code, message = exc.code, str(exc)
    except (report.OutputRefused, FileExistsError) as exc:
        code, message = EXIT_REFUSED, str(exc)
    except fetch.FetchRefused as exc:
        code, message = EXIT_REFUSED, "refused by the fetch safety policy: %s" % exc.reason
    except (OSError, ValueError, csv.Error) as exc:
        code, message = EXIT_USAGE, str(exc) or exc.__class__.__name__
    except Exception as exc:   # last resort: report, never crash without an envelope
        code, message = EXIT_INTERNAL, "internal error: %s: %s" % (exc.__class__.__name__, exc)
    try:
        sys.stdout.write(_error_text(command, fmt, message, now, cat))
        sys.stderr.write("%s: error: %s\n" % (TOOL_NAME, message))
    except OSError:   # stdout or stderr already closed (for example piped into head)
        pass
    return code
