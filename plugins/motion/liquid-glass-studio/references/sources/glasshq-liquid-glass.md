# Source notes: glasshq-liquid-glass (`@glass-sdk/liquid-glass`)

Condensed study notes for one of the five libraries this plugin learned from. Nothing here is vendored; formulas are paraphrased or quoted briefly with attribution. Citations use `<repo-relative path>:line` in the upstream layout (repository `github.com/Glass-HQ/liquid-glass`). The library lives in `packages/liquid-glass/`; demo and native reference apps live in `apps/`.

Observed in the supplied archive on 2026-11-05. The archive is a snapshot, not necessarily the latest release. Recheck the upstream repository before quoting a version or behavior to anyone.

## 1. Identity

| Field | Value | Evidence |
| --- | --- | --- |
| Package | `@glass-sdk/liquid-glass` | `packages/liquid-glass/package.json:2` |
| Version in archive | `0.0.2` | `packages/liquid-glass/package.json:3` |
| License | MIT, "Copyright (c) 2026 Glass HQ" | `packages/liquid-glass/LICENSE:3`, `LICENSE:3` |
| Entry points | `.` (React), `./core`, `./gpu`, `./dom`, `./styles.css` | `packages/liquid-glass/package.json` (exports) |
| Runtime deps | `@base-ui/react`, `@lisse/core` (continuous corners), `vgpu` (WebGPU/WGSL helper) | `packages/liquid-glass/package.json` (dependencies) |
| Peer deps | React and ReactDOM 19 or later | `packages/liquid-glass/package.json` (peerDependencies) |
| Tests | 33 bun test files (morph, filter patching, sampling bounds, springs, unions) | `package.json` root script `bun test packages/liquid-glass` |
| CI | No everyday CI by design; a pre-push hook runs typecheck, lint, tests, build, size and GPU checks; release workflow publishes with npm provenance | `CONTRIBUTING.md:18-20`, `.github/workflows/publish.yml:32-44` |
| Size budgets (gzip, per import) | Surface 47,104 B initial; Everything 127,488 B; lazy GPU path 52,736 B | `packages/liquid-glass/size-budgets.json` |
| Acceptance targets | Chromium, Safari, Firefox, Electron, verified manually | `CONTRIBUTING.md:24`, `AGENTS.md:6` |

**One-line summary.** A WGSL shader (through WebGPU) bakes per-shape material maps once; an SVG filter graph then refracts a live DOM content layer with `feDisplacementMap`. Text stays live and selectable. Only the explicit content layer is refracted (`packages/liquid-glass/README.md:226`).

## 2. Technique pipeline

Architecture: a `GlassScene` holds one `GlassContent` (the backdrop) and any number of transparent surfaces above it. The content element receives one SVG reference filter that replaces pixels inside each surface footprint with refracted, toned and tinted content plus rim light (`packages/liquid-glass/src/dom/index.ts:340-694`, `packages/liquid-glass/src/dom/compose-layers.ts:30-81`). The project forbids DOM screenshots, WebGL/GLSL and CSS approximations of the material (`AGENTS.md:5`).

Chromium and WebKit path, per frame:

1. Measure content and surface rects in a read phase; effective opacity multiplies ancestors up to the scene (`packages/liquid-glass/src/dom/index.ts:166-174`, `:780-968`).
2. Build the outline with `@lisse/core` continuous corners (smoothing 0.8125, squircle curve; arc for circles). The same outline drives `clip-path` and the GPU distance field (`packages/liquid-glass/src/core/shape.ts:6-14`, `:35-37`).
3. Tessellate curves into 32 steps per segment; symmetric shapes send only the top-right quadrant, at most 128 segments (`packages/liquid-glass/src/core/shape.ts:38-108`).
4. Look up maps by `[width, height, radius, dpr, appearance, outline, sliceCapsule]`: memory cache, then a localStorage first-paint set, then IndexedDB, then GPU (`packages/liquid-glass/src/dom/maps.ts:60-128`, `packages/liquid-glass/src/dom/map-store.ts:115-120`).
5. Render all requests from one task into an atlas in one draw and one readback (up to 32 shapes, 4096 segments) (`packages/liquid-glass/src/gpu/index.ts:29-30`, `:72-84`, `:113-159`).
6. Encode pixels to PNG with a hand-written encoder in a worker, as `data:` URLs because Chromium resolves them synchronously for `feImage` (`packages/liquid-glass/src/dom/png.ts:1-5`, `:106-110`, `packages/liquid-glass/src/dom/map-encoder.ts:33-54`).
7. Decode images before swapping them into the filter (`packages/liquid-glass/src/dom/maps.ts:113-137`).
8. Build a per-surface filter unit: field `feImage`, optional edge tiles, optional frost, `feDisplacementMap` with `scale = 2 * refraction` reading R and G, tone curve, optional tint, `feComposite in` with coverage, then the rim overlay (`packages/liquid-glass/src/dom/index.ts:528-605`, `:572`).
9. Compose sparsely: cut covered source pixels and merge layers in paint order with `feMerge`, avoiding arithmetic composites that clamp in software filters (`packages/liquid-glass/src/dom/compose-layers.ts:16-81`).
10. Patch the retained filter description; only changed attributes are written (`packages/liquid-glass/src/dom/filter-patch.ts:25-70`).
11. Apply `filter: <author filter> url(#scene)` to the content element, preserving any author filter (`packages/liquid-glass/src/dom/index.ts:260-280`).

Firefox path: each surface gets an `aria-hidden` layer whose background is `-moz-element(#content)` plus lower glass layers, with its own small filter chain, because Gecko re-rasterizes software filters on every paint (`packages/liquid-glass/src/dom/lens-layers.ts:48-57`, `:85`, `:139-204`).

### Optics (paraphrased)

- Refraction profile (WGSL): depth is `clamp(-d * 0.05)`, so the bezel is a fixed 20 px band; `edge = 1 - sqrt((2 - depth) * depth)` is a quarter-circle profile, largest at the rim (`packages/liquid-glass/src/gpu/maps.wgsl:67-70`). The CPU twin is `edgeDisplacement` (`packages/liquid-glass/src/core/optics.ts:1-10`).
- Encoding: R and G store `0.5 - n * edge * 0.5`; with `scale = 2 * refraction` the sample moves `refraction` px inward at the rim. Default refraction is 60 px (`packages/liquid-glass/src/core/materials.ts:17`, `:24`). There is no Snell, IOR or Fresnel term; this is a shaped heuristic.
- Rim light: a sub-pixel stroke weighted by how vertical the normal is (top and bottom), an 18% inner glow within about 4.5 px, and a dark side shade weighted by horizontal normals (`packages/liquid-glass/src/gpu/maps.wgsl:71-90`).
- Regular frost: blur sigma 7.33 plus a fill blur (23 light, 21.8 dark), lighten or darken blend, mix 0.34 or 0.65; frost happens before displacement (`packages/liquid-glass/src/dom/material-graph.ts:11-17`, `packages/liquid-glass/src/core/materials.ts:14-36`).
- Tone: quadratic tables per appearance plus saturate 1.10 (light) or 1.06 (dark) for Regular; shadow lift and highlight rolloff with a pale veil for Clear (`packages/liquid-glass/src/dom/material-graph.ts:20-47`).
- Tint: hex only; luminance is transmitted through the tint with body 0.78 (Regular) or 0.68 (Clear); text and icons are never tinted (`packages/liquid-glass/src/dom/material-graph.ts:50-75`, `packages/liquid-glass/README.md:67`).
- Chromatic aberration: absent. Drop shadow under glass: absent (only control thumbs use a CSS shadow, `packages/liquid-glass/src/styles.css:326`).
- Nested glass refracts less: `clamp(0.6 * inset, 0, 8)` px (`packages/liquid-glass/src/dom/index.ts:303-312`).

## 3. API tables

### React components (`packages/liquid-glass/src/react/index.tsx:1-23`)

| Component | Purpose | Defaults and notes | Evidence |
| --- | --- | --- | --- |
| `GlassScene` | Scene root and controller | `material="clear"`, `appearance="light"`, `motion="full"`, `maxSurfaces=16` (1 to 64), `onDiagnostic` | `packages/liquid-glass/src/react/scene.tsx:63-118` |
| `GlassContent` | Live backdrop layer | `layout`: `overlay` (default), `flow`, `scroll`; WebKit scroll wraps in `svg > foreignObject` | `packages/liquid-glass/src/react/scene.tsx:119-157` |
| `GlassSurface` | Generic glass container | `radius=8`, `interactive=false`, `fluid=false`, `render` prop | `packages/liquid-glass/src/react/surface.tsx:39-109` |
| `GlassButton` | Base UI Button | `radius="capsule"`, `interactive=true`, sizes `default/xs/sm/lg/icon*`; icon sizes force a circle | `packages/liquid-glass/src/react/button.tsx:16-47` |
| `GlassToolbar` (+ `Button`, `Link`, `Group`, `Spacer`) | Keyboard-navigable toolbar; spacers split clusters | spacer `sizing="flexible"` default, `"fixed"` = 8 px | `packages/liquid-glass/src/react/toolbar.tsx:17-212` |
| `GlassTabs` family | Tabs with a draggable selection lens | `activateOnFocus`; indicator `material="clear"`; `aria-label` default "Sections" | `packages/liquid-glass/src/react/tabs.tsx:24-174` |
| `GlassMenu` family | Base UI menu that morphs from its trigger | content `material="regular"`, `radius=28`, `sideOffset=8`; submenu `neck=0` | `packages/liquid-glass/src/react/menu.tsx:33-183` |
| `GlassSlider` | Slider with glass thumb on press | `min=0`, `max=100`, `step=0.1`, ticks up to 100 | `packages/liquid-glass/src/react/value-controls.tsx:22-65` |
| `GlassSwitch` | Switch with glass thumb | drag commits at midpoint or 40% travel | `packages/liquid-glass/src/react/value-controls.tsx:73-159` |
| `GlassForeground` | Foreground DOM refracted by higher glass | no extra maps | `packages/liquid-glass/src/react/scene.tsx:38-53` |
| `GlassShape`, `GlassShapeContainer`, `GlassCorner` | Continuous-corner clipping and concentric layout without a scene | `radius=8`; corner gap 8 | `packages/liquid-glass/src/react/shape.tsx:16-56` |
| `GlassProgressiveBlur`, `GlassScrollEdges` | Edge blur of content or a scrollport | `size=80`, `blur=20`, `refraction=0` | `packages/liquid-glass/src/react/progressive.tsx:10-43` |

### Material and surface options

| Option | Type | Default | Effect | Evidence |
| --- | --- | --- | --- | --- |
| `material` | `"clear" \| "regular"` | `"clear"`; menus `"regular"` | Clear: no blur, tone curve. Regular: frost, tone, saturate | `packages/liquid-glass/src/core/materials.ts:2-36` |
| `appearance` | `"light" \| "dark"` | `"light"` | Tone constants, light intensity, foreground color | `packages/liquid-glass/src/styles.css:31-37` |
| `radius` | number, `"capsule"`, `"circle"` | 8 | Continuous corner; finite and non-negative | `packages/liquid-glass/src/core/shape.ts:5-14` |
| `concentric` | boolean or `{ inset }` | off | Follows nearest declared container | `packages/liquid-glass/src/dom/shape-layout.ts:168-181` |
| `refraction` | px, 0 or more | 60; nested `clamp(0.6 * inset, 0, 8)` | Displacement travel | `packages/liquid-glass/src/dom/index.ts:303-312`, `:1060-1064` |
| `tint` | `"#rrggbb"` | none | Luminance-transmitting color; other formats silently ignored | `packages/liquid-glass/src/dom/material-graph.ts:50-69` |
| `interactive` | boolean | false (surface), true (controls) | Press grow, drag stretch, glow | `packages/liquid-glass/src/dom/interaction.ts:37` |
| `fluid` | boolean | false | Springs the outline on layout change | `packages/liquid-glass/src/dom/morph.ts:430-447` |
| `morphFrom` | ref or getter | none | Grow from and return to an element | `packages/liquid-glass/src/dom/index.ts:68-71` |
| `morph` | `"become" \| "detach"` | inferred from source | Replace source glass, or drop with a liquid neck | `packages/liquid-glass/src/dom/morph.ts:218-222` |
| `neck` | px | 18 | Neck reach; 0 gives a plain shape | `packages/liquid-glass/src/dom/morph.ts:240` |
| `motion` | `"full" \| "reduced" \| "none"` | `"full"`; system reduced motion always wins | Elasticity and travel | `packages/liquid-glass/src/dom/interaction.ts:5-15` |

`--lg-foreground` overrides text and icon color (`packages/liquid-glass/src/styles.css:31-37`).

### DOM controller (`@glass-sdk/liquid-glass/dom`)

| Export | Role | Evidence |
| --- | --- | --- |
| `createGlassScene(root, { onDiagnostic, maxSurfaces })` | Returns a controller | `packages/liquid-glass/src/dom/index.ts:177-180` |
| `setContent(el)` | Sets the backdrop layer | `packages/liquid-glass/src/dom/index.ts:1038-1054` |
| `addSurface(el, options)` | Returns a remover; throws past `maxSurfaces` | `packages/liquid-glass/src/dom/index.ts:1055-1109` |
| `addForeground(el)`, `addAnimator(...)`, `addProgressiveBlur(...)`, `addScrollEdges(...)` | Extras | `packages/liquid-glass/src/dom/index.ts:1110-1132` |
| `dispose()` | Teardown; restores inline styles | `packages/liquid-glass/src/dom/index.ts:1133-1149` |
| `GlassDiagnostic` | `{ surfaces, maps, mapTime, error }`, `glass:diagnostic` event, `data-glass-ready` | `packages/liquid-glass/src/dom/index.ts:53-58`, `:219-242` |

Core exports include `edgeDisplacement`, `materials`, `Spring`, `springs`, `rubberBand`, `smoothUnion`, `roundRectDistance` (`packages/liquid-glass/src/core/index.ts:1-17`).

## 4. Motion and interaction

- Springs use a perceptual `{ duration, bounce }` form: `omega = 2 pi / duration`, `k = omega^2`, `c = 4 pi (1 - bounce) / duration`, solved in closed form so dropped frames do not slow the animation (`packages/liquid-glass/src/core/spring.ts:24-91`).
- Named springs (duration s, bounce): press 0.24/0.2, release 0.5/0.42, glow 0.42/0, morph 0.42/0.18, layout 0.4/0.16, track 0.18/0 (`packages/liquid-glass/src/core/spring.ts:9-22`).
- Interaction writes only `translate`, `scale` and custom properties so author `transform` still composes (`packages/liquid-glass/src/dom/interaction.ts:33-36`). Drag-follow duration grows with size ("larger glass is heavier") (`:97-101`). Stretch preserves volume: `sx = (1 + grow)(1 + ex) / sqrt(1 + ey)` (`:179-184`). Hover glow only on `(hover: hover) and (pointer: fine)` (`:106-111`). Space and Enter press with a centered glow (`:112-127`).
- Morph: plan 10 to 14 waypoint shapes spaced by a log-size and radius metric, prepare maps ahead, and crossfade two maps per frame with `feComposite arithmetic` (`packages/liquid-glass/src/core/morph-path.ts:37-41`, `:171-237`, `packages/liquid-glass/src/dom/map-blend.ts:10-19`).
- Liquid neck: polynomial smooth-min of two rounded-rect distances, traced by marching squares and simplified (`packages/liquid-glass/src/core/union.ts:13-138`).
- Tabs selection lens springs four values and clicks the nearest tab on release so Base UI keeps state (`packages/liquid-glass/src/dom/selection.ts:6-8`, `:59-107`).

## 5. Platform behavior

| Concern | Chromium / Electron | WebKit | Gecko | Evidence |
| --- | --- | --- | --- | --- |
| Where the filter runs | Content element | Content element (software painted) | Per-surface `-moz-element()` layers | `packages/liquid-glass/src/dom/lens-layers.ts:48-57` |
| Moving surfaces | `will-change: transform` for 400 ms after moving | Content becomes a paint root | Layers move with surfaces | `packages/liquid-glass/src/dom/index.ts:969-983`, `packages/liquid-glass/src/dom/filter-paint-root.ts:11-24` |
| Filter limits | n/a | 4096 x 4096 device px clamp; blur and displacement softened to fit | 64 operations per element | `packages/liquid-glass/src/dom/filter-budget.ts:3-25`, `packages/liquid-glass/src/dom/progressive.ts:488-489` |
| Page zoom | n/a | Measures zoom and rescales primitive lengths | n/a | `packages/liquid-glass/src/dom/page-zoom.ts:39-63` |

Engine detection is UA based (`packages/liquid-glass/src/dom/engine.ts:1-12`). WebGPU is required to render new maps (`packages/liquid-glass/README.md:223`); stored maps let resting glass draw without a GPU device on reload (`packages/liquid-glass/src/dom/map-store.ts:1-5`). On map failure the content clip still applies and the material is simply absent (`packages/liquid-glass/src/dom/index.ts:768-774`). SSR is handled with `useSyncExternalStore` and `"use client"` banners (`packages/liquid-glass/src/react/scene.tsx:123-133`).

Native reference app (`apps/native-reference`, macOS 26+, "not a native port") maps the web concepts to `Glass.clear/.regular.tint()`, `.glassEffect(_:in:)`, `GlassEffectContainer`, `.buttonStyle(.glass)`, `ToolbarSpacer` and `.scrollEdgeEffectStyle` (`apps/native-reference/Sources/NativeReference.swift:163`, `:207`, `:233-234`; `apps/native-reference/Sources/NativeUsage.swift:14-31`).

## 6. Performance notes

- One atlas pass and one readback per task batch; map DPR capped at 2; shapes in motion use 1x maps (`packages/liquid-glass/src/gpu/index.ts:45-47`, `packages/liquid-glass/src/gpu/geometry.ts:19`, `packages/liquid-glass/src/dom/index.ts:157-159`).
- Filter rebuilds during motion throttled to about 60 Hz (`packages/liquid-glass/src/dom/index.ts:215-218`).
- Every primitive gets an explicit subregion, otherwise it covers the whole filter region (`packages/liquid-glass/src/dom/index.ts:591-605`).
- Caches: in-memory 64 entries, IndexedDB LRU 256, localStorage first-paint set up to 3,000,000 chars, keys versioned by a hash of the shader source (`packages/liquid-glass/src/dom/maps.ts:22-27`, `:149-159`, `packages/liquid-glass/src/dom/map-store.ts:11-15`, `:91-141`).
- One rAF driver per window with read and write phases; sleeps after 3 idle frames with a 1 s heartbeat (`packages/liquid-glass/src/dom/ticker.ts:1-87`).
- Safari can take much longer on large content layers; keep scenes small (`packages/liquid-glass/README.md:224`).

## 7. Accessibility

- Buttons, toolbars, tabs, menus, sliders and switches use Base UI behavior, so standard props, refs, accessible names and state callbacks remain available (`packages/liquid-glass/README.md:55`). Tabs activate on focus (`packages/liquid-glass/src/react/tabs.tsx:57`).
- Decorative layers are `aria-hidden`; leaving toolbar clusters are `inert` (`packages/liquid-glass/src/dom/lens-layers.ts:109`, `packages/liquid-glass/src/react/toolbar.tsx:163-164`).
- System reduced motion always overrides `motion="full"` (`packages/liquid-glass/src/dom/interaction.ts:5-15`).
- Reduced transparency and forced colors disable the progressive blur (`packages/liquid-glass/src/dom/progressive.ts:288-289`, `:359-367`). Forced colors also restyles slider and switch tracks, fills and thumbs with system colors (`packages/liquid-glass/src/styles.css:351-355`). The glass material itself has no reduced-transparency or forced-colors path.
- Focus: `:focus-visible` replaces the outline with an 8% `currentColor` fill, and thumbs set `outline: none` (`packages/liquid-glass/src/styles.css:55-59`, `:319`). Inference: this is likely too faint for WCAG 2.4.7 and 1.4.11 on busy backdrops; measure before reuse.
- Surfaces are `visibility: hidden` until their clip path exists, which also hides them from assistive tech until JS runs (`packages/liquid-glass/src/styles.css:359-360`).

## 8. Known bugs and failure modes (from code, tests and README)

1. Only the explicit content layer refracts; arbitrary page backdrops, native video and transformed ancestors are out of scope (`packages/liquid-glass/README.md:226`).
2. Safari shows the original under transparent content; give `GlassContent` an opaque background (`packages/liquid-glass/README.md:225`).
3. WebKit draws over-budget filters stretched so glass lands away from its surface; budget blur and displacement (`packages/liquid-glass/src/dom/filter-budget.ts:3-25`).
4. WebKit partial repaints could blank links far from a lens; pad the final merge reach (`packages/liquid-glass/src/dom/filter-reach.ts:1-63`).
5. WebKit page zoom misplaces lenses unless primitive lengths are scaled (`packages/liquid-glass/src/dom/page-zoom.ts:1-9`).
6. Safari async overflow scrolling moves the cached filtered image including stationary glass; wrap the scrollport in `svg > foreignObject` (`packages/liquid-glass/src/react/scene.tsx:149-155`).
7. Chromium can paint blank frames when switching to an undecoded `feImage`; warm images first and keep the old map until the new one is ready (`packages/liquid-glass/src/dom/warm.ts:8-16`, `packages/liquid-glass/src/dom/index.ts:765-766`).
8. Chromium does not always repaint after graph structure changes; the patcher touches an attribute (`packages/liquid-glass/src/dom/filter-patch.ts:44-45`).
9. Gecko caps a filter at 64 operations (`packages/liquid-glass/src/dom/warm.ts:4-7`).
10. Radius mismatch: corners come from `clip-path` with `border-radius: 0`; use the `radius` prop (`packages/liquid-glass/README.md:78`).
11. Fractional scrolling changed traced union maps until unions moved to source-local coordinates (`packages/liquid-glass/src/core/morph-path.ts:146-153`).
12. Native link and image drag cancels a press with `pointercancel`; prevented while pressed (`packages/liquid-glass/src/dom/interaction.ts:128-136`).

## 9. Borrow and avoid

Borrow:
- Bake an expensive per-shape map once, refract live DOM with a cheap per-frame filter (`packages/liquid-glass/src/gpu/maps.wgsl:1-7`, `packages/liquid-glass/src/dom/index.ts:528-590`).
- One outline for both clip and optics, so the rim matches the visible corner (`packages/liquid-glass/src/core/shape.ts:35-37`).
- Quarter-circle bezel profile with a fixed bezel width; testable on CPU (`packages/liquid-glass/src/core/optics.test.ts:3-12`).
- Duration and bounce springs, volume-preserving stretch, and writing `translate`/`scale` instead of `transform`.
- Shader-hash versioned map caches, decode-before-swap, and a demand-driven ticker.
- Per-engine budgets for WebKit (outset, tiling, zoom) as review checklist items.

Avoid or adapt:
- Requiring WebGPU for first paint without a frost fallback in your own app; this plugin's tiers always keep a frosted baseline.
- Hex-only tint that silently ignores other formats; validate and warn instead.
- Low-contrast focus fill; keep a visible outline that meets 3:1.
- No reduced-transparency path for the material itself; add a solid tier.
- UA sniffing as the only engine signal; it is needed for url() backdrop decisions, but keep a safe default for unknown engines.

## 10. License and attribution

MIT, "Copyright (c) 2026 Glass HQ" (`packages/liquid-glass/LICENSE:1-3`). Runtime dependencies (`@lisse/core`, `vgpu`, `@base-ui/react`) carry their own licenses, which are not in the archive; check them before shipping the package. The native reference app bundles Hugeicons paths (MIT, `apps/native-reference/Hugeicons-LICENSE.md`) and the Inter font (SIL OFL 1.1, `apps/native-reference/Resources/Inter-LICENSE.txt:1-5`). This plugin re-derives ideas and does not copy code; if you copy code, keep the Glass HQ MIT notice.
