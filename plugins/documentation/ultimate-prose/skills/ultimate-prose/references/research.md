# Design provenance

The revision used the research-first-creator workflow: directory discovery, independent GitHub searches, pinned implementation review, a manual source/claim ledger, an original revision, and targeted checks. This is a manually supported design review, not an automated research-gate PASS.

## Adopted ideas

| Requirement | Inspected evidence | Application in this skill |
|---|---|---|
| Scoped suggestions and exceptions | [Vale scopes](https://github.com/vale-cli/vale/blob/cfb21a4ce87238bcfb44b90e8e0db9e0e91d6c09/internal/check/scope.go), [textlint filter ranges](https://github.com/textlint/textlint/blob/02a215ac052ff8c19931a83df84634b522453bc2/docs/filter-rule.md) | Protect source spans, report their original positions, and review patterns in context. `clm_discovery_scopes` |
| Positive and negative rule cases | [textlint tester](https://github.com/textlint/textlint/blob/02a215ac052ff8c19931a83df84634b522453bc2/packages/textlint-tester/test/textlint-tester.test.ts), [editorial exception fixture](https://github.com/tbhb/vale-ai-tells/blob/51f646e366ba7c9dcb078ebeae345b7ff353eb3b/tests/ai-tells/EmDashUsage.test.yml) | Check legitimate uses and preservation as well as patterns that should be found. `clm_discovery_cases` |
| Same-prompt baseline comparison | [Anthropic skill creator](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/skill-creator/SKILL.md), [skill-up evaluation guide](https://github.com/alibaba/skill-up/blob/87f86b57deda76b8eea4963f2b05f33079052202/docs/guide/writing-evals.md) | Keep the uploaded version as baseline; compare identical synthetic tasks. `clm_discovery_baseline` |
| Separate exact requirements from judgment | [Blind comparator](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/skill-creator/agents/comparator.md), [skill-up grading design](https://github.com/alibaba/skill-up/blob/87f86b57deda76b8eea4963f2b05f33079052202/docs/guide/writing-evals.md) | Check numerical/quotation/output requirements separately from voice and usefulness. `clm_discovery_judging` |
| Context-sensitive voice | [Humanizer voice guidance](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/SKILL.md), [Microsoft historical voice guidance](https://github.com/MicrosoftDocs/microsoft-style-guide/blob/c6945c32294e845a84b192a094fb1b7c2c452a6a/styleguide/brand-voice-above-all-simple-human.md) | Use comparable channel evidence; let explicit user direction override defaults. `clm_discovery_voice` |

These are implementation precedents, not controlled evidence that a prose formula improves outcomes. The revision does not import upstream code, rule lists, dependencies, or workflow text. The original skill's own scanners were modified locally. The existing skill name and declared license were retained; no new license-clearance conclusion is made.

The supplied CSV observations support the practical changes: short replies stay short; email history and third-party parent posts are excluded from voice measurements; delivered wording, editing notes, and unknown drafting origins are kept separate. `corpus-notes.md` records the method and limits.

## Rejected approaches

- Global sentence-length floors, mandatory clause percentages, and punctuation quotas.
- Treating a word list as an authorship detector or an automatic rewrite mandate.
- Using publication, the Custom field, or blank ratings as proof of unassisted authorship or strong preference.
- Optimizing a writing rule against likes or impressions without evidence isolating its effect.
- Adopting a large external linting/evaluation runtime for a portable, standard-library skill.
- Requiring a rewrite or change report when the user requested an assessment or copy-ready text only.

## Research scope and limits

Eight independent query rungs produced a screen of fifteen candidates. Seven finalist implementations were inspected, alongside historical and adjacent sources. The separate review bundle contains the query ladder, source ledger, claim ledger, and decision matrix. Star counts, license labels, and freshness observations are not used as proof of fitness or legal rights. Stale or archived sources are historical references, not maintenance recommendations.

No candidate code was run, no dependencies were installed, and no private source text entered research queries. The local research accelerator was not configured; no `verified_claims.json` or automated research verification is claimed. Scanner regression tests and model-assisted smoke tests, when run, have their own evidence in `validation.md` and do not establish host installation or the user's subjective preference.

## Further update from supplied context profiles

Version 4.1.0 adds a local review of `personal-context-1.txt` and `personalization-profile.md`. They corroborate the adaptive prose direction and motivate explicit author/recipient separation, domain routing, current-thread continuity, claim-state checks, and narrow disclosure. `personalization.md` gives their hashes and source locators. The adopted guidance is freshly written and excludes the documents' private fact inventories and verbatim examples.

This is an inspection of secondary syntheses, not independent verification of the social, email, workspace, or account records they cite. Their tool recommendations and embedded prompt blocks were treated as data. No external research refresh was needed for these local editorial changes, and no additional corpus statistics, performance claim, source inspection, or tool connection is asserted. The earlier pinned implementation research remains the design provenance for the unchanged scanner architecture.

## Further GitHub review for 4.2.0

The additional research used ten initial public GitHub query rungs with targeted follow-ups, screened fifteen candidates, and inspected seven finalists at recorded commits. Directory search was used for discovery, with independent repository metadata, changed-file history, and actual source/test review. Historical implementations are explicitly historical; popularity and a pushed timestamp are not proof of current code activity. The review used manual source/claim ledgers and did not run an automated research gate.

| Adopted abstract mechanism | Pinned evidence | Original application |
|---|---|---|
| Narrow redundancy suggestion with preservation cases | [Harper acronym implementation/tests](https://github.com/Automattic/harper/blob/6793cbc86568f1cbb78adf695997c70faae493fe/harper-core/src/linting/redundant_acronyms.rs), [retext implementation](https://github.com/retextjs/retext-redundant-acronyms/blob/e670637aa13a223f7d6505349f4a474695e2c115/lib/index.js) | Tiny uppercase PIN/ATM advisory, exact source spans, no automatic rewrite or authorship label. `clm_acronym_advisory`, `clm_contextual_tests` |
| Contextual repetition and protected text | [Scoped duplication implementation](https://github.com/tbhb/vale-ai-tells/blob/51f646e366ba7c9dcb078ebeae345b7ff353eb3b/styles/config/scripts/ContentDuplication.tengo), [Harper repetition tests](https://github.com/Automattic/harper/blob/6793cbc86568f1cbb78adf695997c70faae493fe/harper-core/src/linting/repeated_words.rs) | Ask what a later sentence adds; preserve exceptions, refinements, and repeated operational instructions. No imported overlap threshold or universal repeat deletion. `clm_repetition_context` |
| Task-shaped sample conditioning | [LaMP profile selection](https://github.com/LaMP-Benchmark/LaMP/blob/38c9d4d87629aba5a821bcddc10ddcc83f8d49a1/LaMP/prompts/prompts.py#L189), [TinyStyler sample handling](https://github.com/zacharyhorvitz/TinyStyler/blob/128e735520f215eb6cd55ac10760b68f8b33f269/authorship_evaluation/tinystyler_authorship.py) | Match available examples to audience/channel/purpose; separate samples from current facts and desired output. `clm_sample_conditioning` |
| Separate condition, source, output, and evaluation | [TinyStyler evaluation](https://github.com/zacharyhorvitz/TinyStyler/blob/128e735520f215eb6cd55ac10760b68f8b33f269/authorship_evaluation/styll_eval_metrics/evaluation_metrics.py), [LaMP generation evaluation](https://github.com/LaMP-Benchmark/LaMP/blob/38c9d4d87629aba5a821bcddc10ddcc83f8d49a1/LaMP/metrics/generation_metrics.py) | Check factual meaning and voice/editorial fit independently; hold calibration evidence apart from judged outputs. No classifier or model runtime adopted. `clm_eval_separation` |

These are implementation precedents, not validated effect sizes for this skill. The new reference and scanner rule are written locally. No external code, rule catalogue, writer profile, corpus, model weight, or dependency was copied or installed. The separate review bundle includes the full matrix, pinned source registry, claim ledger, search screen, and explicit limits. Upstream source snapshots remain working research material rather than redistributed assets.

The additional attachment is a derivative profile that repeats prior evidence. `voice-calibration.md` records its hash, locators, and narrow editorial cues. Attributed quotations, prepared biographies, repeated rules, and unsupported status claims were not merged into a larger natural-writing corpus. A source's own export-safe label was not treated as disclosure permission.

## Unresolved

The available sources and small convenience samples do not establish a universal cadence optimum, wording-caused engagement improvement, or an authorship test. The unavailable Reddit corpus cannot be revalidated. A host-specific installation check and Andrew's approval of generated prose remain separate from local validation.

## Refuted

The inherited phrase "parentheses in half his paragraphs" misstates the earlier profile's comment-level presence statistic as a paragraph statistic. That prescription was removed. The new email sample records parenthetical material in six messages; it does not support a paragraph quota.

## 4.3.0: Clarity and the supplied tells catalog

This revision draws on two user-supplied sources reviewed locally on 7 November 2026: the `clarity-main.zip` archive (Clarity Agent Skill, `SKILL.md` metadata version 0.2.1, MIT License, Copyright (c) 2026 Addy Osmani) and a standalone `tells.md` editing catalog with no stated author or license. Clarity's runtime files, scripts, eval cases, judging protocol, samples, and browser-editor heuristics were read in full; its website build was not run. No network research was needed for these local changes, and no claim from either source was treated as validated evidence of an effect on writing quality.

Clarity's central claim is that generic model prose fails on substance before style, so it diagnoses missing source material first and treats familiar patterns as contextual prompts rather than bans. That matches this skill's existing meaning-first stance and fills four gaps: no ordered diagnosis, no review verdicts, no way to collect the author's own material, and no positive craft step after subtraction.

| Element | Decision | Where it lives now |
|---|---|---|
| Ordered diagnosis: truth and scope, substance, development, sentences, craft | Adopted | SKILL.md working method; the patterns reference |
| What each register owes (argument, explanation, update or guide, message, story) | Adopted, with founder-specific rows (founder post, investor update, outreach) | SKILL.md |
| Review format with keep, revise, ask-author, and cut verdicts | Adopted | `references/review.md` |
| Perspective interview, `[TK: question]` gaps, provenance note | Adapted: the full interview runs only on request, because Andrew's standing preference is to infer and proceed with at most one focused clarification; otherwise the skill drafts what is supported and marks TK gaps, or asks one question when the missing material is the piece | `references/interview.md` |
| Long-form craft: one-job openings, development, the author test, putting craft back, one pass then stop | Adopted, with Andrew's connected long sentences kept and rhetorical-question openings excluded | `references/longform.md` |
| Medium routing (docs, reference, academic, legal and safety, UI, talks, fiction) | Adopted | new sections in `references/voices.md` (talks and pitch scripts, UI copy, reference pages, financial and legal terms) |
| Flatten, relation, and emphasis tests; vague attribution; abstract actors; structural regularity; preserving human material | Adopted | the patterns reference and scanner rules |
| Rewrite check, including a pattern reproduced under new punctuation | Adopted and extended with `scripts/fidelity_check.py` | the delivery checklist |
| `prose_stats.py` and `strip_markdown.py` (no composite score) | Adapted into `scripts/prose_stats.py`: uses this skill's source masks, adds `--compare`, lexical diversity, repeated trigrams, and look-here lists for unsupported importance, kickers, and flourishes | `scripts/` |
| `validate_package.py` | Adapted into a generic validator for routes, budgets, eval schema, and manifests | `scripts/` |
| `evals/cases.json` and `evals/JUDGE.md` | Adapted: categories, prohibitions, hard gates, and blinded scoring | `references/test-cases.json` and `references/test-cases.md` |
| Browser-editor heuristics: Claude-frequency vocabulary cluster, extremes, importance without mechanism | Adopted as look-here lists only; the cluster reports only four or more distinct terms in 150 or more words | `scripts/prose_stats.py` |

The supplied tells catalog contributed the demonstrative kicker, meta throat-clearing, importance-flagging, decorative metaphor, grandiose prediction, correlative and hedged scaffolding, symmetrical hedging, definition openers, a plainer-word lexicon, the "could the author defend it" test, five ordered triage questions, and light versus heavy calibration. Three of its rules were softened to fit this skill's evidence stance: "delete puffery adverbs" became a triage question because degree and warmth can be real, "rhythm needs contrast" became an instruction to inspect uniformity without alternating lengths mechanically, and "vary list length" became "keep two when two is true, and three when three is true."

Rejected:

- Clarity's "prefer shorter words and sentences" as a blanket rule. Its own long-form reference keeps a long sentence when one subject carries the clauses, and that narrower rule is the one adopted. Breaking Andrew's causal chains into short sentences would contradict his voice profile.
- The browser editor's 0 to 100 surface-pattern score and readability grade. They contradict the no-score design and invite optimizing toward a number.
- A stacked-questions rule, which would flag legitimate multi-question support and coordination messages.
- Applying the larger excess-vocabulary list as violations. A small set joins the existing density-scored vocabulary check, which names a plainer choice and never affects the strict exit code.
- Copying Clarity's eighteen-rule essay, site, or command wrappers. The guidance here is rewritten for this skill, and modes are selected through the existing controls.

Clarity reports that a stylometric composite ranked a genuinely human control as the "riskiest" text in its exploratory corpus. That observation is the source's own and was not reproduced here; it is the reason both new scripts report descriptive measurements and lists rather than a score.

## Source merge for 4.4.0

Reviewed on 17 November 2026 from five archives Andrew supplied: plainspoken 0.13.0, humanizer 4.0.0, avoid-ai-writing 3.39.0, writing-quality 0.2.3, and unslop 2.3.0. Nothing from them was installed or executed. Version 4.3.0 already covered much of what they share, so this revision takes only what was missing: the candidate, finding, edit distinction and exact no-op rule; a working definition of a join; sentiment that speaks for the author as a new fact; the reply agenda and first-contact checks; habits a cleanup installs; rankings and same-time claims in the rewrite check; draft-artifact scanner checks; and new promises and causes in `fidelity_check.py`. Left out: authorship scores, stylometric targets, universal bans, blocking gates, cadence quotas, and any allowance to add facts. `validation.md` has the per-source table and `NOTICE.md` the licenses.
