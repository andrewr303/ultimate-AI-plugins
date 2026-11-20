"""Content and GEO text checks (WP05): citability heuristics, claims, lexicon lint, invisible
characters, stale years, templated metadata and near-duplicate pages.

Rules: CONT001-005, CONT007-010, CITE001-003 (per page, `check_text`) and PSEO001, META006 (site
level, `check_site_text`). Every check is a deterministic heuristic over local text; phrase lists
and content thresholds live in data/content-lexicons.json, PSEO limits in data/thresholds.json.
Style hits (filler, hype, dangling openers) are style signals, never AI detection.

Adapted ideas (MIT): passage scorer parts, caps, grades and block extraction from geo-seo-claude
``scripts/citability_scorer.py`` (year range now derived from the current year; mean of all
passages and of the top five); claim kinds, the +/-200 character citation window, the invisible
and bidi character classes and the templated-metadata gates from claude-seo ``content_verify.py``,
``content_humanize.py`` and ``metadata_template.py``; dangling-opener and unsourced-number ideas
from geoptimize. Phrase lists are our own.

`content.py` imports no sibling module except findings and rulesdb, so the Markdown heading and
fence rules of `sections.py` are repeated here (tests assert both agree).
"""
from __future__ import annotations

import bisect
import functools
import hashlib
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .findings import Finding, make
from .rulesdb import RuleCatalog, default_catalog, load_data, thresholds

# ----------------------------------------------------------------------------- lexicons

_CJK_CLASS = "\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff"
_CJK = re.compile("[%s]" % _CJK_CLASS)
_WORDS = re.compile(r"[^\W_%s]+(?:['\u2019][^\W_%s]+)*" % (_CJK_CLASS, _CJK_CLASS))
_SENT_SPLIT = re.compile(r"(?<=[.!?\u3002\uff01\uff1f])\s+|\n+")


@functools.lru_cache(maxsize=1)
def _lexdoc() -> Dict[str, Any]:
    doc = load_data("content-lexicons")
    if not isinstance(doc, dict) or not isinstance(doc.get("lexicons"), dict):
        raise ValueError("data/content-lexicons.json must contain a 'lexicons' object")
    return doc


def lexicon(name: str) -> Dict[str, Any]:
    """One lexicon entry from data/content-lexicons.json; KeyError when unknown."""
    lex = _lexdoc()["lexicons"]
    if name not in lex:
        raise KeyError("unknown lexicon: %s" % name)
    return lex[name]


def _thr(*path: str) -> Any:
    node: Any = _lexdoc().get("thresholds", {})
    for part in path:
        node = node[part]
    return node


def _phrase(item: str) -> str:
    words = item.strip().split()
    return r"\s+".join(re.escape(w).replace("'", "['\u2019]") for w in words)


def _alternation(items: Iterable[str]) -> str:
    uniq = sorted({i.strip().lower() for i in items if i and i.strip()}, key=lambda s: (-len(s), s))
    return "|".join(_phrase(i) for i in uniq) or r"(?!x)x"


def _norm_phrase(text: str) -> str:
    return " ".join(text.lower().replace("\u2019", "'").split())


class _Matcher:
    """Compiled items, patterns and exceptions of one lexicon."""

    def __init__(self, entry: Dict[str, Any]) -> None:
        items = [str(i) for i in entry.get("items", [])]
        self.names = {_norm_phrase(i): i for i in items}
        self.item_re = re.compile(r"(?<!\w)(?:%s)(?!\w)" % _alternation(items), re.I) if items else None
        self.patterns = [(p["name"], re.compile(p["regex"], re.M | (0 if p.get("case_sensitive") else re.I)),
                          bool(p.get("html_only"))) for p in entry.get("patterns", [])]
        exc = entry.get("exceptions") or []
        self.exc_re = re.compile(r"(?<!\w)(?:%s)(?!\w)" % _alternation(exc), re.I) if exc else None

    def hits(self, text: str, html: bool = False) -> List[Dict[str, Any]]:
        spans: List[Tuple[int, int, str]] = []
        if self.item_re is not None:
            for m in self.item_re.finditer(text):
                spans.append((m.start(), m.end(), self.names.get(_norm_phrase(m.group(0)), m.group(0).lower())))
        for name, rx, html_only in self.patterns:
            if html_only and not html:
                continue
            spans.extend((m.start(), m.end(), name) for m in rx.finditer(text) if m.end() > m.start())
        exc = [m.span() for m in self.exc_re.finditer(text)] if self.exc_re is not None else []
        exc_starts = [a for a, _ in exc]
        out: List[Dict[str, Any]] = []
        last = -1
        for start, end, term in sorted(spans, key=lambda s: (s[0], s[0] - s[1], s[2])):
            j = bisect.bisect_right(exc_starts, start) - 1
            if start < last or (j >= 0 and end <= exc[j][1]):
                continue
            out.append({"term": term, "match": text[start:end], "pos": start, "end": end})
            last = end
        return out


@functools.lru_cache(maxsize=None)
def _matcher(name: str) -> _Matcher:
    return _Matcher(lexicon(name))


def lexicon_hits(text: str, lexicon: str, *, html: bool = False) -> List[Dict[str, Any]]:
    """Non-overlapping hits {term, match, pos, end} of a named lexicon, in text order.

    `html=True` also applies patterns marked ``html_only`` (e.g. Markdown fences left in HTML).
    """
    return _matcher(lexicon).hits(text, html)


def count_words(text: str) -> int:
    """Words; each CJK character counts as one word."""
    return len(_CJK.findall(text)) + len(_WORDS.findall(text))


def sentences(text: str) -> List[str]:
    """Rough sentence split on terminal punctuation and line breaks."""
    return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]


def _first_word(text: str) -> str:
    m = re.search(r"[A-Za-z]+", text)
    return m.group(0).lower() if m else ""


@functools.lru_cache(maxsize=1)
def _sets() -> Dict[str, Set[str]]:
    return {name: {_norm_phrase(i) for i in lexicon(name)["items"]}
            for name in ("dangling_openers", "stop_words_en", "stock_cta")}


def _dangling(text: str) -> bool:
    return _first_word(text) in _sets()["dangling_openers"]


def _visible(text: str) -> str:
    """Evidence-safe text: invisible, bidi and control characters shown as <U+XXXX>, whitespace collapsed."""
    out = _INVISIBLE.sub(lambda m: "<U+%04X>" % ord(m.group(0)), " ".join(text.split()))
    return re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", lambda m: "<U+%04X>" % ord(m.group(0)), out)


def _snippet(text: str, start: int, end: int, pad: int = 60) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    return _visible(text[a:b])[:200]


# ----------------------------------------------------------------------------- document model

@dataclass
class _Doc:
    kind: str
    prose: str                                         # main content; positions map via prose_line
    prose_lines: Tuple[List[int], List[int]]
    links: List[Tuple[int, int, str]] = field(default_factory=list)
    blocks: List[Tuple[str, str]] = field(default_factory=list)
    paragraphs: List[Tuple[int, str]] = field(default_factory=list)
    scan: str = ""                                     # all published text (CONT004/CONT010)
    scan_lines: Tuple[List[int], List[int]] = field(default_factory=lambda: ([], []))
    hidden: List[Tuple[int, int, str]] = field(default_factory=list)
    comments: List[Tuple[int, int]] = field(default_factory=list)
    raw: List[Tuple[str, int]] = field(default_factory=list)       # (text, first line) for CONT003
    meta: List[Tuple[str, int]] = field(default_factory=list)      # title/description/frontmatter
    orphans: List[Tuple[str, Optional[int]]] = field(default_factory=list)


def _line_of(table: Tuple[List[int], List[int]], pos: int) -> Optional[int]:
    offsets, lines = table
    if not offsets:
        return None
    i = bisect.bisect_right(offsets, pos) - 1
    return lines[max(i, 0)]


def _newline_table(text: str, first_line: int = 1) -> Tuple[List[int], List[int]]:
    offsets, lines = [0], [first_line]
    for m in re.finditer(r"\r\n|\n|\r", text):
        offsets.append(m.end())
        lines.append(lines[-1] + 1)
    return offsets, lines


class _Stream:
    """Text builder that remembers the source line of every emitted chunk."""

    def __init__(self) -> None:
        self.parts: List[str] = []
        self.size = 0
        self.last = "\n"
        self.offsets: List[int] = []
        self.lines: List[int] = []

    def emit(self, text: str, line: int) -> Tuple[int, int]:
        if self.last == "\n":
            text = text.lstrip(" ")
        if not text:
            return self.size, self.size
        start = self.size
        self.offsets.append(start)
        self.lines.append(line)
        self.parts.append(text)
        self.size += len(text)
        self.last = text[-1]
        return start, self.size

    def newline(self) -> None:
        if self.last != "\n":
            self.parts.append("\n")
            self.size += 1
            self.last = "\n"

    def text(self) -> str:
        return "".join(self.parts)


_VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())
_SKIP = frozenset("nav header footer aside form noscript svg iframe object select button canvas math dialog".split())
_DROP = frozenset(("script", "style"))
_CODE = frozenset(("code", "pre", "kbd", "samp"))
_BLOCK = frozenset(("address article blockquote caption dd details div dl dt fieldset figcaption figure h5 h6 legend "
                    "li main ol p pre section summary table tbody td tfoot th thead tr ul").split())
_HEADINGS = frozenset(("h1", "h2", "h3", "h4"))
_AUTO_CLOSE = frozenset(("p", "li", "dt", "dd", "tr", "td", "th", "option"))
_MAX_DEPTH = 2048
_HIDDEN_STYLE = re.compile(
    r"display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0(?:\.0+)?(?:px|em|rem|pt|%)?\s*(?:!important)?\s*(?:;|$)"
    r"|opacity\s*:\s*0(?:\.0+)?\s*(?:!important)?\s*(?:;|$)|(?:left|top|text-indent|margin-left)\s*:\s*-\d{3,}"
    r"|clip\s*:\s*rect\(\s*0", re.I)
_ASCII_WS = re.compile(r"[ \t\n\r\f\v]+")


def _hidden_reason(tag: str, attrs: Dict[str, str]) -> str:
    if "hidden" in attrs:
        return "hidden attribute"
    if attrs.get("aria-hidden", "").strip().lower() == "true":
        return "aria-hidden"
    if tag == "template":
        return "template"
    if _HIDDEN_STYLE.search(attrs.get("style", "")):
        return "inline style"
    return ""


class _PageText(HTMLParser):
    """Two text streams from HTML: main prose (no chrome, hidden or code) and all published text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.prose = _Stream()
        self.all = _Stream()
        self.stack: List[Tuple[str, bool, str, bool, bool]] = []   # tag, skip, hidden, code, drop
        self.heads: List[Tuple[str, int, int]] = []                 # heading, line start, body start
        self.heading: Optional[Tuple[str, int, List[str]]] = None
        self.anchor: Optional[Tuple[int, str, int]] = None
        self.links: List[Tuple[int, int, str]] = []
        self.fragments: List[Tuple[str, int, int, int]] = []        # fragment, start, end, line
        self.ids: Set[str] = set()
        self.raw: List[Tuple[str, int]] = []
        self.meta: List[Tuple[str, int]] = []
        self.hidden: List[Tuple[int, int, str]] = []
        self.comments: List[Tuple[int, int]] = []
        self.in_title = False
        self.open: Counter = Counter()

    def _flags(self) -> Tuple[bool, str, bool, bool]:
        return self.stack[-1][1:] if self.stack else (False, "", False, False)

    def _break(self) -> None:
        self.prose.newline()
        self.all.newline()

    def _published(self, text: str, line: int) -> None:
        self.all.newline()
        self.all.emit(_ASCII_WS.sub(" ", text), line)
        self.all.newline()
        self.raw.append((text, line))
        self.meta.append((text, line))

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        line = self.getpos()[0]
        for key in ("id",) + (("name",) if tag == "a" else ()):
            if a.get(key, "").strip():
                self.ids.add(a[key].strip())
        if tag == "meta":
            if a.get("name", "").lower() == "description" and a.get("content", "").strip():
                self._published(a["content"], line)
            return
        if tag == "title" and not any(e[0] == "svg" for e in self.stack):
            self.in_title = True
            return
        if tag in _VOID:
            if tag in ("br", "hr"):
                self._break()
            return
        if tag in _AUTO_CLOSE:
            near = [i for i in range(len(self.stack) - 1, max(-1, len(self.stack) - 5), -1) if self.stack[i][0] == tag]
            if near:
                self._pop_to(near[0])
        skip, hidden, code, drop = self._flags()
        entry = (tag, skip or tag in _SKIP, hidden or _hidden_reason(tag, a), code or tag in _CODE,
                 drop or tag in _DROP)
        if len(self.stack) < _MAX_DEPTH:
            self.stack.append(entry)
            self.open[tag] += 1
        if tag in _BLOCK or tag in _HEADINGS:
            self._break()
        if not self._captures(entry):
            return
        if tag in _HEADINGS and self.heading is None:
            self.heading = (tag, self.prose.size, [])
        elif tag == "li":
            self.prose.emit("- ", line)
        elif tag == "a" and a.get("href", "").strip():
            self._close_anchor()
            self.anchor = (self.prose.size, a["href"].strip(), line)

    @staticmethod
    def _captures(entry: Tuple[str, bool, str, bool, bool]) -> bool:
        return not (entry[1] or entry[2] or entry[3] or entry[4])

    def _close_anchor(self) -> None:
        if self.anchor is None:
            return
        start, href, line = self.anchor
        self.anchor = None
        self.links.append((start, self.prose.size, href))
        if href.startswith("#"):
            self.fragments.append((href[1:], start, self.prose.size, line))

    def _end_heading(self) -> None:
        if self.heading is None:
            return
        _, start, buf = self.heading
        self.heading = None
        text = " ".join("".join(buf).split())
        self.prose.newline()
        if text:
            self.heads.append((text, start, self.prose.size))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
            return
        if not self.open[tag]:
            return
        self._pop_to(next(i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag))

    def _pop_to(self, idx: int) -> None:
        popped = self.stack[idx:]
        del self.stack[idx:]
        for entry in reversed(popped):
            self.open[entry[0]] -= 1
            name = entry[0]
            if name in _HEADINGS and self.heading is not None and self.heading[0] == name:
                self._end_heading()
            elif name == "a":
                self._close_anchor()
            if name in _BLOCK:
                self._break()

    def handle_data(self, data: str) -> None:
        line = self.getpos()[0]
        if self.in_title:
            if data.strip():
                self._published(data, line)
            return
        skip, hidden, code, drop = self._flags()
        if drop:
            return
        self.raw.append((data, line))
        text = _ASCII_WS.sub(" ", data)
        if not code:
            start, end = self.all.emit(text, line)
            if hidden and end > start:
                self.hidden.append((start, end, hidden))
        if not (skip or hidden or code):
            self.prose.emit(text, line)
            if self.heading is not None:
                self.heading[2].append(text)

    def handle_comment(self, data: str) -> None:
        line = self.getpos()[0]
        self.all.newline()
        start, end = self.all.emit(_ASCII_WS.sub(" ", data), line)
        self.all.newline()
        if end > start:
            self.hidden.append((start, end, "html comment"))
            self.comments.append((start, end))

    def close(self) -> None:
        super().close()
        self._end_heading()
        self._close_anchor()


def _parse_html(html: str) -> _PageText:
    page = _PageText()
    try:
        page.feed(html)
        page.close()
    except (AssertionError, ValueError):  # malformed markup: keep what was parsed
        pass
    return page


def _html_blocks(prose: str, heads: Sequence[Tuple[str, int, int]]) -> List[Tuple[str, str, int]]:
    bounds = [("", 0, 0)] + list(heads)
    out: List[Tuple[str, str, int]] = []
    for i, (heading, _, body_start) in enumerate(bounds):
        end = bounds[i + 1][1] if i + 1 < len(bounds) else len(prose)
        body = "\n".join(" ".join(x.split()) for x in prose[body_start:end].splitlines() if x.strip())
        if i == 0 and not body:
            continue
        out.append((heading, body, body_start))
    return out


def blocks_from_html(html: str) -> List[Tuple[str, str]]:
    """(heading, text) blocks of the main content.

    Skips script, style, nav, header, footer, aside, form (and similar chrome), hidden elements
    and code; h1-h4 start a new block; paragraphs and list items become lines ("- " for items).
    """
    page = _parse_html(html)
    return [(h, t) for h, t, _ in _html_blocks(page.prose.text(), page.heads)]


def _build_html(html: str) -> _Doc:
    page = _parse_html(html)
    prose = page.prose.text()
    heading_starts = {start for _, start, _ in page.heads}
    paragraphs = []
    pos = 0
    for line in prose.split("\n"):
        if line.strip() and pos not in heading_starts:
            paragraphs.append((pos, line))
        pos += len(line) + 1
    doc = _Doc(kind="html", prose=prose, prose_lines=(page.prose.offsets, page.prose.lines), links=page.links,
               blocks=[(h, t) for h, t, _ in _html_blocks(prose, page.heads)], paragraphs=paragraphs,
               scan=page.all.text(), scan_lines=(page.all.offsets, page.all.lines), hidden=page.hidden,
               comments=page.comments, raw=page.raw, meta=page.meta)
    doc.orphans = _html_orphans(page, prose, doc)
    return doc


# ----------------------------------------------------------------------------- Markdown

_MD_LINE = re.compile(r"[^\r\n]*(?:\r\n|\n|\r)|[^\r\n]+\Z")
_MD_HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_MD_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
_MD_FENCE_CLOSE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*$")
_FRONTMATTER = re.compile(r"\A(\ufeff?(---|\+\+\+)[ \t]*(?:\r\n|\n|\r)(?:.*?(?:\r\n|\n|\r))??\2[ \t]*(?:\r\n|\n|\r|\Z))",
                          re.S)
_MD_LINK = re.compile(r"!?\[([^\]\n]*)\]\(([^)\n]*)\)")
_AUTOLINK = re.compile(r"<(?:https?://|mailto:)[^>\s]+>", re.I)
_BARE_URL = re.compile(r"(?<![(<\w])https?://[^\s)>\]\"'<]+", re.I)
_HTML_LINK = re.compile(r"<a\b[^>]*\bhref\s*=\s*[\"']?[^\"'\s>]+[^>]*>.{0,2000}?</a\s*>", re.I | re.S)
_INLINE_CODE = re.compile(r"(`+)(?!`)[^\n]*?(?<!`)\1(?!`)")
_COMMENT = re.compile(r"<!--.*?(?:-->|\Z)", re.S)
_TAG = re.compile(r"</?[A-Za-z][^>\n]*>")
_REF_DEF_LINE = re.compile(r"^[ \t]{0,3}\[[^\]\n]+\]:[^\n]*$", re.M)
_MDX_LINE = re.compile(r"^(?:import|export)\s[^\n]*$", re.M)
_HTML_OPEN = re.compile(r"<([A-Za-z][\w-]*)\b([^>\n]*)>")
_ATTR = re.compile(r"""([\w:-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+)))?""")


def _blank(text: str) -> str:
    return re.sub(r"[^\r\n]", " ", text)


def _md_scan(body: str) -> List[Tuple[int, str, bool, int, str]]:
    """(offset, line, in_code, heading level, heading text) per line, sections.py rules."""
    out = []
    pos = 0
    marker = ""
    for line in _MD_LINE.findall(body):
        bare = line.rstrip("\r\n")
        level, text, code = 0, "", True
        if marker:
            close = _MD_FENCE_CLOSE.match(bare)
            if close and close.group(1)[0] == marker[0] and len(close.group(1)) >= len(marker):
                marker = ""
        else:
            fence = _MD_FENCE.match(line)
            if fence:
                marker = fence.group(1)
            else:
                code = False
                m = _MD_HEADING.match(bare)
                if m and m.group(2).strip():
                    level, text = len(m.group(1)), m.group(2).strip()
        out.append((pos, line, code, level, text))
        pos += len(line)
    return out


def _sub_blank(pattern: "re.Pattern[str]", text: str) -> str:
    return pattern.sub(lambda m: _blank(m.group(0)), text)


def _md_plain(text: str) -> str:
    """Markdown section body to plain lines (code removed, links unwrapped, markers dropped)."""
    keep = [line for _, line, code, _, _ in _md_scan(text) if not code]
    out = []
    for line in "".join(keep).splitlines():
        line = _COMMENT.sub(" ", line)
        if _REF_DEF_LINE.match(line) or _MDX_LINE.match(line) or re.match(r"^\s*(?:\|?\s*:?-{3,}|={3,}\s*$)", line):
            continue
        line = _MD_LINK.sub(lambda m: m.group(1), line)
        line = re.sub(r"\[([^\]\n]+)\]\[[^\]\n]*\]", r"\1", line)
        line = _TAG.sub(" ", line).replace("`", "")
        line = re.sub(r"(\*\*|__|\*|_)(?=\S)(.+?)(?<=\S)\1", r"\2", line)
        line = re.sub(r"^\s{0,3}>\s?", "", line)
        line = re.sub(r"^\s*[*+]\s+", "- ", line).replace("|", " ")
        line = " ".join(line.split())
        if line:
            out.append(line)
    return "\n".join(out)


def _md_sections(body: str) -> List[Tuple[str, int, str]]:
    """(heading, start offset, section text) using the sections.py splitting rules."""
    out: List[Tuple[str, int, str]] = []
    start, heading = 0, ""
    for pos, _, code, level, text in _md_scan(body):
        if level and not code:
            if pos > start:
                out.append((heading, start, body[start:pos]))
            start, heading = pos, text
    if len(body) > start:
        out.append((heading, start, body[start:]))
    return out


def _split_frontmatter(text: str) -> Tuple[str, str]:
    m = _FRONTMATTER.match(text)
    return (m.group(1), text[m.end(1):]) if m else ("", text)


def blocks_from_markdown(md: str) -> List[Tuple[str, str]]:
    """(heading, plain text) per section after the frontmatter (preamble heading is "")."""
    return _md_blocks(_split_frontmatter(md)[1])


def _md_blocks(body: str) -> List[Tuple[str, str]]:
    out = []
    for heading, _, text in _md_sections(body):
        if heading:
            text = text.split("\n", 1)[1] if "\n" in text else ""
        plain = _md_plain(text)
        if heading or plain:
            out.append((heading, plain))
    return out


def _md_hidden(text: str) -> List[Tuple[int, int, str]]:
    """Ranges of inline HTML elements hidden by attribute or inline style, and HTML comments."""
    out = [(m.start(), m.end(), "html comment") for m in _COMMENT.finditer(text)]
    for m in _HTML_OPEN.finditer(text):
        attrs = {k.lower(): (v1 or v2 or v3 or "") for k, v1, v2, v3 in _ATTR.findall(m.group(2))}
        reason = _hidden_reason(m.group(1).lower(), attrs)
        if reason:
            limit = min(len(text), m.end() + _HIDDEN_WINDOW)
            close = _close_tag(m.group(1).lower()).search(text, m.end(), limit)
            out.append((m.start(), close.end() if close else limit, reason))
    return sorted(out)


_HIDDEN_WINDOW = 20000


@functools.lru_cache(maxsize=256)
def _close_tag(tag: str) -> "re.Pattern[str]":
    return re.compile(r"</%s\s*>" % re.escape(tag), re.I)


class _Spans:
    """Intervals answering "does [start, end) overlap any of them?" in O(log n)."""

    def __init__(self, spans: Iterable[Sequence[Any]]) -> None:
        items = sorted((int(s[0]), int(s[1])) for s in spans if s[1] > s[0])
        self.starts = [a for a, _ in items]
        self.maxend: List[int] = []
        best = -1
        for _, b in items:
            best = max(best, b)
            self.maxend.append(best)

    def overlaps(self, start: int, end: int) -> bool:
        i = bisect.bisect_left(self.starts, end)
        return i > 0 and self.maxend[i - 1] > start


def _link_spans(text: str) -> List[Tuple[int, int, str]]:
    spans = [(m.start(), m.end(), m.group(2).strip()) for m in _MD_LINK.finditer(text)]
    spans += [(m.start(), m.end(), m.group(0)[1:-1]) for m in _AUTOLINK.finditer(text)]
    spans += [(m.start(), m.end(), m.group(0)) for m in _HTML_LINK.finditer(text)]
    spans += [(m.start(), m.end(), m.group(0).rstrip(".,;:")) for m in _BARE_URL.finditer(text)]
    return sorted(spans)


def _mask_code(text: str) -> str:
    parts = [(_blank(line) if code else line) for _, line, code, _, _ in _md_scan(text)]
    return _sub_blank(_INLINE_CODE, "".join(parts))


def _build_markdown(text: str, frontmatter: bool = True) -> _Doc:
    raw_fm, body = _split_frontmatter(text) if frontmatter else ("", text)
    offset = len(raw_fm)
    scan_body = _mask_code(body)
    links = [(a + offset, b + offset, h) for a, b, h in _link_spans(scan_body)]
    prose_body = scan_body
    for pattern in (_COMMENT, _REF_DEF_LINE, _MDX_LINE, _AUTOLINK, _BARE_URL, _TAG):
        prose_body = _sub_blank(pattern, prose_body)
    prose_body = _MD_LINK.sub(lambda m: _blank(m.group(0)[:m.start(1) - m.start()]) + m.group(1)
                              + _blank(m.group(0)[m.end(1) - m.start():]), prose_body)
    prose = _blank(raw_fm) + prose_body
    table = _newline_table(text)
    paragraphs: List[Tuple[int, str]] = []
    current: List[str] = []
    start = 0
    pos = 0
    for line in _MD_LINE.findall(prose):
        bare = line.strip()
        structural = (not bare or bare.startswith(("#", "|", ">", "<")) or re.match(r"^(?:[-*+]|\d+[.)])\s", bare))
        if structural:
            if current:
                paragraphs.append((start, " ".join(current)))
            current = []
        elif bare:
            if not current:
                start = pos + len(line) - len(line.lstrip())
            current.append(bare)
        pos += len(line)
    if current:
        paragraphs.append((start, " ".join(current)))
    hidden = [(a + offset, b + offset, r) for a, b, r in _md_hidden(scan_body)]
    doc = _Doc(kind="markdown", prose=prose, prose_lines=table, links=links, blocks=_md_blocks(body),
               paragraphs=paragraphs, scan=raw_fm + scan_body, scan_lines=table, hidden=hidden,
               comments=[(a, b) for a, b, r in hidden if r == "html comment"], raw=[(text, 1)],
               meta=[(raw_fm, 1)] if raw_fm else [])
    doc.orphans = _md_orphans(_blank(raw_fm) + scan_body, doc)
    return doc


# ----------------------------------------------------------------------------- citation markers

_FOOTNOTE_MARK = re.compile(r"\[\^[\w-]{1,20}\]|\[\d{1,3}(?:\s?[,\u2013-]\s?\d{1,3})*\]")
_PAREN_CITE = re.compile(r"\([A-Z][\w&.'\u2019-]*(?:\s+(?:et\s+al\.|&|and|[A-Z][\w&.'\u2019-]*)){0,4},?\s+(?:19|20)\d\d[a-z]?\)")


@functools.lru_cache(maxsize=1)
def _cite_re() -> "re.Pattern[str]":
    """Attribution phrase (any case) followed by a named source: capital, digit, quote or domain."""
    return re.compile(r"(?<!\w)(?i:%s)\s+(?:(?i:the|an?)\s+)?[\"\u201c(]?(?:[A-Z0-9]|(?i:https?:|www\.)|"
                      r"[a-z0-9-]+\.[a-z]{2,}\b)" % _alternation(lexicon("citation_markers")["items"]))


def _cited_near(text: str, links: "_Spans", start: int, end: int, window: int) -> bool:
    lo, hi = max(0, start - window), min(len(text), end + window)
    if links.overlaps(lo, hi):
        return True
    seg = text[lo:hi]
    return bool(_FOOTNOTE_MARK.search(seg) or _PAREN_CITE.search(seg) or _cite_re().search(seg))


def _reference_section_items(blocks: Sequence[Tuple[str, str]]) -> int:
    names = {_norm_phrase(i) for i in lexicon("reference_headings")["items"]}
    count = 0
    for heading, text in blocks:
        if _norm_phrase(heading).rstrip(":") in names:
            count += len(re.findall(r"^(?:-|\d+[.)])\s", text, re.M))
    return count


def _has_reference_heading(blocks: Sequence[Tuple[str, str]]) -> bool:
    names = {_norm_phrase(i) for i in lexicon("reference_headings")["items"]}
    return any(_norm_phrase(h).rstrip(":") in names for h, _ in blocks)


def _md_orphans(scan: str, doc: _Doc) -> List[Tuple[str, Optional[int]]]:
    defs = {m.group(1).lower() for m in re.finditer(r"^[ \t]{0,3}\[(\^?[^\]\s]+)\]:", scan, re.M)}
    entries = {m.group(1) for m in re.finditer(r"^[ \t]*(?:[-*+][ \t]+)?\[(\d{1,3})\][ \t]+\S", scan, re.M)}
    listed = _reference_section_items(doc.blocks)
    out: List[Tuple[str, Optional[int]]] = []
    for m in re.finditer(r"\[\^([^\]\s]+)\](?!:)|(?<![\w\]\[!])\[(\d{1,3})\](?![(:\[])", scan):
        line_start = scan.rfind("\n", 0, m.start()) + 1
        if not scan[line_start:m.start()].strip(" \t-*+"):
            continue  # a definition or reference entry, not a marker
        if m.group(1) is not None:
            ok = ("^" + m.group(1)).lower() in defs
            label = "[^%s]" % m.group(1)
        else:
            n = m.group(2)
            ok = n in defs or n in entries or 1 <= int(n) <= listed
            label = "[%s]" % n
        if not ok:
            out.append((label, _line_of(doc.scan_lines, m.start())))
    return out


def _html_orphans(page: _PageText, prose: str, doc: _Doc) -> List[Tuple[str, Optional[int]]]:
    out: List[Tuple[str, Optional[int]]] = []
    for frag, start, end, line in page.fragments:
        label = " ".join(prose[start:end].split())
        looks = bool(re.match(r"^\[?\^?[\w-]{1,10}\]?$", label) and re.search(r"\d|\^", label)) or bool(
            re.match(r"^(?:fn|footnote|cite|ref|note|source)", frag, re.I))
        if looks and frag not in page.ids:
            out.append(("#" + frag, line))
    if not _has_reference_heading(doc.blocks) and not page.fragments:
        inside = _Spans(page.links)
        for m in re.finditer(r"(?<![\w\]\[])\[(\d{1,3})\](?![(\[])", prose):
            if not inside.overlaps(m.start(), m.start() + 1):
                out.append((m.group(0), _line_of(doc.prose_lines, m.start())))
    return out


# ----------------------------------------------------------------------------- claims

@functools.lru_cache(maxsize=1)
def _claim_patterns() -> List[Tuple[str, "re.Pattern[str]"]]:
    units = _alternation(lexicon("unit_nouns")["items"])
    more = r"(?:more|less|fewer|faster|slower|higher|lower|better|worse|cheaper|larger|smaller|likely)"
    return [
        ("comparative", re.compile(r"(?<![\w.])\d+(?:\.\d+)?\s?(?:x|\u00d7|times)\s+%s\b|\b(?:twice|three times|half)\s+as\s+"
                                   r"[a-z]+\b|(?<![\w.])\d+(?:\.\d+)?\s?%%\s+%s\b" % (more, more), re.I)),
        ("statistic", re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?\s?(?:%|percent\b|per\s?cent\b)", re.I)),
        ("quantity", re.compile(r"[$\u20ac\u00a3\u00a5]\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:k|m|bn|million|billion|trillion)\b)?"
                                r"|(?<![\w.])\d[\d,]*(?:\.\d+)?\s?(?:USD|EUR|GBP|dollars|euros|pounds)\b"
                                r"|(?<![\w.])\d+(?:\.\d+)?\s?(?:million|billion|trillion)\b"
                                r"|(?<![\w.])\d[\d,]*\+?\s+(?:%s)\b"
                                r"|(?<![\w.])\d{1,3}(?:,\d{3})+(?![\d,])" % units, re.I)),
        ("authority", re.compile(r"(?<!\w)(?:%s)(?!\w)|\baccording\s+to\s+(?:a|an|one|some|several|many)\s+(?:recent\s+)?"
                                 r"(?:study|report|survey|analysis|paper|poll|expert|experts)\b"
                                 % _alternation(lexicon("vague_authority")["items"]), re.I)),
    ]


def _sentence_at(text: str, start: int, end: int) -> str:
    a = max(text.rfind(c, 0, start) for c in ".!?\n")
    b_candidates = [i for i in (text.find(c, end) for c in ".!?\n") if i != -1]
    b = min(b_candidates) + 1 if b_candidates else len(text)
    return _visible(text[a + 1:b])[:200]


def _claims(text: str, links: Sequence[Tuple[int, int, str]], window: int) -> List[Dict[str, Any]]:
    starts: List[int] = []
    found: List[Tuple[int, int, str]] = []
    for kind, rx in _claim_patterns():
        for m in rx.finditer(text):
            s, e = m.span()
            i = bisect.bisect_right(starts, s)
            if (i and found[i - 1][1] > s) or (i < len(starts) and starts[i] < e):
                continue
            starts.insert(i, s)
            found.insert(i, (s, e, kind))
    index = _Spans(links)
    return [{"text": _sentence_at(text, s, e), "match": text[s:e], "kind": kind, "pos": s,
             "has_citation": _cited_near(text, index, s, e, window)} for s, e, kind in found]


def find_claims(text: str) -> List[Dict[str, Any]]:
    """Verifiable claims {text, match, kind, pos, has_citation} in Markdown or plain text.

    Kinds: statistic, quantity, authority, comparative (earlier kinds win overlapping spans in the
    order comparative, statistic, quantity, authority). A claim is cited when a link, footnote
    marker, author-year citation or named attribution ("according to <Name>") is within the
    citation window (200 characters). Fenced and inline code are ignored.
    """
    masked = _mask_code(text)
    return _claims(masked, _link_spans(masked), int(_thr("citation_window_chars")))


# ----------------------------------------------------------------------------- invisible characters

_INVISIBLE = re.compile("[\u061c\u115f\u1160\u180e\u200b-\u200f\u2000-\u200a\u2028-\u202e\u205f-\u2064\u2066-\u2069"
                        "\u2800\u3164\ufe00-\ufe0f\ufeff\uffa0\U000e0000-\U000e007f\U000e0100-\U000e01ef]")
_RTL = re.compile("[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufefc]")
_FLAG_TAGS = re.compile("\U0001f3f4[\U000e0020-\U000e007e]+\U000e007f")
_EMOJI_MODS = "\ufe0f\U0001f3fb\U0001f3fc\U0001f3fd\U0001f3fe\U0001f3ff"


def _kind_of(cp: int) -> str:
    if cp in (0x200C, 0x200D):
        return "joiner"
    if 0x202A <= cp <= 0x202E or 0x2066 <= cp <= 0x2069:
        return "bidi"
    if cp in (0x200E, 0x200F, 0x061C):
        return "bidi_mark"
    if 0xE0000 <= cp <= 0xE007F:
        return "tag"
    if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:
        return "variation_selector"
    if cp in (0x2028, 0x2029):
        return "separator"
    if 0x2000 <= cp <= 0x200A or cp in (0x205F, 0x2800, 0x3164, 0xFFA0, 0x115F, 0x1160):
        return "space"
    return "zero_width"


def _is_letter(ch: str) -> bool:
    return unicodedata.category(ch)[0] in ("L", "M")


def _is_emoji(ch: str) -> bool:
    cp = ord(ch)
    return cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF or 0x2B00 <= cp <= 0x2BFF or unicodedata.category(ch) == "So"


def invisible_chars(text: str) -> List[Dict[str, Any]]:
    """Invisible, bidi-control, tag and exotic-space characters {pos, char, name, kind}.

    Allowed: ZWJ/ZWNJ between letters (Persian, Indic) or inside emoji sequences, tag characters
    inside subdivision flag emoji, a single variation selector after a visible character (Han
    ideographic variants included), LRM/RLM/ALM in text that contains right-to-left script, and a
    leading BOM. Soft hyphens, no-break and ideographic spaces are not flagged.
    """
    flags = [m.span() for m in _FLAG_TAGS.finditer(text)]
    has_rtl = bool(_RTL.search(text))
    out: List[Dict[str, Any]] = []
    for m in _INVISIBLE.finditer(text):
        i, ch = m.start(), m.group(0)
        cp = ord(ch)
        kind = _kind_of(cp)
        prev = text[i - 1] if i > 0 else ""
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if cp == 0xFEFF and i == 0:
            continue
        if kind == "joiner":
            back = i - 1
            while back >= 0 and text[back] in _EMOJI_MODS:
                back -= 1
            before = text[back] if back >= 0 else ""
            if prev and nxt and ((_is_letter(prev) and _is_letter(nxt)) or
                                 (before and _is_emoji(before) and _is_emoji(nxt))):
                continue
        elif kind == "bidi_mark" and has_rtl:
            continue
        elif kind == "tag" and any(a < i < b for a, b in flags):
            continue
        elif kind == "variation_selector":
            stacked = prev and _kind_of(ord(prev)) == "variation_selector" and _INVISIBLE.match(prev)
            if prev and not prev.isspace() and not stacked and (cp <= 0xFE0F or _CJK.match(prev)):
                continue
        out.append({"pos": i, "char": "U+%04X" % cp, "name": unicodedata.name(ch, "U+%04X" % cp), "kind": kind})
    return out


# ----------------------------------------------------------------------------- years and freshness

_MONTHS = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
           r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?")
_Y = r"(?<!\d)((?:19|20)\d\d)(?!\d)"
_FRESH = [
    re.compile(r"\b(?:best|top|latest|newest|current)\b[^.\n]{0,60}?\b(?:of|in|for)\s+" + _Y, re.I),
    re.compile(r"\b(?:best|top)\s+(?:\d+\s+)?[A-Za-z][\w-]*(?:\s+[A-Za-z][\w-]*){0,4}\s+" + _Y + r"(?!\s*[-/])", re.I),
    re.compile(_Y + r"\s+(?:guide|edition|update|review|roundup|round-up|list|rankings?|buyer'?s\s+guide|comparison|"
               r"trends|predictions)\b", re.I),
    re.compile(r"\b(?:updated|refreshed|revised)\s+(?:for|in)\s+" + _Y, re.I),
    re.compile(r"\b(?:this|the\s+current)\s+year\s*\(\s*" + _Y + r"\s*\)", re.I),
    re.compile(r"\bin\s+" + _Y + r"\s+and\s+beyond\b", re.I),
]
_DATED = re.compile(r"\b(?:last\s+)?(?:updated|reviewed|revised|modified|refreshed)\s*(?:on\s+)?[:\u2013\u2014-]?\s*(?:"
                    + _MONTHS + r"\s+(?:\d{1,2}(?:st|nd|rd|th)?,?\s+)?|\d{1,2}\s+" + _MONTHS + r",?\s+|"
                    r"\d{1,2}[/.]\d{1,2}[/.])?" + _Y, re.I)
_UNDATED = [
    re.compile(r"\b(?:recently|newly|freshly|just)\s+(?:updated|refreshed|revised)\b", re.I),
    re.compile(r"\b(?:last\s+)?(?:updated|reviewed|refreshed|modified)\s*:[ \t]*(?:recently|lately|today|"
               r"this\s+(?:week|month|year))?[ \t]*$", re.I | re.M),
    re.compile(r"\bupdated\s+(?:for\s+)?(?:this|the\s+current)\s+year\b(?!\s*\()", re.I),
]
_DATE_NEAR = re.compile(r"(?<!\d)(?:19|20)\d\d(?!\d)|\b\d{1,2}[/.]\d{1,2}[/.]\d{2,4}\b")


def year_pattern(year: int) -> "re.Pattern[str]":
    """Regex matching four-digit years 2000..year+1 (the citability "recent year" signal)."""
    years = "|".join(str(y) for y in range(2000, int(year) + 2))
    return re.compile(r"(?<!\d)(?:%s)(?!\d)" % years)


def stale_years(text: str, *, today: date) -> List[Dict[str, Any]]:
    """Freshness claims tied to a past (or far-future) year {year, kind, pattern, text, pos}.

    ``fresh_claim`` (best/top ... YEAR, YEAR guide, updated for YEAR): stale when YEAR < this year.
    ``dated_label`` (Updated: March 2024): stale when older than the configured age. Plain
    historical mentions ("founded in 2019") are not freshness claims and are ignored.
    """
    max_age = int(_thr("stale_years", "dated_label_max_age_years"))
    ahead = int(_thr("stale_years", "future_years_allowed"))
    seen: Set[int] = set()
    out: List[Dict[str, Any]] = []
    for pattern, rxs in (("dated_label", [_DATED]), ("fresh_claim", _FRESH)):
        for rx in rxs:
            for m in rx.finditer(text):
                pos = m.start(1)
                if pos in seen:
                    continue
                seen.add(pos)
                y = int(m.group(1))
                old = today.year - (max_age if pattern == "dated_label" else 0)
                new = today.year + (0 if pattern == "dated_label" else ahead)
                kind = "stale" if y < old else "future" if y > new else ""
                if kind:
                    out.append({"year": y, "kind": kind, "pattern": pattern, "text": " ".join(m.group(0).split()),
                                "pos": pos})
    return sorted(out, key=lambda h: h["pos"])


def undated_updates(text: str) -> List[Dict[str, Any]]:
    """"Updated" claims with no date within 60 characters {text, pos}."""
    out = []
    for rx in _UNDATED:
        for m in rx.finditer(text):
            near = text[max(0, m.start() - 60): m.end() + 60]
            if not _DATE_NEAR.search(near):
                out.append({"text": " ".join(m.group(0).split()), "pos": m.start()})
    return sorted(out, key=lambda h: h["pos"])


# ----------------------------------------------------------------------------- citability

_GRADES = ((80, "A"), (65, "B"), (50, "C"), (35, "D"))
_PRONOUNS = re.compile(r"\b(?:it|its|they|them|their|this|that|these|those|he|she|his|her)\b", re.I)
_COPULA = re.compile(r"\b(?:is|are|was|were|means|refers)\b", re.I)
_LIST_LINE = re.compile(r"^\s*(?:[-*+\u2022]|\d+[.)])\s|\bstep\s+\d+\b", re.I | re.M)
_PCT = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?\s?%")
_MONEY = re.compile(r"[$\u20ac\u00a3\u00a5]\s?\d|(?<![\w.])\d[\d,.]*\s?(?:USD|EUR|GBP)\b")
_TOOLS = re.compile(r"\b(?:using|with|via|through)\s+[A-Z][\w.+-]*")


@functools.lru_cache(maxsize=1)
def _unit_re() -> "re.Pattern[str]":
    return re.compile(r"(?<![\w.])\d[\d,.]*\+?\s+(?:%s)\b" % _alternation(lexicon("unit_nouns")["items"]), re.I)


def _key_terms(text: str) -> List[str]:
    stop = _sets()["stop_words_en"]
    return [w for w in re.findall(r"[a-z0-9][a-z0-9'-]*", text.lower()) if len(w) >= 3 and w not in stop]


def _term_match(a: str, b: str) -> bool:
    short, long_ = sorted((a, b), key=len)
    return short == long_ or (len(short) >= 4 and long_.startswith(short))


def _entities(sents: Sequence[str]) -> int:
    count = 0
    for s in sents:
        tokens = re.findall(r"[A-Za-z][\w'\u2019&.-]*", s)
        run = False
        for tok in tokens[1:]:
            named = bool(re.match(r"[A-Z][a-z]", tok)) or bool(re.match(r"[A-Z]{2,}\b", tok))
            if named and not run:
                count += 1
            run = named
    return count


def _grade(score: int) -> str:
    return next((g for floor, g in _GRADES if score >= floor), "F")


def score_passage(text: str, *, heading: str = "", query: Optional[str] = None, year: int) -> Dict[str, Any]:
    """Heuristic citability of one passage: {score 0-100, grade A-F, parts, words, flags}.

    Parts and caps: answer <=30 (definition early 12 / later 6; direct first sentence 8; question
    heading answered (as in CITE002) 5; clarity share x5; query terms in the first 60 words x5), self_contained <=25
    (length band 134-167:10, 100-200:7, 40-300:4, <30 or >400:0, else 2; pronoun ratio <2%:8, <4%:5,
    <6%:3; named entities >=3:7, >=1:4; dangling opener -5), structure <=20 (sentence length 10-20:8,
    8-25:5, else 2; transitions 4; list items 4; several lines 4), statistics <=15 (percentages 3
    each up to 6; money 3 each up to 5; counts with units 2 each up to 4; a year 2000..year+1 2;
    named sources 2 each up to 4), uniqueness <=10 (first-party evidence 5; example 3; named tool 2).
    A readiness heuristic (class C), not a prediction of citations.
    """
    words = count_words(text)
    sents = sentences(text) or [text.strip()]
    first = sents[0] if sents else ""
    lead = " ".join(sents[:2])
    window = int(_thr("citability", "answer_window_words"))
    opening = " ".join(re.findall(r"\S+", text)[:window])
    flags: List[str] = []
    dangling = _dangling(first)
    deferred = any(h["pos"] == 0 for h in lexicon_hits(first[:80], "answer_deferrals"))
    defs = lexicon_hits(text, "definition_patterns_en")
    answer = 12 if any(h["pos"] < len(lead) for h in defs) else 6 if defs else 0
    first_words = count_words(first)
    answered = heading.strip().endswith(("?", "\uff1f")) and _answers(heading, text)
    if 5 <= first_words <= 40 and not (deferred or dangling) and (
            re.search(r"\d", first) or _COPULA.search(first) or answered):
        answer += 8
    if answered and not dangling:
        answer += 5
    lengths = [count_words(s) for s in sents]
    answer += round(5 * sum(1 for n in lengths if 5 <= n <= 25) / len(lengths)) if lengths else 0
    if query:
        terms = _key_terms(query)
        have = _key_terms(opening)
        if terms:
            answer += round(5 * sum(1 for t in terms if any(_term_match(t, h) for h in have)) / len(terms))
    answer = min(30, answer)

    band = (10 if 134 <= words <= 167 else 7 if 100 <= words <= 200 else 4 if 40 <= words <= 300
            else 0 if words < 30 or words > 400 else 2)
    ratio = len(_PRONOUNS.findall(text)) / words if words else 1.0
    pron = 8 if ratio < 0.02 else 5 if ratio < 0.04 else 3 if ratio < 0.06 else 0
    named = _entities(sents)
    ents = 7 if named >= 3 else 4 if named >= 1 else 0
    self_contained = max(0, min(25, band + pron + ents - (5 if dangling else 0)))

    avg = (sum(lengths) / len(lengths)) if lengths else 0
    structure = 8 if 10 <= avg <= 20 else 5 if 8 <= avg <= 25 else 2
    structure += 4 if lexicon_hits(text, "cue_transitions") else 0
    structure += 4 if _LIST_LINE.search(text) else 0
    structure += 4 if "\n" in text.strip() else 0
    structure = min(20, structure)

    stats = min(6, 3 * len(_PCT.findall(text))) + min(5, 3 * len(_MONEY.findall(text)))
    stats += min(4, 2 * len(_unit_re().findall(text))) + (2 if year_pattern(year).search(text) else 0)
    sources = len(_cite_re().findall(text)) + len(_PAREN_CITE.findall(text))
    stats = min(15, stats + min(4, 2 * sources))

    unique = (5 if lexicon_hits(text, "cue_first_party") else 0) + (3 if lexicon_hits(text, "cue_examples") else 0)
    unique = min(10, unique + (2 if _TOOLS.search(text) else 0))

    parts = {"answer": answer, "self_contained": self_contained, "structure": structure, "statistics": stats,
             "uniqueness": unique}
    score = min(100, sum(parts.values()))
    if dangling:
        flags.append("dangling_opener")
    if deferred:
        flags.append("answer_deferred")
    if words < 40:
        flags.append("short")
    if words > 300:
        flags.append("long")
    if not re.search(r"\d", text) and named == 0:
        flags.append("no_specifics")
    return {"score": score, "grade": _grade(score), "parts": parts, "words": words, "flags": flags}


def citability(blocks: Sequence[Tuple[str, str]], *, query: Optional[str] = None, year: int,
               top: Optional[int] = None) -> Dict[str, Any]:
    """Score every block with >= 20 words: {passages, mean_all, mean_top5, coverage_70, top, bottom}.

    `mean_top5` averages the best `top` (5) passages; `coverage_70` is the share (0-1) of passages
    scoring >= 70; `top`/`bottom` list the best and worst passages. Empty input gives nulls.
    """
    min_words = int(_thr("citability", "min_block_words"))
    n = int(top or _thr("citability", "top_n"))
    good = int(_thr("citability", "coverage_score"))
    passages: List[Dict[str, Any]] = []
    skipped = 0
    for index, (heading, text) in enumerate(blocks):
        if count_words(text) < min_words:
            skipped += 1
            continue
        row = {"index": index, "heading": heading}
        row.update(score_passage(text, heading=heading, query=query, year=year))
        row["preview"] = " ".join(text.split())[:120]
        passages.append(row)
    ranked = sorted(passages, key=lambda p: (-p["score"], p["index"]))
    scores = [p["score"] for p in passages]

    def brief(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{k: p[k] for k in ("index", "heading", "score", "grade")} for p in rows]

    return {
        "passages": passages,
        "mean_all": round(sum(scores) / len(scores), 1) if scores else None,
        "mean_top5": round(sum(p["score"] for p in ranked[:n]) / len(ranked[:n]), 1) if scores else None,
        "coverage_70": round(sum(1 for s in scores if s >= good) / len(scores), 2) if scores else None,
        "top": brief(ranked[:n]),
        "bottom": brief(sorted(passages, key=lambda p: (p["score"], p["index"]))[:n]),
        "skipped": skipped, "query": query,
        "note": "Heuristic readiness signal (evidence class C); not a prediction of AI citations.",
    }


# ----------------------------------------------------------------------------- prompt injection

@functools.lru_cache(maxsize=1)
def _injection_res() -> List[Tuple[str, "re.Pattern[str]"]]:
    addr = _alternation(lexicon("ai_address_terms")["items"])
    verbs = _alternation(lexicon("ai_imperative_verbs")["items"])
    tail = r"\b[^.\n]{0,160}?(?<!\w)(?:%s)(?!\w)" % verbs
    out = [
        ("instruction addressed to AI", re.compile(
            r"\b(?:note|message|instructions?|attention|notice|reminder|directive|request)\s+(?:to|for)\s+"
            r"(?:all\s+|any\s+|the\s+)?(?:%s)%s" % (addr, tail), re.I)),
        ("instruction addressed to AI", re.compile(
            r"\b(?:dear|hey|hello|hi|attention)\s+(?:all\s+|any\s+)?(?:%s)%s" % (addr, tail), re.I)),
        ("instruction addressed to AI", re.compile(
            r"(?:^[ \t]*|(?<=[.!?])\s+)(?:%s)\s*[:,]\s*(?:please\s+)?(?:%s)(?!\w)" % (addr, verbs), re.I | re.M)),
    ]
    for p in lexicon("prompt_injection_markers").get("patterns", []):
        out.append((p["name"], re.compile(p["regex"], re.M | (0 if p.get("case_sensitive") else re.I))))
    return out


_MAX_HITS = 200


def injection_hits(text: str, hidden: Sequence[Tuple[int, int, str]] = ()) -> List[Dict[str, Any]]:
    """Text that addresses AI systems with instructions {pos, end, name, hidden, reason, text}.

    Visible hits that open with a quotation mark are treated as quoted examples and skipped;
    hidden ones (``hidden`` ranges: comments, hidden elements) always count. At most 200 hits.
    """
    spans: List[Tuple[int, int, str]] = []
    for name, rx in _injection_res():
        spans.extend((m.start(), m.end(), name) for m in rx.finditer(text))
    out: List[Dict[str, Any]] = []
    last = -1
    index = _Spans(hidden)
    for start, end, name in sorted(spans, key=lambda s: (s[0], s[0] - s[1])):
        if start < last or len(out) >= _MAX_HITS:
            continue
        reason = next((r for a, b, r in hidden if a < end and start < b), "") if index.overlaps(start, end) else ""
        lead = text[max(0, start - 2):start + 1]
        if not reason and re.search(r"[\"'\u201c\u2018\u00ab`]", lead):
            continue
        out.append({"pos": start, "end": end, "name": name, "hidden": bool(reason), "reason": reason or "visible",
                    "text": _sentence_at(text, start, end)})
        last = end
    return out


# ----------------------------------------------------------------------------- site level

def _norm(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", (text or "").lower()))


def _split_brand(title: str) -> Tuple[str, str]:
    parts = re.split(r"\s[|\u2013\u2014\u00b7-]\s", title.strip())
    if len(parts) >= 2 and 2 <= len(parts[-1].strip()) <= 30:
        return " ".join(parts[:-1]).strip(), parts[-1].strip()
    return title.strip(), ""


def templated_metadata(pairs: List[Dict[str, str]]) -> Dict[str, Any]:
    """Detect machine-templated title/description pairs across pages.

    Per page: ``echo_cta`` (description repeats the title core and ends with a stock call to
    action), ``duplicate`` (description equals the title or its core), ``shared_skeleton`` (the
    description minus the page's own title words is shared by several pages: a swapped keyword),
    and the informational ``brand_suffix`` signal. Site risk: high when at least 3 pages are templated
    and the ratio reaches 0.30, medium from 0.10, low when any page is templated, else none.
    """
    cfg = _thr("templated_metadata")
    ctas = sorted(_sets()["stock_cta"], key=lambda c: (-len(c), c))
    rows: List[Dict[str, Any]] = []
    for pair in pairs:
        title, desc = (pair.get("title") or "").strip(), (pair.get("description") or "").strip()
        if not title or not desc:
            continue
        core, brand = _split_brand(title)
        n_desc, n_core, n_title = _norm(desc), _norm(core), _norm(title)
        signals: List[str] = []
        cta = next((c for c in ctas if n_desc == c or n_desc.endswith(" " + c)), "")
        echo = len(n_core.split()) >= int(cfg["min_core_tokens"]) and (" %s " % n_core) in (" %s " % n_desc)
        if echo and cta:
            signals.append("echo_cta")
        if n_desc in (n_core, n_title):
            signals.append("duplicate")
        if brand and n_desc.endswith(_norm(brand)):
            signals.append("brand_suffix")
        own = set(n_title.split())
        skeleton = " ".join(w for w in n_desc.split() if w not in own)
        rows.append({"url": pair.get("url"), "signals": signals, "cta": cta, "skeleton": skeleton})
    skeletons = Counter(r["skeleton"] for r in rows if len(r["skeleton"].split()) >= int(cfg["skeleton_min_tokens"]))
    shared = {s for s, c in skeletons.items() if c >= int(cfg["skeleton_min_pages"])}
    for r in rows:
        if r["skeleton"] in shared:
            r["signals"].append("shared_skeleton")
    templated = [r for r in rows if set(r["signals"]) - {"brand_suffix"}]
    ratio = len(templated) / len(rows) if rows else 0.0
    count = len(templated)
    if count >= int(cfg["min_templated_pages"]) and ratio >= float(cfg["high_ratio"]):
        risk = "high"
    elif count >= int(cfg["min_templated_pages"]) and ratio >= float(cfg["medium_ratio"]):
        risk = "medium"
    else:
        risk = "low" if count else "none"
    cta_counts = Counter(r["cta"] for r in rows if r["cta"])
    return {
        "pages": len(rows), "templated_count": count, "ratio": round(ratio, 3),
        "shared_cta_phrases": {k: v for k, v in sorted(cta_counts.items()) if v >= 2},
        "site_risk": risk,
        "templated": [{"url": r["url"], "signals": sorted(r["signals"])} for r in templated],
    }


_TOKENS = re.compile(r"[%s]|[^\W_%s]+" % (_CJK_CLASS, _CJK_CLASS))


def _shingles(text: str, k: int) -> Set[int]:
    tokens = _TOKENS.findall(text.lower())
    if len(tokens) < k:
        return set()
    return {int.from_bytes(hashlib.blake2b(" ".join(tokens[i:i + k]).encode("utf-8"), digest_size=8).digest(), "big")
            for i in range(len(tokens) - k + 1)}


MAX_PAGES = 3000
MAX_PAIRS = 10000


def near_duplicates(texts: Dict[str, str], *, k: int = 5, threshold: float = 0.85, max_pages: int = MAX_PAGES,
                    max_pairs: int = MAX_PAIRS) -> List[Dict[str, Any]]:
    """Page pairs whose word-shingle Jaccard similarity is >= `threshold` {a, b, similarity}.

    Exact similarity with prefix filtering (no sampling). Pages with fewer than `k` words are
    skipped; only the first `max_pages` URLs in sorted order are compared, and the search stops
    once `max_pairs` pairs are found (a result of that length may be truncated).
    """
    urls = sorted(texts)[: max(0, int(max_pages))]
    sets = {u: _shingles(texts[u] or "", int(k)) for u in urls}
    sets = {u: s for u, s in sets.items() if s}
    freq: Counter = Counter()
    for s in sets.values():
        freq.update(s)
    order = sorted(sets, key=lambda u: (len(sets[u]), u))
    index: Dict[int, List[str]] = {}
    out: List[Dict[str, Any]] = []
    t = float(threshold)
    for u in order:
        a = sets[u]
        size = len(a)
        prefix = sorted(a, key=lambda h: (freq[h], h))[: size - math.ceil(t * size - 1e-9) + 1]
        candidates: Set[str] = set()
        for h in prefix:
            candidates.update(index.get(h, ()))
        for v in sorted(candidates):
            b = sets[v]
            if len(b) + 1e-9 < t * size:
                continue
            inter = len(a & b)
            sim = inter / (size + len(b) - inter)
            if sim + 1e-9 >= t:
                x, y = sorted((u, v))
                out.append({"a": x, "b": y, "similarity": round(sim, 3)})
                if len(out) >= max_pairs:
                    return sorted(out, key=lambda p: (-p["similarity"], p["a"], p["b"]))
        for h in prefix:
            index.setdefault(h, []).append(u)
    return sorted(out, key=lambda p: (-p["similarity"], p["a"], p["b"]))


def check_site_text(texts_by_url: Dict[str, str], pairs: List[Dict[str, str]], catalog: Optional[RuleCatalog] = None,
                    *, base_url: Optional[str] = None) -> List[Finding]:
    """Site-level PSEO001 (near-duplicate pages) and META006 (templated metadata) findings."""
    cat = catalog or default_catalog()
    pseo = thresholds().get("pseo") or {}
    k, t = int(pseo.get("shingle", 5)), float(pseo.get("near_dup", 0.85))
    out: List[Finding] = []
    dups = near_duplicates(texts_by_url, k=k, threshold=t)
    if dups:
        pages = sorted({p["a"] for p in dups} | {p["b"] for p in dups})
        out.append(make("PSEO001", "%d page pairs are near-duplicates (shingle similarity >= %.2f) across %d pages."
                        % (len(dups), t, len(pages)), catalog=cat, url=base_url, affected=len(pages), sample=pages,
                        evidence={"pairs": len(dups), "threshold": t, "shingle_words": k, "top_pairs": dups[:5],
                                  "pages_compared": min(len(texts_by_url), MAX_PAGES),
                                  "truncated": len(texts_by_url) > MAX_PAGES or len(dups) >= MAX_PAIRS},
                        key="near-duplicates"))
    meta = templated_metadata(pairs)
    if meta["site_risk"] in ("high", "medium"):
        urls = sorted(str(r["url"]) for r in meta["templated"] if r["url"])
        out.append(make("META006", "%d of %d pages use templated title/description pairs (risk %s)."
                        % (meta["templated_count"], meta["pages"], meta["site_risk"]), catalog=cat, url=base_url,
                        affected=meta["templated_count"], sample=urls,
                        confidence="high" if meta["site_risk"] == "high" else "medium",
                        evidence={k: meta[k] for k in ("pages", "templated_count", "ratio", "shared_cta_phrases",
                                                       "site_risk")},
                        key="templated-metadata"))
    return out


# ----------------------------------------------------------------------------- page checks

_KINDS = {"html": "html", "htm": "html", "markdown": "markdown", "md": "markdown", "mdx": "markdown",
          "text": "text", "txt": "text"}


def _build(text: str, kind: str) -> _Doc:
    norm = _KINDS.get((kind or "").lower())
    if norm is None:
        raise ValueError("kind must be html, markdown or text, not %r" % kind)
    if norm == "html":
        return _build_html(text)
    doc = _build_markdown(text, frontmatter=norm == "markdown")
    doc.kind = norm
    return doc


def _scan_line(doc: _Doc, pos: int) -> Optional[int]:
    if doc.kind == "html":
        return _line_of(doc.scan_lines, pos)
    return _line_of(doc.prose_lines, pos)


def _prose_line(doc: _Doc, pos: int) -> Optional[int]:
    return _line_of(doc.prose_lines, pos)


def _raw_line(base: int, text: str, pos: int) -> int:
    return base + len(re.findall(r"\r\n|\n|\r", text[:pos]))


def lint_metrics(text: str, *, kind: str, today: date) -> Dict[str, Any]:
    """Counts behind the page rules (for `content-lint` summaries); same parsing as check_text."""
    return _analyze(_build(text, kind), today)[1]


def _analyze(doc: _Doc, today: date) -> Tuple[List[Tuple[str, str, Dict[str, Any]]], Dict[str, Any]]:
    """(rule specs [(rule, message, kwargs)], metrics) for one document."""
    specs: List[Tuple[str, str, Dict[str, Any]]] = []
    prose = doc.prose
    window = int(_thr("citation_window_chars"))
    words = count_words(prose)

    def add(rule: str, message: str, line: Optional[int], key: str, evidence: Dict[str, Any],
            confidence: str = "high") -> None:
        specs.append((rule, message, {"line": line, "key": key, "evidence": evidence, "confidence": confidence}))

    claims = _claims(prose, doc.links, window)
    uncited = [c for c in claims if not c["has_citation"]]
    if len(uncited) >= int(_thr("claims", "min_uncited")):
        add("CONT001", "%d of %d quantitative or authority claims have no citation within %d characters."
            % (len(uncited), len(claims), window), _prose_line(doc, uncited[0]["pos"]), "uncited-claims",
            {"claims": len(claims), "uncited": len(uncited),
             "sample": [{"kind": c["kind"], "match": _visible(c["match"]), "text": c["text"]} for c in uncited[:5]]},
            "medium")

    filler = lexicon_hits(prose, "filler")
    per_k = 1000.0 * len(filler) / words if words else 0.0
    if len(filler) >= int(_thr("filler", "min_hits")) and per_k >= float(_thr("filler", "per_1000_words")) - 1e-9:
        add("CONT002", "%d filler phrases (%.1f per 1,000 words); a style signal, not AI detection."
            % (len(filler), per_k), _prose_line(doc, filler[0]["pos"]), "filler",
            {"hits": len(filler), "words": words, "per_1000_words": round(per_k, 2),
             "terms": sorted({h["term"] for h in filler})[:10]}, "low")

    invisible: List[Tuple[Dict[str, Any], int]] = []
    for piece, base in doc.raw:
        invisible.extend((h, _raw_line(base, piece, h["pos"])) for h in invisible_chars(piece))
    if invisible:
        counts = Counter(h["char"] for h, _ in invisible)
        add("CONT003", "%d invisible, bidi-control or tag characters in the content (%s)."
            % (len(invisible), ", ".join(sorted(counts))), invisible[0][1], "invisible-chars",
            {"count": len(invisible), "chars": dict(sorted(counts.items())),
             "kinds": sorted({h["kind"] for h, _ in invisible}),
             "names": sorted({h["name"] for h, _ in invisible})[:10]})

    comment_index = _Spans(doc.comments)
    artifacts = [h for h in lexicon_hits(doc.scan, "ai_artifacts", html=doc.kind == "html")
                 if not comment_index.overlaps(h["pos"], h["pos"] + 1)]
    if artifacts:
        add("CONT004", "%d leftover assistant, editor or template artifacts in published text."
            % len(artifacts), _scan_line(doc, artifacts[0]["pos"]), "artifacts",
            {"hits": len(artifacts), "terms": sorted({h["term"] for h in artifacts})[:10],
             "sample": [_snippet(doc.scan, h["pos"], h["end"], 30) for h in artifacts[:5]]})

    stale: List[Tuple[Dict[str, Any], Optional[int]]] = [(h, _prose_line(doc, h["pos"]))
                                                         for h in stale_years(prose, today=today)]
    for piece, base in doc.meta:
        stale.extend((h, _raw_line(base, piece, h["pos"])) for h in stale_years(piece, today=today))
    undated = undated_updates(prose)
    if stale or undated:
        first_line = stale[0][1] if stale else _prose_line(doc, undated[0]["pos"])
        add("CONT005", "%d stale or future-dated freshness claims and %d undated 'updated' claims."
            % (len(stale), len(undated)), first_line, "stale-years",
            {"stale": [{"year": h["year"], "kind": h["kind"], "text": h["text"]} for h, _ in stale[:5]],
             "undated": [h["text"] for h in undated[:5]], "today": today.isoformat()}, "medium")

    min_pw = int(_thr("dangling", "min_paragraph_words"))
    paras = [(p, t) for p, t in doc.paragraphs if count_words(t) >= min_pw]
    dangling = [(p, t) for p, t in paras if _dangling(t)]
    ratio = len(dangling) / len(paras) if paras else 0.0
    if (len(paras) >= int(_thr("dangling", "min_paragraphs")) and len(dangling) >= int(_thr("dangling", "min_hits"))
            and ratio >= float(_thr("dangling", "ratio"))):
        add("CONT007", "%d of %d paragraphs open with a dangling reference (it/this/these...)."
            % (len(dangling), len(paras)), _prose_line(doc, dangling[0][0]), "dangling-openers",
            {"paragraphs": len(paras), "dangling": len(dangling), "ratio": round(ratio, 2),
             "sample": [_visible(" ".join(t.split()[:8])) for _, t in dangling[:3]]}, "medium")

    hype = lexicon_hits(prose, "hype_superlatives")
    link_index = _Spans(doc.links)
    unsupported = [h for h in hype if not _cited_near(prose, link_index, h["pos"], h["end"], window)]
    per_100 = 100.0 * len(unsupported) / words if words else 0.0
    if len(unsupported) >= int(_thr("hype", "min_unsupported")) and per_100 >= float(_thr("hype", "per_100_words")) - 1e-9:
        add("CONT008", "%d unsupported superlatives (%.2f per 100 words); a style signal, not AI detection."
            % (len(unsupported), per_100), _prose_line(doc, unsupported[0]["pos"]), "hype",
            {"hits": len(hype), "unsupported": len(unsupported), "words": words, "per_100_words": round(per_100, 2),
             "terms": sorted({h["term"] for h in unsupported})[:10]}, "low")

    if doc.orphans:
        add("CONT009", "%d citation markers point to no reference target." % len(doc.orphans), doc.orphans[0][1],
            "orphan-markers", {"markers": sorted({m for m, _ in doc.orphans})[:20], "count": len(doc.orphans)})

    injected = injection_hits(doc.scan, doc.hidden)
    if injected:
        hidden = any(h["hidden"] for h in injected)
        add("CONT010", "%d passages address AI systems with instructions (%s)."
            % (len(injected), "hidden" if hidden else "visible"), _scan_line(doc, injected[0]["pos"]),
            "ai-instructions",
            {"hits": len(injected), "hidden": hidden,
             "locations": [{k: h[k] for k in ("reason", "name", "text")} for h in injected[:5]]},
            "high" if hidden else "medium")

    report = citability(doc.blocks, year=today.year)
    low = float(_thr("citability", "low_mean_top5"))
    if report["passages"] and report["mean_top5"] < low:
        add("CITE001", "Best passages score %.1f on the citability heuristic (below %d); readiness signal only."
            % (report["mean_top5"], low), None, "citability",
            {"mean_all": report["mean_all"], "mean_top5": report["mean_top5"], "coverage_70": report["coverage_70"],
             "passages": len(report["passages"]), "weakest": report["bottom"][:3]})

    unanswered = [h for h, t in doc.blocks if h.strip().endswith(("?", "\uff1f")) and not _answers(h, t)]
    if unanswered:
        add("CITE002", "%d question headings are not answered in the first sentences below them." % len(unanswered),
            None, "question-headings", {"headings": [_visible(h) for h in unanswered[:5]], "count": len(unanswered)},
            "medium")

    lo, hi = _thr("citability", "passage_words")
    total = sum(count_words(t) for _, t in doc.blocks)
    qualifying = [t for _, t in doc.blocks if lo <= count_words(t) <= hi and not _dangling(t)]
    if doc.blocks and total >= int(_thr("citability", "min_block_words")) and not qualifying:
        add("CITE003", "No passage between %d and %d words stands on its own." % (lo, hi), None, "passages",
            {"blocks": len(doc.blocks), "words": total, "block_words": [count_words(t) for _, t in doc.blocks][:20]},
            "medium")

    metrics = {"words": words, "blocks": len(doc.blocks), "claims": len(claims), "uncited_claims": len(uncited),
               "filler_hits": len(filler), "hype_hits": len(hype), "unsupported_hype": len(unsupported),
               "invisible_chars": len(invisible), "artifacts": len(artifacts), "stale_years": len(stale),
               "undated_updates": len(undated), "dangling_paragraphs": len(dangling), "paragraphs": len(paras),
               "orphan_markers": len(doc.orphans), "ai_instructions": len(injected),
               "citability_mean_all": report["mean_all"], "citability_mean_top5": report["mean_top5"],
               "question_headings_unanswered": len(unanswered)}
    return specs, metrics


def _answers(heading: str, text: str) -> bool:
    """True when the first sentences under a question heading look like an answer."""
    sents = sentences(text)
    if not sents:
        return False
    first = sents[0]
    lead = " ".join(sents[:2])
    if any(h["pos"] == 0 for h in lexicon_hits(first, "answer_deferrals")):
        return False
    if re.match(r"^(?:yes|no)\b", first, re.I) or re.search(r"\d", first) or lexicon_hits(first, "definition_patterns_en"):
        return True
    terms = _key_terms(heading)
    have = _key_terms(" ".join(re.findall(r"\S+", lead)[:int(_thr("citability", "answer_window_words"))]))
    return not terms or any(_term_match(t, h) for t in terms for h in have)


def check_text(text: str, catalog: Optional[RuleCatalog] = None, *, kind: str, file: Optional[str] = None,
               url: Optional[str] = None, today: date) -> List[Finding]:
    """Page-level content findings (CONT001-005, CONT007-010, CITE001-003) for HTML or Markdown.

    `kind` is html, markdown (md, mdx) or text. HTML prose excludes chrome (nav, header, footer,
    aside, form), hidden elements and code; CONT003, CONT004 and CONT010 also read hidden text,
    titles and descriptions (CONT010 reads HTML comments too). Raises ValueError on an unknown kind.
    """
    cat = catalog or default_catalog()
    specs, _ = _analyze(_build(text, kind), today)
    return [make(rule, message, catalog=cat, file=file, url=url, **kw) for rule, message, kw in specs]
