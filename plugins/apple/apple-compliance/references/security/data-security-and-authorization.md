# Review data security at real app and service boundaries

## Identify the concrete exposure

Start with the account, data and action the feature protects. Guideline1.6 describes appropriate security for collected user information; privacy sections separately address consent and sharing. A secure transport connection, signed client payload, successful login or valid app signature each proves only part of the system. None independently authorizes access to another account or makes the declared data practice true.

Map local storage, shared extension data, server requests, administrative services, external SDKs and any AI/service processing. Keep sensitive values out of logs and ordinary evidence. Identify the trust boundary before proposing a new framework or a blanket hardening checklist. Preserve a working existing provider/infrastructure unless the task actually requires a migration.

## Inputs

Use the actual data-flow inventory, authentication and authorization code, service roles, target capabilities, supported SDK/deployment versions and release configuration. Obtain service-side collection/retention facts from their owner. Read relevant configurations without printing credential values or dumping environments. A private administrative signing key belongs outside the app; the user-facing client must not be treated as a trusted administrator merely because it is signed.

## Review and repair sequence

1. Identify the user-visible task and the specific private data or mutation at risk.
2. Follow the request from app or extension to server authorization and storage. Validate account/tenant/entity ownership where the action actually executes.
3. Inspect credential/session lifetime, logout, revocation, retry and account-switch behavior. A cached response or extension snapshot must not expose a previous account's data.
4. Reconcile data collection/sharing with the actual permission and privacy declarations. The observed guideline explicitly discusses third-party sharing, including third-party AI; service utility is not a substitute for required disclosure/permission.
5. Make the smallest correction to the demonstrated boundary and update relevant resources/tests.
6. Verify the affected paths and report the limits of mocks, static inspection and the available runtime.

For intents or other non-screen entrypoints, do not assume the main app's login UI protects the operation. For a backend call, a transaction ID, entity ID, push token or locally authenticated device is not by itself permission to access an arbitrary account. Test negative authorization behavior as deliberately as successful access.

## Verification matrix

Cover unauthenticated, expired/revoked session, wrong account/tenant, removed entity, repeated/late request and changed account state. Test error/log redaction with synthetic secrets and personal-data classes. If transport or a framework trust behavior is in scope, inspect the supported implementation and current documentation before changing defaults; do not disable verification merely to silence a connection error.

A finding should state the realistic trigger, affected boundary, observed outcome and proportional remedy. Do not report a security bug solely from a keyword or claim a penetration test from a static grep. Conversely, an unverified server permission should remain unknown even when the Swift view appears correct.

## Status and handoff

Use blocker for a demonstrated unauthorized exposure/mutation or a concrete required control missing from the selected feature. Use unknown for uninspected service behavior or unresolved data facts. Not applicable needs a bounded reason. Satisfied evidence identifies the exact path and negative/positive cases tested, not a guarantee that the app is secure or legally compliant.

Complete the authorized implementation and relevant tests. Do not rotate credentials, revoke team assets, send private source to a remote scanner or change production permissions as routine diagnosis. A source review can prepare those actions concretely, but the actual requested authority and target must govern execution.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_app_privacy_details` — [App Privacy Details - App Store - Apple Developer](https://developer.apple.com/app-store/app-privacy-details/)
- `src_policy_user_privacy_data_use` — [User Privacy and Data Use - App Store - Apple Developer](https://developer.apple.com/app-store/user-privacy-and-data-use/)
- `src_policy_appintent_authentication` — [authenticationPolicy](https://developer.apple.com/documentation/appintents/appintent/authenticationpolicy)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
