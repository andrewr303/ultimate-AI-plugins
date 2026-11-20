# Model adapters and source snapshot

Reviewed **2026-10-27**; GPT Image, Nano Banana and Gemini Omni identifiers rechecked 2026-11-10. These notes guide prompt writing; they are not a permanent capability registry. Check the exact model and UI/API surface against current official documentation before outputting technical fields, limits, supported input types, model IDs, or quality settings. A provider's app and its API may expose different controls.

## Portable behavior first

Use clear natural-language visual direction by default. Keep the copyable creative prompt separate from native settings and attachment instructions. Do not turn desired aspect ratio, high detail, transparency or reference fidelity into a claim of native support. Describe intent in the prompt, then give verified UI settings when available.

Do not add universal syntax such as weighted parentheses, `--ar`, a `negative_prompt` property, a seed, guidance scale, sampler, token limit or reference weight. Use such controls only when explicitly requested, actually supported by the chosen surface, and verified. If verification is unavailable, label the settings unverified or omit them and provide a complete portable prompt immediately.

If the user provides a model name you cannot verify, preserve their label. Say “portable prompt for [user's model label]; native controls unverified.” Do not invent a model ID, endpoint or capability, and do not silently substitute a different engine.

## GPT Image / GPT Image 2.5 and 2.6

The OpenAI image-generation guide, rechecked 2026-11-10, lists `gpt-image-2.6-sunburst` and `gpt-image-2.6-flare` and recommends them for new integrations; the 2.5 identifiers `gpt-image-2.5-sunburst` and `gpt-image-2.5-flare` are still documented. Sunburst is the editing-precision variant and Flare the faster everyday one. Treat these as a dated observation; a family-level prompt normally does not need an exact identifier, and when the user names 2.5 or 2.6, keep their label.

Write a recognizable artifact and subject, followed by precise composition, visible materials and constraints. Labeled sections are useful for complex briefs. Quote required words and specify their position and typography. Number supplied references and explain each role. For edits, separate requested changes from identity, geometry, layout and lettering that must survive.

OpenAI's guidance separates API parameters from prompt text and treats photographic specifications as appearance cues. Preserve that separation. Do not assume older model settings still apply. Real alpha output, output dimensions, quality and input controls must be checked on the selected surface.

Official sources:

- https://developers.openai.com/api/docs/guides/image-generation
- https://developers.openai.com/api/docs/guides/image-prompting

## Grok Imagine image

The reviewed xAI documentation lists `grok-imagine-image-2.0` for current still-image generation. Recheck at use time when an exact identifier is requested.

Lead with the actual subject, form, support and setting. State recognizable physical properties and counts before mood or surface styling. Then give art direction, readable lighting, subject/background colors, and composition. Keep texture attached to the correct object and avoid repeated decorative degradation cues. Use positive descriptions and a small relevant constraint list.

The default detailed treatment remains useful, but every paragraph must define the image. For a surgical edit, lead with the change and follow with preservation locks; do not restage a correct subject and layout through an unnecessarily long generation brief. Do not translate detailed authoring into unsupported control syntax.

Official sources:

- https://docs.x.ai/developers/model-capabilities/images/generation
- https://docs.x.ai/developers/model-capabilities/images/prompting-guide

## Google Gemini image / Nano Banana 2.1

The reviewed Google documentation lists Nano Banana 2.1 as `gemini-nano-banana-2.1`. Use the family name for normal prompt writing and recheck identifiers when technical output is requested.

State visual intent and context, exact materials and framing, and clear relationships between elements. Use readable instructions for complex compositions. Assign reference roles explicitly, preserve subject identity and requested text, and make follow-up edits specific. Phrase exclusions through a clear description of the intended scene where possible.

Do not assume that all Nano Banana variants support the same number or type of references, sequential edits, output sizes or grounding. Do not claim that image generation can process an unsupported input medium. If a user asks about Google Omni for still images, verify that particular surface rather than inferring still-output capability from video support.

Official source:

- https://aistudio.google.com/docs/image-generation (formerly ai.google.dev/gemini-api/docs/image-generation, a permanent redirect; checked 2026-11-10: `gemini-nano-banana-2.1` is the newest listed)

## Other engines and multi-model delivery

For FLUX, Stable Diffusion, Midjourney, Ideogram, Seedream, local engines and future models, provide portable natural language until the relevant official model/surface documentation is available. Preserve requested style and creative intent when adapting; only change syntax, input mapping or detail density when the target actually requires it.

If several models are requested, keep the default five creative alternatives total. Add short model-specific notes that apply to the set, or provide a compact adapter for a chosen variation. If independent per-model copy blocks are requested, repeat the full prompt rather than pointing to another model's block.

## Evidence boundary

OpenAI, xAI and Google independently support concrete visual description, explicit reference roles, requested change/preservation distinctions and deliberate iteration. Their documentation does not establish cross-provider feature equality or guarantee exact text, identity, transparency, geometric preservation, or deterministic output. This plugin's five-variation policy and output format are original design choices based on the user's requirements. No external prompts, code or assets are bundled.
