"""Robots meta tag and X-Robots-Tag parsing with most-restrictive merging (WP02).

Parameter values are bound before tokenizing, so ``max-image-preview: none`` is a parameter and
never the ``none`` directive. ``unavailable_after`` accepts ISO 8601 and RFC 822/850 dates
(which contain commas). Conflicting values resolve to the most restrictive one, as Google
documents; conflicts are reported. Header values may hold several header lines joined by "\\n".
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple

PARAMS = ("max-snippet", "max-image-preview", "max-video-preview", "unavailable_after", "ai-training",
          "ai-grounding")
IGNORED_BY_GOOGLE = ("noarchive", "nocache", "nositelinkssearchbox")
_PARAM_RE = re.compile(r"(%s)\s*:\s*" % "|".join(re.escape(p) for p in PARAMS), re.I)
_DATE_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:\s*(?:Z|[+-]\d{2}:?\d{2}|[A-Z]{2,5}\b))?)?"
    r"|(?:[A-Za-z]{3,9},?\s+)?\d{1,2}[- ][A-Za-z]{3,9}[- ]\d{2,4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?"
    r"(?:\s+(?:[A-Z]{1,5}\b|[+-]\d{4}))?")
_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?)?"
                     r"\s*(Z|[+-]\d{2}:?\d{2})?$", re.I)
_VALUE_RE = re.compile(r"[^\s,]*")
_TOKEN_RE = re.compile(r"[^\s,]+")
_SEP_RE = re.compile(r"[\s,]+")
_AGENT_RE = re.compile(r"(?:^|,)\s*([A-Za-z][A-Za-z0-9_.-]*)\s*:")
_ORDER = {"max-image-preview": {"none": 0, "standard": 1, "large": 2},
          "ai-grounding": {"disallow": 0, "disallowextended": 1, "allow": 2},
          "ai-training": {"disallow": 0, "allow": 1}}


def parse_date(value: str) -> Optional[datetime]:
    """ISO 8601 or RFC 822/850 date as an aware datetime (UTC assumed when no zone); None if unparsable.

    ISO forms are parsed with a regex (not ``fromisoformat``) so results match on Python 3.9-3.13.
    """
    text = (value or "").strip()
    m = _ISO_RE.match(text)
    if m:
        year, month, day, hour, minute, second, zone = m.groups()
        try:
            dt = datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0), int(second or 0))
            if zone and zone.upper() != "Z":
                digits = zone[1:].replace(":", "")
                offset = timedelta(hours=int(digits[:2]), minutes=int(digits[2:]))
                return dt.replace(tzinfo=timezone(offset if zone[0] == "+" else -offset))
        except ValueError:
            return None
        return dt.replace(tzinfo=timezone.utc)
    if not text or re.match(r"\d{4}-", text):
        return None
    try:
        dt = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _tokenize(text: str) -> Tuple[List[str], List[Tuple[str, str]]]:
    tokens: List[str] = []
    pairs: List[Tuple[str, str]] = []
    i, n = 0, len(text)
    while i < n:
        sep = _SEP_RE.match(text, i)
        if sep:
            i = sep.end()
            continue
        m = _PARAM_RE.match(text, i)
        if m:
            name, j = m.group(1).lower(), m.end()
            if name == "unavailable_after":
                dm = _DATE_RE.match(text, j)
                if dm:
                    value, i = dm.group(0), dm.end()
                else:
                    k = text.find(",", j)
                    k = n if k < 0 else k
                    value, i = text[j:k].strip(), k
            else:
                vm = _VALUE_RE.match(text, j)
                value, i = vm.group(0).lower(), vm.end()
            pairs.append((name, value))
            continue
        tm = _TOKEN_RE.match(text, i)
        tokens.append(tm.group(0).lower())
        i = tm.end()
    return tokens, pairs


def _int(value: Any) -> Optional[int]:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _rank(name: str, value: str) -> Tuple[int, Any]:
    """Lower rank = more restrictive; unparsable values rank last."""
    if name in ("max-snippet", "max-video-preview"):
        v = _int(value)
        return (2, 0) if v is None else (0, v) if v >= 0 else (1, 0)
    if name == "unavailable_after":
        dt = parse_date(value)
        return (1, 0) if dt is None else (0, dt.timestamp())
    order = _ORDER.get(name, {})
    return (0, order[value]) if value in order else (1, 0)


def _merge_param(params: Dict[str, str], name: str, value: str, conflicts: List[str]) -> None:
    old = params.get(name)
    if old is None:
        params[name] = value
        return
    if old != value:
        conflicts.append("%s: %s vs %s" % (name, old, value))
        if _rank(name, value) < _rank(name, old):
            params[name] = value


def _summary(tokens: Set[str], params: Dict[str, str], conflicts: List[str]) -> Dict[str, Any]:
    noindex = bool(tokens & {"noindex", "none"})
    nofollow = bool(tokens & {"nofollow", "none"})
    if noindex and tokens & {"index", "all"}:
        conflicts.append("index vs noindex")
    if nofollow and tokens & {"follow", "all"}:
        conflicts.append("follow vs nofollow")
    max_snippet = _int(params.get("max-snippet"))
    return {"tokens": tokens, "params": params, "noindex": noindex, "nofollow": nofollow,
            "nosnippet": "nosnippet" in tokens or max_snippet == 0, "max_snippet": max_snippet,
            "max_image_preview": params.get("max-image-preview"),
            "unavailable_after": params.get("unavailable_after"),
            "ignored": sorted(tokens & set(IGNORED_BY_GOOGLE)), "conflicts": sorted(set(conflicts))}


def parse_robots_values(values: Iterable[str]) -> Dict[str, Any]:
    """Parse robots meta contents (one or more): {tokens:set, params:{}, noindex, nofollow, nosnippet, max_snippet, ...}."""
    tokens: Set[str] = set()
    params: Dict[str, str] = {}
    conflicts: List[str] = []
    for raw in values:
        toks, pairs = _tokenize(str(raw or ""))
        tokens.update(toks)
        for name, value in pairs:
            _merge_param(params, name, value, conflicts)
    return _summary(tokens, params, conflicts)


def _split_agents(line: str) -> List[Tuple[str, str]]:
    marks = [m for m in _AGENT_RE.finditer(line) if m.group(1).lower() not in PARAMS]
    if not marks:
        return [("*", line)] if line.strip() else []
    out = [("*", line[:marks[0].start()])] if line[:marks[0].start()].strip(" ,") else []
    for idx, m in enumerate(marks):
        end = marks[idx + 1].start() if idx + 1 < len(marks) else len(line)
        out.append((m.group(1).lower(), line[m.end():end]))
    return out


def parse_x_robots(values: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    """X-Robots-Tag header values -> {agent: parsed}; unprefixed values go to "*" ("googlebot: noindex")."""
    groups: Dict[str, List[str]] = {}
    for raw in values:
        for line in str(raw or "").split("\n"):
            for agent, text in _split_agents(line):
                groups.setdefault(agent, []).append(text)
    return {agent: parse_robots_values(texts) for agent, texts in sorted(groups.items())}


def effective(meta: Mapping[str, List[str]], xrobots: Optional[Mapping[str, Dict[str, Any]]] = None,
              bot: str = "googlebot") -> Dict[str, Any]:
    """Most restrictive combination of robots + <bot> meta tags and "*" + <bot> X-Robots-Tag groups.

    Adds ``sources`` (where directives came from), ``noindex_sources`` and ``header_noindex``.
    """
    bot = bot.lower()
    parts: List[Tuple[str, Dict[str, Any]]] = []
    for name in dict.fromkeys(("robots", bot)):
        values = list(meta.get(name, []) or [])
        if values:
            parts.append(("meta:" + name, parse_robots_values(values)))
    for agent in dict.fromkeys(("*", bot)):
        if xrobots and agent in xrobots:
            parts.append(("header:" + agent, xrobots[agent]))
    tokens: Set[str] = set()
    params: Dict[str, str] = {}
    conflicts: List[str] = []
    for _, parsed in parts:
        tokens |= set(parsed["tokens"])
        conflicts.extend(parsed["conflicts"])
        for name, value in parsed["params"].items():
            _merge_param(params, name, value, conflicts)
    out = _summary(tokens, params, conflicts)
    out["sources"] = [src for src, _ in parts]
    out["noindex_sources"] = [src for src, parsed in parts if parsed["noindex"]]
    out["header_noindex"] = any(src.startswith("header:") and parsed["noindex"] for src, parsed in parts)
    return out


def bing_ai(meta: Mapping[str, List[str]], xrobots: Optional[Mapping[str, Dict[str, Any]]] = None
            ) -> Dict[str, Optional[str]]:
    """Bingbot AI preferences from the Bingbot meta tag and the "bingbot:" X-Robots-Tag group."""
    params: Dict[str, str] = {}
    sources = []
    if meta.get("bingbot"):
        sources.append(parse_robots_values(meta["bingbot"]))
    if xrobots and "bingbot" in xrobots:
        sources.append(xrobots["bingbot"])
    for parsed in sources:
        for name, value in parsed["params"].items():
            _merge_param(params, name, value, [])
    training = params.get("ai-training")
    grounding = params.get("ai-grounding")
    return {"ai-training": "disallow" if training == "disallow" else None,
            "ai-grounding": grounding if grounding in ("disallow", "disallowextended") else None}
