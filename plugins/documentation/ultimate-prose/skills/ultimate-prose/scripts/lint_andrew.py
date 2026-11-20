#!/usr/bin/env python3
"""Advisory Andrew register overlay for the generic prose scanner.

Register conventions are preferences, not evidence of AI use or quality.
The user-selected channel and voice override defaults. No historical
sentence-length target is enforced. Thresholds were set in 4.5 against a
sample of his sent emails and posts (references/corpus-notes.md), so the
overlay flags departures from his habits rather than the habits themselves.
Read-only; standard library only.

Usage: python lint_andrew.py [draft.txt] --genre email --formality business
Flags: generic scanner options plus --formality natural|business|executive.
Default exits 0 on completed scans. --strict permits exit 1 only for explicit
typography conventions and clear profanity in external business/executive
prose. Code, source quotations and citations are masked by default.
"""

import argparse
import json
from pathlib import Path
import re
import sys
from dataclasses import asdict

# Resolve the sibling scanner even under `python -I` or from another directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint as base  # noqa: E402

FORMALITIES = ("natural", "business", "executive")

HARD_CASUAL = {
    "lmao", "lol", "idk", "tho", "yup", "fuck", "fucking", "fuckin",
    "shit", "shithole", "bullshit", "batshit", "moron", "dumbass",
    "dumbest", "balls",
}

CHAT_SHORTHAND = {"lmao", "lol", "idk", "tho", "yup"}

SOFT_CASUAL = {
    "insane", "crazy", "dumb", "stupid", "gamechanger", "game-changer",
    "dude", "scam of the century",
}

DIRECT_ATTACKS = (
    "you do realize",
    "are you seriously",
    "pretty disturbing you",
    "only an idiot",
)

EMPHASIS_CAPS = {
    "ACTUALLY", "ALL", "ANY", "BEST", "CLEARLY", "DEFINITELY", "EVERYONE",
    "EVERYTHING", "EXACTLY", "FAR", "HEAVILY", "HUGE", "LITERALLY",
    "MASSIVE", "MUCH", "NEED", "NEVER", "NOTHING", "ONLY", "REAL",
    "REALLY", "THE", "VERY", "WAY", "WILD", "WORST",
}

CONTRACTION_RE = re.compile(
    r"\b(?:i'm|i've|i'd|i'll|it's|that's|there's|we're|we've|they're|"
    r"don't|doesn't|didn't|can't|couldn't|wouldn't|shouldn't|won't|"
    r"isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't|would've|"
    r"could've|should've)\b",
    re.I,
)


def _add_at(findings, text, index, severity, category, rule):
    findings.append(base.make_finding(text, index, severity, category, rule))


def _add(findings, text, match, severity, category, rule):
    _add_at(findings, text, match.start(), severity, category, rule)


def _phrase_matches(text, phrase):
    return list(
        re.finditer(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.I)
    )


def _count_words(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def _paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def _sentence_count(text):
    return len(base.split_sentences(text))


def _add_threshold(findings, text, phrase, threshold, severity, category, rule):
    matches = _phrase_matches(text, phrase)
    if len(matches) > threshold:
        _add(
            findings,
            text,
            matches[threshold],
            severity,
            category,
            f"{rule}: {len(matches)} occurrence(s), limit {threshold}",
        )


def check_andrew(text, genre="generic", formality="business", strict=False,
                 include_quotes=False, allow_em_dash=False):
    genre = base.normalize_genre(genre)
    findings, cadence = base.check(text, genre=genre, allow_em_dash=allow_em_dash,
                                  include_quotes=include_quotes)
    if genre == "internal":
        return base.finalize_findings(findings, text, strict=strict), cadence
    prose = base.mask_sources(text, include_quotes=include_quotes)
    lower = prose.lower()
    word_count = _count_words(prose)
    paragraphs = _paragraphs(prose)

    # The 4.5 thresholds below follow the measured sample in corpus-notes.md:
    # they should flag a departure from Andrew's own habits, not the habits.
    # "Let me know if ..." is one of his ordinary email closes.
    if genre == "email" and formality != "executive":
        findings = [f for f in findings
                    if not (f.category == "banned-phrase" and '"let me know if"' in f.rule)]
    # One emphasis word is normal for him; the generic scanner reports each one.
    emphasis_budget = {"natural": 3, "business": max(1, word_count // 150), "executive": 0}[formality]
    generic_emphasis = [f for f in findings if f.category == "intensifier"]
    if len(generic_emphasis) <= emphasis_budget:
        findings = [f for f in findings if f.category != "intensifier"]

    # Casual residue. Natural mode may preserve authentic casual language,
    # but business and executive modes may not copy Reddit heat.
    for term in sorted(HARD_CASUAL, key=len, reverse=True):
        if formality == "natural" and term in CHAT_SHORTHAND:
            continue  # his own casual posts use these now and then
        for match in _phrase_matches(prose, term):
            severity = base.VIOLATION if formality != "natural" else base.WARNING
            _add(
                findings,
                prose,
                match,
                severity,
                "andrew-casual-residue",
                f'register candidate: "{term}"; check literal meaning and context',
            )

    for term in sorted(SOFT_CASUAL, key=len, reverse=True):
        for match in _phrase_matches(prose, term):
            if formality == "executive":
                severity = base.VIOLATION
            elif formality == "business":
                severity = base.WARNING
            else:
                continue
            _add(
                findings,
                prose,
                match,
                severity,
                "andrew-casual-residue",
                f'overheated or casual term: "{term}"',
            )

    for phrase in DIRECT_ATTACKS:
        for match in _phrase_matches(prose, phrase):
            severity = base.VIOLATION if formality != "natural" else base.WARNING
            _add(
                findings,
                prose,
                match,
                severity,
                "andrew-confrontation",
                f'possibly confrontational phrasing: "{phrase}"',
            )

    # All-caps words that function as emphasis rather than acronyms.
    for match in re.finditer(r"\b[A-Z]{2,}\b", prose):
        if match.group(0) in EMPHASIS_CAPS:
            _add(
                findings,
                prose,
                match,
                base.VIOLATION if formality != "natural" else base.WARNING,
                "andrew-all-caps",
                f'all-caps emphasis: "{match.group(0)}"',
            )

    # Andrew's authentic high-frequency markers are controlled, not erased.
    if formality == "natural":
        limits = {
            "obviously": 3,
            "literally": 3,
            "actually": 4,
            "basically": 3,
            "the fact that": 3,
            "not to mention": 2,
        }
    elif formality == "business":
        # He uses each of these about once in a longer email.
        limits = {
            "obviously": 1,
            "literally": 0,
            "actually": 1,
            "basically": 1,
            "the fact that": 1,
            "not to mention": 1,
        }
    else:
        limits = {
            "obviously": 0,
            "literally": 0,
            "actually": 0,
            "basically": 0,
            "the fact that": 0,
            "not to mention": 0,
        }

    for phrase, limit in limits.items():
        matches = _phrase_matches(prose, phrase)
        if len(matches) > limit:
            if formality == "executive" or len(matches) > limit + 1:
                severity = base.VIOLATION
            else:
                severity = base.WARNING
            _add(
                findings,
                prose,
                matches[limit],
                severity,
                "andrew-marker-density",
                f'marker "{phrase}": {len(matches)} occurrence(s); review emphasis and precision',
            )

    # Certainty markers require evidence. The linter cannot verify the evidence,
    # so it raises a review warning even when the term is technically allowed.
    certainty_terms = (
        "clearly", "definitely", "certainly", "undeniably", "guaranteed",
        "100%", "without a doubt", "painfully obvious", "pretty obvious",
    )
    if formality == "natural":
        # Owned opinion ("clearly the best", "definitely") is his casual voice.
        certainty_terms = ("guaranteed", "100%", "without a doubt")
    elif formality == "business":
        certainty_terms = tuple(t for t in certainty_terms if t != "definitely")
    for phrase in certainty_terms:
        for match in _phrase_matches(prose, phrase):
            nearby = lower[max(0, match.start() - 12):match.end() + 8]
            if phrase == "100%" and re.search(r"agree[sd]?\s+100%|100%\s+agree", nearby):
                continue  # agreement, not a factual claim
            severity = base.VIOLATION if formality == "executive" else base.WARNING
            _add(
                findings,
                prose,
                match,
                severity,
                "andrew-certainty",
                f'verify certainty marker: "{phrase}"',
            )

    # Repeated emphasis is a contextual review candidate, not a word quota.
    intensifier_pattern = re.compile(
        r"\b(?:really|genuinely|truly|honestly|very|extremely|absolutely)\b",
        re.I,
    )
    intensifiers = list(intensifier_pattern.finditer(prose))
    limit = emphasis_budget
    if len(intensifiers) > limit:
        _add(
            findings,
            prose,
            intensifiers[limit],
            base.WARNING if formality != "executive" else base.VIOLATION,
            "andrew-intensifier-budget",
            f"{len(intensifiers)} emphasis word(s); check whether each adds useful degree or warmth",
        )

    # Repeated sentence openings may be intentional; review rather than prohibit.
    initial_connectors = list(re.finditer(r"(?m)(?:^|[.!?]\s+)(And|But)\b", prose))
    connector_limit = 4 if formality == "natural" else (2 if formality == "business" else 1)
    if len(initial_connectors) > connector_limit:
        _add(
            findings,
            prose,
            initial_connectors[connector_limit],
            base.WARNING,
            "andrew-opener-density",
            f"sentence-initial And/But repeated {len(initial_connectors)} times",
        )

    # Too many sentence openings with I can turn proof into biography. About a
    # quarter of his sentences open this way, so the check is a share, and it
    # needs enough sentences to mean something.
    i_openers = list(re.finditer(r"(?m)(?:^|[.!?]\s+)I\b", prose))
    total_sentences = _sentence_count(prose)
    i_share = {"natural": 0.6, "business": 0.5, "executive": 0.4}[formality]
    if total_sentences >= 6 and len(i_openers) > i_share * total_sentences:
        _add(
            findings,
            prose,
            i_openers[len(i_openers) // 2],
            base.WARNING,
            "andrew-i-opener",
            f'{len(i_openers)} of {total_sentences} sentences open with "I"',
        )

    # Parentheticals are authentic, but business prose should not bury decisions.
    parentheticals = list(re.finditer(r"\([^()\n]{2,}\)", prose))
    parenthetical_limit = max(1, len(paragraphs))
    if formality == "executive":
        parenthetical_limit = max(1, len(paragraphs) // 2)
    if len(parentheticals) > parenthetical_limit:
        _add(
            findings,
            prose,
            parentheticals[parenthetical_limit],
            base.WARNING,
            "andrew-parenthetical-density",
            f"parenthetical density: {len(parentheticals)} across {len(paragraphs)} paragraph(s)",
        )

    # Semicolons are rare in his writing (about one per 2,500 words of email);
    # a period, a comma, or "and" is his usual join.
    semicolons = list(re.finditer(r";", prose))
    if (genre not in {"docs", "academic"} and len(semicolons) >= 2
            and len(semicolons) > word_count / 150):
        _add(
            findings,
            prose,
            semicolons[1],
            base.WARNING,
            "andrew-semicolon",
            f"{len(semicolons)} semicolons in {word_count} words; he usually joins with a period, a comma, or 'and'",
        )

    # Plus signs between words are common in his casual posts.
    for match in re.finditer(r"(?<=[A-Za-z0-9])\+(?=[A-Za-z0-9])", prose):
        if formality == "natural":
            break
        _add(
            findings,
            prose,
            match,
            base.WARNING,
            "andrew-plus-join",
            'casual plus-sign join; write "and" or use a standard slash',
        )

    # Exclamation points. A warm email reply may use one.
    exclaims = list(re.finditer(r"!", prose))
    exclaim_limit = 3 if formality == "natural" else (1 if formality == "business" else 0)
    if len(exclaims) > exclaim_limit:
        _add(
            findings,
            prose,
            exclaims[exclaim_limit],
            base.VIOLATION if formality != "natural" else base.WARNING,
            "andrew-exclamation-budget",
            f"{len(exclaims)} exclamation point(s); inspect emphasis and relationship context",
        )

    # Genuine multi-part questions are useful in support and correspondence.
    # Question count is not a quality diagnostic.
    external_genres = {"email", "linkedin", "tweet", "marketing", "cover_letter"}

    # A long paragraph may merit a boundary if the subject or decision changes.
    for paragraph in paragraphs:
        sentence_count = _sentence_count(paragraph)
        if sentence_count > 6 and formality != "natural":
            start = prose.find(paragraph)
            if start >= 0:
                _add_at(
                    findings,
                    prose,
                    start,
                    base.WARNING,
                    "andrew-long-paragraph",
                    f"paragraph contains {sentence_count} sentences; consider a boundary "
                    f"if the topic or decision changes",
                )

    # Profile statistics describe a corpus, never a sentence-length quota.
    # The generic scanner already supplies sample-aware advisory cadence.
    # Andrew's stated diagnostic for business prose over about 100 words is a
    # mean near 17 to 24 words. It is recorded as a note, never as a finding,
    # and nothing should be stretched or split to reach it.
    if (formality == "business" and cadence.status == "review"
            and not 17 <= cadence.mean_len <= 24):
        cadence.notes.append(
            f"Mean sentence length is {cadence.mean_len:.1f} words; the stated business "
            "diagnostic is about 17 to 24. Inspect whether related thoughts are joined "
            "and overloaded ones split; do not edit to reach a number.")

    # His emails end "Best regards," and his full name, even on a two-word reply.
    if (genre == "email" and formality != "natural" and word_count >= 5
            and not re.search(r"(?mi)^[ \t]*(best regards|thanks|thank you),?[ \t]*$", text)):
        cadence.notes.append(
            "No sign-off line found. His sent emails close with 'Best regards,' and his "
            "full name on the next line; add it unless the thread or the user says otherwise.")

    # External prose with no contractions can sound stiff and unlike Andrew.
    if (
        formality == "business"
        and genre in external_genres
        and word_count >= 200
        and not CONTRACTION_RE.search(lower)
    ):
        findings.append(
            base.Finding(
                severity=base.WARNING,
                category="andrew-stiff-register",
                rule="no contractions in 200+ words; keep formal wording if it fits the recipient",
                line=1,
                snippet=base.snippet_at(prose, 0),
            )
        )

    # This narrow convention is activated only by an explicit --strict run.
    # Ambiguous casual terms (e.g. balls, dumb, crazy) remain review candidates.
    clear_profanity = {"fuck", "fucking", "fuckin", "shit", "shithole",
                       "bullshit", "batshit", "dumbass"}
    external_business = formality != "natural" and genre in {
        "generic", "email", "linkedin", "marketing", "cover_letter", "pr"}
    if external_business:
        for finding in findings:
            if finding.category == "andrew-casual-residue" and any(
                    f'"{term}"' in finding.rule for term in clear_profanity):
                finding.convention = True
    return base.finalize_findings(findings, text, strict=strict), cadence


def main():
    ap = argparse.ArgumentParser(description="ultimate-prose Andrew voice linter")
    ap.add_argument("path", nargs="?", help="file to scan (default: stdin)")
    ap.add_argument("--genre", default="generic", choices=base.GENRES)
    ap.add_argument("--formality", default="business", choices=FORMALITIES)
    ap.add_argument("--allow-em-dash", action="store_true")
    ap.add_argument("--strict", action="store_true", help="nonzero exit for explicit typography/profile conventions only")
    ap.add_argument("--include-quotes", action="store_true", help="scan quoted source passages too")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--detect", action="store_true",
                    help="audit report: pattern, quoted line, fix; no authorship verdict")
    ap.add_argument("--max-examples", type=int, default=3)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.max_examples < 1:
        ap.error("--max-examples must be at least 1")

    if args.path:
        try:
            with open(args.path, encoding="utf-8", errors="replace", newline="") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"cannot read {args.path}: {exc}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.buffer.read().decode("utf-8", errors="replace")

    if not text.strip():
        print("empty input", file=sys.stderr)
        return 2

    findings, cadence = check_andrew(
        text,
        genre=args.genre,
        formality=args.formality,
        strict=args.strict,
        include_quotes=args.include_quotes,
        allow_em_dash=args.allow_em_dash,
    )

    if args.json:
        print(json.dumps(base.json_payload(findings, cadence, args.genre,
                                          formality=args.formality, strict=args.strict),
                         indent=2, ensure_ascii=False))
        return base.strict_exit(findings)

    print(f"Andrew register: {args.formality}")
    if args.detect:
        return base.report_detect(findings, cadence, max(args.max_examples, 5))
    return base.report(
        findings,
        cadence,
        max_examples=args.max_examples,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    sys.exit(main())
