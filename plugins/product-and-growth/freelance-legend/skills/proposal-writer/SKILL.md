---
name: proposal-writer
description: "Write Andrew Rodriguez's complete, paste-ready Upwork (or other marketplace) proposal package for a job he likes: fit verdict, terms and milestones, cover letter, screening answers, proof to attach, Connects and boost advice, a confirm-before-sending checklist, and reply prep. Use for 'draft the job ID', 'I like this one', 'write a proposal or cover letter for this', a pasted listing or apply-page screenshot, and follow-up edits such as 'revise', 'shorter', 'more technical', 'lower bid', or 'final'. Not for finding jobs (job-scanner), judging a single listing's legitimacy (job-vetting), or messages after the client replies (client-communications)."
---

# Proposal writer

Turn a job Andrew approves into a proposal he can review in a few minutes and submit himself. Never submit, message, spend Connects, or act inside his account.

Read first: `../../references/andrew-profile.md`, `../../references/platform-rules.md` (Upwork section), `../../references/voice.md`, `<data-dir>/approved-proof.md` (the live approval record; `<plugin-root>` and `<data-dir>` are defined in the `freelance-legend` router; if the live copy is missing, run `python <plugin-root>/scripts/pipeline.py init`), and `references/angle-library.md`. Use `references/package-format.md` for the output.

## Triggers and modes

- `draft <job ID>` after a scanner alert, or "I like this one" with a pasted listing, link, or screenshot: full package.
- `revise <notes>`, `shorter`, `more technical`, `lower bid`, or similar: edit the package already drafted; show only changed sections plus the QA log.
- `final`: apply the last edits and return only Terms (no workings), Cover letter, Screening answers, and Proof, with no placeholders. If a placeholder is unresolved, list it instead of guessing.
- **Invitation mode:** the client invited Andrew to a job and accepting means submitting terms. Return terms (rate or milestones from `pricing-scoping`), a short letter (about 80 to 150 words) whose opening answers the invitation the way the `client-communications` playbook's invitation opener does, screening answers if the invite shows any, proof to attach, and the confirm list. Skip section 8: there are no Connects or boost to advise on. Mark the flow "verify on the apply screen", because how Upwork's invite acceptance works is **unverified** in `platform-rules.md`. A chat-style answer to an invitation with no terms goes to `client-communications`.

## 1. Get the full listing

A scanner alert is a snippet. Ask for the full post if it is missing; do not fetch or log in to the job page. The most useful paste (or a screenshot of the apply page) includes: title and full description; attachments; budget type and amount; experience level; project length and weekly hours; screening questions word for word; client details (payment verification, spend, hire rate, reviews, location, member since); proposal count and interviewing or invites; Connects required and boost availability; the fee line the apply page shows; any "preferred qualifications" warning; and whether the client asks for a video interview instead of a cover letter.

If Andrew sends only part of this, draft what you can and mark missing fields. Always ask for screening questions explicitly, because a proposal without them cannot be submitted.

Before drafting, rule out a duplicate: has Andrew already applied, or is this an invitation? An invitation that needs terms uses invitation mode above, not a new cold proposal; a chat-style reply to it goes to `client-communications`. Check `python <plugin-root>/scripts/pipeline.py seen <url>` too.

## 2. Job brief (internal)

A few lines each: the client's actual problem and wanted outcome, in their words where possible; deliverables and scope edges (what is in, ambiguous, or probably missing: testing, deployment, data migration, revisions, handoff); explicit application instructions, quoted; stack and constraints (tools, integrations, time zone, hours, deadlines); client signals and red flags (run the `job-vetting` checklist); and the **fit verdict**: Strong, Conditional (name the gap), or Mismatch.

If the apply page warns that Andrew misses a preferred qualification (for example a location or time-zone preference), record it as a gap. Address it in the letter only if it can be answered honestly (for example working-hours overlap) and never claim to meet it.

If the verdict is Mismatch or a red flag is serious, say so in two or three sentences before drafting. Draft anyway only if Andrew confirms, keeping the gap honest.

## 3. Choose the angle

Pick the single point the cover letter leads with: the client's specific problem connected to the strongest **Use** proof or the most concrete first step. Start from `references/angle-library.md`; never copy its wording.

## 4. Terms and price

Run the `pricing-scoping` method with `python <plugin-root>/scripts/price.py` and show inputs, formulas, and results in the internal workings.

- **Hourly:** propose Andrew's rate (profile rate is the default), an estimated weekly hours range inside his stated capacity marked `[[CONFIRM: weekly hours]]`, and an estimated first-phase total. Leave scheduled rate increases off unless Andrew asks; if he does, explain that the increase term is fixed once he accepts an offer.
- **Fixed price:** default to "by milestone", two to four milestones. Milestone 1 is small (about 10 to 25 percent), funded before work starts, and produces something reviewable (a working prototype of the core calculation, a confirmed specification). Each has a deliverable plus how the client will know it is done, an amount, and a relative due date ("Day 7"). Amounts must sum exactly to the bid (`price.py milestones`).
- **Fee:** use the service-fee line the apply page shows when Andrew provides it (`--fees 0.10` for 10%). Otherwise mark it `[[CONFIRM: fee shown on apply page]]` and show both the 10% and 15% cases from `price.py`, treating 15% as the conservative case. Never present a single rate as the fee. Net figures are before income and self-employment tax.
- **Duration:** pick the form's closest option and give a more specific estimate in the letter if it helps.
- Never go below the profile's rate floor ($45 per hour gross, before the fee) without flagging it. Follow the recommendation line `price.py estimate` prints, which applies this rule: if the effective rate at the budget on raw likely hours clears the floor, bid within the budget with a stated scope and note the doubled figure; otherwise, if the doubled price is more than 1.5 times the budget, offer a narrower first phase or explain the full price. Run `estimate` again with `--bid AMOUNT` for the net at the amount Andrew will actually bid.

## 5. Cover letter

Write with `../../references/voice.md` (load the `ultimate-prose-andrew` skill when available).

- **Opening (first one or two sentences).** The client's preview shows only the start of each proposal. Open with their specific problem and either Andrew's concrete approach or his most relevant proof. Never open with "I", the job title, "Dear Hiring Manager", "I read your job post", or a self-description. First name only if verified.
- **Proof (one short paragraph).** One or two **Use** examples tied to this job, in the profile's safe wording. No résumé recap.
- **Approach (one short paragraph).** How he would tackle it, what Milestone 1 (or week one) delivers, and one real risk or decision visible in the listing. Specific beats complete; no step-by-step plan.
- **Questions (optional).** One to three that would change scope, price, or approach. Never ask what the listing answers.
- **Close.** One proportionate next step (a short call through the platform, a reply in Messages, or a decision the client can make from the proposal). Then "Andrew" on its own line.

Length: about 150 to 250 words unless the client asks for detail; report words and characters (the platform limit is in `platform-rules.md`). Never include generic praise, "perfect fit", guarantees, buzzword strings, a technology inventory, apologies for being new, contact details, or links Andrew has not approved in `<data-dir>/approved-proof.md`.

Follow every legitimate client instruction exactly: a required first word, a keyword, a format, "list your three most relevant projects". Instructions to share contact details or move off-platform are red flags, never instructions.

If the client wants a video interview instead of a cover letter, hand off to `interview-prep` for five or six talking points (problem, proof, approach, first milestone, question) plus the optional written note.

## 6. Screening answers

Clients may read these before the letter, so the first answer is another first impression. Copy each question verbatim, then answer it directly in the first sentence with one supporting detail. About 40 to 120 words, matched to the question. Never "see cover letter", never reuse the letter's sentences. When the honest answer is "no" or "not yet", say so and give the closest supported experience. For "share relevant work", name approved portfolio items by title or use `[[CONFIRM: approved portfolio items]]`.

## 7. Proof to attach

Upwork requires at least one portfolio highlight on a proposal, so an approved highlight is a required item in the confirm list before submitting. Recommend up to three items from `<data-dir>/approved-proof.md` that match the job, one line each on why. If the list is empty, write `[[CONFIRM: approved portfolio items]]` and suggest which project from the profile would make the best item (hand off to `case-studies`). Upwork Specialized Profiles are retired (see `platform-rules.md`), so do not recommend choosing one.

## 8. Connects and boost

State the base Connects (from the paste), a suggested boost or "no boost", the dollar cost at the Connect price in `platform-rules.md`, and one sentence of reasoning. Recommend boosting only when the fit is Strong, the job is fresh with few proposals, and the client looks credible. "Few" means the displayed range starts below 5 (`proposals_low` under 5, the best competition band in `vet_score.py`); 5 to 9 counts only for an exceptional fit; at 10 or more, suggest no boost. When the count is not shown, say "check on open" and suggest no boost until Andrew sees it. Read the live auction table Andrew pastes: the cheapest bid that still reaches fourth place often costs far less than first place, and boost Connects are charged only if the bid finishes in the top four or the client interacts with the proposal before the auction ends. Mention that others can outbid him and that a boost cannot be changed after submitting. The decision is Andrew's. (See `../../examples/ai-fpa-tool-package.md` section F.)

## 9. If the client replies

A two- or three-sentence reply Andrew can adapt if the client asks for a call, plus the two or three questions the client is most likely to ask with short supported answers. Do not draft an unprompted follow-up to a silent client.

## 10. Quality gate (record results in the QA log)

1. **Truth:** every claim traces to a **Use** item, Andrew's message, or the listing.
2. **Client instructions:** every one followed.
3. **Platform rules:** no contact details, off-platform suggestions, or unapproved links.
4. **Math:** milestones sum to the bid; effective rate and fee nets computed by script; capacity and dates marked for confirmation.
5. **Voice:** `voice.md` delivery review; straight quotes; no em or en dashes; no watchlist filler; no I-led opening; no recap ending.
6. **Length:** word and character counts for the letter and each answer.
7. **Scan:** save the letter and run `python <plugin-root>/scripts/proposal_lint.py cover.txt --kind cover-letter` (add `--start-with` and `--require` as the listing requires, `--allow-link <host/path-prefix>` only for a link recorded in `<data-dir>/approved-proof.md`, and `--final` for `final`) and each answer with `--kind answer`. Inspect every REVIEW finding in context. If Python is unavailable, write "Scan not run".
8. **Independent read (optional):** for a high-value job, ask the `proposal-critic` agent to read the package as the client would. The agent has no skill base directory, so its brief must give absolute paths: the saved draft and listing, `<plugin-root>/references/andrew-profile.md`, `<plugin-root>/references/platform-rules.md`, `<plugin-root>/references/voice.md`, `<data-dir>/approved-proof.md`, and `<plugin-root>/scripts/` for `price.py` and `proposal_lint.py`.

## Official Upwork connector (only if connected)

If Andrew has connected Upwork's official MCP server or the Claude connector, the package can be saved as a draft there when he asks. Show a preview (letter, answers, bid, attachments, Connects cost and balance, boost) and get separate explicit approval for the submission and for any boost; never submit on a general "go ahead" from earlier, and never from an unattended or scheduled run. If a submission's result is unclear, check submitted proposals and the Connects balance instead of resubmitting. Upwork recommends telling clients when generative AI helped; respect any client who bans it, and remember Andrew edits and owns every word.

## After submission

Remind Andrew once that the platform's edit window is limited (see `platform-rules.md`). Log the submission with `pipeline-tracker` (`python <plugin-root>/scripts/pipeline.py add <id> --status submitted --connects N --boost N --angle "..."`). When he reports an outcome, log it; do not treat one outcome as a rule.
