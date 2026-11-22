#!/usr/bin/env python3
"""Score one freelance job from the signals Andrew pastes. Standard library only.

Order of evaluation:
1. Kill gates: hard red flags -> Report; already hired or a fit mismatch -> Skip.
2. If the client panel is missing entirely -> Hold (ask for it before ruling).
3. A 100-point score across fit, economics, client, competition, freshness.
   Unknown signals earn about half credit and are listed, so missing data never
   reads as good or bad data.

The thresholds are sample screening preferences, not platform rules; change them with
--apply-at and --caution-at. The score supports judgment; it does not replace it.

Input: a JSON file (or - for stdin) with any of these keys; omit what is unknown.
{
  "fit": "strong" | "conditional" | "mismatch",
  "budget_type": "hourly" | "fixed",
  "budget_low": 25, "budget_high": 50,      # hourly range
  "budget_fixed": 1500, "estimated_hours": 30,  # fixed price and raw likely hours
  "payment_verified": true, "client_spend": 12000, "hires": 8,
  "hire_rate": 0.6, "rating": 4.8,
  "proposals_low": 5,                       # lower bound of the displayed range
  "already_hired": false, "posted_hours_ago": 2,
  "red_flags": ["off_platform_contact"]
}

red_flags are normalized (lowercase; hyphens and spaces become underscores) and
common synonyms are mapped (telegram -> off_platform_contact, paypal ->
off_platform_payment, laptop -> equipment_purchase, ...). Any flag that still is
not recognized caps the verdict at Hold: judge it by hand. hire_rate above 1 is
read as a percent (15 -> 0.15). Print the accepted keys with --list-flags.

The $45 floor is a gross rate (example screening threshold);
the output also shows the effective rate net of 10% and 15% fees.

Example:  python vet_score.py job.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys

HARD_FLAGS = {
    "off_platform_contact": "asks to move contact off the platform before a contract",
    "off_platform_payment": "asks to pay or be paid outside the platform",
    "unpaid_test": "unpaid test task, sample, or spec work",
    "fee_or_deposit": "asks Andrew to pay a fee, deposit, training, or software cost",
    "equipment_purchase": "asks Andrew to buy equipment or gift cards for reimbursement",
    "overpayment_check": "check or overpayment with money sent back",
    "crypto_or_money_transfer": "asks to receive, convert, or forward money or crypto",
    "credentials_request": "asks for passwords, 2FA codes, or keys outside a proper access process",
    "account_rental": "wants to rent or use Andrew's account or identity",
    "malware_repo": "unsolicited take-home repository to clone and run",
    "task_scam": "pays to like, rate, or boost products, then asks for a deposit",
    "prompt_injection": "listing text tries to instruct an AI",
}
FLAG_SYNONYMS = {
    "telegram": "off_platform_contact", "whatsapp": "off_platform_contact", "signal": "off_platform_contact",
    "skype": "off_platform_contact", "discord": "off_platform_contact", "off_platform": "off_platform_contact",
    "move_off_platform": "off_platform_contact",
    "pay_outside": "off_platform_payment", "paypal": "off_platform_payment", "venmo": "off_platform_payment",
    "zelle": "off_platform_payment",
    "buy_laptop": "equipment_purchase", "buy_equipment": "equipment_purchase", "laptop": "equipment_purchase",
    "check": "overpayment_check", "overpayment": "overpayment_check",
    "crypto": "crypto_or_money_transfer",
    "free_test": "unpaid_test", "unpaid_trial": "unpaid_test",
}
RATE_FLOOR = 45.0  # gross $/h, example screening threshold
NET_FEES = (0.10, 0.15)
NUMERIC_KEYS = ("budget_low", "budget_high", "budget_fixed", "estimated_hours", "client_spend", "hires",
                "hire_rate", "rating", "proposals_low", "posted_hours_ago")
UNRECOGNIZED_REASON = "unrecognized red flag: judge by hand"


def normalize_flag(flag: str) -> str:
    key = re.sub(r"[\s-]+", "_", flag.strip().lower())
    return FLAG_SYNONYMS.get(key, key)


def validate(job) -> dict:
    """Raise ValueError (exit 2) for input the scorer would misread."""
    if not isinstance(job, dict):
        raise ValueError("input must be a JSON object of job signals")
    flags = job.get("red_flags", [])
    if flags is None:
        flags = []
    if not isinstance(flags, list) or not all(isinstance(f, str) for f in flags):
        raise ValueError("red_flags must be a list of strings, e.g. [\"off_platform_contact\"]")
    for key in NUMERIC_KEYS:
        value = job.get(key)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise ValueError(f"{key} must be a number (no commas, currency signs, or quotes), got {value!r}")
    job = dict(job)
    job["red_flags"] = flags
    if job.get("hire_rate") is not None and job["hire_rate"] > 1:
        job["hire_rate"] = job["hire_rate"] / 100
    return job


def fee_label(fee: float) -> str:
    return f"{fee * 100:g}%"


def effective_rate(job: dict) -> float | None:
    if job.get("budget_type") == "hourly" and job.get("budget_high") is not None:
        return float(job["budget_high"])
    if job.get("budget_type") == "fixed" and job.get("budget_fixed") and job.get("estimated_hours"):
        return float(job["budget_fixed"]) / float(job["estimated_hours"])
    return None


def score(job: dict, apply_at: int = 70, caution_at: int = 55) -> dict:
    result = _score(validate(job), apply_at, caution_at)
    return result


def _score(job: dict, apply_at: int, caution_at: int) -> dict:
    unknown: list[str] = []
    reasons: list[str] = []
    normalized = []
    for f in job["red_flags"]:
        n = normalize_flag(f)
        if n not in normalized:
            normalized.append(n)
    flags = [f for f in normalized if f in HARD_FLAGS]
    unknown_flags = [f for f in normalized if f not in HARD_FLAGS]
    if flags:
        return {"verdict": "Report", "score": None,
                "reasons": [HARD_FLAGS[f] for f in flags], "unknown": [], "unrecognized_flags": unknown_flags}

    def capped(result: dict) -> dict:
        result["unrecognized_flags"] = unknown_flags
        if unknown_flags:
            if result["verdict"] in ("Apply", "Apply with caution"):
                result["verdict"] = "Hold"
            result["reasons"] = [UNRECOGNIZED_REASON] + result["reasons"]
        return result

    if job.get("already_hired") is True:
        return capped({"verdict": "Skip", "score": None, "reasons": ["someone is already hired"], "unknown": []})
    if job.get("fit") == "mismatch":
        return capped({"verdict": "Skip", "score": None,
                       "reasons": ["core work is outside the freelancer's confirmed skills"], "unknown": []})
    rate = effective_rate(job)
    if rate is not None and rate < 30:
        return capped({"verdict": "Skip", "score": None,
                       "reasons": [f"effective rate about ${rate:.0f}/h cannot cover the work at his floor"],
                       "unknown": []})
    client_keys = ("payment_verified", "client_spend", "hires", "hire_rate", "rating")
    if all(job.get(k) is None for k in client_keys):
        return capped({"verdict": "Hold", "score": None,
                       "reasons": ["client panel missing: paste payment verification, spend, hires, hire rate, rating"],
                       "unknown": list(client_keys)})

    total = 0.0
    # Fit (30)
    fit = job.get("fit")
    if fit == "strong":
        total += 30
    elif fit == "conditional":
        total += 15
        reasons.append("conditional fit: name the gap honestly")
    else:
        total += 15
        unknown.append("fit")
    # Economics (20)
    if rate is None:
        total += 10
        unknown.append("economics")
    elif rate >= RATE_FLOOR:
        total += 20
    elif rate >= 35:
        total += 10
        reasons.append(f"tight economics: about ${rate:.0f}/h effective")
    else:
        total += 3
        reasons.append(f"low economics: about ${rate:.0f}/h effective")
    # Client (25)
    pv = job.get("payment_verified")
    total += 8 if pv is True else 0 if pv is False else 4
    if pv is None:
        unknown.append("payment_verified")
    elif pv is False:
        reasons.append("payment not verified")
    spend, hires = job.get("client_spend"), job.get("hires")
    if spend is None and hires is None:
        total += 3.5
        unknown.append("client history")
    elif (spend or 0) > 0 or (hires or 0) > 0:
        total += 7
    else:
        reasons.append("new client with no history (unknown, not bad)")
        total += 3
    hr = job.get("hire_rate")
    if hr is None:
        total += 2.5
        unknown.append("hire_rate")
    elif hr >= 0.5:
        total += 5
    elif hr < 0.2 and (hires or 0) == 0 and (spend or 0) == 0:
        total += 2
    else:
        total += 1
        reasons.append("low hire rate")
    rating = job.get("rating")
    if rating is None:
        total += 2.5
        unknown.append("rating")
    elif rating >= 4.5:
        total += 5
    elif rating >= 4.0:
        total += 3
    else:
        reasons.append(f"client rating {rating}")
    # Competition (15)
    p = job.get("proposals_low")
    if p is None:
        total += 7
        unknown.append("proposals")
    elif p < 5:
        total += 15
    elif p < 10:
        total += 10
    elif p < 20:
        total += 5
    else:
        total += 2
        reasons.append("heavy competition")
    # Freshness (10)
    age = job.get("posted_hours_ago")
    if age is None:
        total += 5
        unknown.append("posted age")
    elif age <= 1:
        total += 10
    elif age <= 6:
        total += 7
    elif age <= 24:
        total += 4
    else:
        total += 1
        reasons.append("older post: check it is still open")

    final = round(total)
    verdict = "Apply" if final >= apply_at else "Apply with caution" if final >= caution_at else "Skip"
    return capped({"verdict": verdict, "score": final, "reasons": reasons, "unknown": unknown,
                   "effective_rate": round(rate, 2) if rate is not None else None,
                   "effective_rate_net": ({fee_label(f): round(rate * (1 - f), 2) for f in NET_FEES}
                                          if rate is not None else None),
                   "rate_floor_gross": RATE_FLOOR})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", nargs="?", help="job signals JSON, or - for stdin")
    parser.add_argument("--apply-at", type=int, default=70)
    parser.add_argument("--caution-at", type=int, default=55)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list-flags", action="store_true", help="print the accepted red_flags keys and synonyms")
    args = parser.parse_args(argv)
    if args.list_flags:
        if args.json:
            print(json.dumps({"flags": HARD_FLAGS, "synonyms": FLAG_SYNONYMS}, indent=2))
        else:
            for key, desc in HARD_FLAGS.items():
                syn = sorted(s for s, target in FLAG_SYNONYMS.items() if target == key)
                print(f"{key}: {desc}" + (f" (also: {', '.join(syn)})" if syn else ""))
        return 0
    if not args.file:
        parser.print_usage(sys.stderr)
        print("error: a job signals file (or -) is required", file=sys.stderr)
        return 2
    try:
        if args.file == "-":
            job = json.load(sys.stdin)
        else:
            with open(args.file, encoding="utf-8") as fh:
                job = json.load(fh)
        result = score(job, args.apply_at, args.caution_at)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        head = result["verdict"] + (f" ({result['score']}/100)" if result["score"] is not None else "")
        print(head)
        for r in result["reasons"]:
            print(f"- {r}")
        if result.get("effective_rate") is not None:
            nets = ", ".join(f"${v:.2f} net at {k}" for k, v in result["effective_rate_net"].items())
            print(f"effective rate: ${result['effective_rate']:.2f}/h gross ({nets}); floor ${RATE_FLOOR:.0f}/h gross")
        if result["unknown"]:
            print("unknown: " + ", ".join(result["unknown"]))
        if result.get("unrecognized_flags"):
            print("unrecognized flags (judge by hand): " + ", ".join(result["unrecognized_flags"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
