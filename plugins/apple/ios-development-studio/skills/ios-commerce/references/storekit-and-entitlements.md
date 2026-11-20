# StoreKit and entitlement verification

## App behavior

Use the project’s installed SDK/deployment target and existing StoreKit abstraction. Inspect current official APIs before introducing version-specific purchase or subscription behavior. Keep product loading, purchase initiation, user cancellation, pending approval, verification failure and successful entitlement updates distinct.

Do not grant access based only on a client-provided product name or unverified transaction. Use platform transaction verification and the established server trust boundary where the architecture requires it. Keep purchase/subscription state synchronized across launch, app foreground, transaction updates and restore flows without duplicate observers or leaked tasks.

A cancelled purchase is an expected result, not a generic error. A pending transaction does not yet prove entitlement. Subscription expiry, revocation/refund, upgrades/downgrades and billing state may change access; preserve the project’s policy and test it explicitly. Avoid deleting access merely because a transient catalog/network request failed.

## Client and server boundaries

App Store Server API credentials are distinct from normal App Store Connect management credentials. Verify environment, bundle, product/account association and transaction identity. Keep server secrets on the server and never bundle them into app source or this plugin. Do not log raw receipts, signed payloads or customer identifiers by default.

Notifications need signature/trust validation, replay/idempotency handling and safe ordering. Duplicate or out-of-order delivery should not create duplicate entitlement effects. Record the backend’s observed source-of-truth and any eventual-consistency delay; a client success screen does not prove server access was granted.

## Optional provider reconciliation

If RevenueCat is already used, inspect actual configured project/app/environment and the available integration. Compare products, entitlements, offerings and packages against the desired mapping. Produce a reviewable diff and preserve customer access. A named provider in a supplied reference is not an installed tool or authorization to create an account.

Keep catalog sync separate from customer data operations. Restrict scope to the requested resources and use exact verified IDs. After a mutation, re-read the mapping and exercise a sandbox purchase/access case if runtime capability is available. Static mapping validation does not prove transaction processing.

## Meaningful tests

Use local StoreKit configuration/sandbox as appropriate and label which environment was used. Cover available/unavailable products, network/error state, cancellation, pending purchase, verified success, restore, expiry/revocation and duplicate event handling relevant to the change. Test on real hardware when platform constraints require it; do not claim a simulator proves the entire purchase flow.

Never execute a live paid purchase, send promotional offers or alter real customer entitlement as an incidental test. Use existing user authorization for legitimate requested remote configuration, and ask only if necessary next work expands that scope.

Report code checks, sandbox/runtime tests, catalog validation and backend/provider verification separately. Include concrete untested edges instead of declaring the commerce system production-ready from a build pass.
