#!/usr/bin/env python3
"""Map where a draft's habits sit. Descriptive only: no score, no verdict.

Adapted from Clarity's prose_stats.py and strip_markdown.py (MIT License,
Copyright (c) 2026 Addy Osmani; see NOTICE.md) with additions from the
ultimate-prose pattern references. Python standard library only. Reads a file
or stdin; never rewrites, sends, or grades text.

Clarity found that a stylometric composite ranked a genuinely human control
as the "riskiest" text in its exploratory corpus, so this tool reports no
composite and no threshold verdict. Every list is a place to read in context.
Measurements are most useful for comparing two versions of the same piece
(--compare); they are not norms for prose in general.

Code, quotations, blockquotes, links, and addresses are excluded through the
sibling lint.py mask (quotations can be included with --include-quotes).
Headings are excluded from sentence measurements; each list item is a unit.

Usage:
  python scripts/prose_stats.py draft.md
  python scripts/prose_stats.py draft.md --compare earlier.md
  python scripts/prose_stats.py - --json < draft.txt
Exit: 0 completed; 2 usage or read error.
"""

import argparse
import json
from pathlib import Path
import re
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:  # Each skill ships its own lint.py with a compatible mask_sources().
    from lint import mask_sources as _lint_mask
except Exception:  # pragma: no cover - degraded mode keeps the tool usable
    _lint_mask = None

# --------------------------------------------------------------- vocabularies
# Time-dated search aids. They drift with language and model generations; an
# absence is not a pass and a match is not a defect without context.

HEDGES = {
    "may", "might", "could", "perhaps", "possibly", "likely", "generally",
    "typically", "often", "usually", "tends", "tend", "suggests", "suggest",
    "appears", "appear", "seems", "seem", "arguably", "relatively", "somewhat",
    "potentially", "presumably", "largely", "broadly", "commonly", "roughly",
    "sometimes", "mostly", "probably", "fairly", "maybe", "basically", "quite",
    "almost", "occasionally", "apparently", "supposedly", "unclear", "unsure",
}
HEDGE_PHRASES = ["kind of", "sort of", "a bit", "i think", "i guess", "i suspect",
                 "more or less", "pretty much", "in practice", "for the most part"]
BOOSTERS = {
    "crucial", "crucially", "essential", "vital", "significant", "significantly",
    "robust", "powerful", "remarkable", "remarkably", "notable", "notably",
    "critical", "critically", "profound", "profoundly", "compelling", "paramount",
    "pivotal", "important", "importantly", "substantial", "substantially",
    "transformative", "groundbreaking", "invaluable", "seamless", "seamlessly",
    "unprecedented", "revolutionary", "game-changing", "monumental",
}
SIGNPOSTS = {
    "moreover", "furthermore", "additionally", "consequently", "therefore", "thus",
    "notably", "importantly", "ultimately", "indeed", "similarly", "conversely",
    "nevertheless", "nonetheless", "accordingly", "hence", "overall", "meanwhile",
    "crucially", "essentially",
}
PUFFERY_ADVERBS = {"genuinely", "truly", "actually", "simply", "deeply",
                   "structurally", "fundamentally", "incredibly", "absolutely"}
STOCK_OPENERS = [
    "in today's", "in the realm of", "when it comes to", "at its core",
    "it's worth noting", "it is worth noting", "it's important to note",
    "it is important to note", "it's important to consider", "it is important to consider",
    "in a world where", "the reality is", "here's the thing", "let's dive",
    "let's explore", "let's break this down", "here's what you need to know",
    "without further ado", "let me be clear", "the uncomfortable truth", "make no mistake",
    "let that sink in", "here is the tension", "here's the tension", "worth naming",
    "one might argue", "in many ways", "that being said", "looking ahead",
]
STOCK_CLOSERS = ["in conclusion", "in summary", "to sum up", "to summarize", "in short",
                 "all in all", "in essence", "taken together", "at the end of the day",
                 "only time will tell", "the future belongs", "the only question is"]
# Overused lexicon with a plainer choice; keep the original if the plain word is worse.
LEXIS = {
    "delve": "look at", "tapestry": "name the actual thing", "realm": "name the actual thing",
    "landscape": "name the actual thing", "underscore": "show", "underscores": "shows",
    "leverage": "use", "leveraging": "using", "seamless": "easy, or say how",
    "frictionless": "easy, or say how", "crucial": "important, or say why",
    "pivotal": "important, or say why", "testament to": "shows",
    "navigating the": "handling the", "foster": "build", "fostering": "building",
    "cultivate": "build", "elevate": "improve", "unlock": "enable", "unlocks": "enables",
    "empower": "let", "myriad": "many", "plethora": "many", "showcase": "show",
    "showcasing": "showing", "bolster": "strengthen", "garner": "get",
    "game-changer": "say the concrete change", "ever-evolving": "changing",
    "multifaceted": "name the facets", "intricate": "detailed", "meticulous": "careful",
    "utilize": "use", "facilitate": "help", "plays a crucial role": "say what it does",
    "plays a key role": "say what it does", "plays a vital role": "say what it does",
    "shed light on": "explain", "a double-edged sword": "name the tradeoff",
}
CHATBOT = ["i hope this helps", "would you like me to", "great question",
           "you're absolutely right", "certainly!", "as an ai", "as of my last",
           "based on available information", "here is the revised", "here's the revised",
           "here is a revised", "here's a revised", "here is the rewritten",
           "here's the rewritten"]
# Clarity's experimental Claude-frequency subset. Individually ordinary in
# engineering; reported only as a cluster (four or more distinct, 150+ words).
MODEL_REGISTER = [
    "load-bearing", "re-derived", "byte-identical", "mutation-checked",
    "mutation-verified", "mutation-tested", "re-verified", "re-measured",
    "byte-identity", "byte-for-byte", "vacuously", "short-circuits", "self-heals",
    "chokepoint", "backstop", "tripwire", "goldens", "unparseable", "papered over",
    "re-derive", "re-derives", "falsified", "provably", "restated", "ungated",
    "unit-tested", "machinery",
]

CONTRASTIVE = [re.compile(p, re.I) for p in (
    r"\brather than\b", r"\bnot simply\b", r"\bnot merely\b", r"\bnot solely\b",
    r"\bas opposed to\b", r"\bnot just\b[^.?!]{0,60}\bbut\b",
    r"\bnot only\b[^.?!]{0,60}\bbut\b", r"\bisn'?t\b[^.?!]{0,40}\bit'?s\b",
    r"\bis not\b[^.?!]{0,40}\bit is\b", r"\bthe question is ?n'?t\b",
    r"\bless\s+\w+,\s*more\s+\w+\b",
)]
COPULA = re.compile(r"\b(serves as|stands as|represents a|marks a|features a|boasts|offers a)\b", re.I)
ABSTRACT_ACTOR = re.compile(
    r"\bthe (?:data|numbers|market|industry|research|culture|conversation|decision|"
    r"technology|algorithm|process|architecture|landscape) (?:tells?|told|shows? us|"
    r"says|said|wants?|decides?|decided|demands?|rewards?|punishes|speaks?|knows?|"
    r"emerges?|listens?|drives?)\b", re.I)
VAGUE_ATTRIBUTION = re.compile(
    r"\b(?:studies|research) (?:show|shows|suggest|suggests|indicate|indicates|prove|proves)\b|"
    r"\bexperts? (?:say|agree|believe|argue|warn|note)\b|\bcritics (?:say|argue|claim)\b|"
    r"\bobservers (?:say|note|believe|have noted)\b|\b(?:many|some) (?:people )?(?:say|believe|argue)\b|"
    r"\bit is widely (?:believed|accepted|known)\b|\baccording to (?:research|experts|studies|reports)\b|"
    r"\bindustry reports\b|\beveryone knows\b", re.I)
IMPORTANCE = re.compile(
    r"\b(?:important|crucial|vital|pivotal|transformative|groundbreaking|remarkable|"
    r"unprecedented|revolutionary|game-changing|profound|monumental|"
    r"(?<!statistically )significant)\b", re.I)
MECHANISM = re.compile(
    r"\d|\b(?:because|by|through|which|so that|therefore|means|allows?|enables?|"
    r"results? in|leads? to|causes?|prevents?|reduces?|increases?|measured|according to|"
    r"for example|such as|since|when|if|unless|e\.g\.)\b", re.I)
ABSOLUTE = re.compile(
    r"\b(?:always|never|everyone|nobody|impossible|guaranteed|completely|entirely|"
    r"unprecedented|every single)\b", re.I)
METAPHOR_FLOURISH = re.compile(
    r"\bwearing the (?:costume|clothes|mask|uniform) of\b|\bin (?:a |the )?(?:costume|"
    r"disguise) of\b|\bdressed up as\b|\bmasquerading as\b|\bin \w+'?s clothing\b", re.I)
PARTICIPIAL = re.compile(
    r"^\s*(?:building on|drawing on|having|given|considering|looking ahead|looking back|"
    r"leveraging|combining|reflecting|highlighting|underscoring|recognizing|"
    r"acknowledging|understanding|stepping back|zooming out|turning to|moving forward|"
    r"armed with|faced with|against this backdrop)\b[^,\n]{0,60},", re.I)
TRIAD = re.compile(
    r"\b([A-Za-z][\w'-]*(?:[ \t]+[\w'-]+){0,2}),[ \t]+([A-Za-z][\w'-]*(?:[ \t]+[\w'-]+){0,2}),"
    r"[ \t]+(?:and|or)[ \t]+([A-Za-z][\w'-]*(?:[ \t]+[\w'-]+){0,2})\b")
DEFINITION_OPENER = re.compile(
    r"^(?:(?:A|An|The)\s+)?[A-Za-z][\w-]*(?:\s+[\w-]+){0,3}\s+(?:is|are)\s+(?:a|an|the)\b")
DEMONSTRATIVE_KICKER = re.compile(r"^(?:This|That)\b[^?]{0,60}[.!]$")
DASH_RE = re.compile(r"—|–|(?<=\s)--(?=\s)")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*|\d[\d,.]*")
NUM_RE = re.compile(r"\b\d[\d,.]*\b")
QUOTE_RE = re.compile(r'"[^"\n]{4,}"|“[^”]{4,}”')
PROPER_RE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
COMMON_CAPS = set("""The A An I It This That These Those But And Or So If When While You We They
He She There What Why How Where Who Because Although Once For In On At To By As Not No Yes
Every Most Some Each One Two Three After Before Then Now Here His Her Their Our Its My Do
Does Did Please Thanks""".split())


# ---------------------------------------------------------------- structure

def _basic_mask(text, include_quotes=False):
    text = re.sub(r"(?ms)^ {0,3}(`{3,}|~{3,}).*?^ {0,3}\1[ \t]*$",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    return re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), text)


def masked(text, include_quotes=False):
    if _lint_mask is not None:
        scan = _lint_mask(text, include_quotes=include_quotes)
    else:
        scan = _basic_mask(text, include_quotes)
    return scan.replace("\0", " ")


def _clean_inline(line):
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", line)
    line = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: m.group(1) or m.group(2), line)
    line = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", line)
    line = re.sub(r"~~([^~]+)~~", r"\1", line)
    line = re.sub(r"</?[a-zA-Z][^>]*>", "", line)
    return re.sub(r"[ \t]+", " ", line).strip()


def _split_sentences(text):
    guard = ""
    text = re.sub(r"(?<=\d)\.(?=\d)", guard, text)
    text = re.sub(r"\b(?:e\.g|i\.e|vs|etc|Mr|Mrs|Ms|Dr|Prof|St|Inc|Ltd|No)\.",
                  lambda m: m.group(0).replace(".", guard), text)
    parts = re.split(r"(?<=[.!?])[\"'”’)\]]*\s+", text)
    return [p.replace(guard, ".").strip() for p in parts if p.strip()]


def structure(text, include_quotes=False):
    """Return prose units grouped by paragraph, excluding headings and tables."""
    scan = masked(text, include_quotes)
    scan = re.sub(r"\A---\n.*?\n---\n", lambda m: "\n" * m.group(0).count("\n"), scan, flags=re.S)
    scan = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), scan, flags=re.S)
    paragraphs = []
    for block in re.split(r"\n[ \t]*\n", scan):
        units, prose_lines, has_prose = [], [], False
        for line in block.split("\n"):
            if not line.strip() or re.match(r"^[ \t]{0,3}(?:#{1,6}[ \t]|\|)", line) \
                    or re.match(r"^\s*(?:[-*_][ \t]*){3,}$", line):
                continue
            item = re.match(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+(.*)$", line)
            if item:
                units.extend(_split_sentences(_clean_inline(item.group(1))))
                continue
            prose_lines.append(_clean_inline(re.sub(r"^[ \t]{0,3}>[ \t]?", "", line)))
            has_prose = True
        if prose_lines:
            units = _split_sentences(" ".join(prose_lines)) + units
        units = [u for u in units if WORD_RE.search(u)]
        if units:
            paragraphs.append({"units": units, "prose": has_prose})
    return paragraphs


# ---------------------------------------------------------------- analysis

def _cv(values):
    values = [v for v in values if v > 0]
    if len(values) < 2:
        return 0.0
    mean = statistics.mean(values)
    return statistics.pstdev(values) / mean if mean else 0.0


def _words(unit):
    return WORD_RE.findall(unit)


def _mattr(tokens, window=50):
    if len(tokens) < 40:
        return None
    tokens = [t.lower() for t in tokens]
    if len(tokens) <= window:
        return len(set(tokens)) / len(tokens)
    spans = [len(set(tokens[i:i + window])) / window for i in range(len(tokens) - window + 1)]
    return sum(spans) / len(spans)


def _trigram_repeat_rate(tokens):
    if len(tokens) < 60:
        return None
    tokens = [t.lower() for t in tokens]
    seen, repeats, total = set(), 0, 0
    for i in range(len(tokens) - 2):
        gram = tuple(tokens[i:i + 3])
        total += 1
        repeats += gram in seen
        seen.add(gram)
    return repeats / total if total else None


def _phrase_hits(text, phrases):
    low = " " + re.sub(r"\s+", " ", text.lower().replace("’", "'")) + " "
    return sorted({p for p in phrases if re.search(r"(?<![\w'])" + re.escape(p) + r"(?![\w'])", low)})


def _short(unit, width=110):
    unit = re.sub(r"\s+", " ", unit)
    return unit if len(unit) <= width else unit[:width - 3] + "..."


def analyze(text, include_quotes=False):
    paragraphs = structure(text, include_quotes)
    units = [u for p in paragraphs for u in p["units"]]
    joined = "\n\n".join(" ".join(p["units"]) for p in paragraphs)
    tokens = [w for u in units for w in _words(u)]
    n_words = len(tokens) or 1
    lengths = [len(_words(u)) for u in units]
    body = [n for n in lengths if n >= 8]
    lowered = [w.lower().replace("’", "'") for w in tokens]
    low_text = joined.lower()

    hedges = sum(1 for w in lowered if w in HEDGES) + sum(
        len(re.findall(r"\b" + re.escape(p) + r"\b", low_text)) for p in HEDGE_PHRASES)
    boosters = sum(1 for w in lowered if w in BOOSTERS)

    anchors = len(NUM_RE.findall(joined)) + len(QUOTE_RE.findall(text))
    for unit in units:
        for word in unit.split()[1:]:
            token = word.strip(".,;:!?()[]\"'“”‘’")
            if not token or token in COMMON_CAPS:
                continue
            if (PROPER_RE.match(token) and not token.isupper() and len(token) > 1) or \
                    (token.isupper() and token.isalpha() and len(token) > 1):
                anchors += 1

    look = {key: [] for key in (
        "importance_without_mechanism", "vague_attribution", "abstract_actors",
        "hedge_booster_same_sentence", "absolute_claims", "contrastive_pivots",
        "demonstrative_kickers", "metaphor_flourishes", "participial_openers",
        "signpost_openers", "copula_displacement", "triads", "multi_dash_sentences",
        "overloaded_sentences", "definition_openers", "symmetrical_hedging",
        "stock_openers", "stock_closers", "model_lexis", "puffery_adverbs",
        "chatbot_residue", "model_register_cluster")}
    signpost_count = 0
    for p_index, paragraph in enumerate(paragraphs):
        for u_index, unit in enumerate(paragraph["units"]):
            words = {w.lower().replace("’", "'") for w in _words(unit)}
            first = (_words(unit) or [""])[0].lower()
            n = len(_words(unit))
            if IMPORTANCE.search(unit) and not MECHANISM.search(unit):
                look["importance_without_mechanism"].append(_short(unit))
            if VAGUE_ATTRIBUTION.search(unit):
                look["vague_attribution"].append(_short(unit))
            if ABSTRACT_ACTOR.search(unit):
                look["abstract_actors"].append(ABSTRACT_ACTOR.search(unit).group(0))
            if words & HEDGES and words & BOOSTERS:
                look["hedge_booster_same_sentence"].append(_short(unit))
            if ABSOLUTE.search(unit):
                look["absolute_claims"].append(ABSOLUTE.search(unit).group(0))
            for rx in CONTRASTIVE:
                look["contrastive_pivots"].extend(m.group(0) for m in rx.finditer(unit))
            if u_index > 0 and n <= 7 and DEMONSTRATIVE_KICKER.match(unit) and \
                    len(_words(paragraph["units"][u_index - 1])) > n:
                look["demonstrative_kickers"].append(_short(unit))
            look["metaphor_flourishes"].extend(m.group(0) for m in METAPHOR_FLOURISH.finditer(unit))
            if PARTICIPIAL.match(unit):
                look["participial_openers"].append(_short(unit, 90))
            if first in SIGNPOSTS:
                signpost_count += 1
                look["signpost_openers"].append(_short(unit, 90))
            look["copula_displacement"].extend(m.group(0) for m in COPULA.finditer(unit))
            look["triads"].extend(" / ".join(m) for m in TRIAD.findall(unit))
            if len(DASH_RE.findall(unit)) >= 2:
                look["multi_dash_sentences"].append(_short(unit))
            if n > 40:
                look["overloaded_sentences"].append(f"({n}w) " + _short(unit, 96))
    prose_paragraphs = [p for p in paragraphs if p["prose"]]
    openers = [p["units"][0] for p in prose_paragraphs if DEFINITION_OPENER.match(p["units"][0])]
    if len(prose_paragraphs) >= 3 and len(openers) >= 3 and len(openers) / len(prose_paragraphs) >= 0.5:
        look["definition_openers"] = [_short(u, 90) for u in openers]
    if re.search(r"\bon (?:the )?one hand\b", low_text) and "on the other hand" in low_text:
        look["symmetrical_hedging"] = ["on one hand ... on the other hand"]
    look["stock_openers"] = _phrase_hits(joined, STOCK_OPENERS)
    look["stock_closers"] = _phrase_hits(joined, STOCK_CLOSERS)
    look["model_lexis"] = [f"{w} (plainer: {LEXIS[w]})" for w in _phrase_hits(joined, LEXIS)]
    look["puffery_adverbs"] = sorted({w for w in lowered if w in PUFFERY_ADVERBS})
    look["chatbot_residue"] = _phrase_hits(joined, CHATBOT)
    register = _phrase_hits(joined, MODEL_REGISTER)
    if n_words >= 150 and len(register) >= 4:
        look["model_register_cluster"] = register

    dashes = len(DASH_RE.findall(joined))
    mattr = _mattr(tokens)
    trigram = _trigram_repeat_rate(tokens)
    return {
        "size": {"words": len(tokens), "sentences": len(units), "paragraphs": len(prose_paragraphs)},
        "measurements": {
            "mean_body_sentence_words": round(statistics.mean(body), 1) if body else 0.0,
            "body_sentence_cv": round(_cv(body), 3),
            "short_unit_share": round(sum(1 for n in lengths if n < 8) / len(lengths), 3) if lengths else 0.0,
            "paragraph_word_cv": round(_cv([sum(len(_words(u)) for u in p["units"]) for p in prose_paragraphs]), 3),
            "hedge_per_100": round(hedges / n_words * 100, 2),
            "booster_per_100": round(boosters / n_words * 100, 2),
            "anchors_per_100": round(anchors / n_words * 100, 2),
            "signpost_opener_share": round(signpost_count / len(units), 3) if units else 0.0,
            "dash_count": dashes,
            "lexical_diversity_mattr50": round(mattr, 3) if mattr is not None else None,
            "repeated_trigram_rate": round(trigram, 3) if trigram is not None else None,
        },
        "look_here": look,
    }


# ---------------------------------------------------------------- reporting

NOTES = [
    "No composite score, by design. Lists locate passages; they do not grade prose,",
    "detect authorship, or show whether the piece says anything. Read each passage.",
]


def _items(items, limit=8):
    lines = [f"      {item}" for item in items[:limit]]
    if len(items) > limit:
        lines.append(f"      ... {len(items) - limit} more")
    return lines


def report(stats, earlier=None):
    size = stats["size"]
    lines = [f"{size['words']} words, {size['sentences']} sentence units, {size['paragraphs']} prose paragraphs"]
    if size["words"] < 400:
        lines.append("  note: under 400 words; rhythm and density figures are unstable at this length.")
    lines.append("")
    if earlier:
        lines.append("MEASUREMENTS (earlier -> this version; descriptive, not targets)")
        for key, value in stats["measurements"].items():
            lines.append(f"  {key:<28} {earlier['measurements'][key]!s:>8} -> {value!s}")
        lines.append("  A falling anchors_per_100 can mean specifics were lost; check the rewrite against the source.")
    else:
        lines.append("MEASUREMENTS (descriptive, not targets)")
        for key, value in stats["measurements"].items():
            lines.append(f"  {key:<28} {value}")
        lines.append("  Compare versions of the same piece (--compare); there is no universal norm.")
    lines.append("")
    lines.append("LOOK HERE (hypotheses to read in context, not verdicts)")
    any_items = False
    for key, items in stats["look_here"].items():
        before = len(earlier["look_here"][key]) if earlier else None
        if not items and not before:
            continue
        any_items = True
        count = f"{before} -> {len(items)}" if earlier else str(len(items))
        lines.append(f"  {key} ({count})")
        lines.extend(_items(items))
    if not any_items:
        lines.append("  nothing listed by these limited checks")
    lines.append("")
    lines.extend(NOTES)
    return "\n".join(lines)


def _read(path, parser):
    try:
        if path == "-":
            return sys.stdin.buffer.read().decode("utf-8")
        with open(path, encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        parser.exit(2, f"prose_stats.py: cannot read {path}: {exc}\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="UTF-8 draft; '-' reads stdin")
    parser.add_argument("--compare", metavar="EARLIER", help="an earlier version of the same piece")
    parser.add_argument("--json", action="store_true", help="emit structured results")
    parser.add_argument("--include-quotes", action="store_true", help="measure quoted passages too")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    text = _read(args.path, parser)
    if not text.strip():
        parser.exit(2, "prose_stats.py: empty input\n")
    stats = analyze(text, args.include_quotes)
    earlier = analyze(_read(args.compare, parser), args.include_quotes) if args.compare else None
    if args.json:
        payload = {"schema_version": 1, **stats, "notice": " ".join(NOTES)}
        if earlier:
            payload["earlier"] = earlier
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(report(stats, earlier))
    return 0


if __name__ == "__main__":
    sys.exit(main())
