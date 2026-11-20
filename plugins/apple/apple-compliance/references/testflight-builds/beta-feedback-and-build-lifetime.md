# Beta feedback, crashes and build lifetime

Read the [operating contract](../operating-contract.md). Use evidence from the intended build to close issues before submission.

## Establish the inputs

- Feedback/crash build and symbol UUID binding.
- Supported OS/device/test configuration.
- Current beta eligibility and expiry evidence.
- Reproduction, severity and scope of each finding.
- Protected diagnostic retention and app-user data boundaries.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Bind feedback/crashes to version/build, OS/device context, reproduction and symbol UUIDs. Redact user content in shared reports.
2. Track tester reports, expiration and eligibility with current Apple limits rather than hardcoded permanent counts.
3. Reproduce important defects against the same release configuration; preserve diagnostic artifacts and distinguish absence of feedback from proof of correctness.

### Bind feedback to the correct artifact

A crash or screenshot is useful only when it can be tied to the version/build and context that produced it. Resolve symbol UUIDs and release configuration before attributing a stack to the current candidate. Preserve a minimal reproduction with OS/device, account/permission state and relevant steps. Avoid copying personal message content, photos, tokens or user identifiers into a public issue.

Distinguish a confirmed defect from an unverified report and prioritize behavior that affects review or the intended release. Absence of feedback is not evidence that an unexercised feature works. Tester counts, collection windows and build lifetime should be interpreted with the actual denominator and current Apple eligibility state.

### Keep preparation useful while builds age

If a build expires or becomes ineligible, record the state change and choose a deliberate replacement. Do not silently map old feedback to a new artifact or assume a rebuild contains the intended fix. Recheck the affected behavior in the release configuration and maintain a closed-loop link from report to repair to verification.

A beta smoke test does not replace privacy, accessibility, security, purchase/restore or platform-specific validation. Select the smallest meaningful check for the reported concern, then the project's required release checks. Keep known gaps visible so a downstream submission packet does not turn limited test coverage into an unqualified pass.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Crash symbols do not match build | Obtain matching symbols or retain the stack as unsymbolicated/uncertain; do not invent function attribution. |
| Old feedback is attributed to a newer build | Rebind the report to its actual build and verify whether the newer candidate reproduces or fixes it. |
| A beta build expires while release preparation continues | Identify the replacement build and re-evaluate only affected eligibility/access evidence before distributing it. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Version/build/symbol and reproduction context.
- Confirmed versus uncertain finding classification.
- Fix and verification tied to the intended replacement.
- Current eligibility/expiry status and retained gaps.

A passing beta smoke test is not a comprehensive security, accessibility or policy certification. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_testflight` — [TestFlight overview - Test a beta version - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/).
- `src_delivery_fastlane_pilot` — [pilot - fastlane docs](https://docs.fastlane.tools/actions/pilot/).
