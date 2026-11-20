# A provider-neutral plan with concrete owners

## Preserve the integration that already exists

Provider-neutral means assigning a domain contract and keeping provider-specific behavior at an intentional boundary. It does not mean every provider shares credentials, failure semantics, pricing, deployment topology or data consistency. Inspect the actual configured backend, auth, store, worker, object storage and delivery integrations before proposing an adapter. Do not add abstractions for hypothetical replacements during a local fix.

For a greenfield decision, start with constraints that change the outcome: supported client behavior, data ownership, regional/account requirements, expected workload, transaction needs, native execution surfaces and the available operating environment. Recommend the smallest design that satisfies those constraints. Do not choose a service merely because its SDK appears in an example.

## Make the plan reviewable

Use a small plan with these fields:

| Field | Concrete content |
| --- | --- |
| User outcome | Trigger, permitted actor and visible result |
| Authority | Wire definition, domain state and account/entity owner |
| Existing implementation | Paths, resolved versions and adapters to preserve |
| New/changed seam | Exact handler, transport, projection or worker boundary |
| Failure policy | Timeout uncertainty, duplicate/retry rules and recovery |
| Compatibility | Supported old clients, snapshots, events and schema sequence |
| Verification | Fixture/test/build commands and candidate configuration |
| External action | Intended account/environment and already-authorized state change |

Keep product facts and missing prerequisites explicit. A new pricing, authentication, data-retention or regional policy is a real decision, not a default a coding guide can invent. Continue independent work while the needed owner resolves it.

## Separate shared contracts from service-specific semantics

Keep endpoint shapes, stable identifiers and domain errors in the chosen authority artifact. Derived Swift/TypeScript clients still need their own runtime transport and decoding integration. Server runtime validation and authorization remain independent from generation.

At a service boundary, document only semantics the domain actually uses. For a write operation, define operation-key scope, conflicting payload behavior, retention and durable outcome recording before automatic retries. For a webhook, resolve provider signature rules, ordering, acknowledgments and event identity. For media, define upload ownership, validation, completion and cleanup. Do not assume a provider's “success” field represents the same durable business state as another provider's receipt.

Native authentication is another explicit boundary. Public clients cannot safely hold a backend secret. Preserve the selected authorization flow and verifier; do not confuse an identity token with an API access credential, an Apple client-secret signature or an APNs provider token.

## Implement one slice, then evaluate the result

Choose a read or write that exercises the important seam. Implement it with controlled test dependencies, then verify denied access, invalid wire data, duplicates and old-client behavior as relevant. Add a widget/intent projection only when requested and keep its process/lifecycle contract separate. Expand the design after the evidence identifies another need, not to complete a framework checklist.

Finish with the implemented change, preserved choices, exact observed checks and pending platform/provider evidence. Preparation does not authorize deploying or provisioning the design. A proposed adapter that was not connected must remain labeled proposed.

Sources: src_nm_openapi_spec — [OpenAPI](https://spec.openapis.org/oas/v3.1.1.html); src_nm_oauth_native — [Native OAuth boundaries](https://www.rfc-editor.org/rfc/rfc8252.html); src_nm_stripe_idempotency — [A provider-specific idempotency contract](https://docs.stripe.com/api/idempotent_requests); src_nm_bullmq_idempotent — [Worker idempotence](https://docs.bullmq.io/patterns/idempotent-jobs). These inform separate boundaries without recommending a provider or queue by default.
