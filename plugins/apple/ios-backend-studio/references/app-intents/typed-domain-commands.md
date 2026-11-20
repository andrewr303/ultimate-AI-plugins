# App Intents, App Shortcuts and a shared Node command layer

## Inputs and outputs

Inputs: existing domain operations, stable entity IDs, session storage, localization and runtime support. Outputs: typed intent parameters/entities, an authorized service invocation and a localized success/failure result.

## Workflow

1. Map an intent to one concrete user action. Give it localized title, description and a parameter summary that matches the actual effect.
2. Use entity adapters that expose only the necessary ID, display and lookup behavior. Apple explicitly allows separate app-intent models that shadow an app’s internal model rather than coupling the whole persistence object graph to system discovery.
3. Resolve IDs or queries through an account-scoped repository. Recheck the entity and backend permission when `perform` runs; a previously suggested item may have changed or become unauthorized.
4. Invoke the same domain service used by app UI, then map its typed errors to a useful intent result. Keep provider tokens out of intent metadata, shortcut phrases and display representations.
5. Provide preconfigured shortcuts when they help discovery. Updating stored parameter suggestions is distinct from executing a server operation.
6. Select device authentication policy and foreground behavior for the actual action. Destructive or financially meaningful domain actions need the product’s confirmation/authorization design, not a blanket “Siri is trusted” assumption.

## Cross-platform boundary

Node.js owns domain authorization, durable writes and an explicit idempotency contract. The App Intent is a native adapter with localized inputs and system-specific lifecycle. Reusing transport DTOs is useful; sharing every UI/persistence class across targets is not required.

## Failure cases and tests

Test missing and ambiguous entities, a deleted saved shortcut target, an expired session, account switching, denied permission and retry after an uncertain response. For an action that needs UI, test the supported foreground continuation path rather than opening arbitrary views from a background process. Verify generated intent metadata by building the affected target in Xcode, then exercise Siri/Shortcuts on a suitable device.

## Resolve domain and process facts

Record which target contains the intent, where `perform` runs, which local service can exist in that process, and whether the action can complete without foreground UI. Do not reach into a SwiftUI view's transient state to satisfy an intent invoked when the app UI does not exist.

Give server-bound parameters stable meanings. A display string is not an entity identity, and a saved shortcut's identifier may become stale. Resolve identifiers against the current account and map known domain failures to a localized result that does not disclose another account's data. Keep business rules in the shared service/server boundary instead of reimplementing them separately for voice, widgets and the main screen.

## Acceptance matrix

| Fixture | Required behavior |
| --- | --- |
| Saved shortcut names an entity later deleted | Bounded missing-entity result |
| Two entity matches | Supported disambiguation rather than arbitrary first-match selection |
| Same action from UI and Siri | Equivalent domain authorization and effect semantics |
| Device authenticated but backend denies resource | Denied outcome; device policy cannot bypass backend checks |
| Process has no active UI graph | Service resolves explicitly or reports the required foreground path |

Build and inspect metadata for every affected target, then test the native system entrypoint. A unit test of the domain action does not prove Siri can discover or execute it.

## Platform and verification boundary

The fetched `AppIntent`, `AppEntity`, `AppShortcutsProvider` and authentication policy metadata lists iOS/iPadOS 16 and macOS 13 introductions. Individual newer execution/schema properties have their own availability and require installed-SDK checks. The current AppIntent page lists `openAppWhenRun` among deprecated members; do not apply a blanket rewrite to older targets.

## Primary evidence

- `src_backend_apple_007` — [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- `src_backend_apple_008` — [AppShortcutsProvider](https://developer.apple.com/documentation/appintents/appshortcutsprovider)
- `src_backend_apple_009` — [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- `src_backend_apple_010` — [IntentAuthenticationPolicy](https://developer.apple.com/documentation/appintents/intentauthenticationpolicy)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
