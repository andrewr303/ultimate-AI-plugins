# Deep links and iPhone widgets shown on Mac

## Inputs and outputs

Inputs: a canonical route decoder, entity IDs, authentication state and target capabilities. Output: a link that opens the relevant app scene and revalidates current access.

## Workflow

1. Use one deliberate `widgetURL` for the overall surface; use supported `Link` targets for distinct entities where the chosen family/runtime supports them.
2. Decode an allowlisted route schema into typed route values. Never execute arbitrary URL parameters as commands or trust an identifier as proof of permission.
3. Resolve the route against current account, tenant and entity state after launch. Show a useful signed-out, missing-data or access-denied outcome instead of forcing a stale cached screen.
4. Reuse the same domain route semantics from notification actions, Live Activities, widgets and app UI while retaining each entrypoint’s source/context.
5. When the widget is an iPhone widget displayed on Mac, account for remote execution on iPhone and delayed returned timeline data. Do not assume the intent or data store lives in the Mac app process.
6. Keep widget data-sharing configuration tied to the actual app/extension targets. A macOS `containerURL` value alone does not establish that the entitlement or underlying directory is usable.


## Shared-container implementation facts

Enumerate the participating app/extension targets, signing team and exact app-group identifiers before changing code. Use the framework-provided container URL and verify usable access. The macOS API may return a URL-shaped path even for an invalid group; iOS may return no URL. Never construct a private container pathname.

Sharing a directory does not coordinate multiple database writers. Use a versioned atomic snapshot or the selected persistence engine's supported coordination/history mechanism. Specify ownership of migrations, cleanup, account switching and protected data. Share only the data needed by the widget; app-group preferences are not a substitute for appropriately scoped Keychain storage.

## Cross-process acceptance matrix

| Case | Expected result |
| --- | --- |
| Group capability missing on one target | Bounded configuration failure and safe placeholder |
| Widget reads during a snapshot replacement | One complete compatible version, not partial data |
| New app writes while old extension still exists | Supported version decode/fallback |
| Deep link names another user's resource | Route resolves to denied/missing state after authorization |
| Mac receives delayed iPhone-widget update | UI does not imply immediate local execution |

## Failure cases and tests

Test cold start, warm start, a different active account, duplicate URL delivery, a deleted entity, malformed route input and a missing shared container. Verify the selected scene is correct in a multiwindow app. For iPhone widgets on Mac, test delayed acknowledgment and loss of reachability separately from a native macOS widget.

## Design caveats

Current WidgetKit articles differ in their family/version examples for link support, so verify the family and SDK rather than copying one old table as universal. Widget URL routing is a convenience entrypoint, not a backend authentication mechanism or a guarantee that a server mutation occurred.

## Platform and verification boundary

Read the selected project’s generated interfaces and SDK availability before adopting specific symbols. Article prose does not establish the project’s deployment target.

## Primary evidence

- `src_backend_apple_004` — [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- `src_backend_apple_005` — [Linking to specific app scenes from your widget or Live Activity](https://developer.apple.com/documentation/widgetkit/linking-to-specific-app-scenes-from-your-widget-or-live-activity)
- `src_backend_apple_006` — [Developing a WidgetKit strategy](https://developer.apple.com/documentation/widgetkit/developing-a-widgetkit-strategy)
- `src_backend_apple_025` — [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- `src_backend_apple_026` — [containerURL(forSecurityApplicationGroupIdentifier:)](https://developer.apple.com/documentation/foundation/filemanager/containerurl(forsecurityapplicationgroupidentifier:))

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


## Primary source record

- `src_backend_apple_025` — [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- `src_backend_apple_026` — [containerURL(forSecurityApplicationGroupIdentifier:)](https://developer.apple.com/documentation/foundation/filemanager/containerurl(forsecurityapplicationgroupidentifier:))
- `src_backend_apple_030` — [Keychain Access Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/keychain-access-groups)


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
