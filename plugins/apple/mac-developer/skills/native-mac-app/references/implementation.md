# Native implementation patterns

Research checked 2026-11-03. These are design recommendations; resolve exact SDK symbols and availability from installed headers and Apple documentation before use.

## Project and process boundaries

Prefer a structure such as `Domain/`, `Persistence/`, `MacApp/`, `Integrations/`, and a separately testable `Worker/` when needed. Maintain one canonical model/ingestion contract, not two independent implementations that drift. Keep UI state (selection, navigation, draft edits) separate from durable library state. Choose SwiftData/Core Data/SQLite from deployment target, migration complexity, query needs, and concurrency; do not select a store solely because it is newer.

Create an app target that can open a first useful window and import one item before adding background persistence. Put the core in a Swift package or existing shared module so it can run focused tests. An existing Node core can remain a Node core behind an explicit request/reply protocol; it does not become Swift by packaging it.

Use `WindowGroup` for independently openable library windows, `Window` for a unique auxiliary window, `DocumentGroup` when each user document is a first-class file, and `Settings` for preferences. `MenuBarExtra` is a scene for quick access while the application runs; it does not install a login item or establish a daemon. Keep real window and menu state synchronized. [SwiftUI menu bar](https://developer.apple.com/documentation/swiftui/building-and-customizing-the-menu-bar-with-swiftui), [MenuBarExtra](https://developer.apple.com/documentation/swiftui/menubarextra), [multiple windows](https://developer.apple.com/videos/play/wwdc2022/10061/).

Prefer system controls for selection, toolbars, split views, and menus. Use AppKit adaptors for unsupported behavior with clear ownership and delegate lifetime. Do not simulate window chrome inside a web page. Use named commands and focused values for actions; disable unavailable commands with a reason when useful. [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos/), [windows](https://developer.apple.com/design/human-interface-guidelines/windows).

## File access and storage

A managed library should have stable item IDs; an immutable original and its cryptographic digest; typed metadata; relative managed-file paths; migration version; and an ingestion receipt. Create a staging file, validate MIME/decoder and limits, write durable metadata/file state, then issue a receipt. Rebuild thumbnails and search indexes from canonical data. A failed transaction leaves recoverable staging or nothing, not a success badge for missing data. Define whether content dedup and repeated capture history are separate concepts.

For user-selected directories, use native panels and the relevant user-selected-file entitlement when sandboxed. Persist a security-scoped bookmark only when persistent access is needed. Resolve stored bookmarks, detect stale bookmarks, obtain access with `startAccessingSecurityScopedResource()`, and balance successful access with `stopAccessingSecurityScopedResource()` over the actual operation. A granted sandbox extension does not overrule POSIX permissions or privacy controls. Show a reconnect action for moved/deleted folders. [Sandbox file access](https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox), [security scope lifetime](https://developer.apple.com/documentation/foundation/nsurl/startaccessingsecurityscopedresource()).

Use App Groups only when the actual participating signed targets and distribution channel support the selected identifier. A Chrome extension does not gain App Group access by sharing a name. Do not pass arbitrary filesystem paths from browser messages into privileged code. If multiple native processes share SQLite, choose a documented concurrency model and migration owner; do not let each process run migrations independently at startup.

## Permission map

| Feature | Design obligation |
| --- | --- |
| Browser sends an existing image | Validate/import image; no screen-recording prompt merely to receive it |
| Mac app captures a display/window | Use public ScreenCaptureKit APIs, check availability and screen-capture consent, explain denial/revocation |
| User selects external folder | Native picker, scoped access if sandboxed, recoverable revoked access |
| Apple Events automation | Document target automation and purpose; request only for the selected automation feature |
| Global input monitoring or Accessibility control | Justify separately; do not request to make ordinary app controls accessible |
| Child CLI in a sandboxed app | Verify sandbox inheritance requirements and actual helper execution model |

An entitlement is not automatic TCC consent. Never recommend disabling SIP, Gatekeeper, the sandbox, or privacy databases as a shipping solution. Full Disk Access cannot be self-granted by code. [App Sandbox](https://developer.apple.com/documentation/security/protecting-user-data-with-app-sandbox), [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit).

## Native acceptance evidence

On a Mac, import representative PNG/JPEG/WebP/HEIC as supported, malformed files, huge dimensions, duplicates, and interrupted transfers; relaunch and verify persisted originals and metadata. Search/tag/move/export should preserve source information. Exercise keyboard navigation, VoiceOver labels and reading order, focus after dialogs, contrast, zoomed text, dark mode, and window restoration. Measure startup and scrolling using the repository's realistic library fixture. Use `xcodebuild test` for test targets and direct app launch/UI automation for runtime behavior. Report any unsupported image format or system configuration explicitly.

## Version and source policy

[Apple's macOS version list](https://support.apple.com/en-us/109033) identifies Golden Gate as major version 27 and Tahoe as 26 at the research date. Patch numbers and SDK support change; validate them live for each task. Use availability guards and build with the chosen minimum target. Do not infer that every new framework works on every recent macOS version.
