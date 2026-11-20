---
name: motion-navigation
description: "Use when refining route changes, back navigation, tabs with page-level state, list-to-detail continuity, shared elements, insertion/removal, or layout transitions. Preserve identity, reading direction, browser semantics, focus, scroll, and input through interrupted navigation. Use motion-gestures for direct manipulation and motion-overlays for modal lifecycles."
---

# Motion navigation

Help the user recognize where they moved without making navigation wait for animation. Preserve native browser and router behavior. Read [motion principles](../../references/motion-principles.md), [web implementation](../../references/web-implementation.md), and the relevant [component recipe](../../references/component-recipes.md).

## Map the actual relationship

1. Identify router/navigation APIs, history and scroll restoration, loading boundaries, data caches, focus policy, server rendering, existing view/layout animation, and installed versions.
2. Trace the user's real flow: sibling destination, hierarchical drill-in/back, selected-object detail, tab selection, or list mutation. Use spatial movement only when that relationship is meaningful.
3. Record source identity, destination identity, start/end geometry, route commit point, pending/failure UI, interruption policy, focus target, scroll policy, and reduced-motion behavior.
4. Inspect the requested viewport, supported reading directions, and variable text. Preserve product typography, navigation semantics, and responsive layout.
5. Implement the smallest coherent flow and shared components it needs. Do not convert the whole application to a new router or motion framework for local polish.

## Keep navigation authoritative

- Navigate on valid activation; start loading immediately. An exit animation must not delay the operation, URL change, or pending acknowledgment.
- Preserve links, modified click, open-in-new-tab, back/forward history, deep links, and server-rendered fallback behavior. Do not turn links into generic clickable containers.
- Let the router/data layer own route and result relevance. Require a current navigation identity/relevance guard before applying data or completion effects, even when old work is aborted; rely on the router's equivalent relevance guarantee only after verifying it. Abort alone does not prevent an already resolved response or queued animation callback from committing a superseded destination.
- Retarget or simplify the current transition when the user navigates again. Do not queue every destination behind a long choreography.
- Preserve errors and recovery when a destination fails. Do not leave the previous screen hidden, announce success prematurely, or trap the user between routes.
- Keep useful existing content during pending work when safe and make pending state explicit. Route loading belongs to actual work, never a fake minimum duration.

## Preserve identity and spatial continuity

1. Use stable item keys and data identities. Shared-element identifiers must be unique within their scope and match the same object across views.
2. Prefer a single meaningful subject or indicator. Avoid morphing unrelated cards just because they occupy similar coordinates.
3. Measure source/destination geometry only when the chosen mechanism requires it. Batch layout reads before writes; handle resize, font loading, and content changes.
4. Avoid distorted text or stretching complex surfaces. A wrapper or crossfade of content may preserve legibility while geometry changes.
5. Treat visual snapshots as decorative. Prevent duplicate accessible content, live announcements, focus targets, or IDs when an element is represented twice.
6. When a source or destination is absent, virtualized, filtered, offscreen, or unmounted, use a short fade or immediate update. Correct navigation must not depend on a perfect morph.
7. Keep one owner for animated position/transform. Do not combine layout animation, CSS transform, and another engine on the same property without an explicit composition plan.

## Direction, focus, and scroll

| Concern | Decision to make | Acceptance condition |
| --- | --- | --- |
| Hierarchical drill-in/back | Express the established platform hierarchy, adapted for reading direction. | Back returns to the same task context without contradictory direction or lost state. |
| Sibling routes | Prefer a restrained content change unless an actual spatial model exists. | Unrelated pages do not fly through an invented carousel. |
| Tab panels | Follow the primitive's focus/activation model; preserve useful local state. | Keyboard selection and indicator retargeting work during rapid switching. |
| Route focus | Apply the product's accessible navigation policy once the current destination is ready. | Focus is meaningful; an old callback cannot steal it from a newer destination. |
| History restoration | Reuse router/browser restoration; distinguish back from a new destination. | Back recovers the user's place and forward/new routes follow the intended policy. |
| Hash / in-page links | Preserve anchor semantics and offsets for sticky headers. | The target remains visible with reduced motion and keyboard use. |

Do not force scroll-to-top on every render or replace native scrolling with animation. Keep user-initiated scrolling interruptible; remove nonessential smooth scrolling when reduced motion is active. Avoid moving focused content outside the visible viewport.

## Browser view transitions and progressive enhancement

- Check actual browser/API support and the installed framework integration before choosing a view-transition path. Do not assume a feature's availability from a blog example or package name.
- The ordinary DOM/router update must work if the API is absent, skipped, rejected, interrupted, or disabled by preference.
- Separate navigation/data commitment from presentation completion. Handle update and animation failures without replaying the operation or stranding hidden content.
- Keep transition names unique for simultaneously rendered elements. Account for nested layouts, multiple instances, and virtualized items.
- Keep server and initial client states compatible. Content must be readable when JavaScript or animation initialization fails; avoid a permanently hidden initial render.

## Lists and layout changes

Animate genuine insertion, removal, reorder, or expansion rather than every rerender. Preserve the active item and user's place during sorting, filtering, polling, pagination, and virtualizer recycling. If a focused item is removed, choose an adjacent stable control or another meaningful target.

Use content-aware size changes where needed; handle late media and font changes. Do not use oversized fixed max-height values or permanent layout observers for an isolated reveal. Profile layout animation when it changes real geometry.

## Verify and deliver

Exercise rapid A → B → C navigation, back/forward, deep link, route failure, slow data, keyboard activation, modified click, resize, RTL where supported, and a missing shared element. Repeat with reduced motion, including a preference change mid-transition.

Confirm the URL, visible content, focus, scroll, and data all describe the same current destination. Verify there is no entrance replay on ordinary renders, duplicated accessible content, hydration flash, or stale completion. Use [verification guidance](../../references/verification.md) for meaningful runtime evidence.

Deliver working changes with the navigation relationship, identity and fallback choices, focus/scroll policy, and actual checks. For specification-only work, provide those same contracts and identify runtime behavior that remains unverified.
