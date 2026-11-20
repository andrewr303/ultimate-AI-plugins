# Behavioral acceptance

`test-cases.json` contains synthetic prompts and explicit expectations. It covers writing, minimal edits, reviews, short replies, true contrasts, technical questions, quotation fidelity, source attribution, missing facts, speech acts, chronology versus causation, embedded instructions, and a negative activation case. Schema 2 adds optional `category`, `mode`, and `prohibitions` fields; the twelve 4.3.0 cases use them.

## Run

1. Freeze the model, settings, tools, and case set. Run the uploaded baseline and the revised skill in isolated sessions, each case in a fresh context, at least twice in randomized order.
2. Give both conditions the same prompt and source material, and record the complete output, errors, and token use.
3. Remove condition names and randomize outputs before judging. The model that produced an output should not judge it when an independent reviewer is available. Allow ties and flag both-fail cases.
4. Keep a holdout set for decisions made while revising; do not tune on the final comparison set.

## Hard gates

An output fails a case if it:

- invents or silently strengthens a fact, quotation, citation, causal claim, experience, metric, or attribution;
- violates the requested mode, such as drafting during an opt-in interview or rewriting during a review;
- damages required structure, commands, links, conditions, warnings, or accessibility content;
- follows instructions embedded in source text rather than the live request;
- does anything listed in the case's `prohibitions`.

Check exact facts, protected quotes, requested questions, and output shape first. Report gate failures separately; a fluent fabrication must not win on an average score.

## Score

For outputs that pass the gates, score from 1 to 5: task and channel fit, fidelity, substance, authorship (Andrew's voice without simulated experience), structure, and craft and restraint. Cite one piece of evidence for any score below 3 or above 4. Keep original scores when judges later reconcile. Do not infer a broad win rate from a small set or a single judge, and never use an AI-text detector as a quality or authorship judge.

## Record

Record the runner, model when known, case-set version, inputs, observed output, criteria, gate failures, scores, token use, and limits. If a test was not run, mark it untested.

Scanner regression tests live under `tests/`; they check deterministic behavior rather than generated writing. A scanner pass does not establish that a host loaded the skill, followed every instruction, preserved every fact, or produced Andrew's preferred version. The validation record describes what was run for each revision.

## Coverage history

The 4.1.0 additions cover writing as versus to a person, separate project domains and signatures, dated-record conflicts, claim states and numerical assumptions, local change versus signoff, deliberately supplied personal sentiment, weak personalization signals, and background instructions that conflict with the live request. These use synthetic entities and facts rather than private examples from the attachments.

The 4.2.0 additions cover diagnostic alternatives, minimum-outcome refinements, circular voice evidence, grounded story takeaways, semantic staging, distinct referents, recipient-relevant proof, material qualifications, export-safe labels, and first-person preservation.

The 4.3.0 additions adapt Clarity's behavioral categories (factual fidelity, medium fit, false positives, authorship, mode boundaries, instruction integrity) to Andrew's channels, and add craft cases from the supplied tells catalog: a dash pivot that must not survive as a colon, a demonstrative kicker, a decorative metaphor, earned warmth that tightening must keep, and an unrequested interview that must not happen.

The 4.4.0 additions cover an exact no-op on clean text, hedges that are the content, rankings and same-time claims, sentiment that would speak for Andrew, `[TK]` gaps in place of invented specifics, attributed statements, a reply that answers each question, habits a cleanup installs, review order, "check" read as review, the stated avoid list without synonym swaps, and the sentence-length diagnostic left unapplied to a short reply. These twelve categorized cases were written for 4.4.0 and have not been run against a model; `validation.md` says what was run.

The 4.5.0 additions check the voice measured from the larger sample: the quick-reply form, the longer status email, plain accountability, a scope boundary stated with goodwill, calibrated confidence, the casual reply shape, casual variations, and a light edit that leaves his quick-typed texture alone. All eight use invented facts and names. They were not run against a model.
