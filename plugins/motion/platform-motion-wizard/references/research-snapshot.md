# Research snapshot and useful resources

Reviewed for this build on **2026-10-21**, prioritizing changed default-branch files during **2026-09-21 through 2026-10-21**. This is a dated evidence map, not a dependency prescription. Recheck the target app's installed release before applying an API.

The [main decision report](../research/outputs/research-decision-report.md) links broad, manually supported conclusions to independent sources. The [native supplement](../research/native/outputs/native-accessibility-research.md) explains platform-specific limits. Full activity observations and pinned files are in [activity records](../research/artifacts/activity-v2.json) and [finalist inspections](../research/artifacts/pinned-inspections.json).

## Supported engineering lessons

- Model rendering presence independently from visual completion. [clm_presence]
- Protect re-entry from an old exit completion and handle cancellation explicitly. [clm_reentry, clm_cancel]
- Verify live preference behavior instead of relying on an API's name. [clm_live, clm_snapshot]
- Use temporal evidence and actual input sequences when reviewing motion; stable screenshots alone do not establish interaction quality. [clm_evidence; product-specific review policy]

Claim IDs refer to [the ledger](../research/artifacts/claim_ledger.jsonl). These lessons inform original skills and references; no upstream code, tokens, or skill text is bundled.

## Resources by task

| Task | Source entrypoint | How to use it |
| --- | --- | --- |
| Web motion/presence | [Motion](https://github.com/motiondivision/motion) | Inspect installed APIs; separate animation from accessible component behavior |
| Accessible overlays | [Radix Primitives](https://github.com/radix-ui/primitives) and [Base UI](https://github.com/mui/base-ui) | Prefer proven primitives; do not import internal hooks from research examples |
| Press/keyboard behavior | [React Aria / Spectrum](https://github.com/adobe/react-spectrum) | Check input normalization and semantic states before adding visual response |
| Spring and retargeting | [react-spring](https://github.com/pmndrs/react-spring) | Confirm stable versus prerelease APIs and the library's physical units |
| Native motion | [Reanimated](https://github.com/software-mansion/react-native-reanimated) | Verify initial preference versus live updates and UI/application state ownership |
| Svelte preference adapter | [Svelte Motion](https://github.com/humanspeak/svelte-motion) | Check installed release and lifecycle cleanup |
| Motion accessibility | [W3C animation guidance](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | Read the exact criterion scope and level; do not infer full conformance |
| Modal semantics | [WAI-ARIA modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | Focus, modality, dismissal and return behavior |
| Web preferences | [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion) | Coordinate CSS with JS/native adapters and active effects |

See [native adapters](native-platforms.md), [accessibility](accessibility.md), and [performance](performance.md) for further primary entrypoints and qualifications.

## Unresolved

These are directly inspected primary-source observations. Their dates and exact changes are not independently corroborated maintenance guarantees. Commit URLs and full changed-file lists are retained in the activity records.

| Repository | Observed commit / date | Activity classification and decision |
| --- | --- | --- |
| motiondivision/motion | [a03a6daf](https://github.com/motiondivision/motion/commit/a03a6daf30d6ff63286e716a0f612d3b3a493802), Oct 21 | Reorder auto-scroll implementation + unit/browser regression changes; relevant |
| radix-ui/primitives | [d715acbf](https://github.com/radix-ui/primitives/commit/d715acbf2283c7867ad01165586d97fd6c163f09), Oct 14 | First-frame dismissal-layer interaction fix + test; relevant |
| adobe/react-spectrum | [2eb4e0e9](https://github.com/adobe/react-spectrum/commit/2eb4e0e9154943e92466daf9213183af84b6e6ad), Oct 20 | Keyboard typeahead implementation + tests; relevant |
| mui/base-ui | [051a971e](https://github.com/mui/base-ui/commit/051a971ee93dad550ae29f2563f7c2e44592a96d), Oct 20 | IME-composition dismissal implementation + tests; relevant |
| pmndrs/react-spring | [82146aac](https://github.com/pmndrs/react-spring/commit/82146aacf875c175c8f965c339e69c8c1fe049ac), Oct 19 | Source-path probe found resize implementation + tests; latest head is dependency activity; prerelease caveat |
| software-mansion/react-native-reanimated | [8381986b](https://github.com/software-mansion/react-native-reanimated/commit/8381986bc254a0652543dac545cc08e37d90a6e6), Oct 21 | Native worklet implementation; preference hook inspected at this pin, not claimed changed by this commit |
| humanspeak/svelte-motion | [dc421f81](https://github.com/humanspeak/svelte-motion/commit/dc421f810c1922a90f8ab8a22d02d5f28d351ac9), Oct 17 | Separate implementation/test commit; latest head is a version bump |

Adjacent coding-agent research included Motion2Code, a new video-reconstruction skill, and iart-ai/motion-skills, a directory whose latest observed change was README-only. Their verification workflows inform the broad evidence lesson, not product-specific implementation. Transitions.dev was inspected as an adjacent recent agent example; its restricted material is not bundled or copied.

Floating UI's observed recent head changed sponsor data; its observed React source-path history was outside the month. use-gesture and react-spring-bottom-sheet had stale default branches for this screen. They are not presented as recently evolving interaction implementations.

Motion's inspected hook comment and implementation disagree about mounted-consumer updates. Reanimated explicitly documents a startup snapshot. These findings motivate installed-version runtime checks, not a universal library defect assertion. Upstream tests were inspected and were not run.

## Refuted

Using repository push time, directory freshness, stars, or a fresh marketing README as sufficient proof of recent implementation activity was rejected. No upstream runtime reliability, frame-rate, or legal-clearance claim is made.

## Overhaul review — 2026-10-21

The [overhaul decision report](../research/overhaul/outputs/research-decision-report.md) supplements the historical build review above. It uses separate GitHub query rungs and pinned source inspection, with explicit current-versus-background activity decisions in the [new activity record](../research/overhaul/artifacts/activity.json). The optional accelerator was unavailable; this is manual source review, not an automated factual gate.

The source-reviewed lessons are current-intent checks for obsolete presentation completions and explicit release of resources owned by canceled interactions. Motion and Base UI independently support the first; Base UI, React Aria, Headless UI, and dnd-kit support the cleanup lesson. These inform original executable examples and deliberate interruption tests. [ovr_clm_replacement, ovr_clm_cleanup]

Claim IDs refer to the [overhaul ledger](../research/overhaul/artifacts/claim_ledger.jsonl). Direct API, activity, test, and license observations remain qualified in that report's Unresolved annex. The existing research and complete original skill remain preserved.
