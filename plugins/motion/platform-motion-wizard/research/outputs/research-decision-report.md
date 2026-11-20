# Platform Motion Wizard: research decision report

This is a manually supported source review for an original plugin expansion. It is not an automated research-gate result, a runtime test of upstream projects, or legal clearance. The build should preserve the user-supplied skill and add original specialist guidance; no upstream skills, recipes, code, artwork, setup scripts, or hosted-service workflows are copied.

## Research method

The independent GitHub arm executed separate queries for literal microinteractions, React animation topics, gesture animation, accessible headless components, view transitions, animation agent skills, React springs, and UI motion skills. Exact queries and returned candidates are recorded in `../artifacts/query-ladder.json`. The parent also ran the Awesome directory arm. The directory does not establish recency or licensing.

The activity screen used the user's requested rolling window, 2026-09-21 through 2026-10-21. It inspected repository metadata, the repository's actual default-branch commit collection, then commit detail containing nonempty changed-file lists. Source-path commit queries distinguished implementation changes from sponsor data, documentation, dependency updates, and release bumps. `pushed_at` was never used as sufficient activity proof. All directly observed dates and file changes are preserved in `../artifacts/activity-v2.json`; their limits are discussed under Unresolved.

The author inspected pinned README, implementation, test, package manifest, history/release material and license files for the foundational finalists. New agent-oriented motion projects were inspected as an additional arm. Source snapshots remain in scratch only; the distributable should carry URLs and authored analysis, not those snapshots. No upstream code, installers, dependency setup, tests or scripts were executed. Manually supported claims are in `../artifacts/claim_ledger.jsonl`, registered against `../sources/sources.jsonl`. There is no `verified_claims.json` because the configured accelerator/gate tooling was unavailable.

## Supported design conclusions

Rendering presence and animation completion should be treated separately in the original plugin's architecture guidance. Radix's explicit presence machine and Base UI's animation-completion coordination independently illustrate this separation. [clm_presence; src_insp_2_1, src_insp_4_1]

Rapid close/reopen needs explicit stale-completion protection. Motion's re-entry regression cases and react-spring's leave-phase guards independently model this risk. The new plugin should require current-intent checks, cancellation cleanup, and tests for an old exit completing after re-entry. [clm_reentry; src_insp_1_1, src_insp_5_1, src_insp_5_2]

Cancellation is a distinct lifecycle path. Radix, Base UI and react-spring explicitly handle canceled animation or leave results before removing presence. The plugin should specify immediate final-state behavior when motion is absent and should avoid using a lone animation event or assumed duration as a product-state clock. [clm_cancel; src_insp_2_3, src_insp_4_1, src_insp_5_1]

Reduced-motion behavior needs inspection at the installed API version. The inspected web implementations include media-query subscriptions with cleanup; the inspected native hook is an app-start snapshot. The plugin should require a live preference test rather than assume the hook name establishes responsiveness to a preference change. [clm_live, clm_snapshot; src_insp_5_3, src_svelte_live, src_native_snapshot, src_native_snapshot_docs]

Motion-agent verification guidance benefits from rendered temporal evidence. Independent motion-agent projects provide guidance for inspecting rendered moments. For a product interaction this should become normal-speed interaction review, interruption exercises and focused recordings; frame comparison alone is insufficient for input semantics, focus, cancellation, or perceived responsiveness. This final product-specific requirement is our design decision, rather than a copied video-production workflow. [clm_evidence; src_m2c_verify, src_iart_verify]

## Feature-by-feature decisions

The rows below identify the evidence used for the original-design decision. Source-specific facts that lack independent corroboration remain narrow observations, with details in the Unresolved annex and compact inspection records. Every license decision here is a conservative no-copy implementation decision, not an affirmative rights opinion.

| Requirement | Finalist and pinned evidence | Gap / compatibility boundary | License decision | Original design choice |
| --- | --- | --- | --- | --- |
| Interruptible presence | `radix-ui/primitives@eb3a2b7091293e27df8f9ba906632d8daa3d81a3:packages/react/presence/src/presence.tsx`; `mui/base-ui@798983a1392f23c53b0740d047eab53a951376ac:packages/react/src/internals/useAnimationsFinished.ts` | Presence machinery does not itself define app intent, background inertness, or focus behavior. Internal hooks are not stable imports. | Original prose only | Model user intent, render retention, and interaction availability independently. [clm_presence, clm_cancel] |
| Re-entry without stale unmount | `motiondivision/motion@a03a6daf30d6ff63286e716a0f612d3b3a493802:packages/framer-motion/src/components/AnimatePresence/__tests__/reentry-during-exit.test.tsx`; `pmndrs/react-spring@e17c982134c2d62403f8f5b2958efbbcd79de435:packages/core/src/hooks/usePresence.ts` | Tests were read, not run. Inspected react-spring branch includes prerelease APIs. | Original prose only | Require canceled/stale callbacks to verify current phase or generation before settling. [clm_reentry] |
| Live reduced motion | `pmndrs/react-spring@e17c982134c2d62403f8f5b2958efbbcd79de435:packages/shared/src/hooks/useReducedMotion.ts`; `humanspeak/svelte-motion@f2b5d7666cb62767fc4a753391fc35da840f46a2:src/lib/utils/reducedMotion.svelte.ts` | Framework lifecycle and initial SSR policy vary; no universal drop-in hook. | Fresh implementation only | Central preference adapter, cleanup, active-motion settlement, state parity test. [clm_live] |
| Native preference correctness | `software-mansion/react-native-reanimated@8381986bc254a0652543dac545cc08e37d90a6e6:packages/react-native-reanimated/src/hook/useReducedMotion.ts`, compared with Svelte source above | Snapshot APIs need a separate live native preference subscription when the task requires session changes. | Fresh implementation only | Verify both initial preference and mid-session changes on the actual platform. [clm_snapshot] |
| Press feedback and cancellation | `adobe/react-spectrum@2eb4e0e9154943e92466daf9213183af84b6e6ad:packages/react-aria/src/interactions/usePress.ts` | Behavior hooks need visual-state integration; single-source observation, not independent corroboration. | No copied code | Input feedback specialist: press, release, pointer cancel, keyboard activation, disabled/pending semantics. See Unresolved. |
| Temporal review workflow | `lovisdotio/motion2code@7fa40202b485c8e47e0f155135a324151259dd52:skills/motion2code/references/verification.md`; `iart-ai/motion-skills@bb5a3ce666110855a3437de2f70e9968c408e005:tools/verify/README.md` | Video reconstruction and rendered frames do not establish real interaction quality. | No bundled scripts or text | Evidence-based review specialist with explicit runtime/static-only distinction. [clm_evidence] |
| Specialist routing | `lovisdotio/motion2code@7fa40202b485c8e47e0f155135a324151259dd52:skills/motion2code/SKILL.md`; user request | Upstream video workflow differs from app polish; no copied routing table. | Fresh router and skills | Route to minimal relevant specialists; keep the original skill intact and avoid loading an entire corpus for a small fix. |

## Proposed skill and reference coverage

These are original scope decisions derived from the user request and the supported lifecycle findings: one main router; diagnostics/inventory; motion tokens and specifications; immediate input feedback; overlays and focus; navigation and spatial continuity; gestures and direct manipulation; loading/async/streaming; reduced motion and accessibility; stack implementation; native implementation; performance and profiling; interruption/state repair; final interaction review. Specialist roles should have clear handoff contracts and should not claim that a Markdown role file automatically becomes a runtime agent in every host.

Keep shared references for state contracts, token selection, stack API/version verification, native platform mapping, component patterns, performance diagnosis, accessibility test cases, current source resources, and review evidence. Include short original templates and deterministic local validation where it checks a concrete structural or behavioral risk. Do not add sound or haptics; the attached original skill excludes them.

## Unresolved

### Direct activity observations

The candidate screen directly observed changed-file commits within the requested window for Motion, react-spring, Radix, React Spectrum, Base UI, Reanimated, Ark, Svelte Motion and motion-agent candidates. These are primary-source observations, not independently corroborated maintenance guarantees. Exact branch, SHA, date, changed paths and commit URLs are in `activity-v2.json`. Important distinctions:

- Motion's observed current implementation commit changes reorder auto-scroll and unit/browser regression coverage. Radix changes first-frame dismissal-layer input behavior. React Spectrum changes keyboard typeahead. Base UI changes dropped IME-composition dismissal.
- react-spring's latest observed commit is dependency maintenance, but path-specific history separately identifies an implementation change to zero-dimension resize animation with unit/browser tests. The inspected default branch carries prerelease APIs, so use the target app's installed stable APIs.
- Svelte Motion's latest observed commit is a version bump; a separately inspected recent default-branch commit contains implementation and browser-test changes.
- Floating UI's latest observed changes are sponsor data; its observed React source-path change is outside the requested month. It is supplemental context, not evidence of newly evolving interaction code.
- use-gesture's observed main branch is from 2024 and react-spring-bottom-sheet's from 2022. Both are explicitly stale for this screen despite repository push metadata.
- iart-ai/motion-skills' recent change is a README directory update, not proof its individual skill implementations changed recently. Motion2Code is newly created in the requested window and is adjacent video reconstruction rather than a substitute for product-interaction guidance.

### Single-source and conflicting observations

- React Aria's inspected press implementation exposes immediate press-state changes and explicit cancel cleanup. The broader plugin requirement also comes directly from the preserved original skill and the user's request; the specific library behavior remains a pinned single-source observation. [src_insp_3_1, src_insp_3_2, src_insp_3_3]
- The inspected Motion hook's documentation comment describes reactive behavior, while its implementation initializes state from a shared preference reference without a setter/subscription. A global media-query listener alone does not establish mounted-consumer rerendering. Runtime behavior must be checked in the installed version. [src_insp_1_2, src_insp_1_3]
- Source license files were read, but legal clearance is not established by their labels. Transitions.dev's source terms explicitly distinguish restricted transitions/skills from tooling; this research deliberately excludes its text, snippets, tokens, styles, assets and service workflow from the output. It is an adjacent recent agent example, not reusable package material. [src_transitions_license]
- Upstream tests were inspected only. No claims about upstream passing builds, frame rate, latency, runtime accessibility conformance, or measured quality are made.

## Refuted

No broad library reliability or licensing claim is asserted. The research rejects the method of treating `pushed_at`, a repository-directory listing, or a README marketing sentence as sufficient evidence of recent default-branch implementation activity. It also rejects a blanket assumption that every motion hook automatically updates on session preference changes.
