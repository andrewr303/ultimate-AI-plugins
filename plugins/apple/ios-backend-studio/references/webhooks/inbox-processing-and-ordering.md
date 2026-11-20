# Durable receipt is separate from domain processing

## Define receipt and completion

After authenticating the delivery, decide what response acknowledges: durable receipt, synchronous completed work or another provider-defined state. Webhook providers can retry, deliver concurrently and send events in an order different from domain changes. An endpoint returning success should not imply a background mutation is complete unless it actually is.

Use a durable inbox/admission record when work must survive the HTTP process. Scope identity by provider, environment/account and the provider's documented event identity. Store only the fields needed for processing/reconciliation, payload version, verification context and safe processing status. Keep raw bodies only when the product's privacy/retention policy and operational need justify protected storage.

## Atomic admission and duplicates

Protect inbox uniqueness with the authoritative store's atomic constraint or equivalent. A process-local Set cannot coordinate another instance. Persist the event/admission before returning an acknowledgement that tells the provider it need not retry. If admission fails, use the provider's documented retry/error behavior rather than swallowing the failure and returning success.

Separate a delivery attempt from the logical event. Signature timestamps and transport headers can change across retries. Where a payload fingerprint is useful, define what the provider promises about repeated event contents and what discrepancies require reconciliation; do not assume every byte under the same event ID must always be identical across every API-version transition.

| Existing event state | Receipt path | Processing rule |
| --- | --- | --- |
| New authenticated event | Durably admit once | Schedule/perform the intended idempotent domain work |
| Already admitted/in progress | Return the documented duplicate receipt | Do not create a second logical effect |
| Completed | Reconcile/ack existing result | Preserve completed domain receipt |
| Failed transiently | Maintain recoverable state | Retry under the existing logical identity |
| Invalid domain/version state | Preserve a safe blocked/reconciliation record | Do not discard or endlessly retry without a repair policy |

## Apply domain changes safely

Resolve provider entities to internal ownership through stored authoritative mappings. Recheck the relevant account/environment and domain state. A genuine external event does not authorize arbitrary entity IDs supplied by a public client or broaden an internal user's access.

Commit the domain transition and processing/result record together where the database boundary permits it. If processing triggers another external side effect, use the same durable outbox/idempotency principles as ordinary application work. A crash after the side effect but before marking an event processed must not cause another charge, notification campaign or irreversible mutation under a new identity.

Keep a clear distinction between safe duplicate suppression and lost work. Do not mark an event processed before its transaction commits merely to avoid another worker seeing it. Use the chosen engine's lease/claim or transaction mechanism, and understand recovery after a worker dies while holding ownership.

## Ordering and reconciliation

Do not derive a global ordering guarantee from event arrival time, an opaque event ID or a timestamp without the provider's contract. For state snapshots, compare permitted revisions or query authoritative current state when appropriate. For domain events, model legal transitions and the handling of duplicates, missing predecessors and late reversals.

An old success should not overwrite a newer revoked/cancelled state. An event for a missing local record may be a temporary ordering issue, a deleted entity, a configuration error or malicious input; classify it using the verified source and domain mapping. Avoid creating a new user/account automatically from a loosely matched email just to make processing succeed.

When provider state must be fetched, use the intended server credential and account scope, bound the call and keep private data out of logs. The fetch can fail after receipt; retain the inbox item and a recoverable state instead of losing the event or blocking the HTTP connection indefinitely.

## Verification matrix

Deliver duplicates concurrently to different service instances. Crash after inbox commit before acknowledgement, after domain commit before event completion, and after provider side effect before receipt storage. Send a later event first, then an older one; test a revoked entity and an unknown payload version. Assert one intended domain outcome and a recoverable record for blocked work.

Inspect actual database and worker state in integration tests. A unit test that calls the handler once and sees a `200` only proves that narrow path. Record receipt latency and processing lag separately without placing private payloads in metrics.

## Evidence and version cautions

Sources `src_nm_stripe_webhooks`, [provider delivery guidance](https://docs.stripe.com/webhooks); `src_nm_bullmq_idempotent`, [idempotent job design](https://docs.bullmq.io/patterns/idempotent-jobs); and `src_backend_extra_postgres_constraints`, [durable uniqueness](https://www.postgresql.org/docs/current/ddl-constraints.html), support the original workflow. See [source records](../../research/sources/sources.jsonl). Event identities, retry schedules, payload versions and acknowledgement rules must be checked against the selected provider and API version; no live webhook endpoint was exercised by this reference review.
