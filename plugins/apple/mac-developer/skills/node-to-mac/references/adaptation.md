# Architecture and additive adaptation

Research checked: 2026-11-03. Framework versions, supported OS floors, and packaging APIs change: inspect the installed major, lockfile, release notes, and matching official documentation before adding dependencies. These are implementation decision criteria, not a guarantee that every existing program can be wrapped unchanged.

## Compare the actual product

| Approach | Reuses | Fits | Main cost |
| --- | --- | --- | --- |
| SwiftUI/AppKit plus shared Node sidecar | Domain logic, parsers, data model, integrations | Native Mac workflow and long-lived existing Node logic | Typed IPC, bundled runtime, native UI implementation |
| SwiftUI/AppKit plus ported Swift core | Algorithms and fixtures, reimplemented | Small core, close platform integration, few JS dependencies | Porting and equivalence checks |
| Electron | Web UI and Node modules; Chromium rendering | Chromium-specific UI or extensive Node integration | Larger runtime, renderer/main trust boundary, security update cadence |
| Tauri with Rust/Swift adapter and optional Node sidecar | Web UI; Node only if separately bundled | System webview compatibility and controlled native bridge | WebKit differences, explicit capabilities, extra runtime if Node required |
| Menu bar app plus registered agent | Service/CLI behavior and optional settings UI | Background utility or capture receiver | Login lifecycle, user control, durable queue and diagnostics |

Choose based on user outcomes and source evidence. A framework window does not translate HTML into AppKit controls. WebKit and Chromium differ; run the real rendering and capture path rather than assuming browser parity. A CLI/server dependency that starts itself at import should be split into a reusable library and thin original executable without breaking the existing executable contract.

## Suggested additive layout

```text
apps/original/           # Preserve existing form; adapt layout to current repo
apps/macos/             # SwiftUI, Electron, or Tauri target
packages/core/          # Platform-independent logic
packages/contracts/     # Shared schemas, protocol fixtures and compatibility tests
platform/node/          # FS/network/runtime adapters
platform/browser/       # Browser adapters; keep extension permissions narrow
```

Do not impose this layout on a working monorepo. Keep its conventions and make the fewest necessary moves. Factor platform side effects out of imports, inject storage/network/clock/capture dependencies, and retain stable identifiers for documents and synchronization events. Use an existing testable API instead of adding IPC when one already supplies the needed boundary securely.

## Migration contract

1. Capture the original artifact and behavior baseline: scripts, response shape, CLI stdout/stderr/exit codes, extension package and ID, permissions, persisted schema, and representative fixtures.
2. Separate shared core from its original host. Run the original checks before implementing the Mac adapter.
3. Build a Mac vertical slice with the same fixture and compare semantic output. Document necessary platform differences rather than hiding them behind a passing UI smoke test.
4. Keep databases backward compatible while mixed versions are supported. Assign a single writer or choose a tested transaction/concurrency design; never let independent products silently migrate one database in incompatible ways.
5. Add independently runnable build targets. Keep the original form useful when the app is absent or disabled. Provide explicit connect/disconnect and data export behavior when products share a service.

App-specific design suggestions above are engineering synthesis. Framework behavior is grounded in these official sources:

- [Electron security](https://www.electronjs.org/docs/latest/tutorial/security): security crosses Chromium, Node, dependencies, main/preload/renderers; keep privileged APIs away from untrusted content.
- [Electron process sandboxing](https://www.electronjs.org/docs/latest/tutorial/sandbox): renderer Node integration defeats the process sandbox; isolation and sandboxing solve separate parts of the boundary.
- [Tauri architecture](https://v2.tauri.app/concept/architecture/): inspect the framework's process model and system webview assumptions for the selected version.
- [Tauri external binaries](https://v2.tauri.app/develop/sidecar/): Node functionality can be shipped as an executable sidecar rather than assumed to exist on the host.
