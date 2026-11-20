---
name: polish-platform-motion
description: Design, implement, and review Apple-like platform motion and interactions with immediate feedback, spatial continuity, restrained easing, consistent states, and accessible reduced-motion behavior. Use when polishing an app or website, improving microinteractions, making UI feel smoother or more native, or refining buttons, menus, dialogs, navigation, gestures, loading, and state transitions. Excludes sound and audio design.
---

# Polish Platform Motion

Make the product feel responsive, coherent, and effortless. Use motion to explain what changed, where it came from, and what the user can do next. Preserve the product's own brand and platform conventions. Treat “Apple-like” as a quality target for interaction behavior; do not claim Apple endorsement or copy its trademarks or proprietary assets.

Read [references/image-transcript.md](references/image-transcript.md) when checking the source wording or explaining how the original video prompt was adapted. Keep its complete transcription separate from implementation instructions. Do not implement its music or sound guidance. Do not add audio dependencies, sound effects, or haptics unless separately requested.

## 1. Inspect the product before changing it

1. Read applicable project instructions. Identify the framework, routing, component primitives, styling tokens, animation dependencies, and accessibility patterns already in use.
2. Inspect the requested screens and trace actual user tasks. If the request is broad, start with the most frequent flow and the shared components it uses. Avoid unrelated redesigns.
3. Find the specific friction: delayed acknowledgment, snapping layout, disconnected overlays, excessive bounce, unstable loading, inconsistent timing, broken focus, or stale animation callbacks.
4. Reuse the existing animation system. Prefer native platform controls for native apps and existing accessible primitives for web apps. Add a dependency only when a required capability cannot be reasonably implemented with the current stack.
5. Check installed package versions and local APIs before writing framework-specific code. Consult current primary documentation when an API is uncertain.

Produce a short interaction inventory before implementation:

| Element / action | Current friction | Intended feedback and transition | Interrupt / failure behavior | Reduced-motion behavior |
| --- | --- | --- | --- | --- |
| Example: open creator detail | Detail appears disconnected | Preserve the selected creator's identity while revealing the panel | Close or select another creator immediately | Reveal without spatial travel |

Use this inventory to implement the work, not as a stopping point when the user requested a working change.

## 2. Establish the visual and motion rules

- Preserve supplied typography, colors, spacing, radii, and brand assets. When none exist, start with up to three purposeful accent colors, at most two typefaces, and quiet neutral surfaces. Retain necessary semantic error, warning, and success colors.
- Give the active task a clear focal point. Direct attention through hierarchy, spacing, and contrast. Avoid decorative glow, constant gradients in motion, or ornamental blur.
- Design the idle, hover, focus, pressed, selected, disabled, pending, success, and error states that the component actually needs. Make every stable state work without animation.
- Specify the beginning and end of each transition before adding movement. Keep text readable, controls findable, and layout stable throughout.
- Give one semantic event one primary movement. Coordinate associated elements rather than making every child animate independently.
- Preserve familiar browser behavior, native scrolling, keyboard shortcuts, and user control. Do not turn routine product use into a cinematic sequence.

## 3. Define a small shared motion vocabulary

Start with these suggested values, then tune in the actual product. They are implementation defaults authored for this skill, not Apple's official values or measurements from the image. Reuse existing well-working tokens rather than imposing a second system.

| Token / role | Starting range | Guidance |
| --- | --- | --- |
| Immediate acknowledgment | Next available paint | Show pressed, selected, or pending feedback without an intentional delay. |
| Micro feedback | 80–140 ms | Small color, opacity, and press/release changes. |
| Small surface | 140–220 ms | Menus, tooltips, selection indicators. |
| Panel / dialog | 200–300 ms | Short reveal from a meaningful origin. |
| Context transition | 240–360 ms | Navigation or connected detail expansion when it clarifies location. |
| Exit | 120–200 ms | Usually faster than entry; do not keep dismissed controls interactive. |
| Optional stagger | 15–30 ms per item, 100 ms total cap | Use only for a small group with a meaningful order; never delay usability. |

Use a restrained easing family:

- Entry or settling: start with `cubic-bezier(0.22, 1, 0.36, 1)`.
- Movement between positions: start with `cubic-bezier(0.4, 0, 0.2, 1)`.
- Exit: start with `cubic-bezier(0.4, 0, 1, 1)` and a short duration.
- Continuous progress or direct pointer tracking: use linear behavior where it represents the underlying action correctly. Do not apply eased lag to an object while it is being dragged.
- Springs: use the installed library's physical model only when useful for direct manipulation or spatial settling. Favor strong damping and little or no overshoot. Do not copy spring numbers between libraries with different units.

For small surfaces, start with 4–12 px of translation or a subtle 0.98–1 scale change, not both by default. Larger sheets can travel farther when their edge origin communicates structure. Avoid page-wide zooms and stretched text. Never apply these distances mechanically to every component.

## 4. Make motion follow causality and user control

- Start visual feedback when input is received; start network work independently. Never postpone the actual operation until a flourish finishes.
- Anchor popovers to their triggers. Reveal sheets from their attached edge. Preserve selected objects across list-to-detail transitions when practical. Use stable identity for shared elements.
- Keep direction consistent with the hierarchy and adapt directional navigation for the interface's reading direction. Do not invent a spatial relationship between unrelated routes.
- Let dismissal reverse or simplify the entry relationship. Keep motion physically plausible without requiring exact time reversal.
- Retarget active animations from their current visual position. Preserve velocity where the animation system supports it. Avoid snapping back to the initial keyframe on repeated input.
- Cancel stale animations and completion callbacks on replacement, navigation, or unmount. Ensure an old exit cannot close a newly reopened panel.
- Make direct manipulation follow the pointer. Settle on release using displacement and velocity appropriate to the gesture. Define bounds, cancellation, and fallback controls.
- Keep frequently used interactions fast. Hold important information through stable UI, not by making the user wait for a long animation.

## 5. Apply component-specific behavior

| Component | Desired behavior | Avoid |
| --- | --- | --- |
| Buttons and icon controls | Give immediate pressed feedback; use a subtle fill change or optional 0.98–0.99 scale; reset on release or cancellation; keep focus distinct. | Bounce on every click, moving the hit target, hover-only feedback. |
| Links and navigation items | Show active destination clearly; keep navigation responsive; preserve browser link semantics. | Delaying navigation, replacing links with clickable divs, entrance animation on every render. |
| Tabs and segmented controls | Move the selected indicator consistently; update selection immediately; preserve useful panel state and scroll. | Sliding unrelated content through large distances or animating every tab child. |
| Menus and popovers | Open near their trigger with restrained opacity or scale; preserve correct keyboard navigation and dismissal. | Arbitrary entrance direction, lingering invisible click blockers. |
| Dialogs and sheets | Coordinate surface and scrim; manage focus, background inertness, scroll locking, and focus return through proven primitives. | Animating the whole page behind the modal or leaving exiting content tabbable. |
| Accordions | Expand from the header; measure variable content when needed; keep the trigger stable and semantics correct. | Clipped dynamic content, arbitrary max-height tricks, large overshoot. |
| Lists and cards | Preserve stable keys; animate genuine insertion, removal, or reorder; keep the user's place and focused item. | Replaying entry effects on filtering, polling, sorting, or ordinary rerenders. |
| Forms and validation | Preserve input, show contextual errors, and prevent duplicate submission while pending. | Shaking the whole form, moving fields unnecessarily, clearing data after failure. |
| Loading and data refresh | Reserve space, keep useful stale data when safe, and distinguish pending from completed. Suppress spinner flashes only if acknowledgment is already visible. | Fake progress, minimum loading delays for aesthetics, celebratory success before confirmation. |
| Success, error, and toast feedback | Confirm the actual outcome visibly and accessibly; keep persistent errors or critical actions discoverable. | Animation as the only signal, premature success, repeatedly announcing decorative changes. |
| Drag, swipe, and reorder | Track input directly; show a destination cue; settle or return clearly; provide a keyboard or button alternative. | Hijacking scroll, drag-only operation, pointer movement that scrolls the wrong container. |
| Tooltips | Support focus as well as hover and allow dismissal; leave essential instructions visible elsewhere. | Touch-only reliance or making critical information disappear too quickly. |

Use optimistic updates only when an action is safely reversible and has a defined rollback. Keep financial, destructive, or contract-related outcomes explicitly pending until confirmed. Motion must not imply a completed deal or payment before the underlying system confirms it.

## 6. Implement safely in web stacks

- For React, Next.js, TypeScript, and Tailwind projects, centralize durations, easing, and reduced-motion behavior in existing tokens or one small motion module. Keep one owner for each animated property.
- Use CSS transitions for simple state changes. Use the existing animation library or Web Animations API only when orchestration, interruption, shared layout, or gestures justify it.
- Prefer transform and opacity for motion where appropriate. Profile required height or layout animations rather than assuming they are free. Batch layout reads before writes to avoid thrashing.
- Animate a wrapper if nested effects would compete for `transform`. Do not blur or distort text to create movement.
- Avoid `transition: all`, global permanent `will-change`, excessive backdrop-filter animation, and JavaScript updates for every frame when compositor-driven motion suffices.
- Use stable React keys and preserve form state. Keep shared layout identifiers unique and prevent unintended cross-page morphs.
- Guard browser-only APIs during server rendering and hydrate to a stable initial state. Prevent an initial hidden state from stranding content when JavaScript or animation fails.
- Respect pointer cancellation, touch behavior, focus visibility, and component unmount. Do not suppress native scrolling across the page to enable one gesture.
- Keep logical state transitions independent from animation duration. Handle canceled animations and zero-motion paths explicitly; do not rely solely on `transitionend` or a magic timeout to complete an operation.
- Coordinate exit rendering with semantics: remove dismissed content from interaction while it remains visually present, manage focus safely, then unmount. Avoid duplicate accessible copies during shared-element effects.

## 7. Make reduced motion a first-class path

- Respect `prefers-reduced-motion: reduce` on the web and the equivalent preference on native platforms. Respond when the preference changes during the session.
- Remove nonessential spatial travel, parallax, zoom, rotation, bouncing, and staggered reveals. Use an immediate update or a brief opacity transition when suitable.
- Keep every action and all state information available. Retain focus indicators, pending labels, errors, and success messages. Replace decorative shimmer with a static loading treatment; retain a textual pending indication.
- Route CSS, JavaScript animations, and animated scrolling through the same preference. Do not implement reduced motion only in styles while leaving gesture settling or route animations unaffected.
- Stop or settle active nonessential motion safely if the preference changes. Test that cleanup and completion still work without animation events.
- Keep keyboard and touch use equivalent in capability. Provide labels and status semantics; avoid excessive live-region announcements.
- Avoid flashing, autoplay decoration, and perpetual movement unrelated to the task. Do not rely on motion, color, or sound alone to communicate state.

## 8. Verify the complete interaction

Exercise the changed flow in the actual interface when runtime access is available. A screenshot alone cannot establish motion quality. Inspect normal-speed behavior first; use a slow recording or frame inspection only to diagnose a specific issue.

Check:

1. **Responsiveness:** Verify visible acknowledgment at input, usable controls during transitions, and no artificial operation delays.
2. **Continuity:** Verify stable text, logical origins, smooth reversals, and a clear endpoint without flicker or layout jumps.
3. **Interruption:** Rapidly open, close, reopen, switch selection, and navigate away. Verify no stuck overlays, stale callbacks, duplicate operations, or lost input.
4. **Async behavior:** Exercise slow success, failure, and cancellation where supported. Verify truthful pending states and correct rollback.
5. **Accessibility:** Complete the flow with keyboard and touch, verify focus placement and return, then repeat with reduced motion enabled and changed mid-session.
6. **Performance:** Check the changed flow on a representative mobile viewport and under realistic load. Investigate visible dropped frames or long tasks; do not claim a frame rate without measurement.
7. **Consistency:** Compare related components, responsive layouts, and themes already supported by the product. Keep timing and direction coherent.

Use focused tests for concrete state risks such as interrupted dismissal or duplicate submission. Avoid broad new test suites for minor visual tuning. Reuse existing checks required by the project.

If runtime access is unavailable, provide exact implementation or a component-by-component specification, state what was inspected, and clearly identify unverified motion behavior. Do not claim an animation was tested from static code review.

## Delivery

Deliver working changes when code access is provided. Summarize the affected interactions, why they feel clearer or more responsive, how they were verified, and any specific remaining limitation. For specification-only requests, provide triggers, start/end states, timing, easing, interruption, failure, and reduced-motion behavior for each interaction.

Use restraint as the final review: remove any motion that does not improve feedback, continuity, comprehension, or control.
