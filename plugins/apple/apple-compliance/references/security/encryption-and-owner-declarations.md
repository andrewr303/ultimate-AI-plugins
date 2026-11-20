# Determine encryption/export declarations from product facts

## Separate the implementation fact from the declaration

Apple's export-compliance overview asks developers to determine requirements when an app uses, accesses, contains or incorporates encryption, including crypto functionality supplied by the operating system. That does not mean every app needs the same document, and it does not mean a common transport library automatically proves an exemption. The determination depends on real implementation and distribution facts.

Inventory encryption-related features/libraries, operating-system crypto use, proprietary/nonstandard functionality if present, intended regions, existing approved documentation and the owner responsible for classification. Do not export keys or proprietary secret values to build that inventory. A name, Boolean or copied sample answer is not a regulatory analysis.

## Prepare the current determination

1. Resolve the selected app/build and distribution regions, including beta/review lanes affected by missing encryption information.
2. Read the current Apple determination questions and the owner-confirmed technical facts. Keep an unknown answer unknown rather than choosing the fastest submission path.
3. If actual documentation is required, collect the real owner-approved material and the appropriate role/account lane.
4. Prepare the required documentation or attachment and review its app identity, scope and current status.
5. Set the corresponding app declaration only when supported by the determination, then rebuild/inspect the relevant artifact as needed.
6. Verify the remote/document/build state after an authorized operation and report the furthest observed stage.

Apple points developers to the relevant government export/import authorities and assigns responsibility for the determination to the developer. Do not substitute this plugin, a passing unit test or an App Store field accepting input for the required owner/legal decision. If a specific regulatory fact is missing, identify that fact and continue independent technical preparation rather than creating a blanket compliance statement.

## Common traps

Do not set an encryption-exemption Boolean to false simply because a build is blocked. Do not assume “uses only HTTPS” settles every question, or claim use of a well-known algorithm eliminates all documentation obligations. A prior approved document may not cover a changed product, region or cryptographic feature. A placeholder test document must never be represented as the publisher's real authorization.

The documentation may describe expected review timing. Treat that as an observation of a process, not a promised deadline or approval SLA. An upload receipt, document submission and document approval are separate evidence states; so are approval of export information and App Review acceptance of the product.

## Safe verification

Use sanitized fixtures for no determination, owner-confirmed no-documentation outcome, required-but-missing documentation and an approved document attached to the wrong build. Check that the workflow preserves unknowns and blocks only dependent actions. Do not upload an artificial compliance document just to test an account API.

Inspect the built app's relevant declared values without printing sensitive contents. Confirm that the account role used supports the actual operation, rather than treating signing identity, App Store Connect role and API credential as interchangeable. If a native environment or authenticated account is unavailable, finish the local evidence packet and identify the exact pending check.

## Deliverable

Provide the implementation inventory, owner-confirmed determination, current primary source, selected app/build/regions, document state and remaining dependencies. Use satisfied by evidence only for the scope actually established; a real missing required item is a blocker; unresolved technical/regulatory facts are unknown; and not applicable needs the documented reason for that feature/lane. The result should make the next review action concrete without making factual or legal assertions on the owner's behalf.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_export_overview` — [Overview of export compliance - Manage app information - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance/)
- `src_policy_encryption_docs` — [Determine and upload app encryption documentation - Manage app information - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-app-information/determine-and-upload-app-encryption-documentation/)
- `src_policy_beta_release` — [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
