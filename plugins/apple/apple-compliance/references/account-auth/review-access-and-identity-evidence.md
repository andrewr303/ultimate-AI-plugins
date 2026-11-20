# Give reviewers representative access with protected test identities

## Review access is part of the submitted product

A working binary is not reviewable when the backend is disabled, the test account expires or a critical role is inaccessible. Apple's completeness and review-information guidance asks for the information needed to exercise the actual functionality. Treat the release build, backend configuration, review identities, purchase states, hardware and regional features as one review-access contract.

Identify the target app/platform/build and the requested stage before preparing access. A preparation task can create a concrete review packet without uploading or submitting anything. When an external stage is already authorized, carry the resolved identity and evidence into that stage rather than asking again for the same authority.

## Build the review packet

Record the app's concept, business model, intended audience and significant new or changed functionality. List the tested devices/OS versions, external services and any special setup needed to reach the core tasks. Distinguish an actual regional difference from a developer test flag. Explain features that require hardware, location or unusual environments using the current review guidance.

Use representative synthetic accounts and data that allow the reviewer to test the main roles. Where relevant, include an account state that makes the full purchase flow reviewable, such as an expired subscription, rather than only an already-entitled account. Confirm that authentication codes and credentials remain usable for the expected review process. Do not publish those credentials in the repository, plugin package, PR body or normal logs; supply them through the appropriate secure review fields.

## Execution sequence

1. Start from a fresh release installation and follow the exact proposed reviewer steps.
2. Verify every named account/role can access its intended feature without an undocumented administrator action.
3. Test backend availability, relevant regions, feature flags and required hardware against the release environment.
4. For sensitive or regulated contexts where a demonstration mode is appropriate, make it exhibit the full functionality with demonstration data and establish the required review approval/conditions. Do not use a fake success screen to conceal a missing service.
5. Attach actual rights or regulated-field documentation when required, using the owner's evidence rather than a sample certificate.
6. Record the tested path and current unresolved prerequisites, then proceed to the authorized submission lane with the correct build and notes.

## Avoid access that changes under review

A one-time login code consumed during the author's test can make the later review impossible. A credential reset, region firewall, production cleanup job or narrow service uptime window can cause the same defect. Give the access owner a concrete validity requirement and verify it without printing secrets. If the review environment intentionally differs from production, explain the difference accurately rather than claiming identical behavior.

Protect accounts with bounded privileges and synthetic content. Do not give reviewers a production superuser or customer database merely to avoid writing proper test steps. Review access should demonstrate the actual feature while respecting the product's authorization boundary.

## Evidence and status

Test login, wrong/expired credentials, each important role, subscription access, account deletion and a fresh-device route. Record the release build, service configuration class, sanitized account labels and observed outcomes. A video or screenshot supports only what it shows; it cannot establish that the backend remains functional or that the reviewer can repeat the path.

A confirmed inaccessible core task is a blocker. Missing hardware, unverified credential duration or absent regulated documentation is unknown/needs evidence. Not applicable must explain why that access is unnecessary. Satisfied should identify the paths actually exercised. Keep review-access readiness separate from Apple acceptance and never report a prepared packet as a submitted or approved app.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_complete_review` — [Provide information for a complete review - Before submitting for review - App Review - Help - Apple Developer](https://developer.apple.com/help/app-review/before-submitting-for-review/complete-review)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_app_review_overview` — [App Review - Distribute - Apple Developer](https://developer.apple.com/distribute/app-review/)
- `src_policy_account_deletion` — [5.1.1(v) - Offering account deletion in your app - Guideline reference - App Review - Help - Apple Developer](https://developer.apple.com/support/offering-account-deletion-in-your-app/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
