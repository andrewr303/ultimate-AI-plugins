# Principles and decisions

Use motion to clarify **feedback**, **continuity**, **comprehension**, or **control**. If an effect does none of these, remove it. “Apple-like” is a behavioral aspiration; it is not a proprietary aesthetic or a reason to copy brand assets.

## The interaction has three clocks

- **Input acknowledgment:** the user sees the action was received at the next available paint. Do not await a network request or flourish.
- **Domain work:** data changes, navigation, validation, and network operations obey their own real completion conditions.
- **Presentation:** a short transition explains a state change. It may be interrupted, skipped, or disabled without corrupting the domain result.

Do not equate fast presentation with low latency, or a low INP measurement with the time to finish a request.

## Coherent spatial behavior

Identify the source, destination, relationship, and endpoint. A menu belongs to its trigger; a sheet belongs to an edge; a selected item may preserve identity into detail. Unrelated routes do not acquire a meaningful shared geometry merely because a library can morph them.

Use stable identity and one primary movement per event. Keep text readable and hit targets stable. In right-to-left interfaces derive direction from the actual hierarchy and reading direction, not a hard-coded left/right assumption.

## State first, motion second

Every state must be usable as a still frame. Separate stable domain state from transient presence. A dialog can be logically dismissed while a noninteractive visual exit remains; the primitive must still manage focus, modality, and scroll correctly.

Transitions must have a terminal path for complete, cancel, replace, zero-motion, unmount, and preference change. An old terminal callback must not commit into a newer generation.

## Authored starting values

The original supplied skill's suggested roles remain the starting vocabulary: feedback 80–140 ms, small surface 140–220 ms, panel 200–300 ms, context 240–360 ms, dismissal 120–200 ms. Optional stagger is 15–30 ms per item with a 100 ms total cap. Values are tuning proposals, not official Apple measurements, research-proven optima, accessibility thresholds, or promises of performance.

Small surfaces may need only opacity or 4–12 px travel; avoid applying translation and scale together by habit. Prefer minimal overshoot for routine use. During direct manipulation track input without eased lag; release can settle with a checked physical model.

## Technical restraint

Reuse existing native controls and accessible web primitives. Keep one property owner. Profile layout effects, large layers, shadows, filters, and render work. Do not add a heavy timeline engine when a stable-state transition suffices.

Use a live reduced-motion policy and explicit semantic cleanup. A global tiny-duration stylesheet cannot fix JS races, stale hooks, focus problems, or scroll animation.

## Evidence

Bundled [research snapshot](research-snapshot.md) and [decision report](../research/DECISIONS.md) explain the source review. The platform-independent rules above are original implementation policies grounded in the supplied skill and reviewed implementations. The exact timing suggestions are authored defaults.
