# Approval, release and territorial availability

Read the [operating contract](../operating-contract.md). Report the furthest verified distribution state accurately.

## Establish the inputs

- Approved app/platform version and configured release mode.
- Authorized release timing, timezone and storefront scope.
- Current agreement/availability/dependency state.
- Existing phased/scheduled/manual release observations.
- Evidence of actual storefront availability.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Inspect the configured manual, automatic or scheduled release policy and any phased/territorial product requirements.
2. After approval, execute public release only if authorized and verify the selected platform version and regional availability.
3. Distinguish accepted review, Pending Developer Release, processing and actual availability. Preserve the selected schedule/timezone and report propagation uncertainty.

### Approval does not necessarily publish the app

Inspect the selected platform version and configured manual, automatic or scheduled release option. A version can be approved while remaining Pending Developer Release or waiting for another event. Release is platform-specific: an iOS version changing state does not establish that a macOS or other platform version also released.

Preserve the user's intended date/time and timezone. An automation default or immediate-release option must not silently replace a planned launch. If a schedule or availability prerequisite is unresolved, retain that fact while finishing independent preparation. Changing pricing, agreements or countries is not an implied repair for generic submission work.

### Verify the consumer-facing state

Read the observed release/processing state and relevant storefront availability rather than equating a successful API response with public availability. Propagation can be asynchronous. Keep the exact version/build and country/region context in the handoff, with any current source timing as an observation rather than a permanent service-level guarantee.

For an authorized launch, execute the smallest intended release action and capture its receipt/status. If an unexpected availability condition appears, diagnose the specific metadata, agreement, rating or program requirement instead of generalizing it to all territories. A rollback may involve a new release or removal action with its own consequences; do not promise that reverting source code reverses an already distributed app.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Approval remains pending manual release | Report approval and pending manual release separately; perform the release only within matching authorization. |
| One platform releases while another remains pending | Inspect and report each selected platform actual state; do not infer synchronized publication. |
| Storefront is unavailable because a separate account/metadata condition is missing | Identify the country/platform-specific prerequisite and owner before changing distribution or declarations. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Release policy, intended schedule/timezone and authority.
- Exact release action and receipt/current status.
- Platform/storefront availability actually observed.
- Propagation uncertainty and separate unresolved account facts.

Changing pricing, countries, agreements or public release timing does not follow from generic submission preparation. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_release_options` — [Select an App Store version release option - Manage your app's availability - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/select-an-app-store-version-release-option/).
- `src_delivery_review_status` — [App and submission statuses - App information - Reference - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/reference/app-information/app-and-submission-statuses/).
- `src_delivery_asc_workflow` — [App Store Connect workflow - Get started - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-workflow/).
