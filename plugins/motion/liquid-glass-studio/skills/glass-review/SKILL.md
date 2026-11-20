---
name: glass-review
description: "Runs an evidence-based review of liquid glass style UI on the web and native platforms: a phased audit, named detection patterns with a false-positive list, real-browser screenshots across tiers and preferences, a cross-engine probe of whether refraction and backdrop blur actually render, measured worst-case text contrast, a docs drift check, and a report where every check is checked, not checked or not applicable and every finding has severity, repro steps and evidence. Use when the user asks to \"review my liquid glass UI\", \"audit the glassmorphism\", \"check the glass effect before release\", \"why does the glass look wrong in Safari or Firefox\", \"is this Apple glass implementation correct\", or wants a frosted glass or refraction PR assessed. Do not use to build glass from scratch (use glass-web or glass-native) or for a review with no glass in scope."
---

# Glass review

Assess glass surfaces with evidence, not impressions. The review moves in phases: bound the scope, inventory the surfaces, scan the code with named detection patterns, gather runtime evidence in real engines, then triage and report. Every check ends in one of three evidence states, and every finding carries a severity, a repro and the evidence behind it. This pattern adapts two strong reviewers from the skills survey (a phased auditor with a false-positive list, and checked / not checked / not applicable states) and adds what none of them had: a cross-engine render probe and measured contrast over the real backdrop.

## Start here

1. **Bound the request.** Note whether the user wants an assessment, fixes, or both. An assessment authorizes reading and running, not edits. Identify the changed files or flows, supported engines and platforms, and the slowest target device.
2. **Read project instructions and the implementation** before forming any finding. Record the stack, installed versions, how glass is rendered, and existing design tokens.
3. **Record your access**: which browsers, devices, simulators and assistive technology you can run. Missing access becomes "not checked", never a pass.
4. Copy [review-report.md](../../templates/review-report.md) to a scratch location the project ignores (not a tracked path unless asked) and fill it as you go.

## Phase 1: inventory

List every glass surface in scope with its role (floating control, navigation, menu, content), variant, tier per engine, the text and controls on it, and the content it can cover. If a [glass-spec.md](../../templates/glass-spec.md) exists, review against it and treat departures as findings.

## Phase 2: static scan with detection patterns

Search with `rg -n` over the source (exclude `node_modules` and build output). Each hit is a candidate, not a finding, until Phase 4 rules out the false positives.

| ID | Pattern | Signals to search | Default severity |
| --- | --- | --- | --- |
| GR1 | Glass in the content layer | `backdrop-filter`, `glassEffect`, `UIGlassEffect`, `NSGlassEffectView` on cards, rows, article bodies, page backgrounds | Major |
| GR2 | Glass on glass | nested glass elements; glass inside a glass toolbar; custom backgrounds on system bars | Major |
| GR3 | Ungated refraction | `backdrop-filter: url(` or `filter: url(#` with no engine gate; `@supports (backdrop-filter: url(` used as the only gate | Major |
| GR4 | No solid tier or toggle | no `prefers-reduced-transparency`, `prefers-contrast`, `forced-colors` handling; no in-product solid setting | Blocker when text sits on glass |
| GR5 | Asserted contrast | comments or docs claiming a tint "guarantees" a ratio; light or dark text switched by a luminance threshold; no measurement on record | Major |
| GR6 | Focus removed or clipped | `outline: none` or `outline: 0` on glass controls; `overflow: hidden` or `clip-path` on the focusable element; floating bars with no `scroll-padding` | Blocker |
| GR7 | Non-semantic glass control | click handlers on `div` or `span` glass; `pointer-events: none` on interactive glass; decorative canvas or SVG without `aria-hidden` | Major |
| GR8 | Motion without a reduced path | springs, scale or morph code with no `prefers-reduced-motion` or `accessibilityReduceMotion` branch; framework state set per `pointermove` | Major |
| GR9 | Per-frame waste | rAF loops that never sleep; recapture or map rebuild on scroll; `getBoundingClientRect` in render; no DPR cap; unbounded caches | Minor, Major if measured jank |
| GR10 | Map encoding errors | JPEG maps; `yChannelSelector="B"`; missing `color-interpolation-filters="sRGB"`; no neutral-128 correction; dispersion order with green highest | Minor |
| GR11 | Backdrop Root trap | an ancestor of the glass with `opacity` below 1, `filter`, `mask`, `clip-path`, `backdrop-filter`, `mix-blend-mode` or a matching `will-change` | Major |
| GR12 | Native availability and API errors | 26-only symbols with no `#available` while the deployment target is lower; `Glass` in an unguarded signature; API names not in [native.md](../../references/native.md); effect view `alpha` below 1; several glass views with no container | Blocker for a crash or build break, otherwise Major |
| GR13 | Too many live surfaces | more than about 12 refractive surfaces visible; one WebGL context per instance | Minor |

Map hits to the numbered failure modes in [gotchas.md](../../references/gotchas.md) when one applies ("GR11, see G1").

**False positives to rule out before reporting:**

- GR1: a slider thumb or toggle that takes glass only while dragged (Apple's stated exception); a hero lens the spec accepts over a backdrop the product controls.
- GR2: a selection lens inside a tab bar with reduced refraction and a distinct role; overlap that exists only during a morph.
- GR3: refraction behind an engine check such as this plugin's `detectTier` or `explainTier`, or a documented Chromium-only internal tool.
- GR4: preferences handled in script (`matchMedia` listeners driving a solid tier) rather than CSS; native system glass with no custom overlays.
- GR6: `:focus:not(:focus-visible) { outline: none }` with a visible `:focus-visible` ring; a ring drawn on an unclipped wrapper.
- GR7: a `div` with `role="button"`, `tabindex="0"` and Enter and Space handling (still note that a `<button>` is simpler).
- GR8: a global setting such as a motion library configured to follow the user preference; confirm it in the config, not the docs.
- GR9: a loop that stops when settled; a one-shot measurement.
- GR11: a Backdrop Root that is intentional, where the glass should only show content inside its container.
- GR12: a deployment target already at 26 or later; availability handled inside a wrapper modifier.

## Phase 3: runtime evidence

Run the app with its documented dev command on a free port, or use a preview URL you were given. Never drive production or a user's running instance. `<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Run plugin scripts from the user's project directory by path; output paths resolve against the current directory.

1. **Cross-engine probe.** `node <plugin-root>/scripts/glass_probe.mjs --browsers chromium,firefox,webkit --out <scratch>/probe --json`. It reports per engine whether refraction and backdrop blur actually render. Compare with what the code assumes; a tier the code expects but the engine does not render is a finding.
2. **Screenshots across tiers and preferences.** In Playwright or a real browser, capture each surface in scope: refraction (Chromium), frost (WebKit and Gecko, or forced), solid; light and dark; `reducedMotion: 'reduce'` and `forcedColors: 'active'` through `page.emulateMedia`; reduced transparency through the Chromium DevTools Rendering panel; the in-product solid toggle (`data-glass-surfaces="solid"` on `<html>`). Name files `<surface>-<engine>-<state>.png`. For the plugin's own lab, `?tier=frost` and `?tier=solid` force a tier ([glass-lab README](../../examples/glass-lab/README.md#run-it)).
3. **Contrast.** `node <plugin-root>/scripts/glass_contrast.mjs --url <url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto --screenshot <scratch>/<name>.png --json` for the text elements on each glass surface (for example `--selector 'nav.site' --text-selector 'nav.site a, nav.site span'`), never the container alone, whose one color would be compared with every pixel of its box, at the worst scroll positions and media frames, light and dark ([accessibility.md](../../references/accessibility.md#2-worst-case-backdrop-contrast)).
4. **Interaction.** Keyboard pass (reach, operate, visible unclipped ring), screen reader where available, press and morph interruption at normal speed, reduced motion switched on mid-animation.
5. **Performance**, only when jank is visible or claimed: a trace and frame pacing per [performance.md](../../references/performance.md#8-measuring).
6. **Native**: build for the newest SDK and the lowest deployment target, screenshot both, and repeat with Reduce Transparency, Increase Contrast and Reduce Motion.
7. **Drift check** when the review touches this plugin's engine or references: `node --test <plugin-root>/tests/docs_drift.test.mjs`. In the user's project, compare any glass docs or README claims against the code and report contradictions.

## Phase 4: triage

Remove false positives, merge duplicates, and assign severity:

| Severity | Meaning |
| --- | --- |
| Blocker | crashes, fails to build, hides content, traps focus, or leaves text unreadable in a tested state |
| Major | fails a stated requirement (layer rule, preference, measured contrast, interruption) on a common path, or breaks an engine the product supports |
| Minor | reproducible defect with a workable path, or a cost that is measurable but inside budget |
| Note | polish or a risk inferred from code with no observed effect |

Every finding states: ID and pattern, severity, location (file and line, or screen and element), repro steps, expected versus observed, evidence (screenshot file, probe or contrast JSON, trace, or code excerpt) and its type (observed, measured, static, inferred), and the smallest fix with the skill that owns it (`glass-web`, `glass-native`, `glass-accessibility`, `glass-motion`, `glass-performance`, `glass-optics`).

## Phase 5: report

Fill [review-report.md](../../templates/review-report.md): scope, environment, evidence states per check, findings table ordered by severity, screenshot list, measurements, and limitations. "No findings in the checked scope" is a valid result; it is not a certification.

## Rules

- Every check ends as checked, not checked or not applicable; never fill a gap with a guess.
- "Observed" and "measured" are reserved for things you ran; code-only risks are "static" or "inferred".
- One engine is one engine: a Chromium screenshot says nothing about WebKit or Gecko.
- Contrast is measured, never asserted from the tint.
- Do not invent findings to fill severities, and do not call a taste disagreement a Blocker.
- An assessment request does not authorize edits; fixes follow only when asked, and then the failing check is rerun.
- Keep screenshots of real user data out of shared reports; use synthetic or masked data.

## Verify

The review is complete when every check in the report has an evidence state, every finding has repro and evidence, the probe and contrast outputs are saved next to the report, and the limitations list names each engine, device or assistive technology that was not checked. If you changed plugin files during the review, run `python3 <plugin-root>/scripts/validate_plugin.py <plugin-root>` and `node --test <plugin-root>/tests/docs_drift.test.mjs`.

## References

- [review-report.md](../../templates/review-report.md) and [glass-spec.md](../../templates/glass-spec.md)
- [gotchas.md](../../references/gotchas.md): numbered failure modes to cite in findings
- [design-principles.md](../../references/design-principles.md#11-anti-patterns): anti-patterns behind GR1 and GR2
- [browser-support.md](../../references/browser-support.md): engine matrix for GR3 and the probe
- [accessibility.md](../../references/accessibility.md#12-test-procedure): accessibility test procedure
- [performance.md](../../references/performance.md#9-budgets): budgets for GR9 and GR13
- [native.md](../../references/native.md): API facts for GR12
- [web-techniques.md](../../references/web-techniques.md#6-the-backdrop-root-rule): the Backdrop Root rule for GR11
