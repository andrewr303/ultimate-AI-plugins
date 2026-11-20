# Source notes: simple-liquid-glass

Condensed study notes for one of the five libraries this plugin learned from. Nothing here is vendored; formulas are paraphrased or quoted briefly with attribution. Citations use `<repo-relative path>:line` in the upstream layout (repository `github.com/lucaperullo/simple-liquid-glass`).

Observed in the supplied archive on 2026-11-05. The archive is a snapshot, not necessarily the latest release; this project releases often. Recheck upstream before quoting a version or behavior.

## 1. Identity

| Field | Value | Evidence |
| --- | --- | --- |
| Package | `simple-liquid-glass` | `package.json:2` |
| Version in archive | `5.7.0` | `package.json:3`, `CHANGELOG.md:1` |
| License | MIT, "Copyright (c) 2025 lucaperullo" | `LICENSE:1-3` |
| Peer deps | React and ReactDOM 16.8 to 19, both optional | `package.json:185-195` |
| Entry points | `.`, `./interactive`, `./mirror` (deprecated), `./web-component`, `./webgl`, `./backdrop`, `./experimental`, `./engine` | `package.json` (exports) |
| Vendored code | samasante lens generator, @ybouane/liquidglass 1.0.3 WebGL pipeline, html-to-image 1.11.11, liquidGL optics port | `THIRD_PARTY_NOTICES.md` |
| CI | Typecheck, Jest, build, type tests, size-limit, Playwright on Chromium, Firefox and WebKit, React 16.8/17/18/19 matrix | `.github/workflows/ci.yml`, `playwright.config.ts:2-7` |
| Tests | About 202 Jest and Playwright cases, plus real-GPU experiment scripts | `src/__tests__`, `tests/browser`, `package.json` (`test:webgl`) |
| Size limits (Brotli) | core 52.6 KB, interactive 54.7 KB, web component 37.7 KB, engine core 13.6 KB | `package.json:74-125` |

**One-line summary.** One component, three render strategies chosen per engine: SVG `feDisplacementMap` inside `backdrop-filter: url(#id)` on Chromium, WebGL over an explicitly supplied backdrop on Safari, iOS and Firefox (or by opt-in), and a designed frosted CSS fallback (`src/core/renderer.ts:8-18`, `README.md:404-416`).

Maturity caveat: newer modules are written in dense one-line style, so review takes time (for example `src/core/webgl/textureCache.ts`, `src/web-component/index.ts`).

## 2. Strategy selection

- `supportsSvgBackdrop` returns true only for Chromium UA strings, excluding every iOS browser (all WebKit) and Firefox; iPadOS is detected by "Macintosh" plus `maxTouchPoints > 1` (`src/core/renderer.ts:3-13`).
- `wantsWebGL` picks WebGL when the effect is not `off` or `blur` and either SVG backdrops are unsupported or `renderer="webgl"` (`src/core/renderer.ts:16-18`).
- Mobile defaults to CSS unless `mobileFallback="svg"` or `renderer` says otherwise (`src/index.tsx:460-484`).
- On desktop Chromium, 16 or more eligible siblings switch to one shared WebGL scene, and the group returns to SVG below 12 (hysteresis) (`src/core/webgl/crowd.ts:9-17`, `src/index.tsx:393-395`).
- Diagnostics: `data-glass-strategy` and `data-glass-reason` on the root (`src/index.tsx:501-515`, `:658-659`).

DOM per instance: root, optional WebGL holder (`aria-hidden`), glass layer with `backdrop-filter`, gradient border ring, optional brightness veil, then children on top (`src/index.tsx:652-705`).

## 3. Technique pipelines

### A. Chromium SVG lens (default, `refraction="lens"`)

1. Measure with `offsetWidth/offsetHeight` through ResizeObserver, so entrance transforms do not shrink the map (`src/core/useGeometry.ts:26-35`).
2. Resolve lens options from a profile plus clamped overrides (`src/core/nativeOptics.ts:4-61`).
3. Generate a displacement PNG on a 2D canvas, cached by geometry; SVG map size is `clamp(64, ceil(max(w, h) * 0.75), 512)` because Chromium resends map bytes every moving frame (`src/vendor/samasante/displacement.ts:290-592`, `src/core/nativeMapGeometry.ts:1-9`).
4. Build the filter: neutral grey flood under the map, displacement, optional per-channel dispersion, B-channel specular added on top (`src/core/materialFilter.ts:10-41`).
5. Apply `backdrop-filter: saturate(S%) blur(Bpx) url(#id)`; blur runs before refraction (`src/index.tsx:578-581`, `README.md:718`).

Map encoding: R = X offset, G = Y offset (128 neutral), B = specular mask (128 none, 255 full) (`src/vendor/samasante/displacement.ts:7-13`, `:281-282`).

Surface model (paraphrased from `src/vendor/samasante/displacement.ts`):
- Rounded-rect SDF computed for one quadrant and mirrored (`:284-289`, `:427-437`).
- Spherical-cap dome: cap height `curvature * min(halfW, halfH)`, sphere radius `R = (a^2 + h^2) / 2h`, slope normalized so its mean over the half extent is 0.5 (`:161-192`, `:361`).
- Depth feather: displacement times `0.5 * (1 + erf(innerSdf * falloff))`, with erf approximated by `tanh(sqrt(pi) * x)` (`:150-153`, `:470-484`).
- Lip ("bend"): an extra inward push in a band near the rim shaped `6.75 * s^2 * (1 - s)`, peaking at two thirds of the band (`:496-505`).
- Specular sheen: band near the rim with a 16% floor all around, pooling toward a light angle, plus a soft inner glow (`:517-547`).

Dispersion: three displacement passes with scales boosted 22% (red), 11% (green), 0% (blue) and recombined additively (`src/core/materialFilter.ts:23-36`, `DISPERSION_SPREAD` at `src/vendor/samasante/displacement.ts:145-148`). Disabled at `quality="low"` (`src/core/DisplacementFilter.tsx:23`).

Scale in CSS px: `clamp(scale, -320, 320) / 160 * strength * norm`, where `norm` is 500 for the `player` profile or the box diagonal over sqrt 2 (`src/index.tsx:432-436`). With defaults (`scale=160`, player strength 0.16) that is 80 px (`README.md:712-716`).

Filter region is `userSpaceOnUse`, padded by half the scale (with dispersion), three times the blur, plus 2 px (`src/core/materialFilter.ts:43-47`).

Surface layers on top: inset rim shadows, a 1 px gradient ring through `mask-composite: exclude`, an optional veil, and a tint that must be semi-transparent or it falls back with a console warning (`src/index.tsx:445-456`, `:612`, `:622-634`).

### B. Chromium SVG classic map (4.x look)

Legacy props select it (`src/index.tsx:344-345`). The map is an SVG document of crossed gradients plus a blurred inset "frost band"; X reads R and Y reads B (`src/core/displacementMap.ts:239-327`, `src/index.tsx:349`). A fold-free envelope widens the neutral edge band with scale and attenuates amplitude past a ceiling (`src/core/displacementField.ts:15-42`). Correctness criterion: the Jacobian of `p -> p + scale * field(p)` must stay positive (`src/core/displacementField.ts:92-120`). Non-lens strength is capped at 10% of the short side (`src/index.tsx:436`).

### C. SVG port of liquidGL optics (`optics="liquidgl"`)

CPU evaluation of liquidGL's field, `edge * refraction + edge^10 * bevelDepth` with a centre dead zone (`src/core/liquidGLModel.ts:16-19`); maps at 0.75 px per CSS px with LRU caches; frost as a Gaussian blur; neutral offset corrected with a color matrix because a component-transfer LUT re-quantizes in Chromium (`src/core/svgLiquidGL.ts:5-81`, `src/core/LiquidGLSvgFilter.tsx:51-82`).

### D. WebGL over a captured backdrop (Safari, iOS, Firefox; opt-in elsewhere)

1. Resolve the backdrop from `backdropRef`, `backdropSelector` or a `LiquidGlassScene`; reject a backdrop that contains the panel or is inside it (`src/core/webgl/useWebGL.ts:22-26`).
2. Rasterize: `<video>` and `<canvas>` directly; HTML through the vendored html-to-image foreignObject path (`src/core/webgl/source.ts:48-61`, `:92-190`).
3. Measure rects once per frame; hold the document top during iOS overscroll (`src/core/webgl/runtime.ts:124-127`).
4. Skip the frame when geometry, DPR, options and media time are unchanged (`src/core/webgl/runtime.ts:134-141`).
5. Crop and upload, smearing edge rows for padding (`src/core/webgl/runtime.ts:165-202`).
6. Optional blur: 6 iterations of separable 9-tap Gaussian on half-resolution buffers (`src/vendor/ybouane/GlassRenderer.ts:236-264`).
7. Shade with a fragment shader that samples the same 512 px displacement map as SVG, applies per-channel dispersion, Rec.709 saturation and B-channel sheen, with an anti-aliased SDF mask (`src/core/webgl/optics.ts:18-35`).
8. Present via a probed `ImageBitmap` transfer or a 2D copy (`src/core/webgl/runtime.ts:29-50`).

DPR cap `min(devicePixelRatio, 3, maxScale)` (2 for liquidGL optics) (`src/core/webgl/runtime.ts:131-133`).

### E. Frosted CSS fallback

Blur of at least 8 px (mobile or low quality) or 11 px, `saturate(max(sat, 180%))`, a top-lit white gradient tint, and inset rims plus a soft drop shadow (`src/index.tsx:497-499`, `:583`, `:593-594`, `:610-611`). iOS forces a 7 px minimum blur in `iosBlurMode="auto"` (`src/index.tsx:471`).

### F. Animated "liquid" (SVG only)

`feTurbulence` then a second `feDisplacementMap`, with `baseFrequency` rewritten each rAF on the DOM node; presets ripple, flow, wobble (`src/core/liquid.ts:44-74`, `src/index.tsx:550-576`). Not available in WebGL (`README.md:223-224`).

### G. Experimental engine

`simple-liquid-glass/engine` accepts user GLSL materials that define `vec4 slg_shade(vec2 p)` (premultiplied) with helpers for backdrop and under-layer sampling; a material that throws 3 frames in a row falls back (`src/core/engine/types.ts:36-52`, `src/core/engine/glsl.ts:20-49`, `CHANGELOG.md:33-34`).

## 4. API tables

### `<LiquidGlass>` props (`src/index.tsx:58-278`, defaults `:293-340`)

| Prop | Type | Default | Effect |
| --- | --- | --- | --- |
| `renderer` | `'auto' \| 'svg' \| 'webgl'` | `'auto'` | Engine choice; iOS always WebGL |
| `webglScene` | `'auto' \| 'off'` | `'auto'` | Share one canvas among eligible siblings |
| `backdropRef` / `backdropSelector` | ref / string | none | WebGL source; must not be an ancestor |
| `backdropVersion` | string or number | none | Change to force recapture |
| `maxScale` | number | DPR cap 3 (2 for liquidGL) | WebGL drawing scale cap |
| `material` | `'clear' \| 'frosted' \| 'smoked' \| 'subtle'` | none | Preset bundle; explicit props win (`src/materials.ts:7-28`) |
| `refraction` | `'classic' \| 'lens'` | `'lens'` | Map family |
| `lensProfile` | `'material' \| 'loupe' \| 'player' \| 'track'` | `'player'` | Lens preset |
| `lensOptions` | object | none | Clamped per-field overrides (table below) |
| `optics` / `webglOptics` | `'native' \| 'liquidgl'` | native | Optical model |
| `liquidGLOptions` | object | refraction .006, bevelDepth .015, bevelWidth .15, frost blur/8 | liquidGL coefficients (`src/core/webgl/types.ts:2-10`) |
| `displacementScale` | CSS px | none | Overrides lens scale |
| `scale` | number | 160 | Strength; 0 off, 320 double |
| `radius` | px | 50 | Clamped to half size |
| `blur` | px | 0 | Backdrop blur |
| `dispersion` / `aberrationIntensity` | number | 50 / 0 | RGB split; 0 intensity means none |
| `saturation` | % | 140 | `saturate()` or shader luma mix |
| `frost` | 0 to 1 | 0.1 | Fallback tint alpha |
| `borderColor` | color | `rgba(120,120,120,0.7)` | Gradient rim ring |
| `glassColor` | semi-transparent color | `rgba(255,255,255,0.4)` | Tint; opaque values rejected |
| `autoTextColor`, `textOnDark`, `textOnLight`, `forceTextColor` | | false, `#ffffff`, `#111111`, false | Luminance-based text color switch |
| `quality` | `'low' \| 'standard' \| 'high' \| 'extreme'` | `'low'` | Low disables RGB split and caps blur |
| `autodetectquality` | boolean | false | Idle-time benchmark (`src/quality.ts:29-49`) |
| `effectMode` | `'auto' \| 'svg' \| 'blur' \| 'off'` | `'auto'` | Force a strategy |
| `iosMinBlur` / `iosBlurMode` | number / `'auto' \| 'off'` | 7 / `'auto'` | iOS blur floor |
| `reveal` | `'ready' \| 'immediate'` | `'ready'` | Waits up to 400 ms at opacity 0 |
| `liquid`, `liquidSpeed`, `liquidScale` | preset or false | false | Animated turbulence (SVG) |
| `border`, `lightness`, `displace`, `alpha`, `angle`, `shapeAdapt`, `lens`, `lensStrength`, `lensCenter` | | | Classic map shaping (legacy) |
| `onDiagnosticsChange` | function | none | Strategy, reason, quality |

Imperative handle: `refreshBackdrop()`, `element`, `getQuality()`, `getDiagnostics()` (`src/index.tsx:281-290`).

### `lensOptions` profiles (`src/core/nativeOptics.ts:4-13`)

| Option | Range | material | loupe | player | track |
| --- | --- | --- | --- | --- | --- |
| strength | 0 to 0.5 | .05 | .14 | .16 | .03 |
| specular | 0 to 3 | 1 | 1.55 | 1 | 1 |
| depth | 0 to 1 | .5 | .95 | .2 | .3 |
| curvature | 0 to 1 | .3 | .5 | .55 | .25 |
| bend | 0 to 1 | .45 | .4 | .25 | .05 |
| bendWidth | .001 to .5 | .16 | .07 | .08 | .06 |
| sheen | 0 to 2 | .32 | 1.2 | .95 | .35 |
| sheenWidth (px) | 0 to 10 | 3 | 3.5 | 2 | 3 |
| sheenFalloff | .1 to 5 | 1.5 | 1.7 | 1.5 | 1.5 |
| sheenAngle (deg) | -360 to 360 | 45 | 0 | 50 | 45 |
| glowFalloff | .1 to 5 | .5 | .6 | 1.5 | 1.5 |
| glow | 0 to 1 | .1 | .1 | .15 | .1 |

Only geometry fields key the map cache; strength, specular and brightness do not (`src/core/nativeOptics.ts:62-67`).

### Material presets (`src/materials.ts:7-16`)

| Preset | lensProfile | blur | saturation | aberration | frost | glassColor |
| --- | --- | --- | --- | --- | --- | --- |
| clear | player | 0 | 115 | .12 | 0 | `rgba(255,255,255,.08)` |
| frosted | material | 8 | 110 | .03 | .25 | `rgba(255,255,255,.3)` |
| smoked | material | 3 | 90 | .04 | .1 | `rgba(20,24,32,.35)` |
| subtle | track | 1 | 105 | 0 | .04 | `rgba(255,255,255,.06)` |

### Other entries

| Entry | API | Evidence |
| --- | --- | --- |
| `./interactive` | `LiquidGlassInteractive` with `elasticity=.15`, `maxShift=18`, `stiffness=.18`, `damping=.78`, `specular`, `liquidTrigger`, `followPointer`, `clickRipple`; `usePointerElastic(ref, options)` | `src/interactive/index.tsx:94-229` |
| `./web-component` | `<liquid-glass>` with attributes such as `renderer`, `effect-mode`, `backdrop-selector`, `lens-profile`, `radius`, `blur`, `saturation`, `scale`; `defineLiquidGlass(tag)` | `src/web-component/index.ts:16`, `:44`, `:98-99` |
| `./webgl` | `createWebGLSurface(element, output, backdrop, options)`, `supportsSvgBackdrop`, `getGlassEngineStats()` | `src/webgl/index.ts:1-51` |
| `./backdrop` | `<LiquidGlassScene maxCacheBytes>`, `useLiquidGlassBackdrop`, `createLiquidGlassBackdrop` | `src/backdrop/index.tsx:1-25` |
| `./experimental` | `createExperimentalScene(overlay, panels, source, opts)` | `src/experimental/index.ts:5-46` |
| `./engine` | `getGlassEngine()` with `defineMaterial`, `createSurface`, `createLayer`, `registerBackdropSource` | `src/core/engine/types.ts:211-228` |

WebGL statuses: `pending`, `active`, `missing-backdrop`, `invalid-backdrop`, `invalid-selector`, `webgl-unavailable`, `capture-failed` (`src/core/webgl/types.ts:45-46`).

## 5. Motion

- Pointer spring is explicit Euler per frame, `v = (v + (target - x) * stiffness) * damping` (`src/interactive/spring.ts:21-25`). Inference from the code: it runs faster on 120 Hz displays because it steps per frame, not per second.
- The current spring translation is subtracted before measuring, which fixed a feedback loop (`src/interactive/index.tsx:165-177`, `CHANGELOG.md:298`).
- Click ripples use WAAPI on transform and opacity only, capped at 6, and avoid per-ripple `backdrop-filter` because each forces a new backdrop snapshot (`src/interactive/index.tsx:22-49`, `:283-322`).
- No shape-morph API.

## 6. Performance notes

- Map bytes are a per-frame cost on Chromium while glass or backdrop moves; size maps at 0.75 px per CSS px (`src/core/nativeMapGeometry.ts:2-9`).
- Each SVG pane is its own GPU pass; CPU cost scales linearly (829 vs 347 ms/s for 24 scrolling panes), hence the shared WebGL scene for crowds (`CHANGELOG.md:214-215`).
- Each filter primitive is a pass per moving frame; keep graphs short (`CHANGELOG.md:237`).
- One offscreen WebGL context shared by all panels, ref-counted programs, uniform diffing, one rAF with a measure phase (`src/core/webgl/contextPool.ts:7-52`, `src/vendor/ybouane/GlassRenderer.ts:32-57`, `:441-454`).
- IntersectionObserver with a 200 px margin drops `backdrop-filter` and releases WebGL offscreen (`src/core/useGeometry.ts:63-79`).
- Author benchmarks: 104 scrolling panes at 60 fps in 5.6 (`README.md:33-39`).

## 7. Accessibility

- Reduced motion stops turbulence, the pointer spring and ripples, and engine materials get `settle=true` (`src/index.tsx:531-541`, `src/interactive/index.tsx:123-124`, `:286`, `src/core/engine/engine.ts:141-142`).
- Decorative canvases and overlays are `aria-hidden` (`src/index.tsx:662`, `:679`).
- `reveal="ready"` hides with opacity, not visibility, so live regions still announce (`src/index.tsx:636-639`).
- `autoTextColor` switches at relative luminance 0.5 of the nearest opaque ancestor; it is not a contrast-ratio check and ignores the refracted image (`src/cssColor.ts:68-72`, `src/core/useTextColor.ts:40-46`).
- Absent: `prefers-reduced-transparency`, `prefers-contrast`, `forced-colors`, focus styles and roles (the root is a plain `div`) (`src/index.tsx:58`, `:660`).

## 8. Known bugs and failure modes

1. A backdrop that is an ancestor of the lens recaptured itself on every mutation and crashed iOS Safari; now rejected (`CHANGELOG.md:519-523`, `src/core/webgl/useWebGL.ts:26`).
2. An ancestor with opacity, filter, mask or clip-path becomes the backdrop root in Chromium, so `backdrop-filter` sees nothing during a fade; animate transform instead (`README.md:240-242`).
3. Shared scenes paint grouped panes below elements between them; panes with opacity below 1, filters, blend, masks, rotation, own background or negative z-index are ineligible (`src/core/webgl/sharedScene.ts:31-61`).
4. Corner folds at high scale in the classic map, fixed by the fold-free envelope at the cost of weaker refraction on thin bars (`CHANGELOG.md:364-378`).
5. 8-bit neutral is 128/255, not 0.5; corrected with a `-1/510` intercept (`src/core/DisplacementFilter.tsx:63-67`).
6. Scaled entrance animations shrank maps when measured with `getBoundingClientRect` (`CHANGELOG.md:299`).
7. Tainted media or allocation failure reports `capture-failed` and keeps the CSS fallback (`src/core/webgl/runtime.ts:212-215`).
8. Media nested in an HTML source is a snapshot, and CSS-only animations need `backdropVersion` or `refreshBackdrop()` (`README.md:213-226`).
9. Sending `uniform1f` to an `int` uniform fails on real drivers but passed jsdom mocks (`CHANGELOG.md:76-81`).
10. Straight vs premultiplied alpha: some `transferToImageBitmap` implementations mishandle straight alpha, hence a pixel probe (`src/core/webgl/liquidGLOptics.ts:245-257`).
11. An earlier DOM-mirror approach (clone the backdrop inside the lens) was removed in 4.0 as unreliable on iOS (`CHANGELOG.md:384-399`).
12. An unbounded map cache leaked in long-lived SPAs until 2.2.0 (`CHANGELOG.md:577`).
13. Doc drift: `docs/frameworks/README.md:14-20` still says iOS refraction needs the React component, while each guide says the custom element uses WebGL with `backdrop-selector`.

## 9. Borrow and avoid

Borrow:
- Capability tiers with visible diagnostics (`data-glass-strategy`, `data-glass-reason`).
- The lens model knobs (depth, curvature, lip bump, sheen floor) as tuning vocabulary.
- Fold-free check: treat a positive Jacobian determinant as a testable invariant.
- The per-frame SVG cost model and crowd hysteresis.
- Backdrop-must-not-be-an-ancestor rule, plus scene-eligibility rules as a lint list.
- Dispersion as per-channel scale, disabled at low quality.

Avoid or adapt:
- UA regex as the only capability signal; keep it, but default unknown engines to frost.
- Frame-count springs; use time-based integration.
- Missing reduced-transparency, contrast and forced-colors handling; add a solid tier.
- Dense hand-minified style if you fork it; you will need to review it line by line.

## 10. License and attribution

The repository is MIT, "Copyright (c) 2025 lucaperullo" (`LICENSE:3`). It vendors code under other notices (`THIRD_PARTY_NOTICES.md`):

| Vendored path | Origin | Notice |
| --- | --- | --- |
| `src/vendor/samasante/*`, adapted `src/core/materialFilter.ts` | github.com/samasante/liquid-glass, rev `4e7b769e` | MIT, "Copyright (c) 2026 Sam Asante" |
| `src/vendor/ybouane/*` | npm `@ybouane/liquidglass` 1.0.3 | MIT text with no copyright line ("the published source has no separate copyright notice") |
| `src/vendor/html-to-image/*` | github.com/bubkoo/html-to-image 1.11.11 | MIT, "Copyright (c) 2017-2023 W.Y." |
| `src/core/webgl/liquidGLOptics.ts`, `src/core/liquidGLModel.ts`, `src/core/svgLiquidGL.ts`, `src/core/LiquidGLSvgFilter.tsx` | github.com/naughtyduk/liquidGL, commit `88f681ab` | MIT, "Copyright (c) NaughtyDuk" |

Shipping this package's dist means carrying every one of these notices. This plugin re-derives ideas and copies no code.
