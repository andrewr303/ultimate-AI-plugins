# Apple Platforms, Swift, SwiftUI, iOS and macOS

Eleven skills for Apple platform engineering: Swift 6.2+ concurrency, SwiftUI patterns and refactoring, iOS 26+ Liquid Glass, Instruments profiling, iOS Simulator debugging through XcodeBuildMCP, macOS menubar apps with Tuist, Xcode-free SwiftPM packaging, and App Store release notes. Version 1.3.0.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`apple-platform-router`](skills/apple-platform-router/SKILL.md). Try this prompt.

> Review this SwiftUI screen for state ownership and navigation problems. Identify the smallest refactor and the simulator behavior I should verify.

## Install

```
/plugin install apple-swift-ios-and-macos@ultimate-ai-plugins
```

Replace `<owner>/<repo>` with the marketplace that lists this plugin. Start with the router skill, `apple-platform-router`, or name a skill directly.

## Skills

| Skill | Use it for |
| :--- | :--- |
| `swiftui-ui-patterns` | Build SwiftUI screens: navigation, sheets, forms, lists, tabs, theming, app wiring. |
| `swiftui-view-refactor` | Refactor large SwiftUI views toward small subviews and MV-over-MVVM data flow. |
| `swiftui-liquid-glass` | Adopt or review the iOS 26+ Liquid Glass API in SwiftUI. |
| `swiftui-performance-audit` | Code-first audit of SwiftUI invalidation, identity churn and scroll jank. |
| `swift-concurrency-expert` | Fix Swift 6.2+ actor isolation, Sendable and data-race diagnostics. |
| `performance-profiling` | Instruments, Xcode diagnostics and MetricKit for hangs, CPU, memory, launch and energy. |
| `macos-menubar-tuist-app` | Build and maintain macOS menubar apps with Tuist and SwiftUI. |
| `macos-spm-app-packaging` | Scaffold, package, sign and notarize a macOS app from Package.swift without Xcode. |
| `ios-debugger-agent` | Build, run and inspect an iOS app on a booted Simulator through XcodeBuildMCP. |
| `app-store-changelog` | Draft App Store release notes from git history since the last tag. |
| `apple-platform-router` | Entry point: picks the one or two best skills for a request. |

Each skill lives in `skills/<name>/SKILL.md`; detail sits in that skill's `references/` folder.

## Requirements

- `ios-debugger-agent` needs the XcodeBuildMCP server, which you install and configure yourself. This plugin does not declare or start any MCP server. Tool names in that skill were not re-verified against the current XcodeBuildMCP release on 2026-11-10.
- The macOS and iOS skills assume a Mac with Xcode or the Swift toolchain. `macos-menubar-tuist-app` assumes Tuist.
- Nothing in this plugin runs automatically. The scripts under `skills/` run only when you or the agent start them.

## Related plugins

- `plugins/ios-development-studio`: broad iOS development. This plugin is narrower and adds macOS packaging and profiling.
- `plugins/mac-developer`: macOS apps and services. Use it for background services, release and Node-to-Mac work; use this plugin for the SwiftPM and Tuist menubar workflows.
- `plugins/liquid-glass-studio`: glass interfaces on web and native. This plugin covers only the SwiftUI API.
- `plugins/apple-compliance`: App Store policy review, privacy evidence, signing, TestFlight and submission, which this plugin does not cover.
- `plugins/ios-backend-studio`: iOS and Node.js backend integration with shared contracts, which this plugin does not cover.

## Licensing

Manifests declare MIT. The upload carried no license file or copyright notice, so see [NOTICE.md](NOTICE.md) for provenance and what is unclear. Changes are in [CHANGELOG.md](CHANGELOG.md).
