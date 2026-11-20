# ActivityKit APNs tokens, payloads and update ordering

## Inputs and outputs

Inputs: activity-specific tokens or a supported channel, authenticated account/domain event, exact app bundle topic and a ContentState wire schema. Output: a typed APNs job with expiry, ordering information and an inspectable provider result.

## Workflow

1. Distinguish ordinary app notification device tokens, per-activity update tokens, push-to-start tokens and broadcast channel IDs. They serve different roles; do not put all of them in one untyped “push token” column.
2. Subscribe to ActivityKit token-update streams; initial tokens arrive asynchronously and may rotate. Send them through an authenticated registration endpoint and retire the outdated association.
3. Construct the ActivityKit request with `apns-push-type: liveactivity`, the matching `<bundleID>.push-type.liveactivity` topic and an appropriate priority. Keep the APNs signing key on the provider server.
4. Use `aps.timestamp` plus `event` (`start`, `update` or `end`) and a `content-state` that matches the native type. The article warns against custom JSON encoding strategies because the system uses its default decoding strategies.
5. Include final content when ending, an intentional stale date, and a suitable alert only when the event should notify the person. Bind each pending update to the current activity/token generation.
6. Treat broadcast update/end support and push-to-start support as separate capability paths. Apple explicitly says broadcast pushes do not start a Live Activity.

## Reliability boundary

An APNs acceptance response does not prove display. Network loss, system policy and an ended activity can prevent an update from appearing. Use app reconciliation in addition to pushes, coalesce obsolete pending state and respect push budgets/user frequent-update settings. A shared backend should not promise the widget or activity updates immediately on every server event.

## Failure cases and tests

Test rotated token, wrong topic/environment, payload decoding mismatch, old timestamp, update after end, duplicate start request, denied frequent updates and uncertain provider completion. Keep production logs to correlation IDs and result classes; official sample token logging is a local debug example, not a production logging policy. Test real ActivityKit behavior only on supported simulator/device configurations and label provider-only checks separately.

## Registration and wire fixtures

Use separate registration kinds for app notification tokens, activity update tokens, push-to-start tokens and channel subscription information. Store only the association needed to address the correct domain activity/account/device, and retire prior token generations. Do not reuse an ordinary APNs device token merely because it has a similar representation.

Build a shared golden fixture for every supported start/update/end payload. The Node producer and native ContentState decoder should agree on field names, date formats, optionality and numeric values. Generated types are useful but the actual JSON emitted by the server and decoded by the activity still needs validation. Payload or attribute schema migrations must preserve already-installed clients deliberately.

## Acceptance matrix

| Fixture | Observe |
| --- | --- |
| Push token is initially unavailable | Registration waits for the actual asynchronous update |
| Token rotates after a job was queued | Correct generation or explicit stale-registration failure |
| Header topic/push type mismatch | Classified provider failure, no fallback to an unrelated topic |
| Unsupported channel/start option on an old client | Supported fallback rather than a falsely claimed start |
| JSON encoding strategy differs from native expectation | Golden fixture catches the incompatible representation |

Provider receipts and actual display observations are separate evidence, and raw activity tokens remain out of production logs.

## Platform and verification boundary

Apple’s current article says remote start is unavailable on iOS/iPadOS 17.1 and earlier; channels and some start-payload options describe iOS/iPadOS 18 paths. Verify the exact chosen API and payload option in the selected SDK and runtime. These are source observations, not a plugin-wide minimum.

## Primary evidence

- `src_backend_apple_012` — [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- `src_backend_apple_015` — [Establishing a token-based connection to APNs](https://developer.apple.com/documentation/usernotifications/establishing-a-token-based-connection-to-apns)
- `src_backend_apple_016` — [Sending notification requests to APNs](https://developer.apple.com/documentation/usernotifications/sending-notification-requests-to-apns)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
