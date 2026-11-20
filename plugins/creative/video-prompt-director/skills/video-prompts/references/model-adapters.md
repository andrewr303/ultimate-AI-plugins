# Model adapters and source notes

Official guidance was inspected on **2026-10-27**. These notes are a dated authoring snapshot, not a guarantee of model availability, native controls, input allowances, regional access or output fidelity. Recheck the exact selected model **and UI/API/third-party host** when emitting native syntax. If documentation cannot be checked, use natural-language creative prompts and label technical support unverified. Do not interrupt ordinary creative writing merely to enumerate optional settings.

## Portable baseline

Put subject, action and setting first, then camera/framing, light, materials, progression, audio and essential preservation. Use readable structured prose. Timecode instructions express the intended sequence; they do not guarantee exact frame timing. Keep the full director treatment available while fitting each actual model input: preserve hard locks, core story/action, reference/end states, camera, then supporting style. Remove redundancy before detail that controls identity or meaning.

Keep aspect ratio, duration, resolution, frame rate, seed, native audio switches, attached media and frame-pin assignment outside the prompt unless the user asks for a verified technical request. A creative request for a format or look is not proof of a native setting. No universal negative field exists: prefer positive description and a few essential exclusions in ordinary prose unless a dedicated supported field is verified.

## Google Gemini Omni / Google video

The inspected Gemini API docs name **Gemini Omni Flash**, with the identifier `gemini-omni-1.2-flash` (rechecked 2026-11-10; `gemini-omni-1.1-flash` stays available until 2026-12-03, after which requests to it are routed to 1.2 Flash). The same page documents text-to-video, image-to-video, subject references, first/last-image interpolation, conversational edits and extensions. These facts belong to that specific documented surface; another host may expose a subset.

Write detailed scene, camera, subject-motion, light and sound direction. For first/last interpolation, explicitly assign the actual starting and ending images in order and describe how the scene connects them. Do not treat arbitrary style references as pinned frames. For reference clips, state the intended likeness/motion authority and verify how the selected interface interprets them; do not assume their audio transfers.

For native conversational edits, a precise change-and-preserve instruction can be much shorter than an initial treatment. For extension, prompt-local zero begins at the added section, not the beginning of the source clip; keep full-sequence timing in the editorial plan. Source retention, tail-frame alteration and uploaded/generated-source restrictions require a current check before making promises.

The inspected limitations explicitly say **uploaded audio references are unsupported**, audio in video references is ignored, and there is no dedicated negative-prompt control. Do not infer these features from broad multimodal marketing language. Audio generation and arbitrary audio-reference upload are different capabilities. Exact voice editing, multi-video reasoning, upload lengths, reference counts and regional constraints must be checked rather than guessed.

The current Gemini API video overview redirects new video work toward Omni and describes the retirement of its Veo Preview surface. This does not mean Veo is unavailable everywhere. Google enterprise/Vertex-derived surfaces have their own models and controls. Ask which surface only if that changes a technical handoff; otherwise write portable direction.

Sources checked:

- [Google video overview](https://ai.google.dev/gemini-api/docs/video)
- [Gemini Omni generation, editing, interpolation and prompt guide](https://aistudio.google.com/docs/omni)
- [Google enterprise video prompt guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide)

## Grok / xAI Imagine video

Inspected main generation docs name `grok-imagine-video-1.5` and a lite variant; other modes retain different model requirements. Use the human-friendly family in creative output unless an exact identifier is needed and verified. A single latest model ID must not be applied to every workflow automatically.

Separate image-to-video from reference-to-video. A reference can guide a person, product, wardrobe or environment without fixing the opening frame. Give each reference one clear role, keep actor/product positions explicit and prevent unrelated attributes from leaking between inputs. The inspected reference docs describe actual first-frame, last-frame and interior-keyframe controls for a supported 1.5 mode. An exact closing pin is not the same as asking a reference-conditioned clip to resemble an image.

The documented prompt reference tokens begin at `<IMAGE_0>` for the first reference, but **an actual pinned first image occupies that initial slot and shifts subsequent reference indices**. Use these tokens only after verifying the selected mode and actual input ordering. Include a clear mapping outside the prompt. Do not let a fixed token example silently point at the wrong asset. Voice reference modes have their own token/order and access rules; do not invent arbitrary audio upload support.

The dedicated extension page inspected here specifies the classic `grok-imagine-video` mode and treats duration as the **added section**, while main generation documentation discusses 1.5. Its extension output controls differ from fresh generation. Verify the dedicated mode page before outputting model IDs or settings. Do not extrapolate resolution/aspect controls from ordinary generation to extension.

Sources checked:

- [xAI video generation](https://docs.x.ai/developers/model-capabilities/video/generation)
- [xAI reference, first/last frames and keyframes](https://docs.x.ai/developers/model-capabilities/video/reference-to-video)
- [xAI video extension](https://docs.x.ai/developers/model-capabilities/video/extension)

## OpenAI video and other engines

Use the portable director pack unless the current official video model and exact surface have been checked. The user's mention of **GPT Image 2.5 or 2.6** describes an image family; it does not establish that the same model accepts video generation. It can inform separately prepared storyboard/endpoint stills when the user wants that step. Similarly, **Nano Banana 2.1** is an image-family option in the inspected Google image docs, not evidence that an image endpoint generates motion.

For Kling, Runway, Luma, Seedance, Wan, Hunyuan, local pipelines or a future model, preserve the same creative specification and research only the necessary adapter details. Do not fabricate an alias, numeric cap, weighting syntax, camera token, native multishot mode, first/last field or seed. If the surface only accepts a short clip, provide individual clip prompts and an assembly plan. If the surface lacks a required reference feature, label a fallback and its tradeoff rather than promising equivalent fidelity.

Image preparation sources checked:

- [OpenAI image generation](https://developers.openai.com/api/docs/guides/image-generation)
- [OpenAI image prompting](https://developers.openai.com/api/docs/guides/image-prompting)
- [Google image generation / Nano Banana](https://ai.google.dev/gemini-api/docs/image-generation)

## Research provenance and limits

The original workflow adopts abstract practices—role-labeled references, per-shot structure, continuity anchors and scoped evaluation—after source review of independently authored prompt/agent repositories and official provider guidance. No upstream source code, prompt examples, assets, model weights or dependencies are included. The user requirement determines the five-variation default and the high-detail contract.

Provider pages establish what their own docs currently say. They do not independently establish comparative quality, legal rights, exact reproducibility or a cross-provider feature guarantee. No media rendering was performed as part of this guidance. Never turn a source-observed capability into a claim that a particular generated result was tested or will be exact.
