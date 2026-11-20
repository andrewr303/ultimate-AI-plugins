"""hreflang code validation, reciprocity and cluster checks (WP02).

Codes follow Google's localized-versions page (2026-09-21, fact F-T-31): an ISO 639-1 language,
an optional ISO 15924 script, an optional ISO 3166-1 alpha-2 region, or ``x-default``. Region-only
codes, numeric UN M.49 regions (``es-419``) and the reserved ``UK``/``EU``/``UN`` are invalid.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit

from .findings import Finding, make
from .rulesdb import RuleCatalog, default_catalog

ISO_639_1 = frozenset((
    "aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu cv cy da de dv dz ee el "
    "en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he hi ho hr ht hu hy hz ia id ie ig ii ik io is it iu "
    "ja jv ka kg ki kj kk kl km kn ko kr ks ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms mt my na "
    "nb nd ne ng nl nn no nr nv ny oc oj om or os pa pi pl ps pt qu rm rn ro ru rw sa sc sd se sg si sk sl sm sn so "
    "sq sr ss st su sv sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo xh yi yo za zh zu"
).split())
ISO_3166_1 = frozenset((
    "AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ "
    "CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO "
    "FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE "
    "JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO "
    "MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW "
    "PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM "
    "TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW"
).split())
RESERVED_REGIONS = {"UK": "UK is reserved; use GB for the United Kingdom", "EU": "EU is a reserved code, not a country",
                    "UN": "UN is a reserved code, not a country"}
_AS_LANGUAGE = {"uk": " (as a language code, uk means Ukrainian)", "eu": " (as a language code, eu means Basque)"}
_SAFE = "/!$&'()*+,;=:@-._~"
_DEFAULT_PORT = {"http": 80, "https": 443}
Entry = Tuple[str, str, str, Optional[int], str]   # (code, raw href, comparison key of the target, line, origin)


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


def _loose(url: str) -> str:
    n = normalize_url(url)
    parts = urlsplit(n)
    if parts.path.endswith("/") and parts.path != "/":
        return urlunsplit((parts.scheme, parts.netloc, parts.path[:-1], parts.query, ""))
    return n


def code_problem(code: str) -> Optional[str]:
    """None when `code` is a valid hreflang value; otherwise the reason it is not."""
    raw = (code or "").strip()
    if not raw:
        return "empty code"
    if raw.lower() == "x-default":
        return None
    if "_" in raw:
        return "use a hyphen (en-US), not an underscore"
    parts = raw.split("-")
    lang = parts[0].lower()
    if len(parts) == 1 and parts[0].upper() in RESERVED_REGIONS and (parts[0].isupper() or lang not in ISO_639_1):
        return RESERVED_REGIONS[parts[0].upper()] + _AS_LANGUAGE.get(lang, "")
    if len(lang) != 2 or not lang.isalpha():
        if len(lang) == 3 and lang.isalpha():
            return "%s is not an ISO 639-1 two-letter language code" % parts[0]
        return "language must be an ISO 639-1 two-letter code"
    if lang not in ISO_639_1:
        if parts[0].upper() in ISO_3166_1 or parts[0].upper() in RESERVED_REGIONS:
            return "%s is a region, not a language; add a language first (e.g. en-%s)" % (parts[0], parts[0].upper())
        return "%s is not an ISO 639-1 language code" % parts[0]
    rest = parts[1:]
    if rest and len(rest[0]) == 4 and rest[0].isalpha():
        rest = rest[1:]   # ISO 15924 script subtag, e.g. zh-Hant
    if len(rest) > 1:
        return "too many subtags"
    if rest:
        region = rest[0].upper()
        if region in RESERVED_REGIONS:
            return RESERVED_REGIONS[region]
        if region.isdigit():
            return "numeric region codes (UN M.49, e.g. 419) are not supported"
        if len(region) != 2 or region not in ISO_3166_1:
            return "%s is not an ISO 3166-1 alpha-2 region" % rest[0]
    return None


def _primary(code: str) -> str:
    return (code or "").split("-")[0].lower()


def _base(url: str, doc: Any) -> str:
    if getattr(doc, "base_href", None):
        candidate = urljoin(url, doc.base_href)
        return candidate if urlsplit(candidate).scheme in ("http", "https") else url
    return url


def _entries(url: str, doc: Any, sitemap_alternates: Optional[Dict[str, List[Tuple[str, str]]]]) -> List[Entry]:
    base = _base(url, doc)
    out: List[Entry] = []
    for code, href, line in getattr(doc, "hreflang", []) or []:
        out.append((code.strip(), href, _loose(urljoin(base, href.strip())), line, "html"))
    if sitemap_alternates:
        key = _loose(url)
        for loc, pairs in sitemap_alternates.items():
            if _loose(loc) == key:
                for code, href in pairs:
                    entry = (code.strip(), href, _loose(urljoin(url, href.strip())), None, "sitemap")
                    if not any(e[0].lower() == entry[0].lower() and e[2] == entry[2] for e in out):
                        out.append(entry)
    return out


def clusters(pages: Dict[str, Any], *, sitemap_alternates: Optional[Dict[str, List[Tuple[str, str]]]] = None
             ) -> List[Dict[str, Any]]:
    """Connected hreflang clusters: [{pages, matrix: {url: {code: absolute target}}, x_default}], sorted."""
    keys = {_loose(u): u for u in pages}
    parent = {u: u for u in pages}

    def find(u: str) -> str:
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    sets = {u: _entries(u, pages[u], sitemap_alternates) for u in sorted(pages)}
    for u, entries in sets.items():
        for code, _, target, _, _ in entries:
            if target in keys and code_problem(code) is None:
                parent[find(u)] = find(keys[target])
    groups: Dict[str, List[str]] = {}
    for u in sorted(pages):
        if sets[u]:
            groups.setdefault(find(u), []).append(u)
    out = []
    for members in sorted(groups.values()):
        matrix = {u: {e[0].lower(): urljoin(_base(u, pages[u]) if e[4] == "html" else u, e[1].strip())
                      for e in sets[u]} for u in members}
        x_default = next((t for u in members for c, t in matrix[u].items() if c == "x-default"), None)
        out.append({"pages": members, "matrix": matrix, "x_default": x_default})
    return out


def check_hreflang(pages: Dict[str, Any], catalog: Optional[RuleCatalog] = None, *,
                   canonical_of: Optional[Callable[[str], Optional[str]]] = None,
                   sitemap_alternates: Optional[Dict[str, List[Tuple[str, str]]]] = None,
                   noindex_of: Optional[Callable[[str], bool]] = None) -> List[Finding]:
    """HREF001-008 and CANON007 over pages keyed by absolute URL (PageDoc-like objects).

    `canonical_of(url)` and `noindex_of(url)` come from sitescan.hreflang_inputs; without them the
    noindex and non-canonical parts of HREF006 and CANON007 are not evaluated.
    """
    cat = catalog or default_catalog()
    out: List[Finding] = []

    def emit(rule: str, message: str, **kw: Any) -> None:
        if cat.get(rule).status == "v1":
            out.append(make(rule, message, catalog=cat, **kw))

    keys = {_loose(u): u for u in pages}
    sets = {u: _entries(u, pages[u], sitemap_alternates) for u in sorted(pages)}
    self_code: Dict[str, Optional[str]] = {}
    for u, entries in sets.items():
        self_code[u] = next((c for c, _, t, _, _ in entries if t == _loose(u) and c.lower() != "x-default"
                             and code_problem(c) is None), None)
    for url in sorted(pages):
        entries = sets[url]
        if not entries:
            continue
        doc = pages[url]
        loc = {"file": getattr(doc, "path", None), "url": url}
        me = _loose(url)
        seen: Dict[str, Tuple[str, str]] = {}
        for code, href, target, line, origin in entries:
            problem = code_problem(code)
            if problem:
                emit("HREF001", "Invalid hreflang code %r: %s." % (code, problem), key="code:" + code.lower(),
                     line=line, evidence={"observed": code, "reason": problem}, **loc)
                continue
            if not urlsplit(href.strip()).scheme:
                emit("HREF005", "Relative hreflang URL for %s: %s" % (code, href), key="relative:" + href[:200],
                     line=line, evidence={"observed": href, "source": origin}, **loc)
            low = code.lower()
            if low in seen and seen[low][0] != target:
                emit("HREF007", "Code %s is listed for more than one URL." % code, key="dup:" + low, line=line,
                     evidence={"observed": [seen[low][1], urljoin(url, href.strip())]}, **loc)
            seen.setdefault(low, (target, urljoin(url, href.strip())))
        valid = [e for e in entries if code_problem(e[0]) is None]
        if valid and self_code[url] is None and not any(t == me for _, _, t, _, _ in valid):
            emit("HREF002", "Page lists alternates but not itself.", key="self", evidence={"codes": sorted(
                {e[0] for e in valid})}, **loc)
        for code, href, target, line, origin in valid:
            if target == me:
                continue
            other = keys.get(target)
            shown = urljoin(url, href.strip())
            if other is None:
                if urlsplit(target).netloc == urlsplit(me).netloc:
                    emit("HREF006", "hreflang target %s is not in the site." % shown, key="target:" + target,
                         line=line, evidence={"observed": shown, "reason": "missing"}, **loc)
                continue
            back = [c for c, _, t, _, _ in sets[other] if t == me and code_problem(c) is None]
            if not back:
                emit("HREF003", "%s does not link back to this page." % other, key="return:" + target, line=line,
                     evidence={"observed": other, "code": code}, **loc)
            elif self_code[url] and not any(c.lower() == self_code[url].lower() for c in back):
                emit("HREF003", "%s links back with code %s, but this page declares itself as %s." % (
                    other, ", ".join(sorted(back)), self_code[url]), key="return-code:" + target, line=line,
                    evidence={"observed": sorted(back), "expected": self_code[url]}, **loc)
            reason = None
            if noindex_of is not None and noindex_of(other):
                reason = "noindex"
            elif canonical_of is not None:
                canon = canonical_of(other)
                if canon and _loose(canon) != target:
                    reason = "canonicalized to %s" % canon
            if reason:
                emit("HREF006", "hreflang target %s is %s." % (shown, reason), key="target:" + target, line=line,
                     evidence={"observed": shown, "reason": reason}, **loc)
        mine = self_code[url]
        lang = (getattr(doc, "lang", None) or "").strip()
        if mine and lang and _primary(lang) != _primary(mine):
            emit("HREF008", "html lang %s differs from the page's own hreflang %s." % (lang, mine), key="lang",
                 evidence={"observed": lang, "expected": mine}, **loc)
        if canonical_of is not None:
            canon = canonical_of(url)
            if canon and _loose(canon) != me:
                target_code = next((c for c, _, t, _, _ in valid if t == _loose(canon) and c.lower() != "x-default"),
                                   None)
                other = keys.get(_loose(canon))
                other_lang = target_code or self_code.get(other or "") or (
                    getattr(pages[other], "lang", None) if other else None)
                own = mine or lang
                if own and other_lang and _primary(other_lang) != _primary(own):
                    emit("CANON007", "Canonical %s is a %s version; this page is %s." % (canon, other_lang, own),
                         key="cross-language", evidence={"observed": canon, "canonical_lang": other_lang,
                                                         "page_lang": own}, **loc)
    for cluster in clusters(pages, sitemap_alternates=sitemap_alternates):
        if cluster["x_default"] is None:
            first = cluster["pages"][0]
            emit("HREF004", "hreflang cluster of %d pages has no x-default." % len(cluster["pages"]),
                 key="x-default", url=first, file=getattr(pages[first], "path", None),
                 affected=len(cluster["pages"]), sample=cluster["pages"])
    return out
