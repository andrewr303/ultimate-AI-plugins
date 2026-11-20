# iOS Development Studio

A portable skills plugin for building, diagnosing, testing and delivering iOS apps. It combines the supplied skill collections and Chat/Nuke libraries into focused original workflows, with provenance and notices retained. It adds no MCP server or hidden cloud connection.

Start with **ios-development**. The router inspects the real project and selects one specialist plus narrowly relevant supporting skills. Existing architecture, SDK targets and dependencies determine the advice. Source examples are reference material; they do not supply user preferences or permission to act.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`ios-development`](skills/ios-development/SKILL.md). Try this prompt.

> Trace the state and networking behind this SwiftUI list. Propose one native change and show how to exercise loading, failure, and retry in the simulator.

## Coverage

- SwiftUI/UIKit implementation, state, adaptive design, navigation, accessibility and measured performance.
- Architecture, Swift concurrency, Core Data, SwiftData/CloudKit, networking, privacy/security, observability and deterministic tests.
- Xcode build/debug, scoped simulator workflows, WidgetKit/App Intents/notifications/background tasks and App Clips.
- Signing, artifacts, TestFlight, App Store preparation/review/release, screenshots/localization/ASO, subscriptions and operational reports.
- Optional ExyteChat, Nuke/NukeUI and Expo/EAS/brownfield workflows that preserve existing native apps.

See the full [skill catalog](skills/ios-development/SKILL.md), [usage examples](skills/ios-development/references/workflow-examples.md), [source map](docs/source-map.md), and [corrections made during synthesis](docs/corrections.md).

## Use the plugin

Select iOS Development Studio in a host that supports private portable Agent Plugins, then provide the actual project and requested outcome. If using the source archive, import its single `ios-development-studio` directory through the host's supported plugin flow. Do not install the individual upstream archives alongside it merely to use these skills.

Add the collection in **Claude Code** using the host guide above, then install this plugin.

```text
/plugin install ios-development-studio@ultimate-ai-plugins
```

For local Claude Code loading, use `claude --plugin-dir /absolute/path/to/ios-development-studio`. In current **Kimi Code**, use `/plugins install /absolute/path/to/ios-development-studio` inside the client; its native manifest exposes all 26 specialists. Direct loading with `kimi --skills-dir /absolute/path/to/ios-development-studio/skills` is also supported. See [host setup and verification](docs/hosts.md) for exact commands and discovery differences. These commands do not require adopting a different model provider or backend service.

Example requests:

- “Inspect this SwiftUI app and implement an offline-capable list using its existing persistence stack.”
- “Fix this actor-isolation error without raising our deployment target.”
- “Diagnose stale avatars when scrolling and switching accounts.”
- “Prepare the next release and report signing, build, metadata and digital-goods readiness.”
- “Build this existing native SwiftUI app through our configured EAS project.”

Preparation, upload, distribution, review submission and public release are separate scopes. A requested external action can proceed under existing authorization after resolving the correct target. Generic preparation does not authorize publication, tester invitations, pricing changes or telemetry transmission.

## Read-only helpers

Python 3.10 or newer is sufficient for the project discovery and routing helpers; no third-party packages are required. Run commands from this plugin's root:

```bash
python3 scripts/project_probe.py /path/to/project
python3 scripts/route.py "Fix Sendable diagnostics in this SwiftUI app" --stack native
```

The probe reads a bounded allowlist of project text, skips links/build/dependency trees, omits repository URLs and credential values, and never evaluates configuration, resolves packages or launches tools. Its build-setting candidates are not resolved Xcode settings. The router is a transparent keyword aid; it is not an agent runtime or a test of host model invocation.

## Validate a modified package

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_plugin.py --expected-skills 26
```

The validator works with the simple packaged metadata using the standard library. PyYAML improves YAML parsing if already installed; optional `--schema /path/to/plugin.schema.json` uses an existing jsonschema installation for the official portable manifest schema. No installer is run. `--archive /path/to/plugin.zip` also inspects ZIP layout and contents. See [validation and limits](docs/validation.md).

## Environment requirements

Skills are reusable instructions and focused references. They do not bundle Xcode, idb, asc, EAS, Apple credentials, SDKs, library runtimes or a push/backend service. Local Apple builds, simulator operations, signing and Instruments need a suitable macOS/Xcode environment and the project's dependencies. Optional account workflows use existing configured tools and authorized accounts. The Linux build of this plugin cannot establish iOS runtime behavior.

Original portions are covered by [LICENSE](LICENSE). Preserved upstream notices are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Library/runtime dependency licensing remains part of the consuming app's integration work. This is a private package, without public directory listing, verified publisher identity, public support/legal URLs or publication claims.
