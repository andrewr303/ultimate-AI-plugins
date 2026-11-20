#!/usr/bin/env python3
"""Build or check the shared golden vectors from the Python reference.

The vectors pin what contact_rules.py and creator_score.py return, so the TypeScript port
under ../src cannot drift from them. Both test suites assert every vector.

From the plugin directory:
    python3 -I -B scripts/build_vectors.py --check   # exit 1 if a vector file is stale
    python3 -I -B scripts/build_vectors.py --write   # regenerate after a reviewed change

A changed expected value is a behaviour change. Review the diff before committing it.
All inputs are synthetic (janedoe.com style names); never put a real address here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import contact_rules as cr  # noqa: E402
import creator_score as cs  # noqa: E402

VECTOR_DIR = HERE.parent / "vectors"
SITE = "janedoe.com"


def _run(fn):
    try:
        return {"expected": fn()}
    except (TypeError, ValueError):
        return {"throws": True}


# --- contact rules -----------------------------------------------------------------------

DECODE = [
    ("plain", "plain text"),
    ("null", None),
    ("numeric-entity-at", "jane&#64;janedoe.com"),
    ("hex-entity-at", "jane&#x40;janedoe.com"),
    ("named-commat-period", "jane&commat;janedoe&period;com"),
    ("named-amp-single-pass", "a &amp;#64; b"),
    ("unknown-named-entity-kept", "a &copy; b"),
    ("entity-needs-semicolon", "jane&#64janedoe.com"),
    ("entity-nul-kept", "a&#0;b"),
    ("entity-out-of-range-kept", "a&#x110000;b"),
    ("entity-surrogate-kept", "a&#xD800;b"),
    ("unicode-escape-at", "jane\\u0040janedoe.com"),
    ("unicode-escape-surrogate-kept", "x\\ud83d\\ude00y"),
    ("literal-tab-newline", "Rates:\\tJane\\nDoe\\rX"),
    ("not-a-string", 42),
]

EXTRACT = [
    ("tab-escape-does-not-glue", "Rates and availability:\\tOlu.Adeyemi@adeyemi-studio.net"),
    ("newline-escape", "Talk to me\\nJane.Doe@janedoe.com"),
    ("entity-decoded-first", "hello&#64;janedoe.com"),
    ("trailing-punctuation", "mail jane@janedoe.com. or (jane@janedoe.com)"),
    ("dedupe-and-case", "Jane@janedoe.com, jane@JaneDoe.com"),
    ("two-addresses-comma", "a@janedoe.com,b@janedoe.org"),
    ("plus-tag-kept", "jane+brands@janedoe.com"),
    ("preceded-by-letter-unicode", "éjane@janedoe.com"),
    ("preceded-by-digit-arabic", "٣jane@janedoe.com"),
    ("preceded-by-superscript", "²jane@janedoe.com"),
    ("preceded-by-dot", ".jane@janedoe.com"),
    ("preceded-by-space", " jane@janedoe.com"),
    ("tld-too-long-not-truncated", "jane@janedoe.abcdefghijklmnopqrstuvwxyzab"),
    ("digit-after-tld-not-truncated", "jane@janedoe.com2"),
    ("hyphen-after-tld-not-truncated", "jane@janedoe.com-shop"),
    ("sentence-end-dot", "Write to jane@janedoe.com."),
    ("subdomain-chain-kept-whole", "jane@mail.janedoe.co.uk"),
    ("non-ascii-prefix-blocks", "\u0c5cjane@janedoe.com"),
    ("non-ascii-astral-prefix-blocks", "\U0001F600jane@janedoe.com"),
    ("percent-prefix-blocks", "x%jane@janedoe.com"),
    ("underscore-in-local-kept", "jane_doe@janedoe.com"),
    ("underscore-prefix-blocks", "_\u00e9_jane@janedoe.com x_@janedoe.com"),
    ("non-ascii-after-tld-blocks", "jane@janedoe.com\u00e9"),
    ("underscore-after-tld-blocks", "jane@janedoe.com_x"),
    ("recall-trailing-hyphen", "a@b.com-"),
    ("recall-dot-letter", "a@b.com.x"),
    ("recall-dot-digit", "a@b.com.5"),
    ("recall-trailing-dot-kept", "a@b.com."),
    ("local-64-kept", "a" * 64 + "@janedoe.com"),
    ("local-65-dropped", "a" * 65 + "@janedoe.com"),
    ("label-63-kept", "jane@" + "b" * 63 + ".com"),
    ("label-64-dropped", "jane@" + "b" * 64 + ".com"),
    ("domain-253-kept", "jane@" + ".".join(["c" * 62] * 3 + ["c" * 60]) + ".com"),
    ("domain-254-dropped", "jane@" + ".".join(["c" * 62] * 3 + ["c" * 61]) + ".com"),
    ("asset-shaped", "logo@2x.png sprite@bundle.css"),
    ("obfuscated-at-not-decoded", "jane (at) janedoe (dot) com"),
    ("no-address", "nothing here"),
    ("null", None),
]

REGISTRABLE = [
    ("plain-host", "www.janedoe.com"),
    ("address", "jane@mail.janedoe.com"),
    ("co-uk", "jane@mail.janedoe.co.uk"),
    ("com-au", "blog.janedoe.com.au"),
    ("io-two-labels", "www.janedoe.io"),
    ("bare-co-uk-is-none", "co.uk"),
    ("bare-com-au-is-none", "jane@com.au"),
    ("single-label", "localhost"),
    ("empty-label", "a..b.com"),
    ("trailing-dot", "janedoe.com."),
    ("uppercase", "JaneDoe.COM"),
    ("url-is-none", "https://janedoe.com/sponsor"),
    ("port-is-none", "janedoe.com:8080"),
    ("space-is-none", "jane doe.com"),
    ("non-ascii-is-none", "jäne.com"),
    ("ascii-whitespace-trimmed", "  janedoe.com\t"),
    ("not-a-string", None),
]

ROSTER = [
    ("five-domains", {"addresses": [f"x@studio{i}.net" for i in range(5)]}),
    ("four-domains", {"addresses": [f"x@studio{i}.net" for i in range(4)]}),
    ("one-domain-many", {"addresses": [f"writer{i}@janedoe.com" for i in range(9)]}),
    ("subdomains-collapse", {"addresses": [f"x@s{i}.janedoe.com" for i in range(6)]}),
    ("custom-threshold", {"addresses": ["a@one.com", "b@two.com"], "min_domains": 2}),
    ("invalid-ignored", {"addresses": ["a@one.com", "junk", "b@two.com"], "min_domains": 3}),
    ("zero-threshold-throws", {"addresses": [], "min_domains": 0}),
    ("string-not-list-throws", {"addresses": "a@one.com"}),
]

CLASSIFY = [
    ("asset-density", {"address": "banner@3x.png", "site_domain": SITE}),
    ("asset-css", {"address": "sprite@bundle.css", "site_domain": SITE}),
    ("placeholder-local", {"address": "you@example.org"}),
    ("placeholder-domain", {"address": "jane@yourcompany.com", "site_domain": SITE}),
    ("reserved-tld", {"address": "jane@mail.test", "site_domain": SITE}),
    ("tooling-domain", {"address": "abc123@sentry.io", "site_domain": SITE}),
    ("platform-domain", {"address": "jane@ghost.io", "site_domain": SITE, "platform_domains": ["ghost.io"]}),
    ("platform-domain-case-sensitive", {"address": "jane@ghost.io", "site_domain": SITE, "platform_domains": ["GHOST.IO"]}),
    ("purpose-abuse", {"address": f"abuse@{SITE}", "site_domain": SITE}),
    ("purpose-do-not-reply", {"address": f"do-not-reply@{SITE}", "site_domain": SITE}),
    ("purpose-noreply-digits", {"address": f"noreply2@{SITE}", "site_domain": SITE}),
    ("legal", {"address": f"legal@{SITE}", "site_domain": SITE}),
    ("legal-dpo-prefix", {"address": f"dpo-uk@{SITE}", "site_domain": SITE}),
    ("legal-privacy-plus-tag", {"address": f"privacy+eu@{SITE}", "site_domain": SITE}),
    ("incidental-legal-page", {"address": f"jane@{SITE}", "site_domain": SITE, "page": "legal"}),
    ("incidental-roster-page", {"address": f"jane@{SITE}", "site_domain": SITE, "page": "roster"}),
    ("incidental-footer-page", {"address": f"partnerships@{SITE}", "site_domain": SITE, "page": "footer"}),
    ("sitewide-three-pages", {"address": f"jane@{SITE}", "site_domain": SITE, "page": "homepage", "pages_seen_on": 3}),
    ("two-pages-not-sitewide", {"address": f"jane@{SITE}", "site_domain": SITE, "page": "homepage", "pages_seen_on": 2}),
    ("deal-inbox-own-domain", {"address": f"collabs@{SITE}", "site_domain": f"www.{SITE}", "page": "sponsor"}),
    ("deal-inbox-spelled-out", {"address": f"work-with-me@{SITE}", "site_domain": SITE}),
    ("deal-inbox-plus-tag", {"address": f"partnerships+2026@{SITE}", "site_domain": SITE}),
    ("deal-inbox-subdomain-own", {"address": f"business@mail.{SITE}", "site_domain": SITE}),
    ("deal-inbox-other-domain", {"address": "collabs@northbridge-agency.com", "site_domain": SITE}),
    ("deal-inbox-no-site", {"address": f"business@{SITE}"}),
    ("deal-inbox-free-mail", {"address": "business@gmail.com", "site_domain": SITE}),
    ("deal-inbox-site-is-url", {"address": f"business@{SITE}", "site_domain": f"https://{SITE}/"}),
    ("deal-inbox-co-uk", {"address": "brands@janedoe.co.uk", "site_domain": "shop.janedoe.co.uk"}),
    ("deal-inbox-different-co-uk", {"address": "brands@other.co.uk", "site_domain": "janedoe.co.uk"}),
    ("role-info", {"address": f"info@{SITE}", "site_domain": SITE}),
    ("role-support-plus", {"address": f"support+vip@{SITE}", "site_domain": SITE}),
    ("role-sales-digit", {"address": f"sales7@{SITE}", "site_domain": SITE}),
    ("role-customer-service", {"address": f"customer-service@{SITE}", "site_domain": SITE}),
    ("role-hello-sponsor-page", {"address": f"hello@{SITE}", "site_domain": SITE, "page": "sponsor"}),
    ("role-press", {"address": f"press@{SITE}", "site_domain": SITE}),
    ("personal-contact-page", {"address": f"jane@{SITE}", "site_domain": SITE, "page": "contact"}),
    ("personal-free-mail-bio", {"address": "jane.doe@gmail.com", "site_domain": SITE, "page": "bio"}),
    ("personal-only-digits-local", {"address": f"2026@{SITE}", "site_domain": SITE}),
    ("personal-local-64", {"address": "a" * 64 + f"@{SITE}", "site_domain": SITE}),
    ("malformed-local-65", {"address": "a" * 65 + f"@{SITE}", "site_domain": SITE}),
    ("personal-uppercase-trimmed", {"address": f"  Jane.Doe@JaneDoe.com\n", "site_domain": SITE}),
    ("personal-vendor-zero-pages", {"address": f"jane@{SITE}", "site_domain": SITE, "page": "bio", "pages_seen_on": 0}),
    ("malformed-no-local", {"address": f"@{SITE}", "site_domain": SITE}),
    ("malformed-no-at", {"address": SITE, "site_domain": SITE}),
    ("malformed-single-label", {"address": "jane@localhost", "site_domain": SITE}),
    ("malformed-two-ats", {"address": f"a@b@{SITE}", "site_domain": SITE}),
    ("malformed-path-in-domain", {"address": f"jane@{SITE}/x", "site_domain": SITE}),
    ("malformed-numeric-tld", {"address": "jane@10.0.0.1", "site_domain": SITE}),
    ("malformed-trailing-dot", {"address": f"jane@{SITE}.", "site_domain": SITE}),
    ("malformed-bare-suffix", {"address": "jane@co.uk", "site_domain": SITE}),
    ("malformed-local-leading-dot", {"address": f".jane@{SITE}", "site_domain": SITE}),
    ("malformed-local-non-ascii", {"address": f"jäne@{SITE}", "site_domain": SITE}),
    ("malformed-kelvin-sign", {"address": f"Kate@{SITE}", "site_domain": SITE}),
    ("malformed-quote-local", {"address": f"o'brien@{SITE}", "site_domain": SITE}),
    ("throws-negative-pages", {"address": f"jane@{SITE}", "pages_seen_on": -1}),
    ("throws-fractional-pages", {"address": f"jane@{SITE}", "pages_seen_on": 1.5}),
    ("throws-boolean-pages", {"address": f"jane@{SITE}", "pages_seen_on": True}),
    ("throws-address-not-string", {"address": None}),
    ("throws-page-not-string", {"address": f"jane@{SITE}", "page": 3}),
    ("throws-platform-domains-string", {"address": f"jane@{SITE}", "platform_domains": "ghost.io"}),
]


def _classify(inp):
    kwargs = {k: v for k, v in inp.items() if k != "address"}
    verdict = cr.classify(inp["address"], **kwargs)
    return {"kind": verdict.kind, "keep": verdict.keep, "reason": verdict.reason}


def contact_vectors() -> dict:
    return {
        "schema": "creator-intelligence/contact-rules-vectors-v1",
        "reference": "scripts/contact_rules.py",
        "decode": [{"id": i, "input": x, **_run(lambda x=x: cr.decode(x))} for i, x in DECODE],
        "extract": [{"id": i, "input": x, **_run(lambda x=x: cr.extract(x))} for i, x in EXTRACT],
        "registrable_domain": [{"id": i, "input": x, **_run(lambda x=x: cr.registrable_domain(x))} for i, x in REGISTRABLE],
        "is_roster_page": [{"id": i, "input": x, **_run(lambda x=x: cr.is_roster_page(**x))} for i, x in ROSTER],
        "classify": [{"id": i, "input": x, **_run(lambda x=x: _classify(x))} for i, x in CLASSIFY],
    }


# --- creator score -----------------------------------------------------------------------


def _posts(values, age=200):
    return [{"id": f"p{i}", "views": v, "age_hours": age} for i, v in enumerate(values)]


def _full(score, conf="high"):
    return {k: {"score": score, "confidence": conf} for k in cs.WEIGHTS}


def _with(base, **changes):
    out = dict(base)
    for k, v in changes.items():
        out[k] = v
    return out


BASELINE = [("zero", 0), ("eleven", 11), ("twelve", 12), ("nineteen", 19), ("twenty", 20),
            ("integral-float", 12.0), ("negative-throws", -1), ("fraction-throws", 2.5),
            ("boolean-throws", True), ("null-throws", None)]

OUTLIER = [
    ("median-not-mean", {"posts": _posts([100] * 11 + [10_000])}),
    ("labels", {"posts": _posts([100] * 10 + [160, 250, 600])}),
    ("even-median", {"posts": _posts([100, 200, 300, 400])}),
    ("young-excluded", {"posts": _posts([100] * 12) + [{"id": "new", "views": 5, "age_hours": 5}]}),
    ("unknown-age-excluded", {"posts": _posts([100] * 3) + [{"id": "noage", "views": 900}, {"id": "nullage", "views": 900, "age_hours": None}]}),
    ("missing-metric-counted-separately", {"posts": _posts([100] * 3) + [{"id": "m", "views": None, "age_hours": 500}, {"id": "k", "age_hours": 500}]}),
    ("no-settled", {"posts": [{"id": "x", "views": 1, "age_hours": 1}]}),
    ("empty", {"posts": []}),
    ("baseline-zero", {"posts": _posts([0, 0, 0, 5])}),
    ("youtube-cutoff", {"posts": _posts([100] * 3, age=200) + _posts([50], age=400), "min_age_hours": 336}),
    ("exact-cutoff-is-settled", {"posts": _posts([10, 20, 30], age=72)}),
    ("other-metric", {"posts": [{"id": "a", "likes": 10, "age_hours": 100}, {"id": "b", "likes": 40, "age_hours": 100}, {"id": "c", "views": 99, "age_hours": 100}], "metric": "likes"}),
    ("numeric-and-null-ids", {"posts": [{"id": 7, "views": 10, "age_hours": 100}, {"views": 30, "age_hours": 100}]}),
    ("stable-tie-order", {"posts": _posts([100, 300, 300, 100, 200])}),
    ("float-lift", {"posts": _posts([3, 7, 11])}),
    ("throws-negative-views", {"posts": _posts([100, -1])}),
    ("throws-string-views", {"posts": [{"id": "a", "views": "100", "age_hours": 100}]}),
    ("throws-boolean-views", {"posts": [{"id": "a", "views": True, "age_hours": 100}]}),
    ("throws-negative-age", {"posts": [{"id": "a", "views": 1, "age_hours": -5}]}),
    ("throws-reserved-metric", {"posts": _posts([1]), "metric": "lift"}),
    ("throws-posts-not-list", {"posts": {"id": "a"}}),
    ("throws-post-not-object", {"posts": [5]}),
    ("throws-negative-min-age", {"posts": _posts([1]), "min_age_hours": -1}),
    ("throws-boolean-id", {"posts": [{"id": True, "views": 1, "age_hours": 100}]}),
    ("safe-integer-id-max", {"posts": [{"id": 2**53 - 1, "views": 1, "age_hours": 100}]}),
    ("large-id-as-string", {"posts": [{"id": "3456789012345678901", "views": 1, "age_hours": 100}]}),
    ("integral-float-id", {"posts": [{"id": 7.0, "views": 1, "age_hours": 100}]}),
    ("throws-unsafe-integer-id", {"posts": [{"id": 2**53, "views": 1, "age_hours": 100}]}),
    ("throws-instagram-size-id", {"posts": [{"id": 3456789012345678901, "views": 1, "age_hours": 100}]}),
    ("throws-fractional-id", {"posts": [{"id": 1.5, "views": 1, "age_hours": 100}]}),
    ("throws-metric-proto", {"posts": [{"id": "a", "views": 1, "age_hours": 100}], "metric": "__proto__"}),
    ("throws-metric-constructor", {"posts": [{"id": "a", "views": 1, "age_hours": 100}], "metric": "constructor"}),
    ("throws-metric-prototype", {"posts": [{"id": "a", "views": 1, "age_hours": 100}], "metric": "prototype"}),
]

SCORE = [
    ("uniform-80-high", {"dimensions": _full(80)}),
    ("uniform-100-band-capped", {"dimensions": _full(100)}),
    ("uniform-0-band-floored", {"dimensions": _with(_full(0), authenticity={"score": 0, "confidence": "high"})}),
    ("gate-rejects", {"dimensions": _full(95), "gates": ["G2"]}),
    ("gates-sorted-deduped", {"dimensions": _full(95), "gates": ["G4", "G1", "G4"]}),
    ("each-gate-G1", {"dimensions": _full(50), "gates": ["G1"]}),
    ("each-gate-G3", {"dimensions": _full(50), "gates": ["G3"]}),
    ("each-gate-G5", {"dimensions": _full(50), "gates": ["G5"]}),
    ("missing-renormalised", {"dimensions": _with(_full(80), audience_fit={"score": None})}),
    ("omitted-renormalised", {"dimensions": {k: v for k, v in _full(70).items() if k not in ("reach", "contactability")}}),
    ("mixed-weights", {"dimensions": {"niche_fit": {"score": 90, "confidence": "high"}, "reach": {"score": 40, "confidence": "high"}, "contactability": {"score": 100, "confidence": "medium"}}}),
    ("authenticity-floor", {"dimensions": _with(_full(95), authenticity={"score": 30, "confidence": "high"})}),
    ("brand-safety-floor", {"dimensions": _with(_full(95), brand_safety={"score": 49.9, "confidence": "high"})}),
    ("both-floors", {"dimensions": _with(_full(95), authenticity={"score": 10, "confidence": "high"}, brand_safety={"score": 10, "confidence": "high"})}),
    ("floor-hit-but-total-below-cap", {"dimensions": _with(_full(50), authenticity={"score": 39, "confidence": "high"})}),
    ("floor-exact-not-capped", {"dimensions": _with(_full(95), authenticity={"score": 40, "confidence": "high"})}),
    ("weakest-confidence", {"dimensions": _with(_full(70), reach={"score": 70, "confidence": "medium"})}),
    ("default-confidence-low", {"dimensions": {k: {"score": 70} for k in cs.WEIGHTS}}),
    ("nothing-scorable-g3", {"dimensions": {k: {"score": None} for k in cs.WEIGHTS}}),
    ("empty-dimensions-g3", {"dimensions": {}}),
    ("half-even-tie-down", {"dimensions": {"niche_fit": {"score": 62.25, "confidence": "high"}}}),
    ("half-even-tie-up", {"dimensions": {"niche_fit": {"score": 62.75, "confidence": "high"}}}),
    ("half-even-quarter", {"dimensions": {"niche_fit": {"score": 0.25, "confidence": "high"}}}),
    ("non-tie-rounding", {"dimensions": {"niche_fit": {"score": 33.35, "confidence": "high"}, "reach": {"score": 71.15, "confidence": "high"}}}),
    ("thirds", {"dimensions": {"niche_fit": {"score": 10, "confidence": "high"}, "audience_fit": {"score": 20, "confidence": "high"}, "reach": {"score": 33.3333, "confidence": "high"}}}),
    ("evidence-kept-out-of-output", {"dimensions": {"reach": {"score": 60, "confidence": "high", "evidence": "median 41k views, n=22"}}}),
    ("throws-unknown-dimension", {"dimensions": {"charisma": {"score": 50}}}),
    ("throws-score-above-100", {"dimensions": {"reach": {"score": 120}}}),
    ("throws-score-negative", {"dimensions": {"reach": {"score": -0.1}}}),
    ("throws-score-boolean", {"dimensions": {"reach": {"score": True}}}),
    ("throws-score-string", {"dimensions": {"reach": {"score": "50"}}}),
    ("throws-missing-score-key", {"dimensions": {"reach": {"confidence": "high"}}}),
    ("throws-extra-key", {"dimensions": {"reach": {"score": 50, "weight": 99}}}),
    ("throws-bad-confidence", {"dimensions": {"reach": {"score": 50, "confidence": "none"}}}),
    ("throws-evidence-not-string", {"dimensions": {"reach": {"score": 50, "evidence": 5}}}),
    ("throws-unknown-gate", {"dimensions": _full(50), "gates": ["G9"]}),
    ("throws-gates-not-list", {"dimensions": _full(50), "gates": "G1"}),
    ("throws-dimensions-not-object", {"dimensions": [1, 2]}),
]


def _score(inp):
    return cs.score_creator(cs.dimensions_from_json(inp["dimensions"]), inp.get("gates"))


def _outlier(inp):
    return cs.outlier_report(inp["posts"], inp.get("metric", "views"),
                             inp.get("min_age_hours", cs.MIN_POST_AGE_HOURS))


def score_vectors() -> dict:
    return {
        "schema": "creator-intelligence/creator-score-vectors-v1",
        "reference": "scripts/creator_score.py",
        "tolerance": 1e-9,
        "baseline_confidence": [{"id": i, "input": x, **_run(lambda x=x: cs.baseline_confidence(x))} for i, x in BASELINE],
        "outlier_report": [{"id": i, "input": x, **_run(lambda x=x: _outlier(x))} for i, x in OUTLIER],
        "score_creator": [{"id": i, "input": x, **_run(lambda x=x: _score(x))} for i, x in SCORE],
    }


FILES = {
    "contact-rules.vectors.json": contact_vectors,
    "creator-score.vectors.json": score_vectors,
}


def render(build) -> str:
    return json.dumps(build(), indent=2, ensure_ascii=True) + "\n"


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "--check"
    if mode not in ("--check", "--write"):
        print("usage: build_vectors.py --check | --write", file=sys.stderr)
        return 2
    stale = []
    for name, build in FILES.items():
        path = VECTOR_DIR / name
        text = render(build)
        if mode == "--write":
            VECTOR_DIR.mkdir(exist_ok=True)
            path.write_text(text, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != text:
            stale.append(name)
    if stale:
        print("stale vectors (review, then run --write): " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
