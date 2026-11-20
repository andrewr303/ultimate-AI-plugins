# Ultimate Prose 4.5.0

Edit emails, posts, and longer drafts in Andrew Rodriguez’s voice. The bundled profile covers professional and casual writing. Use [Ultimate Prose Universal](../ultimate-prose-universal/README.md) to choose a different tone or calibrate to another author.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`ultimate-prose`](skills/ultimate-prose/SKILL.md). Try this prompt.

> Polish this project update in Andrew’s professional register. Keep every commitment and date, and flag any detail I need to verify before sending.

## Editing workflow

A standalone writing skill for Andrew Rodriguez. The editing workflow includes an ordered diagnosis that fixes substance before surface, a table of what each register owes the reader, a review format with keep, revise, ask-author, and cut verdicts, `[TK: question]` gaps instead of invented detail, an opt-in co-write interview, and a craft pass that restores evidence and warmth after cuts. The 4.2 profile, personalization boundaries, and channel guidance carry over, with new sections for talks and pitch scripts, UI copy, reference pages, and financial or legal terms.

Version 4.5.0 tunes the voice to a larger sample of Andrew's writing: 85 sent emails for the professional register and 93 posts on X for the casual one. The profile now describes both registers from measured habits (answer-first quick replies, the constant sign-off, calibrated confidence, a first-person closing line in casual replies), and `lint_andrew.py` was recalibrated so it reports departures from those habits and stops flagging the habits themselves. The samples are not in the package; [`references/corpus-notes.md`](skills/ultimate-prose/references/corpus-notes.md) records the counts and limits.

Version 4.4.0 merges the missing pieces from five further supplied projects (plainspoken, humanizer, avoid-ai-writing, writing-quality, unslop): [`references/preservation.md`](skills/ultimate-prose/references/preservation.md) on what must survive an edit and the habits a cleanup must not install, the candidate, finding, edit distinction with an exact no-op rule, reply and first-contact guidance, the rest of Andrew's stated avoid list, scanner checks for draft artifacts and contrast staged across sentences, and new promises and causes in `fidelity_check.py` with a `--mode summary` for requested cuts.

The `.skill` archive contains one `ultimate-prose/` directory with `SKILL.md`, references, standard-library Python tools, and regression tests. Import it through a host that supports this standalone skill format, or extract the directory into that host's skill location. No external account, network access, package installation, or background service is required. A host import was not performed during this revision.

From the [standalone skill directory](skills/ultimate-prose), run these commands with Python.

```sh
python scripts/lint.py draft.txt --genre email
python scripts/lint_andrew.py draft.txt --genre email --formality business
python scripts/lint.py draft.txt --genre x --detect
python scripts/prose_stats.py draft.md --compare original.md
python scripts/fidelity_check.py original.txt draft.txt
python scripts/fidelity_check.py original.txt summary.txt --mode summary
python scripts/validate_package.py --release
python -m unittest discover -s tests -v
```

The two linters report contextual review candidates, now including unsupported importance, vague attribution, abstract actors, demonstrative kickers, decorative metaphors, and plainer-word suggestions; whole-document measurements are labelled as such instead of pointing at line 1. `prose_stats.py` maps where habits sit, with no composite score, and is most useful for comparing two versions of one piece. `fidelity_check.py` lists the numbers, names, dates, links, quotes, code, negation, hedges, attributions, and conditions that a rewrite dropped or added. `validate_package.py` checks routes, the SKILL.md word budget, the eval schema, and Python syntax.

Use `--json` for structured output. Editorial findings exit 0. `--strict` makes selected formatting and register conventions affect the linters' exit status, and makes `fidelity_check.py` exit 1 when a number, date, link, quote, code span, name, or negation changed; it does not turn any tool into a quality gate or authorship detector. Read each tool's `--help` for its flags.

The attached CSVs and private messages are not embedded. [`references/corpus-notes.md`](skills/ultimate-prose/references/corpus-notes.md) records aggregates and provenance, [`references/research.md`](skills/ultimate-prose/references/research.md) records design provenance, [`references/test-cases.md`](skills/ultimate-prose/references/test-cases.md) describes the behavioral cases and the judging protocol, [`references/validation.md`](skills/ultimate-prose/references/validation.md) states the checks performed, and `NOTICE.md` carries Clarity's MIT license for adapted material.
