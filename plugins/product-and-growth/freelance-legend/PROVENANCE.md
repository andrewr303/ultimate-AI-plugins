# Provenance

Freelance Legend is an original instruction package and standard-library tool set. No third-party prompt text, skill text, or code is included. Research informed design decisions only.

## Andrew's own materials (the foundation)

| Material | What it became |
| --- | --- |
| `01-grok-upwork-scanner-prompt.md` v2.0 (2026-11-02) | `job-scanner`: compliance model, fit rules, notification format, quiet mode, ledger rules, seed IDs (`references/scanner-seed-ids.txt`). Rewritten for Claude Code and extended to other platforms. Original kept in `research/2026-11-04/source-material/`. |
| `03-upwork-proposal-writer.md` v1.0 (2026-11-02) | `proposal-writer`, `pricing-scoping`, the package format and angle library, quality gate. Specialized Profile advice removed (retired 2026-05-28). Original kept in `research/2026-11-04/source-material/`. |
| `02-andrew-rodriguez-profile.md` v2.0 | `references/andrew-profile.md` v2.1 with the proof library. |
| Résumé (PDF) | New proof-library rows, each marked Use, Confirm, or Internal. Phone number and email address deliberately excluded from the package. The PDF itself is not committed. |
| Upwork apply-page screenshot (2026-11-04) | Dated observations in `platform-rules.md` and the worked example in `examples/`. |
| Ultimate Prose Andrew plugin (this repository) | `references/voice.md` defers to it and condenses its rules as a fallback; the lint watchlist mirrors its editing watchlist. |

## What the research changed

Research ran on 2026-11-04 in the research-first-creator plugin's manual review mode (its automated gates were not configured; no automated PASS is claimed). Evidence is in `research/2026-11-04/`: `sources/sources.jsonl`, `artifacts/claim_ledger.jsonl`, and `outputs/freelance-legend-research.md`.

| Decision | Evidence |
| --- | --- |
| Upwork's official MCP server and Claude connector are the only live Upwork connection; on-demand use only, within published rate limits, with explicit per-submission confirmation | clm_up_005, clm_up_006, clm_up_007, clm_gh_001, clm_gh_008; `upwork/upwork-agent-plugin` (Apache-2.0) read for workflow ideas only |
| Forbid scrapers, page monitors, extensions, cookie reuse, RSS replacements | clm_up_001 to clm_up_003, clm_up_031; community scrapers `roperi/UpworkScraper` and `richardadonnell/Upwork-Job-Scraper` cited as approaches to avoid |
| Per-platform intake and fee matrix | clm_pl_001 to clm_pl_033 |
| Remove Specialized Profile advice; one broad main profile | clm_up_020 |
| Read the fee from the apply screen; gross-up helper | clm_up_013 |
| Boost guidance: cheapest top-four slot, charged only on top-four finish or interaction | clm_up_017, observed auction on the apply page |
| Edit-window reminder after submitting | clm_up_019 |
| Scam checklist including developer malware lures, task scams, account rental, paid-test rule | clm_cr_007 to clm_cr_016, clm_cr_029 |
| CAN-SPAM and LinkedIn outreach rules | clm_cr_001 to clm_cr_006 |
| Kill gates before scoring, Hold without the client panel, unknowns at partial credit, calibration anchors | Our own design choices, informed by ideas from `abullaisi/upwork-skills`, `waseemnasir2k26/upwork-mcp-toolkit`, `career-ops-hq/career-ops`, `Nadarisgetae/Upwork-Asisstance-Plugin` (clm_gh_016 to clm_gh_020; most are unresolved because each describes a community repo backed only by that repo); weights and code are original |
| Duplicate-application check; "Accepted" means submitted | clm_gh_013, clm_gh_014 (unverified beyond Upwork's skill) |
| Proposal-safe website build as a separate deployment, plus a contact scan | clm_pf_011, clm_pf_012, clm_pf_019, clm_pf_020; Next.js and schema.org docs (clm_pf_001 to clm_pf_010) |
| No template code vendored (CC BY-NC and unlicensed repositories are idea-only) | clm_pf_016, clm_pf_021, clm_gh_024 |

## Research method notes

- Several Upwork legal and help pages returned HTTP 403 to automated fetches; help-center articles were read through Upwork's public help-center JSON API instead. The User Agreement and the API and MCP Terms of Use were not read directly, so rules that depend on them are marked unverified.
- GitHub per-repository API calls were refused in this session, so two research agents took commit SHAs and dates from shallow, blob-less clones into the session scratchpad. No candidate code was installed or executed. The research-first method prefers not to clone; this is disclosed rather than hidden.
- The awesome-repositories directory held no freelance or Upwork tooling; it contributed portfolio-template taxonomy only.
