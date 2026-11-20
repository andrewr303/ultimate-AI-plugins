# Resubmit without losing the original evidence trail

Read the [operating contract](../operating-contract.md). Verify that the repair reaches the intended review artifact and does not create a new regression.

## Establish the inputs

- Original rejection and implemented repair.
- Eligible new/existing build and version relationship.
- Changed privacy/commerce/content/permission facts.
- Current draft/item composition and review access.
- Affected regression checks and required release gates.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Bind the fixed code/metadata to a new or existing eligible build as appropriate, preserving the original rejection and repair evidence.
2. Rerun the affected behavior and required release checks; ensure pending products/assets and access data still match the submission.
3. Read current submission state, reuse or replace only within the chosen lane, and report the exact resubmitted version/build/items.

### Carry the repair into the actual candidate

Track the issue from reviewer evidence to code or metadata change to the exact candidate selected in App Store Connect. A successful local build does not establish that the correct binary was uploaded, processed and attached. Recheck identifiers and release configuration at the selection boundary.

A narrow correction can change other material facts: adding a permission, SDK, external purchase path, account flow or backend dependency can affect declarations and review access. Reassess the affected evidence instead of treating the old packet as permanently valid. Reuse unrelated successful checks when their inputs remain unchanged.

### Preserve submission continuity

Inspect current drafts, live review and selected item relationships before resubmission. Reuse a supported existing lane when appropriate and avoid bringing unrelated stale items into the repaired submission. If another item remains blocked, report that dependency rather than sending a partially repaired release as though it is ready.

Capture the resulting version/build/item/submission identifiers and current state. Preserve the original rejection and repair verification so a maintainer can understand what changed. Neither successful resubmission nor a message receipt establishes acceptance or public release; report the furthest actual state.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| A fixed app is built but an older binary is selected | Resolve the candidate mismatch and attach the intended eligible build before relying on the fix. |
| Repair changes privacy or commerce facts that were not rechecked | Refresh the affected declaration/product evidence and complete its required checks before the dependent action. |
| A stale draft carries unrelated items | Inspect ownership and scope of each item; correct only the intended composition without blanket draft deletion. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Original issue-to-change-to-candidate trace.
- Relevant regression and declaration rechecks.
- Current submission composition and authorized action.
- Observed resubmission state and remaining dependencies.

Do not automatically submit a partially repaired release while a dependent blocker remains unresolved. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_choose_build` — [Choose a build to submit - Manage builds - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-builds/choose-a-build-to-submit/).
- `src_delivery_review_messages` — [Reply to App Review messages - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/reply-to-app-review-messages/).
- `src_comp_delivery_code_018` — [rorkai/app-store-connect-cli-skills@0915e9da1016:skills/asc-submission-health/SKILL.md](https://github.com/rorkai/app-store-connect-cli-skills/blob/0915e9da1016a6cc953659d43906dcf7839a4c52/skills/asc-submission-health/SKILL.md).
