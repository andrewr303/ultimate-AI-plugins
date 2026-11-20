#!/usr/bin/env python3
"""Freelance pipeline ledger: dedupe jobs, track proposals and outcomes.

Standard library only. The ledger is an append-only JSONL file; the latest
event for a key wins. It stores short records only (no full listing text, no
credentials, no client contact details).

User data directory: $FREELANCE_LEGEND_HOME, else $CLAUDE_PLUGIN_DATA, else
~/.freelance-legend. Default ledger: --ledger, else $FREELANCE_LEGEND_LEDGER, else
<data-dir>/pipeline.jsonl. Run markers live in runs.jsonl next to the ledger.

Commands
--------
init                                  create the data dir and the live approved-proof file
normalize <id-or-url>                 print the stable key for a job
seen <id-or-url> [--platform P]       exit 0 if already recorded, 1 if new
add <id-or-url> --title T --status S  record an event (also used for updates)
seed <file> [--platform P]            record IDs from a file as already notified
list [--status S] [--platform P]      latest state of each job
stats [--today YYYY-MM-DD]            funnel, Connects and boost spent, overdue invoices
run-start / run-done [--note N]       record the start or successful end of a scanner run
last-run                              print the last run-done time (exit 1 if none)

The platform is inferred from the URL host when a URL is given; --platform
overrides it. Bare IDs and ~0 tokens default to upwork. Pass --connects and
--boost only on the event where they were spent: stats sums them per event.
--ledger and --json work before or after the subcommand.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

STATUSES = [
    "seen", "invited", "needs-listing", "held", "rejected", "notified", "drafting", "submitted",
    "viewed", "interviewing", "offer", "hired", "invoiced", "paid", "declined", "no-response", "withdrawn",
    "archived",
]
FUNNEL = ["submitted", "viewed", "interviewing", "offer", "hired"]
UPWORK_TOKEN = re.compile(r"~0([12])([0-9a-z]+)", re.I)
UPWORK_DIGITS = re.compile(r"(?<!\d)(?:0[12])?(\d{19})(?!\d)")
DISALLOWED_KEYS = {"description", "listing", "email", "phone", "password", "token", "cookie"}
FREE_TEXT = ("title", "reason", "angle", "url", "invoice", "note")
CONTACT_EMAIL = re.compile(r"[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")
CONTACT_PHONE = re.compile(
    r"(?<![\w.])(?:\+?1[\s.-]?)?(?:\(\d{3}\)\s?|\d{3}[\s.-])\d{3}[\s.-]\d{4}(?!\d)"
    r"|(?<![\w+])\+\d{1,3}[\s.-]?\(?\d{1,4}\)?(?:[\s.-]\d{2,4}){2,}(?!\d)")
HOST_PLATFORMS = [
    ("upwork.com", "upwork"), ("freelancer.com", "freelancer"), ("contra.com", "contra"),
    ("fiverr.com", "fiverr"), ("linkedin.com", "linkedin"), ("peopleperhour.com", "peopleperhour"),
    ("toptal.com", "toptal"), ("arc.dev", "arc"), ("wellfound.com", "wellfound"), ("gun.io", "gunio"),
    ("news.ycombinator.com", "hn"), ("weworkremotely.com", "wwr"),
]
URL_HOST = re.compile(r"^(?:[a-z][a-z0-9+.-]*://)?(?:www\.)?([a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,})(?=[/:?#]|$)", re.I)


def data_dir() -> Path:
    for var in ("FREELANCE_LEGEND_HOME", "CLAUDE_PLUGIN_DATA"):
        value = os.environ.get(var)
        if value:
            return Path(value).expanduser()
    return Path.home() / ".freelance-legend"


def ledger_path(arg: str | None) -> Path:
    if arg:
        return Path(arg).expanduser()
    env = os.environ.get("FREELANCE_LEGEND_LEDGER")
    return Path(env).expanduser() if env else data_dir() / "pipeline.jsonl"


def runs_path(ledger: Path) -> Path:
    return ledger.parent / "runs.jsonl"


def infer_platform(raw: str) -> str | None:
    """Platform from the URL host, or None when the text is not a URL."""
    m = URL_HOST.match(raw.strip())
    if not m:
        return None
    host = m.group(1).lower()
    for suffix, name in HOST_PLATFORMS:
        if host == suffix or host.endswith("." + suffix):
            return name
    if "braintrust" in host:
        return "braintrust"
    return host


def check_free_text(field: str, value: str | None) -> None:
    if value is None:
        return
    if CONTACT_EMAIL.search(value) or CONTACT_PHONE.search(value):
        raise UsageError(f"refusing to store contact details in --{field}; the ledger keeps no email or phone")


class UsageError(ValueError):
    """Bad input: exit 2."""


def parse_date(field: str, value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise UsageError(f"--{field} must be YYYY-MM-DD, got {value!r}") from exc


def normalize(raw: str, platform: str | None = None) -> str:
    """Return 'platform:id'. Upwork ~01/~02 tokens and URL variants collapse to one key."""
    text = raw.strip()
    plat = (platform or infer_platform(text) or "upwork").lower()
    if plat == "upwork" or "upwork.com" in text.lower():
        plat = "upwork"
        token = UPWORK_TOKEN.search(text)
        if token:
            body = token.group(2).lower()
            return f"upwork:{body}"
        digits = UPWORK_DIGITS.search(text)
        if digits:
            return f"upwork:{digits.group(1)}"
    cleaned = re.sub(r"[?#].*$", "", text).rstrip("/").lower()
    cleaned = re.sub(r"^https?://(www\.)?", "", cleaned)
    if not cleaned:
        raise ValueError("empty job id")
    return f"{plat}:{cleaned}"


def read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events = []
    with path.open(encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{n}: invalid JSON ({exc})") from exc
    return events


def latest(events: list[dict]) -> dict[str, dict]:
    state: dict[str, dict] = {}
    for ev in events:
        if "key" not in ev:
            continue
        merged = {**state.get(ev["key"], {}), **{k: v for k, v in ev.items() if v is not None}}
        merged.setdefault("history", [])
        merged["history"] = state.get(ev["key"], {}).get("history", []) + [ev["status"]]
        state[ev["key"]] = merged
    return state


def append(path: Path, event: dict) -> None:
    bad = DISALLOWED_KEYS & set(event)
    if bad:
        raise ValueError(f"refusing to store fields: {sorted(bad)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def cmd_add(args) -> int:
    if args.status not in STATUSES:
        print(f"error: status must be one of {', '.join(STATUSES)}", file=sys.stderr)
        return 2
    for field in ("title", "reason", "angle", "url", "invoice"):
        check_free_text(field, getattr(args, field))
    if args.fee is not None and not 0 <= args.fee < 1:
        raise UsageError("--fee is a fraction, e.g. 0.10 for 10%")
    if args.amount is not None and args.amount < 0:
        raise UsageError("--amount cannot be negative")
    if (args.connects or 0) < 0 or (args.boost or 0) < 0:
        raise UsageError("--connects and --boost cannot be negative")
    path = ledger_path(args.ledger)
    platform = args.platform or (infer_platform(args.url) if args.url else None)
    key = normalize(args.job, platform)
    event = {
        "key": key, "platform": key.split(":", 1)[0], "status": args.status, "at": args.at or now_iso(),
        "title": args.title, "url": args.url, "reason": args.reason, "angle": args.angle,
        "bid": args.bid, "connects": args.connects, "boost": args.boost, "budget": args.budget,
        "amount": args.amount, "due": parse_date("due", args.due), "invoice": args.invoice, "fee": args.fee,
        "met_on": parse_date("met-on", args.met_on),
    }
    append(path, {k: v for k, v in event.items() if v is not None})
    print(f"{key} -> {args.status}")
    return 0


def cmd_seen(args) -> int:
    key = normalize(args.job, args.platform)
    state = latest(read_events(ledger_path(args.ledger)))
    if key in state:
        print(f"seen: {key} (status {state[key]['status']})")
        return 0
    print(f"new: {key}")
    return 1


def cmd_seed(args) -> int:
    path = ledger_path(args.ledger)
    state = latest(read_events(path))
    added = 0
    for line in Path(args.file).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        key = normalize(line, args.platform)
        if key in state:
            continue
        append(path, {"key": key, "platform": key.split(":", 1)[0], "status": "notified",
                      "at": args.at or now_iso(), "reason": "seeded from previous scanner"})
        state[key] = {"status": "notified"}
        added += 1
    print(f"seeded {added} new key(s) into {path.resolve()}")
    return 0


def cmd_init(args) -> int:
    home = data_dir()
    home.mkdir(parents=True, exist_ok=True)
    proof = home / "approved-proof.md"
    template = Path(__file__).resolve().parents[1] / "references" / "approved-proof.md"
    if not proof.exists():
        if not template.exists():
            raise UsageError(f"approved-proof template missing at {template}")
        shutil.copyfile(template, proof)
    print(f"ledger: {ledger_path(args.ledger).resolve()}")
    print(f"approved proof: {proof.resolve()}")
    return 0


def cmd_run(args) -> int:
    path = runs_path(ledger_path(args.ledger))
    event = {"event": args.cmd, "at": args.at or now_iso()}
    if args.cmd == "run-done" and args.note:
        check_free_text("note", args.note)
        event["note"] = args.note
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")
    print(f"{args.cmd} {event['at']} ({path.resolve()})")
    return 0


def cmd_last_run(args) -> int:
    done = [e for e in read_events(runs_path(ledger_path(args.ledger))) if e.get("event") == "run-done"]
    if not done:
        print("no completed run recorded")
        return 1
    print(done[-1]["at"])
    return 0


def cmd_list(args) -> int:
    state = latest(read_events(ledger_path(args.ledger)))
    rows = [r for r in state.values()
            if (not args.status or r["status"] == args.status) and (not args.platform or r["platform"] == args.platform)]
    rows.sort(key=lambda r: r.get("at", ""), reverse=True)
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    for r in rows:
        print(f"{r.get('at', '')[:16]}  {r['status']:13} {r['key']:40} {r.get('title', '')}")
    if not rows:
        print("no records")
    return 0


def as_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def cmd_stats(args) -> int:
    path = ledger_path(args.ledger)
    events = read_events(path)
    state = latest(events)
    today = date.fromisoformat(parse_date("today", args.today)) if args.today else date.today()
    reached = Counter()
    for r in state.values():
        hist = set(r["history"])
        for i, stage in enumerate(FUNNEL):
            if stage in hist or any(s in hist for s in FUNNEL[i + 1:]):
                reached[stage] += 1
    connects = sum(as_int(ev.get("connects")) for ev in events if "key" in ev)
    boost = sum(as_int(ev.get("boost")) for ev in events if "key" in ev)
    overdue = []
    for r in state.values():
        hist = r["history"]
        if "invoiced" not in hist:
            continue
        last_inv = len(hist) - 1 - hist[::-1].index("invoiced")
        if "paid" in hist[last_inv:] or not r.get("due"):
            continue
        try:
            due = date.fromisoformat(r["due"])
        except (TypeError, ValueError):
            continue
        if due < today:
            overdue.append({"key": r["key"], "invoice": r.get("invoice"), "amount": r.get("amount"),
                            "due": r["due"], "days_overdue": (today - due).days})
    overdue.sort(key=lambda o: o["due"])
    out = {"ledger": str(path.resolve()), "jobs": len(state),
           "current_status": dict(Counter(r["status"] for r in state.values())),
           "funnel": {s: reached[s] for s in FUNNEL}, "connects_recorded": connects, "boost_recorded": boost,
           "overdue_invoices": overdue}
    sub = reached["submitted"]
    out["rates"] = {s: (round(reached[s] / sub, 3) if sub else None) for s in FUNNEL[1:]}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"ledger: {out['ledger']}")
        print(f"jobs tracked: {out['jobs']}")
        print("funnel: " + " -> ".join(f"{s} {reached[s]}" for s in FUNNEL))
        if sub:
            print("rates vs submitted: " + ", ".join(f"{k} {v:.0%}" for k, v in out["rates"].items()))
        print(f"connects recorded: {connects} (bids) + {boost} (boost) = {connects + boost}")
        for o in overdue:
            amount = f" ${o['amount']:.2f}" if isinstance(o["amount"], (int, float)) else ""
            print(f"OVERDUE: {o['key']} invoice {o['invoice'] or '?'}{amount} due {o['due']} "
                  f"({o['days_overdue']} days)")
        if sub and sub < 20:
            print("note: fewer than 20 proposals; treat rates as anecdotes, not a trend")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ledger", help="path to the JSONL ledger")
    parser.add_argument("--json", action="store_true", help="JSON output (list, stats)")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--ledger", default=argparse.SUPPRESS, help="path to the JSONL ledger")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="JSON output (list, stats)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add(name: str):
        return sub.add_parser(name, parents=[common])

    add("init")

    p = add("normalize")
    p.add_argument("job")
    p.add_argument("--platform", help="override the platform inferred from the URL host")

    p = add("seen")
    p.add_argument("job")
    p.add_argument("--platform", help="override the platform inferred from the URL host")

    p = add("add")
    p.add_argument("job")
    p.add_argument("--platform", help="override the platform inferred from the URL host")
    p.add_argument("--status", required=True)
    for opt in ("title", "url", "reason", "angle", "bid", "budget", "at"):
        p.add_argument(f"--{opt}")
    p.add_argument("--connects", type=int, help="Connects spent on this event")
    p.add_argument("--boost", type=int, help="boost Connects spent on this event")
    p.add_argument("--amount", type=float, help="amount billed or paid, USD")
    p.add_argument("--due", help="invoice due date, YYYY-MM-DD")
    p.add_argument("--invoice", help="invoice number or label")
    p.add_argument("--fee", type=float, help="platform fee taken, as a fraction (0.10)")
    p.add_argument("--met-on", help="date the client first met Andrew on a marketplace, YYYY-MM-DD")

    p = add("seed")
    p.add_argument("file")
    p.add_argument("--platform", help="override the platform inferred from each line")
    p.add_argument("--at")

    p = add("list")
    p.add_argument("--status")
    p.add_argument("--platform")

    p = add("stats")
    p.add_argument("--today", help="date to judge overdue invoices against, YYYY-MM-DD (default today)")

    for name in ("run-start", "run-done"):
        p = add(name)
        p.add_argument("--at")
        if name == "run-done":
            p.add_argument("--note")

    add("last-run")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "normalize":
            print(normalize(args.job, args.platform))
            return 0
        return {"seen": cmd_seen, "add": cmd_add, "seed": cmd_seed, "list": cmd_list, "stats": cmd_stats,
                "init": cmd_init, "run-start": cmd_run, "run-done": cmd_run,
                "last-run": cmd_last_run}[args.cmd](args)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
