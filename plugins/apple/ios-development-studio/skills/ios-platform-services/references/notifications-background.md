# Notifications and background execution

## Permission and provider boundary

Distinguish local notification scheduling, remote provider delivery, app receipt, foreground presentation and a notification action opening the app. Request notification permission in product context with a denial path. Use the real usage and privacy requirements; do not claim permission a feature does not need. Never store a provider signing key in the client.

For push registration, account for token replacement, sign-out and account switching. The server must bind tokens to the correct authorized account and app environment. A token is an address for delivery, not proof of user identity. Avoid logging its raw value or treating failed delivery as immediate proof of an invalid installation.

Handle repeated, delayed and out-of-order notifications. Decode only an allowlisted route/action schema, validate identifiers, and recheck access when opening content. Reconcile current state rather than applying destructive actions from an arbitrary payload. Keep processing idempotent when the action may run more than once.

## Background task lifecycle

Determine whether the job belongs to a supported background task, a background URLSession transfer, a user-initiated finite task or no background execution at all. Inspect identifiers, registration, permitted configuration and scheduling constraints for the selected API. A timer or detached Swift task does not confer indefinite execution.

Define a bounded unit of work, completion policy and checkpoint. Register expiration handling that cooperatively cancels work and avoids publishing stale partial state. Signal completion exactly once for each launched system task. Persist enough progress for the next opportunity without storing secret payloads in generic logs. Do not report submission/scheduling as actual execution.

The UI must remain correct when the process is suspended or terminated, delivery is coalesced, the user disables refresh, network access is absent or the OS does not launch the job. Separate client retry from server idempotency; cancellation alone does not undo a remote mutation.

## Verification matrix

| Scenario | Observe |
| --- | --- |
| Permission denied | Usable in-app fallback, no misleading enabled state |
| Token/account changes | Old association cleared or retired; new registration scoped correctly |
| Duplicate/late payload | No duplicate domain mutation or stale view overwrite |
| Expiration during work | Cooperative stop, durable checkpoint, one completion signal |
| Process killed before completion | Next launch reconciles current authoritative state |
| Unsupported runtime | Feature degrades using the actual availability branch |

Use test doubles for scheduling and transport to exercise state transitions. A simulated push or debugger-triggered background task demonstrates handler behavior; it does not establish production provider delivery or scheduling guarantees. Verify relevant real-device and server paths separately.

Sources: simulator upload's push/state-capture topics, concurrency upload's cancellation/continuation topics, and observability upload's bounded diagnostics. Verify notification and BackgroundTasks APIs against official Apple docs and the actual SDK.
