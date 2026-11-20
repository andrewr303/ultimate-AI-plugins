---
name: glass-accessibility
description: "Makes liquid glass style surfaces accessible: a solid tier for reduced transparency, more contrast and forced colors, an in-product solid toggle where browser support is missing, reduced motion, worst-case text contrast measured over the real rendered backdrop with scripts/glass_contrast.mjs, focus rings that survive any backdrop, and semantics for glass controls. Use when the user asks \"is my glass accessible\", \"text on frosted glass is hard to read\", \"glassmorphism contrast\", \"liquid glass and reduced transparency\", \"Apple glass accessibility\", \"WCAG on a glass effect\", or how glass should behave in high contrast mode. Do not use for general WCAG audits without glass, for picking glass parameters for looks alone (use glass-design or glass-optics), or for a full multi-area review (use glass-review)."
---

# Glass accessibility

Glass changes its own background every time the content beneath it moves, and its effects collide with user settings for transparency, contrast and motion. This skill gives every glass surface a designed solid fallback, wires the preferences that exist and covers the ones that do not, measures text contrast against the worst pixel actually rendered behind the text, and keeps focus and semantics intact. The worst-case method is this plugin's engineering inference from WCAG 1.4.3 and 1.4.11, not a W3C procedure; say so in reports.

## Start here

1. **Inventory** every glass surface: variant (clear or regular, tier per engine), the text and controls on it, the content it can float over (photos, video, user content, scrolling feeds), and its states (hover, pressed, selected, open).
2. **Find existing handling**: `rg -n "prefers-reduced-transparency|prefers-contrast|forced-colors|prefers-reduced-motion|accessibilityReduce|colorSchemeContrast" .` and note any user setting for themes or contrast that a solid toggle can join.
3. **Find the tokens** for an opaque surface, its text color and its border in the existing design system. The solid tier uses these, not new colors.
4. **Check support for the engines you ship** in [browser-support.md](../../references/browser-support.md#1-feature-matrix), and read the caveat below before relying on any media query.
5. Write the preference behaviour and acceptance checks into [glass-spec.md](../../templates/glass-spec.md).

## Preferences and their support

| Preference | Web signal | Support caveat (checked 2026-11-05) | Required behaviour |
| --- | --- | --- | --- |
| Reduced transparency | `prefers-reduced-transparency: reduce` | Chromium supports it; Firefox only behind a pref. **Not supported in Safari as of the 2026-11-05 snapshot**: MDN browser-compat-data records no Safari version, and the WebKit implementation bug 175497 (https://bugs.webkit.org/show_bug.cgi?id=175497) is still NEW. | go solid; **also ship an in-product "Solid surfaces" toggle** |
| More contrast | `prefers-contrast: more` | Chrome 96, Firefox 101, Safari 14.1 | go solid or near-solid with a stronger border; also serves as the Safari proxy for reduced transparency |
| Forced colors | `forced-colors: active` | Chrome 89, Firefox 89; Safari 16 always matches `none` | system colors, a real border, no filters, decorative layers hidden |
| Reduced motion | `prefers-reduced-motion: reduce` | Chrome 74, Firefox 63, Safari 10.1 | no stretch, lean or travel; morphs become fades; feedback stays |
| Apple Reduce Transparency, Increase Contrast, Reduce Motion | `\.accessibilityReduceTransparency`, `\.colorSchemeContrast`, `\.accessibilityReduceMotion` | system glass adapts; your own overlays do not | see the `glass-native` skill |

Because Safari users cannot reach the solid tier through `prefers-reduced-transparency`, never let a media query be the only path to opaque surfaces. The toggle is required in every web product that ships glass, whatever the media query does, and stays required when Safari ships the query, since users on older versions keep the gap.

## Build the solid tier and the toggle

The toggle has one name everywhere in this plugin: the attribute `data-glass-surfaces="solid"` on the `<html>` element. The tokens are the ones [glass-web](../glass-web/SKILL.md#tier-order-solid-then-frost-then-refract) defines on `:root`; if glass-web already wrote this CSS, check it rather than adding a second copy.

```css
:root {
  --glass-solid: Canvas;          /* map each to a design-system token */
  --glass-solid-ink: CanvasText;
  --glass-solid-line: color-mix(in srgb, CanvasText 30%, transparent);
}
.glass[data-glass-tier="solid"],
:root[data-glass-surfaces="solid"] .glass {
  backdrop-filter: none; -webkit-backdrop-filter: none; filter: none;
  background: var(--glass-solid); color: var(--glass-solid-ink);
  border: 1px solid var(--glass-solid-line);
}
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more) {
  .glass {
    backdrop-filter: none; -webkit-backdrop-filter: none; filter: none;
    background: var(--glass-solid); color: var(--glass-solid-ink);
    border: 1px solid var(--glass-solid-line);
  }
}
```

Swap `Canvas` and `CanvasText` for your own opaque tokens on `:root`, never on `.glass`, so every rule reads the same values. Then:

- Put the toggle in settings with a plain label ("Solid surfaces", "Reduce transparency"), store the choice, and set the attribute from a small inline script in `<head>` before first paint, so the page never flashes glass first. Guard storage access with try and catch:

```html
<script>
  try {
    if (localStorage.getItem('surfaces') === 'solid') {
      document.documentElement.setAttribute('data-glass-surfaces', 'solid');
    }
  } catch (e) { /* storage blocked: the media queries still apply */ }
</script>
```

- With this plugin's engine, the attribute is all you need: the engine watches it and switches every instance to `solid` live, with the reason "the user turned on solid surfaces". It also drops to `solid` for forced colors, reduced transparency and more contrast ([glass-lab README](../../examples/glass-lab/README.md#solid-surfaces-setting)). Other JavaScript renderers must watch the same attribute and tear down their effect. Style `[data-glass-tier="solid"]` with the opaque tokens, because the engine's stylesheet removes the backdrop filter but does not paint a background.
- Forced colors: `background: Canvas; color: CanvasText; border: 1px solid CanvasText`, buttons on `ButtonFace` and `ButtonText`, selected states on `Highlight`, and decorative canvases and overlays `display: none` ([accessibility.md](../../references/accessibility.md#6-forced-colors)).
- Rims drawn only with `box-shadow` or gradients vanish in forced colors; always add a real border there.

## Measure worst-case contrast

Measuring the text color against the tint alone, or one screenshot, certifies nothing. Measure what the text actually sits on, at its worst:

Run the plugin's script from the user's project directory by path. `<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads); output paths resolve against the current directory.

```sh
node <plugin-root>/scripts/glass_contrast.mjs --url http://127.0.0.1:5173/ \
  --selector ".toolbar" --text-selector ".toolbar .label, .toolbar a" \
  --dpr 2 --color-scheme dark --require auto --screenshot review/toolbar-dark.png --json
```

Measure text, never a whole container. `--selector` alone compares one color (the matched element's own) with every pixel of its box, so a toolbar that holds icons, logos or buttons with their own fills gives false passes and false failures. `--text-selector` measures each matched text element over its own box, with its own computed color, and reports each element and the worst. The script (optional Playwright dependency, Chromium only) hides the text without changing layout, screenshots each element, and compares the text color with every pixel behind it; `--require auto` picks 4.5:1 or 3:1 from the computed font size and weight and exits 1 below it. One run covers one scroll position and one animation moment, so repeat it:

1. for every text element on glass, at each scroll position where the surface crosses different content;
2. over the brightest and darkest media frames you can pin;
3. in light and dark, and in hover, pressed and selected states;
4. per tier you ship. The script runs Chromium only, so measure the frost tier by forcing it in Chromium (with this plugin's engine, `tier: 'frost'`), and record real WebKit and Gecko contrast as not checked unless you measured it another way.

For component boundaries, toggle states and focus rings, sample the ring just outside the edge and require 3:1. When the minimum fails, fix in this order: regular instead of clear, a dimming layer under the glass, heavier or larger text, a halo wide enough to count as the text's background, moving the surface off the brightest content, a solid surface ([accessibility.md](../../references/accessibility.md#2-worst-case-backdrop-contrast)). Treat any claim that a tint "guarantees" a ratio as a finding: a fixed tint cannot bound contrast over an arbitrary backdrop.

## Focus and semantics

- Never remove the outline from glass controls. A two-tone ring (light outline plus a dark outer ring) stays visible over any backdrop; in forced colors use `Highlight` ([accessibility.md](../../references/accessibility.md#8-focus-visibility)).
- Check that `overflow: hidden` or `clip-path` on the glass does not cut the ring off; draw it on an unclipped wrapper or inset it.
- Floating glass bars must not hide the focused element (WCAG 2.4.11): set `scroll-padding` to the bar heights.
- A clickable glass surface is a `<button>` or `<a href>`, with glass as styling. Icon-only glass buttons get an accessible name.
- Decorative canvases, SVG filter hosts and rim layers get `aria-hidden="true"`. Do not set `pointer-events: none` on interactive glass, do not set `user-select: none` on content, and keep content in the accessibility tree while the effect loads (hide with `opacity`, not `visibility`).
- Drag-to-move glass needs a keyboard alternative.

## Rules

- Every glass surface has a designed opaque tier with a visible border.
- Every web product with glass ships an in-product solid toggle (`data-glass-surfaces="solid"` on `<html>`); `prefers-reduced-transparency` is not supported in Safari as of the 2026-11-05 snapshot, so no media query is the only route.
- `prefers-contrast: more` and `forced-colors: active` always reach the opaque tier.
- Contrast is measured on rendered pixels at the worst backdrop state; ratios are never asserted from the tint, and 4.499:1 fails.
- Focus outlines are never removed, clipped or hidden under a floating bar.
- Report the measurement method as an engineering inference from WCAG, not a conformance certificate.

## Verify

1. `node --test <plugin-root>/tests/contrast.test.mjs` checks the luminance and contrast math the script uses.
2. Contrast sweep with `node <plugin-root>/scripts/glass_contrast.mjs ... --text-selector "<text elements>" --require auto --screenshot <file>` across the states above; keep every JSON report and screenshot for the record.
3. Engine detection: `node <plugin-root>/scripts/glass_probe.mjs --browsers chromium,firefox,webkit --json` reports which engines actually render refraction and backdrop blur, so you know which tiers need a contrast sweep.
4. Preferences in a real browser: DevTools Rendering panel (or Playwright `page.emulateMedia({ reducedMotion: 'reduce', forcedColors: 'active' })`) for each preference, plus the solid toggle. Screenshot each state. Pass: opaque surfaces with borders, system colors in forced colors, no travel under reduced motion.
5. Keyboard: Tab through every control; each shows an unclipped ring with 3:1 contrast and is not covered by a floating bar.
6. Screen reader: VoiceOver and NVDA or Narrator announce every control with a role and name; decorative layers stay silent.
7. Mark each check checked, not checked or not applicable, with the engine and device it ran on.

## References

- [accessibility.md](../../references/accessibility.md): criteria, worst-case method, treatments, preferences, focus, semantics, test procedure
- [browser-support.md](../../references/browser-support.md#2-what-users-see-per-tier-and-engine): what each engine shows
- [research-snapshot.md](../../references/research-snapshot.md): sources and check dates
- [gotchas.md](../../references/gotchas.md#accessibility): accessibility failure modes in the libraries
- [motion.md](../../references/motion.md#7-reduced-motion-alternatives): reduced-motion alternatives
- [glass-lab README](../../examples/glass-lab/README.md#accessibility-in-the-lab): a working example
