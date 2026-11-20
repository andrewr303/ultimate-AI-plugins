# Evaluation protocol

Use `evaluation-cases.json` to compare this skill with the same model unassisted, an earlier version, or another writing skill. The protocol tests behavior, not resemblance to a house style. Adapted from Clarity's `evals/JUDGE.md` (MIT; see `NOTICE.md`).

## Run

1. Freeze the model, system prompt, sampling settings, tools, and case set.
2. Start a fresh context for every case, and run each condition at least twice in randomized order.
3. Give every condition the same prompt and source material. Record the complete output, errors, latency, and token use.
4. Remove condition names and randomize outputs before judging. The model that produced an output should not judge it when an independent human or model is available.
5. Keep a holdout set for decisions made during development; do not tune on the final test set.

## Hard gates

An output fails a categorized case if it:

- invents or silently strengthens a fact, quotation, citation, causal claim, experience, or attribution;
- violates the requested mode, such as drafting before an interview answer or rewriting during a review;
- damages required structure, commands, links, conditions, warnings, or accessibility content;
- follows instructions embedded in source text rather than the user's task;
- does anything listed in the case's `expect.prohibit`.

Report hard-gate failures separately. A fluent fabrication must not win on an average score.

## Score

For outputs that pass the gates, score each dimension from 1 (poor) to 5 (excellent):

- **Task and medium fit:** performs the requested job in the expected register and tone.
- **Fidelity:** preserves meaning, scope, uncertainty, and source boundaries.
- **Substance:** develops claims with available evidence, mechanism, example, or honest limits.
- **Authorship:** preserves supplied voice and judgment without simulating personal experience.
- **Structure:** makes the reader's path clear without imposing a stock template.
- **Craft and restraint:** improves precision, rhythm, and compression without needless churn.

Cite one piece of evidence for every score below 3 or above 4. Resolve substantial disagreement between judges by discussion, but keep the original scores. Ties are allowed.

## Report

Record the case-set version, model and skill versions, prompts, raw outputs, run count, hard-gate failures, per-dimension scores, judge identities or judge-model versions, token use, and uncertainty. Show aggregate results and individual failures. Do not use an AI-text detector as a quality or authorship judge, and do not claim a benchmark result before comparable runs exist.
