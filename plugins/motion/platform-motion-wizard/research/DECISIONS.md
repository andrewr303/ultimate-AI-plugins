# Design decisions and provenance

Read the [main report](outputs/research-decision-report.md), [native supplement](native/outputs/native-accessibility-research.md), and [activity table](../references/research-snapshot.md).

| Requirement | Adopted idea and evidence | Original implementation |
| --- | --- | --- |
| Immediate feedback and coherent states | User request and complete supplied skill; pinned input observations are qualified in main report | controls, async, contracts |
| Interruptible presence | clm_presence, clm_reentry, clm_cancel in main claim ledger | state-lifecycles reference, overlay/web/gesture checklists |
| Live reduced-motion policy | clm_live, clm_snapshot; native_clm_001 and native_clm_003 | accessibility and native specialists; lab policy |
| Semantic exits | native_clm_002 plus original skill | explicit overlay focus/inert/presence ownership |
| Current coding-agent workflow | clm_evidence; user request for routing and multiple skills | fresh router, focused skills, bounded agents and temporal review |
| Restrained vocabulary | Preserved source skill's authored starter ranges | opt-in token example and system skill |
| Honest performance claims | User request and authored verification policy | profiling specialist and evidence report |
| Reviewable deliverable | User request for full ZIP | manifests, provenance hashes, package validation and regression fixtures |

No third-party implementation or skill is incorporated. Source-specific constraints and rights observations remain in the reports' Unresolved sections. The final architecture is original; source review informed the behavioral invariants.

## Executable lifecycle overhaul

| Requirement | Adopted abstract idea and evidence | Original implementation |
| --- | --- | --- |
| Obsolete visual completion must not mutate current state | ovr_clm_replacement, Motion and Base UI pinned in the [overhaul report](overhaul/outputs/research-decision-report.md) | Scalar controller with generation invalidation and controllable completion tests |
| Cancel only owned work and release it during teardown | ovr_clm_cleanup, independent component implementations | Controller disposal and scoped policy subscriptions; no document-wide effect cancellation |
| Race evidence must execute the unwanted callback | Source tests and their documented limits; original verification requirement | Response delivery controls plus deterministic delayed-completion tests |
| Claims must retain honest review state | Existing manual research contract | Explicit status/risk/proof validation and malformed-ledger regressions |
