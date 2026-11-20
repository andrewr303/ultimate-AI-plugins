# Review format

Use for a review, critique, audit, or assessment. Review the text the user supplied; do not return a replacement draft or modify a file unless the user asks for one. A useful review ranks problems by what they cost the reader, so the largest material issue comes first and line edits come second.

## Lead with the piece

Use only the fields that add information for this piece:

```text
Job:          medium, reader, and intended outcome
Substance:    what the piece specifically contributes, or what is missing
Trust:        factual support, attribution, uncertainty, and any preservation risk
Development:  how the material progresses, and where it turns into a list or repeats itself
Voice:        what reads as the author's, and where a generic register takes over
Ending:       whether it stops on the last useful thought
Top fixes:    the two or three changes with the largest expected gain, ranked
```

Judge reference, procedural, academic, legal, and message writing by the job it does. A runbook does not owe a thesis, a museum label does not owe data, and an email does not owe narrative momentum.

If the substance is too thin to support a useful rewrite, say so plainly and offer the co-write interview in `references/interview.md`. Line feedback can continue, but surface edits cannot supply missing evidence or experience, and the review should say that once.

## Then the passages

Write one block per material issue:

```text
Passage:     the shortest exact quote that locates the issue
Verdict:     keep | revise | ask-author | cut
Pattern:     a short name from references/patterns.md
Why:         what the passage does instead of its job, and what that costs the reader
Suggestion:  a supported replacement, a precise question for the author, or the reason to cut
```

- **keep:** a pattern is present but earned, required by the medium, or better than the alternatives. Say what earns it.
- **revise:** the text already contains enough material for an honest improvement.
- **ask-author:** the fix needs a fact, mechanism, example, opinion, or experience the text does not supply. Ask for exactly that and offer a cut or a plain fallback in the meantime.
- **cut:** the passage adds only repetition, ceremony, unsupported emphasis, or closure.

Check every suggestion against the passage it replaces. It must keep the facts, attribution, scope, and voice, and it must not reproduce the same formula with different punctuation: a dash pivot rewritten as a colon pivot, or split into two short sentences, is still the same pivot.

## Discipline

- Separate errors from likely improvements, and both from taste. Label taste as taste.
- Quote the previous sentence when context decides whether a contrast, adjective, list, passive, or closing beat is earned.
- Prefer a few high-impact findings to an exhaustive word list, and group overlapping matches into one finding.
- When the prose already does its job, say so and report no finding.
- Scanner output (`scripts/lint.py --detect`, `scripts/prose_stats.py`) points at passages worth reading. It is never a finding by itself, and no detector verdict is evidence that a passage is good, bad, human, or generated.
- If asked who or what wrote the text, say that style cannot establish authorship, then review what the reader can inspect.
- End with the findings: no score, no offer to rewrite, no recap.
