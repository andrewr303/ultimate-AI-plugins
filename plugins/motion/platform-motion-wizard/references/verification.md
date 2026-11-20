# Interaction verification and evidence

Verification closes the loop between a motion specification and the actual user task. Keep evidence proportional to the change. A small timing edit does not need a new test framework; a dismissal race or duplicate mutation needs a targeted regression check.

## Evidence vocabulary

| Label | Meaning |
| --- | --- |
| Observed | The stated action sequence was exercised in the recorded runtime |
| Measured | A named tool captured a defined quantity in the recorded conditions |
| Code-reviewed | The implementation was inspected; behavior may still need runtime confirmation |
| Inferred risk | A plausible failure follows from code, but has not been reproduced |
| Unverified | The relevant path or environment was unavailable or not exercised |

Do not convert code review into a runtime pass. A recording demonstrates only the shown scenario. Passing a keyboard flow and an automated accessibility scan does not establish complete accessibility compliance.

## Common test sequence

1. Enter the flow from a realistic starting state. Observe normal-speed response and the complete terminal state.
2. Repeat the action rapidly. Reverse midway and replace the target before completion.
3. Navigate away or unmount the owner during motion and work. Return and inspect for stuck state or replayed effects.
4. Exercise the actual input modes supported: pointer, keyboard, touch, and assistive technology when available.
5. Enable reduced motion at load, then change it during the interaction. Verify a complete immediate path with no animation callbacks.
6. Exercise slow work, failure, cancellation, retry, and out-of-order completion when the flow contains asynchronous work.
7. Use representative content and layout: small viewport, long labels, zoom, supported themes, reading direction, and dynamic content where relevant.
8. Trace visible stutter or delayed input. Do not claim performance from the absence of a screenshot defect.

Select applicable steps; state exclusions. Do not demand every platform, device, or input mode for a change that cannot affect it.

## Interaction-specific probes

| Interaction | Reproduction probes | State assertion |
| --- | --- | --- |
| Button/form | Double activation, press cancellation, failure then retry | One accepted mutation; input retained; truthful pending |
| Popover/dialog | Open and immediately click; close/reopen; nested surface; Escape during composition where relevant | Correct layer, focus, background interaction, and cleanup from the first frame |
| Tabs/navigation | Rapid switch, back/forward, resize, deep link | Active content and focus agree; state and scroll preserved appropriately |
| Accordion | Toggle repeatedly; load content/images during expansion | Header stable; content unclipped; hidden content not focusable |
| List/reorder | Drag through edge; cancel; remove focused item; refresh during settle | Correct order, scroll owner, focus, stable identity, and keyboard alternative |
| Streaming | Read above end; select text; cancel; fail after partial output | No forced scroll or selection loss; partial state and recovery remain clear |
| Loading/refresh | Cached content, rapid success, slow failure, late old result | No fake delay; latest owner wins; confirmed data remains truthful |

## Focus and exit lifecycle

Check semantics throughout the transition rather than only at rest. Confirm where focus goes when a surface opens, which controls remain operable during dismissal, when the backdrop stops intercepting input, when background inertness and scroll locking end, and where focus returns if the trigger no longer exists. Prefer proven primitive ownership; avoid adding a second independent focus manager.

If exiting content remains mounted for presentation, it must not leave an invisible tab stop, stale click blocker, or duplicated accessible surface. Do not move focus into an inert subtree. Cancelled or zero-duration exits must release the same owned resources as completed exits.

## Regression tests worth keeping

Test concrete contracts: an old dismissal cannot close a reopened dialog; a stale request cannot overwrite a newer result; submit accepts one mutation; reduced motion completes cleanup; drag cancellation restores the model; focus returns to a valid target.

Avoid tests that merely mirror implementation, such as checking an exact duration constant without a behavioral requirement. Reuse the project's test runner and accessible queries. Browser tests should assert stable semantic states and race behavior rather than wait arbitrary milliseconds.

An obsolete-completion test must deliver the obsolete callback after newer intent. Record that it arrived, then check that it did not mutate the latest state. A live-reduction test must first establish an active owned effect, then check its settlement and logical-state parity. [Executable recipes](executable-recipes.md) distinguish deterministic ownership tests from actual browser animation evidence.

## Review report shape

For each finding record `id`, `severity`, `interaction`, `location`, `reproduction`, `expected`, `observed`, `evidence_type`, `environment`, `fix`, and `closure_check`. A compact JSON array can accompany a human-readable report when automation consumes it. Do not label that JSON an automated verdict unless a real tool produced the verdict.

Close with the tested scope, commands or runtime sequences, actual results, remaining limitations, and whether each finding is fixed, open, or unverified. Report “no findings in tested scope” when supported; do not imply that untested paths passed.
