# Interactive widget commands and acknowledgment reconciliation

## Decision to make

A button or toggle should execute a domain action; a link opens the app. Determine whether the action belongs in the widget process or app process and which data is shared before adding a network call.

## Workflow

1. Define a typed App Intent with already populated widget parameters. Widget interactions do not resolve missing parameters the same way a Siri conversation can.
2. Give the intent access to an appropriately scoped application service, not the entire app UI singleton graph. Match target membership to the intent protocol and actual execution process.
3. Send a stable command/resource identity and an app-generated idempotency key when the backend operation requires it. Backend authorization is mandatory even when local device authentication has succeeded.
4. Model pending, acknowledged and failed state. A toggle may display an optimistic state while `perform` is still running; it must later show server-confirmed state or an explicit retry/error outcome.
5. Persist the result needed by the timeline provider before returning from the intent. The automatic reload following interaction is useful only if the data source already contains the right state.
6. Handle errors into an appropriate visible stale/error state instead of relying only on a thrown error to explain failure to the widget user.

## Process and authentication boundary

Apple describes ordinary App Intent widget actions as running in the widget extension by default, with app-process behavior for specific intent protocols or execution configuration. Check the installed SDK; do not hardcode every intent as foreground app code. Choose `IntentAuthenticationPolicy` intentionally for the action, but do not confuse it with server authentication or resource authorization.

## Failure cases and tests

Deliver duplicate taps, a network timeout after a successful remote write, a denied resource, a logout during the action, an old acknowledgment after a newer command and a process stop before local state commits. Assert that retries do not duplicate the domain effect and the final widget state matches authoritative data. Also test delayed iPhone-to-Mac interaction, where an optimistic toggle can remain visible longer.

## Command result design

The widget-facing action should return a small typed outcome: authoritative success/revision, a recoverable pending status, denied/missing resource, or a safe failure that the presentation can explain. An HTTP timeout after a write is uncertain completion, not proof that the write failed. Keep a command identity so retry/reconciliation can settle that ambiguity without repeating the business effect.

A toggle's optimistic appearance is not a local transaction receipt. The handler must reconcile the local projection and server state, including the case where the system stops the process after the remote side committed. An outbox/pending-command row in the chosen local store may be appropriate; adding a second persistence engine solely for a widget is usually unnecessary.

## Acceptance matrix

| Fixture | Observe |
| --- | --- |
| Two rapid toggles with reversed responses | Current user intent/revision wins; late success cannot undo it |
| Backend write committed, response lost | Retry or fetch settles one domain effect |
| Authorization expires during perform | Useful denied/session state rather than false completed status |
| App/extension database versions differ | Compatible projection or safe unavailable result |
| iPhone widget interaction originates on Mac | Pending UI remains understandable during remote execution delay |

Instrument command identity, execution owner and reconciliation result without exposing raw tokens or private record payloads. Claim success only for the layer actually observed.

## Platform and verification boundary

`AppIntent` and `IntentAuthenticationPolicy` metadata lists iOS/iPadOS 16 and macOS 13 introductions. The interactive-widget article demonstrates an iOS 17 availability branch. These are source-specific observations, not permission to raise an existing deployment target.

## Primary evidence

- `src_backend_apple_004` — [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- `src_backend_apple_007` — [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- `src_backend_apple_010` — [IntentAuthenticationPolicy](https://developer.apple.com/documentation/appintents/intentauthenticationpolicy)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
