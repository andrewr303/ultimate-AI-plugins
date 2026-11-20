# Review widgets, App Clips and shared data as separate surfaces

## Start with the extension topology

List each widget, App Clip, notification service/content extension and other executable target. Record its bundle identity, supported platforms, shared containers, capabilities, resource files and data sources. An extension is not simply another view inside the main app process; it can expose data and execute with a different lifecycle, permission context and user-visible surface.

The observed review guidance requires widgets, extensions and notifications to relate to the app's content and functionality. It separately constrains advertising placement and states that App Clip functionality must be present in the main app. Do not turn a lightweight extension into an unrelated marketing surface or claim a hidden main-app feature exists merely because an App Clip implements it.

## Data and permission inputs

Map which values are shared, cached or fetched and why they are safe for the selected surface. A backend account token, user-specific response or protected record does not become public because a widget needs a snapshot. Identify sign-out/account-change behavior, shared-container readers/writers and how stale data is removed or redacted.

Review required manifest resources and purpose strings for every relevant executable and SDK. Do not assume the main app's privacy file covers an embedded executable's own covered API use. Inspect the archived target rather than only the source directory. Capability and provisioning configuration should match the actual bundle and intended use; adding an entitlement indiscriminately is not a review fix.

## Workflow

1. Establish the app's purpose and map each extension feature to it.
2. Inspect target membership, embedded products, data-sharing configuration and the final resource tree.
3. Classify every displayed field and action for lock-screen, signed-out, shared-device and stale-cache conditions.
4. Verify shared state uses an intentional supported storage boundary; do not assume process memory or arbitrary database access is coordinated.
5. Route URLs/actions through validated app/domain authorization, with a fallback for deleted entities or a different account.
6. Rebuild the affected targets and test the actual product surfaces before marking a claim satisfied.

Keep developer tooling and platform fallback behavior explicit. If the host cannot run the widget/App Clip on a suitable Apple runtime, complete source and artifact inspection and name the pending tests. A screenshot of a preview is not proof of real shared-container, signing or locked-device behavior.

## Useful failure cases

Exercise a fresh install, a signed-out account, account switching, missing shared data, a stale network response and an app update with an old cached snapshot. Test that removing/restricting access in the main app changes the relevant extension exposure. Verify a deep link to a deleted record and an action initiated from another scene/device state.

Check that a required resource omitted from one target remains a blocker even if the main app report looks valid. A feature that appears only behind a hidden remote flag needs accurate review disclosure. Advertising or unrelated promotional content should be evaluated against the exact current surface rule instead of assumed permitted by a global ad SDK configuration.

## Evidence and status

Record target/configuration, bundle identity, source section/date, shared data class and observed cases with sanitized artifacts. A proven exposure, unrelated function or missing required resource is a blocker. Unverified capability, data or device behavior is unknown. Not applicable must identify the absent target/surface or actual rule limitation. Satisfied evidence applies to the built targets and tested scenarios, not every future device or privacy claim.

The output should let a reviewer trace a main-app feature through its extension, data and authorization boundary without revealing customer records. Keep local readiness, valid signing, successful upload and App Review approval separate.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_adding_manifest` — [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- `src_policy_privacy_manifest_current` — [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- `src_policy_purpose_strings` — [5.1.1(ii) - Write clear purpose strings - Guideline reference - App Review - Help - Apple Developer](https://developer.apple.com/help/app-review/guideline-reference/5-1-1-purpose-strings)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
