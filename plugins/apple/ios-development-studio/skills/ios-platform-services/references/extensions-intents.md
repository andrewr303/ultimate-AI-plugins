# Extensions, widgets and intents

## Target and storage boundary

Inspect app/extension identifiers, deployment targets, signing, capability files, build dependencies and which shared code actually belongs to both targets. Match entitlements to the actual use case and selected Apple team. Share only needed data; a widget should not require loading an entire app service container or exposing access tokens.

For an app-group store, verify the container URL and coordination behavior of the chosen persistence engine. Do not point independent writers at an arbitrary SQLite file. Handle absent store, migration in progress and stale snapshot with a usable placeholder. Preserve the app's ordinary behavior when the extension is absent.

## Widget workflow

Model placeholder, snapshot and timeline data as small immutable presentation values. Identify data freshness and the system's scheduling discretion. The app can request reloads when relevant data changes, but that is not a promise of exact execution. Avoid network fan-out in view construction. Keep sensitive content out of lock-screen surfaces according to actual product settings.

Route widget URLs or actions through the app's validated route decoder. Validate identifiers and authorization at resolution time; do not assume a previously generated link still grants access. Keep fallbacks for missing/deleted entities and a signed-out user. Do not infer new API availability from a source reference's version labels.

## App Intents and shortcuts

Identify intent input/output types, entity lookup, display names, discoverability and whether an action needs foreground UI or authenticated account state. Validate inputs and existing permissions at execution. A shortcut and a deep link must not bypass the same domain authorization enforced by the screen.

Inject clock/store/network boundaries for tests. Verify an existing entity, deleted entity, missing account, ambiguous query and repeated invocation. Use supported localized display representations and intentional error messages. Confirm generated metadata and extension registration by building the actual target with its toolchain.

## App Clips and Expo boundary

Treat an App Clip as a separately configured target with restricted scope, dependencies and invocation routes. Inspect current Apple limits and API availability rather than hardcoding a source snapshot's size/platform assumptions. If an Expo native module is involved, check the project's actual SDK compatibility and target membership. Do not run Expo prebuild over a manually maintained native host.

## Evidence to retain

Record target names, data-sharing boundary, entitlements changed, invalid-input results and build/device outcomes. Avoid putting container paths, account data or user-specific invocation payloads in public review artifacts.

Sources: `skills-lower/skills-main/plugins/expo/skills/expo-app-clip/` and `expo-module/`; SwiftUI and architecture uploads for state/route ownership. Current API contract: Apple's WidgetKit, App Intents and App Clips documentation and installed generated interfaces.
