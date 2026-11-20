# mac-developer

A research-backed coding agent plugin for building macOS Golden Gate and recent
macOS apps, adapting existing software, and keeping companion products compatible.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`mac-developer`](skills/mac-developer/SKILL.md). Try this prompt.

> Plan a native macOS menu bar companion for this Node.js service. Identify the lifecycle, signing, and permissions the first working version needs.

Install:

```sh
/plugin install mac-developer@ultimate-ai-plugins
```

Start with `mac-developer` for end-to-end work, or invoke a focused workflow:

| Skill | Purpose |
| --- | --- |
| mac-developer | Inspect, choose architecture, implement, verify |
| native-mac-app | SwiftUI/AppKit apps and platform integration |
| node-to-mac | Node.js, web and CLI adaptation; native shell, Electron or Tauri |
| background-services | Login items, helpers, agents, XPC and lifecycle |
| browser-companion | Chrome/Safari bridge and durable screenshot transfer |
| mac-research-and-debug | Current official research, project inspection and diagnosis |
| mac-release | Signing, entitlements, packaging, notarization and distribution |

Example requests:

- Build a SwiftUI menu bar app that indexes a folder and pauses background work.
- Turn this Node.js app into a Mac app, keeping its CLI and web frontend working.
- Add a Mac companion to my Chrome web clipper. Keep Chrome capture working when
  the app is absent; queue screenshots and organize them after reconnecting.
- Diagnose why my helper works in Terminal but fails in the signed installed app.

The package contains skills, source references, templates and small supporting
utilities. It uses the coding agent's existing tools and does not deploy a server,
ship a running service, grant device permissions or connect an Apple account.
It is not an automatic guarantee that any extension can be converted unchanged.

On a Mac, the agent can use the available local Xcode toolchain. On other systems,
it can write code, inspect projects and run portable tests; actual macOS builds,
permissions, helper lifecycle, signing, Gatekeeper and installation must be
verified on a Mac. Distribution credentials remain in your normal secure tools.

Research was checked on 2026-11-03 against primary documentation. Each workflow
requires rechecking volatile APIs and policies for the project's selected versions.
Golden Gate is macOS 27; the chosen minimum OS is an explicit project decision.

The plugin preserves existing entrypoints, browser identity and data unless a
requested change requires migration. Reliability is demonstrated with old/new
version, offline, crash, duplicate-delivery and installed-artifact tests.

No third-party runtime dependencies or remote MCP server are bundled.

Version 1.0.1. The downloadable package under `artifacts/mac-developer` holds 1.0.0 and is not rebuilt from this source.
