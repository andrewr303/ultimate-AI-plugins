#!/usr/bin/env python3
"""Mechanical pre-send checks for proposals, screening answers, and client messages.

Standard library only. A clean scan does not prove the writing is good; it only
catches the mistakes a machine can see: contact details and off-platform asks,
unapproved links, typography, I-led openings, watchlist words, unresolved
placeholders, client keyword instructions, and length.

Exit codes: 0 no errors, 1 at least one ERROR, 2 usage problem.

Examples
--------
python proposal_lint.py cover.txt --kind cover-letter
python proposal_lint.py cover.txt --kind cover-letter --start-with spreadsheet --final
python proposal_lint.py reply.txt --kind message --platform-contract-active
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass

KINDS = {
    # kind: (target_min_words, target_max_words, hard_max_chars)
    "cover-letter": (150, 250, 5000),
    "answer": (40, 120, None),
    "message": (None, None, None),
    "outreach": (50, 150, None),
    "profile-overview": (None, None, 5000),
}

# Contact detection. ERROR-shaped patterns are graded at the contact level (ERROR
# before a contract); REVIEW-shaped ones are ambiguous (often technology) and are
# graded REVIEW (INFO off-marketplace).
EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
OBFUSCATED_EMAIL = [
    re.compile(r"\b[\w.+-]+\s*[\[({]\s*at\s*[\])}]\s*[\w-]+(?:\s*[\[({]\s*dot\s*[\])}]\s*[\w-]+|\.[\w-]+)+", re.I),
    re.compile(r"\b[\w.+-]+\s+at\s+[\w-]+(?:\s+dot\s+[A-Za-z]{2,})+\b", re.I),
]
PHONE_FORMATTED = re.compile(
    r"(?<![\w.+])(?:\+?1[\s.-]?)?(?:\(\d{3}\)\s?|\d{3}[\s.-])\d{3}[\s.-]\d{4}(?!\d)")
PHONE_INTERNATIONAL = re.compile(r"(?<![\w+])\+\d{1,3}[\s.-]?\(?\d{1,4}\)?(?:[\s.-]\d{2,4}){2,}(?!\d)")
PHONE_BARE = re.compile(r"(?<![\w.@/+-])\d{10}(?![\w@]|\.\d)")
PHONE_SEVEN = re.compile(r"(?<![\w.@/$+-])\d{3}-\d{4}(?![\w-])")
PHONE = PHONE_FORMATTED  # backwards-compatible name
LINK = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+"
                  r"|(?<![@\w./-])[a-z0-9][\w-]*(?:\.[\w-]+)*\.[a-z]{2,}/[^\s<>\"')\]]*", re.I)
BARE_DOMAIN = re.compile(r"(?<![@\w./-])[a-z0-9][\w-]*(?:\.[\w-]+)*\.(?:com|io|dev|ai|net|org|co|app|me|xyz|sh|"
                         r"land|us|gg|so|tech|ly|to|cc|link|site|page)(?![\w/@-])", re.I)
URL = LINK  # backwards-compatible name
PRODUCT_NAMES = {
    "next.js", "node.js", "vue.js", "nuxt.js", "express.js", "trigger.dev", "socket.io", "three.js", "d3.js",
    "chart.js", "nest.js", "deno.land", "bun.sh", "asp.net",
}
CONTACT_PHRASES = re.compile(
    r"\b(?:email me|e-mail me|text me|(?:shoot|send|drop) me a text|call me at|call me on|my number|"
    r"my (?:phone|cell|mobile)(?: number)?|my email|my e-mail|reach me at|reach me on|message me on|"
    r"contact me (?:at|on|via)|dm me|add me on|pay me directly|pay (?:you |me )?outside|pay directly|"
    r"outside (?:of )?upwork|off[- ]platform)\b", re.I)
CHANNEL_WORDS = (r"discord|telegram|slack|paypal|venmo|crypto(?:currency)?|skype|whats\s?app|signal|zoom|"
                 r"(?:microsoft |ms )?teams|facetime|google meet|linkedin|instagram|insta|twitter|protonmail|icloud")
CHANNEL_IN_CONTACT = re.compile(
    rf"\b(?:(?:message|ping|call|text|reach|contact|find|add|chat with|talk to|meet)\s+(?:me|us)"
    rf"|let'?s (?:continue|chat|talk|move|switch)|move (?:this|the conversation|our chat))\s+"
    rf"(?:on|via|over|through|to|at|in)\s+(?:{CHANNEL_WORDS})\b", re.I)
HANDLE_ON_NETWORK = re.compile(
    r"@[A-Za-z0-9_.]{2,}\s+on\s+(?:x|twitter|instagram|insta|ig|telegram|tiktok|discord|threads|linkedin|"
    r"whatsapp|signal|skype|snapchat|facebook|fb|github)\b", re.I)
# Off-platform channels that are rarely technology: ERROR before a contract.
OFF_PLATFORM = re.compile(
    r"\b(?:wechat|gmail|zoom\.us|calendly|cal\.com|zelle|cash ?app|wire transfer|signal app)\b", re.I)
# Channels that are also technology a proposal may name: REVIEW unless in a contact phrase.
OFF_PLATFORM_TECH = [
    re.compile(r"\b(?:discord|telegram|slack|paypal|venmo|crypto(?:currency)?|skype|whats\s?app|zoom|facetime|"
               r"google meet|linkedin|instagram|twitter|protonmail|icloud)\b", re.I),
    re.compile(r"\b(?:Signal|Teams)\b"),  # capitalized only: 'buying signal' and 'sales teams' are prose
    re.compile(r"\b(?:microsoft|ms) teams\b", re.I),
]
PLACEHOLDER = re.compile(r"\[\[(?:CONFIRM|TODO|TBD)[^\]]*\]\]", re.I)
DASHES = {"—": "em dash", "–": "en dash"}
CURLY = {"“": "curly double quote", "”": "curly double quote", "‘": "curly single quote",
         "’": "curly apostrophe"}
BAD_OPENINGS = [
    (re.compile(r"^(?:hi|hello|hey)?[\s,!]*(?:i|i'm|i am|i've|i have)\b", re.I), "I-led opening"),
    (re.compile(r"^dear (?:hiring manager|sir|madam|client)", re.I), "generic salutation"),
    (re.compile(r"^(?:hi|hello)?[\s,!]*(?:i )?(?:read|saw|came across|noticed) your (?:job|post|listing)", re.I),
     "'I read your post' opening"),
    (re.compile(r"^(?:hi|hello)?[\s,!]*my name is", re.I), "self-introduction opening"),
]
WATCHLIST = [
    "delve", "tapestry", "landscape", "pivotal", "foster", "bolster", "garner", "underscore", "multifaceted",
    "seamless", "seamlessly", "streamline", "unlock", "elevate", "empower", "transformative", "world-class",
    "game-changer", "game changer", "synergy", "moreover", "furthermore", "additionally", "cutting-edge",
    "leverage", "robust", "passionate", "rockstar", "ninja", "10x", "guru", "vibrant", "crucial", "nuanced",
    "intricate", "meticulous", "harness", "realm", "holistic", "comprehensive", "spearheading", "paradigm",
    "revolutionize", "ecosystem", "navigate", "genuinely", "at its core", "in today's world", "let's dive in",
    "it's important to note", "i wanted to reach out", "just circling back", "look no further",
]
CLAIM_RISKS = [
    (re.compile(r"\bperfect fit\b", re.I), "'perfect fit' claim"),
    (re.compile(r"\bguarantee[ds]?\b", re.I), "guarantee"),
    (re.compile(r"\b100\s?%", re.I), "100% claim"),
    (re.compile(r"\b(?:expert|senior|top[- ]rated)\b|\bthe best\b|\bbest[- ]in[- ]class\b|"
                r"\bbest (?:developer|engineer|freelancer|designer|programmer|consultant|analyst)s?\b", re.I),
     "superlative or unverified badge"),
    (re.compile(r"\b(?:years of experience|\d+\+? years)\b", re.I), "years-of-experience claim: confirm it is true"),
    (re.compile(r"\b(?:we|our team|my team)\b", re.I),
     "'we' or 'team' implies others did the work; use 'I' unless it means HypeStake as a company"),
]
WEAK_ENDINGS = re.compile(
    r"(?:looking forward to (?:hearing|working)|don't hesitate|do not hesitate|feel free to reach|excited to|"
    r"thank you for (?:your )?(?:time|consideration)|hope to hear|best regards|kind regards)", re.I)
FILLER_OPENERS = re.compile(r"^(?:i hope this (?:message|email) finds you well|hope you(?:'re| are) (?:well|doing well))", re.I)


@dataclass
class Finding:
    level: str  # ERROR | REVIEW | INFO
    code: str
    message: str
    excerpt: str = ""


def first_sentence(text: str) -> str:
    body = text.strip()
    match = re.match(r"(.+?[.!?])(?:\s|$)", body, re.S)
    return (match.group(1) if match else body.split("\n", 1)[0]).strip()


def link_parts(link: str) -> tuple[str, str]:
    """Return (host, path) without scheme, www, query, or fragment; lowercase host."""
    bare = re.sub(r"^[a-z][a-z0-9+.-]*://", "", link.strip(), flags=re.I)
    bare = re.sub(r"[?#].*$", "", bare)
    host, _, path = bare.partition("/")
    host = host.lower().split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host, "/" + path


def link_allowed(link: str, allow_links: list[str]) -> bool:
    """Exact host plus path prefix (on a path-segment boundary)."""
    host, path = link_parts(link)
    for allowed in allow_links:
        a_host, a_path = link_parts(allowed)
        if host != a_host:
            continue
        a_path = a_path.rstrip("/")
        if not a_path or path.rstrip("/") == a_path or path.startswith(a_path + "/"):
            return True
    return False


def term_pattern(term: str) -> re.Pattern:
    """Case-insensitive whole-term match; lookarounds keep 'C++' and '.NET' working."""
    start = r"\b" if re.match(r"\w", term) else r"(?<!\w)"
    end = r"\b" if re.search(r"\w$", term) else r"(?!\w)"
    return re.compile(start + re.escape(term) + end, re.I)


def contact_findings(text: str, contact_level: str, review_level: str,
                     allow_links: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    taken: list[tuple[int, int]] = []

    def add(level: str, code: str, message: str, m: re.Match, excerpt: str | None = None) -> None:
        span = (m.start(), m.end())
        if any(a < span[1] and span[0] < b for a, b in taken):
            return
        taken.append(span)
        findings.append(Finding(level, code, message, excerpt if excerpt is not None else m.group(0)))

    for m in EMAIL.finditer(text):
        add(contact_level, "contact-email", "email address in text", m)
    for pattern in OBFUSCATED_EMAIL:
        for m in pattern.finditer(text):
            add(contact_level, "contact-email", "obfuscated email address in text", m)
    for m in LINK.finditer(text):
        link = m.group(0).rstrip(".,);:!?")
        host = link_parts(link)[0]
        is_product = not re.match(r"(?:https?://|www\.)", link, re.I) and (
            host in PRODUCT_NAMES or host.endswith(".js"))
        if is_product or link_allowed(link, allow_links):
            taken.append((m.start(), m.end()))
            continue
        add(contact_level, "unapproved-link",
            "link not approved for this listing (pass --allow-link host/path if Andrew approved it)", m, link)
    for m in BARE_DOMAIN.finditer(text):
        token = m.group(0)
        if token.lower() in PRODUCT_NAMES or link_allowed(token, allow_links):
            continue
        add(review_level, "unapproved-link",
            "looks like a domain: if it is a link, get it approved; if it is a product name, ignore", m)
    for m in PHONE_INTERNATIONAL.finditer(text):
        add(contact_level, "contact-phone", "phone number in text", m)
    for m in PHONE_FORMATTED.finditer(text):
        add(contact_level, "contact-phone", "phone number in text", m)
    for m in PHONE_BARE.finditer(text):
        add(review_level, "contact-phone", "10-digit number: check it is not a phone number", m)
    for m in PHONE_SEVEN.finditer(text):
        add(review_level, "contact-phone", "7-digit number shape: check it is not a phone number", m)
    for m in HANDLE_ON_NETWORK.finditer(text):
        add(contact_level, "off-platform", "social handle on another network", m)
    for m in CONTACT_PHRASES.finditer(text):
        add(contact_level, "off-platform", "off-platform contact or payment wording", m)
    for m in CHANNEL_IN_CONTACT.finditer(text):
        add(contact_level, "off-platform", "asks to talk on an outside channel", m)
    for m in OFF_PLATFORM.finditer(text):
        add(contact_level, "off-platform", "off-platform contact or payment wording", m)
    for pattern in OFF_PLATFORM_TECH:
        for m in pattern.finditer(text):
            add(review_level, "off-platform",
                "outside channel named: fine as technology, not as a way to reach Andrew before a contract", m)
    return findings


def lint(text: str, kind: str, start_with: str | None = None, require: list[str] | None = None,
         allow_links: list[str] | None = None, final: bool = False,
         contract_active: bool = False, off_marketplace: bool = False) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    allow_links = [a.lower() for a in (allow_links or [])]
    words = re.findall(r"\b[\w'’-]+\b", text)
    stats = {"words": len(words), "characters": len(text.strip()), "kind": kind}

    contact_level = "INFO" if off_marketplace else "REVIEW" if contract_active else "ERROR"
    review_level = "INFO" if off_marketplace else "REVIEW"
    findings.extend(contact_findings(text, contact_level, review_level, allow_links))

    for ch, name in {**DASHES, **CURLY}.items():
        count = text.count(ch)
        if count:
            findings.append(Finding("REVIEW", "typography", f"{count} x {name}; use plain punctuation", ch))

    placeholders = PLACEHOLDER.findall(text)
    for p in placeholders:
        findings.append(Finding("ERROR" if final else "INFO", "placeholder", "unresolved placeholder", p))

    opener = first_sentence(text)
    if kind in {"cover-letter", "outreach"}:
        for pattern, label in BAD_OPENINGS:
            if pattern.search(opener):
                findings.append(Finding("REVIEW", "opening", label, opener[:120]))
                break
    if FILLER_OPENERS.search(text.strip()):
        findings.append(Finding("REVIEW", "warmup", "filler warmup opening", opener[:120]))

    lowered = text.lower()
    for word in WATCHLIST:
        for m in re.finditer(rf"\b{re.escape(word)}\b", lowered):
            findings.append(Finding("REVIEW", "watchlist", f"watchlist word '{word}'",
                                    text[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")))
    for pattern, label in CLAIM_RISKS:
        for m in pattern.finditer(text):
            findings.append(Finding("REVIEW", "claim", label,
                                    text[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")))

    tail = text.strip()[-220:]
    if kind in {"cover-letter", "outreach"} and WEAK_ENDINGS.search(tail):
        findings.append(Finding("REVIEW", "ending", "stock closing line; end on a concrete next step",
                                WEAK_ENDINGS.search(tail).group(0)))

    if start_with:
        first_word = re.match(r"\W*([\w'-]+)", text)
        if not first_word or first_word.group(1).lower() != start_with.lower():
            findings.append(Finding("ERROR", "client-instruction",
                                    f"client asked the proposal to start with '{start_with}'",
                                    text.strip()[:60]))
    for term in require or []:
        if not term_pattern(term).search(text):
            findings.append(Finding("ERROR", "client-instruction", f"required term missing: '{term}'"))

    lo, hi, hard = KINDS[kind]
    if hard and stats["characters"] > hard:
        findings.append(Finding("ERROR", "length", f"{stats['characters']} characters exceeds the {hard} limit"))
    if lo and stats["words"] < lo * 0.8:
        findings.append(Finding("REVIEW", "length", f"{stats['words']} words; target {lo}-{hi}"))
    if hi and stats["words"] > hi * 1.2:
        findings.append(Finding("REVIEW", "length", f"{stats['words']} words; target {lo}-{hi}"))
    return findings, stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", help="text file to check, or - for stdin")
    parser.add_argument("--kind", choices=sorted(KINDS), default="cover-letter")
    parser.add_argument("--start-with", help="word the client asked the proposal to start with")
    parser.add_argument("--require", action="append", default=[], help="term the client asked to include")
    parser.add_argument("--allow-link", action="append", default=[],
                        help="approved link as host plus path prefix, e.g. safe.example.dev/work")
    parser.add_argument("--final", action="store_true", help="treat unresolved placeholders as errors")
    parser.add_argument("--platform-contract-active", action="store_true",
                        help="a contract is active, so contact details are REVIEW rather than ERROR")
    parser.add_argument("--off-marketplace", action="store_true",
                        help="direct email or outreach outside any marketplace: contact details are INFO")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        text = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    findings, stats = lint(text, args.kind, args.start_with, args.require, args.allow_link, args.final,
                           args.platform_contract_active, args.off_marketplace)
    errors = sum(f.level == "ERROR" for f in findings)
    if args.json:
        print(json.dumps({"stats": stats, "errors": errors, "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        print(f"{stats['kind']}: {stats['words']} words, {stats['characters']} characters")
        for f in findings:
            extra = f"  [{f.excerpt}]" if f.excerpt else ""
            print(f"{f.level:6} {f.code}: {f.message}{extra}")
        print("No mechanical issues found." if not findings else f"{errors} error(s), {len(findings) - errors} other finding(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
