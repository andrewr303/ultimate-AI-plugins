# Design provenance

This plugin is an original instruction package. Its default of five alternatives, detailed image direction, and expanded scene-by-scene video direction comes from the creator's requirements. No repository prompt text, implementation, example images, assets, model weights, or dependencies are bundled or required.

## Source-reviewed design decisions

Research compared independent public prompt and skill implementations, inspected pinned source files, and cross-checked shared practices against official provider documentation. Review was manual; no automated research-verification result or upstream test success is claimed. Repository license observations were not used as legal clearance because no source material is copied.

The following links document abstract design ideas considered during research, rather than runtime dependencies or endorsements:

- Visual dimensions and preservation: [wuyoscar source at inspected commit](https://raw.githubusercontent.com/wuyoscar/GPT-Image2-Skill/9f8aa1a44a4a5c0f5a5d6e45eed564b3e2d5b87f/skills/get-prompt-from-image/SKILL.md). The implementation here uses fresh instructions tailored to this plugin.
- Change boundaries in edits: [Hunyuan-PromptEnhancer source at inspected commit](https://raw.githubusercontent.com/Hunyuan-PromptEnhancer/PromptEnhancer/add1f59fd9883e02df5aba41c11f873e01729184/inference/prompt_enhancer_img2img.py). The implementation here uses fresh instructions tailored to this plugin.

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
