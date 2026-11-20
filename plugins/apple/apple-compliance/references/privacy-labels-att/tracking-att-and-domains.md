# Connect tracking behavior, ATT and declared domains

## Classify the use, not the library name

Apple's tracking definition concerns linking user or device data with data from other companies' properties for specified advertising/measurement purposes, or sharing with data brokers. Not every analytics event is tracking, and an SDK can track even when the app does not intentionally use its advertising feature. Determine the actual configuration, data joins and downstream use before deciding whether ATT applies.

Collect the app/SDK data-flow map, tracking-domain declarations, authorization-state handling and relevant service/vendor facts. A privacy label, ATT prompt and `NSPrivacyTracking` declaration describe related but different aspects. None substitutes for the others. A consent screen drawn by the app does not replace the supported system permission where required.

## Evaluate the permission path

1. Identify any covered tracking or advertising-identifier use and when the first relevant data can leave the device.
2. Confirm the target has the truthful usage description and supported authorization implementation for its SDK/deployment target.
3. Verify behavior before authorization, after grant, after denial/restriction and after a later settings change. Do not assume presenting the prompt means permission was granted.
4. Compare actual tracking destinations with the privacy manifest domain list and the product's declared data uses.
5. Remove or defer disallowed tracking behavior; do not substitute fingerprinting, another persistent identifier or a server-side join to evade the choice.
6. Reconcile the store label and policy text after changing the implementation or SDK behavior.

Apple's documentation describes enforcement associated with declared tracking domains when permission has not been granted. Inspect resulting network errors without treating every unreachable endpoint as proof of a tracking-policy issue. Preserve the distinction between transport failure, permission state and an inaccurately classified domain.

## Context and user choice

Explain what the product actually does in a purpose string, using accurate localized language. Do not gate purchased functionality, basic content or compensation on agreeing to tracking. A pre-permission explanation should not manipulate the choice or obscure the system prompt. Verify the actual product's behavior rather than relying on a screen mockup.

The current privacy support page contains region- and OS-specific changes to ATT presentation and reprompt behavior. Those observations must be checked against the live source and installed SDK when the feature is implemented. Do not turn a newly announced capability into a universal “reprompt annually” rule or hardcode a future OS version as the app's deployment default.

## Evidence and failure cases

A useful test records the authorization state, the data flow that is enabled/disabled, target version and expected domain classes without storing advertising IDs or personal payloads. Cover a third-party SDK starting before the user's choice, a server joining a pseudonymous identifier to cross-company data, and a settings revocation while the app is running.

Use blocker for a demonstrated prohibited flow, unknown for unverified downstream use or unresolved applicability, and not applicable only with an evidence-backed definition match. A structural linter can check keys and types; it cannot prove that an SDK honors consent. Finish with the concrete implementation/declaration changes and the real device/runtime checks still required.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_user_privacy_data_use` — [User Privacy and Data Use - App Store - Apple Developer](https://developer.apple.com/app-store/user-privacy-and-data-use/)
- `src_policy_att` — [App Tracking Transparency](https://developer.apple.com/documentation/apptrackingtransparency)
- `src_policy_privacy_manifest_current` — [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- `src_policy_privacy_required_reasons` — [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
