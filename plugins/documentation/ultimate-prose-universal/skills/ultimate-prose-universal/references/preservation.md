# Keeping the meaning

Read this before an edit that could change what a piece says, and after any substantial rewrite. A piece can read better and say something different, and the writer is usually the last to see it. Polish is worth nothing if a number, a refusal, or a condition did not survive it.

## Candidate, finding, edit

These are three separate decisions.

1. A **candidate** is a passage worth a second look: a scanner match, a pattern from `patterns.md`, or a sentence that reads oddly.
2. A candidate becomes a **finding** only after the surrounding text and the pattern's own exceptions have been read. Most candidates in careful writing are not findings.
3. A finding becomes an **edit** only when the requested job allows one. A review reports it. A light polish fixes it only if the fix is small. A quotation, code, or attributed passage is reported and left exactly as written.

A scanner hit, an unusual rhythm, a suspicion about origin, or a personal preference does not justify a change on its own. Every changed span should trace to a finding or to a transformation the user asked for.

**When nothing needs fixing, return the text exactly as supplied** and say it already works. Do not merge two sentences, add a contraction, or swap a word to show that editing happened.

## What must survive

Identify these before changing anything, in your head for a short piece:

- Numbers with their units, denominators, time windows, and rounding. "42%" can become "about four in ten"; it cannot become "almost half".
- Names, dates, places, versions, identifiers, links, and exact error text.
- Quotations and attributed statements, word for word inside the marks. Do not tidy a quotation's grammar.
- Negation and limits: a refusal, an exception, "not yet", "only", "except", "unless".
- Conditions and dependencies: "if testing passes", "subject to review", "once the contract is signed".
- Strength: the difference between may and will, some and all, estimate and result, plan and done, association and cause, a local check and an approval.
- Order and ranking ("the second-largest"), and claims that two things happen at the same time.
- The words that carry a requirement in legal, medical, safety, and security text: shall, must, never, always, may cause, preliminary, observational. Treat each as a constraint, not a style choice.

Three edits lose these more often than any other: merging list items into a sentence, trimming qualifiers to sound decisive, and turning a labeled list into flowing prose. Reread the protected items after each of those.

## Remove or repair before adding

In a factual edit or a smoothing pass, cut what adds nothing and repair what is unclear. Adding is the risky direction.

- **A join** links two sentences with "and", "but", or a semicolon, or merges them into one. It never adds a clause, a detail, or a reason. "Because", "so", "which means", and "as a result" are claims about the world; use one only when the source states that relation.
- **A line that speaks for the user is a new fact.** Thanks, reassurance, enthusiasm, an apology, a promise, or a feeling that the brief does not supply should not appear, however warm it sounds.
- **Definitions and background are facts too.** Memory is not a source for a detail the piece will assert.
- **Vague wording can be the honest wording.** If the source says someone is "associated with" a project and nothing more, keep that. Do not invent the role to make the sentence specific.
- **If the facts cannot carry the requested length, write the shorter piece** and say why. Never pad, and never restate a fact to reach a length or a rhythm.
- **An empty claim is different from a gap.** If "a place where people come together" has nothing behind it, cut it; restating it in fresher words keeps the emptiness. Where a real specific is missing, mark `[TK: specific question]` as `interview.md` describes.

When sources disagree, say so or ask. Do not average them or pick one without saying so. Creative writing inside a requested fictional frame is the exception: invention is the job there, and it stays inside the frame.

## Claims and their support

For factual, persuasive, or decision writing, sort the claims that matter:

| State | Meaning | Usual move |
|---|---|---|
| Supported | The supplied or verified evidence carries the claim at its stated scope | Keep |
| Partly supported | Evidence covers a narrower period, place, group, or size | Narrow the claim to the evidence |
| Uncertain | Evidence is incomplete, old, indirect, or in conflict | Qualify, attribute, or verify |
| Unsupported | Nothing in the allowed material carries it | Cut, or mark a `[TK]` |
| Not a factual claim | Opinion, preference, instruction, or a labeled projection | Keep it labeled as what it is |

Missing support is not proof that a claim is false, and the absence of a contradiction is not support. Repairs come in four kinds, tried in this order: **soften, attribute, qualify, cut**. None of them adds a new fact.

Check the dimensions where a claim usually outruns its evidence: number and rounding, period, geography, population, scope, and causation. A title or summary should not say more than the body. "For the whole sector" needs sector-wide evidence; "for this street" needs only the street. A source near a sentence is not support unless it says the thing.

An **attributed statement** is a report of what someone said. If it looks wrong, do not correct or reverse it inside the attribution. State the conflicting evidence separately, or raise it with the user.

In persuasive writing, promise the levers the writer controls (what is delivered, by when, at what price) and describe outcomes that depend on other people, a market, or a platform as aims.

## What a fix must not create

Removing one habit often installs another, and the replacement is as recognizable as the original. After an edit, read once for these:

- **A synonym swap.** "Leverage" becomes "utilize", "delve into" becomes "dig into". The empty claim is still empty. Repair the meaning or delete the sentence.
- **Clipped fragments.** "Not the technology. The people." "Move fast. Stay close. Ship." Removing connectives produces punchy lines that state relations the source never asserted, or hide ones it did.
- **A new closer.** One slogan is replaced with a sharper slogan.
- **Punctuation moved sideways.** A removed dash becomes a comma splice, a colon pivot, or the same contrast split into two short sentences.
- **Lost hedges.** "Roughly 60%" becomes "60%"; "may" becomes "will". Where the hedge is the content, removing it changes the claim.
- **Manufactured voice.** An invented opinion, a contrarian stance the source never took, a performed confession ("I'll be honest"), a quirk, a typo, or forced casualness.
- **Flattened voice.** Opinions, mixed feelings, first person, and humor that the source had are gone. Restore them; voice the source already had outranks a pattern cleanup.

When a paragraph keeps resisting, rewrite it around its main point. Patching flagged phrases one at a time leaves the seams showing.

## After the edit

Check in this order, because the first items are the costly ones:

1. Did any fact, name, number, date, quotation, citation, ranking, or same-time claim change or disappear?
2. Did a refusal, limit, condition, or uncertainty get weaker? Did a plan, estimate, or possibility get stronger?
3. Did any new specific, cause, feeling, or commitment appear?
4. Is every remaining change tied to a finding or to the request?
5. Did the fix create a new habit from the list above?

`scripts/fidelity_check.py` covers the mechanical part of items 1 to 3 when tools are available; use `--mode summary` for a requested cut. Every line it prints is a prompt to look, and many are legitimate. It is word-level, so a claim invented in plain words passes untouched and its silence does not establish that the meaning held. If it was not run, the check was done by reading; never report a tool result that does not exist.
