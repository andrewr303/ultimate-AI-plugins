---
name: motion-audit
description: "Diagnose how a product feels before changing it. Use for broad app polish, inconsistent interactions, unclear friction, or a prioritized motion backlog. Inspect real user flows and state behavior. Use motion-review for verification of an already implemented change."
---

# Audit product feel

Find the interaction that costs the user the most effort. Do not start with a list of animation effects.

## Inputs and scope

Inspect the requested screens, primary task, platform, package/OS versions, input methods, accessibility settings, current tokens, and constraints. Read [principles](../../references/motion-principles.md). With no runtime, inspect code and clearly label hypotheses. Do not invent user research or observations.

## Observe before prescribing

1. Walk the normal path at normal speed. Note the input, first visible acknowledgment, stable outcome, and whether the next action is available.
2. Repeat with keyboard, touch where available, reduced motion, slow requests, failure, rapid repeated input, back navigation, and viewport/content changes.
3. Trace state ownership: domain state, interaction state, render/presence state, async request identity, focus, and scroll owner.
4. Inspect shared primitives and package versions. Find whether a local patch or missing token causes the friction before proposing new infrastructure.
5. Separate delay from duration: slow work, main-thread contention, late feedback, and a long transition need different remedies.
6. Find the strongest problem in the most frequent flow. Confirm its cause with a focused trace or reproduction where possible.

## Record useful evidence

| Flow / action | Observed friction | Impact and frequency | Cause / confidence | Smallest repair | Check |
| --- | --- | --- | --- | --- | --- |
| Actual product action | What the user sees or cannot do | Known facts or explicit unknown | Observed, inferred, or hypothesis | Concrete component/state change | Reproduction and expected result |

Prioritize blocked input, incorrect outcomes, lost focus, stuck overlays, inaccessible motion, and lost data before cosmetic consistency. Avoid a numerical score whose precision exceeds the evidence.

## Inspect these failure families

- Feedback: press absent, pending too late, spinner flash, false completion.
- Continuity: unstable keys, text stretch, layout jump, detached reveal, repeated entrance on rerender.
- Control: ignored reversal, locked gesture, scroll hijack, duplicate submission, stale completion.
- Semantics: hidden interactive content, wrong focus return, modal background usable, hover-only affordance.
- Comfort: unnecessary zoom/travel/parallax, persistent motion, reduced preference ignored or stale.
- Consistency: sibling controls use contradictory state names, origins, durations, or navigation directions.
- Cost: synchronous layout reads/writes, huge composited layers, unnecessary React renders, excessive measurement.

## Decide and proceed

Choose **keep**, **tune**, **replace implementation**, or **remove motion** for each material item. State the tradeoff. Preserve the brand, platform conventions, and working behaviors.

Output a prioritized, bounded interaction inventory with concrete acceptance checks. For an implementation request, route to the selected surface skills and implement the agreed scope in the same task. An audit-only request ends with evidence and recommendations, not unsolicited changes.

Use [motion-review](../motion-review/SKILL.md) after implementation; do not mark audit hypotheses as resolved without the required evidence.
