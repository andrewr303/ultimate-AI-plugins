# Live Activity state, lifecycle and stale content

## Inputs and outputs

Inputs: one ongoing domain event/task, a stable domain ID, compact state and user authorization. Outputs: ActivityAttributes/static identity, ContentState/dynamic presentation, update/end behavior and a stale/final presentation.

## Workflow

1. Choose a suitable ongoing event instead of using a Live Activity as a permanent dashboard or unlimited background service.
2. Separate static attributes from changing content state, and give the app/server one versioned JSON contract for the dynamic state. Keep payloads small and avoid private data that is inappropriate for a highly visible Lock Screen surface.
3. Check authorization before starting and observe authorization changes. Starting or updating can still fail because runtime support and system limits differ.
4. Reconcile active ActivityKit instances on app launch. A process crash or removal from the display must not leave the app’s domain workflow in an incorrect state.
5. Include an explicit stale policy and a useful final state. A dismissed activity does not cancel a delivery/order or other backend action unless a separate authorized command actually does so.
6. End the activity when the underlying event ends and choose a supported dismissal policy. Do not keep it running purely to obtain more background time.

## Surface boundary

The Live Activity UI is part of a widget extension but is not a widget timeline. Its sandbox cannot independently access network/location updates. Feed state through ActivityKit in the app or the ActivityKit APNs channel. Native display/lifecycle limits and user controls are separate from durable backend state.

## Failure cases and tests

Exercise disabled authorization, app crash/relaunch with an ongoing activity, stale data, old updates after end, several simultaneous activities, explicit user dismissal and a final state delivered while offline. Verify decoded payloads with fixture data and then test the real selected iOS/iPadOS presentations. A successful Node serialization test does not establish Dynamic Island appearance or system delivery.

## State contract and ownership facts

Record the domain event identity, ActivityKit instance identity, account/tenant, attributes type, dynamic schema version and which service produces each field. A server event and a Live Activity instance are separate records: one domain event may be represented on several devices, while a person may dismiss one presentation without cancelling the event.

Use a compact normalized content projection, not a full database record. Choose consistent wire types and supported native decoding for dates, missing/null fields and numeric values. Keep assets available through an appropriate app preparation path; the activity display cannot fetch arbitrary images directly from a remote URL.

## Acceptance matrix

| Fixture | Required state behavior |
| --- | --- |
| User disables activities | App does not report an activity as running when start fails |
| Activity dismissed while backend event continues | Domain event remains intact; no implicit cancellation |
| Old update arrives after final state | Ended state is not reopened by an obsolete event |
| App restarts with active activities | Instances reconciled against authoritative event state |
| Content becomes stale while offline | Honest stale presentation instead of unchanged “live” assurance |
| Several activities for one account | IDs, relevance and cleanup remain instance-scoped |

Keep device UI and app/backend observability separate. A passing content-state fixture cannot prove native presentation, authorization or visibility.

## Platform and verification boundary

`ActivityAttributes` and `ActivityAuthorizationInfo` metadata lists iOS/iPadOS 16.1 introductions. Push-to-start, channels, scheduling and newer presentation features have independent availability. Do not assume the earliest ActivityKit minimum supports every current article example.

## Primary evidence

- `src_backend_apple_011` — [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- `src_backend_apple_013` — [ActivityAttributes](https://developer.apple.com/documentation/activitykit/activityattributes)
- `src_backend_apple_014` — [ActivityAuthorizationInfo](https://developer.apple.com/documentation/activitykit/activityauthorizationinfo)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
