# Live Activity freshness, end states and recovery

## Facts to resolve

Identify the durable domain event, current account, ActivityKit instance, applicable token/channel generation, server event revision and supported runtime. Decide what makes content stale, what ends the event, and whether a user's dismissal has any separate product meaning. Do not assume that removing a visual activity cancels the backend order, trip or workout.

## Workflow

1. Model the activity as a projection of an authoritative event rather than the event store itself. Persist enough app/server association to reconcile after a crash, account change or provider outage.
2. Coalesce queued updates when only the newest projection matters. Preserve a final state deliberately; do not let a late intermediate update overtake it or create a new activity accidentally.
3. Advance freshness using the supported stale-date field and truthful content. A timer or an unchanged screen must not imply fresh server data when no update arrived.
4. Treat provider success as one layer. Inspect APNs results and the activity's actual lifecycle separately, and use app launch/foreground reconciliation to heal lost or ignored pushes.
5. On account/permission changes, stop exposing private state through the applicable instance and retire associated delivery addresses. Do not clear another user's activity or all app data as a generic cleanup step.
6. End with the latest final ContentState and an intentional supported dismissal policy. Handle an already-ended/dismissed instance idempotently. A scheduled job that runs late must check whether the domain event still needs a display update.

## Token and process boundary

The app observes activity/token streams and authorization updates; the Node server owns its provider credentials and durable event/job state; the extension renders a bounded snapshot. Each can be restarted independently. A token rotation is not a new domain event, and a backend retry is not a reason to start another native activity without a valid start command.

When a task is cancelled locally, decide whether remote work was never sent, was accepted, completed, or remains uncertain. The UI can report pending reconciliation instead of manufacturing a definitive failure. Native budgets and user frequent-update controls remain independent of backend queue throughput.

## Failure cases and tests

| Controlled case | Required observation |
| --- | --- |
| Update reaches APNs after the activity ends | No claimed renewed display; final event remains durable |
| Final push is lost | Foreground reconciliation can still settle the event |
| Activity is dismissed by the user | Domain action is not silently cancelled |
| Current token changes while retries exist | Old generation retired according to explicit policy |
| Server process restarts with pending jobs | Work is recovered/coalesced with preserved expiry/revision |
| Native app crashes then relaunches | Ongoing instances inspected and reconciled, not duplicated |
| Content stops arriving | Stale state is visible and accurate |
| One account becomes another | No previous account's private activity data is retained accidentally |

Test ordering, idempotency and classification with a fake clock/transport and controlled app service. Then verify the selected native lifecycle, device settings, compact/expanded/Lock Screen presentations and push path in the actual Apple environment. Report which layer passed; do not call all layers “real time” based on a unit test.

## Availability and evidence limit

ActivityKit's base types and newer push-start/channel/scheduling APIs have different introductions. Use generated SDK interfaces and current official docs for the chosen path. This reference does not raise the deployment target or promise scheduling/delivery. No Xcode build, real APNs send or native activity was executed while authoring it.


## Primary source record

- `src_backend_apple_011` — [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- `src_backend_apple_012` — [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- `src_backend_apple_013` — [ActivityAttributes](https://developer.apple.com/documentation/activitykit/activityattributes)
- `src_backend_apple_014` — [ActivityAuthorizationInfo](https://developer.apple.com/documentation/activitykit/activityauthorizationinfo)
- `src_backend_apple_016` — [Sending notification requests to APNs](https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns)


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
