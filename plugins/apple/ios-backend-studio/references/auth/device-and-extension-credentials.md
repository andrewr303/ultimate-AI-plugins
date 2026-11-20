# Credentials usable by the right app or extension only

## Inputs and outputs

Inputs: the app’s existing session design, required background/extension access, device-lock behavior and sharing needs. Output: a credential/accessibility policy and narrow service interfaces that do not expose provider secrets.

## Workflow

1. Separate app session/access/refresh tokens, Apple identity credentials, Keychain item access and backend service credentials. Only client-appropriate secrets belong on the device.
2. Store small client secrets with Keychain Services and deliberate access groups/accessibility controls. Do not put an APNs provider `.p8`, database password or server-side signing secret in the app bundle or widget projection.
3. Share a Keychain group only with targets that need that credential. App Group membership, Keychain Sharing and a logged-in app singleton are not the same permission mechanism.
4. Match accessibility to actual use: lock-state restrictions can prevent background/extension access, and weakening them merely to suppress an error can violate the product’s exposure requirements.
5. Treat intent authentication policy as device interaction policy; separately validate backend identity and resource authorization on each relevant operation.
6. On sign-out/revocation/account switch, retire the right credentials and associated caches/jobs. Avoid silently leaving a widget or notification registration attached to the previous account.

## Failure cases and tests

Test locked device, first launch after reboot, absent Keychain item, denied access group, expired/revoked refresh token, concurrent refresh and old-account callbacks. Keep credential values out of logs and test artifacts. Use physical-device checks for protection/lock semantics; simulator success does not establish the complete security behavior.

## Cross-platform boundary

Reuse the session and error contract across Swift, Node, web and other clients, but preserve each platform’s secure storage and lifecycle. A Node endpoint must never accept “the Keychain was unlocked” as proof that a resource mutation is authorized.

## Access and process worksheet

Record the credential's role, issuer, intended audience, account scope, expiry/rotation, authorized targets and lock-state requirements. Keep the narrow client session interface usable from an app or eligible extension without exposing the backend's provider/database credentials.

A shared app-group projection can contain an opaque account-scoped presentation identifier and freshness information, but should not become a universal token bucket. Keychain access groups and accessibility controls must reflect which signed targets genuinely need each item. A failed extension lookup needs diagnosis of target entitlement, account and protection state before any policy is loosened.

## Acceptance matrix

| Case | Expected boundary |
| --- | --- |
| Widget runs with no app UI process | It obtains only its intended credential/service or a safe unavailable result |
| Device locked or just rebooted | Defined protected-data outcome; no insecure storage fallback |
| Target lacks a Keychain group | Clear configuration diagnosis, no widening to every target |
| Account switches during refresh | Old credential/cache cannot install under the new principal |
| Backend refresh token revoked | Client removes/re-authenticates the proper session without deleting unrelated data |

Node authentication tests and simulator checks do not prove real device lock/accessibility behavior. Verify that part on the supported target device.

## Platform and verification boundary

Read the selected project’s generated interfaces and SDK availability before adopting specific symbols. Article prose does not establish the project’s deployment target.

## Primary evidence

- `src_backend_apple_010` — [IntentAuthenticationPolicy](https://developer.apple.com/documentation/appintents/intentauthenticationpolicy)
- `src_backend_apple_029` — [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- `src_backend_apple_030` — [Keychain Access Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/keychain-access-groups)
- `src_backend_apple_034` — [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
