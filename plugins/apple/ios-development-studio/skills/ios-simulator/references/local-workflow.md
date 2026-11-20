# Local simulator workflow

## Environment and target

Local iOS Simulator requires a compatible macOS/Xcode installation and an installed runtime. Discover actual versions and tools rather than relying on a minimum copied from an upload. `xcrun simctl` provides device lifecycle/app commands; interactive automation needs an available controller such as XCTest, idb or AXe. Do not install controllers automatically or fabricate tool names/bindings.

Read the installed help before constructing commands:

```sh
xcrun simctl help
xcrun simctl help list
xcrun simctl help boot
xcrun simctl help install
xcrun simctl help launch
```

Then discover devices using the help-supported JSON output. Prefer an exact available UDID matching the requested runtime/device. Multiple booted devices are not permission to choose an arbitrary one. Record whether the selected simulator was already running and who owns the session if that context is known.

A lifecycle template, after selectors and paths are resolved:

```sh
xcrun simctl boot "$IOS_SIMULATOR_UDID"
xcrun simctl install "$IOS_SIMULATOR_UDID" "$IOS_SIMULATOR_APP_PATH"
xcrun simctl launch "$IOS_SIMULATOR_UDID" "$IOS_APP_BUNDLE_ID"
```

Boot only when needed and wait using a supported readiness check. Do not hide every boot failure with `|| true`; inspect whether the device is already booted or actually failed. Use the app’s build settings to locate the real `.app`; do not hardcode a guessed product path.

## Semantic navigation

Inspect the available controller’s help and obtain a fresh accessibility tree. Select a unique accessibility identifier first, then an exact label/type when unambiguous. Read disabled/selected/value state before acting. A cached tree can become stale after navigation, overlays or scrolling, so refresh it before the next action.

If the controller reports success but UI state does not change, inspect modal overlays, hit targets, app responsiveness and tool/runtime compatibility. Avoid repeated blind taps. For coordinate fallback, establish points versus screenshot pixels and the screen’s orientation/scale. Webview-relative frames must not be used as global screen coordinates without conversion.

Screenshots are useful for layout, clipping, color and animation results. An accessibility tree cannot prove those visual properties; a screenshot cannot establish VoiceOver order or reachable actions. Use both when the acceptance criterion needs both.

## A reproducible UI scenario

State preconditions explicitly: app build, account/fixture, network behavior, permissions, locale, orientation, text size and starting screen. Prefer a dedicated test account and deterministic fixture over modifying the user’s real data. Execute a short sequence, asserting a visible/accessible state at each significant transition. Check failure, empty and cancellation states when relevant to the change.

Capture only the evidence needed: screenshot or UI tree, exact expected and observed result, runtime/UDID and app version. If the app crashes or hangs, preserve the first failure and use build/debug plus observability workflows. Do not reset the simulator to conceal the failed state.
