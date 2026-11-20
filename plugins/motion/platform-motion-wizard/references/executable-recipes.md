# Executable lifecycle recipes

Use these examples when a lifecycle bug needs a reproduction. Prefer the product's existing primitive and animation system; this is a small reference, not a framework adapter or an accessible component library.

The [browser lab](../examples/motion-lab/index.html) loads the original [lifecycle controller](../examples/motion-lab/motion-lifecycle.js) as a classic script, including when opened from disk. The same file exports its API to CommonJS for [deterministic tests](../tests/test_motion_lifecycle.cjs). No runtime package installation is needed.

## Choose the ownership boundary

| Responsibility | Owner | Observable check |
| --- | --- | --- |
| Expanded/selected/pending state | Component or data layer | Changes on accepted input even without animation |
| Focus, modality, dismissal and hit testing | Existing accessible primitive | Correct on the first frame and during dismissal |
| Scalar presentation and its animation handle | Presentation controller | Rapid replacement starts from the visible value |
| Operating-system and local motion preference | Shared live policy | Local setting can reduce further, never override system reduction |
| Request identity and reconciliation | Existing request/cache owner | A delivered obsolete response cannot replace newer intent |

Do not use a presentation completion to close a modal, save data, restore focus, or confirm a request. A controller finishing is evidence only about its own visual work.

## Retarget a decorative effect

The example API accepts a finite numeric value. Its adapter reads presentation, writes a stable endpoint, and starts a finite effect. Keep each property under one owner.

```js
const policy = PlatformMotion.createMotionPolicy();
const keyframe = (value) => ({ opacity: value });
const presentation = PlatformMotion.createPresentation({
  policy,
  read: () => Number(getComputedStyle(decoration).opacity),
  write: (value) => { decoration.style.opacity = String(value); },
  start: typeof decoration.animate === 'function'
    ? (from, to, { duration }) => decoration.animate(
        [keyframe(from), keyframe(to)],
        { duration, easing: 'ease-out', fill: 'both' }
      )
    : undefined,
  onError: (error) => reportPresentationError(error)
});

// The component updates its logical state and semantics separately.
presentation.set(1, { duration: 180 });
presentation.set(0, { duration: 180 });
// Sample visible opacity, invalidate old callbacks, then replace the effect.
presentation.set(1, { duration: 180 });

// On teardown, before removing the owned node:
presentation.dispose();
policy.dispose(); // Only the owner of this policy disposes it.
```

`decoration` and `reportPresentationError` are application-supplied values. The duration is an authored example, not a platform recommendation. The adapter is limited to scalar presentation; it does not preserve spring velocity, measure layout, or arbitrate competing CSS/framework transforms.

`set` commits the base endpoint synchronously before an optional effect. `settle` applies the latest target and releases the owned effect. A live change to reduced motion settles active work. `dispose` invalidates callbacks, unsubscribes and releases the effect without writing to a node that its owner may have removed. Dispose presentations before disposing a shared policy. Recreate disposed controllers when remounting; disposal is terminal.

Missing animation support and zero duration take the same endpoint path. Unexpected animation failures reach `onError`; a canceled `finished` promise is handled explicitly. The example accepts finite effects only; it does not wait for document-wide animations, decorative loops, or unrelated components.

Keep `onError` a diagnostic sink. Unexpected failures from old or disposed work may still be reported; that callback must not write to a captured view or change current interaction state without its own lifetime/ownership check.

## Deliver the stale result in the test

Clearing a timer or aborting a mock request proves cancellation was requested. To prove stale-result protection, retain a controllable response and actually deliver it:

1. Start attempt A; assert pending acknowledgement immediately.
2. Start replacement B without resolving A.
3. Resolve B; assert B's confirmed visible state.
4. Resolve A; assert delivery occurred and B still owns the state.
5. Repeat with A failing, with local cancellation, and with the original view removed.

The lab's local response controls expose delivery and ignored-result counts. In a real product, use its existing deferred-promise, request interception, or cache-test facilities. Do not expose debug globals in production or equate ignoring a view callback with canceling server work.

## Prove there was an effect to interrupt

Before testing live reduction or cancellation, assert that motion is active. Then change the preference or target and check the endpoint, logical state and absence of an owned running effect. A test that starts with no animations cannot prove an active animation was settled.

Use controllable handles for deterministic ordering, then exercise actual browser animation in the product. The reference tests are state/ownership evidence; stable screenshots and fake timers do not establish perceptual smoothness, assistive-technology support or device performance. See [verification](verification.md) and the [overhaul research report](../research/overhaul/outputs/research-decision-report.md).
