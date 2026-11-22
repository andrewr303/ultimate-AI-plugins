#!/usr/bin/env python3
"""Deterministic pricing math for freelance-legend.

Standard library only. Every number a proposal quotes should come from here so
the inputs, formulas, and results can be checked.

Subcommands
-----------
estimate    Bottom-up task estimate -> raw and multiplied hours, price at rate,
            budget comparison, effective rate at the client's budget, net after fee.
milestones  Split a fixed total into milestones that sum exactly to the total.
hourly      Weekly range and phase total for an hourly engagement, with net.
gross       Gross price or rate needed to net a target after a platform fee.
connects-ev Expected value of spending Connects on a proposal, and break-even win odds.

Examples
--------
python price.py estimate --task "Spec review:2:3" --task "Calc engine:10:14" \
    --rate 50 --budget-fixed 1500
python price.py milestones --total 2400 --split 20,40,40 --days 7,21,35
python price.py hourly --rate 50 --hours 15-20 --weeks 6
python price.py gross --net 45 --fee 0.10
python price.py connects-ev --connects 10 --boost 4 --project-gross 6000 --fee 0.10 --win-prob 0.05

--json works before or after the subcommand. The $45/h floor is a GROSS rate
(example screening threshold); outputs also show net-at-fee
rates. Net figures are before income and self-employment tax.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

DEFAULT_FEES = (Decimal("0.10"), Decimal("0.15"))
RATE_FLOOR = Decimal("45")  # gross $/h, example screening threshold
PHASE_RATIO = Decimal("1.5")
TAX_NOTE = "Net figures are before income and self-employment tax."
REC_WITHIN = "bid within budget with stated scope; note the doubled figure"
REC_PHASE = "offer a narrower first phase or explain the full price"
REC_PRICE = "bid the full price with stated scope and explain it; the budget is within 1.5x"


def fee_label(fee: Decimal) -> str:
    """Exact percent label: 0.105 -> '10.5%', 0.10 -> '10%'."""
    return f"{(fee * 100).normalize():f}%"


def pct(value: Decimal) -> str:
    return f"{money(value).normalize():f}"


def nets(amount: Decimal, fees: tuple[Decimal, ...]) -> dict[str, str]:
    return {fee_label(f): str(money(amount * (1 - f))) for f in fees}


def positive(name: str, value: Decimal | None) -> None:
    if value is not None and value <= 0:
        raise ValueError(f"{name} must be positive")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def whole(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def parse_task(spec: str) -> dict[str, Any]:
    """Parse "name:low:likely" (name may contain colons only if quoted away)."""
    parts = spec.rsplit(":", 2)
    if len(parts) != 3:
        raise ValueError(f"task must be 'name:low:likely', got {spec!r}")
    name, low, likely = parts
    low_d, likely_d = Decimal(low), Decimal(likely)
    if low_d < 0 or likely_d < 0:
        raise ValueError(f"hours must be non-negative in {spec!r}")
    if likely_d < low_d:
        raise ValueError(f"likely hours below low hours in {spec!r}")
    return {"name": name.strip(), "low": low_d, "likely": likely_d}


def parse_range(text: str) -> tuple[Decimal, Decimal]:
    if "-" in text:
        lo, hi = text.split("-", 1)
        lo_d, hi_d = Decimal(lo), Decimal(hi)
    else:
        lo_d = hi_d = Decimal(text)
    if hi_d < lo_d:
        raise ValueError(f"range upper bound below lower bound: {text!r}")
    return lo_d, hi_d


def parse_fees(text: str | None) -> tuple[Decimal, ...]:
    if not text:
        return DEFAULT_FEES
    fees: list[Decimal] = []
    for part in text.split(","):
        fee = Decimal(part)
        if not Decimal("0") <= fee < Decimal("1"):
            raise ValueError("fees are fractions, e.g. 0.10 for 10%")
        if fee not in fees:
            fees.append(fee)
    return tuple(fees)


def estimate(tasks: list[dict[str, Any]], rate: Decimal, multiplier: Decimal,
             fees: tuple[Decimal, ...], budget_fixed: Decimal | None,
             budget_hourly: tuple[Decimal, Decimal] | None, bid: Decimal | None = None) -> dict[str, Any]:
    if not tasks:
        raise ValueError("at least one --task is required")
    positive("--rate", rate)
    positive("--multiplier", multiplier)
    positive("--bid", bid)
    raw_low = sum((t["low"] for t in tasks), Decimal("0"))
    raw_likely = sum((t["likely"] for t in tasks), Decimal("0"))
    planned_hours = raw_likely * multiplier
    price = money(planned_hours * rate)
    result: dict[str, Any] = {
        "tasks": [{"name": t["name"], "low": str(t["low"]), "likely": str(t["likely"])} for t in tasks],
        "raw_low_hours": str(raw_low),
        "raw_likely_hours": str(raw_likely),
        "multiplier": str(multiplier),
        "planned_hours": str(planned_hours),
        "rate": str(money(rate)),
        "price_at_rate": str(price),
        "formula": f"{raw_likely} likely h x {multiplier} x ${money(rate)}/h = ${price}",
        "net_after_fee": nets(price, fees),
        "rate_floor_gross": str(money(RATE_FLOOR)),
        "warnings": [],
    }
    if rate < RATE_FLOOR:
        result["warnings"].append(f"rate ${money(rate)}/h is below the ${RATE_FLOOR}/h floor")
    if budget_fixed is not None:
        if budget_fixed <= 0:
            raise ValueError("--budget-fixed must be positive")
        eff_planned = money(budget_fixed / planned_hours) if planned_hours else None
        eff_raw = money(budget_fixed / raw_likely) if raw_likely else None
        result["budget"] = {
            "type": "fixed",
            "amount": str(money(budget_fixed)),
            "gap_vs_price": str(money(price - budget_fixed)),
            "effective_rate_on_planned_hours": str(eff_planned) if eff_planned is not None else None,
            "effective_rate_on_raw_likely_hours": str(eff_raw) if eff_raw is not None else None,
            "effective_rate_on_raw_likely_hours_net": nets(eff_raw, fees) if eff_raw is not None else None,
            "net_after_fee": nets(budget_fixed, fees),
            "price_to_budget_ratio": str((price / budget_fixed).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        }
        ratio = price / budget_fixed
        if eff_raw is not None and eff_raw >= RATE_FLOOR:
            result["recommendation"] = REC_WITHIN
        elif ratio > PHASE_RATIO:
            result["recommendation"] = REC_PHASE
        else:
            result["recommendation"] = REC_PRICE
        if eff_raw is not None and eff_raw < RATE_FLOOR:
            result["warnings"].append(
                "budget implies less than the rate floor even on raw likely hours: "
                "narrow the scope or explain the price")
    if budget_hourly is not None:
        lo, hi = budget_hourly
        result["budget"] = {
            "type": "hourly",
            "range": f"{money(lo)}-{money(hi)}",
            "rate_position": ("above range" if rate > hi else "below range" if rate < lo else "within range"),
            "phase_cost_at_rate": str(price),
            "phase_cost_at_client_max": str(money(planned_hours * hi)),
        }
        if hi < RATE_FLOOR:
            result["warnings"].append("client's hourly ceiling is below the rate floor")
    if bid is not None:
        eff_bid_raw = money(bid / raw_likely) if raw_likely else None
        eff_bid_planned = money(bid / planned_hours) if planned_hours else None
        result["bid"] = {
            "amount": str(money(bid)),
            "net_after_fee": nets(bid, fees),
            "effective_rate_on_planned_hours": str(eff_bid_planned) if eff_bid_planned is not None else None,
            "effective_rate_on_raw_likely_hours": str(eff_bid_raw) if eff_bid_raw is not None else None,
            "effective_rate_on_raw_likely_hours_net": nets(eff_bid_raw, fees) if eff_bid_raw is not None else None,
        }
        if eff_bid_raw is not None and eff_bid_raw < RATE_FLOOR:
            result["warnings"].append("bid implies less than the rate floor even on raw likely hours")
    return result


def milestones(total: Decimal, split: list[Decimal], days: list[int] | None,
               names: list[str] | None) -> dict[str, Any]:
    if total <= 0:
        raise ValueError("--total must be positive")
    if not 2 <= len(split) <= 6:
        raise ValueError("use between 2 and 6 milestones")
    if any(pct_ <= 0 for pct_ in split):
        raise ValueError("every split percentage must be positive")
    if sum(split) != Decimal("100"):
        raise ValueError(f"split percentages must sum to 100, got {sum(split)}")
    if days is not None and len(days) != len(split):
        raise ValueError("--days needs one value per milestone")
    if days is not None and any(b <= a for a, b in zip(days, days[1:])):
        raise ValueError("--days must be strictly increasing")
    if names is not None and len(names) != len(split):
        raise ValueError("--names needs one value per milestone")
    amounts = [whole(total * pct / 100) for pct in split[:-1]]
    amounts.append(money(total - sum(amounts, Decimal("0"))))
    if amounts[-1] <= 0:
        raise ValueError("rounding left the last milestone non-positive; adjust the split")
    rows = []
    for i, amount in enumerate(amounts):
        rows.append({
            "n": i + 1,
            "name": names[i] if names else f"Milestone {i + 1}",
            "percent": pct(money(amount) / total * 100),
            "nominal_percent": str(split[i]),
            "amount": str(money(amount)),
            "due": f"Day {days[i]}" if days else None,
        })
    check = sum((Decimal(r["amount"]) for r in rows), Decimal("0"))
    warnings = []
    first_share = Decimal(rows[0]["amount"]) / total * 100
    if not Decimal("10") <= first_share <= Decimal("25"):
        warnings.append(f"first milestone is {money(first_share)}% of the total; the default is 10-25%")
    return {"total": str(money(total)), "sum_check": str(money(check)),
            "sums_exactly": money(check) == money(total), "milestones": rows, "warnings": warnings}


def hourly(rate: Decimal, hours: tuple[Decimal, Decimal], weeks: Decimal,
           fees: tuple[Decimal, ...], capacity: Decimal) -> dict[str, Any]:
    lo, hi = hours
    positive("--rate", rate)
    if lo < 0:
        raise ValueError("--hours cannot be negative")
    if weeks <= 0:
        raise ValueError("--weeks must be positive")
    warnings = []
    if hi > capacity:
        warnings.append(f"upper weekly hours {hi} exceed stated capacity {capacity}; confirm with the freelancer")
    if rate < RATE_FLOOR:
        warnings.append(f"rate ${money(rate)}/h is below the ${RATE_FLOOR}/h floor")
    weekly_lo, weekly_hi = money(rate * lo), money(rate * hi)
    total_lo, total_hi = money(weekly_lo * weeks), money(weekly_hi * weeks)
    return {
        "rate": str(money(rate)), "hours_per_week": f"{lo}-{hi}", "weeks": str(weeks),
        "weekly_billing": f"{weekly_lo}-{weekly_hi}",
        "phase_total": f"{total_lo}-{total_hi}",
        "net_rate_after_fee": nets(rate, fees),
        "net_phase_after_fee": {fee_label(f): f"{money(total_lo * (1 - f))}-{money(total_hi * (1 - f))}"
                                for f in fees},
        "warnings": warnings,
    }


def gross(net: Decimal, fee: Decimal) -> dict[str, Any]:
    if net <= 0:
        raise ValueError("--net must be positive")
    if not Decimal("0") <= fee < Decimal("1"):
        raise ValueError("--fee is a fraction, e.g. 0.10 for 10%")
    exact = net / (1 - fee)
    # Round up to the cent so the net never falls short of the target.
    rounded = exact.quantize(Decimal("0.01"), rounding="ROUND_CEILING")
    return {"net_target": str(money(net)), "fee": str(fee), "gross": str(rounded),
            "net_at_gross": str(money(rounded * (1 - fee))),
            "formula": f"{money(net)} / (1 - {fee}) = {rounded}", "warnings": []}


CONNECT_PRICE = Decimal("0.15")


def connects_ev(connects: int, boost: int, project_gross: Decimal, fee: Decimal,
                win_prob: Decimal | None) -> dict[str, Any]:
    if connects < 0 or boost < 0:
        raise ValueError("Connects cannot be negative")
    if project_gross <= 0 or not Decimal("0") <= fee < Decimal("1"):
        raise ValueError("--project-gross must be positive and --fee a fraction")
    cost = (connects + boost) * CONNECT_PRICE
    net = project_gross * (1 - fee)
    result: dict[str, Any] = {
        "connects": connects, "boost": boost, "cost_usd": str(money(cost)),
        "note": "boost Connects are charged only if the bid finishes top four or the client interacts; "
                "this treats them as spent (worst case)",
        "project_net": str(money(net)),
        "break_even_win_probability": str((cost / net).quantize(Decimal("0.00001"))),
        "warnings": [],
    }
    if win_prob is not None:
        if not Decimal("0") <= win_prob <= Decimal("1"):
            raise ValueError("--win-prob is a fraction between 0 and 1")
        result["win_probability"] = str(win_prob)
        result["expected_value_usd"] = str(money(win_prob * net - cost))
        result["warnings"].append("win probability is an assumption unless it comes from Andrew's own logged results")
    return result


def render(result: dict[str, Any], kind: str) -> str:
    lines: list[str] = []
    if kind == "estimate":
        lines.append("| Task | Low h | Likely h |")
        lines.append("| --- | ---: | ---: |")
        for t in result["tasks"]:
            lines.append(f"| {t['name']} | {t['low']} | {t['likely']} |")
        lines.append(f"| **Raw total** | {result['raw_low_hours']} | {result['raw_likely_hours']} |")
        lines.append("")
        lines.append(f"Planned hours: {result['planned_hours']} (x{result['multiplier']})")
        lines.append(f"Price: {result['formula']}")
        lines.append(f"Net of fee on the price ${result['price_at_rate']}: " + fmt_nets(result["net_after_fee"]))
        budget = result.get("budget")
        if budget and budget["type"] == "fixed":
            lines.append(f"Client budget: ${budget['amount']} (price minus budget: ${budget['gap_vs_price']})")
            lines.append(f"Net of fee at the client budget ${budget['amount']}: " + fmt_nets(budget["net_after_fee"]))
            raw_net = budget.get("effective_rate_on_raw_likely_hours_net")
            lines.append(f"Effective rate at budget ${budget['amount']}: ${budget['effective_rate_on_planned_hours']}/h "
                         f"on planned hours, ${budget['effective_rate_on_raw_likely_hours']}/h on raw likely hours"
                         + (f" (net {fmt_nets(raw_net, '/h')})" if raw_net else "")
                         + f"; floor ${result['rate_floor_gross']}/h gross")
            lines.append(f"Doubled price / budget: {budget['price_to_budget_ratio']}x")
        elif budget:
            lines.append(f"Client hourly range: ${budget['range']} ({budget['rate_position']})")
        bid = result.get("bid")
        if bid:
            lines.append(f"Net of fee at the bid ${bid['amount']}: " + fmt_nets(bid["net_after_fee"]))
            raw_net = bid.get("effective_rate_on_raw_likely_hours_net")
            lines.append(f"Effective rate at bid ${bid['amount']}: ${bid['effective_rate_on_planned_hours']}/h on "
                         f"planned hours, ${bid['effective_rate_on_raw_likely_hours']}/h on raw likely hours"
                         + (f" (net {fmt_nets(raw_net, '/h')})" if raw_net else ""))
        if result.get("budget", {}).get("type") == "fixed":
            lines.append(f"Recommendation: {result['recommendation']}")
    elif kind == "milestones":
        for m in result["milestones"]:
            due = f" · due {m['due']}" if m["due"] else ""
            lines.append(f"{m['n']}. {m['name']} · ${m['amount']} ({m['percent']}%){due}")
        lines.append(f"Sum ${result['sum_check']} of ${result['total']}: "
                     f"{'exact' if result['sums_exactly'] else 'MISMATCH'}")
    elif kind == "hourly":
        lines.append(f"${result['rate']}/h x {result['hours_per_week']} h/week = ${result['weekly_billing']} per week")
        lines.append(f"{result['weeks']} weeks: ${result['phase_total']}")
        lines.append("Net rate: " + ", ".join(f"{k}: ${v}/h" for k, v in result["net_rate_after_fee"].items()))
    elif kind == "connects-ev":
        lines.append(f"Cost: {result['connects']}+{result['boost']} Connects = ${result['cost_usd']}; "
                     f"project net ${result['project_net']}")
        lines.append(f"Break-even win probability: {result['break_even_win_probability']}")
        if "expected_value_usd" in result:
            lines.append(f"Expected value at p={result['win_probability']}: ${result['expected_value_usd']}")
    elif kind == "gross":
        lines.append(f"Gross needed: ${result['gross']} ({result['formula']}); nets ${result['net_at_gross']}")
    for w in result.get("warnings", []):
        lines.append(f"WARNING: {w}")
    lines.append(TAX_NOTE)
    return "\n".join(lines)


def fmt_nets(values: dict[str, str], unit: str = "") -> str:
    return ", ".join(f"{k}: ${v}{unit}" for k, v in values.items())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="print JSON instead of text")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add(name: str):
        return sub.add_parser(name, parents=[common])

    est = add("estimate")
    est.add_argument("--task", action="append", default=[], help="name:low:likely (hours)")
    est.add_argument("--tasks-json", help="file with [{name, low, likely}, ...]")
    est.add_argument("--rate", type=Decimal, default=Decimal("50"))
    est.add_argument("--multiplier", type=Decimal, default=Decimal("2"))
    est.add_argument("--fees", help="comma-separated fee fractions (default 0.10,0.15)")
    group = est.add_mutually_exclusive_group()
    group.add_argument("--budget-fixed", type=Decimal)
    group.add_argument("--budget-hourly", help="lo-hi, e.g. 25-50")
    est.add_argument("--bid", type=Decimal, help="the amount Andrew will bid; shows the net at that bid")

    ms = add("milestones")
    ms.add_argument("--total", type=Decimal, required=True)
    ms.add_argument("--split", required=True, help="percentages, e.g. 20,40,40")
    ms.add_argument("--days", help="relative due days, e.g. 7,21,35")
    ms.add_argument("--names", help="milestone names separated by '|'")

    hr = add("hourly")
    hr.add_argument("--rate", type=Decimal, default=Decimal("50"))
    hr.add_argument("--hours", required=True, help="weekly hours range, e.g. 15-20")
    hr.add_argument("--weeks", type=Decimal, required=True)
    hr.add_argument("--fees")
    hr.add_argument("--capacity", type=Decimal, default=Decimal("25"))

    gr = add("gross")
    gr.add_argument("--net", type=Decimal, required=True, help="target net amount or hourly rate")
    gr.add_argument("--fee", type=Decimal, required=True, help="fee fraction, e.g. 0.20 for Fiverr")

    ev = add("connects-ev")
    ev.add_argument("--connects", type=int, required=True)
    ev.add_argument("--boost", type=int, default=0)
    ev.add_argument("--project-gross", type=Decimal, required=True)
    ev.add_argument("--fee", type=Decimal, default=Decimal("0.10"))
    ev.add_argument("--win-prob", type=Decimal)

    args = parser.parse_args(argv)
    try:
        if args.cmd == "connects-ev":
            result = connects_ev(args.connects, args.boost, args.project_gross, args.fee, args.win_prob)
        elif args.cmd == "gross":
            result = gross(args.net, args.fee)
        elif args.cmd == "estimate":
            tasks = [parse_task(t) for t in args.task]
            if args.tasks_json:
                with open(args.tasks_json, encoding="utf-8") as fh:
                    for item in json.load(fh):
                        tasks.append(parse_task(f"{item['name']}:{item['low']}:{item['likely']}"))
            result = estimate(tasks, args.rate, args.multiplier, parse_fees(args.fees), args.budget_fixed,
                              parse_range(args.budget_hourly) if args.budget_hourly else None, args.bid)
        elif args.cmd == "milestones":
            split = [Decimal(s) for s in args.split.split(",")]
            days = [int(d) for d in args.days.split(",")] if args.days else None
            names = [n.strip() for n in args.names.split("|")] if args.names else None
            result = milestones(args.total, split, days, names)
        else:
            result = hourly(args.rate, parse_range(args.hours), args.weeks, parse_fees(args.fees), args.capacity)
    except (ValueError, ArithmeticError, OSError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else render(result, args.cmd))
    if args.cmd == "milestones" and not result["sums_exactly"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
