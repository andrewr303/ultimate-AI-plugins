# Changelog

## 1.0.1 (2026-11-10)

- `proposal-writer` description no longer contains angle brackets (rejected by the shared lint); trigger phrases unchanged.
- `client-communications` playbook opens with a contents list.

## Unreleased

- User data directory (`$FREELANCE_LEGEND_HOME`, else `$CLAUDE_PLUGIN_DATA`, else `~/.freelance-legend`) for the ledger, the live `approved-proof.md`, and scanner run markers; `pipeline.py init`. `references/approved-proof.md` is now a template and gains a Testimonials table.
- Skills and the `proposal-critic` agent use `python <plugin-root>/scripts/<name>.py`; the router defines `<plugin-root>` and `<data-dir>`.
- Compliance: `cold-outreach` checks whether a recipient met Andrew on a marketplace within two years before drafting; one scam-reply rule (hard scams get no reply and a report through the arriving channel, an off-platform ask alone gets the compliant decline); the clm_up_009 exceptions in `job-vetting`; unsourced fee, refund, saved-search, and field-limit statements removed or sourced.
- Proof library: degree wording, ROI calculator tense, and rate floor (gross or net) are Confirm items; angle library maps every proof cell to a Use row and uses a calibration job outside Andrew's core work.
- Pricing: bid rule (within budget when the raw-hours rate clears the floor, otherwise a narrower first phase when the doubled price is over 1.5 times the budget), `--bid`, nets labelled by amount, net figures noted as before income and self-employment tax, Fiverr fee marked unverified.
- `proposal-writer` invitation mode; "few proposals" defined for boost advice; router splits scheduled rate increases (pricing) from raises for existing clients (communications) and routes invoices, testimonials, and Fiverr gigs.
- Pipeline docs: `invoiced` and `paid` statuses, `--amount`, `--due`, `--invoice`, `--fee`, `--met-on`, integer `--boost`, platform inferred from the URL host, per-event Connects totals, overdue invoices, `run-start`/`run-done`/`last-run`; `vet_score.py --list-flags` and flag normalization.
- Worked example: floor wording corrected, working-hours claim removed from the letter, location traced to the profile, portfolio highlight required before submitting.

## 1.0.0 (2026-11-04)

- First release: 13 skills (router, job scanner, job vetting, proposal writer, pricing and scoping, client communications, interview prep, contracts and scope, profile optimizer, case studies, portfolio website, cold outreach, pipeline tracker) and the `proposal-critic` agent.
- Shared references: candidate profile and proof library (v2.1, adds résumé-derived claims as Confirm or Internal), dated platform rules for Upwork and 15 other platforms, voice rules, approved-proof template, scanner seed IDs.
- Standard-library scripts with tests: `price.py` (estimates, milestones, hourly, gross-up, Connects expected value), `proposal_lint.py`, `pipeline.py`, `vet_score.py` (with calibration anchors), `contact_scan.py`.
- Worked example package for an AI FP&A job from a 2026-11-04 apply page.
- Research-first evidence in `research/2026-11-04/` (manual review mode).
