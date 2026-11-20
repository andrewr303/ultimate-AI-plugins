---
name: ios-commerce
description: "Use for iOS IAP/subscription catalogs, localization, pricing plans, StoreKit integration, in-app events and explicit RevenueCat reconciliation. Do not infer commercial changes, purchases, provider availability or live price/event publication from a general app-development request."
---

# Build and reconcile iOS commerce

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Establish the exact app, commerce backend, products/subscription groups, territories, environment and requested endpoint. Separate app StoreKit behavior from App Store Connect catalog state and third-party entitlement mapping.

1. Inspect source/config and current catalog read-only. Resolve product identifiers and opaque resource IDs without substituting one for the other.
2. Prepare an explicit catalog/pricing/localization/event or entitlement diff. Preserve existing customer access and approved commercial terms.
3. Implement app-side behavior with deterministic sandbox/StoreKit tests where available; validate server-side verification and entitlement state separately.
4. Apply only the remote effects the user asked for using current installed help/API docs. Check receipts and state before retrying uncertain mutations.
5. Report app/runtime, store catalog and backend verification independently. Never claim real purchases, revenue impact or availability from a static catalog check.

Use `ios-release` when commerce items must join review, `ios-store-metadata` for listing copy and `ios-store-insights` for measured commercial analysis.

Read only the references needed for the current step:

- [Catalog, prices and in-app events](references/catalog-pricing-events.md)
- [StoreKit and entitlement verification](references/storekit-and-entitlements.md)
- [Commerce provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
