"""robots.txt parsing (RFC 9309), AI crawler access analysis and live access checks (WP03).

Offline and deterministic. `access_check` makes requests only through the `fetch` callable that
cli injects (the SSRF-guarded ``fetch.fetch`` behind ``--live``); this module never opens sockets.

Semantics: lines split on CR, LF or CRLF only (U+2028/U+2029 inside a comment stay comments); BOM
stripped; content after 500 KiB ignored; consecutive User-agent lines share one group; a token uses the
union of the groups naming it (case-insensitive product token), else the union of ``*`` groups; policy
tokens such as ``__usage_ai-training`` never fall back to ``*``; longest match wins and Allow wins ties;
``*`` and a trailing ``$`` are wildcards; empty rules are ignored; ``/robots.txt`` is always allowed.
"""
from __future__ import annotations

import copy
import difflib
import functools
import hashlib
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from .findings import Finding, make, truncate
from .rulesdb import RuleCatalog, default_catalog, load_data, loads_json, thresholds

OUR_TOKEN = "seo-geo-god"
_LINES = re.compile(r"\r\n|\r|\n")
_PRODUCT = re.compile(r"[A-Za-z_-]+")
_PCT = re.compile(r"%([0-9A-Fa-f]{2})")
_UNRESERVED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")
_FIELDS = ("user-agent", "allow", "disallow", "sitemap", "content-signal")
_CF_MARKER = "begin cloudflare managed content"
_CF_END = "end cloudflare managed content"
_TRAINING_WORDS = re.compile(r"\b(?:train(?:ing)?|machine[- ]learning|llms?|genai|generative ai|"
                             r"ai[- ](?:crawlers?|bots?|scrapers?|models?|usage))\b", re.I)
_ALWAYS_ALLOWED = frozenset({"/robots.txt", "/robots.txt$"})
_FIELD_NOTES = {
    "crawl-delay": " Anthropic's crawlers honor Crawl-delay; Google, Apple and Amazon ignore it.",
    "noindex": " Use a robots meta tag or X-Robots-Tag to keep pages out of the index.",
    "host": " Set the preferred host with redirects and canonical links instead.",
}
ASSET_PROBES = ("/_next/static/chunks/main.js", "/assets/index.js", "/assets/index.css", "/static/js/main.js",
                "/static/css/main.css", "/css/style.css", "/js/app.js", "/wp-includes/js/jquery/jquery.min.js",
                "/wp-content/themes/theme/style.css", "/images/photo.jpg", "/style.css", "/app.js")
BOT_GROUPS = {"search": ("INDEX", "MIXED"), "user": ("USER", "AGENT"), "training": ("TRAIN", "CONTROL", "CORPUS"),
              "ai": ("TRAIN", "INDEX", "USER", "AGENT", "MIXED", "CONTROL", "CORPUS")}
WELL_KNOWN = ("/.well-known/api-catalog", "/.well-known/oauth-protected-resource",
              "/.well-known/oauth-authorization-server", "/.well-known/agent-card.json")
HTML_ACCEPT = "text/html,application/xhtml+xml;q=0.9,text/plain;q=0.8,*/*;q=0.5"
TEXT_ACCEPT = "text/plain,text/markdown;q=0.9,*/*;q=0.1"

Rule3 = Tuple[str, str, int]


@dataclass
class Group:
    """One group: consecutive User-agent lines plus the rules and Content-Signal lines that follow."""
    agents: List[str]
    rules: List[Rule3]                 # (allow|disallow, raw path, line); empty paths kept, never matched
    signals: List[Dict[str, Any]]      # parse_content_signal() output plus "line" and "value"
    line: int
    end_line: int = 0


@dataclass
class RobotsTxt:
    """Parsed robots.txt (only the first robots_max_bytes are parsed)."""
    groups: List[Group]
    sitemaps: List[str]
    unknown: List[Tuple[str, int]]     # (field name as written, line)
    orphans: List[Tuple[str, int]]     # rule or signal lines before any User-agent line
    size: int
    truncated: bool
    cloudflare_managed: bool
    errors: List[str]
    sitemap_lines: List[int] = field(default_factory=list)
    malformed: List[Tuple[str, int]] = field(default_factory=list)
    comments: List[Tuple[str, int]] = field(default_factory=list)
    managed_range: Optional[Tuple[int, int]] = None
    looks_html: bool = False


# ----------------------------------------------------------------------------- parsing

def parse_robots(text: str, *, max_bytes: Optional[int] = None) -> RobotsTxt:
    """Parse robots.txt text; content past the byte limit (and a partial last line) is dropped."""
    limit = int(max_bytes if max_bytes is not None else thresholds()["robots_max_bytes"])
    text = text[1:] if text.startswith("\ufeff") else text
    data = text.encode("utf-8", "replace")
    truncated = len(data) > limit
    if truncated:
        cut = data[:limit]
        end = max(cut.rfind(b"\n"), cut.rfind(b"\r"))
        text = cut[: end + 1].decode("utf-8", "ignore") if end >= 0 else ""
    rb = RobotsTxt(groups=[], sitemaps=[], unknown=[], orphans=[], size=len(data), truncated=truncated,
                   cloudflare_managed=False, errors=[], looks_html=_looks_html(text))
    current: Optional[Group] = None
    cf_start = None
    lines = _LINES.split(text)
    for no, raw in enumerate(lines, 1):
        line, hash_at = raw, raw.find("#")
        if hash_at >= 0:
            note = raw[hash_at + 1:].strip()
            if note:
                rb.comments.append((note, no))
                low = note.lower()
                if _CF_MARKER in low:
                    rb.cloudflare_managed, cf_start = True, no
                elif _CF_END in low and cf_start is not None:
                    rb.managed_range = (cf_start, no)
            line = raw[:hash_at]
        line = line.strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        name, value = key.strip().lower(), value.strip()
        if not sep or not name:
            rb.malformed.append((line, no))
            rb.errors.append("line %d: no 'field: value' separator" % no)
            continue
        if name == "user-agent":
            if not value:
                rb.malformed.append((line, no))
                rb.errors.append("line %d: empty User-agent value" % no)
            elif current is None or current.rules:
                current = Group(agents=[value], rules=[], signals=[], line=no, end_line=no)
                rb.groups.append(current)
            else:
                current.agents.append(value)
                current.end_line = no
        elif name in ("allow", "disallow"):
            if current is None:
                rb.orphans.append((line, no))
            else:
                current.rules.append((name, value, no))
                current.end_line = no
        elif name == "sitemap":
            rb.sitemaps.append(value)
            rb.sitemap_lines.append(no)
        elif name == "content-signal":
            if current is None:
                rb.orphans.append((line, no))
            else:
                sig = parse_content_signal(value)
                sig.update(line=no, value=value[:200])
                current.signals.append(sig)
                current.end_line = no
        else:
            guess = difflib.get_close_matches(name, _FIELDS, n=1, cutoff=0.8)
            if guess:
                rb.malformed.append((line, no))
                rb.errors.append("line %d: field %r looks like a misspelling of %s" % (no, key.strip()[:40], guess[0]))
            else:
                rb.unknown.append((key.strip()[:60], no))
            if current is not None:
                current.end_line = no
    if rb.cloudflare_managed and rb.managed_range is None:
        rb.managed_range = (cf_start or 1, len(lines))
    return rb


def _looks_html(text: str) -> bool:
    head = text.lstrip()[:100].lower()
    return head.startswith(("<!doctype", "<html", "<head", "<body", "<?xml"))


def parse_content_signal(value: str, *, registry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Parse a Content-Signal value.

    Returns {search, ai-input, ai-train, use: value or None, unknown: [keys], malformed: bool, problems: [str]};
    keys and allowed values come from the registry's content_signals block.
    """
    spec = (registry or _registry())["content_signals"]
    keys, values, testing = list(spec["keys"]), set(spec["values"]), dict(spec["testing_keys"])
    out: Dict[str, Any] = {k: None for k in keys + sorted(testing)}
    out.update(unknown=[], malformed=False, problems=[])
    if not value.strip():
        out["malformed"] = True
        out["problems"].append("empty value")
        return out
    for item in (x.strip() for x in value.split(",")):
        k, sep, v = item.partition("=")
        k, v = k.strip().lower(), v.strip().lower()
        if not sep or not k or not v:
            out["malformed"] = True
            out["problems"].append("%r is not key=value" % item[:40])
            continue
        if k not in out:
            out["unknown"].append(k[:40])
            continue
        allowed = values if k in keys else set(testing[k])
        if v not in allowed:
            out["malformed"] = True
            out["problems"].append("%s=%s (expected %s)" % (k, v[:20], "|".join(sorted(allowed))))
        elif out[k] is not None and out[k] != v:
            out["malformed"] = True
            out["problems"].append("conflicting values for %s" % k)
        else:
            out[k] = v
    return out


# ----------------------------------------------------------------------------- matching

def _product(value: str) -> str:
    v = value.strip()
    if v == "*":
        return "*"
    m = _PRODUCT.match(v)
    return m.group(0).lower() if m else v.lower()


def _is_policy(token: str) -> bool:
    return _product(token).startswith("__")


def _encode(s: str) -> str:
    out = []
    for ch in s:
        if 0x20 < ord(ch) < 0x7F:
            out.append(ch)
        else:
            out.append("".join("%%%02X" % b for b in ch.encode("utf-8", "replace")))
    return _PCT.sub(lambda m: chr(int(m.group(1), 16)) if chr(int(m.group(1), 16)) in _UNRESERVED
                    else "%" + m.group(1).upper(), "".join(out))


@functools.lru_cache(maxsize=8192)
def _norm_pattern(pattern: str) -> str:
    return _encode(re.sub(r"\*+", "*", pattern))


def _norm_path(path: str) -> str:
    if path.lower().startswith(("http://", "https://")):
        parts = urllib.parse.urlsplit(path)
        path = (parts.path or "/") + ("?" + parts.query if parts.query else "")
    if not path.startswith("/"):
        path = "/" + path
    return _encode(path)[:4096]


def _matches(pattern: str, path: str) -> bool:
    """Prefix match with '*' wildcards and a trailing '$' anchor (greedy leftmost; linear-time finds)."""
    anchored = pattern.endswith("$")
    parts = (pattern[:-1] if anchored else pattern).split("*")
    if not path.startswith(parts[0]):
        return False
    pos = len(parts[0])
    if len(parts) == 1:
        return not anchored or pos == len(path)
    for seg in parts[1:-1]:
        if seg:
            pos = path.find(seg, pos)
            if pos < 0:
                return False
            pos += len(seg)
    last = parts[-1]
    if anchored:
        return len(path) - len(last) >= pos and path.endswith(last)
    return not last or path.find(last, pos) >= 0


def _allowed(rules: Optional[Sequence[Rule3]], path: str) -> bool:
    if rules is None:
        return True
    p = _norm_path(path)
    if p == "/robots.txt":
        return True
    best, allow = -1, True
    for directive, raw, _line in rules:
        pat = _norm_pattern(raw)
        if _matches(pat, p) and (len(pat) > best or (len(pat) == best and directive == "allow")):
            best, allow = len(pat), directive == "allow"
    return allow


def _select(robots: Optional[RobotsTxt], token: str, fallback: Optional[str] = None
            ) -> Tuple[Optional[List[Rule3]], str]:
    """(effective rules or None, group kind: named | fallback:<token> | * | none)."""
    if robots is None:
        return None, "none"
    want = _product(token)

    def union(name: str) -> List[Group]:
        return [g for g in robots.groups if name in {_product(a) for a in g.agents}]

    def flat(groups: List[Group]) -> List[Rule3]:
        return [r for g in groups for r in g.rules if r[1]]

    named = union(want)
    if named:
        return flat(named), "named"
    if fallback and union(_product(fallback)):
        return flat(union(_product(fallback))), "fallback:" + fallback
    if want.startswith("__"):
        return None, "none"
    star = union("*")
    return (flat(star), "*") if star else (None, "none")


def rules_for(robots: Optional[RobotsTxt], token: str, *, fallback: Optional[str] = None
              ) -> Optional[List[Tuple[str, str]]]:
    """Effective (directive, path) rules for a token; None when no group applies (everything allowed)."""
    rules, _kind = _select(robots, token, fallback)
    return None if rules is None else [(d, p) for d, p, _ in rules]


def is_allowed(robots: Optional[RobotsTxt], token: str, path: str, *, fallback: Optional[str] = None) -> bool:
    """RFC 9309 decision for `token` on a URL path or absolute URL."""
    return _allowed(_select(robots, token, fallback)[0], path)


def allow_predicate(text: str, token: str = OUR_TOKEN) -> Callable[[str], bool]:
    """Predicate over absolute URLs for fetch.robots_gate (our crawler's token by default)."""
    robots = parse_robots(text)
    return lambda url: is_allowed(robots, token, url)


def _blocks_site(rules: Optional[Sequence[Rule3]]) -> bool:
    if not rules or _allowed(rules, "/"):
        return False
    return all(_norm_pattern(p) in _ALWAYS_ALLOWED for d, p, _ in rules if d == "allow")


def _first_line(robots: RobotsTxt, token: str) -> Optional[int]:
    want = _product(token)
    return next((g.line for g in robots.groups if want in {_product(a) for a in g.agents}), None)


# ----------------------------------------------------------------------------- registry and access table

@functools.lru_cache(maxsize=1)
def _registry() -> Dict[str, Any]:
    return load_data("ai-crawlers")


def load_registry() -> Dict[str, Any]:
    """data/ai-crawlers.json (a fresh copy)."""
    return copy.deepcopy(_registry())


def _class_filter(classes: Union[None, str, Iterable[str]]) -> Optional[set]:
    if classes is None:
        return None
    names = [classes] if isinstance(classes, str) else list(classes)
    out: set = set()
    for name in names:
        if name.lower() == "all":
            return None
        if name in ("TRAIN", "INDEX", "USER", "AGENT", "ADS", "PREVIEW", "MIXED", "CONTROL", "CORPUS"):
            out.add(name)
        elif name.lower() in BOT_GROUPS:
            out.update(BOT_GROUPS[name.lower()])
        else:
            raise ValueError("unknown crawler class or group: %r" % name)
    return out


def _honored_summary(policy: Dict[str, Any]) -> str:
    return "; ".join("%s: %s" % (h["vendor"], h["from"]) for h in policy["honored_by"])


def _impacts(e: Dict[str, Any], allowed: Dict[str, bool]) -> Tuple[str, str]:
    blocked_all, allowed_all = not any(allowed.values()), all(allowed.values())
    surfaces = ", ".join(e["visibility_surfaces"])
    if not surfaces:
        vis = "no visibility surface documented"
    elif blocked_all:
        vis = ("rules may be ignored; where honored, excluded from " if e["honors_robots"] in ("no", "partial")
               else "excluded from ") + surfaces
    else:
        vis = ("eligible for " if allowed_all else "partially blocked for ") + surfaces
    if e["class"] == "CORPUS":
        train = "open corpus that third parties reuse, including for AI training"
    elif e["training"] is True:
        train = ("preference against %s training stated" % e["vendor"] if blocked_all else
                 "may be used for %s model training" % e["vendor"] if allowed_all else "training use partly restricted")
    elif e["training"] is False:
        train = "not used for training (vendor statement)"
    else:
        train = "training use not documented"
    return vis, train


def access_table(robots: Optional[RobotsTxt], *, registry: Optional[Dict[str, Any]] = None,
                 paths: Sequence[str] = ("/",), classes: Union[None, str, Iterable[str]] = None
                 ) -> List[Dict[str, Any]]:
    """Per-token rows: allowed per path, group used, visibility and training impact, verification and source.

    `classes`: None/"all", upper-case class names (TRAIN, INDEX, USER, ...) or lower-case groups
    ai|search|user|training (user = USER + AGENT).
    Policy tokens (class CONTROL) and named agents missing from the registry are appended.
    """
    reg = registry or _registry()
    wanted = _class_filter(classes)
    paths = list(paths) or ["/"]
    rows: List[Dict[str, Any]] = []
    known = set()
    for e in reg["crawlers"]:
        known.add(_product(e["token"]))
        if wanted is not None and e["class"] not in wanted:
            continue
        rules, kind = _select(robots, e["token"], e.get("fallback"))
        allowed = {p: _allowed(rules, p) for p in paths}
        vis, train = _impacts(e, allowed)
        rows.append({"token": e["token"], "vendor": e["vendor"], "class": e["class"], "allowed": allowed,
                     "group": kind, "blocks_site": _blocks_site(rules), "visibility_impact": vis,
                     "training_impact": train, "honors_robots": e["honors_robots"],
                     "verify": e["ip_list_url"] or e["rdns"] or "no published verification method",
                     "source_url": e["source_url"], "source_label": e["source_label"],
                     "verified_on": e["verified_on"], "needs_verification": e["needs_verification"],
                     "in_registry": True, "notes": e["notes"]})
    for p in reg["policy_tokens"]:
        known.add(_product(p["token"]))
        if wanted is not None and "CONTROL" not in wanted:
            continue
        rules, kind = _select(robots, p["token"])
        allowed = {x: _allowed(rules, x) for x in paths}
        pref = ("no preference expressed (User-agent: * never applies)" if rules is None else
                "against AI training" if not any(allowed.values()) else
                "in favor of or no preference on AI training" if all(allowed.values()) else "mixed by path")
        rows.append({"token": p["token"], "vendor": "shared policy token", "class": "CONTROL", "allowed": allowed,
                     "group": kind, "blocks_site": _blocks_site(rules),
                     "visibility_impact": "none: a preference, not a crawling directive",
                     "training_impact": "%s; honored by %s" % (pref, _honored_summary(p)),
                     "honors_robots": "token-only",
                     "verify": "n/a (not a crawler)", "source_url": p["source_url"], "source_label": p["source_label"],
                     "verified_on": p["verified_on"], "needs_verification": False, "in_registry": True,
                     "notes": p["notes"]})
    if wanted is None and robots is not None:
        extra = sorted({a.strip() for g in robots.groups for a in g.agents
                        if _product(a) not in known and _product(a) != "*"}, key=str.lower)
        for agent in extra:
            rules, kind = _select(robots, agent)
            rows.append({"token": agent[:80], "vendor": None, "class": None,
                         "allowed": {x: _allowed(rules, x) for x in paths}, "group": kind,
                         "blocks_site": _blocks_site(rules), "visibility_impact": "unknown",
                         "training_impact": "unknown", "honors_robots": "unknown", "verify": "unknown",
                         "source_url": None, "source_label": None, "verified_on": None, "needs_verification": True,
                         "in_registry": False, "notes": "Token not in the SEO-GEO-god registry (as of 2026-11-01)."})
    return rows


def robots_summary(robots: Optional[RobotsTxt]) -> Dict[str, Any]:
    """JSON-ready overview of a parsed file (groups, sitemaps, fields, flags)."""
    if robots is None:
        return {"present": False}
    return truncate({
        "present": True, "size": robots.size, "truncated": robots.truncated,
        "cloudflare_managed": robots.cloudflare_managed, "looks_html": robots.looks_html,
        "groups": [{"agents": g.agents, "line": g.line, "rules": len([r for r in g.rules if r[1]]),
                    "signals": [s["value"] for s in g.signals]} for g in robots.groups],
        "sitemaps": robots.sitemaps, "unknown_fields": sorted({u[0].lower() for u in robots.unknown}),
        "errors": robots.errors,
    })


# ----------------------------------------------------------------------------- offline checks

class _Emitter:
    def __init__(self, catalog: Optional[RuleCatalog], profile: str, **loc: Any) -> None:
        self.cat = catalog or default_catalog()
        self.profile, self.loc = profile, loc
        self.out: List[Finding] = []

    def __call__(self, rule: str, message: str, key: str, **kw: Any) -> None:
        loc = dict(self.loc)
        loc.update({k: kw.pop(k) for k in ("file", "url") if k in kw})
        self.out.append(make(rule, message, catalog=self.cat, key=key,
                             severity=self.cat.severity_for(rule, profile=self.profile), **loc, **kw))


def _star_groups(robots: RobotsTxt) -> List[Group]:
    return [g for g in robots.groups if "*" in {_product(a) for a in g.agents}]


def _named_groups(robots: RobotsTxt) -> List[Group]:
    return [g for g in robots.groups if any(_product(a) != "*" and not _is_policy(a) for a in g.agents)]


def check_robots(robots: Optional[RobotsTxt], catalog: Optional[RuleCatalog] = None, *,
                 registry: Optional[Dict[str, Any]] = None, asset_paths: Sequence[str] = (),
                 file: Optional[str] = None, url: Optional[str] = None, profile: str = "default") -> List[Finding]:
    """CRAWL001-007, CRAWL009, AI001-009, AI014 for one robots.txt (None = file absent)."""
    reg = registry or _registry()
    emit = _Emitter(catalog, profile, file=file if (file or url) else "robots.txt", url=url)
    if robots is None:
        emit("CRAWL001", "No robots.txt found: every path is crawlable by default and no crawl or AI-access "
             "policy is stated.", "missing")
        return emit.out
    _crawl_checks(robots, emit, asset_paths)
    _ai_checks(robots, emit, reg)
    return emit.out


def _crawl_checks(robots: RobotsTxt, emit: _Emitter, asset_paths: Sequence[str]) -> None:
    if robots.truncated:
        limit = thresholds()["robots_max_bytes"]
        emit("CRAWL002", "robots.txt is %d bytes; Google ignores content after %d bytes (500 KiB), so later rules "
             "do not apply." % (robots.size, limit), "size", evidence={"size_bytes": robots.size, "limit_bytes": limit})
    fields: Dict[str, List[int]] = {}
    for name, no in robots.unknown:
        fields.setdefault(name.lower(), []).append(no)
    for name in sorted(fields):
        lines = fields[name]
        emit("CRAWL003", "robots.txt uses the field %r (line %d%s); Google supports only user-agent, allow, "
             "disallow and sitemap and ignores it.%s" % (name[:40], lines[0], ", +%d more" % (len(lines) - 1)
                                                         if len(lines) > 1 else "", _FIELD_NOTES.get(name, "")),
             "field:" + name, line=lines[0], evidence={"field": name, "lines": lines})
    bad = list(robots.orphans) + list(robots.malformed)
    bad += [("%s: %s" % (d, p), no) for g in robots.groups for d, p, no in g.rules if p and p[0] not in "/*"]
    if bad or robots.looks_html:
        bad.sort(key=lambda x: x[1])
        what = ("robots.txt looks like an HTML page, not a robots file; " if robots.looks_html else "")
        emit("CRAWL009", "%s%d line(s) sit outside any User-agent group, are malformed, or have a rule path that "
             "does not start with / or *%s; crawlers ignore or misread them." % (
                 what, len(bad), " (first at line %d)" % bad[0][1] if bad else ""), "malformed",
             line=bad[0][1] if bad else None,
             evidence={"lines": [b[1] for b in bad], "examples": [b[0] for b in bad[:5]]})
    odd = [(p, no) for g in robots.groups for _d, p, no in g.rules if any(ord(c) > 127 or c.isspace() for c in p)]
    if odd:
        emit("CRAWL007", "%d rule path(s) contain spaces or non-ASCII characters (first at line %d); percent-encode "
             "them so every crawler matches the same URLs." % (len(odd), odd[0][1]), "encoding", line=odd[0][1],
             evidence={"paths": [p for p, _ in odd[:10]], "lines": [n for _, n in odd]})
    invalid = [(s, no) for s, no in zip(robots.sitemaps, robots.sitemap_lines) if not _absolute(s)]
    if not robots.sitemaps:
        emit("CRAWL006", "robots.txt has no Sitemap: line; add the absolute URL of each sitemap or sitemap index.",
             "sitemap-missing")
    elif invalid:
        emit("CRAWL006", "%d Sitemap: line(s) are not absolute http(s) URLs (first at line %d)." % (
            len(invalid), invalid[0][1]), "sitemap-invalid", line=invalid[0][1],
            evidence={"values": [s for s, _ in invalid]})
    star = _star_groups(robots)
    star_rules = [r for g in star for r in g.rules if r[1]]
    open_named = [g for g in _named_groups(robots) if not _blocks_site([r for r in g.rules if r[1]])]
    if star and _blocks_site(star_rules) and not open_named:
        emit("CRAWL004", "User-agent: * disallows the whole site (line %d) and no named group allows any crawler: "
             "search engines and AI crawlers that honor robots.txt will not crawl it." % star[0].line,
             "all-blocked", line=star[0].line, evidence={"group_line": star[0].line})
    g_rules, _ = _select(robots, "Googlebot")
    if not _blocks_site(g_rules):
        probes = not asset_paths
        paths = list(ASSET_PROBES if probes else dict.fromkeys(asset_paths))
        blocked = [p for p in paths if not _allowed(g_rules, p)]
        if blocked:
            emit("CRAWL005", "Googlebot is disallowed from %d %s needed to render pages (e.g. %s); allow CSS, "
                 "JavaScript and image paths." % (len(blocked), "typical asset path(s)" if probes else
                                                 "asset path(s)", blocked[0][:80]),
                 "assets", confidence="medium" if probes else "high",
                 evidence={"blocked": blocked[:20], "probe_paths": probes})


def _absolute(value: str) -> bool:
    parts = urllib.parse.urlsplit(value)
    return parts.scheme.lower() in ("http", "https") and bool(parts.netloc)


def _ai_checks(robots: RobotsTxt, emit: _Emitter, reg: Dict[str, Any]) -> None:
    star_only, crawl004 = [], any(f.rule == "CRAWL004" for f in emit.out)
    for e in reg["crawlers"]:
        rules, kind = _select(robots, e["token"], e.get("fallback"))
        rule, token, blocked = e["block_rule"], e["token"], _blocks_site(rules)
        line = _first_line(robots, kind.split(":", 1)[1] if kind.startswith("fallback:") else token)
        if line is None and kind == "*":
            line = _star_groups(robots)[0].line
        surfaces = ", ".join(e["visibility_surfaces"]) or "no documented surface"
        ev = {"token": token, "group": kind, "class": e["class"], "source_url": e["source_url"]}
        if rule == "AI004" and blocked:
            emit("AI004", "%s is disallowed from the whole site%s (line %s): this removes the site from %s." % (
                token, " by the * group" if kind == "*" else "", line, surfaces), "token:" + token.lower(),
                line=line, evidence=ev)
        elif rule == "AI003" and kind == "named" and any(d == "disallow" for d, _p, _n in rules or ()):
            emit("AI003", "robots.txt rules for %s (%s, user-triggered) may not be honored: the vendor documents "
                 "robots.txt support as %r. Use authentication or WAF rules if access must be blocked; blocking also "
                 "removes live answers that fetch the site." % (token, e["vendor"], e["honors_robots"]),
                 "token:" + token.lower(), line=line, evidence=ev)
        elif rule in ("AI001", "AI002") and blocked and kind == "*":
            if rule == "AI001":
                star_only.append(token)
        elif rule == "AI001" and blocked:
            via = " (it follows the %s group)" % kind.split(":", 1)[1] if kind.startswith("fallback:") else ""
            emit("AI001", "%s (%s) is disallowed from the whole site%s (line %s): the site is excluded from %s%s." % (
                token, e["vendor"], via, line, surfaces, "; the vendor does not describe its robots.txt handling"
                if e["honors_robots"] == "unknown" else ""), "token:" + token.lower(), line=line, evidence=ev)
        elif rule == "AI002" and blocked:
            emit("AI002", "%s (%s) is disallowed from the whole site (line %s): %s. It does not remove the site from "
                 "search results." % (token, e["vendor"], line, _training_effect(e)), "token:" + token.lower(),
                 line=line, evidence=ev)
    if star_only and not crawl004:
        star = _star_groups(robots)
        emit("AI014", "The * group blocks the whole site (line %d) for %d AI search or answer crawler(s) that have no "
             "group of their own (%s); add explicit groups to record the decision." % (
                 star[0].line, len(star_only), ", ".join(star_only[:6]) + (", ..." if len(star_only) > 6 else "")),
             "star-only", line=star[0].line, evidence={"tokens": star_only})
    _signal_checks(robots, emit)
    _policy_checks(robots, emit, reg)
    _cloudflare_check(robots, emit)


def _training_effect(e: Dict[str, Any]) -> str:
    if e["class"] == "CORPUS":
        return "the site leaves future %s corpus snapshots, which third parties reuse for AI training" % e["vendor"]
    if e["training"] is True:
        extra = "; it also stops use for %s" % ", ".join(e["visibility_surfaces"]) if e["visibility_surfaces"] else ""
        return "it states a preference against %s model training%s" % (e["vendor"], extra)
    return "the vendor does not document this token's purpose (%s)" % (e["notes"][:80] or "no notes")


def _signal_checks(robots: RobotsTxt, emit: _Emitter) -> None:
    for g in robots.groups:
        for s in g.signals:
            if s["malformed"] or s["unknown"]:
                emit("AI005", "Content-Signal on line %d is malformed or uses unknown keys; write comma-separated "
                     "key=yes|no pairs for search, ai-input and ai-train (use= is in testing)." % s["line"],
                     "signal:" + s["value"], line=s["line"],
                     evidence={"value": s["value"], "problems": s["problems"], "unknown_keys": s["unknown"]})
    star_signal = [s for g in _star_groups(robots) for s in g.signals]
    lacking = [g for g in _named_groups(robots) if not g.signals and "*" not in {_product(a) for a in g.agents}]
    if star_signal and lacking:
        emit("AI006", "%d named group(s) (first at line %d) have no Content-Signal line while the * group has one; "
             "named groups do not inherit lines from *." % (len(lacking), lacking[0].line), "signal-inherit",
             line=lacking[0].line, evidence={"groups": [g.agents for g in lacking[:20]],
                                             "star_signal": star_signal[0]["value"]})


def _policy_checks(robots: RobotsTxt, emit: _Emitter, reg: Dict[str, Any]) -> None:
    star = _star_groups(robots)
    for p in reg["policy_tokens"]:
        rules, kind = _select(robots, p["token"])
        if kind == "named":
            line = _first_line(robots, p["token"])
            allowed = _allowed(rules, "/")
            pref = "against AI training" if _blocks_site(rules) else "in favor" if allowed and not any(
                d == "disallow" for d, _x, _n in rules or ()) else "mixed by path"
            emit("AI007", "robots.txt states the shared AI-training preference %s (line %s): %s. It is a preference "
                 "(IETF individual draft), not access control; adoption differs by vendor (see evidence)." % (
                     p["token"], line, pref), "policy:" + p["token"], line=line,
                 evidence={"preference": pref, "honored_by": [h["vendor"] + ": " + h["from"] for h in p["honored_by"]],
                           "source_url": p["source_url"]})
            continue
        reasons = []
        if any(s.get("ai-train") == "no" for g in star for s in g.signals):
            reasons.append("Content-Signal ai-train=no in the * group")
        if any(g.line - 3 <= no <= g.end_line and _TRAINING_WORDS.search(c) for g in star
               for c, no in robots.comments):
            reasons.append("a comment about AI or training next to the * group")
        if reasons:
            emit("AI008", "The * group appears to carry an AI-training preference (%s), but User-agent: * never "
                 "matches the shared %s token; add a %s group, and keep vendor tokens, if that is the intent." % (
                     "; ".join(reasons), p["token"], p["token"]), "star-training:" + p["token"], line=star[0].line,
                 evidence={"reasons": reasons})


def _cloudflare_check(robots: RobotsTxt, emit: _Emitter, **loc: Any) -> None:
    if robots.cloudflare_managed:
        rng = robots.managed_range or (1, 1)
        inside = sorted({a for g in robots.groups if rng[0] <= g.line <= rng[1] for a in g.agents
                         if _blocks_site([r for r in g.rules if r[1]])}, key=str.lower)
        emit("AI009", "robots.txt contains a Cloudflare managed block (line %d), so rules injected at the edge can "
             "differ from the repository file; review the managed robots.txt and AI crawler settings with the "
             "owner." % rng[0], "cloudflare-managed", line=rng[0],
             evidence={"managed_lines": list(rng), "disallowed_in_block": inside[:30]}, **loc)


# ----------------------------------------------------------------------------- page directives and noindex

def _tokens(d: Any) -> set:
    if not isinstance(d, dict):
        return set()
    out = {str(t).strip().lower() for t in d.get("tokens") or ()}
    out.update(str(k).strip().lower() for k in (d.get("params") or {}))
    return out


def _int(value: Any) -> Optional[int]:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def check_page_ai_directives(directives_by_url: Dict[str, Dict[str, Any]],
                             catalog: Optional[RuleCatalog] = None) -> List[Finding]:
    """AI010-AI012 from page directives supplied by cli (via directives.py).

    Per URL: {"file"?, "google": effective(...,"googlebot"), "bingbot"?: effective(...,"bingbot"),
    "bing_ai"?: {"ai-training", "ai-grounding"}, "tokens"?: [...], "data_nosnippet"?: int}.
    `google` may be omitted when its keys (tokens, params, nosnippet, max_snippet, noindex) sit at top level.
    """
    emit = _Emitter(catalog, "default")
    for url in sorted(directives_by_url):
        entry = directives_by_url[url] or {}
        g = entry.get("google") if isinstance(entry.get("google"), dict) else entry
        loc = {"url": url if "://" in url else None, "file": entry.get("file") or (None if "://" in url else url)}
        toks = _tokens(g) | _tokens(entry.get("bingbot")) | _tokens(entry)
        params = g.get("params") or {}
        maxs = _int(g.get("max_snippet") if g.get("max_snippet") is not None else params.get("max-snippet"))
        if maxs is None:  # tolerate unparsed "max-snippet:N" tokens
            maxs = next((_int(t.split(":", 1)[1]) for t in sorted(_tokens(g)) if t.startswith("max-snippet:")), None)
        nosnip = bool(g.get("nosnippet")) or "nosnippet" in _tokens(g) or maxs == 0
        dns = _int(entry.get("data_nosnippet")) or 0
        noindex = bool(g.get("noindex")) or bool({"noindex", "none"} & _tokens(g))
        if not noindex and (nosnip or (maxs is not None and maxs > 0) or dns > 0):
            parts = []
            if nosnip:
                parts.append("nosnippet prevents its use as direct input for Google AI Overviews and AI Mode")
            elif maxs is not None and maxs > 0:
                parts.append("max-snippet:%d limits how much of it AI Overviews and AI Mode may use" % maxs)
            if dns:
                parts.append("%d data-nosnippet element(s) are excluded from snippets and that input" % dns)
            emit("AI010", "On this page " + "; ".join(parts) + ".", "snippet-controls",
                 evidence={"nosnippet": nosnip, "max_snippet": maxs, "data_nosnippet": dns}, **loc)
        used = sorted({"noarchive", "nocache"} & toks)
        if used:
            emit("AI011", "%s does nothing for Google; Bing reads it as a Copilot AI signal only until 2027-03-01 "
                 "(as of 2026-11-01). Use Google-Extended and Bingbot ai-training or ai-grounding directives for AI "
                 "choices." % "/".join(used), "noarchive", evidence={"directives": used}, **loc)
        bing = {k: v for k, v in (entry.get("bing_ai") or {}).items() if v}
        if bing:
            emit("AI012", "Bingbot %s is set; Bing honors these preferences from 2027-02-01, and a page-level training "
                 "preference overrides robots.txt." % ", ".join("%s:%s" % (k, v) for k, v in sorted(bing.items())),
                 "bing-ai", evidence={"bing_ai": bing}, **loc)
    return emit.out


def check_blocked_noindex(robots: Optional[RobotsTxt], noindex_urls: Sequence[str],
                          catalog: Optional[RuleCatalog] = None) -> List[Finding]:
    """CRAWL008: noindex pages (URLs or URL paths) that robots.txt hides from Googlebot or bingbot."""
    emit = _Emitter(catalog, "default")
    if robots is None:
        return []
    for u in sorted(set(noindex_urls)):
        blocked = [t for t in ("Googlebot", "bingbot") if not is_allowed(robots, t, u)]
        if blocked:
            loc = {"url": u} if "://" in u else {"file": u}
            emit("CRAWL008", "This page is noindex but robots.txt disallows it for %s, so the noindex cannot be seen "
                 "and the URL can stay indexed without its content." % " and ".join(blocked), "noindex-blocked",
                 evidence={"blocked_for": blocked}, **loc)
    return emit.out


# ----------------------------------------------------------------------------- live access check

def _origin(origin: str) -> str:
    parts = urllib.parse.urlsplit(origin.strip())
    if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
        raise ValueError("origin must be an absolute http(s) URL")
    return "%s://%s" % (parts.scheme.lower(), parts.netloc.lower())


def _resp(r: Any) -> Dict[str, Any]:
    headers = {str(k).lower(): str(v) for k, v in (getattr(r, "headers", None) or {}).items()}
    status = getattr(r, "status", None)
    ctype = (getattr(r, "content_type", None) or headers.get("content-type", "")).split(";", 1)[0].strip().lower()
    return {"status": status, "headers": headers, "content_type": ctype, "text": getattr(r, "text", None) or "",
            "error_kind": getattr(r, "error_kind", None), "error": getattr(r, "error", None),
            "ok": status is not None and 200 <= status < 300 and getattr(r, "error_kind", None) in (None, "too_large"),
            "final_url": getattr(r, "url", None)}


def _robots_preference(robots: Optional[RobotsTxt], reg: Dict[str, Any]) -> Dict[str, Tuple[str, str]]:
    pref: Dict[str, Tuple[str, str]] = {}
    if robots is None:
        return pref
    groups = _star_groups(robots) or robots.groups
    for g in groups:
        for s in g.signals:
            for k in reg["content_signals"]["keys"]:
                if s.get(k) and (k not in pref or s[k] == "no"):
                    pref[k] = (s[k], "robots.txt Content-Signal line %d" % s["line"])
    if pref.get("ai-train", ("",))[0] != "no":
        for p in reg["policy_tokens"]:
            if _blocks_site(_select(robots, p["token"])[0]):
                pref["ai-train"] = ("no", "robots.txt %s group" % p["token"])
    if "ai-train" not in pref:
        trains = [e["token"] for e in reg["crawlers"] if e["class"] in ("TRAIN", "CONTROL") and e["training"] is True]
        kinds = [(_select(robots, t)) for t in trains]
        named = [(r, k) for r, k in kinds if k == "named"]
        if named and all(_blocks_site(r) for r, _k in named):
            pref["ai-train"] = ("no", "robots.txt training-crawler groups")
    return pref


def access_check(origin: str, *, fetch: Callable[..., Any], catalog: Optional[RuleCatalog] = None,
                 registry: Optional[Dict[str, Any]] = None,
                 llms_check: Optional[Callable[[str], Sequence[Finding]]] = None, ignore_robots: bool = False,
                 robots_findings: bool = False, probe_well_known: bool = True) -> Tuple[Dict[str, Any], List[Finding]]:
    """Live AI-access checks for one origin through the injected `fetch(url, accept=, max_bytes=)`.

    robots.txt status (AI015; 4xx gives CRAWL001), Cloudflare managed block (AI009), Content-Signal response
    headers vs robots.txt (AI013), unknown-URL probe (HTTP004), llms.txt served as HTML (AGENT004),
    /.well-known/ JSON documents (AGENT008). Our crawler's robots semantics apply to every probe unless
    `ignore_robots`. `llms_check(text)` (from cli) validates a served llms.txt; `robots_findings` adds
    check_robots() findings for the live file.
    """
    reg = registry or _registry()
    emit = _Emitter(catalog, "default")
    base = _origin(origin)
    data: Dict[str, Any] = {"origin": base, "skipped": [], "requests": 0}

    def get(path: str, accept: str, max_bytes: int) -> Dict[str, Any]:
        data["requests"] += 1
        return _resp(fetch(base + path, accept=accept, max_bytes=max_bytes))

    rurl = base + "/robots.txt"
    r = get("/robots.txt", "text/plain,*/*;q=0.1", 1_048_576)
    info: Dict[str, Any] = {"url": rurl, "status": r["status"], "content_type": r["content_type"],
                            "error_kind": r["error_kind"]}
    robots: Optional[RobotsTxt] = None
    if r["error_kind"] == "url_refused" and r["status"] is None:
        info["outcome"] = "refused"
        data.update(robots=info, error="refused by the fetch safety policy: %s" % (r["error"] or "")[:160])
        return truncate(data), emit.out
    if r["ok"]:
        robots = parse_robots(r["text"])
        info.update(outcome="parsed", size=robots.size, truncated=robots.truncated or r["error_kind"] == "too_large",
                    cloudflare_managed=robots.cloudflare_managed, groups=len(robots.groups),
                    content_signals=[{"agents": g.agents, "line": s["line"], "value": s["value"],
                                      "malformed": s["malformed"]} for g in robots.groups for s in g.signals])
        if robots_findings:
            emit.out.extend(check_robots(robots, emit.cat, registry=reg, url=rurl))
        else:
            _cloudflare_check(robots, emit, url=rurl)
    elif r["error"] is None and r["status"] is not None and 400 <= r["status"] < 500 and r["status"] != 429:
        info["outcome"] = "no-restrictions"
        emit("CRAWL001", "robots.txt returns HTTP %d: crawlers treat every path as allowed and no crawl or AI policy "
             "is stated." % r["status"], "missing", url=rurl, evidence={"status": r["status"]})
    elif r["error_kind"] == "too_many_redirects":
        info["outcome"] = "too-many-redirects"
        emit("CRAWL001", "robots.txt redirects more than 5 times: Google follows at least 5 hops and treats a longer "
             "chain as not found, so no crawl or AI policy may apply. Serve the file directly or with one redirect.",
             "missing", url=rurl, confidence="medium", evidence={"error_kind": r["error_kind"]})
    elif r["error_kind"] == "url_refused":
        info["outcome"] = "refused"
    else:
        info["outcome"] = "unreachable"
        emit("AI015", "robots.txt %s: RFC 9309 crawlers treat this as a full disallow. Google stops crawling for about "
             "12 hours, then relies on its last cached copy for up to 30 days (as of 2026-11-01)." % (
                 "returns HTTP %d" % r["status"] if r["status"] else "is unreachable (%s)" % (r["error_kind"] or "error")),
             "robots-status", url=rurl, evidence={"status": r["status"], "error_kind": r["error_kind"]})
    data["robots"] = info

    def permitted(path: str) -> bool:
        if ignore_robots or info["outcome"] in ("no-restrictions", "too-many-redirects"):
            return True
        if info["outcome"] == "parsed":
            ok = is_allowed(robots, OUR_TOKEN, path)
        else:
            ok = path == "/"
        if not ok:
            data["skipped"].append({"path": path, "reason": "robots.txt disallows %s or is unreachable" % OUR_TOKEN})
        return ok

    pref = _robots_preference(robots, reg)
    clashes = []
    if permitted("/"):
        for source, accept in (("homepage", HTML_ACCEPT), ("markdown", "text/markdown")):
            resp = get("/", accept, 65536)
            value = resp["headers"].get("content-signal")
            data[source] = {"url": base + "/", "status": resp["status"], "content_type": resp["content_type"],
                            "content_signal": value, "x_robots_tag": resp["headers"].get("x-robots-tag")}
            if source == "markdown":
                data[source].update(served_markdown=resp["content_type"] == "text/markdown",
                                    vary_accept="accept" in [v.strip().lower() for v in
                                                             resp["headers"].get("vary", "").split(",")])
            parsed = parse_content_signal(value, registry=reg) if value else {}
            diff = [{"key": k, "robots": pref[k][0], "robots_source": pref[k][1], "header": parsed[k]}
                    for k in reg["content_signals"]["keys"] if parsed.get(k) and k in pref and pref[k][0] != parsed[k]]
            if diff:
                clashes.append(source)
                emit("AI013", "The %s response sends Content-Signal %r, which contradicts robots.txt (%s); align the "
                     "CDN or origin header with robots.txt." % (source, value[:80], ", ".join(
                         "%s=%s" % (d["key"], d["robots"]) for d in diff)), "content-signal-header:" + source,
                     url=base + "/", evidence={"source": source, "conflicts": diff})
    data["contradictions"] = clashes
    probe = "/seo-geo-god-404-probe-" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    soft = False
    if permitted(probe):
        p = get(probe, HTML_ACCEPT, 65536)
        soft = bool(p["ok"])
        data["not_found_probe"] = {"url": base + probe, "status": p["status"], "final_url": p["final_url"],
                                   "soft_404": soft}
        if soft:
            emit("HTTP004", "An unknown URL returned HTTP %s instead of 404 or 410 (catch-all route); crawlers can "
                 "index such pages as soft 404s." % p["status"], "soft-404-probe", url=base + probe,
                 evidence={"status": p["status"], "final_url": p["final_url"]})
    if permitted("/llms.txt"):
        lr = get("/llms.txt", TEXT_ACCEPT, 1_048_576)
        html = lr["ok"] and (lr["content_type"] in ("text/html", "application/xhtml+xml") or _looks_html(lr["text"]))
        data["llms"] = {"url": base + "/llms.txt", "status": lr["status"], "content_type": lr["content_type"],
                        "present": bool(lr["ok"]) and not html, "served_as_html": bool(html)}
        if html:
            emit("AGENT004", "/llms.txt returns an HTML page (HTTP %s, %s), which is likely a soft 404; serve text or "
                 "Markdown, or return 404." % (lr["status"], lr["content_type"] or "no content type"),
                 "llms-html", url=base + "/llms.txt", evidence={"status": lr["status"],
                                                               "content_type": lr["content_type"]})
        elif lr["ok"] and llms_check is not None:
            emit.out.extend(llms_check(lr["text"]))
    if permitted("/llms-full.txt"):
        fr = get("/llms-full.txt", TEXT_ACCEPT, 65536)
        data["llms_full"] = {"url": base + "/llms-full.txt", "status": fr["status"],
                             "present": bool(fr["ok"]) and not _looks_html(fr["text"])}
    if probe_well_known:
        data["well_known"], issues = [], []
        for path in WELL_KNOWN:
            if not permitted(path):
                continue
            w = get(path, "application/json,application/linkset+json;q=0.9,*/*;q=0.1", 262144)
            if not w["ok"]:
                outcome = "absent"
            elif w["content_type"] in ("text/html", "application/xhtml+xml") or _looks_html(w["text"]):
                outcome = "html"
            else:
                outcome = "too-large" if w["error_kind"] == "too_large" else _json_outcome(w["text"])
            data["well_known"].append({"path": path, "status": w["status"], "content_type": w["content_type"],
                                       "outcome": outcome})
            if outcome in ("html", "invalid-json"):
                issues.append("%s (%s)" % (path, outcome))
        if issues:
            emit("AGENT008", "%d /.well-known/ document(s) return HTML or invalid JSON: %s; serve valid JSON or return "
                 "404.%s" % (len(issues), ", ".join(issues), " The unknown-URL probe also returned 200, so a "
                             "catch-all route is the likely cause." if soft else ""), "well-known",
                 url=base + "/.well-known/", evidence={"documents": issues})
    return truncate(data), emit.out


def _json_outcome(text: str) -> str:
    try:
        loads_json(text)
    except ValueError:
        return "invalid-json"
    return "json"
