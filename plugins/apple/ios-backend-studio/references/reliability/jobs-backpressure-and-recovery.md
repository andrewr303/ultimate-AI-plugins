# Durable jobs, bounded concurrency and recovery

## Decide whether work must outlive the request

Identify the work's owner, input identity, deadline, side effect and accepted failure state. A request can complete synchronously when that fits its latency and durability needs. Work that must survive process termination needs durable admission and an explicit processor/recovery path; do not rely on an unawaited promise or a process-local array after returning success.

Preserve the queue/job system already in the project. For a new choice, inspect persistence, atomic admission, retries, leasing/locks, scheduling, observability, hosting compatibility and operational cost. A library can support several adapters whose durability and locking contracts differ. Do not copy a Redis deployment recipe into another backend because both expose a similarly named Worker.

## Admit work with a domain contract

When an HTTP transaction creates a job, associate admission with the authoritative mutation through an outbox or another proven atomic design. A “write database, then enqueue” sequence can lose the job between steps; “enqueue, then write” can process work that never committed. Define how the selected system closes that gap.

Keep job payloads small and versioned. Prefer durable domain references and explicit operation/account scope over copying secrets, entire HTTP requests or mutable user objects. Re-fetch and validate the relevant current domain state when that is required. A stale job must not preserve revoked access forever just because it was once admitted.

Distinguish queue delivery identity from business effect identity. A retried or stalled job may execute more than once, and deleting a completed job can change queue-level deduplication. Use a durable domain receipt or provider identity where the side effect needs it. The [idempotency card](durable-idempotency.md) describes that separate boundary.

## Concurrency and backpressure

Set concurrency from actual CPU, memory, connection pool, provider limit and fairness needs. Bound fan-out inside each job as well as the number of workers. One account or poisoned job type should not starve unrelated work; define per-scope quotas or queues only when justified by the product and infrastructure.

Use the queue's real leasing/heartbeat mechanism and understand lock expiry. A slow CPU-bound callback can prevent heartbeat progress; an expired lease can cause another worker to retry. Increasing a timeout blindly may hide the problem and delay recovery. Measure the workload, isolate blocking work when appropriate and retain idempotent side-effect handling.

| State | Operational signal | Recovery contract |
| --- | --- | --- |
| Admitted | Durable job/operation receipt | Safe to acknowledge the promised admission |
| Running | Owned lease/progress under bounded lifetime | Retry/reconcile if ownership is lost |
| Retry scheduled | Classified failure and next eligible attempt | Budget and fairness remain enforced |
| Permanently blocked | Safe reason and repair route | Quarantine/manual repair under task authority |
| Completed | Durable domain/provider outcome recorded | Duplicates reconcile existing result |

## Graceful shutdown and restart

Stop taking new work according to the runtime's shutdown model, allow an intentional bounded drain, preserve incomplete work and close resources the process owns. Do not mark a job successful merely to make shutdown quick. A platform can terminate before the grace period finishes, so restart behavior must be correct without a clean exit.

On uncertain completion, inspect the durable operation/provider state before replaying. Keep a repair path for jobs with incompatible old payloads, repeated permanent errors or missing referenced records. Record what an operator can safely retry, requeue or compensate; do not give a generic “delete failed jobs” command that loses domain intent or audit evidence.

## Verification and acceptance

Kill a worker at admission, after the side effect, before receipt storage and during acknowledgement. Run competing workers for the same logical action. Exercise queue outage, lease loss, retry exhaustion, invalid payload version, revoked account access and a poisoned job alongside healthy work.

Use actual persistence/adapter integration tests for durability and locks. Mock tests are useful for the processor state machine but cannot establish the broker's recovery behavior. Observe queue lag, retry/blocked counts and domain completion without including private payloads or tokens in metrics/logs.

## Evidence and version cautions

Sources `src_backend_repo_079`, `src_backend_repo_080` and `src_backend_repo_083` are the pinned [worker implementation](https://github.com/taskforcesh/bullmq/blob/804fc03a84ca79453856ce287dfc66a6d6a6f01c/src/classes/worker.ts), [idempotent job guidance](https://github.com/taskforcesh/bullmq/blob/804fc03a84ca79453856ce287dfc66a6d6a6f01c/docs/gitbook/patterns/idempotent-jobs.md) and [PostgreSQL worker tests](https://github.com/taskforcesh/bullmq/blob/804fc03a84ca79453856ce287dfc66a6d6a6f01c/tests/postgres/worker.test.ts). `src_nm_redis_persistence` identifies [Redis persistence choices](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/). See [the catalog](../../research/sources/sources.jsonl). These sources were inspected, not run; validate the chosen queue/adapter/version and do not infer exactly-once effects from a successful job state.
