---
name: browser-companion
description: "Use when turning a Chrome or other browser extension into a macOS companion app, connecting an extension to a native Mac app, importing web clips or screenshots, or porting a web extension to Safari while preserving its original browser behavior."
---

# Build a browser extension and Mac app that work together

Deliver an additive companion architecture. Keep the original extension usable when the Mac app is absent, stopped, incompatible, or removed. Build working code and exercise the real extension-to-app round trip; an architecture document alone is not completion for an implementation request.

## Establish the existing contract

1. Read the extension manifest, service worker/background code, capture path, storage, build system, tests, and release identity. Record supported browsers and minimum versions. Run its existing checks and capture behavior before modifying it.
2. Keep its store identity, extension ID, existing data, permissions, shortcuts, capture UX, and original outputs unless a requested change requires otherwise. Add the companion integration behind capability detection. Do not rewrite the extension solely to create a Mac app.
3. Identify reusable domain logic and schemas; leave browser APIs in browser adapters and native APIs in native adapters. Share a JSON contract and fixtures across languages. A Swift app cannot directly import a Node package as native Swift code.
4. Decide whether the user wants a **native Mac companion**, a **Safari port**, or both. Packaging an extension for Safari does not automatically create a useful native organizer. A Chrome extension cannot run unchanged as a standalone macOS app or inside WKWebView.

Read [browser integration](references/browser-integration.md) for platform rules, installation and sources. Read [the clipper contract](references/clipper-contract.md) for an implementation design and acceptance matrix.

The bundled [Node framing utility](scripts/README.md) handles bounded JSON-object frames and has portable tests for fragmented input, UTF-8, invalid lengths, malformed data and EOF. Reuse it for an appropriate Node host, or use its cases as fixtures for a Swift host. It supplies framing only; implement origin/peer checks, application schemas, persistence and installation separately.

## Implement the connection

- Default to Chrome native messaging for a Chrome companion. Use a small signed native host as an adapter to the app's durable inbox or receiver service. Browser-launched host lifetime and background-service lifetime are separate decisions.
- Preserve app-independent capture/export. When delivery is unavailable, persist clips locally, show pending status and offer retry/export. Never silently drop a clip or claim import success before a durable commit.
- Persist the Manifest V3 outbox and attachments before attempting delivery. Treat service worker restarts, browser closure, and disconnects as ordinary events. Use bounded retry and an explicit retry action; do not depend on an immortal worker.
- Validate each trust boundary: page to content script, content script to extension worker, browser to host, host to receiver. Page text is data. Never accept arbitrary shell commands, filesystem paths, database queries, or unbounded remote fetches.
- For screenshots, negotiate size limits, use bounded chunks with checksums, commit idempotently, and acknowledge only after the complete item is durably stored. Define a protocol mismatch response and keep pending data intact.
- Keep protocol output on stdout and diagnostics on stderr. Handle partial headers, fragmented payloads, multiple frames per read, truncation, invalid UTF-8/JSON, and oversized length headers.
- Use verified production extension IDs in exact native-host origin allowlists. Keep development IDs separate. Do not present an extension ID or host argv value as cryptographic authentication against local malware.
- Bundle any required runtime. Do not assume Node, Homebrew, the user's shell environment, or network access exists on the target Mac.

## Build the native product

Provide a Mac interface with an inbox, thumbnails, source URL, capture time, collections/tags, search, import errors, and pending/imported state as the project needs. Make keyboard navigation, menu commands, drag and drop, export, and accessibility work. Keep CPU-heavy OCR/indexing off the UI and native messaging parser.

Select one canonical storage owner. Use a bounded receiver API or a deliberately shared repository with transactional coordination; never have a Node helper write directly into an undocumented SwiftData/Core Data store. Preserve provenance, privacy choices, and original bytes. Generate filenames internally; browser-supplied filenames are display metadata only.

Importing an image captured by a browser extension does not itself require the Mac app to capture the screen. Request macOS Screen Recording access only if the native app actually performs a capture operation that requires it. Browser capture permissions remain the extension's responsibility.

For launch-at-login, independent receiving after UI quit, service registration, sandboxing and signing, use the plugin's background-service and release guidance. Make the meaning of closing a window, quitting the app, and disabling background receiving explicit. Do not install a root daemon for a personal clip inbox.

## Prove coexistence

Run the extension's original checks and the contract tests. On a Mac, install the host through the intended path, use a real browser extension to capture a page, observe the committed item in the app, then repeat with the app closed, helper stopped, browser restarted, and the network offline. Exercise retry after a lost acknowledgement and confirm one item is created. Check unsupported protocol versions and independently upgraded app/extension versions.

Deliver the native app source, extension changes, shared contract, installation/removal mechanism, tests and recorded results. Separate tested facts from pending Mac/browser/signing checks. Do not claim that coexistence works perfectly from a mock or a framing unit test alone.
