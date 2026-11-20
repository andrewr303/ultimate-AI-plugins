# iOS Backend Studio

Connect a native iOS app to an online Node.js platform with one explicit wire contract, shared lifecycle/data boundaries and reproducible tooling. The default design is provider-neutral and preserves an existing app/service stack.

The plugin provides **21 focused skills** and **63 original reference guides**, plus an operating contract, source catalog, pinned research, helper tools and tests. References include current primary documentation beyond GitHub, with exact source IDs/URLs and applicability checks. Full third-party documentation and upstream runtimes are not mirrored.

Start with **ios-backend-studio**. Select the specialist that owns the actual task, then load only its relevant references. Preserve existing frameworks, providers and SDKs. Source snapshots inform decisions; installed tools, actual artifacts and current authoritative requirements decide execution.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`ios-backend-studio`](skills/ios-backend-studio/SKILL.md). Try this prompt.

> Trace this iOS sign-in flow through the Node.js API. Map token refresh, expired sessions, and error responses, then propose a contract test for each gap.

## Install and use

The complete source tree supports portable Agent Plugins/Codex, Claude Code and current Kimi Code. Keep the shared reference/library paths together.

In Claude Code, add the collection using the host guide above, then install this plugin.

```text
/plugin install ios-backend-studio@ultimate-ai-plugins
```

Or run `claude --plugin-dir /absolute/path/to/ios-backend-studio`. In current Kimi Code, run `/plugins install /absolute/path/to/ios-backend-studio` inside the client, then `/reload`. Direct loading with `kimi --skills-dir /absolute/path/to/ios-backend-studio/skills` is also available. No model provider or backend account is configured by installation.

Read [host setup](docs/hosts.md), [the reference library](references/INDEX.md), [the source index](references/source-index.md), [research decisions](research/outputs/design-decision.md) and [verification](docs/validation.md). Native host installation/discovery and model-driven behavior are different checks.

## Typical requests

- “Inspect our Swift app and Node service, then centralize the API contract and compatibility checks.”
- “Connect widgets and Siri actions to our backend with account-safe shared state.”
- “Design APNs and Live Activity updates that survive token rotation and offline clients.”
- “Make Xcode/SwiftPM, web-client and server checks run from one documented development workflow.”

## Local tools

A small [Node contract kit](examples/node-contract-kit/README.md) demonstrates real HTTP wire behavior and focused tests without external dependencies. Its in-memory store and injected authentication are explicit teaching seams, not production durability or an auth service. The accompanying Swift wire fragment is source-reviewed but uncompiled here.

Run the kit with `node --test examples/node-contract-kit/test/server.test.mjs`; inspect its README before adapting it. Nothing starts automatically when the plugin loads.

The package's Python helpers require Python 3.10 or newer and use the standard library for their main checks. Optional PyYAML/jsonschema improve metadata/schema validation when already installed. They are not installed automatically. Run from the plugin root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_plugin.py --expected-skills 21 --json
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_kimi.py --expected-skills 21 --json
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_references.py --json
```

These checks validate structure, scope and local examples; they do not establish factual/legal truth or an iOS app's runtime result. Xcode, devices, signing, live provider delivery and Apple account operations need the target environment. The plugin does not bundle those tools, credentials or services. Original portions use [MIT](LICENSE); helper attribution and source boundaries are in [third-party notices](THIRD_PARTY_NOTICES.md).
