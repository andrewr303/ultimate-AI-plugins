---
name: pds-ui-motion
description: "Use when reconstructing verified product UI for controlled animation or implementing deterministic frame motion, cursor choreography, springs, camera focus and connected transformations in product video."
---

# Faithful UI and motion

Read [motion](../../references/motion.md) and the source-bound storyboard. Reuse actual components when practical; otherwise reproduce verified layout, labels, data and states in an isolated replay.

1. Build a pure frame-to-image or seek-time composition. Derive animated values from named playhead events; avoid timers, uncontrolled transitions, network races and random state.
2. Separate product coordinates, camera and screen overlays. Measure cursor targets in rendered geometry and transform cursor/target consistently. Hold during the press.
3. Use ramps for travel and damped springs for arrivals when useful. Animate to clarify meaning and keep results settled.
4. Interpolate status/color intentionally; keep font/layout stable when interpolation causes reflow. Count only sourced/sample quantities and show typing only when that is the product action.
5. Connected transforms need separate incoming/outgoing content windows so text does not overlap. Use them when they serve the story, not as a universal rule.
6. Preview important frames and transition neighborhoods; inspect native sharpness, cursor alignment, clipping and maximum zoom. Watch movement for timing and shimmer.

A faithful replay remains source/revision bound and labeled when needed. It does not become an actual live capture.
