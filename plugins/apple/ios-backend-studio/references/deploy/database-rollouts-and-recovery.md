# Database migrations, staged clients and recovery

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Inputs and compatibility window

Identify the actual database engine/version, migration tool major, authoritative schema, applied migration history, deployed backend, supported mobile/web clients and background jobs. Inspect existing release instructions and permissions. A development reset command is not a production migration plan. A rollback of source code is not proof customer data can be rolled back.

Record which old payloads and stored representations must remain usable during staggered app upgrades. Widgets and offline clients can submit data later than the foreground app, so queued operation and snapshot versions belong in the compatibility review. Keep migration steps tied to the same domain/API contract rather than deploying a schema independently of the consumers it affects.

## Choose an additive path where practical

Prefer expand, compatible code, observable backfill and later contract retirement when the support policy permits. Assess lock/scanning duration and concurrent writer behavior of each actual SQL/tool operation. PostgreSQL ALTER TABLE forms differ in locking and validation behavior; a statement labelled small in a review can still block a busy table. Use the deployed database's exact documentation and inspect the plan before execution.

Current Prisma documentation differs from older guides and describes newer migration commands. The correct command follows the installed major, project workflow and actual help. Do not force a newer interface into an existing project or copy an older migrate-deploy/reset recipe as universal advice. Keep applied migration files immutable according to project policy; repair forward where required.

## Execution sequence

1. Capture the current schema/history and domain invariants without dumping private data. Resolve the intended database/account/environment before any mutation.
2. Prepare a reviewable migration/backfill plan, including lock/runtime expectations, indexes/constraints, external writers and old-client compatibility.
3. Test from realistic prior schema/data fixtures on the relevant engine. Include null/default behavior, relationships/counts, constraints and repeated launches/requests.
4. Stage compatible application code and schema changes in the required order. Make partial completion and restart/backfill checkpoints observable and idempotent where needed.
5. Apply only authorized production changes through the established migration process. If completion is uncertain, inspect history/current state before retrying.
6. Verify invariants and application behavior, then retire compatibility only with actual adoption/support evidence. Keep backups and a tested restore/reconciliation procedure separate from the source revert.

## Failure cases

| Case | Expected response |
| --- | --- |
| Old client omits a new field | Compatible default or explicit supported rejection, not silent data destruction |
| Concurrent writer during backfill | Defined invariant/conflict policy and resumable progress |
| Migration lock exceeds expectation | Controlled stop/recovery plan based on actual transaction state |
| Tool reports drift | Diagnose history/schema ownership; do not reset production by default |
| New code rolls back after data change | Old code can handle the state or a deliberate recovery path exists |
| Backup exists but restore untested | State that recovery readiness remains unverified |

## Evidence and handoff

Use a real relevant database for lock, constraint and isolation behavior; mocks do not establish those properties. Record engine/tool versions, schema/history identity, command/plan and observed state. Do not log customer rows, connection secrets or private backup locations in public artifacts.

Report whether preparation, local migration fixture, staging/production application, backfill and validation actually completed. Keep independent code and contract work moving when external credentials are unavailable. A generic green deployment check must not hide a failed or skipped data migration.

## Sources and applicability

- [PostgreSQL: Documentation: 18: ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) — `src_nm_postgres_alter`.
- [PostgreSQL: Documentation: 18: 13.2. Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — `src_nm_postgres_isolation`.
- [Applying a migration in Prisma ORM | Prisma Documentation](https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production) — `src_nm_prisma_migrate`.
- [OpenAPI Specification v3.1.1](https://spec.openapis.org/oas/v3.1.1.html) — `src_nm_openapi_spec`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
