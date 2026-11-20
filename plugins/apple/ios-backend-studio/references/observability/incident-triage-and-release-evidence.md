# Incident triage, release evidence and recovery handoff

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Start from the concrete failure

Resolve the affected app version/build, backend revision, API/schema revision, account/environment, time window and user-visible symptom using safe evidence. Distinguish a client decode/version mismatch, expired authorization, stale conflict, transport disconnect, queue delay, database migration issue, provider rejection and Apple lifecycle limitation. A recent code change is a hypothesis until connected to the failure path.

Keep unrelated user data and running applications intact. Do not begin with deleting stores, resetting simulators, clearing all caches, restarting all services or rotating every credential. Such actions can destroy the evidence and create new failures. Scope any diagnostic capture to the intended process/device and keep its duration/output bounded.

## Build a discriminating timeline

Connect safe request/operation/job/provider identifiers and actual state transitions. Determine the authoritative outcome when the client saw a timeout: was work admitted, committed, retried, rejected or still pending? Examine the versions and deployment/migration order around the incident. A dashboard's aggregated success rate can hide a small incompatible client cohort or repeated duplicate processing.

Separate source-level reasoning from observed runtime evidence. A Node stack trace cannot prove a native widget rendered, and a passing Xcode test plan cannot establish the backend's deployed database state. Read actual result bundles and provider receipts rather than interpreting queued work or partial logs as completion.

## Triage and repair sequence

1. Define the failure trigger and expected behavior. Preserve safe evidence and a minimal synthetic reproduction fixture.
2. Locate the earliest incorrect boundary: decode/validation, account authorization, domain invariant, transaction, job delivery, provider transport or UI/platform lifecycle.
3. Use a controlled test or targeted observation to distinguish competing hypotheses. Avoid repeated unchanged commands and broad test runs without new information.
4. Repair the smallest originating mechanism and test relevant denied, duplicate, out-of-order, cancellation and recovery cases. Keep tests deterministic with explicit gates/clock control.
5. Plan any authorized deployment/data repair with exact target and completion state. After a timeout, inspect current remote state before retry; code rollback and data recovery are separate operations.
6. Verify the affected path and required coupled checks against the final revision. Preserve unresolved device/provider/hosting limits honestly.

## Recovery questions

| Boundary | Question |
| --- | --- |
| Database | Is the invariant restored, and can old/new clients still read/write supported data? |
| Queue/outbox | Which operations are pending, duplicated, poisoned or already committed? |
| Provider | Can uncertain effects be reconciled without replaying an unsafe mutation? |
| Process shutdown | Were accepted operations drained or durably checkpointed? |
| Native client | Does the actual target build and handle the corrected wire/state behavior? |
| Release | Which artifact/revision is deployed, submitted, approved or public? |

## Evidence and handoff

Report what changed, its concrete effect, exact test/build/deployment result and material residual risk. Include safe artifact and operation identifiers rather than full user payloads, credentials or signed links. A backup's existence is not proof restore works; a clean health check is not proof data integrity or notification delivery.

Distinguish implementation complete, relevant checks passed, independent review, merge, deployment and user-visible recovery. Do not promise future monitoring unless an actual session or configured mechanism will perform it. Keep a focused follow-up for genuinely unverified target-environment behavior instead of presenting a broad all-platform guarantee.

## Sources and applicability

- [Process | Node.js v26.12.1 Documentation](https://nodejs.org/api/process.html) — `src_nm_node_process`.
- [PostgreSQL: Documentation: 18: 13.2. Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — `src_nm_postgres_isolation`.
- [Redis persistence | Docs](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) — `src_nm_redis_persistence`.
- [Running tests and interpreting results](https://developer.apple.com/tutorials/data/documentation/xcode/running-tests-and-interpreting-results.json) — `src_nm_xcode_results`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
