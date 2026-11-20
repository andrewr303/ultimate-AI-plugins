---
name: motion-gestures
description: "Use when implementing or polishing drag, swipe, pan, reorder, resize, pull-to-refresh, or gesture-driven sheet interactions. Keep direct manipulation coupled to input, resolve scroll ownership, define cancellation and settling, and provide keyboard/button alternatives. Use motion-navigation for route transitions and motion-native for platform-specific gesture adapters."
---

# Motion gestures

Make an object follow the user's intent, then settle to an understandable state. Preserve native scrolling and accessible alternatives. Read [state lifecycles](../../references/state-lifecycles.md), [accessibility](../../references/accessibility.md), and [component recipes](../../references/component-recipes.md).

## Inspect the input contract

1. Identify the existing gesture primitive, pointer/touch/native event system, animation owner, scroll containers, data mutation, selection behavior, and installed APIs.
   Check the package family as well as its version. A repository can contain modern adapters and older APIs with similar names; research from current main does not authorize replacing the product's installed integration.
2. Define the task and the non-gesture way to perform it. Reorder may expose move-up/down controls; swipe actions need ordinary buttons; a drawer needs an accessible dismiss control.
3. Map the allowed axis, handle, activation region, bounds, competing scroll axis, nested gesture owners, safe areas, and edge/browser gestures.
4. Record the states `idle`, `armed`, `dragging`, and `settling`, alongside independent logical data state. Add accepted/canceled outcomes only where the task needs them.
5. Specify threshold meaning, destination selection, cancellation, reduced-motion behavior, pending/error handling, and focus retention before adding a spring.

Use platform-native gesture ownership for native applications; pair with [motion native](../motion-native/SKILL.md). Do not transplant web pointer event assumptions into native views.

## Establish ownership without hijacking scroll

- Reuse the gesture primitive's supported arbitration and capture behavior. A down event alone should not commit a drag or mutate data.
- Scope touch behavior to the handle/region before the gesture begins. Choose touch-action according to the intended free scroll axis; avoid page-wide `touch-action: none` or global cancellation of all touch events.
- Distinguish click/tap intent from a drag with the existing platform/library threshold. Preserve text selection and editable inputs outside deliberate handles.
- Let native scrolling win when the gesture does not own that direction. Account for nested scrollers, zoom, browser edge gestures, and the operating system canceling the sequence.
- Use pointer capture only within the API's valid lifecycle when needed; release owned capture and listeners on completion, cancellation, or unmount.
- `pointercancel`, lost capture, blur/background, removed targets, route change, and competing gestures must have explicit cleanup. Ensure a release followed by lost capture does not finalize twice.

## Couple movement to input

1. While dragging, map the relevant input displacement directly to the visual position. Do not apply a smoothing ease that leaves the object trailing the pointer.
2. Keep one owner for each animated property and cancel/retarget prior settling when a new gesture begins. Start from the current presentation state without jumping to an old origin.
3. Keep movement out of the component's full render path when the installed system supports a lighter motion value/native path. Do not add per-frame React state updates by default.
4. Apply bounds and any resistance deliberately. Distinguish constrained presentation from the logical candidate destination.
5. Make destination cues readable without relying on movement or color alone. Keep nearby targets stable enough to understand what will happen on release.
6. For reorder, use stable data identities and preserve focused-item identity. Measure geometry when needed; account for changing item sizes and virtualized items.
7. For autoscroll, target the intended container, cap work, stop at bounds, and stop on every end/cancel path. A custom speed must be elapsed-time based, not fixed pixels per frame.
8. If activation awaits rendering or measurement, deliver movement and cancellation while activation is pending. Once it resolves, apply only the current gesture's latest input; canceled or replaced initialization must not resume a drag.

## Release, cancel, and settle

| Event | Logical decision | Presentation / cleanup |
| --- | --- | --- |
| Release over accepted destination | Commit the intended operation once through the data owner. | Settle from current position; preserve velocity only when supported and useful. |
| Release without accepted intent | Keep the prior logical state. | Return to its valid position without suggesting success. |
| Cancellation / lost ownership | Apply the explicit cancellation policy; do not infer a successful drop. | Stop autoscroll, release resources, and restore a stable usable state. |
| New gesture during settle | Preserve the latest logical state and current visual position. | Cancel stale completion and begin tracking without a snap. |
| Async failure | Reconcile with current authoritative data; do not overwrite newer work. | Show a persistent recovery path and a clear rollback or refresh. |
| Preference changes to reduce | Keep the current intended value and full task capability. | Remove nonessential settle travel and complete cleanup without end events. |

Choose a destination using the task's displacement and velocity policy, in units appropriate to the installed engine. Tune with the real handle and device; do not copy spring or velocity constants across libraries. Prefer restrained damping and bounded overshoot. A throw animation must not imply an irreversible action before confirmation.

Keep the actual operation independent of spring completion. For a reversible optimistic reorder, retain enough identity/version information to roll back without erasing later edits. For a destructive swipe, follow the product's confirmation/undo contract; motion alone is never confirmation.

## Preserve focus and alternative control

- Keep the active item or a stable handle focused as positions change. If an item disappears, choose a meaningful nearby control; do not leave focus on a detached node.
- Provide keyboard and ordinary pointer/touch controls with equivalent outcomes, including cancellation and the ability to discover the action.
- Announce meaningful reorder/move outcomes through the established accessibility pattern, not every pixel or pointer event. Keep visible destination/status information available with motion disabled.
- For sheets, coordinate drag cancellation, dismissal, focus, scrim, and locks with [motion overlays](../motion-overlays/SKILL.md). Do not give the gesture a competing modal lifecycle.
- Reduced motion does not remove direct control or task capability. Keep essential tracking understandable; remove decorative inertia, large settle travel, zoom, and bounce.
- Do not add sound or haptics unless separately requested.

## Verify and deliver

Exercise mouse, touch, and keyboard/button alternatives where supported; slow drag, quick flick, diagonal intent, nested scroll, edge/bounds, cancellation, release outside, lost capture, rapid re-grab, resize, and unmount. Test variable item sizes and offscreen/virtualized destinations when applicable.

Confirm native scroll still works, accepted operations commit once, canceled operations do not commit, no listeners/capture/autoscroll remain, and the latest logical value matches the visible settled value. Repeat with reduced motion enabled and toggled while settling. Inspect actual performance under representative load; do not infer smoothness from source or a recording alone.

Deliver the implementation with ownership, destination/cancel policy, alternative controls, and real verification. If device or native runtime access is unavailable, name the untested input/platform behavior and provide an exact reproduction checklist.
