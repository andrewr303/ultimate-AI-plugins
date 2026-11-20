---
name: contracts-scope
description: "Protect Andrew Rodriguez's freelance contracts and scope: statements of work, acceptance criteria, assumptions and exclusions, milestone design that keeps Upwork payment protection, change orders when scope grows, hourly vs fixed contract hygiene, disputes and refunds, contract-to-hire and off-platform conversion questions, NDAs and IP clauses to flag, and SOW plus invoice templates for direct clients from LinkedIn or outreach. Use for 'write the SOW', 'the client keeps adding features', 'change order', 'client won't approve the milestone', 'they want to hire me off Upwork', or 'review this contract'. Not legal advice; flags clauses for a lawyer. Not for routine messages (client-communications)."
---

# Contracts and scope

This skill writes and checks the business side of a contract. It is not legal advice: anything about liability, IP assignment, non-competes, indemnity, taxes, or employment status gets flagged for Andrew to review with a lawyer or accountant, not decided here.

Read `../../references/platform-rules.md` (contract protection rules) and `../../references/andrew-profile.md` (payment preferences).

## Statement of work (any platform)

Draft from the accepted proposal and call notes:

1. **Objective:** one sentence in the client's terms.
2. **Deliverables:** numbered, each with acceptance criteria the client can check ("calculator outputs match the workbook to the cent on the five agreed test scenarios").
3. **Assumptions:** inputs and access the client provides, and by when.
4. **Out of scope:** the likely asks that are not included (extra integrations, data cleanup, new reports, ongoing support).
5. **Milestones and payment:** from `pricing-scoping`; amounts sum exactly to the price.
6. **Revisions:** how many rounds per milestone and what counts as a revision versus a change.
7. **Change process:** any new scope becomes a written change order with price and timeline before work starts.
8. **Communication and handoff:** channel, cadence, what handoff includes (code, docs, a walkthrough).

## Upwork contract hygiene

- **Fixed price:** never start a milestone until Upwork shows it **funded**. Deliver through **Submit Work for Payment**, matching the milestone description; submitting starts a 14-day auto-payment countdown. Split large projects into smaller milestones. Unfunded work cannot be recovered. (`platform-rules.md`)
- **Hourly:** track time in the Upwork Desktop App with memos, keep screenshots relevant, and stay within the weekly limit to keep Hourly Payment Protection; manual, idle, or over-limit time is excluded. There are 3 days to respond to an hourly dispute.
- **Scope growth on fixed price:** ask the client to add or update a milestone first. Work outside a funded, matching milestone is unprotected.
- **Off-platform:** clients met on Upwork stay on Upwork for two years unless the Conversion Fee is paid (client-initiated; 13.5% x rate x 2,080 hours). Never agree to off-platform payment; flag the request (`client-communications` has the decline wording). Record the date the client first met Andrew on the marketplace when the contract starts: `python <plugin-root>/scripts/pipeline.py add <id> --status hired --met-on YYYY-MM-DD` (`<plugin-root>` is defined in the `freelance-legend` router). `cold-outreach` reads that date before any off-platform message.
- **Contract-to-hire:** route through Upwork's own options in the current help center; do not improvise an off-platform arrangement.

## Change orders

When the client asks for something outside the SOW or milestone description:

1. Acknowledge the request and name it as new scope, without refusing the client.
2. Estimate it with `pricing-scoping` (task hours, doubled, rate).
3. Offer the options: add it as a new funded milestone, swap it for an equal-sized item already in scope, or defer it to a later phase.
4. Confirm in writing on the platform before starting. Draft the message with `client-communications`.

```text
Change order <n> · <project>
Request: <client's words>
Impact: +<hours> h, +$<price>, timeline +<days> days
Options: A) new milestone "<name>" $<amount> due Day <n>; B) swap for <item>; C) defer to phase 2
Needs: client approval and funding before work starts
```

## Disputes and refunds

Lay out the facts (milestone description, what was submitted and when, messages), the platform's process from the current help center, and a calm message that proposes a concrete resolution. Never threaten or ask for reviews in exchange for refunds. On Upwork the Freelancer Service Fee is refunded on any amount refunded to the client (`platform-rules.md`, clm_up_013).

## Direct clients (LinkedIn, outreach, referrals)

No platform escrow, so require a signed SOW, a deposit (Andrew's preference is roughly 10 to 20 percent upfront or regular billing), milestone invoices, and payment terms (for example net 7 or net 15). Provide a plain invoice template: invoice number, date, client, SOW reference, line items per milestone, amount, due date, and payment instructions Andrew supplies. After Andrew sends an invoice, log it so reminders and the weekly review can find it:

```bash
python <plugin-root>/scripts/pipeline.py add <job-or-client-id> --status invoiced --invoice "INV-001" --amount 1200 --due 2026-11-20
python <plugin-root>/scripts/pipeline.py add <job-or-client-id> --status paid --amount 1200
```

Keep the invoice field to the number only; the script refuses free text that contains an email address or phone number. For hourly direct work, keep a simple time log (date, hours, task, milestone) that matches the invoice lines.

Flag tax questions (1099, sales tax, quarterly estimated payments) for his accountant. Marketplace income is self-employment income too, so every net figure is before income and self-employment tax.

## Clauses to flag in a client's contract

Unlimited revisions; IP assignment before payment; broad non-competes or non-solicits; indemnity or uncapped liability; payment on "client satisfaction" only; net 60 or longer; work-for-hire language for pre-existing code or tools; requests for personal accounts or credentials. Explain the practical risk in one line each and suggest a fairer alternative to discuss.
