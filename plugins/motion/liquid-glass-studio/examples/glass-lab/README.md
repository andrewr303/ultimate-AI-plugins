# Glass Lab

A self-contained page for tuning liquid glass style refraction, plus the engine it runs on. Everything here is original code with no dependencies. The page makes no network requests and loads no external fonts or images.

- `liquid-glass.js`: the engine. It is an ES module. The math exports are safe to import in Node; the browser API is `capabilities()` and `createGlass()`.
- `liquid-glass.d.ts`: TypeScript declarations for every export (see [TypeScript](#typescript)).
- `index.html`: the lab. It shows a busy, colorful backdrop under a toolbar, a card, a pill button and a switch with a glass knob. A control panel covers every engine parameter.
- Tests: `../../tests/engine.test.mjs`. Run them with `node --test tests/engine.test.mjs` from the plugin root.

Not affiliated with Apple. "Liquid Glass" is Apple's name for its material; this lab builds a liquid glass style effect for the web.

## Run it

Browsers block ES module imports from `file://` pages, so serve the folder over http. `<plugin-root>` is the folder that holds this plugin's `scripts/` folder: two directories above the skill's base directory that Claude Code prints as "Base directory for this skill" when a skill loads, or the folder a filesystem search for `scripts/glass_probe.mjs` finds.

```sh
cd <plugin-root>/examples/glass-lab
python3 -m http.server 8000 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8000/`. Stop the server with Ctrl+C.

Query parameters preset any control, which is useful for screenshots: `?tier=frost`, `?profile=lip`, `?chromaticAberration=0.3`, `?foldGuard=0`, `?offset=200`, `?surfaces=solid`.

## What each tier means

| Tier | What renders | When the engine picks it |
| --- | --- | --- |
| `refract` | SVG displacement through `backdrop-filter: url(#id)`, plus blur, saturation and a rim light | Chromium with `backdrop-filter` support and no user preference against transparency |
| `frost` | CSS `backdrop-filter: blur() saturate()` from the engine's base stylesheet, with a tint | Any other engine with `backdrop-filter`, or an element under 2 CSS px, or a map that failed to build |
| `solid` | An opaque surface | Forced colors, the page's solid surfaces setting, reduced transparency, more contrast, or no `backdrop-filter` |

The tier override in the panel can lower the tier but never raise it. A user who asked for reduced transparency gets `solid` even if the page asks for `refract`.

Why the engine checks the browser engine: `@supports` reports that `backdrop-filter` exists, but it cannot tell whether a `url()` backdrop filter actually renders. That works in Chromium. WebKit bug 245510 is still open (https://bugs.webkit.org/show_bug.cgi?id=245510, checked 2026-11-05), and Firefox bug 1961378 is still open (https://bugzilla.mozilla.org/show_bug.cgi?id=1961378, checked 2026-11-05). User-agent checks can be wrong when a UA is spoofed, frozen or new, so an unknown engine falls back to `frost`, which is safe wherever `backdrop-filter` exists.

Safari does not expose `prefers-reduced-transparency` (https://web-platform-dx.github.io/web-features-explorer/features/prefers-reduced-transparency, checked 2026-11-05). The engine treats `prefers-contrast: more` as a signal for `solid` too, and a production page should also offer its own "solid surfaces" setting.

### Solid surfaces setting

The page-level setting has one name: the attribute `data-glass-surfaces="solid"` on the `<html>` element (the export `SOLID_SURFACES_ATTRIBUTE` holds the attribute name). `createGlass()` watches that attribute with a `MutationObserver` and switches every instance to `solid` the moment it appears, with the reason "the user turned on solid surfaces". Removing it lets each instance pick its tier again. Only forced colors outrank it. CSS that does not go through the engine follows the same setting with `:root[data-glass-surfaces="solid"]` selectors:

```css
:root[data-glass-surfaces="solid"] .site-header { background: #eef0f5; backdrop-filter: none; }
```

Store the user's choice wherever the app keeps settings and set the attribute before the first paint. The lab's "Solid surfaces" checkbox sets and clears it.

### How the frost and solid tiers are styled

The engine writes `backdrop-filter` inline only in the `refract` tier, as `url(#id)`, because each instance needs its own filter id. For the other tiers it sets `data-glass-tier` and two custom properties on the element, `--lg-frost-blur` (from `frostBlur`) and `--lg-saturation` (from `saturation`), and injects one stylesheet, `<style id="lgs-base-styles">` (the export `BASE_STYLES`):

```css
:where([data-glass-tier="frost"]) {
  -webkit-backdrop-filter: blur(var(--lg-frost-blur, 14px)) saturate(var(--lg-saturation, 1.5));
  backdrop-filter: blur(var(--lg-frost-blur, 14px)) saturate(var(--lg-saturation, 1.5));
}
:where([data-glass-tier="solid"]) {
  -webkit-backdrop-filter: none;
  backdrop-filter: none;
}
```

`:where()` has zero specificity, so any author rule wins. To tune frost in CSS, write your own rule for `[data-glass-tier="frost"]`; to tune it from script, pass `frostBlur` and `saturation`. If an author rule sets `backdrop-filter` on the glass element for every tier, scope it to a tier, or it also overrides the `solid` default. Under a Content Security Policy that blocks inline styles, ship the same rules yourself in an element with the id `lgs-base-styles` (a `<style>` with a nonce, or a `<link>`); the engine then injects nothing. The engine removes the sheet it injected when the last instance is destroyed.

## Controls

| Control | Engine option | Effect |
| --- | --- | --- |
| Bezel profile | `profile` | Height function across the bezel: `convexCircle`, `convexSquircle`, `concave`, `lip` |
| Corner shape | `shape` | `rounded` matches CSS `border-radius`; `squircle` only changes the map, so pair it with a matching clip |
| Bezel width | `bezelWidth` | Width of the refracting band in CSS px; clamped to half the short side |
| Glass thickness | `thickness` | Height of the glass at the plateau; more height bends more |
| Index of refraction | `ior` | 1 means no bending; 1.5 is typical window glass |
| Strength | `strength` | Multiplier on the physical offset |
| Chromatic aberration | `chromaticAberration` | Splits the red, green and blue passes; blue bends most |
| Blur (refract tier) | `blur` | Frost applied before refraction, inside the SVG filter |
| Blur (frost tier) | `frostBlur` | CSS blur for the `frost` tier |
| Saturation | `saturation` | Saturation of the backdrop seen through the glass |
| Rim light, angle, width | `specularIntensity`, `lightAngle`, `rimWidth` | The specular rim map |
| Tint opacity | CSS `--tint` | White tint over the glass; the main legibility control |
| Backdrop offset | CSS `--offset` | Slides the backdrop so content passes under the rim |
| Fold guard | `foldGuard` | Keeps the rim unfolded; turn off for the mirrored-rim look |
| Pointer elasticity | `elasticity` | Small pull toward the pointer; disabled under reduced motion |
| Solid surfaces | page attribute `data-glass-surfaces` | Sets `data-glass-surfaces="solid"` on `<html>`; every surface switches to `solid` live |

## How the engine works

1. **Profile.** A height function `h(t)` on `t` from 0 at the outer edge to 1 where the bezel meets the flat interior. All four profiles have zero slope at `t = 1`, so there is no seam.
2. **Refraction.** For each `t`, the engine takes the surface normal from the height derivative and refracts a straight-down ray with the vector form of Snell's law. The offset is the ray's sideways travel down to the backdrop. This is an approximation: one refracting surface, no Fresnel loss, and corners handled by following the distance field. The comments in `liquid-glass.js` compare it with the arc falloff in `glasshq-liquid-glass src/gpu/maps.wgsl`, the `(1 - 1/ior)` gradient scaling in `ybouane-liquidglass src/shaders.ts`, and the dome slope in `simple-liquid-glass src/vendor/samasante/displacement.ts`.
3. **Map.** `displacementField()` walks a rounded-rectangle distance field at `devicePixelRatio`. Each pixel gets the offset along the inward normal. The field uses a corner radius of at least the bezel width, so the normal turns smoothly around corners instead of tearing across the diagonal. The outer edge fades to neutral over a fixed `fadeBand` of 1 CSS px (never under one device pixel, never over half the bezel). A band that widened with the rim offset was measured and rejected: at 360 x 200, bezel 28, thickness 40 it cut the peak offset from 6.9 to 4.7 px for `convexSquircle` and from 3.9 to 2.6 px for `lip`.
4. **Fold guard.** The warp must stay locally one-to-one, which means the Jacobian determinant stays positive. The engine measures the minimum determinant and lowers the amplitude until it reaches 0.2. `simple-liquid-glass src/core/displacementField.ts` checks the same criterion. The readout shows the reduction as "Fold guard: amplitude xN".
5. **Encoding.** Red holds the x offset and green the y offset, stored around a neutral value of 128. Because 128/255 is not 0.5, the filter subtracts `1/510` from both channels before displacing. The filter scale is `maxDisplacement * 255 / 127`, so byte 255 means exactly the maximum offset.
6. **Filter.** `buildFilterMarkup()` emits an optional `feGaussianBlur` (the `blur` option) and `feColorMatrix` saturate step, then `feImage` for the map, an `feColorMatrix` for the neutral correction, and `feDisplacementMap` with `xChannelSelector="R"` and `yChannelSelector="G"`. With chromatic aberration it runs three passes, keeps one channel from each with `feColorMatrix`, adds them with `feComposite operator="arithmetic"`, and takes alpha from the green pass with `feComposite operator="in"`. A specular `feImage` is screen-blended on top with `feBlend`. The filter uses `color-interpolation-filters="sRGB"` so map bytes are not converted to linear light. `tests/docs_drift.test.mjs` fails if this list and the emitted markup disagree.
7. **Browser wiring.** `createGlass()` caches maps by size and options (24 entries; a custom `profile` function gets its own id in the cache key, so two different functions never share a map). It rebuilds on `ResizeObserver` callbacks coalesced into one animation frame, on a pixel ratio change (a `(resolution: Ndppx)` query that it re-arms after each change, so zoom or a move to another display rebuilds the map at the new ratio), on live changes to the four media queries, and on the solid surfaces attribute. It waits for the map images to decode before swapping in a new versioned filter id, and removes everything in `destroy()`. It never changes `outline` or focus styles.

`info` (the `onRender` argument and the handle's `info`) reports `width` and `height` in CSS px and `pixelRatio` as used. In the `refract` tier it adds `mapWidth` and `mapHeight` in map pixels (CSS px times the pixel ratio), plus the map fields such as `maxDisplacement`, `filterScale`, `attenuation`, `fadeBand`, `cacheHit` and `buildMs`. Every outcome other than a working refract filter (a lower tier, an element under 2 CSS px, a map that failed to build) sets `data-glass-tier`, the handle's `tier`, `info` and the `onRender` call to the same tier, and removes the inline `url()` filter.

## Exports

Every export below is covered by `tests/engine.test.mjs`, and `tests/docs_drift.test.mjs` fails if an export is added without a row here.

| Export | Layer | What it gives you |
| --- | --- | --- |
| `smoothstep(e0, e1, x)`, `smootherstep(t)` | math | The easing curves the profiles and edge fades use |
| `convexCircle`, `convexSquircle`, `concave`, `lip` | math | Height functions `h(t)` on 0 to 1 |
| `PROFILES` | math | The four profiles by name; the `profile` option takes one of these names or a function |
| `refractionProfile({ bezelWidth, thickness, ior, profile, samples, strength })` | math | A `Float64Array` of signed offsets in px across the bezel; positive samples inward |
| `roundedRectSDF(x, y, hw, hh, r, shape)` | math | Signed distance to a centered rounded rectangle, negative inside |
| `NEUTRAL`, `NEUTRAL_BIAS` | math | The neutral byte (128) and the filter correction (128/255 minus 0.5, which is 1/510) |
| `encodeDisplacement(offset, maxDisplacement)`, `decodeDisplacement(byte, maxDisplacement, filterScale)` | math | Byte encoding of one offset and its exact inverse through the corrected filter |
| `displacementField({ width, height, radius, bezelWidth, profile, ior, thickness, strength, pixelRatio, shape, foldHeadroom, minJacobian })` | math | The RGBA map plus `maxDisplacement`, `filterScale`, `attenuation` (fold guard factor) and `minJacobian` |
| `specularField({ width, height, radius, shape, pixelRatio, lightAngle, intensity, rimWidth })` | math | The RGBA rim light map |
| `buildFilterMarkup({ id, mapHref, specularHref, width, height, scale, chromaticAberration, blur, saturation, neutralBias, specularOpacity })` | math | The `<filter>` element as a string |
| `explainTier(input)`, `detectTier(input)` | math | The tier decision with its reason, or the tier alone; `input` takes `reducedTransparency`, `contrastMore`, `forcedColors`, `solidSurfaces`, `supportsBackdrop`, `engine` and `preferred` |
| `detectEngine(navigator)` | math | `chromium`, `webkit`, `gecko` or `unknown` from a navigator-like object |
| `SOLID_SURFACES_ATTRIBUTE` | browser | `data-glass-surfaces`, the attribute on `<html>` that turns on solid surfaces |
| `MEDIA_QUERIES` | browser | The four preference queries the engine listens to |
| `capabilities(window)` | browser | Preferences, `solidSurfaces`, `backdrop-filter` support and engine; safe defaults without a window |
| `findBackdropRoot(element)` | browser | The nearest ancestor that starts a Backdrop Root, with the property that caused it, or `null` |
| `DEFAULTS` | browser | The `createGlass` options and their defaults |
| `BASE_STYLES_ID`, `BASE_STYLES` | browser | The id `lgs-base-styles` and the text of the frost and solid stylesheet the engine injects |
| `createGlass(element, options)` | browser | A handle with `tier`, `info`, `update(options)`, `refresh()` and `destroy()` |
| `clearGlassCache()` | browser | Empties the shared map cache |

## TypeScript

`liquid-glass.d.ts` declares the public API: every export, the `GlassOptions`, `GlassInfo` and `GlassHandle` interfaces, and the option and result types of the math functions. To use the engine in a TypeScript project, copy `liquid-glass.js` and `liquid-glass.d.ts` side by side and keep the attribution header at the top of both files. `tests/docs_drift.test.mjs` fails if the declared exports differ from the module's, or if `GlassOptions` and `DEFAULTS` name different options.

## Pitfalls the engine warns about or avoids

- **Backdrop Root.** If an ancestor has `opacity` below 1, a `filter`, a `mask`, `clip-path`, `backdrop-filter`, `mix-blend-mode` or a matching `will-change`, the glass only sees content inside that ancestor (Filter Effects Level 2, https://drafts.csswg.org/filter-effects-2/, checked 2026-11-05). `createGlass()` logs a console warning when it finds one. The check runs on the instance's first render, so it also catches the most common case, glass inside glass: the outer element only gets its `backdrop-filter` when it renders, so the engine also warns whenever an ancestor is itself a `createGlass()` element. The lab's switch knob sits inside the glass switch row on purpose: it follows the nesting exception in [design-principles.md](../../references/design-principles.md) (smaller bezel and thickness, `blur` and `frostBlur` of 0), so its options pass `warn: false`.
- **Reading y from the blue channel.** `liquid-glass-react src/index.tsx` sets `yChannelSelector="B"`, and one of its baked maps has blue at 0 everywhere. That produces a constant vertical shift instead of refraction. This engine always reads y from green, and the tests check every pass.
- **Undisplayed SVG.** The filter host is a zero-size, absolutely positioned `<svg>`, not `display: none`.
- **Lossy maps.** Maps are PNG data URLs, never JPEG.

## Legibility

The "Worst-case contrast" note composites the current tint over every backdrop color and reports the lowest WCAG ratio for the card's body text against the 4.5:1 minimum (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, checked 2026-11-05). It is an estimate. It treats each color as a flat region and ignores refraction and blur, which can move a darker or brighter pixel under a glyph. Measuring the real rendered pixels behind the text is the stronger check, and treating the worst-case backdrop as the test case is an engineering inference, not a W3C rule.

`scripts/glass_contrast.mjs` does that measurement. It loads a page in headless Chromium through Playwright (an optional dependency it never installs), hides the text, screenshots what sits behind it, and reports the minimum, 5th percentile and median contrast of the text color against every pixel. Measure text, never a whole container: the card also holds a dark button with white text, so `--text-selector` measures each text element over its own box with its own computed color and reports each one and the worst. With the lab served as above, run it from your project directory (a relative `--screenshot` path resolves against the current directory, and missing folders are created):

```sh
node <plugin-root>/scripts/glass_contrast.mjs --url http://127.0.0.1:8000/ --selector '#card' --text-selector '#card .meta, #card h2, #card p' --require 4.5
node <plugin-root>/scripts/glass_contrast.mjs --url 'http://127.0.0.1:8000/?offset=200' --selector '#card' --text-selector '#card .meta, #card h2, #card p' --json --screenshot glass-review/card.png
```

`--require 4.5` (or `3`, or `auto`, which uses 3:1 for large text and 4.5:1 otherwise) makes the exit code 1 when any measured element falls short; exit code 2 means it could not run. When Playwright is missing it says so and does not add it to your project: install it in a scratch directory (`npm i playwright --prefix <scratch>`) and set `PLAYWRIGHT_MODULE=<scratch>/node_modules/playwright`, or install it globally, after asking. Other options: `--text-color`, `--dpr`, `--viewport`, `--color-scheme light|dark`, `--wait`, `--timeout`. One run measures one scroll position and one animation frame, so repeat it with the backdrop moved (`?offset=`) to find the worst case. Run `node <plugin-root>/scripts/glass_contrast.mjs --help` for the full list.

With the defaults (tint 0.6, blur 3 px) the estimate is about 4.97:1 for refract, 6.2:1 for frost and 11.4:1 for solid.

## Accessibility in the lab

- Every control is a native `input` or `select` with a visible label, reachable by Tab.
- Focus shows as a dark outline with a white inner ring, which stays visible over any backdrop. The engine never removes outlines.
- `prefers-reduced-motion: reduce` disables transitions and pointer elasticity.
- `forced-colors: active` switches every glass surface to system colors.
- The tier line is a `role="status"` region; the parameter readout is not live, so dragging a slider does not flood a screen reader.

## Verified in Chromium (2026-11-05, Playwright, deviceScaleFactor 1 and 2)

- No console errors or warnings at either pixel ratio. Every request went to the local server or a `data:` URL; nothing external.
- The card readout showed "360 x 203 CSS px" at both ratios, and "360 x 203 map px at 1x" and "720 x 406 map px at 2x", matching the card's `offsetWidth` and `offsetHeight`.
- With tint 0, blur 0 and no rim light, strength 1 against strength 0 changed only pixels within the 28 px bezel (5990 pixels at 1x, 21602 device pixels at 2x) and none deeper inside.
- Setting `data-glass-surfaces="solid"` on `<html>` from the console switched all five surfaces to `solid` (computed `backdrop-filter: none`, reason "the user turned on solid surfaces") and ticked the lab checkbox; removing it brought all five back to `refract`.
- The `frost` override gave computed `backdrop-filter: blur(14px) saturate(1.5)` from the injected stylesheet, with no inline `backdrop-filter`, and `blur(0px)` on the nested knob.
- Earlier run (deviceScaleFactor 1): a neutral map of all 128 with scale 2040 moved a sharp edge by 4 px without the neutral correction and by 0 px with it, and emulated `prefers-contrast: more` with reduced motion produced `solid`.

Safari and Firefox were not tested here. On those engines the lab should show `frost`, based on the tier rules above.

## Check it in real engines

`scripts/glass_probe.mjs` renders instead of guessing. It serves the plugin folder locally, opens a fixture page in each installed Playwright engine, screenshots a pane with a `url()` backdrop filter, a pane with a blur backdrop filter, a control pane and a real `createGlass()` card, and compares the pixels. Its report puts the tier each engine earned by rendering next to the tier the `createGlass()` card picked from its user-agent check, and flags an engine where `CSS.supports` accepts a `url()` backdrop filter that did not render.

```sh
node <plugin-root>/scripts/glass_probe.mjs
node <plugin-root>/scripts/glass_probe.mjs --browsers chromium,firefox,webkit --out glass-review/probe --json
```

Run it from your project directory; `--out` resolves against the current directory and is created when missing. A missing Playwright package or browser build is reported as unavailable, not installed. Add `--strict` in CI so an unavailable engine fails the job, and `--url` with `--selector` to capture one of your own pages in every engine. Why this matters: [web-techniques.md, Render-level detection](../../references/web-techniques.md#render-level-detection).
