"""Claims-hygiene and registry-consistency tests (blueprint sections 0.2, 5.1, 7.2).

Scans the shipped Markdown, templates and data for stale or folk claims, using one regex list with
allow-listed negations: a claim pattern is a violation only when the same unit (one table row or one
sentence) carries no negation or qualifier from that claim's allow list. Generated examples and test
fixtures are excluded because they intentionally quote synthetic bad pages.

Also checks that every cited fact ID exists in references/current-facts.md, that fact rows carry a
label and a source, data freshness, the AI-crawler registry against its reference, the SD007 table
against data/structured-data.json, the Apache-2.0 modification headers and NOTICE.md. Assertions
about files another package has not written yet are skipped with a reason; they run once the files
exist.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Pattern, Sequence, Set, Tuple

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
sys.path.insert(0, str(TESTS_DIR))
try:  # shared network sentinel (tests/helpers.py)
    import helpers  # noqa: E402
except ImportError:  # pragma: no cover
    helpers = None

DATA_DIR = ROOT / "data"
REFERENCES_DIR = ROOT / "references"
TEMPLATES_DIR = ROOT / "templates"
FACTS = REFERENCES_DIR / "current-facts.md"
NOTICE = ROOT / "NOTICE.md"
AS_OF = "2026-11-01"
EXPECTED_DATA = ["rules.json", "thresholds.json", "ai-crawlers.json", "structured-data.json",
                 "content-lexicons.json", "ai-referrers.json", "search-updates.json"]
# Section 5.1 seed registry: F-AI-01..40 and F-T-01..53 must all exist.
SEED_FACTS = ["F-AI-%02d" % i for i in range(1, 41)] + ["F-T-%02d" % i for i in range(1, 54)]
FACT_LABELS = {"V", "S", "R", "P", "PP", "IR", "3P", "SR"}
EIGHT_SOURCES = ["claude-seo", "geo-seo-claude", "open-seo-mcp-skills", "eGEOagents", "aaron-marketing-skills",
                 "notfair", "geoptimize", "GEOFlow"]
APACHE_HEADER = re.compile(
    r"^(?:# )?<!-- Portions adapted from aaron-marketing-skills \(Apache-2\.0, Copyright 2024 Aaron He Zhu\)\. "
    r"Modified for SEO-GEO-god on 2026-11-01: (?P<summary>[^\n]+?)\. See NOTICE\.md\. -->$")
APACHE_MARKER = "Portions adapted from aaron-marketing-skills"
FACT_ID = re.compile(r"(?<![\w-])F-(?:AI|T)-\d{2}(?!\d)")
TEXT_SUFFIXES = {".md", ".json", ".txt", ".yml", ".yaml", ".csv", ".py", ".example", ".svg"}
EXCLUDED_PARTS = {"__pycache__", ".git", ".seo-geo-god", "fixtures"}
# Detection phrase lists (hype, AI artifacts, prompt-injection markers) quote bad phrasing on purpose.
CLAIM_EXEMPT_DATA = {"content-lexicons.json"}

# ----------------------------------------------------------------------------- forbidden claims

GENERAL_NEGATION = (
    r"\b(?:not|no|never|nor|neither|none|cannot|can't|don't|doesn't|isn't|aren't|won't|without|"
    r"unaffected|unrelated|myths?|misconceptions?|folklore|false|incorrect|wrong|stale|refuse[sd]?|refusing|"
    r"declines?|declined|avoid|instead|ignored|ignores|ignore|unused|retired|removed|deprecated|replaced|"
    r"dropped|stopped|ended)\b|no longer|does not|do not|is not|are not|has no|have no|nothing"
)


class Claim:
    """One forbidden-claim pattern.

    A unit violates the claim when every `require` regex matches it, `allow` (negations and
    qualifiers) does not match the unit itself, and `section_allow` (sources such as a fact ID or a
    URL, when the claim accepts them) does not match the enclosing section.
    """

    def __init__(self, key: str, description: str, require: Sequence[str], allow: str = GENERAL_NEGATION,
                 section_allow: Optional[str] = None, flags: int = re.I) -> None:
        self.key = key
        self.description = description
        self.require: List[Pattern[str]] = [re.compile(r, flags) for r in require]
        self.allow: Pattern[str] = re.compile(allow, re.I)
        self.section_allow: Optional[Pattern[str]] = re.compile(section_allow, re.I) if section_allow else None

    def violated_by(self, unit: str, section: str = "") -> bool:
        if not all(r.search(unit) for r in self.require) or self.allow.search(unit):
            return False
        return not (self.section_allow and self.section_allow.search(section))


SOURCE = r"F-(?:AI|T)-\d{2}|https?://|arxiv"
SOURCE_OR_LABEL = (r"F-(?:AI|T)-\d{2}|https?://|arxiv|\bheuristic\b|\bexample\b|\bsynthetic\b|\billustrative\b|"
                   r"\bhypothetical\b|\bREPLACE\b|\bplaceholder\b|\bneeds verification\b|\bunverified\b|"
                   r"\bthird-party\b|\b3P\b|\bclaimed\b|\bpreprint\b")

CLAIMS: List[Claim] = [
    Claim("google-extended-ai-overviews", "Google-Extended presented as controlling AI Overviews or AI Mode",
          [r"Google-Extended", r"\bAI (?:Overviews?|Mode)\b"]),
    Claim("gptbot-chatgpt-search", "GPTBot presented as the ChatGPT search crawler",
          [r"\bGPTBot\b", r"ChatGPT search|search (?:crawler|index|inclusion|results)"],
          allow=GENERAL_NEGATION + r"|OAI-SearchBot"),
    Claim("claudebot-claude-search", "ClaudeBot presented as the Claude search crawler",
          [r"\bClaudeBot\b", r"Claude search|search (?:crawler|index|inclusion|results)"],
          allow=GENERAL_NEGATION + r"|Claude-SearchBot"),
    Claim("llms-txt-ranking", "llms.txt presented as a ranking or citation factor",
          [r"llms\.txt", r"\b(?:rank(?:s|ing|ings)?|citations?|cited|boosts?|ranking factor|ranking signal)\b"],
          allow=GENERAL_NEGATION + r"|neither helps|optional|no evidence|unproven|no effect|convention"),
    Claim("faq-howto-rich-results", "FAQ or HowTo rich results promised",
          [r"\b(?:FAQ|FAQPage|HowTo|How-to)\b", r"rich (?:results?|snippets?)"],
          allow=GENERAL_NEGATION + r"|SD007|phas(?:ed|ing) out|2026-05-07|2023-09-14"),
    Claim("fid-current-metric", "FID presented as a current metric",
          [r"\bFID\b|First Input Delay"],
          allow=GENERAL_NEGATION + r"|former(?:ly)?|legacy|histor|superseded|\bwas\b|\buntil\b|2024-03-12|INP"
          r"|^\s*FID\s*$"),
    Claim("guarantee", "ranking, rich-result or citation guarantees",
          [r"\bguarantee(?:s|d|ing)?\b"],
          allow=GENERAL_NEGATION + r"|nobody|no one"),
    Claim("indexnow-google", "IndexNow presented as used by Google",
          [r"\bIndexNow\b", r"\bGoogle(?:bot)?\b"],
          allow=GENERAL_NEGATION + r"|Bing|Yandex|Naver|Seznam|Yep|participat"),
    Claim("indexing-api-general", "Indexing API presented as usable for general pages",
          [r"Indexing API"],
          allow=GENERAL_NEGATION + r"|JobPosting|job posting|BroadcastEvent|livestream|only|restricted|F-T-30"),
    Claim("title-pixel-limit", "fixed title pixel limit stated as a rule",
          [r"\btitles?\b|title link", r"~?\b\d{3}\s?(?:px|pixels?)\b"],
          allow=GENERAL_NEGATION + r"|heuristic|F-T-38|device width"),
    Claim("title-char-limit", "fixed title character limit stated as a Google rule",
          [r"\btitles?\b", r"\b\d{2}\s?(?:characters|chars)\b",
           r"\b(?:limit|maximum|max|must|cap|at most|no more than|cut off|cuts off|requires?|truncates? at)\b"],
          allow=GENERAL_NEGATION + r"|heuristic|informational|hint|F-T-38|device width|guideline|display"),
    Claim("description-char-limit", "fixed meta description length stated as a Google rule",
          [r"\bdescriptions?\b", r"\b1\d{2}\s?(?:characters|chars)\b",
           r"\b(?:limit|maximum|max|must|cap|at most|no more than|cut off|cuts off|requires?|truncates? at)\b"],
          allow=GENERAL_NEGATION + r"|heuristic|informational|hint|F-T-39|guideline|display"),
    Claim("keyword-density", "keyword density targets",
          [r"keyword density|density target|\b\d+(?:\.\d+)?\s?%\s+(?:keyword\s+)?density"]),
    Claim("lsi-keywords", "LSI keywords",
          [r"\bLSI\b"]),
    Claim("meta-keywords", "meta keywords presented as helping ranking",
          [r"meta keywords|meta name=[\"']?keywords|keywords meta"],
          allow=GENERAL_NEGATION + r"|F-T-40|no effect"),
    Claim("rel-next-prev", "rel=next/prev presented as used by Google",
          [r"rel=[\"']?(?:next|prev)|rel next/prev|rel=next/prev|rel next|rel prev"],
          allow=GENERAL_NEGATION + r"|F-T-25|F-T-40|Bing|other engines|accessibility|harmless"),
    Claim("studies-show", "unsourced 'studies show' phrasing",
          [r"(?<!what the )(?<!what )\b(?:studies|research|experts?|data)\s+(?:show|shows|prove|proves|confirms?)\b"],
          allow=GENERAL_NEGATION + r"|" + SOURCE_OR_LABEL + r"|\bif\b|\bwhether\b|\bclaims?\b",
          section_allow=SOURCE),
    Claim("uplift-numbers", "uplift percentages without a source",
          [r"(?:\+\d{1,3}(?:\.\d+)?\s?%|\b\d{1,3}(?:\.\d+)?\s?%\s+(?:more|higher|increase|boost|uplift|lift|better)\b|"
           r"\b(?:increase|boost|improve|lift|raise)s?\b[^.|]{0,40}\bby\s+\d{1,3}(?:\.\d+)?\s?%)"],
          allow=GENERAL_NEGATION + r"|" + SOURCE_OR_LABEL, section_allow=SOURCE),
    Claim("relative-date", "relative time words instead of absolute dates (section 0.2)",
          [r"\b(?:recently|last year|this year|next year|last month|next month|nowadays|these days)\b"],
          allow=r"[\"'`](?:recently|last year|this year|next year|last month|next month|nowadays|these days)[\"'`]"),
    Claim("ai-attribution", "AI attribution or generated-by footer",
          [r"generated (?:by|with) (?:Claude|ChatGPT|GPT|Gemini|Copilot|an? AI\b|AI\b)|Co-Authored-By|\U0001F916"],
          allow=r"[\"'`](?:generated (?:by|with)|Co-Authored-By)"),
]

FENCE_LINE = re.compile(r"^\s*(?:`{3,}|~{3,})")
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\[`(*\"'])")


def setUpModule() -> None:
    block = getattr(helpers, "block_network", None)
    if callable(block):
        block()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def claim_sources() -> List[Path]:
    """All Markdown (except tests/ and examples/), every template file and every data file."""
    paths: Set[Path] = set()
    for path in ROOT.rglob("*.md"):
        parts = path.relative_to(ROOT).parts
        if parts[0] not in ("tests", "examples") and not EXCLUDED_PARTS.intersection(parts):
            paths.add(path)
    if TEMPLATES_DIR.is_dir():
        paths.update(p for p in TEMPLATES_DIR.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    if DATA_DIR.is_dir():
        paths.update(p for p in DATA_DIR.glob("*.json") if p.name not in CLAIM_EXEMPT_DATA)
    return sorted(paths)


def json_strings(value: Any, context: str = "") -> Iterator[Tuple[str, str]]:
    """(string, enclosing object as JSON) pairs for every key and string value."""
    if isinstance(value, str):
        yield value, context
    elif isinstance(value, dict):
        here = json.dumps(value, ensure_ascii=False)[:20000]
        for key, item in value.items():
            yield str(key), here
            yield from json_strings(item, here)
    elif isinstance(value, list):
        for item in value:
            yield from json_strings(item, context)


def sections_by_line(lines: Sequence[str]) -> List[str]:
    """For each line, the text of its Markdown section (from the previous heading to the next)."""
    bounds = [i for i, line in enumerate(lines) if re.match(r"^#{1,6}\s", line)] + [len(lines)]
    out = [""] * len(lines)
    start = 0
    for end in bounds:
        block = "\n".join(lines[start:end])
        for i in range(start, end):
            out[i] = block
        start = end
    return out


def units(path: Path) -> Iterator[Tuple[int, str, str]]:
    """(line number, unit, section) triples: a table row is one unit, other lines are split into sentences."""
    text = read(path)
    if path.suffix == ".json" and path.parent == DATA_DIR:
        try:
            data = json.loads(text)
        except ValueError:
            data = None
        if data is not None:
            for value, context in json_strings(data):
                for piece in SENTENCE_SPLIT.split(value):
                    if piece.strip():
                        yield 0, piece, context
            return
    lines = text.splitlines()
    sections = sections_by_line(lines) if path.suffix == ".md" else [text] * len(lines)
    for index, line in enumerate(lines):
        if not line.strip() or FENCE_LINE.match(line):
            continue
        if line.lstrip().startswith("|"):
            yield index + 1, line, sections[index]
            continue
        for piece in SENTENCE_SPLIT.split(line):
            if piece.strip():
                yield index + 1, piece, sections[index]


def claim_violations(paths: Sequence[Path], claims: Sequence[Claim] = CLAIMS) -> List[str]:
    problems = []
    for path in paths:
        for number, unit, section in units(path):
            for claim in claims:
                if claim.violated_by(unit, section):
                    problems.append("%s:%s [%s] %s: %s" % (rel(path), number, claim.key, claim.description,
                                                          unit.strip()[:200]))
    return problems


# ----------------------------------------------------------------------------- registry helpers

def fact_rows() -> Dict[str, List[str]]:
    """Fact ID -> table cells for each `<a id="f-...">` row in current-facts.md."""
    rows: Dict[str, List[str]] = {}
    for line in read(FACTS).splitlines():
        match = re.match(r'^\|\s*<a id="(f-(?:ai|t)-\d{2})"></a>\s*(F-(?:AI|T)-\d{2})\s*\|(.*)\|\s*$', line)
        if match:
            cells = [c.strip() for c in match.group(3).split("|")]
            rows[match.group(1).upper()] = [match.group(2)] + cells
    return rows


def registry_ids() -> Set[str]:
    return {a.upper() for a in re.findall(r'<a id="(f-(?:ai|t)-\d{2})"></a>', read(FACTS))}


def cited_fact_files() -> List[Path]:
    out = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        parts = path.relative_to(ROOT).parts
        if EXCLUDED_PARTS.intersection(parts) or (parts[0] == "tests" and path.suffix == ".py"):
            continue  # test code may use synthetic IDs; tests/skill-scenarios.json is still checked
        out.append(path)
    return out


def markdown_section(text: str, heading_prefix: str) -> Optional[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match and match.group(2).strip().startswith(heading_prefix):
            level = len(match.group(1))
            body = []
            for following in lines[index + 1:]:
                nxt = re.match(r"^(#{1,6})\s", following)
                if nxt and len(nxt.group(1)) <= level:
                    break
                body.append(following)
            return "\n".join(body)
    return None


def first_table(text: str) -> List[List[str]]:
    rows: List[List[str]] = []
    started = False
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            started = True
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif started:
            break
    return rows


def apache_header_files() -> List[Path]:
    out = []
    for path in cited_fact_files():
        if path.suffix == ".py" or rel(path).startswith("tests/"):
            continue
        if APACHE_MARKER in read(path):
            out.append(path)
    return out


def header_line(path: Path) -> str:
    lines = read(path).splitlines()
    if lines and lines[0] == "---":  # header goes right after frontmatter
        try:
            end = lines.index("---", 1)
        except ValueError:
            return lines[0]
        lines = lines[end + 1:]
        lines = [line for line in lines if line.strip()] or [""]
    return lines[0] if lines else ""


# ----------------------------------------------------------------------------- tests

class ForbiddenClaimTests(unittest.TestCase):
    def test_sources_exist(self) -> None:
        self.assertGreater(len(claim_sources()), 20)

    def test_no_forbidden_claims(self) -> None:
        problems = claim_violations(claim_sources())
        self.assertEqual(problems, [], "forbidden claims found:\n" + "\n".join(problems))

    def test_patterns_catch_known_bad_phrasing(self) -> None:
        bad = {
            "google-extended-ai-overviews": "Block Google-Extended to remove your pages from AI Overviews.",
            "gptbot-chatgpt-search": "Allow GPTBot so your pages appear in ChatGPT search.",
            "llms-txt-ranking": "Publish llms.txt to boost your Google rankings.",
            "faq-howto-rich-results": "Add FAQPage markup to win FAQ rich results.",
            "fid-current-metric": "Keep FID under 100 ms on mobile.",
            "guarantee": "This change is guaranteed to get you cited.",
            "indexnow-google": "IndexNow notifies Google within minutes.",
            "indexing-api-general": "Submit every blog post through the Indexing API.",
            "title-pixel-limit": "Titles must stay under 600px.",
            "title-char-limit": "Google cuts off titles at 60 characters, so that is the limit.",
            "keyword-density": "Aim for a 2% keyword density.",
            "meta-keywords": "Add meta keywords to help ranking.",
            "studies-show": "Studies show that answer-first pages get cited more.",
            "uplift-numbers": "Answer-first intros increase CTR by 35%.",
            "relative-date": "Google recently changed how AI Mode is counted.",
            "ai-attribution": "Generated with Claude.",
        }
        by_key = {c.key: c for c in CLAIMS}
        for key, sentence in bad.items():
            with self.subTest(claim=key):
                self.assertTrue(by_key[key].violated_by(sentence), sentence)

    def test_negated_phrasing_is_allowed(self) -> None:
        good = [
            "Google-Extended does not affect AI Overviews or AI Mode.",
            "GPTBot is the training crawler; OAI-SearchBot governs ChatGPT search.",
            "Google Search ignores llms.txt; it is not a ranking factor.",
            "Google no longer shows FAQ rich results.",
            "INP replaced FID on 2024-03-12.",
            "Never guarantee rankings or citations.",
            "IndexNow is not used by Google.",
            "The Indexing API is only for JobPosting and BroadcastEvent pages.",
            "Google sets no fixed title length; 600px is folklore.",
            "Do not set keyword density targets.",
            "Google does not use meta keywords.",
            "The GEO paper reports +41% for quotations (F-AI-31).",
        ]
        for sentence in good:
            with self.subTest(sentence=sentence):
                hits = [c.key for c in CLAIMS if c.violated_by(sentence)]
                self.assertEqual(hits, [])


class FactRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        if not FACTS.is_file():
            self.skipTest("references/current-facts.md not written yet")

    def test_seed_facts_present(self) -> None:
        missing = sorted(set(SEED_FACTS) - registry_ids())
        self.assertEqual(missing, [], "section 5.1 fact IDs missing from current-facts.md")

    def test_fact_rows_have_label_and_source(self) -> None:
        rows = fact_rows()
        self.assertEqual(set(rows), registry_ids(), "every fact anchor must start a table row")
        for fid, cells in sorted(rows.items()):
            with self.subTest(fact=fid):
                self.assertEqual(cells[0], fid, "row text ID must equal its anchor")
                self.assertGreaterEqual(len(cells), 5, "row needs ID | fact | label | date | source")
                fact, label, source = cells[1], cells[2], cells[-1]
                self.assertTrue(fact, "empty fact text")
                tokens = set(re.findall(r"[A-Z0-9]+", label))
                self.assertTrue(tokens & FACT_LABELS, "label cell %r has no evidence label" % label)
                self.assertTrue("https://" in source or "URL to confirm" in source,
                                "source cell needs an https:// URL or 'URL to confirm': %r" % source)

    def test_every_cited_fact_id_exists(self) -> None:
        known = registry_ids()
        problems = []
        for path in cited_fact_files():
            if path == FACTS:
                continue
            for number, line in enumerate(read(path).splitlines(), 1):
                for fid in FACT_ID.findall(line):
                    if fid not in known:
                        problems.append("%s:%d cites unknown fact %s" % (rel(path), number, fid))
        self.assertEqual(problems, [])

    def test_fact_links_point_at_their_own_anchor(self) -> None:
        problems = []
        link = re.compile(r"\[(F-(?:AI|T)-\d{2})\]\(([^)\s]*)\)")
        for path in cited_fact_files():
            if path.suffix != ".md":
                continue
            for number, line in enumerate(read(path).splitlines(), 1):
                for fid, target in link.findall(line):
                    file_part, _, anchor = target.partition("#")
                    same_file = not file_part and path == FACTS
                    if not (file_part.endswith("current-facts.md") or same_file) or anchor != fid.lower():
                        problems.append("%s:%d %s links to %s" % (rel(path), number, fid, target))
        self.assertEqual(problems, [])


class DataFreshnessTests(unittest.TestCase):
    def test_data_files_are_as_of_2026_11_01(self) -> None:
        for name in EXPECTED_DATA:
            with self.subTest(data=name):
                path = DATA_DIR / name
                if not path.is_file():
                    self.skipTest("data/%s not written yet (owned by another package)" % name)
                data = json.loads(read(path))
                self.assertEqual(data.get("as_of"), AS_OF)

    def test_no_unexpected_data_files_without_as_of(self) -> None:
        for path in sorted(DATA_DIR.glob("*.json")):
            with self.subTest(data=path.name):
                self.assertEqual(json.loads(read(path)).get("as_of"), AS_OF)


class CrawlerRegistryTests(unittest.TestCase):
    def test_every_registry_token_appears_in_ai_crawlers_reference(self) -> None:
        registry = DATA_DIR / "ai-crawlers.json"
        reference = REFERENCES_DIR / "ai-crawlers.md"
        if not registry.is_file():
            self.skipTest("data/ai-crawlers.json not written yet")
        if not reference.is_file():
            self.skipTest("references/ai-crawlers.md not written yet")
        data = json.loads(read(registry))
        text = read(reference)
        tokens = [c["token"] for c in data.get("crawlers", [])] + [p["token"] for p in data.get("policy_tokens", [])]
        self.assertTrue(tokens)
        for token in tokens:
            with self.subTest(token=token):
                self.assertRegex(text, r"(?<![\w-])%s(?![\w-])" % re.escape(token))


class StructuredDataMatrixTests(unittest.TestCase):
    @staticmethod
    def since_value(value: Any) -> Optional[str]:
        if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
            return value.strip()
        return None  # "phasing out", null and other non-dates compare equal

    def matrix_rows(self) -> List[Tuple[str, Optional[str]]]:
        matrix = REFERENCES_DIR / "structured-data-matrix.md"
        if not matrix.is_file():
            self.skipTest("references/structured-data-matrix.md not written yet")
        body = markdown_section(read(matrix), "Types flagged as no rich result (SD007)")
        self.assertIsNotNone(body, "missing heading 'Types flagged as no rich result (SD007)'")
        table = first_table(body or "")
        self.assertGreaterEqual(len(table), 3, "SD007 table needs a header, a divider and rows")
        header = [h.lower() for h in table[0]]
        self.assertIn("type", header)
        self.assertIn("since", header)
        t_col, s_col = header.index("type"), header.index("since")
        return sorted((row[t_col], self.since_value(row[s_col])) for row in table[2:])

    def test_matrix_table_lists_the_blueprint_types(self) -> None:
        types = {t for t, _ in self.matrix_rows()}
        for required in ("FAQPage", "HowTo", "SpecialAnnouncement", "ClaimReview", "Occupation", "WebSite"):
            with self.subTest(type=required):
                self.assertIn(required, types)
        for never in ("Course", "Quiz", "Vehicle", "Book"):
            with self.subTest(type=never):
                self.assertNotIn(never, types, "%s must not be flagged as no rich result" % never)

    def test_matrix_table_equals_structured_data_json(self) -> None:
        rows = self.matrix_rows()
        path = DATA_DIR / "structured-data.json"
        if not path.is_file():
            self.skipTest("data/structured-data.json not written yet (owned by another package)")
        data = json.loads(read(path))
        expected = sorted((entry["type"], self.since_value(entry.get("since"))) for entry in data["no_rich_result"])
        self.assertEqual(rows, expected, "SD007 table must equal data/structured-data.json no_rich_result")


class LicensingTests(unittest.TestCase):
    def test_apache_headers_are_exact_and_first(self) -> None:
        files = apache_header_files()
        self.assertTrue(files, "no Apache-derived files found")
        for path in files:
            with self.subTest(file=rel(path)):
                match = APACHE_HEADER.match(header_line(path))
                self.assertIsNotNone(match, "the section 0.2 header must be the first line (after frontmatter)")
                if match:
                    self.assertTrue(match.group("summary").strip())
                    if path.suffix != ".txt":
                        self.assertFalse(header_line(path).startswith("# "), "'# ' prefix is only for .txt files")

    def notice(self) -> str:
        if not NOTICE.is_file():
            self.skipTest("NOTICE.md not written yet (owned by another package)")
        return read(NOTICE)

    def test_notice_lists_every_apache_derived_file(self) -> None:
        text = self.notice()
        for path in apache_header_files():
            with self.subTest(file=rel(path)):
                self.assertIn(rel(path), text)

    def test_files_listed_as_apache_derived_in_notice_carry_the_header(self) -> None:
        text = self.notice()

        def listed_paths(body: str) -> Set[str]:
            return {p for p in re.findall(r"[A-Za-z0-9_.\-/]+\.(?:md|txt|json|csv|yml|yaml)", body)
                    if (ROOT / p).is_file() and not p.startswith("licenses/") and p != "NOTICE.md"}

        # The Apache-2.0 section is the level-2+ heading mentioning Apache that lists the most files.
        candidates = []
        for line in text.splitlines():
            match = re.match(r"^#{2,6}\s+(.*Apache.*)$", line)
            if match:
                body = markdown_section(text, match.group(1).strip()) or ""
                candidates.append((len(listed_paths(body)), body))
        self.assertTrue(candidates, "NOTICE.md needs an Apache-2.0 section (## heading) listing modified files")
        listed = sorted(listed_paths(max(candidates, key=lambda c: c[0])[1]))
        self.assertTrue(listed, "no files listed in the Apache-2.0 section")
        for rel_path in listed:
            with self.subTest(file=rel_path):
                self.assertIsNotNone(APACHE_HEADER.match(header_line(ROOT / rel_path)),
                                     "listed as Apache-derived but lacks the section 0.2 header")

    def test_notice_names_all_sources_and_geoflow_ideas_only(self) -> None:
        text = self.notice()
        for source in EIGHT_SOURCES:
            with self.subTest(source=source):
                self.assertIn(source.lower(), text.lower())
        self.assertRegex(text, r"(?is)GEOFlow.{0,600}ideas[ -]only|ideas[ -]only.{0,600}GEOFlow")


if __name__ == "__main__":
    unittest.main()
