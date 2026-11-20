# Widget snapshots, timelines and backend read projections

## Inputs and outputs

Inputs: selected widget families, authorized domain entity IDs, existing app-group store, server freshness rules and a supported runtime. Output: a small presentation snapshot plus a timeline policy with an explicit stale/offline state.

## Workflow

1. Start with a useful static widget type and a clear display projection. Configuration by the user and a timeline’s changing data are separate choices.
2. Build a snapshot quickly. Use deliberate placeholder/sample data for the gallery instead of waiting indefinitely for an authenticated network request.
3. Store a bounded local projection with account scope, entity ID, server revision, fetched-at and stale-after semantics. The exact schema is a project decision, not a WidgetKit requirement.
4. Let the provider render cached state immediately and make eligible inline/background requests while it has execution time. Commit new data before requesting the appropriate timeline reload.
5. Represent predictable future changes in timeline entries rather than scheduling repeated server fetches for every visual timer tick.
6. Support signed-out, missing entity, stale data and request failure presentations. On sign-out, invalidate account-specific projections and refresh widgets so another user’s content does not remain visible.

## Scheduling boundary

WidgetKit renders archived representations and does not keep the extension continuously active. Reload budgets vary with visibility, usage, system conditions and active widget configuration. `after` is a reload request, not a backend SLA or exact polling timer. A server should also tolerate many clients requesting data around similar timeline boundaries, using caching and sensible load distribution.

Current Apple documentation describes WidgetKit push notifications as an additional update mechanism, not a replacement for timelines. Gate adoption on the real SDK and capability setup; do not turn that statement into a universal deployment baseline.

## Failure cases and tests

Use controlled fixtures for cache hit, no cache, stale cache, offline refresh, unauthorized account and a deleted configured entity. Verify completion on every provider path and stable rendering with a slow server. Test timeline generation independently, then inspect actual gallery, Lock Screen and supported family appearances. Never interpret a debugger-observed immediate reload as production scheduling reliability.

## Snapshot contract and deployment skew

Keep one small stable projection for the entity a configured widget represents. A useful envelope identifies the account scope, entity, schema version, server revision, fetch time and freshness policy without requiring all internal persistence fields. Choose exact types/date semantics in the shared wire contract; the widget must tolerate supported old snapshots after an app update.

Avoid exposing session tokens in a projection or a deep-link query. Render an account-neutral placeholder while protected data is unavailable, and make a clear choice about private content on locked/Always-On surfaces. A widget can remain visible long after the process that created the snapshot stopped.

## Acceptance matrix

| Fixture | Expected presentation/state |
| --- | --- |
| Valid cached projection and slow network | Immediate useful snapshot, bounded asynchronous refresh |
| No cached data and no network | Deliberate empty/unavailable placeholder, no indefinite spinner |
| Old snapshot schema after app update | Compatible decode/migration or safe fallback |
| Sign-out then widget reload | Previous account's content is removed/redacted |
| Server projection revision goes backward | Client rejects or safely handles obsolete state |
| System delays timeline reload | UI remains honest about freshness; no exact update-time promise |

Verify family/layout/privacy behavior in Xcode and an appropriate runtime. A passing projection test proves decoding/state choices, not actual system refresh timing.

## Platform and verification boundary

Read the selected project’s generated interfaces and SDK availability before adopting specific symbols. Article prose does not establish the project’s deployment target.

## Primary evidence

- `src_backend_apple_001` — [Creating a widget extension](https://developer.apple.com/documentation/widgetkit/creating-a-widget-extension)
- `src_backend_apple_002` — [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)
- `src_backend_apple_003` — [Making network requests in a widget extension](https://developer.apple.com/documentation/widgetkit/making-network-requests-in-a-widget-extension)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
