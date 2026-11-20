---
name: motion-controls
description: "Use when implementing or refining buttons, links, toggles, tabs, form feedback, accordions, tooltips, or other small control interactions. Produce immediate, truthful feedback with stable targets and complete keyboard, pending, failure, and reduced-motion states. Use motion-overlays for menu/dialog lifecycles and motion-gestures for drag/swipe behavior."
---

# Motion controls

Make the action understandable as soon as input arrives. Preserve the product's visual language and existing component primitives. Read [motion principles](../../references/motion-principles.md) and only the relevant [component recipe](../../references/component-recipes.md).

## Establish the contract

1. Inspect the actual control, its callers, installed primitive, styling tokens, disabled behavior, submit handler, and relevant project checks. Trace the operation beyond the visual component.
2. Identify the friction with an observable reproduction: delayed press feedback, moving hit area, a spinner that changes width, false success, lost focus, or repeated actions.
3. Write the smallest useful state table. Use only applicable states: idle, hovered, focused, pressed, selected, disabled, pending, success, error. Focus and selection can coexist with pending; these are not one mutually exclusive enum.
4. Record the input, actual state change, immediate acknowledgment, interruption, error recovery, and reduced-motion alternative. For shared controls, identify consumers before altering their default behavior.
5. If the user requested implementation, make the code change after this inventory. A state table alone does not finish the task.

## Implement feedback and semantics

- Keep native semantics: a button performs an action, a link navigates, a checkbox/toggle communicates its checked state. Preserve native keyboard activation and browser link behavior.
- Apply pressed appearance immediately through the existing primitive or platform state. Start work from the intended activation event, not from animation completion or a second custom pointer handler.
- Give hover, focus, and press separate roles. A keyboard user needs a persistent visible focus cue even when an optional press transform is suppressed.
- Keep the hit region stationary. Animate an inner visual surface when necessary so scale does not shrink or shift the target. Retain readable text and a stable accessible name.
- Restore pressed appearance after release, pointer cancellation, lost capture, blur, disabled state, or unmount. Avoid a permanent pressed state when the pointer leaves the surface.
- Use the existing timing/easing tokens. For a small control, a fill/opacity change is often sufficient; add subtle scale only if it improves acknowledgment without text distortion.
- Set only intended transition properties. Do not animate every style, position focus rings away from their target, or add repeated bounce to routine activation.
- Do not add audio or haptics unless the user separately requests them.

## Preserve truthful async state

1. On valid activation, acknowledge the input and begin the operation independently of the animation. Record an operation identity when overlapping requests are possible.
2. Preserve the label's meaning and reserve any indicator space. Expose pending status accessibly without repeatedly announcing every visual frame.
3. Prevent duplicate submission according to the operation contract. A visual disabled style or `aria-disabled` alone does not prevent handler execution. Preserve focus deliberately when choosing native disabled behavior.
4. Confirm success only from the actual result. For an optimistic reversible action, record the prior value and define a rollback that will not overwrite a newer edit.
5. On failure, preserve the user's data and provide an actionable error/retry path. Do not shake the whole form, clear inputs, or announce success because an animation completed.
6. If a result arrives after unmount, cancellation, or a newer operation, follow the data layer's cancellation/relevance policy. Do not let an old visual callback reset a newer pending control.

For complex async flows, pair this skill with [motion async](../motion-async/SKILL.md) through the main router. Use the [state lifecycle reference](../../references/state-lifecycles.md) to separate logical state from visual presence.

## Adapt the component

| Component | Implementation decision | Failure to exercise |
| --- | --- | --- |
| Toggle / checkbox | Commit the selected value immediately; retain checked semantics; move only its visual indicator. | Rapid toggles and an older server response reverting the latest value. |
| Tabs / segmented control | Keep focus and selected state distinct; follow the primitive's activation model; retarget one indicator. | Arrow navigation during indicator movement and dynamic label widths. |
| Accordion | Preserve the trigger; measure changing content if necessary; keep expanded semantics correct. | Resize, late images, nested focus, and collapse during expansion. |
| Form submission | Preserve input, acknowledge valid submission, reserve status space, and identify invalid fields. | Enter key, repeated activation, server validation, and retry. |
| Tooltip | Support focus and hover with Escape dismissal; keep essential instructions elsewhere. | Keyboard access, touch use, hover moving into tooltip, and dismissal. |
| Icon button | Keep an explicit accessible name and a stable target. | Pending icon replacement losing the name or focus indicator. |
| Link | Navigate on normal activation; retain modified click, open-in-new-tab, and URL affordances. | A press effect swallowing modifier keys or delaying route change. |

For tabs that change routes or preserve page-level scroll, use [motion navigation](../motion-navigation/SKILL.md). For an anchored interactive popup, use [motion overlays](../motion-overlays/SKILL.md), not tooltip semantics.

## Implement the zero-motion path

- Preserve all selected, pressed, pending, success, and error information when transform, travel, and stagger are removed.
- Observe the active preference through the shared motion system. A preference change during an active transition must leave the latest logical state visible and usable.
- Do not depend on transition or animation end events to enable the control, submit work, resolve a promise, or show a critical result.

## Verify and deliver

Exercise the changed action with pointer, keyboard, touch where available, and reduced motion. Test cancellation and the relevant pending/error path; compare related controls for consistent timing.

Inspect the first paint after input as well as the settled state. Verify focus stays findable, the label and target remain stable, and an interrupted effect cannot disable or reset the latest action. Add a focused state-risk test only where it protects a real failure such as duplicate submit or stale rollback; use existing project checks.

Deliver working changes with the affected states, why the feedback is clearer, and what was actually exercised. If runtime access is missing, provide the exact interaction contract and identify unverified behavior. A screenshot cannot prove responsiveness or interruption safety.
