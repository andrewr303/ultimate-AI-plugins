"""Byte-exact Markdown frontmatter and section splitting for surgical rewrites (WP05).

Rules (adapted from eGEOagents ``egeo/sections.py``, MIT):

* A heading is an ATX line ``^(#{1,6})[ \\t]+text`` outside fenced code. ``#hashtag`` (no space) and
  setext underlines (``===`` / ``---``) are not headings. A closing ``#`` run is dropped only when a
  space precedes it, so ``# C#`` keeps its text.
* A fence opens with a line whose left-stripped form starts with three or more backticks or tildes
  and closes with a line holding only the same character repeated at least as many times. A shorter
  fence inside a longer one does not close it; an unclosed fence runs to the end.
* Lines end at ``\\n``, ``\\r\\n`` or ``\\r`` only (never at U+2028 or form feeds).
* Text before the first heading is a preamble section (level 0, heading "") when it is non-empty,
  even if it is only whitespace. Ids are ``s00``, ``s01``, ... in document order.
* ``join_sections(split_sections(body)) == body`` for every input, byte for byte.

Only the standard library is used; nothing here edits files.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Sequence, Tuple

_LINE = re.compile(r"[^\r\n]*(?:\r\n|\n|\r)|[^\r\n]+\Z")
_HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})")
_FENCE_CLOSE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*$")
_FRONTMATTER = re.compile(r"\A(\ufeff?(---|\+\+\+)[ \t]*(?:\r\n|\n|\r)(?:.*?(?:\r\n|\n|\r))??\2[ \t]*(?:\r\n|\n|\r|\Z))",
                          re.S)
_WORD = re.compile(r"\w+")


@dataclass(frozen=True)
class Section:
    """One section: its full text starts with the heading line (empty heading for the preamble)."""
    id: str
    heading: str
    level: int
    text: str
    word_count: int


def lines(text: str) -> List[str]:
    """Lines with their line endings kept; ``"".join(lines(t)) == t``."""
    return _LINE.findall(text)


def heading_of(line: str) -> Tuple[int, str]:
    """(level, heading text) for an ATX heading line, else (0, "")."""
    match = _HEADING.match(line.rstrip("\r\n"))
    if not match or not match.group(2).strip():
        return 0, ""
    return len(match.group(1)), match.group(2).strip()


def fence_marker(line: str) -> str:
    """The fence run that opens a code block on this line, or ""."""
    match = _FENCE.match(line)
    return match.group(1) if match else ""


def closes_fence(line: str, marker: str) -> bool:
    """True when `line` closes a block opened with `marker`."""
    match = _FENCE_CLOSE.match(line.rstrip("\r\n"))
    return bool(match) and match.group(1)[0] == marker[0] and len(match.group(1)) >= len(marker)


def split_frontmatter(text: str) -> Tuple[str, str]:
    """(raw_frontmatter, body) with ``raw + body == text``; YAML ``---`` or TOML ``+++`` delimiters."""
    match = _FRONTMATTER.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end(1):]


def _section(index: int, heading: str, level: int, text: str) -> Section:
    return Section("s%02d" % index, heading, level, text, len(_WORD.findall(text)))


def split_sections(body: str) -> List[Section]:
    """Split a Markdown body at ATX headings outside fenced code (lossless; see module doc)."""
    out: List[Section] = []
    chunk: List[str] = []
    heading, level = "", 0
    marker = ""
    for line in lines(body):
        if marker:
            if closes_fence(line, marker):
                marker = ""
            chunk.append(line)
            continue
        marker = fence_marker(line)
        new_level, new_heading = (0, "") if marker else heading_of(line)
        if new_level:
            if chunk:
                out.append(_section(len(out), heading, level, "".join(chunk)))
            chunk, heading, level = [], new_heading, new_level
        chunk.append(line)
    if chunk:
        out.append(_section(len(out), heading, level, "".join(chunk)))
    return out


def join_sections(sections: Sequence[Section]) -> str:
    """Concatenate section texts (inverse of split_sections)."""
    return "".join(s.text for s in sections)


def get_section(sections: Sequence[Section], sid: str) -> Section:
    """The section with id `sid`; KeyError when unknown."""
    for section in sections:
        if section.id == sid:
            return section
    raise KeyError("unknown section id: %s" % sid)


def replace_section(sections: Sequence[Section], sid: str, new_text: str) -> List[Section]:
    """New list with section `sid` replaced by `new_text` (id kept); KeyError on an unknown id."""
    target = get_section(sections, sid)
    first = lines(new_text)[:1]
    level, heading = heading_of(first[0]) if first else (0, "")
    if not level:
        level, heading = target.level, target.heading
    new = replace(target, heading=heading, level=level, text=new_text, word_count=len(_WORD.findall(new_text)))
    return [new if s.id == sid else s for s in sections]


def section_table(sections: Sequence[Section], *, first_line: int = 1) -> List[Dict[str, Any]]:
    """Rows for listing: id, heading, level, word_count, start_line (1-based, offset by `first_line`)."""
    rows: List[Dict[str, Any]] = []
    line_no = first_line
    for s in sections:
        rows.append({"id": s.id, "heading": s.heading, "level": s.level, "word_count": s.word_count,
                     "start_line": line_no})
        line_no += len(lines(s.text))
    return rows


def clean_rewrite(original: str, rewritten: str) -> str:
    """Tidy an agent's rewrite of one section before it is joined back.

    Strips surrounding whitespace, drops one outer code fence wrapped around the whole answer
    (only when the original section is not itself a fenced block), then restores the original's
    leading and trailing whitespace so joins stay byte-exact.
    """
    body = rewritten.strip()
    parts = lines(body)
    wrapped = (len(parts) >= 2 and fence_marker(parts[0]) and closes_fence(parts[-1], fence_marker(parts[0]))
               and not fence_marker(original.lstrip()))
    if wrapped:
        body = "".join(parts[1:-1]).strip()
    stripped = original.strip()
    if not stripped:
        return original
    lead = original[: len(original) - len(original.lstrip())]
    trail = original[len(original.rstrip()):]
    return lead + body + trail


def unified(a: str, b: str, name: str) -> str:
    """Unified diff of `a` -> `b` labelled ``a/<name>`` and ``b/<name>`` ("" when equal)."""
    out: List[str] = []
    for line in difflib.unified_diff(lines(a), lines(b), fromfile="a/" + name, tofile="b/" + name):
        if line.endswith(("\n", "\r")):
            out.append(line)
        else:
            out.append(line + "\n\\ No newline at end of file\n")
    return "".join(out)
