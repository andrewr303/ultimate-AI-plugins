# Which library or approach should I use?

A decision guide for liquid glass style refraction on the web: five open-source libraries this plugin studied, plus the option of building on the plugin's own engine. Use it to pick an approach, then read the matching source note for API details.

**Versions are as observed in the supplied archives on 2026-11-05.** They are snapshots and not necessarily the latest releases. Before recommending a library to a client, check its registry page and repository for the current version, license file and open issues.

Tier names (1, 2a, 2b, 2c, 3, 4) follow [web-techniques.md](web-techniques.md#1-the-rendering-tiers). Platform facts cite [research-snapshot.md](research-snapshot.md).

## 1. Short answer

| If you need | Start with | Why |
| --- | --- | --- |
| Native Apple, Android or Flutter UI | Platform APIs, see [native.md](native.md) | System glass handles accessibility settings for you; none of these libraries target native |
| Frosted glass only, no refraction | Plain CSS `backdrop-filter` (Tier 1) | Works in every current engine; no library needed |
| Refraction in Chromium, frost elsewhere, full control, no dependencies | The bundled engine (section 5) | Small, tiered, accessibility-first; you own maintenance |
| Refraction in Chromium, Safari and Firefox over content you control, React 19 | glasshq-liquid-glass | Filters a live content layer in all three engines; text stays live |
| Refraction in most engines over arbitrary page content, video or canvas, React 16.8+ or a web component | simple-liquid-glass | SVG on desktop Chromium, WebGL over a supplied backdrop elsewhere, designed CSS fallback. Android Chromium refracts only with an opt-in (`renderer="webgl"`/`"svg"` or `mobileFallback="svg"`) |
| Vanilla JS hero lenses, magnifiers or docks on a GSAP or Lenis site | liquidGL | One shared WebGPU or WebGL canvas, fluid pointer deformation |
| A few self-contained vanilla panels with rich per-pixel lighting | ybouane-liquidglass | Height-field shader with Fresnel and multi-light specular |
| A quick Chromium-only React prototype | liquid-glass-react, or the bundled engine | One component, but demo grade (section 4) |

## 2. Matrix: rendering and reach

| Library (version observed) | Technique and tier | Engines where refraction shows | Fallback when refraction is unavailable |
| --- | --- | --- | --- |
| glasshq-liquid-glass (`@glass-sdk/liquid-glass` 0.0.2) | Tier 2c: WGSL maps baked through WebGPU, SVG filter on an explicit content layer; Gecko uses per-surface `-moz-element()` layers | Chromium, Safari, Firefox, Electron (manual acceptance targets, `CONTRIBUTING.md:24`). Only the declared content layer refracts | Material absent, content still clipped and visible; stored maps let resting glass draw without a GPU on reload |
| simple-liquid-glass (5.7.0) | Tier 2a on Chromium; Tier 3 WebGL over a supplied backdrop elsewhere; Tier 1 frost fallback | Desktop Chromium by default; Android Chromium only with `renderer="webgl"`/`"svg"` or `mobileFallback="svg"` (layered CSS otherwise, `README.md:411`, `src/index.tsx:381-385`, `:478-482`); Safari, iOS and Firefox when you pass `backdropRef`, `backdropSelector` or a `LiquidGlassScene` | Designed frosted CSS with rims; status reasons such as `missing-backdrop` |
| liquidGL (`liquid-gl` 3.0.0) | Tier 4 or 3: in-house DOM rasterizer, one shared WebGPU or WebGL canvas | All engines claimed (`README.md:301-313`); Safari "can be unstable" for lenses over half the viewport | CSS blur only when no GPU is detected up front; none after a late async GPU failure |
| ybouane-liquidglass (`@ybouane/liquidglass` 1.0.3) | Tier 3: html-to-image capture into WebGL 1 | All evergreen engines claimed (`README.md:236-238`) | None: `init()` rejects without WebGL |
| liquid-glass-react (1.1.1) | Tier 2b: `backdrop-filter` plus `filter: url()` on one layer | Chromium only (`README.md:27`) | Blur and saturate in Firefox; Safari only where unprefixed `backdrop-filter` works, with the SVG filter still attached |
| Bundled engine (`examples/glass-lab/liquid-glass.js`) | Tier 2a on Chromium, Tier 1 frost elsewhere, solid tier for accessibility preferences | Chromium only | Frost on other engines; solid under reduced transparency, more contrast or forced colors |

Why Chromium-only for Tier 2a and 2b: Safari has not shipped `backdrop-filter: url()` (WebKit bug 245510) and Firefox ignores some url() backdrop filters (bug 1961378); see [research-snapshot.md](research-snapshot.md) rows W3 and W4.

## 3. Matrix: frameworks, size, interaction, accessibility

| Library | Frameworks | Size facts (from the archive) | Interaction and morph | Accessibility support |
| --- | --- | --- | --- | --- |
| glasshq-liquid-glass | React 19+ components on Base UI; framework-free DOM controller (`/dom`) | Gzip budgets per import: Surface 47,104 B, Everything 127,488 B, lazy GPU 52,736 B (`packages/liquid-glass/size-budgets.json`) | Duration and bounce springs, press grow, drag stretch, glow, menu morph with liquid neck, tab selection lens, fluid layout | Base UI roles and keyboard; system reduced motion always wins; no reduced-transparency path for the material; faint focus fill |
| simple-liquid-glass | React 16.8 to 19, `<liquid-glass>` custom element, vanilla WebGL surface, experimental GLSL engine | Brotli limits: core 52.6 KB, web component 37.7 KB, engine core 13.6 KB (`package.json:74-125`) | Pointer lean spring (per frame), tracked specular, ripples, animated turbulence; no morph | Reduced motion honored; luminance text-color switch; no reduced transparency, contrast, forced colors, roles or focus styles |
| liquidGL | Vanilla global or ESM default export; GSAP, Lenis and Locomotive sync | One 297,144 byte unminified file, about 61.6 KB gzip, measured on `package/liquidGL.js`; no minified build | Fluid pointer deformation (time based), tilt, drag; shape follows live border radius; no morph | None: no reduced motion, no ARIA; non-draggable lenses get `pointer-events: none` |
| ybouane-liquidglass | Vanilla ESM class | `src/` 99,946 bytes, about 27.7 KB gzip of source; published bundle also includes html-to-image (not measured) | Drag (`floating`), one-frame hover and press; no springs or morph | None; forces `user-select: none` on the root; content stays live DOM |
| liquid-glass-react | React 18+ | `src/` 67,421 bytes including about 41 KB of base64 maps, about 35.4 KB gzip of source | Mouse-driven stretch and translate, mouse-steered rim, press `scale(0.96)`, CSS transitions | None; `onClick` on a div without role or keyboard; forced white text |
| Bundled engine | Any framework; one ES module | Single dependency-free file; measure it in your own build | Optional pointer elasticity; no morph | Tiers drop to solid for reduced transparency, more contrast and forced colors; never touches focus styles |

Size figures for liquidGL, ybouane-liquidglass and liquid-glass-react are `gzip -c` of archive files on 2026-11-05, not production bundles. Treat them as order-of-magnitude only.

## 4. Matrix: maturity, license and attribution

| Library | Maturity signals | License and attribution obligations |
| --- | --- | --- |
| glasshq-liquid-glass | Version 0.0.x; 33 test files; pre-push hook with GPU checks, no everyday CI; size budgets; detailed per-engine workarounds | MIT, "Copyright (c) 2026 Glass HQ". Runtime deps `@lisse/core`, `vgpu`, `@base-ui/react` have their own licenses (not in the archive). Native reference app includes Hugeicons (MIT) and Inter (SIL OFL 1.1) |
| simple-liquid-glass | CI with Playwright on three engines and a React version matrix; about 202 tests; very high release cadence; dense hand-minified style in newer modules | MIT, "Copyright (c) 2025 lucaperullo". **Vendors** samasante/liquid-glass (MIT, Sam Asante), @ybouane/liquidglass 1.0.3 (MIT text, no copyright line), html-to-image 1.11.11 (MIT, W.Y.) and a liquidGL optics port (MIT, NaughtyDuk), listed in `THIRD_PARTY_NOTICES.md`. Shipping it means carrying all of these notices |
| liquidGL | No tests, CI or changelog; 10 demo pages; hardened edge cases; one dead method | MIT, "Copyright (c) NaughtyDuk", for `scripts/` and `package/` only. Fonts and audio in `assets/` are excluded and must not be copied |
| ybouane-liquidglass | No tests, CI or changelog; small and well commented | `package.json` and README declare MIT, but **the archive has no LICENSE file and no copyright line**. The exact notice and holder cannot be reproduced; cite as inspiration and do not copy. Bundles html-to-image 1.11.13 (MIT) with a local patch |
| liquid-glass-react | No tests, CI or changelog; metadata drift (phantom workspace, stale build config) | MIT, "Copyright 2025 MAX ROVENSKY". `src/shader-utils.ts` is "Adapted from https://github.com/shuding/liquid-glass", whose license is not in the archive (unverified). Embedded maps have no stated origin |
| Bundled engine | Unit tests in `tests/engine.test.mjs`; part of this plugin | MIT (this plugin). Original code; studied libraries are credited in `NOTICE.md` |

This plugin studied all five and copied no code. If you copy code from any of them, keep that project's notice, and for simple-liquid-glass also the notices of the code it vendors.

## 5. Build your own with the bundled engine

`examples/glass-lab/liquid-glass.js` is an original, dependency-free ES module that ships with this plugin. It has two layers:

- **Pure math** (safe to import in Node): surface profiles, a Snell-based refraction profile, displacement and specular maps, SVG filter markup, and the tier decision (`displacementField`, `specularField`, `buildFilterMarkup`, `explainTier`, `detectTier`).
- **Browser API**: `capabilities()` reads the engine and user preferences, `createGlass(element, options)` renders PNG maps and wires them to `backdrop-filter: url(#id)`, and `findBackdropRoot(element)` reports an ancestor that would make the glass blur nothing.

Behavior: refraction on Chromium, frost (blur and saturate) on other engines, and a solid tier when the user prefers reduced transparency or more contrast, when forced colors are active, or when the page sets `data-glass-surfaces="solid"` on `<html>` (watched live). The engine writes `data-glass-tier` so you style the tint per tier. It does not touch outline, focus styles or content.

To use it in a project, copy `liquid-glass.js` and keep its attribution header. In a TypeScript project, copy `liquid-glass.d.ts` beside it with the same header; it declares the public API ([glass-lab README](../examples/glass-lab/README.md#typescript)).

Choose it when:
- Chromium-only refraction with a frosted baseline is acceptable.
- You want no runtime dependencies and full control over optics.
- Accessibility tiers matter more than cross-engine refraction.

Do not choose it when:
- You need refraction in Safari or Firefox (pick glasshq-liquid-glass or simple-liquid-glass).
- You need shape morphing, menus or ready-made accessible components (glasshq-liquid-glass has them).

Start with the lab in `examples/glass-lab/` ([README](../examples/glass-lab/README.md)) to tune parameters, then follow [optics.md](optics.md) and [web-techniques.md](web-techniques.md).

## 6. Decision tree

1. **Is the target native (SwiftUI, UIKit, AppKit, Compose, Flutter)?** Use platform APIs; see [native.md](native.md). Stop here.
2. **Does the design need refraction, or is frost enough?** Frost only: Tier 1 CSS, no library. Check [accessibility.md](accessibility.md) for contrast over variable backdrops.
3. **Is Chromium-only refraction acceptable, with frost elsewhere?**
   - Yes, and you want minimal code: the bundled engine.
   - Yes, and you want a drop-in React component: liquid-glass-react, but budget for fixing its accessibility and the issues in its source note.
   - No: continue.
4. **Can you restructure the page so glass sits over an explicit content layer that you own (no arbitrary page backdrop, no native video, no rotated ancestors)?**
   - Yes, and the app uses React 19 or can use a DOM controller, and WebGPU is acceptable for first map render: glasshq-liquid-glass.
   - No: continue.
5. **Must the glass refract arbitrary page content, video or canvas in every engine?**
   - With React or as a web component, and you can supply a backdrop element that is not an ancestor of the glass: simple-liquid-glass.
   - Vanilla JS, fixed or sticky lenses, scroll-library integration, and you will add accessibility yourself: liquidGL.
   - A small number of panels inside one root, and you will add a fallback yourself: ybouane-liquidglass (confirm license status first).
6. **Whatever you pick**, run the checks in [gotchas.md](gotchas.md), [performance.md](performance.md) and [accessibility.md](accessibility.md) before shipping.

## 7. Questions to answer before choosing

- Which engines must show refraction, and is frost acceptable elsewhere?
- What is behind the glass: your own content layer, the whole page, video, canvas, or cross-origin media? DOM capture approaches (Tier 3 and 4) miss iframes, some CSS features and tainted images.
- How many glass surfaces at once? SVG costs scale per pane; shared-canvas approaches scale better.
- Which accessibility preferences must the glass respect? Only the bundled engine covers reduced transparency, contrast and forced colors. glasshq-liquid-glass and simple-liquid-glass honor reduced motion (glasshq also restyles slider and switch parts under forced colors).
- Can you carry every license notice the dependency brings, including vendored code?

## Source notes

- [glasshq-liquid-glass](sources/glasshq-liquid-glass.md)
- [simple-liquid-glass](sources/simple-liquid-glass.md)
- [liquidGL](sources/liquidgl.md)
- [ybouane-liquidglass](sources/ybouane-liquidglass.md)
- [liquid-glass-react](sources/liquid-glass-react.md)
