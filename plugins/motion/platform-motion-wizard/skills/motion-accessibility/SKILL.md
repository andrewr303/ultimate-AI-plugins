---
name: motion-accessibility
description: "Implement or review reduced-motion behavior, live preference changes, focus and semantics during animated exits, keyboard and touch parity, drag alternatives, and accessible status feedback. Use when motion affects comfort or access. Pair with the interaction implementation skill; this is not a full accessibility conformance audit."
---

# Accessible motion and interaction

Make the same task understandable and operable with movement removed. Reduced motion is an alternate presentation of the same state machine, with the same outcomes and cleanup.

Read [the accessibility reference](../../references/accessibility.md). For native apps, also use [motion-native](../motion-native/SKILL.md). Keep the existing accessible primitive's ownership of focus, dismissal, and modality.

## Establish the contract

Inspect the target interaction, component primitive, animation owner, current preference source, and supported browsers or OS versions. Identify the actual user task and failure or interruption risks. Preserve existing labels and keyboard behavior.

For each affected interaction, record:

| Contract field | Required decision |
| --- | --- |
| Input | Pointer, touch, keyboard, assistive action, or programmatic update |
| Semantic state | What changes immediately, independently of animation |
| Normal presentation | Feedback, movement, origin, endpoint |
| Reduced presentation | Immediate endpoint or restrained fade, with equivalent information |
| Focus and announcement | Initial focus, return destination, message and announcement owner |
| Interruption | Cancellation, replacement, preference change, unmount |

Do not classify an effect as essential merely because the current implementation uses it. Ask whether the same task and information work without that effect.

## Implement one preference policy

1. Find all motion producers: CSS, animation libraries, imperative animations, smooth scrolling, SVG/canvas, video, skeletons, gestures, and route transitions.
2. Reuse or establish a shared preference adapter. Keep CSS and imperative consumers consistent.
3. On the web, use `prefers-reduced-motion` and subscribe to media-query changes where JavaScript owns motion. Remove subscriptions at teardown.
4. Guard browser APIs during server rendering. Render a usable stable initial state before preferences are available; do not strand essential content behind an animation-only reveal.
5. An optional product preference may further reduce motion. Do not silently override the system request to reduce movement.
6. On preference change, cancel or settle active nonessential movement to the logical endpoint and clear its resources. Do not start a fresh spatial animation to demonstrate the new setting.
7. When a library exposes only a startup snapshot, bridge the platform's live accessibility event. Verify behavior for the installed version rather than assuming a hook is reactive.

Do not blanket-set every animation duration to a tiny nonzero value. That can preserve unwanted motion, break delays, or leave lifecycle logic dependent on animation events. Select the reduced presentation by interaction role.

## Keep semantics independent of appearance

- Logical selection, expanded state, pending state, and route ownership update when the action occurs. Animation completion does not decide whether the action happened.
- Zero motion must follow the same completion and resource-release path. Handle canceled animation promises or callbacks explicitly.
- For exit motion, define when the surface stops accepting input and leaves the accessibility tree. A fading surface is not automatically inactive.
- Move focus out of a closing subtree before marking it hidden or inert. Do not place `aria-hidden` on a focused element or its ancestor.
- Return focus only when the closing interaction still owns that responsibility. An old exit must not steal focus from a newly opened surface.
- Use a surviving, logical fallback if the original trigger was removed, disabled, or replaced.
- Keep modal background inertness and scroll locking under the proven dialog primitive. Preserve nested-modal stack ownership.
- A visual transition clone must not duplicate accessible names, IDs, live regions, focus targets, or interactive controls.

## Preserve input and status equivalence

- Buttons, links, tabs, and menus keep their native or established widget semantics. Press feedback must also work from the keyboard.
- Hover content also works with focus where appropriate; essential instructions remain available without hover.
- Drag/reorder functions provide both keyboard operation and a click/tap alternative without dragging, such as Move up/down or Move to… controls. Keyboard support alone does not establish the pointer alternative.
- Preserve browser scrolling, zoom, and text selection. Constrain custom gesture handling to the relevant control and intended axis.
- Keep focus visible while content moves. Test that sticky headers, sheets, and animated surfaces do not cover the focused control.
- Preserve input values on failure. Explain pending, success, and error in text or semantics; motion and color cannot be the only signals.
- Announce meaningful outcomes once. Do not announce every animation frame, repeated loading tick, or decorative change.
- Do not hide a persistent error or required recovery action in a fleeting toast. Preserve enough time and an accessible way to reach critical information.

## Verify the complete path

Run the smallest checks that expose the affected risks. A static screenshot and an automated accessibility scan cannot establish animation comfort, focus order, or live preference behavior.

| Exercise | Expected result |
| --- | --- |
| Load with reduced motion already enabled | Stable useful content; no spatial entrance or decorative shimmer |
| Toggle reduction during entry, exit, and gesture settling | Motion settles safely; no stranded surface or stale callback |
| Open → close → reopen rapidly | Correct surface owns focus; earlier exit cannot hide the new instance |
| Keyboard complete flow | Visible focus, expected keys, usable dismissal and focus return |
| Touch without dragging | Same task through tap controls; scrolling remains usable |
| Screen-reader navigation | One meaningful semantic instance, accurate state, restrained status announcements |
| Failed request and retry | Input retained; actual outcome communicated; no duplicate operation |
| Navigate away or unmount | Listeners, locks, observers, animations, and temporary nodes released |

Exercise the platform's real preference as well as browser emulation or test doubles when available. Report any assistive-technology or device checks that could not run.

For a live-change test, positively establish an active effect before toggling reduction; a zero-effect fixture cannot prove interruption. Check only the effects owned by the changed component. The [executable recipes](../../references/executable-recipes.md) demonstrate this distinction and an immediate endpoint path when animation support is absent.

## Deliver

Return the working changes or, for a specification request, the filled contract for each interaction. Include the preference source, reduced presentation, focus/semantics decisions, checks executed, and remaining limitations. Describe issues against named criteria only when the criterion and scope were actually evaluated. Do not claim whole-product WCAG compliance from this focused pass.
