# Web techniques for liquid glass style UI

This reference compares the ways a browser can render refractive glass, explains how to layer them with progressive enhancement, and lists the integration traps in React, Vue, Svelte, web components and server rendering. For the optics each tier approximates, see [optics.md](optics.md). For engine versions, see [browser-support.md](browser-support.md).

## Source keys

Claims about a library cite `<library> <path>`: glasshq (`@glass-sdk/liquid-glass`, paths under `packages/liquid-glass/`), simple-liquid-glass, liquidGL, ybouane (`@ybouane/liquidglass`), liquid-glass-react. Platform facts cite a URL and the date they were checked. **Inference** marks reasoning that was not observed in a browser.

## 1. The rendering tiers

| Tier | Technique | Refraction | Engines that render it fully (as of 2026-11-05) | Studied examples |
| --- | --- | --- | --- | --- |
| 0 | Solid surface | none | all | the required fallback for every tier |
| 1 | CSS frost: `backdrop-filter` blur and saturate, tint, rim | none | Chromium, Firefox, Safari (prefixed before 18) | simple-liquid-glass fallback, liquidGL fallback |
| 2a | SVG displacement inside `backdrop-filter: url(#f)` | live page | Chromium only | simple-liquid-glass lens path |
| 2b | SVG `filter: url(#f)` on a backdrop-filtered layer | live page | Chromium only (per the library) | liquid-glass-react |
| 2c | SVG filter on an explicit content layer, with baked maps | content layer only | Chromium, WebKit; Firefox through `-moz-element()` layers | glasshq |
| 3 | WebGL over a captured backdrop | captured snapshot | all engines with WebGL | ybouane, liquidGL, simple-liquid-glass (non-Chromium default) |
| 4 | WebGPU, either baking maps or rendering lenses | depends on tier it feeds | engines with WebGPU | glasshq (bakes maps), liquidGL (renders lenses) |

### Tier 1: CSS frost

```text
page pixels behind the element
  -> backdrop-filter: blur(Npx) saturate(S%)
  -> background: translucent tint or top-lit gradient
  -> box-shadow: inset rims + soft outer shadow
  -> ::before / extra span: 1px gradient ring via mask-composite
  -> content on top
```

- simple-liquid-glass's fallback: `blur(8 to 11px) saturate(>= 180%)`, a 168 degree white gradient from 50% to 0% alpha, inset top and bottom rims and a hairline ring (simple-liquid-glass `src/index.tsx`).
- liquidGL's fallback: `rgba(white, 0.07)` or the tint, plus `backdrop-filter: blur(12px)` with the `-webkit-` prefix (liquidGL `scripts/liquidGL.js`).
- The rim ring trick: `padding: 1.5px; mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); mask-composite: exclude` with the `-webkit-` pair `xor` (liquid-glass-react `src/index.tsx`).

Pros: one declaration, compositor accelerated, no JavaScript, works across engines. Cons: no bending, so it reads as frosted plastic unless rims and gradients carry the depth.

### Tier 2a: SVG displacement as a backdrop filter

```text
displacement map (PNG data URL, generated per size)
  -> <svg><filter id="f-123"> feFlood neutral -> feImage map -> feComposite over
                              -> feDisplacementMap (one or three passes)
                              -> optional specular add </filter></svg>
glass layer: backdrop-filter: saturate(S%) blur(Bpx) url(#f-123)
content layer above, unfiltered
```

simple-liquid-glass builds this graph from `materialFilterStages` and applies it to its glass layer (simple-liquid-glass `src/core/materialFilter.ts`, `src/index.tsx`). It enables the path only when the user agent is Chromium and not iOS, because WebKit and Gecko ignore `url()` inside `backdrop-filter` (simple-liquid-glass `src/core/renderer.ts`).

Pros: refracts the live page, including video, canvas and scrolling content, with no capture step. Cons: Chromium only; every pane is its own GPU pass; map bytes are resent each moving frame (simple-liquid-glass `CHANGELOG.md`, `src/core/nativeMapGeometry.ts`).

### Tier 2b: CSS filter on a backdrop-filtered layer

```text
span.warp { backdrop-filter: blur() saturate(); filter: url(#f); }   (inset: 0 inside the glass box)
  -> filter post-processes the span's painted output, which includes its backdrop
children in a sibling div with z-index: 1, never filtered
```

liquid-glass-react uses this combination and states that displacement is visible only in Chromium; it skips the `filter` on Firefox by user-agent check (liquid-glass-react `src/index.tsx`, `README.md`). WebKit bug 297770 ("filter: url() ignored when backdrop-filter applied") is REOPENED, last change 2026-08-31 (https://bugs.webkit.org/show_bug.cgi?id=297770, checked 2026-11-05, High).

Pros and cons match 2a; the extra wrapper makes it easier to keep children sharp.

### Tier 2c: filter on an explicit content layer (glasshq)

```text
GlassScene
  GlassContent (the only thing that is refracted: text, images, SVG)
  GlassSurface x N (transparent, positioned above)

per frame: measure rects -> request maps by [w, h, radius, dpr, appearance, outline]
maps: WGSL atlas render on WebGPU -> PNG (worker) -> data: URL -> Image.decode()
filter on GlassContent: per surface feImage map -> frost -> feDisplacementMap
  -> tone/tint -> feComposite in coverage -> overlay light
  -> sparse merge back into the content in paint order
```

The content element receives one SVG filter that replaces its own pixels inside each surface footprint (glasshq `src/dom/index.ts`, `src/dom/compose-layers.ts`). Maps are cached in memory, in IndexedDB and in a synchronous localStorage first-paint set, so resting glass draws without a GPU on reload (glasshq `src/dom/maps.ts`, `src/dom/map-store.ts`).

Firefox path: each surface gets an `aria-hidden` child layer whose `background-image` is `-moz-element(#content)`, with its own small filter, because Gecko filters with images re-rasterize on every paint (glasshq `src/dom/lens-layers.ts`).

Pros: text stays live and selectable; parity across three engines; no screenshots. Cons: only the declared content layer refracts; no native video composition or transformed ancestors (glasshq `README.md`); engine-specific workarounds for WebKit buffer limits, zoom and tiling; requires WebGPU to bake new maps.

### Tier 3: WebGL over a captured backdrop

```text
backdrop element (must not contain the glass)
  -> rasterize: html-to-image (SVG foreignObject) or a custom DOM painter
     video/canvas: drawImage directly
  -> upload texture (crop per pane or one shared texture)
  -> optional separable blur in FBOs
  -> fragment shader: SDF mask, refraction, dispersion, light, shadow
  -> present into a canvas behind the glass's live DOM content
```

| Library | Capture | Canvas layout | Source |
| --- | --- | --- | --- |
| ybouane | html-to-image per direct child of `root`; root's own background never captured | one hidden WebGL canvas, copied into a per-glass 2D canvas at `z-index:-1` | ybouane `src/LiquidGlass.ts`, `src/GlassRenderer.ts` |
| liquidGL | custom "NaughtyDOM" painter rasterizes the `snapshot` element (default `body`) once; scroll only moves UV bounds | one shared canvas per (snapshot, fixed/sticky anchor, zIndex) group | liquidGL `scripts/liquidGL.js` |
| simple-liquid-glass | vendored html-to-image into a canvas; `backdropRef` or `backdropSelector` names a sibling | shared offscreen context; crowds of panes share one canvas | simple-liquid-glass `src/core/webgl/source.ts`, `src/core/webgl/runtime.ts` |

Pros: works in every engine with WebGL; full shader control (Snell, Fresnel, multi-light). Cons: the backdrop is a copy, so anything the capture cannot draw is missing (section 5); capture is main-thread work; changes need explicit invalidation; WebGL context limits.

### Tier 4: WebGPU

- **Baking maps (glasshq).** A WGSL shader renders displacement plus coverage and a light overlay for up to 32 shapes per atlas pass, with one readback per task batch. The maps then feed SVG filters, so the per-frame path stays SVG (glasshq `src/gpu/maps.wgsl`, `src/gpu/index.ts`).
- **Rendering lenses (liquidGL).** WebGPU is the first backend tried; a WGSL port of the GLSL lens shader draws all lenses into one canvas; any WGSL compile error falls back to WebGL (liquidGL `scripts/liquidGL.js`).

Pros: batching and compute headroom. Cons: device loss and adapter failure paths must fall back. liquidGL leaves lenses unstyled when async GPU setup fails after the synchronous check passed (liquidGL `scripts/liquidGL.js`).

## 2. When to pick each tier

1. **Default to Tier 1 with a Tier 0 fallback.** It covers every engine and every accessibility preference. Add refraction only where it earns attention: a hero lens, a floating control, a tab indicator.
2. **Chromium-heavy audience, live backdrop (video, scrolling feed):** add Tier 2a or 2b on top of Tier 1, gated by engine.
3. **Need parity in Safari and Firefox, content is a known region you control:** Tier 2c (glasshq's model) or Tier 3.
4. **Need refraction over arbitrary page content in Safari:** Tier 3, with a named sibling backdrop and a plan for capture gaps.
5. **Many panes at once:** prefer a shared canvas (Tier 3 crowd mode) over many SVG panes. simple-liquid-glass switches 16 or more Chromium panes to one WebGL scene and back below 12 (simple-liquid-glass `src/core/webgl/crowd.ts`).
6. **Native app:** use the platform material instead; see [native.md](native.md).

## 3. Progressive enhancement and detection

Build from the bottom up so every failure lands on a designed state.

```css
.glass {
  /* Tier 0: always valid */
  background: var(--glass-solid, rgb(245 245 247));
}
@supports ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px))) {
  .glass {
    /* Tier 1 */
    background: var(--glass-tint, rgb(255 255 255 / 0.18));
    -webkit-backdrop-filter: blur(12px) saturate(160%);
    backdrop-filter: blur(12px) saturate(160%);
  }
}
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more), (forced-colors: active) {
  .glass {
    background: var(--glass-solid, rgb(245 245 247));
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }
}
/* Tier 2 and 3 are opt-in classes added by script after detection. */
```

Detection rules:

- `@supports` proves the property parses, not that `url()` displacement renders. No CSS test can detect Tier 2 rendering, so gate it by engine (https://bugs.webkit.org/show_bug.cgi?id=245510, https://bugzilla.mozilla.org/show_bug.cgi?id=1961378, checked 2026-11-05, High for bug status).
- Every iOS browser is WebKit, and iPadOS reports a Macintosh user agent; simple-liquid-glass treats "Macintosh" with `maxTouchPoints > 1` as iOS (simple-liquid-glass `src/core/renderer.ts`). glasshq also checks `navigator.vendor === "Apple Computer, Inc."` (glasshq `src/dom/engine.ts`).
- WebGL: try `getContext("webgl2")`, then `"webgl"`, and handle `webglcontextlost`. WebGPU: `"gpu" in navigator` is only a hint; adapter or device requests can still fail (liquidGL `scripts/liquidGL.js`).
- Safari does not expose Reduce Transparency to CSS (https://bugs.webkit.org/show_bug.cgi?id=175497, checked 2026-11-05, High). Offer an in-app "solid surfaces" setting (the attribute `data-glass-surfaces="solid"` on `<html>`, which the bundled engine honors live) and treat `prefers-contrast: more` as a proxy.
- Publish the chosen tier for review tooling: simple-liquid-glass sets `data-glass-strategy` and `data-glass-reason`; glasshq sets `data-glass-ready` and emits `glass:diagnostic` (simple-liquid-glass `src/index.tsx`; glasshq `src/dom/index.ts`).

A full detection sketch is in [browser-support.md](browser-support.md#3-detection-sketch). Why parse-level tests and UA checks fall short, and how the plugin's probe checks real rendering instead: [Render-level detection](#render-level-detection).

## 4. Framework integration

### 4.1 Rules for every framework

1. **One filter id per instance.** Two glass instances with the same `id` make both use whichever filter the document finds first. liquid-glass-react emits `id="feimage"` in every instance (liquid-glass-react `src/index.tsx`). glasshq's patcher throws on duplicate filter `result` names (glasshq `src/dom/filter-patch.ts`).
2. **Make ids safe inside `url(#...)`.** React 18 `useId()` values look like `:r0:`. liquid-glass-react places them unquoted in `url(#...)`; special characters in filter ids are a portability risk (inference, unverified). Strip to `[A-Za-z0-9_-]` or quote the URL.
3. **Never read `navigator` or `window` during render.** liquid-glass-react reads `navigator.userAgent` in the render body, which throws in Node versions without a global `navigator` (liquid-glass-react `src/index.tsx`). Detect in an effect or a client-only module.
4. **Measure layout size, not transformed size.** Use `ResizeObserver` with `offsetWidth`/`offsetHeight`. `getBoundingClientRect` includes scale from entrance or press animations, which leaves maps undersized or starts resize loops (simple-liquid-glass `src/core/useGeometry.ts`; ybouane `src/LiquidGlass.ts`).
5. **Keep pointer motion out of the render cycle.** liquid-glass-react sets two state values on every `mousemove` and reads layout four times per render (liquid-glass-react `src/index.tsx`). Write `transform` and CSS custom properties directly in a `requestAnimationFrame` callback instead.
6. **Do not overwrite author styles.** liquid-glass-react replaces `style.transform` and `style.transition`; glasshq writes `translate` and `scale` so an author `transform` still composes (liquid-glass-react `src/index.tsx`; glasshq `src/dom/interaction.ts`).
7. **Dispose everything.** Remove observers, listeners, injected canvases and inline styles on unmount (ybouane `destroy()`; glasshq `controller.dispose()`; liquidGL `lens.destroy()`).

### 4.2 React

- Mark client modules with `"use client"`; both glasshq and simple-liquid-glass ship that banner (glasshq `vite.config.ts`; simple-liquid-glass `rollup.config.js`).
- Use `useSyncExternalStore` with a server snapshot of `false` for "is client" so server and client markup match (glasshq `src/react/scene.tsx`; simple-liquid-glass `src/index.tsx`).
- React 16 and 17 lack `useId`; simple-liquid-glass falls back to a post-mount id (simple-liquid-glass `src/core/useStableId.ts`).

### 4.3 Vue and Nuxt

- Register `liquid-glass` style custom elements with `compilerOptions.isCustomElement` in Vite, and load them in a Nuxt `.client.ts` plugin (simple-liquid-glass `docs/frameworks/vue.md`).
- Give the element an explicit width, height and `display: block`; every framework guide in simple-liquid-glass insists on it (simple-liquid-glass `docs/frameworks/vue.md`).

### 4.4 Svelte and SvelteKit

- Guard with `browser` from `$app/environment` or import the glass module inside `onMount` (simple-liquid-glass `docs/frameworks/svelte.md`).

### 4.5 Web components

- simple-liquid-glass's `<liquid-glass>` builds an open shadow root with holder, glass, border, content and filter layers, and its import is DOM-safe on the server (simple-liquid-glass `src/web-component/index.ts`).
- Keep the `<filter>` in the same shadow root as the element that references it. **Inference:** fragment references resolve within the tree scope, so a filter in the document is not a reliable target from inside a shadow root.
- Angular needs `CUSTOM_ELEMENTS_SCHEMA` (simple-liquid-glass `docs/frameworks/vanilla.md`).

### 4.6 SSR and hydration pitfalls

| Pitfall | Effect | Fix | Source |
| --- | --- | --- | --- |
| `navigator` read during render | Server crash or mismatch | Detect after mount | liquid-glass-react `src/index.tsx` |
| Filter ids generated with a counter | Server and client ids differ | Framework id hook | simple-liquid-glass `src/core/useStableId.ts` |
| Surfaces hidden until JavaScript runs | Blank chrome without JS; `visibility: hidden` also removes it from the accessibility tree | Hide with `opacity` and a short timeout, or render the Tier 1 look on the server | glasshq `src/styles.css`; simple-liquid-glass `src/index.tsx` (`reveal="ready"`, at most 400 ms, opacity only) |
| WebGL or capture at module scope | Server crash | Lazy-load renderer modules on the client | glasshq `src/dom/renderer.ts` (lazy GPU import) |

## 5. HTML capture limits (Tier 3)

A captured backdrop is a copy of the page. What the copier cannot draw, the glass cannot refract.

| Content | Behavior | Source |
| --- | --- | --- |
| Cross-origin images without CORS | Taint the canvas; upload fails. ybouane logs the error every frame and glass stops for the whole root | ybouane `README.md`, `src/LiquidGlass.ts`; liquidGL `scripts/liquidGL.js`; html2canvas docs (https://html2canvas.hertzen.com/documentation, checked 2026-11-05, High) |
| `<iframe>` | Never drawn; cross-origin frames cannot be read by DOM serialization | liquidGL `scripts/liquidGL.js`; same-origin policy (platform snapshot, Medium) |
| `<video>` | liquidGL composites live frames separately; simple-liquid-glass samples a `<video>` passed as the source directly, but media nested in an HTML source is a still snapshot | liquidGL `scripts/liquidGL.js`; simple-liquid-glass `README.md`. Library behavior of html2canvas and html-to-image for video: UNVERIFIED |
| html2canvas unsupported CSS | `background-blend-mode`, `border-image`, `box-decoration-break`, `box-shadow`, `filter`, `mix-blend-mode`, `object-fit`, `repeating-linear-gradient()`, `writing-mode`, `zoom`; `backdrop-filter` not listed (treat as unsupported, Low) | https://html2canvas.hertzen.com/features, checked 2026-11-05, High |
| html-to-image limits | Tainted `<canvas>` children fail; very large DOMs hit data-URI size limits; WebKit can draw a large embedded image blank on first rasterization | https://github.com/bubkoo/html-to-image, checked 2026-11-05, High |
| NaughtyDOM (liquidGL) gaps | Pseudo-elements, CSS `filter`, `clip-path` and `mask` on HTML elements are not painted | liquidGL `scripts/liquidGL.js` |
| Web fonts | Must be loaded and CORS-readable before capture, or captured text uses fallback fonts and misaligns with live text; html-to-image 1.11.13 shrinks font sizes, which ybouane patches out | ybouane `src/HtmlCapture.ts`, `patches/html-to-image+1.11.13.patch` |
| CSS animations and state changes | Not seen until recapture: `registerDynamic()` (liquidGL), `data-dynamic` or `markChanged()` (ybouane), `backdropVersion` or `refreshBackdrop()` (simple-liquid-glass) | liquidGL `README.md`; ybouane `README.md`; simple-liquid-glass `README.md` |
| An ancestor of the glass as backdrop | Clone loop and memory exhaustion; crashed iOS Safari | simple-liquid-glass `CHANGELOG.md`, `src/core/webgl/useWebGL.ts` |

Future path: HTML-in-Canvas (`drawElementImage`) is in a Chrome origin trial (Chrome 148, extended to 154; Chrome 155 renames `layoutsubtree` to `content="drawable"`). No other engine signal was found (https://developer.chrome.com/blog/html-in-canvas-ot-changes, checked 2026-11-05, Medium). Do not ship on it without a fallback.

## 6. The Backdrop Root rule

A `backdrop-filter` only sees content painted up to its nearest **Backdrop Root**. The Filter Effects Level 2 Editor's Draft (2 Oct 2026) defines a Backdrop Root as formed by:

- the root element;
- `filter` other than `none`;
- `opacity` below 1;
- `mask` or `clip-path`;
- `backdrop-filter` other than `none`;
- `mix-blend-mode` other than `normal`;
- `will-change` naming one of these.

Transforms, `z-index`, and fixed or sticky positioning alone do not create one. The draft notes this section does not yet have Working Group consensus (https://drafts.csswg.org/filter-effects-2/, checked 2026-11-05, High).

Consequences:

1. **A fading ancestor blanks the glass.** During an `opacity` fade-in on a wrapper, the glass blurs nothing because the wrapper is now the Backdrop Root. Animate `transform` on wrappers instead (simple-liquid-glass `README.md`, which reports this in Chromium).
2. **Nested glass sees only its parent.** A glass inside another glass (which has `backdrop-filter`) samples the parent's content, not the page behind both. Design nested surfaces to refract the parent, as glasshq does with reduced refraction for nested surfaces (glasshq `src/dom/index.ts`).
3. **Filters and masks on layout wrappers break glass far below them.** Audit ancestors for `filter`, `mask`, `clip-path` and `mix-blend-mode` before blaming the glass component.

Engine coverage of this rule beyond Chromium was not verified in this snapshot.

## Render-level detection

The question a Tier 2 gate has to answer is "does this engine paint a `url()` backdrop filter?" Neither of the usual tests can answer it.

- **Parse-level tests answer a different question.** `@supports (backdrop-filter: url(#f))` and `CSS.supports('backdrop-filter', 'url(#f)')` ask whether the declaration parses. The `backdrop-filter` grammar accepts `<url>` references (https://drafts.csswg.org/filter-effects-2/, checked 2026-11-05, High), so an engine that parses `backdrop-filter` can say yes and then draw nothing or an unreliable result: WebKit bug 245510 is open, and Firefox bug 1961378 reports `url()` backdrop filters ignored in some cases (https://bugs.webkit.org/show_bug.cgi?id=245510, https://bugzilla.mozilla.org/show_bug.cgi?id=1961378, checked 2026-11-05, High for bug status). That Safari and Firefox return true here follows from the grammar (**inference**); the probe below records what each engine actually answers.
- **User-agent sniffing names the engine, not the result.** UA strings can be frozen, reduced or spoofed, iPadOS reports a Macintosh UA, and a new engine is unknown by definition. A correct engine name still says nothing about the installed version: if WebKit fixes bug 245510, a sniffing gate keeps serving frost until someone edits it.

**What the plugin does instead.** `scripts/glass_probe.mjs` renders and samples. It loads a fixture page in each installed Playwright engine (Chromium, Firefox, WebKit): a pane whose `url()` backdrop filter shifts the backdrop by a known 8 px, a pane with `backdrop-filter: blur()`, a control pane with no filter, and a real `createGlass()` card. It screenshots each pane and compares it with the control. Refraction counts as rendered only when the pane matches the control shifted by the expected amount; blur counts when edges soften and average brightness holds. The report lists the tier each engine earned by rendering beside the tier the engine's own user-agent check picked, and it flags any engine where `CSS.supports` accepts `url()` but nothing rendered. Usage is in the [glass-lab README](../examples/glass-lab/README.md#check-it-in-real-engines).

**Why this stays in CI, not in the page.** In-page JavaScript cannot read composited pixels. Backdrop filters are applied by the browser's compositor, and no DOM API returns the page as painted: a canvas only holds what the script draws into it, DOM-to-canvas copiers re-implement painting and do not reproduce backdrop filters (see [section 5](#5-html-capture-limits-tier-3)), and screen capture needs a permission prompt. So in production:

1. Gate Tier 2 by engine detection plus the user's preferences, as the bundled engine's `explainTier()` does, with an unknown engine falling back to frost.
2. Offer a visible "solid surfaces" setting, because Safari exposes no reduced-transparency signal to CSS (see [section 3](#3-progressive-enhancement-and-detection)).
3. Run the probe in CI on every engine you support, with `--strict` so a missing browser fails the job, and change the engine gate when the probe's rendered tier and the sniffed tier disagree.

## Related references

- [optics.md](optics.md), [browser-support.md](browser-support.md), [gotchas.md](gotchas.md)
- [performance.md](performance.md) for the cost model of each tier
- [accessibility.md](accessibility.md) for reduced transparency, contrast and focus
