# Validation scope: 5.2.0

## 5.2.0 checks

Revision 5.2.0 was checked on 18 November 2026 with Python 3.13 in a cloud workspace. It was built on the installed 5.1.0 package, not on the older 5.0.1 archive.

- `python -m unittest discover -s tests -v`: **32 tests passed**. The 24 tests from 5.1.0 are unchanged. Five new scanner tests cover each added construction beside an ordinary counterexample that must stay clean; contrast frames reported only on repetition; draft artifacts read through quotations and links but never code; front matter, HTML comments, and ignore regions; and label echo with user-selected avoid terms under `--strict`. Three new shared-tool tests cover quiet same-family swaps with reported net changes, new promises and causes, and `--mode summary`.
- `python scripts/validate_package.py --release`: passed. SKILL.md is 2,474 words against a 2,500-word budget; SKILL.md plus its 11 routed references is within the 18,000-word budget; the 50 eval cases have unique ids, and the 26 categorized cases cover all six required categories with prohibitions.
- Self-scan: the scanner's default checks report nothing on the repository documents used as ordinary-prose controls or on two of the source projects' README files. That is a small false-positive screen, not a measured rate.
- One behavior change in `fidelity_check.py` is deliberate: a swap inside one family ("may" to "might", "about" to "roughly") no longer prints a dropped and an added line. A net loss or gain in the family still does.

Not run for 5.2.0: a model-generated run of the twelve new behavioral cases, a baseline comparison, a host import, and any detector trial. Until `evaluation-protocol.md` is run, no behavioral improvement is claimed; the supportable claim is that the tools behave as their tests state.

Known limits of the additions: `fidelity_check.py` remains word-level and English-centred, so a claim invented in plain words passes untouched; the commitment and causation families report only additions; the new scanner constructions are a short English list and their silence proves nothing.

## 5.1.0 checks

Revision 5.1.0 was checked on 7 November 2026 (America/Denver) with Python 3.13 in a cloud workspace.

- `python -m unittest discover -s tests -v`: **24 tests passed**. The 10 earlier scanner tests are unchanged. Two new scanner tests cover vague attribution, abstract actors, and leaked assistant framing (with citation, link, quotation, and measured-result exceptions) and three earned devices that must produce no findings. Twelve shared-tool tests cover `fidelity_check.py`, `prose_stats.py`, and the package validator.
- `python scripts/validate_package.py --release`: passed. SKILL.md is 2,237 words against a 2,500-word budget; SKILL.md plus its 10 routed references is 11,379 words against 18,000; the 38 eval cases have unique ids, the 14 categorized cases cover all six required categories with prohibitions, and all three plugin manifests carry 5.1.0.
- Scanner comparison on Clarity's sample pairs (`--genre essay`): the 5.0.1 scanner reported no candidates on either "before" essay; 5.1 reports 1 and 2 (vague attribution and an abstract actor) and none on the "after" versions. The descriptive map in `prose_stats.py` lists the larger set of habits on those essays without turning them into findings, which keeps the no-banned-vocabulary design.
- Prose in the new and changed references was scanned with a linter configured for straight quotes and no dashes; flagged wording was revised where it was the author's choice rather than a quoted example.

Not run for 5.1.0: a model-generated comparison of the fourteen new behavioral cases, a host import, and any detector trial. `evaluation-protocol.md` defines how to run that comparison; until it runs, no behavioral improvement is claimed.

## 5.0.1 record

This release generalized the supplied 4.2.0 skill. Historical corpus analysis, old research, and prior-version evaluation results are not evidence for that revision and are not bundled.

### Scanner checks

The original neutral scanner and its tests use the Python standard library. Ten unittest test methods cover contextual signals, nonfindings for ordinary vocabulary and typography, quoted/code/technical source protection, Unicode and CRLF offsets, no matching across masks, repeated framing and adjacent duplication, explicit strict conventions, read-only file behavior, stdin/JSON/report interfaces, and usage/read/UTF-8 errors. The release review bundle records the execution output and archive verification.

These tests validate the scanner's limited contract, not natural writing quality. Source masking and sentence approximation remain heuristic. Tone and genre are metadata; the scanner does not judge them. It has no network or rewrite behavior.

### Generated writing smoke review

Twenty-four synthetic prompts were given to one separate generation agent applying the candidate skill and relevant references. The generator saw the prompts, but not the grading expectations. Another agent reviewed the saved outputs against the expectations. All 24 were judged to meet the scoped checks, with no failed cases.

Cases cover the six core tones over one factual brief; warm refusal; bold uncertainty; custom and formal blends; exact preservation of already-good prose and technical literals; assessment-only output; embedded source commands; flow without invented causation; sample privacy; expert explanation; requested fiction; Spanish warmth; condolence; a code-only negative case; a genuine contrast with no defect; requested alternatives; and diagnostic/minimum-outcome distinctions. Literal-preservation, exclusion, exact-text, and explicit word-limit checks also passed. A source reviewer found minor drift in the tone guide's shared-fact examples; those examples were corrected before packaging.

The six short tone variants were distinguishable, with appropriately modest differences between analytical and expert. This is a single-generator, model-assisted smoke review, with no no-skill baseline, human preference panel, target-host installation, or detector trial. It does not establish a measured improvement, universal quality, or complete absence of AI-associated patterns. Example outputs are evidence for the cases only, not a personal voice corpus.

### Packaging and source checks

Release checks parse JSON/YAML/Python, validate the declared portable manifest and skill contracts, resolve local references, compare the standalone skill with the plugin skill, inspect archive paths and file types, exclude caches and unrelated source evidence, and run the scanner tests from a fresh extracted archive. A targeted scan checks that supplied personal names, profile/corpus files, private-source hashes, source identifiers, and the personal scanner are absent. The separate review bundle records final results.

The available Codex CLI has plugin installation commands but no standalone package-validation command. Structural checks therefore do not establish host import or implicit activation. No plugin is sent or published by the writing skill itself.

### Research limits

The separate manual research records pin repositories and changed files within 19 September–19 October 2026. Exact repository metadata remains a primary-source observation; manually supported design observations are corroborated across independent authors. No automated research-gate PASS is claimed. Maintainer benchmarks were not rerun, and no external candidate code was executed.
