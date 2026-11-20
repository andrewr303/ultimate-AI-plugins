# Durable idempotency is a domain and storage contract

## Identify the logical operation

Name the business effect that must not happen twice: accepting one transfer, sending one invitation under a defined campaign, committing one offline edit or applying one provider event. List every caller and process that can trigger it. An HTTP request ID traces an attempt; a logical operation ID persists across attempts and lost responses. Choose them separately.

Define the idempotency scope from authenticated account/tenant, operation kind and stable operation identity. Record a reviewed payload fingerprint so reusing the same identity for different intent has a defined conflict outcome. Validate and normalize according to the wire contract before fingerprinting; incidental JSON field order or tracing metadata should not accidentally change domain identity.

## Enforce the local authoritative boundary

Persist admission/result state in the authoritative durable store. Use the engine's unique constraint or equivalent atomic operation and a transaction that protects both the domain mutation and its recorded result. A memory map, cache entry without the required durability, or mutex in one Node process cannot coordinate another replica or survive restart.

The duplicate path must handle an operation still in progress as well as one that completed. Do not return the result of another account or accept a different payload simply because the key string matches. A safe result representation can include the operation's state, stable public result/receipt and a route to reconcile it under normal authorization.

| Condition | Contract to implement |
| --- | --- |
| New operation | Atomically admit and perform/queue the defined action |
| Duplicate completed operation | Return/reconcile the existing logical outcome |
| Duplicate in-progress operation | Return a defined pending/retry outcome without a second effect |
| Same key with changed intent | Stable conflict/rejection; no silent replacement |
| Lost response after commit | Lookup/retry with the same logical identity |
| Key/result retention expired | Reconcile domain state before creating new intent |

Transaction isolation matters. A uniqueness conflict can wait for another transaction, and the losing request must then read a result it can actually observe. Do not assume an earlier snapshot inside a single SQL statement sees a newly committed row. Use the selected engine's proven pattern and test it with concurrent connections.

## External effects require another boundary

For an external payment, push, upload-finalization call or similar provider operation, a local database transaction cannot also commit the remote service atomically. Record a durable outbox/admission with the domain change. The worker uses a stable provider-operation key when the provider supports it, stores the receipt and reconciles an unknown outcome before trying a new identity.

If a crash occurs after the provider acts but before the receipt is stored, the next worker must not blindly repeat under a fresh key. Use the provider's documented duplicate/result-query semantics or an explicit recovery path. Provider retention windows, payload matching rules and response caching differ; local idempotency does not extend them automatically.

Avoid holding database locks while waiting for a remote provider as a substitute for a protocol. That can exhaust connections and still leaves an uncertain external outcome. Keep job completion, provider acceptance and completed domain work distinct in logs, metrics and user-facing status.

## Retention and confidentiality

Choose operation/result retention from offline duration, retry/reconciliation needs, domain risk and actual data policy. Do not invent a universal TTL. Removing old queue jobs can also remove queue-level deduplication; a durable domain receipt may need a different lifecycle. Keep payloads/results minimal and access-controlled.

Do not log full idempotency payloads, tokens or sensitive operation keys. The operation-status endpoint requires the same relevant account/entity authorization as the original operation. An opaque or unguessable ID is not an access policy.

## Tests and acceptance

Run two service instances or independently controlled connections with the same identity. Verify one authoritative mutation, consistent duplicate results and a changed-payload conflict. Stop the process immediately before commit, after commit before response, after external acceptance and before receipt storage. Verify retry/recovery with the same identity, not merely that one in-memory function was called once.

The packaged Node fixture may demonstrate control flow, but an in-memory record is not evidence for production durability. Real-engine and provider-contract tests establish those layers separately.

## Evidence and version cautions

Sources: `src_nm_stripe_idempotency`, [provider idempotent requests](https://docs.stripe.com/api/idempotent_requests); `src_nm_bullmq_idempotent`, [idempotent jobs](https://docs.bullmq.io/patterns/idempotent-jobs); and `src_backend_extra_postgres_constraints`, [durable constraints](https://www.postgresql.org/docs/current/ddl-constraints.html). Read the [source catalog](../../research/sources/sources.jsonl) and the actual provider/engine version. These sources inform original workflow design; they do not make all providers' retention, response or conflict rules identical.
