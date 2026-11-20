---
name: mps-scroll-story
description: "Use when a product workflow should change with forward and reverse scroll, including pinned stages, synchronized interface states, progress controls and a reduced-motion reading alternative."
---

# Scroll storytelling

Read [scroll story](../../references/scroll-story.md). Use one reversible progress model derived from geometry. A CSS animation does not become scroll-triggered because a comment mentions an observer.

1. State the understanding the scroll sequence adds and select a short causal workflow. Keep product promise and CTA available outside the sequence.
2. Define stage boundaries and a pure `state(progress)` mapping. Derive progress from the section's bounding box and usable travel, clamp it, and update all connected elements from the same value.
3. On reverse scroll, restore the earlier state deterministically. Avoid timers or accumulating `classList.add` state that drifts out of sync.
4. Use pinning only when reading and product change benefit from it. Keep normal wheel/touch behavior, reasonable section travel and escape routes. Offscreen sections should stop unnecessary frame work.
5. For mobile and reduced motion, provide an ordered semantic sequence or direct step controls. All content remains reachable with JavaScript disabled where practical.
6. Verify start/mid/end in both directions, resizing while inside the section, browser restoration, keyboard focus and offscreen behavior. Inspect screenshots and actual movement.

Adapt Scrollcraft's normalized progress and state verification principles without inheriting its photographic world requirement, device-count quota, fixed art direction or external asset provider.
