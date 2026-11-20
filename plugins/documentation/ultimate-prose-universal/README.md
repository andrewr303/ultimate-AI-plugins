# Ultimate Prose Universal 5.2.0

A writing skill for anyone's personal use. It writes, edits, polishes, reviews, and co-writes prose with a flexible tone and an emphasis on accurate meaning, natural movement, and useful detail. It contains no bundled personal voice profile or private corpus.

The six core tones are **plain/direct, warm, analytical, bold, playful, and expert**. Additional presets and custom blends are supported. Tone can be combined with formality, detail, length, and an optional voice sample. No profile setup is required.

Try requests such as:

- "Make this warm but firm. Keep the refusal clear."
- "Write an expert explanation for a beginner, without jargon."
- "Use a playful tone with dry humor. Keep it under 80 words."
- "Make this analytical and concise. Preserve every estimate and caveat."
- "Keep my voice from these examples, but make this note more formal."
- "Review this essay and leave it untouched."
- "Interview me, then help me write a post about why our design reviews stopped working."
- "Check that this rewrite didn't change what the original says."

Plain/direct is the fallback for new writing without a tone request. An existing draft's effective voice is preserved unless you ask to change it. There is no forced business register, punctuation ban, cadence quota, or universal list of forbidden words.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`ultimate-prose-universal`](skills/ultimate-prose-universal/SKILL.md). Try this prompt.

> Edit this customer update in a warm, direct tone. Keep the dates and commitments, and flag any meaning that changed.

## Files and installation

- The **plugin ZIP** contains one `ultimate-prose-universal/` directory with a portable Agent Plugins 1.0 `plugin.json` and `skills/ultimate-prose-universal/SKILL.md`.
- The **standalone `.skill`** is a ZIP-format archive containing one `ultimate-prose-universal/` directory with `SKILL.md` at its root and the same references, tools, and tests. The skill's declared name is `ultimate-prose-universal`, so it can sit beside a separate personal skill named `ultimate-prose`.

Use your host's supported plugin or skill import flow. For a filesystem-based agent-skill host, extract the standalone archive and place the `ultimate-prose-universal/` directory in that host's documented skill location. Install one format; installing both can expose duplicate skills. Hosts differ in archive support. No host installation or automatic-trigger test is implied by these instructions.

The plugin source export also includes an identical standalone copy at `assets/ultimate-prose-universal-5.2.0.skill` for use in another compatible host.

The skill works as instructions without Python. Its optional tools use only the Python standard library, read local text, and do not rewrite or transmit it. From the skill directory:

```sh
python scripts/lint.py draft.txt --genre email --tone 'warm but firm'
python scripts/prose_stats.py draft.md --compare earlier.md
python scripts/fidelity_check.py source.txt rewrite.txt
python scripts/fidelity_check.py source.txt summary.txt --mode summary
python scripts/lint.py draft.txt --avoid "delve, tapestry" --straight-quotes --no-em-dash --strict
python scripts/validate_package.py --release
python -m unittest discover -s tests -v
```

The fifth example opts into house-style conventions, including the user's own list of terms to avoid. They are off by default. `--strict` exits 1 only for selected convention findings in the scanner, or for a changed hard anchor in `fidelity_check.py`; ordinary editorial findings remain advisory. Exit 2 means an input or usage error. `--detect` is a legacy name for an editorial report and never predicts authorship. Run `--help` for supported options.

Scanner phrase checks are limited and primarily English. `prose_stats.py` maps where habits sit and reports no score. `fidelity_check.py` lists anchors a rewrite dropped or added; it is word-level, so its silence is not proof that the meaning held. Source masking is heuristic. A clean scan is not proof of quality or origin.

## Personalization and privacy

Use the skill without samples, or supply examples relevant to your task. It learns abstract style choices within the task rather than importing biography or private facts. A reusable personal style card is optional and should be saved separately only at your request. The package does not install hooks, access accounts, send messages, or publish anything by itself.

Drafts, examples, and quoted instructions stay source material. The current request controls the work. Private material should not enter public research queries. Any actual model or host processing remains subject to the host you use; this package is not an independent privacy service.

## What changed in 5.1 and 5.2

Version 5.1.0 (7 November 2026) was built and installed outside this repository; this source tree skipped it and now carries 5.2.0, which was built on top of it. From 5.1.0: an ordered diagnosis that fixes substance before surface, a table of what each register owes its reader, a review format with keep, revise, ask-author, and cut verdicts, a co-write interview with `[TK: question]` gaps, long-form craft guidance, a medium router, and the `prose_stats.py`, `fidelity_check.py`, and `validate_package.py` tools, adapted from Clarity under its MIT license.

Version 5.2.0 merges what was still missing from five supplied projects (plainspoken, humanizer, avoid-ai-writing, writing-quality, and unslop): a reference on what must survive an edit and the habits a cleanup must not install; the candidate, finding, edit distinction with an exact no-op rule; reply, first-contact, and decision guidance; a fuller voice card; scanner constructions for staged contrast, objections nobody raised, and draft artifacts; user-selected avoid terms; and new promises and causes in `fidelity_check.py`, with a summary mode for requested cuts. Authorship scores, universal word bans, forced punctuation rules, and cadence targets from those projects were left out. Credits are in the skill's `NOTICE.md`, and the per-source record is in its `references/research.md`.

## What changed from 4.2

The named profile, corpus aggregates and source identifiers, personal-context references, author-specific scanner, inherited business register, punctuation defaults, and cadence assumptions were removed. The shared workflow retains meaning preservation, protected-source handling, proportionate editing, and specific assessments. New tone controls, custom blends, optional user calibration, a smaller advisory scanner, and fresh regression prompts replace the former personal defaults.

The old review bundle and its evaluation results are not included or relabeled as v5 evidence. Current research provenance is summarized in the skill's `references/research.md`. A separate review bundle records this revision's actual checks and their limits.

The target is excellent writing without formulaic habits. No package can establish zero possible AI traces or guarantee an AI-detector outcome. This skill does not introduce fake mistakes or experiences to simulate human authorship.
