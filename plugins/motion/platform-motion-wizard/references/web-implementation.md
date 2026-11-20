# Web implementation decisions

## Pick an implementation

| Need | Default path | Check |
| --- | --- | --- |
| Fill, opacity, small press state | Existing CSS tokens + state selectors | Keyboard focus distinct; no transform competition |
| Interruptible imperative sequence | Existing library or WAAPI | Cancellation, retargeting, zero-motion endpoint |
| Enter/exit rendering | Existing primitive/presence support | Semantics, focus, hit testing, completion ownership |
| Reflow/accordion | Existing measurement/layout support | Dynamic content, resize, fonts, read/write batching |
| Route/shared identity | Existing router + progressive enhancement | Back, scroll, focus, uniqueness, no-animation fallback |
| Gesture | Existing gesture system or local pointer events | Axis arbitration, capture cleanup, scroll owner |

Check installed versions and runtime targets. Repository main can contain unreleased fixes.

The [executable recipes](executable-recipes.md) include an original scalar presentation controller, live preference policy, and deterministic replacement/failure tests. Adapt the ownership pattern to the installed stack; do not import an upstream internal hook or replace accessible primitive behavior with this example.

## Logical state and visual presence

Example conceptual ownership:

- operationId identifies the latest domain action.
- desiredOpen identifies the current requested overlay state.
- presentationHandle identifies a cancelable visual effect.
- generation identifies the latest presentation transition.

On replacement, increment the relevant generation, cancel the old handle, read current presentation when retargeting, and begin the new effect. A completion must check its generation and current desired state before doing any presence cleanup. Keep operation IDs separate: a successful request must not be discarded solely because decorative motion was canceled.

Use effect cleanup and explicit stable endpoints. Do not hide content in initial CSS unless no-JS and failure paths restore it.

## WAAPI and CSS failure cases

An animation may be canceled because a newer action supersedes it; its finished promise can reject. Catch expected cancellation and settle to the correct state. Do not swallow unrelated errors.

transitionend may not fire when duration is zero, a property does not change, the element is removed, or the transition is canceled. Use events only for presentation cleanup with an explicit fallback path, never to confirm a save or permit an action.

Avoid transition: all. Apply only needed properties. Do not put permanent will-change on whole component trees. Transform/opacity often avoid layout work but can still cost raster, memory, and compositing.

## SSR and framework lifecycle

Use a server-safe initial preference and render useful content. Subscribe on the client with cleanup. Reconcile the first client preference without replaying unrelated entrance motion. React development Strict Mode, Vue remounts, and Svelte lifecycle cleanup must not duplicate listeners or operation timers.

Motion hook names are not a guarantee of live OS changes. Test a preference toggle while the component is mounted and while an effect is active. Prefer one observable policy shared by CSS, JS, and scroll utilities.

## View Transitions

Treat the animation as optional; the route/data update remains authoritative. Check support, skipped/rejected transition promises, overlapping updates, unique transition names, focus transfer, browser history, and reduced motion. Do not make old and new content both interactive or expose duplicate accessible copies.

Cross-document behavior and framework integrations vary by release and browser. Verify target support instead of enabling an API from a generic snippet.

## Layout and scrolling

Measure before writing, batch operations, use stable keys, and test dynamic content. A virtualized list can recycle DOM nodes while item identity changes; do not infer identity from the node alone. Preserve the reading/focus anchor when insertions or streams arrive.

Respect native scroll. Where a drag needs edge auto-scroll, use elapsed time rather than an assumed frame rate, clamp it, and stop on release/cancel/unmount. Test nested containers and page scroll independently.
