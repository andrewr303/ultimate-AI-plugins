"""HTML and Markdown extraction into PageDoc (WP02; standard library ``html.parser`` only).

Every text field is page-derived and untrusted: callers truncate it before reporting.
Extraction rules worth knowing:

* ``titles`` holds ``<title>`` elements in the head only; a ``<title>`` inside ``<svg>`` or in the
  body is ignored. Canonical and hreflang ``<link>`` tags count only in the head.
* ``rel`` values are matched as case-insensitive token lists (``rel="Alternate Canonical"``).
* Image ``alt`` is ``None`` when the attribute is absent and ``""`` when it is empty.
* Visible text excludes head, script, style, template, noscript, svg and form widgets;
  ``main_text`` is the text of ``<main>``/``<article>``/``role=main`` when present, otherwise the
  visible text outside nav/header/footer/aside/form.
"""
from __future__ import annotations

import functools
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urldefrag, urljoin, urlsplit

from .rulesdb import loads_json, thresholds

VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())
INLINE = frozenset("a abbr b bdi bdo cite code data del dfn em font i ins kbd label mark q rp rt ruby s samp "
                   "small span strike strong sub sup time tt u var".split())
HEAD_OK = frozenset("html head title meta link style script base noscript template".split())
BOILERPLATE = frozenset("nav header footer aside form".split())
NO_TEXT = frozenset("script style template svg math textarea select iframe object noscript".split())
P_CLOSERS = frozenset("address article aside blockquote details div dl fieldset figure footer form h1 h2 h3 h4 h5 "
                      "h6 header hr main nav ol p pre section table ul li dd dt".split())
APP_ROOT_IDS = frozenset("root app __next __nuxt ___gatsby svelte q-app react-root".split())
APP_ROOT_TAGS = frozenset(["app-root"])
INLINE_SCRIPT_CAP = 20_000
TITLE_CAP = 1_000
LINK_TEXT_CAP = 200
JSONLD_NODE_CAP = 10_000
INVALID_JSONLD = "<invalid-json-ld>"
_WS = re.compile(r"\s+")
_CJK = re.compile("[぀-ヿ㐀-䶿一-鿿豈-﫿가-힯]")
_WORD = re.compile(r"\w+(?:['’]\w+)*")
_ICONISH = re.compile(r"logo|icon|avatar|sprite|pixel|badge", re.I)
_LAZY_CLASS = re.compile(r"(?:^|\s)lazy(?:load(?:ed)?|-loaded)?(?:\s|$)", re.I)
_SCHEMA_PREFIX = re.compile(r"^(?:https?://)?schema\.org/", re.I)


@dataclass
class PageDoc:
    """Extracted page facts (see module docstring). Fields after `meta_refresh` are additive."""
    path: Optional[str] = None
    url: Optional[str] = None
    raw_size: int = 0
    titles: List[str] = field(default_factory=list)
    meta: Dict[str, List[str]] = field(default_factory=dict)
    lang: Optional[str] = None
    base_href: Optional[str] = None
    canonicals: List[Tuple[str, int]] = field(default_factory=list)
    hreflang: List[Tuple[str, str, int]] = field(default_factory=list)
    alternates: List[Dict[str, Any]] = field(default_factory=list)
    links: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    headings: List[Tuple[int, str, int]] = field(default_factory=list)
    jsonld: List[Dict[str, Any]] = field(default_factory=list)
    has_microdata: bool = False
    has_rdfa: bool = False
    scripts: List[Dict[str, Any]] = field(default_factory=list)
    visible_text: str = ""
    main_text: str = ""
    word_count: int = 0
    paragraphs: List[str] = field(default_factory=list)
    app_root_text_len: Optional[int] = None
    noscript_text_len: int = 0
    onclick_divs: int = 0
    unlabeled_inputs: int = 0
    meta_refresh: Optional[str] = None
    link_tags: List[Dict[str, Any]] = field(default_factory=list)   # every <link>: rel, href, as, type, line, in_head
    resources: List[Dict[str, Any]] = field(default_factory=list)   # subresource URLs: {tag, url, line}
    body_attrs: Dict[str, str] = field(default_factory=dict)
    kind: str = "html"


def collapse(text: str) -> str:
    """Whitespace-collapsed, stripped text."""
    return _WS.sub(" ", text or "").strip()


def count_words(text: str) -> int:
    """Word count; each CJK character counts as one word."""
    return len(_CJK.findall(text)) + len(_WORD.findall(_CJK.sub(" ", text)))


@functools.lru_cache(maxsize=1)
def _hints() -> Tuple[int, int]:
    block = thresholds().get("images")
    block = block if isinstance(block, dict) else {}
    return int(block.get("viewport_words", 150)), int(block.get("lcp_candidate_min_px", 200))


def _num(value: Optional[str]) -> Optional[float]:
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*(?:px)?\s*$", value or "")
    return float(m.group(1)) if m else None


def _srcset_urls(value: str) -> List[str]:
    return [part.strip().split()[0] for part in (value or "").split(",") if part.strip()]


class _Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.doc = PageDoc()
        self.stack: List[str] = []
        self.open: Dict[str, int] = {}
        self.in_head = False
        self.body_started = False
        self.chunks: List[Tuple[str, bool, bool]] = []
        self.caps: List[Dict[str, Any]] = []   # open captures: {kind, depth, parts, ...}
        self.cdata: Optional[Dict[str, Any]] = None
        self.root_depth: Optional[int] = None
        self.root_parts: List[str] = []
        self.main_marks: List[int] = []
        self.main_seen = False
        self.words = 0
        self.label_for: set = set()
        self.inputs: List[Tuple[str, bool]] = []
        self.viewport_words, self.lcp_min_px = _hints()

    # ------------------------------------------------------------------ context helpers
    def _in(self, *tags: str) -> bool:
        return any(self.open.get(t) for t in tags)

    def _in_main(self) -> bool:
        return bool(self.main_marks) or self._in("main", "article")

    def _sep(self) -> None:
        if self.chunks and not self.chunks[-1][0].isspace():
            self.chunks.append((" ", self._in_main(), self._in(*BOILERPLATE)))

    def _push(self, tag: str) -> None:
        self.stack.append(tag)
        self.open[tag] = self.open.get(tag, 0) + 1

    def _pop_to(self, tag: str) -> None:
        while self.stack:
            t = self.stack.pop()
            self.open[t] -= 1
            self._closed(len(self.stack))
            if t == tag:
                return

    def _closed(self, depth: int) -> None:
        if self.cdata is not None and self.cdata["depth"] == depth:
            self.cdata = None
        if self.root_depth == depth:
            self.doc.app_root_text_len = len(collapse("".join(self.root_parts)))
            self.root_depth = None
        while self.main_marks and self.main_marks[-1] >= depth:
            self.main_marks.pop()
        keep = []
        for cap in self.caps:
            if cap["depth"] != depth:
                keep.append(cap)
                continue
            text = collapse("".join(cap["parts"]))
            if cap["kind"] == "title":
                self.doc.titles.append(text[:TITLE_CAP])
            elif cap["kind"] == "heading":
                self.doc.headings.append((cap["level"], text[:TITLE_CAP], cap["line"]))
            elif cap["kind"] == "link":
                cap["rec"]["text"] = (text or collapse(" ".join(cap["alts"])))[:LINK_TEXT_CAP]
            elif cap["kind"] == "para" and len(text) > 20:
                self.doc.paragraphs.append(text)
        self.caps = keep

    def _cap(self, kind: str, **extra: Any) -> None:
        self.caps.append(dict(kind=kind, depth=len(self.stack), parts=[], **extra))

    # ------------------------------------------------------------------ parser callbacks
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        a: Dict[str, str] = {}
        for k, v in attrs:
            a.setdefault(k.lower(), v if v is not None else "")
        line = self.getpos()[0]
        foreign = self._in("svg", "math")
        if tag == "head" and not self.body_started:
            self.in_head = True
        elif tag == "body":
            self.in_head, self.body_started = False, True
            self.doc.body_attrs = dict(a)
        elif tag not in HEAD_OK and not foreign:
            self.in_head, self.body_started = False, True
        head_ctx = self.in_head or not self.body_started
        if tag in P_CLOSERS and self.open.get("p") and "p" in self.stack:
            self._pop_to("p")
        if tag in ("li", "dd", "dt") and self.stack:
            for t in reversed(self.stack):
                if t in ("ul", "ol", "dl", "table"):
                    break
                if t in ("li", "dd", "dt"):
                    self._pop_to(t)
                    break
        if "itemscope" in a or "itemtype" in a or "itemprop" in a:
            self.doc.has_microdata = True
        if "typeof" in a or "vocab" in a or ("property" in a and tag != "meta"):
            self.doc.has_rdfa = True
        self._element(tag, a, line, head_ctx, foreign)
        if tag not in VOID:
            self._push(tag)
        if tag not in INLINE:
            self._sep()

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID:
            self.handle_endtag(tag)

    def _element(self, tag: str, a: Dict[str, str], line: int, head_ctx: bool, foreign: bool) -> None:
        doc = self.doc
        if tag == "html" and doc.lang is None and a.get("lang", "").strip():
            doc.lang = a["lang"].strip()
        elif tag == "base" and doc.base_href is None and "href" in a:
            doc.base_href = a["href"].strip()
        elif tag == "meta" and not foreign:
            key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").strip().lower()
            if key:
                doc.meta.setdefault(key, []).append(a.get("content", ""))
                if key == "refresh" and doc.meta_refresh is None:
                    doc.meta_refresh = a.get("content", "")
            if "charset" in a:
                doc.meta.setdefault("charset", []).append(a["charset"])
        elif tag == "link":
            self._link_tag(a, line, head_ctx)
        elif tag == "title" and head_ctx and not foreign:
            self._cap("title")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and not foreign and not self._in("noscript", "template"):
            self._cap("heading", level=int(tag[1]), line=line)
        elif tag == "a" and not foreign:
            rel = a.get("rel", "").lower().split()
            rec = {"href": a.get("href"), "text": "", "rel": rel, "line": line, "nofollow": "nofollow" in rel,
                   "onclick": "onclick" in a, "role": a.get("role")}
            doc.links.append(rec)
            self._cap("link", rec=rec, alts=[])
        elif tag == "img":
            self._image(a, line)
        elif tag == "script":
            self._script(a, line, head_ctx)
        elif tag in ("p", "li", "dd") and not any(c["kind"] == "para" for c in self.caps):
            self._cap("para")
        elif tag in ("input", "select", "textarea"):
            kind = a.get("type", "text").lower()
            if kind not in ("hidden", "submit", "button", "image", "reset"):
                named = bool(a.get("aria-label") or a.get("aria-labelledby") or a.get("title"))
                self.inputs.append((a.get("id", ""), named or self._in("label")))
        elif tag == "label" and a.get("for"):
            self.label_for.add(a["for"])
        if tag in ("iframe", "video", "audio", "source", "embed", "track"):
            for attr in ("src", "poster"):
                if a.get(attr):
                    doc.resources.append({"tag": tag, "url": a[attr], "line": line})
            for u in _srcset_urls(a.get("srcset", "")):
                doc.resources.append({"tag": tag, "url": u, "line": line})
        elif tag == "object" and a.get("data"):
            doc.resources.append({"tag": tag, "url": a["data"], "line": line})
        if tag in ("div", "span") and "onclick" in a:
            doc.onclick_divs += 1
        if self.body_started and self.root_depth is None and doc.app_root_text_len is None and (
                a.get("id", "").strip() in APP_ROOT_IDS or tag in APP_ROOT_TAGS) and tag not in VOID:
            self.root_depth, self.root_parts = len(self.stack), []
        if tag in ("main", "article") or a.get("role", "").strip().lower() == "main":
            self.main_seen = True
            if a.get("role", "").strip().lower() == "main":
                self.main_marks.append(len(self.stack))

    def _link_tag(self, a: Dict[str, str], line: int, head_ctx: bool) -> None:
        doc = self.doc
        rel = a.get("rel", "").lower().split()
        href = a.get("href")
        doc.link_tags.append({"rel": rel, "href": href, "as": a.get("as", "").lower(), "type": a.get("type", "").lower(),
                              "hreflang": a.get("hreflang"), "imagesrcset": a.get("imagesrcset"), "line": line,
                              "in_head": head_ctx})
        if href and set(rel) & {"stylesheet", "preload", "modulepreload", "icon"}:
            doc.resources.append({"tag": "link", "url": href, "line": line})
        if not head_ctx:
            return
        if "canonical" in rel:
            doc.canonicals.append(((href or "").strip(), line))
        if "alternate" in rel and a.get("hreflang") is not None:
            doc.hreflang.append((a["hreflang"].strip(), (href or "").strip(), line))
        elif "alternate" in rel or "describedby" in rel:
            doc.alternates.append({"rel": "describedby" if "describedby" in rel else "alternate",
                                   "type": a.get("type", "").strip().lower(), "href": (href or "").strip(),
                                   "line": line})

    def _image(self, a: Dict[str, str], line: int) -> None:
        src = a.get("src")
        cls = "%s %s" % (a.get("class", ""), a.get("id", ""))
        lazy = None
        if a.get("loading", "").strip().lower() == "lazy":
            lazy = "native"
        elif any(k in a for k in ("data-src", "data-lazy-src", "data-srcset", "data-lazy")) or _LAZY_CLASS.search(cls):
            lazy = "js"
        w, h = _num(a.get("width")), _num(a.get("height"))
        small = w is not None and h is not None and max(w, h) < self.lcp_min_px
        iconish = bool(_ICONISH.search("%s %s %s" % (src or "", cls, a.get("alt") or "")))
        guess = (self.body_started and not self._in("nav", "footer", "aside", "noscript") and not small
                 and not iconish and bool(src) and not (src or "").startswith("data:")
                 and self.words < self.viewport_words)
        rec = {"src": src, "alt": a.get("alt") if "alt" in a else None, "width": a.get("width"),
               "height": a.get("height"), "loading": a.get("loading"), "fetchpriority": a.get("fetchpriority"),
               "srcset": a.get("srcset"), "sizes": a.get("sizes"), "line": line, "in_first_viewport_guess": guess,
               "lazy": lazy, "style": a.get("style", ""), "decorative": a.get("aria-hidden", "").lower() == "true"
               or a.get("role", "").lower() in ("presentation", "none")}
        self.doc.images.append(rec)
        for cap in self.caps:
            if cap["kind"] == "link" and rec["alt"]:
                cap["alts"].append(rec["alt"])
        for u in ([src] if src else []) + _srcset_urls(a.get("srcset", "")):
            self.doc.resources.append({"tag": "img", "url": u, "line": line})

    def _script(self, a: Dict[str, str], line: int, head_ctx: bool) -> None:
        kind = a.get("type", "").strip().lower()
        if kind == "application/ld+json":
            rec: Dict[str, Any] = {"raw": "", "line": line}
            self.doc.jsonld.append(rec)
            self.cdata = {"kind": "jsonld", "depth": len(self.stack), "rec": rec}
            return
        rec = {"src": a.get("src"), "type": kind, "async": "async" in a, "defer": "defer" in a,
               "module": kind == "module", "inline_text": "", "in_head": head_ctx, "line": line, "length": 0}
        self.doc.scripts.append(rec)
        if a.get("src"):
            self.doc.resources.append({"tag": "script", "url": a["src"], "line": line})
        self.cdata = {"kind": "script", "depth": len(self.stack), "rec": rec}

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID or not self.open.get(tag):
            return
        self._pop_to(tag)
        if tag == "head":
            self.in_head = False
        if tag not in INLINE:
            self._sep()

    def handle_data(self, data: str) -> None:
        if self.cdata is not None:
            kind = self.cdata["kind"]
            if kind == "jsonld":
                self.cdata["rec"]["raw"] += data
            elif kind == "script":
                rec = self.cdata["rec"]
                rec["length"] += len(data)
                if len(rec["inline_text"]) < INLINE_SCRIPT_CAP:
                    rec["inline_text"] = (rec["inline_text"] + data)[:INLINE_SCRIPT_CAP]
            return
        for cap in self.caps:
            if cap["kind"] == "title":
                cap["parts"].append(data)
                return
        if self._in("noscript"):
            self.doc.noscript_text_len += len(collapse(data))
            return
        if self._in(*NO_TEXT) or (self.in_head and not self.body_started):
            return
        if not self.body_started:
            if not data.strip():
                return
            self.body_started = True
        self.chunks.append((data, self._in_main(), self._in(*BOILERPLATE)))
        if data.strip():
            self.words += count_words(data)
        for cap in self.caps:
            cap["parts"].append(data)
        if self.root_depth is not None:
            self.root_parts.append(data)

    def finish(self) -> PageDoc:
        self.close()
        while self.stack:
            self._pop_to(self.stack[-1])
        doc = self.doc
        doc.visible_text = collapse("".join(c[0] for c in self.chunks))
        if self.main_seen:
            doc.main_text = collapse("".join(c[0] for c in self.chunks if c[1]))
        else:
            doc.main_text = collapse("".join(c[0] for c in self.chunks if not c[2]))
        doc.word_count = count_words(doc.main_text)
        doc.unlabeled_inputs = sum(1 for ident, named in self.inputs if not named and ident not in self.label_for)
        return doc


def parse_html(text: str, *, path: Optional[str] = None, url: Optional[str] = None) -> PageDoc:
    """Extract a PageDoc from HTML text (never raises on malformed markup)."""
    parser = _Extractor()
    try:
        parser.feed(text or "")
    except (AssertionError, ValueError):  # pragma: no cover - html.parser is tolerant
        pass
    doc = parser.finish()
    doc.path, doc.url = path, url
    doc.raw_size = len((text or "").encode("utf-8", "replace"))
    return doc


# ---------------------------------------------------------------------------------------- Markdown

_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")
_ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
_MD_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
_AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
_MDX_LINE = re.compile(r"^\s*(?:(?:import|export)\s|</?[A-Z][\w.]*(?:[\s/>]|$))")
_LIST = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_FM_KEYS = {"title": "title", "description": "description", "canonical": "canonical", "canonical_url": "canonical",
            "canonicalurl": "canonical", "lang": "lang", "language": "lang", "robots": "robots"}


def _frontmatter(text: str) -> Tuple[Dict[str, Tuple[str, int]], List[str], int]:
    lines = text.splitlines()
    if not lines or lines[0].strip() not in ("---", "+++"):
        return {}, lines, 0
    fence = lines[0].strip()
    closers = ("---", "...") if fence == "---" else ("+++",)
    for end in range(1, len(lines)):
        if lines[end].strip() in closers:
            break
    else:
        return {}, lines, 0
    sep = ":" if fence == "---" else "="
    out: Dict[str, Tuple[str, int]] = {}
    for i in range(1, end):
        key, found, value = lines[i].partition(sep)
        key = key.strip().lower()
        if not found or lines[i][:1].isspace() or key not in _FM_KEYS and key != "noindex":
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key == "noindex":
            if value.lower() in ("true", "yes"):
                out.setdefault("robots", ("noindex", i + 1))
            continue
        if value and value[0] not in "[{|>&*!":
            out.setdefault(_FM_KEYS[key], (value, i + 1))
    return out, lines[end + 1:], end + 1


def parse_markdown(text: str, *, path: Optional[str] = None) -> PageDoc:
    """PageDoc from Markdown/MDX: frontmatter (--- YAML or +++ TOML scalars), CommonMark fences."""
    doc = PageDoc(path=path, kind="markdown", raw_size=len((text or "").encode("utf-8", "replace")))
    text = (text or "").lstrip("﻿")
    fm, body, offset = _frontmatter(text)
    mdx = bool(path and path.lower().endswith(".mdx"))
    fence: Optional[Tuple[str, int]] = None
    visible: List[str] = []
    block: List[str] = []
    for idx, line in enumerate(body, start=offset + 1):
        if fence is not None:
            m = _FENCE_CLOSE.match(line)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1]:
                fence = None
            continue
        m = _FENCE_OPEN.match(line)
        if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            fence = (m.group(1)[0], len(m.group(1)))
            _flush(doc, block)
            continue
        if mdx and _MDX_LINE.match(line):
            continue
        for m2 in _MD_LINK.finditer(line):
            if m2.group(1):
                doc.images.append({"src": m2.group(3), "alt": m2.group(2), "width": None, "height": None,
                                   "loading": None, "fetchpriority": None, "srcset": None, "sizes": None,
                                   "line": idx, "in_first_viewport_guess": False, "lazy": None, "style": "",
                                   "decorative": False})
            else:
                doc.links.append({"href": m2.group(3), "text": _strip_md(m2.group(2)), "rel": [], "line": idx,
                                  "nofollow": False, "onclick": False, "role": None})
        for m3 in _AUTOLINK.finditer(line):
            doc.links.append({"href": m3.group(1), "text": m3.group(1), "rel": [], "line": idx, "nofollow": False,
                              "onclick": False, "role": None})
        h = _ATX.match(line)
        if h:
            _flush(doc, block)
            heading = _strip_md(h.group(2) or "")
            doc.headings.append((len(h.group(1)), heading, idx))
            visible.append(heading)
            continue
        if not line.strip() or _LIST.match(line):
            _flush(doc, block)
        plain = _strip_md(line)
        if plain:
            block.append(plain)
            visible.append(plain)
    _flush(doc, block)
    doc.visible_text = doc.main_text = collapse(" ".join(visible))
    doc.word_count = count_words(doc.main_text)
    if "title" in fm:
        doc.titles = [fm["title"][0][:TITLE_CAP]]
    else:
        h1 = next((t for lvl, t, _ in doc.headings if lvl == 1 and t), None)
        doc.titles = [h1] if h1 else []
    for key in ("description", "robots"):
        if key in fm:
            doc.meta[key] = [fm[key][0]]
    if "canonical" in fm:
        doc.canonicals = [fm["canonical"]]
    if "lang" in fm:
        doc.lang = fm["lang"][0]
    return doc


def _strip_md(line: str) -> str:
    s = _MD_LINK.sub(lambda m: m.group(2), line)
    s = _AUTOLINK.sub(lambda m: m.group(1), s)
    s = re.sub(r"<[^>\n]+>", " ", s)
    s = re.sub(r"^\s{0,3}(?:#{1,6}\s+|>\s?)+", "", s)
    s = _LIST.sub("", s)
    s = re.sub(r"[*_~`]+", "", s)
    return collapse(s)


def _flush(doc: PageDoc, block: List[str]) -> None:
    text = collapse(" ".join(block))
    if len(text) > 20:
        doc.paragraphs.append(text)
    del block[:]


# ---------------------------------------------------------------------------------------- helpers

def extract_links(html: str, base_url: str) -> List[str]:
    """Absolute http(s) hrefs of <a> elements (base href honoured, fragments stripped, first-seen order)."""
    doc = parse_html(html, url=base_url)
    base = base_url
    if doc.base_href:
        candidate = urljoin(base_url, doc.base_href)
        if urlsplit(candidate).scheme in ("http", "https"):
            base = candidate
    out: List[str] = []
    seen = set()
    for link in doc.links:
        href = (link.get("href") or "").strip()
        if not href or href.startswith("#"):
            continue
        try:
            absolute = urldefrag(urljoin(base, href))[0]
            parts = urlsplit(absolute)
        except ValueError:
            continue
        if parts.scheme in ("http", "https") and parts.netloc and absolute not in seen:
            seen.add(absolute)
            out.append(absolute)
    return out


def jsonld_types(blocks: List[Dict[str, Any]]) -> List[str]:
    """Sorted unique @type values across JSON-LD blocks; "<invalid-json-ld>" marks unparsable blocks."""
    found = set()
    for block in blocks:
        try:
            data = loads_json(block.get("raw", "") if isinstance(block, dict) else str(block))
        except ValueError:
            found.add(INVALID_JSONLD)
            continue
        stack, seen = [data], 0
        while stack and seen < JSONLD_NODE_CAP:
            node = stack.pop()
            seen += 1
            if isinstance(node, dict):
                kind = node.get("@type")
                for t in (kind if isinstance(kind, list) else [kind]):
                    if isinstance(t, str) and t.strip():
                        found.add(_SCHEMA_PREFIX.sub("", t.strip()))
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    return sorted(found)
