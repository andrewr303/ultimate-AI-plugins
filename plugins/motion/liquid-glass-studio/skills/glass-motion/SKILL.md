---
name: glass-motion
description: "Designs and implements motion for liquid glass style surfaces on the web and in SwiftUI: press and grow, pointer stretch and elasticity, rubber banding, morphing a button into its menu, merging nearby glass shapes, spring tuning, interruption and reversal, and reduced-motion alternatives. Use when the user asks to \"make the glass feel liquid\", \"add a press or squish effect\", \"stretch toward the cursor\", \"morph the button into a menu\", \"merge glass shapes\", tune springs or bounce on a glass effect, fix glass animation jank or lag, or respect reduced motion on glassmorphism or frosted glass UI. Do not use for static optics such as refraction strength or bezel shape (use glass-optics), for general page animation without glass, or for frame-rate profiling (use glass-performance)."
---

# Glass motion

Make glass respond like a soft material without turning it into motion for its own sake. Small controls give a little under the finger, larger surfaces stay heavy, morphs grow out of the control that opened them, and every animation can be interrupted and reversed from where it is. Reduced motion removes travel and stretch but keeps visible feedback. The models below come from the studied libraries (cited in [motion.md](../../references/motion.md)); the code is original.

## Start here

1. **Inspect the project.** Record the framework, any installed animation library and its version (`npm ls motion framer-motion gsap @react-spring/web`, or the SwiftUI deployment target), how the glass is rendered (this plugin's engine, a library, plain CSS, system glass), and whether the app already has motion tokens (durations, easings, springs). Reuse them.
2. **Find existing reduced-motion handling**: `rg -n "prefers-reduced-motion|accessibilityReduceMotion|reducedMotion|MotionConfig" src`. Extend it rather than adding a second mechanism.
3. **List the interactions in scope**: press, hover light, drag, open or close a menu, tab indicator travel, appear and disappear. Skip anything that is not glass.
4. **Pick one motion vocabulary** (next section) and map each interaction to a named spring before writing code.
5. Record durations, bounces and reduced alternatives in the motion rows of [glass-spec.md](../../templates/glass-spec.md).

## One vocabulary of springs

Name a few springs and reuse them so every surface moves like the same material. glasshq's set, parameterized by perceptual duration and bounce (glasshq `src/core/spring.ts`, cited in [motion.md](../../references/motion.md#22-glasshq-springs-and-volume-preserving-stretch)):

| Spring | Duration (s) | Bounce | Use |
| --- | --- | --- | --- |
| press | 0.24 | 0.2 | the material catching a finger or pointer |
| release | 0.5 | 0.42 | gel-like overshoot back to rest |
| morph | 0.42 | 0.18 | growing into or out of another shape |
| layout | 0.4 | 0.16 | layout changes, tab indicator |
| track | 0.18 | 0 | a lens following a drag |
| glow | 0.42 | 0 | light settling in and out |

Convert for script springs with `k = (2 * PI / duration)^2` and `c = 4 * PI * (1 - bounce) / duration`. SwiftUI's `.spring(duration:bounce:)` takes the same two numbers, so one spec serves web and native. These values are a library's choices, not Apple constants; tune them in context.

## Press, stretch and elasticity

- **Grow on press** by `min(0.16, 8 / max(w, h))` of the press amount: a 44 px button grows up to 16%, a 400 px panel 2% (glasshq `src/dom/interaction.ts`).
- **Stretch** along the drag or pointer axis and squash across it, with volume preserved: `sx = (1 + grow)(1 + ex) / sqrt(1 + ey)`, mirrored for `sy`. Cap the stretch near 0.2 for controls and 0.12 for large surfaces.
- **Rubber band** past a limit instead of stopping hard: `sign(o) * L * (1 - 1 / (|o| * 0.55 / L + 1))`.
- **Write only `translate`, `scale` and custom properties.** An author's `transform` keeps working, and layout size (`offsetWidth`) stays unchanged, so `ResizeObserver` does not loop.
- **Pointer events, one frame.** Store the latest pointer event and apply it in one `requestAnimationFrame` that sleeps once springs settle. Never set framework state on every `pointermove`. Measure on `pointerdown` or `pointerenter` from layout size, never from a transformed rect.
- **Reset on `pointerup`, `pointercancel` and `pointerleave`.** Space and Enter press the same way as a pointer.
- **Hover light only for fine pointers**: gate on `(hover: hover) and (pointer: fine)`.

A complete press recipe with substepped springs, keyboard parity and a reduced path is in [motion.md](../../references/motion.md#3-a-press-and-stretch-recipe). With this plugin's engine, `createGlass(el, { elasticity: 0.3 })` adds a small pull toward the pointer, clamped to 0..1, and turns itself off under `prefers-reduced-motion` ([glass-lab README](../../examples/glass-lab/README.md#controls)).

## Morphing and merging

**Web, refraction tier.** Refraction maps are baked per shape, so a morph needs a planned path of prepared shapes with cross-fades, not a new map every frame. glasshq's approach (leading axis first, drop-like corners in flight, stops spaced by shape distance, content revealed late) is summarized in [motion.md](../../references/motion.md#41-glasshq-a-planned-path-of-prepared-shapes). If your stack has no such planner, morph on the frost tier and switch to refraction at rest.

**Web, frost tier.** Use FLIP: measure the source and target boxes, animate `clip-path: inset(... round r)` or `border-radius` plus `transform` with the Web Animations API, and fade content in after about 40% of the progress so content waits for room. Keep morphing surfaces small, because the blur repaints every frame.

**Become versus detach.** A button that turns into its menu "becomes" it: the source hides during the morph. A drop that leaves its source "detaches" and may show a thinning liquid neck ([motion.md](../../references/motion.md#42-become-versus-detach-and-the-liquid-neck)).

**SwiftUI.** Put both shapes in one `GlassEffectContainer`, give each a `glassEffectID` in a shared namespace, and change state inside `withAnimation(.spring(duration: 0.42, bounce: 0.18))`. Container spacing larger than the stack spacing makes nearby shapes merge at rest. `glassEffectTransition(.materialize)` suits shapes far from a partner. System menus, sheets and toolbars already animate; do not rebuild them to change timing.

## Interruption

- Retarget the running spring and keep its velocity. Never restart from zero.
- Reopening mid-close runs forward from the current point.
- Keep exiting elements mounted (and inert, `aria-hidden`) until the spring settles, then remove them.
- Step with the real frame delta, clamp very long frames (about 64 ms) and reset the timestamp after idle, so 120 Hz screens and background tabs do not change speed or fling the glass.
- Avoid CSS transitions for physics the user can reverse: a retargeted transition restarts its curve with zero velocity.

## Reduced motion

| Motion | Reduced alternative |
| --- | --- |
| Press grow, hover lean, drag stretch | no scale or travel; brighter rim, stronger tint or an inset border |
| Popup morph | appear in place with a short content fade |
| SwiftUI `matchedGeometry` morph | `.materialize` or `.identity` when `\.accessibilityReduceMotion` is true |
| Tab indicator travel | jump to the new tab with a short crossfade |
| Turbulence, specular sweep, tilt, ripples | off |

Listen for live changes (`matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', ...)`) so the setting applies mid-session. Logic must never wait on an animation event that the reduced path removes. More in [motion.md](../../references/motion.md#7-reduced-motion-alternatives).

## Rules

- Every glass animation is interruptible and reversible from its current value.
- Feedback starts on the same frame as the input; work such as network requests runs independently of the animation.
- No continuous animation at rest: no looping sweeps, no idle wobble.
- Pointer handling never re-renders a component tree per move and never measures a transformed rect.
- Reduced motion removes stretch, lean and travel, keeps a visible state change, and reacts to live changes.
- Glass motion uses one named spring set across the product.
- Morphs keep content clipped to the glass and reveal it only when there is room.

## Verify

1. Engine behaviour: `node --test <plugin-root>/tests/engine.test.mjs` if you use or adapt the engine. `<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads).
2. Frame independence: unit test your spring by stepping one second at `dt = 1/60` and at `dt = 1/120`; the values must agree within a small tolerance. A per-frame Euler spring fails this (simple-liquid-glass `src/interactive/spring.ts`, [motion.md](../../references/motion.md#24-simple-liquid-glass-a-lesson-in-frame-dependence)).
3. Real browser, normal speed first: press, drag, release, open and close each surface. Then interrupt: release mid-press, reopen mid-close, click twice fast. Record with Playwright (`recordVideo` on the context) or a screen recording; screenshots cannot show timing.
4. Reduced motion: `page.emulateMedia({ reducedMotion: 'reduce' })` in Playwright, or the DevTools Rendering panel. Test once at load and once switched on while a morph is running. Pass: no scale or travel, feedback still visible.
5. Frame pacing: run the `sampleFrames()` snippet from [performance.md](../../references/performance.md#8-measuring) during the interaction; p95 should fit the refresh budget.
6. SwiftUI: run on a 26+ simulator with Reduce Motion off and on (Simulator Settings > Accessibility > Motion).
7. Report each interaction as checked, not checked or not applicable, and say which engine and device the evidence came from.

## References

- [motion.md](../../references/motion.md): elasticity models, recipes, morphing, interruption, reduced motion, pointer handling
- [accessibility.md](../../references/accessibility.md#7-reduced-motion): the reduced-motion requirement
- [performance.md](../../references/performance.md#6-frame-scheduling-and-skipping): loop scheduling
- [native.md](../../references/native.md#13-swiftui-recipes): SwiftUI glass recipes
- [gotchas.md](../../references/gotchas.md#interaction-and-framework-integration): interaction failure modes
- [glass-lab README](../../examples/glass-lab/README.md): the engine's elasticity option
