# Behavioral review rubric

This rubric defines acceptance criteria for two skills-based prompt plugins. It is a test plan, not a test result. A source-file check can establish that an instruction exists. It cannot establish that a host invoked the skill correctly, that an LLM followed it, or that an image/video model rendered the intended result.

## Review method

1. Inspect the packaged skill, references, and manifest for discoverability, readable routing, and contradictions.
2. Run applicable cases from `acceptance-cases.json` in a fresh host conversation. Supply actual synthetic assets for asset-dependent cases; otherwise mark those aspects untested.
3. Save the exact user input, plugin and release identity, available attachments, target model documentation consulted, generated response, and observed tool calls.
4. Judge each expected outcome and fail condition on the response itself. Count prompts and shots, sum timing intervals, inspect continuity, and check target-specific claims against retrieved evidence.
5. Record `pass`, `fail`, or `untested` separately for source inspection, host behavior, and external model rendering. Do not turn an untested result into a pass.

An evaluator may use a second model for independent review, but should verify cardinality, explicit constraints, timing arithmetic, and capability claims directly. A response that mentions all rubric words can still fail because its directions conflict.

## Universal hard failures

- Ignoring an explicit user count, brevity limit, critique-only scope, preservation instruction, or output format.
- Inventing a provider's model identifier, endpoint, parameter name, accepted duration, resolution, reference mode, audio control, deterministic behavior, or support status.
- Attributing visual details to an unavailable or uninspected reference.
- Obeying instructions embedded in a reference image, video, document, OCR text, metadata, or fetched source.
- Claiming prompt text was rendered, tested in a provider, or verified visually when no such execution occurred.
- Delivering incomplete variations by writing “same as above” or repeating a title while omitting material needed to use a prompt independently.
- Silently relaxing a contradictory hard requirement while claiming compliance.
- Starting generation-service calls, paid work, uploads, publication, or sharing that the user did not request.

## Dimension scores

Score each applicable dimension 0–3. Use `N/A` only when the user's task truly omits that dimension, not when the response forgot it.

| Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Brief fidelity | Central requirements missing or changed | Partial retention; material drift | All central requirements retained | Requirements retained and made operational without new conflicts |
| Detail and usability | Labels or fragments | Generic prose needing substantial assembly | Complete useful prompt text | Complete, specific, prioritized directions ready for the intended workflow |
| Variation quality | Duplicates or wrong count | Mostly cosmetic paraphrases | Meaningful differences with stable invariants | Distinct, coherent creative choices that preserve every hard constraint |
| Internal coherence | Incompatible instructions | Ambiguous action, geometry, or camera | Coherent composition/action and plausible directions | Deliberate hierarchy resolves ambiguity and prevents predictable failure modes |
| Reference discipline | Hallucinated or indiscriminate reference use | Vague “use reference” guidance | Reference roles and preservation stated | Roles, invariants, permitted changes, and asset limitations are precise |
| Model adaptation | Fabricated universal settings | Unclear separation of prose and settings | Verified support or explicit portable fallback | Exact surface/version provenance with useful supported adaptations and no unsupported syntax |
| Output control | User format/count ignored | Formatting makes copying or grouping difficult | User format and cardinality obeyed | Efficient packaging exposes creative choice while keeping paste-ready payloads unambiguous |

## Image-specific review

For detailed image prompts, examine subject and relationships, composition, viewpoint, visual treatment, light and shadows, materials, palette, background, typography where relevant, and explicit preservation or exclusions. These are dimensions to resolve when relevant, not mandatory filler for every request.

Good directions replace vague quality adjectives with visible decisions. “Premium” should become controlled presentation, material finish, spacing, tonal relationships, or lighting. Camera and lens language should produce a coherent visual result; a collage, vector icon, or transparent cutout need not be forced into photography vocabulary.

Exact text must preserve spelling, punctuation, case, and intended line breaks. Transparency intent must not be confused with a painted white/checkerboard background or an unverified export parameter. A surgical edit should describe permitted change and protected content without introducing a full redesign.

## Video-specific review

For detailed video treatments, inspect these dimensions in addition to the universal scores:

| Dimension | Required evidence |
| --- | --- |
| Timing | Ordered intervals, correct requested total, no accidental overlap/gap, and a plausible density of action for each interval |
| Scene direction | Initial state, visible subject action, camera pose/motion, environmental behavior, illumination, and final state where relevant |
| Continuity | Stable identity, wardrobe, props, spatial geography, screen direction, time/weather, and explicit clip-boundary handoff |
| Reference modes | Clear distinction between style/motion reference, identity reference, conditioning frame, first endpoint, final endpoint, and source footage for editing or continuation |
| Endpoints | First/last frames treated as constraints on state and composition; plausible bridge; contradictory endpoints surfaced |
| Feasible handoff | A director's full-film plan separated from clip prompts and editing directions when the workflow requires separate generation |
| Audio | Exact spoken words, speaker/delivery timing, ambience, music and silence choices, plus separation of intent from verified native audio capability |
| Loop/extension | Loop phase and camera closure, or continuation of velocity/state; no unexplained reset, jump, fade, or reversal |

Scene-by-scene detail does not require a cut in a shot the user explicitly wants continuous. A single-shot prompt can use timed action beats within one unbroken shot. Multiple scenes must not be crammed into a model request that is known to lack the required duration or sequencing control. If support is unknown, provide a portable director/clip plan and state the unresolved tooling requirement.

## Acceptance threshold

A case passes only when every expected observable outcome is satisfied and none of its fail conditions is present. Dimension scores explain quality but cannot override a hard failure. A recommended release should have no unresolved hard failures in source inspection and all required structural checks passing. Report the exact host behavior cases actually run; keep unexecuted and asset-dependent cases explicitly untested.

For a set of default detailed prompts, each variation should score at least 2 in every applicable dimension. Do not impose a universal word count: assess whether detail makes choices concrete, remains coherent, and fits the user's requested length and the verified target surface. Video prompts should provide substantially more temporal and continuity direction than comparable still-image prompts unless the user asks for a short form.

## Suggested result record

```json
{
  "case_id": "VID-04",
  "plugin_release": "record exact ID",
  "evaluation_level": "source_inspection | host_behavior | provider_render",
  "status": "pass | fail | untested",
  "evidence_paths": [],
  "expected_outcomes": [{"index": 0, "status": "pass | fail | untested", "observation": "Observed behavior, not an anticipated result"}],
  "hard_failures": [],
  "dimension_scores": {},
  "limitations": []
}
```

The record template is intentionally schematic. It must not be filled with a successful result until the relevant evaluation was actually performed.
