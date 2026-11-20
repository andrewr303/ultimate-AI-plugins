# Present subscription terms and regional lanes truthfully

## Align the offer with the product people will buy

Read the actual StoreKit product, current subscription status, billing interval, commitment term, offer eligibility and storefront. A manually entered price string or a marketing mockup is not the product contract. When a recurring product is offered, the observed Apple guidance asks for clear service/duration, full renewal price and a way for existing subscribers to sign in or restore purchases, with Terms of Use and Privacy Policy links.

The amount actually billed must be the prominent pricing element. An annual price cannot be hidden behind a larger monthly-equivalent figure. For a trial, describe the duration and amount billed afterward. If the selected current product has a commitment term distinct from its billing frequency, do not describe it as freely cancellable monthly billing without establishing that fact.

## Prepare the offer and eligibility matrix

Record localized product values, active/expired entitlements, the offer rules, subscription-group structure and the exact account/storefront lane. Include the owner-confirmed agreement and entitlement status for external offers. A regional program can constrain destinations, interstitial APIs, domains, eligible app type, support/reporting and child-related purchase behavior; do not copy one program's presentation into another.

The current reader-app page distinguishes primary reader functionality from incidental content, and describes account-link eligibility separately from newer regional purchase offers. The Netherlands dating-app page is a narrow program. The EU support page describes recently effective business-term and payment-choice conditions. Preserve this scope and refresh the source before implementation or an external action.

## Workflow

1. Reconcile the offer text with the configured product, localized StoreKit values and actual entitlement state.
2. Make billing amount, duration, commitment/trial conditions, renewal and included service understandable before purchase.
3. Provide a usable existing-customer sign-in/restore path and the relevant management route. Avoid accidental duplicate subscriptions for the same benefit.
4. For an external purchase/account link, verify the exact current category/storefront/platform/agreement requirements and approved entitlement before showing it.
5. Test the eligible and ineligible lanes, including age/parental-control facts where applicable, without inventing an age or consent result.
6. Compare the built UI and metadata with the same release's configured products and source applicability record.

## Meaningful failure cases

Check an annual bill displayed as a monthly price, an ineligible free trial, a stale currency/price cache, an already-subscribed account shown a duplicate offer, a restore control that does nothing, and a changed external URL/domain not reflected in the submitted configuration. Test large text and assistive navigation in the actual paywall; a screenshot alone cannot establish that pricing and controls remain operable.

Do not automatically alter prices, enroll in a program, accept terms, send marketing or submit a review item merely because a reference describes how. Execute actions already authorized after resolving the target; otherwise prepare the exact reviewable change and identify the missing authority or product fact.

## Record the decision

A false price/term or demonstrated ineligible lane is a blocker. Unknown eligibility, agreement terms, billing commitment or child-protection facts remain unknown. Not applicable needs a specific product/storefront rationale. Satisfied evidence names the tested offer, build, storefront and customer state. Neither a successful charge nor a correct-looking paywall independently establishes policy eligibility, legal compliance or review acceptance.

Avoid maintaining an evergreen universal fee or exception table in the app/plugin. Keep a small dated applicability matrix with links to the live primary program and an owner responsible for the commercial decisions.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_subscriptions` — [Auto-renewable Subscriptions - App Store - Apple Developer](https://developer.apple.com/app-store/subscriptions/)
- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_dma` — [Changes for apps in the European Union - Support - Apple Developer](https://developer.apple.com/support/dma-and-apps-in-the-eu/)
- `src_policy_reader_apps` — [Distributing “reader” apps with a link to your website - Support - Apple Developer](https://developer.apple.com/support/reader-apps/)
- `src_policy_external_link_entitlement` — [Distributing dating apps in the Netherlands - Support - Apple Developer](https://developer.apple.com/support/storekit-external-entitlement/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
