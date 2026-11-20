---
name: backend-webhooks
description: "Use for authenticated incoming provider webhooks, raw-body signature handling, replay resistance, durable event inboxes, ordering and safe recovery in a Node backend. Follow the actual provider protocol; do not treat arbitrary HMAC, decoded JWTs or a successful delivery response as proof of an authorized completed domain action."
---

# Provider webhook boundaries

First read the [operating contract](../../references/operating-contract.md).

1. Identify the provider, account/environment, endpoint version, signature scheme, secret/key lifecycle and domain actions. Inspect middleware that may already consume or transform the body.
2. Use [signature and raw-body handling](../../references/webhooks/signatures-and-raw-bodies.md) before trusting event data or admitting work.
3. Use [durable inbox processing](../../references/webhooks/inbox-processing-and-ordering.md) to separate safe receipt, duplicate handling, ordering and domain completion.
4. Use [provider changes and operations](../../references/webhooks/provider-change-and-operations.md) for version changes, key rotation, replay and recovery.
5. Verify bad signatures, altered bodies, duplicate/out-of-order events, unknown versions, competing workers and crashes at the admission/ack boundary. Keep fixtures synthetic and diagnostic output redacted.

Return the verified protocol, account/domain mapping, durable processing changes, exact tests and remaining live-provider limitations. Preparation does not authorize creating provider endpoints, replaying production events or changing live secrets.
