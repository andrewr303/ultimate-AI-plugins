---
name: ios-networking
description: "Build and debug native iOS networking with URLSession, async isolation, cancellation, HTTP validation, bounded retries, pagination and offline consistency. Use for transport and API state, not adding a backend provider, release automation, or replacing an established client without a requirement."
---

# iOS networking

First read [the operating contract](../ios-development/references/operating-contract.md).

## Workflow

1. Inspect the current client, API contract, authentication integration, Swift mode and deployment minimum. Identify endpoint semantics, response/error shape, pagination and ownership before writing transport code.
2. Read [transport design](references/transport-design.md). Use [consistency and tests](references/consistency-and-tests.md) for retries, refresh races, offline data, pagination and deterministic verification.
3. Keep request construction, HTTP validation, decoding and domain mapping separate enough to test. Inject the transport and clock/sleep dependency at a useful seam; keep isolation explicit and avoid blanket unchecked Sendable.
4. Implement cancellation, finite timeouts, bounded retries only for eligible operations, and observable errors with sensitive fields redacted. Preserve the backend's idempotency semantics.
5. Exercise protocol fixtures for success, invalid status/body, timeout, cancellation, token refresh races and stale responses. Run integration checks only against an authorized configured environment.

## Boundaries and output

An async function does not guarantee heavy decoding runs off the main actor. A successful URLSession transfer does not by itself establish an acceptable HTTP response. Reachability is a UI hint; the actual request determines connectivity.

Do not invent endpoints, credentials, auth scopes or automatic replay rules for writes. Route credential storage, ATS and privacy declarations to `ios-security`. Finish with API assumptions, changes, test evidence and the limitations of mocks. References synthesize official Apple documentation and library architecture; see [source map](../../docs/source-map.md).
