# Notary submission, wait and diagnostics

Read the [operating contract](../operating-contract.md). Submit the intended signed artifact and interpret the service result correctly.

## Establish the inputs

- Final signed app/package/disk image and artifact hash.
- Current notarytool/API capabilities and selected Xcode.
- Credential type/team/profile and authorized operation.
- Prior submission IDs and current status.
- Protected diagnostic destination and bounded wait policy.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Inspect actual signed artifact and supported archive form, the selected notarytool/API auth method and relevant installed Xcode/tool capability.
2. Submit only under matching authorization, preserve the submission ID and distinguish upload from the final Accepted/Invalid result.
3. Fetch and inspect diagnostics even after acceptance where available. Resolve code-signature, timestamp, hardened-runtime or packaging problems without broad entitlements or blind resubmission.

### Separate upload from the service verdict

Inspect the actual signed artifact and supported container before submission. Verify the selected developer directory and installed tool help, particularly when authentication capabilities differ between Xcode/tool versions. Use the existing supported credential mechanism without exposing a password or private key in scripts or logs.

Submit only under the task's authority, preserve the submission identifier and distinguish upload success from a final Accepted or Invalid result. A timeout can leave a real submission on the service. Read its status before sending another copy. A bounded wait or a concrete resumable monitor step is more useful than an endless polling loop.

### Read logs and repair the originating problem

Inspect diagnostics, including warnings available after acceptance. Resolve the specific signature, timestamp, executable layout, runtime, entitlement or packaging issue. Do not add broad entitlements, disable checks or indiscriminately re-sign every nested item just to suppress a message. Preserve the artifact identity through the repair and resubmit only the deliberately changed candidate.

Use current notarytool or the supported Notary API path for notarization. The older notarization altool path is a different contract from App Store binary uploads that may use another tool lane. Treat third-party notes about API-key restrictions as version-specific evidence to verify against current Apple documentation and installed help.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Unexpected non-JSON tool result | Preserve a redacted diagnostic and classify the unexpected output/exit status; do not parse it as a successful receipt. |
| Upload accepted but notary status Invalid | Record the Invalid result and relevant issue paths, then repair and rebuild the intended artifact. |
| Auth guide and installed tool differ on key-type support | Check the selected tool/Xcode/auth capability and choose a supported scoped method without assuming one guide is universal. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Artifact identity and verified notary lane.
- Submission ID, wait/monitor result and final service status.
- Relevant redacted diagnostics and concrete repair.
- Next notary/stapling step and remaining runtime limitations.

Use notarytool/current API for notarization; do not generalize notarization altool deprecation to every App Store upload operation. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_notarization` — [Notarizing macOS software before distribution](https://developer.apple.com/tutorials/data/documentation/security/notarizing-macos-software-before-distribution.json).
- `src_delivery_notary_custom` — [Customizing the notarization workflow](https://developer.apple.com/tutorials/data/documentation/security/customizing-the-notarization-workflow.json).
- `src_delivery_notary_errors` — [Resolving common notarization issues](https://developer.apple.com/tutorials/data/documentation/security/resolving-common-notarization-issues.json).
- `src_comp_delivery_code_059` — [electron/notarize@9ef0c5bd463b:src/notarytool.ts](https://github.com/electron/notarize/blob/9ef0c5bd463b79b18d614b239a9cbe15df99cea5/src/notarytool.ts).
