# Profiling motion without guessing

Use the application's existing profiler and a representative runtime. This reference defines an investigation method; it does not claim that any platform or library automatically meets a frame-rate target.

## Record enough context to compare

Capture the interaction sequence, build mode, commit or local change, device class, OS, browser/runtime, viewport, data size, network conditions, motion preference, and refresh rate when known. Record which tools produced the evidence. A before/after comparison needs sufficiently comparable conditions; label changes in hardware or throttling.

Observe the normal-speed interaction before inspecting a slowed recording. Slow playback is useful for diagnosing a jump, but it can exaggerate inconsequential details. Screenshots reveal stable states and layout; they cannot prove responsiveness or continuous motion.

## Separate timings

| Measurement | What it can answer | What it does not establish |
| --- | --- | --- |
| Input to visible acknowledgement | Whether this accepted action produced feedback promptly | Site-wide responsiveness or server latency |
| Handler/render duration | Which local work blocks the next update | End-to-end user-perceived latency on its own |
| Animation interval/frame trace | Whether this transition presents frames consistently in this runtime | Smoothness on every device |
| Network/operation duration | How long the underlying work took | Whether feedback appeared immediately |
| Web INP | The metric as defined and captured by appropriate tooling | A value inferred from one easing duration or arbitrary timer |

Do not report a custom `performance.now()` span as INP. Use supported performance tooling and its actual metric definitions. Event-to-next-paint observations and INP have related concerns but different measurement contracts.

The theoretical refresh interval is `1000 / Hz` milliseconds. This interval is shared by all work needed to present a frame and is not an allotment of JavaScript execution time. Measured dropped frames, long tasks, and delayed interaction should be reported with the device and scenario that produced them.

## Read the work, not the property name

Transforms and opacity often suit visual motion, but can still trigger costly compositing, large raster surfaces, blending, or layer memory. Height and layout changes can be justified for accordions and evolving content; constrain and measure them rather than banning them mechanically.

Inspect forced layouts, repeated geometry reads, paint areas, expensive filters, rasterization, large blurred backdrops, image decoding, synchronous parsing, repeated React renders, and excess DOM. One trace-backed cause is more useful than a broad animation rewrite.

Batch reads before writes. Measure geometry when inputs change and invalidate it on relevant resize, content, font, image, or scroll changes. Overcaching can create wrong endpoints; reading after every write can force layout.

Use a scoped `will-change` hint only when measurement supports it. Release it after the operation. Creating a layer for every card can increase memory pressure and make scrolling worse.

## Continuous interactions

Keep drag positions in the established gesture or motion-value path where available. Business state, React commits, analytics, status announcements, and network work should not run on every visual frame unless required and measured.

When implementing custom auto-scroll, use elapsed time for distance, clamp bounds, identify the correct scroll container, and stop on cancellation, release, unmount, or loss of eligibility. A fixed pixel increment per frame changes speed with refresh rate and throttling. Hidden-tab time gaps need a bounded recovery policy rather than a huge catch-up jump.

## Lists and shared layout

Preserve stable entity keys and focus. Coordinate animation with the virtualizer's measured sizes and mounting boundaries. Animate the visible representation without retaining the entire dataset or defeating virtualization for a decorative transition.

Watch for duplicate shared-element identity, scroll-linked measurement errors, images arriving mid-transition, and an item disappearing while focused. A transform can make a row look elsewhere without changing its logical order; keep accessibility order and target behavior coherent.

## Cleanup and power

Inspect listener, observer, timer, animation, and retained-node counts after repeated use. Stop optional loops when offscreen or hidden and release objects when their owner ends. Reduced-motion preference changes must cancel or settle active optional motion without leaking callbacks.

Measure battery or power only with suitable tools and conditions. Lower idle activity is useful evidence; it is not a quantified battery-life claim.

## Useful resources

- [Web performance: INP](https://web.dev/articles/inp)
- [MDN: Animation performance and frame rate](https://developer.mozilla.org/en-US/docs/Web/Performance/Guides/Animation_performance_and_frame_rate)
- [Chrome DevTools performance panel](https://developer.chrome.com/docs/devtools/performance)
- [React Profiler](https://react.dev/reference/react/Profiler)

Consult current documentation for the installed browser and framework. These are further-reading links, not a record that an app was measured.
