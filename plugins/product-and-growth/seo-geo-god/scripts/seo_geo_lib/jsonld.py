"""JSON-LD extraction, structural validation and Google structured-data checks (WP04).

Emits SD001-SD015 and SD017-SD020 (SD016 is planned). Functions take strings and dicts; the only
file read is data/structured-data.json. Nothing here touches the network.

Structural semantics are re-implemented from the geoptimize validator (MIT): @graph members
inherit @context, an explicit "@context": null resets it, and nested property objects need
neither @context nor @type. The quote-atomic tag scanner, the template-expression skip list and
part of the placeholder list adapt ideas from claude-seo's schema hook (MIT).

Block dicts from `extract_blocks`: raw, line (of the <script> tag), content_line, index (1-based),
skipped (None or "template-expression"), self_closing, closed.
"""
from __future__ import annotations

import functools
import json
import math
import re
from datetime import date
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Set, Tuple
from urllib.parse import urlsplit

from . import rulesdb
from .findings import Finding, make, truncate
from .rulesdb import RuleCatalog

COMPONENT_EXTS = (".jsx", ".tsx", ".vue", ".svelte", ".astro", ".php", ".liquid", ".njk", ".erb", ".ejs", ".hbs")
JSON_EXTS = (".json", ".jsonld")
MAX_BLOCK_BYTES = 1_048_576
MAX_DEPTH = 64
MAX_BLOCKS = 500
NODE_CAP = 10_000
SUMMARY_ENTITIES = 200
SKIP_TEMPLATE = "template-expression"

_OPEN_RE = re.compile(r"<script(?=[\s/>])|<!--", re.I)
_CLOSE_RE = re.compile(r"</script(?=[\s/>])", re.I)
# Quoted spans are atomic and the fallback class excludes quotes, so scanning stays linear.
_TAG_TOKEN = re.compile(r'"[^"]*"|\'[^\']*\'|[^"\'>]+|>')
_TAG_TOKEN_COMPONENT = re.compile(r'"[^"]*"|\'[^\']*\'|`[^`]*`|[{}]|[^"\'`{}>]+|>')
_ATTR_RE = re.compile(r'([^\s"\'=<>`/]+)(?:\s*=\s*("[^"]*"|\'[^\']*\'|`[^`]*`|\{[^{}]*\}|[^\s"\'=<>`]+))?')
_TEMPLATE_MARKERS = ("{{", "{%", "{@html", "${", "<?php", "<?=", "<%")
_JSON_STRING_RE = re.compile(r'"(?:[^"\\]|\\[\s\S])*"')
_STRING_OR_QUOTE_RE = re.compile(r'"(?:[^"\\]|\\[\s\S])*"|"')
_JSX_EXPR_RE = re.compile(r"\{\s*[A-Za-z_$]")
_LDJSON_RE = re.compile(r"application/ld\+json", re.I)
_STRINGIFY_RE = re.compile(r"JSON\.stringify\s*\(")
_ESCAPED_RE = re.compile(r"\\u003c|\\x3c|replace(?:All)?\s*\(\s*(?:/[^/\n]{0,40}<|[\"'`]<)|JSON_HEX_TAG", re.I)
_MICRODATA_RE = re.compile(r"[\s\"']itemscope(?=[\s=>/])|[\s\"']itemtype\s*=", re.I)
_RDFA_RE = re.compile(r"[\s\"'](?:typeof|vocab)\s*=\s*[\"']", re.I)
_PLACEHOLDER_RE = re.compile(r"\[\s*(?:REPLACE|FILL|INSERT|TODO)|\[(?:Business Name|City|State|Phone|Address|URL|Email)\]"
                             r"|\[Your\b|lorem\s+ipsum|yourdomain", re.I)
_PLACEHOLDER_CS_RE = re.compile(r"\bREPLACE(?:_[A-Z]+)*\b|YOUR_")
_ISO_RE = re.compile(r"(\d{4})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2})(?:[.,]\d{1,9})?)?"
                     r"(Z|[+-](\d{2})(?::?(\d{2}))?)?)?)?)?")
_NUM_RE = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)")
_COUNT_RE = re.compile(r"\d{1,3}(?:,\d{3})+|\d+")
_PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_FRAC_RE = re.compile(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)")
_CURRENCY_RE = re.compile(r"[A-Z]{3}")
_PRIMARY_RE = re.compile(r"\.mainEntity(?:\[\d+\])?")
_CONTAINER_KEYS = ("@context", "@id", "@graph")
_REF_KEYS = {"@id", "@type"}


# ----------------------------------------------------------------------------- registry

@functools.lru_cache(maxsize=1)
def load_registry() -> Dict[str, Any]:
    """data/structured-data.json (cached; treat as read-only)."""
    return rulesdb.load_data("structured-data")


class _Reg:
    """Derived lookups over a structured-data registry dict."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        self.subtypes = {k: list(v) for k, v in (data.get("feature_subtypes") or {}).items()}
        self.features = [(f, self.expand(f.get("types") or ())) for f in data.get("features") or ()
                         if f.get("status") != "no_rich_result"]
        self.no_rich: Dict[str, List[Mapping[str, Any]]] = {}
        for entry in data.get("no_rich_result") or ():
            self.no_rich.setdefault(entry["type"], []).append(entry)
        self.self_serving = self.expand(data.get("self_serving_review_types") or ("Organization", "LocalBusiness"))
        self.rating_types = set(data.get("rating_types") or ("AggregateRating",))
        self.url_props = set(data.get("url_properties") or ())
        self.date_props = set(data.get("date_properties") or ())
        self.never_nudge = set(data.get("never_nudge") or ())
        self.placeholder_hosts = tuple(data.get("placeholder_hosts") or ("example.com",))
        self.placeholder_props = set(data.get("placeholder_properties") or ("@id", "logo", "url"))
        defaults = data.get("rating_defaults") or {}
        self.best = float(defaults.get("bestRating", 5))
        self.worst = float(defaults.get("worstRating", 1))

    def expand(self, names: Sequence[str]) -> Set[str]:
        """Names plus all listed subtypes (transitively)."""
        out: Set[str] = set()
        todo = list(names)
        while todo:
            name = todo.pop()
            if name not in out:
                out.add(name)
                todo.extend(self.subtypes.get(name, ()))
        return out

    def compatible(self, a: Set[str], b: Set[str]) -> bool:
        return not a or not b or bool(a & b) or bool(self.expand(sorted(a)) & b) or bool(self.expand(sorted(b)) & a)


@functools.lru_cache(maxsize=1)
def _default_reg() -> _Reg:
    return _Reg(load_registry())


def _prepare(registry: Optional[Mapping[str, Any]]) -> _Reg:
    return _default_reg() if registry is None else _Reg(registry)


# ----------------------------------------------------------------------------- extraction

def _is_component(filename: str) -> bool:
    return filename.lower().endswith(COMPONENT_EXTS)


class _Lines:
    """Incremental 1-based line numbers for increasing offsets."""

    def __init__(self, text: str) -> None:
        self.text, self.pos, self.line = text, 0, 1

    def at(self, pos: int) -> int:
        if pos < self.pos:
            return self.text.count("\n", 0, pos) + 1
        self.line += self.text.count("\n", self.pos, pos)
        self.pos = pos
        return self.line


def _tag_end(text: str, pos: int, component: bool) -> int:
    """Offset just past the '>' that closes a start tag, or -1 when the tag never closes."""
    token = _TAG_TOKEN_COMPONENT if component else _TAG_TOKEN
    depth, n = 0, len(text)
    while pos < n:
        m = token.match(text, pos)
        if m is None:
            return -1
        tok, pos = m.group(), m.end()
        if tok == ">":
            if depth == 0:
                return pos
        elif tok == "{":
            depth += 1
        elif tok == "}":
            depth = max(depth - 1, 0)
    return -1


def _is_jsonld_type(attrs: str) -> bool:
    for m in _ATTR_RE.finditer(attrs):
        name = m.group(1).lower()
        name = name[7:] if name.startswith("v-bind:") else name.lstrip(":")
        if name == "type":
            value = (m.group(2) or "").strip().strip("{}").strip().strip("\"'`").strip()
            return value.split(";")[0].strip().lower() == "application/ld+json"
    return False


def _skip_reason(raw: str, component: bool, self_closing: bool) -> Optional[str]:
    if not component:
        return None
    body = raw.strip()
    if self_closing or not body or any(marker in raw for marker in _TEMPLATE_MARKERS) or body[0] not in "{[":
        return SKIP_TEMPLATE
    return SKIP_TEMPLATE if _JSX_EXPR_RE.search(_JSON_STRING_RE.sub('""', body)) else None


def extract_blocks(text: str, *, filename: str = "", template_mode: Optional[bool] = None) -> List[Dict[str, Any]]:
    """JSON-LD script blocks in document order (a .json/.jsonld file is one block).

    Template-expression skipping applies to component files (COMPONENT_EXTS) or when
    `template_mode` is True. HTML comments are ignored; scanning is linear in the input.
    """
    if filename.lower().endswith(JSON_EXTS):
        return [{"raw": text, "line": 1, "content_line": 1, "index": 1, "skipped": None, "self_closing": False,
                 "closed": False}]
    component = _is_component(filename) if template_mode is None else bool(template_mode)
    lines, blocks, pos, n = _Lines(text), [], 0, len(text)
    while len(blocks) < MAX_BLOCKS:
        m = _OPEN_RE.search(text, pos)
        if m is None:
            break
        if m.group() == "<!--":
            end = text.find("-->", m.end())
            if end < 0:
                break
            pos = end + 3
            continue
        tag_end = _tag_end(text, m.end(), component)
        if tag_end < 0:
            break
        attrs = text[m.end():tag_end - 1]
        self_closing = component and attrs.rstrip().endswith("/")
        closed = True
        if self_closing:
            content_end = close_end = tag_end
        else:
            c = _CLOSE_RE.search(text, tag_end)
            if c is None:
                content_end = close_end = n
                closed = False
            else:
                gt = text.find(">", c.end())
                content_end, close_end = c.start(), (n if gt < 0 else gt + 1)
        if _is_jsonld_type(attrs):
            raw = text[tag_end:content_end]
            blocks.append({"raw": raw, "line": lines.at(m.start()), "content_line": lines.at(tag_end),
                           "index": len(blocks) + 1, "skipped": _skip_reason(raw, component, self_closing),
                           "self_closing": self_closing, "closed": closed})
        pos = max(close_end, m.end())
    return blocks


# ----------------------------------------------------------------------------- parsing and structure

def _json_error(exc: json.JSONDecodeError) -> Tuple[str, int, int]:
    """Python-version-independent (message, line, column): Python 3.13+ reports a trailing comma at the
    comma; older versions report the closing bracket after it, so both are normalized to the 3.13 form."""
    doc, pos, msg = exc.doc, exc.pos, exc.msg
    if not msg.startswith("Illegal trailing comma") and pos < len(doc) and doc[pos] in "}]":
        k = pos - 1
        while k >= 0 and doc[k] in " \t\r\n":
            k -= 1
        if k >= 0 and doc[k] == ",":
            msg, pos = "Illegal trailing comma before end of %s" % ("object" if doc[pos] == "}" else "array"), k
    return msg, doc.count("\n", 0, pos) + 1, pos - doc.rfind("\n", 0, pos)


def _parse(raw: str, max_bytes: int) -> Tuple[Any, Optional[str], Optional[int]]:
    if len(raw) > max_bytes or len(raw.encode("utf-8", "replace")) > max_bytes:
        return None, "block is larger than %d bytes" % max_bytes, None
    if not raw.strip():
        return None, "empty JSON-LD block", None
    try:
        return rulesdb.loads_json(raw, max_depth=MAX_DEPTH), None, None
    except json.JSONDecodeError as exc:
        msg, line, col = _json_error(exc)
        return None, "malformed JSON (%s at line %d column %d)" % (msg, line, col), line
    except (ValueError, RecursionError) as exc:
        return None, str(exc) or "JSON could not be parsed", None


def parse_block(raw: str, *, max_bytes: int = MAX_BLOCK_BYTES) -> Tuple[Any, Optional[str]]:
    """(data, error): error is set for oversize, empty, malformed or deeper-than-64 JSON."""
    data, err, _ = _parse(raw, max_bytes)
    return data, err


def _kind(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, str):
        return "a string"
    return "an array" if isinstance(value, list) else "an object"


def _missing(value: Any) -> bool:
    return value is None or value == ""


def _is_context(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return True
    return isinstance(value, list) and bool(value) and all(
        x is None or isinstance(x, dict) or (isinstance(x, str) and bool(x.strip())) for x in value)


def _is_type(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return isinstance(value, list) and bool(value) and all(isinstance(x, str) and x.strip() for x in value)


def _scan(data: Any) -> Tuple[List[Tuple[str, str, str, str]], List[Tuple[str, Dict[str, Any], Any]]]:
    """(diagnostics as (rule, kind, path, message), top-level entities as (path, node, context))."""
    diags: List[Tuple[str, str, str, str]] = []
    top: List[Tuple[str, Dict[str, Any], Any]] = []
    stack: List[Tuple[Any, str, Any, int, bool]] = [(data, "$", None, 0, True)]
    seen = 0
    while stack:
        value, path, ctx, depth, is_root = stack.pop()
        seen += 1
        if depth > MAX_DEPTH or seen > NODE_CAP:
            diags.append(("SD002", "limit", path, "structure is too deep or too large to inspect"))
            break
        if isinstance(value, list):
            if not is_root:
                diags.append(("SD002", "root", path, "expected an object, found a nested array"))
                continue
            stack.extend((value[i], "%s[%d]" % (path, i), ctx, depth + 1, False) for i in range(len(value) - 1, -1, -1))
            continue
        if not isinstance(value, dict):
            diags.append(("SD002", "root", path, "expected an object, found %s" % _kind(value)))
            continue
        if "@context" in value:
            ctx = value["@context"]
            if not _missing(ctx) and not _is_context(ctx):
                diags.append(("SD005", "context", path, "@context must be a string, an object or an array of those, "
                              "found %s" % _kind(ctx)))
        has_graph = "@graph" in value
        if not has_graph or any(k not in _CONTAINER_KEYS for k in value):
            top.append((path, value, ctx))
            if _missing(ctx):
                why = "is null, which resets the inherited context" if "@context" in value else "is missing"
                diags.append(("SD003", "context", path, "entity @context %s" % why))
            if "@type" not in value or _missing(value["@type"]):
                diags.append(("SD004", "type", path, "entity has no @type"))
            elif not _is_type(value["@type"]):
                diags.append(("SD005", "type", path, "@type must be a non-empty string or array of strings, "
                              "found %s" % _kind(value["@type"])))
        if has_graph:
            graph, gpath = value["@graph"], path + ".@graph"
            if isinstance(graph, list):
                stack.extend((graph[i], "%s[%d]" % (gpath, i), ctx, depth + 1, False)
                             for i in range(len(graph) - 1, -1, -1))
            elif isinstance(graph, dict):
                stack.append((graph, gpath, ctx, depth + 1, False))
            else:
                diags.append(("SD002", "root", gpath, "@graph must be an object or an array of objects, "
                              "found %s" % _kind(graph)))
    return diags, top


def structural(data: Any, *, block: int = 1, line: Optional[int] = None) -> List[Dict[str, Any]]:
    """Diagnostics for SD002-SD005: {rule, kind, path, message, block, line}."""
    return [{"rule": r, "kind": k, "path": p, "message": m, "block": block, "line": line}
            for r, k, p, m in _scan(data)[0]]


def _norm_type(value: str) -> str:
    v = value.strip()
    for prefix in ("https://schema.org/", "http://schema.org/", "schema:"):
        if v.startswith(prefix):
            return v[len(prefix):]
    return v


def _types(node: Mapping[str, Any]) -> List[str]:
    raw = node.get("@type")
    items = raw if isinstance(raw, list) else [raw]
    return sorted({_norm_type(t) for t in items if isinstance(t, str) and t.strip()})


def _record(path: str, node: Dict[str, Any], ctx: Any, top: bool, primary: bool) -> Dict[str, Any]:
    eid = node.get("@id")
    return {"path": path, "node": node, "types": _types(node), "id": eid if isinstance(eid, str) else None,
            "top_level": top, "primary": primary, "context": ctx}


def _nested(node: Dict[str, Any], path: str, ctx: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    stack = [(node[k], "%s.%s" % (path, k), ctx, 1) for k in reversed(list(node)) if k not in ("@graph", "@context")]
    seen = 0
    while stack:
        value, vpath, vctx, depth = stack.pop()
        seen += 1
        if depth > MAX_DEPTH or seen > NODE_CAP:
            break
        if isinstance(value, list):
            stack.extend((value[i], "%s[%d]" % (vpath, i), vctx, depth + 1) for i in range(len(value) - 1, -1, -1))
        elif isinstance(value, dict):
            vctx = value["@context"] if "@context" in value else vctx
            if "@type" in value:
                out.append(_record(vpath, value, vctx, False, bool(_PRIMARY_RE.fullmatch(vpath[len(path):]))))
            stack.extend((value[k], "%s.%s" % (vpath, k), vctx, depth + 1)
                         for k in reversed(list(value)) if k != "@context")
    return out


def entities(data: Any) -> List[Dict[str, Any]]:
    """Top-level entities (root, root array, @graph members) and nested typed nodes, in document order.

    Each record: {path, node, types, id, top_level, primary, context}; `primary` marks top-level
    entities and the direct mainEntity of one.
    """
    out: List[Dict[str, Any]] = []
    for path, node, ctx in _scan(data)[1]:
        out.append(_record(path, node, ctx, True, True))
        out.extend(_nested(node, path, ctx))
    return out


def _scalars(data: Any) -> Iterator[Tuple[str, Optional[str], Any, Any]]:
    """(path, property, value, context) for every scalar value; @context values are not visited."""
    stack: List[Tuple[Any, str, Optional[str], Any, int]] = [(data, "$", None, None, 0)]
    seen = 0
    while stack:
        value, path, key, ctx, depth = stack.pop()
        seen += 1
        if seen > NODE_CAP or depth > MAX_DEPTH + 1:
            return
        if isinstance(value, dict):
            ctx = value["@context"] if "@context" in value else ctx
            stack.extend((value[k], "%s.%s" % (path, k), k, ctx, depth + 1)
                         for k in reversed(list(value)) if k != "@context")
        elif isinstance(value, list):
            stack.extend((value[i], "%s[%d]" % (path, i), key, ctx, depth + 1) for i in range(len(value) - 1, -1, -1))
        else:
            yield path, key, value, ctx


# ----------------------------------------------------------------------------- value helpers

def _is_schema(ctx: Any) -> bool:
    if isinstance(ctx, str):
        return "schema.org" in ctx.lower()
    if isinstance(ctx, dict):
        return any(isinstance(v, str) and "schema.org" in v.lower() for v in ctx.values())
    return isinstance(ctx, list) and any(_is_schema(x) for x in ctx)


def _placeholder(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    m = _PLACEHOLDER_RE.search(value) or _PLACEHOLDER_CS_RE.search(value)
    return m.group() if m else None


def _host(url: Any) -> Optional[str]:
    if not isinstance(url, str):
        return None
    try:
        parts = urlsplit(url.strip())
        host = parts.hostname
    except ValueError:
        return None
    if parts.scheme not in ("http", "https") or not host:
        return None
    host = host.lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def _on_host(host: Optional[str], domains: Sequence[str]) -> bool:
    return bool(host) and any(host == d or host.endswith("." + d) for d in domains)


def _same_site(a: str, b: str) -> bool:
    return a == b or a.endswith("." + b) or b.endswith("." + a)


def _url_problem(value: str, key: str) -> Optional[str]:
    v = value.strip()
    if key == "@id" and (v.startswith("_:") or v.lower().startswith("urn:")):
        return None
    if not v:
        return "empty"
    if v.startswith("//"):
        return "protocol-relative"
    try:
        parts = urlsplit(v)
    except ValueError:
        return "malformed"
    if parts.scheme in ("http", "https"):
        return None if parts.netloc else "malformed"
    return "non-http scheme %s:" % parts.scheme if parts.scheme else "relative"


def _iso_ok(value: str) -> bool:
    m = _ISO_RE.fullmatch(value.strip())
    if not m:
        return False
    year, month, day, hour, minute, second, _tz, tz_h, tz_m = m.groups()
    try:
        if month and not 1 <= int(month) <= 12:
            return False
        if day:
            date(int(year), int(month), int(day))
    except ValueError:
        return False
    if hour is not None and (int(hour) > 23 or int(minute) > 59 or (second is not None and int(second) > 60)):
        return False
    return tz_h is None or (int(tz_h) <= 14 and (tz_m is None or int(tz_m) <= 59))


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, str) and _NUM_RE.fullmatch(value.strip()):
        return float(value.strip())
    return None


def _count(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if math.isfinite(value) and value == int(value) else None
    if isinstance(value, str) and _COUNT_RE.fullmatch(value.strip()):
        return int(value.strip().replace(",", ""))
    return None


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return not (isinstance(value, (list, dict)) and not value)


def _resolve(value: Any, index: Mapping[str, Dict[str, Any]]) -> Any:
    if isinstance(value, dict) and set(value) <= _REF_KEYS and isinstance(value.get("@id"), str):
        return index.get(value["@id"], value)
    return value


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else [value]


def _present_simple(node: Any, dotted: str, index: Mapping[str, Dict[str, Any]]) -> bool:
    current = [node]
    for seg in dotted.split("."):
        found: List[Any] = []
        for value in current:
            for item in _as_list(_resolve(value, index)):
                item = _resolve(item, index)
                if isinstance(item, dict) and seg in item:
                    found.extend(_as_list(item[seg]))
        if not found:
            return False
        current = found
    return any(_has_value(_resolve(v, index)) for v in current)


def _present(node: Any, path: str, index: Mapping[str, Dict[str, Any]]) -> bool:
    """Path grammar: dotted keys; "a|b" alternatives; "list[].rest" every item; "list[:-1].rest" all but the last."""
    for marker, every in (("[].", True), ("[:-1].", False)):
        at = path.find(marker)
        if at >= 0:
            base, rest = path[:at], path[at + len(marker):]
            holder = _resolve(node, index)
            raw = holder.get(base) if isinstance(holder, dict) else None
            items = [_resolve(i, index) for i in _as_list(raw) if i is not None]
            if every:
                return bool(items) and all(_present(i, rest, index) for i in items)
            return all(_present(i, rest, index) for i in items[:-1])
    return any(_present_simple(node, alt, index) for alt in path.split("|"))


# ----------------------------------------------------------------------------- checks

class _Ctx:
    """Shared state for one lint_text call."""

    def __init__(self, catalog: RuleCatalog, reg: _Reg, filename: str, url: Optional[str],
                 merchant: Optional[bool]) -> None:
        self.cat, self.reg, self.file, self.url, self.merchant = catalog, reg, filename or None, url, merchant
        self.page_host = _host(url)
        self.page_is_placeholder_host = _on_host(self.page_host, reg.placeholder_hosts)
        self.findings: List[Finding] = []

    def add(self, rule: str, message: str, *, line: Optional[int], key: str, **kw: Any) -> None:
        self.findings.append(make(rule, message, catalog=self.cat, file=self.file, url=self.url, line=line,
                                  key=key, **kw))


def _label(rec: Mapping[str, Any]) -> str:
    return "%s (%s)" % (rec["path"], ", ".join(rec["types"]) or "untyped")


def _check_values(c: _Ctx, data: Any, b: Mapping[str, Any]) -> None:
    """SD006 placeholders (any vocabulary), SD013 URL and SD014 date values (schema.org only)."""
    holders: List[Tuple[str, str]] = []
    bad_urls: Dict[str, List[Tuple[str, str, str]]] = {}
    bad_dates: Dict[str, List[Tuple[str, Any]]] = {}
    for path, key, value, ctx in _scalars(data):
        token = _placeholder(value)
        if token is None and key in c.reg.placeholder_props and not c.page_is_placeholder_host:
            if _on_host(_host(value), c.reg.placeholder_hosts):
                token = "example.com"
        if token is not None:
            holders.append((path, token))
            continue
        if key is None or not _is_schema(ctx):
            continue
        if key in c.reg.url_props and isinstance(value, str):
            problem = _url_problem(value, key)
            if problem:
                bad_urls.setdefault(key, []).append((path, value, problem))
        elif key in c.reg.date_props and not isinstance(value, str) and value is not None:
            bad_dates.setdefault(key, []).append((path, value))
        elif key in c.reg.date_props and isinstance(value, str) and not _iso_ok(value):
            bad_dates.setdefault(key, []).append((path, value))
    i, line = b["index"], b["line"]
    if holders:
        c.add("SD006", "JSON-LD block %d has %d unreplaced placeholder value(s), first at %s (%s)."
              % (i, len(holders), holders[0][0], holders[0][1]), line=line, key="placeholder:b%d" % i,
              evidence={"block": i, "count": len(holders), "paths": [p for p, _ in holders[:10]],
                        "tokens": sorted({t for _, t in holders})},
              confidence="high" if any(t != "example.com" for _, t in holders) or c.page_host else "medium")
    for key, rows in sorted(bad_urls.items()):
        c.add("SD013", "JSON-LD block %d: %s is not an absolute http(s) URL (%s)." % (i, key, rows[0][2]),
              line=line, key="url:b%d:%s" % (i, key),
              evidence={"block": i, "property": key, "values": [v for _, v, _ in rows[:10]],
                        "paths": [p for p, _, _ in rows[:10]], "problems": sorted({p for _, _, p in rows})})
    for key, rows in sorted(bad_dates.items()):
        c.add("SD014", "JSON-LD block %d: %s value %r is not an ISO 8601 date." % (i, key, rows[0][1]),
              line=line, key="date:b%d:%s" % (i, key),
              evidence={"block": i, "property": key, "values": [v for _, v in rows[:10]],
                        "paths": [p for p, _ in rows[:10]]})


def _check_no_rich(c: _Ctx, rec: Mapping[str, Any], b: Mapping[str, Any], index: Mapping[str, Any]) -> None:
    for t in rec["types"]:
        for entry in c.reg.no_rich.get(t, ()):
            prop = entry.get("property")
            if prop:
                want = entry.get("value_type")
                values = [_resolve(v, index) for v in _as_list(rec["node"].get(prop)) if v is not None]
                if not values or (want and not any(isinstance(v, dict) and want in _types(v) for v in values)):
                    continue
            when = "since %s" % entry["since"] if entry.get("since") else "(being phased out)"
            what = "%s with %s" % (t, prop) if prop else t
            c.add("SD007", "%s: Google shows no %s rich result %s; keeping the markup is optional, not an error."
                  % (what, entry.get("feature", t), when), line=b["line"], severity=c.cat.severity_for("SD007"),
                  key="norich:%s:%s" % (t, prop or ""),
                  evidence={"type": t, "property": prop, "feature": entry.get("feature"), "since": entry.get("since"),
                            "status": entry.get("status"), "fact": entry.get("fact"), "path": rec["path"]})


def _offers(node: Mapping[str, Any], index: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [o for o in (_resolve(v, index) for v in _as_list(node.get("offers"))) if isinstance(o, dict)]


def _plain_offers(node: Mapping[str, Any], index: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return [o for o in _offers(node, index) if "AggregateOffer" not in _types(o)]


def _check_features(c: _Ctx, rec: Mapping[str, Any], b: Mapping[str, Any], index: Mapping[str, Any]) -> None:
    """SD008 missing required, SD009 missing recommended (nudge list only)."""
    node, types = rec["node"], set(rec["types"])
    for feature, ftypes in c.reg.features:
        if not types & ftypes:
            continue
        nested = not rec["primary"]
        if nested and not feature.get("nested"):
            continue
        confidence = "high"
        if feature.get("condition") == "has_offer":
            if c.merchant is False or (c.merchant is None and not _plain_offers(node, index)):
                continue
            confidence = "high" if c.merchant else "medium"
        exempt = set(feature.get("nested_exempt") or ()) if nested else set()
        missing = [p for p in feature.get("required") or () if p not in exempt and not _present(node, p, index)]
        missing += [" or ".join(g) for g in feature.get("required_one_of") or ()
                    if not any(_present(node, p, index) for p in g)]
        name = feature["feature"]
        if missing:
            c.add("SD008", "JSON-LD block %d %s: %s needs %s." % (b["index"], _label(rec), name, ", ".join(missing)),
                  line=b["line"], key="required:b%d:%s:%s" % (b["index"], rec["path"], name), confidence=confidence,
                  evidence={"block": b["index"], "path": rec["path"], "types": rec["types"], "feature": name,
                            "missing": missing})
        nudge = [p for p in feature.get("nudge") or () if p.split(".")[0] not in c.reg.never_nudge
                 and not _present(node, p, index)]
        if nudge:
            c.add("SD009", "JSON-LD block %d %s: %s recommends %s." % (b["index"], _label(rec), name, ", ".join(nudge)),
                  line=b["line"], key="recommended:b%d:%s:%s" % (b["index"], rec["path"], name),
                  evidence={"block": b["index"], "path": rec["path"], "feature": name, "missing": nudge})


def _check_self_serving(c: _Ctx, rec: Mapping[str, Any], b: Mapping[str, Any], index: Mapping[str, Any]) -> None:
    node, types = rec["node"], set(rec["types"])
    subject: Optional[Mapping[str, Any]] = None
    if types & c.reg.self_serving and any(_has_value(node.get(k)) for k in ("review", "aggregateRating")):
        subject = node
    elif rec["primary"] and types & (c.reg.rating_types | {"Review"}):
        reviewed = _resolve(node.get("itemReviewed"), index)
        if isinstance(reviewed, dict) and set(_types(reviewed)) & c.reg.self_serving:
            subject = reviewed
    if subject is None:
        return
    own = _host(subject.get("url")) or _host(subject.get("@id"))
    if c.page_host and own:
        if not _same_site(own, c.page_host):
            return
        confidence = "high"
    else:
        confidence = "medium" if c.page_host else "low"
    c.add("SD010", "JSON-LD block %d %s: a %s rates itself on what looks like its own site; Google treats "
          "self-serving reviews as ineligible." % (b["index"], rec["path"], "/".join(_types(subject)) or "business"),
          line=b["line"], key="selfserving:b%d:%s" % (b["index"], rec["path"]), confidence=confidence,
          evidence={"block": b["index"], "path": rec["path"], "types": _types(subject), "entity_host": own,
                    "page_host": c.page_host})


def _rating_problems(c: _Ctx, node: Mapping[str, Any]) -> List[str]:
    problems: List[str] = []
    value = node.get("ratingValue")
    if _has_value(value) and _placeholder(value) is None:
        num = _number(value)
        if num is None:
            text = value.strip() if isinstance(value, str) else ""
            pct, frac = _PCT_RE.fullmatch(text), _FRAC_RE.fullmatch(text)
            if pct and float(pct.group(1)) > 100:
                problems.append("ratingValue %s is above 100%%" % text)
            elif frac and (float(frac.group(2)) <= 0 or float(frac.group(1)) > float(frac.group(2))):
                problems.append("ratingValue %s is not a valid fraction" % text)
            elif not (pct or frac):
                problems.append("ratingValue %r is not numeric" % (value,))
        else:
            best = _number(node.get("bestRating"))
            worst = _number(node.get("worstRating"))
            best = c.reg.best if best is None else best
            worst = c.reg.worst if worst is None else worst
            if best <= worst:
                problems.append("bestRating %g is not above worstRating %g" % (best, worst))
            elif not worst <= num <= best:
                problems.append("ratingValue %g is outside %g-%g" % (num, worst, best))
    for key in ("ratingCount", "reviewCount"):
        raw = node.get(key)
        if not _has_value(raw) or _placeholder(raw) is not None:
            continue
        count = _count(raw)
        if count is None:
            problems.append("%s %r is not a whole number" % (key, raw))
        elif count <= 0:
            problems.append("%s is %d" % (key, count))
    return problems


def _check_rating(c: _Ctx, rec: Mapping[str, Any], b: Mapping[str, Any]) -> None:
    if not set(rec["types"]) & c.reg.rating_types:
        return
    problems = _rating_problems(c, rec["node"])
    if problems:
        c.add("SD011", "JSON-LD block %d %s: %s." % (b["index"], _label(rec), "; ".join(problems)), line=b["line"],
              key="rating:b%d:%s" % (b["index"], rec["path"]),
              evidence={"block": b["index"], "path": rec["path"], "problems": problems})


def _price_and_currency(offer: Mapping[str, Any]) -> Tuple[Any, Any]:
    price, currency = offer.get("price"), offer.get("priceCurrency")
    specs = [s for s in _as_list(offer.get("priceSpecification")) if isinstance(s, dict)]
    specs.sort(key=lambda s: 1 if s.get("priceType") else 0)
    for spec in specs:
        price = spec.get("price") if not _has_value(price) else price
        currency = spec.get("priceCurrency") if not _has_value(currency) else currency
    return price, currency


def _check_merchant(c: _Ctx, rec: Mapping[str, Any], b: Mapping[str, Any], index: Mapping[str, Any]) -> None:
    if c.merchant is False or not rec["primary"]:
        return
    if not any(f.get("condition") == "has_offer" and set(rec["types"]) & ft for f, ft in c.reg.features):
        return
    problems: List[str] = []
    for n, offer in enumerate(_plain_offers(rec["node"], index), 1):
        price, currency = _price_and_currency(offer)
        if _placeholder(price) is None:
            amount = _number(price)
            if not _has_value(price):
                problems.append("offer %d has no price" % n)
            elif amount is None:
                problems.append("offer %d price %r is not a plain number" % (n, price))
            elif amount <= 0:
                problems.append("offer %d price %g is not above 0" % (n, amount))
        if _placeholder(currency) is None:
            if not _has_value(currency):
                problems.append("offer %d has no priceCurrency" % n)
            elif not (isinstance(currency, str) and _CURRENCY_RE.fullmatch(currency.strip())):
                problems.append("offer %d priceCurrency %r is not an ISO 4217 code" % (n, currency))
    if problems:
        c.add("SD017", "JSON-LD block %d %s: %s." % (b["index"], _label(rec), "; ".join(problems)), line=b["line"],
              key="merchant:b%d:%s" % (b["index"], rec["path"]), confidence="high" if c.merchant else "medium",
              evidence={"block": b["index"], "path": rec["path"], "problems": problems})


def _breakout_markers(raw: str, parse_failed: bool, closed: bool) -> Tuple[List[str], str]:
    low = raw.lower()
    marks = [m for m in ("</script", "<script", "<!--") if m in low]
    if marks:
        return marks, "high"
    marks = ["<"] if "<" in raw else []
    if parse_failed and closed and any(m.group() == '"' for m in _STRING_OR_QUOTE_RE.finditer(raw)):
        marks.append("block ends inside a JSON string (a </script> in a value may have cut it)")
    return marks, "medium"


def _unsafe_stringify(text: str) -> List[int]:
    """Offsets of application/ld+json occurrences whose tag or expression stringifies without escaping '<'."""
    low = text.lower()
    hits = [m.start() for m in _LDJSON_RE.finditer(text)][:MAX_BLOCKS]
    out: List[int] = []
    for i, pos in enumerate(hits):
        nxt = hits[i + 1] if i + 1 < len(hits) else len(text)
        tag = low.rfind("<script", max(0, pos - 400), pos)
        start = tag if tag >= 0 else max(0, pos - 200)
        close = low.find("</script", pos, nxt)
        end = min(close if close >= 0 else nxt, nxt, pos + 1200)
        window = text[start:end]
        if _STRINGIFY_RE.search(window) and not _ESCAPED_RE.search(window):
            out.append(pos)
    return out


def _signature(entity: Mapping[str, Any]) -> Optional[Tuple[Tuple[str, ...], Optional[str], Optional[str]]]:
    node = entity.get("node") if isinstance(entity.get("node"), dict) else entity
    types = tuple(entity.get("types") or (_types(node) if isinstance(node, dict) else ()))

    def norm(value: Any, url: bool) -> Optional[str]:
        value = next((v for v in _as_list(value) if isinstance(v, str)), None)
        if value is None or not value.strip():
            return None
        return value.strip().lower().rstrip("/") if url else " ".join(value.split()).casefold()

    name, url = norm(node.get("name"), False), norm(node.get("url"), True)
    return (types, name, url) if (types or name or url) else None


def _conflicts(a: Tuple[Tuple[str, ...], Optional[str], Optional[str]],
               b: Tuple[Tuple[str, ...], Optional[str], Optional[str]], reg: _Reg) -> bool:
    if not reg.compatible(set(a[0]), set(b[0])):
        return True
    return any(x is not None and y is not None and x != y for x, y in ((a[1], b[1]), (a[2], b[2])))


def _variant(sig: Tuple[Tuple[str, ...], Optional[str], Optional[str]]) -> Dict[str, Any]:
    return {"types": list(sig[0]), "name": sig[1], "url": sig[2]}


def _id_groups(rows: Sequence[Tuple[str, str, Any]], reg: _Reg) -> Dict[str, List[Tuple[Any, Set[str]]]]:
    """@id -> conflicting variants with the locations (urls or block labels) that declare them."""
    variants: Dict[str, Dict[Any, Set[str]]] = {}
    for eid, where, sig in rows:
        variants.setdefault(eid, {}).setdefault(sig, set()).add(where)
    out: Dict[str, List[Tuple[Any, Set[str]]]] = {}
    for eid in sorted(variants):
        items = sorted(variants[eid].items(), key=lambda kv: repr(kv[0]))[:50]
        bad = {i for i in range(len(items)) for j in range(len(items))
               if i != j and _conflicts(items[i][0], items[j][0], reg)}
        if bad:
            out[eid] = [items[i] for i in sorted(bad)]
    return out


# ----------------------------------------------------------------------------- public entry points

def lint_text(text: str, catalog: Optional[RuleCatalog] = None, *, filename: str = "", url: Optional[str] = None,
              registry: Optional[Mapping[str, Any]] = None, template_mode: Optional[bool] = None,
              markup: Optional[Mapping[str, bool]] = None,
              merchant: Optional[bool] = None) -> Tuple[Dict[str, Any], List[Finding]]:
    """Lint every JSON-LD block in one document.

    `markup` = {"microdata": bool, "rdfa": bool} from an HTML parser (detected from the text when
    None) feeds SD020. `merchant`: None treats a Product with a plain Offer as a merchant-listing
    candidate (medium confidence), True treats every Product as one (profile ecommerce), False
    skips merchant-listing checks. Returns (summary, findings).
    """
    cat = catalog or rulesdb.default_catalog()
    reg = _prepare(registry)
    c = _Ctx(cat, reg, filename, url, merchant)
    blocks = extract_blocks(text, filename=filename, template_mode=template_mode)
    parsed: List[Tuple[Mapping[str, Any], Any, List[Dict[str, Any]]]] = []
    for b in blocks:
        i = b["index"]
        if b["skipped"]:
            c.add("SD019", "JSON-LD block %d contains a template expression and was not validated; check the built "
                  "HTML instead." % i, line=b["line"], key="skip:b%d" % i, evidence={"block": i, "reason": b["skipped"]})
            continue
        data, err, err_line = _parse(b["raw"], MAX_BLOCK_BYTES)
        marks, confidence = _breakout_markers(b["raw"], err is not None, b["closed"])
        if marks:
            c.add("SD012", "JSON-LD block %d contains %s; a value can close the script element." % (i, marks[0]),
                  line=b["line"], key="breakout:b%d" % i, confidence=confidence, evidence={"block": i, "markers": marks})
        if err is not None:
            line = b["content_line"] + err_line - 1 if err_line else b["line"]
            c.add("SD001", "JSON-LD block %d: %s." % (i, err), line=line, key="syntax:b%d" % i,
                  evidence={"block": i, "error": err})
            token = _placeholder(b["raw"])
            if token:
                c.add("SD006", "Malformed JSON-LD block %d also contains a placeholder (%s)." % (i, token),
                      line=b["line"], key="placeholder:b%d" % i, confidence="medium",
                      evidence={"block": i, "tokens": [token]})
            continue
        for rule, kind, path, message in _scan(data)[0]:
            c.add(rule, "JSON-LD block %d %s: %s." % (i, path, message), line=b["line"],
                  key="%s:b%d:%s" % (kind, i, path), evidence={"block": i, "path": path, "kind": kind})
        _check_values(c, data, b)
        parsed.append((b, data, entities(data)))
    index: Dict[str, Dict[str, Any]] = {}
    for _b, _data, recs in parsed:
        for rec in recs:
            if rec["id"] and set(rec["node"]) - _REF_KEYS and len(rec["node"]) > len(index.get(rec["id"], ())):
                index[rec["id"]] = rec["node"]
    rows: List[Tuple[str, str, Any]] = []
    for b, _data, recs in parsed:
        for rec in recs:
            if not _is_schema(rec["context"]):
                continue
            _check_no_rich(c, rec, b, index)
            _check_features(c, rec, b, index)
            _check_self_serving(c, rec, b, index)
            _check_rating(c, rec, b)
            _check_merchant(c, rec, b, index)
            sig = _signature(rec) if rec["id"] else None
            if sig is not None:
                rows.append((rec["id"], "block %d %s" % (b["index"], rec["path"]), sig))
    for eid, variants in _id_groups(rows, reg).items():
        c.add("SD015", "@id %s is used for %d different entities on this page." % (eid, len(variants)),
              line=blocks[0]["line"] if blocks else None, key="idconflict:%s" % eid,
              evidence={"id": eid, "variants": [dict(_variant(s), at=sorted(w)[:5]) for s, w in variants]})
    if filename.lower().endswith(COMPONENT_EXTS) or template_mode:
        lines = _Lines(text)
        for n, pos in enumerate(_unsafe_stringify(text), 1):
            c.add("SD018", "application/ld+json is filled with JSON.stringify without escaping '<'.",
                  line=lines.at(pos), key="stringify:%d" % n, evidence={"occurrence": n})
    if not blocks and not filename.lower().endswith(JSON_EXTS):
        flags = dict(markup) if markup is not None else {"microdata": bool(_MICRODATA_RE.search(text)),
                                                         "rdfa": bool(_RDFA_RE.search(text))}
        if flags.get("microdata") or flags.get("rdfa"):
            kinds = " and ".join(k for k, label in (("Microdata", "microdata"), ("RDFa", "rdfa")) if flags.get(label))
            c.add("SD020", "Page uses %s but no JSON-LD; Google supports all three and recommends JSON-LD." % kinds,
                  line=None, key="format", confidence="medium",
                  evidence={"microdata": bool(flags.get("microdata")), "rdfa": bool(flags.get("rdfa"))})
    all_recs = [rec for _b, _d, recs in parsed for rec in recs]
    summary = {
        "blocks": len(blocks), "parsed": len(parsed), "skipped": sum(1 for b in blocks if b["skipped"]),
        "invalid": len(blocks) - len(parsed) - sum(1 for b in blocks if b["skipped"]),
        "truncated": len(blocks) >= MAX_BLOCKS,
        "types": sorted({t for rec in all_recs for t in rec["types"]}),
        "entities": truncate([{"id": rec["id"], "types": rec["types"], "name": _signature(rec)[1],
                               "url": _signature(rec)[2], "path": rec["path"]}
                              for rec in all_recs if rec["id"] and _signature(rec)][:SUMMARY_ENTITIES]),
    }
    return summary, c.findings


def lint_entities_site(entities_by_url: Mapping[str, Sequence[Mapping[str, Any]]],
                       catalog: Optional[RuleCatalog] = None, *,
                       registry: Optional[Mapping[str, Any]] = None) -> List[Finding]:
    """SD015 across pages: one @id describing conflicting entities on two or more pages.

    Accepts records from `entities()` (with "node") or the compact summary["entities"] rows
    ({id, types, name, url}). Conflict = incompatible @type sets, or different name or url.
    """
    cat = catalog or rulesdb.default_catalog()
    reg = _prepare(registry)
    rows: List[Tuple[str, str, Any]] = []
    for page in sorted(entities_by_url):
        for ent in entities_by_url[page] or ():
            eid, sig = ent.get("id"), _signature(ent)
            if isinstance(eid, str) and eid.strip() and sig is not None:
                rows.append((eid, page, sig))
    out: List[Finding] = []
    for eid, variants in _id_groups(rows, reg).items():
        pages = sorted({p for _s, where in variants for p in where})
        if len(pages) < 2:
            continue
        out.append(make("SD015", "@id %s describes different entities across %d pages." % (eid, len(pages)),
                        catalog=cat, url=pages[0], key="idconflict:%s" % eid, affected=len(pages), sample=pages,
                        evidence={"id": eid, "variants": [dict(_variant(s), pages=len(w)) for s, w in variants]}))
    return out
