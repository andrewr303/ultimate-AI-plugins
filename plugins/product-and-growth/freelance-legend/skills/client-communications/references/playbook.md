# Client message playbook

Templates show structure and the moves that work; write each reply fresh from the actual thread, in the freelancer's voice. Bracketed items are placeholders.

## Contents

- Invitation or interview request (pre-contract)
- Clarifying questions before quoting
- Kickoff
- Status update
- Deliverable handoff
- Scope creep or change request
- Delay, blocker, or the freelancer's mistake
- Declining
- Off-platform or contact-detail request (pre-contract, Upwork)
- Unpaid test or free sample request
- Late payment, unfunded milestone, unapproved submission
- Price pushback or discount request
- Difficult feedback or an unhappy client
- Rate increase (ongoing client)
- Asking for feedback at the end
- Asking for a testimonial
- Closing a contract
- Re-engaging a past client

## Invitation or interview request (pre-contract)

Answer the invitation directly, show one sign he read their need, and propose the next step on the platform.

> Thanks for the invite. The part I'd want to understand first is [specific risk or unknown from their post], since it decides [what it decides]. I can do a short video call here on Upwork [[CONFIRM: times that work]], or if it's easier, send me [the file, the current spreadsheet, a sample of the data] and I'll come back with how I'd approach it.

On a submitted Upwork proposal the client messages first; the freelancer replies in the room the client opens (from Upwork's official skill, unverified elsewhere). Never try a cold first message on Upwork. (clm_gh_014)

## Clarifying questions before quoting

At most three questions that change scope or price, each answerable in a line. Say why the answer matters.

## Kickoff

Confirm the first milestone's deliverable and done signal, list the access or files needed and by when, the update cadence, and the first check-in date.

## Status update

Lead with what changed and the reviewable artifact; then what is next and any decision or blocker with an owner. Distinguish "built", "tested", and "approved".

> The calculation layer is done and reconciles with your workbook on all [n] test scenarios. Next is the input screens, which I expect to have ready for review by [[CONFIRM: date]]. One decision for you: [decision], because [consequence].

## Deliverable handoff

What is delivered, where it is, how to check it against the acceptance criteria, known limits, and the requested action ("If it matches, please approve the milestone; if anything is off, tell me which scenario and I'll fix it").

## Scope creep or change request

Acknowledge, name it as new scope without refusing, give the options from `contracts-scope` (new funded milestone, swap, defer), and ask which they prefer. Do not start until it is agreed and funded.

> That's a useful addition. It isn't in the current milestone, so here are the options: add it as a new milestone ([[CONFIRM: price]], about [days] days), swap it for [in-scope item of similar size], or keep it for phase two. Which works best for you?

## Delay, blocker, or the freelancer's mistake

Say it early and plainly: what happened, the impact, what he is doing, the new date. Own a mistake in one sentence without over-apologizing. Never blame the client in writing.

## Declining

Thank them briefly, give a short honest reason if useful (fit, capacity, budget), and, when true, point to what would make it a fit later. No lecture.

## Off-platform or contact-detail request (pre-contract, Upwork)

Use this only when the request has no hard-scam sign. Equipment purchases, pay-to-work fees, overpayment or checks, task scams, credential or account requests, and malware repositories get no reply at all: the freelancer reports them through the channel they arrived on (`job-vetting`, section 4).

Decline politely in Upwork's own terms and keep the conversation moving on the platform.

> I'm glad to talk this through. Upwork asks us to keep communication here until a contract starts, so let's use a call through Upwork Messages. I'll share my contact information once we have a contract in place.

If they push to pay or be paid outside Upwork: decline, mention that Upwork's only route for moving a relationship off-platform within two years is the Conversion Fee, and flag the request to the freelancer as a scam and account risk. Do not argue repeatedly; suggest reporting if it continues.

## Unpaid test or free sample request

> I'm happy to show how I'd approach it. Upwork asks that test projects be paid, so I'd suggest a small fixed-price test: [scoped piece] for [[CONFIRM: price]], which gives you [what it proves]. If it works for you, the rest builds directly on it.

If they insist on free work, flag it to the freelancer as a policy problem and suggest reporting. (clm_cr_014)

## Late payment, unfunded milestone, unapproved submission

- **Unfunded milestone:** do not start; ask the client to fund it so work can begin, with the start date that follows.
- **Submitted but not approved:** a short reminder of what was delivered and the acceptance criteria. Upwork's fixed-price countdown releases payment automatically after 14 days unless the client acts; mention it neutrally only if useful.
- **Hourly dispute:** respond within the platform's 3-day window with the work diary facts. Hour disputes are about billed time against Hourly Protection criteria (tracked segments, memos), not quality; handle quality complaints by conversation. (clm_up_022, clm_cr_020)
- **Fixed-price dispute path:** resolve in writing in the workroom with dated evidence; then Upwork's free mediation; after non-resolution, arbitration is optional, has fees, and a short deadline. Confirm the current steps, deadlines, and fees on Upwork's help center before acting, because the figures in research were unverified. (clm_cr_018, clm_cr_019)
- **Direct client late payment:** polite reminder with the invoice number and due date taken from the ledger (`python <plugin-root>/scripts/pipeline.py list --status invoiced --json` or the overdue list in `stats`), then a firmer second notice; pause new work after the date the SOW allows. Once paid, log it (`python <plugin-root>/scripts/pipeline.py add <id> --status paid`).

## Price pushback or discount request

Hold the rate; trade scope, phasing, or milestone order instead.

> I'd rather keep the rate and fit the scope to your budget. If we start with [smaller phase], that comes to [amount] and gives you [what it proves]; the rest can follow once you've seen it work.

## Difficult feedback or an unhappy client

Thank them for the specifics, restate the concrete problem, say what he will do and by when, and ask one question if something is unclear. No defensiveness, no staged empathy.

## Rate increase (ongoing client)

Give notice ahead of the change, the new rate and effective date, a short reason tied to the work, and what stays the same. On Upwork hourly contracts, scheduled increases can only be set in the original proposal; otherwise the client must accept a rate change.

## Asking for feedback at the end

After the client confirms the work is complete:

> Thanks for the project. If you have a minute when you close the contract, honest feedback helps other clients understand how I work. And if [specific follow-on] becomes a priority, I'd be glad to help.

Never offer refunds, discounts, bonuses, or extra work for a review, never ask for a specific rating, and never withhold deliverables pending feedback. Upwork's end-of-contract feedback window and double-blind rules are in its help center (unverified in research; check before quoting). (clm_cr_021, clm_cr_022)

## Asking for a testimonial

For a direct client, or a marketplace client who wants to give a quote the freelancer can reuse. Ask only after the client confirms the work is complete, and ask on the channel the relationship lives on (a client met on Upwork within two years is asked in Upwork Messages).

> Thanks again for the project. Would you be willing to share a sentence or two about working together that I could show on my portfolio and profiles? Use whatever wording feels right, and tell me how you'd like it attributed (your name and title, or something like "Founder, B2B SaaS company"). Nothing goes up without your OK on the exact text.

Never offer anything in exchange, never draft the quote for the client, and never edit it beyond a typo fix the client approves. Record the approved quote through `case-studies`.

## Closing a contract

Summarize what was delivered, where everything lives, any handoff notes, and the open items with owners. Ask the client to close the contract on the platform.

## Re-engaging a past client

Only with a specific, useful reason (a fix for something they mentioned, a feature that now makes sense, a seasonal need). One message; no generic check-ins.
