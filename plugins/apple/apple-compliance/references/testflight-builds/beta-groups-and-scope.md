# TestFlight groups, invitations and beta review

Read the [operating contract](../operating-contract.md). Distribute only to the selected testers/groups and preserve the requested endpoint.

## Establish the inputs

- Intended internal/external groups and exact build.
- Current processing/eligibility/beta-review state.
- Required test information and reviewer access.
- Authority for invitations, notifications and group changes.
- Tester-data handling and expiration/criteria policy.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Inspect internal/external group configuration, eligible build state, required beta test information and current beta review status.
2. If upload-only was requested, stop at its verified state. Resolve whether group assignment, external review, tester invitation or notification is authorized.
3. Observe actual group/build association and tester access after an authorized distribution; protect tester contact details and feedback media.

### Resolve distribution scope explicitly

TestFlight is a distribution/testing workflow with its own review and group configuration. Identify whether the user requested upload only, assignment to a known group, internal testing, external testing, invitations or notifications. These are separate effects. Existing authorization for one should not be repeatedly requested, but it should not be expanded to the others by implication.

Inspect the selected build and group relationship, current eligibility, beta information and review state. Current Apple limits and review conditions can change, so resolve them from the relevant official page when needed rather than embedding a universal count or lifetime in the plugin. Distinguish App Store Connect users with internal access from externally invited testers.

### Verify access without exposing people

After an authorized distribution, observe the intended group/build association and actual eligible testing state. An invitation request being accepted is different from the tester accepting it or successfully installing a build. Protect tester addresses, feedback screenshots and device reports in logs and handoffs.

Avoid broad import/export or group cleanup as a default repair. A successful upload can still require processing, beta review, test information, encryption answers or access corrections. Diagnose the concrete blocker without publishing to another group as a workaround. Production App Review remains a separate requested endpoint.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Internal and external review paths differ | Select the appropriate internal/external lane and identify the real prerequisite without conflating review types. |
| First external build requires action although upload succeeded | Report the observed beta blocker and complete independent preparation; do not label upload failure when upload succeeded. |
| Wrong group or unintended notification | Stop the affected mutation, resolve the intended group/notification scope and repair only authorized associations. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Build/group identifiers and requested distribution endpoint.
- Observed eligibility, test information and beta-review state.
- Invitations/notifications actually sent under authority.
- Privacy-safe access result and unresolved tester actions.

Beta review and App Store review are separate; never guarantee acceptance or send invitations from a generic preparation task. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_testflight` — [TestFlight overview - Test a beta version - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/).
- `src_delivery_fastlane_pilot` — [pilot - fastlane docs](https://docs.fastlane.tools/actions/pilot/).
- `src_comp_delivery_code_039` — [expo/eas-cli@bcb5d96ea825:packages/eas-cli/src/submit/ios/IosSubmitCommand.ts](https://github.com/expo/eas-cli/blob/bcb5d96ea8257747e48ebe2a0ac68f51b70ddcf4/packages/eas-cli/src/submit/ios/IosSubmitCommand.ts).
