# Bounded demonstration recipes

Select patterns by the claim they teach. The bundled fixture implements representative states; adapt its data and components to the current product.

## State contract

Declare stable state IDs and transitions in the interactive-demo contract. Keep rendering separate from transitions and asynchronous side effects. A useful input/result machine is:

```text
initial -> input -> loading -> success
                    |          |
                    v          v
                  error      editable result
                    |
                   retry -> loading
loading -> cancel -> input
any state -> reset -> initial
valid input with no matches -> empty -> input
```

Not every pattern needs every state, but omitted states need a reason. Increment a request generation ID on cancel/reset and ignore completions from older generations. Disable duplicate submissions while busy; retain a way to cancel a slow operation. Announce important status changes politely and keep focus on an operable control.

## Tabs

Purpose: let visitors compare meaningful product capabilities or states. Use buttons with tab/tabpanel semantics, one selected tab and one roving tab stop. Arrow keys move between tabs; Home/End are useful for larger sets. The corresponding panel has a label relationship and does not leave hidden controls in the tab order. Maintain sufficient panel height to limit layout shift. Tabs should reveal distinct information, not cosmetic duplicates.

## Input to result

Purpose: connect a representative input to a bounded outcome. Provide an editable prompt or form, explain the sample scope, and show the result only after the initiating action. Local deterministic data is the default. Include a reliable failure path for review, a real retry and a reset that clears pending work. A fake typing animation is not a live AI response; label the sample.

## Search and filter

Purpose: show how the product narrows information. Search actual sample fields and update visible results plus count. Provide an empty state with a clear recovery such as clearing filters. Keep the input label persistent and avoid moving focus on every keystroke. Debounce only when useful; small local sets can update synchronously.

## Before and after

Purpose: make a specific change inspectable. Use comparable source states at equal scale. A range slider needs a visible label, keyboard adjustment and a text alternative stating the change. Do not make essential evidence dependent on a precise pointer drag. Avoid comparing unrelated input/output cases.

## Workflow progression

Purpose: expose a causal sequence. Keep each step's input, action and resulting state clear. Use direct step buttons or Back/Next with current-step state. Reset returns to a known baseline. A result must not precede the action that produces it. Preserve enough context to understand why the step matters.

## Reordering and drag interactions

Purpose: demonstrate prioritization or arranging work. Support pointer/touch dragging where relevant, plus keyboard Move up/Move down or an equivalent listbox interaction. Announce the new position and preserve focus on the moved item. Do not rely on a color-only drop target. Reordering must change the actual displayed order and survive subsequent filtering sensibly.

## Editable output

Purpose: show that generated or suggested work remains controllable. Use labeled text inputs or a textarea with explicit save/copy/reset behavior. Escape all sample/user text before injecting into HTML. Keep output edits distinct from source input and indicate whether reset discards them. Do not suggest server persistence when the demo is local only.

## Expandable details

Purpose: reveal proof without overwhelming the default view. Use native `details/summary` or a button with `aria-expanded` and a controlled region. Keep important qualifications visible before expansion. Esc should close a modal detail if a modal is used, with focus restored to its opener; do not create a modal for a small inline explanation.

## Scroll state and replay

Purpose: let the visitor scrub a connected workflow and replay it deliberately. Map state to normalized scroll progress, not elapsed wall time. Offer direct controls when pinning would hinder mobile or keyboard users. Replay resets the same state machine, cancels pending work and does not accumulate duplicate event listeners. See [scroll story](scroll-story.md).

## Choreography

Move attention between action and consequence. Animate spatial relation, status and selected state deliberately; avoid unnecessary camera effects or indefinite decorative motion. Product labels stay readable while important information appears. Under reduced motion, replace movement with direct state changes while retaining the full information and operable controls.

## Verification table

For each control record purpose, initial state, action, expected result, empty/error recovery, keyboard action and reset behavior. Exercise repeated use and interleavings: start then cancel; fail then retry; edit then reset; filter then reorder; scroll forward then reverse. A single successful click proves little about cancellation or recovery.
