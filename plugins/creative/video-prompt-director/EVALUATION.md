# Release evaluation — 1.0.0

Reviewed 2026-10-27.

## Structural checks

The root manifest was parsed and validated against the official Agent Plugins 1.0.0 schema. Skill and agent YAML parsed successfully. Skill discovery location/name, semantic version, listing lengths, starter prompts, contained file paths and every Markdown reference were checked. No missing local reference, unwanted dependency directory or symlink was found. The final archive is checked against the source inventory before account upload.

## Independent source review

All fourteen video cases and three shared cases in `tests/acceptance-cases.json` have explicit support in the inspected instructions and references. One count ambiguity was corrected: the default applies per separate brief, while several target models for one brief do not multiply concepts. No unresolved source finding remained. This establishes instruction coverage, not model compliance. The complete worked example intentionally uses an explicit one-variation override.

## Simulated skill invocations

A separate assistant read the local skill and applicable references and wrote actual response files for two requests. The primary reviewer inspected every variation and independently checked count, hard-lock coverage and timeline arithmetic:

- Twelve-second cobalt-blue water-bottle launch film, no text or dialogue: five complete detailed variations, each with three independent shot payloads. Every timeline uses 0–4, 4–8 and 8–12 seconds, totaling twelve seconds. The treatments include subject/material continuity, camera and action beats, lighting, sound intent and editorial handoff. Every shot preserves the blue reusable bottle on wet black stone.
- Explicit one-shot kite brief: one continuous eight-second prompt, 114 whitespace-separated words, no preamble, meeting the requested 150-word maximum.

No authoring issue was found in those saved samples. These are **simulated skill invocations**, not installed-host activation tests. They do not establish deterministic timing, consistency or behavior of every model or host.

## Remaining validation

No provider request or rendered video was produced. Reference-dependent cases have source coverage; their synthetic asset descriptions are test specifications, not uploaded media. Actual attachment handling, frame pinning, keyframes, extension, audio capability, model acceptance and rendered continuity require separate host/provider testing. Use `tests/review-rubric.md` for future reviews and record unexecuted cases as untested.
