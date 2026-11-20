#!/usr/bin/env python3
"""Optional, local prose review aid; Python standard library only.

Usage: python scripts/lint.py [draft.txt | -] --genre email --tone warm
Reads UTF-8 from a file or stdin. Never writes files, sends data, rewrites prose,
scores writing, or predicts authorship. A match is a REVIEW candidate, not an
error: context, evidence and intentional repetition can justify every example.
The small English phrase checks have limited coverage; silence proves nothing.

Default checks are narrow constructions: stock openings and closers, staged
insight, unsupported scope, vague attribution, abstract actors, staged
contrast, an objection nobody raised, an example explained twice, assistant
framing left in a deliverable, a stated knowledge gap, repeated framing,
duplicated sentences, and draft artifacts (open placeholders, citation markup,
tracking parameters, zero-width characters). There is no default vocabulary,
typography or rhythm check; prose_stats.py maps those without findings.

Conventions the user can select: --straight-quotes, --no-em-dash, and
--avoid / --avoid-file for their own list of terms.

Code, quotations, blockquotes, URLs, email addresses, path tokens, HTML
comments, closed YAML front matter and regions between whole-line
<!-- prose:ignore-start --> and <!-- prose:ignore-end --> markers are
protected. --include-quotes includes prose quotations/blockquotes, while code
and technical tokens remain protected. Draft-artifact checks also read
quotations and links, never code. Positions are zero-based Unicode character
offsets, with exclusive end offsets; lines/columns are one-based. CRLF is
preserved. Genre and free-text tone are reported as context, never scored.
Exit: 0 completed; 1 only when --strict finds a selected convention; 2 error.
To compare a revision with its source, use scripts/fidelity_check.py.
"""

import argparse
from bisect import bisect_right
from dataclasses import asdict, dataclass
import json
import re
import sys

GENRES = ("generic", "email", "message", "post", "essay", "docs", "marketing", "fiction")
REVIEW = "REVIEW"


@dataclass(frozen=True)
class Finding:
    severity: str
    rule_id: str
    message: str
    line: int
    column: int
    offset_start: int
    offset_end: int
    snippet: str
    convention: bool = False


def _mask(value):
    # A sentinel prevents a regex from joining prose across an excluded span.
    return "".join(ch if ch in "\r\n" else "\0" for ch in value)


def mask_code(text):
    """Mask code, comments, front matter and ignore regions; keep the length."""
    source = text.splitlines(keepends=True)
    bare = [line.rstrip("\r\n") for line in source]
    skip = set()
    if bare and re.fullmatch(r"---[ \t]*", bare[0]):
        closing = next((i for i in range(1, len(bare))
                        if re.fullmatch(r"(?:---|\.\.\.)[ \t]*", bare[i])), None)
        if closing:  # an unclosed block is prose, not metadata
            skip.update(range(closing + 1))
    opened = None
    for index, line in enumerate(bare):
        if re.fullmatch(r"[ \t]*<!--[ \t]*prose:ignore-start\b.*-->[ \t]*", line):
            opened = index if opened is None else opened
        elif opened is not None and re.fullmatch(r"[ \t]*<!--[ \t]*prose:ignore-end[ \t]*-->[ \t]*", line):
            skip.update(range(opened, index + 1))
            opened = None
    lines, fence = [], None
    prefix = r"^(?: {0,3}>[ \t]?)* {0,3}"
    for index, line in enumerate(source):
        marker = re.match(prefix + r"(`{3,}|~{3,})(.*)", line)
        if index in skip:
            lines.append(_mask(line))
        elif fence:
            lines.append(_mask(line))
            if re.match(prefix + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*\r?\n?$", line):
                fence = None
        elif marker:
            fence = marker.group(1)
            lines.append(_mask(line))
        else:
            lines.append(line)
    scan = "".join(lines)
    scan = re.sub(r"(?<!`)(`+)(?!`)[\s\S]*?(?<!`)\1(?!`)", lambda m: _mask(m[0]), scan)
    return re.sub(r"<!--[\s\S]*?-->", lambda m: _mask(m[0]), scan)


def mask_sources(text, include_quotes=False):
    """Return an equal-length scan surface; never alter the original text."""
    scan = mask_code(text)
    if not include_quotes:
        # Include Markdown lazy continuation lines until an empty line.
        in_block = False
        lines = []
        for line in scan.splitlines(keepends=True):
            if not line.strip():
                in_block = False
            elif re.match(r"^ {0,3}>", line):
                in_block = True
            lines.append(_mask(line) if in_block else line)
        scan = "".join(lines)
        for pattern in (
            r'"(?:[^"\\]|\\.)*"', r"“[^”]*”", r"«[^»]*»", r"‹[^›]*›",
            r"「[^」]*」", r"『[^』]*』", r"„[^“”]*[“”]",
            r"(?<!\w)'(?:[^'\n]|(?<=\w)'(?=\w))*'(?!\w)",
            r"(?<!\w)‘(?:[^’]|(?<=\w)’(?=\w))*’(?!\w)",
        ):
            scan = re.sub(pattern, lambda m: _mask(m[0]), scan)
    # Keep trailing sentence punctuation available for boundary checks.
    def token(match):
        raw = match[0]
        body = raw.rstrip(".,;:!?)]}")
        return _mask(body) + raw[len(body):]

    for pattern in (
        r"\b(?:https?://|www\.)[^\s<>\"]+",
        r"\b[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+\.[\w-]+\b",
        r"(?<!\w)(?:[A-Za-z]:[\\/]|\\\\|\.{0,2}/|~/|[\w.-]+[/\\])[^\s<>\"']+",
    ):
        scan = re.sub(pattern, token, scan)
    return scan


# These are narrow constructions, not a vocabulary blacklist. A match cannot
# determine whether a claim is supported or whether an author intended a device.
PHRASES = (
    ("stock-opening", r"\bI hope this (?:email|message) finds you well\b",
     "Consider opening with the purpose or news if this greeting adds little for the reader."),
    ("stock-opening", r"\bIn (?:today['’]s (?:fast[- ]paced |ever[- ]changing )?world|a world where)\b",
     "Check whether this broad opening can begin with the specific subject instead."),
    ("staged-insight", r"\b(?:Here['’]s what (?:most people miss|nobody tells you|you need to know)|The uncomfortable truth is|"
     r"What if I told you|Here['’]s the thing|Let['’]s (?:dive in|break (?:this|it) down)|Without further ado|"
     r"Let that sink in|Read that again)\b",
     "Check whether the promised revelation earns this setup; the point may stand on its own."),
    ("claim-scope", r"\b(?:the world['’]s (?:best|leading|only)|100% (?:safe|effective|accurate|guaranteed)|guaranteed to (?:work|succeed)|this changes everything)\b",
     "Verify the evidence and scope of this claim; this scan cannot judge its support."),
    ("staged-contrast", r"\b(?:This|That|It) (?:does not|doesn['’]t) mean\b[^.!?\n]{1,120}[.!?]\s+It means\b",
     "Check whether a reader would hold the view being denied; if not, state the point directly."),
    ("staged-contrast", r"(?:(?<=[.!?]\s)|(?<=^)|(?<=\n))Not (?:just |only |merely )?(?:a|an|the|about|because) [^.!?\n]{1,40}[.!?]"
     r"\s+(?:A|An|The|About|Because|It['’]s|That['’]s|They['’]re)(?: [^\s.!?]+){1,5}[.!?]",
     "Check whether this fragment contrast names a real difference; a plain sentence may carry it."),
    ("unprompted-rebuttal", r"\b(?:I(?:['’]m| am) not (?:saying|arguing|suggesting)|Don['’]t get me wrong|This is not to say|"
     r"A tempting approach would be|One might be tempted to|It would be easy to (?:just )?(?:say|assume|think|dismiss))\b",
     "Check whether anyone raised this objection; keep it when the text attributes or answers a real one."),
    ("explained-example", r"\b(?:This (?:shows|demonstrates|illustrates) (?:the importance of|just how|why this matters)|"
     r"The message (?:was|is) clear:|It was a lesson in)\b",
     "Check whether the example already made this point before the sentence names it."),
    ("vague-attribution",
     r"\b(?:(?:studies|research) (?:show|shows|suggest|suggests|indicate|indicates|prove|proves)|"
     r"experts? (?:say|agree|believe|argue|warn)|it is widely (?:believed|accepted|known)|"
     r"according to (?:research|experts|studies|reports))\b",
     "Check whether a named source supports this; name it, keep its uncertainty, ask for it, or cut the claim."),
    ("abstract-actor",
     r"\bthe (?:data|numbers|market|industry|culture|algorithm) (?:tells|told|wants|decides|decided|speaks|knows)\b",
     "Check who or what actually acts; name the person, team, system, or measurement when known."),
    ("assistant-residue",
     r"\b(?:As an AI(?: language model| assistant)?|As a large language model|"
     r"Here(?:['’]s| is) (?:a|the|your) (?:revised|rewritten|polished|improved|updated) (?:version|draft|text)|"
     r"I hope this helps|Great question|Excellent question|You(?:['’]re| are) absolutely right|"
     r"Would you like me to|Should I continue|Let me know if you(?:['’]d| would) like me to|"
     r"I (?:don['’]t|do not) have access to real-time)\b|"
     r"(?:(?<=^)|(?<=\n)|(?<=[.!?]\s))(?:Certainly|Of course|Absolutely)!",
     "Check whether assistant framing leaked into the deliverable; it may fit a chat reply but rarely a finished piece."),
    ("knowledge-gap", r"\b(?:(?:as of|up to) my (?:last |latest )?(?:knowledge|training)(?: data)? (?:cutoff|cut-off|update)|"
     r"while specific details (?:are|remain) (?:limited|scarce|unclear)|based on (?:the )?available information|"
     r"(?:is|are|remains?) not (?:publicly available|widely documented)|it is believed that)\b",
     "Check whether this covers a gap with a guess; say what the source does not show, or cut the sentence."),
)

CITATION_NEARBY = re.compile(r"\0|\((?:[^()]*\b(?:19|20)\d{2}\b[^()]*)\)|\[\d+\]")

# Read on a surface where only code is masked, so a quotation or link still counts.
ARTIFACTS = (
    ("open-placeholder", r"\[(?:Your|Insert|Recipient|Company|Client|First|Last|Full)\b[^\]\n]{0,60}\](?![(\[:])|"
     r"\[(?:Name|Date|Title|Link|URL|TBD|TODO)\](?![(\[:])|\[TK(?::[^\]\n]*)?\]",
     "An open placeholder remains; fill it from a source or tell the reader what is missing."),
    ("tool-artifact", r"contentReference\[oaicite:[^\]\n]*\](?:\{[^}\n]*\})?|\[oaicite:[^\]\n]*\]|\boai_citation\b|"
     r"\bturn\d+(?:search|view|news|file)\d+\b|\[attached_file:\d+\]|"
     r"[?&]utm_source=(?:chatgpt|openai|copilot|claude|grok|gemini|perplexity)(?:\.com|\.ai)?\b",
     "This looks like markup or a tracking parameter left by a tool; remove it or restore the real citation."),
    ("tool-artifact", "[​‌⁠]|(?<!^)﻿",
     "An invisible zero-width character is present; check that it is intended."),
)

CONTRAST_FRAME = re.compile(
    r"\b(?:(?:is|are|was|were|does|do|did)(?:n['’]t| not)|not) (?:just|only|merely|simply) \w+|"
    r"\bit['’]s not\b[^.!?\n]{1,60}[,;.]\s*it['’]s\b|\bnot because\b[^.!?\n]{1,80}\bbut because\b", re.I)

def term_pattern(term):
    """A whole-word, case-insensitive pattern; single words match common endings."""
    words = term.split()
    if len(words) == 1 and term.isalpha() and len(term) > 3:
        if term.endswith("e"):
            body = re.escape(term[:-1]) + r"(?:e|es|ed|ing|ely|er|ers)"
        else:
            body = re.escape(term) + r"(?:s|es|d|ed|ing|ly)?"
    else:
        body = r"[\s-]+".join(re.escape(word).replace("'", "['’]") for word in re.split(r"[\s-]+", term))
    return re.compile(r"(?<![\w-])" + body + r"(?![\w-])", re.I)


def _sentences(scan, start, end):
    """Conservative sentence approximation: (offset, text) pairs inside a span."""
    for match in re.finditer(r"[^.!?\n]+(?:[.!?]+(?=\s|$)|(?=\n|$))", scan[start:end]):
        body = match[0].strip()
        if body:
            yield start + match.start() + len(match[0]) - len(match[0].lstrip()), body


def _paragraphs(scan):
    """(offset, text, is_prose) for blocks separated by blank lines."""
    for match in re.finditer(r"[^\r\n]+(?:\r?\n[^\r\n]+)*", scan):
        body = match[0]
        if body.replace("\0", "").strip():
            prose = not re.match(r"\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|\||>)", body) and "\0\0\0" not in body[:3]
            yield match.start(), body, prose


def check(text, *, genre="generic", tone="", include_quotes=False,
          straight_quotes=False, no_em_dash=False, avoid=()):
    """Return advisory findings only. Genre/tone do not change thresholds."""
    if genre not in GENRES:
        raise ValueError("unknown genre: " + genre)
    scan = mask_sources(text, include_quotes)
    findings = []
    line_starts = [0] + [match.end() for match in re.finditer(r"\r\n|[\r\n]", text)]

    def add(start, end, rule_id, message, convention=False, surface=None):
        if "\0" in (surface or scan)[start:end]:
            return
        line = bisect_right(line_starts, start)
        findings.append(Finding(REVIEW, rule_id, message, line,
                                start - line_starts[line - 1] + 1,
                                start, end, text[start:end], convention))

    for rule_id, pattern, message in PHRASES:
        for match in re.finditer(pattern, scan, re.I):
            if rule_id == "vague-attribution":
                # A citation, link, or quotation in the same sentence may name the source.
                left = max(scan.rfind(ch, 0, match.start()) for ch in ".!?\n") + 1
                rights = [i for i in (scan.find(ch, match.end()) for ch in ".!?\n") if i >= 0]
                if CITATION_NEARBY.search(scan[left:min(rights) if rights else len(scan)]):
                    continue
            add(match.start(), match.end(), rule_id, message)

    code_only = mask_code(text)
    for rule_id, pattern, message in ARTIFACTS:
        for match in re.finditer(pattern, code_only):
            add(match.start(), match.end(), rule_id, message, surface=code_only)

    closer = re.search(r"\b(?:Only time will tell|The possibilities are endless|This is just the beginning|"
                       r"The future looks bright|Exciting times (?:lie |are )?ahead|"
                       r"(?:It|This) is a step in the right direction)[.!]?\s*\Z", scan, re.I)
    if closer:
        end = closer.start() + len(closer[0].rstrip())
        add(closer.start(), end, "stock-closer",
            "Check whether this final sentence gives the reader a useful ending.")

    framing = r"\b(?:It(?: is|['’]s) important to note that|The key takeaway is|What this means is)\b"
    seen = set()
    for match in re.finditer(framing, scan, re.I):
        # Only sentence/paragraph openings; one occurrence alone is not a finding.
        before = scan[:match.start()]
        if before.strip() and before.rstrip()[-1] not in ".!?" and before.rsplit("\n", 1)[-1].strip():
            continue
        key = re.sub(r"\s+", " ", match[0].casefold())
        if key in seen:
            add(match.start(), match.end(), "repeated-framing",
                "This sentence opening repeats; check whether the framing is doing useful work.")
        seen.add(key)

    previous = None
    # Deliberately conservative sentence approximation; no cadence measurements.
    for start, body in _sentences(scan, 0, len(scan)):
        if "\0" in body:
            previous = None
            continue
        key = re.sub(r"\s+", " ", body.casefold())
        if len(re.findall(r"\b\w+\b", body)) >= 4 and key == previous:
            add(start, start + len(body), "adjacent-duplicate",
                "This sentence repeats the preceding sentence; check whether that is intentional.")
        previous = key

    paragraphs = list(_paragraphs(scan))
    for offset, body, _ in paragraphs:
        # One contrast frame can correct a real misreading; a second in the same
        # paragraph is a reason to look.
        frames = list(CONTRAST_FRAME.finditer(body))
        for match in frames[1:]:
            add(offset + match.start(), offset + match.end(), "repeated-contrast",
                "A second contrast frame in one paragraph; check that each corrects something a reader might believe.")
    for match in re.finditer(r"(?im)^[ \t]*[-*+][ \t]+\*\*([^*:\n]{3,40}):?\*\*:?[ \t]+(?:the[ \t]+)?\1\b", scan):
        add(match.start(1), match.end(), "label-echo",
            "The label is repeated as the first words of its item; one of them is probably enough.")

    for term in avoid:
        for match in term_pattern(term).finditer(scan):
            add(match.start(), match.end(), "avoid-term",
                "Selected convention: this writer avoids the term; keep it only where it is the exact word.", True)

    for enabled, pattern, rule_id, message in (
        (straight_quotes, r"[‘’“”]", "straight-quotes", "Selected convention: use straight quotation marks/apostrophes in authored prose."),
        (no_em_dash, "—", "no-em-dash", "Selected convention: avoid em dashes in authored prose."),
    ):
        if enabled:
            for match in re.finditer(pattern, scan):
                add(match.start(), match.end(), rule_id, message, True)
    return sorted(findings, key=lambda finding: (finding.offset_start, finding.rule_id))


def read_terms(values, path):
    terms = [part.strip() for value in values for part in value.split(",")]
    if path:
        with open(path, encoding="utf-8") as source:
            terms += [line.split("#", 1)[0].strip() for line in source]
    return tuple(dict.fromkeys(term for term in terms if term))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", nargs="?", help="UTF-8 file; default or '-' reads stdin")
    parser.add_argument("--genre", choices=GENRES, default="generic", help="reader-supplied context")
    parser.add_argument("--tone", default="", help="free-text context; never scored")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--json", action="store_true", help="emit structured findings and context")
    mode.add_argument("--detect", action="store_true", help="alias for the default advisory text report; no authorship detection")
    parser.add_argument("--include-quotes", action="store_true", help="also review prose quotations and blockquotes")
    parser.add_argument("--straight-quotes", action="store_true", help="select a straight-quotes convention")
    parser.add_argument("--no-em-dash", action="store_true", help="select a no-em-dash convention")
    parser.add_argument("--avoid", action="append", default=[], metavar="TERMS",
                        help="comma-separated words or phrases this writer avoids; repeatable")
    parser.add_argument("--avoid-file", metavar="PATH", help="UTF-8 file with one avoided term per line; # starts a comment")
    parser.add_argument("--strict", action="store_true", help="exit 1 only for findings under a selected convention")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        avoid = read_terms(args.avoid, args.avoid_file)
        if args.path and args.path != "-":
            with open(args.path, encoding="utf-8", newline="") as source:
                text = source.read()
        else:
            text = sys.stdin.buffer.read().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        parser.exit(2, "lint.py: unable to read UTF-8 input: " + str(exc) + "\n")
    findings = check(text, genre=args.genre, tone=args.tone,
                     include_quotes=args.include_quotes,
                     straight_quotes=args.straight_quotes, no_em_dash=args.no_em_dash,
                     avoid=avoid)
    context = {"genre": args.genre, "tone": args.tone,
               "include_quotes": args.include_quotes,
               "conventions": [name for name, selected in
                               (("straight-quotes", args.straight_quotes), ("no-em-dash", args.no_em_dash),
                                ("avoid-term", bool(avoid))) if selected]}
    if args.json:
        print(json.dumps({"schema_version": 1, "context": context,
                          "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=2))
    else:
        print("Advisory review; genre=" + args.genre + "; tone=" + (args.tone or "unspecified"))
        for finding in findings:
            print(f"REVIEW {finding.line}:{finding.column} [{finding.rule_id}] {finding.snippet!r}: {finding.message}")
        if not findings:
            print("No candidates matched these limited checks.")
    return int(args.strict and any(f.convention for f in findings))


if __name__ == "__main__":
    sys.exit(main())
