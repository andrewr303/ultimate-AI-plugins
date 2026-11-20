---
name: liquid-glass-studio
description: 'Route liquid glass style UI work to the right specialist skill in this plugin: design decisions, optics tuning, web implementation, library choice, the tuning lab, native platforms, motion, accessibility, performance and review. Use when the user asks for "liquid glass", "glassmorphism", "frosted glass", "Apple glass", "glass effect", "glass UI", "refraction", "glass nav bar" or "make it look like iOS 26", or when the request spans more than one of those areas and you need a plan. Use it to pick the smallest skill set, not to load everything. Do not use for opaque card or shadow styling with no translucency, for physically based 3D glass in a game or product render, for photo filters, or for copying Apple assets, names or exact visuals.'
---

# Liquid Glass Studio

Plan and route work on translucent, refractive "liquid glass style" interfaces for the web and native platforms. "Liquid Glass" is Apple's name for its system material; this plugin is unaffiliated with Apple and helps you build your own glass that respects the platform, the user's settings and the product's brand. Open only the skills a task needs, and read references on demand.

## Start here

1. Read the project's own agent instructions, then inspect the actual product: stack, framework version, rendering mode (SPA, SSR, static), supported browsers or OS versions, and installed UI or glass libraries with their exact versions from the lockfile.
2. Find existing design tokens for surfaces, radii, blur, tint, focus and motion. Reuse them before adding new ones.
3. Classify the request: **design** (where and how much glass), **implement**, **tune**, **port**, **debug** or **review**. An implementation request ends with working code and checks, not a plan.
4. Name the one surface that matters first (usually the main navigation bar or toolbar) and the content it floats over. Broad requests start there and widen only when the scope supports it.
5. Pick skills from the table below. Open each chosen SKILL.md before acting on it.
6. Ship the solid tier first, then frost, then refraction. Every later tier must fail back to the one below it.

## Route by need

Paths are relative to this skill directory.

| User need or symptom | Open first | Add when relevant |
| --- | --- | --- |
| "Where should glass go?", how much, clear or regular, tint, radii, brand fit | [glass-design](../glass-design/SKILL.md) | glass-accessibility |
| Choose CSS frost, SVG refraction, WebGL capture or a library | [glass-library-select](../glass-library-select/SKILL.md) | glass-web |
| Build glass in vanilla, React, Vue, Svelte, web components or SSR | [glass-web](../glass-web/SKILL.md) | glass-optics, glass-accessibility |
| Edges tear, glass looks flat, rainbow fringes, wrong bend, map encoding | [glass-optics](../glass-optics/SKILL.md) | glass-lab |
| Tune parameters live, compare variants, export settings | [glass-lab](../glass-lab/SKILL.md) | glass-optics |
| SwiftUI, UIKit, AppKit, Compose, Flutter or React Native glass | [glass-native](../glass-native/SKILL.md) | glass-design, glass-accessibility |
| Press, stretch, morph, merge, springs, reduced motion | [glass-motion](../glass-motion/SKILL.md) | glass-performance |
| Contrast over moving backdrops, Reduce Transparency, forced colors, focus | [glass-accessibility](../glass-accessibility/SKILL.md) | glass-design |
| Jank, scroll cost, many panes, map rebuilds, DPR, GPU limits | [glass-performance](../glass-performance/SKILL.md) | glass-web |
| Pre-merge check or independent critique of existing glass | [glass-review](../glass-review/SKILL.md) | accessibility, performance |

## Combination recipes

**Add glass to an existing nav bar.**
1. glass-design: confirm the bar floats over scrolling content and is the only glass layer there; choose regular, decide tint (usually none) and radius.
2. glass-library-select: the bundled engine is the default unless the bar must refract in Safari or Firefox.
3. glass-web: solid tier in CSS, frost under `@supports`, refraction last; unique filter id; check for a Backdrop Root ancestor.
4. glass-accessibility: measure worst-case contrast while content scrolls under the bar; keep the focus outline.
5. glass-review before handoff.

**Build a glass component library.**
1. glass-design writes the decision record: which components get glass, variants, tint rules, concentric radii.
2. glass-library-select picks one rendering approach for the whole library and lists license notices to carry.
3. glass-web wraps the engine once (a hook, directive, action or custom element) with tier styling through `data-glass-tier`.
4. glass-motion for press and morph; glass-performance for the visible-surface budget.
5. glass-accessibility and glass-review for every component in light, dark and each preference mode.

**Port web glass to SwiftUI.**
1. glass-native: map each web surface to system components first, then `glassEffect` inside a `GlassEffectContainer`.
2. glass-design: drop web-only workarounds (manual frost, rim gradients) that the system material already provides.
3. glass-accessibility: verify Reduce Transparency, Increase Contrast and the Clear or Tinted setting on device.

**Fix "glass looks flat in Safari".**
1. glass-web: confirm the tier. Safari has not shipped SVG filters inside `backdrop-filter` (WebKit bug 245510, row W3 in the research snapshot), so a frost tier there is expected, not a bug.
2. glass-optics: make the frost tier carry depth with a rim, a top-lit gradient and saturation.
3. If refraction in Safari is a hard requirement, glass-library-select for a content-layer or WebGL capture path, then glass-performance.
4. Also rule out a Backdrop Root ancestor and `prefers-contrast: more` forcing the solid tier.

**Review only.** glass-review plus the reference for each finding area. Report findings with evidence states; do not rewrite the product.

Choose one owner per shared file. Design, accessibility and performance reviews can run in parallel. Bounded briefs for delegated work live in `<plugin-root>/agents/`, with a delegation guide in [docs/agent-briefs.md](../../docs/agent-briefs.md) (pass each worker the absolute plugin root), and Claude Code users can start with the `/glass` and `/review-glass` commands in `commands/`. Their presence does not create tools or grant authority.

## Rules

- **Glass belongs to the navigation and control layer only.** Content (cards, rows, article text, tables, page backgrounds) stays opaque or uses a standard frosted material.
- **A solid tier always exists and always works.** Forced colors, reduced transparency, more contrast, missing `backdrop-filter`, failed map builds and lost GPU contexts all land on a designed solid or frosted surface, never on a blank one.
- **Never remove or hide focus outlines** to keep glass clean. Focus indicators need 3:1 contrast over the worst backdrop.
- **Measure contrast over the worst-case backdrop**, on the rendered page, per tier and per scroll position. A tint never "guarantees" a ratio.
- **Refraction through `backdrop-filter: url()` is a Chromium-only enhancement.** `@supports` cannot detect whether it renders. Only a WebGL or content-layer capture path refracts in Safari and Firefox, with its own costs.
- **Check installed versions** of any glass library, framework and SDK before using an API. Repository main is not proof that the installed release has it.
- **Cite moving facts** (browser bugs, media query support, Apple guidance, iOS changes) from [research-snapshot.md](../../references/research-snapshot.md) with the check date, and re-open the source before gating code or advising a client on them.
- One glass layer over any point of content at rest. No glass on glass.
- Do not name the component "Liquid Glass", ship Apple assets, or imply Apple endorsement.
- Keep a small task small. Do not create spec documents just to fill a template.

## Verify

`<plugin-root>` is this plugin's install folder: two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Run the scripts from the user's project directory by path; output paths such as `--out` and `--screenshot` resolve against the current directory, and missing folders are created.

```sh
node --test <plugin-root>/tests/engine.test.mjs          # engine math, map encoding, tier table
node <plugin-root>/scripts/glass_contrast.mjs --url http://127.0.0.1:4173/ \
  --selector ".nav-bar" --text-selector ".nav-bar a, .nav-bar span" --require auto --json
python3 <plugin-root>/scripts/validate_plugin.py <plugin-root>   # when you edit this plugin itself
cd <plugin-root>/examples/glass-lab && python3 -m http.server <free port> --bind 127.0.0.1   # the tuning lab
```

- Measure text, never a whole container. `--selector` alone compares one color (the container's own) with every pixel of its box, including logos, icons and buttons with their own fills, so it gives false passes and false failures. `--text-selector` measures each matched text element over its own box with its own color and reports the worst; run it once per distinct text style if one selector cannot reach them all.
- `glass_contrast.mjs` needs Playwright and never installs it or its browsers. It looks for it through `PLAYWRIGHT_MODULE`, the project, the plugin and the global npm root. If it is missing, do not add it to the user's project without asking; offer a scratch install (`npm i playwright --prefix <scratch>`, then `PLAYWRIGHT_MODULE=<scratch>/node_modules/playwright`) or a global one. Exit 2 means it could not run, which is not a pass.
- Take real-browser screenshots of each tier the user can reach: Chromium (refract), WebKit and Gecko (frost), and the solid tier under emulated `prefers-contrast: more` and `forced-colors: active`.
- Report what ran, what passed, what was not run, and which engines were never opened.

## References

- [design-principles.md](../../references/design-principles.md), [accessibility.md](../../references/accessibility.md), [motion.md](../../references/motion.md), [performance.md](../../references/performance.md)
- [web-techniques.md](../../references/web-techniques.md), [browser-support.md](../../references/browser-support.md), [optics.md](../../references/optics.md), [gotchas.md](../../references/gotchas.md)
- [library-matrix.md](../../references/library-matrix.md), [native.md](../../references/native.md), [research-snapshot.md](../../references/research-snapshot.md)
- Engine and lab: [examples/glass-lab/README.md](../../examples/glass-lab/README.md)
