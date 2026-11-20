#!/usr/bin/env python3
"""Compare a source draft with its rewrite and list the anchors that changed.

Advisory; Python standard library only. Reads two UTF-8 files ("-" reads one
of them from stdin). Never rewrites, sends, or scores text.

An anchor is something a rewrite normally carries with the same force:
numbers and units, dates, links and addresses, quoted strings, code, names,
negation, attribution, and the small words that set certainty and scope
(may, about, at least, if, unless, pending, only, all), plus the words that
add a promise or a cause (will, must, because, therefore). The report lists
what disappeared and what is new. A dropped hedge can turn an estimate into a
promise; a dropped "thinks" can turn an opinion into a fact; a new "because"
asserts a cause; a new number or name needs a source. Within one family a
swap is quiet ("about" to "roughly"); a family is reported only when its total
falls or rises. Some changes are intended, so every line is a prompt to check,
not an error. A clean result does not prove that meaning survived: read both
versions. The comparison is word-level and English-centred; a claim invented
in plain words is invisible to it.

Usage: python scripts/fidelity_check.py source.txt rewrite.txt [--mode summary] [--json] [--strict]
--mode summary is for a requested cut: it lists only what is new, because a
summary is expected to leave material out.
Exit: 0 completed; 1 with --strict when a reported hard anchor (number, date,
link, quote, code, name, negation) changed; 2 usage or read error.
"""

import argparse
from collections import Counter
import json
import re
import sys

HARD = ("numbers", "dates", "links", "quotes", "code", "names", "negation")

# Families keep synonyms together, so "about" -> "approximately" is quiet while
# "may" -> "will" (a hedge disappearing) is reported.
FAMILIES = {
    "hedge": ["may", "might", "could", "possibly", "perhaps", "probably", "likely",
              "unlikely", "potentially", "presumably", "maybe"],
    "evidential": ["suggests", "suggest", "suggested", "appears", "appear", "appeared",
                   "seems", "seem", "seemed", "indicates", "indicate", "is consistent with"],
    "approximation": ["about", "around", "approximately", "roughly", "nearly", "almost",
                      "circa", "estimated", "estimate", "estimates", "or so", "~"],
    "lower-bound": ["at least", "more than", "over", "no fewer than", "minimum"],
    "upper-bound": ["at most", "up to", "less than", "fewer than", "under", "no more than",
                    "maximum"],
    "condition": ["if", "unless", "until", "provided", "except", "only if", "assuming",
                  "subject to", "depends on", "dependent on"],
    "status": ["pending", "preliminary", "not yet", "so far", "to date", "initial",
               "planned", "target", "goal", "forecast", "projected", "expected"],
    "scope-limiter": ["only", "some", "several", "a few", "few", "many", "most", "part of",
                      "partial", "partially"],
    "absolute": ["all", "every", "always", "never", "none", "everyone", "nobody",
                 "guaranteed", "completely", "entirely", "proves", "proven"],
    "attribution": ["says", "said", "thinks", "think", "thought", "believes", "believe",
                    "reports", "reported", "according to", "claims", "claimed", "argues",
                    "argued", "notes", "noted", "told", "found", "feels",
                    "felt", "expects", "hopes", "suspects"],
    # The two families below matter when they are new: a promise or a cause
    # the source did not state.
    "commitment": ["will", "shall", "must", "promise", "promises", "promised",
                   "commit", "commits", "committed", "guarantee", "guarantees"],
    "causation": ["because", "therefore", "thus", "hence", "consequently",
                  "as a result", "due to", "thanks to", "which means", "leads to",
                  "led to", "results in", "resulted in", "causes", "caused"],
}

# Reported only when new: losing a "because" or a "will" removes a claim, and
# that loss already shows in the sentence the reader compares.
ADDED_ONLY = {"commitment", "causation"}

# These words set scope only before a quantity ("about 12%", not "about pricing").
NUMERIC_ONLY = {"about", "around", "over", "under"}

NEGATION_RE = re.compile(
    r"\b(?:not|no|never|none|neither|nor|without|cannot)\b|n['’]t\b", re.I)

NUMBER_WORDS = {
    "zero": 0, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
    "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "dozen": 12,
}
UNITS = (r"%|(?:percent|per\s+cent|pp|bps|x|k|m|bn|b|ms|s|sec|secs|seconds?|min|mins|minutes?|"
         r"h|hrs?|hours?|days?|weeks?|months?|years?|kb|mb|gb|tb|usd|eur|gbp)\b")
NUMBER_RE = re.compile(
    r"(?<![\w.])([-+]?[$€£¥]?\d[\d,]*(?:\.\d+)?)(?:\s?(" + UNITS + r"))?", re.I)
WORD_NUMBER_RE = re.compile(r"\b(" + "|".join(NUMBER_WORDS) + r")\b(?:\s?(" + UNITS + r"))?", re.I)

MONTHS = ("January|February|March|April|June|July|August|September|October|November|December|"
          "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec")
DATE_RE = re.compile(
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
    r"Mon|Tue|Tues|Wed|Thu|Thur|Thurs|Fri|Sat|Sun)\b|"
    r"\b(?:" + MONTHS + r")\b|\bMay(?=\s+\d)|(?<=\d\s)May\b|"
    r"\bQ[1-4]\b|\bH[12]\b|\bFY\s?\d{2,4}\b|"
    r"\b(?:today|tonight|tomorrow|yesterday|this week|next week|last week|this month|"
    r"next month|end of day|EOD|EOW|end of week|this quarter|next quarter)\b|"
    r"\b\d{1,2}(?::\d{2})?\s?(?:a\.?m\.?|p\.?m\.?)(?=\W|$)", re.I)

LINK_RE = re.compile(
    r"\b(?:https?://|www\.)[^\s<>\"')\]]+|"
    r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b|(?<![\w@])@[A-Za-z0-9_]{2,}")
QUOTE_RE = re.compile(r'"([^"\n]{2,})"|“([^”]{2,})”')
INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[^\n]*\n(.*?)^ {0,3}\1[ \t]*$", re.M | re.S)

COMMON_CAPS = set("""
A An The This That These Those It Its I We You They He She Our Your Their My His Her
And But Or So Yet For Nor If When While Because Although Though Once After Before Then
Now Here There What Why How Where Who Which Whose Each Every Some Most Many All Any No
Not Yes One Two Three First Second Third Next Last Finally Also Still Even Just Only
Please Let See Note Read Write Run Use Add Check Make Keep Send Start Stop Open Close
Click Select Enter Set Get Do Don't Try Ask Tell Give Take Find Install Update Remove
Review Confirm Create Deploy Verify Revoke Rotate Thanks Thank Hi Hello Hey Dear Best
Regards Cheers Sincerely In On At To By As Of With Without From Into Over Under About
Since Until Unless Despite During Instead However Moreover Overall Today Tomorrow
Yesterday Could Would Should Can Will May Might Must Is Are Was Were Be Been Has Have Had
Think Imagine Consider Remember Notice Look Picture Suppose Yet Still Despite
""".split())
# A capitalized sentence opener with an ordinary English suffix is rarely a name.
COMMON_SUFFIX_RE = re.compile(
    r"(?:ing|ed|ly|tion|sion|ment|ness|ity|ent|ant|ive|al|ous|ers|ors|ance|ence|ies|es|cy)$")

DATE_ALIASES = {
    "jan": "january", "feb": "february", "mar": "march", "apr": "april", "jun": "june",
    "jul": "july", "aug": "august", "sep": "september", "sept": "september",
    "oct": "october", "nov": "november", "dec": "december", "mon": "monday",
    "tue": "tuesday", "tues": "tuesday", "wed": "wednesday", "thu": "thursday",
    "thur": "thursday", "thurs": "thursday", "fri": "friday", "sat": "saturday",
    "sun": "sunday", "eod": "end of day", "eow": "end of week",
}

SENTENCE_START_RE = re.compile(
    r"(?:^|[.!?:]\s+|\n[ \t]*(?:(?:[-*+>#]+|\d+\.)[ \t]*)*)(?:\*\*|__|[*_])?$")
# Presence matters for these; a rewrite that mentions a name once instead of
# six times has not dropped it.
PRESENCE = ("numbers", "dates", "links", "quotes", "code", "names")


def _norm_number(raw, unit):
    value = raw.replace(",", "")
    unit = (unit or "").lower()
    unit = re.sub(r"\s+", " ", unit)
    if unit in ("percent", "per cent"):
        unit = "%"
    unit = {"secs": "s", "sec": "s", "second": "s", "seconds": "s", "mins": "min",
            "minute": "min", "minutes": "min", "hr": "h", "hrs": "h", "hour": "h",
            "hours": "h", "day": "days", "week": "weeks", "month": "months",
            "year": "years"}.get(unit, unit)
    return (value + ("" if unit in ("", "%") else " ") + unit).strip()


def _strip_code(text):
    blocks = [m.group(2).strip() for m in FENCE_RE.finditer(text)]
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    spans = [m.group(2) for m in INLINE_CODE_RE.finditer(text)]
    text = INLINE_CODE_RE.sub(" ", text)
    return text, blocks, spans


def lowercase_vocabulary(text):
    return set(re.findall(r"\b[a-z][a-z'’-]*\b", text))


def anchors(text, shared_vocabulary=frozenset()):
    """Return a Counter per anchor category for one text.

    A capitalized word at a sentence start counts as a name only when neither
    text uses it in lowercase, so "Startup is..." does not look like a new name
    when the other version says "startup".
    """
    out = {name: Counter() for name in ("numbers", "dates", "links", "quotes", "code",
                                         "names", "negation", *FAMILIES)}
    text, blocks, spans = _strip_code(text)
    for block in blocks:
        first = block.splitlines()[0] if block else ""
        out["code"]["block: " + first[:60] + (" ..." if len(block) > len(first) else "")] += 1
    for span in spans:
        out["code"][span] += 1

    for match in LINK_RE.finditer(text):
        out["links"][match.group(0).rstrip(".,;:!?")] += 1
    prose = LINK_RE.sub(" ", text)

    for match in QUOTE_RE.finditer(prose):
        out["quotes"][(match.group(1) or match.group(2)).strip()] += 1

    for match in DATE_RE.finditer(prose):
        date = re.sub(r"\s+", " ", match.group(0)).strip().lower()
        out["dates"][DATE_ALIASES.get(date, date)] += 1

    for match in NUMBER_RE.finditer(prose):
        out["numbers"][_norm_number(match.group(1), match.group(2))] += 1
    for match in WORD_NUMBER_RE.finditer(prose):
        out["numbers"][_norm_number(str(NUMBER_WORDS[match.group(1).lower()]), match.group(2))] += 1

    out["negation"]["negation"] += len(NEGATION_RE.findall(prose))
    if not out["negation"]["negation"]:
        del out["negation"]["negation"]

    lowered = " " + re.sub(r"\s+", " ", prose.lower()) + " "
    lowered = re.sub(r"(?<=\w)['’]ll\b", " will", lowered)
    for family, words in FAMILIES.items():
        for word in sorted(words, key=len, reverse=True):
            pattern = r"(?<![\w-])" + re.escape(word) + r"(?![\w-])"
            if word in NUMERIC_ONLY:
                pattern += r"(?=\s+[$€£¥~]?(?:\d|(?:" + "|".join(NUMBER_WORDS) + r")\b))"
            hits = re.findall(pattern, lowered)
            if hits:
                out[family][word] += len(hits)
                lowered = re.sub(pattern, " ", lowered)

    lower_words = lowercase_vocabulary(prose) | set(shared_vocabulary)
    # Title-case headings are not evidence of names.
    prose = re.sub(r"(?m)^[ \t]{0,3}#{1,6}[ \t].*$", lambda m: " " * len(m.group(0)), prose)
    for match in re.finditer(r"\b[A-Z][A-Za-z0-9'’&.-]*[A-Za-z0-9]|\b[A-Z]\b", prose):
        token = re.sub(r"['’](?:s|ll|re|ve|d|m)$", "", match.group(0).rstrip("."))
        if token in COMMON_CAPS or len(token) < 2:
            continue
        if DATE_RE.fullmatch(token):
            continue
        initial = bool(SENTENCE_START_RE.search(prose[max(0, match.start() - 12):match.start()]))
        if initial and not token.isupper() and (
                token.lower() in lower_words or COMMON_SUFFIX_RE.search(token.lower())):
            continue
        out["names"][token] += 1
    for category in PRESENCE:
        out[category] = Counter(dict.fromkeys(out[category], 1))
    return out


def compare(source, rewrite, mode="rewrite"):
    """List anchors that changed. mode "summary" reports additions only."""
    if mode not in ("rewrite", "summary"):
        raise ValueError("unknown mode: " + mode)
    vocabulary = lowercase_vocabulary(source) | lowercase_vocabulary(rewrite)
    before, after = anchors(source, vocabulary), anchors(rewrite, vocabulary)
    dropped, added, kept = {}, {}, 0
    for category in before:
        gone = before[category] - after[category]
        new = after[category] - before[category]
        kept += sum((before[category] & after[category]).values())
        if category in FAMILIES:
            # A swap inside a family keeps its force; report only a net change.
            net = sum(after[category].values()) - sum(before[category].values())
            kept += min(sum(gone.values()), sum(new.values()))
            gone = gone if net < 0 and category not in ADDED_ONLY else Counter()
            new = new if net > 0 else Counter()
        if gone and mode == "rewrite":
            dropped[category] = dict(sorted(gone.items()))
        if new:
            added[category] = dict(sorted(new.items()))
    return {"dropped": dropped, "added": added, "unchanged_anchor_count": kept}


def _describe(values):
    return ", ".join(name if count == 1 else f"{name} x{count}" for name, count in values.items())


def report(result, source_name, rewrite_name):
    lines = [f"Fidelity check: {source_name} -> {rewrite_name}"]
    if result["dropped"]:
        lines.append("\nGone from the rewrite (confirm each was meant to go):")
        for category, values in result["dropped"].items():
            lines.append(f"  {category}: {_describe(values)}")
    if result["added"]:
        lines.append("\nNew in the rewrite (confirm each has a source):")
        for category, values in result["added"].items():
            lines.append(f"  {category}: {_describe(values)}")
    if not result["dropped"] and not result["added"]:
        lines.append("\nNo anchor changed.")
    if result.get("mode") == "summary":
        lines.append("\nSummary mode: anchors missing from the rewrite are not listed.")
    lines.append(f"\nUnchanged anchors: {result['unchanged_anchor_count']}.")
    lines.append("Advisory only. A family change (for example hedge or attribution) can strengthen")
    lines.append("a claim; a clean result does not prove meaning survived. Read both versions.")
    return "\n".join(lines)


def _read(path, parser):
    try:
        if path == "-":
            return sys.stdin.buffer.read().decode("utf-8")
        with open(path, encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        parser.exit(2, f"fidelity_check.py: cannot read {path}: {exc}\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", help="original draft or brief (UTF-8); '-' reads stdin")
    parser.add_argument("rewrite", help="rewritten text (UTF-8); '-' reads stdin")
    parser.add_argument("--mode", choices=("rewrite", "summary"), default="rewrite",
                        help="summary lists only what is new; use it for a requested cut")
    parser.add_argument("--json", action="store_true", help="emit structured results")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when a reported number, date, link, quote, code span, name or negation changed")
    args = parser.parse_args(argv)
    if args.source == "-" and args.rewrite == "-":
        parser.error("only one input can come from stdin")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    source, rewrite = _read(args.source, parser), _read(args.rewrite, parser)
    if not source.strip() or not rewrite.strip():
        parser.exit(2, "fidelity_check.py: empty input\n")
    result = {"mode": args.mode, **compare(source, rewrite, args.mode)}
    if args.json:
        print(json.dumps({"schema_version": 1, **result,
                          "notice": "Advisory anchor comparison; not a meaning or quality verdict."},
                         ensure_ascii=False, indent=2))
    else:
        print(report(result, args.source, args.rewrite))
    changed_hard = any(category in HARD for category in (*result["dropped"], *result["added"]))
    return int(args.strict and changed_hard)


if __name__ == "__main__":
    sys.exit(main())
