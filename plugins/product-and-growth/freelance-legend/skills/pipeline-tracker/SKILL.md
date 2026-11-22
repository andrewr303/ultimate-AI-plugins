---
name: pipeline-tracker
description: "Track the freelancer's freelance pipeline in a local JSONL ledger: dedupe jobs across alerts and URL variants, record verdicts, proposals, Connects spent, angles used, outcomes (viewed, interviewing, hired, declined), and direct-client invoices and payments, and report funnel conversion, Connects spend, and overdue invoices in a weekly review. Use for 'log that I submitted', 'they hired me', 'log this invoice', 'they paid', 'have I seen this job before?', 'how are my proposals doing?', 'weekly review', or seeding the scanner's already-notified IDs. Not for drafting proposals (proposal-writer) or scanning new alerts (job-scanner)."
---

# Pipeline tracker

The ledger is kept by `<plugin-root>/scripts/pipeline.py` (`<plugin-root>` and `<data-dir>` are defined in the `freelance-legend` router) in an append-only JSONL file: `<data-dir>/pipeline.jsonl` by default, that is `$FREELANCE_LEGEND_HOME`, else `$CLAUDE_PLUGIN_DATA`, else `~/.freelance-legend`. `$FREELANCE_LEGEND_LEDGER` or `--ledger PATH` override it. The data directory survives plugin updates; never keep the ledger inside the plugin folder. `seed` and `stats` print the absolute ledger path they used; tell the freelancer where it lives, and if it sits inside a repository, keep it out of version control.

The latest event per job wins for status and details. It stores short records only: no full listing text, no client contact details, no credentials. The script refuses (exit 2) a title, reason, angle, URL, or invoice value that contains an email address or phone number.

## Commands

```bash
python <plugin-root>/scripts/pipeline.py init
python <plugin-root>/scripts/pipeline.py normalize "https://www.upwork.com/jobs/fixture-dashboard-001"
python <plugin-root>/scripts/pipeline.py seed <path-to-your-own-seed-file> --platform upwork
python <plugin-root>/scripts/pipeline.py seen "fixture-dashboard-001"
python <plugin-root>/scripts/pipeline.py add "fixture-dashboard-001" --status submitted --title "AI FP&A Tool Development" \
  --connects 10 --boost 4 --bid "50/hr" --angle "deterministic math under the AI layer"
python <plugin-root>/scripts/pipeline.py add "fixture-dashboard-001" --status viewed
python <plugin-root>/scripts/pipeline.py add "fixture-dashboard-001" --status hired --met-on 2026-11-10 --fee 0.10
python <plugin-root>/scripts/pipeline.py add "<id>" --status invoiced --invoice "INV-001" --amount 1200 --due 2026-11-20
python <plugin-root>/scripts/pipeline.py add "<id>" --status paid --amount 1200
python <plugin-root>/scripts/pipeline.py list --status submitted
python <plugin-root>/scripts/pipeline.py stats
```

`init` creates the data directory, copies the approved-proof template there if it is absent, and prints both absolute paths. `seen` exits 0 when a key exists and 1 when it is new, so the scanner can branch on it. Upwork `~01`/`~02` tokens, apply-page URLs, and bare 19-digit IDs collapse to one key (`upwork:<id>`). For other platforms the key is the URL without query string, and the platform is inferred from the URL host (freelancer.com, contra.com, fiverr.com, linkedin.com, peopleperhour.com, toptal.com, arc.dev, wellfound.com, Braintrust, gun.io, Hacker News as `hn`, We Work Remotely as `wwr`). `--platform` overrides the inferred value; bare IDs and `~0` tokens default to `upwork`. `--json` and `--ledger` work before or after the subcommand.

`add` options: `--title`, `--url`, `--reason`, `--angle`, `--bid`, `--budget`, `--at`, `--connects N` and `--boost N` (whole numbers; pass them only on the event where the Connects were spent, usually `submitted`, because every event is added up), `--amount` (USD), `--due YYYY-MM-DD`, `--invoice` (number only), `--fee` (fraction, for example 0.10), and `--met-on YYYY-MM-DD` (the date the client first met the freelancer on a marketplace, which `cold-outreach` checks before any off-platform message).

Statuses: `seen, invited, needs-listing, held, rejected, notified, drafting, submitted, viewed, interviewing, offer, hired, declined, no-response, withdrawn, archived, invoiced, paid`.

On Upwork, a proposal shown as "Accepted" means submitted and validated, not hired: log it as `submitted`. Log `hired` only when a contract starts. Log `invoiced` when the freelancer sends a direct-client invoice and `paid` when the money arrives.

`stats` sums `--connects` and `--boost` across every `add` event (each event counted once, so a later status update does not erase earlier spend), reports boost separately, and lists overdue invoices: status `invoiced`, due date before today, and no later `paid` event. `run-start`, `run-done [--note]`, and `last-run` keep the scanner's run markers in `<data-dir>/runs.jsonl` (next to the ledger when the ledger path is overridden).

## First run

If the user has a prior scanner history, import their own list with `seed`.

## Weekly review

Run `stats`, then write a short review:

1. Funnel counts (submitted, viewed, interviewing, offer, hired), Connects and boost Connects recorded, and any overdue invoices from `stats` with their invoice numbers and due dates.
2. Which angles and job types reached "viewed" or "interviewing" (from `list --json` angles), and which did not. Below 20 proposals, call these anecdotes, not a trend, and never turn one outcome into a rule.
3. Connects spent versus remaining (ask the freelancer for the current balance; balances in the profile are snapshots).
4. Money in: amounts invoiced and paid this week from the ledger. These are gross receipts before income and self-employment tax; set-asides are a question for his accountant.
5. One or two concrete adjustments for next week (for example, stop bidding on a job type that never gets views, or tighten openings for one category).

## Logging rules

- Log when the freelancer reports it, with the date he gives; do not infer outcomes.
- After a submission, remind him once about the platform's edit window (see `../../references/platform-rules.md`).
- Do not draft follow-ups to silent clients just because the ledger shows `no-response`.
