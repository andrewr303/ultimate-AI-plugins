# Delete accounts and data without confusing billing cancellation

## Define the user's requested outcome

Account deletion, temporary deactivation, consent withdrawal, local logout and subscription cancellation are different actions. Apple's account-deletion guidance applies when the app supports account creation, including automatically created or guest accounts. The ability to hide a profile, disable sign-in or send a support message is not automatically the required deletion capability.

Map the full account graph: first-party records, user-generated content shared with others, linked providers, device tokens, extension snapshots, server caches and downstream processors. Obtain the real retention obligations from the product owner. Do not invent a legal need to retain everything, or promise immediate erasure from systems whose deletion and backup behavior has not been established.

## Prepare a transparent flow

Make in-app initiation easy to find, normally near account settings. Confirmation and proportionate identity verification can prevent accidental or unauthorized deletion, but unnecessary friction can defeat the flow. If a website completes the action, link directly to the relevant completion page rather than sending the person to a generic home/help page. Read platform-specific alternatives, such as tvOS, in the current guidance before applying them.

Apple describes a customer-service exception for certain highly regulated industries. Do not apply it to every app because support exists. An ordinary app should not require a phone call, email or chat as its default deletion route. A lawful retention fact or a regulated-service exception needs specific evidence and a clear explanation to the person.

## Implement the lifecycle

1. Verify the current account and requested scope without exposing the deletion route to another account.
2. Confirm intent and describe the consequences, retained information and expected completion time accurately.
3. Execute or enqueue the supported deletion operation with an auditable state. Repeated requests must not delete another account, repeatedly charge a service or appear successful before work is accepted.
4. Revoke or unlink provider credentials as required by the actual provider flow; Sign in with Apple has a documented token-revocation and account-change path.
5. Remove or de-identify associated records according to confirmed requirements, including relevant shared UGC. Expire device tokens, sessions and private extension snapshots.
6. Report pending, completed or failed state truthfully and provide the promised confirmation when completion occurs.

## Keep billing distinct

Deleting the app or app account does not itself cancel an Apple-billed auto-renewable subscription. Explain continuing billing accurately and offer the supported subscription-management path. Do not tell a person that a local account flag guarantees cancellation at Apple. Check the current deletion guidance before conditioning deletion on a subscription action; do not create a coercive or impossible loop.

The current subscription state may be known through server notifications/status APIs, but a cached state can be stale. Keep the billing explanation and entitlement reconciliation separate from the actual deletion job. A receipt or transaction identifier is not authorization to erase another person's account.

## Failure cases and evidence

Test a guest account, private-relay login, an expired session, wrong-account request, active subscription, delayed processor deletion, repeated request and partial failure. Verify that retained data follows the disclosed reason and that completed deletion cannot be reversed merely by a late background synchronization event. Preserve synthetic evidence of state transitions rather than customer records.

Use blocker for a concrete missing/incorrect flow, unknown for unconfirmed retention or downstream deletion, not applicable only with evidence that account creation does not occur, and satisfied for the specific end-to-end behavior actually demonstrated. Finish the authorized implementation and identify the exact remaining owner decision instead of supplying a fabricated retention policy.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_account_deletion` — [5.1.1(v) - Offering account deletion in your app - Guideline reference - App Review - Help - Apple Developer](https://developer.apple.com/support/offering-account-deletion-in-your-app/)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_subscriptions` — [Auto-renewable Subscriptions - App Store - Apple Developer](https://developer.apple.com/app-store/subscriptions/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
