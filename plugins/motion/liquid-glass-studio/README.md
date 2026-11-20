# Liquid Glass Studio

A coding-agent plugin for designing, building, tuning and reviewing liquid glass style interfaces: translucent controls that bend the content behind them at the rim, frost the middle, catch a rim light and fall back cleanly when the browser, platform or user setting cannot support them. It works in Claude Code, Codex and other hosts that read the Agent Plugins 1.0 layout.

The plugin is built on a close reading of five open-source glass libraries, Apple's current documentation and a survey of ten existing liquid glass agent skills. It ships an original refraction engine, a tuning lab and the checks those skills lacked: a probe that renders glass in each browser engine and measures the pixels, worst-case text contrast over the real backdrop, and tests that fail when the docs drift from the engine.

"Liquid Glass" is Apple's name for its system material. This plugin is unaffiliated with Apple and helps you build your own glass that respects each platform, the user's settings and the product's brand.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`liquid-glass-studio`](skills/liquid-glass-studio/SKILL.md). Try this prompt.

> Review the glass treatment for this floating toolbar. Compare native material and CSS frost for the target platforms, including contrast and reduced-transparency behavior.

## What an agent gets

**Eleven skills.** Start with the router, `liquid-glass-studio`, which picks the smallest set for the request.

| Skill | Use it for |
| --- | --- |
| liquid-glass-studio | Classify the request and route it; combination recipes for common jobs |
| glass-design | Where glass belongs, how much a screen can carry, regular versus clear, tint, radii, brand fit |
| glass-library-select | CSS frost, the bundled engine, a WebGL capture library or a native API, with license obligations |
| glass-web | Building the tiers in vanilla JS, React, Vue, Svelte, web components and server-rendered apps |
| glass-optics | Bezel profiles, index of refraction, strength, chromatic aberration, tearing and flat-looking glass |
| glass-lab | Live tuning in the bundled lab and exporting the chosen settings |
| glass-native | SwiftUI, UIKit and AppKit glass on the 26 SDKs with availability checks, plus Android, Flutter and React Native options |
| glass-motion | Press, stretch, morphing and merging, springs, interruption and reduced motion |
| glass-accessibility | Solid fallbacks for reduced transparency, more contrast and forced colors, measured contrast, focus and semantics |
| glass-performance | Cost per rendering tier, map caching, pixel ratio, instance budgets and measurement |
| glass-review | Evidence-based review with screenshots per tier, the cross-engine probe and a report template |

**Five agent briefs** for delegation: designer, implementer, reviewer, accessibility reviewer and performance investigator. Reviewers stay read-only. [docs/agent-briefs.md](docs/agent-briefs.md) explains when to use each and how to run them in parallel.

**Three Claude Code commands.** `/glass` carries a request through routing, implementation and verification. `/review-glass` reviews a path or URL and reports without editing. `/tune-glass` opens the tuning workflow. When command names clash with another plugin, Claude Code shows them with the plugin prefix, such as `/liquid-glass-studio:glass`.

**References** on optics, web techniques, browser support, 58 numbered gotchas, native APIs (including a list of APIs that do not exist), design principles, accessibility, performance, motion, a library decision matrix and condensed notes on each studied library. Moving facts live in [references/research-snapshot.md](references/research-snapshot.md) with source URLs and the date they were checked; skills tell agents to re-check them before relying on them.

## How the web glass works

Every surface gets three tiers, built in this order so each one falls back to the one below it:

1. **Solid.** An opaque surface for reduced transparency, more contrast, forced colors and the in-product "solid surfaces" toggle (`data-glass-surfaces="solid"` on `<html>`).
2. **Frost.** `backdrop-filter` blur and saturation with a rim light. This is what Safari and Firefox users see.
3. **Refract.** An SVG displacement map applied through `backdrop-filter: url()`. Only Chromium renders this today; Safari has not shipped SVG filters in `backdrop-filter` (WebKit bug 245510) and Firefox support is incomplete (Mozilla bug 1961378), per the 2026-11-05 snapshot.

Refraction in Safari or Firefox needs a different architecture: filtering the content layer itself, or capturing the page into WebGL. [glass-library-select](skills/glass-library-select/SKILL.md) covers those paths and what they cost.

## The engine and lab

[examples/glass-lab/liquid-glass.js](examples/glass-lab/liquid-glass.js) is an original, dependency-free ES module with TypeScript declarations. It computes displacement with vector Snell refraction over four bezel profiles. A Jacobian check keeps the map from folding at the corners, and the 128/255 neutral-point error is corrected inside the SVG filter. Chromatic aberration reads x from red and y from green in every pass. `createGlass(element, options)` chooses the tier, caches maps, rebuilds on resize and pixel-ratio changes, follows preference changes live and never removes focus outlines. Frost styling sits in a zero-specificity stylesheet, so your CSS always wins.

The [lab](examples/glass-lab/README.md) renders the engine over a busy backdrop with a control for every parameter, a tier override and a contrast estimate. It makes no network requests. To open it:

```sh
cd <plugin-root>/examples/glass-lab
python3 -m http.server 8000
```

Then visit `http://localhost:8000`. `<plugin-root>` is the folder that holds this README.

## Checks you can run on a product

Run these from your project directory. They use the Node `playwright` package and a browser that are already installed. If Playwright is missing they stop and explain how to install it in a scratch folder; they never add it to your project.

```sh
node <plugin-root>/scripts/glass_contrast.mjs --url http://localhost:3000 --selector 'nav.site' --text-selector 'nav.site a'
```

This hides the text, captures the rendered glass and backdrop behind each matched element, and reports the worst, 5th percentile and median contrast against WCAG thresholds. Measuring the worst-case backdrop is a stricter reading of WCAG 1.4.3, not a W3C rule.

```sh
node <plugin-root>/scripts/glass_probe.mjs --out glass-probe
```

This renders a known displacement filter and a backdrop blur in each installed Playwright engine and measures whether they actually took effect, instead of trusting user-agent strings or `CSS.supports`. Add `--url` and `--selector` to capture one of your own pages in every engine.

## Install

**Claude Code, this repository's marketplace:**

```sh
claude plugin marketplace add andrewr303/ultimate-AI-plugins
```

```sh
claude plugin install liquid-glass-studio@ultimate-ai-plugins
```

**Claude Code, local folder or ZIP for a single session:**

```sh
claude --plugin-dir /path/to/liquid-glass-studio
```

**Other hosts:** import the folder or the ZIP from `artifacts/liquid-glass-studio/` in this collection through the host's plugin workflow. `plugin.json` is the portable manifest; `.claude-plugin/plugin.json` carries the same identity for Claude Code. Each skill also has `agents/openai.yaml` display metadata.

No MCP server, hook, account, API key or background process is bundled.

## Limits

- Refraction was rendered and measured in Chromium only. Firefox and WebKit builds were not available where this was built, so their frost-only behavior comes from documentation and bug trackers, not observation. Run the probe on a machine with all three engines to confirm.
- The Swift, Kotlin and Dart samples were checked against published signatures but not compiled.
- Two of the six eval cases in `evals/` were scored with `claude plugin eval`; the other four were written and validated but not run. See [VALIDATION.md](VALIDATION.md) for results.
- Library facts describe the versions in the supplied archives, which may be older than the latest releases.

## Provenance

[NOTICE.md](NOTICE.md) lists the five studied projects, their licenses and the third-party code inside them. No upstream code is redistributed. The survey of existing agent skills, with its source register, claim ledger and decision report, is in [research/skills-survey](research/skills-survey/outputs/research-decision-report.md).

## Maintain

```sh
python3 scripts/validate_plugin.py .
```

```sh
node --test
```

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
```

```sh
python3 scripts/package_plugin.py . --output /absolute/path/liquid-glass-studio-1.0.0.zip
```

Run them from the plugin root. Development needs Python 3.10+ with PyYAML ([requirements-dev.txt](requirements-dev.txt)) and Node (tested on 22).
