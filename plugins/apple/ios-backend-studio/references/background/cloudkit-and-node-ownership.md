# CloudKit sync and a Node backend without accidental dual ownership

## Decision to make

Name the authoritative data plane before adding CloudKit. CloudKit private/shared databases, iCloud identity, app-local persistence and a Node service account are not automatically interchangeable.

## Architecture choices

- Keep an existing Node domain store authoritative and use the app’s explicit offline/sync protocol when web/Android/server workflows share that domain.
- Keep an existing CloudKit-backed domain when its iCloud/private-sharing semantics fit, and add a narrow Node integration only for a concrete need.
- If both are necessary, define one owner per resource/field plus explicit mapping, conflict and failure policies. Do not promise a cross-service atomic transaction.

## Workflow

1. Identify container, environment, database scope and account identity. Public, private and shared databases have different access and synchronization roles.
2. Persist CKSyncEngine’s opaque serialization state across launches and keep the pending local mutation state it needs. The engine still relies on a delegate to supply changes and consume results.
3. Respond to account changes by updating local persistence deliberately. Do not let one iCloud account’s cache or pending writes become another Node user’s data.
4. Let the engine handle its documented transient retries, but implement domain-specific conflict behavior such as server-record changes yourself. Respect scoped batches and current service limits.
5. Evolve production schema compatibly. Apple’s design guide permits additive production changes and prohibits deleting deployed schema components; do not suggest deleting customer stores as the ordinary repair.
6. For shared records, model permission changes, participant removal and share acceptance as first-class changes and refresh the local view from authoritative state.

## Failure cases and tests

Test no iCloud account, offline writes, account switch, old serialized state, expired cursors/tokens, partial batches, conflict, deleted zones and revoked shares. Verify real development/production environment configuration and sharing with distinct accounts. CKSyncEngine’s schedule is indeterminate and it is not a public-database sync solution.

## Ownership and compatibility worksheet

For each resource, name the authoritative store, identity system, local cache, allowed writers, conflict policy and deletion semantics. If one field is derived from another service, identify the direction and replay/checkpoint behavior. Do not let both CloudKit and Node accept incompatible authoritative updates with an implied distributed transaction.

CloudKit record identifiers, iCloud accounts, sharing participants and Node account subjects require deliberate mapping. Device sign-out, server account deletion and withdrawal from a CloudKit share are different events. Decide what remains cached/offline and what must be removed or hidden, using the actual product retention/access requirements.

## Acceptance matrix

| Fixture | Required boundary |
| --- | --- |
| iCloud account absent but Node session valid | Explicit supported degraded/offline state |
| iCloud account changes | Old engine state and pending writes cannot cross into the new account |
| One service commits and the other is unavailable | Recoverable reconciliation rather than invented atomic success |
| Record conflict or revoked share | Domain-specific conflict/permission handling |
| Old installed schema meets a new server projection | Compatible representation or intentional migration |
| Expired local sync metadata | Defined resynchronization without default customer-data deletion |

Test on copied nonproduction stores and separate accounts where relevant. Do not bootstrap schema or repair a production environment by deleting customer data.

## Platform and verification boundary

Fetched CKSyncEngine metadata lists iOS/iPadOS 17, macOS 14 and watchOS 10 introductions. The older CloudKit sharing sample has different sample minimums; it is not proof every new engine API is available at that sample’s baseline.

## Primary evidence

- `src_backend_apple_027` — [Designing and Creating a CloudKit Database](https://developer.apple.com/documentation/cloudkit/designing-and-creating-a-cloudkit-database)
- `src_backend_apple_028` — [Sharing CloudKit Data with Other iCloud Users](https://developer.apple.com/documentation/cloudkit/sharing-cloudkit-data-with-other-icloud-users)
- `src_backend_apple_033` — [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
