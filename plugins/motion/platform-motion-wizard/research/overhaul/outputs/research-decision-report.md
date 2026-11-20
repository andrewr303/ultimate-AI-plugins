# Platform Motion Wizard overhaul: research decisions

This is a manually supported source review for an original plugin overhaul. It is not an automated research-gate result. The optional accelerator and report-gate tooling were unavailable. Source snapshots stayed in the workspace's scratch area; the plugin carries source URLs, authored observations, and original implementation examples.

## Deliverable and method

Preserve the plugin identity, the complete original polish skill, and the existing specialist boundaries. Make the lifecycle guidance executable: a small original presentation controller and live motion policy, an interaction lab that actually receives obsolete responses, and focused behavioral checks. Tighten package research and scenario-fixture validation. These are local design decisions for the requested overhaul, not claims about upstream code.

The research used Awesome intent/tag/filtered/unfiltered/named retrieval plus separate GitHub queries. The [query ladder](../artifacts/query-ladder.json) records the executed searches. The [activity observations](../artifacts/activity.json) retain the default branch, changed-file commits, and the distinction between implementation, tests, documentation, dependencies, workflows, and release activity. Directory ranking, stars, and `pushed_at` were not accepted as proof of current implementation.

The [inspection records](../artifacts/pinned-inspections.json) retain pinned README, implementation, tests, dependency surface, history, and license entrypoints for the finalists. Some finalists are explicitly older background comparisons. The activity screen and direct source-specific observations are qualified under **Unresolved** below. Upstream code, setup scripts, dependencies, and tests were not executed. No `verified_claims.json` or automated factual PASS is produced.

## Manually supported conclusions

Independent interaction implementations distinguish current or replacement presentation work from obsolete completion callbacks. Motion clears exit bookkeeping when a child is present again and includes a re-entry regression; Base UI checks abort state and waits for replacement animations after cancellation. The broad lesson is supported by independent authors. The original controller should invalidate an old generation before cancellation, retarget from current presentation, and settle only the latest target. [ovr_clm_replacement; ovr_src_motion_presence, ovr_src_motion_reentry, ovr_src_base_finish, ovr_src_base_finish_test]

Independent interaction implementations explicitly release resources owned by canceled interactions. Base UI disconnects its owned observer on abort; React Aria removes global listeners and invokes stored disposables during press cancellation; Headless UI and dnd-kit also model owned cancellation cleanup. The original controller should keep resource release separate from permission to mutate current state. [ovr_clm_cleanup; ovr_src_base_finish, ovr_src_aria_press, ovr_src_headless_implementation_0, ovr_src_dnd_implementation_1]

## Original implementation provenance

The presentation controller's generation contract follows the abstract replacement lesson above, not an upstream algorithm or copied helper. Its adapter owns only decorative presentation; existing accessible primitives and data owners remain authoritative. The live policy and the deliberate obsolete-response lab are authored integration decisions. Their correctness must be established by the local tests and real-browser evidence, separately from source research. [ovr_clm_replacement, ovr_clm_cleanup]

The validator changes originate in inspection of this plugin's own malformed-ledger and fixture boundaries. They check integrity and cannot establish factual truth, legal clearance, host routing quality, or animation quality. No upstream validator is incorporated.

## Unresolved

These are pinned primary-source observations, not independently corroborated maintenance, compatibility, runtime, or legal guarantees. They remain outside affirmative factual synthesis. [ovr_clm_details]

### Requirement-to-design comparison

These rows compare behavioral ideas, not dependency recommendations. Each source-specific boundary is qualified in the annex. Internal helpers are evidence, not supported imports. The original implementation adds no upstream runtime dependency.

| Requirement | Finalist and pinned evidence | Gap / boundary | License decision | Original design choice |
| --- | --- | --- | --- | --- |
| Superseded completion cannot undo current intent | `motiondivision/motion@a03a6daf30d6ff63286e716a0f612d3b3a493802:packages/framer-motion/src/components/AnimatePresence/index.tsx` and `.../__tests__/reentry-during-exit.test.tsx` | Rendering presence does not own application operations or overlay focus. | Fresh implementation; no source copied. | Generation ownership and deliberate late-completion tests. [ovr_clm_replacement; ovr_src_motion_presence, ovr_src_motion_reentry] |
| Cancellation with replacement and immediate fallback | `mui/base-ui@798983a1392f23c53b0740d047eab53a951376ac:packages/react/src/internals/useAnimationsFinished.ts` and companion test | Internal React helper; cannot be treated as a public cross-framework API. | Fresh implementation; no source copied. | Handle cancellation, replacement, API failure, no effect, and zero duration as explicit paths. [ovr_clm_replacement, ovr_clm_cleanup; ovr_src_base_finish, ovr_src_base_finish_test] |
| Input and cleanup ownership | `adobe/react-spectrum@2eb4e0e9154943e92466daf9213183af84b6e6ad:packages/react-aria/src/interactions/usePress.ts` | A decorative presentation controller cannot replace native controls, press normalization, focus, or dismissal primitives. | Fresh implementation; no source copied. | Keep domain/input semantics with existing primitives and scope cleanup to the effect owner. [ovr_clm_cleanup; ovr_src_aria_press] |
| Guard deferred input work | `clauderic/dnd-kit@01bc678e93477e56a78aa2244c69b08a96cb0da6:packages/dom/src/core/sensors/pointer/PointerSensor.ts` | Modern modular adapters differ from legacy package examples; inspect installed versions. | Fresh implementation; no source copied. | Preserve current intent across deferred rendering and distinguish cancellation from an accepted operation. [ovr_clm_replacement, ovr_clm_cleanup; ovr_src_dnd_implementation_1] |
| Compare cancellation without depending on fresh releases | `tailwindlabs/headlessui@eea57cf46fd6767ed1059012f7073b88eb159fba:packages/@headlessui-react/src/hooks/use-transition.ts` | Older background; disabled upstream fixtures are not passing-test evidence. | Fresh implementation; no source copied. | Explicit no-effect completion and disposed-callback suppression. [ovr_clm_replacement, ovr_clm_cleanup; ovr_src_headless_implementation_0] |
| Distinguish pausing effects from disposal | `formkit/auto-animate@06882a8e69ba9bc8456d8f2ae6010f697fd7a37c:src/index.ts` | Older source-path history; initial preference reads do not establish live behavior. See annex. | Fresh implementation; no source copied. | Separate settle from dispose; test preference changes during a positively observed active effect. [ovr_clm_cleanup, ovr_clm_details; ovr_src_auto_implementation_0, ovr_src_auto_implementation_1, ovr_src_auto_implementation_2] |
| Scope preference listeners and active effects | `juliangarnier/anime@34f417983c1d33103c5d6d50d1c435ef2787ece0:src/scope/scope.js` | Relaxed-screen background; inspected scope-root tests do not prove cancellation behavior. | Fresh implementation; no source copied. | Explicit policy subscription/disposal and current-target settlement on reduction. [ovr_clm_cleanup, ovr_clm_details; ovr_src_anime_0] |

### Activity observations

The task's review date was **2026-10-21 America/Denver**. Preferred activity was a changed default-branch implementation during the preceding month; an extended screen allowed older evidence with explicit labels. Full commit URLs, timestamps, and changed paths are in the activity artifact.

| Candidate | Observed activity and screening decision |
| --- | --- |
| Motion | Default head `a03a6daf`, October 21, changes reorder auto-scroll implementation and unit/browser fixtures; current implementation exemplar. |
| Base UI | Default head `798983a`, October 21, changes documentation/blog support. Separate default-path commit `bf66e3ad`, October 20, changes lifecycle/portal implementation and tests; current implementation evidence comes from that path observation. |
| React Spectrum | Default head `2eb4e0e9`, October 20, changes typeahead implementation and tests; current implementation exemplar. |
| dnd-kit | Head `01bc678e`, October 15, is release metadata; source-path commit `bbf1b4dd`, October 15, changes pointer implementation and tests. Current implementation evidence is separate from the release head. |
| react-spring | Head `e17c9821`, October 20, is dependency activity; separate `29452d32`, September 25, changes presence implementation and tests. Relevant existing-plugin context; prerelease/API boundary retained. |
| Svelte Motion | Head `f2b5d766`, October 17, is a version bump; separate `dc421f81` changes implementation and browser fixtures. Relevant existing-plugin context. |
| Radix Primitives | Head `eb3a2b70`, October 14, changes package tooling. This run's source-path probe failed; the head alone does not prove recent implementation activity. Existing historical evidence is preserved separately. |
| Headless UI | Head `eea57cf4`, April 13, is workflow-only; transition path observation `da2fa94e` is from September 2025. Background outside the extended screen. |
| AutoAnimate | Head `06882a8e`, July 10, changes documentation and browser fixtures; core path `91f32019` is from September 2025. Background implementation comparison, not current core evidence. |
| Anime.js | Source-path commit `34f41798`, June 22, is within the relaxed source screen only. Background finalist; no fresh default-head implementation claim. |
| GSAP | Source-path commit `13e2b790`, April 13, falls outside the extended screen. Background exploration, not a selected current exemplar. |
| Number Flow | `c5906cf3`, September 20, changes README only; numeric-transition utility is adjacent to the requested lifecycle overhaul. |
| interact.js | `a993eb8c`, August 1, changes a publishing workflow; no preferred-screen interaction implementation proof. |
| next-view-transitions | `67326d61`, March 6, changes example layout; older background. |
| Lottie iOS | `1fb4d7d5`, October 6, changes deployment-target/package files; authored-animation playback is adjacent rather than a lifecycle implementation replacement. |
| Micron | `c46d1bd8`, May 2018, changes release/readme metadata; stale for the screen. |
| animate-presence | `5ebd679f`, November 2020, changes funding data; stale for the screen. |

### Source-specific limits

- AutoAnimate's inspected initialization reads `matchMedia.matches`; the function does not register a media-query change listener. Its disable and destroy paths differ. That source observation does not establish all framework adapters' runtime preference behavior. The inspected disable test allows a nonpositive in-flight baseline, so it is not proof that an active effect was interrupted. [ovr_src_auto_implementation_0, ovr_src_auto_implementation_1, ovr_src_auto_implementation_2, ovr_src_auto_test_0]
- Headless UI's nested transition cases include disabled `xit` fixtures. Those examples were read and were not represented as executed or passing. [ovr_src_headless_test_0]
- dnd-kit's inspected DOM package and adapters differ from legacy examples. Read the actual installed package/API before using any source observation in a product. [ovr_src_dnd_manifest, ovr_src_dnd_history]
- Anime scope source handles media changes and removes listeners during reversion; its inspected scope suite covers root-selection behavior. No upstream cleanup or performance test result was obtained. [ovr_src_anime_0, ovr_src_anime_1]
- Anime's README and dependency manifest were inspected at the source-path pin. The manifest is a parsed JSON object, with optional Three.js peers and no runtime dependencies field. `CHANGELOG.md` returned 404, so official release notes and commit history were inspected instead. The observed release tag points to a different commit from the source-path pin; release history is contextual and does not establish shipped-version equivalence. [ovr_clm_anime_release; ovr_src_anime_readme, ovr_src_anime_3, ovr_src_anime_release, ovr_src_anime_tag]
- The initial React Aria press-test URL returned 404. The corrected `packages/react-aria/test/interactions/usePress.test.js` path was subsequently retrieved and inspected. This was an evidence-path correction, not a missing upstream test claim. [ovr_src_aria_press_test]

### License and reuse boundaries

The inspected Motion, Base UI, Headless UI, AutoAnimate, dnd-kit, and Anime license files contain MIT labels/text; the inspected React Spectrum file contains Apache License Version 2.0 text. These labels are source observations only. Their notices and conditions matter to any future source redistribution; no legal clearance, complete rights chain, or blanket copying permission is asserted. License entrypoints are retained in the inspection records. The implementation decision is to incorporate no upstream source, tests, assets, skill text, or prose.

GSAP's repository metadata points to a license page that returned a forum-offline page during inspection. Its rights were not resolved and its material was not used in the implementation.

Upstream tests were read, not run. No source inspection establishes frame rate, input latency, browser or native accessibility conformance, installed host routing, or production integration. Local verification belongs in the plugin's validation evidence and is not inferred from this report.

## Refuted

The review rejects using a repository push timestamp, directory freshness, popularity, release-only head, or a documentation-only commit as sufficient proof of a current default-branch interaction implementation. It also rejects treating a canceled timer as evidence that a delivered obsolete response was ignored. These are methodological exclusions; no universal defect or reliability conclusion about a library is asserted.
