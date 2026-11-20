# Liquid glass gotchas

Numbered failure modes with symptom, cause, fix and evidence, collected from the five studied libraries (code comments, tests, changelogs and READMEs) and the platform snapshot. Use the numbers in reviews ("G12: WebKit buffer clamp").

Source keys: glasshq (`@glass-sdk/liquid-glass`, paths under `packages/liquid-glass/`), simple-liquid-glass, liquidGL, ybouane (`@ybouane/liquidglass`), liquid-glass-react. **Inference** marks reasoning not observed in a browser.

## Index

| Group | Entries |
| --- | --- |
| [Compositing and stacking](#compositing-and-stacking) | G1 to G9 |
| [Backdrop capture](#backdrop-capture) | G10 to G16 |
| [Optics and map encoding](#optics-and-map-encoding) | G17 to G26 |
| [Engine-specific rendering](#engine-specific-rendering) | G27 to G38 |
| [WebGL and WebGPU runtime](#webgl-and-webgpu-runtime) | G39 to G45 |
| [Interaction and framework integration](#interaction-and-framework-integration) | G46 to G53 |
| [Accessibility](#accessibility) | G54 to G58 |

## Compositing and stacking

### G1. Glass blurs nothing while a wrapper fades in

- **Symptom:** the backdrop-filtered surface shows an empty or flat background during an entrance animation, then pops in when the animation ends.
- **Cause:** an ancestor with `opacity < 1` (or `filter`, `mask`, `clip-path`, `mix-blend-mode`, `backdrop-filter`) becomes the Backdrop Root, so the glass only sees what is painted inside that ancestor.
- **Fix:** animate `transform` on wrappers, not `opacity`. Audit ancestors for the listed properties. Put fades on the glass element itself.
- **Source:** simple-liquid-glass `README.md` (reports this in Chromium); Filter Effects 2 Editor's Draft, https://drafts.csswg.org/filter-effects-2/ (checked 2026-11-05, High).

### G2. Shared-canvas glass paints under the elements between it and the root

- **Symptom:** labels, badges or cards that sit between grouped glass panes and the scene root appear above or below the glass in the wrong order.
- **Cause:** a shared WebGL canvas draws all grouped panes in one layer, so any element between a pane and the root is either fully above or fully below all of them.
- **Fix:** keep panes eligible (static position, opacity 1, no filter, blend, clip, mask, rotation, own background or negative `z-index`, no non-plain ancestor between pane and root), or opt out with `webglScene="off"`. In liquidGL, give lenses that must share a canvas the same effective `zIndex`.
- **Source:** simple-liquid-glass `src/core/webgl/sharedScene.ts`, `CHANGELOG.md`; liquidGL `scripts/liquidGL.js` (renderer key includes zIndex), `README.md`.

### G3. Output canvas paints beneath the glass's own siblings

- **Symptom:** the refracted canvas vanishes behind a neighbor or behind the glass background.
- **Cause:** ybouane injects its canvas at `z-index:-1`; if the glass element is not a stacking context, the canvas paints in an ancestor's context.
- **Fix:** give each glass element `isolation: isolate` or a `z-index`, and no opaque background (inference from the code).
- **Source:** ybouane `src/LiquidGlass.ts`.

### G4. The root's own background never appears in the glass

- **Symptom:** glass over a section shows white where the section's background should be.
- **Cause:** ybouane captures only the root's children and starts each scene from white.
- **Fix:** put backgrounds in a sibling element inside the root.
- **Source:** ybouane `README.md`, `src/LiquidGlass.ts`.

### G5. Original content shows through its refracted copy in Safari

- **Symptom:** doubled, ghosted text or images under glass in Safari.
- **Cause:** with a content-layer filter, a transparent content element lets the unfiltered original show beneath.
- **Fix:** give the content layer an opaque background.
- **Source:** glasshq `README.md`.

### G6. Injected layers break `:first-child` or `:last-child` styling

- **Symptom:** child spacing or borders shift after glass initializes.
- **Cause:** ybouane inserts its canvas as the glass's first child; glasshq's Firefox path appends a layer as the surface's last child.
- **Fix:** avoid structural pseudo-classes on glass children, or target classes instead.
- **Source:** ybouane `README.md`; glasshq `README.md`, `src/dom/lens-layers.ts`.

### G7. Shadow halo is cut off

- **Symptom:** a hard edge on the drop shadow, usually at the bottom.
- **Cause:** ybouane draws its shadow inside a fixed 20 px pad, and `overflow: hidden` ancestors clip the halo. A `shadowSpread` well above 10 or a large offset exceeds the pad (derived).
- **Fix:** size the pad to the shadow spread plus offset; keep clipping ancestors away from glass.
- **Source:** ybouane `README.md`, `src/defaults.ts` (`SHADOW_PAD = 20`), `src/shaders.ts`.

### G8. Lens vanishes when tilt and `clip-path` combine

- **Symptom:** a tilting lens disappears.
- **Cause:** `clip-path` conflicts with `perspective` and `preserve-3d` on the tilted element.
- **Fix:** use `border-radius` with `overflow: hidden` instead of `clip-path`.
- **Source:** liquidGL `demos/frost-specular.html`.

### G9. Blend-mode rim layers change look inside isolated parents

- **Symptom:** the rim highlight looks different on one page than another.
- **Cause:** `mix-blend-mode` layers only blend with content in the same stacking context; a parent with `transform`, `filter` or `isolation` changes what they blend with.
- **Fix:** test rims inside every container type that hosts glass (inference).
- **Source:** liquid-glass-react `src/index.tsx`.

## Backdrop capture

### G10. iOS Safari crashes when the backdrop is an ancestor of the glass

- **Symptom:** tab reload or crash on iOS after enabling glass.
- **Cause:** an auto-detected backdrop that contains the lens is cloned on every mutation, and each clone triggers the observer again, exhausting memory.
- **Fix:** require an explicit sibling or background backdrop; reject any source that contains the glass or is contained by it.
- **Source:** simple-liquid-glass `CHANGELOG.md`, `src/core/webgl/useWebGL.ts`.

### G11. Cross-origin images taint the capture

- **Symptom:** glass goes blank or stops updating; console errors repeat every frame.
- **Cause:** a cross-origin image without CORS approval taints the canvas, so texture upload fails. ybouane's render loop logs the error every frame and disables glass for the whole root (inferred).
- **Fix:** serve images with `Access-Control-Allow-Origin` and set `crossorigin="anonymous"`, or mark them ignored.
- **Source:** ybouane `README.md`, `src/LiquidGlass.ts`; liquidGL `README.md`; simple-liquid-glass `src/core/webgl/runtime.ts`.

### G12. Iframes, embeds and some media are missing from the refraction

- **Symptom:** glass over an embedded map, video or iframe shows a hole or stale frame.
- **Cause:** DOM capture cannot read iframe content; liquidGL's rasterizer skips `<video>` and `<iframe>` and composites video separately; media nested inside an HTML source is captured as a still.
- **Fix:** pass `<video>` or `<canvas>` as the backdrop source directly, or use a Tier 2 path that refracts the live page in Chromium.
- **Source:** liquidGL `scripts/liquidGL.js`; simple-liquid-glass `README.md`; same-origin policy (platform snapshot, Medium).

### G13. Refracted text does not line up with live text

- **Symptom:** text under glass looks shifted or in another font.
- **Cause:** web fonts not loaded or not CORS-readable at capture time; html-to-image 1.11.13 floors every font size and subtracts 0.1 px, so captured glyphs come out smaller.
- **Fix:** await `document.fonts.ready` before init, serve fonts with CORS, and remove the font-size shrink (ybouane patches it).
- **Source:** ybouane `README.md`, `src/HtmlCapture.ts`, `patches/html-to-image+1.11.13.patch`.

### G14. Animated or changed content is not refracted

- **Symptom:** glass shows an old state of content beneath it.
- **Cause:** captured snapshots are static.
- **Fix:** register changes explicitly: `liquidGL.registerDynamic()`, ybouane `data-dynamic` or `markChanged()`, simple-liquid-glass `backdropVersion` or `refreshBackdrop()`.
- **Source:** liquidGL `README.md`; ybouane `README.md`; simple-liquid-glass `README.md`.

### G15. Position-only animation of a liquidGL lens in tilt mode

- **Symptom:** a lens moved with `left`/`top` or a translate samples its old spot. In liquidGL 3.0.0 the code points to tilt (mirror) mode as the only case where this can happen; runtime behavior is unverified (not observed in a browser).
- **Cause:** liquidGL runs a self-rescheduling `requestAnimationFrame` loop that calls `render()` every frame (`scripts/liquidGL.js:21-29`, started at `:8845`), and `render()` calls `updateMetrics()` on every lens (`:6110`). `updateMetrics()` re-reads `getBoundingClientRect()` unless mirror mode is active, where it reuses a cached `_baseRect` (`:7957-7962`). A demo comment says lenses refresh only through the `ResizeObserver` (`demos/ai-search.html:719-721`); the 3.0.0 render loop contradicts it.
- **Fix:** outside tilt mode, do nothing: the per-frame loop picks up the new position. Do not copy the demo's `updateMetrics()` plus `render()` call into every animation update, because that renders a second time per frame. In tilt mode, confirm in a browser before adding manual updates.
- **Source:** liquidGL `scripts/liquidGL.js`, `demos/ai-search.html`.

### G16. Long pages lose snapshot resolution

- **Symptom:** blurry or blocky refraction on long documents.
- **Cause:** a document-sized snapshot is scaled down to fit the GPU texture limit.
- **Fix:** snapshot a smaller background element instead of `body`.
- **Source:** liquidGL `README.md`, `scripts/liquidGL.js`.

## Optics and map encoding

### G17. The whole surface drifts by a fraction of a pixel

- **Symptom:** text and edges under glass shimmer or sit slightly off even where no refraction is intended.
- **Cause:** 8-bit neutral 128 decodes to 0.50196, not 0.5, so every pixel moves by `scale * 0.00196` px.
- **Fix:** subtract `1/510` from the X and Y channels; use `feColorMatrix` for the offset in Chromium, which re-quantizes component-transfer tables.
- **Source:** simple-liquid-glass `src/core/DisplacementFilter.tsx`, `src/core/LiquidGLSvgFilter.tsx`. See [optics.md](optics.md#52-the-128-neutral-pitfall).

### G18. Blocky noise or a constant offset from JPEG maps

- **Symptom:** faint blocks in refracted content; the center is not neutral.
- **Cause:** lossy compression of vector data; liquid-glass-react's baked JPEG maps center at R 124 / B 132 with green noise up to 18.
- **Fix:** store maps as PNG or generate them at runtime.
- **Source:** liquid-glass-react `src/utils.ts` (pixel measurement in the source dossier).

### G19. Vertical refraction missing, content shifted up or down

- **Symptom:** in liquid-glass-react's `prominent` mode, only horizontal edges refract and the backdrop slides vertically.
- **Cause:** the filter reads Y from the blue channel, but the `prominent` PNG stores Y in green and has blue at 0, which decodes as a constant full-strength offset.
- **Fix:** put Y in the channel the filter reads, or set `yChannelSelector` to match the map.
- **Source:** liquid-glass-react `src/index.tsx`, `src/utils.ts`, `src/shader-utils.ts` (shader mode copies G into B for this reason).

### G20. Corners and vertical bending disappear on wide pills

- **Symptom:** a wide capsule refracts like a flat strip.
- **Cause:** `preserveAspectRatio="xMidYMid slice"` scales a square map to cover and crops its top and bottom.
- **Fix:** use `preserveAspectRatio="none"` and generate the map at the element's aspect ratio.
- **Source:** liquid-glass-react `src/index.tsx`; glasshq `src/dom/map-image.ts` (uses `none`).

### G21. Half the displacement range saturates

- **Symptom:** refraction plateaus abruptly instead of growing toward the rim.
- **Cause:** encoding `d / max + 0.5` maps [-max, max] to [-0.5, 1.5], and the clamp clips the stronger half.
- **Fix:** encode `d / (2 * max) + 0.5` and set `scale = 2 * max`.
- **Source:** liquid-glass-react `src/shader-utils.ts`.

### G22. Content folds or tears at corners under strong refraction

- **Symptom:** mirrored slivers or torn seams in corners at high strength.
- **Cause:** the displacement stops being one-to-one (its Jacobian determinant goes negative).
- **Fix:** widen the neutral band at the edge as strength grows and attenuate amplitude past a ceiling; cap travel relative to the short side; test the Jacobian on a grid.
- **Source:** simple-liquid-glass `src/core/displacementField.ts`, `CHANGELOG.md`, `README.md` (10% cap for classic maps).

### G23. Edge pixels smear or clip at the rim

- **Symptom:** streaks at the outer rim, or refracted content cut off.
- **Cause:** refraction reach exceeds the sampled pad or SVG filter region; samples clamp to the crop edge. ybouane's rim offset (about 60 device px at defaults, derived) exceeds its 20 px pad.
- **Fix:** pad the filter region or crop by maximum reach plus blur: `ceil(|scale| * (1 + 0.22 * dispersion) / 2 + 3 * blur + 2)` in simple-liquid-glass.
- **Source:** ybouane `src/shaders.ts`, `src/GlassRenderer.ts`; simple-liquid-glass `src/core/materialFilter.ts`.

### G24. Refraction ignores the corner radius

- **Symptom:** the clip is rounded but the bending pattern is not; rims look offset in corners.
- **Cause:** the optical map and the CSS clip use different shapes: fixed baked maps (liquid-glass-react), only the top-left radius read (liquidGL), or a CSS radius out of sync with the filter (fixed in simple-liquid-glass 1.2.3).
- **Fix:** derive the clip path and the map from one outline and one radius, clamped to half the short side.
- **Source:** liquid-glass-react `src/index.tsx`; liquidGL `scripts/liquidGL.js`; simple-liquid-glass `CHANGELOG.md`; glasshq `src/core/shape.ts`, `README.md`.

### G25. Blur looks weaker on high-DPR screens

- **Symptom:** the same setting looks half as frosted on a 2x display.
- **Cause:** blur step measured in device pixels without DPR scaling.
- **Fix:** multiply blur radii by `devicePixelRatio` in shader paths.
- **Source:** ybouane `src/GlassRenderer.ts`.

### G26. Glass near the content edge refracts transparency

- **Symptom:** dark or empty bands where glass overlaps the edge of the content layer.
- **Cause:** displacement samples past the source image read transparent pixels.
- **Fix:** emulate clamp-to-edge with edge tiles (glasshq), smear edge rows into the pad (simple-liquid-glass), or fade refraction out for out-of-bounds samples (liquidGL).
- **Source:** glasshq `src/dom/filter-bounds.ts`; simple-liquid-glass `src/core/webgl/runtime.ts`; liquidGL `scripts/liquidGL.js`.

## Engine-specific rendering

### G27. Glass lands away from its surface in WebKit

- **Symptom:** in Safari, refraction is drawn stretched or offset on large scenes.
- **Cause:** WebKit sums the outsets of blur and displacement primitives and clamps the filter buffer to 4096 x 4096 device pixels, then draws the result stretched.
- **Fix:** keep the sum of outsets inside the budget; soften blur and displacement proportionally when it would overflow.
- **Source:** glasshq `src/dom/filter-budget.ts`.

### G28. WebKit page zoom scales lenses toward the origin

- **Symptom:** at browser zoom other than 100%, Safari draws lenses shifted and scaled.
- **Cause:** WebKit reads filter user-space lengths unzoomed.
- **Fix:** measure zoom (binary search on `min-resolution`) and multiply primitive lengths by it.
- **Source:** glasshq `src/dom/page-zoom.ts`.

### G29. Safari refilters the whole content layer on every caret blink or hover

- **Symptom:** high CPU and jank in Safari when anything small changes.
- **Cause:** WebKit reapplies reference filters on every paint of the filtered element.
- **Fix:** give the content its own compositing layer with `will-change: transform`; restore author `will-change` on teardown.
- **Source:** glasshq `src/dom/filter-paint-root.ts`.

### G30. Stationary glass slides with scrolled content in Safari

- **Symptom:** in a scrolling region, glass moves with content during async scroll.
- **Cause:** Safari's async overflow scrolling translates the cached filtered image, glass included.
- **Fix:** wrap the scrollport in `svg > foreignObject`, and filter the scrollport itself.
- **Source:** glasshq `src/react/scene.tsx`, `src/dom/progressive.ts`.

### G31. Hovering far from any lens erases content in WebKit

- **Symptom:** a link far from glass disappears on hover in Safari.
- **Cause:** a primitive subregion missed the dirty region during partial repaint.
- **Fix:** extend the final merge's reach with transparent `feOffset` padding.
- **Source:** glasshq `src/dom/filter-reach.ts`, `src/dom/filter-reach.test.ts`.

### G32. Firefox drops the whole filter chain

- **Symptom:** in Firefox, every glass effect on an element disappears at once when one more surface is added.
- **Cause:** Gecko drops CSS filter chains above 64 operations per element.
- **Fix:** count primitives per element; split scenes or cap probes (glasshq caps warmer probes at 48 per filter).
- **Source:** glasshq `src/dom/warm.ts`, `src/dom/maps.ts`, `src/dom/progressive.ts`.

### G33. Firefox repaints are slow with image-based filters

- **Symptom:** low frame rate in Firefox whenever anything on the page paints.
- **Cause:** Gecko renders filters with images or displacement in software and re-rasterizes them on every paint.
- **Fix:** give each surface its own `-moz-element()` layer with a small filter, so an unchanged layer is never rasterized again.
- **Source:** glasshq `src/dom/lens-layers.ts`.

### G34. A blank frame when a new map is first used in Chromium

- **Symptom:** glass blinks when its shape changes.
- **Cause:** a newly referenced `feImage` paints blank until decoded.
- **Fix:** decode maps with `Image.decode()` before swapping, keep the old map until the new one is warm, and pre-warm with hidden probes.
- **Source:** glasshq `src/dom/maps.ts`, `src/dom/warm.ts`, `src/dom/index.ts`.

### G35. Chromium does not repaint after a filter graph edit

- **Symptom:** an updated filter shows the old result until something else repaints.
- **Cause:** Chromium does not always repaint after filter graph structure changes; a detached `feImage` does not repaint when its image arrives.
- **Fix:** touch an attribute (glasshq rewrites `x`) after structural edits; link images only after the graph is connected.
- **Source:** glasshq `src/dom/filter-patch.ts`.

### G36. Two glass instances share one look

- **Symptom:** every instance renders with the first instance's map or filter.
- **Cause:** duplicate filter or `feImage` ids across instances (liquid-glass-react emits `id="feimage"` in each); duplicate `result` names inside one graph.
- **Fix:** generate a unique, `url()`-safe id per instance and per filter; reject duplicate result names.
- **Source:** liquid-glass-react `src/index.tsx`; glasshq `src/dom/filter-patch.ts`.

### G37. Safari pays for an SVG filter it never shows

- **Symptom:** slow Safari rendering with no visible refraction.
- **Cause:** the displacement filter stays attached on engines that cannot render it; liquid-glass-react only skips it for Firefox.
- **Fix:** detach the filter outside Chromium and keep the Tier 1 frost.
- **Source:** liquid-glass-react `src/index.tsx`; WebKit bug 245510, https://bugs.webkit.org/show_bug.cgi?id=245510 (checked 2026-11-05, High).

### G38. No blur at all on older Safari

- **Symptom:** a flat translucent box on Safari 17 and earlier.
- **Cause:** Safari before 18 needs `-webkit-backdrop-filter`; inline React styles do not add prefixes.
- **Fix:** always emit both declarations.
- **Source:** liquid-glass-react `src/index.tsx`; https://github.com/mdn/browser-compat-data/blob/main/css/properties/backdrop-filter.json (checked 2026-11-05, High).

## WebGL and WebGPU runtime

### G39. `GL_INVALID_OPERATION` on real GPUs only

- **Symptom:** materials work in unit tests but fail in a browser.
- **Cause:** sending `uniform1f` to a GLSL `int` uniform; mocked WebGL contexts never validated it.
- **Fix:** read uniform types with `getActiveUniform` after linking and call the matching `uniformNi` or `uniformNf`; test on a real GPU.
- **Source:** simple-liquid-glass `CHANGELOG.md`.

### G40. Drawing past a surface's own box is silently clipped

- **Symptom:** bleed, rim or shadow beyond the panel box is lost, or shifted.
- **Cause:** a scissor rectangle can only shrink what the viewport covers; clamping the near edge to 0 shifted rects.
- **Fix:** widen the viewport once to the union of all rects, then scissor per rect.
- **Source:** simple-liquid-glass `CHANGELOG.md`.

### G41. Glass stops rendering after a GPU reset

- **Symptom:** glass freezes or goes blank after sleep, driver update or tab backgrounding.
- **Cause:** `webglcontextlost` not handled (liquidGL); every texture, program and buffer dies with the context.
- **Fix:** call `preventDefault()` on context loss, rebuild on `webglcontextrestored`, invalidate all caches, and mark everything dirty.
- **Source:** liquidGL `scripts/liquidGL.js` (no handler); ybouane `src/GlassRenderer.ts` (handles it); simple-liquid-glass `src/core/webgl/runtime.ts`.

### G42. Too many WebGL contexts

- **Symptom:** older glass instances go blank as new ones mount.
- **Cause:** browsers cap concurrent WebGL contexts (ybouane warns of about 16); allocating contexts for offscreen panels exhausts them.
- **Fix:** share one context per page or per stacking group; allocate only when visible.
- **Source:** ybouane `README.md`; simple-liquid-glass `CHANGELOG.md`, `src/core/webgl/contextPool.ts`; liquidGL `scripts/liquidGL.js`.

### G43. Dark fringes or double-darkened edges

- **Symptom:** antialiased edges look too dark or haloed.
- **Cause:** mixing straight and premultiplied alpha; blending a straight-alpha result again squares alpha; some `transferToImageBitmap` implementations mishandle straight alpha.
- **Fix:** pick one convention per context, disable blending where the shader already composites, and probe bitmap transfer before trusting it.
- **Source:** simple-liquid-glass `src/vendor/ybouane/GlassRenderer.ts`, `src/core/webgl/liquidGLOptics.ts`.

### G44. Lenses stay unstyled after GPU setup fails

- **Symptom:** plain, un-glassed elements in some browsers.
- **Cause:** the CSS fallback is chosen only by a synchronous check; when `navigator.gpu` exists but the adapter or device fails and WebGL also fails, lenses keep their original styles.
- **Fix:** fall back to Tier 1 on any asynchronous failure.
- **Source:** liquidGL `scripts/liquidGL.js`.

### G45. No glass at all without WebGL

- **Symptom:** `init()` rejects and elements show no styling.
- **Cause:** ybouane throws when WebGL is unavailable and ships no fallback.
- **Fix:** catch the failure and apply Tier 1 CSS.
- **Source:** ybouane `src/GlassRenderer.ts`.

## Interaction and framework integration

### G46. Pointer movement re-renders every layer

- **Symptom:** jank while moving the mouse over glass.
- **Cause:** two state updates per `mousemove` and four or more layout reads per render, with no frame batching.
- **Fix:** keep pointer data in refs; write `transform` and CSS variables in one `requestAnimationFrame` callback.
- **Source:** liquid-glass-react `src/index.tsx`.

### G47. The effect stops at the top or left edge of the viewport

- **Symptom:** elastic motion freezes when the pointer touches row 0 or column 0.
- **Cause:** `0` treated as "no pointer" by a falsy check.
- **Fix:** use `null` for "unset" and compare explicitly.
- **Source:** liquid-glass-react `src/index.tsx`.

### G48. Server render crashes or hydration mismatches

- **Symptom:** `navigator is not defined` on the server, or a hydration warning.
- **Cause:** reading `navigator.userAgent` during render.
- **Fix:** detect in an effect or a client-only module; use a framework id hook for filter ids.
- **Source:** liquid-glass-react `src/index.tsx`; simple-liquid-glass `src/core/useStableId.ts`.

### G49. Maps undersized after an entrance animation, or springs chasing themselves

- **Symptom:** a lens map too small after a scale-in; an elastic element that drifts.
- **Cause:** measuring with `getBoundingClientRect`, which includes the current transform.
- **Fix:** measure `offsetWidth`/`offsetHeight`; subtract the current spring translation before computing the center.
- **Source:** simple-liquid-glass `src/core/useGeometry.ts`, `src/interactive/index.tsx`, `CHANGELOG.md`; ybouane `src/LiquidGlass.ts`.

### G50. Glass controls ignore clicks

- **Symptom:** buttons on glass do not respond.
- **Cause:** liquidGL sets `pointer-events: none` on non-draggable lens elements.
- **Fix:** restore `pointer-events: auto` on interactive children (its demos do this).
- **Source:** liquidGL `scripts/liquidGL.js`, `demos/ai-search.html`.

### G51. Tilt bakes in the wrong base transform

- **Symptom:** a tilting lens stays scaled to 0 or offset after an entrance animation.
- **Cause:** tilt caches the element's inline transform on first bind.
- **Fix:** animate a wrapper, never the lens element.
- **Source:** liquidGL `demos/frost-specular.html`, `scripts/liquidGL.js`.

### G52. Author `transform` and `transition` disappear

- **Symptom:** custom positioning or animation on the glass is lost.
- **Cause:** the component overwrites `style.transform` and `style.transition`.
- **Fix:** write individual `translate` and `scale` properties so author `transform` composes.
- **Source:** liquid-glass-react `src/index.tsx`; glasshq `src/dom/interaction.ts`.

### G53. Over-light darkening does nothing

- **Symptom:** `overLight` has no visible effect.
- **Cause:** the layers depend on Tailwind utility classes the host app may not ship.
- **Fix:** use inline styles or shipped CSS for behavior-critical layers.
- **Source:** liquid-glass-react `src/index.tsx`.

## Accessibility

### G54. Focus indicator is nearly invisible

- **Symptom:** keyboard users cannot see which glass control has focus.
- **Cause:** `:focus-visible` replaces the outline with an 8% `currentColor` background, and slider and switch thumbs set `outline: none`.
- **Fix:** keep a visible outline with 3:1 contrast against the worst backdrop; never remove it without an equal replacement.
- **Source:** glasshq `src/styles.css`. See [accessibility.md](accessibility.md).

### G55. Surfaces are hidden until JavaScript runs

- **Symptom:** blank toolbars without JavaScript or before hydration; content missing from the accessibility tree.
- **Cause:** `visibility: hidden` until the clip path is written.
- **Fix:** hide with `opacity` for a bounded time (simple-liquid-glass caps it at 400 ms and keeps content in the accessibility tree) or render the frosted look on the server.
- **Source:** glasshq `src/styles.css`; simple-liquid-glass `src/index.tsx`, `README.md`.

### G56. Text under glass cannot be selected

- **Symptom:** users cannot select or copy text in the glass region.
- **Cause:** ybouane forces `user-select: none` on the whole root.
- **Fix:** limit `user-select: none` to draggable handles.
- **Source:** ybouane `src/LiquidGlass.ts`.

### G57. Motion runs regardless of reduced-motion settings

- **Symptom:** animated highlights, tilt, fluid deformation or elastic stretch continue for users who asked for less motion.
- **Cause:** no `prefers-reduced-motion` handling (liquidGL, ybouane, liquid-glass-react); liquidGL's time-based specular also forces continuous rendering.
- **Fix:** honor the media query live; make highlights static under reduced motion. glasshq lets the system preference always win over a component prop.
- **Source:** liquidGL `scripts/liquidGL.js`; ybouane `src/` (no `prefers-` media queries anywhere); liquid-glass-react `src/index.tsx`; glasshq `src/dom/interaction.ts`.

### G58. Clickable glass is not a button

- **Symptom:** keyboard and screen-reader users cannot activate glass controls.
- **Cause:** `onClick` on a plain `div` with no role, `tabindex` or key handling; pointer-only drag with no keyboard alternative.
- **Fix:** render a real `<button>` (or wrap an accessible primitive, as glasshq does with Base UI); add keyboard alternatives for drag.
- **Source:** liquid-glass-react `src/index.tsx`; liquidGL `scripts/liquidGL.js`; ybouane `src/LiquidGlass.ts`; glasshq `README.md`.

## Related references

- [optics.md](optics.md), [web-techniques.md](web-techniques.md), [browser-support.md](browser-support.md)
- [performance.md](performance.md) and [accessibility.md](accessibility.md) for cost and inclusive design rules
