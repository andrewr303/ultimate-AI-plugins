# Freelance Legend

A Claude Code plugin for running Andrew Rodriguez's freelance business on Upwork and beyond: find the right jobs without breaking platform rules, vet clients, price with checked math, write proposals from claims he can prove, handle every client message, keep profiles and case studies sharp, ship a proposal-safe portfolio website, and track what wins.

It drafts; Andrew decides and sends. It never logs in to a marketplace, scrapes or polls job pages, submits proposals, sends messages, spends Connects, or moves money.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`freelance-legend`](skills/freelance-legend/SKILL.md). Try this prompt.

> Review this pasted job listing and my work samples. Draft milestones and a fee estimate, and flag any proposal claims I still need to substantiate.

## Skills

| Skill | Use it for |
| --- | --- |
| `freelance-legend` | Entry point. Routes a request and enforces the shared rules. |
| `job-scanner` | Processing alert emails, pasted listings, and allowed feeds into at most three ranked alerts per run. |
| `job-vetting` | One listing or client: fit, economics, credibility, scams and red flags. |
| `proposal-writer` | The full paste-ready package: terms, milestones, cover letter, screening answers, proof, boost advice, confirm list, reply prep, QA log. |
| `pricing-scoping` | Bottom-up estimates with Andrew's doubled-hours method, budget comparison, fee nets, gross-up, milestones that sum exactly. |
| `client-communications` | Every client message from first reply to closing, with a situation playbook. |
| `interview-prep` | Discovery calls, likely questions, video-interview talking points, post-call recap. |
| `contracts-scope` | SOWs, change orders, Upwork payment-protection hygiene, disputes, direct-client invoices, clauses to flag. |
| `profile-optimizer` | Upwork title, overview, skills, Project Catalog, reputation plan; LinkedIn, Contra, and other profiles. |
| `case-studies` | Truthful, anonymized portfolio items and case studies with an approval record. |
| `portfolio-website` | Building and maintaining his personal portfolio site, including a page that is safe to link from proposals. |
| `cold-outreach` | One-to-one direct emails and LinkedIn messages with a CAN-SPAM checklist. |
| `pipeline-tracker` | The local ledger: dedupe, outcomes, funnel stats, weekly review. |

Agent: `proposal-critic` reads a draft the way a busy client would and returns blocking findings and improvements.

## Shared references

- `references/andrew-profile.md`: the proof library. Every claim is **Use**, **Confirm**, or **Internal**. Contains no phone number or email address. Never send it to a client.
- `references/platform-rules.md`: dated rules for Upwork and 15 other platforms (automation, contact details, fees, Connects, boosts, protection), each tied to claim IDs in the research ledger.
- `references/voice.md`: Andrew's voice rules for client-facing text. Uses the companion **Ultimate Prose Andrew** plugin (`.claude/plugins/ultimate-prose-andrew`) when installed.
- `references/approved-proof.md`: the **template** for the portfolio items, links, and testimonials Andrew approves. The live copy is `<data-dir>/approved-proof.md` (below), so plugin updates never overwrite his approvals.
- `references/scanner-seed-ids.txt`: 15 Upwork job IDs the previous scanner already notified.

## Your data directory

Andrew's own records live outside the plugin, so updates cannot wipe them: `$FREELANCE_LEGEND_HOME` if set, else `$CLAUDE_PLUGIN_DATA` if set, else `~/.freelance-legend`. It holds the pipeline ledger (`pipeline.jsonl`; `FREELANCE_LEGEND_LEDGER` or `--ledger` override it), the live `approved-proof.md`, and the scanner's run markers (`runs.jsonl`). Create it and see both paths with:

```bash
python <plugin-root>/scripts/pipeline.py init
```

## Scripts (Python 3.10+, standard library only)

Skills write commands as `python <plugin-root>/scripts/<name>.py`, where `<plugin-root>` is this plugin's install directory (two levels above any skill's folder, or `${CLAUDE_PLUGIN_ROOT}` when the host substitutes it). From a checkout, `<plugin-root>` is `plugins/freelance-legend`. Text output of `price.py` ends with "Net figures are before income and self-employment tax."

```bash
python <plugin-root>/scripts/price.py estimate --task "Calc engine:8:12" --task "UI:8:10" --rate 50 --budget-fixed 2000 --bid 2000
```

```bash
python <plugin-root>/scripts/price.py milestones --total 2400 --split 15,45,40 --days 7,21,35
```

```bash
python <plugin-root>/scripts/price.py gross --net 45 --fee 0.10
```

```bash
python <plugin-root>/scripts/proposal_lint.py cover.txt --kind cover-letter --start-with spreadsheet
```

```bash
python <plugin-root>/scripts/pipeline.py seed <plugin-root>/references/scanner-seed-ids.txt --platform upwork
```

```bash
python <plugin-root>/scripts/pipeline.py add "~022118027855728317369" --status submitted --connects 10 --boost 4
```

```bash
python <plugin-root>/scripts/pipeline.py stats
```

```bash
python <plugin-root>/scripts/vet_score.py job.json
```

```bash
python <plugin-root>/scripts/vet_score.py --list-flags
```

```bash
python <plugin-root>/scripts/price.py connects-ev --connects 10 --boost 4 --project-gross 6000 --fee 0.10
```

```bash
python <plugin-root>/scripts/contact_scan.py out --allow "upwork.com/freelancers/"
```

`--json` (and `--ledger PATH` for `pipeline.py`) work before or after the subcommand.

Run the tests from the plugin root:

```bash
python -m unittest discover -s tests -v
```

## Install

From a Claude Code session in this repository, add the marketplace and install the plugin:

```text
/plugin marketplace add ./
/plugin install freelance-legend@ultimate-ai-plugins
```

Skills are then available as `/freelance-legend:<skill>` and also trigger from ordinary requests such as "I like this one, write the proposal".

## Optional connections

- **Email:** an email connector scoped to the label where Upwork and other alert emails land lets `job-scanner` read them; otherwise forward or paste alerts.
- **Upwork's official MCP server or Claude connector:** Upwork's own plugin installs with `/plugin marketplace add upwork/upwork-agent-plugin` and signs in through Upwork's browser OAuth page. If Andrew connects it, the scanner can run searches he asks for in the moment (within Upwork's published rate limits) and the proposal writer can save drafts he then confirms. Never scheduled, never continuous monitoring.
- **awesome-repositories MCP:** used by `portfolio-website` research when available.

## Research and provenance

Built research-first on 2026-11-04 in manual review mode (the automated verification gates were not configured, so no automated PASS is claimed). Sources, the claim ledger, and the decision report are in `research/2026-11-04/`. See `PROVENANCE.md` for what came from Andrew's own materials and what the research changed. Platform rules move quickly: `platform-rules.md` tells each skill to re-verify any rule older than 60 days before relying on it.

## Limits

- Rules marked **unverified** in `platform-rules.md` could not be read from an official page (several Upwork legal and help pages returned HTTP 403 to automated fetches); skills present them as guidance, not fact.
- Not legal, tax, or financial advice. `contracts-scope` flags clauses for a lawyer or accountant.
- The plugin cannot see Andrew's live Upwork account; Connects balances, fees, and proposal counts come from what he pastes.
