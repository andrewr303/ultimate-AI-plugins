# Draft a clear response and supporting evidence

Read the [operating contract](../operating-contract.md). Prepare a truthful, minimal response tied to the reported issue.

## Establish the inputs

- Actual issue and cited guideline/feature.
- Concrete implemented change or factual explanation.
- Reviewer steps and representative supporting attachments.
- Secure access details and approved communication scope.
- Current reply/resubmission/appeal route and desired outcome.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Summarize the issue, actual change or explanation, exact reproduction/reviewer steps and relevant attachments using synthetic or approved data.
2. Keep sensitive access instructions in the intended secure channel. Check whether a reply, resubmission or separate appeal path is appropriate for the observed state.
3. When authorized to communicate, submit the prepared response and record its receipt; otherwise hand over the reviewable draft without transmitting it.

### Write a response the reviewer can verify

Use a short issue-to-evidence structure: acknowledge the reported concern, state the actual fix or relevant product fact, identify the build/metadata where it exists, and provide exact steps to observe it. Avoid broad assertions such as “fully compliant” that exceed the evidence. An appeal needs a specific contested interpretation and supporting facts, not only disagreement with the result.

Attachments should demonstrate the relevant path using approved or synthetic data and match the submitted artifact. Preserve accessibility and localization context where it matters. A polished mockup or development-only flow is not proof of a fix in the review candidate. Do not include private customer data, production secrets or unnecessary internal logs.

### Keep preparation separate from communication

Determine whether the user requested a draft, an actual reply, a resubmission or an appeal. Prepare the complete reviewable response first. If transmission is already authorized, use the intended secure channel and record the observed receipt/state; do not ask for the same authorization again. A draft request does not authorize sending messages.

Keep demo credentials and other sensitive access information in the intended review-information surface, not public marketing copy or repository text. If a fact remains uncertain, identify it rather than presenting it as a legal or technical conclusion. After sending, distinguish message acceptance from review resolution.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Response claims a fix absent from submitted build | Correct the build/metadata binding or the proposed response; never claim a future or local-only fix was submitted. |
| Attachment contains private user data | Replace/redact the owned attachment before transmission and preserve only necessary evidence. |
| Appeal requested when a simple factual metadata correction is needed | Choose the supported proportionate route from the actual message and state; do not turn every correction into a dispute. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Prepared issue-to-fix/explanation mapping.
- Verified reviewer steps and artifact identity.
- Approved attachment/access handling.
- Communication action/receipt or explicit draft-only status.

An internal note or source reference is not authorization to send a message to App Review or another person. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_review_messages` — [Reply to App Review messages - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/reply-to-app-review-messages/).
- `src_delivery_review_status` — [App and submission statuses - App information - Reference - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/reference/app-information/app-and-submission-statuses/).
