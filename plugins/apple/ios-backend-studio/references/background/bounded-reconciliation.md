# Bounded background work and recoverable server reconciliation

## Decision to make

Select finite foreground-continuation, refresh, processing, background transfer or a notification service extension based on the job. A detached Swift task or an open socket does not create an unlimited server worker on the phone.

## Workflow

1. Keep the durable job/event on the Node server. The app requests a bounded incremental page or resumable step, performs a finite unit and persists a checkpoint.
2. Register the identifiers/capabilities needed by the selected Apple background API in the actual target. Treat earliest/scheduled opportunities as system decisions rather than cron guarantees.
3. Implement expiration handling that cancels work cooperatively, records resumable state and avoids an obsolete completion updating a newer account/session.
4. Signal each launched system task’s completion exactly once. Separate completion of the local attempt from remote acceptance and durable reconciliation.
5. When a silent push arrives, reconcile the newest authoritative state/cursor. Assume earlier pushes may be replaced or missed and the user may not open the app for some time.
6. Foreground launch/pull-to-refresh must heal missed background work, with a useful offline state when the server is unavailable.

## Server contract

Expose stable pagination/cursors, bounded results, explicit resource versions and idempotent writes where retries are valid. A resumed client should not need every past push to reconstruct state. Make authentication failure, retryable service failure and a completed/no-change result distinguishable.

## Failure cases and tests

Control expiration before and after persistence, simulate a partial page and retry, switch accounts during work, deliver duplicate wakeups and revoke credentials. Assert no duplicate side effect, a valid checkpoint and one completion signal. Node tests and scheduler fakes establish state transitions; actual scheduling, force-quit behavior and device power policy require the real Apple environment. The fetched BackgroundTasks sample explicitly requires a physical device.

## Data and task state to preserve

Keep the account/tenant, operation/cursor identity, last committed revision, pending local mutation and attempt outcome explicit. Persist a checkpoint only when the corresponding data is durable. If a process stops after a server commit but before the local checkpoint, the next attempt must be able to reconcile without duplicating the business effect.

Use the existing database and service seams when they already support this behavior. A background integration does not require a new queue/cloud service on the phone, and a second store can increase migration and account-isolation work instead of reducing it.

## Acceptance matrix

| Fixture | Required outcome |
| --- | --- |
| Expiration before request send | Recoverable local state; no fabricated server effect |
| Expiration after server commit | Explicit uncertainty reconciled by operation identity/current state |
| Partial incremental page saved | Cursor and data remain consistent on resume |
| Silent push is coalesced or absent | Next eligible foreground/background fetch heals missed updates |
| Session expires during a task | No work is retried as another account |
| Duplicate task/wakeup | Completion and durable effects remain idempotent |

Capture only bounded task IDs, state transitions and redacted errors. OS scheduling is an external input; control the app state machine in tests and observe actual scheduling separately on device.

## Platform and verification boundary

Read the selected project’s generated interfaces and SDK availability before adopting specific symbols. Article prose does not establish the project’s deployment target.

## Primary evidence

- `src_backend_apple_019` — [Pushing background updates to your App](https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app)
- `src_backend_apple_021` — [Choosing Background Strategies for Your App](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- `src_backend_apple_022` — [Refreshing and Maintaining Your App Using Background Tasks](https://developer.apple.com/documentation/backgroundtasks/refreshing-and-maintaining-your-app-using-background-tasks)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
