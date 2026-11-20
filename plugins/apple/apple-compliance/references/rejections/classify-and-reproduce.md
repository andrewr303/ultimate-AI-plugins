# Classify and reproduce a review issue

Read the [operating contract](../operating-contract.md). Understand the actual rejection message and affected build before editing or replying.

## Establish the inputs

- Exact rejection message, cited guideline and affected item.
- App/platform/version/build and current submission status.
- Reviewer reproduction, attachments and environment.
- Current implementation/product facts and relevant policy source.
- Repair scope and checks needed to discriminate the cause.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Read the exact reviewer message, cited guideline, screenshots, affected item and build/version; separate technical, metadata, policy interpretation and access issues.
2. Reproduce the reported path using an appropriate build/environment. Trace actual implementation and product behavior rather than arguing from intent.
3. Create a concrete repair/evidence plan; note when metadata can be corrected without a new build, subject to the actual message and current state.

### Start from the reported behavior

Read the actual message and identify which item/build and guideline are involved. Separate inability to access the feature, a binary/runtime problem, metadata inaccuracy, missing information, product-policy eligibility and an unresolved policy interpretation. A generic rejection label does not describe the cause or the correct resubmission lane.

Reproduce the reviewer path with the intended release configuration where possible. Inspect surrounding code, backend/feature flags, permission/account state and artifact identity before claiming the issue fixed. If reproduction is unavailable, record the precise missing condition and the evidence that would settle it. Do not assert that a developer-only success disproves a reviewer's report.

### Choose a proportional repair

A metadata issue may be corrected using the same build, while a binary defect requires an appropriate new build or another eligible artifact. Determine that from the actual message and current state. Check the applicable platform/storefront and current guideline text rather than borrowing a broad exception from an unrelated app or region.

Prepare a concrete repair or factual explanation that can be tested. Do not invent product facts, argue from intended behavior or promise successful approval. When the task includes implementation, make and verify the scoped correction; when it is review-only, leave a clear actionable finding and evidence gap without sending a response automatically.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Metadata-only issue mistaken for binary rejection | Identify the actual affected field/state and avoid an unnecessary binary rebuild unless the message or implementation requires it. |
| Reviewer could not log in although app works for developer | Test the reviewer-facing credentials/environment and repair access rather than assuming the reviewer made an error. |
| Policy citation applies only to a specific feature/storefront | Record the narrow applicability and verify the actual user case before generalizing any exception. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Exact reported issue and relevant current policy source.
- Observed reproduction or named missing prerequisite.
- Root cause, scoped repair and selected correction lane.
- Build/metadata binding and verification needed before reply.

Do not invent a legal interpretation or promise a successful appeal; identify the exact missing product evidence. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_review_messages` — [Reply to App Review messages - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/reply-to-app-review-messages/).
- `src_delivery_review_status` — [App and submission statuses - App information - Reference - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/reference/app-information/app-and-submission-statuses/).
- `src_delivery_submit_review` — [Submit an app - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/).
