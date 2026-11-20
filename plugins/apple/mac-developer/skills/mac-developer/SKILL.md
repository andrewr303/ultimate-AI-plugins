---
name: mac-developer
description: "Use for end-to-end macOS development: new native apps, adapting Node.js/web/CLI projects, background services, or Mac companions for Chrome/Safari extensions while preserving the original product. Route to focused bundled workflows and implement and verify the requested result."
---

# mac-developer

Act as an implementation partner. Research, inspect, implement, build, exercise,
and report evidence. A plan alone does not complete a coding request. This package
supplies coding instructions and utilities, not a remote Mac or an app converter.
Use the host agent's actual tools; do not invent MCP tools or claim access to a Mac.

## Start from evidence

1. Read repository instructions and inspect current changes. Protect user edits.
   Use [mac-research-and-debug](../mac-research-and-debug/SKILL.md) for an unknown
   project, a platform question, or a failure. Its inspection script never executes
   repository code. Establish original run/build/test commands before changing them.
2. Identify the product outcome, current stack, target OS minimum, hardware, native
   integrations, background lifetime, storage/privacy, and distribution route.
   Infer routine choices and continue. Ask only for missing decisions that alter
   implementation substantially; do independent inspection while waiting.
3. Verify current Apple release names, SDK/API availability, framework versions,
   and selected distribution requirements against official sources. Golden Gate 27
   was verified on 2026-11-03; recheck for each task. Do not freeze a latest patch,
   infer APIs from a marketing name, or silently change a repository's minimum OS.
4. Write a short architecture decision in the target repository when multiple
   processes or products are involved. Use [the template](references/project-brief.md).
   Specify data ownership, trust boundaries, compatibility, and lifecycle.

## Load only the relevant workflows

| Requested outcome | Bundled workflow |
| --- | --- |
| SwiftUI/AppKit desktop app, menu bar app, document app, native integration | [native-mac-app](../native-mac-app/SKILL.md) |
| Existing Node.js, website, SPA, CLI, server, Electron, or Tauri project | [node-to-mac](../node-to-mac/SKILL.md) |
| Login item, helper, agent, background worker, scheduled processing, XPC | [background-services](../background-services/SKILL.md) |
| Chrome/Safari extension companion, native messaging, screenshot receiver | [browser-companion](../browser-companion/SKILL.md) |
| Build failures, research, capability detection, performance, crash or permission issue | [mac-research-and-debug](../mac-research-and-debug/SKILL.md) |
| Signing, entitlements, notarization, installer, updates, Mac App Store or release | [mac-release](../mac-release/SKILL.md) |

## Architecture choices

- Prefer SwiftUI with AppKit bridges for a new native macOS UI. Use established
  project conventions. Deliver native menus, shortcuts, window behavior,
  accessibility, error recovery, and persistent data, not only a web view.
- For existing JavaScript, compare a native frontend + bundled worker, Electron,
  and Tauri against reuse, footprint, capabilities, and distribution constraints.
  Be explicit about which UI is native and which is web-rendered.
- Preserve browser capture in the extension and organization in the companion.
  Keep the extension useful when the app is absent, disabled, or older. Share
  domain types and protocol contracts; keep platform APIs behind adapters.
- A windowless app, a login item, and an independent service have different
  lifetimes. Choose the least powerful mechanism that meets the user outcome.
  User-visible controls govern start at login, background work, pause, and quit.
- Prefer local private storage unless sync is requested. Use Keychain for secrets,
  narrow entitlements, authenticated IPC, bounded payloads, and stable identifiers.
  Do not introduce telemetry, a cloud backend, root privilege, or broad access
  solely to simplify implementation.

## Implement and prove

Keep original entrypoints and add adapters/new targets incrementally. Record any
unavoidable behavior changes and supply a migration/rollback path. Schema changes
must tolerate concurrent old/new versions or block them safely with a clear error.

Implement a working vertical slice before broad UI polish. For the screenshot
example: capture in Chrome → durable extension outbox → validated native bridge →
transactional app inbox → collection view → search/tag/export. Acknowledge receipt
only after durable commit; retry with the same idempotency key.

Use [acceptance cases](references/acceptance.md) to choose meaningful verification.
Run original tests and builds after shared-code changes. On a Mac, build selected
schemes and exercise real permissions, installation, startup, service shutdown,
and browser delivery. On Linux, perform portable checks and prepare exact Mac
commands; mark those checks unrun. Signing or notarization is not implied by a
successful unsigned development build.

Finish with changed behavior, evidence, remaining limitations, and runnable next
steps. Never promise perfect coexistence or platform support without testing the
specified OS, browser, architecture, and installed release artifact.
