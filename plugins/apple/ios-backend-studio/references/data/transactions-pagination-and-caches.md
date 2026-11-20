# Transactions, stable reads and cache scope

## Start with the invariant and observation

Identify the operation's authoritative write, the readers that must observe it and the product's tolerated staleness. A database commit, a queue acknowledgement, a cache update and a widget snapshot refresh are different events. Document which one the API response promises; do not call a response “complete” if it only admits work for later processing.

Inspect the engine's actual isolation level, transaction wrapper, connection pool and retry behavior. An ORM abstraction does not eliminate serialization failures, unique conflicts or lost-update risks. Use the smallest transaction that enforces the invariant, and make retries safe at the whole-transaction/domain boundary rather than repeating an arbitrary failed statement.

## Concurrency decisions

Use durable uniqueness, atomic compare-and-update, row locking or an appropriate serializable transaction according to the engine and invariant. A read-then-write check without coordination can race across service instances. A process-local mutex cannot protect another process or survive restart.

For optimistic concurrency, publish an explicit version/ETag contract and reject or merge a stale edit according to product rules. For a lock-based operation, keep acquisition order consistent and avoid waiting on external network calls while holding locks. Treat deadlock or serialization errors as classified retry candidates only when the surrounding operation is safe to repeat.

Be careful with duplicate admission under concurrent transactions. A uniqueness conflict can mean another transaction is still completing. Re-read its durable result using a statement/transaction that can actually observe the committed row; do not assume a single SQL statement's earlier snapshot sees a row that appeared while it waited. The exact behavior belongs to the selected engine and isolation level.

## Pagination that survives real updates

Choose a deterministic order with a stable tie-breaker, such as a domain timestamp plus an immutable ID when that matches the product. Define whether pagination represents a snapshot or a moving feed. An offset over changing rows can duplicate or omit items; keyset/cursor pagination also needs an explicit policy for updates and deletions.

Treat the cursor as an opaque transport representation of a query boundary, not authorization. Validate its structure, filter/order version and account/query scope. A signed cursor can protect integrity, but it does not grant access to the entity or make a revoked session valid. If cursor expiration or schema evolution invalidates it, return a stable recovery outcome that lets the client restart without inventing data.

For a native feed, deduplicate by stable domain ID and preserve intended ordering when a refresh races with “load more.” An empty page is not necessarily the same as “no more data” unless the contract says so. Test concurrent inserts, ties, deletes and filter changes using controlled fixtures.

## Cache deliberately

Scope cache keys by account/tenant, resource/query identity, representation version and any locale/variant that changes the result. A URL alone may be insufficient when authorization or content negotiation changes the response. Never share private content across users because a CDN or in-memory cache ignored those dimensions.

Decide who invalidates or replaces a cache entry after a write and how a failed invalidation recovers. Where events drive invalidation, publish them from a durable outbox associated with the commit rather than before the transaction succeeds. A finite TTL can bound stale data but is not an immediate consistency guarantee.

The app and its extensions may intentionally read a versioned snapshot with a freshness marker. Keep that representation separate from mutable server models and account credentials. On sign-out or account change, invalidate or re-scope caches and snapshots; an old asynchronous response must not repopulate the new account's state.

## Failure matrix and checks

| Scenario | Required observation |
| --- | --- |
| Competing decrement/edit | Domain invariant holds; conflict has a stable response |
| Transaction retry after timeout | One logical operation/result, with safe duplicate handling |
| New rows during paging | Defined snapshot/feed semantics; no accidental duplicate display |
| Cache invalidation delayed | Bounded staleness or reconciliation, not cross-account disclosure |
| Account switch during fetch | Old completion cannot enter new account state |
| Cursor from another scope | Safe denial or restart outcome; no broadened query |

Use real-engine tests for isolation and dependency-controlled tests for client ordering. Measure query/serialization behavior before adding speculative caching. Record what was observed, including eventual consistency windows and unavailable device checks.

## Evidence and version cautions

Sources: `src_nm_postgres_isolation`, [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html); `src_backend_extra_postgres_constraints`, [constraints](https://www.postgresql.org/docs/current/ddl-constraints.html); `src_backend_repo_074`, [PowerSync CRUD completion](https://github.com/powersync-ja/powersync-swift/blob/b77dc2f00366db9540f2ecd3903cfefb63fc29e8/Sources/PowerSync/Protocol/db/CrudTransaction.swift); and `src_nm_redis_persistence`, [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/). The [catalog](../../research/sources/sources.jsonl) records the exact sources. Engine semantics, cache defaults and provider behavior must be verified for the actual deployment; this card does not certify a chosen isolation or durability setting.
