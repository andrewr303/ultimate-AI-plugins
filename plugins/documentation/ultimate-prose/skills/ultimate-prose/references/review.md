# Review format

Use for a review, critique, audit, or `MODE: detect` request. Review the text Andrew supplied; do not return a replacement draft or modify a file unless he asks for one. A useful review ranks problems by what they cost the reader, so the largest material issue comes first and line edits come second. Write the review itself in his business register: direct, specific, and free of a sales-like offer to continue.

## Lead with the piece

Use only the fields that add information for this piece:

```text
Job:          channel, reader, and intended outcome
Substance:    what the piece specifically contributes, or what is missing
Trust:        factual support, attribution, uncertainty, claim state, and any preservation risk
Development:  how the material progresses, and where it turns into a list or repeats itself
Voice:        what reads as Andrew, and where a generic register takes over
Ending:       whether it stops on the last useful fact, decision, or ask
Top fixes:    the two or three changes with the largest expected gain, ranked
```

Judge a support request, runbook, data table note, or confirmation by the job it does. It does not owe a thesis, a story, or a mechanism paragraph.

If the substance is too thin to support a useful rewrite (a founder post with no operating observation, an investor note with no change to report), say so plainly and name the material that would fix it. Offer the interview in `references/interview.md` only as an option; surface edits cannot supply missing evidence or experience, and the review should say that once.

## Then the passages

Write one block per material issue:

```text
Passage:     the shortest exact quote that locates the issue
Verdict:     keep | revise | ask-author | cut
Pattern:     a short name from references/tells.md
Why:         what the passage does instead of its job, and what that costs the reader
Suggestion:  a supported replacement, a precise question for Andrew, or the reason to cut
```

- **keep:** a pattern is present but earned, required by the channel, or better than the alternatives. Say what earns it.
- **revise:** the text already contains enough material for an honest improvement.
- **ask-author:** the fix needs a fact, mechanism, example, opinion, or experience the text does not supply. Ask for exactly that (for example the actual metric, the customer's words, or the date), and offer a cut or a plain fallback in the meantime.
- **cut:** the passage adds only repetition, ceremony, unsupported emphasis, or closure.

Check every suggestion against the passage it replaces. It must keep the facts, attribution, claim state, and voice, and it must not reproduce the same formula with different punctuation. Andrew's no-dash default makes this failure common: "It's not a dashboard, it's a decision engine" and "It's not a dashboard: it's a decision engine" are the same pivot as the dashed original.

## Discipline

- Separate errors from likely improvements, and both from taste. Label taste as taste.
- Quote the previous sentence when context decides whether a contrast, adjective, list, passive, or closing beat is earned.
- Prefer a few high-impact findings to an exhaustive word list, and group overlapping matches into one finding.
- When the prose already does its job, say so and report no finding.
- Scanner output (`scripts/lint.py --detect`, `scripts/lint_andrew.py --detect`, `scripts/prose_stats.py`) points at passages worth reading. It is never a finding by itself, and no detector verdict is evidence that a passage is good, bad, human, or generated.
- If asked who or what wrote the text, say that style cannot establish authorship, then review what the reader can inspect.
- End with the findings: no score, no offer to rewrite, no recap.
