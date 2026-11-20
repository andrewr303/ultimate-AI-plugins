# Reversible scroll-controlled product stories

Adapted at the technique level from Scrollcraft's normalized progress and visual state verification, without its art-direction mandates or asset providers.

## One coordinate system

For a story section, compute the available travel from its height minus the viewport. Derive normalized progress from its current bounding rectangle and clamp to `[0, 1]`. Handle zero/negative travel explicitly. Use the same progress for product state, copy emphasis, cursor position and progress indicators.

```text
travel = max(sectionHeight - viewportHeight, 1)
progress = clamp(-sectionTop / travel, 0, 1)
stage = stateForProgress(progress)
```

This is a conceptual contract; use the bundled controller implementation rather than treating this outline as a complete engine. Geometry changes after fonts/images load require a recalculation. Read layout together, then write styles together to avoid repeated layout work.

## Pure stage mapping

A stage can be an interval with local progress. Keep named thresholds in one place. All visual state must be derivable from the current progress; reverse scrolling must restore earlier values. Avoid accumulated events such as "once the result appears, never hide it" unless the interaction deliberately changes the persistent sample state and that boundary is explicit.

Use meaningful phases such as input, classify, review and resolved result. The number follows the workflow. Hold the complete result long enough to read; do not consume a long scroll span for an inert screen.

## Pinning and normal navigation

CSS sticky can hold the product surface while nearby text advances. Give the sticky area a defined container and avoid nested scroll traps. Do not intercept the wheel to enforce a cinematic pace. Ensure visitors can use standard touch, Page Down, Home/End and anchor navigation.

For mobile, a short sequence of readable cards or direct steps can communicate better than a narrow sticky dashboard. Reduced motion should expose the same ordered content without required interpolation. A JavaScript failure should leave semantic content readable, not permanently transparent.

## Efficient updates

Use one `requestAnimationFrame` update loop when active. Mark scroll/resize changes and render at most once per frame. Pause offscreen animation work and observers that are no longer needed. Do not run an unbounded timer that keeps changing an invisible component. Respect `prefers-reduced-motion` initially and when the preference changes.

A normal CSS animation is independent of scroll. If an IntersectionObserver adds a class, verify the class is actually added and that reverse/visibility behavior is intentional. If the story requires scrubbed state, derive it from progress rather than hoping an entrance animation approximates it.

## Browser checks

Capture start, each meaningful stage boundary, result and end, then repeat in reverse. Test resizing while the story is active, navigating to an anchor, refreshing mid-section and restoring browser history. Check that pointer controls and keyboard focus remain aligned with the currently visible state. Confirm no horizontal overflow, excessive dead scroll or hidden CTA.

Test reduced motion and narrow widths independently. Inspect actual motion at normal scroll speed; a correct set of stills does not establish pacing or the feeling of scroll resistance.
