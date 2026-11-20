#!/usr/bin/env python3
"""Baseline-aware outlier lift and a transparent creator score.

Stdlib only, pure functions. Weights, thresholds and age cutoffs are judgment defaults,
not research results (see references/scoring-rubric.md). Calibrate them against deal
outcomes before treating the number as predictive.

This score is not HypeStake's Match Score. It describes one creator against one brief,
from public data, and it explains a shortlist. It never recommends accepting a deal.

Parity: src/creator-score.ts is a TypeScript port of this module for the HypeStake runtimes.
Both must return the same result for every vector in ../vectors/creator-score.vectors.json
(see build_vectors.py). Sums use a plain left-to-right loop, not sum(), because Python 3.12
and later compensate float sums and the port does not.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from dataclasses import dataclass

WEIGHTS = {
    "niche_fit": 20, "audience_fit": 15, "engagement_quality": 15, "authenticity": 15,
    "reach": 10, "brand_safety": 10, "sponsor_readiness": 10, "contactability": 5,
}
GATES = {
    "G1": "brand-safety floor hit",
    "G2": "strong evidence of inauthentic audience or engagement",
    "G3": "insufficient public data to score",
    "G4": "identity unverifiable (profile, site and handle do not agree)",
    "G5": "persistent undisclosed sponsored content",
}
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
BAND = {"high": 5, "medium": 10, "low": 20}  # +/- points shown around the score
MIN_POST_AGE_HOURS = 72  # younger posts have not finished accruing views (YouTube: use 336)
FLOORS = {"authenticity": 40, "brand_safety": 50}
FLOOR_CAP = 60
# Output keys, and names that are object-prototype keys in JavaScript, cannot be a metric name.
RESERVED_POST_KEYS = {"id", "lift", "label", "__proto__", "constructor", "prototype"}
MAX_SAFE_ID = 2**53 - 1  # numeric ids above this collapse in JavaScript; pass them as strings


def _is_number(value: object) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:  # an int too large for a float, such as 10**400
        return False


def _is_post_id(value: object) -> bool:
    """None, a string, or a whole number JavaScript can hold exactly (abs <= 2**53 - 1)."""
    if value is None or isinstance(value, str):
        return True
    return _is_number(value) and float(value).is_integer() and abs(value) <= MAX_SAFE_ID


def baseline_confidence(n: int) -> str:
    """A 10-post median can be off by roughly 1.5-1.8x (simulation, independence assumed)."""
    if not _is_number(n) or not float(n).is_integer() or n < 0:
        raise ValueError("n must be a whole number >= 0")
    return "high" if n >= 20 else "medium" if n >= 12 else "low"


def outlier_report(posts: list[dict], metric: str = "views",
                   min_age_hours: float = MIN_POST_AGE_HOURS) -> dict:
    """posts: [{"id", metric, "age_hours"}]. Baseline is the median of posts old enough to be settled.

    An id is a string, a whole number of at most 2**53 - 1, or null; pass larger platform ids
    (Instagram, TikTok, X) as strings so they survive JSON and JavaScript unchanged.

    Score one platform and one format at a time; never pool platforms. A post with no metric
    value, or with no age, is left out and counted, because unknown is not settled and not zero.
    Invalid values (negative, non-numeric, booleans) raise ValueError.
    """
    if not isinstance(posts, list):
        raise ValueError("posts must be a list")
    if not isinstance(metric, str) or not metric or metric in RESERVED_POST_KEYS:
        raise ValueError("metric must be a non-empty name other than id, lift, label, __proto__, constructor or prototype")
    if not _is_number(min_age_hours) or min_age_hours < 0:
        raise ValueError("min_age_hours must be a number >= 0")
    settled = []
    missing_metric = unknown_age = too_young = 0
    for i, post in enumerate(posts):
        if not isinstance(post, dict):
            raise ValueError(f"posts[{i}] must be an object")
        post_id = post.get("id")
        if not _is_post_id(post_id):
            raise ValueError(f"posts[{i}].id must be a string, a whole number of at most 2**53 - 1, or null")
        value = post.get(metric)
        age = post.get("age_hours")
        if value is not None and (not _is_number(value) or value < 0):
            raise ValueError(f"posts[{i}].{metric} must be a number >= 0 or null")
        if age is not None and (not _is_number(age) or age < 0):
            raise ValueError(f"posts[{i}].age_hours must be a number >= 0 or null")
        if value is None:
            missing_metric += 1
        elif age is None:
            unknown_age += 1
        elif age < min_age_hours:
            too_young += 1
        else:
            settled.append((post_id, value))
    counts = {"excluded_too_young": too_young, "excluded_unknown_age": unknown_age,
              "excluded_missing_metric": missing_metric}
    if not settled:
        return {"baseline": None, "n": 0, "confidence": "low", **counts, "posts": []}
    baseline = statistics.median(v for _, v in settled)
    scored = []
    for post_id, value in settled:
        lift = (value / baseline) if baseline else None
        label = None
        if lift is not None:
            label = "huge" if lift >= 5 else "strong" if lift >= 2 else "mild" if lift >= 1.5 else None
        scored.append({"id": post_id, metric: value, "lift": lift, "label": label})
    scored.sort(key=lambda p: (p["lift"] is None, -(p["lift"] or 0)))
    return {"baseline": baseline, "n": len(settled), "confidence": baseline_confidence(len(settled)),
            **counts, "posts": scored}


@dataclass(frozen=True)
class Dimension:
    score: float | None  # 0-100, or None when public data cannot support it
    confidence: str = "low"
    evidence: str = ""


def dimensions_from_json(raw: object) -> dict[str, Dimension]:
    """Build dimensions from the JSON payload shape, refusing unknown keys and wrong types."""
    if not isinstance(raw, dict):
        raise ValueError("dimensions must be an object")
    out = {}
    for name, value in raw.items():
        if not isinstance(value, dict) or "score" not in value or set(value) - {"score", "confidence", "evidence"}:
            raise ValueError(f"{name} must be an object with score and optional confidence and evidence")
        out[name] = Dimension(**value)
    return out


def score_creator(dimensions: dict[str, Dimension], gates: list[str] | None = None) -> dict:
    if not isinstance(dimensions, dict):
        raise ValueError("dimensions must be a mapping")
    unknown = set(dimensions) - set(WEIGHTS)
    if unknown:
        raise ValueError(f"unknown dimensions: {sorted(unknown)}")
    for name, dim in dimensions.items():
        if dim.score is not None and (not _is_number(dim.score) or not 0 <= dim.score <= 100):
            raise ValueError(f"{name} score out of range: {dim.score}")
        if dim.confidence not in CONFIDENCE_RANK:
            raise ValueError(f"{name} confidence must be low, medium or high")
        if not isinstance(dim.evidence, str):
            raise ValueError(f"{name} evidence must be a string")
    if gates is not None and (not isinstance(gates, list) or not all(isinstance(g, str) for g in gates)):
        raise ValueError("gates must be a list of gate codes")
    triggered = sorted(set(gates or []))
    bad = [g for g in triggered if g not in GATES]
    if bad:
        raise ValueError(f"unknown gates: {bad}")
    if triggered:
        return {"verdict": "reject", "gates": {g: GATES[g] for g in triggered}, "score": None}

    present = {k: d for k, d in dimensions.items() if d.score is not None}
    missing = sorted(set(WEIGHTS) - set(present))
    if not present:
        return {"verdict": "reject", "gates": {"G3": GATES["G3"]}, "score": None}
    weight_sum = 0
    weighted = 0.0
    for k, d in present.items():
        weight_sum += WEIGHTS[k]
        weighted += d.score * WEIGHTS[k]
    total = weighted / weight_sum  # renormalised, never zero-filled
    capped_by = [k for k, floor in FLOORS.items() if k in present and present[k].score < floor]
    if capped_by and total > FLOOR_CAP:
        total = FLOOR_CAP
    confidence = min((d.confidence for d in present.values()), key=CONFIDENCE_RANK.get)
    if missing:
        confidence = "low"
    band = BAND[confidence]
    return {
        "verdict": "score",
        "score": round(total, 1),
        "band": [max(0, round(total - band, 1)), min(100, round(total + band, 1))],
        "confidence": confidence,
        "missing": missing,
        "floor_capped_by": capped_by,
        "weights_used": {k: round(WEIGHTS[k] / weight_sum * 100, 1) for k in present},
    }


def main() -> int:
    """Read one JSON object on stdin: {"posts": [...]} or {"dimensions": {...}, "gates": [...]}."""
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")
        if "posts" in payload:
            result = outlier_report(payload["posts"], payload.get("metric", "views"),
                                    payload.get("min_age_hours", MIN_POST_AGE_HOURS))
        elif "dimensions" in payload:
            gates = payload.get("gates")
            if gates is not None and not isinstance(gates, list):
                raise ValueError("gates must be a list such as [\"G1\"]")
            dims = dimensions_from_json(payload["dimensions"])
            result = score_creator(dims, gates)
        else:
            raise ValueError('input needs a "posts" list or a "dimensions" object')
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        print(f"creator_score: invalid input: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
