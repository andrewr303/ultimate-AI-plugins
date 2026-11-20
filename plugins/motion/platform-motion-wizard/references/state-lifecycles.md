# State and presence lifecycles

This is authored engineering guidance for the plugin. It describes invariants to implement using the product's existing primitives, not a replacement framework or official Apple specification. Timing and easing live in [motion principles](motion-principles.md).

## Separate the authorities

| Layer | Question it answers | Typical owner | Forbidden dependency |
| --- | --- | --- | --- |
| Domain / data | Did the action actually happen? | Data store, server response, validated local operation | A fade or spring finishing cannot establish success. |
| Logical UI | Which item, destination, or surface is current? | Router, component state, reducer, platform control | An old animation callback cannot restore a superseded target. |
| Semantic interaction | What can receive focus/input and what is exposed to assistive technology? | Accessible primitive / native control | Opacity alone cannot hide content from input or accessibility. |
| Presentation | Where and how does the current state appear? | CSS, existing animation system, native animation | Presentation cannot be the only record of selection or pending state. |

An implementation may colocate these responsibilities, but it must preserve the boundaries. Separate generation identities for animation, navigation, and network work when their lifecycles differ. An animation cancellation does not necessarily cancel a server mutation; an aborted request does not prove a mutation was not applied.

## Specify an interaction before coding

Record only fields the actual interaction needs:

- Trigger and input modes; relevant element/data identities.
- Stable initial and target states; immediate acknowledgment.
- Logical commitment point and source of truth.
- Semantic/focus/scroll behavior at each phase.
- Animated properties and their single owners; meaningful origin and endpoint.
- Timing/easing token; no-motion equivalent.
- Replacement, reverse, cancellation, unmount, failure, and stale-result behavior.
- Observable acceptance checks and runtime evidence available.

If one of these is undefined, choose a simpler presentation rather than making correctness depend on choreography.

## Latest-target presentation

A useful presentation model has a current target, current visual state, animation generation, and an optional active handle. The exact library API is deliberately unspecified.

```text
requestPresentation(target):
  increment presentation generation BEFORE canceling the previous handle
  capture generation and target for this request
  cancel/replace the previous handle using the installed system
  release superseded generation resources explicitly and idempotently,
    even if cancellation produces no completion callback
  apply current logical/semantic decisions through their real owner
  if animation is unavailable or motion policy requests an immediate update:
    set the current target appearance
    complete presentation for this generation
  otherwise:
    animate from the current visual state toward the current target
    on finish/cancel/error: normalize the outcome under the policy below

completePresentation(capturedGeneration):
  always release resources still owned only by capturedGeneration, idempotently
  if capturedGeneration differs from current generation: return
  apply current presentation cleanup / remove its obsolete decorative presence
  do not perform an unrelated domain action here
```

Invalidate before canceling: some systems invoke cancellation handlers synchronously. Always release a finished, canceled, or replaced generation's own resources, even when its result is stale; do not put that release behind the current-generation guard. Make release idempotent because explicit replacement cleanup and a cancellation callback may both run. Guard semantic/DOM mutations and shared-state changes by current generation and ownership. Never release a lock, listener, or handle transferred to or acquired by a newer interaction, and do not let a stale completion remove its DOM.

### Normalize termination deliberately

| Termination | What to do | What to avoid |
| --- | --- | --- |
| Natural finish | Settle to the current target and release owned resources. | Replaying a network operation. |
| Superseded by new input | Release superseded generation resources, suppress stale mutations, and retarget from current presentation where supported. | Returning to an old keyframe or committing the old selection. |
| Explicit cancel with no replacement | Choose the valid endpoint from current logical state; complete cleanup. | Leaving an in-between value indefinitely. |
| Reduced motion enabled mid-flight | Apply the latest target using the shared reduced-motion policy and complete cleanup. | Waiting for an event that will no longer fire. |
| Zero duration / feature unavailable | Follow the same semantic/logical path and settle immediately. | A hidden initial state stranded without JavaScript or an animation event. |
| Unmount / navigation away | Invalidate callbacks, stop owned work, release capture/listeners/locks through their owners. | Stale callbacks touching detached or newly reused nodes. |
| API failure / rejected animation promise | Preserve the correct DOM/logical update and recover the presentation. | Treating a presentation rejection as proof the operation failed. |

Handle the installed API's cancellation semantics explicitly. A canceled Web Animations `finished` promise, a library stop callback, and a CSS transition cancellation do not share one universal contract.

## Overlay lifecycle transaction

The implementation must use its accessible primitive's supported lifecycle. Two valid strategies exist when the primitive supports them; choose one coherent strategy, not an accidental mixture.

| Strategy | During close | At the end |
| --- | --- | --- |
| Immediate semantic dismissal with decorative exit | Return/rehome focus safely, release semantic ownership in the primitive's order, and retain only a noninteractive inaccessible visual representation. | Remove the decorative representation for the active generation. |
| Primitive-owned modal presence through bounded exit | Keep focus scope, background inertness, scroll lock, and blocking consistent with the still-present modal. | Let the primitive release semantics, focus, and locks together. |

For either strategy:

1. Record whether this is the top layer and which trigger/parent should receive focus.
2. Never set `aria-hidden` or inert on a subtree while leaving focus inside it. Coordinate focus departure and semantic removal rather than scattering them across unrelated effects.
3. Returning focus to a trigger while its ancestor is still inert may fail; follow the primitive's ordering and test the actual result.
4. A child close must preserve the parent's lock and focus context. Use stack/ownership-aware cleanup, not a global boolean.
5. A close followed by reopen invalidates the old exit's DOM/focus changes, while still releasing resources the old generation owns. It must not remove the new surface or return focus away from it.
6. A disappearing trigger needs a meaningful fallback. A replacing surface must receive focus without an older return-focus callback stealing it.
7. Separate the dismissing input sequence from subsequent background input. Prevent unintended click-through for that gesture without retaining an invisible blocker after completion.

## Gesture lifecycle

```text
idle --eligible input--> armed --intent accepted--> dragging
armed --tap/release--> ordinary activation or idle
dragging --accepted release--> commit current destination once; settling
dragging --cancel/ownership lost--> no inferred drop; restore valid state; settling
settling --new eligible gesture--> invalidate old settle; track current visual state
settling --current completion--> idle
any state --unmount--> invalidate; release owned resources
```

The operation may be pending independently of settling. A release followed by lost capture is one finalized gesture, not two. Cancellation must stop autoscroll and release capture/listeners even when the animation system never produces an end callback. If a drag commits before server confirmation, retain a defined reconciliation path.

## Async relevance and rollback

- Capture the identity/version of the operation and the object it changes. A global `isLoading` flag cannot distinguish two successive operations on different targets.
- Update the UI only if a response is still relevant under the data layer's rules. Do not ignore authoritative server results globally just because the original view unmounted; let the data owner reconcile them.
- An optimistic rollback must not restore a stale whole-object snapshot over subsequent edits. Reconcile the affected field/operation against current state or refetch safely.
- Keep destructive, financial, or contractual outcomes explicitly pending until the underlying confirmation required by the product exists.
- Distinguish request cancellation, visual cancellation, and server cancellation. Label uncertainty instead of implying a completed or safely undone operation.
- Preserve draft input and a recovery action after failure. Do not dismiss critical errors merely because a toast exit ended.

## Interruption fixtures

Use [executable recipes](executable-recipes.md) to make old completions arrive deliberately. The bundled controller's controllable-handle tests isolate presentation ownership; the lab adds real browser effects and visible response-delivery controls. Neither substitutes for the application's own request/cache, focus, and navigation tests.

These are behavioral scenarios for the host project, not claims of completed testing. Choose relevant scenarios and implement focused tests using its existing tools.

| Sequence | Invariant to assert |
| --- | --- |
| Open → close → reopen before exit ends | The reopened surface stays present and owns the correct focus; stale DOM/focus changes are ignored while old owned resources are released. |
| A → B → C with responses C, A, B | C remains current; data reconciliation follows the authoritative policy. |
| Begin drag → cancel → lost capture | No drop commit; cleanup occurs once; scroll still works. |
| Release drag → lost capture | Exactly one accepted operation; no second rollback. |
| Start transition → enable reduced motion | Latest state is visible and usable; cleanup does not await an end event. |
| Start pending action → unmount | No stale view callback; data owner handles the result; no orphan listener/lock. |
| Open child modal → close child | Parent remains usable and modal; page is not prematurely unlocked. |
| Remove focused item during layout animation | Focus moves to the chosen meaningful target, with no duplicate accessible copies. |

Do not assert motion quality from these state tests alone. Use [verification guidance](verification.md) for normal-speed runtime assessment and measured performance where relevant.
