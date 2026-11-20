# Source notes: ybouane-liquidglass (`@ybouane/liquidglass`)

Condensed study notes for one of the five libraries this plugin learned from. Nothing here is vendored; because the archive has no LICENSE file, formulas are restated in our own notation with attribution and no code is quoted. Citations use `<repo-relative path>:line` in the upstream layout (repository `github.com/ybouane/liquidglass`).

Observed in the supplied archive on 2026-11-05 (zip comment names commit `59af227103795f06421a96e2c7d3dceb081decd2`). The archive is a snapshot, not necessarily the latest release. Recheck upstream before quoting a version, behavior or license status.

## 1. Identity

| Field | Value | Evidence |
| --- | --- | --- |
| Package | `@ybouane/liquidglass` | `package.json:2` |
| Version in archive | `1.0.3` | `package.json:3` |
| License field | `"MIT"`; README has a "License / MIT" section | `package.json:35`, `README.md:240-242` |
| LICENSE file | **Absent from the archive** | archive listing: `.gitignore`, `README.md`, `package.json`, `package-lock.json`, `tsconfig.json`, `patches/`, `src/` |
| Copyright holder | **Not stated anywhere**; `author` is an empty string | `package.json:34` |
| Credit | "Built by @ybouane" | `README.md:1` |
| Module format | ESM only | `package.json:5-14` |
| Build | `tsc` for types plus `esbuild --bundle` | `package.json:21` |
| Runtime deps | None declared; `html-to-image` 1.11.13 is a devDependency that esbuild bundles, patched with `patch-package` | `package.json:20-21`, `:36-41`, `patches/html-to-image+1.11.13.patch` |
| Size (measured from the archive) | `src/` TypeScript is 99,946 bytes, about 27.7 KB gzip; the published bundle also contains html-to-image, not measured | `gzip -c` on the archive files, 2026-11-05 |
| Tests, CI, changelog | None | `package.json:19-23` |
| Source files | 6 files, about 2,900 lines (`LiquidGlass.ts`, `HtmlCapture.ts`, `GlassRenderer.ts`, `shaders.ts`, `defaults.ts`, `index.ts`) | `src/` |

**One-line summary.** A WebGL 1 library that reconstructs the DOM behind each glass element into a 2D canvas (html-to-image for HTML, `drawImage` for media), blurs it, and runs one fragment shader with an SDF rounded rectangle, height-field refraction, chromatic aberration, Fresnel, four fixed lights, a rim stroke and a drop shadow. Output goes into a canvas injected in each glass element (`README.md:64-69`, `src/GlassRenderer.ts:1-8`).

## 2. Technique pipeline

1. `_renderLoop` runs on rAF; it returns early when nothing is dirty, nothing is `data-dynamic` or video, and no drag is active (`src/LiquidGlass.ts:937-995`).
2. Root children are sorted by a re-implementation of CSS stacking order (`src/LiquidGlass.ts:591-667`).
3. Each glass re-shades only when dirty, moved more than 0.5 px, under a re-rendered earlier glass, over dynamic content, or dragged (`src/LiquidGlass.ts:1056-1078`).
4. Compose a local scene canvas for the glass's sample rect (bounding rect plus a 20 px pad), filled white first, then every earlier child: media through `drawImage` with `object-fit` emulation, wrappers through cached html-to-image rasters, and earlier glass outputs plus their labels, so glass refracts glass (`src/LiquidGlass.ts:1125-1394`).
5. Crop, upload with `texImage2D`, and copy into framebuffers (`src/GlassRenderer.ts:157-206`).
6. Blur when `blurAmount > 0`: 6 rounds of horizontal and vertical 9-tap Gaussian, step `2.5 * blurAmount` texels, at full resolution (`src/GlassRenderer.ts:208-225`, `src/defaults.ts:76`).
7. Run the glass shader with sharp and blurred textures, all sizes multiplied by DPR (`src/GlassRenderer.ts:232-282`).
8. Read back: the hidden shared WebGL canvas (`preserveDrawingBuffer: true`) is copied with 2D `drawImage` into the per-glass canvas, which sits inside the glass at `-20px` offset with `z-index: -1` (`src/GlassRenderer.ts:59-70`, `src/LiquidGlass.ts:754-776`, `:1108-1114`).
9. The glass element's live children render on top as normal HTML.

### Shader (paraphrased, `src/shaders.ts`)

- Shape: the standard rounded-box distance with radius clamped to half the short side (`:122-125`, `:144-146`). Rounded rectangle, not a squircle.
- Height: a circular bevel `h(d) = sqrt(d * (2 zR - d))` for `d` inside distance below `zR`, flat above it (`:133-137`). `zR` is `zRadius` times DPR.
- Normals: central differences of the height with a 2 device px step, five SDF evaluations per fragment (`:169-182`).
- Refraction, biconvex mode: offset in device px is the height gradient times `(1 - 1/1.5)`, counted for entry and exit plus a thickness term, times `refraction * 30`, plus a centre pull `refraction * 4 * depth` (`:187-200`). Entry and exit use the same gradient, so the "dual surface" amounts to a gain of 2. Not vector Snell.
- Refraction, dome mode: sample position contracted toward the centre by `refraction * depth * 0.35` (`:202-205`). Derived from the code: default `refraction = 0.69` gives about 1.32x magnification on the plateau.
- Micro distortion: static hash noise, `distortion * 4` px wide (`:139-141`, `:209-211`).
- Chromatic aberration: red and blue sampled along `N.xy`, offset `chromAberration * 36 * (0.3 + 0.7 * edge)` device px, from both textures, six fetches (`:214-227`). It appears only on the bevel because `N.xy` is about zero on the plateau.
- Blur mix: at least 85% blurred everywhere, the rim slightly sharper (`:231-232`).
- Grading: multiplicative brightness, Rec.601 saturation, fixed cool tint `(0.92, 0.95, 1.05)`, interior up to 6% brighter (`:235-243`).
- Lighting: Fresnel `(1 - |N.z|)^4`, three Blinn-Phong lobes (exponents 90, 50, 120) and a Lambert bloom with fixed light vectors, a 1.5 px inner stroke biased to the top, rim and inner glow, a fake environment term, and a white mix of `fresnel * 0.2` (`:246-285`). Inference from the y-down frame: the fixed lights favour the bottom and right rims while the stroke favours the top; recheck light vectors before reuse.
- Shadow: outside the shape, a Gaussian term (65%) plus an exponential contact term (35%), offset in y (`:149-159`).
- Blending: straight alpha, `SRC_ALPHA, ONE_MINUS_SRC_ALPHA` (`src/GlassRenderer.ts:65-70`, `:244-245`).

Not present: SVG filters, `backdrop-filter`, squircles, lip profiles, user tint color, animated uniforms.

## 3. API tables

### Exports (`src/index.ts:21-25`)

| Export | Kind | Notes |
| --- | --- | --- |
| `LiquidGlass` | class | Start with `LiquidGlass.init()`; `new` alone does not render (`src/LiquidGlass.ts:87-91`) |
| `LiquidGlassOptions` | type | `src/LiquidGlass.ts:22-29` |
| `DEFAULTS`, `GlassConfig` | const, type | `src/defaults.ts:33-73` |
| `invalidateFontEmbedCache()` | function | Clears the font-embed promise (`src/HtmlCapture.ts:26-34`) |

### `LiquidGlass.init(options)` returns `Promise<LiquidGlass>`

| Option | Type | Default | Effect | Evidence |
| --- | --- | --- | --- | --- |
| `root` | `HTMLElement` | required | Container whose children are captured; the root's own paint never is; gets `user-select: none` | `src/LiquidGlass.ts:24`, `:178`, `:216-217` |
| `glassElements` | elements | `[]` | Must be direct children of `root` | `src/LiquidGlass.ts:26`, `:334-338` |
| `defaults` | `Partial<GlassConfig>` | `{}` | Instance overrides | `src/LiquidGlass.ts:28`, `:181` |

`init` waits for font prefetch, glass content capture and static pre-warm (README: typically 100 to 500 ms) (`src/LiquidGlass.ts:215-282`, `README.md:232`).

### Instance members

| Member | Effect | Evidence |
| --- | --- | --- |
| `fps` | Frames in the last window of at least 1 s | `src/LiquidGlass.ts:940-947` |
| `destroy()` | Stops the loop and removes canvases, listeners and inline `position`, `overflow`, `touch-action` | `src/LiquidGlass.ts:284-323` |
| `markChanged(el?)` | Re-shade glasses intersecting `el`, or all | `src/LiquidGlass.ts:490-496` |

### Per-element config (`data-config` JSON over instance defaults; `src/defaults.ts:53-73`)

| Option | Default | Effect |
| --- | --- | --- |
| `blurAmount` | 0 | Blur step `2.5 * v` texels, 6 passes per axis |
| `refraction` | 0.69 | Scales gradient offset (x30), centre pull (x4), dome zoom (x0.35) |
| `chromAberration` | 0.05 | RGB split along the normal |
| `edgeHighlight` | 0.05 | Rim, inner glow and stroke |
| `specular` | 0 | Four-light sum |
| `fresnel` | 1 | Fresnel white mix and environment term |
| `distortion` | 0 | Static noise |
| `cornerRadius` | 65 (CSS px) | Clamped to half the short side |
| `zRadius` | 40 (CSS px) | Bevel width and height |
| `opacity` | 1 | Panel alpha (shadow unaffected) |
| `saturation` | 0 | -1 grey to +1 vivid |
| `tintStrength` | 0 | Mix toward the fixed cool tint |
| `brightness` | 0 | `col *= 1 + v` |
| `shadowOpacity`, `shadowSpread`, `shadowOffsetY` | 0.3, 10, 1 | Shadow |
| `floating` | false | Drag to move |
| `button` | false | Hover +0.2 brightness; press `zRadius * 0.8`, `shadowSpread * 1.2` |
| `bevelMode` | 0 | 0 biconvex pill, 1 dome magnifier |

No range validation; invalid JSON warns and falls back to `{}` (`src/LiquidGlass.ts:692-712`). Attribute `data-dynamic` on a root child recaptures every frame (`src/LiquidGlass.ts:669-686`, `README.md:144-160`). Half-sphere magnifier recipe: `bevelMode: 1` with `cornerRadius === zRadius` (`README.md:140`).

## 4. Motion

- No springs, inertia, morphing or pointer-tracked lighting; the shader has no time input.
- `floating`: pointer drag with `setPointerCapture`, clamped to the root with a 10 px margin, written as `transform: translate()` (`src/LiquidGlass.ts:821-931`).
- `button`: hover and press change uniforms in one frame, not animated (`src/LiquidGlass.ts:498-524`, `:716-727`).
- Sizing uses `offsetWidth/Height` so hover scale does not trigger resize loops (`src/LiquidGlass.ts:758-760`, `:781-783`).

## 5. Platform behavior

- Requires WebGL 1, Canvas 2D and SVG `foreignObject`; README claims all evergreen browsers (`README.md:236-238`). Because it does not use `backdrop-filter: url()`, refraction can show in Safari and Firefox too (inference from the architecture; not observed in a browser for this note).
- On missing WebGL it throws, so `init()` rejects; there is no CSS fallback (`src/GlassRenderer.ts:65-74`).
- Context loss is handled: `webglcontextlost` prevents default, restore recompiles programs and marks everything dirty (`src/GlassRenderer.ts:80-98`, `src/LiquidGlass.ts:200-203`).
- Shader compile failures are only logged (`src/GlassRenderer.ts:378-400`).

## 6. Performance notes

- Per re-shaded glass: 2D compose, CPU to GPU upload, up to 15 draws, then a GPU to 2D readback that needs `preserveDrawingBuffer` (`src/GlassRenderer.ts:157-282`, `src/LiquidGlass.ts:1108-1114`).
- html-to-image capture is expensive; keep wrappers small and shallow (`README.md:219`).
- Dirty tracking with rect-intersection fan-out and cascade only to later overlapping glasses (`src/LiquidGlass.ts:110-135`, `:407-472`).
- Fonts: one shared prefetch promise; per-element filtering by family, weight, style and the unicode ranges actually rendered (`src/HtmlCapture.ts:126-220`, `:294-310`).
- One WebGL context per instance; README warns of about 16 concurrent contexts (`README.md:221`).
- Window resize recaptures everything; no ResizeObserver (`src/LiquidGlass.ts:736-752`).
- Blur step is in device pixels, not scaled by DPR (`src/GlassRenderer.ts:210`). Derived: the same `blurAmount` looks about half as strong in CSS px on a 2x display.

## 7. Accessibility

- No `prefers-*` media query handling at all (no `matchMedia` in `src/`).
- Default glass is fully clear (no blur, no tint), the worst case for text contrast (`src/defaults.ts:54`, `:65`).
- `button: true` adds no role, tabindex, keyboard activation or focus style (`src/LiquidGlass.ts:69-75`).
- `user-select: none` is forced on the whole root (`src/LiquidGlass.ts:216-217`).
- Positive: glass content stays live DOM above a `pointer-events: none` canvas (`src/LiquidGlass.ts:361-363`).

## 8. Known bugs and failure modes

From the README "Limitations & Gotchas" (`README.md:207-234`) and code comments:

1. Glass must be a direct child of the root; nested glass is rejected (`src/LiquidGlass.ts:333-338`).
2. Root background, padding and border are never captured; the scene starts white (`src/LiquidGlass.ts:1150-1151`).
3. The injected canvas becomes the glass's first child and breaks `:first-child` selectors (`src/LiquidGlass.ts:363`).
4. The shadow halo overflows by 20 px and gets clipped by `overflow: hidden` ancestors.
5. Overlays must form a recognized stacking context or they paint in the wrong order (`src/LiquidGlass.ts:619-628`).
6. Webfonts must load before `init()` and be CORS friendly, or captured text will not line up with live text (`src/HtmlCapture.ts:373-391`).
7. Cross-origin images need `crossorigin="anonymous"`; a tainted canvas disables glass for the whole root.
8. `destroy()` does not restore an original `position: static`.
9. html-to-image floors font sizes and subtracts 0.1; the local patch removes that so glyph metrics match (`patches/html-to-image+1.11.13.patch:13-20`).

Found by reading the code (inference, not observed in a browser):

10. Rim offsets can exceed the 20 px crop pad, so edge pixels repeat (`src/GlassRenderer.ts:185-186`).
11. Scaled or rotated glass samples a misaligned background, because the shader assumes an untransformed rect (`src/GlassRenderer.ts:259-260`).
12. Drag overwrites `transform` with a plain `translate()` (`src/LiquidGlass.ts:917`).
13. `_hasDynamic` is computed once, so dynamic children added later never trigger per-frame rendering (`src/LiquidGlass.ts:219`).
14. Glass added after init is not supported (`src/LiquidGlass.ts:182`, `:268-276`).
15. A tainted-canvas upload error is caught and logged every frame (`src/LiquidGlass.ts:963-967`).

## 9. Borrow and avoid

Borrow:
- Height field to normal to refraction: one model drives refraction, aberration, Fresnel and specular.
- Two presets from one shader: pill edge vs dome magnifier.
- Normal-aligned, rim-weighted chromatic aberration.
- Sharp and blurred dual sampling with a sharper rim.
- Back-to-front glass compositing so glass refracts glass.
- Dirty tracking with an idle short-circuit; context-loss recovery.
- Font fidelity steps for any DOM rasterization.

Avoid or adapt:
- Throwing with no fallback; keep a frost or solid tier.
- Blur not normalized by DPR; refraction offsets larger than the sampled pad.
- Forcing `user-select: none` on a region; one-frame hover and press jumps.
- Per-frame GPU readback where a native compositing path exists.

## 10. License and attribution

`package.json` and the README say MIT, but the archive contains **no LICENSE file and no copyright line**, so the MIT text and the rights holder cannot be reproduced from local evidence. Treat it as permissively licensed by declaration only: cite the repository as inspiration, reimplement ideas in original code, and do not copy source. The bundled html-to-image 1.11.13 is MIT (`package-lock.json:879-884`); redistributing the dist carries that notice. Common idioms in the shaders (rounded-box SDF, the 9-tap Gaussian weights, the `fract(sin(dot()))` hash) are widely published techniques. simple-liquid-glass vendors this package's 1.0.3 code and notes the missing copyright line in its `THIRD_PARTY_NOTICES.md`.
