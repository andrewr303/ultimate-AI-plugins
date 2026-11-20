#!/usr/bin/env python3
"""Advisory prose scanner; standard library only.

The scan finds review candidates, not grammatical errors or evidence of AI
use. Read a file or stdin; it never modifies or transmits the draft.

Usage: python lint.py [draft.txt] --genre email [--json | --detect]
Genres include x (alias of tweet) and internal. Quoted source passages,
code, citations, URLs and email addresses are excluded by default.
--include-quotes scans quotations too; code and technical tokens stay masked.
--allow-em-dash overrides the default dash preference. --strict makes only
explicit typography conventions affect the exit status, never style/cadence.
Exit codes: 0 scan completed, 1 strict convention findings, 2 usage/read error.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field

# Windows consoles default to a codepage that cannot print em dashes or
# curly quotes, which would crash the report on exactly the text we care
# about most. Force UTF-8 and degrade gracefully.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

VIOLATION = "VIOLATION"
WARNING = "WARNING"


@dataclass
class Finding:
    severity: str
    category: str
    rule: str
    line: int
    snippet: str
    rule_id: str = ""
    evidence: str = ""
    origin: str = "heuristic"
    convention: bool = False
    offset_start: int = -1
    offset_end: int = -1

    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = "prose." + self.category
        if not self.evidence:
            self.evidence = self.snippet


@dataclass
class Cadence:
    sentences: int = 0
    words: int = 0
    mean_len: float = 0.0
    stdev_len: float = 0.0
    coef_var: float = 0.0
    longest_uniform_run: int = 0
    fragments: int = 0
    paragraphs: int = 0
    para_mean: float = 0.0
    para_stdev: float = 0.0
    short_share: float = 0.0
    joined_share: float = 0.0
    longest_short_run: int = 0
    notes: list = field(default_factory=list)
    status: str = "insufficient_sample"
    connector_cue_share: float = 0.0
    method: str = "heuristic punctuation/subordinator cues; not a clause parser"



# ---------------------------------------------------------------------------
# Pattern tables
# ---------------------------------------------------------------------------

# Phrase candidates. Word-boundary matches are contextual review suggestions.
BANNED_PHRASES = [
    # filler transitions and throat-clearing
    "at its core", "in today's world", "in todays world", "in a world where",
    "in an era of", "that said,", "with that in mind", "it's important to note",
    "it is important to note", "it's worth noting", "it is worth noting",
    "it bears mentioning", "needless to say", "it goes without saying",
    "what this means is", "the key takeaway", "let's explore", "let's dive",
    "first and foremost", "at the end of the day", "the fact of the matter",
    "without further ado", "here's what you need to know",
    "let's break this down", "let's break it down", "let's unpack",
    "in order to achieve", "due to the fact that", "at this point in time",
    "has the ability to", "in the event that",
    # meta commentary
    "in this essay", "this piece explores", "this article will",
    "in summary", "to summarize", "in conclusion", "as we've seen",
    "here are the key takeaways",
    # therapy voice
    "i hear you", "you're valid", "give yourself grace", "be kind to yourself",
    "hold space", "that sounds hard", "that sounds really hard",
    "it's okay to feel",
    # manufactured suspense / authority
    "here's the kicker", "here's the thing", "here's where it gets",
    "here's what most people miss", "the truth is simple",
    "nobody talks about", "what most people miss", "what nobody tells you",
    "make no mistake", "let me be clear", "the real question is",
    "here's what i mean", "here is what i mean", "i'll be honest",
    "here is the tension", "here's the tension", "worth naming",
    "the part nobody tells you", "here's the twist", "here is the twist",
    "sit with that", "that's not nothing", "that is not nothing",
    "the only question is", "the only thing that matters",
    "the uncomfortable truth", "the part everyone misses",
    "the part most people miss", "this is the part most people skip",
    "what most people get wrong", "what everyone gets wrong",
    "what if i told you", "think about it:", "plot twist",
    # interpretive metadiscourse: telling the reader what to notice
    "matters more than it sounds", "this distinction matters",
    "is not a footnote", "isn't a footnote", "this is not to say",
    "the key point is", "the key point here", "as you can see",
    "the important thing to understand", "what's important here",
    "pay attention to this", "read that again",
    # hype declaratives
    "this is huge", "changes everything", "paradigm shift",
    "will define the next decade", "will define the decade",
    "the future isn't coming", "the future is not coming",
    "it's already here", "it is already here", "and it's already here",
    # stock significance
    "serves as a reminder", "stark reminder", "a testament to",
    "testament to the", "rich tapestry", "gone are the days",
    "plays a vital role", "plays a key role", "plays a crucial role",
    "plays a pivotal role", "marking a pivotal", "evolving landscape",
    "indelible mark", "setting the stage for", "solidifies its position",
    "solidify its position", "underscores its significance",
    "underscores the significance", "cements its",
    # hedged confidence and stock openers
    "one might argue", "in many ways", "it's important to consider",
    "it is important to consider", "that being said", "looking ahead,",
    "against this backdrop", "zooming out,",
    # despite-challenges formula
    "despite these challenges", "despite its challenges",
    # cliches
    "the smoking gun", "a perfect storm", "move the needle",
    "double-edged sword", "tip of the iceberg",
    "between a rock and a hard place", "imagine a world where",
    # chatbot artifacts and sycophancy
    "i hope this helps", "great question", "you're absolutely right",
    "let me know if", "i hope this email finds you well",
    "please don't hesitate to reach out", "hope this helps",
    # knowledge-cutoff and gap-filling
    "up to my last training", "while specific details are limited",
    "based on available information", "maintains a low profile",
    "keeps personal details private", "prefers to stay out of the spotlight",
    # reassurance kickers
    "and that's okay", "and that's fine", "there's nothing wrong with that",
    "you're not alone", "it's completely normal",
    # patronizing analogy / pedagogical
    "think of it as", "let's take a closer look",
    # anthropomorphized abstractions
    "the data tells a story", "the numbers speak for themselves",
    "the market is telling us", "the data is clear", "the numbers don't lie",
    # closer zingers (fake gavel)
    "that's the whole game", "that's the job.", "that's the work.",
    "full stop.", "that's the point.", "and that's the point",
    "and that matters.",
    # 4.4 additions. Each family has a legitimate use; see references/tells.md.
    # chat exchange left in standalone text
    "of course!", "certainly!", "would you like me to", "should i continue",
    "excellent question", "that's a great point", "as an ai language model",
    # a stated gap or guess in place of a source
    "as of my last", "not publicly available", "not widely documented",
    "it is believed that",
    # answering an objection nobody raised
    "i'm not saying", "don't get me wrong", "a tempting approach would be",
    "one might be tempted to", "it would be easy to just",
    # narrated candor and salience
    "to be honest", "honest answer", "truth be told", "let's be honest",
    "real talk", "why this matters", "here's the catch",
    "but here's the twist",
    # naming what an example already showed
    "this shows the importance of", "the message was clear",
    "it was a lesson in",
    # stock significance and uplift
    "reflects a broader", "exciting times ahead", "the future looks bright",
    "a step in the right direction", "deeply rooted", "enduring legacy",
    "key turning point", "marks a pivotal", "marks a significant",
    "stands as a testament",
    # reasoning narration
    "let me think step by step", "here's my thought process",
    # more cliches
    "low-hanging fruit", "boil the ocean", "table stakes",
    "now more than ever", "the new normal", "thrilled to share",
    "excited to announce", "unpopular opinion", "hot take",
]

# Often-empty phrases. Warnings, not violations: each has a legitimate use,
# but most instances delay the point. Cut unless the sentence still earns
# its place with the phrase in it.
EMPTY_PHRASES = [
    "the reality is", "the truth is", "when it comes to", "in terms of",
    "with regard to", "with regards to", "in order to", "going forward",
    "in this article", "in this post", "in other words", "to be clear",
    "it should be noted", "as mentioned", "as noted above",
    "significantly improves", "significantly improved", "dramatically improves",
    "greatly improves", "vastly improves", "improves efficiency",
    "improved efficiency", "enhances productivity", "boosts productivity",
    # 4.4 additions: forced balance, scope disclaimers, vague endorsement
    "on the one hand", "good arguments on both sides", "not an exhaustive",
    "this is a simplified view", "i'm oversimplifying", "i should caveat",
    "worth a look", "worth your time", "worth checking out",
]

# Pleonastic pairs: two near-synonyms joined by "and" to fake precision.
PLEONASTIC_PAIRS = [
    "clear and concise", "simple and straightforward", "safe and secure",
    "fast and efficient", "quick and easy", "open and honest",
    "each and every", "first and foremost", "any and all",
    "tried and tested", "tried and true", "full and complete",
    "clean and simple", "smooth and seamless", "powerful and flexible",
]

# Soft vocabulary. Scored by density rather than raw count, since several
# are legitimate in some registers (robust in statistics, ecosystem in
# biology, framework in software).
SOFT_WORDS = [
    "delve", "delving", "tapestry", "unpack", "seamless", "seamlessly",
    "robust", "crucial", "vital", "pivotal", "paramount", "foster",
    "fostering", "harness", "harnessing", "leverage", "leveraging",
    "elevate", "elevating", "empower", "empowering", "resonate", "resonates",
    "myriad", "plethora", "nuanced", "multifaceted", "holistic",
    "transformative", "game-changer", "game changer", "landscape",
    "navigate", "navigating", "realm", "beacon", "cornerstone", "linchpin",
    "boasts", "profound", "profoundly", "ultimately", "moreover",
    "furthermore", "additionally", "notably", "arguably", "essentially",
    "undeniably", "journey", "deep dive", "cultivate", "underscore",
    "underscores", "underscoring", "highlighting", "quietly", "subtly",
    "deftly", "effortlessly", "fundamentally", "utilize", "utilizing",
    "streamline", "streamlines", "streamlining", "paradigm", "synergy",
    "ecosystem", "intricate", "intricacies", "interplay", "showcase",
    "showcases", "showcasing", "vibrant", "compelling", "meticulous",
    "meticulously", "unwavering", "commendable", "garner", "cutting-edge",
    "groundbreaking", "renowned", "breathtaking", "nestled", "stunning",
    "world-class", "state-of-the-art", "iconic", "ever-evolving", "embark",
    "embarking", "supercharge", "supercharged", "facilitate", "facilitates",
    "elevated", "beacon", "frictionless", "bolster", "bolstering", "spearhead",
    "spearheading", "illuminate", "illuminating", "comprehensive", "encompass",
    "surpass", "catalyze", "grapple", "grappling", "unleash", "unlock", "unlocks",
    "unlocking", "trove", "noteworthy", "captivating", "revolutionize",
    "revolutionizing", "versatile", "innovative",
    # 4.4 additions: the rest of Andrew's stated avoid list, then words several
    # public catalogs agree are overused in abstract prose.
    "bolsters", "bolstered", "illuminates", "streamlined", "encompasses",
    "encompassing", "cultivating", "embody", "embodies", "epitomize",
    "epitomizes", "spearheaded", "indelible", "endeavor", "endeavour",
    "advent", "underpin", "underpins", "reimagine", "galvanize", "elucidate",
    "quintessential", "overarching", "burgeoning", "nascent", "poised",
    "daunting", "bustling", "impactful", "actionable", "learnings",
    "unparalleled", "testament", "north star", "flywheel",
]

# Literal technical uses that the docs genre leaves alone.
TECHNICAL_TERMS = {
    "robust", "comprehensive", "seamless", "seamlessly", "ecosystem",
    "leverage", "leveraging", "facilitate", "facilitates", "underpin",
    "underpins", "streamline", "streamlines", "streamlining", "streamlined",
    "navigate", "navigating", "paradigm", "utilize", "utilizing",
}

# Read where only code is masked, so a quotation or link still counts.
DRAFT_ARTIFACTS = [
    (r"\[(?:Your|Insert|Recipient|Company|Client|First|Last|Full)\b[^\]\n]{0,60}\](?![(\[:])"
     r"|\[(?:Name|Date|Title|Link|URL|TBD|TODO)\](?![(\[:])|\[TK(?::[^\]\n]*)?\]",
     "open placeholder; fill it from a source or tell the reader what is missing"),
    (r"contentReference\[oaicite:[^\]\n]*\](?:\{[^}\n]*\})?|\[oaicite:[^\]\n]*\]|\boai_citation\b"
     r"|\bturn\d+(?:search|view|news|file)\d+\b|\[attached_file:\d+\]"
     r"|[?&]utm_source=(?:chatgpt|openai|copilot|claude|grok|gemini|perplexity)(?:\.com|\.ai)?\b",
     "tool markup or tracking parameter; remove it or restore the real citation"),
    ("[\u200b\u200c\u2060]|(?<!^)\ufeff", "invisible zero-width character"),
]

INTENSIFIERS = [
    "very", "truly", "really", "incredibly", "extremely", "absolutely",
    "deeply", "remarkably", "undoubtedly", "certainly", "genuinely",
]

# Vague attribution: a claim borrowed from an unnamed authority.
VAGUE_ATTRIBUTION = [
    r"\b(?:studies|research)\s+(?:show|shows|suggest|suggests|indicate|indicates|prove|proves)\b",
    r"\bexperts?\s+(?:say|agree|believe|argue|warn|note)\b",
    r"\b(?:some\s+)?critics\s+(?:say|argue|claim)\b",
    r"\bobservers\s+(?:say|note|believe|have\s+noted)\b",
    r"\b(?:many|some)\s+(?:people\s+)?(?:say|believe|argue)\b",
    r"\bit\s+is\s+widely\s+(?:believed|accepted|known)\b|\bwidely\s+regarded\s+as\b",
    r"\baccording\s+to\s+(?:research|experts|studies|reports)\b",
    r"\bindustry\s+reports\b|\beveryone\s+knows\b|\bit(?:'s|\s+is)\s+well\s+known\b",
]

# An abstraction presented as the actor. Fine when the actor is unknown or
# irrelevant; otherwise name the person, team, system, or measurement.
ABSTRACT_ACTOR_RE = (
    r"\bthe\s+(?:data|numbers|market|industry|research|culture|conversation|decision|"
    r"technology|algorithm|process|architecture|landscape)\s+(?:tells?|told|shows?\s+us|"
    r"says|said|wants?|decides?|decided|demands?|rewards?|punishes|speaks?|knows?|"
    r"emerges?|listens?)\b")

# Importance claims need a mechanism, example, or evidence in the same sentence.
IMPORTANCE_RE = (
    r"\b(?:important|crucial|vital|pivotal|transformative|groundbreaking|remarkable|"
    r"unprecedented|revolutionary|game-changing|profound|monumental|"
    r"(?<!statistically\s)significant)\b")
MECHANISM_RE = (
    r"\d|\b(?:because|by|through|which|so\s+that|therefore|means|allows?|enables?|"
    r"results?\s+in|leads?\s+to|causes?|prevents?|reduces?|increases?|measured|"
    r"according\s+to|for\s+example|such\s+as|since|when|if|unless|e\.g\.)\b")

# Plainer alternatives; legal and technical registers may need the original.
PLAIN_WORDS = {
    "a number of": "some, many, or the number", "a majority of": "most",
    "the majority of": "most", "a large number of": "many",
    "at the present time": "now", "prior to": "before", "subsequent to": "after",
    "in the near future": "soon, or the date", "on a regular basis": "regularly",
    "is able to": "can", "are able to": "can", "have the ability to": "can",
    "for the purpose of": "to, or for", "in spite of the fact that": "although",
    "with the exception of": "except", "in conjunction with": "with",
    "whether or not": "whether", "commence": "start", "ascertain": "find out",
    "endeavor": "try", "endeavour": "try",
}

# Plainer choices for frequent stock vocabulary (shown in the finding).
PLAINER = {
    "delve": "look at", "delving": "looking at", "tapestry": "name the actual thing",
    "realm": "name the actual thing", "landscape": "name the actual thing",
    "underscore": "show", "underscores": "shows", "underscoring": "showing",
    "leverage": "use", "leveraging": "using", "seamless": "easy, or say how",
    "seamlessly": "easily, or say how", "frictionless": "easy, or say how",
    "robust": "reliable, or say how", "crucial": "important, or say why",
    "pivotal": "important, or say why", "vital": "important, or say why",
    "navigate": "handle", "navigating": "handling", "foster": "build",
    "fostering": "building", "cultivate": "build", "elevate": "improve",
    "elevating": "improving", "unlock": "enable", "unlocks": "enables",
    "unlocking": "enabling", "empower": "let", "empowering": "letting",
    "myriad": "many", "plethora": "many", "showcase": "show", "showcases": "shows",
    "showcasing": "showing", "bolster": "strengthen", "garner": "get",
    "game-changer": "say the concrete change", "game changer": "say the concrete change",
    "utilize": "use", "utilizing": "using", "facilitate": "help", "facilitates": "helps",
    "spearheading": "leading", "comprehensive": "complete, or say what it covers",
    "illuminate": "explain", "encompass": "include", "intricate": "detailed",
    "meticulous": "careful", "multifaceted": "name the parts",
}

# Contrast constructions to review for decorative repetition; real contrasts are useful.
PIVOT_PATTERNS = [
    (r"\bisn'?t\s+(just\s+|only\s+|merely\s+|simply\s+)?about\b[^.?!\n]{0,80}[.?!,;]?\s*(it'?s|it\s+is)\s+about\b",
     'reversal pivot: "isn\'t about X ... it\'s about Y"'),
    (r"\bit'?s\s+not\b[^.?!\n]{1,60}[.?!,;]\s*(it'?s|it\s+is)\b",
     'reversal pivot: "it\'s not X. it\'s Y"'),
    (r"\bnot\s+(just|only|merely|simply|solely)\s+[^.,;\n]{1,50},?\s+but\b",
     'reversal pivot: "not just X, but Y"'),
    (r"\bnot\s+because\b[^.?!\n]{1,80}[.?!]?\s*(but\s+)?because\b",
     'reversal pivot: "not because X. because Y"'),
    (r"\b\w[\w\s]{0,40}\s+isn'?t\s+the\s+(problem|point|issue|story|answer)[.;]\s*\w[\w\s]{0,40}\s+is\b",
     'reversal pivot: "X isn\'t the problem. Y is"'),
    (r"\bnot\s+only\b[^.?!\n]{1,80}\bbut\s+(also\s+)?",
     '"not only ... but also" scaffolding'),
    (r"\bnot\s+\w[\w\s]{0,30}[.,]\s*not\s+\w[\w\s]{0,30}[.,]\s*(just|only)\b",
     'countdown negation: "Not X. Not Y. Just Z."'),
    (r"\bless\s+about\b[^.;\n]{2,60}\b(than|and\s+more\s+about)\b",
     'reversal pivot escape hatch: "less about X than Y"'),
    (r"\bmore\s+than\s+(just|a\s+mere|simply)\b",
     'reversal pivot: "more than just X"'),
    (r"\bthe\s+(question|point|issue|problem|goal)\s+is(n'?t|\s+not)\s+(whether|about|just|if)\b",
     'reversal pivot: "the question isn\'t X"'),
    (r"\b(doesn'?t|don'?t|didn'?t|won'?t)\s+(just|merely|simply)\s+[^.;\n]{2,60}\b(it|they|he|she|we)\b",
     'reversal pivot: "doesn\'t just X, it Y"'),
    (r"\bno\s+\w+,\s*no\s+\w+(,\s*no\s+\w+)?[,.]?\s*just\b",
     'tailing negation stack: "no X, no Y, just Z"'),
    (r"\bwe'?re\s+not\s+(just\s+)?(talking about|looking at|dealing with)\b",
     'reversal pivot: "we\'re not just talking about X"'),
    (r"\bless\s+\w+,\s*more\s+\w+\b",
     'compressed pivot: "less X, more Y"'),
    (r"\bthink\s+\w[\w\s]{0,25},\s*not\s+\w+",
     'compressed pivot: "think X, not Y"'),
    (r"(?:^|[.!?]\s+)(this|that|it)\s+(?:(?:is|was)n'?t|'s\s+not)\s+(a|an)\s+\w+[.;]\s*(this|that|it)(?:\s+(?:is|was)|'s)\s+(a|an)\b",
     'reversal pivot: "this isn\'t a X. it\'s a Y"'),
    (r"\bdon'?t\s+\w+\s+(?:it|them)\s*[,;:.]\s*\w+\s+(?:it|them)\b",
     'slogan contrast: "don\'t X it; Y it"'),
    # 4.4 additions: the same contrast staged across two sentences. These are
    # also the shapes an over-cut rewrite tends to produce.
    (r"\b(this|that|it)\s+(does\s+not|doesn'?t)\s+mean\b[^.?!\n]{1,120}[.?!]\s+it\s+means\b",
     'split pivot: "this does not mean X. it means Y"'),
    (r"(?:^|(?<=[.!?]\s)|(?<=\n))not\s+(?:just\s+|only\s+|merely\s+)?(?:a|an|the|about|because)\s+[^.?!\n]{1,40}[.?!]"
     r"\s+(?:a|an|the|about|because|it'?s|that'?s|they'?re)(?:\s+[^\s.?!]+){1,5}[.?!]",
     'fragment pivot: "Not the X. The Y."'),
]

# Subject-term variation candidates. This heuristic cannot establish that
# two terms share a referent; model, agent and tool may name distinct things.
SYNONYM_CLUSTERS = {
    "product": {"agent", "assistant", "tool", "system", "model", "bot",
                "platform", "product", "app", "software", "solution",
                "engine", "service", "feature"},
    "company": {"company", "firm", "startup", "business", "organization",
                "organisation", "team", "outfit", "venture"},
    "people": {"user", "users", "customer", "customers", "client", "clients",
               "buyer", "buyers", "reader", "readers", "audience"},
    "creator": {"creator", "creators", "influencer", "influencers",
                "talent"},
    "brand": {"brand", "brands", "sponsor", "sponsors", "advertiser",
              "advertisers"},
}

# Contextual review hints for --detect; no automatic deletions or rewrites.
FIX_HINTS = {
    "punctuation": "Apply the requested typography; preserve source quotations and user overrides.",
    "formatting-emoji": "Keep emoji when the requested tone or channel supports them.",
    "banned-phrase": "Check whether the phrase adds useful meaning, attribution, warmth or navigation; cut only filler.",
    "empty-phrase": "Keep useful relationship or navigation cues; replace vague magnitude only when a verified detail is available.",
    "pleonasm": "Check whether the terms add distinct meaning before removing either.",
    "redundant-acronym": "Check the intended meaning; use the acronym alone or its full expansion only if that preserves the context.",
    "pivot": "Preserve a real comparison; simplify only decorative or repetitive contrast.",
    "participle": "Keep a concrete operation or consequence; revise only empty significance commentary.",
    "copula": "Use the precise verb; serves as or acts as may describe a real role.",
    "concept-label": "Check whether the label is established or useful; define it when needed.",
    "self-question": "Keep a genuine question or useful framing; trim decorative suspense.",
    "colon-punch": "Keep useful labels, evidence and explanations; simplify only decorative repetition.",
    "colon-reveal": "Keep the colon if it introduces useful evidence or explanation; revise decorative suspense.",
    "false-range": "Keep real numerical ranges or useful coverage; trim only unsupported sweeps.",
    "triad": "Keep all necessary items; trim only redundant or decorative list padding.",
    "hedging": "Preserve each distinct uncertainty; remove only redundant qualifiers.",
    "intensifier": "Keep meaningful warmth, degree or emphasis; trim unsupported inflation.",
    "stock-vocab": "Preserve literal technical terms; replace vague promotional wording only when more precise language is available.",
    "stock-vocab-marketing": "Replace unsupported promotion with a verified benefit or mechanism when available.",
    "synonym-cycling": "First check whether these are distinct referents; repeat a term only when the referent is the same.",
    "formatting-bullet": "Keep lists when they help scanning; simplify only unnecessary decoration.",
    "formatting-bold": "Use the formatting requested by the user and supported by the channel.",
    "formatting-header": "Keep headings when they help navigation or the genre requires them.",
    "signposting": "Keep navigation needed by the reader; trim redundant announcements.",
    "formatting-broetry": "Keep intentional short paragraphs; combine them only when this improves the actual reading flow.",
    "engagement-bait": "Keep a genuine request for feedback; remove empty response bait.",
    "email-padding": "Match the relationship and thread; keep useful warmth or follow-up context.",
    "diff-anchored": "Keep change narration in PRs or release notes; describe current behavior in evergreen documentation.",
    "opening": "Check whether this opening gives the intended reader a useful start.",
    "ending": "Keep a useful action, implication, definition or courteous ending; trim empty restatement.",
    "fragment": "Short sentences may be complete; join only when meaning or flow improves.",
    "cadence": "Read the passage aloud; revise repetition only when it obscures the intended logic.",
    "anaphora": "Keep intentional emphasis or parallel instructions; revise accidental repetition.",
    "texture": "Check whether the logic is clear; join related sentences only when the connection is supported and improves reading.",
    "importance-claim": "Remove the emphasis and reread: if the claim still names an actor, mechanism, result or limit, state that and let the reader judge; otherwise ask for the evidence or cut.",
    "vague-attribution": "Name the supplied source and keep its uncertainty, ask for the source, or cut the claim. Do not upgrade 'may' to 'will' or 'some' to 'most'.",
    "abstract-actor": "Name the person, team, system or measurement that acts; keep the abstraction when the actor is unknown, protected or irrelevant.",
    "plain-word": "Use the plainer wording when it keeps the meaning; legal, academic and technical registers may require the original.",
    "kicker": "Cut the verdict or fold it into the previous sentence; keep a short beat the author would defend.",
    "flourish": "State the plain relation the image stands for unless the image itself carries meaning the author wants.",
    "false-balance": "If the author holds a view, state it and give the strongest real objection its own space.",
    "draft-artifact": "Resolve the placeholder or remove the tool artifact; never fill a gap with an unsupported detail.",
    "borrowed-authority": "Name the one source and what it said, if supplied; otherwise keep the claim as modest as its support.",
    "vague-quantity": "Give the count or the examples when the source has them; a vague quantity can be the honest one.",
    "announcement": "Let the sentence carry its own weight; keep a flag that changes what the reader should do.",
    "transition-density": "Keep a connective that names a real relation; drop one that only starts the paragraph.",
}

TRAILING_PARTICIPLES = [
    "highlighting", "underscoring", "emphasizing", "reminding us",
    "making it clear", "raising questions", "cementing", "signaling",
    "showcasing", "demonstrating the importance", "reflecting the",
    "reflecting broader", "proving that", "ensuring that", "symbolizing",
    "fostering", "cultivating", "contributing to the", "encompassing",
    "illustrating", "reinforcing", "signifying", "representing a",
    "solidifying", "paving the way",
]

# CLI genre identifiers. Genre changes review context, never proves quality.
GENRES = ["generic", "academic", "tweet", "x", "reddit", "linkedin", "email",
          "essay", "marketing", "docs", "cover_letter", "pr", "fiction", "internal"]


def normalize_genre(genre):
    return "tweet" if genre == "x" else genre


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _blank(match):
    """Mask content without changing source offsets or line numbers."""
    return re.sub(r"[^\n]", " ", match.group(0))


def strip_code(text):
    """Mask fenced/inline code, preserving newlines and character offsets."""
    # A closing fence must use the opening character and at least its length.
    lines = text.splitlines(keepends=True)
    fence = None
    result = []
    for line in lines:
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence is None and marker:
            fence = marker.group(1)
            result.append(re.sub(r"[^\n]", " ", line))
        elif fence is not None:
            result.append(re.sub(r"[^\n]", " ", line))
            if re.match(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$", line):
                fence = None
        else:
            result.append(line)
    text = "".join(result)
    return re.sub(r"(`+)(?!`)([^\n]*?)(?<!`)\1(?!`)", _blank, text)


def mask_sources(text, include_quotes=False):
    """Exclude source material; this is boundary hygiene, not a truth check.

    Blockquotes and paired quoted passages are source material by default.
    Author-year/numeric citation markers and technical address tokens remain
    excluded even when --include-quotes is selected. Markdown link labels
    remain prose; only their destination is masked.
    """
    scan = strip_code(text)
    if not include_quotes:
        scan = re.sub(r"(?m)^ {0,3}>[^\n]*", _blank, scan)
        for pattern in (r'"(?:[^"\\]|\\.)*"', r'“[^”]*”',
                        r"(?<!\w)'[^'\n]*\s[^'\n]*'(?!\w)", r"‘[^’\n]*’"):
            scan = re.sub(pattern, _blank, scan)
    scan = re.sub(r"\[(?:\d+[a-z]?(?:\s*[,;–-]\s*\d+[a-z]?)*|\^[-\w]+)\]", _blank, scan)
    author_year = (r"[A-Z][A-Za-z'’-]+(?:\s+(?:et al\.|(?:and|&)\s+[A-Z][A-Za-z'’-]+))?,?"
                   r"\s+(?:19|20)\d{2}[a-z]?(?:,\s*(?:pp?\.\s*)?\d+(?:[-–]\d+)?)?")
    scan = re.sub(r"\(" + author_year + r"(?:;\s*" + author_year + r")*\)", _blank, scan)
    scan = re.sub(r"(?<=\]\()[^\s)]+(?=\))", _blank, scan)
    scan = re.sub(r"\b[\w.!#$%&'*+/=?^`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", _blank, scan)
    def mask_url(match):
        raw = match.group(0)
        body = raw.rstrip(".!?,;:)")
        return " " * len(body) + raw[len(body):]
    scan = re.sub(r"\b(?:https?://|www\.)[^\s<>\"']+", mask_url, scan)
    return scan


GREETING_RE = re.compile(
    r"^\s*(?:hi|hello|hey|dear)(?:\s+(?:[A-Za-z][\w'-]*)(?:\s+[A-Za-z][\w'-]*){0,2})?[,]?\s*$",
    re.I,
)
SIGNOFF_RE = re.compile(
    r"^\s*(?:best|thanks|thank you|regards|kind regards|best regards|cheers|"
    r"sincerely|warmly|talk soon|speak soon)[,.!]?\s*$", re.I,
)


def _drop_salutations(text):
    """Remove exact standalone greetings/signoffs, never arbitrary short lines."""
    lines = text.split("\n")
    nonempty = [i for i, line in enumerate(lines) if line.strip()]
    if not nonempty:
        return text
    first, last = nonempty[0], nonempty[-1]
    if GREETING_RE.fullmatch(lines[first]) and lines[first].strip().endswith(","):
        lines[first] = ""
    # A bare personal name counts as a signature only after an actual signoff.
    for i in nonempty[-4:]:
        if SIGNOFF_RE.fullmatch(lines[i]) and i >= last - 3:
            following = [j for j in nonempty if j > i]
            if not following or all(re.fullmatch(r"[A-Z][a-z]+(?: [A-Z][a-z]+){0,2}", lines[j].strip()) for j in following):
                lines[i] = ""
                for j in following:
                    lines[j] = ""
                break
    return "\n".join(lines)


def split_sentences(text):
    """Conservative sentence approximation, with common technical tokens masked.

    Abbreviations are ambiguous; these numbers are descriptive estimates.
    """
    prose = re.sub(r"^[ \t]{0,3}#{1,6}[ \t].*$", "", text, flags=re.MULTILINE)
    prose = re.sub(r"^[ \t]*[-*+][ \t].*$", "", prose, flags=re.MULTILINE)
    prose = _drop_salutations(prose)
    dot = "\ue000"
    def protect(match):
        return match.group(0).replace(".", dot)
    # Decimal/version dots, email addresses, URLs, initials and abbreviations.
    prose = re.sub(r"(?<=\d)\.(?=\d)", dot, prose)
    prose = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", protect, prose)
    def protect_url(match):
        raw = match.group(0)
        body = raw.rstrip(".!?,;:)")
        return body.replace(".", dot) + raw[len(body):]
    prose = re.sub(r"\b(?:https?://|www\.)[^\s<>]+", protect_url, prose)
    prose = re.sub(r"\b(?:Dr|Mr|Mrs|Ms|Prof|Sr|Jr|St|vs|e\.g|i\.e)\.", protect, prose, flags=re.I)
    prose = re.sub(r"\b(?:[A-Z]\.){2,}", protect, prose)
    prose = re.sub(r"\b[A-Z]\.(?=\s+[A-Z][a-z])", protect, prose)
    chunks = re.split(r"(?<=[.!?])(?:[\"')\]]+)?\s+", prose.replace("\n", " "))
    return [c.replace(dot, ".").strip() for c in chunks if c.strip()]


def has_connector_cue(sentence):
    """A punctuation/subordinator cue, not proof of a grammatical joined clause."""
    return bool(re.search(
        r"[;:()]|,\s*(?:and|but|or|nor|for|yet|so)\b|"
        r"\b(?:because|although|though|while|whereas|unless|until|which|if|when|"
        r"after|before|provided|so that|even if)\b", sentence, re.I))


def has_joined_clause(sentence):
    """Compatibility alias; the result is only a heuristic connector cue."""
    return has_connector_cue(sentence)


def split_paragraphs(text):
    prose = re.sub(r"^[ \t]{0,3}#{1,6}[ \t].*$", "", text, flags=re.MULTILINE)
    parts = re.split(r"\n\s*\n", prose)
    out = []
    for p in parts:
        p = p.strip()
        if not p or re.match(r"^\s*([-*+]|\d+\.)\s", p) or p.startswith(">"):
            continue
        out.append(p)
    return out


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def snippet_at(text, index, width=64):
    start = max(0, index - 12)
    raw = text[start:start + width].replace("\n", " ")
    return re.sub(r"\s+", " ", raw).strip()


def locate_sentences(scan, sentences):
    """Best-effort source offsets for split sentences, searched in order.

    Returns -1 for a sentence that cannot be found (for example after
    salutation removal), so callers can fall back to a document-level finding.
    """
    positions, cursor = [], 0
    for sentence in sentences:
        tokens = re.findall(r"\S+", sentence)[:6]
        match = re.search(r"\s+".join(re.escape(t) for t in tokens), scan[cursor:]) if tokens else None
        if match:
            positions.append(cursor + match.start())
            cursor += match.start() + 1
        else:
            positions.append(-1)
    return positions


def stdev(values):
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    return (sum((v - mean) ** 2 for v in values) / (n - 1)) ** 0.5


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def make_finding(text, index, severity, category, rule, snippet=None):
    index = max(0, min(index, len(text)))
    line_start = text.rfind("\n", 0, index) + 1
    line_end = text.find("\n", index)
    if line_end < 0:
        line_end = len(text)
    return Finding(severity, category, rule, line_of(text, index),
                   snippet if snippet is not None else snippet_at(text, index),
                   evidence=text[line_start:line_end], offset_start=index,
                   offset_end=min(index + 1, len(text)))


def finalize_findings(findings, text, strict=False):
    """Make subjective rules advisory and suppress exact-location duplicates."""
    unique = {}
    priority = {"punctuation": 10, "banned-phrase": 8, "vague-attribution": 8, "pivot": 7,
                "abstract-actor": 7, "flourish": 6, "importance-claim": 5, "kicker": 5,
                "plain-word": 3,
                "andrew-certainty": 6, "andrew-marker-density": 6,
                "andrew-casual-residue": 6, "pleonasm": 2, "intensifier": 1}
    for finding in findings:
        finding.convention = finding.convention or finding.category == "punctuation"
        finding.origin = "preference" if finding.convention or finding.category.startswith("formatting-") or finding.category.startswith("andrew-") else "heuristic"
        finding.severity = VIOLATION if strict and finding.convention else WARNING
        if finding.offset_start >= 0:
            finding.evidence = make_finding(text, finding.offset_start, WARNING,
                                           finding.category, finding.rule).evidence
        if finding.offset_start >= 0 and finding.category not in {"cadence", "texture", "fragment", "anaphora"}:
            key = ("span", finding.offset_start)
        else:
            key = (finding.rule_id, finding.rule, finding.line, finding.snippet)
        previous = unique.get(key)
        if previous is None or priority.get(finding.category, 4) > priority.get(previous.category, 4):
            unique[key] = finding
    return sorted(unique.values(), key=lambda f: (f.line, f.offset_start, f.rule_id, f.rule))


def check(text, genre="generic", allow_em_dash=False, strict=False, include_quotes=False):
    genre = normalize_genre(genre)
    findings = []
    scan = mask_sources(text, include_quotes=include_quotes)
    lower = scan.lower()
    word_count = max(1, len(scan.split()))
    per_1k = 1000.0 / word_count

    def add(sev, cat, rule, idx, snip=None):
        findings.append(make_finding(text, idx, sev, cat, rule,
                                     snip if snip is not None else snippet_at(scan, idx)))

    def add_doc(sev, cat, rule, snip=""):
        """A whole-document measurement has no single source line to quote."""
        finding = make_finding(text, 0, sev, cat, rule, snip or "(document-level measurement)")
        finding.offset_start = finding.offset_end = -1
        finding.evidence = finding.snippet
        findings.append(finding)

    def add_at_sentence(sev, cat, rule, i, snip):
        if positions[i] >= 0:
            add(sev, cat, rule, positions[i], snip)
        else:
            add_doc(sev, cat, rule, snip)

    # --- Punctuation and typography -------------------------------------
    if not allow_em_dash:
        for m in re.finditer("—", scan):
            add(VIOLATION, "punctuation", "em dash (—)", m.start())
        for m in re.finditer(r"(?<!\d)–(?!\d)", scan):
            add(VIOLATION, "punctuation", "en dash used as a dash", m.start())
        for m in re.finditer(r"\s--\s|\w--\w", scan):
            add(VIOLATION, "punctuation", "double-hyphen dash (--)", m.start())

    for m in re.finditer(r"[→⇒➡➔]", scan):
        add(VIOLATION, "punctuation", "unicode arrow used as a connector", m.start())
    for m in re.finditer(r"[“”‘’]", scan):
        add(VIOLATION, "punctuation", "curly quote or apostrophe (use straight)", m.start())
    for m in re.finditer(r"[\U0001F300-\U0001FAFF☀-➿⬀-⯿]", scan):
        add(VIOLATION, "formatting-emoji", "emoji", m.start())

    # --- Banned phrases --------------------------------------------------
    for phrase in BANNED_PHRASES:
        for m in re.finditer(r"(?<![\w'])" + re.escape(phrase) + r"(?![\w'])", lower):
            add(VIOLATION, "banned-phrase", f'phrase candidate: "{phrase}"', m.start())

    # --- Often-empty phrases (warnings) ----------------------------------
    for phrase in EMPTY_PHRASES:
        for m in re.finditer(r"(?<![\w'])" + re.escape(phrase) + r"(?![\w'])", lower):
            add(WARNING, "empty-phrase",
                f'often-empty phrase: "{phrase}" (cut unless the sentence still needs it)',
                m.start())

    # --- Pleonastic pairs ------------------------------------------------
    for pair in PLEONASTIC_PAIRS:
        for m in re.finditer(r"\b" + re.escape(pair) + r"\b", lower):
            add(WARNING, "pleonasm", f'possible overlap: "{pair}"; check whether both terms add meaning', m.start())

    # --- Narrow acronym redundancy candidates ---------------------------
    # Keep ordinary pin usage and noun compounds outside this two-pair check.
    for m in re.finditer(
            r"(?<![\w'’‐‑-])(?:PIN[ \t]+(?i:numbers?)|ATM[ \t]+(?i:machines?))(?![\w'’‐‑-])",
            scan):
        # Masked source material must not create adjacency between words.
        if text[m.start():m.end()] != m.group(0):
            continue
        finding = make_finding(
            text, m.start(), WARNING, "redundant-acronym",
            "possible acronym redundancy; check whether the noun repeats the acronym's meaning",
            snippet=m.group(0))
        finding.offset_end = m.end()
        findings.append(finding)

    # --- Reversal pivots -------------------------------------------------
    for pattern, label in PIVOT_PATTERNS:
        for m in re.finditer(pattern, lower):
            add(VIOLATION, "pivot", label, m.start())

    # --- Trailing participial commentary ---------------------------------
    for word in TRAILING_PARTICIPLES:
        for m in re.finditer(r",\s*" + re.escape(word), lower):
            add(VIOLATION, "participle",
                f'trailing participial commentary: ", {word}..."', m.start())

    # --- "serves as" dodge ----------------------------------------------
    for m in re.finditer(r"\b(serves?|stands?|functions?|acts?)\s+as\b", lower):
        add(WARNING, "copula", '"serves/stands/functions as" dodge; prefer "is"', m.start())
    for m in re.finditer(r"\b(boasts|features|offers)\s+(a|an|the|over|more than)\b", lower):
        add(WARNING, "copula", "copula avoidance: boasts/features/offers", m.start())
    for m in re.finditer(r"\b(represents|marks)\s+(a|an)\s+(shift|turning point|milestone|new era|"
                         r"major|significant|pivotal|fundamental|paradigm|leap|step change)\b", lower):
        add(WARNING, "copula", 'significance copula: "represents/marks a ..."; name what changed', m.start())

    # --- Vague attribution, abstract actors, unsupported importance -------
    for pattern in VAGUE_ATTRIBUTION:
        for m in re.finditer(pattern, lower):
            add(VIOLATION, "vague-attribution",
                "unnamed authority; name the source, keep its uncertainty, or cut", m.start())
    for m in re.finditer(ABSTRACT_ACTOR_RE, lower):
        add(WARNING, "abstract-actor", f'abstraction as actor: "{m.group(0)}"', m.start())
    for m in re.finditer(IMPORTANCE_RE, lower):
        left = max(scan.rfind(ch, 0, m.start()) for ch in ".!?\n") + 1
        rights = [i for i in (scan.find(ch, m.end()) for ch in ".!?\n") if i >= 0]
        sentence = lower[left:min(rights) + 1 if rights else len(lower)]
        if re.search(r"important\s+to\s+(?:note|consider|remember)", sentence):
            continue
        if not re.search(MECHANISM_RE, sentence):
            add(WARNING, "importance-claim",
                f'importance without mechanism: "{m.group(0)}"; show the consequence or evidence',
                m.start())
    for phrase, plain in PLAIN_WORDS.items():
        for m in re.finditer(r"(?<![\w'])" + re.escape(phrase) + r"(?![\w'])", lower):
            add(WARNING, "plain-word", f'plainer option: "{phrase}" -> {plain}', m.start())

    # --- Demonstrative kickers and decorative metaphors -------------------
    for m in re.finditer(r"([^.!?\n]{20,})[.!?][ \t]+((?:This|That)\b[^.!?\n]{0,50}[.!])(?=[ \t]*(?:\n|$)|[ \t]+[A-Z])", scan):
        kicker = m.group(2)
        if len(kicker.split()) <= 7 and len(m.group(1).split()) > len(kicker.split()) and not re.search(
                r"\b(?:works|helps|makes sense|sounds good|is fine|is ready|is right|is correct)\b", kicker, re.I):
            add(WARNING, "kicker", "demonstrative verdict after a sentence; check whether it restates the point",
                m.start(2), kicker)
    for m in re.finditer(r"\bwearing\s+the\s+(?:costume|clothes|mask|uniform)\s+of\b|\bdressed\s+up\s+as\b|"
                         r"\bmasquerading\s+as\b|\bin\s+\w+'?s\s+clothing\b", lower):
        add(WARNING, "flourish", "decorative metaphor; state the plain relation if the image adds nothing", m.start())
    if re.search(r"\bon\s+(?:the\s+)?one\s+hand\b", lower) and "on the other hand" in lower:
        m = re.search(r"\bon\s+(?:the\s+)?one\s+hand\b", lower)
        add(WARNING, "false-balance", 'symmetrical hedging: "on one hand ... on the other hand"', m.start())

    # --- Invented concept labels -----------------------------------------
    for m in re.finditer(r"\bthe\s+\w+\s+(paradox|trap|creep|vacuum|inversion|divide)\b", lower):
        add(WARNING, "concept-label", "possible invented concept label", m.start())

    # --- Self-answered questions -----------------------------------------
    # The prefix alternation has to cover both mid-paragraph ("...trends. The
    # result? Devastating.") and paragraph-initial questions, which a plain
    # [.!?]\s prefix misses because the blank line breaks the match.
    for m in re.finditer(
            r"(?m)(?:^|[.!?])\s*([A-Z][^.?!\n]{2,45}\?)\s+([A-Z][^.?!\n]{0,35}[.!])", scan):
        if len(m.group(1).split()) <= 7 and len(m.group(2).split()) <= 5:
            add(VIOLATION, "self-question", "question followed by a short answer; check whether the question is useful",
                m.start(1), (m.group(1) + " " + m.group(2))[:64])

    # --- Colon-punch -----------------------------------------------------
    colon_punch = list(re.finditer(r"(?:^|[.!?]\s)(The\s+\w+):\s+\w[\w\s]{0,20}\.", scan))
    if len(colon_punch) >= 2:
        for m in colon_punch:
            add(WARNING, "colon-punch", "repeated colon labels; review whether they help navigation", m.start())

    # --- Colon reveal ----------------------------------------------------
    # A noun phrase, a colon, then a lowercase dramatic reveal that runs to
    # the end of the sentence: "The detail that makes it work: a separate
    # agent grades it." Distinct from colon-punch (which needs "The X:" twice)
    # because a single instance is already the pattern. Labels followed by a
    # list, a quote, code, or a capitalized clause are not matched.
    for m in re.finditer(
            r"(?:^|[.!?]\s+)((?:The|This|That|One|My|Our|Its)\s+[^.:;!?\n]{2,60}):\s+([a-z][^.!?\n]{3,120}[.!?])",
            scan, flags=re.M):
        reveal = m.group(2)
        if "," in reveal and reveal.count(",") >= 2:
            continue  # probably a list
        add(WARNING, "colon-reveal",
            'colon explanation or reveal; review whether the emphasis helps',
            m.start(1), (m.group(1) + ": " + reveal)[:64])

    # --- Synonym cycling -------------------------------------------------
    # Three or more distinct members of one referent cluster used as the
    # grammatical subject of sentences in the same paragraph.
    for para in split_paragraphs(scan):
        psents = split_sentences(para)
        if len(psents) < 3:
            continue
        subjects = []
        for sent in psents:
            head = re.findall(r"[a-z']+", sent.lower()[:40])
            head = [w for w in head if w not in ("the", "a", "an", "this", "that",
                                                  "our", "your", "my", "its", "their")]
            if head:
                subjects.append(head[0])
        for name, members in SYNONYM_CLUSTERS.items():
            hits = [w for w in subjects if w in members]
            if len(set(hits)) >= 3:
                idx = scan.find(para)
                add(WARNING, "synonym-cycling",
                    f"possible referent naming variation: {len(set(hits))} subject terms "
                    f"({', '.join(sorted(set(hits)))}) in one paragraph; check whether the referents differ",
                    max(0, idx), para[:64])
                break

    # --- False ranges and sweeps -----------------------------------------
    for m in re.finditer(r"\bfrom\s+[^.;,\n]{3,45}\s+to\s+[^.;,\n]{3,45}", lower):
        if len(re.findall(r"\d+", m.group(0))) >= 2:
            continue
        add(WARNING, "false-range", 'possible false range: "from X to Y"', m.start())
    for m in re.finditer(r"\bwhether\s+you(?:'re|\s+are)\s+[^.;\n]{2,60}\bor\b", lower):
        add(WARNING, "false-range", 'coverage phrase: "whether you\'re X or Y"; review relevance', m.start())

    # --- Triads ----------------------------------------------------------
    triads = list(re.finditer(r"\b(\w+),\s+(\w+),\s+and\s+(\w+)[.!?,;]", scan))
    triads += list(re.finditer(r"\b(\w+\s+\w+),\s+(\w+\s+\w+),\s+and\s+(\w+\s+\w+)", scan))
    # Report repeated list structure for review, preserving necessary items.
    # These thresholds are scanner heuristics, never list-length rules.
    if len(triads) >= 2 and len(triads) * per_1k > 3.0:
        for m in triads:
            add(WARNING, "triad",
                f"tricolon density high ({len(triads)} in {word_count} words)", m.start())

    # --- Hedging stacks --------------------------------------------------
    for m in re.finditer(
            r"\b(could|might|may|can)\s+(potentially|possibly|arguably|perhaps|often)\b"
            r"|\bit\s+could\s+be\s+argued\b|\bsome\s+might\s+say\b", lower):
        add(VIOLATION, "hedging", "multiple uncertainty markers; keep each if it expresses a distinct uncertainty", m.start())

    # --- Intensifiers ----------------------------------------------------
    for word in INTENSIFIERS:
        for m in re.finditer(r"\b" + re.escape(word) + r"\b", lower):
            add(WARNING, "intensifier", f'intensifier: "{word}"', m.start())

    # --- Soft vocabulary, density scored ---------------------------------
    soft_hits = []
    for word in dict.fromkeys(SOFT_WORDS):
        if genre == "docs" and word in TECHNICAL_TERMS:
            continue
        for m in re.finditer(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", lower):
            soft_hits.append((word, m.start()))
    soft_density = len(soft_hits) * per_1k
    for word, idx in soft_hits:
        sev = VIOLATION if soft_density > 12 else WARNING
        cat = "stock-vocab-marketing" if word in (
            "seamless", "seamlessly", "empower", "empowering", "unlock",
            "game-changer", "game changer", "cutting-edge", "world-class",
            "state-of-the-art", "groundbreaking") else "stock-vocab"
        hint = f'; plainer: {PLAINER[word]}' if word in PLAINER else ""
        add(sev, cat, f'vocabulary candidate: "{word}"; preserve literal technical usage{hint}', idx)

    # --- Draft artifacts (4.4) --------------------------------------------
    code_only = strip_code(text)
    for pattern, label in DRAFT_ARTIFACTS:
        for m in re.finditer(pattern, code_only):
            add(VIOLATION, "draft-artifact", label, m.start(), m.group(0)[:64])

    # --- Prestige lists, vague quantities, announcements (4.4) -------------
    for m in re.finditer(r"\b(?:cited|featured|profiled|covered)\s+in\b[^.\n]{0,80},[^.\n]{0,80}\band\b", lower):
        add(WARNING, "borrowed-authority", "list of outlets in place of what one source said", m.start())
    vague = list(re.finditer(
        r"\b(?:various|numerous|countless|a (?:wide )?(?:range|variety|host|myriad|number) of)\b", lower))
    if len(vague) >= 3:
        add(WARNING, "vague-quantity",
            f"{len(vague)} vague quantities; one is fine, a cluster hides the count", vague[2].start())
    for m in re.finditer(
            r"(?:^|(?<=[.!?]\s)|(?<=\n))(?:Importantly|Crucially|Critically|Interestingly|Surprisingly|Notably),", scan):
        add(WARNING, "announcement", "sentence opens by announcing its own importance", m.start())
    for m in re.finditer(r"(?im)^(?:here are|these are|below are)\s+(?:the\s+)?(?:top\s+)?\d+\s+\w+", scan):
        add(WARNING, "announcement", "numbered-list announcement; check the count is the content's own", m.start())
    for m in re.finditer(
            r"\(\s*(?:and,?\s+)?(?:increasingly|notably|importantly|crucially|interestingly|perhaps)[,]?\s+[^)\n]{3,60}\)", lower):
        add(WARNING, "hedging", "parenthetical hedge; keep it if it states a real limit", m.start())
    for m in re.finditer(r"(?im)^[ \t]*[-*+][ \t]+\*\*([^*:\n]{3,40}):?\*\*:?[ \t]+(?:the[ \t]+)?\1\b", scan):
        add(WARNING, "formatting-bullet", "label repeated as the first words of its item", m.start())
    prose_paragraphs = split_paragraphs(scan)
    openers = [p for p in prose_paragraphs if re.match(
        r"(?:however|moreover|furthermore|additionally|in addition|overall|consequently|nevertheless|"
        r"ultimately|in conclusion|that said)\b", p, re.I)]
    if len(openers) >= 3 and len(openers) > 0.3 * len(prose_paragraphs):
        add(WARNING, "transition-density",
            f"{len(openers)} of {len(prose_paragraphs)} paragraphs open with a connective",
            max(0, scan.find(openers[2])), openers[2][:64])

    # --- Formatting ------------------------------------------------------
    for m in re.finditer(r"(?m)^[ \t]*(?:[-*+]|\d+\.)[ \t]+\*\*[^*\n]{1,50}\*\*[ \t]*[:.]?", scan):
        add(VIOLATION, "formatting-bullet", "bold-first bullet; review whether the structure helps scanning", m.start())

    body_bold = list(re.finditer(r"(?m)^(?![ \t]*(?:[-*+]|\d+\.)[ \t])(?![ \t]*#).*?\*\*[^*\n]{2,60}\*\*", scan))
    paragraphs = split_paragraphs(scan)
    if genre in ("reddit", "tweet"):
        # Formatting conventions vary by community and user preference.
        for m in re.finditer(r"\*\*[^*\n]{2,60}\*\*", scan):
            add(VIOLATION, "formatting-bold",
                f"bold text in {genre}; review channel conventions", m.start())
    elif paragraphs and len(body_bold) > max(1, len(paragraphs) / 3.0):
        for m in body_bold:
            add(WARNING, "formatting-bold",
                f"bold scattered through prose ({len(body_bold)} in {len(paragraphs)} paragraphs)",
                m.start())

    headers = list(re.finditer(r"(?m)^[ \t]{0,3}#{1,6}[ \t]+\S", scan))
    if headers and word_count < 400:
        add(WARNING, "formatting-header",
            f"headers on a short text ({len(headers)} headers, {word_count} words)",
            headers[0].start())
    for m in re.finditer(r"(?m)^[ \t]{0,3}#{1,6}[ \t]+(.*)$", scan):
        title = m.group(1).strip()
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", title)]
        if len(words) >= 3:
            capped = sum(1 for w in words[1:] if w[0].isupper() and not w.isupper())
            if capped >= len(words[1:]) * 0.8:
                add(WARNING, "formatting-header", "title case heading", m.start(), title[:60])
        if re.match(r"^[A-Z][\w\s]{2,30}:\s+\w", title):
            add(WARNING, "formatting-header", "title-case colon headline", m.start(), title[:60])

    for m in re.finditer(r"(?im)^[ \t]*#*[ \t]*(phase|stage|step|part)[ \t]+\d+[ \t]*[:.]", scan):
        add(WARNING, "signposting", "numbered phase/stage label (fine in procedures, a crutch in argument)",
            m.start())
    for m in re.finditer(r"(?m)^[ \t]*(First(ly)?|Second(ly)?|Third(ly)?|Finally|Lastly)[ \t]*,", scan):
        add(WARNING, "signposting", "explicit signposting", m.start())

    # --- Broetry: runs of one-line paragraphs ----------------------------
    lines = scan.split("\n")
    run = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s and not s.startswith(("#", "-", "*", ">", "|")) and len(s.split()) <= 14:
            nxt_blank = (i + 1 >= len(lines)) or not lines[i + 1].strip()
            prev_blank = (i == 0) or not lines[i - 1].strip()
            if nxt_blank and prev_blank:
                run += 1
                if run >= 4:
                    add(WARNING, "formatting-broetry",
                        "stacked one-line paragraphs (broetry cadence)", sum(
                            len(x) + 1 for x in lines[:i]))
                    run = 0
                continue
        run = 0

    # --- Engagement bait -------------------------------------------------
    for m in re.finditer(r"\b(what do you think\?|agree\?|thoughts\?|let'?s connect|"
                         r"drop a comment|let that sink in|read that again)", lower):
        add(VIOLATION, "engagement-bait", "engagement bait", m.start())

    # --- Email padding ---------------------------------------------------
    for m in re.finditer(r"\b(just wanted to (circle back|follow up|check in)|"
                         r"circling back|touching base|as per my last email)", lower):
        add(WARNING, "email-padding", "email padding phrase", m.start())

    # --- Diff-anchored narration -----------------------------------------
    for m in re.finditer(r"\b(this (function|method|class|change) was added to|"
                         r"previously,? (we|this|the code)|replaces the (previous|old) approach)", lower):
        add(WARNING, "diff-anchored", "diff-anchored narration", m.start())

    # --- Sentence and paragraph shape ------------------------------------
    sentences = split_sentences(scan)
    positions = locate_sentences(scan, sentences)
    cad = Cadence()
    cad.paragraphs = len(paragraphs)
    review_cadence = len(sentences) >= 6 and sum(len(s.split()) for s in sentences) >= 100 and genre not in {"tweet", "internal", "docs", "fiction"}
    cad.status = "review" if review_cadence else ("exempt" if genre in {"tweet", "internal", "docs", "fiction"} else "insufficient_sample")
    cad.notes.append("Descriptive estimates only. Sentence length, repetition and punctuation cannot establish quality or authorship.")
    if not review_cadence:
        cad.notes.append("Cadence advice omitted for this channel or a sample under 100 words / six sentences.")

    if sentences:
        lengths = [len(s.split()) for s in sentences]
        cad.sentences = len(sentences)
        cad.words = sum(lengths)
        cad.mean_len = sum(lengths) / len(lengths)
        cad.stdev_len = stdev(lengths)
        cad.coef_var = (cad.stdev_len / cad.mean_len) if cad.mean_len else 0.0

        for opener in ("imagine ", "in today's", "in a world where", "in an era of",
                       "have you ever", "picture this"):
            if sentences[0].lower().startswith(opener):
                add(VIOLATION, "opening", f'opening candidate: "{opener.strip()}"', 0,
                    sentences[0][:64])

        tail = " ".join(sentences[-2:]).lower()
        for phrase in ("ultimately", "in the end", "at the end of the day",
                       "reminds us", "reminder that", "if we can",
                       "there's no telling", "one thing is clear",
                       "only time will tell", "the future looks",
                       "already here", "isn't coming", "is not coming",
                       "the rest is", "everything else is",
                       "the future belongs", "and that changes",
                       "welcome to", "looking ahead", "remains to be seen",
                       "the only question is", "is being written"):
            if phrase in tail:
                add(WARNING, "ending", f'summary or uplift ending signal: "{phrase}"',
                    max(0, lower.rfind(phrase)), sentences[-1][:64])

        # A short definitional/aphoristic ending may be intentional. This
        # shape heuristic cannot determine whether it names a concrete fact.
        last = sentences[-1]
        last_words = last.split()
        if 3 <= len(last_words) <= 12 and not re.search(r"\d", last):
            if re.search(r"\b(is|are|was|becomes?)\s+(the|a|an)\s+\w+\s+of\s+\w+", last, re.I) \
               or re.search(r"\b(is|are)\s+(a|an|the)\s+\w+,\s+not\s+(a|an|the)?\s*\w+", last, re.I) \
               or re.search(r"^(the|that)\s+\w+\s+is\s+(the\s+)?\w+\.$", last.strip(), re.I) \
               or re.search(r"\b(it'?s|that'?s)\s+(already|all|everything)\b", last, re.I):
                add(WARNING, "ending",
                    "short definitional or aphoristic ending; keep concrete definitions",
                    len(text) - 1, last[:64])

        # Fragments.
        frags = [s for s in sentences if len(s.split()) <= 3]
        cad.fragments = len(frags)
        allowed = max(1.0, cad.words / 150.0)
        if len(frags) > allowed * 1.5:
            add_doc(WARNING, "fragment",
                    f"short-sentence density ({len(frags)} sentences of three words or fewer "
                    f"in {cad.words} words); review intended pacing", "; ".join(frags[:3])[:64])
        for i in range(len(sentences) - 1):
            if len(sentences[i].split()) <= 3 and len(sentences[i + 1].split()) <= 3:
                add_at_sentence(WARNING, "fragment", "consecutive sentences of three words or fewer", i,
                                (sentences[i] + " " + sentences[i + 1])[:64])
                break

        # Uniform sentence length runs.
        run = 1
        best = 1
        for i in range(1, len(lengths)):
            a, b = lengths[i - 1], lengths[i]
            if a >= 6 and b >= 6 and abs(a - b) <= max(2, 0.2 * max(a, b)):
                run += 1
                best = max(best, run)
                if run >= 5:
                    add_at_sentence(WARNING, "cadence",
                                    "5+ consecutive sentences of similar length; uniform rhythm",
                                    i - 4, sentences[i - 4][:64])
                    run = 1
            else:
                run = 1
        cad.longest_uniform_run = best

        if review_cadence and cad.sentences >= 8 and cad.coef_var < 0.35:
            add_doc(WARNING, "cadence",
                    f"low sentence-length variance (CV {cad.coef_var:.2f}; a descriptive heuristic only)")

        # Anaphora: 3+ consecutive sentences opening with the same word.
        run, start_i = 1, 0
        for i in range(1, len(sentences)):
            w0 = sentences[i - 1].split()[0].lower().strip(",.;:") if sentences[i - 1].split() else ""
            w1 = sentences[i].split()[0].lower().strip(",.;:") if sentences[i].split() else ""
            if w0 and w0 == w1:
                run += 1
                if run >= 3:
                    add_at_sentence(WARNING, "anaphora",
                                    f'anaphora run: {run} sentences opening with "{w1}"',
                                    start_i, sentences[start_i][:64])
                    run = 1
            else:
                run, start_i = 1, i

        # Subject-first uniformity.
        openers_varied = sum(
            1 for s in sentences
            if s.endswith("?") or "," in s.split(".")[0][:40]
            or s.split()[0].lower() in ("when", "if", "while", "after", "before",
                                        "because", "although", "though", "as")
        )
        if review_cadence and cad.sentences >= 10 and openers_varied / cad.sentences < 0.12:
            add_doc(WARNING, "cadence",
                    "nearly every sentence opens subject-first; no inversions or "
                    "subordinate leads")

    if paragraphs:
        plens = [len(split_sentences(p)) for p in paragraphs]
        plens = [p for p in plens if p > 0]
        if plens:
            cad.para_mean = sum(plens) / len(plens)
            cad.para_stdev = stdev(plens)
            if len(plens) >= 4 and cad.para_stdev < 0.6 and 2.5 <= cad.para_mean <= 5.5:
                add_doc(WARNING, "cadence",
                        f"uniform paragraph length ({cad.para_mean:.1f} sentences each, "
                        f"stdev {cad.para_stdev:.2f}); five-paragraph-essay shape")

    # --- Texture: over-cut prose -----------------------------------------
    # Optional review of short/repetitive rhythm. These thresholds are
    # editorial heuristics, not universal targets or author fingerprints.
    if review_cadence:
        lengths = [len(s.split()) for s in sentences]
        short = [s for s, n in zip(sentences, lengths) if n <= 8]
        cad.short_share = len(short) / cad.sentences
        eligible = [s for s, n in zip(sentences, lengths) if n > 8]
        if eligible:
            cad.joined_share = sum(1 for s in eligible if has_connector_cue(s)) / len(eligible)
            cad.connector_cue_share = cad.joined_share

        if cad.mean_len < 10:
            add_doc(VIOLATION, "texture",
                    f"mean sentence length {cad.mean_len:.1f} words; prose has been cut "
                    f"short; review whether necessary relationships are clear")
        elif cad.mean_len < 13:
            add_doc(WARNING, "texture",
                    f"mean sentence length {cad.mean_len:.1f} words; "
                    f"check whether relationships remain clear")

        if cad.short_share > 0.5:
            add_doc(WARNING, "texture",
                    f"{cad.short_share:.0%} of sentences are 8 words or fewer; "
                    f"review intended pacing", "; ".join(short[:3])[:64])

        # Runs of short sentences can be intentional; offer review only.
        run, best, start_i = 0, 0, 0
        for i, n in enumerate(lengths):
            if n <= 8:
                run += 1
                if run == 1:
                    start_i = i
                best = max(best, run)
            else:
                if run >= 3:
                    sev = VIOLATION if run >= 4 else WARNING
                    add_at_sentence(sev, "texture",
                                    f"{run} consecutive sentences of 8 words or fewer (staccato run)",
                                    start_i, " ".join(sentences[start_i:start_i + run])[:64])
                run = 0
        if run >= 3:
            sev = VIOLATION if run >= 4 else WARNING
            add_at_sentence(sev, "texture",
                            f"{run} consecutive sentences of 8 words or fewer (staccato run)",
                            start_i, " ".join(sentences[start_i:start_i + run])[:64])
        cad.longest_short_run = best

        if len(eligible) >= 5 and cad.joined_share < 0.35:
            add_doc(WARNING, "texture",
                    f"{cad.joined_share:.0%} of sentences over 8 words carry a "
                    f"connector cue (punctuation/subordinator heuristic, not a grammar judgment)")

        # Alternating lengths may be intentional. Detect the pattern without
        # attributing it to a model or prescribing a replacement rhythm.
        if cad.sentences >= 8:
            signs = []
            for n in lengths:
                signs.append(1 if n >= cad.mean_len * 1.2 else (-1 if n <= cad.mean_len * 0.6 else 0))
            alt, best_alt = 1, 1
            for i in range(1, len(signs)):
                if signs[i] != 0 and signs[i] == -signs[i - 1]:
                    alt += 1
                    best_alt = max(best_alt, alt)
                else:
                    alt = 1
            if best_alt >= 6:
                add_doc(WARNING, "texture",
                        f"{best_alt} sentences alternating long/short/long/short; "
                        f"review whether the repetition is intentional")

        # Closing zinger: a long sentence followed by a 1 to 4 word landing.
        if len(sentences) >= 2 and lengths[-1] <= 4 and lengths[-2] >= 15:
            add_at_sentence(WARNING, "texture",
                            "short closing after a long sentence; check whether it serves the intended ending",
                            len(sentences) - 1, sentences[-1][:64])

    # Genres set context, not automatic quality or authorship verdicts.
    # All rhythm/structure findings are advisory, and are suppressed on tiny
    # samples or channels where concise instructions/fragments are expected.
    cadence_categories = {"cadence", "texture", "fragment", "anaphora"}
    if not review_cadence:
        findings = [f for f in findings if f.category not in cadence_categories]
    return finalize_findings(findings, text, strict=strict), cad


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _where(finding):
    return f"line {finding.line}" if finding.offset_start >= 0 else "document"


def strict_exit(findings):
    return 1 if any(f.severity == VIOLATION for f in findings) else 0


def report(findings, cad, max_examples=3, quiet=False):
    """Advisory report. A scan is never an authorship test or quality score."""
    groups = {}
    for finding in findings:
        if quiet and finding.severity != VIOLATION:
            continue
        groups.setdefault(finding.rule_id, []).append(finding)
    for rule_id, items in groups.items():
        print(f"\n{rule_id}: {items[0].rule}")
        for item in items[:max_examples]:
            print(f"  {item.severity.lower()} {_where(item)}: {item.evidence}")
        if len(items) > max_examples:
            print(f"  {len(items) - max_examples} more finding(s)")
    print(f"\nCadence: {cad.status}; {cad.sentences} estimated sentence(s), "
          f"{cad.words} prose words, mean {cad.mean_len:.1f} words.")
    if cad.status == "review":
        print(f"  connector cues: {cad.connector_cue_share:.0%}; "
              "punctuation/subordinator heuristic, not a clause parser.")
    for note in cad.notes:
        print(f"  {note}")
    print(f"\n{len(findings)} review candidate(s). Keep contextually useful wording; "
          "a clean scan is not a quality verdict.")
    return strict_exit(findings)


def report_detect(findings, cad, max_examples=5):
    """Quote mechanical candidates without rewriting or guessing authorship."""
    if not findings:
        print("No catalog patterns found. This does not establish quality or authorship.")
        return 0
    groups = {}
    for finding in findings:
        groups.setdefault((finding.rule_id, finding.rule), []).append(finding)
    for (rule_id, rule), items in groups.items():
        print(f"\nPattern candidate: {rule} [{rule_id}]")
        for item in items[:max_examples]:
            print(f"  {_where(item)}: {item.evidence}")
        if len(items) > max_examples:
            print(f"  {len(items) - max_examples} more finding(s)")
        print("  Review: " + FIX_HINTS.get(items[0].category,
              "Check the wording against the requested channel and preserve useful meaning."))
    print("\nThese are contextual review candidates, not evidence of who wrote the text.")
    return strict_exit(findings)


def json_payload(findings, cadence, genre, **extra):
    return {
        "schema_version": 2,
        "genre": normalize_genre(genre),
        **extra,
        "findings": [asdict(f) for f in findings],
        # Preserve the legacy lists for callers; default scans have no hard violations.
        "violations": [asdict(f) for f in findings if f.severity == VIOLATION],
        "warnings": [asdict(f) for f in findings if f.severity == WARNING],
        "cadence": asdict(cadence),
        "notice": "Review candidates only; no quality score or authorship inference.",
    }


def main():
    ap = argparse.ArgumentParser(add_help=True, description="ultimate-prose linter")
    ap.add_argument("path", nargs="?", help="file to scan (default: stdin)")
    ap.add_argument("--genre", default="generic", choices=GENRES)
    ap.add_argument("--allow-em-dash", action="store_true")
    ap.add_argument("--strict", action="store_true", help="nonzero exit for explicit typography conventions only")
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

    findings, cad = check(text, genre=args.genre, allow_em_dash=args.allow_em_dash,
                          strict=args.strict, include_quotes=args.include_quotes)

    if args.json:
        print(json.dumps(json_payload(findings, cad, args.genre, strict=args.strict),
                         indent=2, ensure_ascii=False))
        return strict_exit(findings)

    if args.detect:
        return report_detect(findings, cad, max(args.max_examples, 5))

    return report(findings, cad, args.max_examples, args.quiet)


if __name__ == "__main__":
    sys.exit(main())
