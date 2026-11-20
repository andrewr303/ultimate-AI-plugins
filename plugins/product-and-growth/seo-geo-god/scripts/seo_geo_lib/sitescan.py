"""Static build scan, page checks, duplicates, link graph and redirect maps (WP02).

``scan_build`` walks a build directory read-only: sorted order, realpath containment, symlinks,
special files, dot-directories and ``node_modules`` skipped, size caps on every read, ``.env``
files never opened. It reads HTML pages plus ``robots.txt``, ``sitemap*.xml(.gz)``, ``llms.txt``,
``_headers``, ``_redirects`` and ``vercel.json`` (headers, redirects and catch-all rewrites).

Search-facing checks (canonical presence, titles, descriptions, Open Graph, headings, rendering,
images) skip pages that are noindex or meta-refresh redirects; directive, structural and launch
checks run on every page. Composition for ``audit-build`` (done by cli.py) is listed in
``check_pages``.
"""
from __future__ import annotations

import codecs
import csv
import hashlib
import io
import ipaddress
import os
import re
import stat
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Pattern, Set, Tuple, Union
from urllib.parse import parse_qsl, quote, unquote, urlencode, urljoin, urlsplit, urlunsplit

from . import directives, htmlparse
from .findings import Finding, make
from .htmlparse import PageDoc
from .rulesdb import RuleCatalog, default_catalog, loads_json, thresholds

URL_STYLES = ("directory", "clean", "preserve")
PSEUDO_ORIGIN = "https://site.invalid"
INDEX_NAMES = ("index.html", "index.htm")
NOT_FOUND_NAMES = ("404.html", "404.htm", "404/index.html")
SITEMAP_NAME = re.compile(r"(?i)sitemap[\w.-]*\.xml(?:\.gz)?$")
AUX_MAX_BYTES = 5_242_880
SITEMAP_MAX_BYTES = 52_428_800
MAX_ENTRIES = 200_000
REDIRECT_STATUSES = (301, 302, 303, 307, 308)
TEMPORARY = (302, 303, 307)
_SAFE = "/!$&'()*+,;=:@-._~"
_DEFAULT_PORT = {"http": 80, "https": 443}
_GENERIC_ANCHORS = frozenset([
    "click here", "here", "read more", "learn more", "more", "more info", "more information", "this", "this link",
    "link", "continue", "continue reading", "details", "go", "see more", "find out more", "info", "click"])
_PLACEHOLDER_TITLES = frozenset([
    "home", "untitled", "untitled document", "document", "welcome", "title", "page title", "my site", "new page",
    "create next app", "vite + react", "vite + react + ts", "vite + vue", "vite + vue + ts", "vite + svelte",
    "vite app", "react app", "astro", "welcome to astro", "gatsby default starter", "nuxt", "sveltekit app",
    "angular", "undefined", "null", "index"])
_TEMPLATE_TOKEN = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\$\{[^}]*\}|%[A-Z_]{3,}%|\[(?:REPLACE|INSERT|TITLE|PAGE TITLE)",
                             re.I)
_LOCAL_SUFFIX = (".localhost", ".local", ".internal", ".lan", ".home.arpa")
_PREVIEW_SUFFIX = (".vercel.app", ".netlify.app", ".pages.dev", ".herokuapp.com", ".ngrok.io", ".ngrok-free.app",
                   ".ngrok.app", ".loca.lt", ".trycloudflare.com", ".amplifyapp.com", ".azurestaticapps.net",
                   ".workers.dev")
_STAGING_LABEL = re.compile(r"^(?:staging|stage|stg|preview|dev|development|uat|qa|test|sandbox)(?:[-\d]|$)"
                            r"|-(?:staging|preview|stage|dev)(?:-|$)")
_URL_IN_TEXT = re.compile(r"https?://[^\s\"'<>\\]+", re.I)
_PAGE_PATH = re.compile(r"^(.*?/)(?:page|p)/(\d+)/?$", re.I)
_PAGE_PARAMS = ("page", "p", "pg", "paged")
_YEAR = re.compile(r"(?<![\d-])((?:19|20)\d{2})(?![\d-])")
_YEAR_HISTORIC = re.compile(r"(?:since|founded|established|est\.?|from|copyright|\u00a9)\s*$", re.I)
_FILENAME_ALT = re.compile(r"^(?:[\w-]+\.(?:jpe?g|png|gif|webp|avif|svg|bmp|tiff?)|(?:img|dsc|dcim|pxl|image|photo|"
                           r"screenshot|picture|pic)[\s_-]*\d*|[a-z0-9]+(?:[_-][a-z0-9]+){2,})$", re.I)
_GBP_TEXT = re.compile(r"\b(?:message|chat with) us on google\b|\bchat (?:on|via|with) google (?:business|maps)\b|"
                       r"\bgoogle business (?:chat|messages?)\b", re.I)
_PUSHSTATE = re.compile(r"history\s*\.\s*pushState\s*\(")
_POPSTATE = re.compile(r"addEventListener\s*\(\s*['\"]popstate['\"]|onpopstate\s*=")
_ONLOAD = re.compile(r"DOMContentLoaded|addEventListener\s*\(\s*['\"](?:load|pageshow)['\"]|\bonload\s*=")
_USER_EVENT = re.compile(r"addEventListener\s*\(\s*['\"](?:click|submit|keydown|keyup|change|input|pointerdown)['\"]"
                         r"|\bon(?:click|submit|change)\s*=")
_ORG_TYPES = ("WebSite", "Corporation", "LocalBusiness", "OnlineStore", "OnlineBusiness", "Store", "NGO", "Consortium")


# ---------------------------------------------------------------------------------------- data

@dataclass
class BuiltSite:
    """A scanned build (or live crawl). Fields after `skipped` are additive to the blueprint."""
    root: Optional[str]
    base_url: Optional[str]
    url_style: str
    pages: Dict[str, PageDoc] = field(default_factory=dict)       # key = mapped URL (URL path when no base)
    files: Dict[str, str] = field(default_factory=dict)           # url -> rel file path
    status: Dict[str, int] = field(default_factory=dict)          # live crawls only
    headers: Dict[str, Dict[str, str]] = field(default_factory=dict)
    redirects: List[Dict[str, Any]] = field(default_factory=list)
    robots_txt: Optional[str] = None
    sitemap_paths: List[str] = field(default_factory=list)
    llms_txt: Optional[str] = None
    not_found_page: Optional[str] = None
    skipped: List[Dict[str, str]] = field(default_factory=list)
    not_found_doc: Optional[PageDoc] = None
    spa_fallback: Optional[str] = None                            # "200.html", "_redirects:3", "vercel.json"
    assets: Set[str] = field(default_factory=set)                 # URL paths of every regular file
    header_rules: List[Dict[str, Any]] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------------------- URLs

def normalize_url(url: str) -> str:
    """Comparison key: lower-case scheme/host, default port and fragment dropped, path encoding normalized."""
    text = (url or "").strip()
    try:
        parts = urlsplit(text)
        port = parts.port
    except ValueError:
        return text
    path = quote(unquote(parts.path), safe=_SAFE)
    if not parts.scheme and not parts.netloc:
        return urlunsplit(("", "", path, parts.query, ""))
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    host = "[%s]" % host if ":" in host else host
    netloc = host if port is None or port == _DEFAULT_PORT.get(scheme) else "%s:%d" % (host, port)
    return urlunsplit((scheme, netloc, path or "/", parts.query, ""))


def _slashless(url: str) -> str:
    parts = urlsplit(url)
    if parts.path.endswith("/") and parts.path != "/":
        return urlunsplit((parts.scheme, parts.netloc, parts.path[:-1], parts.query, ""))
    return url


def same_ignoring_slash(a: str, b: str) -> bool:
    """True when two URLs are equal after normalization and trailing-slash removal."""
    return _slashless(normalize_url(a)) == _slashless(normalize_url(b))


def _check_base(base_url: Optional[str]) -> Optional[str]:
    if not base_url:
        return None
    parts = urlsplit(base_url.strip())
    if parts.scheme not in ("http", "https") or not parts.netloc or parts.query or parts.fragment or "@" in parts.netloc:
        raise ValueError("base URL must be an absolute http(s) URL without credentials, query or fragment")
    return base_url.strip().rstrip("/")


def url_for(rel_path: str, base_url: Optional[str], url_style: str) -> str:
    """Map a build-relative file path to its URL (directory | clean | preserve), §4.3 rules."""
    if url_style not in URL_STYLES:
        raise ValueError("url_style must be one of %s" % ", ".join(URL_STYLES))
    rel = rel_path.replace("\\", "/").lstrip("/")
    segs = rel.split("/")
    low = segs[-1].lower()
    if url_style != "preserve" and low in INDEX_NAMES:
        path = "/" + "/".join(segs[:-1])
        if url_style == "directory" and len(segs) > 1:
            path += "/"
    elif url_style == "clean" and low.endswith((".html", ".htm")):
        path = "/" + rel[: rel.rfind(".")]
    else:
        path = "/" + rel
    path = "/".join(quote(seg, safe="!$&'()*+,;=:@-._~") for seg in path.split("/"))
    return (base_url.rstrip("/") + path) if base_url else path


def _origin(url: str) -> str:
    parts = urlsplit(normalize_url(url))
    return "%s://%s" % (parts.scheme, parts.netloc)


# ---------------------------------------------------------------------------------------- safe reading

def _read_file(path: str, cap: int) -> bytes:
    """Read a regular file without following symlinks; ValueError when larger than cap."""
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("not a regular file")
        with os.fdopen(fd, "rb") as fh:
            fd = -1
            data = fh.read(cap + 1)
    finally:
        if fd >= 0:
            os.close(fd)
    if len(data) > cap:
        raise ValueError("file exceeds %d bytes" % cap)
    return data


def decode_html(data: bytes) -> str:
    """BOM > <meta charset> in the first 4,096 bytes > UTF-8 (replacement on errors)."""
    for bom, codec in ((b"\xef\xbb\xbf", "utf-8"), (b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be")):
        if data.startswith(bom):
            return data[len(bom):].decode(codec, "replace")
    m = re.search(rb"<meta[^>]+charset\s*=\s*[\"']?\s*([A-Za-z0-9_.:-]+)", data[:4096], re.I)
    codec = "utf-8"
    if m:
        try:
            codec = codecs.lookup(m.group(1).decode("ascii")).name
        except (LookupError, UnicodeDecodeError):
            codec = "utf-8"
        if codec.startswith("utf-16"):
            codec = "utf-8"
    return data.decode(codec, "replace")


def _walk(root: str, skipped: List[Dict[str, str]]) -> List[Tuple[str, str, int]]:
    out: List[Tuple[str, str, int]] = []
    stack = [("", root)]
    seen = 0
    while stack:
        rel_dir, full_dir = stack.pop()
        try:
            entries = sorted(os.scandir(full_dir), key=lambda e: e.name)
        except OSError as exc:
            skipped.append({"path": rel_dir or ".", "reason": "unreadable directory: %s" % exc.__class__.__name__})
            continue
        for entry in entries:
            seen += 1
            if seen > MAX_ENTRIES:
                skipped.append({"path": rel_dir or ".", "reason": "entry limit %d reached" % MAX_ENTRIES})
                return sorted(out)
            rel = (rel_dir + "/" + entry.name) if rel_dir else entry.name
            if entry.name.startswith(".") or entry.name == "node_modules":
                continue
            try:
                if entry.is_symlink():
                    skipped.append({"path": rel, "reason": "symlink"})
                elif entry.is_dir(follow_symlinks=False):
                    real = os.path.realpath(entry.path)
                    if real == root or real.startswith(root + os.sep):
                        stack.append((rel, entry.path))
                    else:
                        skipped.append({"path": rel, "reason": "outside root"})
                elif entry.is_file(follow_symlinks=False):
                    out.append((rel, entry.path, entry.stat(follow_symlinks=False).st_size))
                else:
                    skipped.append({"path": rel, "reason": "special file"})
            except OSError as exc:
                skipped.append({"path": rel, "reason": "unreadable: %s" % exc.__class__.__name__})
    return sorted(out)


# ---------------------------------------------------------------------------------------- host config

def _path_regex(pattern: str) -> Optional[Pattern[str]]:
    """Netlify/Cloudflare `*` and `:name`, plus the Vercel subset `(.*)`, `(.+)`, `:name*|+|?`."""
    if re.match(r"(?i)https?://", pattern):
        pattern = urlsplit(pattern).path or "/"
    if not pattern.startswith("/"):
        return None
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith(("(.*)", "(.+)"), i):
            out.append(".*" if pattern[i + 1] == "." and pattern[i + 2] == "*" else ".+")
            i += 4
        elif pattern[i] == "*":
            out.append(".*")
            i += 1
        elif pattern[i] == ":" and i + 1 < len(pattern) and (pattern[i + 1].isalpha() or pattern[i + 1] == "_"):
            j = i + 1
            while j < len(pattern) and (pattern[j].isalnum() or pattern[j] == "_"):
                j += 1
            suffix = pattern[j] if j < len(pattern) and pattern[j] in "*+?" else ""
            out.append({"*": ".*", "+": ".+", "?": "[^/]*"}.get(suffix, "[^/]+"))
            i = j + len(suffix)
        elif pattern[i] in "()":
            return None
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def parse_headers_file(text: str, source: str = "_headers") -> List[Dict[str, Any]]:
    """Netlify / Cloudflare Pages `_headers`: unindented path pattern, indented `Name: value` lines."""
    rules: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    for no, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[:1].isspace():
            current = {"pattern": raw.strip(), "headers": [], "source": "%s:%d" % (source, no)}
            rules.append(current)
        elif current is not None:
            name, sep, value = raw.strip().partition(":")
            if sep and name.strip() and not name.startswith("!"):
                current["headers"].append((name.strip().lower(), value.strip()))
    return rules


def parse_redirects_file(text: str, source: str = "_redirects") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Netlify / Cloudflare `_redirects` -> (redirects, rewrites). Status defaults to 301; `!` forces."""
    redirects, rewrites = [], []
    for no, raw in enumerate(text.splitlines(), start=1):
        parts = raw.split()
        if len(parts) < 2 or parts[0].startswith("#"):
            continue
        status, force = 301, False
        if len(parts) > 2:
            m = re.match(r"^(\d{3})(!?)$", parts[2])
            if m:
                status, force = int(m.group(1)), bool(m.group(2))
        entry = {"from": parts[0], "to": parts[1], "status": status, "force": force, "source": "%s:%d" % (source, no)}
        if status == 200:
            rewrites.append(entry)
        elif 300 <= status < 400:
            redirects.append(entry)
    return redirects, rewrites


def _vercel(text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    data = loads_json(text)
    if not isinstance(data, dict):
        return [], [], []
    redirects, rules, rewrites = [], [], []
    for i, r in enumerate(data.get("redirects") or []):
        if isinstance(r, dict) and isinstance(r.get("source"), str) and isinstance(r.get("destination"), str):
            code = r.get("statusCode") if isinstance(r.get("statusCode"), int) else (
                308 if r.get("permanent", True) else 307)
            redirects.append({"from": r["source"], "to": r["destination"], "status": code, "force": True,
                              "source": "vercel.json:redirects[%d]" % i})
    for i, h in enumerate(data.get("headers") or []):
        if isinstance(h, dict) and isinstance(h.get("source"), str):
            pairs = [(str(x.get("key", "")).lower(), str(x.get("value", ""))) for x in h.get("headers") or []
                     if isinstance(x, dict) and x.get("key")]
            rules.append({"pattern": h["source"], "headers": pairs, "source": "vercel.json:headers[%d]" % i})
    for i, r in enumerate(data.get("rewrites") or []):
        if isinstance(r, dict) and isinstance(r.get("source"), str):
            rewrites.append({"from": r["source"], "to": str(r.get("destination", "")),
                             "source": "vercel.json:rewrites[%d]" % i})
    return redirects, rules, rewrites


def _is_catch_all(rewrite: Dict[str, Any]) -> bool:
    rx = _path_regex(rewrite.get("from", ""))
    to = rewrite.get("to", "").split("?")[0]
    return bool(rx and rx.match("/no-such-route-x/y") and (to in ("/", "/index.html") or to.endswith(".html")))


# ---------------------------------------------------------------------------------------- scanning

def scan_build(root: str, *, base_url: Optional[str] = None, url_style: str = "directory", max_pages: int = 5000,
               max_file_bytes: int = 5_242_880) -> BuiltSite:
    """Scan a static build directory (read-only). Raises ValueError/NotADirectoryError on bad input."""
    if url_style not in URL_STYLES:
        raise ValueError("url_style must be one of %s" % ", ".join(URL_STYLES))
    if os.path.islink(root):
        raise ValueError("build root must not be a symlink")
    real = os.path.realpath(root)
    if not os.path.isdir(real):
        raise NotADirectoryError("not a directory: %s" % root)
    site = BuiltSite(root=real, base_url=_check_base(base_url), url_style=url_style)
    overflow = 0
    rewrites: List[Dict[str, Any]] = []
    for rel, full, size in _walk(real, site.skipped):
        if len(site.assets) < MAX_ENTRIES:
            site.assets.add(url_for(rel, None, "preserve"))
        low = rel.lower()
        name = low.rsplit("/", 1)[-1]
        try:
            if low.endswith((".html", ".htm")):
                if low == "200.html":
                    site.spa_fallback = site.spa_fallback or "200.html"
                    continue
                if size > max_file_bytes:
                    site.skipped.append({"path": rel, "reason": "too_large", "size": str(size)})
                    continue
                if low in NOT_FOUND_NAMES:
                    if site.not_found_page is None:
                        site.not_found_page = rel
                        site.not_found_doc = htmlparse.parse_html(decode_html(_read_file(full, max_file_bytes)),
                                                                  path=rel)
                    continue
                if len(site.pages) >= max_pages:
                    overflow += 1
                    continue
                url = url_for(rel, site.base_url, url_style)
                if url in site.pages:
                    site.skipped.append({"path": rel, "reason": "url collision with %s" % site.files[url]})
                    continue
                data = _read_file(full, max_file_bytes)
                doc = htmlparse.parse_html(decode_html(data), path=rel, url=url)
                doc.raw_size = len(data)
                site.pages[url], site.files[url] = doc, rel
            elif low == "robots.txt":
                site.robots_txt = _read_file(full, AUX_MAX_BYTES).decode("utf-8-sig", "replace")
            elif low == "llms.txt":
                site.llms_txt = _read_file(full, AUX_MAX_BYTES).decode("utf-8-sig", "replace")
            elif SITEMAP_NAME.search(name):
                site.sitemap_paths.append(rel)
            elif low == "_headers":
                site.header_rules.extend(parse_headers_file(_read_file(full, AUX_MAX_BYTES).decode("utf-8", "replace")))
                site.config_files.append(rel)
            elif low == "_redirects":
                reds, rws = parse_redirects_file(_read_file(full, AUX_MAX_BYTES).decode("utf-8", "replace"))
                site.redirects.extend(reds)
                rewrites.extend(rws)
                site.config_files.append(rel)
            elif low == "vercel.json":
                reds, rules, rws = _vercel(_read_file(full, AUX_MAX_BYTES).decode("utf-8", "replace"))
                site.redirects.extend(reds)
                site.header_rules.extend(rules)
                rewrites.extend(rws)
                site.config_files.append(rel)
        except (OSError, ValueError) as exc:
            site.skipped.append({"path": rel, "reason": "unreadable: %s" % str(exc)[:80]})
    if overflow:
        site.skipped.append({"path": ".", "reason": "max_pages %d reached; %d pages not scanned" % (max_pages, overflow)})
    for rw in rewrites:
        if site.spa_fallback is None and _is_catch_all(rw):
            site.spa_fallback = rw["source"]
    _apply_header_rules(site)
    return site


def _apply_header_rules(site: BuiltSite) -> None:
    compiled = [(_path_regex(r["pattern"]), r) for r in site.header_rules]
    for url in site.pages:
        path = urlsplit(url).path if site.base_url else url
        if site.base_url:
            prefix = urlsplit(site.base_url).path.rstrip("/")
            path = path[len(prefix):] if prefix and path.startswith(prefix) else path
        merged: Dict[str, str] = {}
        for rx, rule in compiled:
            if rx is not None and rx.match(path):
                for name, value in rule["headers"]:
                    merged[name] = merged[name] + "\n" + value if name in merged else value
        if merged:
            site.headers[url] = merged


def site_from_fetches(results: List[Dict[str, Any]], *, base_url: str) -> BuiltSite:
    """BuiltSite from live fetch records (fetch.FetchResult.as_record(): url, requested_url, status, headers,
    text, content_type, redirect_chain of 3xx hops, too_large; optional redirect_target for unfollowed hops)."""
    site = BuiltSite(root=None, base_url=_check_base(base_url), url_style="preserve")
    for r in results:
        url = r.get("url") or r.get("requested_url")
        if not url:
            continue
        chain = [dict(h) for h in (r.get("redirect_chain") or []) if isinstance(h, dict) and h.get("url")]
        status = r.get("status")
        headers = {str(k).lower(): str(v) for k, v in (r.get("headers") or {}).items()}
        for hop in chain:
            site.status.setdefault(hop["url"], int(hop.get("status") or 0))
        if chain:
            final = r.get("redirect_target") or url if isinstance(status, int) and 300 <= status < 400 else url
            site.redirects.append({"from": chain[0]["url"], "to": final, "status": int(chain[0].get("status") or 0),
                                   "chain": chain, "source": "live", "force": True})
        if isinstance(status, int):
            site.status[url] = status
        if headers:
            site.headers[url] = headers
        text = r.get("text")
        path = urlsplit(url).path
        ok = isinstance(status, int) and 200 <= status < 300
        if path == "/robots.txt":
            site.robots_txt = text if ok else site.robots_txt
        elif path == "/llms.txt":
            site.llms_txt = text if ok else site.llms_txt
        elif SITEMAP_NAME.search(path.rsplit("/", 1)[-1]):
            site.sitemap_paths.append(url)
        elif r.get("too_large"):
            site.skipped.append({"path": url, "reason": "too_large"})
        elif ok and isinstance(text, str):
            ctype = str(r.get("content_type") or headers.get("content-type", "")).lower()
            if "html" in ctype or (not ctype and "<html" in text[:2048].lower()):
                doc = htmlparse.parse_html(text, url=url)
                site.pages[url], site.files[url] = doc, url
    return site


# ---------------------------------------------------------------------------------------- lookups

class _Index:
    """URL resolution over a BuiltSite (page keys, assets, redirects, live status)."""

    def __init__(self, site: BuiltSite) -> None:
        self.site = site
        self.origin = _origin(site.base_url) if site.base_url else PSEUDO_ORIGIN
        self.base_path = urlsplit(site.base_url).path.rstrip("/") if site.base_url else ""
        self.netloc = urlsplit(self.origin).netloc
        self.exact: Dict[str, str] = {}
        self.loose: Dict[str, str] = {}
        for key in site.pages:
            n = normalize_url(self.absolute(key))
            self.exact.setdefault(n, key)
            self.loose.setdefault(_slashless(n), key)
        prefix = self.origin + self.base_path
        self.assets = {_slashless(normalize_url(prefix + p)) for p in site.assets}
        self.status = {normalize_url(u): s for u, s in site.status.items()}
        self.rules = [(_path_regex(r["from"]) if "://" not in r["from"] else None, r) for r in site.redirects]
        nf = site.not_found_page
        self.not_found = normalize_url(self.absolute(url_for(nf, site.base_url, site.url_style))) if nf else None

    def absolute(self, key: str) -> str:
        return key if "://" in key else self.origin + key

    def internal(self, url: str) -> bool:
        parts = urlsplit(normalize_url(url))
        return parts.scheme in ("http", "https") and parts.netloc == self.netloc

    def key_of(self, url: str) -> Optional[str]:
        n = normalize_url(url)
        bare = urlunsplit(urlsplit(n)._replace(query=""))
        for cand in dict.fromkeys((n, bare)):
            if cand in self.exact:
                return self.exact[cand]
            path = urlsplit(cand).path
            variants = [cand]
            if self.site.url_style == "directory" and path.endswith(("/index.html", "/index.htm")):
                variants.append(cand[: cand.rfind("/") + 1])
            elif self.site.url_style == "clean" and path.endswith((".html", ".htm")):
                variants.append(cand[: cand.rfind(".")])
            elif self.site.url_style == "preserve" and path.endswith("/"):
                variants.append(cand + "index.html")
            for v in variants:
                if v in self.exact:
                    return self.exact[v]
                if _slashless(v) in self.loose:
                    return self.loose[_slashless(v)]
        return None

    def is_asset(self, url: str) -> bool:
        n = normalize_url(url)
        return _slashless(urlunsplit(urlsplit(n)._replace(query=""))) in self.assets

    def _site_path(self, url: str) -> str:
        path = urlsplit(normalize_url(url)).path
        if self.base_path and path.startswith(self.base_path):
            path = path[len(self.base_path):] or "/"
        return path

    def redirect_of(self, url: str) -> Optional[Dict[str, Any]]:
        n = normalize_url(url)
        path = self._site_path(url)
        for rx, rule in self.rules:
            if rx is None:
                hit = normalize_url(rule["from"]) == n
            else:
                hit = bool(rx.match(path) or rx.match(_slashless(path)) or rx.match(path + "/"))
                if hit and not rule.get("force") and self.key_of(url):
                    hit = False   # Netlify-style shadowing: an existing file wins unless forced
            if hit:
                return rule
        return None

    def status_of(self, url: str) -> Optional[int]:
        return self.status.get(normalize_url(url))

    def comparable(self, url: Optional[str]) -> Optional[str]:
        """Without a base URL, absolute URLs compare by path only (host unknown offline)."""
        if url is None or self.site.base_url or self.site.status:
            return url
        try:
            parts = urlsplit(url)
        except ValueError:
            return url
        if parts.netloc:
            return self.origin + (parts.path or "/") + ("?" + parts.query if parts.query else "")
        return url

    def canonical(self, key: str) -> Optional[str]:
        """Comparable resolved canonical of a page key."""
        return self.comparable(canonical_of(self.site, key, self))


def _resolve(href: str, page_abs: str, base_href: Optional[str]) -> Optional[str]:
    try:
        base = urljoin(page_abs, base_href) if base_href else page_abs
        if urlsplit(base).scheme not in ("http", "https"):
            base = page_abs
        return urljoin(base, href.strip())
    except ValueError:
        return None


def _header_canonicals(value: str) -> List[str]:
    out = []
    for m in re.finditer(r"<([^>]*)>\s*((?:;[^,<]*)*)", value or ""):
        if re.search(r"rel\s*=\s*\"?[^\";]*\bcanonical\b", m.group(2), re.I):
            out.append(m.group(1).strip())
    return out


def canonical_declarations(site: BuiltSite, key: str) -> List[Tuple[str, Optional[int], str]]:
    """[(href, line, source)] from <link rel=canonical> in the head and Link headers (html|header)."""
    doc = site.pages[key]
    out: List[Tuple[str, Optional[int], str]] = [(h, line, "html") for h, line in doc.canonicals]
    out.extend((h, None, "header") for h in _header_canonicals(site.headers.get(key, {}).get("link", "")))
    return out


def canonical_of(site: BuiltSite, key: str, _idx: Optional[_Index] = None) -> Optional[str]:
    """First declared canonical, resolved to an absolute URL (None when absent or unresolvable)."""
    if key not in site.pages:
        return None
    idx = _idx or _Index(site)
    for href, _, _ in canonical_declarations(site, key):
        if href:
            return _resolve(href, idx.absolute(key), site.pages[key].base_href)
    return None


def page_directives(site: BuiltSite, key: str, bot: str = "googlebot") -> Dict[str, Any]:
    """Effective robots directives for a page: meta tags plus X-Robots-Tag (config or live)."""
    doc = site.pages[key]
    value = site.headers.get(key, {}).get("x-robots-tag")
    return directives.effective(doc.meta, directives.parse_x_robots([value]) if value else {}, bot)


def is_noindex(site: BuiltSite, key: str) -> bool:
    """True when the page is noindex for Googlebot from any source."""
    return bool(page_directives(site, key)["noindex"])


def sitemap_inputs(site: BuiltSite) -> Dict[str, Any]:
    """Inputs for sitemaps.check_sitemaps: normalized `site_urls` and an `indexable(url)` callable.

    `indexable` returns True, or a reason string: "missing", "noindex", "redirects", "canonicalized to <url>".
    """
    idx = _Index(site)
    urls = {normalize_url(idx.absolute(k)) for k in site.pages}
    if not site.base_url:
        urls = {urlsplit(u).path or "/" for u in urls}
    noindex = {k: is_noindex(site, k) for k in site.pages}

    def indexable(url: str) -> Union[bool, str]:
        absolute = idx.absolute(url) if url.startswith("/") else url
        if idx.redirect_of(absolute) or (idx.status_of(absolute) or 200) in REDIRECT_STATUSES:
            return "redirects"
        key = idx.key_of(absolute)
        if key is None:
            return "missing"
        if noindex[key]:
            return "noindex"
        canon = idx.canonical(key)
        if canon and not same_ignoring_slash(canon, idx.absolute(key)):
            return "canonicalized to %s" % canonical_of(site, key, idx)
        return True

    return {"site_urls": urls, "indexable": indexable}


def _declared_origin(site: BuiltSite) -> Optional[str]:
    """Most common origin of absolute canonical and hreflang hrefs (used when no base URL is given)."""
    counts: Dict[str, int] = {}
    for doc in site.pages.values():
        for href in [h for h, _ in doc.canonicals] + [h for _, h, _ in doc.hreflang]:
            try:
                parts = urlsplit(href.strip())
            except ValueError:
                continue
            if parts.scheme.lower() in ("http", "https") and parts.netloc and "@" not in parts.netloc:
                origin = _origin(href.strip())
                counts[origin] = counts.get(origin, 0) + 1
    return min(counts, key=lambda o: (-counts[o], o)) if counts else None


def hreflang_inputs(site: BuiltSite) -> Dict[str, Any]:
    """Inputs for hreflang.check_hreflang: pages keyed by absolute URL, canonical_of and noindex_of callables.

    Without a base URL (offline), page URLs take the origin the pages declare in their canonical and
    hreflang links, so absolute hreflang targets can be matched to built pages.
    """
    idx = _Index(site)
    origin = None if site.base_url or site.status else _declared_origin(site)

    def outward(url: Optional[str]) -> Optional[str]:
        if origin and url and url.startswith(PSEUDO_ORIGIN):
            return origin + url[len(PSEUDO_ORIGIN):]
        return url

    def inward(url: str) -> str:
        if origin and normalize_url(url).startswith(normalize_url(origin + "/")):
            return PSEUDO_ORIGIN + urlsplit(url).path + ("?" + urlsplit(url).query if urlsplit(url).query else "")
        return url

    pages = {outward(idx.absolute(k)): doc for k, doc in site.pages.items()}

    def canon(url: str) -> Optional[str]:
        key = idx.key_of(inward(url))
        return outward(idx.canonical(key)) if key else None

    def noindex(url: str) -> bool:
        key = idx.key_of(inward(url))
        return bool(key and is_noindex(site, key))

    return {"pages": pages, "canonical_of": canon, "noindex_of": noindex}


def _first_page(url: str) -> Optional[str]:
    """URL of page 1 when `url` is page >= 2 of a paginated series (path /page/N or ?page=N)."""
    parts = urlsplit(url)
    m = _PAGE_PATH.match(parts.path)
    if m and int(m.group(2)) >= 2:
        return urlunsplit(parts._replace(path=m.group(1), fragment=""))
    query = parse_qsl(parts.query, keep_blank_values=True)
    hits = [v for k, v in query if k.lower() in _PAGE_PARAMS]
    if hits and hits[0].isdigit() and int(hits[0]) >= 2:
        rest = [(k, v) for k, v in query if k.lower() not in _PAGE_PARAMS]
        return urlunsplit(parts._replace(query=urlencode(rest), fragment=""))
    return None


def launch_host_problem(host: str, base_host: Optional[str]) -> Optional[str]:
    """Why a host looks like a local, staging or preview origin (None for production-looking hosts)."""
    h = (host or "").lower().strip("[]").rstrip(".")
    base = (base_host or "").lower().strip("[]")
    if not h or h == base:
        return None
    if h == "localhost" or h.endswith(_LOCAL_SUFFIX):
        return "local host"
    try:
        ip = ipaddress.ip_address(h)
        return "local or private address" if (ip.is_loopback or ip.is_private or ip.is_unspecified
                                              or ip.is_link_local) else None
    except ValueError:
        pass
    for suffix in _PREVIEW_SUFFIX:
        if h.endswith(suffix) and not base.endswith(suffix):
            return "preview host"
    if _STAGING_LABEL.search(h.split(".")[0]) or "staging" in h.split(".")[:-1]:
        return "staging host"
    return None


def _robots_blocks_all(text: Optional[str]) -> bool:
    """Minimal grouping: does the `User-agent: *` group disallow `/` with no allow rule?"""
    if not text:
        return False
    groups: List[Tuple[List[str], List[Tuple[str, str]]]] = []
    agents: List[str] = []
    rules: List[Tuple[str, str]] = []
    for raw in re.split(r"\r\n|\r|\n", text.lstrip("\ufeff")):
        line = raw.split("#", 1)[0].strip()
        name, sep, value = line.partition(":")
        name, value = name.strip().lower(), value.strip()
        if not sep:
            continue
        if name == "user-agent":
            if rules:
                groups.append((agents, rules))
                agents, rules = [], []
            agents.append(value.lower())
        elif name in ("allow", "disallow") and agents:
            rules.append((name, value))
    if agents:
        groups.append((agents, rules))
    star = [r for a, rs in groups if "*" in a for r in rs]
    return any(n == "disallow" and v in ("/", "/*") for n, v in star) and not any(n == "allow" and v for n, v in star)


# ---------------------------------------------------------------------------------------- page checks

class _Checks:
    """Shared state for one check run: catalog, severities, index, thresholds and output."""

    def __init__(self, site: BuiltSite, catalog: Optional[RuleCatalog], profile: str = "default",
                 expect_indexable: bool = False, today: Optional[date] = None) -> None:
        self.site, self.cat = site, catalog or default_catalog()
        self.profile, self.expect = profile, expect_indexable
        self.today = today or date.today()
        self.idx = _Index(site)
        self.th = thresholds()
        self.out: List[Finding] = []
        self._dirs: Dict[str, Dict[str, Any]] = {}

    def emit(self, rule: str, message: str, **kw: Any) -> None:
        if self.cat.get(rule).status != "v1":
            return
        sev = self.cat.severity_for(rule, profile=self.profile, expect_indexable=self.expect)
        self.out.append(make(rule, message, catalog=self.cat, severity=sev, **kw))

    def where(self, key: str) -> Dict[str, Any]:
        url = self.idx.absolute(key) if self.site.base_url or "://" in key else key
        return {"file": self.site.files.get(key) if self.site.root else None, "url": url}

    def directives(self, key: str) -> Dict[str, Any]:
        if key not in self._dirs:
            self._dirs[key] = page_directives(self.site, key)
        return self._dirs[key]

    def th_get(self, block: str, name: str, default: Any) -> Any:
        value = self.th.get(block)
        return value.get(name, default) if isinstance(value, dict) else default


def check_pages(site: BuiltSite, catalog: Optional[RuleCatalog] = None, *, expect_indexable: bool = False,
                profile: str = "default", today: Optional[date] = None,
                sitemap_urls: Optional[Set[str]] = None) -> List[Finding]:
    """Per-page and site-level page rules: IDX, CANON001-003/006/008, META (not 003/005/006), HDG, REND,
    IMG, LINK004, SPAM, LOCAL002, LAUNCH001/003/004/005, HTTP001-003/005/007/008.

    `audit-build` composition (cli): check_pages, check_duplicates, link_graph + check_links,
    sitemaps.check_sitemaps(**sitemap_inputs(site)), hreflang.check_hreflang(**hreflang_inputs(site)),
    perf.check_static per page. LAUNCH001/LAUNCH005 run only with profile "launch".
    """
    ck = _Checks(site, catalog, profile, expect_indexable, today)
    for key in sorted(site.pages):
        _page(ck, key)
    _site_level(ck, sitemap_urls)
    return ck.out


def _page(ck: _Checks, key: str) -> None:
    site, doc, idx = ck.site, ck.site.pages[key], ck.idx
    loc = ck.where(key)
    page_abs = idx.absolute(key)
    eff = ck.directives(key)
    redirect_page = bool(doc.meta_refresh and re.search(r"url\s*=", doc.meta_refresh, re.I))
    search_facing = not eff["noindex"] and not redirect_page
    # ---- directives
    if eff["noindex"]:
        ck.emit("IDX001", "Page is noindex (%s)." % ", ".join(eff["noindex_sources"]), key="noindex",
                evidence={"observed": eff["noindex_sources"], "expected": "indexable"}, **loc)
        if eff["header_noindex"] and key not in site.status:
            rules = [r["source"] for r in site.header_rules
                     if any(n == "x-robots-tag" for n, _ in r["headers"])]
            ck.emit("IDX004", "X-Robots-Tag noindex applied by the host headers config.", key="xrobots-config",
                    evidence={"observed": site.headers.get(key, {}).get("x-robots-tag", ""), "config": rules}, **loc)
    if eff["conflicts"]:
        ck.emit("IDX002", "Conflicting robots directives: %s." % "; ".join(eff["conflicts"]), key="conflict",
                evidence={"observed": eff["conflicts"], "sources": eff["sources"]}, **loc)
    if eff["ignored"]:
        ck.emit("IDX003", "Directives Google ignores: %s." % ", ".join(eff["ignored"]), key="ignored",
                evidence={"observed": eff["ignored"]}, **loc)
    if eff["unavailable_after"]:
        when = directives.parse_date(eff["unavailable_after"])
        if when is not None and when.date() < ck.today:
            ck.emit("IDX005", "unavailable_after date %s is in the past." % eff["unavailable_after"],
                    key="unavailable_after", evidence={"observed": eff["unavailable_after"],
                                                       "today": ck.today.isoformat()}, **loc)
    # ---- canonical
    decls = canonical_declarations(site, key)
    if not decls and search_facing:
        ck.emit("CANON001", "No rel=canonical link or Link header.", key="canonical-missing", **loc)
    if len(decls) > 1:
        ck.emit("CANON002", "Page declares %d canonical links." % len(decls), key="canonical-count",
                line=decls[0][1], evidence={"observed": [d[0] for d in decls],
                                            "expected": "exactly one absolute canonical"}, **loc)
    for href, line, source in decls:
        problem = _canonical_problem(href)
        if problem:
            ck.emit("CANON003", "Canonical %s: %s." % (problem, href[:120] or "(empty)"), line=line,
                    key="canonical-invalid:" + href[:200], evidence={"observed": href, "source": source}, **loc)
    real_canon = canonical_of(site, key, idx) if decls else None
    canon = idx.comparable(real_canon)
    if canon and search_facing:
        first = _first_page(page_abs)
        if first and same_ignoring_slash(canon, first):
            ck.emit("CANON006", "Paginated page canonicalizes to page 1 (%s)." % canon, key="paginated",
                    evidence={"observed": canon, "expected": "self-referencing canonical"}, **loc)
        if normalize_url(canon) != normalize_url(page_abs) and same_ignoring_slash(canon, page_abs):
            ck.emit("CANON008", "Canonical differs from the mapped URL only by a trailing slash.",
                    key="canonical-slash", evidence={"observed": canon, "mapped": page_abs}, **loc)
    # ---- metadata
    titles = doc.titles
    title = titles[0] if titles else ""
    if len(titles) > 1:
        ck.emit("META007", "%d title elements in the head." % len(titles), key="title-count",
                evidence={"observed": titles}, **loc)
    if search_facing:
        if not title:
            ck.emit("META001", "Missing or empty title element.", key="title-missing", **loc)
        elif title.casefold() in _PLACEHOLDER_TITLES or _TEMPLATE_TOKEN.search(title):
            ck.emit("META002", "Placeholder or framework-default title: %s" % title, key="title-placeholder",
                    evidence={"observed": title}, **loc)
        if title and len(title) > int(ck.th.get("title_hint_chars", 60)):
            ck.emit("META011", "Title is %d characters; display may truncate it (Google sets no limit)." % len(title),
                    key="title-length", evidence={"observed": len(title)}, confidence="low", **loc)
        years = _obsolete_years([title] + [h for lvl, h, _ in doc.headings if lvl == 1], ck)
        if years:
            ck.emit("META012", "Obsolete year in title or H1: %s." % ", ".join(years), key="year",
                    evidence={"observed": years, "today": ck.today.isoformat()}, confidence="medium", **loc)
        if not any(v.strip() for v in doc.meta.get("description", [])):
            ck.emit("META004", "Missing meta description.", key="description-missing", **loc)
        missing_og = [k for k in ("og:title", "og:image", "og:url") if not any(v.strip() for v in doc.meta.get(k, []))]
        if missing_og:
            ck.emit("META010", "Missing Open Graph basics: %s." % ", ".join(missing_og), key="og",
                    evidence={"missing": missing_og}, **loc)
        og_url = next((v.strip() for v in doc.meta.get("og:url", []) if v.strip()), None)
        if og_url and real_canon and not same_ignoring_slash(_resolve(og_url, page_abs, None) or og_url, real_canon):
            ck.emit("META014", "og:url differs from the canonical URL.", key="og-url",
                    evidence={"observed": og_url, "expected": real_canon}, **loc)
        _headings(ck, key, doc, loc)
        _rendering(ck, doc, loc)
        _images(ck, doc, loc)
    if doc.kind == "html" and not doc.lang:
        ck.emit("META008", "Missing html lang attribute.", key="lang", **loc)
    if doc.kind == "html" and not _viewport_ok(doc.meta.get("viewport", [])):
        ck.emit("META009", "Missing or invalid viewport meta.", key="viewport",
                evidence={"observed": doc.meta.get("viewport", [])}, **loc)
    if doc.meta.get("keywords"):
        ck.emit("META013", "meta keywords present; Google does not use it.", key="keywords", **loc)
    # ---- links, alternates, spam, local, size, transport
    _page_links(ck, doc, loc, page_abs, search_facing)
    md_missing = []
    for alt in doc.alternates:
        href = alt.get("href") or ""
        if alt.get("rel") != "alternate" or not (alt.get("type") in ("text/markdown", "text/x-markdown")
                                                  or urlsplit(href).path.lower().endswith((".md", ".mdx"))):
            continue
        target = _resolve(href, page_abs, doc.base_href) if href else None
        if not target or (idx.internal(target) and not site.status and idx.key_of(target) is None
                          and not idx.is_asset(target)):
            md_missing.append(href or "(empty href)")
    if md_missing:
        ck.emit("AGENT005", "Markdown alternate declared but not in the build: %s." % ", ".join(md_missing[:3]),
                key="md-alternate", evidence={"observed": md_missing[:10]}, **loc)
    if redirect_page:
        ck.emit("SPAM002", "Meta refresh redirect: %s" % doc.meta_refresh, key="meta-refresh",
                evidence={"observed": doc.meta_refresh}, **loc)
    _spam(ck, doc, loc)
    limit = int(ck.th.get("googlebot_html_bytes", 2097152))
    if doc.raw_size > limit:
        ck.emit("HTTP005", "HTML is %d bytes uncompressed; Googlebot reads the first %d." % (doc.raw_size, limit),
                key="size", evidence={"observed": doc.raw_size, "limit": limit}, **loc)
    _mixed_content(ck, doc, loc, page_abs)
    _launch_urls(ck, key, doc, loc, page_abs)


def _canonical_problem(href: str) -> Optional[str]:
    if not href.strip():
        return "is empty"
    if re.search(r"[\x00-\x20\x7f]", href.strip()):
        return "contains spaces or control characters"
    try:
        parts = urlsplit(href.strip())
        parts.port
    except ValueError:
        return "is malformed"
    if not parts.scheme:
        return "is relative"
    if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
        return "is not an absolute http(s) URL"
    if "@" in parts.netloc:
        return "contains credentials"
    if parts.fragment:
        return "contains a fragment"
    return None


def _obsolete_years(texts: List[str], ck: _Checks) -> List[str]:
    window = int(ck.th_get("metadata", "obsolete_year_window", 5))
    now = ck.today.year
    found = []
    for text in texts:
        years = [int(m.group(1)) for m in _YEAR.finditer(text or "")]
        if any(y >= now for y in years):
            continue
        for m in _YEAR.finditer(text or ""):
            y = int(m.group(1))
            if now - window <= y < now and not _YEAR_HISTORIC.search(text[: m.start()]):
                found.append(str(y))
    return sorted(set(found))


def _viewport_ok(values: List[str]) -> bool:
    for value in values:
        low = value.lower().replace(" ", "")
        if "width=device-width" in low or ("initial-scale=" in low and "width=" not in low):
            return True
    return False


def _headings(ck: _Checks, key: str, doc: PageDoc, loc: Dict[str, Any]) -> None:
    levels = [lvl for lvl, _, _ in doc.headings]
    if 1 not in levels:
        ck.emit("HDG001", "No H1 heading.", key="h1", **loc)
    skips = ["H%d->H%d" % (a, b) for a, b in zip(levels, levels[1:]) if b > a + 1]
    if skips:
        ck.emit("HDG002", "Skipped heading levels: %s." % ", ".join(skips[:3]), key="heading-skip",
                evidence={"observed": skips[:3], "count": len(skips)}, **loc)
    min_words = int(ck.th_get("headings", "content_min_words", 300))
    if not levels and doc.word_count >= min_words:
        ck.emit("HDG003", "%d words of content without any heading." % doc.word_count, key="no-headings",
                evidence={"words": doc.word_count, "threshold": min_words}, **loc)


def _rendering(ck: _Checks, doc: PageDoc, loc: Dict[str, Any]) -> None:
    csr = ck.th.get("csr") if isinstance(ck.th.get("csr"), dict) else {}
    root_max = int(csr.get("root_text_max", 50))
    words_max = int(csr.get("page_words_max", 200))
    visible_min = int(csr.get("visible_text_min", 100))
    visible = len(doc.visible_text)
    scripted = [s for s in doc.scripts if s.get("src") or s.get("module")]
    inline = sum(int(s.get("length", 0)) for s in doc.scripts if not s.get("src"))
    shell = False
    if doc.app_root_text_len is not None and doc.app_root_text_len <= root_max and doc.word_count < words_max:
        shell = True
        ck.emit("REND001", "App root holds %d characters of server HTML text; content is rendered client-side."
                % doc.app_root_text_len, key="csr-shell", evidence={"root_text_chars": doc.app_root_text_len,
                                                                    "words": doc.word_count}, **loc)
    elif doc.app_root_text_len is None and visible < visible_min and scripted:
        shell = True
        ck.emit("REND001", "Only %d characters of visible server HTML text next to %d scripts." % (
            visible, len(scripted)), key="csr-shell", confidence="medium",
            evidence={"visible_chars": visible, "scripts": len(scripted)}, **loc)
    ratio = float(csr.get("inline_script_ratio", 5))
    floor = int(csr.get("inline_script_min_chars", 2000))
    if not shell and doc.word_count < words_max and inline >= max(floor, ratio * visible):
        ck.emit("REND002", "Inline scripts (%d chars) dwarf the server HTML text (%d chars)." % (inline, visible),
                key="thin-html", confidence="medium", evidence={"inline_script_chars": inline,
                                                                "visible_chars": visible}, **loc)
    nos_min = int(csr.get("noscript_min_chars", 200))
    if doc.noscript_text_len >= nos_min and doc.noscript_text_len > visible:
        ck.emit("REND003", "%d characters of text appear only inside noscript." % doc.noscript_text_len,
                key="noscript", evidence={"noscript_chars": doc.noscript_text_len, "visible_chars": visible}, **loc)
    hashes = [l["href"].strip() for l in doc.links if (l.get("href") or "").strip().startswith(("#/", "#!"))]
    if hashes:
        ck.emit("REND004", "%d links use hash-fragment routes." % len(hashes), key="hash-routes",
                line=next(l["line"] for l in doc.links if (l.get("href") or "").strip() in hashes),
                evidence={"observed": hashes[:10], "count": len(hashes)}, **loc)


def _images(ck: _Checks, doc: PageDoc, loc: Dict[str, Any]) -> None:
    missing = [i for i in doc.images if i["alt"] is None and not i.get("decorative")]
    if missing:
        ck.emit("IMG001", "%d images without an alt attribute." % len(missing), key="img-alt", line=missing[0]["line"],
                evidence={"observed": [i["src"] for i in missing][:10], "count": len(missing)}, **loc)
    weak = [i["alt"] for i in doc.images if i["alt"] and (
        _FILENAME_ALT.match(i["alt"].strip())
        or (i["alt"].count(",") >= 4 and not re.search(r"[.!?]", i["alt"])))]
    if weak:
        ck.emit("IMG002", "%d alt texts look like file names or keyword lists." % len(weak), key="img-alt-weak",
                evidence={"observed": weak[:10]}, confidence="medium", **loc)


def _page_links(ck: _Checks, doc: PageDoc, loc: Dict[str, Any], page_abs: str, search_facing: bool) -> None:
    bad = []
    for link in doc.links:
        href = (link.get("href") or "").strip()
        if link.get("href") is None:
            if link.get("onclick") or (link.get("role") or "").lower() == "link":
                bad.append("(no href)")
        elif href.lower().startswith("javascript:") or (href == "#" and link.get("onclick")):
            bad.append(href[:80])
    if bad:
        ck.emit("LINK004", "%d links are not crawlable (javascript:, missing href)." % len(bad), key="non-crawlable",
                evidence={"observed": bad[:10], "count": len(bad)}, **loc)
    gbp = [l["href"] for l in doc.links if _gbp_link(l.get("href") or "")]
    text_hit = _GBP_TEXT.search(doc.visible_text)
    if gbp or text_hit:
        ck.emit("LOCAL002", "Links or text refer to retired Google Business Profile features.", key="gbp",
                evidence={"links": gbp[:10], "text": text_hit.group(0) if text_hit else None}, **loc)


def _gbp_link(href: str) -> bool:
    try:
        host = (urlsplit(href.strip()).hostname or "").lower()
    except ValueError:
        return False
    return host == "business.site" or host.endswith(".business.site")


def _spam(ck: _Checks, doc: PageDoc, loc: Dict[str, Any]) -> None:
    for script in doc.scripts:
        text = script.get("inline_text") or ""
        if script.get("src") or not _PUSHSTATE.search(text):
            continue
        reasons = [name for name, rx in (("popstate trap", _POPSTATE), ("on load", _ONLOAD)) if rx.search(text)]
        if not reasons and not _USER_EVENT.search(text):
            reasons.append("no user-event handler")
        if reasons:
            ck.emit("SPAM001", "Inline script calls history.pushState (%s)." % ", ".join(reasons), key="history",
                    line=script.get("line"), confidence="medium", evidence={"signals": reasons}, **loc)
            return


def _mixed_content(ck: _Checks, doc: PageDoc, loc: Dict[str, Any], page_abs: str) -> None:
    if urlsplit(page_abs).scheme != "https" or (not ck.site.base_url and not ck.site.status):
        return
    insecure = sorted({r["url"].strip() for r in doc.resources if r["url"].strip().lower().startswith("http://")})
    if insecure:
        ck.emit("HTTP007", "HTTPS page loads %d subresources over http (mixed content)." % len(insecure),
                key="mixed-content", evidence={"observed": insecure[:10]}, **loc)


def _launch_urls(ck: _Checks, key: str, doc: PageDoc, loc: Dict[str, Any], page_abs: str) -> None:
    base_host = urlsplit(ck.site.base_url).hostname if ck.site.base_url else None
    hits = []
    candidates = [("canonical", h) for h, _, _ in canonical_declarations(ck.site, key)]
    candidates += [("og:url", v) for v in doc.meta.get("og:url", [])]
    candidates += [("hreflang", h) for _, h, _ in doc.hreflang]
    candidates += [("json-ld", u) for block in doc.jsonld for u in _URL_IN_TEXT.findall(block.get("raw", ""))]
    for where, url in candidates:
        try:
            host = urlsplit(url.strip()).hostname
        except ValueError:
            continue
        reason = launch_host_problem(host or "", base_host)
        if reason:
            hits.append({"where": where, "url": url.strip()[:200], "reason": reason})
    if hits:
        ck.emit("LAUNCH003", "%d URLs point at local, staging or preview hosts." % len(hits), key="staging-urls",
                evidence={"observed": hits[:10], "expected": "production origin"}, **loc)


def _site_level(ck: _Checks, sitemap_urls: Optional[Set[str]]) -> None:
    site = ck.site
    base_loc = {"url": site.base_url + "/" if site.base_url else None}
    if site.spa_fallback:
        ck.emit("REND005", "SPA fallback (%s) serves the app shell for unknown routes." % site.spa_fallback,
                key="spa-fallback", file=site.spa_fallback.split(":")[0] if site.root else None,
                evidence={"observed": site.spa_fallback}, **base_loc)
    limit = int(ck.th.get("googlebot_html_bytes", 2097152))
    for skip in site.skipped:
        size = int(skip.get("size") or 0) if str(skip.get("size") or "").isdigit() else 0
        if skip.get("reason") == "too_large" and skip["path"].lower().endswith((".html", ".htm")) and size > limit:
            ck.emit("HTTP005", "HTML file of %s bytes was too large to scan (Googlebot reads the first %d)." % (
                skip.get("size", "?"), limit), key="size", file=skip["path"], evidence={"observed": skip.get("size")})
    _live_http(ck)
    _config_redirects(ck)
    _launch_site(ck, sitemap_urls, base_loc)


def _live_http(ck: _Checks) -> None:
    site = ck.site
    for url in sorted(site.status):
        code = site.status[url]
        if _aux_resource(url):
            continue   # robots.txt, llms.txt, sitemaps and /.well-known/ files have their own rules
        if code in (401, 403, 429):
            ck.emit("HTTP008", "Audit crawler received HTTP %d." % code, key="blocked", url=url,
                    evidence={"observed": code})
        elif code >= 400:
            ck.emit("HTTP001", "Page returns HTTP %d." % code, key="status", url=url, evidence={"observed": code})
    insecure = sorted(k for k in site.pages if urlsplit(k).scheme == "http"
                      and not launch_host_problem(urlsplit(k).hostname or "", None))
    if insecure:
        ck.emit("HTTP007", "%d pages are served over plain http." % len(insecure), key="plain-http", url=insecure[0],
                affected=len(insecure), sample=insecure)
    for red in site.redirects:
        chain = red.get("chain") or []
        if len(chain) > 1:
            ck.emit("HTTP002", "Redirect chain of %d hops before %s." % (len(chain), red["to"]), key="chain",
                    url=red["from"], evidence={"chain": chain})


def _aux_resource(url: str) -> bool:
    path = urlsplit(url).path.lower()
    name = path.rsplit("/", 1)[-1]
    return (path in ("/robots.txt", "/llms.txt", "/llms-full.txt") or path.startswith("/.well-known/")
            or bool(SITEMAP_NAME.search(name)))


def _config_redirects(ck: _Checks) -> None:
    for red in ck.site.redirects:
        temp = [h["status"] for h in red.get("chain", [])] if red.get("chain") else [red.get("status")]
        temp = [s for s in temp if s in TEMPORARY]
        if temp:
            where = {"url": red["from"]} if "://" in red["from"] else {
                "file": red["source"].split(":")[0] if ck.site.root else None, "url": ck.idx.absolute(red["from"])}
            ck.emit("HTTP003", "Temporary redirect (%s) from %s to %s." % (temp[0], red["from"], red["to"]),
                    key="temporary:" + red["from"], confidence="medium",
                    evidence={"observed": temp, "source": red["source"]}, **where)


def _launch_site(ck: _Checks, sitemap_urls: Optional[Set[str]], base_loc: Dict[str, Any]) -> None:
    site = ck.site
    reasons = []
    if _robots_blocks_all(site.robots_txt):
        reasons.append("robots.txt disallows / for User-agent: *")
    pages = list(site.pages)
    if len(pages) >= 2 and all(ck.directives(k)["noindex"] for k in pages):
        reasons.append("every page is noindex")
    if reasons:
        ck.emit("LAUNCH004", "Site-wide crawl or index block shipped: %s." % "; ".join(reasons), key="sitewide-block",
                file="robots.txt" if site.root and "robots.txt disallows / for User-agent: *" in reasons else None,
                evidence={"observed": reasons}, affected=max(1, len(pages)), **base_loc)
    if ck.profile != "launch":
        return
    home = url_for("index.html", site.base_url, site.url_style) if site.root else (
        (site.base_url or "") + "/")
    key = ck.idx.key_of(ck.idx.absolute(home))
    if key is None:
        ck.emit("LAUNCH001", "No home page found in the build.", key="home", evidence={"missing": ["home page"]},
                **base_loc)
    else:
        doc = site.pages[key]
        missing = []
        if not (doc.titles and doc.titles[0]):
            missing.append("title")
        if not any(v.strip() for v in doc.meta.get("description", [])):
            missing.append("meta description")
        canon = ck.idx.canonical(key)
        if not canon or not same_ignoring_slash(canon, ck.idx.absolute(key)):
            missing.append("self-canonical")
        types = htmlparse.jsonld_types(doc.jsonld)
        if not any("Organization" in t or t in _ORG_TYPES for t in types):
            missing.append("Organization/WebSite JSON-LD")
        if missing:
            ck.emit("LAUNCH001", "Home page lacks: %s." % ", ".join(missing), key="home",
                    evidence={"missing": missing}, **ck.where(key))
    if site.root and site.not_found_page is None:
        ck.emit("LAUNCH005", "No custom 404 page (404.html) in the build.", key="404", **base_loc)
    elif site.not_found_doc is not None:
        nf_url = normalize_url(ck.idx.absolute(url_for(site.not_found_page, site.base_url, site.url_style)))
        problems = []
        if sitemap_urls and any(same_ignoring_slash(u, nf_url) for u in sitemap_urls):
            problems.append("listed in the sitemap")
        if not directives.effective(site.not_found_doc.meta)["noindex"]:
            problems.append("no noindex (indexable if the host serves it with status 200)")
        if problems:
            ck.emit("LAUNCH005", "404 page %s." % " and ".join(problems), key="404", file=site.not_found_page,
                    url=nf_url, confidence="medium", evidence={"observed": problems})


# ---------------------------------------------------------------------------------------- duplicates

def _hreflang_targets(doc: PageDoc, page_abs: str) -> Dict[str, str]:
    out = {}
    for code, href, _ in doc.hreflang:
        target = _resolve(href, page_abs, doc.base_href)
        if target:
            out[_slashless(normalize_url(target))] = code.lower()
    return out


def _lang(doc: PageDoc, page_abs: str) -> str:
    if doc.lang:
        return doc.lang.split("-")[0].lower()
    return _hreflang_targets(doc, page_abs).get(_slashless(normalize_url(page_abs)), "").split("-")[0]


def check_duplicates(site: BuiltSite, catalog: Optional[RuleCatalog] = None) -> List[Finding]:
    """META003/META005 duplicate groups, CANON004 (target state) and CANON005 (incl. shared targets).

    Duplicate groups ignore noindex, meta-refresh, paginated (page >= 2) and canonicalized pages, and
    are suppressed when every pair is a reciprocal hreflang pair in different languages.
    """
    ck = _Checks(site, catalog)
    idx = ck.idx
    candidates = []
    canon_map: Dict[str, Optional[str]] = {}
    for key in sorted(site.pages):
        doc = site.pages[key]
        page_abs = idx.absolute(key)
        canon = idx.canonical(key)
        canon_map[key] = canon
        redirect_page = bool(doc.meta_refresh and re.search(r"url\s*=", doc.meta_refresh, re.I))
        if ck.directives(key)["noindex"] or redirect_page or _first_page(page_abs):
            continue
        if canon and not same_ignoring_slash(canon, page_abs):
            continue
        candidates.append(key)
    for rule, getter, label in (("META003", lambda d: d.titles[0] if d.titles else "", "title"),
                                ("META005", lambda d: next((v for v in d.meta.get("description", []) if v.strip()),
                                                           ""), "description")):
        groups: Dict[str, List[str]] = {}
        for key in candidates:
            value = htmlparse.collapse(getter(site.pages[key])).casefold()
            if value:
                groups.setdefault(value, []).append(key)
        for value, keys in sorted(groups.items()):
            if len(keys) < 2 or _all_reciprocal_languages(site, idx, keys):
                continue
            urls = [ck.where(k)["url"] for k in keys]
            ck.emit(rule, "%d pages share the same %s." % (len(keys), label),
                    key="%s:%s" % (label, hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]),
                    evidence={"observed": value[:200], "pages": len(keys)}, affected=len(keys), sample=urls,
                    **ck.where(keys[0]))
    shared: Dict[str, int] = {}
    for key, canon in canon_map.items():
        if canon and not same_ignoring_slash(canon, idx.absolute(key)):
            shared[_slashless(normalize_url(canon))] = shared.get(_slashless(normalize_url(canon)), 0) + 1
    for key in sorted(site.pages):
        canon = canon_map[key]
        doc = site.pages[key]
        if not canon or _canonical_problem(canon) in ("is malformed", "is empty"):
            continue
        page_abs = idx.absolute(key)
        if same_ignoring_slash(canon, page_abs) or (doc.meta_refresh and re.search(r"url\s*=", doc.meta_refresh, re.I)):
            continue
        reason = None
        if idx.internal(canon):
            target = idx.key_of(canon)
            live = idx.status_of(canon)
            if idx.redirect_of(canon) or (live is not None and 300 <= live < 400):
                reason = "redirects"
            elif live is not None and live != 200:
                reason = "returns HTTP %d" % live
            elif target is None and not (site.status and live is None):
                reason = "missing from the site" if not idx.is_asset(canon) else None
            elif target is not None and ck.directives(target)["noindex"]:
                reason = "noindex"
        if reason:
            ck.emit("CANON004", "Canonical target %s %s." % (canon, reason), key="canonical-target",
                    evidence={"observed": canon, "reason": reason}, **ck.where(key))
            continue
        first = _first_page(page_abs)
        if first and same_ignoring_slash(canon, first):
            continue   # CANON006 covers paginated pages
        count = shared.get(_slashless(normalize_url(canon)), 1)
        ck.emit("CANON005", "Canonical points to a different URL: %s." % canon, key="canonical-other",
                confidence="medium", evidence={"observed": canon, "pages_sharing_target": count}, **ck.where(key))
    return ck.out


def _all_reciprocal_languages(site: BuiltSite, idx: _Index, keys: List[str]) -> bool:
    info = []
    for k in keys:
        page_abs = idx.absolute(k)
        info.append((_slashless(normalize_url(page_abs)), _hreflang_targets(site.pages[k], page_abs),
                     _lang(site.pages[k], page_abs)))
    for i, (u1, t1, l1) in enumerate(info):
        for u2, t2, l2 in info[i + 1:]:
            if not (u2 in t1 and u1 in t2 and l1 and l2 and l1 != l2):
                return False
    return True


# ---------------------------------------------------------------------------------------- link graph

def link_graph(site: BuiltSite) -> Dict[str, Any]:
    """Internal link graph: nodes, edges, in/outlinks, BFS depth from home, orphans, broken, anchors."""
    idx = _Index(site)
    nodes = sorted(site.pages)
    edges: Set[Tuple[str, str]] = set()
    broken, redirected, nofollow = [], [], []
    anchors_total = anchors_generic = 0
    generic_samples: List[str] = []
    for key in nodes:
        doc = site.pages[key]
        page_abs = idx.absolute(key)
        for link in doc.links:
            href = (link.get("href") or "").strip()
            if not href or href.startswith("#") or re.match(r"(?i)(javascript|mailto|tel|data|sms):", href):
                continue
            target = _resolve(href, page_abs, doc.base_href)
            if not target or not idx.internal(target):
                continue
            text = re.sub(r"[^\w\s+]", "", (link.get("text") or "").lower()).strip()
            if text:
                anchors_total += 1
                if text in _GENERIC_ANCHORS:
                    anchors_generic += 1
                    if len(generic_samples) < 10:
                        generic_samples.append(link.get("text") or "")
            item = {"source": key, "href": href[:200], "target": target[:300], "line": link.get("line")}
            if link.get("nofollow"):
                nofollow.append(item)
            dest = idx.key_of(target)
            red = idx.redirect_of(target)
            live = idx.status_of(target)
            if red or (live is not None and 300 <= live < 400):
                redirected.append(dict(item, to=(red or {}).get("to"), status=(red or {}).get("status", live)))
                if red and red.get("to"):
                    final = _resolve(red["to"], target, None)
                    dest = idx.key_of(final) if final else None
            elif live is not None and live >= 400:
                broken.append(dict(item, status=live))
                continue
            elif dest is None:
                if site.status:
                    continue   # live crawl: unfetched targets are unknown, not broken
                if not idx.is_asset(target) or (idx.not_found and normalize_url(target) == idx.not_found):
                    broken.append(item)
                continue
            if dest is not None and dest != key:
                edges.add((key, dest))
    inlinks = {k: 0 for k in nodes}
    outlinks = {k: 0 for k in nodes}
    adjacency: Dict[str, List[str]] = {k: [] for k in nodes}
    for src, dst in sorted(edges):
        inlinks[dst] += 1
        outlinks[src] += 1
        adjacency[src].append(dst)
    home = idx.key_of(idx.absolute(url_for("index.html", site.base_url, site.url_style))) if site.root else (
        idx.key_of((site.base_url or "") + "/") if site.base_url else None)
    depth: Dict[str, Optional[int]] = {k: None for k in nodes}
    if home is not None:
        depth[home] = 0
        queue = [home]
        while queue:
            cur = queue.pop(0)
            for nxt in adjacency[cur]:
                if depth[nxt] is None:
                    depth[nxt] = depth[cur] + 1
                    queue.append(nxt)
    histogram: Dict[str, int] = {}
    for value in depth.values():
        label = "unreachable" if value is None else str(value)
        histogram[label] = histogram.get(label, 0) + 1
    return {"nodes": nodes, "home": home, "edges": [list(e) for e in sorted(edges)], "inlinks": inlinks,
            "outlinks": outlinks, "depth": depth, "depth_histogram": dict(sorted(histogram.items())),
            "orphans": [k for k in nodes if inlinks[k] == 0 and k != home], "broken": broken,
            "redirected": redirected, "nofollow": nofollow,
            "anchors": {"total": anchors_total, "generic": anchors_generic, "generic_samples": generic_samples}}


def check_links(site: BuiltSite, graph: Dict[str, Any], catalog: Optional[RuleCatalog] = None, *,
                sitemap_urls: Optional[Set[str]] = None) -> List[Finding]:
    """LINK001-003 and LINK005-007 from a link_graph() result (LINK004 is per page in check_pages)."""
    ck = _Checks(site, catalog)
    for rule, items, what in (("LINK001", graph["broken"], "broken internal links"),
                              ("LINK006", graph["redirected"], "internal links to redirecting URLs"),
                              ("LINK007", graph["nofollow"], "internal links marked nofollow")):
        by_source: Dict[str, List[Dict[str, Any]]] = {}
        for item in items:
            by_source.setdefault(item["source"], []).append(item)
        for source in sorted(by_source):
            group = by_source[source]
            ck.emit(rule, "%d %s." % (len(group), what), key="links", line=group[0].get("line"),
                    evidence={"observed": sorted({g["target"] for g in group})[:10], "count": len(group)},
                    **ck.where(source))
    if sitemap_urls:
        listed = {ck.idx.key_of(u if "://" in u else ck.idx.absolute(u)) for u in sitemap_urls}
        for key in graph["orphans"]:
            if key in listed:
                ck.emit("LINK002", "Listed in the sitemap but has no internal inlinks.", key="orphan", **ck.where(key))
    max_depth = int(ck.th_get("links", "max_click_depth", 3))
    for key in sorted(graph["depth"]):
        value = graph["depth"][key]
        if value is not None and value > max_depth:
            ck.emit("LINK003", "Page is %d clicks from the home page." % value, key="depth",
                    evidence={"observed": value, "threshold": max_depth}, **ck.where(key))
    anchors = graph["anchors"]
    share = float(ck.th_get("links", "generic_anchor_share", 0.25))
    minimum = int(ck.th_get("links", "generic_anchor_min_links", 10))
    if anchors["total"] >= minimum and anchors["generic"] / float(anchors["total"]) >= share:
        ck.emit("LINK005", "%d of %d internal anchors are generic." % (anchors["generic"], anchors["total"]),
                key="generic-anchors", affected=max(2, anchors["generic"]),
                url=site.base_url + "/" if site.base_url else None,
                evidence={"observed": anchors["generic_samples"], "share": round(anchors["generic"] /
                                                                                  float(anchors["total"]), 3)})
    return ck.out


# ---------------------------------------------------------------------------------------- redirect maps

def parse_redirect_map(path: str) -> List[Dict[str, Any]]:
    """CSV `old_url,new_url[,status]` (optional header row). Malformed rows carry an `error`."""
    text = _read_file(path, 10 * 1024 * 1024).decode("utf-8-sig")
    entries: List[Dict[str, Any]] = []
    reader = csv.reader(io.StringIO(text))
    first = True
    for row in reader:
        line = reader.line_num
        cells = [c.strip() for c in row]
        if not any(cells) or cells[0].startswith("#"):
            continue
        if first and cells[0].lower() in ("old_url", "old", "from", "source", "old url"):
            first = False
            continue
        first = False
        entry: Dict[str, Any] = {"line": line, "old": cells[0], "new": cells[1] if len(cells) > 1 else "",
                                 "status": None, "error": None}
        if len(cells) < 2 or len(cells) > 3:
            entry["error"] = "expected old_url,new_url[,status]"
        elif not all(_map_url_ok(c) for c in cells[:2]):
            entry["error"] = "URLs must be absolute http(s) URLs or paths starting with /"
        elif len(cells) == 3 and cells[2]:
            if cells[2].isdigit() and int(cells[2]) in REDIRECT_STATUSES:
                entry["status"] = int(cells[2])
            else:
                entry["error"] = "status must be one of %s" % ", ".join(map(str, REDIRECT_STATUSES))
        entries.append(entry)
    return entries


def _map_url_ok(value: str) -> bool:
    if value.startswith("/") and not value.startswith("//"):
        return not re.search(r"\s", value)
    try:
        parts = urlsplit(value)
    except ValueError:
        return False
    return parts.scheme in ("http", "https") and bool(parts.netloc) and "@" not in parts.netloc and not re.search(
        r"\s", value)


def _map_key(value: str) -> str:
    parts = urlsplit(normalize_url(value))
    return parts.path + ("?" + parts.query if parts.query else "")


def check_redirects(entries: Iterable[Dict[str, Any]], catalog: Optional[RuleCatalog] = None, *,
                    old_site: Optional[BuiltSite] = None, new_site: Optional[BuiltSite] = None) -> List[Finding]:
    """REDIR001-007 for a parsed redirect map, optionally against old and new builds."""
    site = new_site or old_site or BuiltSite(root=None, base_url=None, url_style="directory")
    ck = _Checks(site, catalog)
    valid: List[Dict[str, Any]] = []
    mapping: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        where = {"url": e.get("old") or None}
        if e.get("error"):
            ck.emit("REDIR007", "Row %s: %s." % (e.get("line"), e["error"]), key="row:%s|%s" % (e.get("old"), e.get("new")),
                    evidence={"observed": [e.get("old"), e.get("new")]}, **where)
            continue
        k = _map_key(e["old"])
        if k in mapping:
            ck.emit("REDIR007", "Duplicate source URL %s (row %s)." % (e["old"], e.get("line")), key="dup:" + k,
                    evidence={"observed": e["old"], "first_row": mapping[k].get("line")}, **where)
            continue
        mapping[k] = e
        valid.append(e)
    new_idx = _Index(new_site) if new_site else None
    finals: List[Tuple[Dict[str, Any], str]] = []
    for e in valid:
        where = {"url": e["old"]}
        chain, cur, loop = [_map_key(e["old"])], e, False
        while True:
            nxt = _map_key(cur["new"])
            if nxt in chain:
                loop = True
                break
            if nxt not in mapping or len(chain) > 20:
                break
            chain.append(nxt)
            cur = mapping[nxt]
        if loop:
            ck.emit("REDIR002", "Redirect loop: %s." % " -> ".join(chain + [_map_key(cur["new"])]), key="loop",
                    evidence={"chain": chain}, **where)
            continue
        if len(chain) > 1:
            ck.emit("REDIR001", "Redirect chain of %d hops ending at %s." % (len(chain), cur["new"]), key="chain",
                    evidence={"chain": chain + [_map_key(cur["new"])]}, **where)
        if e.get("status") in TEMPORARY:
            ck.emit("REDIR004", "Temporary status %d for a mapped move." % e["status"], key="temporary",
                    evidence={"observed": e["status"]}, **where)
        finals.append((e, cur["new"]))
        if new_idx is not None:
            final_abs = cur["new"] if "://" in cur["new"] else new_idx.origin + new_idx.base_path + cur["new"]
            if new_idx.internal(final_abs) and new_idx.key_of(final_abs) is None and not new_idx.is_asset(final_abs) \
                    and not new_idx.redirect_of(final_abs):
                ck.emit("REDIR003", "Destination %s is not in the new build." % cur["new"], key="destination",
                        evidence={"observed": cur["new"]}, **where)
    home_hits = [e["old"] for e, final in finals if _map_key(final) in ("/", (new_idx.base_path + "/") if new_idx
                                                                      else "/")]
    min_count = int(ck.th_get("redirects", "home_min_count", 3))
    share = float(ck.th_get("redirects", "home_share", 0.2))
    if valid and len(home_hits) >= min_count and len(home_hits) / float(len(valid)) >= share:
        ck.emit("REDIR005", "%d of %d mapped URLs redirect to the home page." % (len(home_hits), len(valid)),
                key="home", affected=len(home_hits), sample=home_hits, url=home_hits[0],
                evidence={"observed": len(home_hits), "share": round(len(home_hits) / float(len(valid)), 3)})
    if old_site is not None and new_site is not None and new_idx is not None:
        old_idx = _Index(old_site)
        for key in sorted(old_site.pages):
            path = _map_key(old_idx.absolute(key))
            rel = old_idx._site_path(old_idx.absolute(key))
            if path in mapping or _map_key(_slashless(path)) in mapping or _map_key(path + "/") in mapping:
                continue
            if new_idx.key_of(new_idx.origin + new_idx.base_path + rel) is None:
                ck.emit("REDIR006", "Old URL is neither in the new build nor redirected.", key="unmapped",
                        url=old_idx.absolute(key), file=old_site.files.get(key))
    return ck.out


# ---------------------------------------------------------------------------------------- drift records

def page_record(url: str, page: PageDoc, *, status: Optional[int] = None,
                headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Canonical snapshot record for drift (WP06 §4.3 shape, plus `noindex`)."""
    hdrs = {str(k).lower(): v for k, v in (headers or {}).items()}
    meta_robots = directives.parse_robots_values(page.meta.get("robots", []) + page.meta.get("googlebot", []))
    xr_value = hdrs.get("x-robots-tag")
    xr = directives.parse_x_robots([xr_value]) if xr_value else {}

    def flat(parsed: Dict[str, Any]) -> List[str]:
        return sorted(set(parsed["tokens"]) | {"%s:%s" % kv for kv in parsed["params"].items()})

    base = urljoin(url, page.base_href) if page.base_href else url
    canonical = next((_resolve(h, url, page.base_href) for h, _ in page.canonicals if h), None)
    title = page.titles[0] if page.titles else None
    description = next((v for v in page.meta.get("description", []) if v.strip()), None)
    types = htmlparse.jsonld_types(page.jsonld)
    host = urlsplit(url).netloc.lower()
    internal = 0
    for link in page.links:
        href = (link.get("href") or "").strip()
        if href and not href.startswith("#") and not re.match(r"(?i)(javascript|mailto|tel|data):", href):
            target = _resolve(href, base, None) or ""
            if urlsplit(target).netloc.lower() == host:
                internal += 1
    digest = hashlib.sha256("\n".join([title or "", description or "", ",".join(types),
                                       htmlparse.collapse(page.main_text)]).encode("utf-8")).hexdigest()
    eff = directives.effective(page.meta, xr)
    return {"url": url, "status": status, "title": title, "meta_description": description, "canonical": canonical,
            "robots": flat(meta_robots), "x_robots": {a: flat(p) for a, p in xr.items()} if xr else None,
            "h1": next((t for lvl, t, _ in page.headings if lvl == 1), None),
            "h2": [t for lvl, t, _ in page.headings if lvl == 2],
            "hreflang": sorted([c.lower(), _resolve(h, base, None) or h] for c, h, _ in page.hreflang),
            "jsonld_types": types, "og": {k: v[0] for k, v in sorted(page.meta.items()) if k.startswith("og:") and v},
            "word_count": page.word_count, "internal_links": internal, "content_hash": digest,
            "noindex": bool(eff["noindex"])}


def build_time(site: BuiltSite) -> Optional[str]:
    """Newest mtime among scanned HTML files as ISO 8601 UTC (for sitemaps SMAP006), or None."""
    if not site.root:
        return None
    newest = 0.0
    for rel in site.files.values():
        try:
            newest = max(newest, os.lstat(os.path.join(site.root, rel)).st_mtime)
        except OSError:
            continue
    return datetime.fromtimestamp(newest, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if newest else None
