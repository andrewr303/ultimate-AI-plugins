# Notification device registration and account-safe delivery

## Decision to make

Treat a device token as an opaque delivery address for a specific app/device/environment, not as user identity. Decide which account owns a registration and what changes when the person signs out or switches accounts.

## Workflow

1. Configure the actual app ID, Push Notifications capability and signed entitlement. Register through the platform API and handle both success and failure callbacks.
2. Send the newly returned token through an authenticated Node endpoint. Do not assume a cached local token remains valid or has a fixed length.
3. Store recipient registrations with account/tenant, app topic, environment and installation/lifecycle data needed by the product. Support multiple devices per account and retire obsolete associations deliberately.
4. Define sign-out, account-switch, uninstall/reinstall and revoked-access behavior. A token previously bound to one account must not receive another account’s private event because an old job survived.
5. Register notification categories/actions and map selected actions into the same authorized domain service used elsewhere. Revalidate resource access at execution; a payload route is untrusted input.
6. For background refresh, send a background push as a hint to reconcile current state. It must not be the only copy of an event or the mechanism that commits a critical server mutation.

## Delivery and permission boundary

Alert presentation permission, APNs registration, foreground handling and background execution are separate concerns. Background pushes can be delayed, throttled, coalesced or discarded. They do not show alert/sound/badge content. Provider acceptance and client action completion must be reported separately.

## Failure cases and tests

Test malformed/old token registration, duplicate registrations, two devices, account changes, an unauthorized topic, stale jobs, denied notification presentation, foreground delivery and a cold launch from an action. Verify that a push referencing deleted or unauthorized content fails safely and that app launch reconciles missed changes. Log registration IDs/hashes and error classes instead of raw device tokens or private payloads.

## Registration contract and ownership

Define a registration resource rather than treating a token string as the database primary key of a user. Inputs include an authenticated app principal, intended bundle/topic and environment plus the current opaque device address. Server-generated registration identity/version enables retiring the proper association even when the address changes. Derive account/tenant from verified authentication, not from a caller-supplied account ID alone.

Decide whether sign-out disables delivery, removes the association or retains explicitly nonpersonal notifications. Apply that policy to pending jobs as well as future selection. The product's behavior must remain safe if the client never completes a final sign-out network call. A delayed job must recheck the registration/account relationship according to the delivery policy.

## Acceptance matrix

| Scenario | Expected boundary |
| --- | --- |
| Two devices belong to one account | Both eligible registrations coexist; one does not overwrite the other |
| Same device changes accounts | Old personal delivery association cannot leak into the new account |
| App gets a new token after reinstall | New registration replaces/retires the intended old lifecycle only |
| Registration request names another tenant | Server ignores/rejects that authority claim |
| Device token is malformed or unexpected length | Opaque-input validation fails safely without fixed-size assumptions |

Audit logs need registration IDs and redacted classes, not raw delivery addresses. Device receipt must be measured through an explicit client event when that evidence is required; an APNs provider result cannot substitute for it.

## Platform and verification boundary

Read the selected project’s generated interfaces and SDK availability before adopting specific symbols. Article prose does not establish the project’s deployment target.

## Primary evidence

- `src_backend_apple_017` — [Setting up a remote notification server](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server)
- `src_backend_apple_018` — [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- `src_backend_apple_019` — [Pushing background updates to your App](https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app)
- `src_backend_apple_020` — [Handling notifications and notification-related actions](https://developer.apple.com/documentation/usernotifications/handling-notifications-and-notification-related-actions)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
