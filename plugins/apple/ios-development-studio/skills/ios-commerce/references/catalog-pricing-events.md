# Catalog, prices and in-app events

## Map identities and ownership

Record bundle/app ID, product identifiers, subscription-group structure, opaque version/resource IDs, territories, currency/base region and provider environment. App Store product ID, RevenueCat product/entitlement/offering/package ID and transaction ID represent different concepts. Do not synthesize a mapping from similar names.

Read the project’s existing StoreKit configuration, backend contracts and catalog exports. Check installed `asc` or another selected tool’s help for supported IAP, subscriptions, pricing and event surfaces. Do not guess an endpoint, modern version-scoped field or command from an uploaded snapshot. An optional RevenueCat MCP connection is usable only if actually available and authorized.

## Prepare a catalog diff

Compare the intended products to current state with explicit create/update/archive actions and exact IDs. Keep display names/descriptions and their locales distinct from immutable product identifiers. Understand group ordering, duration, introductory/promotional offers and current subscription behavior before editing. Preserve active customer entitlement paths; removing an offering is not equivalent to removing a purchased entitlement.

Test fixtures should use sandbox data and unique identifiers in the task’s scope. Do not create throwaway live products or irreversible identifiers to test access. Retrying a timed-out creation requires a read to determine whether it already completed.

## Pricing decisions

Prepare a territory table that identifies current price, proposed price, currency, effective date, basis and intended customer treatment. Use current supported price points and API/tool semantics rather than computing an arbitrary currency amount and assuming it is allowed. PPP suggestions are a commercial hypothesis requiring the user’s policy; do not invent purchasing-power data or promise conversion gains.

Account for existing subscribers, price consent/notification rules and tax/currency interpretation using current official guidance. Do not silently use the current date, roll a schedule forward or change every territory. Resolve timezone and schedule boundaries when they materially affect the requested result.

Apply scoped pricing changes only when requested. Verify the resulting schedules and retain before/after receipts. A successful price mutation does not establish what every customer currently sees.

## Localizations and events

Prepare exact locale/product/group/version associations and validate required fields. Keep translated terms consistent with actual benefits and billing periods. Missing local text should not cause silent deletion or fallback changes.

For in-app events, resolve event identity, schedule, territories/locales, deep link and media. Validate that the event describes real app behavior and that the link opens the intended app state. Drafting an event does not authorize submission or publication. Readiness and event review may have their own state lifecycle; inspect it before retrying.

When products/events must accompany app review, hand exact prepared IDs and blockers to the release workflow. Do not create an independent competing submission.
