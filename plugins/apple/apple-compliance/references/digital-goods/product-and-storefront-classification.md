# Classify products before choosing the payment route

## Ask what is being sold and consumed

Start with the actual product or service, not the backend payment provider. A digital unlock, subscription, physical delivery, enterprise service, reader-content account and real-time person-to-person service can fall under different current rules. An app can contain more than one category, so classify each offering and the route used to buy or access it.

Record the app platform, storefront, distribution channel, audience, intended purchaser, consumption location and current agreement/entitlement facts. A company calling itself B2B does not automatically make all consumer sales enterprise services. A social app containing video does not automatically become a reader app. A web account or shared Node.js service does not create a universal in-app billing exception.

## Use a conditional decision table

For each product, identify the current guideline section and any exact exception. The reviewed guideline distinguishes digital functionality, physical goods/services consumed outside the app, qualifying enterprise services, certain real-time one-to-one services, reader apps, multiplatform access and narrow free companion-app scenarios. Read the entire relevant clause rather than transferring its headline to a different business model.

For cross-platform services, separate access to an entitlement acquired elsewhere from an in-app call to purchase it. Guideline 3.1.3(b) has its own conditions; a shared entitlement database does not settle how the iOS purchase route may be presented. Other storefront or program conditions can change the allowable calls to action. Do not use device language, IP address or a guessed country as a substitute for the supported storefront/capability decision.

## Prepare and execute the selected lane

1. Inventory every paid feature and route, including a link in metadata, onboarding, account management, email and a web view.
2. Document the product classification and the exact current applicability evidence.
3. Resolve approved entitlements and agreement status where a selected program needs them. Legal acceptance and commercial enrollment are owner actions, not something a reference grants automatically.
4. Implement a supported purchase or access flow with clear product information and robust entitlement verification.
5. Test an eligible storefront, an ineligible storefront and transitions between account/device states using supported test tools.
6. Reconcile the in-app UI, backend entitlement state, product configuration and store metadata for the same release.

## Keep regional rules current

The reviewed primary pages include United States storefront exceptions and newer EU terms, while the legacy-looking external-entitlement URL is specifically a Netherlands dating-app program. Those pages must not be merged into an evergreen worldwide permission. Record observation date separately from effective date and verify the selected agreement before changing a purchase lane.

Do not freeze a fee, enrollment threshold or age rule into a default simply because a repository implements it. A region-specific fee table can become stale even when the code still builds. If eligibility or a legal obligation is not established, retain unknown status and continue independent technical preparation.

## Failure cases and handoff

Cover a digital unlock routed as a physical good, one-to-many sessions treated as one-to-one services, a free companion app with purchase calls to action, and a reader entitlement added to a non-reader app. Test that an existing subscriber can access a valid entitlement without buying it again, while an invalid or revoked entitlement does not gain access.

The output is a product-by-route matrix with source sections, evidence, current status and owner. Mark a demonstrated incompatible lane as a blocker, an unconfirmed category/eligibility fact as unknown, and not applicable only with a reason. Successful payment processing or a valid transaction format does not establish policy eligibility or review approval.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_reader_apps` — [Distributing “reader” apps with a link to your website - Support - Apple Developer](https://developer.apple.com/support/reader-apps/)
- `src_policy_dma` — [Changes for apps in the European Union - Support - Apple Developer](https://developer.apple.com/support/dma-and-apps-in-the-eu/)
- `src_policy_storekit_selection` — [Choosing a StoreKit API for Apple In-App Purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
