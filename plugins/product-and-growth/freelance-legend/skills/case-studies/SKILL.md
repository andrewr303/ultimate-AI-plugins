---
name: case-studies
description: "Turn Andrew Rodriguez's finished or ongoing projects into truthful, confidentiality-safe portfolio items and case studies for his Upwork portfolio, Project Catalog, personal website, and proposals: problem, constraints, approach, what he built, verification, and result, with anonymization rules and an approval record. Use for 'make a portfolio item for the ROI calculator', 'write a case study', 'what should I put in my Upwork portfolio', or when proposal-writer finds no approved proof. Not for the website build itself (portfolio-website) or profile headlines (profile-optimizer)."
---

# Case studies and portfolio items

A case study is proof a client can check in under a minute. It must be true, anonymized where required, and approved by Andrew before any skill attaches it.

Read `../../references/andrew-profile.md` (proof library and confidentiality rules), `../../references/voice.md`, and `<data-dir>/approved-proof.md` (the live approval record; `<plugin-root>` and `<data-dir>` are defined in the `freelance-legend` router).

## Inputs to collect

Ask Andrew for what the profile does not already establish: the client type (anonymized), the problem in the client's terms, constraints (data, deadline, stack, budget shape), what he built, how correctness was verified, what changed for the client (only measured or client-stated outcomes), screenshots he is allowed to show, and the confidentiality terms. Never fill a gap with a plausible guess.

## Confidentiality and claim rules

- The ROI calculator engagement is under confidentiality: never name the agency, its client, the client's industry details, scenarios, pricing, or figures. Use the profile's safe wording ("a spreadsheet-to-web ROI calculator for an agency client...").
- HypeStake has no customers, revenue, or funding; describe what was built, never traction.
- **Confirm** items (Velotic, Meridian, Pixelpush, figures from the résumé) need Andrew's approval for each piece.
- Screenshots: masked or synthetic data only; no client logos, names, emails, or real figures unless Andrew confirms written permission.
- No outcome claims ("saved 40 hours a month") without a measured figure Andrew supplies.

## Structure (website or long form, 250 to 600 words)

1. **Title:** the outcome or artifact in plain words ("Spreadsheet ROI model rebuilt as a web calculator with PDF reports").
2. **The problem:** one paragraph in the client's terms.
3. **Constraints:** what made it hard (source of truth in Excel, multi-year scenarios, non-technical users).
4. **Approach and build:** the key decisions and stack, tied to the problem (for finance work, how the math was kept deterministic and reconciled with the source model).
5. **Verification:** how Andrew proved it was right (reconciliation against the workbook, test cases, review steps).
6. **Result:** delivered scope and any client-stated or measured outcome; otherwise state what shipped.
7. **Role:** "Solo engineer" or the actual role. No implied team.

## Upwork portfolio item (short form)

Upwork portfolio items take a title, a role, a description, skills, and media. Keep the description to a few short sentences: problem, what Andrew built, how it was verified. `platform-rules.md` records no portfolio field limits, so ask Andrew to check the limits shown on the live Upwork form and trim to them before finalizing. A Project Catalog listing is a priced offer, not a case study: hand off to `profile-optimizer` for that.

## Approval record

After Andrew approves an item, add a row to `<data-dir>/approved-proof.md` (title, where it lives, safe one-line description, allowed listings, date). If that file does not exist yet, run `python <plugin-root>/scripts/pipeline.py init` first, which copies the template there. Never write approvals into the plugin's own `../../references/approved-proof.md`: it is the shipped template and a plugin update replaces it. Only rows in the live copy can be attached by `proposal-writer`.

## Testimonials

Never invent or paraphrase a testimonial. To ask for one, draft the request with `client-communications` (playbook, "Asking for a testimonial"); a client met on a marketplace within two years is asked on that platform. When a client sends a quote and agrees to its use, add a row to the Testimonials table in `<data-dir>/approved-proof.md`: the exact quote, how the client gave permission and when, the attribution they agreed to (for example "Founder, B2B SaaS company"), allowed uses, and the date Andrew approved it. `portfolio-website` and `profile-optimizer` use only rows from that table.

## Output

Return the long-form case study, the Upwork short form, a one-line proposal mention, alt text for each image, and a "Confirm before publishing" checklist. Run `python <plugin-root>/scripts/proposal_lint.py <file> --kind profile-overview` on each text and fix any contact-detail or link finding before Andrew publishes on Upwork.
