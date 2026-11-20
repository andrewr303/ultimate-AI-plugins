---
name: node-to-mac
description: "Use when adapting an existing Node.js, JavaScript, TypeScript, web, CLI, or server project into a macOS app while preserving its original entry points and behavior."
---

# Adapt Node or web software into a Mac app

Implement the requested app, including build wiring and a working end-to-end feature. Do not stop at a wrapper recommendation. Start with [architecture and adaptation](references/adaptation.md); load [runtime and IPC](references/runtime-ipc.md) for a sidecar, Electron, or Tauri integration.

## Establish the existing contract

Read repository instructions, package manifests and lockfiles, scripts, entry points, persisted-data formats, and native dependencies. Run the existing appropriate checks and capture baseline behavior before refactoring. Identify browser APIs, DOM assumptions, server routes, CLI output, credentials, and filesystem/network permissions. Never claim browser extension APIs exist in a desktop webview.

Preserve the original build/run/test commands, public APIs, extension identity, deployment target, and user data. Prefer an additive `apps/macos/` target with a shared library/package and platform adapters. Make backwards-compatible changes to a shared module before replacing original code. Build a feature parity matrix with columns for original behavior, Mac equivalent, shared implementation, and verification.

## Choose and implement the boundary

- For a native interface, prefer SwiftUI/AppKit and reuse Node business logic in a bundled, narrowly scoped sidecar where rewriting it would add unnecessary risk. This gives native controls while keeping proven logic.
- For substantial web UI reuse, compare Electron and Tauri against actual dependencies, Chromium compatibility, native modules, footprint, and maintenance. Call the result a desktop app with web UI unless its interface is implemented with native controls. Tauri does not include Node; Electron does.
- For a server/CLI utility, implement a native menu bar or settings interface plus a service when useful. Do not create an empty window solely to make a `.app`.

Record the choice briefly, then build the smallest real vertical slice through UI, reused logic, persistence, and an error state. Use the `native-mac-app` skill for native UX, `background-services` for execution beyond UI lifetime, `browser-companion` for coexistence with an extension, and `mac-release` for signed packaging. If those skills are unavailable, proceed using the repository and official platform documentation.

## Package for a normal Mac

Bundle a supported runtime and production dependencies or a compatible single executable. A user's Mac must not need Homebrew, an interactive shell, Xcode, npm, a repository checkout, or `/usr/local/bin/node`. Resolve resources relative to the bundle, writable data through platform directories, and native modules for each architecture and runtime ABI. Do not write mutable state into the signed bundle.

Use explicit typed/versioned operations at each process boundary, bounded input, timeouts, cancellation, graceful shutdown, crash recovery, and visible errors. Never expose an unrestricted shell, arbitrary filesystem writes, raw Electron IPC, or Tauri shell execution to page content. Development servers and broad development permissions must not ship.

## Prove coexistence and installation

Run the original project's checks after changes. On macOS, launch the packaged app from Finder with a clean shell environment and verify one real operation, stored results, relaunch, missing dependency handling, and sidecar crash recovery. Test arm64 and any supported x86_64 build and minimum/latest supported macOS. Verify both original and Mac app can run simultaneously without port, database, file lock, or credential conflicts. Define intentional single-instance behavior separately for each product.

Deliver source changes, reproducible build commands, the parity matrix, and evidence of checks performed. If working on Linux, finish platform-independent code and tests, add a concrete macOS CI or local verification path, and label Xcode compilation, Finder launch, TCC, signing, and Gatekeeper checks as unrun until observed on a Mac.
