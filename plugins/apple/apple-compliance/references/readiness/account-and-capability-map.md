# Account, app and capability map

Read the [operating contract](../operating-contract.md). Resolve the actual organization, app record, platform, version and operation-specific authority before a release action.

## Establish the inputs

- Publisher/team and the configured credential provider.
- App Store app identifier, bundle identifier, platform and version.
- Requested operation and current account role/app access.
- Existing signing/auth configuration and ownership of any repair.
- Storefront/channel and relevant agreement or program eligibility.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Inventory the existing account/provider context without printing credentials. Resolve the bundle ID to the intended App Store app and record canonical app/platform identifiers.
2. Choose the requested endpoint: review-only, local preparation, upload, beta distribution, submission, or release. Identify which role and auth method can perform that operation.
3. Separate missing product/legal facts from missing credentials and technical failures. Continue independent local checks while a dependent fact is unresolved.

### Resolve identity before capability

A display name, repository name or bundle identifier alone is not the full remote target. Establish which configured account is in use, which team/provider it selects and which app record is visible. A person can belong to several organizations and have different access to each app. Record safe identifiers in the evidence packet; keep key material, account session cookies and tester contacts out of it.

Treat permission failure as a diagnostic, not an invitation to rotate credentials, recreate an app or switch teams. Determine whether the operation requires a role the current identity lacks, whether app-specific access is missing, whether the token/key is expired or revoked, or whether the tool is using a different authentication mechanism than expected. Read-only inventory can continue while the correct owner resolves a privileged prerequisite.

### Match credentials to the operation

App Store management API keys, In-App Purchase server keys, local signing identities, notarization credentials and app-user authentication are different capabilities. A token that can query one API does not establish permission to upload, create certificates, submit for review or sign agreements. A Swift management SDK compiling on iOS does not make it appropriate to ship administrative private keys in a client.

Use the existing supported authentication integration when possible. Discover readiness without printing values or triggering an unnecessary login. If a CLI uses a web session for an unsupported API, identify that boundary and its current documented requirements rather than silently promoting it to a universal supported API lane. Credential creation and role changes should be concrete, scoped repairs only when authorized.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Wrong Apple team with matching display name | Stop the dependent mutation, show the resolved team/app mismatch, and keep independent local checks moving. |
| Insufficient role for submission although upload is permitted | Report the specific missing capability and owner; do not infer that every account operation is blocked. |
| Expired/revoked key or inaccessible app | Preserve the error classification and selected identity; do not dump tokens or repeatedly reauthenticate. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Resolved account/team/app/platform/version identifiers.
- Requested endpoint and permitted mutation lane.
- Role/capability observations and missing prerequisite owner.
- Authentication method and source/help version, without secret values.

Administrative automation keys do not belong in a distributed iOS app; existing authorization persists within its scope. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_asc_workflow` — [App Store Connect workflow - Get started - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-workflow/).
- `src_delivery_asc_roles` — [Overview of accounts and roles - Manage your team - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-your-team/overview-of-accounts-and-roles/).
- `src_delivery_fastlane_api` — [Using App Store Connect API - fastlane docs](https://docs.fastlane.tools/app-store-connect-api/).
