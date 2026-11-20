# Conflicts, tombstones and resynchronization

## Define conflict policy per domain operation

Identify which values can merge, which require a current server precondition and which must be confirmed by a user or domain rule. A profile preference, a balance adjustment and deletion of a shared object need different conflict behavior. Do not apply last-write-wins to every field because it is easy to implement.

Use an explicit server revision, ETag or equivalent concurrency contract when updates depend on a known state. Client clocks can be skewed, reset or manipulated; do not use their wall-clock ordering as the only authority for sensitive writes. A device timestamp can still be useful input when the domain defines how it is interpreted.

For each conflict response, define the safe public code and enough non-sensitive information for recovery: current revision, a permitted current projection, or a route to refetch. Do not return another account's data just to explain why a proposed update failed. Keep automatic retry of a stale payload separate from an actual merge decision.

## Merge intent rather than blindly replaying snapshots

Where possible, represent a user's intended operation rather than replacing an entire stale server object. The server must still validate the operation against current domain state. If a merge is safe, persist the resolved outcome under the operation's identity and let every client observe the same decision.

For field-level merges, define how absent, null and deleted values differ. An omitted field can mean “leave unchanged,” while explicit null may mean “clear”; a generated client that drops null or fills a default can change intent. Test the actual serializers used by supported clients. Arrays and ordered collections need explicit add/remove/reorder identities; naïve replacement can lose concurrent edits.

| Conflict | Product decision to record | Verification |
| --- | --- | --- |
| Two edits to one value | Merge, reject or require resolution | Both delivery orders reach the intended stable result |
| Edit after delete | Reject, restore or create a new entity under policy | A late client cannot silently resurrect removed content |
| Account permission revoked | Stop/re-auth/repair without broadening access | Pending work cannot reuse stale grants |
| Schema/payload version changed | Upgrade intent, preserve supported form or quarantine | Old persisted operations remain interpretable or visibly blocked |
| Lost acknowledgement | Reconcile the same operation result | No second business mutation under a fresh ID |

## Tombstones and deletion

If clients can remain offline, decide how they learn that an entity was deleted. A tombstone or versioned change feed can convey deletion until the relevant progress/retention policy permits removal. Do not invent a universal retention period: it depends on supported offline duration, privacy/deletion requirements and service design.

A soft-delete marker alone does not enforce authorization or content retention. Ensure ordinary queries, caches, search indexes, media delivery and extension snapshots apply the intended visibility. Distinguish hiding content, removing local cache, deleting authoritative data and retaining a minimal operation/audit record under actual policy.

## Cursor reset and full resync

When a server no longer recognizes a cursor, return a defined restart outcome. Rebuild the authoritative local projection without discarding pending user intent. Preserve or quarantine the outbox, fetch a consistent baseline according to the protocol, then replay/rebase supported operations against current versions. A “delete local database and sign in again” repair should not be the routine path for an ordinary expired cursor.

Make resync restartable. Persist the baseline/progress boundary and swap a completed projection atomically when useful, rather than exposing half an account's records as complete. Scope progress to the account, query/filter definition and protocol version. A cursor from a previous account or changed filter is not safe merely because its string parses.

## Tests that discriminate real convergence

Deliver the same operations in different orders, repeat them, delay an old success or failure until after a newer result, and stop the process between durable steps. Assert the final domain state and local pending/rejected state, not just that requests were issued. Cover a deletion during pagination, an invalid old payload, permission revocation and a reset cursor with unsent edits.

Use a real persistent store when testing crash recovery or transaction boundaries. Network mocks and in-memory collections are useful for state-machine behavior but do not establish storage durability. A finite bounded retry test is more useful than an arbitrary sleep intended to let synchronization finish.

## Evidence and version cautions

`src_nm_postgres_isolation` identifies [database isolation behavior](https://www.postgresql.org/docs/current/transaction-iso.html). `src_backend_repo_073` and `src_backend_repo_074` cover [sync upload responsibility](https://github.com/powersync-ja/powersync-swift/blob/b77dc2f00366db9540f2ecd3903cfefb63fc29e8/Sources/PowerSync/Protocol/PowerSyncBackendConnector.swift) and [local completion](https://github.com/powersync-ja/powersync-swift/blob/b77dc2f00366db9540f2ecd3903cfefb63fc29e8/Sources/PowerSync/Protocol/db/CrudTransaction.swift); `src_nm_openapi_spec` provides the [wire-description reference](https://spec.openapis.org/oas/v3.1.1.html). The original policy choices above must be resolved for the actual product and versions, not inferred from library defaults. See [source records](../../research/sources/sources.jsonl).
