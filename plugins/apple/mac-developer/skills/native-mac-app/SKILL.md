---
name: native-mac-app
description: Build or improve native macOS apps with SwiftUI and AppKit, including document libraries, menu bar utilities, storage, permissions, keyboard commands, accessibility, and integration with an existing core.
---

# Build a native Mac app

Deliver working project changes. Read the repository's instructions, current targets, build configuration, and tests before editing. Preserve existing CLI, web, extension, and library interfaces unless the user requests replacement. Read [the implementation guide](references/implementation.md) for native structure and permission design.

## Establish the target

1. Record the actual OS, Xcode/Swift/SDK, deployment target, architectures, distribution channel, and bundle IDs. Use `sw_vers`, `xcodebuild -version`, `xcodebuild -list -json`, and project settings when on a Mac. On other hosts, inspect files and say which Mac checks remain. Never claim a Linux build proves an app launches on macOS.
2. Target macOS Golden Gate 27 or a user-selected recent minimum. Recheck [Apple's version page](https://support.apple.com/en-us/109033), current release notes, and API availability when making a version-dependent decision. The research baseline is 2026-11-03, not a permanent latest-version guarantee.
3. Choose SwiftUI scenes and models for a native interface; bridge to AppKit where window lifecycle, document behavior, editing, drag/drop, or specialized controls need it. Reuse a well-tested existing Swift core. For a JavaScript core, define a bounded process/IPC adapter rather than assuming WKWebView can execute Node.js. Distinguish a native UI from a web UI packaged inside a native app.

## Implement a useful vertical slice

- Create a real Xcode app target, or extend the existing target; include Info.plist, assets, entitlements, bundle identifiers, and reproducible build instructions. A Swift package containing a view alone is not a distributable app.
- Separate domain models and storage from scenes, platform adapters, browser bridges, and worker processes. Keep UI mutations on the main actor and move costly decoding, OCR, indexing, and I/O off the UI thread. Use cancellation and explicit error results; do not swallow failures.
- For the screenshot organizer: implement Inbox/Collections, thumbnail grid or list, selection/detail, search, tags, source URL, capture timestamp, duplicate handling, export, and recoverable import errors according to requested scope. Browser input enters the same ingestion boundary as file import.
- Implement File/Edit/View/Window commands and appropriate shortcuts; contextual commands act on focused selection. Support resizing, multiwindow behavior where useful, Settings, open/save panels, drag/drop, reveal/export, and an explicit Quit action. Specify what happens when the last window closes.
- Use standard controls and semantic materials; accommodate light/dark appearance, reduced motion/transparency, increased contrast, localized strings, and larger text. Test labels, focus order, keyboard-only operation, VoiceOver, and empty/loading/error states.

## Protect the library

Use the app's Application Support/container location for managed data, Caches for rebuildable thumbnails, and Keychain for secrets. Keep originals, thumbnails, metadata, and search indexes distinct. Use atomic import, durable transactions, schema migrations, backup/export, and tests that interrupt an import before acknowledging success. Do not hardcode a user's home path or mutate browser profile storage.

Inventory entitlements and privacy prompts by operation and executing process. App Sandbox, filesystem permissions, TCC, hardened runtime, and signing each solve different constraints. Request the minimum access when the user invokes the feature; preserve a useful denied-permission state. Receiving a screenshot file from a browser is not itself screen recording. Use ScreenCaptureKit permissions only if this Mac app captures screen content.

## Verify and hand off

Build with the discovered scheme and a separate derived-data directory. Run relevant model/storage tests and macOS UI smoke checks. Exercise first launch, reopen, missing/corrupt data, denied/revoked file access, migration, import/export round trip, cancellation, restart, accessibility, and large libraries. Validate both the original product and the app when sharing a core. Record exact commands, outcomes, artifact paths, and any checks requiring a Mac or signing identity. Do not label an unrun check as passed.
