---
name: glass-performance
description: "Measures and budgets the cost of liquid glass style surfaces: a cost model per rendering tier (CSS backdrop blur, SVG displacement, map generation, WebGL capture, native containers), map caching, device pixel ratio caps, instance limits with hysteresis, resize and scroll handling, frame scheduling, a repeatable measurement procedure and starting budgets. Use when the user says \"the glass effect is slow\", \"glassmorphism lags on scroll\", \"frosted glass drops frames on mobile\", \"refraction makes the page janky\", \"how many glass panels can I have\", or asks to profile, optimize or set a performance budget for a liquid glass or Apple glass style UI. Do not use for general page speed work without glass, for optics tuning that does not affect cost (use glass-optics), or for choosing a library by features (use glass-library-select)."
---

# Glass performance

Glass reads what is behind it, and every technique pays for that read somewhere: in the compositor for backdrop blur, in a filter graph that reruns while anything moves for SVG displacement, in map generation on the CPU or GPU, or in copying the page into a texture for WebGL. This skill finds which of those costs dominates on the slowest device you support, measures it while the glass moves, and brings it inside a budget with caching, DPR caps, instance limits and frame scheduling. Library numbers quoted in the references are author measurements, labeled as such.

## Start here

1. **Identify the tier per engine.** Read how glass is built (this plugin's engine, a library from [library-matrix.md](../../references/library-matrix.md), hand-written CSS, system glass). If the engine is in use, log `glass.info` (tier, engine, width, height, pixelRatio) from the `onRender` callback. Run `node <plugin-root>/scripts/glass_probe.mjs --json` from the user's project to see which engines actually render refraction and blur; cost differs by tier.
2. **Count surfaces** visible at once, their sizes, and whether they overlap.
3. **Name the target device** (the slowest one you support) and its refresh rate, and the interaction that feels slow: scroll under glass, drag, open a menu, resize, first load.
4. **Reproduce before changing code.** Record a trace of the slow interaction (procedure below). Optimizing an idle page proves nothing.
5. Write the budget you will hold into the performance rows of [glass-spec.md](../../templates/glass-spec.md).

## Cost model

| Tier | Where it costs | Grows with |
| --- | --- | --- |
| CSS `backdrop-filter` blur | compositor, each frame the glass or its backdrop changes | glass area, blur radius (it reads past the box), overlapping surfaces |
| SVG displacement in `backdrop-filter` or `filter: url()` | one GPU pass per primitive per moving frame; map bytes resent while moving | primitive count, filter region area, map resolution, pane count |
| Map generation | main thread or GPU, once per size change | width x height x DPR squared |
| WebGL over a captured backdrop | DOM serialization, upload, shader passes, readbacks | captured DOM size, capture resolution, recapture frequency |
| Native system glass | the system compositor | number of separately rendered glass views; containers render them together |

Details and evidence per library: [performance.md](../../references/performance.md#1-cost-model-per-tier).

Map generation is easy to underestimate. On the machine that built this plugin (Node 22, single run, 2026-11-05), `displacementField` took about 12 ms for a 200 x 56 pill at DPR 2 and about 80 ms for an 800 x 400 panel at DPR 2, several frames of main thread for the large one. Measure your own sizes (write `<plugin-root>` as an absolute path):

```sh
node --input-type=module -e "
import { displacementField } from '<plugin-root>/examples/glass-lab/liquid-glass.js';
const t = performance.now();
displacementField({ width: 800, height: 400, radius: 32, pixelRatio: 2 });
console.log((performance.now() - t).toFixed(1) + ' ms');"
```

## Fixes, cheapest first

1. **Shrink the glass.** Refraction belongs on small floating controls. Panels wider than half the viewport get a standard frosted material or a solid surface.
2. **Cache maps by geometry.** Key on width, height, radius, DPR and every optic parameter, bound the cache with LRU eviction, and decode images before swapping a filter so the switch draws in one frame. The engine caches 24 entries and exposes `clearGlassCache()`; glasshq and simple-liquid-glass bounds are in [performance.md](../../references/performance.md#2-caching).
3. **Cap DPR at 2** and scale every length (blur, bezel, displacement) by the same ratio. The engine's `maxPixelRatio` defaults to 2. Re-read DPR when a window moves between screens.
4. **Limit instances.** Plan for 3 to 6 refractive surfaces visible at once. Past about 12, render through one shared canvas or downgrade the extras to frost, with hysteresis (switch at 16, back at 12) so a changing list does not flap. Share one WebGL context per page; browsers cap concurrent contexts.
5. **Do no work on scroll.** Position glass in content coordinates or move sample coordinates; never recapture or rebuild maps on scroll. Use passive listeners.
6. **Measure with `ResizeObserver` and layout size** (`offsetWidth`), coalesce callbacks into one frame, and debounce expensive rebuilds. Add `will-change: transform` only while a surface moves.
7. **One `requestAnimationFrame` loop that sleeps** when nothing is dirty, skips hidden documents, and pauses off-screen surfaces with `IntersectionObserver`. No continuous animation at rest.
8. **Move map generation off the main thread** (worker or GPU) when sizes vary often, and never generate on pointer move.
9. **Shorten the filter graph.** Every primitive is a pass; give primitives explicit subregions and drop ones that do nothing visible.
10. **Native:** group glass in `GlassEffectContainer`, `UIGlassContainerEffect` or `NSGlassEffectContainerView`, which Apple says render together for better performance. On Android, branch blur and shader paths by API level and honor the cross-window blur listener.

Engine-specific limits (WebKit 4096 px filter buffer, Gecko 64 filter operations per element, WebGL texture size) are in [performance.md](../../references/performance.md#7-engine-limits) with their workarounds.

## Measurement procedure

Measure on the slowest target, with the real backdrop, while the glass moves.

1. **Chrome DevTools Performance panel** with 4x or 6x CPU throttling on desktop runs. Record the slow interaction. Look for long tasks during map generation, style and layout from pointer moves, and long paint or composite during scroll.
2. **Rendering drawer:** paint flashing (the whole content layer flashing while one lens moves means the filter covers too much), layer borders, frame rendering stats.
3. **Frame pacing:** run the `sampleFrames()` snippet from [performance.md](../../references/performance.md#8-measuring) during the interaction and compare p95 with the frame budget (16.7 ms at 60 Hz, 8.3 ms at 120 Hz).
4. **Field data:** feature-detect `long-animation-frame` in `PerformanceObserver` and log long frames with the glass tier attached.
5. **Every tier and preference path:** repeat with frost forced and with the solid tier, so a fallback is not secretly slower.
6. **Native:** Xcode Instruments (Animation Hitches, Time Profiler) on a real device; Android `adb shell dumpsys gfxinfo <package>` or a Perfetto trace.
7. Record device, OS, browser version, DPR, surface count and the numbers before and after each change.

## Budgets

Starting budgets from [performance.md](../../references/performance.md#9-budgets); adjust them from measurements on your slowest device.

| Budget | Value |
| --- | --- |
| Frame time during glass interaction | p95 within the refresh budget |
| Glass script per frame | at most 4 ms of main thread |
| Map generation | off the main thread, or under one frame per map; never on pointer move |
| Visible refractive surfaces | 3 to 6 typical; change strategy at about 12 to 16 |
| Rendering DPR | at most 2 |
| WebGL recapture | never on scroll; content changes debounced 120 to 250 ms |
| Continuous animation | none at rest |
| First paint | frost or solid visible immediately; refraction may arrive later |

## Rules

- Measure the slow interaction before and after every change, on the slowest supported device; never claim a gain you did not measure.
- Keep refraction on small floating controls; large surfaces get frost or solid.
- Bound every cache, cap DPR at 2, and share contexts and loops.
- No work on scroll and no rendering at rest.
- A performance fix never removes a fallback, a preference path or a focus style.
- Report measured numbers with their environment; label inferences as inferences.

## Verify

`<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Run plugin scripts from the user's project directory by path; output paths resolve against the current directory.

1. `node --test <plugin-root>/tests/engine.test.mjs` after touching engine map, cache or filter code.
2. `node <plugin-root>/scripts/glass_probe.mjs --browsers chromium,firefox,webkit --json` to confirm which tier each engine renders after the change.
3. The measurement procedure above, before and after, with the same device, DPR and interaction. Pass: the budgets hold, or the report says which one does not and why.
4. Real-browser screenshots of each tier after the change, to show the optimization did not degrade the look or drop a fallback.

## References

- [performance.md](../../references/performance.md): cost model, caching, DPR, instance limits, scheduling, engine limits, measuring, budgets
- [gotchas.md](../../references/gotchas.md#engine-specific-rendering): engine bugs behind the limits
- [web-techniques.md](../../references/web-techniques.md#2-when-to-pick-each-tier): choosing a cheaper tier
- [motion.md](../../references/motion.md#8-pointer-handling-without-re-renders): pointer handling without re-renders
- [glass-lab README](../../examples/glass-lab/README.md#how-the-engine-works): how the engine caches and rebuilds
