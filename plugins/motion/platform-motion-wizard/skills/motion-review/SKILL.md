---
name: motion-review
description: "Use when reviewing platform motion, auditing interaction polish, checking a motion change, or verifying readiness across input, interruption, accessibility, async, and performance paths. Report evidence and actionable findings; pair with a focused implementation skill when fixes are requested."
---

# Review motion and interaction quality

Assess whether the interaction helps users act, understand state, and recover. Read [verification](../../references/verification.md). Use [review report template](../../templates/review-report.md) when a saved review is useful; otherwise report compactly in chat.

## Bound the review

1. Identify the requested flow, changed files, supported platforms, and expected user outcome. Read project instructions and the implementation before forming conclusions.
2. Determine whether the user requested assessment, fixes, or both. An assessment request authorizes inspection, not an unrelated redesign.
3. Locate shared motion tokens, accessibility primitives, operation state, navigation ownership, and cleanup code.
4. Build an interaction inventory only for the requested scope. Prioritize frequent and consequential paths; avoid a shallow checklist across unrelated screens.
5. Record available runtime access, devices, data, and known constraints. Separate missing evidence from a demonstrated defect.

## Run the flow in meaningful conditions

Review the normal path at normal speed before slowing a recording. Static screenshots can verify stable states, geometry, and styling; they cannot establish timing, smooth reversal, or interruption safety.

For each changed interaction, test the applicable paths:

- **Input:** Pointer, keyboard, and touch produce immediate, visible acknowledgement. Focus remains distinct from hover and selection.
- **Continuity:** Start, end, origin, direction, identity, and reading position are coherent. Text remains readable and targets remain usable.
- **Interruption:** Repeat the action, reverse it mid-transition, replace its target, and navigate away. Check cleanup after cancellation.
- **State:** Open → close → reopen cannot be defeated by a previous exit callback. Pending cannot masquerade as success. Old requests cannot overwrite newer intent.
- **Overlay semantics:** Test the first opening frame and the entire dismissal interval. Check focus, tab order, background interaction, scroll lock, and nested surfaces.
- **Async:** Exercise slow success, failure, retry, duplicate submission, partial output, cancellation, and rollback where relevant.
- **Motion preference:** Test normal motion, reduced motion at load, and a preference change while motion is active. No logical work may depend on an animation event.
- **Accessibility:** Check labels, status announcements, keyboard alternatives, focus return, and touch capability. Use actual assistive technology where available; code inspection is not a substitute.
- **Responsive behavior:** Resize during the transition where plausible; test the supported small viewport, reading direction, themes, zoom, and representative content length.
- **Performance:** Investigate visible stutter or delayed feedback with a trace. Keep measured results tied to their exact environment.

Do not announce a universal pass when only one environment or path was exercised.

For race evidence, verify the test actually delivers the old callback. A canceled timer cannot establish that a delivered stale result is ignored. For reduced-motion evidence, verify an owned animation was active before the preference changed. Use [executable recipes](../../references/executable-recipes.md) for controlled sequences and keep simulated state evidence distinct from real-browser observations.

## Evaluate restraint and consistency

Check whether motion explains feedback, identity, hierarchy, or direct manipulation. Flag decorative entrances on repeated renders, excessive travel, unnecessary overshoot, hidden content before hydration, and operation delays inserted for appearance. Compare related components against the existing vocabulary rather than imposing a different aesthetic.

Treat Apple-like quality as immediate response, continuity, clarity, and restraint. It is not a requirement to copy Apple visuals or use purported official timing values.

## Write findings that can be acted on

For each finding, include:

1. Severity and affected user outcome.
2. Exact component/file location and reproducible action sequence.
3. Expected behavior and observed behavior, with evidence type.
4. The smallest relevant fix and the focused skill that owns it.
5. Verification needed to close the issue.

Use these severities consistently:

| Level | Meaning |
| --- | --- |
| Blocker | A tested path traps users, prevents the core task, misstates a consequential result, or creates a serious inaccessible state |
| High | A frequent path loses input/state, fails interruption, or materially prevents an input mode |
| Medium | A reproducible inconsistency, distraction, or performance issue impairs use but has a workable path |
| Low | Local polish with little effect on comprehension or control |

Qualify untested code risks as inferred. Reserve “observed” for executed behavior. Do not invent findings to fill severity levels or call a preference disagreement a blocker.

## Complete the authorized work

When fixes are requested, load the relevant skill, implement the narrow changes, then retest the failing sequence and affected neighboring behavior. Keep review and implementation evidence distinct. Use targeted regression tests for lifecycle races, duplicate mutations, or focus bugs; do not add tests that merely assert an easing literal.

Deliver findings ordered by user impact, the tested scope and evidence, corrected issues when authorized, and a short list of unverified paths. “No findings in the tested scope” is acceptable; it is not a compliance certification or a claim of flawless motion.
