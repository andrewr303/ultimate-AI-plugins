# Component interaction recipes

Choose the recipe that matches the user's actual task and the installed primitive. These are original starting contracts; reuse established product behavior and tokens. They are not official Apple timings or a requirement to add movement everywhere. Read [motion principles](motion-principles.md) for the shared vocabulary and [state lifecycles](state-lifecycles.md) for interruption ownership.

## Recipe selection

| User friction | Primary skill | Useful partner |
| --- | --- | --- |
| A control feels unresponsive or loses its pressed state | [motion-controls](../skills/motion-controls/SKILL.md) | Accessibility for input equivalence |
| A popup feels disconnected or leaves an input blocker | [motion-overlays](../skills/motion-overlays/SKILL.md) | Accessibility for focus and semantic exits |
| Navigation snaps or loses the selected object's identity | [motion-navigation](../skills/motion-navigation/SKILL.md) | Async feedback for route loading |
| Dragging fights scroll or settles to the wrong place | [motion-gestures](../skills/motion-gestures/SKILL.md) | Native adapter or performance review |

Use the main router for loading/performance/design-system skills. A recipe's acceptance checks are specifications until exercised in the target product.

## Press and pending action

**Trigger:** activation of a button or action control. **Stable states:** available, pending, confirmed, failed; focus/hover/press can coexist with them.

- Acknowledge press at the next available visual update using the existing primitive's state. Start valid work on activation immediately.
- Keep the hit region stationary and preserve the control's accessible name. Reserve space for a pending indicator or use a stable label layout.
- If optional scale is used, apply it to the visual surface and keep text legible. Fill/opacity may be sufficient.
- Reject duplicate activation according to the operation contract. Native disabled and `aria-disabled` differ; preserve deliberate focus behavior and guard handlers where necessary.
- Confirm success from the operation result; show failure with retained input and a retry path. A short visual confirmation cannot replace persistent critical information.
- **Interrupt:** cancel the press appearance on pointer cancellation/blur and invalidate old result effects when a new operation becomes current.
- **Reduced motion:** retain fill, focus, pending label, checked state, and results; omit nonessential scale/bounce.
- **Accept:** keyboard and pointer activate once; pending does not shift the target; failure does not erase input; old completion cannot reset a newer action.

## Selected indicator and tabs

**Trigger:** selection change through the primitive's expected input. **Endpoint:** the current tab/segment has truthful selected semantics and its corresponding content is available.

- Use one indicator retargeted to the selected item's actual geometry. Keep its visual movement independent from selection commitment.
- Separate focused from selected state and follow the existing automatic/manual activation model. Do not invent new arrow-key behavior for aesthetics.
- Handle responsive labels, fonts, localization, RTL, and a removed tab. Keep useful panel state/scroll when the product expects it.
- **Interrupt:** rapid switching targets the latest selection; no queue of obsolete indicator moves or older panel focus callbacks.
- **Reduced motion:** place the indicator immediately; preserve selection and keyboard behavior.
- **Accept:** the selected label, visible panel, and accessible state agree while switching quickly and resizing.

## Anchored menu or popover

**Trigger:** the surface's documented open action. **Origin:** the actual positioned anchor after collision handling. **Endpoint:** the content is usable under the correct menu/popover contract.

- Keep positioning and presentation from competing for a transform. Use a supported wrapper/origin API where needed.
- Use one restrained reveal; do not stagger commands so they become usable at different times. Preserve typeahead and keyboard focus handling for menus.
- Keep nonmodal background access as intended. A generic scrim must not silently change a popover into a modal.
- **Interrupt:** close/reopen suppresses stale exit DOM/focus changes and releases the old generation's own resources; replacement preserves the latest anchor and focus destination.
- **Reduced motion:** reveal promptly without spatial travel, with all dismissal and focus behavior intact.
- **Accept:** pointer activation works from the first usable frame, Escape/outside interaction dismisses the intended surface, and no invisible layer survives closure.

## Modal dialog and sheet

**Trigger:** a task requiring the chosen modal or sheet pattern. **Endpoint:** a named surface with deliberate focus, consistent background inertness, and a reachable completion/dismissal action.

- Prefer the installed accessible primitive/native presentation. Coordinate surface and scrim as one event.
- A sheet may reveal from its attached edge; a centered dialog often needs only opacity or a small restrained surface change.
- Choose a coherent semantic exit strategy using [overlay lifecycles](state-lifecycles.md#overlay-lifecycle-transaction). Do not make visual opacity the owner of focus or locks.
- Keep child/parent overlay ownership separate; close only the intended layer. Verify Escape and text composition do not conflict.
- **Interrupt:** reopen during exit must survive old callbacks. A trigger removed by the action needs a meaningful return-focus fallback.
- **Reduced motion:** preserve exactly the same modal contract and complete cleanup without an animation event.
- **Accept:** keyboard containment/return, scroll lock, nested dismissal, rapid reopening, first-frame pointer behavior, and post-close background input all work.

## Accordion and size reveal

**Trigger:** an expandable region's semantic control. **Origin:** the header and content boundary; keep the trigger fixed where practical.

- Set expanded state truthfully and keep content readable at the endpoint. Use measured or supported intrinsic-size behavior if the stack needs it.
- Avoid arbitrary oversized max-height values. Handle late media, font changes, variable content, and rapid reversal.
- Keep focus valid when collapsing content that contains the active element; use the primitive's policy or a deliberate header fallback.
- **Interrupt:** retarget from current geometry; a previous expansion completion cannot overwrite a newer collapse.
- **Reduced motion:** show/hide immediately with the same semantics and focus result.
- **Accept:** no clipped late content, no unexpected page jump, no detached focus, and no stale height after resize.

## List mutation and list-to-detail

**Trigger:** an actual insertion/removal/reorder or navigation to an identified object. **Continuity:** stable data identity, not coincident geometry.

- Animate only changed relationships. Keep keys stable and do not replay entrances on polling, sorting, filters, or ordinary renders.
- Preserve the user's reading position and active item. A virtualizer's recycled DOM identity must not become the identity for a shared-element transition.
- Choose one meaningful subject; avoid stretched text. Decorative snapshots must not duplicate IDs, accessible content, or focus targets.
- **Interrupt:** latest destination/data wins; disappearing/offscreen source or destination falls back to a fade or immediate state.
- **Reduced motion:** keep the same destination, selection, focus, and scroll outcome without spatial morphing.
- **Accept:** back returns to useful context, missing-source transitions still work, and URL/content/focus/data agree after rapid navigation.

## Drag, swipe, and reorder

**Trigger:** eligible input on a deliberate handle/region. **Feedback:** direct input-coupled position plus an understandable destination cue.

- Negotiate axis/scroll ownership before activation; preserve native scrolling outside the owned direction and region.
- Track directly while dragging. On release, choose the destination from the task's displacement/velocity policy and settle using the installed engine's units.
- Commit accepted operations once independently of spring completion. Canceled/lost ownership is not a successful drop.
- Scope capture, listeners, autoscroll, and resistance to the gesture owner. Custom autoscroll uses elapsed time and stops at bounds/end/cancel.
- Expose ordinary controls with equivalent outcomes and understandable status announcements. Do not make moving something depend on drag alone.
- **Interrupt:** a re-grab starts from current presentation; release then lost capture does not commit twice; stale server rollback cannot erase a newer reorder.
- **Reduced motion:** preserve direct control and task capability while removing decorative inertia/bounce/large settling travel.
- **Accept:** mouse/touch/alternative controls, diagonal intent, nested scroll, bounds, canceled capture, rapid re-grab, and failure recovery leave the correct stable state.

## Loading, refresh, and changing values

**Trigger:** real work or a genuine data update. **Endpoint:** truthful current data or a recoverable error, independent of decorative completion.

- Acknowledge pending promptly and reserve layout space. Keep useful stale data when safe and label its relationship to refresh.
- Suppress a spinner flash only if acknowledgment is already visible; do not introduce a minimum work delay for a prettier sequence.
- Do not fabricate percentages. A rolling number animation must not alter the accessible value or imply intermediate values are confirmed facts.
- Keep important counts/text legible; decorative digit copies must not create repeated accessible announcements.
- **Interrupt:** route/action identity governs which result remains relevant; stop obsolete effects and preserve current draft data.
- **Reduced motion:** static pending treatment and immediate value update retain all information; stop shimmer, repeated travel, and nonessential loops.
- **Accept:** fast success, slow success, failure, retry, superseded response, and preference change all preserve truthful state without layout collapse.

## Tooltip and transient feedback

**Trigger:** relevant hover/focus or an actual result. **Endpoint:** discoverable information or truthful status, not a timed visual flourish.

- Keep essential instructions visible elsewhere. A tooltip should not be the only route to an action or critical information.
- Support expected hover/focus access and dismissal. Cancel a delayed appearance when the trigger is no longer relevant.
- Keep errors, undo actions, and critical results available according to the product's recovery needs. An exit duration must not determine how long the user can act.
- Avoid repeated announcements from decorative changes or a toast that re-enters on every render.
- **Interrupt:** replacement removes obsolete information cleanly without an old timeout dismissing the newer message.
- **Reduced motion:** show truthful text immediately or with a brief suitable opacity change; retain the same discovery and dismissal behavior.
- **Accept:** keyboard/touch paths can obtain needed information, replacement does not lose the latest result, and no hidden tooltip blocks input.

## Final restraint pass

Remove motion that does not improve acknowledgment, continuity, comprehension, or control. Verify behavior at normal speed before diagnosing with slowed frames. Use [verification guidance](verification.md), and state any missing runtime/device coverage plainly.
