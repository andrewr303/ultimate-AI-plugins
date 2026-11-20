# Submission state machine and multi-item review

Read the [operating contract](../operating-contract.md). Move one intended version through a coherent current submission lane.

## Establish the inputs

- App/team/platform/version and intended processed build.
- Existing draft, in-progress submission and item identities.
- Current readiness, metadata and product/asset dependencies.
- Authorized target endpoint and release policy.
- Tool lane and expected observable server transitions.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Resolve app/platform/version/build and inspect existing draft or in-progress submissions; select one lane rather than combining unrelated wrappers.
2. Attach the intended build and required review items, inspect readiness and draft composition, then execute the already authorized submit action.
3. Report Ready for Review, Waiting for Review, In Review, item Accepted/rejected and completed submission as distinct states; account for other items gating completion.

### Select one coherent review lane

Start by reading the current app version and its attached build, selected platform and existing submissions. Do not combine a high-level submit wrapper with lower-level item creation after one has already created a live submission. A draft can contain products, assets or other items outside the current tool's ownership; inspect it before modifying or reusing it.

Apple's current preparation flow distinguishes adding an item for review from actually submitting the submission. Ready for Review is not Waiting for Review or In Review. An accepted item can remain gated by another rejected item in the same submission. Preserve that composition and identify the dependent blocker rather than calling the app approved for publication.

### Carry authority and evidence through the state machine

Resolve exact canonical identifiers instead of an app-name search or unconstrained latest build. Stage the intended build and required items, assess readiness against that current state, and execute the requested submit action when its dependencies and existing authorization are satisfied. A supported CLI confirm flag is a command mechanism, not a reason to ask the user again.

Capture the resulting submission/item identifiers and status. If a gate fails, stop only dependent mutation and continue authorized diagnosis. If completion is uncertain, read current remote state before retrying. Review acceptance, manual release, scheduled release and actual storefront availability remain separate stages even when one command can orchestrate several of them.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| A draft exists with items not managed by the current tool | Identify item ownership and choose a supported reuse/correction path; do not erase unknown draft items or create a duplicate blindly. |
| One accepted app item is blocked by another rejected item | Report each item and the resulting submission dependency; repair or remove an item only within requested scope. |
| Wrong platform version selected by latest | Resolve the exact app/platform/version/build relationship before attachment or submission. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Selected lane and canonical target relationships.
- Readiness against the currently attached build/items.
- Submission/item IDs and furthest observed status.
- Authorized mutations, partial results and next dependency.

Tool --confirm flags are execution mechanics, not a reason to ask the user repeatedly after authority is established. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_submit_review` — [Submit an app - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/).
- `src_delivery_review_status` — [App and submission statuses - App information - Reference - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/reference/app-information/app-and-submission-statuses/).
- `src_comp_delivery_code_004` — [fastlane/fastlane@a540df301c4a:deliver/lib/deliver/submit_for_review.rb](https://github.com/fastlane/fastlane/blob/a540df301c4ada0621cdb50358049734712f7ee7/deliver/lib/deliver/submit_for_review.rb).
