---
name: motion-overlays
description: "Use when implementing or reviewing menus, popovers, dialogs, sheets, drawers, tooltips with complex presence, or nested overlay transitions. Coordinate meaningful origins, visual presence, focus, dismissal, pointer blocking, scroll locks, and interrupted exits. Use motion-controls for a simple control state and motion-navigation for route changes."
---

# Motion overlays

Make a surface appear connected to its trigger and make dismissal complete. Motion must never leave a hidden layer intercepting input or expose background controls while a modal still owns focus. Read [state lifecycles](../../references/state-lifecycles.md) and [accessibility](../../references/accessibility.md).

## Inspect before changing presence

1. Identify the installed overlay primitive, portal owner, controlled/uncontrolled state, presence mechanism, focus scope, outside-interaction handlers, scroll lock, and stacking context.
2. Trace the first opening frame, entry, steady open state, exit, immediate reopen, and unmount. Inspect both the surface and its scrim/dismissal layer.
3. Decide which pattern the content actually needs. A command menu, nonmodal popover, tooltip, and modal dialog have different keyboard/focus contracts. Do not add dialog semantics simply to obtain an animation wrapper.
4. Record the trigger, anchor, opening cause, initial focus, dismissal causes, return-focus target, nested behavior, and reduced-motion path.
5. Preserve the primitive's behavior by extending its supported styling/presence API. Do not replace its focus or dismissal system with custom timers to make an exit easier.

## Define one lifecycle owner

Use logical openness and visual presence as separate concepts. An `open → closing → closed` transition must not make an old closing callback authoritative after a new `open` request.

- Assign one owner to open state and one coordinated presence lifecycle. Avoid competing wrappers each waiting for their own animation to finish.
- On open, invalidate the previous exit generation, establish the current surface/anchor, and let the primitive establish semantics and focus in its supported order.
- On close, commit the logical dismissal promptly. Coordinate focus release/return, accessibility exposure, and background inertness as a single transaction through the primitive; never hide a still-focused subtree from assistive technology.
- If a decorative exiting copy remains, make it noninteractive and absent from the accessibility tree after focus has safely left it. Remove duplicate IDs and accessible content.
- Keep lock and inert ownership correct for nested modals. Closing a child must not unlock the page or return focus behind its still-open parent.
- Remove the visual presence only for the active close generation. Reopening during exit invalidates the old completion's DOM/focus mutations and retargets from the current visual state when supported. Still release each superseded generation's own resources idempotently; never release resources now owned by the newer surface.
- Implement completion for canceled, skipped, reduced-motion, unmounted, or failed animation paths. Treat animation end as a presentation signal, not the sole source of lifecycle truth.

Follow the primitive's documented modal lifecycle rather than globally dropping pointer blocking, inertness, or locks when a CSS class changes. If the primitive keeps modal semantics until exit completes, keep its focus scope and blocking consistent during that interval and bound the exit; do not create a half-modal state.

## Choose restrained movement

- Anchor popovers and menus to the actual trigger/positioned surface. Derive transform origin from the placement after collision handling; update placement coherently when the viewport changes.
- Reveal a sheet from its attached edge. A centered dialog may need only a brief opacity change or small scale; avoid moving the entire page behind it.
- Coordinate scrim and surface as one event. Dismissal should feel prompt; do not wait through a child-by-child stagger before releasing the interface.
- Keep text sharp and the target geometry stable. Animate a wrapper when positioning and presentation would otherwise compete for `transform`.
- Do not use blur, excessive overshoot, long travel, or backdrop animation as a substitute for a clear hierarchy.
- Prefer existing tokens and library capabilities; add no animation dependency solely for a menu reveal.

## Preserve the component contract

| Pattern | Required behavior | Motion-specific edge case |
| --- | --- | --- |
| Menu | Preserve the primitive's keyboard navigation, typeahead, focus transfer, Escape, and outside dismissal. | Item activation must work from the first usable opening frame, not only after entry finishes. |
| Nonmodal popover | Keep its actual focus/return policy; allow expected background interaction. | A lingering scrim must not accidentally turn it into a modal. |
| Modal dialog | Accessible name, deliberate initial focus, contained interaction, background inertness, and safe focus return. | Surface/scrim exits cannot leave invisible blockers or active tabbable content. |
| Sheet / drawer | Retain modal or nonmodal semantics chosen by the product; preserve scroll and safe-area behavior. | Swipe cancellation restores the same logical surface without losing focus or locking the page. |
| Tooltip | Hover/focus access and dismissal; no essential hidden-only instructions. | Delayed show must be canceled when its trigger loses relevance. |
| Nested surface | Track parent and topmost ownership; dismiss according to the primitive's stack. | Escape closes the intended layer, while a child close does not destroy the parent's lock. |

Do not duplicate Escape handlers on the document and the surface. Preserve IME composition behavior: verify the primitive/version prevents a composition-cancel key from also dismissing the user's surface. Use the component's supported events rather than overriding browser text input.

## Interruption and missing targets

- Exercise open → close → open before either transition finishes. The final open request wins; the old exit cannot unmount, hide, or steal focus from it.
- Handle anchor movement, responsive placement flips, scroll, zoom, and a trigger removed by the action. Choose a meaningful fallback focus target if the original trigger no longer exists.
- If opening another surface replaces this one, coordinate ownership explicitly. Do not momentarily focus the page background or allow an old focus-return callback to steal focus from the new surface.
- Scope outside-pointer behavior to the correct layer and input sequence. Prevent the dismissing gesture from also activating an unintended background target; avoid a permanent invisible click blocker afterward.
- Clean up listeners, animation handles, portals, and owned locks on unmount. Do not mutate global styles without restoring their previous values and respecting other owners.

## Reduced motion, verification, and delivery

With reduced motion, remove nonessential spatial reveal/settle and use immediate state or brief opacity if suitable. Keep the same focus, Escape, inertness, scroll lock, and completion behavior. Toggle the preference while entering and exiting.

Test first-frame pointer activation, keyboard opening, typeahead where applicable, Escape during text composition, nested surfaces, outside dismissal, rapid reopen, navigation away, and disappearance of the trigger. Confirm no scroll jump, focus loss, leftover portal, or ghost blocker after close. Use [verification guidance](../../references/verification.md) and the project's existing checks.

Deliver the implementation and identify the lifecycle owner, changed entry/exit relationship, interruption policy, and tested input modes. State runtime limitations explicitly; never claim a dialog's motion or focus was verified from a static screenshot.
