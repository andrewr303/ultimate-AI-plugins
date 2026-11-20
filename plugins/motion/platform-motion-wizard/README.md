# Platform Motion Wizard

A skills-first plugin for designing, implementing, and reviewing responsive product interactions: immediate feedback, spatial continuity, restrained easing, consistent states, interruption safety, and accessible reduced motion.

The package contains a main router, focused skills, five bounded agent briefs, shared references, templates, research evidence, and an optional dependency-free interaction lab. The complete supplied `polish-platform-motion/SKILL.md` is preserved byte for byte.

Version 1.1 turns the lifecycle guidance into executable examples: an original presentation controller, a live motion policy, controllable obsolete-response delivery, and focused ownership regressions. The existing skill names and invocation paths remain available.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`platform-motion-wizard`](skills/platform-motion-wizard/SKILL.md). Try this prompt.

> Review this dialog’s opening and closing motion. Specify what should happen when someone presses Escape mid-transition or reopens it before it closes.

## Use it

Start with **platform-motion-wizard** for a broad request. Ask for a specific specialist when the task is already clear. Examples:

- “Polish this checkout's feedback and transitions. Preserve the design, implement the changes, and verify failure and reduced-motion behavior.”
- “Fix this dialog's rapid close/reopen bug and first-frame interaction.”
- “Make drag reordering feel direct without interfering with page scroll; include non-drag alternatives.”
- “Review these motion changes for focus, interruption, reduced motion, and performance. Report evidence before suggesting fixes.”
- “Tune two restrained variants in a local interaction preview, then apply the selected behavior to the actual app.”

In a host supporting skill invocation, use `$platform-motion-wizard` or the host's plugin-qualified equivalent. See [router](skills/platform-motion-wizard/SKILL.md).

## Skill map

| Skill | Purpose |
| --- | --- |
| platform-motion-wizard | Route to the smallest relevant specialist set |
| polish-platform-motion | Complete original end-to-end skill, unchanged |
| motion-audit | Diagnose friction and prioritize real flows |
| motion-spec | Define states, triggers, interruption, and acceptance |
| motion-system | Consolidate motion roles, tokens, and policies |
| motion-web | CSS, WAAPI, framework lifecycle, SSR and enhancement |
| motion-controls | Buttons, forms, tabs, accordions and list state |
| motion-overlays | Menus, dialogs, sheets, presence and focus |
| motion-navigation | Routes, history, scroll and shared identity |
| motion-gestures | Drag, swipe, reorder and cancellation |
| motion-async | Truthful loading, failure, optimism and streaming |
| motion-accessibility | Reduced motion, focus, input and state parity |
| motion-native | Version-aware native platform adapters |
| motion-performance | Measure and repair rendering/input cost |
| motion-lab | Build bounded live previews and comparisons |
| motion-research | Refresh source evidence and check APIs |
| motion-review | Verify completed interactions with honest evidence |

## Package and host support

`plugin.json` uses the Agent Plugins 1.0 portable manifest. Skills are under `skills/<name>/SKILL.md`; each has optional OpenAI display metadata. The small `.claude-plugin/plugin.json` compatibility manifest carries the same identity/version and uses Claude Code's conventional skills/agents directories.

Import the ZIP through your host's supported plugin-file workflow. This delivery does not install, publish, or save a plugin to an account. Markdown agent briefs are usable assignments; automatic agent discovery and tools depend on the host. No MCP server, account, API key, network service, hook, or background automation is bundled.

For local Claude Code preview, if the installed CLI supports `--plugin-dir`, launch it with the extracted plugin directory. Check the installed CLI help; compatibility was structurally checked, not installed in a host during authoring.

## Immediate feedback lab

Open [the interaction lab](examples/motion-lab/index.html) locally. Its [README](examples/motion-lab/README.md) explains the controls and simulated requests. It demonstrates the intended contracts and is not a reusable replacement for production accessible primitives. It makes no external requests.

Start with [executable recipes](references/executable-recipes.md) for retargeting, teardown, live preference changes, and testing an old response that really arrives. The [controller source](examples/motion-lab/motion-lifecycle.js) works in the browser and with Node's built-in test runner. It owns scalar presentation only; component semantics and authoritative request state stay with the product.

## Research and provenance

The [research snapshot](references/research-snapshot.md) highlights useful sources. The [decision report](research/outputs/research-decision-report.md), pinned inspections, source/claim ledgers, query ladder, and activity records retain the evidence.

Research prioritized actual default-branch changed-file activity in **September 21–October 21, 2026** and distinguished implementation changes from documentation, dependency, release, and sponsor edits. Older background sources are labeled. Main-branch APIs may be unreleased; all implementation skills check the target product's installed versions.

The [overhaul report](research/overhaul/outputs/research-decision-report.md) adds fresh independent GitHub and directory discovery, pinned lifecycle implementations and test-quality observations. It records current implementation candidates separately from older background sources. Both research passes use manual source review; package validation is not an automated factual gate.

No upstream library code or third-party skill text is included. References to source projects are evidence, not endorsements or dependency requirements. [NOTICE](NOTICE.md) describes the provenance and licensing limits.

The attached transcript is archived source material. Its imperative wording, including video and sound instructions, does not supersede the requested product-interaction work. Sound and haptics remain excluded unless explicitly requested.

## Validate and maintain

Development validation uses Python 3.10+ and PyYAML; see [requirements-dev.txt](requirements-dev.txt). Install development dependencies only in a chosen development environment, not as a normal plugin-use step.

```sh
python scripts/validate_plugin.py .
python -m unittest discover -s tests -v
node --test tests/test_motion_lifecycle.cjs
python scripts/package_plugin.py . --output /absolute/path/platform-motion-wizard.zip
python scripts/validate_plugin.py --archive /absolute/path/platform-motion-wizard.zip
```

The validator checks manifests, frontmatter, names, contained local references, assets, research ledger integrity, scenario fixture structure, provenance hashes, and archive safety. Node is needed only for the optional controller development tests, not plugin use. Its checks do not certify animation quality, accessibility conformance, factual truth, or host installation. See [validation notes](VALIDATION.md).
