"""XML / text sitemap parsing, discovery and checks; IndexNow payloads (WP02).

XML is parsed with ``xml.etree.ElementTree`` only after refusing ``<!DOCTYPE`` and ``<!ENTITY``
(no entity expansion). Gzip input is decompressed incrementally and aborted at the byte cap
(decompression-bomb safe). IndexNow support builds payloads only; nothing is ever sent.
"""
from __future__ import annotations

import ipaddress
import os
import re
import stat
import zlib
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from xml.etree import ElementTree

from .findings import Finding, make
from .rulesdb import RuleCatalog, default_catalog, thresholds

NS_SITEMAP = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS_IMAGE = "http://www.google.com/schemas/sitemap-image/1.1"
NS_XHTML = "http://www.w3.org/1999/xhtml"
REMOVED_IMAGE_TAGS = ("caption", "title", "geo_location", "license")
COMMON_NAMES = ("sitemap.xml", "sitemap_index.xml", "sitemap-index.xml", "wp-sitemap.xml", "sitemap.xml.gz",
                "sitemap.txt")
_W3C_DATE = re.compile(r"^\d{4}(?:-(0[1-9]|1[0-2])(?:-(0[1-9]|[12]\d|3[01])(?:T([01]\d|2[0-3]):[0-5]\d"
                       r"(?::[0-5]\d(?:\.\d+)?)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d))?)?)?$")
_SAFE = "/!$&'()*+,;=:@-._~"
_PARITY_TEXT = {"missing": "not in the build", "noindex": "noindex", "redirects": "redirecting",
                "canonicalized": "canonicalized to another URL"}
_DEFAULT_PORT = {"http": 80, "https": 443}
_LOCAL_SUFFIX = (".localhost", ".local", ".internal", ".lan", ".home.arpa")
_PREVIEW_SUFFIX = (".vercel.app", ".netlify.app", ".pages.dev", ".herokuapp.com", ".ngrok.io", ".ngrok-free.app",
                   ".ngrok.app", ".loca.lt", ".trycloudflare.com", ".amplifyapp.com", ".azurestaticapps.net",
                   ".workers.dev")
_STAGING_LABEL = re.compile(r"^(?:staging|stage|stg|preview|dev|development|uat|qa|test|sandbox)(?:[-\d]|$)"
                            r"|-(?:staging|preview|stage|dev)(?:-|$)")


def normalize_url(url: str) -> str:
    """Same comparison key as sitescan.normalize_url (kept in sync by tests)."""
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
    return url[:-1] if url.endswith("/") and not url.endswith("://") and urlsplit(url).path not in ("", "/") else url


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _ns(tag: str) -> str:
    return tag[1:].split("}", 1)[0] if isinstance(tag, str) and tag.startswith("{") else ""


def _decompress(data: bytes, max_bytes: int) -> Tuple[bytes, bool]:
    """Incremental gzip decompression that stops once output exceeds max_bytes."""
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    out = bytearray()
    pending = data
    while pending:
        out.extend(d.decompress(pending, max_bytes + 1 - len(out)))
        if len(out) > max_bytes:
            return bytes(out[:max_bytes]), True
        pending = d.unconsumed_tail
    return bytes(out), False


def parse_sitemap(data: bytes, *, source: str, max_bytes: int = 52_428_800) -> Dict[str, Any]:
    """Parse one sitemap: {kind: urlset|sitemapindex|text|feed|invalid, urls, sitemaps, errors, size, source, ...}.

    Each URL: {loc, lastmod, changefreq, priority, images, image_removed_tags, alternates: [(code, href)]}.
    `too_large` is True when the uncompressed size exceeds `max_bytes` (parsing stops).
    """
    result: Dict[str, Any] = {"source": source, "kind": "invalid", "urls": [], "sitemaps": [], "errors": [],
                              "size": len(data), "too_large": False, "notes": []}
    if data[:2] == b"\x1f\x8b":
        try:
            data, over = _decompress(data, max_bytes)
        except zlib.error as exc:
            result["errors"].append("gzip error: %s" % exc)
            return result
        result["size"] = len(data) + (1 if over else 0)
        if over:
            result.update(too_large=True, size=max_bytes + 1)
            result["errors"].append("exceeds %d bytes uncompressed" % max_bytes)
            return result
    elif len(data) > max_bytes:
        result.update(too_large=True)
        result["errors"].append("exceeds %d bytes uncompressed" % max_bytes)
        return result
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        result["errors"].append("not UTF-8")
        return result
    head = text.lstrip()[:1]
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
        result["errors"].append("DOCTYPE or ENTITY declaration refused")
        return result
    if head != "<":
        return _parse_text(text, result)
    try:
        root = ElementTree.fromstring(text)
    except (ElementTree.ParseError, ValueError) as exc:
        result["errors"].append("XML parse error: %s" % str(exc)[:120])
        return result
    kind = _local(root.tag)
    if kind == "urlset":
        result["kind"] = "urlset"
        for node in root:
            if _local(node.tag) == "url":
                result["urls"].append(_url_entry(node))
    elif kind == "sitemapindex":
        result["kind"] = "sitemapindex"
        for node in root:
            if _local(node.tag) == "sitemap":
                result["sitemaps"].append({"loc": _child_text(node, "loc"), "lastmod": _child_text(node, "lastmod")})
    elif kind in ("rss", "feed"):
        result["kind"] = "feed"
        for node in root.iter():
            if _local(node.tag) == "link":
                href = node.get("href") or (node.text or "").strip()
                if href and (kind == "feed" and node.get("rel", "alternate") == "alternate" or kind == "rss"):
                    result["urls"].append({"loc": href, "lastmod": None, "changefreq": None, "priority": None,
                                           "images": [], "image_removed_tags": [], "alternates": []})
    else:
        result["errors"].append("unexpected root element <%s>" % kind)
        return result
    if kind in ("urlset", "sitemapindex") and _ns(root.tag) != NS_SITEMAP:
        result["notes"].append("root element is not in the sitemaps.org namespace")
    return result


def _child_text(node: Any, name: str) -> Optional[str]:
    for child in node:
        if _local(child.tag) == name:
            return (child.text or "").strip()
    return None


def _url_entry(node: Any) -> Dict[str, Any]:
    entry: Dict[str, Any] = {"loc": None, "lastmod": None, "changefreq": None, "priority": None, "images": [],
                             "image_removed_tags": [], "alternates": []}
    for child in node:
        name, ns = _local(child.tag), _ns(child.tag)
        if name in ("loc", "lastmod", "changefreq", "priority") and ns in (NS_SITEMAP, ""):
            entry[name] = (child.text or "").strip()
        elif name == "image" and ns == NS_IMAGE:
            for sub in child:
                if _local(sub.tag) == "loc":
                    entry["images"].append((sub.text or "").strip())
                elif _local(sub.tag) in REMOVED_IMAGE_TAGS:
                    entry["image_removed_tags"].append(_local(sub.tag))
        elif name == "link" and ns == NS_XHTML and child.get("rel") == "alternate" and child.get("hreflang"):
            entry["alternates"].append((child.get("hreflang", "").strip(), (child.get("href") or "").strip()))
    return entry


def _parse_text(text: str, result: Dict[str, Any]) -> Dict[str, Any]:
    result["kind"] = "text"
    for no, line in enumerate(text.splitlines(), start=1):
        value = line.strip()
        if not value:
            continue
        try:
            parts = urlsplit(value)
        except ValueError:
            parts = None
        if parts is None or parts.scheme not in ("http", "https") or not parts.netloc or re.search(r"[\s\\]", value) \
                or "@" in parts.netloc:
            result["errors"].append("line %d is not an absolute http(s) URL" % no)
        result["urls"].append({"loc": value, "lastmod": None, "changefreq": None, "priority": None, "images": [],
                               "image_removed_tags": [], "alternates": []})
    if result["errors"] and len(result["errors"]) == len(result["urls"]):
        result["kind"] = "invalid"
    return result


def load_sitemaps(root: str, paths: Sequence[str], *, max_bytes: int = 52_428_800) -> List[Dict[str, Any]]:
    """Read and parse sitemap files under `root` (no symlinks, realpath containment, size cap).

    Absolute URLs (remote robots.txt `Sitemap:` entries from discover) are skipped: fetch them only live.
    """
    real_root = os.path.realpath(root)
    out = []
    for rel in sorted(dict.fromkeys(p for p in paths if "://" not in p)):
        full = os.path.realpath(os.path.join(real_root, rel))
        if not full.startswith(real_root + os.sep) or os.path.islink(os.path.join(real_root, rel)):
            continue
        try:
            fd = os.open(full, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
            with os.fdopen(fd, "rb") as fh:
                if not stat.S_ISREG(os.fstat(fh.fileno()).st_mode):
                    continue
                raw = fh.read(max_bytes + 1)
        except OSError as exc:
            out.append({"source": rel, "kind": "invalid", "urls": [], "sitemaps": [], "size": 0, "too_large": False,
                        "errors": ["unreadable: %s" % exc.__class__.__name__], "notes": []})
            continue
        if len(raw) > max_bytes:
            out.append({"source": rel, "kind": "invalid", "urls": [], "sitemaps": [], "size": len(raw),
                        "too_large": True, "errors": ["exceeds %d bytes" % max_bytes], "notes": []})
            continue
        out.append(parse_sitemap(raw, source=rel, max_bytes=max_bytes))
    return out


def discover(root: str, robots_text: Optional[str]) -> List[str]:
    """Sitemap candidates: existing local files (robots `Sitemap:` paths and common names) as relative
    paths, then robots `Sitemap:` URLs that map to no local file (absolute URLs, for live fetching)."""
    real_root = os.path.realpath(root) if root else None
    local: List[str] = []
    remote: List[str] = []

    def exists(rel: str) -> bool:
        if not real_root:
            return False
        full = os.path.join(real_root, rel)
        return (not os.path.islink(full) and os.path.isfile(full)
                and os.path.realpath(full).startswith(real_root + os.sep))

    for line in re.split(r"\r\n|\r|\n", robots_text or ""):
        m = re.match(r"^\s*sitemap\s*:\s*(\S+)", line.split("#", 1)[0], re.I)
        if not m:
            continue
        rel = unquote(urlsplit(m.group(1)).path).lstrip("/")
        if rel and exists(rel):
            local.append(rel)
        elif re.match(r"(?i)https?://", m.group(1)):
            remote.append(m.group(1))
    for name in COMMON_NAMES:
        if exists(name):
            local.append(name)
    return list(dict.fromkeys(local)) + list(dict.fromkeys(remote))


def _parse_lastmod(value: str) -> Optional[datetime]:
    if not _W3C_DATE.match(value or ""):
        return None
    text = value
    if len(text) == 4:
        text += "-01-01"
    elif len(text) == 7:
        text += "-01"
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?)(?:\.\d+)?(Z|[+-]\d{2}:\d{2})$", value)
        if not m:
            return None
        dt = datetime.fromisoformat(m.group(1) + (m.group(2).replace("Z", "+00:00")))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def launch_host_problem(host: str, base_host: Optional[str]) -> Optional[str]:
    """Same heuristic as sitescan.launch_host_problem (kept in sync by tests)."""
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


def check_sitemaps(parsed: List[Dict[str, Any]], catalog: Optional[RuleCatalog] = None, *,
                   base_url: Optional[str], site_urls: Optional[Set[str]] = None,
                   indexable: Optional[Callable[[str], Union[bool, str]]] = None, build_time: Optional[str] = None,
                   today: Optional[date] = None, profile: str = "default") -> List[Finding]:
    """SMAP001-011 plus LAUNCH003 for sitemap locs.

    `site_urls`: normalized built URLs (paths when no base_url); `indexable(url)` returns True or a
    reason ("missing", "noindex", "redirects", "canonicalized to ..."); `build_time` (ISO 8601) and
    `today` feed the lastmod accuracy heuristics.
    """
    cat = catalog or default_catalog()
    th = thresholds()
    smap = th.get("sitemap") if isinstance(th.get("sitemap"), dict) else {}
    out: List[Finding] = []

    def emit(rule: str, message: str, **kw: Any) -> None:
        if cat.get(rule).status == "v1":
            out.append(make(rule, message, catalog=cat, severity=cat.severity_for(rule, profile=profile), **kw))

    base_host = (urlsplit(base_url).hostname or "").lower() if base_url else None
    home = (base_url.rstrip("/") + "/") if base_url else None
    if not parsed:
        emit("SMAP001", "No sitemap found in the build or robots.txt.", key="none", url=home)
        return out
    max_urls = int(smap.get("max_urls", 50000))
    max_bytes = int(smap.get("max_bytes", 52428800))
    per_url = int(smap.get("image_per_url", 1000))
    uniform_min = int(smap.get("uniform_lastmod_min_urls", 3))
    tolerance = float(smap.get("build_time_tolerance_s", 60))
    build_share = float(smap.get("build_time_share", 0.5))
    built = _parse_lastmod(build_time) if build_time else None
    ref_day = today or (built.date() if built else date.today())
    listed: Set[str] = set()
    sources = {_source_key(p["source"]) for p in parsed}
    for sm in sorted(parsed, key=lambda p: p["source"]):
        src = sm["source"]
        where = {"file": None if "://" in src else src, "url": src if "://" in src else home}
        if sm["kind"] == "invalid" and not sm.get("too_large"):
            emit("SMAP003", "Sitemap %s is not valid: %s." % (src, "; ".join(sm["errors"][:3])), key="invalid:" + src,
                 evidence={"errors": sm["errors"][:5]}, **where)
            continue
        count = len(sm["urls"]) + len(sm["sitemaps"])
        if sm.get("too_large") or sm["size"] > max_bytes or count > max_urls:
            emit("SMAP002", "Sitemap %s exceeds the protocol limits (%d entries, %d bytes)." % (src, count, sm["size"]),
                 key="limits:" + src, evidence={"entries": count, "bytes": sm["size"], "max_urls": max_urls,
                                                "max_bytes": max_bytes}, **where)
            if sm.get("too_large"):
                continue
        for child in sm["sitemaps"]:
            loc = child.get("loc") or ""
            if _source_key(loc) not in sources:
                emit("SMAP011", "Sitemap index %s references %s, which is missing." % (src, loc or "(empty loc)"),
                     key="child:%s|%s" % (src, loc), evidence={"observed": loc}, **where)
        bad_loc, bad_lastmod, staging, removed, many_images = [], [], [], [], []
        lastmods: List[datetime] = []
        ignored_fields = 0
        for entry in sm["urls"]:
            loc = entry.get("loc") or ""
            problem = _loc_problem(loc, base_host)
            if problem:
                bad_loc.append("%s (%s)" % (loc[:150], problem))
            else:
                listed.add(normalize_url(loc))
                reason = launch_host_problem(urlsplit(loc).hostname or "", base_host)
                if reason:
                    staging.append({"url": loc[:200], "reason": reason})
            if entry.get("lastmod"):
                when = _parse_lastmod(entry["lastmod"])
                if when is None:
                    bad_lastmod.append(entry["lastmod"][:40])
                else:
                    lastmods.append(when)
            if entry.get("priority") or entry.get("changefreq"):
                ignored_fields += 1
            if entry.get("image_removed_tags"):
                removed.extend(entry["image_removed_tags"])
            if len(entry.get("images") or []) > per_url:
                many_images.append(loc[:150])
        if bad_loc:
            emit("SMAP004", "%d sitemap locs are not absolute http(s) URLs on the site host." % len(bad_loc),
                 key="loc:" + src, affected=len(bad_loc), evidence={"observed": bad_loc[:10]}, **where)
        if staging:
            emit("LAUNCH003", "%d sitemap locs point at local, staging or preview hosts." % len(staging),
                 key="sitemap:" + src, affected=len(staging), evidence={"observed": staging[:10]}, **where)
        if bad_lastmod:
            emit("SMAP005", "%d lastmod values are not W3C Datetime." % len(bad_lastmod), key="lastmod:" + src,
                 affected=len(bad_lastmod), evidence={"observed": bad_lastmod[:10]}, **where)
        reasons = _lastmod_reasons(lastmods, len(sm["urls"]), uniform_min, ref_day, built, tolerance, build_share)
        if reasons:
            emit("SMAP006", "lastmod values look inaccurate: %s." % "; ".join(reasons), key="accuracy:" + src,
                 confidence="medium", evidence={"observed": reasons}, **where)
        if ignored_fields:
            emit("SMAP007", "%d entries carry priority or changefreq (ignored by Google and Bing)." % ignored_fields,
                 key="ignored:" + src, evidence={"entries": ignored_fields}, **where)
        if removed or many_images:
            emit("SMAP010", "Image sitemap issues: %s." % ", ".join(
                (["removed tags: " + ", ".join(sorted(set(removed)))] if removed else [])
                + (["%d URLs list more than %d images" % (len(many_images), per_url)] if many_images else [])),
                key="images:" + src, evidence={"removed_tags": sorted(set(removed)), "over_limit": many_images[:10]},
                **where)
        if indexable is not None or site_urls is not None:
            _parity_listed(emit, sm, where, base_url, site_urls, indexable)
    if site_urls is not None:
        keys = {_key(u, base_url) for u in listed}
        loose = {_slashless(k) for k in keys}
        missing = sorted(u for u in site_urls if _key(u, base_url) not in keys and _slashless(_key(u, base_url))
                         not in loose and (indexable is None or indexable(u) is True))
        if missing:
            emit("SMAP009", "%d indexable built pages are not in any sitemap." % len(missing), key="unlisted",
                 url=missing[0] if "://" in missing[0] else (home or None), affected=len(missing), sample=missing,
                 evidence={"count": len(missing)})
    return out


def _source_key(value: str) -> str:
    """Comparable form of a sitemap location: URL path without the leading slash (or the rel path)."""
    if "://" in value:
        value = urlsplit(value).path
    return unquote(value).lstrip("/").lower()


def _loc_problem(loc: str, base_host: Optional[str]) -> Optional[str]:
    try:
        parts = urlsplit(loc)
    except ValueError:
        return "malformed"
    if not loc:
        return "empty"
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return "not absolute http(s)"
    if "@" in parts.netloc or re.search(r"\s", loc):
        return "credentials or spaces"
    if base_host and (parts.hostname or "").lower() != base_host and not launch_host_problem(parts.hostname or "",
                                                                                             base_host):
        return "different host"
    return None


def _key(url: str, base_url: Optional[str]) -> str:
    n = normalize_url(url)
    if base_url:
        return n
    parts = urlsplit(n)
    return parts.path + ("?" + parts.query if parts.query else "")


def _lastmod_reasons(values: List[datetime], total: int, uniform_min: int, ref_day: date,
                     built: Optional[datetime], tolerance: float, share: float) -> List[str]:
    reasons = []
    if total >= uniform_min and len(values) == total and len({v.isoformat() for v in values}) == 1:
        reasons.append("all %d entries share one lastmod" % total)
    future = [v for v in values if v.date() > ref_day + timedelta(days=1)]
    if future:
        reasons.append("%d lastmod values are in the future" % len(future))
    if built is not None and values:
        near = [v for v in values if abs((v - built).total_seconds()) <= tolerance]
        if len(near) / float(len(values)) >= share and len(near) >= 2:
            reasons.append("%d lastmod values equal the build time" % len(near))
    return reasons


def _parity_listed(emit: Callable[..., None], sm: Dict[str, Any], where: Dict[str, Any], base_url: Optional[str],
                   site_urls: Optional[Set[str]], indexable: Optional[Callable[[str], Union[bool, str]]]) -> None:
    keys = {_key(u, base_url) for u in (site_urls or set())}
    loose = {_slashless(k) for k in keys}
    problems: Dict[str, List[str]] = {}
    for entry in sm["urls"]:
        loc = entry.get("loc") or ""
        base_host = (urlsplit(base_url).hostname or "").lower() if base_url else None
        if _loc_problem(loc, base_host) or launch_host_problem(urlsplit(loc).hostname or "", base_host):
            continue
        k = _key(loc, base_url)
        reason: Union[bool, str] = True
        if indexable is not None:
            reason = indexable(loc if base_url else k)
        if reason is True and site_urls is not None and k not in keys:
            reason = "redirects (trailing-slash variant)" if _slashless(k) in loose else "missing"
        if reason is not True:
            label = str(reason).split(" to ")[0].split(" (")[0] if reason else "not indexable"
            problems.setdefault(label, []).append(loc[:200])
    for reason in sorted(problems):
        urls = problems[reason]
        emit("SMAP008", "%d sitemap URLs are %s." % (len(urls), _PARITY_TEXT.get(reason, reason)),
             key="parity:%s|%s" % (sm["source"], reason), affected=len(urls), sample=urls,
             evidence={"reason": reason, "observed": urls[:10]}, **where)


def indexnow_payload(urls: List[str], *, host: str, key: str, key_location: Optional[str]) -> Dict[str, Any]:
    """Validated IndexNow POST body {host, key, keyLocation?, urlList}; raises ValueError. Never sends it."""
    block = thresholds().get("indexnow")
    block = block if isinstance(block, dict) else {}
    if not re.match(block.get("key_regex", r"^[A-Za-z0-9-]{8,128}$"), key or ""):
        raise ValueError("IndexNow key must be 8-128 characters of letters, digits or dashes")
    host = (host or "").strip().lower().rstrip(".")
    if not host or "/" in host or "@" in host:
        raise ValueError("host must be a bare host name")
    scope = "/"
    if key_location:
        parts = urlsplit(key_location)
        if parts.scheme not in ("http", "https") or (parts.hostname or "").lower() != host:
            raise ValueError("keyLocation must be an absolute URL on %s" % host)
        if not parts.path.endswith(".txt"):
            raise ValueError("keyLocation must point at a .txt key file")
        scope = parts.path.rsplit("/", 1)[0] + "/"
    unique = list(dict.fromkeys(u.strip() for u in urls if u and u.strip()))
    if not unique:
        raise ValueError("no URLs to submit")
    limit = int(block.get("max_urls", 10000))
    if len(unique) > limit:
        raise ValueError("IndexNow accepts at most %d URLs per request (%d given)" % (limit, len(unique)))
    for u in unique:
        parts = urlsplit(u)
        if parts.scheme not in ("http", "https") or (parts.hostname or "").lower() != host:
            raise ValueError("URL not on %s: %s" % (host, u[:200]))
        if not (parts.path or "/").startswith(scope):
            raise ValueError("URL outside the keyLocation scope %s: %s" % (scope, u[:200]))
    payload: Dict[str, Any] = {"host": host, "key": key, "urlList": unique}
    if key_location:
        payload["keyLocation"] = key_location
    return payload
