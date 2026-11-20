---
name: glass-library-select
description: 'Choose how to render liquid glass style refraction on the web: plain CSS frost, the bundled dependency-free engine, or one of five studied open-source libraries (glasshq-liquid-glass, simple-liquid-glass, liquidGL, ybouane-liquidglass, liquid-glass-react), with license and notice obligations, engine reach, framework fit, bundle cost and accessibility gaps. Use when the user asks "which liquid glass library should I use", "is there an npm package for Apple glass", "liquid-glass-react vs simple-liquid-glass", "glassmorphism library", "refraction in Safari", "can I use this glass code commercially", or before adding any glass dependency. Do not use for native apps (glass-native), for tuning an already chosen renderer (glass-optics), or for wiring code (glass-web).'
---

# Select a glass library or approach

Pick the smallest rendering approach that meets the engines, backdrop and accessibility the product needs, and write down what the choice obliges the project to carry. The default answer is the bundled engine (Chromium refraction, frost elsewhere, solid for accessibility preferences) unless the product truly needs refraction outside Chromium, which only a content-layer or WebGL capture path provides.

## Start here

1. Inspect the project: framework and version, SSR, bundle budget, CSP (inline SVG and data URLs), supported browsers with their share of real traffic, and any glass or GPU library already installed (check the lockfile, not the README).
2. Ask or infer the answers to the five questions in [library-matrix.md section 7](../../references/library-matrix.md#7-questions-to-answer-before-choosing). The second one (what is behind the glass) decides more than any other.
3. Walk the decision procedure below. Stop at the first step that settles it.
4. Re-check the moving facts the choice depends on (next section) and record the decision.
5. Hand off to [glass-web](../glass-web/SKILL.md) for implementation.

## Re-check before you recommend

Versions in this plugin are snapshots observed on 2026-11-05. Before naming a library to a user:

- Open its registry page and repository for the current version, license file and recent open issues.
- Re-open WebKit bug 245510 and Firefox bug 1961378 ([research-snapshot.md](../../references/research-snapshot.md) rows W3 and W4). If Safari or Firefox ships SVG filters inside `backdrop-filter`, the case for capture-based libraries weakens.
- If a fact cannot be re-checked, state the check date and say it is unconfirmed.

## Decision procedure

1. **Native target** (SwiftUI, UIKit, AppKit, Compose, Flutter, React Native)? Use platform APIs through [glass-native](../glass-native/SKILL.md). Stop.
2. **Is frost enough?** Many bars and menus look right with blur, saturation, tint and a rim. Use CSS only (Tier 1 over a solid Tier 0). No dependency.
3. **Is Chromium-only refraction acceptable, with designed frost elsewhere?**
   - Yes: the bundled engine. Smallest footprint, accessibility tiers built in, tests included, you own maintenance.
   - Yes, and the team insists on a ready React component: liquid-glass-react, but budget for its known issues (blue-channel y selector, fixed `id`, clickable div, `navigator` read during render; see its source note).
4. **Must refraction show in Safari and Firefox?** This requires a capture path. Decide what is behind the glass:
   - A content region you own and can declare as the layer under the glass, React 19 or a DOM controller is fine: glasshq-liquid-glass.
   - Arbitrary page content, video or canvas, React or a web component, and you can name a backdrop element that is not an ancestor of the glass: simple-liquid-glass.
   - Vanilla hero lenses, magnifiers or docks with GSAP or Lenis, and you will add accessibility yourself: liquidGL.
   - A few self-contained vanilla panels with rich lighting, and you accept no fallback: ybouane-liquidglass, after resolving its license gap.
5. **Many surfaces at once (more than about 12)?** Prefer a shared-canvas approach over many SVG panes, and read [performance.md section 4](../../references/performance.md#4-instance-limits-and-the-16-pane-heuristic).
6. **Whatever you pick**, the project still needs the solid tier, a visible focus style and measured contrast. No studied library supplies all three.

The full tree with reasons is in [library-matrix.md section 6](../../references/library-matrix.md#6-decision-tree).

## Quick comparison

| Option | Refracts in | Fallback it ships | Accessibility it ships | Main cost |
| --- | --- | --- | --- | --- |
| CSS frost only | nowhere | you write the solid tier | what you write | none |
| Bundled engine | Chromium | frost, and solid for preferences | solid tier for reduced transparency, more contrast, forced colors; leaves focus alone | you maintain one file |
| glasshq-liquid-glass | Chromium, Safari, Firefox (declared content layer only) | content stays visible without the material | Base UI roles and keyboard; no reduced-transparency path; faint focus | React 19 or DOM controller; version 0.0.x |
| simple-liquid-glass | Chromium; Safari and Firefox with a named backdrop | designed frost | reduced motion only | carries several vendored notices |
| liquidGL | all engines claimed | blur only, when no GPU is found up front | none | about 62 KB gzip unminified, no tests |
| ybouane-liquidglass | all evergreen engines claimed | none; init rejects without WebGL | none | license file missing |
| liquid-glass-react | Chromium | blur and saturate elsewhere | none | demo grade, known map and id bugs |

Sizes, versions and engine claims come from [library-matrix.md sections 2 and 3](../../references/library-matrix.md#2-matrix-rendering-and-reach); verify them before quoting.

## License and notice obligations

| Option | Obligation |
| --- | --- |
| Bundled engine | MIT. Keep the file header and include the plugin's copyright line and license text in third-party notices. |
| glasshq-liquid-glass | MIT, "Copyright (c) 2026 Glass HQ". Its runtime dependencies carry their own licenses, not reviewed here; check each. |
| simple-liquid-glass | MIT, "Copyright (c) 2025 lucaperullo", plus every notice in its `THIRD_PARTY_NOTICES.md` for the code it vendors (samasante/liquid-glass, @ybouane/liquidglass, html-to-image, a liquidGL optics port). |
| liquidGL | MIT, "Copyright (c) NaughtyDuk", for `scripts/` and `package/` only. Fonts and audio under `assets/` are excluded; do not copy them. |
| ybouane-liquidglass | package metadata says MIT but the studied archive has no LICENSE file or copyright line. Do not copy code until the holder and notice are confirmed; cite it as inspiration only. |
| liquid-glass-react | MIT, "Copyright 2025 MAX ROVENSKY". `src/shader-utils.ts` is adapted from another repository whose license was not verified; resolve that before copying it. |

These come from [library-matrix.md section 4](../../references/library-matrix.md#4-matrix-maturity-license-and-attribution). This is engineering diligence, not legal advice; route real license questions to the project's legal owner.

## Decision record

Record in the PR or design doc:

1. The chosen option and version (from the lockfile after install, or the plugin file date for the engine).
2. Engines that get refraction, frost and solid.
3. What sits behind the glass and any capture gaps accepted (iframes, cross-origin images, video).
4. Accessibility gaps the project must fill (solid tier, focus style, roles).
5. License notices added and where.
6. Facts re-checked, with dates, and anything left unconfirmed.

## Rules

- Prefer the bundled engine when no WebGL or content-layer capture path is required.
- Never add a dependency the user did not approve; propose it with the record above.
- Check the installed version and its docs before using any library API; repository main is not the installed release.
- Count every notice the dependency brings, including vendored code.
- A library never replaces the project's own solid tier, focus style or contrast measurement.
- Cite library facts with the library and file, as the source notes do.

## Verify

`<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Run plugin scripts from the user's project directory by path; output paths resolve against the current directory.

- After install, confirm the version in the lockfile matches the record.
- Build once and compare bundle size before and after with the project's own build output.
- Open the page in Chromium, WebKit and Firefox and screenshot what each actually shows; compare against the "Refracts in" column.
- Run [glass-accessibility](../glass-accessibility/SKILL.md) checks on whatever the library renders, including `node <plugin-root>/scripts/glass_contrast.mjs --url <url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto`, which measures each text element rather than the whole container.
- For the bundled engine: `node --test <plugin-root>/tests/engine.test.mjs`.

## References

- [library-matrix.md](../../references/library-matrix.md): matrices, decision tree, questions
- Source notes: [glasshq-liquid-glass](../../references/sources/glasshq-liquid-glass.md), [simple-liquid-glass](../../references/sources/simple-liquid-glass.md), [liquidGL](../../references/sources/liquidgl.md), [ybouane-liquidglass](../../references/sources/ybouane-liquidglass.md), [liquid-glass-react](../../references/sources/liquid-glass-react.md)
- [web-techniques.md](../../references/web-techniques.md) for tiers and capture limits; [browser-support.md](../../references/browser-support.md) for engines
- [research-snapshot.md](../../references/research-snapshot.md) for dated platform facts
