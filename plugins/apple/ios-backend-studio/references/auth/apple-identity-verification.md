# Sign in with Apple: identity verification and application sessions

## Inputs and outputs

Inputs: actual app/service identifiers, registered redirect configuration where applicable, an authorization response, expected audience and request nonce/state. Output: a verified provider identity mapped to an application principal and an application-owned session.

## Workflow

1. Configure the native capability and account flow in the actual signed target. Send identity/authentication material to the Node server over the existing secure API; a native callback alone is not a server verification.
2. Verify the provider signature using the official public signing keys and an explicitly allowed algorithm, then validate issuer, expected audience, expiry and the applicable nonce/request binding. Do not use decoded JWT claims as trusted input before verification.
3. Keep token roles separate: the Apple identity token, the server’s client-secret JWT, an APNs provider JWT and the app’s own session token are different credentials with different keys, claims and lifetimes.
4. Exchange/validate authorization material according to the current provider endpoint contract. Maintain application sessions rather than requiring a new interactive Apple identity token on every API call.
5. Map a stable verified provider subject into the domain account. Do not use display name or a relay email address as the sole durable account/authorization key.
6. Handle revoked/changed Apple credentials, account switches and refresh failures by invalidating the appropriate app session and requiring the correct user interaction. Preserve actual product account-deletion and data-retention decisions.

## Source inconsistency worth retaining

The fetched “Verifying a user” article literally says “JWS E256”. That wording is not a safe implementation contract. The actual official OIDC discovery document advertises `id_token_signing_alg_values_supported: ["RS256"]`, and the fetched public JWKS keys also declare `RS256`. This is same-author cross-surface evidence, not an independent organization check. Follow the live provider metadata and a maintained JOSE implementation with a deliberate algorithm allowlist; do not confuse identity-token verification with the ES256 APNs provider-signing role.

## Failure cases and tests

Use fixtures for invalid signature, wrong issuer/audience, replayed nonce, expired token, changed key ID, stale JWKS cache and authorization-code reuse. Test session/account revocation independently of a successful initial login. Never log raw identity/refresh tokens or put client signing keys in the native app. These are security integration checks, not a guarantee of policy/legal compliance or a substitute for the actual provider contract.

## Server integration seams

Keep provider verification, application-account lookup/creation and application-session issuance as separate inspectable steps. Do not trust an account/tenant field from the client merely because the accompanying Apple token verified. Resolve the verified provider subject through the project's account-linking policy and enforce the resulting domain authorization.

Use an explicit trust configuration for issuer, audiences, allowed algorithms and key retrieval/cache behavior. A token's own unverified `alg` or arbitrary key URL cannot choose the verification policy. Unknown key IDs may require a bounded refresh from the configured official source; repeatedly fetching keys for every malformed token is an avoidable load/availability problem.

## Acceptance matrix

| Fixture | Expected outcome |
| --- | --- |
| Token has a valid signature but wrong audience | Authentication fails for this application |
| Unverified claims name another tenant | Account/resource authorization still derives from trusted mapping |
| Provider key rotates | Bounded configured-source refresh, no verification disablement |
| Authorization code is replayed | Safe rejection/reconciliation according to provider contract |
| User revokes or changes Apple credentials | Appropriate application-session invalidation/re-authentication |

Never include identity tokens, refresh tokens, private signing keys or full provider payloads in support logs or packaged fixtures.

## Platform and verification boundary

The native Sign in with Apple sample lists iOS/iPadOS 13 as sample introductions. Server identity verification is a protocol/service contract, not an iOS deployment minimum. The public OIDC/JWKS observations were fetched on 2026-10-26 UTC and should be rechecked when implementing or diagnosing algorithm/key issues.

## Primary evidence

- `src_backend_apple_034` — [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- `src_backend_apple_035` — [Verifying a user](https://developer.apple.com/documentation/signinwithapple/verifying-a-user)
- `src_backend_apple_036` — [apple-oidc-discovery](https://appleid.apple.com/.well-known/openid-configuration)
- `src_backend_apple_037` — [apple-jwks](https://appleid.apple.com/auth/keys)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
