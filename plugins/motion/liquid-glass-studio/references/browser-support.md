# Browser support for liquid glass style techniques

Engine support for every feature the web tiers depend on, what users actually see per tier, and a detection sketch. Tiers are defined in [web-techniques.md](web-techniques.md#1-the-rendering-tiers).

All rows were checked on 2026-11-05. Versions come from MDN browser-compat-data (BCD) unless noted; bug status comes from the WebKit and Mozilla bug trackers. Recheck before quoting a version to a client: these facts move.

**Confidence:** High = primary source read on the check date. Medium = indirect primary source or reputable secondary source consistent with primary evidence. Low = single secondary source or inference. UNVERIFIED = not confirmed; do not state as fact.

## 1. Feature matrix

| Feature | Chromium (Chrome / Edge) | Firefox | Safari (macOS and iOS) | Source (checked 2026-11-05) | Confidence |
| --- | --- | --- | --- | --- | --- |
| `backdrop-filter` | Chrome 76; Edge 79 (17 to 78 with `-webkit-`) | 103; before 123 not supported on systems with an unknown GPU vendor | 18 unprefixed; 9 to 17 need `-webkit-backdrop-filter` | https://github.com/mdn/browser-compat-data/blob/main/css/properties/backdrop-filter.json | High |
| `backdrop-filter: url(#svg)` with `feDisplacementMap` | Works (basis of most CSS plus SVG glass demos) | Partial and unreliable: bug 1961378 "backdrop-filter gets ignored if it would fall back to a blob image (such like with some SVG url filters)" is NEW; a regression in 120 was fixed (bug 1868479) | Not shipped: bug 245510 NEW, last change 2026-09-06, community patches pending | https://bugs.webkit.org/show_bug.cgi?id=245510 ; https://bugzilla.mozilla.org/show_bug.cgi?id=1961378 ; https://bugzilla.mozilla.org/show_bug.cgi?id=1868479 ; https://kube.io/blog/liquid-glass-css-svg/ | Chromium Medium; Safari High; Firefox High (status) / Medium (impact) |
| `filter: url()` together with `backdrop-filter` on one element | Works (liquid-glass-react relies on it) | Not used by liquid-glass-react (skipped by UA check) | Bug 297770 "filter: url() ignored when backdrop-filter applied" REOPENED, last change 2026-08-31 | https://bugs.webkit.org/show_bug.cgi?id=297770 | High (bug status) |
| CSS `filter` (including `url()`) on an element | 53 (prefixed from 18) | 35 | 9.1 (prefixed from 6) | https://github.com/mdn/browser-compat-data/blob/main/css/properties/filter.json | High |
| SVG `feDisplacementMap` (as a normal filter) | Chrome 5, Edge 12 | 3 | 6 | https://github.com/mdn/browser-compat-data/blob/main/svg/elements/feDisplacementMap.json | High |
| `-moz-element()` | No | 57 with `-moz-` prefix (29 to 56 limited to background properties) | No | https://github.com/mdn/browser-compat-data/blob/main/css/types/image.json | High |
| WebGL 1 | 9 | 4 | 5.1 | https://github.com/mdn/browser-compat-data/blob/main/api/WebGLRenderingContext.json | High |
| WebGL 2 | 56 (Android 58) | 51 | 15 | https://github.com/mdn/browser-compat-data/blob/main/api/WebGL2RenderingContext.json | High |
| WebGPU (`navigator.gpu`) | 113 on ChromeOS, macOS, Windows; 144 adds Linux (Intel Gen12+ GPUs only); Android 121 | 141, partial: Windows from 141, macOS Tahoe on Apple silicon from 145, older macOS on Apple silicon from 147; no Intel Macs, no Linux | 26 | https://github.com/mdn/browser-compat-data/blob/main/api/GPU.json | High |
| `prefers-reduced-transparency` | 118 (BCD) or 119 (web-features) | 113 behind the pref `layout.css.prefers-reduced-transparency.enabled`; enabling bug 1822176 NEW | No; bug 175497 NEW, privacy concerns cited | https://web-platform-dx.github.io/web-features-explorer/features/prefers-reduced-transparency ; https://bugzilla.mozilla.org/show_bug.cgi?id=1822176 ; https://bugs.webkit.org/show_bug.cgi?id=175497 | High (support) / Medium (exact Chrome version) |
| `prefers-reduced-motion` | 74 | 63 | 10.1 | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json | High |
| `prefers-contrast` | 96 | 101 | 14.1 | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json | High |
| `forced-colors` | 89 (Edge 79) | 89 | 16, but always matches `none` (Apple platforms have no forced-colors mode) | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/media.json | High |
| `color-mix()` | 111 | 113 | 16.2 | https://github.com/mdn/browser-compat-data/blob/main/css/types/color.json | High |
| `@property` (animate tint custom properties) | 85 | 128 | 16.4 | https://github.com/mdn/browser-compat-data/blob/main/css/at-rules/property.json | High |
| Backdrop Root definition | Chromium behavior reported by simple-liquid-glass `README.md` | not verified | not verified | https://drafts.csswg.org/filter-effects-2/ (Editor's Draft 2 Oct 2026, no WG consensus yet) | High (spec text) / UNVERIFIED (per-engine behavior) |
| HTML-in-Canvas (`drawElementImage`) | Origin trial, Chrome 148 extended to 154; Chrome 155 renames `layoutsubtree` to `content="drawable"` | no signal found | no signal found | https://developer.chrome.com/blog/html-in-canvas-ot-changes ; https://groups.google.com/a/chromium.org/g/blink-dev/c/BpWbzJ9P22s | Medium |

Notes:

- Every iOS and iPadOS browser uses WebKit, whatever its brand, so the Safari column applies to Chrome and Firefox on iOS (simple-liquid-glass `src/core/renderer.ts` comment; glasshq `src/dom/engine.ts` comment).
- `@supports (backdrop-filter: url(#f))` parses in engines that do not render it. No CSS test detects `url()` rendering inside `backdrop-filter`.
- Firefox behavior for displacement inside `backdrop-filter` is inconsistent in reports: simple-liquid-glass treats Gecko as ignoring `url(#...)` (simple-liquid-glass `src/core/renderer.ts`), while bug data shows simple color-matrix filters working. Treat it as unsupported for displacement.

## 2. What users see, per tier and engine

Tier numbers follow [web-techniques.md](web-techniques.md#1-the-rendering-tiers). "Designed fallback" means the result if the implementation follows the detection sketch below; an implementation without detection can show worse results, listed in the last column.

| Tier | Chromium desktop | Chromium Android | Safari macOS and all iOS browsers | Firefox desktop | Failure without detection |
| --- | --- | --- | --- | --- | --- |
| 0 Solid | Solid surface | Solid | Solid | Solid | n/a |
| 1 CSS frost | Blur, saturation, tint, rims | Same; blur cost is higher on low-end devices | Same from Safari 18; Safari 9 to 17 need the `-webkit-` declaration or show no blur | Same from 103 | Missing `-webkit-` prefix: flat translucent box on older Safari (liquid-glass-react `src/index.tsx` emits no prefix) |
| 2a SVG in `backdrop-filter` | Live refraction | Live refraction; simple-liquid-glass defaults Android to layered CSS for cost (simple-liquid-glass `README.md`) | Designed fallback: Tier 1 frost | Designed fallback: Tier 1 frost | Safari and Firefox drop the whole `backdrop-filter` value or ignore the `url()`; the glass can lose its blur too (inference from the bug reports above) |
| 2b `filter: url()` on a frosted layer | Live refraction | Live refraction | Designed fallback: frost; WebKit bug 297770 can drop the filter | Designed fallback: frost | Safari keeps the filter attached at a cost with no benefit (liquid-glass-react `src/index.tsx`) |
| 2c Content-layer filter (glasshq) | Refraction of the declared content layer | Same | Same, software filtered; slower on large content; needs an opaque content background | Refraction through per-surface `-moz-element()` layers | Without WebGPU, new maps cannot be baked; stored maps from earlier visits still draw (glasshq `src/dom/map-store.ts`) |
| 3 WebGL capture | Refraction of a captured snapshot | Same; capture is slower | Same; html-to-image fidelity differs in WebKit (blank first draw of large images) | Same | No WebGL: ybouane throws and leaves no fallback; liquidGL falls back to CSS only when the synchronous check fails (ybouane `src/GlassRenderer.ts`; liquidGL `scripts/liquidGL.js`) |
| 4 WebGPU | Chrome 113+ on ChromeOS, macOS, Windows | Android 121+ | Safari 26+ | Firefox 141+ on Windows; Apple silicon macOS from 145 or 147; no Linux or Intel Mac | Adapter or device failure after `navigator.gpu` exists: liquidGL leaves lenses unstyled (liquidGL `scripts/liquidGL.js`) |

Accessibility overrides apply on top of every tier:

| Preference | Chromium | Firefox | Safari |
| --- | --- | --- | --- |
| Reduce transparency | Detectable; go solid | Only behind a pref; offer an in-app setting | Not detectable from CSS; offer an in-app setting and use `prefers-contrast: more` as a proxy |
| Increase contrast | `prefers-contrast: more` | same | same |
| Forced colors | `forced-colors: active`; backgrounds and filters are overridden, so design glass to fail to a solid surface | same | never matches |
| Reduce motion | `prefers-reduced-motion: reduce` | same | same |

See [accessibility.md](accessibility.md) for the full treatment.

## 3. Detection sketch

Original code for this plugin. It picks the highest tier the current engine can render, records why, and always leaves the Tier 1 CSS in place underneath. Engine sniffing is used only where no capability test exists (Tier 2).

```js
// Returns { tier, reason }. Run on the client only (never during server render).
export async function chooseGlassTier({ wantRefraction = true, hasSiblingBackdrop = false } = {}) {
  if (typeof window === "undefined") return { tier: 0, reason: "server" };

  const mq = (q) => window.matchMedia?.(q).matches === true;
  if (mq("(forced-colors: active)")) return { tier: 0, reason: "forced-colors" };
  if (mq("(prefers-reduced-transparency: reduce)")) return { tier: 0, reason: "reduced-transparency" };
  if (mq("(prefers-contrast: more)")) return { tier: 0, reason: "more-contrast" };
  // The page-level solid-surfaces setting: data-glass-surfaces="solid" on <html> (the bundled engine honors it live).
  if (document.documentElement.dataset.glassSurfaces === "solid") return { tier: 0, reason: "user-setting" };

  const frost = CSS.supports("backdrop-filter", "blur(1px)") ||
                CSS.supports("-webkit-backdrop-filter", "blur(1px)");
  if (!frost) return { tier: 0, reason: "no-backdrop-filter" };
  if (!wantRefraction) return { tier: 1, reason: "frost-requested" };

  const ua = navigator.userAgent;
  const iOS = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  const webkit = iOS || navigator.vendor === "Apple Computer, Inc.";
  const gecko = /Gecko\//.test(ua) && !/like Gecko/.test(ua);
  const chromium = !webkit && !gecko && /(Chrome|Chromium|Edg|OPR)\//.test(ua);

  // Tier 2: no capability test exists for url() inside backdrop-filter (WebKit 245510, Gecko 1961378).
  if (chromium) return { tier: 2, reason: "chromium-svg-backdrop" };

  // Tier 3 needs WebGL and a backdrop element that is not an ancestor of the glass.
  if (hasSiblingBackdrop && hasWebGL()) return { tier: 3, reason: "webgl-capture" };

  return { tier: 1, reason: webkit ? "webkit-no-svg-backdrop" : "gecko-no-svg-backdrop" };
}

function hasWebGL() {
  try {
    const c = document.createElement("canvas");
    return Boolean(c.getContext("webgl2") || c.getContext("webgl"));
  } catch {
    return false;
  }
}

// WebGPU is only a hint until an adapter and device exist.
export async function hasWebGPU() {
  if (!("gpu" in navigator)) return false;
  try {
    const adapter = await navigator.gpu.requestAdapter();
    if (!adapter) return false;
    const device = await adapter.requestDevice();
    device.destroy();
    return true;
  } catch {
    return false;
  }
}
```

Usage notes:

1. Write the result to the DOM, for example `el.dataset.glassTier = String(tier)` and `el.dataset.glassReason = reason`, so reviewers and tests can see which path ran (pattern from simple-liquid-glass `src/index.tsx`).
2. Listen for changes to the media queries and re-run; preferences can change while the page is open.
3. After choosing Tier 3 or 4, still handle `webglcontextlost` and WebGPU `device.lost`; fall back to Tier 1 instead of leaving the element unstyled (lessons from liquidGL and ybouane, see [gotchas.md](gotchas.md)).
4. Reuse one WebGL or WebGPU context for all glass on the page; browsers cap concurrent WebGL contexts (ybouane `README.md` warns of about 16).

## Related references

- [web-techniques.md](web-techniques.md) for the pipelines behind each tier.
- [gotchas.md](gotchas.md) for engine-specific failure modes.
- [research-snapshot.md](research-snapshot.md) for the full platform fact list.
