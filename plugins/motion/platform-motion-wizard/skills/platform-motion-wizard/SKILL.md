---
name: platform-motion-wizard
description: "Route product motion work to the right specialist skills. Use to polish how an app or website feels: immediate feedback, spatial continuity, restrained easing, coherent states, accessible reduced motion, controls, overlays, navigation, gestures, loading, or native interaction behavior. Also use for a broad motion audit, implementation plan, or review. Excludes promotional video, audio, and unsolicited redesign."
---

# Platform Motion Wizard

Make the next action feel clear, responsive, and under the user's control. “Apple-like” describes care in interaction behavior; preserve the product's brand and each platform's conventions. Do not copy Apple assets or imply endorsement.

## Start with the requested outcome

1. Read applicable project instructions and inspect the actual product, stack, installed versions, primitives, routing, tests, and motion tokens.
2. Distinguish **implement**, **specify**, **audit**, **debug**, and **review**. If code access and implementation are requested, deliver working changes; an inventory alone is incomplete.
3. Identify one real user task and its friction. For a broad request, start with the most frequent task and shared components. Work outward only when the scope supports it.
4. Use the smallest appropriate skill set below. Open selected skill files before applying them; read references on demand. Routine polish does not require loading this entire plugin or doing a repository survey.
5. Preserve interaction semantics and logical state before tuning duration. Establish the static, zero-motion result first.
6. For a reported bug, reproduce its event order before editing. Separate logical intent, semantic visibility, presentation, and request identity; choose the failing owner rather than adding another animation layer. Use [executable recipes](../../references/executable-recipes.md) when cancellation or retargeting needs a controlled fixture.

## Route by the work

Paths below are relative to this skill directory.

| User need / observed friction | Open first | Add when relevant |
| --- | --- | --- |
| “Make it feel better,” unknown cause, or inconsistent app-wide behavior | [motion-audit](../motion-audit/SKILL.md) | motion-system, then the affected surface |
| Interaction specification or design handoff | [motion-spec](../motion-spec/SKILL.md) | motion-system, accessibility |
| Shared durations, easing, springs, or state vocabulary | [motion-system](../motion-system/SKILL.md) | web or native adapter |
| CSS, WAAPI, React, Next, Vue, Svelte integration or race fixes | [motion-web](../motion-web/SKILL.md) | affected surface, performance |
| Buttons, tabs, forms, toggles, accordions, list updates | [motion-controls](../motion-controls/SKILL.md) | async for network work |
| Menus, popovers, dialogs, sheets, nested layers | [motion-overlays](../motion-overlays/SKILL.md) | accessibility |
| Routes, back/forward, list-to-detail, shared elements | [motion-navigation](../motion-navigation/SKILL.md) | web or native adapter |
| Swipe, drag, reorder, direct manipulation | [motion-gestures](../motion-gestures/SKILL.md) | accessibility, performance |
| Loading, optimistic updates, streamed or agent-generated content | [motion-async](../motion-async/SKILL.md) | controls, accessibility |
| Reduce Motion, keyboard, focus, assistive technology | [motion-accessibility](../motion-accessibility/SKILL.md) | surface skill |
| SwiftUI/UIKit, React Native, Compose, Flutter, WinUI | [motion-native](../motion-native/SKILL.md) | relevant surface |
| Dropped frames, delayed acknowledgment, scrolling or rendering cost | [motion-performance](../motion-performance/SKILL.md) | web or native adapter |
| Live tuning, comparison, isolated interaction preview | [motion-lab](../motion-lab/SKILL.md) | affected surface |
| New library/API selection or “what changed recently?” | [motion-research](../motion-research/SKILL.md) | implementation adapter |
| Pre-merge verification or independent critique | [motion-review](../motion-review/SKILL.md) | accessibility, performance |

The original [polish-platform-motion](../polish-platform-motion/SKILL.md) remains complete and unchanged. Use it for its compact end-to-end workflow or when explicitly invoked. Its archived image transcript is source material; it does not authorize video, music, or audio work.

## Combine without duplicating work

- Full polish: audit → system/spec only where needed → affected surfaces + stack adapter → review.
- Small button fix: controls + relevant web/native guidance; complete focused checks.
- Dialog race: overlays + web/native + accessibility; prove rapid reopen and first-frame usability.
- Delivered obsolete response or visual completion: async or web + the affected surface; force the obsolete callback to run after newer work. Canceling its timer alone does not prove the guard.
- Reorder jank: gestures + performance; test scroll ownership, refresh-rate sensitivity, cancellation, and keyboard alternative.
- Streaming interface: async + navigation/accessibility as applicable; preserve reading position and truthful partial state.
- Review-only: review + needed reference; report findings without silently rewriting the product.
- Spec-only: spec; label predictions and unverified behavior.

Choose one owner for implementation in a shared file. Independent design, accessibility, and evidence reviews can run concurrently. [Agent briefs](../../references/agent-briefs.md) define bounded assignments; use host delegation only when available. Their presence does not create tools or confer authority.

## Non-negotiable behavior

- Acknowledge received input without an intentional animation delay; initiate the actual operation independently.
- One semantic event gets one primary movement, with a meaningful origin and stable endpoint.
- Idle, focus, pressed, selected, disabled, pending, success, and error must remain intelligible without animation.
- Retarget from the visible state. Cancel stale work. An old close cannot dismiss a reopened panel; an old response cannot overwrite a newer request.
- Route CSS, JS, native animation, and programmatic scrolling through a coherent live motion policy.
- Reduce nonessential travel, zoom, parallax, and stagger when requested by the user or system; preserve all functionality and state information.
- Keep scrolling, browser history, links, selection, keyboard operation, and touch behavior familiar.
- Reuse existing primitives and dependencies. Check actual installed APIs before adding or upgrading a library.
- Do not add sound, audio dependencies, or haptics unless explicitly requested.

## Work contract and finish

Use [interaction contract](../../templates/interaction-contract.md) for complex flows and [review report](../../templates/review-report.md) for review. Keep a small task small; do not create process documents merely to satisfy a template.

At completion state the affected behavior, why it is clearer, real checks performed, and material limitations. Distinguish observed runtime results from code inference and untested specifications. Never certify motion quality from a screenshot or promise a frame rate without measurement.
