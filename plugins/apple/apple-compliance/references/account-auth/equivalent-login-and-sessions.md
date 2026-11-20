# Apply the login-service rule to the real account model

## Determine which rule actually applies

Guideline 4.8 is more specific than “every app needs Sign in with Apple.” It describes an equivalent privacy-preserving login option for covered third-party/social primary-account login and lists exceptions. Start with the account a person uses to identify themselves and access the app's services. Distinguish an organization's own sign-in, an existing enterprise/education account, a specific third-party-service client and consumer social login rather than treating every authentication button as the same business model.

The observed rule describes limited name/email collection, private-email capability and no advertising interaction collection without consent for the equivalent service. Verify the current wording and applicability before choosing an implementation. Do not infer an exception from the product's name, a B2B sales page or an SDK being installed.

## Inputs and decisions

Map registration, login, account linking, session refresh, logout and deletion. Record providers, requested claims, the primary account boundary, supported platforms and any actual exception evidence. Identify whether non-account functionality should remain accessible without login. Missing product facts remain unknown while implementation and test work continues.

For Sign in with Apple, inspect the actual app and service configuration, target capabilities, verified identity-token handling and supported revocation/account-change processing. A client result is not an automatic grant of access to a server account. Use the existing server's authorization design and validate the relevant current provider contracts. Do not copy demonstration credential-display code from an official sample into production.

## Build a coherent lifecycle

1. Decide whether the covered login rule applies and record the source section or precise exception.
2. Present the equivalent option as a real usable choice when required, not a disabled placeholder or a route that loses the user's work.
3. Establish identity on the server using the supported validation flow, then authorize the actual app account and tenant.
4. Link accounts only through an intentional verified process. A matching or private-relay email alone is not permission to merge unrelated accounts.
5. Scope sessions, caches, widgets and extension access to the current account. A logout or revocation must not leave the previous account's private data exposed through a second surface.
6. Connect deletion to the actual account/provider lifecycle and preserve clear error/recovery states.

## What to test

Exercise initial registration, repeat login, cancellation, unavailable provider, private email, changed/revoked authorization, an existing account and an account-linking conflict. Confirm that a denied permission or absent optional profile claim does not accidentally create a privileged account. Test app and server failure independently; a backend timeout after account creation needs state reconciliation rather than creating another account on retry.

Verify what is displayed, persisted and sent to the server using synthetic users. Keep identity tokens, authorization codes, passwords and actual review account credentials out of logs, fixtures, screenshots and source control. Record validation method and sanitized identity relationships rather than raw credentials.

## Classify and hand off

A demonstrated missing required equivalent option or insecure account-binding path is a blocker. Unverified exception eligibility or provider configuration is unknown. Not applicable needs a specific supported account-model explanation. Satisfied evidence identifies the tested build, flow and server scope; it does not assert that every legal or identity requirement is satisfied.

The final review packet should include the applicability decision, real login paths, tested cancellation/revocation cases and exact unresolved owner facts. If the user requested implementation, complete the authorized fix and meaningful tests; do not stop at proposing a provider or describing a checklist.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_siwa_implementation` — [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- `src_policy_account_deletion` — [5.1.1(v) - Offering account deletion in your app - Guideline reference - App Review - Help - Apple Developer](https://developer.apple.com/support/offering-account-deletion-in-your-app/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
