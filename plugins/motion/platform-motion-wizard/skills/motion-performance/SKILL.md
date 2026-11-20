---
name: motion-performance
description: "Use when motion stutters, input feedback is late, scrolling or dragging drops frames, layouts jump, or animation work consumes excessive CPU, GPU, or memory. Profile the real interaction and make targeted fixes; use motion-review for an assessment without implementation."
---

# Motion performance

Find the work that blocks the user's action, then remove or reschedule it. Read [performance](../../references/performance.md); keep [verification](../../references/verification.md) open when recording evidence. Smoothness is observed behavior, not a property guaranteed by an animation library.

## Establish a reproducible baseline

1. Read project instructions, lockfile, runtime versions, existing profiling tools, and performance budgets. Preserve the current architecture unless evidence requires a change.
2. Reproduce one high-value flow with a precise input sequence and a realistic amount of data. Include repeated interaction after initial warm-up.
3. Record environment: device class, OS, browser/runtime, viewport, refresh rate if known, build mode, motion preference, data size, and any throttling.
4. Observe normal-speed behavior. Then capture the smallest useful performance trace, profiler recording, or frame analysis; screenshots cannot demonstrate smoothness.
5. Separate startup, input acknowledgement, network waiting, transition execution, and cleanup. Locate the phase that causes visible friction.

Use a production-like build when practical. A development trace can locate work but does not establish production performance. State the limitation if only a desktop emulator or remote browser is available.

## Diagnose before changing motion

Classify the evidence:

| Symptom | Inspect first | Possible focused action |
| --- | --- | --- |
| Press appears late | Event handler, long task, sync rendering | Show pending state and move nonessential work out of the blocking path |
| Drag lags behind pointer | Per-frame state updates, layout reads, capture handling | Use the stack's gesture/motion values and batch geometry work |
| Sheet stutters | Layout, paint, filters, raster layers | Reduce affected area or simplify the expensive property |
| List jumps | Keys, image dimensions, virtualization, measurement | Preserve identity, reserve geometry, coordinate with virtualizer |
| Page slows after use | Retained nodes, listeners, observers, loops | Clean up the actual owner on cancel and unmount |
| High idle activity | Repeating animation, timers, offscreen work | Stop optional motion when hidden or irrelevant |

Confirm the suspected cause with trace evidence or a controlled small change. Do not replace the motion library as an unexplained first step.

## Implement the narrow fix

1. Keep one writer per animated property. If nested effects compete, give them distinct wrappers or consolidate ownership.
2. Prefer compositor-suitable properties where they express the design, but verify paint and compositing. Transforms and opacity can still be expensive across large surfaces or layers.
3. Batch geometry reads before writes. Measure on meaningful layout changes and reuse valid geometry; avoid a forced layout for every pointer event.
4. Use the platform's animation scheduler or existing motion values for continuous visual updates. Keep business state and semantic announcements out of frame-by-frame work.
5. Narrow layout animation scope. Handle images, fonts, responsive resizing, and dynamic content rather than caching permanently incorrect measurements.
6. Coordinate virtualization with animation: animate mounted, stable items only; preserve scroll anchors, focused items, and measured sizes. Never disable virtualization merely to animate every row.
7. For custom auto-scroll or simulation, derive distance from elapsed time and constrain bounds. Pixels per frame make behavior vary with refresh rate.
8. Apply `will-change` only to measured candidates around the operation, then release it. Avoid blanket layer promotion or persistent large offscreen layers.
9. Stop unnecessary loops, observers, and animations when their owner disappears or the page is hidden. Resume from current state without replaying unrelated entrances.
10. Keep cancellation and reduced-motion paths correct. Removing animation must not skip state, focus, cleanup, or status work.

Do not mask a long task with a longer easing curve. Do not sacrifice readable text, accessible semantics, or input capability for a cleaner recording.

## Measure again

Repeat the same sequence, build mode, data, and environment. Compare the evidence that motivated the change and check for new layout, memory, or interaction regressions. Broaden testing only when the changed path or a new failure warrants it.

“Visible response at the next available paint” is a design goal. A trace may measure acknowledgement timing for a particular event. Web INP is a separately defined responsiveness metric; do not relabel a custom timer or one transition as INP.

The theoretical interval is `1000 / refreshRateHz` milliseconds per refresh. The application shares that interval with browser or native work; it is not a guaranteed JavaScript budget or proof that every displayed frame met a target.

## Deliver

Provide the reproduced problem, evidence-supported cause, working fix, before/after measurement method and result, and any untested devices or runtime conditions. Use [motion-gestures](../motion-gestures/SKILL.md) for gesture semantics and [motion-accessibility](../motion-accessibility/SKILL.md) for reduced-motion or assistive-technology issues. Never claim a frame rate, zero jank, or universal improvement without corresponding measurements.
