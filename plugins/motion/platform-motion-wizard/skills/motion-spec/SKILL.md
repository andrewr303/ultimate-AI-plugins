---
name: motion-spec
description: "Specify an interaction before implementation or produce a motion handoff. Use when behavior, start/end states, interruption, failure, accessibility, or timing is ambiguous. For an implementation request, use the specification to build the change and continue through verification."
---

# Specify the interaction contract

Read [principles](../../references/motion-principles.md) and use [contract template](../../templates/interaction-contract.md) selectively. The specification is an executable behavioral agreement, not a mood board.

## Establish the event and states

1. Identify the user goal, trigger, input modality, semantic owner, stable IDs, and source of truth.
2. Define domain states separately from presentation phases. For a save action, pending/success/error belongs to the operation; fading does not determine success.
3. Make the initial, intermediate, and final states readable. Document where focus, hit testing, scroll position, and screen-reader exposure belong.
4. Give related movement a causal origin: trigger for popover, attached edge for sheet, selected object for detail. Use a simple reveal if there is no real shared identity.
5. Name cancellation, reversal, error, retry, stale response, unmount, viewport change, and preference change behavior.
6. Then choose a shared motion role from the product's existing vocabulary.

## Specify every material transition

| Field | Required decision |
| --- | --- |
| Trigger and precondition | Exact event and allowed starting states |
| Immediate feedback | What changes at the next available paint without delaying work |
| Stable endpoint | Logical result, geometry, and next action |
| Presentation | Property, owner, origin, duration/easing role or physical model |
| Interruption | Retarget, cancel, reverse, or commit; new request wins rule |
| Semantics | Focus, pointer/keyboard availability, announcements, scroll |
| Async truth | What is pending, confirmed, failed, canceled, or reversible |
| Reduced behavior | Immediate or minimal nonspatial equivalent, including active changes |
| Evidence | Reproduction steps and observable acceptance result |

Do not transfer spring constants between libraries with different units. Values in [motion system](../motion-system/SKILL.md) are authored starting points, not measured Apple settings.

## Design for the awkward paths

- Open → close → reopen before exit completes: old completion must be ignored.
- Select A → B, A returns late: B remains current.
- Drag → pointer cancellation or OS interruption: ownership releases and object settles.
- Dismiss modal while focused inside: focus moves safely; dismissed content is not left interactive.
- Enable reduced motion mid-transition: settle to the correct logical endpoint and clean up.
- Slow font/image/stream arrival: anchor remains meaningful; text remains readable.
- Change locale, direction, viewport, or zoom: layout and relationship still make sense.

For a complex flow sketch a state table or Mermaid state diagram. Document events and guards; diagrams should clarify race behavior, not merely mirror component names.

## Handoff and acceptance

Deliver the contract, any token changes, affected files/primitives, normal/reduced variants, and a short interaction-specific test plan. Use stable IDs and event names that can map into the real application.

For code work, implement the contract and validate it. For spec-only work, label all timing and performance judgments as unverified until exercised in the actual product.
