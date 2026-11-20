"""llms.txt parsing, validation and drafting per the llmstxt.org v2 format (WP03).

llms.txt is optional. It can help agents and developer tools that read it; Google Search ignores it
(it neither helps nor hurts), and no AI search vendor page checked on 2026-11-01 says its crawlers read
it. Structure: optional BOM, an H1 (the only required element), an optional blockquote summary, optional
detail text, H2 sections of ``- [name](url): notes`` link lists, and an optional ``## Optional`` section.
The drafter never invents descriptions, notes, contact data or facts.
"""
from __future__ import annotations

import re
import urllib.parse
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from .findings import Finding, make
from .rulesdb import RuleCatalog, default_catalog

_LINES = re.compile(r"\r\n|\r|\n")
_HEADING = re.compile(r"^(#{1,6})(?:[ \t]+(.*?))?[ \t]*$")
_FENCE = re.compile(r"^(`{3,}|~{3,})")
_ITEM = re.compile(r"^[-*+][ \t]+(.*)$")
_LINK = re.compile(r"^\[((?:\\.|[^\]\\])*)\]\(\s*(<[^<>]*>|[^()\s]*)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
                   r"[ \t]*(?::[ \t]*(.*))?$")
_UNESCAPE = re.compile(r"\\([\\\[\]])")


def looks_like_html(text: str) -> bool:
    """True when the text starts like an HTML document (a soft 404 served instead of the file)."""
    head = text.lstrip("\ufeff \t\r\n")[:100].lower()
    return head.startswith(("<!doctype", "<html", "<head", "<body"))


def _heading(line: str) -> Optional[tuple]:
    if len(line) - len(line.lstrip(" ")) > 3:
        return None
    m = _HEADING.match(line.strip())
    if not m:
        return None
    text = re.sub(r"[ \t]+#+$", "", m.group(2) or "").strip()
    return len(m.group(1)), "" if set(text) <= {"#"} else text


def parse_llms(text: str) -> Dict[str, Any]:
    """{h1, h1_line, summary, details, sections: [{title, line, links: [{title, url, notes, line}], malformed, prose}],
    has_optional, is_html, errors, notes}. Fenced code is skipped; errors are structural (AGENT002)."""
    text = text[1:] if text.startswith("\ufeff") else text
    out: Dict[str, Any] = {"h1": None, "h1_line": None, "summary": None, "details": "", "sections": [],
                           "has_optional": False, "is_html": looks_like_html(text), "errors": [], "notes": []}
    if out["is_html"]:
        out["errors"].append("content looks like an HTML page, not Markdown (soft 404?)")
    fence: Optional[str] = None
    first: Optional[int] = None
    section: Optional[Dict[str, Any]] = None
    details: List[str] = []
    quote: List[str] = []
    state = "start"
    for no, line in enumerate(_LINES.split(text), 1):
        stripped = line.strip()
        fm = _FENCE.match(line.lstrip(" ")) if len(line) - len(line.lstrip(" ")) <= 3 else None
        if fence is not None:
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= len(fence) and \
                    stripped.strip(fence[0]) == "":
                fence = None
            continue
        if not stripped:
            continue
        first = first or no
        if fm:
            fence = fm.group(1)
            if section is None:
                details.append(stripped)
                state = "details"
            continue
        head = _heading(line)
        if head and head[0] == 1:
            if out["h1"] is None:
                out["h1"], out["h1_line"], state = head[1], no, "after_h1"
                if first != no:
                    out["errors"].append("line %d: content before the H1 (the H1 must come first)" % first)
                if not head[1]:
                    out["errors"].append("line %d: the H1 is empty" % no)
            else:
                out["errors"].append("line %d: more than one H1" % no)
            continue
        if head and head[0] == 2:
            section = {"title": head[1], "line": no, "links": [], "malformed": [], "prose": 0}
            out["sections"].append(section)
            out["has_optional"] = out["has_optional"] or head[1].lower() == "optional"
            state = "sections"
            continue
        if state in ("after_h1", "summary") and stripped.startswith(">"):
            quote.append(stripped.lstrip(">").strip())
            state = "summary"
            continue
        if section is None:
            details.append(stripped)
            state = "details"
            continue
        im = _ITEM.match(stripped)
        lm = _LINK.match(im.group(1).strip()) if im else None
        if lm:
            section["links"].append({"title": _UNESCAPE.sub(r"\1", lm.group(1)), "url": lm.group(2).strip("<>"),
                                     "notes": (lm.group(3) or "").strip() or None, "line": no})
        elif im:
            section["malformed"].append({"text": im.group(1)[:200], "line": no})
        else:
            section["prose"] += 1
    if out["h1"] is None:
        out["errors"].append("missing H1 title (the only required element)")
    out["summary"] = " ".join(x for x in quote if x) or None
    out["details"] = "\n".join(details)
    if out["h1"] is not None and out["summary"] is None:
        out["notes"].append("no blockquote summary after the H1 (recommended)")
    if not out["sections"]:
        out["notes"].append("no H2 sections with link lists")
    for s in out["sections"]:
        if not s["links"]:
            out["notes"].append("line %d: section %r has no links" % (s["line"], s["title"][:60]))
    if fence is not None:
        out["notes"].append("unclosed code fence")
    return out


def _norm(url: str) -> Optional[str]:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
        return None
    host = parts.hostname.lower()
    port = parts.port if parts.port not in (None, 80 if parts.scheme.lower() == "http" else 443) else None
    path = parts.path or "/"
    path = path.rstrip("/") or "/"
    return "%s://%s%s%s%s" % (parts.scheme.lower(), host, ":%d" % port if port else "", path,
                             "?" + parts.query if parts.query else "")


def _mirror_targets(url: str) -> List[str]:
    parts = urllib.parse.urlsplit(url)
    path = parts.path
    if path.endswith("/index.html.md") or path.endswith("/index.md"):
        bases = [path.rsplit("/", 1)[0] + "/"]
    elif path.endswith(".html.md"):
        bases = [path[:-3]]
    elif path.endswith(".md"):
        bases = [path[:-3], path[:-3] + ".html", path[:-3] + "/index.html"]
    else:
        return []
    return [urllib.parse.urlunsplit((parts.scheme, parts.netloc, b, parts.query, "")) for b in bases]


def _link_problem(url: str, base_host: Optional[str], site: Optional[Set[str]]) -> Optional[str]:
    if not url:
        return "empty URL"
    if any(c.isspace() for c in url):
        return "URL contains whitespace"
    parts = urllib.parse.urlsplit(url)
    if not parts.scheme and not parts.netloc:
        return "relative URL (use an absolute URL)"
    if parts.scheme.lower() not in ("http", "https"):
        return "non-http(s) URL"
    if not parts.hostname:
        return "malformed URL"
    if site is not None and base_host and parts.hostname.lower() == base_host:
        keys = [_norm(url)] + [_norm(u) for u in _mirror_targets(url)]
        if not any(k in site for k in keys if k):
            return "not found in the site"
    return None


def check_llms(parsed: Optional[Dict[str, Any]], catalog: Optional[RuleCatalog] = None, *,
               base_url: Optional[str] = None, site_urls: Optional[Set[str]] = None, present: bool = True,
               full_present: bool = False, file: Optional[str] = None, url: Optional[str] = None) -> List[Finding]:
    """AGENT001 (absent), AGENT002 (structure), AGENT003 (links), AGENT009 (llms-full.txt present).

    `site_urls` are the site's page (and file) URLs; a `.md` link also passes when its HTML page exists.
    """
    cat = catalog or default_catalog()
    loc = {"file": file if (file or url) else "llms.txt", "url": url}
    out: List[Finding] = []
    if not present or parsed is None:
        out.append(make("AGENT001", "No llms.txt found. It is optional: some agents and developer tools read it, "
                        "while Google Search ignores it and no AI search vendor documents using it (as of "
                        "2026-11-01).", catalog=cat, key="missing", **loc))
    else:
        errors = parsed.get("errors") or []
        if errors:
            at = re.match(r"line (\d+):", errors[0])
            out.append(make("AGENT002", "llms.txt structure is invalid: %s%s." % (
                errors[0], " (+%d more)" % (len(errors) - 1) if len(errors) > 1 else ""), catalog=cat,
                key="structure", line=int(at.group(1)) if at else None,
                evidence={"errors": errors, "notes": parsed.get("notes") or []}, **loc))
        base_host = (urllib.parse.urlsplit(base_url).hostname or "").lower() if base_url else None
        site = {k for k in (_norm(u) for u in site_urls) if k} if site_urls is not None else None
        problems = []
        for s in parsed.get("sections") or []:
            problems += [{"line": m["line"], "url": m["text"][:120], "problem": "list item is not a Markdown link"}
                         for m in s.get("malformed") or []]
            for link in s.get("links") or []:
                why = _link_problem(link["url"], base_host, site)
                if why:
                    problems.append({"line": link["line"], "url": link["url"][:200], "problem": why})
        problems.sort(key=lambda p: p["line"])
        if problems:
            first = problems[0]
            out.append(make("AGENT003", "%d llms.txt link(s) are relative, malformed or missing from the site (first "
                            "at line %d: %s)." % (len(problems), first["line"], first["problem"]), catalog=cat,
                            key="links", line=first["line"], evidence={"links": problems}, **loc))
    if full_present:
        sibling = (lambda p: p.rsplit("/", 1)[0] + "/llms-full.txt" if "/" in p else "llms-full.txt")
        out.append(make("AGENT009", "llms-full.txt is present. It is a community convention outside the llms.txt "
                        "spec; keep it only if it is generated and maintained.", catalog=cat, key="llms-full",
                        file=sibling(loc["file"]) if loc["file"] else None,
                        url=sibling(url) if url else None))
    return out


def _one_line(value: Any) -> str:
    return " ".join(str(value or "").split())


def _escape(label: str) -> str:
    return label.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _url(url: str) -> str:
    for a, b in ((" ", "%20"), ("(", "%28"), (")", "%29"), ("<", "%3C"), (">", "%3E")):
        url = url.replace(a, b)
    return url


def _section_title(path: str) -> str:
    seg = urllib.parse.unquote(path.strip("/").split("/")[0]) if path.strip("/") else ""
    if not seg or ("." in seg and "/" not in path.strip("/")):
        return "Pages"
    title = _one_line(seg.replace("-", " ").replace("_", " "))
    title = title[:1].upper() + title[1:]
    return title + " pages" if title.lower() == "optional" else title


def _optional(url: str, path: str, prefixes: Iterable[str]) -> bool:
    for p in prefixes:
        p = str(p).strip()
        if p and (url.startswith(p) if "://" in p else path.startswith(p if p.startswith("/") else "/" + p)):
            return True
    return False


def _rank(page: Dict[str, Any]) -> tuple:
    # Duplicate URLs: keep the most complete record, independent of input order.
    title, note, sec = (_one_line(page.get(k)) for k in ("title", "description", "section"))
    return (not title, not note, title, note, sec)


def draft_llms(pages: List[Dict[str, str]], *, title: str, summary: Optional[str] = None,
               optional_urls: Sequence[str] = (), max_entries: int = 200) -> str:
    """Deterministic llms.txt draft from page records {url, title, description, section, noindex?}.

    Labels come from page titles (or the URL path), notes only from existing descriptions; `\\`, `[` and `]`
    are escaped. Sections use `section` or the first path segment; URLs matching an `optional_urls` prefix
    (path or absolute URL) go to `## Optional`. Pages marked noindex are skipped; for a repeated URL the most
    complete record wins. Raises ValueError without a title.
    """
    head = _one_line(title)
    if not head:
        raise ValueError("title is required")
    lines = ["# " + head, ""]
    if _one_line(summary):
        lines += ["> " + _one_line(summary), ""]
    unique: Dict[str, Dict[str, str]] = {}
    for page in pages:
        u = str(page.get("url") or "").strip()
        if u and not page.get("noindex") and (u not in unique or _rank(page) < _rank(unique[u])):
            unique[u] = page
    groups: Dict[str, List[str]] = {}
    optional: List[str] = []
    for u in sorted(unique)[:max(0, int(max_entries))]:
        page, path = unique[u], urllib.parse.urlsplit(u).path or "/"
        label = _escape(_one_line(page.get("title"))) or _escape(path)
        note = _one_line(page.get("description"))
        item = "- [%s](%s)%s" % (label, _url(u), ": " + note if note else "")
        if _optional(u, path, optional_urls):
            optional.append(item)
        else:
            sec = _one_line(page.get("section")) or _section_title(path)
            sec = sec + " pages" if sec.lower() == "optional" else sec
            groups.setdefault(sec, []).append(item)
    for sec in sorted(groups, key=lambda s: (s != "Pages", s.lower(), s)):
        lines += ["## " + sec, ""] + groups[sec] + [""]
    if optional:
        lines += ["## Optional", ""] + optional + [""]
    return "\n".join(lines).rstrip("\n") + "\n"
