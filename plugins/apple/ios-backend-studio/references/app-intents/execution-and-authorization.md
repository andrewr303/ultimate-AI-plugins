# Intent execution, authentication and cancellation

## Inputs and decisions

Inspect the action's real side effect, current principal, entity lookup, backend endpoint, supported runtime and execution target. Choose a local device-authentication policy separately from server session validation. Determine whether the action can run without UI or needs a supported foreground continuation.

## Workflow

1. Map one intent to one domain command with explicit typed inputs. Resolve missing/ambiguous entities using the system's supported parameter/query behavior rather than a hidden default account or arbitrary first result.
2. Determine process ownership and target membership from the selected App Intent protocol and current SDK interfaces. A widget extension cannot assume an active app-only service singleton exists.
3. Obtain only the client credential the action needs through the existing secure session service. A local authentication policy cannot mint server trust, and unlocking a device does not grant access to an arbitrary backend record.
4. Invoke the authorized domain service with a stable operation identity where the command can be retried. Keep account identity derived from validated server credentials; caller-supplied tenant/entity IDs remain untrusted.
5. Define cancellation, expiration and uncertain completion. Stopping the Swift task does not undo a Node write. Reconcile a durable command receipt/current entity state before a repeat can create another effect.
6. Persist any local projection needed by the dependent widget or UI before reporting success. Return a localized truthful result for denied, missing, stale, pending or completed state.

## Permission and product boundaries

Use `IntentAuthenticationPolicy` for the desired local interaction requirements and current platform support. Do not require all intents to use one policy: reading a harmless public summary and modifying protected data are different product decisions. At the same time, do not weaken a credential's protection merely because a background action cannot read it while locked.

For consequential actions, respect the product's actual confirmation and authority design. An existing authorized user action should not be burdened with invented host approval steps, but an intent's discovery metadata also does not authorize an unrelated purchase, account deletion or publication. Keep those decisions in the application/backend contract.

## Failure cases and controlled verification

| Case | Expected boundary |
| --- | --- |
| Device unlock succeeds but session is revoked | Backend denial is handled honestly |
| Account changes while lookup is pending | Old result cannot act under the new account |
| Duplicate invocation or timeout after commit | One durable domain effect and a reconciled result |
| Cancellation before versus after remote acceptance | Distinct outcomes; no assumed rollback |
| Intent requires UI from an extension process | Uses a supported continuation or reports the limitation |
| Entity becomes unauthorized between query and perform | Permission checked again at execution |
| Credential unavailable after reboot/lock | Safe protected-data/session state |

Control service completions and clocks in unit tests instead of sleeping. Verify generated metadata and target membership with a real Xcode build. Exercise actual Siri/Shortcuts and lock behavior on a suitable runtime; a mocked `perform` test does not establish system invocation.

## Availability and version scope

The AppIntent/authentication-policy overview metadata lists iOS/iPadOS 16 and macOS 13 introductions. Individual execution, confirmation and schema APIs have separate requirements. Current docs list `openAppWhenRun` in a deprecated section; that is not a reason to rewrite a compatible older-target implementation without checking its SDK and behavior. No installed-target or device execution was performed while authoring this reference.


## Primary source record

- `src_backend_apple_007` — [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- `src_backend_apple_009` — [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- `src_backend_apple_010` — [IntentAuthenticationPolicy](https://developer.apple.com/documentation/appintents/intentauthenticationpolicy)
- `src_backend_apple_034` — [Implementing User Authentication with Sign in with Apple](https://developer.apple.com/documentation/authenticationservices/implementing-user-authentication-with-sign-in-with-apple)
- `src_backend_apple_035` — [Verifying a user](https://developer.apple.com/documentation/signinwithapple/verifying-a-user)


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
