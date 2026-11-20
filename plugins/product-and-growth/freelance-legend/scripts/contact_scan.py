#!/usr/bin/env python3
"""Scan a built website for anything that would expose contact details.

Use on the proposal-safe build of Andrew's portfolio site (for example the
`out/` folder of a static export, or `.next/server/app` HTML) before linking
any page from an Upwork proposal or pre-contract message. Standard library only.

Checks every .html, .htm, .json, .txt (including React Server Component payloads),
.xml, .rss, .md, and .mdx file (and .js bundles with --include-js) for: email
addresses, mailto: and tel: links, phone numbers, <form> elements, booking and
calendar domains, messaging apps and handles, and contact properties inside
JSON-LD (email, telephone, address, contactPoint). HTML entities (&#64;) are
decoded first, obfuscated emails ("name [at] domain [dot] com") are caught, and
any .vcf or .pdf file in the tree is reported as "file-review" (a vCard or a
resume PDF usually carries contact details).

--allow is matched against the flagged token itself (the URL or the matched
text), never the text around it, so a contact line next to the allowed Upwork
link is still reported.

Exit codes: 0 clean, 1 findings, 2 usage problem.

Example:  python contact_scan.py out/ --allow "upwork.com/freelancers/"
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

EXTENSIONS = {".html", ".htm", ".json", ".txt", ".xml", ".rss", ".md", ".mdx"}
PATTERNS = [
    ("email", re.compile(r"(?<![\w.@/-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")),
    ("mailto", re.compile(r"mailto:", re.I)),
    ("tel", re.compile(r"\btel:", re.I)),
    ("sms", re.compile(r"\bsms:", re.I)),
    ("email", re.compile(r"\b[\w.+-]+\s*[\[({]\s*at\s*[\])}]\s*[\w-]+"
                         r"(?:\s*[\[({]\s*dot\s*[\])}]\s*[\w-]+|\.[\w-]+)+", re.I)),
    ("email", re.compile(r"\b[\w.+-]+\s+at\s+[\w-]+(?:\s+dot\s+[A-Za-z]{2,})+\b", re.I)),
    ("phone", re.compile(r"(?<![\d.])(?:\+?1[\s.-]?)?(?:\([2-9]\d{2}\)[\s.-]?|[2-9]\d{2}[\s.-])\d{3}[\s.-]\d{4}"
                         r"(?!\d)(?!\.\d)")),
    ("phone", re.compile(r"(?<![\w+])\+\d{1,3}[\s.-]?\(?\d{1,4}\)?(?:[\s.-]\d{2,4}){2,}(?!\d)")),
    ("form", re.compile(r"<form\b", re.I)),
    ("booking", re.compile(r"calendly\.com|cal\.com/|savvycal\.com|tidycal\.com|zcal\.co|meetings\.hubspot|"
                           r"zoom\.us/|meet\.google\.com|youcanbook\.me|acuityscheduling", re.I)),
    ("messaging", re.compile(r"t\.me/|telegram\.me|wa\.me/|whatsapp\.com|signal\.me|discord\.gg|discord\.com/users|"
                             r"skype:|m\.me/", re.I)),
    ("social", re.compile(r"linkedin\.com/in/|\btwitter\.com/|\bx\.com/[A-Za-z0-9_]+|instagram\.com/|facebook\.com/", re.I)),
]
JSONLD_KEYS = {"email", "telephone", "faxNumber", "address", "contactPoint"}
JSONLD = re.compile(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", re.I | re.S)
# Image and asset names often contain "@2x" etc.; skip obvious false positives.
EMAIL_FALSE_POSITIVE = re.compile(r"@\d+x\.(?:png|jpe?g|webp|avif|svg)$", re.I)
REVIEW_FILES = {".vcf": "vCard file: contact card, remove it from a proposal-safe build",
                ".pdf": "PDF file: check it (a resume PDF usually lists email and phone)"}
TOKEN_STOP = set(" \t\r\n\"'<>()[]{},;`")


def token_at(text: str, start: int, end: int) -> str:
    """The whitespace/quote-delimited token (a URL, an email) that contains text[start:end]."""
    while start > 0 and text[start - 1] not in TOKEN_STOP:
        start -= 1
    while end < len(text) and text[end] not in TOKEN_STOP:
        end += 1
    return text[start:end]


def walk_jsonld(node, path="$"):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in JSONLD_KEYS:
                yield f"{path}.{key}"
            yield from walk_jsonld(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from walk_jsonld(item, f"{path}[{i}]")


def scan_text(text: str, allow: list[str]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    raw = text
    text = html.unescape(text.replace("\\u0040", "@").replace("\\u002e", "."))
    allow = [a.lower() for a in allow]
    spans: dict[str, list[tuple[int, int]]] = {}
    for name, pattern in PATTERNS:
        for m in pattern.finditer(text):
            if name == "email" and EMAIL_FALSE_POSITIVE.search(m.group(0)):
                continue
            taken = spans.setdefault(name, [])
            if any(a < m.end() and m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            token = token_at(text, m.start(), m.end()) if name not in ("form",) else m.group(0)
            if any(a in token.lower() or a in m.group(0).lower() for a in allow):
                continue
            context = text[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")
            found.append((name, context.strip()))
    for block in JSONLD.findall(raw):
        try:
            data = json.loads(block.replace("\\u003c", "<"))
        except json.JSONDecodeError:
            found.append(("jsonld-unparsed", block.strip()[:80]))
            continue
        for key_path in walk_jsonld(data):
            found.append(("jsonld-contact", key_path))
    return found


def scan(root: Path, allow: list[str], include_js: bool = False) -> list[dict]:
    exts = EXTENSIONS | ({".js", ".mjs"} if include_js else set())
    every = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
    results = []
    for path in sorted(every):
        if path.suffix.lower() in REVIEW_FILES:
            results.append({"file": str(path), "kind": "file-review", "context": REVIEW_FILES[path.suffix.lower()]})
    files = [root] if root.is_file() else [p for p in every if p.suffix.lower() in exts]
    for path in sorted(files):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for kind, context in scan_text(text, allow):
            results.append({"file": str(path), "kind": kind, "context": context})
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="build output directory or a single file")
    parser.add_argument("--allow", action="append", default=[],
                        help="substring allowed inside a flagged URL or match (for example the Upwork profile URL)")
    parser.add_argument("--include-js", action="store_true", help="also scan JavaScript bundles (noisier)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.path)
    if not root.exists():
        print(f"error: {root} does not exist", file=sys.stderr)
        return 2
    results = scan(root, args.allow, args.include_js)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['kind']:16} {r['file']}: {r['context']}")
        print("clean: no contact details found" if not results else f"{len(results)} finding(s): not proposal-safe")
    return 1 if results else 0


if __name__ == "__main__":
    raise SystemExit(main())
