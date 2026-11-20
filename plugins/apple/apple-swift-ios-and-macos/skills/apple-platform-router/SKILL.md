---
name: apple-platform-router
description: "Entry-point router for the Apple Platforms, Swift, SwiftUI, iOS & macOS plugin (11 skills). Routes requests involving SwiftUI screen architecture, MV view refactoring, iOS 26+ Liquid Glass APIs, Swift 6.2+ strict concurrency (`Sendable`, `@MainActor`, actors), SwiftUI & Instruments runtime performance profiling, XcodeBuildMCP iOS simulator debugging, macOS Tuist menubar apps, Xcode-free SwiftPM app packaging, and App Store release notes."
argument-hint: "[task description or goal to route to the best skill(s) in Apple Platforms, Swift, SwiftUI, iOS & macOS]"
metadata:
  plugin: apple-swift-ios-and-macos
  category: router
  version: "1.3.0"
---

# Apple Platforms (Swift, SwiftUI, iOS & macOS) Router (`apple-platform-router`)

> **Plugin Router for Apple Platforms, Swift, SwiftUI, iOS & macOS** — Automatically routes your request to the 1–2 most precise skills in this plugin and executes their workflow.

## Core Routing Principles

1. **Route to the most specific skill, not a generic neighbor.** Match the exact artifact, framework, or visual style named in the user's request.
2. **Select 1–2 skills in execution order — never a pile.** Pick one primary skill when it fully covers the request (`Direct`). Add a second skill only when the task spans two distinct phases (e.g., *design system selection → micro-interaction polish*, or *architecture → verification*).
3. **Load and follow the selected `SKILL.md` files.** Once routed, read the target skill's `SKILL.md` (and any referenced files in its `references/` directory) before writing code or output.

---

## Decision Tree

```text
User Request (iOS, macOS, Swift 6.2+, SwiftUI, Xcode, Instruments, or App Store)
│
├── 1. SwiftUI Views, Architecture & iOS 26+ Liquid Glass (4 skills)?
│   ├── Building new SwiftUI screens, navigation, sheets, forms, or async state? ─→ `swiftui-ui-patterns`
│   ├── Refactoring large SwiftUI views toward small subviews & MV/Observation? ──→ `swiftui-view-refactor`
│   ├── Adopting or reviewing iOS 26+ Liquid Glass modifiers, containers & morphs? → `swiftui-liquid-glass`
│   └── Auditing SwiftUI view invalidation storms, identity churn & scroll jank? ─→ `swiftui-performance-audit`
│
├── 2. Swift Concurrency & Deep Native Profiling (2 skills)?
│   ├── Fixing Swift 6.2+ actor isolation, `Sendable`, `@MainActor` & data races? → `swift-concurrency-expert`
│   └── Profiling CPU, memory, hangs, launch time & MetricKit in Instruments? ────→ `performance-profiling`
│
├── 3. macOS App Development & Packaging (2 skills)?
│   ├── Building or reviewing a macOS `LSUIElement` menubar app with Tuist? ──────→ `macos-menubar-tuist-app`
│   └── Scaffolding, building, signing & notarizing a macOS app with SwiftPM only? → `macos-spm-app-packaging`
│
└── 4. iOS Simulator Debugging & App Store Release (2 skills)?
    ├── Building, launching, inspecting UI & capturing logs on iOS Simulator? ────→ `ios-debugger-agent`
    └── Generating user-facing App Store "What's New" notes from git history? ────→ `app-store-changelog`
```

---

## Common Situations & Recommended Skill Chains

| Situation | Recommended Skill(s) | Execution Order |
| :--- | :--- | :--- |
| Build a new SwiftUI feature with modern iOS 26 Liquid Glass styling | `swiftui-ui-patterns` → `swiftui-liquid-glass` | Structure the view/navigation hierarchy first, then apply Liquid Glass containers and modifiers |
| Clean up a massive SwiftUI view that has slow scrolling and compiler concurrency warnings | `swiftui-view-refactor` → `swift-concurrency-expert` (or `swiftui-performance-audit`) | Decompose subviews and stabilize identity, then resolve actor isolation |
| Diagnose an app hang or stutter on iOS using code review and Instruments | `swiftui-performance-audit` → `performance-profiling` | Audit SwiftUI invalidation smells first, then capture Instruments traces |
| Build, run, and visually verify an iOS change in the booted simulator | `ios-debugger-agent` | Direct — uses XcodeBuildMCP to build, launch, tap, and screenshot |
| Create a standalone macOS utility app without an `.xcodeproj` and sign it for distribution | `macos-spm-app-packaging` | Direct — SwiftPM-only bundle, codesign, and notarization pipeline |

---

## Disambiguation Rules

- **`swiftui-performance-audit` vs `performance-profiling`** — `swiftui-performance-audit` focuses specifically on SwiftUI view identity churn, `@Observable` invalidation storms, and layout thrash; `performance-profiling` covers system-wide Instruments templates (Time Profiler, Allocations, Leaks, System Trace, MetricKit).
- **`macos-menubar-tuist-app` vs `macos-spm-app-packaging`** — Use `macos-menubar-tuist-app` when using Tuist (`Project.swift`) for a macOS menubar app; use `macos-spm-app-packaging` when building and packaging a macOS `.app` directly from `Package.swift` without Xcode or Tuist.

---

## Complete Plugin Skill Directory (10 Member Skills)

### Swiftui Architecture And Liquid Glass (4 skills)

| Skill | Description |
| :--- | :--- |
| [`swiftui-ui-patterns`](../swiftui-ui-patterns/SKILL.md) | Best practices and example-driven guidance for building SwiftUI views and components, including navigation hierarchies, custom view modifiers, and responsive la... |
| [`swiftui-view-refactor`](../swiftui-view-refactor/SKILL.md) | Refactor and review SwiftUI view files with strong defaults for small dedicated subviews, MV-over-MVVM data flow, stable view trees, explicit dependency injecti... |
| [`swiftui-liquid-glass`](../swiftui-liquid-glass/SKILL.md) | Implement, review, or improve SwiftUI features using the iOS 26+ Liquid Glass API. Use when asked to adopt Liquid Glass in new SwiftUI UI, refactor an existing ... |
| [`swiftui-performance-audit`](../swiftui-performance-audit/SKILL.md) | Audit and improve SwiftUI runtime performance from code review and architecture. Use for requests to diagnose slow rendering, janky scrolling, high CPU/memory u... |

### Swift Concurrency And Profiling (2 skills)

| Skill | Description |
| :--- | :--- |
| [`swift-concurrency-expert`](../swift-concurrency-expert/SKILL.md) | Swift Concurrency review and remediation for Swift 6.2+. Use when asked to review Swift Concurrency usage, improve concurrency compliance, or fix Swift concurre... |
| [`performance-profiling`](../performance-profiling/SKILL.md) | Guide performance profiling for Apple platform apps with Instruments, Xcode diagnostics, and MetricKit. Use when investigating app hangs, stutters, high CPU, me... |

### Macos Tuist And Spm Packaging (2 skills)

| Skill | Description |
| :--- | :--- |
| [`macos-menubar-tuist-app`](../macos-menubar-tuist-app/SKILL.md) | Build, refactor, or review macOS menubar apps that use Tuist and SwiftUI. Use when creating or maintaining LSUIElement menubar utilities, defining Tuist targets... |
| [`macos-spm-app-packaging`](../macos-spm-app-packaging/SKILL.md) | Scaffold, build, and package SwiftPM-based macOS apps without an Xcode project. Use when you need a from-scratch macOS app layout, SwiftPM targets/resources, a ... |

### Ios Debugging And Release (2 skills)

| Skill | Description |
| :--- | :--- |
| [`ios-debugger-agent`](../ios-debugger-agent/SKILL.md) | Use XcodeBuildMCP to build, run, launch, and debug the current iOS project on a booted simulator. Trigger when asked to run an iOS app, interact with the simula... |
| [`app-store-changelog`](../app-store-changelog/SKILL.md) | Create user-facing App Store release notes by collecting and summarizing all user-impacting changes since the last git tag (or a specified ref). Use when asked ... |
