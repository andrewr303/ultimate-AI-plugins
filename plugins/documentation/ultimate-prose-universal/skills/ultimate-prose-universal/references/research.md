# Design provenance

Research reviewed on 19 October 2026. Repository eligibility was restricted to verified default-branch file changes from **19 September through 19 October 2026**, with no relaxed date window. A recent push timestamp alone was insufficient. Files were read at pinned commits; no candidate code was cloned, installed, or executed.

Discovery used the awesome-repositories directory first and ten independent, date-filtered GitHub search queries. Seven qualified finalists were inspected. A separate review bundle contains the manual source/claim ledgers, query log, changed-file inventory, and decision report. No automated research-gate result is claimed.

## Source observations and design choices

| Repository and inspected commit | Relevant observation | Choice in this revision |
|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer/tree/8c307f367c91bd974002f10f2be2965d642c13df) — `SKILL.md` | Reviews rhetorical structure as well as words; supports sample-informed work | Original contextual review, optional samples; do not inherit its punctuation bans |
| [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing/tree/f516147d017a3fe43ae99192cb89d8261b0c8679) — `SKILL.md` | Distinguishes decisive writing from removing material uncertainty | Bold tone retains conditions and scope |
| [forjd/better-writing](https://github.com/forjd/better-writing/tree/8e45d0b241fc042d39444f499bbce4cfdb7a6c86) — `skills/better-writing/SKILL.md`, `evals/README.md` | Situational controls, light edits, contextual exceptions, behavioral comparison | Separate tone from other controls; preserve good writing; test output properties separately from scans |
| [adewale/anti-slop-writing](https://github.com/adewale/anti-slop-writing/tree/00b0809cdd5335d54ae61ee1459d78c95db4c61b) — `skills/anti-slop-writing/SKILL.md` | Earned uses of devices need contextual judgment | No universal word blacklist or rhythm recipe |
| [phuryn/work-humanizer](https://github.com/phuryn/work-humanizer/tree/0a9065791d021f3dda695f3887cb2ae4c0eacbcf) — `skills/work-humanizer/SKILL.md` | Explicit meaning, commitment, and certainty checks | Protect substantive meaning before and after tone changes; reject artificial camouflage |
| [product-on-purpose/writing-style-catalog](https://github.com/product-on-purpose/writing-style-catalog/tree/cff5923afb926d23c0d202d2cfad92fc58b19b85) — `skills/writing-instruction-builder/SKILL.md` | Composes voice, tone, style, and format as separate axes | Independently written tone controls and blends; no catalog entries or code copied |
| [parasdoshicom/your-voice](https://github.com/parasdoshicom/your-voice/tree/e92148bdd28ebb33ff78a017302b64075eb78caf) — `SKILL.md`, `references/evaluation.md` | Optional samples, preservation modes, separate evaluation material | Voluntary user-owned calibration, no bundled persona; semantic checks independent of style preference |

Shared design observations were checked against independent project authors. Their existence in source guidance does not establish universal efficacy. The report separates direct repository metadata from independently corroborated observations.

## Freshness and evidence limits

All seven repositories have nonempty default-branch file changes in the specified window. The exact inspected skill paths in Anti-Slop Writing and Writing Style Catalog did not themselves change during that window; their recent activity concerns other repository files. They informed abstract design only. The other five have verified skill-file changes in the window. Exact activity dates and changed paths are recorded in the separate inventory and primary-source annex.

Maintainer evaluations were inspected for methodology and failure modes, not rerun. Their scores do not transfer to this package. No source establishes that a word list, punctuation rule, or this revision guarantees human authorship, zero possible AI traces, or a detector outcome.

License files and the catalog's separate content notice were inspected. This revision bundles no third-party implementation, style-entry text, corpus, model asset, or tests. The original tone descriptions, synthetic examples, scanner, and fixtures were written for this task. Public sources informed abstract choices; the package has no runtime dependency on them.

## Maintenance

Treat the contextual pattern guide as revisable editorial advice. When a model changes or users report recurring problems, record the actual failure, add a preservation counterexample, compare generated results on held-out tasks, and keep ties or regressions visible. Favor relevant human judgment and factual fidelity over optimizing detector scores or warning counts. This is a recommended maintenance process, not a claim that this package updates itself.

## 5.1.0: Clarity and the supplied tells catalog

This revision draws on two user-supplied sources reviewed locally on 7 November 2026: the `clarity-main.zip` archive (Clarity Agent Skill, `SKILL.md` metadata version 0.2.1, MIT License, Copyright (c) 2026 Addy Osmani) and a standalone `tells.md` editing catalog with no stated author or license. Clarity's runtime files, scripts, eval cases, judging protocol, samples, and browser-editor heuristics were read in full; its website build was not run. No network research was needed for these local changes, and no claim from either source was treated as validated evidence of an effect on writing quality.

Clarity's central claim is that generic model prose fails on substance before style, so it diagnoses missing source material first and treats familiar patterns as contextual prompts rather than bans. That matches this skill's existing meaning-first stance and fills four gaps: no ordered diagnosis, no review verdicts, no way to collect the author's own material, and no positive craft step after subtraction.

| Element | Decision | Where it lives now |
|---|---|---|
| Ordered diagnosis: truth and scope, substance, development, sentences, craft | Adopted | SKILL.md working method; the patterns reference |
| What each register owes (argument, explanation, update or guide, message, story) | Adopted, with the full set of seven registers | SKILL.md |
| Review format with keep, revise, ask-author, and cut verdicts | Adopted | `references/review.md` |
| Perspective interview, `[TK: question]` gaps, provenance note | Adopted for explicit co-write requests and for authored pieces whose value depends on experience the brief lacks; a user who wants a draft now gets one with marked gaps | `references/interview.md` |
| Long-form craft: one-job openings, development, the author test, putting craft back, one pass then stop | Adopted | `references/longform.md` |
| Medium routing (docs, reference, academic, legal and safety, UI, talks, fiction) | Adopted | the quick router and new sections in `references/channels.md` |
| Flatten, relation, and emphasis tests; vague attribution; abstract actors; structural regularity; preserving human material | Adopted | the patterns reference and scanner rules |
| Rewrite check, including a pattern reproduced under new punctuation | Adopted and extended with `scripts/fidelity_check.py` | the delivery checklist |
| `prose_stats.py` and `strip_markdown.py` (no composite score) | Adapted into `scripts/prose_stats.py`: uses this skill's source masks, adds `--compare`, lexical diversity, repeated trigrams, and look-here lists for unsupported importance, kickers, and flourishes | `scripts/` |
| `validate_package.py` | Adapted into a generic validator for routes, budgets, eval schema, and manifests | `scripts/` |
| `evals/cases.json` and `evals/JUDGE.md` | Adapted: categories, prohibitions, hard gates, and blinded scoring | `references/evaluation-cases.json` and `references/evaluation-protocol.md` |
| Browser-editor heuristics: Claude-frequency vocabulary cluster, extremes, importance without mechanism | Adopted as look-here lists only; the cluster reports only four or more distinct terms in 150 or more words | `scripts/prose_stats.py` |

The supplied tells catalog contributed the demonstrative kicker, meta throat-clearing, importance-flagging, decorative metaphor, grandiose prediction, correlative and hedged scaffolding, symmetrical hedging, definition openers, a plainer-word lexicon, the "could the author defend it" test, five ordered triage questions, and light versus heavy calibration. Three of its rules were softened to fit this skill's evidence stance: "delete puffery adverbs" became a triage question because degree and warmth can be real, "rhythm needs contrast" became an instruction to inspect uniformity without alternating lengths mechanically, and "vary list length" became "keep two when two is true, and three when three is true."

Rejected:

- Clarity's "prefer shorter words and sentences" as a blanket rule. Its own long-form reference keeps a long sentence when one subject carries the clauses, and that narrower rule is the one adopted. Rhythm stays a consequence of the thought, as before.
- The browser editor's 0 to 100 surface-pattern score and readability grade. They contradict the no-score design and invite optimizing toward a number.
- A stacked-questions rule, which would flag legitimate multi-question support and coordination messages.
- Turning the excess-vocabulary lists into scanner findings. This skill keeps no banned vocabulary; the words appear only in `prose_stats.py` look-here lists and in the plainer-word table, which keeps the original when the plain word is worse.
- Copying Clarity's eighteen-rule essay, site, or command wrappers. The guidance here is rewritten for this skill, and modes are selected through the existing controls.

Clarity reports that a stylometric composite ranked a genuinely human control as the "riskiest" text in its exploratory corpus. That observation is the source's own and was not reproduced here; it is the reason both new scripts report descriptive measurements and lists rather than a score.

## 5.2.0: five supplied writing projects

Reviewed on 17 November 2026 from five archives the user supplied. Each was read in place; no code from them was installed or executed, and their maintainers' benchmarks were not rerun. Versions are those in the archives, not necessarily the latest upstream. The review found that 5.1.0 already covered much of what these projects share (ordered diagnosis, review verdicts, a rewrite check, descriptive statistics with no score), so this revision takes only what was missing.

| Source | Taken, in this skill's own wording | Left out |
|---|---|---|
| plainspoken 0.13.0 | A working definition of a join; a line that speaks for the user counts as a new fact; the reply agenda; first-contact and follow-up checks; the control test for promises; evidence dimensions and the soften, attribute, qualify, cut order; count gates as a scanner design | Blocking severities and pass/fail gates; a universal ban list; cadence and vocabulary metrics as targets; rules that demand informality; a default locale or reading level |
| humanizer 4.0.0 | Weighting a habit by how rarely a careful writer chooses it; paragraph-scale forms of sentence habits; the wrong-reader reply; objections nobody raised; writing about the document; rankings and same-time claims in the post-edit check | Its 4.0 allowance to add a true detail or a reaction; the forced dash ban; a default three-part output; "sounds AI-generated" framing |
| avoid-ai-writing 3.39.0 | The candidate, finding, edit distinction; the exact no-op rule; change accounting; draft-artifact checks (placeholders, citation markup, tracking parameters, zero-width characters); cluster gates in place of single-word reports | Authorship labels and probabilities; stylometric signals; a universal tier-1 word list; automatic edits inside protected text. Its own measurements report that its composite score does not separate machine text from human text |
| writing-quality 0.2.3 | Claim states and remedies; the least-mutating default; voice outranking pattern cleanup; document-job coverage checks; confidence tied to sample size | The numeric quality gate; "always replace" word rules; decisive-conclusion enforcement that erases real uncertainty; per-user persistence |
| unslop 2.3.0 | Its own adversarial critique: a cleanup trades one recognizable register for clipped fragments, antithesis without a connective, and slogan closers, and it deletes hedges; legal, medical, and security words as preservation constraints; never correct an attributed statement; voice-card provenance and uncovered gaps; one-dimension preference pairs | The banned catalog and hard severities; blocking gates; stylometric scores; cadence quotas; personality presets; examples that invent facts |

Where the sources disagreed, this skill kept the option that changes less and claims less. Humanizer 4.0 permits adding a specific the editor knows to be true, and plainspoken deletes even its fiction exemption; this skill keeps invention inside a requested creative frame and nowhere else. Several sources ban punctuation or words outright; here they stay user-selected conventions (`--no-em-dash`, `--avoid`).

Tool decisions. A separate before-and-after comparison script was drafted and then dropped, because `fidelity_check.py` already did that job; the useful differences were folded into it (a swap inside one family is now quiet, as its description promised; new promises and causes are reported; `--mode summary` serves requested cuts). Structure and vocabulary observations stayed in `prose_stats.py` and were not duplicated as scanner findings. New scanner constructions entered the default set only if an ordinary business reply, a technical paragraph, and this package's own documents stayed clean under them.
