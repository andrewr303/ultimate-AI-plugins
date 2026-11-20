---
name: ios-development
description: Use for end-to-end iOS app work, an unfamiliar SwiftUI/UIKit project, or deciding which iOS specialist applies. Inspect the actual stack and constraints, then route to focused skills. Do not activate for Android, generic web apps, image generation, or an unrelated use of the word Apple.
---

# iOS development

Read [the operating contract](references/operating-contract.md). Build, diagnose or review the user's requested outcome; discovery is a means to that result.

## Establish the project contract

1. Identify the requested behavior and observable completion criteria. Read relevant project instructions and changes. For a new app, choose a small native implementation unless the user selected another stack; name assumptions that affect the artifact.
2. Inspect the real project and tools. From the plugin root, use `python3 scripts/project_probe.py /path/to/project` for bounded static evidence. Then inspect actual manifests, selected scheme/configuration, resolved settings and diagnostics. The probe never builds or evaluates config and cannot replace those checks.
3. Classify native SwiftUI/UIKit, Expo/React Native, mixed/brownfield, or still unknown. Preserve native hosting and existing dependency versions. A Node tooling wrapper or EAS app configuration does not imply an Expo app.
4. Choose one primary skill below. Add a supporting skill only for a distinct concern. Read its entrypoint and relevant references. Do not load the entire collection into context.
5. Implement the smallest coherent change, verify acceptance behavior, and finish authorized work. If a prerequisite is missing, complete independent work and state the exact remaining dependency.

## Route by the actual problem

| Concern | Skill |
| --- | --- |
| Feature/module boundaries, existing MVVM/MVI/TCA/VIPER/MVP/Coordinator/Combine architecture | [ios-architecture](../ios-architecture/SKILL.md) |
| Sendable, actors, tasks, async streams, cancellation, concurrency migration | [ios-concurrency](../ios-concurrency/SKILL.md) |
| Native screens, state and UIKit interoperability | [ios-swiftui](../ios-swiftui/SKILL.md) |
| Adaptive UI, typography, theme, localization, requested Glass | [ios-design](../ios-design/SKILL.md) |
| Navigation paths, sheets, deep links, restoration | [ios-navigation](../ios-navigation/SKILL.md) |
| Measured scrolling, launch, memory or rendering problems | [ios-performance](../ios-performance/SKILL.md) |
| VoiceOver, Dynamic Type, RTL, reduced motion | [ios-accessibility](../ios-accessibility/SKILL.md) |
| Existing NSManagedObject/context/history/migration stack | [ios-core-data](../ios-core-data/SKILL.md) |
| Existing ModelContainer/ModelContext/@Model/@Query stack | [ios-swiftdata](../ios-swiftdata/SKILL.md) |
| URLSession, retries, pagination, offline transport | [ios-networking](../ios-networking/SKILL.md) |
| Authentication, Keychain, permissions, privacy manifests | [ios-security](../ios-security/SKILL.md) |
| Logger, signposts, MetricKit, production crash/hang evidence | [ios-observability](../ios-observability/SKILL.md) |
| Deterministic unit/integration/UI tests | [ios-testing](../ios-testing/SKILL.md) |
| Compiler/build failure, xcresult, LLDB, archive/export | [ios-build-debug](../ios-build-debug/SKILL.md) |
| Simulator target selection, launch, UI interaction, capture | [ios-simulator](../ios-simulator/SKILL.md) |
| Widgets, App Intents, push, background tasks, App Clips | [ios-platform-services](../ios-platform-services/SKILL.md) |
| Chat UI, stable messages, drafts and backend adapters | [ios-chat](../ios-chat/SKILL.md) |
| Nuke/NukeUI, media loading/cache lifecycle | [ios-images](../ios-images/SKILL.md) |
| Provisioning, signing identities, device distribution | [ios-signing](../ios-signing/SKILL.md) |
| Upload, processing, TestFlight, review and release state | [ios-release](../ios-release/SKILL.md) |
| Screenshots, store localization, ASO, changelogs | [ios-store-metadata](../ios-store-metadata/SKILL.md) |
| IAP/subscriptions, pricing, events, RevenueCat catalog | [ios-commerce](../ios-commerce/SKILL.md) |
| App Store/beta crashes and analytical reports | [ios-store-insights](../ios-store-insights/SKILL.md) |
| Actual Expo app, native module/brownfield integration, authorized EAS lane | [ios-expo](../ios-expo/SKILL.md) |
| Scoped code review or incremental SDK/API/architecture migration | [ios-review-migrate](../ios-review-migrate/SKILL.md) |

Optional routing aid: `python3 scripts/route.py "Fix actor isolation in this SwiftUI app" --stack native`. It explains keyword matches using [routes.json](references/routes.json). It suggests skill entrypoints; it neither executes skills nor verifies model invocation.

## Resolve common forks

- Unknown persistence: inspect imports and stack configuration. Use the existing engine. Ask about new product requirements only when they change the decision; no uploaded author preference becomes the user's preference.
- Expo UI: use Expo guidance for runtime-specific work. A Swift native-module isolation error may also need concurrency. An EAS delivery wrapper must preserve the SwiftUI/UIKit host.
- “Prepare a release”: produce a readiness report and concrete plan. “Upload only”: stop at verified upload/processing as scoped. “Submit”: use the intended existing review lane, inspect remote state and avoid duplicate submission.
- No Apple environment: continue source review and available portable checks. Report exactly which Xcode/device validations remain. Use existing authorized remote infrastructure when appropriate; do not invent a passing build.
- API examples conflict: verify the resolved implementation/SDK and official docs. Keep unsupported source claims out of the app.

## Completion evidence

Return the implemented outcome or review findings, changed files, relevant test/build result and material limitations. When external state changes, include account-safe app/version/build/submission identifiers and furthest verified state. Never replace the requested artifact with only a plan or repository list.

See [source provenance](../../docs/source-map.md), [workflow examples](references/workflow-examples.md), and [validation limits](../../docs/validation.md).
