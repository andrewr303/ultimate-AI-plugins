# Node.js APNs provider boundary and operational policy

## Inputs and outputs

Inputs: selected Apple team/topic/environment, server-held signing key, authorized recipient associations and a durable notification job. Output: an APNs HTTP/2 request plus a classified provider receipt, never a claimed device-display result.

## Workflow

1. Keep APNs credentials in the server deployment’s secret store. The native app registers its current delivery address; it never receives the `.p8` provider key or a provider JWT minting capability.
2. Model separate connection pools for incompatible team/key/topic/environment scopes. Reuse healthy HTTP/2 connections, handle connection shutdowns and do not assume a fixed concurrent-stream count.
3. Sign an ES256 provider JWT with the intended key ID, team issuer and issued-at time. It is a signed JWS; signing does not hide its claims. Apple’s article uses “encrypt” colloquially, so do not copy that wording into a security design.
4. Cache/refresh provider authentication according to the current APNs time/rotation requirements instead of minting a new token for every notification. Account for clock skew and rejected/rotated keys.
5. Build the POST device path, authorization, topic, push type, priority, expiry and collapse behavior deliberately. Keep custom routing/domain fields out of `aps` unless their schema belongs there.
6. Persist a correlation identifier and inspect the response for each request. Distinguish credential, malformed payload, stale recipient and transient transport failures; only retry an eligible failure with bounded backoff and job expiry.

## Contract and data boundary

APNs is best effort and may reorder/coalesce notifications. An acknowledgment means provider acceptance, not user receipt or a completed domain action. Use the Node database/event log as the durable authority. A notification usually carries a small projection or a signal to fetch authorized state; it is not a reliable unbounded event bus.

Apple’s current server guide discusses a trust-root transition. Use the deployment’s maintained TLS trust store and check the live Apple notice; do not pin an obsolete root or disable verification to repair a connection. Certificate and token authentication have different supported push-type behavior.

## Failure cases and tests

Use a controlled HTTP/2 transport to test the exact method/path/headers/body, rejected signing material, clock expiry, GOAWAY, uncertain completion and job coalescing. Use separate sandbox/device verification for provider integration. Never package real tokens/keys in examples or add live APNs sends to a generic unit test.

## Facts to resolve before editing

Record the deployment runtime, HTTP/2 support, Apple team, selected credential kind, topic allowlist, environment and existing job store. Inventory certificate/key rotation ownership without printing credentials. A runtime that supports HTTP requests is not automatically configured for the persistent HTTP/2 behavior the provider needs.

The operation receipt should retain a stable internal job ID, an APNs correlation ID, recipient-registration version, attempted topic/environment, expiry and classified outcome. Use a reference to an internal recipient row rather than logging the raw address. Keep a distinction between “queued”, “provider accepted”, “retry eligible”, “terminally rejected” and any separately observed client acknowledgment.

## Controlled verification matrix

| Fixture | Required observation |
| --- | --- |
| Same job retried after uncertain transport completion | No duplicate domain mutation; expiration/coalescing policy applied |
| Key scope or topic mismatch | Classified configuration failure, no blind retry storm |
| Pool receives GOAWAY or closes midstream | Owned jobs remain recoverable; new streams use a valid pool |
| Clock/provider JWT is stale | Token policy refreshes safely; failure does not disclose token contents |
| Expired business notification | Job discarded intentionally instead of delivering misleading old state |

A provider adapter test can establish these transitions with a controlled clock and transport. It cannot establish Apple scheduling, the user's device state or notification presentation.

## Platform and verification boundary

Read the selected project’s generated interfaces and SDK availability before adopting specific symbols. Article prose does not establish the project’s deployment target.

## Primary evidence

- `src_backend_apple_015` — [Establishing a token-based connection to APNs](https://developer.apple.com/documentation/usernotifications/establishing-a-token-based-connection-to-apns)
- `src_backend_apple_016` — [Sending notification requests to APNs](https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns)
- `src_backend_apple_017` — [Setting up a remote notification server](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
