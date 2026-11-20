# Source notes: liquid-glass-react

Condensed study notes for one of the five libraries this plugin learned from. Nothing here is vendored; formulas are paraphrased or quoted briefly with attribution. Citations use `<repo-relative path>:line` in the upstream layout (repository `github.com/rdev/liquid-glass-react`, per `README.md:7`).

Observed in the supplied archive on 2026-11-05. The archive is a snapshot, not necessarily the latest release. Recheck upstream before quoting a version or behavior.

Evidence labels: "measured" means pixel values sampled from the embedded map images by a separate script outside the repo; "inference" means reasoning from the SVG and CSS specs, not observed in a browser.

## 1. Identity

| Field | Value | Evidence |
| --- | --- | --- |
| Package | `liquid-glass-react` | `package.json:2` |
| Version in archive | `1.1.1` (`package-lock.json` still says `1.0.0`) | `package.json:3`, `package-lock.json:3` |
| License | MIT, "Copyright 2025 MAX ROVENSKY" | `LICENSE:1-7` |
| Adapted code | `src/shader-utils.ts` says "Adapted from https://github.com/shuding/liquid-glass" | `src/shader-utils.ts:1` |
| Peer deps | React and ReactDOM 18 or later | `package.json:19-22` |
| Runtime deps | None | `package.json:23-31` |
| Outputs | CJS, ESM and `.d.ts` built by esbuild | `package.json:5-14` |
| Size (measured from the archive) | `src/` is 67,421 bytes (about 41 KB of it is three base64 displacement maps in `src/utils.ts`), about 35.4 KB gzip | `gzip -c` on the archive files, 2026-11-05 |
| Tests, CI, changelog | None | `package.json:10-18` |
| Metadata drift | Phantom workspace, unused `esbuild.config.js` entry pointing at a missing file, empty `repository.url` | `package.json:9`, `:35-38`, `esbuild.config.js:5` |

**One-line summary.** A single React component. A span carries both `backdrop-filter: blur() saturate()` and `filter: url(#svg)`; the SVG filter warps the element's own painted output (which in Chromium includes the blurred backdrop) with `feDisplacementMap` and per-channel chromatic aberration. Rim highlights are CSS gradients that follow the mouse (`src/index.tsx:190-193`, `:508-559`). README: "Safari and Firefox only partially support the effect (displacement will not be visible)" (`README.md:27`).

## 2. Technique pipeline

The component renders up to eight sibling layers sharing the same position and transform (`src/index.tsx:458-611`):

| # | Layer | Purpose | Evidence |
| --- | --- | --- | --- |
| 1, 2 | Black divs, plain and `mix-blend-overlay` | Over-light darkening (Tailwind classes) | `src/index.tsx:461-482` |
| 3 | `GlassContainer` | SVG filter defs, warped backdrop span, children | `src/index.tsx:484-506` |
| 4 | Span, `screen` blend, opacity 0.2 | Soft rim ring | `src/index.tsx:509-533` |
| 5 | Span, `overlay` blend | Strong rim ring | `src/index.tsx:536-559` |
| 6 to 8 | Radial gradients, only with `onClick` | Hover and press glow | `src/index.tsx:562-609` |

Inside `GlassContainer` (`src/index.tsx:195-242`):

1. An `aria-hidden` SVG holds `<filter id={useId()}>` with region `-35%` / `170%` and `color-interpolation-filters="sRGB"` (`src/index.tsx:44-51`, `:177`).
2. `div.glass` is the visible shape: `border-radius`, `overflow: hidden`, padding and a drop shadow (`src/index.tsx:199-211`).
3. `span.glass__warp` fills it and carries both the backdrop filter and the SVG filter; Firefox gets no SVG filter through a UA check (`src/index.tsx:180`, `:190-193`, `:218-227`).
4. Children sit in a separate unfiltered div at `z-index: 1`, forced white, `500 20px/1 system-ui`, with a text shadow (`src/index.tsx:229-240`).

Blur radius in px is `(overLight ? 12 : 4) + blurAmount * 32`, so the default 0.0625 gives 6 px (`src/index.tsx:192`, `:271`).

### Displacement maps

`getMap(mode)` selects the `feImage` source (`src/index.tsx:19-32`): `standard` (256 px JPEG), `polar` (256 px JPEG), `prominent` (256 px PNG), or `shader` (generated at runtime). The image uses `preserveAspectRatio="xMidYMid slice"`, which crops square maps on wide pills (`src/index.tsx:52`; inference).

- The filter reads X from R and Y from **B** (`src/index.tsx:72`, `:84`, `:96`).
- Measured: `standard` has separable S-shaped ramps in R (x) and B (y) with G near 0; the centre is slightly off neutral (R 124, B 132).
- Measured: `prominent` has B = 0 everywhere, so with the Y channel read from B the vertical offset is a constant shift (inference: about 35 px at the default scale) and only horizontal edges refract.
- Baked maps use a negative scale and shader maps a positive one: `scale = displacementScale * (shader ? 1 : -1)` (`src/index.tsx:72`); default 70, halved over light (`src/index.tsx:270`, `:489`).

### Chromatic aberration

Three `feDisplacementMap` passes on the same source, red at the base scale and green and blue at `-aberration * 0.05` and `-aberration * 0.1` added to the sign term, each isolated with `feColorMatrix` and recombined with `screen` blends (`src/index.tsx:71-109`). With defaults (scale 70, aberration 2) the scales are -70, -77, -84. In shader mode the order of the fringes flips (70, 63, 56). A small blur `max(0.1, 0.5 - aberration * 0.1)` follows (`src/index.tsx:112`).

An "edge only" mask is intended (`src/index.tsx:55-66`, `:114-124`), but inference from the spec: the map is opaque, so the discrete alpha transfer maps every pixel to 1 and the mask covers the whole area; an unused radial gradient is also defined (`src/index.tsx:46-50`). Verify in a browser before relying on edge-only aberration.

### Shader mode

A CPU loop on a hidden 2D canvas evaluates a `uv -> sampleUV` function and encodes the offset into a PNG (`src/shader-utils.ts:48-134`). The provided fragment uses the standard rounded-box distance and two smoothsteps to pull samples toward the centre near the edges (`src/shader-utils.ts:24-43`). Inference: the fixed radius 0.6 exceeds both half extents, so the shape term degenerates into a corner-weighted falloff, and the encoding `d / max + 0.5` clips half the range (correct would be `d / (2 * max) + 0.5`) (`src/shader-utils.ts:112-119`). Maps are rendered at 1 CSS px per pixel regardless of DPR (`src/shader-utils.ts:51`). B duplicates G "for SVG filter compatibility" (`src/shader-utils.ts:118`).

### Rim highlight

Two spans draw a 1.5 px gradient ring with the mask-composite border trick; the gradient angle is `135deg + 1.2 * mouseOffset.x`, band positions shift with `mouseOffset.y`, and brightness grows with `|mouseOffset.x|` (`src/index.tsx:518-531`, `:545-557`). Screen and overlay blends let the rim pick up backdrop color.

### Over-light mode

`overLight` adds the black layers (Tailwind `opacity-20`, `mix-blend-overlay`), raises the blur base to 12 px, halves displacement, deepens the shadow to `0 16px 70px rgba(0,0,0,.75)` and removes the text shadow (`src/index.tsx:192`, `:210`, `:236`, `:461-482`, `:489`). Without Tailwind in the host app, the darkening layers do nothing (inference).

## 3. API table

Single default export `LiquidGlass` (`src/index.tsx:268`); props at `src/index.tsx:249-266`, defaults at `:268-285`.

| Prop | Type | Default | Effect | Evidence |
| --- | --- | --- | --- | --- |
| `children` | `ReactNode` | required | Unfiltered content, forced white | `src/index.tsx:230-240` |
| `displacementScale` | number | 70 | `feDisplacementMap` scale (sign by mode), halved over light | `src/index.tsx:72`, `:489` |
| `blurAmount` | number | 0.0625 | Blur px `(overLight ? 12 : 4) + v * 32` | `src/index.tsx:192` |
| `saturation` | number | 140 | `saturate(N%)` | `src/index.tsx:192` |
| `aberrationIntensity` | number | 2 | Green and blue scale offsets, mask threshold, softening blur | `src/index.tsx:65`, `:84`, `:96`, `:112` |
| `elasticity` | number | 0.15 | Translate and stretch toward the cursor | `src/index.tsx:382`, `:425-426` |
| `cornerRadius` | px | 999 | Radius of the glass and all overlay layers | `src/index.tsx:202`, `:467` |
| `globalMousePos` | `{ x, y }` | internal | External viewport mouse position | `src/index.tsx:294`, `:324` |
| `mouseOffset` | `{ x, y }` | internal | External percent offset driving the rim | `src/index.tsx:295`, `:526-529` |
| `mouseContainer` | ref or null | null | Element whose `mousemove` is tracked | `src/index.tsx:300`, `:329` |
| `className` | string | `""` | Appended to the container | `src/index.tsx:196` |
| `padding` | string | `"24px 32px"` (README says "-") | Glass padding | `src/index.tsx:207`, `:280`, `README.md:107` |
| `overLight` | boolean | false | Darker, blurrier, less refraction | see above |
| `style` | object | `{}` | Position fields copied to every layer; `transform` and `transition` overwritten | `src/index.tsx:446-456` |
| `mode` | `"standard" \| "polar" \| "prominent" \| "shader"` | `"standard"` | Map selection; README calls `shader` "most accurate but not the most stable" | `src/index.tsx:19-32`, `README.md:112` |
| `onClick` | function | none | Pointer cursor, press `scale(0.96)`, glow layers | `src/index.tsx:444`, `:562` |

Reference presets: button `displacementScale 64, blurAmount 0.1, saturation 130, aberrationIntensity 2, elasticity 0.35, cornerRadius 100` (`README.md:57-68`); card `100, 0.5, 140, 2, 0, 32` (`liquid-glass-example/src/pages/index.tsx:13-20`).

## 4. Motion

- One `mousemove` listener on the tracked element; every event sets two React states (`src/index.tsx:309-339`). No pointer or touch events, no leave reset, no rAF batching.
- Elastic stretch activates within 200 px of the box edge with a linear fade; stretch along the cursor axis by `+0.3 * I`, squash across by `-0.15 * I`, floor 0.8 (`src/index.tsx:357-390`).
- Translation toward the cursor is `delta * elasticity * 0.1 * fade` (`src/index.tsx:424-427`).
- Press replaces the stretch with `scale(0.96)` (`src/index.tsx:444`).
- No springs: all smoothing is CSS transitions of 0.15 to 0.2 s (`src/index.tsx:209`, `:449`, `:572`).
- No morphing; the example app flips `overLight` by scroll range (`liquid-glass-example/src/pages/index.tsx:36-44`).

## 5. Platform behavior

| Engine | Blur and saturate | Displacement and aberration | Evidence |
| --- | --- | --- | --- |
| Chromium | yes | yes | `README.md:27` |
| Safari | only where unprefixed `backdrop-filter` works (no `-webkit-` declaration is emitted) | not visible; the filter is still attached | `src/index.tsx:191-192` |
| Firefox | yes | disabled by UA check | `src/index.tsx:180`, `:191` |

- `navigator.userAgent` is read during render, an SSR hazard on runtimes without a global `navigator` (`src/index.tsx:180`; inference).
- `useId()` keeps filter IDs stable across server and client (`src/index.tsx:177`).

## 6. Performance notes

- Five layers always, eight when clickable, several with blend modes (`src/index.tsx:458-611`).
- One filter graph per instance with three displacement passes, and a 170% filter region (`src/index.tsx:51-125`). Inference: about 2.9 times the pixel area is processed.
- Every `mousemove` re-renders all layers and calls `getBoundingClientRect` several times during render (`src/index.tsx:309-317`, `:444`).
- Shader mode runs a synchronous per-pixel JS loop and PNG encode on every size change, with no cache (`src/shader-utils.ts:71-124`, `src/index.tsx:183-188`).
- The 41 KB of baked maps ship in every bundle (`src/utils.ts`).
- Size is measured on mount and window resize only; no ResizeObserver (`src/index.tsx:431-442`).

## 7. Accessibility

- `onClick` sits on a plain `div`: no role, tabindex, key handlers or focus style (`src/index.tsx:196`).
- No reduced-motion, reduced-transparency or contrast handling.
- Children forced to white text with a shadow and `line-height: 1`, which can clip multi-line text (`src/index.tsx:231-236`).
- Decorative SVG is `aria-hidden`; overlays use `pointer-events: none` (`src/index.tsx:44`, `:517`).
- Mouse-only input.

## 8. Known bugs and failure modes

1. The layers are fragment siblings; with the default `position: relative` they misalign, so use `position: fixed` or `absolute` with `top` and `left` as the README does (`src/index.tsx:444-456`, `README.md:84`).
2. The root is block level while `.glass` is `inline-flex`, so measured size can exceed the visible glass when not absolutely positioned (`src/index.tsx:196`, `:204`; inference).
3. No ResizeObserver: content changes leave rims, overlays and SVG stale (`src/index.tsx:431-442`).
4. Prominent mode has no vertical refraction (measured B = 0).
5. Shader encoding clips half the range (inference).
6. Edge-only aberration mask is inert (inference).
7. `slice` cropping of square maps removes corner and vertical refraction on pills (inference).
8. Coordinates of 0 are treated as "no mouse" (`src/index.tsx:343`, `:395`).
9. No `mouseleave` reset leaves the glass stretched (inference from `src/index.tsx:323-339`).
10. External mouse control works only when both `globalMousePos` and `mouseOffset` are passed (`src/index.tsx:324`).
11. User `transform` and `transition` are overwritten (`src/index.tsx:446-450`).
12. Every instance emits `id="feimage"`, duplicating IDs (`src/index.tsx:52`).
13. The refraction profile ignores `cornerRadius`; only `overflow: hidden` clips to the shape.

## 9. Borrow and avoid

Borrow:
- `backdrop-filter` plus `filter: url()` on one layer with content on a separate unfiltered layer, gated so other engines keep blur and saturate.
- Per-channel displacement for aberration with a single "dispersion" knob.
- Mouse-steered rim ring via `mask-composite`, doubled in screen and overlay blends.
- Edge-distance activation zone for elasticity, stretch along and squash across the pointer axis.
- Over-light as a bundle of adjustments, driven by sampled luminance rather than a manual flag.
- Press feedback of a small scale plus a top-centre glow, with real button semantics.

Avoid or adapt:
- JPEG for vector displacement data; square maps stretched or cropped to any size; maps that ignore the radius.
- UA sniffing during render; missing `-webkit-backdrop-filter`; Tailwind-only styling.
- React state updates on every mouse event; no ResizeObserver; duplicate IDs; overwriting user transforms.
- Click handlers on divs and mouse-only input.

## 10. License and attribution

MIT, "Copyright 2025 MAX ROVENSKY" (`LICENSE:1`). Copying code, the filter graph or the base64 maps requires keeping that notice. `src/shader-utils.ts` is marked as adapted from `shuding/liquid-glass`, whose license is not in the archive, so its terms are unverified from local evidence; reimplement from first principles instead of copying. The three embedded maps have no stated origin (`src/utils.ts:1-8`). This plugin re-derives ideas. References quote at most a few short lines from the MIT-licensed files with attribution, and quote nothing from `src/shader-utils.ts`; its formulas appear only as paraphrased math (for example [optics.md](../optics.md#34-liquid-glass-react-smoothstep-corner-map)).
