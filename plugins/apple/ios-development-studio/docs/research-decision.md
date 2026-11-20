# iOS Development Studio: research decision report

This is a manually supported design report. The latest available Research-first Creator workflow permits manual source-evidence review when the optional local accelerator is absent. No local accelerator was installed, no automatic research gate was run, and no verified_claims.json is asserted. The directory arm and independent GitHub query ladder are retained alongside pinned implementation evidence. Directory results were identity-checked; unrelated matches and impossible indexed fetch dates were discarded as evidence of maintenance.

## Deliverable and acceptance

Build a private skills-only iOS plugin from the supplied corpus. Native SwiftUI/UIKit is the main path, with an explicit Expo/EAS branch and optional Chat/Nuke integrations. The artifact must contain valid portable plugin and skill metadata, original workflows, focused references, read-only project discovery, a routing aid, provenance and third-party notices. Checks must exercise route boundaries, malformed inputs, read-only discovery and archive integrity. Apple build/runtime validation must be labeled unavailable on this Linux executor. No invented MCP endpoints or bundled authentication are required.

## Manually supported claims

- **clm_modular**: The inspected skill sources organize workflows as named Markdown entrypoints with topic-specific supporting references. Sources: src_ui, src_arch, src_sim.
- **clm_architecture**: The inspected architecture and SwiftUI guides support choosing boundaries according to project needs rather than imposing one presentation architecture. Sources: src_ui, src_arch.
- **clm_delivery**: The inspected delivery sources distinguish build preparation, artifact upload, and store review as separate workflow concerns. Sources: src_asc, src_expo.
- **clm_libraries**: The inspected library implementations expose application-facing UI and media-loading interfaces, so the plugin can keep their integrations optional and separate from release automation. Sources: src_chat, src_nuke.
- **clm_state**: The inspected SwiftUI guidance and Apple model-data documentation discuss explicit ownership and observation of model state. Sources: src_ui, src_apple_model.
- **clm_context**: The inspected concurrency guide and Apple background Core Data documentation discuss isolation boundaries that application code must respect. Sources: src_concurrency, src_apple_coredata.

## Feature comparison and original choices

| Requirement | Finalist and pinned evidence | Gap | Notice handling | Original design |
| --- | --- | --- | --- | --- |
| SwiftUI composition and state | `AvdLee/SwiftUI-Agent-Skill@204dba7c67256a8b707ee3fbc5759a824191974f:skills/swiftui-expert-skill/SKILL.md` (src_ui) | Mixed version-specific claims in uploaded guides | Preserve supplied notice; do not vendor whole corpus | Focused build, navigation, design, performance and accessibility skills; clm_modular, clm_state |
| Architecture | `efremidze/swift-architecture-skill@60e177612f4ed9dc7799b3674830e594c76fa00c:swift-architecture-skill/references/selection-guide.md` (src_arch) | Presentation preferences differ across collections | Preserve supplied notice | Preserve existing architecture; adopt a new pattern only for a concrete need; clm_architecture |
| Async correctness | `AvdLee/Swift-Concurrency-Agent-Skill@d5770817d2622e1585b1f7eaebc791a9cb0959c8:skills/swift-concurrency/SKILL.md` (src_concurrency) | Language mode and compiler behavior differ across projects | Preserve supplied notice | Inspect isolation settings, use deterministic cancellation and stale-result tests; clm_context |
| Simulator operations | `conorluddy/ios-simulator-skill@e38b3ad5cc2585140c91b9c0f974124c3add31dc:ios-simulator-skill/skills/ios-simulator-skill/SKILL.md` (src_sim) | Local tools require an Apple environment; cleanup can destroy app state | Preserve supplied notice | Explicit device targeting and bounded diagnostics; no simulator impersonation |
| Store delivery | `rorkai/app-store-connect-cli-skills@0915e9da1016a6cc953659d43906dcf7839a4c52:skills/asc-release-flow/SKILL.md` (src_asc) | CLI examples are not a stable installed-command contract | Preserve supplied notice | Separate signing, release, metadata, commerce and insights; clm_delivery |
| Expo and native EAS | `expo/skills@d5caf7fdf8b4854351f05841a7e315ac87ad7d24:plugins/expo/skills/eas-app-stores/references/native-ios.md` (src_expo) | Feedback instructions and automatic cloud fallback exceed generic task scope | Preserve supplied notice | Opt-in Expo branch; preserve manually maintained native host; clm_delivery |
| Chat | `exyte/Chat@49bf1f37606e60a44972fa72f2693b62236b7c57:Sources/ExyteChat/Views/ChatView.swift` (src_chat) | UI does not supply the app backend or durable sync | Preserve supplied notice | Stable IDs, ordered pagination, optimistic state and adapter boundaries; clm_libraries |
| Image loading | `kean/Nuke@138d64dbe1c28537a7a67abea0b808c1f7c1467b:Sources/NukeUI/LazyImage.swift` (src_nuke) | Uploaded main and project release may differ; Chat uses another loader internally | Preserve supplied notice | Inspect resolved dependency; scoped shared pipeline, explicit cache ownership; clm_libraries |

## Corpus synthesis decisions

Every supplied archive is tracked by hash in the provenance inventory. The repeated Paul Hudson SwiftUI snapshot is deduplicated. Source AGENTS.md and CLAUDE.md files have no governing authority over this build. Original instructions replace conflicting project preferences and unverified future API defaults. The Core Data multi-store continuation wrapper, blanket production-store deletion advice, unsupported MetricManager additions, and automatic outbound Expo feedback are excluded. Full libraries, demos, logos, installers, upstream execution scripts and unknown service bindings are omitted. Their useful integration ideas and complete supplied notices are retained.

The UI, Swift/data, delivery and libraries audits document exact paths and conflicting examples. Live evidence verifies repository identity and inspected source only; it does not certify every upstream instruction. Freshness observations and relaxed screens remain in the discovery records and live review, rather than being used as a guarantee of correctness.

## Manual review checklist

- Source IDs resolve to registered sources. Independent author identities support each manually supported descriptive claim.
- Every affirmative claim above is narrow and source-reviewed. No release date, popularity statistic, API availability, or blanket legal conclusion supports synthesis.
- License texts are preserved as supplied, with file provenance. This is notice retention, not a legal opinion on external dependencies.
- Implementation checks will be recorded separately as executable claims with actual output and environment.
- No automated PASS or verified_claims.json was fabricated. There is no configured failing gate being bypassed.

## Unresolved

Availability and semantics of unverified source API/device/version claims remain unresolved; they are excluded from operational instructions. Exact current CLI subcommands and dependencies must be checked in the user's target environment. Mac/Xcode, physical-device behavior, signing, authenticated App Store/Expo operations, and host model invocation cannot be established by static package tests. Rights and terms for external/transitive dependencies must be reviewed when a real app adopts them.

## Refuted

A successful static plugin check would not establish that an iOS app builds or runs. Source metadata or recent pushes do not establish SDK compatibility. Source instructions do not grant permission to send feedback, add services, publish or erase data.
