# Build upload, receipts and processing

Read the [operating contract](../operating-contract.md). Observe the boundary between delivery acceptance and usable processed builds.

## Establish the inputs

- Artifact hash, bundle ID, marketing version and build number.
- Selected App Store app/team/platform.
- Supported uploader and authentication lane.
- Existing remote build/receipt state.
- Bounded processing wait and failure-reporting policy.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Inspect the release artifact bundle ID, marketing version, build number and intended platform before uploading.
2. Use the configured supported upload lane, capture upload receipt/build identifiers and wait only within a bounded processing policy.
3. On uncertainty, query for the same build/version/platform before retrying. Report upload, processing success or processing failure separately.

### Verify identity before upload

Inspect the built artifact, not just app configuration or a cloud dashboard counter. The bundle ID, app version, build string and platform determine its relationship to App Store Connect. A local source increment is insufficient if the archived bundle still contains an earlier value. Confirm the intended app record already exists and that the selected account can access it.

Use the project's supported upload path. Xcode, supported API/Transporter workflows and a configured service can have different host requirements and receipts. A cross-platform upload service does not mean an arbitrary Xcode project can be built locally on Linux, and using that service does not justify introducing React Native into a native app.

### Observe processing rather than implying success

Capture the upload receipt and subsequent build identity. Delivery acceptance and completed Apple processing are separate states. A build may still be processing, rejected by processing, or associated with an unintended version. Keep a bounded wait and a resumable status command/receipt so a task can finish with an honest pending state instead of polling indefinitely.

After a network timeout, inspect whether the same artifact identity/build already exists before retrying. Prefer the precise intended build identifier over an unconstrained latest selector. Report only the furthest observed state; do not distribute, invite testers or create a review submission because upload was requested.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Upload times out after server accepted the artifact | Query the same app/platform/version/build and receipt; retry only after resolving whether delivery already completed. |
| Duplicate build string rejected | Inspect the conflict and actual artifact versioning; do not blindly increment source files and assume the rebuilt archive changed. |
| Processing succeeds for the wrong selected build | Correct the selection after checking ownership and processing state; preserve the intended artifact binding. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Artifact identity and selected remote target.
- Uploader/version and receipt/build identifiers.
- Processing observation and bounded wait outcome.
- Any retry decision, remote re-read and remaining next step.

An uploaded or processed build is not automatically distributed to beta groups or submitted for production review. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_upload_builds` — [Upload builds - Manage builds - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/).
- `src_delivery_choose_build` — [Choose a build to submit - Manage builds - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-builds/choose-a-build-to-submit/).
- `src_delivery_eas_submit_ios` — [Submit to the Apple App Store with EAS Submit - Expo documentation](https://docs.expo.dev/submit/ios/).
