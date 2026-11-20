# Performance of liquid glass style UI

Glass is expensive because it reads what is behind it. Every technique pays for that read somewhere: in the compositor (backdrop blur), in a filter graph that reruns while anything moves (SVG displacement), in map generation (CPU or GPU), or in copying the page into a texture (WebGL capture). This reference gives a cost model per tier, the caching and scheduling patterns the studied libraries use, the hard engine limits, and how to measure and budget.

## Source keys

Library claims cite `<library> <path>`: glasshq (paths under `packages/liquid-glass/`), simple-liquid-glass, liquidGL (`scripts/liquidGL.js` abbreviated as `liquidGL.js`), ybouane, liquid-glass-react. Numbers measured by a library author are labeled "author's measurement". Platform facts cite a URL and "checked 2026-11-05". **Inference** marks reasoning that was not measured.

## 1. Cost model per tier

Tier numbers follow [web-techniques.md](web-techniques.md#1-the-rendering-tiers).

| Tier | Where the cost lands | Grows with | Evidence |
| --- | --- | --- | --- |
| 1. CSS `backdrop-filter` blur | compositor/GPU, every frame the glass or its backdrop changes | glass area, blur radius (the blur reads beyond the box), number of overlapping surfaces | inference from how blurs work; WebKit charges each Gaussian blur an outset of `3 * (sigma * 0.75 * sqrt(2 * pi)) / 2` device px (glasshq `src/dom/filter-budget.ts`) |
| 2a/2b. SVG displacement in `backdrop-filter` or `filter: url()` | GPU pass per filter primitive per moving frame; map image bytes resent to the GPU process each moving frame | primitive count, filter region area, map resolution, pane count (each pane is its own pass) | simple-liquid-glass `CHANGELOG.md`, `src/core/nativeMapGeometry.ts` |
| 2c. Filter on a content layer with baked maps | one filter over the content element; maps rendered once | content layer area (Safari "can spend substantially longer filtering large content layers"), number of surfaces in the graph | glasshq `README.md`, `src/dom/index.ts` |
| Map generation on the CPU | main thread, once per size change | width x height | liquid-glass-react `src/shader-utils.ts` |
| Map generation on the GPU | one atlas draw and one readback per batch, then PNG encode in a worker | batch size, map DPR | glasshq `src/gpu/index.ts`, `src/dom/map-encoder.ts` |
| 3. WebGL over a captured backdrop | DOM serialization and rasterization, CPU to GPU upload, shader passes, sometimes GPU to 2D readback | DOM size of the captured region, capture resolution, frequency of recapture, number of glass panes | ybouane `src/LiquidGlass.ts`, `src/GlassRenderer.ts`; liquidGL `liquidGL.js` |

### 1.1 Backdrop blur

- Large blur radii on large surfaces are the most common silent cost. Keep blur on the small floating surfaces it is meant for. (Inference: browsers usually downsample for big radii, so cost does not grow linearly forever, but area always matters.)
- Each `backdrop-filter` reads the backdrop separately. Stacking several glass surfaces over each other multiplies the work. simple-liquid-glass avoids per-ripple `backdrop-filter` for this reason: "each forces a new GPU backdrop snapshot" (simple-liquid-glass `src/interactive/index.tsx`).
- A blurred panel outside the viewport still costs if it is rendered. simple-liquid-glass drops `backdrop-filter` and releases WebGL work when a surface leaves an `IntersectionObserver` with a 200 px root margin (simple-liquid-glass `src/core/useGeometry.ts`).

### 1.2 SVG filter chains

- **Every primitive is a pass.** simple-liquid-glass shortened its graph to one `over` composite instead of a mask plus three composites, and replaced 16 frost maps with one map plus a matched `feGaussianBlur` (simple-liquid-glass `src/core/LiquidGLSvgFilter.tsx`, `CHANGELOG.md`).
- **Every pane is a pass.** Author's measurement: CPU time grew linearly with SVG panes, 829 versus 347 ms per second for 24 scrolling panes after moving crowds to a shared WebGL scene (simple-liquid-glass `CHANGELOG.md`).
- **Map bytes are a per-frame cost.** Chromium resends a backdrop filter's `feImage` map whenever the glass or its backdrop moves, so simple-liquid-glass sizes maps at 0.75 map px per CSS px of the longer side, clamped to 64..512 (simple-liquid-glass `src/core/nativeMapGeometry.ts`).
- **Filter region is area.** liquid-glass-react uses a 170% filter region on each axis, about 2.9 times the pixel area (inference from the attribute), with 17 filter primitives including three `feDisplacementMap` passes for chromatic aberration (liquid-glass-react `src/index.tsx`).
- **Subregions.** glasshq gives every primitive an explicit subregion: "Without a subregion every primitive covers the whole filter region." Sampling stages get the reach box; pointwise stages get only the lens box (glasshq `src/dom/index.ts`).

### 1.3 Map generation: CPU versus GPU

| Approach | Cost | Example |
| --- | --- | --- |
| CPU loop per pixel, `toDataURL` | O(width x height) synchronous JavaScript on the main thread; re-run on every size change; no cache across instances | liquid-glass-react shader mode builds a `number[]` of 2 x w x h with `push`, then encodes a PNG (liquid-glass-react `src/shader-utils.ts`, `src/index.tsx`) |
| Baked image stretched to size | free at runtime, but soft or banded on large or high-DPR surfaces; JPEG maps add block noise to vector data | liquid-glass-react `src/utils.ts` (256 x 256 maps) |
| GPU atlas | requests in one task batched into an atlas (up to 32 shapes per pass), one draw, one readback; PNG encoded in a Web Worker with a hand-written encoder, never a canvas, because canvas encoding "competes with the compositor" | glasshq `src/gpu/index.ts`, `src/dom/png.ts`, `src/dom/map-encoder.ts` |
| Analytic shader per frame | no maps; cost moves to fragment shader taps | liquidGL: 5 taps without frost, 16 with frost, 48 with frost plus aberration (liquidGL `liquidGL.js`) |

Rules from these: generate maps off the main thread or on the GPU; cache them by geometry; decode before swapping (glasshq hands out maps only after `Image.decode()` so a filter switch draws in the same frame, glasshq `src/dom/maps.ts`); use lower-density maps while shapes move (glasshq uses 1x maps in motion, "a quarter of the pixels", glasshq `src/dom/index.ts`).

### 1.4 WebGL capture

- **Capture.** DOM-to-canvas serialization (html-to-image, or liquidGL's own rasterizer) clones the DOM, inlines styles and fonts, and rasterizes. ybouane calls it "expensive" and advises small, shallow wrappers (ybouane `README.md`). liquidGL rasterizes in 8 ms chunks during idle time, still proportional to DOM size (liquidGL `liquidGL.js`).
- **Upload.** `texImage2D` of a 2D canvas each time the region under a glass changes (ybouane `src/GlassRenderer.ts`).
- **Shader work.** ybouane runs up to 15 draws per re-shaded glass: blit, copy, 12 blur passes, glass pass, at full panel resolution (ybouane `src/GlassRenderer.ts`).
- **Readback.** ybouane copies the shared WebGL canvas into a per-glass 2D canvas with `drawImage`, which needs `preserveDrawingBuffer: true` (ybouane `src/GlassRenderer.ts`, `src/LiquidGlass.ts`). liquidGL's tilt copies the full canvas to a 2D canvas every rendered frame per tilting lens (liquidGL `liquidGL.js`). Inference: GPU to 2D copies can force synchronization; avoid them per frame.
- **Recapture triggers.** Scrolling should not recapture: both liquidGL and simple-liquid-glass capture once and move sample coordinates on scroll (liquidGL `liquidGL.js`; simple-liquid-glass `README.md`). Content changes do: liquidGL throttles heavy recaptures to every 250 ms; simple-liquid-glass debounces HTML recapture by 120 ms (liquidGL `liquidGL.js`; simple-liquid-glass `src/core/webgl/source.ts`).

## 2. Caching

| Cache | Key | Bound and eviction | Source |
| --- | --- | --- | --- |
| Material maps in memory | `[width, height, radius, dpr, appearance, outline, sliceCapsule]` | beyond 64 entries, evict the oldest not drawn for 10 s; decoded `Image` kept with each map | glasshq `src/dom/maps.ts` |
| Map version | FNV-1a hash of shader source plus encoder tag | shader changes never reuse stale maps | glasshq `src/dom/maps.ts` |
| Maps on disk | same key, in IndexedDB store `liquid-glass/maps` | LRU 256 entries; batched reads and writes; writes deferred 400 ms; stale versions purged after 5 s; preload dropped after 30 s | glasshq `src/dom/map-store.ts` |
| First-paint maps | maps claimed in the first 4 s, in `localStorage` (up to 3,000,000 chars), written after 2.5 s | read synchronously because "IndexedDB answers in a task, which cannot run while a framework is still mounting" | glasshq `src/dom/map-store.ts` |
| Displacement map data URIs | geometry and parameters | LRU 64 (an unbounded cache leaked in long-lived apps before 2.2.0) | simple-liquid-glass `src/displacementCache.ts`, `CHANGELOG.md` |
| Shader programs | per WebGL context | shared, ref-counted, 12 idle kept | simple-liquid-glass `src/vendor/ybouane/GlassRenderer.ts` (vendored from ybouane and extended) |
| Textures | context plus source and version | partial `texSubImage2D` patches | simple-liquid-glass `src/core/webgl/textureCache.ts` |
| Backdrop sources | element (WeakMap) | one MutationObserver and ResizeObserver per source | simple-liquid-glass `src/core/webgl/source.ts` |
| HTML captures | element, device-pixel size | fresh within 0.5 px; stale ones stretch-drawn while an async recapture runs; concurrent captures deduplicated | ybouane `src/HtmlCapture.ts` |
| FBO pool | `"WxH"` | flushed on window resize | ybouane `src/GlassRenderer.ts` |

**Only cache resting shapes persistently.** glasshq stores only resting shapes; transient morph shapes render without waiting on the store (glasshq `src/dom/maps.ts`). Morph paths are better prepared ahead in memory ([motion.md](motion.md#4-morphing-shapes)).

**Shared contexts and devices.**

- One WebGPU device and one compiled pipeline for every scene (glasshq `src/gpu/index.ts`); one shared device across liquidGL renderers (liquidGL `liquidGL.js`).
- One offscreen WebGL context for all own-canvas panels, disposed with `WEBGL_lose_context` when the last user leaves (simple-liquid-glass `src/core/webgl/contextPool.ts`).
- One canvas per renderer group (snapshot, anchor, z-index), not per lens (liquidGL `liquidGL.js`).
- ybouane opens one WebGL context per `LiquidGlass` instance and warns that browsers cap concurrent contexts, "typically 16 system-wide" (ybouane `README.md`). Share one context per page.
- Ref-count anything shared and release it when the count reaches zero; invalidate every cache keyed to a context on `webglcontextlost` (simple-liquid-glass `src/core/webgl/runtime.ts`; ybouane `src/GlassRenderer.ts`).

## 3. Device pixel ratio

| Library | DPR policy | Source |
| --- | --- | --- |
| glasshq | map DPR capped at 2; lowered down to 0.25 for very large surfaces instead of failing; 1x during motion | glasshq `src/gpu/geometry.ts`, `src/dom/index.ts` |
| liquidGL | capped at 2 everywhere | liquidGL `liquidGL.js` |
| simple-liquid-glass | WebGL `min(DPR, 3 or 2, maxScale)`; engine default `min(DPR, 2)`, 1.5 on its lite tier; SVG liquidGL maps at density `min(DPR, 0.75)` | simple-liquid-glass `src/core/webgl/runtime.ts`, `src/core/engine/engine.ts`, `src/core/svgLiquidGL.ts` |
| ybouane | all shader lengths scaled by DPR except blur, so blur looks weaker on high-DPR screens | ybouane `src/GlassRenderer.ts` |
| liquid-glass-react | maps generated at CSS px (`canvasDPI = 1`) | liquid-glass-react `src/shader-utils.ts` |

**Our rule:** cap glass rendering at DPR 2. Refraction fields are smooth, so extra density buys little (simple-liquid-glass's comment calls 0.75 map px per CSS px "visually indistinguishable" from 512, `src/core/nativeMapGeometry.ts`). Scale every length (blur, bezel, displacement) by the same DPR you render at. Re-read DPR on `resize` and when a `matchMedia('(resolution: Xdppx)')` query changes, since windows move between screens.

## 4. Instance limits and the 16-pane heuristic

Three libraries converge on roughly 16 as the point where per-surface rendering stops scaling:

| Library | Limit | Behavior | Source |
| --- | --- | --- | --- |
| simple-liquid-glass | `CROWD_ON = 16`, `CROWD_OFF = 12` | at 16 scene-eligible sibling panes on desktop Chromium, switch from per-pane SVG to one shared WebGL canvas; switch back below 12 so a list that grows and shrinks does not flap | simple-liquid-glass `src/core/webgl/crowd.ts` |
| glasshq | `maxSurfaces` default 16, clamped 1..64 | `addSurface` throws past the limit, suggesting a split scene | glasshq `src/react/scene.tsx`, `src/dom/index.ts` |
| ybouane | about 16 WebGL contexts | browser cap on contexts; share one | ybouane `README.md` |
| liquidGL | README says tested to 30 lenses | `shadow`, `specular` and `tilt` "can clog the render pipeline" with many instances | liquidGL `README.md` |

Author's measurements: 104 scrolling panes at 60 fps with 531 ms/s Chrome CPU in simple-liquid-glass 5.6, versus 35 fps (SVG) and 12 fps (WebGL) in 5.5.1 (simple-liquid-glass `README.md`); 48 WebKit panes over a live canvas went from 25 to 50 fps after sharing one upload; 48 blurred panes on a Galaxy A54 from 9 to 42 fps with a shared blur (simple-liquid-glass `CHANGELOG.md`).

**Our rule:** design for at most a handful of refractive surfaces visible at once. If a layout needs more than about 12, render them through one shared canvas or downgrade the extras to frosted CSS, with hysteresis between the two modes.

## 5. Resize and scroll

- **Measure with `ResizeObserver`, not only `window.resize`.** liquid-glass-react and ybouane listen to window resize only, so content or font changes leave maps and overlays stale (liquid-glass-react `src/index.tsx`; ybouane `src/LiquidGlass.ts`).
- **Measure layout size, not the transformed rect.** `getBoundingClientRect()` includes scale; simple-liquid-glass switched to `offsetWidth/Height` after entrance animations left maps undersized (simple-liquid-glass `CHANGELOG.md`, `src/core/useGeometry.ts`); ybouane does the same to avoid resize loops from hover scale (ybouane `src/LiquidGlass.ts`).
- **Debounce expensive rebuilds.** liquidGL resizes its canvas immediately but recaptures after a 250 ms debounce, and defers resizes until 200 ms after scrolling stops (liquidGL `liquidGL.js`).
- **Avoid rebuilding during live resize.** glasshq renders wide capsules from one 3 x height map sliced into caps and middle while a capsule is resizing, so a width change does not need a new map (glasshq `src/dom/map-image.ts`, `src/dom/index.ts`). It also resizes its SVG host only when content size changes, because resizing it invalidates every filter (glasshq `src/dom/index.ts`).
- **Scroll without work.** Position lenses in content coordinates (glasshq `src/dom/index.ts`) or move sample coordinates (liquidGL, simple-liquid-glass), never recapture or rebuild on scroll. Use passive listeners; simple-liquid-glass removed synchronous non-passive scroll handlers (simple-liquid-glass `CHANGELOG.md`).
- **Layer promotion only while moving.** glasshq adds `will-change: transform` to a moving surface for 400 ms so Chromium does not refilter the whole content layer (glasshq `src/dom/index.ts`); simple-liquid-glass removed permanent `will-change` pinning (simple-liquid-glass `CHANGELOG.md`).
- **Pinch zoom.** liquidGL skips resize handling while `visualViewport.scale !== 1` (liquidGL `liquidGL.js`); glasshq turns repaint padding off while magnified (glasshq `src/dom/page-zoom.ts`).

## 6. Frame scheduling and skipping

- **One `requestAnimationFrame` loop per window, with a read phase before writes.** glasshq runs one driver for all tickers with separate read and write phases (glasshq `src/dom/ticker.ts`); simple-liquid-glass measures in one phase and memoizes rects for the frame (simple-liquid-glass `src/core/webgl/contextPool.ts`).
- **Sleep when idle.** glasshq's ticker wakes on input, scroll, resize, mutation, CSS transition and animation events and `visibilitychange`, plus a 1 s heartbeat, and sleeps after 3 idle frames; it ignores mutations caused by its own SVG and layers (glasshq `src/dom/ticker.ts`, `src/dom/index.ts`).
- **Dirty tracking.** ybouane re-shades a glass only when it is dirty, moved more than 0.5 px, sits over a re-rendered glass or dynamic content, or is dragged; the loop returns early when nothing is dirty (ybouane `src/LiquidGlass.ts`). liquidGL compares a per-frame signature of rects and options and renders only on change, though building that signature costs layout reads every frame (liquidGL `liquidGL.js`).
- **Throttle rebuilds.** glasshq throttles filter rebuilds during motion to about 60 Hz: "rebuilding at 60 Hz lands every frame on time instead of alternating one and two" (glasshq `src/dom/index.ts`).
- **Hold still while waiting.** While a surface waits for its maps, glasshq freezes animation time ("quiet") to free the GPU (glasshq `src/dom/index.ts`, `src/dom/interaction.ts`).
- **Skip hidden work.** Skip rendering when `document.hidden` and hide off-screen canvases (liquidGL `liquidGL.js`).
- **Warm up.** glasshq requests the GPU device 600 ms after scene creation and submits a 4 x 4 dummy render, because "a fresh device's first work is held back while the page keeps painting"; GPU code is lazy-imported (glasshq `src/dom/index.ts`, `src/gpu/index.ts`, `src/dom/renderer.ts`).
- **Avoid continuous rendering by default.** liquidGL's `specular: true` renders every frame while visible (liquidGL `liquidGL.js`).

## 7. Engine limits

| Limit | Engine | Consequence | Mitigation | Source |
| --- | --- | --- | --- | --- |
| Filter buffer clamped to 4096 x 4096 device px | WebKit (software reference filters) | past the clamp the result is drawn stretched, so "glass lands away from its surface" | keep box plus summed outsets inside the budget (glasshq uses 90% of 4096 squared) and scale blur and displacement down proportionally when it would overflow | glasshq `src/dom/filter-budget.ts` |
| Outsets summed along filter chains and across graph branches | WebKit | many blurs or displacements in one graph exhaust the budget | share one frosted backdrop between surfaces; cluster branches by area | glasshq `src/dom/filter-budget.ts`, `src/dom/shared-backdrop.ts`, `src/dom/filter-groups.ts` |
| Layer tiling above 2048 pt (1024 on touch) | WebKit | each tile needs about twice the reach | extend reach; kernel capped at 500 px, so chain blurs | glasshq `src/dom/page-zoom.ts`, `src/dom/filter-reach.ts` |
| Reference filters reapplied on every paint (caret blink, hover) | WebKit | whole content layer refiltered | give content its own compositing layer with `will-change: transform` | glasshq `src/dom/filter-paint-root.ts` |
| 64 filter operations per element | Gecko | a larger graph errors (glasshq raises a RangeError for its progressive blur) | count primitives; split per surface | glasshq `src/dom/progressive.ts`, `src/dom/maps.ts` |
| Software filters re-rasterize on every paint | Gecko | any repaint reruns image-based filters | per-surface `-moz-element()` layers, so "An unchanged layer is never rasterized again" | glasshq `src/dom/lens-layers.ts` |
| Elements over half the viewport | Safari (liquidGL) | "can be unstable" | keep lenses small | liquidGL `README.md` |
| `MAX_TEXTURE_SIZE` (8192 default assumed by liquidGL) | WebGL | long documents lose capture resolution | snapshot a smaller background container | liquidGL `liquidGL.js`, `README.md` |
| HTML capture budget | simple-liquid-glass | 16 MP pixel budget, 16384 px dimension limit | partial capture of independent sections | simple-liquid-glass `src/core/webgl/alignedCaptureScale.ts`, `src/core/webgl/partialCapture.ts` |

The specific bug behind each limit is in [gotchas.md](gotchas.md#engine-specific-rendering).

## 8. Measuring

Measure on the slowest device you support, with the real backdrop, while the glass moves (scroll under it, drag it, open a morphing menu). Idle measurements say little.

**Chrome DevTools**

1. Performance panel: record an interaction, with CPU throttling (4x or 6x) on a desktop run. Look for long tasks during map generation, "Recalculate Style" and "Layout" triggered by pointer moves, and long "Paint" or "Composite Layers" during scroll.
2. Rendering drawer: Paint flashing (whole content layer flashing while only a lens moves means the filter covers too much), Layer borders, and Frame Rendering Stats.
3. Rendering drawer emulation for `prefers-reduced-transparency` and `prefers-reduced-motion`, to measure fallback paths too.

**In the field, with PerformanceObserver.** Long Animation Frames attribute slow frames to scripts. Support was not re-checked for this snapshot; feature-detect it.

```js
if (PerformanceObserver.supportedEntryTypes?.includes('long-animation-frame')) {
  new PerformanceObserver((list) => {
    for (const frame of list.getEntries()) {
      if (frame.duration < 50) continue;
      report({
        duration: frame.duration,
        blocking: frame.blockingDuration,
        scripts: frame.scripts?.map((s) => `${s.sourceURL}:${s.sourceFunctionName}`),
      });
    }
  }).observe({ type: 'long-animation-frame', buffered: true });
}
```

**Frame pacing during an animation.**

```js
function sampleFrames(durationMs = 2000) {
  return new Promise((resolve) => {
    const deltas = [];
    let last = performance.now();
    const end = last + durationMs;
    requestAnimationFrame(function tick(now) {
      deltas.push(now - last);
      last = now;
      if (now < end) requestAnimationFrame(tick);
      else {
        deltas.sort((a, b) => a - b);
        resolve({ p50: deltas[deltas.length >> 1], p95: deltas[Math.floor(deltas.length * 0.95)] });
      }
    });
  });
}
```

Trigger the interaction, call `sampleFrames()`, compare p95 to the frame budget (16.7 ms at 60 Hz, 8.3 ms at 120 Hz).

**Library diagnostics.** glasshq reports `{surfaces, maps, mapTime, error?}` through `onDiagnostic` and a `glass:diagnostic` event (glasshq `src/dom/index.ts`). simple-liquid-glass exposes `data-glass-strategy` and `data-glass-reason` (simple-liquid-glass `src/index.tsx`). Log these with your timings so a slow device can be traced to its tier.

## 9. Budgets

These are this plugin's starting budgets, not standards. Adjust them from measurements on your slowest target device.

| Budget | Value | Why |
| --- | --- | --- |
| Frame time during glass interaction | p95 within the refresh budget (16.7 ms at 60 Hz) | dropped frames read as jank exactly where glass draws attention |
| Glass script per frame | at most 4 ms of main thread | leaves room for the app's own work |
| Map generation | off the main thread, or under one frame per map; never on pointer move | liquid-glass-react's per-size CPU loop is the counter-example |
| Visible refractive surfaces | 3 to 6 typical; switch strategy at about 12 to 16 | section 4 |
| Blur radius on large surfaces (wider than half the viewport) | prefer standard frosted materials or a solid surface; refraction only on small controls | WebKit buffer clamp, Safari instability, compositor cost |
| Recapture (Tier 3) | never on scroll; content changes debounced 120 to 250 ms | section 1.4 |
| Rendering DPR | at most 2 | section 3 |
| Continuous animation | none at rest | section 6 |
| First paint | solid or frosted fallback visible immediately; refraction may arrive later | cached maps (glasshq) or a staged reveal (simple-liquid-glass waits up to 400 ms, `src/index.tsx`) |

## Related references

- [web-techniques.md](web-techniques.md) for the tiers and detection
- [gotchas.md](gotchas.md) for the engine bugs behind the limits
- [motion.md](motion.md) for pointer handling without re-renders
- [library-matrix.md](library-matrix.md) for library choice
