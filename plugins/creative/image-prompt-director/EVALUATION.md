# Release evaluation — 1.0.0

Reviewed 2026-10-27.

## Structural checks

The root manifest was parsed and validated against the official Agent Plugins 1.0.0 schema. Skill and agent YAML parsed successfully. Skill discovery location/name, semantic version, listing lengths, starter prompts, contained file paths and every Markdown reference were checked. No missing local reference, unwanted dependency directory or symlink was found. The final archive is checked against the source inventory before account upload.

## Independent source review

All twelve image cases and three shared cases in `tests/acceptance-cases.json` have explicit support in the inspected instructions and references. No unresolved source finding remained. This establishes instruction coverage, not model compliance. The worked example contains five complete original prompts and a scoped follow-up edit.

## Simulated skill invocations

A separate assistant read the local skill and applicable references and wrote actual response files for two requests. The primary reviewer inspected the responses and independently measured their fenced prompt blocks:

- Sparse tea-set brief: five complete prompts, with 342, 354, 362, 369 and 376 whitespace-separated words. Each retained the ceramic set and rainy morning while changing deliberate visual choices.
- Explicit two-prompt desert-bicycle brief: exactly two prompts, 52 and 53 words, with no preamble; both met the requested sixty-word maximum.

No authoring issue was found in those saved samples. These are **simulated skill invocations**, not installed-host activation tests. They do not prove the behavior of every model or host.

## Remaining validation

No provider request or rendered image was produced. Reference-dependent cases have source coverage; their synthetic asset descriptions are test specifications, not uploaded media. Actual attachment handling, model acceptance, image fidelity, typography and alpha output require separate host/provider testing. Use `tests/review-rubric.md` for future reviews and record unexecuted cases as untested.
