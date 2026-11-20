# Apple Compliance

Prepare Apple-platform apps for policy review, submission and distribution using explicit scope, current sources and evidence. Unknown product facts remain unknown; a checklist or static scan cannot grant App Store approval.

The plugin provides **17 focused skills** and **51 original reference guides**, plus an operating contract, source catalog, pinned research, helper tools and tests. References include current primary documentation beyond GitHub, with exact source IDs/URLs and applicability checks. Full third-party documentation and upstream runtimes are not mirrored.

Start with **apple-compliance**. Select the specialist that owns the actual task, then load only its relevant references. Preserve existing frameworks, providers and SDKs. Source snapshots inform decisions; installed tools, actual artifacts and current authoritative requirements decide execution.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`apple-compliance`](skills/apple-compliance/SKILL.md). Try this prompt.

> Review this iOS app’s privacy manifest and App Store privacy answers. Give me an evidence checklist and flag any answers that need input from the app owner.

## Install and use

The complete source tree supports portable Agent Plugins/Codex, Claude Code and current Kimi Code. Keep the shared reference/library paths together.

In Claude Code, add the collection using the host guide above, then install this plugin.

```text
/plugin install apple-compliance@ultimate-ai-plugins
```

Or run `claude --plugin-dir /absolute/path/to/apple-compliance`. In current Kimi Code, run `/plugins install /absolute/path/to/apple-compliance` inside the client, then `/reload`. Direct loading with `kimi --skills-dir /absolute/path/to/apple-compliance/skills` is also available. No model provider or backend account is configured by installation.

Read [host setup](docs/hosts.md), [the reference library](references/INDEX.md), [the source index](references/source-index.md), [research decisions](research/outputs/design-decision.md) and [verification](docs/validation.md). Native host installation/discovery and model-driven behavior are different checks.

## Typical requests

- “Prepare an evidence-backed submission report for this app, with blockers and missing facts.”
- “Reconcile our actual SDK/data behavior with privacy manifests, labels, ATT and required reasons.”
- “Check which current purchase/account rules apply to our app and storefronts.”
- “Finish the authorized submission stage, or diagnose a rejection, without confusing upload and release.”

## Local tools

[readiness.py](scripts/readiness.py) evaluates an explicit evidence packet and can inspect bounded plist observations in an app/archive directory. It never contacts Apple or changes signing/submission state. It does not authenticate evidence assertions or infer legal/product declarations.

Start from [the unknown-filled packet](examples/readiness-packet.json). From the plugin root:

```bash
python3 scripts/readiness.py --evidence examples/readiness-packet.json
python3 scripts/readiness.py --evidence /path/to/owner-evidence.json --artifact /path/to/App.app
```

Exit 0 means ready only for the requested evidence profile/stage; 1 means blockers or missing evidence; 2 means invalid input. The starter packet intentionally returns 1. Artifact identity contradictions override a claimed satisfied check. Privacy manifests remain per-bundle observations rather than one combined declaration.

The package's Python helpers require Python 3.10 or newer and use the standard library for their main checks. Optional PyYAML/jsonschema improve metadata/schema validation when already installed. They are not installed automatically. Run from the plugin root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_plugin.py --expected-skills 17 --json
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_kimi.py --expected-skills 17 --json
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_references.py --json
```

These checks validate structure, scope and local examples; they do not establish factual/legal truth or an iOS app's runtime result. Xcode, devices, signing, live provider delivery and Apple account operations need the target environment. The plugin does not bundle those tools, credentials or services. Original portions use [MIT](LICENSE); helper attribution and source boundaries are in [third-party notices](THIRD_PARTY_NOTICES.md).
