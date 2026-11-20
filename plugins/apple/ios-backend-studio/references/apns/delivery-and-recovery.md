# APNs delivery, recovery and product state

## Inputs and outputs

Start with the real product event, recipient policy, notification kind, delivery expiry and the current registration state. Produce a durable job state machine and a diagnostic receipt that distinguishes the business effect from the notification attempt. A push cannot be the only durable record of an event that a client must eventually reconcile.

## Decide the notification's purpose

A visible notification asks for attention, a background notification offers an opportunity to refresh, and an ActivityKit push updates a specific activity surface. Choose the correct topic/push type and payload; do not turn one into another just to obtain a more aggressive delivery schedule. User presentation permission, provider registration and server authorization are different inputs.

Coalescing is appropriate when only the latest state matters, such as an unread-count projection. It is unsafe to interpret a collapse key as an exactly-once command or to collapse distinct domain operations that need separate accounting. Keep the authoritative event/cursor in the Node data plane and let the client fetch its current authorized view after waking.

## Workflow

1. Atomically record the relevant business event and the eligible notification work using the project's existing transaction/outbox design where warranted. An in-memory queue alone loses work on process restart.
2. Select the current recipient registration and enforce account/topic/environment constraints. Recheck whether the event is still useful before an attempt.
3. Construct a finite request with a deliberate expiration, correlation ID, push type and privacy-appropriate payload. Keep backend secrets and excessive private content out of it.
4. Classify the actual provider result. Authentication/configuration failures need repair; malformed payloads need correction; invalidated registration needs lifecycle handling; eligible transient failures may use bounded retry.
5. On uncertain completion, preserve the attempt identity and read available state before repeating an action that could produce a visible duplicate. Retrying a push must never repeat the underlying purchase, message or domain mutation.
6. On client launch/wake, reconcile from authoritative state using a stable cursor or revision. Treat the push's payload as context/hint unless the surface contract explicitly consumes a validated state projection.

## Background delivery boundary

Apple calls background pushes low priority and says delivery is not guaranteed. It may hold, replace or discard pending notifications, including when a user kills the app. A successful send and a correctly configured capability therefore do not justify saying “the app will run now.” Product UI needs a stale/offline path and foreground reconciliation.

## Failure cases and tests

| Controlled case | Observe |
| --- | --- |
| Old push arrives after a newer server revision | Newer state remains authoritative; no rollback of the UI |
| Duplicate provider attempt | Domain side effect is not executed again |
| Token rotates while work is queued | Job follows the explicit registration-version policy |
| User signs out before delivery | Private content and action authorization remain scoped correctly |
| Provider unavailable until expiry | Work terminates with an inspectable expired outcome |
| Background notification is never delivered | Next foreground fetch repairs the client without a missing-event gap |
| Notification action targets a deleted entity | Safe missing/denied outcome, no arbitrary route execution |

Use transport and clock test doubles for server transitions. Use a signed development app and sandbox APNs for the integration lane only when requested/configured. Record “provider accepted” separately from “device received”, “displayed” and “user acted”. Keep raw addresses and private payloads out of support logs.

## Platform and evidence limit

The source guides describe HTTP/2 APNs and native notification callbacks, not an installed Node package or a guaranteed transport stream count. Inspect the actual provider adapter and deployed runtime. Current best-effort delivery and background-execution limits must remain visible when choosing retry/alert policies. No live provider/device operation was run for this reference.


## Primary source record

- `src_backend_apple_016` — [Sending notification requests to APNs](https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns)
- `src_backend_apple_017` — [Setting up a remote notification server](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server)
- `src_backend_apple_018` — [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- `src_backend_apple_019` — [Pushing background updates to your App](https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app)
- `src_backend_apple_020` — [Handling notifications and notification-related actions](https://developer.apple.com/documentation/usernotifications/handling-notifications-and-notification-related-actions)


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
