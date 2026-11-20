# Migrations that tolerate old clients and overlapping servers

## Inputs and preflight

Identify the authoritative migration history, deployed service/worker versions, database engine/version, volume, indexes and constraints. Determine which mobile/web/extension versions remain supported. Read the existing ORM's production workflow and the actual deployment arrangement; development schema synchronization is not automatically a safe production migration.

Describe the requested before/after behavior, the data invariant, expected lock/work duration, failure signal and rollback limitation. Use a representative non-production copy or synthetic prior-schema fixture that exercises the relevant shape. Do not copy private production data into this plugin, a PR or an unprotected diagnostic directory.

## Expand, adopt, then contract

Prefer additive compatibility when the product permits it. Introduce the new representation without making old writers invalid; make the service understand both representations; backfill with explicit progress; adopt the new path in clients; and remove old structures only under the actual support/retention policy. An additive column can still cause problems through defaults, table rewrites, index creation or application assumptions, so inspect the chosen engine's behavior.

For each step, state which old and new binaries can coexist and which representation is authoritative. Avoid permanent dual-write ambiguity. If two columns temporarily represent the same value, choose an authoritative write path and reconciliation rule, and test an old writer updating a record after backfill. A `version` label alone does not solve divergent values.

| Stage | Safe completion evidence | Recovery question |
| --- | --- | --- |
| Expand | Schema exists and old app/worker behavior still works | Can previous binaries continue if the next step is delayed? |
| Backfill | Bounded checkpoints and invariant checks cover the intended rows | Can a chunk repeat after crash without corruption or omissions? |
| Adopt | New path works while supported old clients remain usable | What if a new write arrives before every reader is upgraded? |
| Contract | Product support policy permits removal; no needed writer remains | Can source rollback still read values already written? |

## Backfill without a single fragile transaction

Choose a stable traversal order and durable progress record. Bound each unit of work and make it repeatable. Account for rows inserted, changed or deleted while the backfill runs; a simple offset can skip or repeat work under concurrent changes. Where a snapshot or keyset boundary is appropriate, document exactly what it covers and how later writes are reconciled.

Keep network calls outside database locks unless a reviewed design requires otherwise. For external side effects, write a durable outbox record with the database change and process it separately with domain idempotency. A long database transaction waiting for an HTTP provider can exhaust connections and still cannot atomically commit the remote system.

Validate counts, relationships, required-field completion and domain invariants rather than only checking that a migration command exited successfully. Retain safe diagnostics about failed keys without logging private row content. Define whether a failed row stops the job, is quarantined for repair or can be retried; never silently mark a partial migration complete.

## Rollback and irreversible effects

Distinguish reverting source, reversing schema, restoring a backup and compensating a domain operation. Data written in a new format may not be understood by old binaries. A restored database may omit external events that already reached providers. Decide the recovery strategy before the step that makes it necessary; do not promise that every migration can be undone.

Preserve applied migration files according to the project's conventions. Repair production history with a deliberate forward migration rather than editing a historical file and assuming deployed systems will converge. Avoid reset/drop/recreate commands as routine troubleshooting. Authorization for preparing a migration does not by itself authorize a destructive production repair.

## Acceptance and rollout checklist

- Apply from the relevant prior schema and reopen the app/service repeatedly.
- Test interrupted and repeated backfill, concurrent old/new writers and invalid historical values.
- Verify old and new API fixtures, serialized nullability and constraint-conflict errors.
- Observe lock/connection impact with realistic data volume in an appropriate environment.
- Confirm exact target environment and migration state before an already authorized apply.
- After uncertain completion, inspect current state before retrying.

## Evidence and version cautions

Source IDs `src_nm_prisma_migrate`, `src_nm_postgres_alter` and `src_nm_postgres_isolation` identify the [Prisma production/development workflow](https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production), [PostgreSQL ALTER TABLE reference](https://www.postgresql.org/docs/current/sql-altertable.html) and [isolation guide](https://www.postgresql.org/docs/current/transaction-iso.html). These support an original staged process; they do not supply a universal command for another ORM or host. Consult the [source records](../../research/sources/sources.jsonl), resolved tools and actual engine documentation. No production migration was performed by this reference review.
