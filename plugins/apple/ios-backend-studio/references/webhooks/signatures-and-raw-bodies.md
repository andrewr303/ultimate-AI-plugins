# Verify the actual signature over the actual signed input

## Protocol and middleware inputs

Identify the provider and endpoint version, test/production account, signature header/envelope, key identifier, algorithm, signed input and replay rules. Some providers use HMAC over raw HTTP body bytes; others use signed tokens or certificate-backed envelopes. Do not apply one generic verifier to every Apple, payment or identity event.

Inspect middleware order before adding a verifier. A JSON parser, decompressor, proxy or text conversion can change the input the provider signed. Preserve the required byte representation at the route boundary with the framework's documented mechanism. Do not recreate it with JSON.stringify after parsing, normalize whitespace or change Unicode encoding and expect the same signature.

Set an intentional raw-body byte bound and timeout while receiving the request. Handle an aborted or truncated stream explicitly. Signature verification does not make an unlimited upload safe. Reject unsupported content types/encodings according to the actual provider contract rather than accepting every request into a large memory buffer.

## Authenticate before using event fields

Use the provider's maintained verification SDK when it supplies the correct protocol, with the resolved supported version and configured endpoint secret/key set. Decode-only JWT APIs do not verify a signature, issuer, audience or certificate chain. Do not trust an unverified body field or header that tells the server which arbitrary algorithm/key URL to use.

For a documented HMAC protocol, build exactly the prescribed signed input and decode the supplied digest strictly. Compare using the appropriate constant-time primitive once input lengths/encoding are valid. Node's timingSafeEqual requires equal byte lengths and does not guarantee that the surrounding code is timing-safe. Avoid hand-written equality loops, coercive digest parsing or accepting a truncated digest.

For a signed-token/certificate protocol, use the documented trust anchors, algorithms, claims and environment/account binding. Fetch keys only through the provider's intended trusted mechanism, with caching/rotation policy and bounded retrieval. Never follow an attacker-supplied key URL as a substitute for trust configuration. Keep identity-token verification distinct from client-secret or APNs signing.

## Replay and key lifecycle

If the provider signs a timestamp or nonce, enforce its documented interpretation and accepted replay window using a controlled clock. A timestamp that is merely present in unsigned JSON does not protect replay. Handle malformed, implausibly future and expired inputs deliberately; do not hardcode another provider's default window.

Plan key/secret rotation according to the provider's supported overlap. Record a safe key identifier or verification outcome without the secret, full signature or private payload. Accepting an old key indefinitely defeats rotation; removing it too early may reject legitimate deliveries still in flight. Determine the correct state from the provider's actual endpoint configuration.

Cryptographic authenticity establishes the signed sender/input under the chosen protocol, not every business decision. Map the authenticated event to the intended provider account, environment and internal tenant. A valid event from a different connected account must not affect an unrelated user's records.

## Failure behavior and diagnostics

Reject unverifiable input before domain effects. Keep public errors small and consistent enough for the documented integration without disclosing key material or internal parsing details. Retain bounded private diagnostics such as route, protocol/version, safe failure class, correlation ID and body length; do not log credentials, raw event bodies or signed capabilities by default.

Do not “temporarily” bypass signatures to resolve a provider outage. Diagnose middleware/body transformation, selected secret/account, clock interpretation and delivery environment. An endpoint verification failure should remain visible until its cause is fixed.

## Acceptance checks

Use synthetic signed fixtures or the actual provider's test helpers. Change one body byte, alter whitespace after signing, send malformed/truncated signatures, use a wrong environment secret, repeat an event, move the clock and interrupt body receipt. Assert that no inbox/domain work is admitted before successful verification. Also test a legitimate rotation overlap and a payload whose header format includes several signatures when the provider supports that form.

## Evidence and version cautions

Source `src_nm_stripe_webhooks` is [Stripe's webhook guide](https://docs.stripe.com/webhooks), including its provider-specific raw-body verification contract. `src_backend_extra_node_crypto` is the [Node crypto reference](https://nodejs.org/api/crypto.html); `src_nm_node_http` is [Node HTTP](https://nodejs.org/api/http.html). The [source catalog](../../research/sources/sources.jsonl) records these reads. This is original verification guidance, not a claim that all providers use Stripe's signing syntax or that a local HMAC example is a production provider verifier.
