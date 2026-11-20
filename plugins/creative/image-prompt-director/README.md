# Image Prompt Director

Develop image prompts with specific direction for composition, lighting, text, and how to use references.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`image-prompts`](skills/image-prompts/SKILL.md). Try this prompt.

> Write five launch-image prompts for a handmade ceramic lamp. Keep the silhouette in the reference, vary the lighting, and frame each prompt for a 4:5 crop.

Turn a brief into five fully developed image prompt variations by default. Direct composition, subjects, materials, lighting, color, exact text, and reference fidelity. Supports new images, edits, inpainting, outpainting, transparent assets, product and character consistency, and coordinated series. Includes dated guidance for GPT Image 2.5 and 2.6, Grok Imagine, Nano Banana 2.1, and a portable workflow for other models. Respects requested counts and brevity. Authors prompts; rendering uses your chosen model separately.

## Start

Install or enable this plugin in your plugin library, select it in chat, and describe the result you want. Include the target model or app, aspect ratio, references, and any must-preserve details you already know. A short brief is enough to begin; the workflow fills reasonable visual choices and labels material assumptions.

> Create five detailed product-image prompts for a sage-green ceramic espresso cup on limestone. Use Nano Banana 2.1.

> Use reference A for product shape and B for the palette. Create five launch-poster prompts. Exact headline: FIRST LIGHT.

> Revise variation 3 only: replace the background with transparent alpha. Preserve the product, angle, and lighting.

The default is **five creative variations total**. Request a different count, shorter output, one continuous shot, a narrow edit, or a specific format at any time. Each prompt is usable independently. Five variations are alternatives, rather than five images or shots generated automatically.

## Contents and operation

The portable `plugin.json` and `skills/image-prompts/SKILL.md` define a skills-only plugin. Supporting references live with the skill. There is no MCP server, API key, paid rendering integration, or background service to configure. The host assistant follows the workflow in chat. Actual generation, reference upload/assignment, clip editing, and final quality inspection happen in the model or production tools you select.

Model guidance is a source-reviewed snapshot dated **2026-10-27**. Check the exact model version and host surface before using technical controls or limits. The workflow can write portable prose without network tools; it does not claim a current capability when it cannot verify one. Prompt detail and continuity instructions are creative targets, and rendered results still need inspection.

## Review

`EVALUATION.md` records package checks and behavioral review, including the boundary between source checks and actual rendered-media validation. `PROVENANCE.md` explains the original design and source research. No external prompt library is required at runtime. The bundled `tests/acceptance-cases.json` and `tests/review-rubric.md` define future regression reviews.

The downloadable package in `artifacts/prompt-directors/` is built from this source, and `artifacts/prompt-directors/validate.py` checks that the two match. See `CHANGELOG.md` for what changed in each version.
