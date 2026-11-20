# Video Prompt Director

Develop video prompts with explicit timing, camera direction, sound, and continuity across shots.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`video-prompts`](skills/video-prompts/SKILL.md). Try this prompt.

> Write three eight-second video prompts for a ceramic lamp launch. Give each a shot timeline and keep the product silhouette consistent.

Develop five complete video concepts by default, each with detailed scene and shot direction, timed action, camera choreography, continuity, sound, and copy-ready clip prompts. Covers text-to-video, image-to-video, reference media, first/last frames, narrative endpoints, keyframes, continuation, edits, loops, and longer sequences. Includes dated Grok and Google Omni guidance and a portable workflow for other models. Respects requested counts, duration, brevity, and single-shot requirements. Authors prompts and production plans; rendering and assembly use your chosen tools separately.

## Start

Install or enable this plugin in your plugin library, select it in chat, and describe the result you want. Include the target model or app, aspect ratio, references, and any must-preserve details you already know. A short brief is enough to begin; the workflow fills reasonable visual choices and labels material assumptions.

> Create five 12-second cinematic video prompt variations for a ceramic cup launch. Include scene timing and sound.

> Use reference A as the first frame and B as the last frame. Write five plausible motion bridges for Grok video.

> Write one continuous 8-second shot for Google Omni using this character reference. No dialogue. Keep the camera locked.

The default is **five creative variations total**. Request a different count, shorter output, one continuous shot, a narrow edit, or a specific format at any time. Each prompt is usable independently. Five variations are alternatives, rather than five images or shots generated automatically.

## Contents and operation

The portable `plugin.json` and `skills/video-prompts/SKILL.md` define a skills-only plugin. Supporting references live with the skill. There is no MCP server, API key, paid rendering integration, or background service to configure. The host assistant follows the workflow in chat. Actual generation, reference upload/assignment, clip editing, and final quality inspection happen in the model or production tools you select.

Model guidance is a source-reviewed snapshot dated **2026-10-27**. Check the exact model version and host surface before using technical controls or limits. The workflow can write portable prose without network tools; it does not claim a current capability when it cannot verify one. Prompt detail and continuity instructions are creative targets, and rendered results still need inspection.

## Review

`EVALUATION.md` records package checks and behavioral review, including the boundary between source checks and actual rendered-media validation. `PROVENANCE.md` explains the original design and source research. No external prompt library is required at runtime. The bundled `tests/acceptance-cases.json` and `tests/review-rubric.md` define future regression reviews.

The downloadable package in `artifacts/prompt-directors/` is built from this source, and `artifacts/prompt-directors/validate.py` checks that the two match. See `CHANGELOG.md` for what changed in each version.
