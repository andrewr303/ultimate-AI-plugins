# Reconcile real data flows with privacy labels

## Start with what leaves the device

Build the privacy answer from the actual feature and service behavior. List first-party and third-party destinations, data types, purposes, identity linkage, tracking uses and retention. Include account and app-functionality data, not just advertising or analytics. Apple defines collection for its labels and has specific conditions for optional disclosures; a familiar legal or engineering term does not replace that definition.

Use the selected app/extension/SDK versions. A vendor document, manifest or code search is one evidence surface. Combine those with product-owner facts and relevant runtime observations; do not infer a universal “no collection” answer from an empty manifest, an offline screen, a privacy-focused SDK description or an unavailable report.

## Required inputs and evidence owner

For each flow record the source feature, receiving service, fields, time retained, purpose, linkage to an account/device and further sharing. Identify who can confirm service-side behavior. Describe data using categories and synthetic examples rather than copying raw personal records into the review packet. If a backend or SDK owner cannot confirm a fact, mark that item unknown and continue the checks that do not depend on it.

## Reconcile the declarations

1. Inventory collection by feature, including optional feedback, support, diagnostics, authentication and external SDKs.
2. Classify each type using the current Apple label definitions and all relevant purposes.
3. Evaluate linkage and tracking from actual joining/sharing behavior. Hashing or pseudonymization alone does not settle those answers.
4. Apply an optional-disclosure exception only when every documented criterion fits. Infrequent user-supplied support data and ongoing post-permission collection are different cases.
5. Compare the map with bundled manifests, the generated archive privacy report, privacy-policy statements and App Store Connect responses.
6. Resolve differences in the implementation or facts, then update the owner-controlled declaration. Do not choose whichever answer produces fewer labels.

The app's manifest and an SDK's manifest have separate collection responsibilities. The aggregation helps the app owner understand the combined product, but it does not replace accurate store responses or the owner's responsibility for integrated code. A declared SDK list is not an exhaustive network data-flow audit.

## Changes and unknowns

Repeat the affected review when a feature, endpoint, SDK, server retention rule or data purpose changes. Apple permits updating privacy responses without necessarily shipping a binary update, but the right operational lane still depends on the actual remote state and user's request. A prepare-only task can produce the corrected answer set without publishing it.

Treat an identified undisclosed flow as a blocker for the relevant truthful declaration. Treat unsupported vendor retention or onward-sharing answers as unknown. Not applicable requires actual evidence that the data type/flow does not apply. Satisfied evidence should name the reviewed scope and version; it must not become a blanket statement that all privacy law or all future versions are covered.

## Verification cases

Exercise a clean account, existing account, optional support submission, consent withdrawal, sign-out and a changed SDK configuration. Verify expected destination/payload classes without exposing customer contents. Add a fixture in which a field is collected solely for app functionality, one in which a “feedback” flow is routine core functionality, and one in which a derived identifier is joined with an account. The expected outcome is an accurate evidence map and explicit unresolved facts, not an automatic marketing claim.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_app_privacy_details` — [App Privacy Details - App Store - Apple Developer](https://developer.apple.com/app-store/app-privacy-details/)
- `src_policy_privacy_data` — [Describing data use in privacy manifests](https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests)
- `src_policy_user_privacy_data_use` — [User Privacy and Data Use - App Store - Apple Developer](https://developer.apple.com/app-store/user-privacy-and-data-use/)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
