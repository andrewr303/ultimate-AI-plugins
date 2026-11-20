"""Deterministic fidelity gate for section rewrites (WP05; rules FID001-FID010).

A rewrite may change wording, order and emphasis. It may not change facts. The checks are adapted
from eGEOagents ``egeo/fidelity.py`` (MIT) and extended with HTML ``<a href>`` links, reference-style
link definitions, ``<pre>`` blocks, the full heading sequence, superlative additions and caveat
removals:

* ``heading_changed``: the heading lines (ATX outside fences, or ``<h1>``-``<h6>``) differ; skipped
  when the original has no heading.
* ``link_removed:<url>`` / ``link_added:<url>``: targets of Markdown links and images, autolinks,
  bare http(s) URLs (trailing ``.,;:`` stripped), HTML ``href`` values and reference definitions.
* ``number_removed:<n>`` / ``number_added:<n>``: ``(?<![\\w.])[$\u20ac\u00a3]?\\d[\\d,]*(?:\\.\\d+)?%?`` after
  removing fenced code, link targets and HTML tags; ``$``, ``\u20ac``, ``\u00a3`` and ``,`` are dropped
  (``$1,185`` -> ``1185``; ``40%`` stays ``40%``).
* ``table_rows_decreased``: fewer lines starting with ``|`` (plus ``<tr>`` tags).
* ``code_block_changed``: the fenced code blocks (exact text, in order) differ.
* ``too_short`` / ``too_long``: rewrite/original word ratio outside the limits; only when the
  original has at least `min_words` words.
* ``superlative_added:<w>`` / ``caveat_removed:<p>``: presence-based phrase checks (case-insensitive)
  using data/content-lexicons.json unless lists are passed in.

Violations are reported in that group order, alphabetically within a group.
"""
from __future__ import annotations

import functools
import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .findings import Finding, make
from .rulesdb import RuleCatalog, default_catalog, load_data, thresholds

VIOLATION_RULES = {
    "heading_changed": "FID001", "link_removed": "FID002", "link_added": "FID003", "number_removed": "FID004",
    "number_added": "FID005", "table_rows_decreased": "FID006", "code_block_changed": "FID007",
    "too_short": "FID008", "too_long": "FID008", "superlative_added": "FID009", "caveat_removed": "FID010",
}
_DEFAULTS = {"min_ratio": 0.8, "max_ratio": 1.6, "min_words": 20}

_LINE = re.compile(r"[^\r\n]*(?:\r\n|\n|\r)|[^\r\n]+\Z")
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
_FENCE_CLOSE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*$")
_PRE = re.compile(r"<pre\b[^>]*>.*?</pre\s*>", re.I | re.S)
_ATX = re.compile(r"^#{1,6}[ \t]+\S")
_HTML_HEADING = re.compile(r"<h[1-6]\b[^>]*>.*?</h[1-6]\s*>", re.I | re.S)
_MD_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))")
_AUTOLINK = re.compile(r"<(https?://[^>\s]+)>", re.I)
_BARE = re.compile(r"https?://[^\s)>\]\"'<]+", re.I)
_HREF = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+))""", re.I)
_REF_DEF = re.compile(r"^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*(?:<([^>\n]+)>|(\S+))", re.M)
_TAG = re.compile(r"<[^>\n]*>")
_NUM = re.compile(r"(?<![\w.])[$\u20ac\u00a3]?\d[\d,]*(?:\.\d+)?%?")
_WORD = re.compile(r"\w+")


@functools.lru_cache(maxsize=1)
def _lexicon_lists() -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
    lex = load_data("content-lexicons")["lexicons"]
    hype = lex["hype_superlatives"]
    return tuple(hype["items"]), tuple(hype.get("exceptions", ())), tuple(lex["caveats"]["items"])


def _limits() -> Dict[str, float]:
    block = thresholds().get("fidelity") or {}
    return {k: float(block.get(k, v)) for k, v in _DEFAULTS.items()}


def split_code(text: str) -> Tuple[List[str], str]:
    """(fenced and ``<pre>`` code blocks in order, text with each block replaced by a newline)."""
    blocks: List[str] = []
    kept: List[str] = []
    current: List[str] = []
    marker = ""
    for line in _LINE.findall(text):
        if marker:
            current.append(line)
            close = _FENCE_CLOSE.match(line.rstrip("\r\n"))
            if close and close.group(1)[0] == marker[0] and len(close.group(1)) >= len(marker):
                blocks.append("".join(current))
                current, marker = [], ""
            continue
        match = _FENCE.match(line)
        if match:
            marker, current = match.group(1), [line]
            kept.append("\n")
            continue
        kept.append(line)
    if current:
        blocks.append("".join(current))
    rest = "".join(kept)
    pres = _PRE.findall(rest)
    return blocks + pres, _PRE.sub("\n", rest)


def _url_spans(text: str) -> List[Tuple[int, int, str]]:
    """(start, end, target) of every link target in prose (call on text without code)."""
    spans: List[Tuple[int, int, str]] = []
    for rx in (_MD_LINK, _REF_DEF, _HREF):
        for m in rx.finditer(text):
            g = next(i for i in range(1, (rx.groups or 0) + 1) if m.group(i) is not None)
            spans.append((m.start(g), m.end(g), m.group(g).strip()))
    spans.extend((m.start(1), m.end(1), m.group(1)) for m in _AUTOLINK.finditer(text))
    for m in _BARE.finditer(text):
        url = m.group(0).rstrip(".,;:")
        spans.append((m.start(), m.start() + len(url), url))
    return sorted(spans)


def _mask_urls(text: str) -> str:
    """`text` with every link target replaced by spaces (one pass, same length)."""
    out: List[str] = []
    pos = 0
    for start, end, _ in _url_spans(text):
        if end > pos:
            start = max(start, pos)
            out.append(text[pos:start])
            out.append(" " * (end - start))
            pos = end
    out.append(text[pos:])
    return "".join(out)


def extract_links(text: str) -> Set[str]:
    """Link targets in prose (call on text without code)."""
    return {url for _, _, url in _url_spans(text) if url}


def extract_numbers(text: str) -> Set[str]:
    """Normalized numbers in prose after masking link targets and removing HTML tags."""
    text = _TAG.sub(" ", _mask_urls(text))
    out = set()
    for m in _NUM.finditer(text):
        value = re.sub(r"[$\u20ac\u00a3,]", "", m.group(0))
        if value and value[0].isdigit():
            out.add(value)
    return out


def headings(text: str) -> List[str]:
    """Heading lines (stripped) in order; call on text without code."""
    found: List[Tuple[int, str]] = []
    pos = 0
    for line in _LINE.findall(text):
        if _ATX.match(line):
            found.append((pos, line.strip()))
        pos += len(line)
    found.extend((m.start(), re.sub(r"\s+", " ", m.group(0)).strip()) for m in _HTML_HEADING.finditer(text))
    return [h for _, h in sorted(found)]


def table_rows(text: str) -> int:
    """Markdown table lines plus HTML ``<tr>`` tags (call on text without code)."""
    md = sum(1 for line in _LINE.findall(text) if line.strip().startswith("|"))
    return md + len(re.findall(r"<tr\b", text, re.I))


def _phrase_re(phrases: Sequence[str]) -> Optional["re.Pattern[str]"]:
    items = sorted({p.strip().lower() for p in phrases if p and p.strip()}, key=lambda p: (-len(p), p))
    if not items:
        return None
    body = "|".join(r"\s+".join(re.escape(w) for w in p.split()) for p in items)
    return re.compile(r"(?<!\w)(?:%s)(?!\w)" % body, re.I)


def phrases_present(text: str, phrases: Sequence[str], exceptions: Sequence[str] = ()) -> Set[str]:
    """Phrases from `phrases` found in `text` (lowercased), ignoring hits inside `exceptions`."""
    pattern = _phrase_re(phrases)
    if pattern is None:
        return set()
    masked = text
    exc = _phrase_re(exceptions)
    if exc is not None:
        masked = exc.sub(lambda m: " " * len(m.group(0)), text)
    return {" ".join(m.group(0).lower().split()) for m in pattern.finditer(masked)}


def _prose(text: str) -> Tuple[List[str], str, Set[str], str]:
    code, rest = split_code(text)
    return code, rest, extract_links(rest), _mask_urls(rest)


def check_fidelity(original: str, rewrite: str, *, min_ratio: Optional[float] = None,
                   max_ratio: Optional[float] = None, min_words: Optional[int] = None,
                   superlatives: Optional[Sequence[str]] = None,
                   caveats: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """Compare a rewrite with its original; returns {"passed", "violations", "stats"}.

    Limits default to data/thresholds.json ``fidelity``; superlatives and caveats default to
    data/content-lexicons.json (hype exceptions such as "best practice" are always ignored).
    """
    limits = _limits()
    lo = limits["min_ratio"] if min_ratio is None else float(min_ratio)
    hi = limits["max_ratio"] if max_ratio is None else float(max_ratio)
    floor = int(limits["min_words"] if min_words is None else min_words)
    default_hype, exceptions, default_caveats = _lexicon_lists()
    hype = default_hype if superlatives is None else tuple(superlatives)
    hedges = default_caveats if caveats is None else tuple(caveats)

    code_a, rest_a, links_a, plain_a = _prose(original)
    code_b, rest_b, links_b, plain_b = _prose(rewrite)
    nums_a, nums_b = extract_numbers(rest_a), extract_numbers(rest_b)
    heads_a, heads_b = headings(rest_a), headings(rest_b)
    rows_a, rows_b = table_rows(rest_a), table_rows(rest_b)
    words_a, words_b = len(_WORD.findall(original)), len(_WORD.findall(rewrite))

    sup_a, sup_b = phrases_present(plain_a, hype, exceptions), phrases_present(plain_b, hype, exceptions)
    cav_a, cav_b = phrases_present(plain_a, hedges), phrases_present(plain_b, hedges)

    violations: List[str] = []
    if heads_a and heads_a != heads_b:
        violations.append("heading_changed")
    violations += ["link_removed:" + u for u in sorted(links_a - links_b)]
    violations += ["link_added:" + u for u in sorted(links_b - links_a)]
    violations += ["number_removed:" + n for n in sorted(nums_a - nums_b)]
    violations += ["number_added:" + n for n in sorted(nums_b - nums_a)]
    if rows_b < rows_a:
        violations.append("table_rows_decreased")
    if code_a != code_b:
        violations.append("code_block_changed")
    ratio = (words_b / words_a) if words_a else None
    checked = words_a >= floor
    if checked and ratio is not None:
        if ratio < lo:
            violations.append("too_short")
        elif ratio > hi:
            violations.append("too_long")
    violations += ["superlative_added:" + w for w in sorted(sup_b - sup_a)]
    violations += ["caveat_removed:" + p for p in sorted(cav_a - cav_b)]
    stats = {
        "original_words": words_a, "rewrite_words": words_b,
        "ratio": None if ratio is None else round(ratio, 3), "ratio_checked": checked,
        "min_ratio": lo, "max_ratio": hi, "min_words": floor,
        "headings": {"original": len(heads_a), "rewrite": len(heads_b)},
        "links": {"original": len(links_a), "rewrite": len(links_b)},
        "numbers": {"original": len(nums_a), "rewrite": len(nums_b)},
        "table_rows": {"original": rows_a, "rewrite": rows_b},
        "code_blocks": {"original": len(code_a), "rewrite": len(code_b)},
    }
    return {"passed": not violations, "violations": violations, "stats": stats}


def rule_for(violation: str) -> str:
    """FID rule id for a violation code such as ``link_removed:https://...``; KeyError if unknown."""
    return VIOLATION_RULES[violation.split(":", 1)[0]]


def fidelity_findings(result: Dict[str, Any], *, file: Optional[str] = None, url: Optional[str] = None,
                      catalog: Optional[RuleCatalog] = None) -> List[Finding]:
    """One FID finding per violation in a check_fidelity result (empty when it passed)."""
    cat = catalog or default_catalog()
    out: List[Finding] = []
    for violation in result.get("violations", []):
        code, _, value = violation.partition(":")
        evidence: Dict[str, Any] = {"violation": violation}
        if code in ("too_short", "too_long"):
            stats = result.get("stats", {})
            evidence.update(ratio=stats.get("ratio"), allowed=[stats.get("min_ratio"), stats.get("max_ratio")])
        message = "Rewrite violates fidelity: %s." % (code.replace("_", " ") + (" " + value if value else ""))
        out.append(make(rule_for(violation), message, catalog=cat, file=file, url=url, evidence=evidence,
                        key=violation))
    return out
