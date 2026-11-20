---
name: backend-data
description: "Use for authoritative Node-side schemas, tenant ownership, transactions, migrations, pagination and cache consistency consumed by iOS or other clients. Preserve the installed database/ORM; do not replace a native persistence engine or run destructive production repairs as a default."
---

# Authoritative backend data

First read the [operating contract](../../references/operating-contract.md).

1. Inspect the actual database, ORM/query layer, schema history, writers, tenant model and supported client versions. Identify the invariant that the requested change must preserve.
2. Use [schema and tenant ownership](../../references/data/authoritative-schema-and-tenancy.md) to separate wire DTOs, stored models and domain authorization.
3. Use [migration rollouts](../../references/data/migrations-and-rollouts.md) for compatible schema/backfill changes; prepare a concrete plan before any action beyond existing authority.
4. Use [transactions, paging and caches](../../references/data/transactions-pagination-and-caches.md) to implement durable invariants and predictable reads across processes.
5. Verify denied access, competing writes, old data, rollback/retry and the app-visible result. Use the actual engine for isolation/migration behavior; an in-memory substitute does not prove it.

Return the invariant, schema/query changes, compatibility and recovery plan, actual checks and material limits. A successful database statement is not evidence that every client cache or extension snapshot is current.
