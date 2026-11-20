# Application sessions, account changes and authorization

## Inputs and decisions

Inspect the existing identity provider, session format, account/tenant model, native/web client flows and supported extensions. A bearer credential need not be a JWT. Preserve a functioning provider/session design unless the task requires changing it; adding Sign in with Apple does not require replacing every other application login.

## Trust boundaries

Provider authentication establishes an external identity according to that provider's contract. Application session validation establishes the current app principal. Resource authorization decides what that principal may read or change. Keychain access and local device authentication control local interactions/storage. Keep those checks separate and prove the complete path.

Do not treat user IDs, tenant IDs, widget entity IDs, delivery tokens or a parsed token payload as independent authority. Derive the principal from the validated credential and resolve domain permissions at the operation boundary. The app's display name or relay email may change and is not a sufficient durable authorization key.

## Workflow

1. Verify identity/session material through the actual configured mechanism. For JWTs use an explicit trusted issuer/audience/algorithm/key policy; for opaque sessions use the configured server/session authority rather than trying to parse them as JWTs.
2. Resolve the account and tenant from trusted mapping. Apply current resource permissions after lookup, including when an entity was suggested or a deep link was created before access changed.
3. Define session expiry, refresh ownership and revocation behavior. Serialize or otherwise coordinate concurrent refresh according to the actual provider/session contract; do not let a late old-account completion replace the new account's credentials.
4. Decide offline behavior deliberately. Cached presentation may remain available within product rules, but it must not claim a privileged server mutation succeeded without authoritative evidence.
5. On sign-out/account change, clear or replace the intended session, projections, pending operations and personal delivery associations. Make server-side revocation/lifecycle policy robust when the final client cleanup request is lost.
6. For account linking/deletion or security-sensitive changes, implement the product's current proof/confirmation rules and audit outcome without credential contents. Preparation/review does not authorize performing those actions on a real account.

## Native integration and Apple roles

A Siri intent or widget action should use the same domain authorization as the app screen. Device authentication is helpful for local interaction but cannot grant access to another tenant. If Sign in with Apple is involved, verify provider identity on the server and manage an app-owned session; do not request a fresh interactive identity token for every ordinary API call. An APNs provider JWT is not a user login credential.

## Failure cases and controlled tests

| Fixture | Required behavior |
| --- | --- |
| Expired access credential and concurrent requests | One intentional refresh policy; no uncontrolled refresh storm |
| Refresh completes after an account switch | Old account cannot overwrite the current session |
| Valid session but unauthorized entity/tenant | Authorization fails without leaking private resource details |
| Replay or duplicate mutation after uncertain timeout | One durable domain effect according to operation identity |
| User revokes upstream credentials | Session lifecycle reconciles and requires the intended reauthentication |
| Sign-out network request is lost | Local UI remains safe and server recipient/session policy does not rely only on that request |
| App is offline | Truthful cached/pending state; no fictitious server confirmation |

Inject the clock, provider/session verifier and account repository for deterministic tests. Test denial as well as success. Use a configured authorized integration environment for real provider flows. Lock-state, biometric, signed-target and Siri invocation behavior require actual Apple-runtime checks; no such runtime was exercised for this reference.

## Evidence and availability scope

Apple's identity verification guide supports the distinction between verified provider identity and application-owned sessions, while native credential/capability samples are not a complete authorization system. The protocol verification algorithm must follow current provider metadata; do not apply one Apple token role's key/algorithm to another. No version in this reference is a new project deployment default.


## Primary source record

- `src_backend_apple_007` — [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- `src_backend_apple_010` — [IntentAuthenticationPolicy](https://developer.apple.com/documentation/appintents/intentauthenticationpolicy)
- `src_backend_apple_018` — [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- `src_backend_apple_029` — [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- `src_backend_apple_030` — [Keychain Access Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/keychain-access-groups)
- `src_backend_apple_034` — [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- `src_backend_apple_035` — [Verifying a user](https://developer.apple.com/documentation/signinwithapple/verifying-a-user)
- `src_backend_apple_036` — [apple-oidc-discovery](https://appleid.apple.com/.well-known/openid-configuration)
- `src_backend_apple_037` — [apple-jwks](https://appleid.apple.com/auth/keys)


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
