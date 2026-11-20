# Source notes: liquidGL (NaughtyDuk)

Condensed study notes for one of the five libraries this plugin learned from. Nothing here is vendored; formulas are paraphrased or quoted briefly with attribution. Citations use `<repo-relative path>:line` in the upstream layout (repository `github.com/naughtyduk/liquidGL`). Almost all code is one file, `scripts/liquidGL.js` (8,982 lines); `package/liquidGL.js` is the same code with an ESM default export and an SSR guard.

Observed in the supplied archive on 2026-11-05. The archive is a snapshot, not necessarily the latest release. Recheck upstream before quoting a version or behavior.

## 1. Identity

| Field | Value | Evidence |
| --- | --- | --- |
| npm package | `liquid-gl` | `package/package.json` (`name`) |
| Version in archive | `3.0.0` | `package/package.json`, `scripts/liquidGL.js:7`, `README.md:5` |
| License | MIT, "Copyright (c) NaughtyDuk", for `scripts/` and `package/` only | `LICENSE:1-3`, `LICENSE:23-33` |
| Excluded assets | `assets/` (fonts, audio) "may not be copied, redistributed, or reused" | `LICENSE:23-33` |
| Module format | Browser IIFE assigning `window.liquidGL`; npm copy adds `export default` and returns early when `window` is undefined | `scripts/liquidGL.js:10`, `:8705` |
| Runtime deps | None ("own built-in rasteriser") | `README.md:81` |
| Dev helper | `scripts/liquidGL-helper.js` loads `lil-gui@0.19.1` from jsDelivr with SRI | `scripts/liquidGL-helper.js:37-42` |
| Size (measured from the archive) | `package/liquidGL.js` is 297,144 bytes unminified, about 61.6 KB gzip; no minified build ships | `gzip -c` on the archive file, 2026-11-05 |
| Tests, CI, changelog | None; release notes live in the README "What's New" | `README.md:18-36` |

**One-line summary.** Rasterizes the page (default `body`) into a texture with an in-house DOM painter ("NaughtyDOM"), then draws every lens in one shared WebGPU or WebGL canvas with a refraction fragment shader (`README.md:10`, `:46`, `scripts/liquidGL.js:332`, `:5458`).

## 2. Technique pipeline

1. `liquidGL(options)` merges defaults, parses `tint` through a 2D-canvas `fillStyle` probe, validates `zIndex`, and resolves `engine` (option or `?liquidGL-engine=` URL param) (`scripts/liquidGL.js:8705-8757`, `:222-279`).
2. Probe GPUs: WebGPU by `"gpu" in navigator`, WebGL by trying contexts. If neither exists, or `window.__liquidGLNoWebGL__` is true, apply the CSS fallback (`scripts/liquidGL.js:8759-8801`).
3. Group lenses into renderers keyed by snapshot target, nearest fixed or sticky ancestor, and zIndex. One renderer owns one canvas appended to that anchor (`scripts/liquidGL.js:8815-8838`, `:5470-5473`).
4. Pick a backend asynchronously: WebGPU, else WebGL2, WebGL, experimental-webgl; lenses created earlier are queued (`scripts/liquidGL.js:5652-5693`, `:198-203`).
5. Snapshot: rasterize the snapshot element at `min(resolution, maxTex / size)` with NaughtyDOM in 8 ms idle slices, skipping the canvas, `[data-liquid-ignore]`, lenses and content roots; retry 3 times (`scripts/liquidGL.js:5713-5835`, `:2201-2252`).
6. Upload the snapshot as a texture; patch dynamic regions later with sub-image uploads (`scripts/liquidGL.js:3282-3333`, `:4412-4465`).
7. Per frame, render only when a serialized "render signature" (viewport, scroll, rects, options, video frames) changed or something animates (`scripts/liquidGL.js:6085-6321`).
8. Per lens, map the lens rect into snapshot UV using the snapshot element's current client rect. Scrolling only changes these bounds; there is no recapture on scroll (`scripts/liquidGL.js:6668-6675`).
9. Stacked lenses: copy lower lens output into a stack texture and sample it over the snapshot (`scripts/liquidGL.js:2998-3008`, `:3659`).
10. Tilt copies the GL canvas into a per-lens 2D mirror canvas that is CSS 3D transformed (`scripts/liquidGL.js:6429-6474`, `:8630-8680`).

### Shader (paraphrased)

- Shape: the standard rounded-box distance `length(max(abs(p) - b + r, 0)) - r` (`scripts/liquidGL.js:3010-3012`), and a corner-aware normal that blends the radial direction toward the corner-arc normal with a smoothstep weight (`:3014-3023`).
- Bevel: `edge = 1 - smoothstep(0, bevelWidth * min(w, h), insideDistance)` (`scripts/liquidGL.js:3037-3041`).
- Offset: `offsetAmt = edge * refraction + edge^10 * bevelDepth`, multiplied by `smoothstep(0.15, 0.45, length(p))` so the centre stays still, along the corner-aware direction (`scripts/liquidGL.js:3063-3075`). This is a heuristic, not Snell's law, and there is no height function.
- Units: offsets are in snapshot UV, so the same `refraction` value moves pixels further on a larger snapshot (`scripts/liquidGL.js:6205-6227`).
- Out-of-bounds guard: fade back to the unrefracted coordinate when a sample leaves the texture (`scripts/liquidGL.js:3085-3087`).
- `magnify` zooms around the lens centre (`scripts/liquidGL.js:3080`).
- Sampling: 5-tap plus average without frost; 16 random-disc taps of radius `frost * 4` texels with frost (`scripts/liquidGL.js:3096-3121`).
- Chromatic aberration: red sampled at `-chroma`, blue at `+chroma`, with `chroma = offset * aberration`, so dispersion vanishes where the offset is zero (`scripts/liquidGL.js:3094`, `:3123-3126`). The README says blue moves further than red; the code splits them symmetrically.
- Tint: `mix(rgb, rgb * tint.rgb, tint.a)`, applied before the highlight so highlights stay white (`scripts/liquidGL.js:3139`).
- Specular: two soft blobs drifting with `u_time`, adding at most about 0.18; no rim, Fresnel or light direction (`scripts/liquidGL.js:3141-3148`). Being time driven, it forces continuous rendering (`scripts/liquidGL.js:6253-6260`).
- Shadow: CSS `box-shadow` normally; in fluid mode a GPU-blurred SDF mask sampled at 10% outside the shape with interleaved-gradient-noise dithering to stop banding (`scripts/liquidGL.js:2271-2298`, `:3051-3057`).
- Output is premultiplied (`scripts/liquidGL.js:3155-3156`, `:3678`).

WebGPU path: a line-for-line WGSL port with 64 floats of uniforms per lens in one dynamic-offset buffer; any shader compile error falls back to WebGL (`scripts/liquidGL.js:3732-3934`, `:4013`, `:4049-4057`).

Content children with CSS `backdrop-filter: blur() saturate()` are emulated on the GPU; other filter functions are not parsed (`scripts/liquidGL.js:2535-2596`).

NaughtyDOM paints backgrounds and gradients, borders, box shadows, text runs, inline SVG, canvas and form values, in CSS stacking order (`scripts/liquidGL.js:737-893`, `:1000-1068`, `:1882-1912`). It skips `<video>` (composited from live frames instead), `<iframe>`, pseudo-elements, CSS `filter`, `clip-path` and `mask` (`scripts/liquidGL.js:1513`).

## 3. API tables

### Functions and globals

| Symbol | Effect | Evidence |
| --- | --- | --- |
| `liquidGL(options)` | Returns one lens or an array; `undefined` when no targets match | `scripts/liquidGL.js:8705-8858` |
| `liquidGL.registerDynamic(target)` | Marks elements whose appearance changes so their snapshot region is re-rasterized | `scripts/liquidGL.js:8863-8868`, `:7597-7822` |
| `liquidGL.syncWith(config)` | Hands the loop to the GSAP ticker or its own rAF that also ticks Lenis or Locomotive | `scripts/liquidGL.js:8873-8981` |
| `window.__liquidGLNoWebGL__ = true` | Forces the CSS fallback | `scripts/liquidGL.js:8777` |
| `?liquidGL-engine=webgl2` | Overrides `engine` when it is `auto` | `scripts/liquidGL.js:8746-8750` |

### Options (defaults at `scripts/liquidGL.js:8706-8733`)

| Option | Default | Clamp or parse | Effect | Evidence |
| --- | --- | --- | --- | --- |
| `target` | `".liquidGL"` | | Elements to glassify | `scripts/liquidGL.js:8707` |
| `snapshot` | `"body"` | falls back to body | Refraction source | `scripts/liquidGL.js:5491-5493` |
| `resolution` | 2.0 | 0.1 to 3.0, then texture cap | Snapshot scale | `scripts/liquidGL.js:5577-5580` |
| `engine` | `"auto"` | unknown becomes auto | `webgpu`, `webgl2`, `webgl` | `scripts/liquidGL.js:198-203` |
| `zIndex` | element's effective z | integer or `TypeError` | Stacking and renderer grouping | `scripts/liquidGL.js:8736-8744` |
| `content` | target | selector or `false` | Live content layer | `scripts/liquidGL.js:5987-5990` |
| `refraction` | 0.01 | none | Linear offset across the bevel (snapshot UV) | `scripts/liquidGL.js:3065` |
| `aberration` | 0 | | RGB split proportional to offset | `scripts/liquidGL.js:3094` |
| `bevelDepth` | 0.08 | none | `edge^10` rim term | `scripts/liquidGL.js:3065` |
| `bevelWidth` | 0.15 | none | Bevel band as a fraction of the short side | `scripts/liquidGL.js:3039` |
| `frost` | 0 | none | 16-tap disc blur | `scripts/liquidGL.js:3096-3114` |
| `shadow` | true | | CSS or GPU SDF shadow | `scripts/liquidGL.js:8229-8281` |
| `specular` | true | | Two animated blobs | `scripts/liquidGL.js:3141-3148` |
| `reveal` | `"fade"` | anything else means none | 1000 ms linear fade-in | `scripts/liquidGL.js:8284-8331` |
| `tilt`, `tiltFactor`, `tiltEase` | false, 5 deg, 400 ms | ignored when draggable | 3D tilt via mirror canvas | `scripts/liquidGL.js:8355-8361`, `:8414` |
| `draggable` | false | | Pointer drag with `translate3d` | `scripts/liquidGL.js:8107-8185` |
| `interaction` | `"none"` | `"fluid"` | Viscous pointer deformation | `scripts/liquidGL.js:6478-6617` |
| `interactionStrength`, `interactionRadius` | 0.5, 0.35 | accepted 0 to 5 (README says 0 to 1) | Deformation size | `scripts/liquidGL.js:6599`, `:6634` |
| `interactionViscosity` | 0.65 | 0 to 1 | Follow and settle times | `scripts/liquidGL.js:6584-6586` |
| `magnify` | 1 | 0.001 to 3.0 | Source zoom | `scripts/liquidGL.js:6677-6683` |
| `tint` | null | any CSS color; alpha is dye strength | Multiplicative dye | `scripts/liquidGL.js:8735`, `:3139` |
| `helper` | false | needs helper script | lil-gui panel | `scripts/liquidGL.js:8847-8855` |
| `on.init`, `on.dragstart`, `on.drag`, `on.dragend` | | | Callbacks | `scripts/liquidGL.js:8693-8699`, `:8134-8178` |

### Lens methods

`destroy()`, `setTint(color)`, `setDraggable(bool)`, `setTilt(bool)`, `setShadow(bool)`, `updateMetrics()`, `clearDrag()`; options can also be mutated live on `lens.options` because the loop reads them every frame (`scripts/liquidGL.js:7854-8211`, `:6185-6200`).

Attribute hook: `data-liquid-ignore` excludes an element and its subtree from the snapshot and tracking (`scripts/liquidGL.js:5764-5773`). Only `borderTopLeftRadius` is read for the lens shape (`scripts/liquidGL.js:7990-8001`).

### README presets (`README.md:255-261`)

| Name | refraction | bevelDepth | bevelWidth | frost | shadow | specular |
| --- | --- | --- | --- | --- | --- | --- |
| Default | 0 | 0.052 | 0.211 | 2 | true | true |
| Alien | 0.073 | 0.2 | 0.156 | 2 | true | false |
| Pulse | 0.03 | 0 | 0.273 | 0 | false | false |
| Frost | 0 | 0.035 | 0.119 | 0.9 | true | true |
| Edge | 0.047 | 0.136 | 0.076 | 2 | true | false |

Pattern in the demos: UI chrome uses refraction about 0.006 to 0.01, bevelDepth 0.04 to 0.09 and frost 4 to 6; magnifier looks use refraction 0.07 to 0.15, bevelDepth about 0.2 and magnify 1.15 to 1.35 (`demos/frost-specular.html:1425-1463`, `demos/true-refraction.html:1089-1132`).

## 4. Motion

- Fluid interaction smooths a `[cx, cy, dx, dy]` state with time constants `follow = 1 - exp(-dt / (25 + viscosity * 180))` and `settle = 1 - exp(-dt / (80 + viscosity * 620))`; displacement is `min(size * 0.12, speed * 45) * strength`, decaying after the last move (`scripts/liquidGL.js:6584-6609`). It uses real `dt`, so it is frame-rate independent.
- The shader deforms the SDF itself near the pointer, so the outline bulges (`scripts/liquidGL.js:3029-3035`, `:3068-3074`).
- Tilt: rotation proportional to pointer offset, cubic ease-out, cancelled on scroll (`scripts/liquidGL.js:8377-8380`, `:8459`, `:8557-8572`).
- Drag has no inertia or snapping (`scripts/liquidGL.js:8107-8185`).
- No morph API; shape follows live rect and border radius. Position changes are re-measured every frame: the rAF loop calls `render()` (`scripts/liquidGL.js:21-29`), which calls `updateMetrics()` on every lens (`:6110`), and `updateMetrics()` reads `getBoundingClientRect()` except in tilt mirror mode, where it reuses `_baseRect` (`:7957-7962`). A demo comment says lenses refresh only via the ResizeObserver and calls `updateMetrics()` plus `render()` in a GSAP `onUpdate` (`demos/ai-search.html:719-727`); the 3.0.0 loop contradicts that comment, and the extra call renders twice per frame. Runtime behavior is unverified (code reading only).

## 5. Platform behavior

| Layer | Condition | Behavior | Evidence |
| --- | --- | --- | --- |
| WebGPU | adapter, device and clean WGSL compile | Primary; one cached device | `scripts/liquidGL.js:4016-4069` |
| WebGL2, WebGL, experimental | context creation succeeds | GLSL ES 1.0 shader | `scripts/liquidGL.js:2931-2968` |
| CSS fallback | no GPU detected up front | 7% white or tint background with `backdrop-filter: blur(12px)` | `scripts/liquidGL.js:8777-8801` |
| Late failure | WebGPU announced but fails, and WebGL throws | No CSS fallback; lenses keep original styles | `scripts/liquidGL.js:5681-5687` |
| WebGL context loss | | Not handled | no `webglcontextlost` listener in the file |

README claims Chrome, Safari, Firefox and Edge support, with the caveat that Safari can be unstable when lenses exceed half the viewport width or height (`README.md:301-313`). No UA sniffing in the code.

## 6. Performance notes

- One canvas and context per renderer group, not per lens; README says tested to 30 lenses (`README.md:274`).
- Snapshot is document sized and capped by `MAX_TEXTURE_SIZE` (default 8192), so long pages lose resolution; snapshot a smaller element (`scripts/liquidGL.js:5735-5749`, `README.md:293-295`).
- DPR capped at 2 (`scripts/liquidGL.js:5697`, `:6339`).
- The render signature itself costs layout reads every frame (`scripts/liquidGL.js:6160-6321`).
- `specular`, fluid motion and recent pointer activity force frames (`scripts/liquidGL.js:6253-6272`).
- Tilt copies the full GL canvas to 2D every frame per tilting lens (`scripts/liquidGL.js:6418-6442`).
- `preserveDrawingBuffer: true` (`scripts/liquidGL.js:2938`).
- Rasterizing `body` is main-thread work proportional to DOM size (`scripts/liquidGL.js:2251`).
- Heavy dynamic elements recapture at most every 250 ms; resize recapture is debounced 250 ms (`scripts/liquidGL.js:13`, `:7716-7723`, `:5517-5551`).

## 7. Accessibility

- No `prefers-reduced-motion`, `prefers-reduced-transparency` or `prefers-contrast` handling in the library (grep of `scripts/` finds none). Specular, fade, tilt and fluid run regardless.
- Non-draggable lenses get `pointer-events: none`, which disables clicks on the element; demos override it with `!important` (`scripts/liquidGL.js:7938`, `:8102`, `demos/ai-search.html:242`).
- No ARIA, roles or focus styling; drag has no keyboard alternative. The generated canvas, shadow div and mirror canvas are not `aria-hidden` (`scripts/liquidGL.js:5470-5473`, `:8255-8263`).
- Legibility advice is limited to raising content `z-index` and optionally `mix-blend-mode: difference` (`README.md:325`).

## 8. Known bugs and failure modes

1. Content that changes after init is not refracted until `registerDynamic()`; set initial animation states before calling `liquidGL()` (`README.md:161-180`, `:290`).
2. Preloaders and overlays get baked into the snapshot; mark them `data-liquid-ignore` (`README.md:271-272`).
3. Different zIndex values mean separate canvases (`README.md:273`, `scripts/liquidGL.js:8820-8825`).
4. Cross-origin images without CORS draw blank (`scripts/liquidGL.js:593-599`).
5. Pseudo-elements, CSS filters, clip-path, masks and iframes are missing from refraction (`scripts/liquidGL.js:1513`).
6. CSS animations are not refracted in real time; the README feature table marks this unsupported (`README.md:56`).
7. `clip-path` with tilt can make the lens vanish; use `border-radius` with `overflow: hidden` (`demos/frost-specular.html:505-512`).
8. Tilt caches the inline transform on first bind; animate a wrapper, not the lens (`demos/frost-specular.html:1353-1360`).
9. GSAP `clearProps: "all"` wipes library inline styles (`demos/ai-search.html:729-731`).
10. Per-corner and elliptical radii are ignored (`scripts/liquidGL.js:7990-8001`).
11. `_handleOverscrollCompensation()` is defined but never called (`scripts/liquidGL.js:8012-8074`).
12. Async GPU failure skips the CSS fallback (`scripts/liquidGL.js:5681-5687`).
13. `resolution` below 0.1 is silently clamped (`scripts/liquidGL.js:5577-5580`).

## 9. Borrow and avoid

Borrow:
- Rounded-box SDF plus corner-aware normal, so refraction follows any radius.
- Two-term bevel `edge * k1 + edge^10 * k2` with a centre dead zone: separate body refraction from a thin bright rim.
- Dispersion proportional to displacement.
- Change-signature render gating, with time-driven effects explicitly marked as animated.
- One shared canvas per stacking group and one shared GPU device.
- Stacked lenses via a stack texture.
- Ordered dither on low-alpha shadows.
- Integration lessons: content above the canvas, ignore attributes for overlays, animate wrappers under 3D tilt.

Avoid or adapt:
- Offsets in snapshot UV units; express strength in CSS px so it does not depend on page length.
- Whole-page DOM rasterization when a native backdrop path exists.
- `pointer-events: none` on interactive glass; missing reduced-motion and contrast handling.
- No fallback after async GPU failure and no context-loss handling.

## 10. License and attribution

MIT, "Copyright (c) NaughtyDuk", for `scripts/` and `package/` only (`LICENSE:1-21`). The fonts and audio under `assets/` are excluded from the grant and must not be copied (`LICENSE:23-33`). The helper loads lil-gui (MIT) from a CDN. Common shader idioms in the file (rounded-box SDF, `fract(sin(dot()))` hash, interleaved gradient noise) are unattributed public techniques. This plugin re-derives ideas and copies no code; copying code would require keeping the NaughtyDuk notice.
