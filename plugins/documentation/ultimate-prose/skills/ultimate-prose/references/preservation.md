# Keeping the meaning

Read this before an edit that could change what a piece says, and after a substantial rewrite. A piece can read better and say something different, and polish is worth nothing if a number, a refusal, or a condition did not survive it.

## Candidate, finding, edit

A scanner match or a pattern from `tells.md` is a **candidate**. It becomes a **finding** only after the surrounding text and the pattern's exceptions are read. A finding becomes an **edit** only when the job allows one: a review reports it, a light polish fixes it only if the fix is small, and a quotation, code, or attributed passage is reported and left as written. Every changed span should trace to a finding or to the request.

**When nothing needs fixing, return the text exactly as supplied** and say it already works. Do not merge two sentences or swap a word to show that editing happened.

## What must survive

- Numbers with their units, denominators, time windows, and rounding. "42%" can become "about four in ten"; it cannot become "almost half".
- Names, dates, versions, identifiers, links, exact error text, and quotations word for word.
- Negation and limits: a refusal, an exception, "not yet", "only", "unless".
- Conditions and dependencies: "if testing passes", "once the contract is signed".
- Strength: may versus will, some versus all, estimate versus result, plan versus done, association versus cause, a local check versus an approval.
- Rankings ("the second-largest") and claims that two things happen at the same time.
- Requirement words in legal, financial, medical, and security text: shall, must, never, always, preliminary. Each is a constraint, not a style choice.

Three edits lose these most often: merging list items into a sentence, trimming qualifiers to sound decisive, and turning a labeled list into prose. Reread the protected items after each.

## Remove or repair before adding

- **A join** uses "and", "but", or a semicolon, or merges two sentences. It never adds a reason: "because", "so", and "which means" are claims, used only when the source states that relation.
- **A line that speaks for Andrew is a new fact.** A promise, praise for specific work, thanks for something that did not happen, a feeling about an event, or an apology where the brief establishes no fault of his should not appear unless the brief supplies it. When the brief states his own mistake, one plain apology beside the fix is how he handles it.
- **His habitual warmth is voice, not a new fact, when the brief supports the act behind it.** "Sounds good" for an agreement he has given, "happy to" for work he is taking on, "thanks for the feedback" when replying to feedback, and plain interest ("excited to try it", "curious to see how it holds up") in something he says he will try are how he writes. Use one such line where it fits. Do not attach enthusiasm to a fact the brief frames neutrally or negatively, and do not let courtesy widen a commitment.
- **Vague wording can be the honest wording.** If the source says only "associated with", keep it; do not invent the role.
- **An empty claim is not a gap.** Cut it; restating it in fresher words keeps the emptiness. Where a real specific is missing, mark `[TK: specific question]`.
- **If the facts cannot carry the requested length, write the shorter piece** and say why.

When sources disagree, say so or ask. An **attributed statement** reports what someone said: if it looks wrong, do not correct it inside the attribution; state the conflicting evidence separately.

## Claims and their support

A claim is supported, partly supported, uncertain, unsupported, or not a factual claim (an opinion or a labeled projection). Narrow a partly supported claim to its evidence; qualify, attribute, or verify an uncertain one; cut an unsupported one or mark a `[TK]`. Repairs come in this order: **soften, attribute, qualify, cut**. None adds a fact. Check where claims outrun evidence: number and rounding, period, geography, population, scope, and causation. In a pitch, promise the levers Andrew controls (what is delivered, by when, at what price) and describe outcomes that depend on other people or a market as aims.

## What a fix must not create

Removing one habit often installs another. After an edit, read once for these:

- **A synonym swap.** "Leverage" becomes "utilize". The empty claim is still empty; repair the meaning or delete the sentence.
- **Clipped fragments.** "Not the technology. The people." Removing connectives states relations the source never asserted, and it is the opposite of connected reasoning.
- **A new closer.** One slogan replaced with a sharper one.
- **Punctuation moved sideways.** Replacing a dash needs a decision: a period if what follows could stand as a sentence, a comma or parentheses if it adds detail to the same subject, a rebuilt sentence if neither reads right. Never a comma splice.
- **Lost hedges.** "Roughly 60%" becomes "60%". Where the hedge is the content, removing it changes the claim.
- **Manufactured or flattened voice.** An invented opinion or quirk goes in, or a stated opinion, mixed feeling, or first person the draft had comes out. Voice the source already had outranks a pattern cleanup.

## After the edit

Check in this order: a changed or missing fact, name, number, date, quotation, ranking, or same-time claim; a weakened limit or a strengthened claim; anything new (a specific, cause, feeling, or commitment); a change tied to no finding; a new habit from the list above. `scripts/fidelity_check.py` covers the mechanical part (`--mode summary` for a requested cut). It is word-level, so its silence does not establish that the meaning held.
