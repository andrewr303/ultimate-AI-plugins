# Mutation lifecycle, idempotency and stable errors

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Inputs and ownership

Determine what the requested mutation changes, which authenticated principal owns it, whether it calls external systems and how a client learns the final result. Identify the authoritative database transaction and every non-transactional side effect. Establish the product's duplicate/conflict policy before enabling retry. A network request ID, database transaction and durable business operation ID are different concepts.

The iOS app, a widget action, a web client and a resumed background transfer may all attempt the same work. Give the operation a stable identity before sending it when the domain requires retry after app termination. Preserve that identity across reconnects; bind the backend record to the correct principal, operation and relevant payload fingerprint. Do not use email addresses or other private values as public idempotency keys.

## Model the state transition

Define pending, accepted, committed, failed and reconciled states only where they have distinct behavior. An accepted response must name its actual durability boundary. A response sent after adding an item to process memory cannot promise durable completion. If a request starts asynchronous work, expose a supported status/reconciliation path rather than making the app guess whether a timeout means success.

For a valid duplicate, return the existing outcome or supported in-progress state. Reject an operation key reused for a different account or payload. Use atomic database constraints/transactions where needed to prevent concurrent duplicate commits. A provider's own idempotency retention, parameter comparison and error caching rules are provider-specific; they do not automatically define the application's lifetime or recovery policy.

## Implementation sequence

1. Write the operation's invariant and before/after state. Identify the exact database rows and external side effects involved.
2. Choose the operation key scope and durable receipt/result representation. Define concurrent in-progress handling, expiration and safe recovery from abandoned work.
3. Atomically admit or reject the operation using the project's database primitives. Authorize the resource in the same domain flow; token parsing alone is insufficient.
4. Keep external calls outside unsupported assumptions of database atomicity. Use an existing outbox/job/reconciliation boundary when it solves a demonstrated cross-system gap.
5. Return a stable machine code and safe human-facing context. Separate unauthorized, invalid, conflict, temporary dependency failure and unknown completion. Include a safe correlation/operation identifier, not internal stack traces.
6. Map these results into Swift/web state deliberately. User cancellation stops ownership of UI work but must not be presented as proof a remote side effect was undone.

## Failure cases worth a real test

| Race or interruption | Expected property |
| --- | --- |
| Simultaneous identical requests | At most one intended authoritative mutation, consistent repeated result |
| Timeout after commit before response | Client reconciles using stable operation identity |
| Same key, different payload | Explicit rejection instead of silently executing another action |
| Logout/account switch during completion | Result cannot update another account's view/cache |
| Process death after external mutation | Durable recovery can determine or reconcile outcome |
| Stale optimistic version | Product conflict is distinct from a generic transport retry |

## Verification and handoff

Control concurrent admissions with a test gate rather than hoping two requests overlap. Use the real database mechanism for uniqueness/transaction behavior; a mock map does not establish distributed concurrency safety. Inject provider responses for timeout, rejection and uncertain completion, and test a repeated operation after server restart where the requirement includes persistence.

Return the chosen scope/lifetime policy, atomicity boundary, public response/error behavior and recovery procedure. State which part was tested with mocks, which with a real local store and which needs the configured provider. Avoid exactly-once delivery claims: the guarantee should describe the business invariant actually established.

## Sources and applicability

- [HTTP | Node.js v26.12.1 Documentation](https://nodejs.org/api/http.html) — `src_nm_node_http`.
- [PostgreSQL: Documentation: 18: 13.2. Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — `src_nm_postgres_isolation`.
- [Idempotent requests | Stripe API Reference](https://docs.stripe.com/api/idempotent_requests) — `src_nm_stripe_idempotency`.
- [Idempotent jobs | BullMQ](https://docs.bullmq.io/patterns/idempotent-jobs) — `src_nm_bullmq_idempotent`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
