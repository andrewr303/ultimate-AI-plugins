# Verify purchase, restore and shared entitlement behavior

## Choose the actual API and ownership boundary

Inspect the minimum OS versions, resolved StoreKit implementation, configured products and existing server integration. Apple's API-selection article distinguishes modern Swift-based signed transactions from the original receipt/payment-queue API and states that the original API is deprecated. The separately reviewed purchase/restoration article is a legacy SKPaymentQueue sample; its title does not make it StoreKit 2 guidance.

Do not migrate an established implementation incidentally during a policy review. If a change is required, route it through the app's supported-target and test strategy. Keep the payment provider, transaction verification, durable fulfillment and app account authorization as separate boundaries. A purchase completion callback is not proof that every backend entitlement and user-visible screen is correct.

## Inputs to reconcile

Use the real product identifiers, product types, subscription groups/levels, availability, server verification design, app-account mapping and restore/manage UI. Identify the authoritative entitlement state and how the app handles delayed or repeated events. Store/service credentials belong on the appropriate backend or configured tool, never in the shipped app, plugin examples or diagnostics.

## Workflow

1. Fetch and display the currently configured product information through the supported API. Handle unavailable products and storefront limitations explicitly.
2. Process the transaction according to the actual API, including verification and any required finish/acknowledgment semantics. Design retry/recovery around durable fulfillment rather than assuming one callback runs once.
3. Bind the resulting access to the intended authorized app account. Do not allow possession of an arbitrary transaction identifier to claim another account's purchase.
4. Reconcile asynchronous server events with app refresh and current status. Duplicate, delayed, reordered or missed events must not double-grant access or revive a revoked entitlement.
5. Provide the appropriate sign-in, restore and subscription-management paths. Explain the behavior for consumable and restorable product types accurately.
6. Verify that legitimate users can access what they paid for on the supported devices/platforms while still following each platform's purchase-presentation rules.

A unified backend can reduce duplicated account/entitlement logic across web and Apple clients. It cannot make every billing route policy-equivalent. Keep product classification and storefront eligibility evidence alongside the technical entitlement design.

## Test lifecycle states, not only successful checkout

Use the supported sandbox or local StoreKit testing setup and distinguish it from production. Exercise purchase success, user cancellation, pending/deferred state, failure, relaunch before fulfillment completes, duplicate delivery, restore, expired subscription, upgrade/downgrade and refund/revocation. Verify a signed-out or different-account case rather than assuming the current device account and app account always match.

A mocked server response can prove app state handling, but not Apple transaction authenticity or real storefront configuration. A sandbox purchase can prove the tested lane, but not every production product or commercial eligibility claim. Record those boundaries and the exact environment/product/build used.

## Evidence and outcome

Keep sanitized transaction/event references and observed states without raw receipts, tokens or customer payment data. A demonstrated lost purchase, duplicate grant, broken restore or cross-account claim is a blocker. Unverified product availability, server status or lifecycle behavior stays unknown. Not applicable must identify the product type or feature absent from scope. Satisfied evidence should name the exercised lifecycle and supported API, not say merely “SDK installed.”

Finish with the implemented repair or preparation packet, real checks and remaining target-environment work. Do not report App Store approval, full commercial compliance or live fulfillment from source inspection alone.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_storekit_selection` — [Choosing a StoreKit API for Apple In-App Purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- `src_policy_storekit_purchase` — [Offering, completing, and restoring Apple In-App Purchases](https://developer.apple.com/documentation/storekit/offering-completing-and-restoring-in-app-purchases)
- `src_policy_subscriptions` — [Auto-renewable Subscriptions - App Store - Apple Developer](https://developer.apple.com/app-store/subscriptions/)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
