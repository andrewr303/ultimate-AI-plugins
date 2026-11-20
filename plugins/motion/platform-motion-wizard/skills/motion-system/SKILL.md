---
name: motion-system
description: "Create or consolidate a small motion vocabulary across a product. Use for inconsistent duration, easing, springs, movement roles, state transitions, or design-system motion tokens. Preserve existing well-working tokens; use a surface skill for a single isolated interaction."
---

# Build one small motion system

Read [principles and token roles](../../references/motion-principles.md). Inventory existing tokens and actual component usage before adding values.

## Establish roles

1. Sample representative controls, small surfaces, overlays, navigation, and async feedback.
2. List duplicated values, inconsistent outcomes, and missing reduced behavior. Record any intentional brand or platform variation.
3. Name roles by purpose: feedback, surface, context, dismissal, direct manipulation. Avoid a separate preset for every component.
4. Keep domain state independent of timing. Define normal and reduced policies centrally, with component-level exceptions only when necessary.
5. Assign one owner to each property. Nest wrappers when press scale and layout transform would otherwise compete.

## Authored starter vocabulary

Use the existing system where it works. If none exists, start small:

| Role | Suggested start | Constraint |
| --- | --- | --- |
| Input acknowledgment | next available paint | No intentional delay or dependency on an animation |
| Feedback | 80–140 ms | Small fill/opacity change or restrained press response |
| Small surface | 140–220 ms | Origin tied to its trigger |
| Dialog/panel | 200–300 ms | Coordinate surface and scrim |
| Context | 240–360 ms | Use only for a meaningful spatial relationship |
| Dismissal | 120–200 ms | Semantics and hit testing follow logical dismissal |
| Optional group stagger | 15–30 ms, capped at 100 ms total | Never gate usability or reading |

These are product-tuning suggestions inherited from the supplied skill, not Apple specifications or universal performance budgets.

A restrained entry can begin with cubic-bezier(0.22, 1, 0.36, 1); position changes with cubic-bezier(0.4, 0, 0.2, 1); short exits with cubic-bezier(0.4, 0, 1, 1). Use linear tracking for direct input. Avoid layering a duration tween on top of a spring.

## Specify policies rather than magic numbers

For each role define: semantic purpose; timing/easing or spring model and units; distance/origin; allowed properties; interruption; reduced equivalent; and exceptions. Short travel can begin at 4–12 CSS pixels for small surfaces; use actual geometry and the task to decide. Do not animate both scale and translation by habit.

Reduced policy removes nonessential travel, zoom, parallax, and stagger; it preserves focus, state, and operations. Do not globally force tiny animation durations or remove all transitions if lifecycle code still depends on their completion.

Store tokens in the existing design-system format. [Starter token data](../../examples/motion-tokens.json) is illustrative and opt-in. Map duration roles to CSS variables, installed library transitions, or native equivalents without assuming matching units.

## Migrate and compare

Change one representative interaction per role. Verify normal, zero-motion, rapid reversal, loading/failure, responsive geometry, and themes. Compare at normal speed before adjusting values. Where available, use [motion-lab](../motion-lab/SKILL.md) for a controlled comparison.

Then replace duplicate constants in the authorized scope. Do not reformat unrelated components or change every animation solely for uniformity. Keep intentional exceptions with a reason.

Deliver the token map, usage guidance, changed references, exception list, and real validation evidence. Review sibling components for coherent behavior rather than identical numbers.
