---
name: backend-reliability
description: "Use for durable idempotency, duplicate writes, retry budgets, timeouts, cancellation, background jobs and recovery across iOS clients and Node replicas. Distinguish admission from completion; do not call an in-memory demo, queue job ID or client cancellation a production exactly-once guarantee."
---

# Reliable operations across clients and workers

First read the [operating contract](../../references/operating-contract.md).

1. Identify the authoritative side effect, its durable identity, callers, workers and unknown-outcome paths. Define what the endpoint or receipt actually promises.
2. Use [durable idempotency](../../references/reliability/durable-idempotency.md) to protect competing requests and uncertain external effects.
3. Use [retries, timeouts and cancellation](../../references/reliability/retries-timeouts-and-cancellation.md) to classify outcomes and bound work without multiplying writes.
4. Use [jobs and recovery](../../references/reliability/jobs-backpressure-and-recovery.md) when work must survive the request or process. Keep existing queue/provider choices unless the task justifies a change.
5. Verify duplicates from different instances, process death at commit/ack boundaries, delayed responses, unavailable dependencies and recovery with deterministic gates.

Return the operation/acknowledgement contract, implemented durable protections, observed checks and remaining provider/isolation limits. Request IDs support diagnostics; they are not automatically business idempotency keys.
