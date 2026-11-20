# Version changes, rotation and recovery for webhook consumers

## Inventory before changing a live endpoint

Record the provider product/API version, endpoint identity, test/production environment, connected-account scope, event subscriptions, signature keys and processing deployment. Discover these through the configured account/tool without printing credential values. “Prepare webhook setup” does not authorize creating or changing a production endpoint; complete a concrete plan before requesting genuinely missing authority.

Keep endpoint configuration and application code aligned. A deployed parser may support a different event representation than the version selected in the provider dashboard. An endpoint URL alone does not prove which account sends to it, which event types are enabled or whether the intended secret is installed.

## Change the contract deliberately

Treat provider payloads as an external versioned contract. Capture synthetic or properly minimized fixtures for the event types the feature actually consumes. Keep the processing model separate from the entire provider payload so a new optional field does not spread through the domain. Validate required fields and unknown-version behavior before applying effects.

For a provider-version migration, identify whether existing events, replays and newly delivered events use the old or new representation. Support an overlap when the provider/product needs it. Test semantic changes as well as field shapes: amount units, status transitions, absent/null values, entity references and snapshot versus event semantics can change behavior without a simple compile error.

Do not subscribe to every event type merely because a sample does. Each subscription adds parsing, retention, load and domain surface. Explicitly ignore a recognized irrelevant event only after authenticating the delivery and following the provider's acknowledgement contract. Unknown or malformed relevant events need a visible safe outcome, not silent success that loses required business state.

## Rotate secrets and deploy safely

Use the provider's supported key overlap and exact environment/account mapping. Stage code/configuration in an order that preserves verification during the intended overlap, then retire old material deliberately. Keep secrets in the service's configured store and use safe identifiers in diagnostics. Never put a signing secret in a native app, generated client or repository fixture.

When endpoints or workers change, verify both receipt and processing. A health endpoint, successful image build or dashboard “enabled” label does not establish that a signed delivery reaches the right consumer and produces the intended domain transition. Use an authorized test environment and synthetic provider events where available.

## Replay is a domain operation

Before replaying events, resolve the exact account/environment, event range, current state and intended repair. A replay can trigger external effects if idempotency or historical mapping is incomplete. Preparation/diagnosis does not authorize replaying production events or cancelling provider resources.

Use the same event identity and durable processing record where the provider permits it. Distinguish retrying a transient failure from intentionally correcting an earlier wrong domain outcome. A correction may require a forward domain action or compensation under product policy; deleting the inbox row to “try again” can erase the evidence and permit a second irreversible effect.

| Operational symptom | Inspect first | Avoid as a default |
| --- | --- | --- |
| Signature failures | Raw-body pipeline, active key, clock and account/environment | Disable verification |
| Provider retries despite success logs | Actual HTTP outcome and durable admission boundary | Assume a log line proves acknowledgement |
| Growing processing lag | Dependency health, poison events, worker ownership and rate limits | Increase concurrency without a capacity model |
| Duplicate domain effects | Event/operation scopes and transaction boundaries | Add only a process-local cache |
| Missing state after a version change | Endpoint version, fixtures and semantic mapping | Reparse all production payloads under the new schema blindly |

## Diagnostics and acceptance

Keep safe counts for admitted, duplicate, blocked, failed and completed events, plus processing age/lag. Distinguish auth/protocol failures from domain and dependency failures. Retain a minimal repair receipt and correlation ID; avoid raw payloads, account secrets and signatures in general logs or alert bodies.

Test rotation overlap, old/new fixtures, replay after completion, unknown event types, replay with expired historical mappings and a timeout after a committed effect. Verify that an operator can identify the intended repair without receiving private customer content. Document the exact observed provider state after an already authorized change, including what remains unverified.

## Evidence and version cautions

`src_nm_stripe_webhooks` identifies [the provider webhook contract](https://docs.stripe.com/webhooks); `src_nm_stripe_idempotency` identifies [provider request idempotency](https://docs.stripe.com/api/idempotent_requests). `src_backend_extra_node_crypto` supplies [cryptographic primitive details](https://nodejs.org/api/crypto.html), and `src_nm_otel_node` supplies [Node instrumentation guidance](https://opentelemetry.io/docs/languages/js/getting-started/nodejs/). These sources inform an original operating process, not a universal provider schedule or guarantee. Read [source records](../../research/sources/sources.jsonl) and current account/version documentation before a live mutation.
