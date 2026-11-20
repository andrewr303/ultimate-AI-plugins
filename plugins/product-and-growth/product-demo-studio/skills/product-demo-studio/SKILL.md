---
name: product-demo-studio
description: "Use when producing a product demo video, organic launch clip, paid social creative, feature announcement, verified walkthrough or homepage loop that shows meaningful product behavior. Also use for purposeful campaign variants; do not activate for a live marketing site or unrelated video editing."
---

# Product Demo Studio

Produce an editable, rendered product film with a clear benefit, visible product action, defensible evidence and an appropriate next step. Complete the render and encoded-media review; a script or title animation alone is insufficient.

## Start

Resolve the installed plugin root from this skill. Read [execution](../../references/execution.md), run `python scripts/studio.py doctor`, and inspect the supplied product before asking for information. Apply [foundation](../../references/foundation.md) for a new product or changed evidence.

The bundled deterministic HTML/Playwright renderer is the primary local production path. Real-footage editing and optional engines use explicit adapters. Consult [renderer guidance](../../references/renderer.md); never silently drop narration, change the visual approach or substitute an unavailable engine.

## Route only the current work

| Need | Skill | Resource |
| --- | --- | --- |
| Audience, placement, ad matrix and meaningful variants | `pds-campaign` | [campaign](../../references/campaign.md) |
| Product discovery, verified workflow and capture | `pds-product-evidence` | [capture](../../references/capture.md) |
| Distinct hooks and defensible scripts | `pds-hooks-and-script` | [script](../../references/script.md) |
| Shot list, styleframes, pacing and recipe selection | `pds-storyboard` | [shot recipes](../../references/shot-recipes.md) |
| Faithful UI, pure frame motion, camera and cursor | `pds-ui-motion` | [motion](../../references/motion.md) |
| Narration, captions, music and mixing | `pds-audio-captions` | [audio](../../references/audio.md) |
| Preview, explicit adapter, render and reproducibility | `pds-render` | [renderer](../../references/renderer.md) |
| Encoded-media checks and visual/editorial repair | `pds-review` | [video QA](../../references/video-qa.md) |
| Final files, posters, copy and page handoff | `pds-delivery` | [delivery](../../references/delivery.md) |

Load one specialist and its relevant resource at a time. Search [the reference index](../../references/README.md); do not load the entire library.

## Complete the production

1. Define audience, awareness, problem/opportunity, single promise, demonstrating action, benefit, CTA and placement. Record claims, rights and visual modes.
2. Choose a story grammar and write a causal script. For ads, create a bounded experiment matrix with distinct hypotheses.
3. Capture the real product or build a faithful labeled replay from verified states. Inspect styleframes at intended viewing size.
4. Build frame-based motion and a low-cost moving preview. Repair missing action, unreadable proof and poor pacing before final renders.
5. Render selected compositions/variants. Inspect actual encoded frames, run technical QA, watch normal-speed motion when playback is available and distinguish audio measurements from listening.
6. Deliver source, final media, posters, captions, variant manifest, copy, source/configuration binding and honest limitations. Publish only when requested.

The synthetic Tandem fixture demonstrates local workflows with sample data. Replace its identity and claims for client work. See [ready prompts and evaluations](../../references/evaluation.md).
