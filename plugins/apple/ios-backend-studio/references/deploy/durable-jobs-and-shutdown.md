# Durable jobs, outbox delivery and graceful termination

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Define accepted and completed

Identify which operation needs background execution, who owns its authoritative state and how the client learns progress. Distinguish request receipt, durable admission, queue delivery, worker execution and domain completion. An in-memory queue entry is not durable acceptance. Do not add a new queue/service unless the existing system lacks a boundary the product actually needs.

For a database mutation that must lead to external work, consider the existing outbox or transactional receipt pattern. The durable record and authoritative mutation should share an atomic boundary where the design requires it. Publishing to a queue and committing a database transaction are not automatically one atomic action. Decide how the dispatcher finds/retries unfinished work after a crash.

## Small idempotent work units

Design a job so retry does not create another intended business effect. Include stable operation/account/entity identity and a schema version, not raw credentials or arbitrary executable input. Keep a durable result/checkpoint where the requirements include restart recovery. External provider calls may need provider idempotency keys and reconciliation; queue deduplication alone does not prove the provider acted only once.

BullMQ's idempotent-job guidance favors small simple jobs because multi-action partial progress is harder to recover. The same principle applies to other selected services. Redis persistence configuration has explicit durability/latency tradeoffs; do not promise a lossless queue from its mere presence. Determine acknowledgement, leases/visibility, retry/backoff, expiration and poison-work handling from the actual configured platform.

## Implementation sequence

1. Write the domain invariant and durability boundary. Define the public progress/result contract before returning an asynchronous-accepted response.
2. Atomically admit domain work and its durable delivery record where needed. Make repeated dispatch/execution safe under concurrent workers.
3. Classify temporary dependency failure, invalid payload, authorization loss and permanently rejected provider operations. Retry only eligible work with finite budgets/backoff.
4. Keep job handlers and external side effects small, observable and checkpointed. Route poison work to a deliberate review/recovery path rather than retrying forever.
5. Handle process termination according to the host: stop accepting new work, cooperate with cancellation, drain or checkpoint within its deadline and release resources correctly.
6. On restart or uncertain completion, reconcile authoritative state. A shutdown signal handler and a successful queue acknowledgement are not evidence that every downstream action completed.

## Failure matrix

| Interruption | Expected invariant |
| --- | --- |
| Crash after database commit before publish | Durable dispatcher can still discover the work |
| Crash after provider mutation before acknowledgement | Retry/reconciliation does not duplicate the business effect |
| Worker lease expires during slow operation | Concurrent execution follows the same idempotent admission/result policy |
| Queue persistence loss | Recovery guarantees match the documented data boundary |
| Permanently invalid payload | Finite attempts and visible poison-work handling |
| Logout or resource deletion | Work rechecks the applicable authorization/entity state |

## Verification and handoff

Control crash/acknowledgement points in tests instead of using timing guesses. Use a real relevant store/queue when testing persistence or concurrent admission; keep provider interactions in a configured sandbox when authorized. Inspect safe operation IDs and state transitions, not raw payloads or tokens.

Return the acceptance/completion definitions, chosen existing infrastructure, durable recovery path and actual failure tests. Separate Node process signal behavior from the hosting platform's termination contract. If a service cannot be exercised here, state the exact remaining recovery test without calling mocks a production durability proof.

## Sources and applicability

- [Idempotent jobs | BullMQ](https://docs.bullmq.io/patterns/idempotent-jobs) — `src_nm_bullmq_idempotent`.
- [Redis persistence | Docs](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) — `src_nm_redis_persistence`.
- [PostgreSQL: Documentation: 18: 13.2. Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — `src_nm_postgres_isolation`.
- [Process | Node.js v26.12.1 Documentation](https://nodejs.org/api/process.html) — `src_nm_node_process`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
