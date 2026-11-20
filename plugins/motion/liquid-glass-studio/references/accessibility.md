# Accessibility of liquid glass style UI

Translucent, refracting surfaces change their own background every time the content beneath them moves. That breaks the usual "check the two colors once" approach to contrast, and the effects themselves (blur, elasticity, morphs) collide with user settings for transparency, contrast and motion. This reference gives the criteria that apply, a measurement method for variable backdrops, the fallbacks to build, and a test procedure.

## Source keys

W3C, Apple and browser facts cite a URL and "checked 2026-11-05" (see [research-snapshot.md](research-snapshot.md)). Library claims cite `<library> <path>`: glasshq (paths under `packages/liquid-glass/`), simple-liquid-glass, liquidGL, ybouane, liquid-glass-react. **Inference** marks reasoning that is not a W3C or vendor rule.

## 1. WCAG criteria that apply to glass

| Criterion | Level | Requirement | What it means on glass |
| --- | --- | --- | --- |
| 1.4.3 Contrast (Minimum) | AA | 4.5:1 for text, 3:1 for large text (18 pt, or 14 pt bold; about 24 px or 18.5 px bold). Ratios are not rounded: 4.499:1 fails. Measured against "the specified background over which the text is rendered in normal usage" | The background is the composited glass over whatever content is beneath, so it changes with scroll and media. Failure F83 covers text over background images without enough contrast |
| 1.4.11 Non-text Contrast | AA | 3:1 for visual information needed to identify components, their states, and graphical objects, against adjacent colors (2.999:1 fails) | A glass button's boundary, a toggle's state, a slider track: each must reach 3:1 against what is next to it, which for glass is the backdrop |
| 2.4.7 Focus Visible | AA | keyboard focus indicator is visible | Do not trade the outline for a faint tint (section 8) |
| 2.4.11 Focus Not Obscured (Minimum) | AA, new in 2.2 | a focused component is not entirely hidden by author content | Floating glass tab bars and toolbars can cover focused items in scrolling content |

Sources: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html ; https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html ; https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html (all checked 2026-11-05; the 2.4.11 page was confirmed to exist but not re-read). For gradients, the 1.4.11 Understanding text suggests the central color of the area in one place and the least contrasting area in its testing principles. On glass, use the least contrasting area.

Two further criteria matter when glass animates: 2.3.3 Animation from Interactions (AAA) and 2.2.2 Pause, Stop, Hide (A) for anything that moves by itself for more than five seconds, such as a looping specular sweep. These were not re-checked for this snapshot.

## 2. Worst-case backdrop contrast

WCAG has no rule written for translucent surfaces. The method below is an **engineering inference** from 1.4.3 and 1.4.11, not a W3C procedure. It is defensible because it measures the background the text is actually rendered on, at its worst.

**Method**

1. Render the real page with the real glass, in the target engine, at the target device pixel ratio. Effects differ by engine ([browser-support.md](browser-support.md)), so measure each tier you ship.
2. Hide the text (set its color to transparent) without changing layout, so the sample contains only what the text sits on: the composited glass, tint, rim and backdrop.
3. Capture the region under each text box, inset by one or two pixels to avoid antialiased borders.
4. Convert each pixel to relative luminance. For each sRGB channel c in 0..1, linearize: `c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ^ 2.4`; then `L = 0.2126 R + 0.7152 G + 0.0722 B`. (Current WCAG 2.1 and 2.2 text uses 0.04045; versions before May 2021 printed 0.03928, which makes no difference at 8 bits. https://www.w3.org/TR/WCAG22/, checked 2026-11-05.)
5. Compute the contrast of the text color against every pixel: `(L_lighter + 0.05) / (L_darker + 0.05)`. Keep the minimum. Optionally also report the 1st percentile to spot a single stray pixel, but pass or fail on the minimum.
6. Repeat across backdrop states: every scroll position where the surface can sit over different content, every media frame you can sample (or the brightest and darkest frames), light and dark appearance, hover and pressed states.
7. Pass when the minimum is at least 4.5:1 (3:1 for large text). For component boundaries and focus indicators, sample the ring just outside the glass edge and require 3:1.

The bundled `scripts/glass_contrast.mjs` (optional Playwright dependency, Chromium only) automates steps 2 to 5 for one URL and scroll position; run it again per backdrop state. Point it at the text, never at a whole container: `--text-selector` measures each matched text element over its own box with its own computed color, hides the text during capture, and reports every element and the worst. Run it from your project directory by path, with the plugin root two directories above the skill's base directory:

```sh
node <plugin-root>/scripts/glass_contrast.mjs --url http://localhost:5173/ --selector 'nav.site' --text-selector 'nav.site a, nav.site span'
```

If Playwright is missing, the script exits with code 2 and explains how to point `PLAYWRIGHT_MODULE` at a scratch install; do not add Playwright to the project without asking. The pure luminance and contrast functions live in `scripts/contrast-math.mjs` and work on any pixel buffer.

**Shortcuts that give wrong answers**

- Measuring the text against the glass tint color alone ignores the backdrop.
- Measuring one screenshot certifies one scroll position.
- simple-liquid-glass `autoTextColor` picks light or dark text from the nearest opaque ancestor's background color with a luminance threshold of 0.5 (simple-liquid-glass `src/cssColor.ts`, `src/core/useTextColor.ts`). It is a light or dark switch, not a contrast check, and it does not look at the refracted image.
- liquid-glass-react forces white text with a dark text shadow and relies on a manual `overLight` flag (liquid-glass-react `src/index.tsx`).

**When the minimum fails**, fix in this order: switch clear to regular; add or strengthen a dimming layer (Apple suggests 35% dark under clear glass over bright content, HIG Materials, https://developer.apple.com/design/human-interface-guidelines/materials, checked 2026-11-05); raise text weight or size; add a halo (section 3); move the surface so it does not cross the brightest content; use a solid surface.

## 3. Text treatments on glass

| Treatment | Effect | Notes |
| --- | --- | --- |
| Regular (frosted) variant | blur averages the backdrop, so the contrast range narrows | first choice for any text-heavy surface (HIG Materials) |
| Dimming layer or scrim | a uniform dark (or light) layer under the glass shifts the whole backdrop range | 35% dark under clear glass on bright content (HIG Materials); liquidGL demos use dark tints of 0.3 to 0.6 alpha behind text over media (liquidGL `demos/multiple-lenses.html`, `demos/tinted-glass.html`) |
| Vibrancy colors (Apple) | label, fill and separator colors designed to sit on materials | avoid `quaternaryLabel` on thin and ultraThin materials: "contrast is too low" (HIG Materials) |
| Halo or wide outline | a dark or light band around glyphs | WCAG treats a sufficiently wide outline as the text's background, so contrast is measured against the halo (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, checked 2026-11-05). A soft blurry shadow is not a reliable halo; measure it |
| `mix-blend-mode: difference` | text inverts against the backdrop | suggested by liquidGL for legibility (liquidGL `README.md`). Contrast is unpredictable over mid-grey backdrops; test before using (inference) |
| Weight and size | thicker strokes resist backdrop noise | prefer medium or semibold labels on glass |
| Padding past the rim | keeps glyphs out of the refractive band | glasshq bends a 20 px band (glasshq `src/gpu/maps.wgsl`) |

## 4. Reduced transparency

| Signal | Chrome | Firefox | Safari | Source (checked 2026-11-05) |
| --- | --- | --- | --- | --- |
| `prefers-reduced-transparency` | 118 (BCD) or 119 (web-features) | 113 behind the pref `layout.css.prefers-reduced-transparency.enabled`; enabling bug 1822176 NEW | not supported; WebKit bug 175497 NEW, privacy concerns cited | https://web-platform-dx.github.io/web-features-explorer/features/prefers-reduced-transparency ; https://bugzilla.mozilla.org/show_bug.cgi?id=1822176 ; https://bugs.webkit.org/show_bug.cgi?id=175497 |
| Apple Reduce Transparency (native) | | | SwiftUI `\.accessibilityReduceTransparency`, UIKit `UIAccessibility.isReduceTransparencyEnabled` | https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency |

Safari cannot see the macOS or iOS Reduce Transparency setting from CSS. A web glass UI on Apple devices therefore needs an in-app control ("Solid surfaces") as well as the media query.

```css
/* Tier 0: the opaque fallback every glass surface must have. */
:root {
  --glass-solid: Canvas;          /* same token set as the glass-web and glass-accessibility skills */
  --glass-solid-ink: CanvasText;
  --glass-solid-line: color-mix(in srgb, CanvasText 30%, transparent);
}

@media (prefers-reduced-transparency: reduce) {
  .glass {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    filter: none;                    /* drop SVG refraction too */
    background: var(--glass-solid);
    color: var(--glass-solid-ink);
    border: 1px solid var(--glass-solid-line);
  }
}

/* Same result from an in-app toggle, for Safari. The setting is the attribute
   data-glass-surfaces="solid" on <html>; the bundled engine honors it live. */
:root[data-glass-surfaces="solid"] .glass {
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  filter: none;
  background: var(--glass-solid);
  color: var(--glass-solid-ink);
  border: 1px solid var(--glass-solid-line);
}
```

`Canvas` and `CanvasText` are CSS system colors that follow the page's color scheme; define the tokens once on `:root` (never on `.glass`, which would override the project's tokens) and map them to your own opaque design tokens. `color-mix()` needs Chrome 111, Firefox 113, Safari 16.2 (https://github.com/mdn/browser-compat-data/blob/main/css/types/color.json, checked 2026-11-05).

For JavaScript renderers (WebGL, WebGPU), listen for changes and tear the effect down rather than drawing a transparent canvas:

```js
const solid = matchMedia('(prefers-reduced-transparency: reduce)');
const root = document.documentElement;
const userPrefersSolid = () => root.getAttribute('data-glass-surfaces') === 'solid';
const apply = () => glass.setMode(solid.matches || userPrefersSolid() ? 'solid' : 'glass');
solid.addEventListener('change', apply);
new MutationObserver(apply).observe(root, { attributes: true, attributeFilter: ['data-glass-surfaces'] });
apply();
```

The bundled engine already does this: `createGlass()` watches `data-glass-surfaces` on `<html>` and switches every instance to the solid tier while it is set ([glass-lab README](../examples/glass-lab/README.md)).

What the libraries do: glasshq disables its progressive blur under `prefers-reduced-transparency: reduce` or `forced-colors: active`, and under forced colors it restyles slider and switch parts with system colors; the glass material itself has no reduced-transparency path (glasshq `src/dom/progressive.ts`, `src/dom/index.ts`, `src/styles.css`). simple-liquid-glass, liquidGL, ybouane and liquid-glass-react have no handling (no `prefers-reduced-transparency` query in their library source). Any of them needs a wrapper that swaps to the solid tier.

## 5. Increased contrast

- Web: `prefers-contrast: more` is supported in Chrome 96, Firefox 101 and Safari 14.1 (https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json, checked 2026-11-05). Because Safari lacks the transparency query, treat `prefers-contrast: more` as a proxy and go solid or near-solid under it.
- Apple: system glass adapts to Increase Contrast. Apple asks for custom control colors with an increased contrast variant for both light and dark (https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass, checked 2026-11-05). SwiftUI exposes `\.colorSchemeContrast`.

```css
@media (prefers-contrast: more) {
  .glass {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    filter: none;
    background: var(--glass-solid);
    color: var(--glass-solid-ink);
    border: 2px solid CanvasText;
  }
}
```

## 6. Forced colors

Windows High Contrast and similar modes replace author colors with a small system palette. `forced-colors` is supported in Chrome 89, Firefox 89 and Safari 16, where it always matches `none` because Apple platforms have no forced-colors mode (https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json, checked 2026-11-05). Design glass to fail to a plain bordered surface:

```css
@media (forced-colors: active) {
  .glass {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    filter: none;
    background: Canvas;
    color: CanvasText;
    border: 1px solid CanvasText;        /* rims made of shadows or gradients disappear */
  }
  .glass-button {
    background: ButtonFace;
    color: ButtonText;
    border: 1px solid ButtonText;
  }
  .glass-button[aria-pressed="true"],
  .glass-tab[aria-selected="true"] {
    background: Highlight;
    color: HighlightText;
  }
  .glass canvas,
  .glass .glass-layer { display: none; }   /* decorative WebGL output and overlays */
}
```

Inference: shadows and background images used as rims are typically dropped or recolored in forced colors, so a glass edge drawn only with `box-shadow` or gradients vanishes. Always supply a real `border` in this mode. glasshq ships forced-colors rules only for its slider and switch tracks and thumbs (glasshq `src/styles.css`).

## 7. Reduced motion

Elastic stretch, pointer lean, morph travel and looping highlights are motion. Under `prefers-reduced-motion: reduce` (Chrome 74, Firefox 63, Safari 10.1, https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json, checked 2026-11-05):

- Remove stretch, lean and travel. Keep state changes visible with opacity, brightness or a border.
- Replace morphs with an in-place appearance and a short content fade. glasshq does exactly this: system reduced motion always overrides `motion="full"`, removes stretching and travel, and popups "materialize in place" (glasshq `src/dom/interaction.ts`, `src/dom/morph.ts`, `README.md`).
- Stop continuous effects (animated turbulence, specular sweeps). simple-liquid-glass stops its turbulence, pointer spring and ripples and reacts to live changes (simple-liquid-glass `src/index.tsx`, `src/interactive/index.tsx`). liquidGL, ybouane and liquid-glass-react have no reduced-motion handling.
- On Apple platforms Reduce Motion "can remove or modify certain effects" of system glass (Adopting page above); check custom animations with `\.accessibilityReduceMotion`.

Details and code in [motion.md](motion.md#7-reduced-motion-alternatives).

## 8. Focus visibility

**Never remove the focus outline from glass controls.** glasshq replaces it on buttons and tabs with an 8% `currentColor` background tint and sets `outline: none` on slider thumbs and switches (glasshq `src/styles.css`). An 8% tint over a changing backdrop will not reliably reach 3:1 and is easy to miss. Do not copy this pattern.

A two-tone outline stays visible over any backdrop because one of the two rings contrasts with it:

```css
.glass-button:focus-visible {
  outline: 2px solid #ffffff;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px #111111;   /* dark ring outside the light one */
}

@media (forced-colors: active) {
  .glass-button:focus-visible {
    outline: 2px solid Highlight;
    box-shadow: none;
  }
}
```

Check that the focus ring is not clipped: glass layers often use `overflow: hidden` and `clip-path`, which cut off an outline drawn outside the box. Draw the outline on an unclipped wrapper, or use a negative `outline-offset` inside the shape when the clip cannot change.

**Focus not obscured (2.4.11).** Floating glass bars cover content that scrolls beneath them. Reserve the space so focused elements scroll clear:

```css
html { scroll-padding-top: 72px; scroll-padding-bottom: 96px; }  /* heights of your floating bars */
```

glasshq's scroll-content example uses `scroll-padding` and a focusable `role="region"` with an `aria-label` for the same purpose (glasshq `README.md`).

## 9. Semantics and input

- **Use real controls.** A glass button is a `<button>` (or `<a href>` for navigation) with the glass applied as styling. liquid-glass-react attaches `onClick` to a plain `div` with no role, tab stop or key handling (liquid-glass-react `src/index.tsx`); ybouane's `button: true` adds only a pointer cursor and shader states (ybouane `src/LiquidGlass.ts`). Neither is keyboard operable. glasshq wraps Base UI primitives (Button, Toolbar, Tabs, Menu, Slider, Switch), which keeps roles, keyboard navigation and focus restoration (glasshq `README.md`, `src/react/*.tsx`).
- **Do not block pointer events.** liquidGL sets `pointer-events: none` on non-draggable lens elements, and its demos override it to make controls clickable (liquidGL `scripts/liquidGL.js`, `demos/ai-search.html`).
- **Hide decorative layers.** Canvases, SVG filter hosts, rim overlays and probe images get `aria-hidden="true"`; glasshq and simple-liquid-glass do this (glasshq `src/dom/index.ts`, `src/dom/lens-layers.ts`; simple-liquid-glass `src/index.tsx`). liquidGL does not mark its canvas, shadow and mirror elements (liquidGL `scripts/liquidGL.js`).
- **Keep content in the accessibility tree while the effect loads.** glasshq hides surfaces with `visibility: hidden` until their clip path exists, which also removes them from the accessibility tree until script runs (glasshq `src/styles.css`). simple-liquid-glass hides with `opacity` so content and live regions stay available (simple-liquid-glass `src/index.tsx`). Prefer the opacity approach.
- **Do not break text selection.** ybouane sets `user-select: none` on its whole root (ybouane `src/LiquidGlass.ts`).
- **Pointer, touch and keyboard parity.** Drag-to-move glass needs a keyboard alternative; mouse-only listeners (liquid-glass-react) exclude touch and pen.
- **Icon-only glass buttons** need accessible names (`aria-label`, or a visually hidden label). Apple's adoption guide asks for accessibility labels on toolbar items (Adopting page above).

## 10. Apple platform settings

| Setting | System glass behavior | What custom glass must do | API |
| --- | --- | --- | --- |
| Reduce Transparency | adapts automatically (HIG Materials) | test custom `glassEffect` surfaces; inference: they use the system material and likely adapt, but anything you draw yourself (overlays, custom blurs) must switch to opaque | `\.accessibilityReduceTransparency`, `UIAccessibility.isReduceTransparencyEnabled` |
| Increase Contrast | adapts automatically | supply increased contrast color variants | `\.colorSchemeContrast` |
| Reduce Motion | may remove or modify effects | gate custom springs and morphs | `\.accessibilityReduceMotion` |
| Liquid Glass: Clear or Tinted (26.1+) | Tinted is more opaque with more contrast | verify text on custom surfaces under both | none found |

SwiftUI environment values are available from iOS 13, macOS 10.15 and visionOS 1 (https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency, checked 2026-11-05). The 26.1 setting is reported by secondary sources (https://www.macrumors.com/2025/10/20/ios-26-1-liquid-glass-toggle/, checked 2026-11-05, Medium).

```swift
@available(iOS 26.0, macOS 26.0, tvOS 26.0, watchOS 26.0, *)   // glassEffect and Glass are 26.0 only
struct FloatingPanel<Content: View>: View {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @ViewBuilder var content: Content

    var body: some View {
        content
            .padding()
            .background(reduceTransparency ? AnyShapeStyle(.background) : AnyShapeStyle(.clear),
                        in: .rect(cornerRadius: 20))
            .glassEffect(reduceTransparency ? .identity : .regular, in: .rect(cornerRadius: 20))
    }
}
```

Use a branch like this only if testing shows the system adaptation is not enough for your surface; `Glass.identity` keeps the view tree stable while turning the glass off. If the app supports OS versions before 26, call the panel inside `if #available(iOS 26.0, macOS 26.0, tvOS 26.0, watchOS 26.0, *)` and use `.background(.regularMaterial, in: .rect(cornerRadius: 20))` in the `else` branch.

## 11. Lessons from published critique

The Nielsen Norman Group review of iOS 26 (Raluca Budiu, "Liquid Glass Is Cracked, and Usability Suffers in iOS 26", Oct 10, 2025, https://www.nngroup.com/articles/liquid-glass/, checked 2026-11-05) reports:

- "the contrast between the text and the background is often too low";
- overlapping text, such as search UI over message previews;
- floating controls that blend into content;
- context-dependent controls that are "harder to learn and less predictable";
- "Motion for motion's sake is not usability."

Apple later added a Tinted option (26.1), a Lock Screen clock transparency slider (26.2) and, per reports, a wider transparency control in iOS 27. Our interpretation: legibility is a recognized problem with the material, so any custom glass should ship with at least the same escape hatches.

## 12. Test procedure

Run on each engine tier you ship (Chromium refraction, WebKit and Gecko frosted or WebGL, solid fallback) and on each native platform.

1. **Inventory.** List every glass surface, its variant, the text and controls on it, and the content it can float over.
2. **Contrast sweep.** For each text element, run the worst-case method (section 2) across scroll positions, media frames, light and dark, hover and pressed. Record the minimum ratio. Pass: 4.5:1 (3:1 large).
3. **Boundaries and states.** Sample the ring around each control and each state indicator (selected tab, toggle). Pass: 3:1.
4. **Keyboard.** Tab through every control. Each is reachable, operable with Enter or Space (and arrows where the pattern expects them), and shows a focus ring with 3:1 contrast that is not clipped and not hidden under a floating bar.
5. **Screen reader.** VoiceOver (macOS, iOS) and NVDA or Narrator (Windows): every control has a role and name; decorative canvases and overlays are silent; content is announced before and after the effect loads.
6. **Reduced transparency.** Chrome: DevTools Rendering panel, emulate `prefers-reduced-transparency: reduce`. Safari: use the in-app solid toggle. Native: turn on Reduce Transparency. Pass: every glass surface is opaque, with borders, and text passes contrast trivially.
7. **Increased contrast.** Emulate `prefers-contrast: more`; native Increase Contrast. Pass: solid or near-solid surfaces, stronger borders.
8. **Forced colors.** Windows High Contrast, or Chrome DevTools forced-colors emulation. Pass: surfaces use system colors, every control has a visible border, selected states use `Highlight`.
9. **Reduced motion.** Emulate `prefers-reduced-motion: reduce`; native Reduce Motion. Pass: no stretch, lean, travel or looping effect; morphs become fades; state changes remain visible.
10. **Zoom and text size.** 200% browser zoom and large Dynamic Type: text stays outside the refractive rim and does not clip.
11. **Apple Tinted and Clear.** On 26.1+, check both settings.
12. **Record.** Store minimum ratios, screenshots per mode, and failures with the fix applied. Re-run after any change to tint, blur, variant or layout.

## Related references

- [design-principles.md](design-principles.md) for legibility rules and anti-patterns
- [motion.md](motion.md) for reduced-motion alternatives
- [web-techniques.md](web-techniques.md) for the solid and frosted tiers
- [gotchas.md](gotchas.md#accessibility) for accessibility failure modes found in the libraries
