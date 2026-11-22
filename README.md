# Ultimate AI Plugins

![Ultimate AI Plugins catalog banner](docs/assets/catalog-banner.jpg)

Give coding agents a workflow to follow. The catalog includes 21 plugins for
writing documentation, planning delivery, reviewing code and sites, building
Apple apps, and producing launch materials. Each plugin README names the
starting skill, a first prompt, and any tools it needs.

[Doc Atlas starter](docs/starter.md) · [Worked example](#see-doc-atlas-in-action) · [Install](#install) · [Plugin catalog](#plugin-catalog) · [Host verification](docs/verification.md) · [Credits](docs/credits.md)

## See Doc Atlas in action

Try this request.

> Audit TinyRoute’s README. Check each instruction against the CLI source and
> verify the corrected command.

A controlled trial applied the Doc Atlas instructions to this synthetic Python
CLI. The workflow inspected the parser, project metadata and tests. It removed
an unimplemented `--fast` flag, a speed claim, an unsupported MIT badge and a
link to a missing manual.

Run the corrected command from the [fixture directory](plugins/documentation/doc-atlas/evals/fixtures/tinyroute/README.md).

```sh
PYTHONPATH=src python3 -m tinyroute --name Ada
```

```text
Hello, Ada!
```

All three fixture tests passed, and the final local Markdown check reported zero
findings. Source inspection caught the false claims. The Markdown checker
caught the broken link. [Trial record](plugins/documentation/doc-atlas/evals/workflow-trial.md) · [Recorded commands and before/after README](plugins/documentation/doc-atlas/evals/workflow-trial.json)

## Install

Use the [versioned Doc Atlas starter](docs/starter.md) to try the worked example.
Clone the full collection to browse or install other plugins.

```sh
git clone https://github.com/andrewr303/ultimate-AI-plugins.git
cd ultimate-AI-plugins
```

| Host | Start with Doc Atlas |
| --- | --- |
| Codex CLI | Run `codex plugin marketplace add "$PWD"`, then `codex plugin add doc-atlas@ultimate-ai-plugins`. Open a new session. |
| Claude Code | Run `claude --plugin-dir ./plugins/documentation/doc-atlas` to load Doc Atlas in the current session. |
| Kimi Code | In an interactive session, use `/plugins install` followed by the absolute Doc Atlas directory, then `/reload`. |
| ChatGPT desktop | Open the checkout as a project. In the Plugins Directory, choose **Ultimate AI Plugins**, then **Doc Atlas**. |
| Other Agent Skills hosts | Register a project skill with `python3 scripts/plugin_catalog.py register-skill doc-atlas --project /path/to/project`. Use the generated skill file directly if the host does not discover it. |

Open a session on the project you want to document and ask for `repo-docs`.
For the generated project skill, ask for `ucp-doc-atlas`. The
[host guide](docs/hosts.md) explains discovery, compatibility, and setup.

## Plugin catalog

Each plugin page includes a first prompt, the entry skill, and package-specific setup.

[Engineering](#engineering-and-delivery) · [Writing and docs](#documentation-and-writing) · [Apple](#apple-platforms) · [Design](#ui-and-design-systems) · [Motion](#motion-and-interaction) · [Quality](#security-accessibility-and-performance) · [Growth](#product-marketing-and-growth) · [Creative](#image-and-video-direction)

### Engineering and delivery

| Plugin | Start with | What it does |
| --- | --- | --- |
| [Ultimate SDD](plugins/engineering/ultimate-sdd/README.md) | `orchestrator` | Turns a project brief into a PRD, requirements, scoped tasks, and verification evidence under the target project’s `docs/plan/`. Its Python tools validate the artifact graph, govern lifecycle transitions, and support checkpoints and read-only rollback previews. Independent review steps require a separate reviewer. |
| [Issue Assistant](plugins/engineering/issue-assistant/README.md) | `issue-assistant` | Reconciles GitHub or Linear issues with code, PRs, and acceptance evidence. Preview a backlog review, investigate a named issue, or break it down into verifiable subtasks. Live tracker reads and writes require suitable connections and authorization. |

### Documentation and writing

| Plugin | Start with | What it does |
| --- | --- | --- |
| [Doc Atlas](plugins/documentation/doc-atlas/README.md) | `repo-docs` | Builds and audits READMEs, guides, documentation sites, API references, and diagrams using repository evidence. Includes read-only inventory and Markdown preflight helpers. A site’s build and rendering checks use its own stack. |

### Apple platforms

| Plugin | Start with | What it does |
| --- | --- | --- |
| [Apple Compliance](plugins/apple/apple-compliance/README.md) | `apple-compliance` | Prepares evidence for App Store review and distribution, including privacy manifests and labels, signing and entitlements, TestFlight, store assets, and rejection follow-up. Use it to identify what your app still needs to verify before submission. |
| [iOS Backend Studio](plugins/apple/ios-backend-studio/README.md) | `ios-backend-studio` | Plans and verifies services behind iOS apps. Covers provider selection, auth, data and sync, webhooks, notifications, environments, observability, and rollout. Use its provider-specific guidance with the credentials and tools available in your host. |
| [iOS Development Studio](plugins/apple/ios-development-studio/README.md) | `ios-development` | Covers native iOS architecture, SwiftUI, UIKit, persistence, networking, concurrency, test evidence, App Store work, and selected React Native or Expo workflows. Local builds and simulator runs depend on the project’s Apple toolchain. |
| [Mac Developer](plugins/apple/mac-developer/README.md) | `mac-developer` | Plans and builds native Mac apps, adapts Node.js projects, and covers background services, browser companions, debugging, and distribution. It directs work through the existing product’s architecture and release constraints. |

### UI and design systems

| Plugin | Start with | What it does |
| --- | --- | --- |
| [Design Variations](plugins/design/design-variations/README.md) | `design-variations` | Explores directions in interactive rounds, usually ten variations per round, then iterates on selected options. Uses available design-reference tools and maintains a comparison record. Live canvas and browser evidence depend on the host. |
| [UI Component Expert](plugins/design/ui-component-expert/README.md) | `ui-component-expert` | Turns a manually downloaded Claude Design export into a typed design contract and a reviewed implementation worklist for React and TypeScript. It compares native HTML and headless primitives, quarantines raw exports, and requires separately observed browser evidence before claiming visual verification. Experimental. |

### Motion and interaction

| Plugin | Start with | What it does |
| --- | --- | --- |
| [Liquid Glass Studio](plugins/motion/liquid-glass-studio/README.md) | `liquid-glass-studio` | Designs and reviews glass interfaces from optics and rim lighting through motion, contrast, native APIs, and performance. Includes a reference engine and a lab for inspecting effects and fallbacks. |

### Security, accessibility and performance

| Plugin | Start with | What it does |
| --- | --- | --- |
| [DeepSec Agent](plugins/quality/deepsec-agent/README.md) | `deepsec-review` | Runs local defensive source review with a Node.js CLI, rules, baselines, and JSON, Markdown, or SARIF output. Bind its local MCP server to an authorized checkout before starting it. Findings are evidence for source review and remediation. |
| [Security Audit](plugins/quality/security-audit/README.md) | `security-audit` | Plans source and dependency audits, triages scanner results, compares reports against a baseline, and prepares remediation findings. Scanners are optional external dependencies. Inspect the plan and coverage before drawing conclusions. |
| [Ult Accessability](plugins/quality/ult-accessability/README.md) | `ult-accessability` | Routes WCAG 2.2 AA or AAA audit, contrast, testing, and remediation work. Combines automated results with manual interaction evidence when a live page is available. The spelling is the package ID used by installers. |
| [Ult Performance](plugins/quality/ult-performance/README.md) | `ult-performance` | Investigates loading, interaction, media, scroll, and Core Web Vitals. Includes DevTools snippets for lab measurement and guidance for distinguishing those results from field data. A live browser is needed for traces. |

### Product, marketing and growth

| Plugin | Start with | What it does |
| --- | --- | --- |
| [Creator Intelligence](plugins/product-and-growth/creator-intelligence/README.md) | `creator-research` | Discovers and vets creators using public content and public business contact data. Includes transparent scoring, comment and transcript analysis, competitor research, trend discovery, and optional ScrapeCreators workflows. |
| [Freelance Legend](plugins/product-and-growth/freelance-legend/README.md) | `freelance-legend` | Evaluates freelance leads, develops scoped proposals, and guides client communication and delivery. It uses a local freelancer profile and ships fictional examples. |
| [Marketing Page Studio](plugins/product-and-growth/marketing-page-studio/README.md) | `marketing-page-studio` | Builds marketing sites around product evidence, an audience and conversion story, and interactive demonstrations. Includes composition and scroll workflows plus steps for checking claims and browser behavior. |
| [Product Demo Studio](plugins/product-and-growth/product-demo-studio/README.md) | `product-demo-studio` | Produces product-demo scripts, storyboards, footage plans, captions, and social variants. Its Python tooling supports render and delivery receipts. Real capture and render work uses a browser and media tools such as FFmpeg. |
| [SEO GEO God](plugins/product-and-growth/seo-geo-god/README.md) | `seo-geo-god` | Audits and changes site implementation for crawlability, rendered metadata, canonical URLs, structured data, sitemaps, international targeting, and AI-crawler access. Its Python CLI supports offline checks and CI gates. |

### Image and video direction

| Plugin | Start with | What it does |
| --- | --- | --- |
| [Image Prompt Director](plugins/creative/image-prompt-director/README.md) | `image-prompts` | Writes five image prompts by default, with direction for composition, lighting, materials, exact text, and reference fidelity. Supports targeted edits and consistent series. Generate images in the chosen image model. |
| [Video Prompt Director](plugins/creative/video-prompt-director/README.md) | `video-prompts` | Writes five video concepts by default, with timed action, shots, camera direction, continuity, sound, and reference roles. Supports keyframes, loops, edits, and longer sequences. Render and assemble the clips in your chosen tools. |

## Companion tools

[Session Control Chrome](companion-tools/session-control-chrome/README.md) packages a Chrome extension and local bridge for working with agent sessions and browser profiles. Follow its own installation guide and use its [release ZIP](artifacts/session-control-chrome/session-control-chrome-0.5.0.zip) when you need the original download.

## Maintaining the collection

- [`plugins/`](plugins) contains editable source under eight categories. Plugin names are stable marketplace identifiers. Each package carries a portable manifest and the host manifests for its supported native entry points.
- [`artifacts/`](artifacts/README.md) holds original distributable ZIP and skill releases, including versions older than the editable sources. `dist/` holds retained legacy Claude upload packages.
- Catalog entries are generated from plugin folders and manifests. After changing a package or moving it, run `python3 scripts/plugin_catalog.py sync` and `python3 scripts/plugin_catalog.py check`. Verify changes with the affected plugin’s own checks as well.

To build a Claude upload archive for Doc Atlas, run `python3 scripts/pack_plugin.py plugins/documentation/doc-atlas /tmp` from the repository root. The packer checks manifest placement, archive paths, and shell script handling. Verify the runtime on the intended host separately.

See the [repository license](LICENSE) and the license or notices shipped with each plugin and its bundled assets. The [distribution review](docs/distribution.md) records packages withdrawn while rights are reviewed. The [credits](docs/credits.md) record the original collection’s upstream sources.
