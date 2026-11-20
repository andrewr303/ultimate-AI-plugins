# Design provenance

This plugin is an original instruction package. Its default of five alternatives, detailed image direction, and expanded scene-by-scene video direction comes from the creator's requirements. No repository prompt text, implementation, example images, assets, model weights, or dependencies are bundled or required.

## Source-reviewed design decisions

Research compared independent public prompt and skill implementations, inspected pinned source files, and cross-checked shared practices against official provider documentation. Review was manual; no automated research-verification result or upstream test success is claimed. Repository license observations were not used as legal clearance because no source material is copied.

The following links document abstract design ideas considered during research, rather than runtime dependencies or endorsements:

- Frame roles and reference authority: [CyberJ0605 source at inspected commit](https://raw.githubusercontent.com/CyberJ0605/cinematic-video-prompt-engineer-skill/2c05089f5704339de544554c4d1bd810177cdd9a/cinematic-video-prompt-engineer/references/multimodal_reference_roles.md). The implementation here uses fresh instructions tailored to this plugin.
- Shot continuity and continuation: [CyberJ0605 source at inspected commit](https://raw.githubusercontent.com/CyberJ0605/cinematic-video-prompt-engineer-skill/2c05089f5704339de544554c4d1bd810177cdd9a/cinematic-video-prompt-engineer/references/continuation_workflow.md). The implementation here uses fresh instructions tailored to this plugin.
- Scene-by-scene narrative organization: [jnMetaCode source at inspected commit](https://raw.githubusercontent.com/jnMetaCode/ai-shortfilm-prompts/d196a96d581c403cda78fc8f09a6e38f887e09e2/skills/shortfilm-prompt/SKILL.md). The implementation here uses fresh instructions tailored to this plugin.

## Provider guidance

The model-adapter references contain official source links and the snapshot date. Current model-specific observations are primary-source guidance, rather than independently corroborated guarantees. General practices—clear subject direction, role-labeled references, change/preserve edits, and separation of settings from prose—are supported across independent provider documentation.

- [OpenAI image prompting](https://developers.openai.com/api/docs/guides/image-prompting)
- [xAI image prompting](https://docs.x.ai/developers/model-capabilities/images/prompting-guide)
- [Google image generation](https://aistudio.google.com/docs/image-generation)
- [Google Omni video direction](https://aistudio.google.com/docs/omni)
- [xAI reference-to-video](https://docs.x.ai/developers/model-capabilities/video/reference-to-video)

## Unresolved

Model capabilities, supported settings, reference limits, regional access, and exact version availability can change. Recheck the chosen surface when technical controls are needed. Prompt text alone does not establish deterministic identity, timing, exact typography, seamless loops, or rendered-media quality.

## Refuted

No refuted external assertion is used to implement this plugin. Provider-specific syntax and hard limits are not treated as universal.
