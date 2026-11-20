# Native and accessible motion research

Manual source review for the platform-motion-wizard build. No automated research gate was configured or claimed. This arm supplements the main repository discovery report; it is not a separate recommendation shortlist.

## Supported synthesis

- Support system preferences and remove or replace nonessential movement while preserving the task. Independently supported by W3C guidance and MDN preference documentation. [native_src_001, native_src_002; native_clm_001]
- Treat visual disappearance separately from interactive and accessible removal. W3C modal guidance requires controlled focus and inert background; Android's Compose guide explicitly warns that alpha does not remove a composable. This engineering synthesis informed the exit lifecycle checks. [native_src_004, native_src_011; native_clm_002]
- Inspect whether a preference API actually subscribes to changes. React Native documents a live preference event; Software Mansion separately documents a startup snapshot hook. This comparison informs the policy to test live changes rather than infer reactivity from an API name. [native_src_005, native_src_006; native_clm_003]

## Original implementation decisions

| Requirement | Evidence | Gap | Original package choice |
| --- | --- | --- | --- |
| First-class reduced path | native_src_001 and native_src_002 | Docs do not implement the user's product | motion-accessibility requires a per-interaction normal/reduced contract |
| Safe semantic exits | native_src_004 and native_src_011 | No single primitive covers every stack | Explicit ownership of focus, semantic removal, cancellation, locks and clones |
| Live setting changes | native_src_005 and native_src_006 | Startup hooks and live events differ | Verify installed adapters and test preference changes while moving |
| Native compatibility | native_src_009, native_src_010, native_src_012..015 | Exact SDK availability is project-specific | motion-native requires installed versions and matching docs before adapter code |
| Pointer and keyboard equivalence | native_src_003 and native_src_016 | No second independent author establishing the exact standard requirement | Cite the primary guidance as an entrypoint; require both practical checks |

No upstream implementation code or documentation prose was copied into plugin skills or references. Read-only pinned code excerpts in this research workspace are evidence only. No third-party dependency is selected, installed, run, or redistributed by these authored documents; no license-clearance claim is made.

## Files authored

- skills/motion-accessibility/SKILL.md
- skills/motion-native/SKILL.md
- references/accessibility.md
- references/native-platforms.md

## Unresolved

The following are direct source observations retained for inspection, not independently corroborated cross-organization claims under the Research First Creator ledger's strict rule:

- Reanimated's pinned `packages/react-native-reanimated/src/hook/useReducedMotion.ts` at `8381986bc254a0652543dac545cc08e37d90a6e6` stores a module-level startup value. Official docs agree, but code and docs have the same author organization. [native_src_006, native_src_007]
- Flutter's pinned `packages/flutter/lib/src/widgets/media_query.dart` at `7e5619891ad4ad6e66a65a414e20ebdbd8c46cea` distinguishes `disableAnimations` and `reduceMotion`; official docs have the same author organization. Apply only after inspecting the installed SDK. [native_src_009, native_src_010]
- Activity observations in artifacts/activity-observations.json record nonempty changes on the named default branches during the requested window. Commit dates and changed-file observations come from each repository's API response only; no independent author proves the date. No claim is made that the motion-related files themselves changed in that window.
- Exact WCAG criterion numbers/levels and distinctions are primary W3C observations, not a legal or conformance conclusion with independent corroboration.
- Apple full documentation retrieval was blocked by JavaScript requirements or unsupported markdown; search extracts identified API names. Compose MotionDurationScale's full page exceeded retrieval size. Exact API availability remains a target-project verification task.
- No native GUI, SDK build, screen reader, mobile device, animation profile, or live preference runtime test was run by this research arm.

## Refuted

None established. Lack of evidence or unavailable runtime access is not a refutation.
