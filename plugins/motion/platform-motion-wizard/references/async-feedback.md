# Async feedback patterns

This reference contains authored implementation patterns. Adapt them to the application's real service contract, existing primitives, and installed libraries. Timings from the preserved skill are starting points, not service guarantees.

## Separate three lifecycles

| Lifecycle | Owns | Must not depend on |
| --- | --- | --- |
| Business operation | Request identity, confirmation, error, retry, cancellation, reconciliation | Transition duration or visual mount state |
| Interaction | Input acceptance, duplicate protection, focus, user intent | Spinner visibility or animation completion |
| Presentation | Pending label, progress, reveal, exit, reduced-motion substitution | Invented success or unconfirmed cancellation |

A component may disappear while a durable operation continues. Decide which owner receives its result and where that result remains discoverable. Avoid updating an unmounted owner or silently losing a consequential result.

## Minimal state contract

| State | Visible information | Available actions | Exit condition |
| --- | --- | --- | --- |
| Idle | Current confirmed value or empty explanation | Start | Input accepted |
| Pending | Work accepted; truthful stage if known | Cancel if supported; safe navigation | Confirmation, failure, cancellation, or partial result |
| Partial | Incomplete content clearly identified | Read/copy if safe; stop; applicable retry | Terminal protocol event |
| Success | Actual confirmed outcome | Continue; undo only if real | New user intent or normal dismissal |
| Error | What failed and relevant recovery | Retry, edit, or return | New attempt or explicit dismissal |
| Cancelled | What stopped and what remains uncertain | Retry/resume if supported | New user intent |

Not every component needs every state. A background refresh can preserve confirmed data while exposing a pending or failed refresh indicator. Do not replace the whole screen with a skeleton when useful confirmed content is already available.

## Request identity and stale completion

Assign an identity to each logical attempt. Before applying a completion, compare it against the active owner and intent. The same guard applies to animation callbacks, rollback, status announcements, and focus restoration.

When attempt A is replaced by B, cancel A when the runtime supports it and stop treating A as current. If A later resolves, it may update an appropriate shared cache according to the application's policy, but it must not overwrite B's local view indiscriminately. An HTTP abort does not prove that a submitted server mutation was cancelled.

For retries, distinguish safe reads from writes that may already have committed. Use the service's idempotency key or established mutation strategy. A lost response is an unknown outcome until reconciliation, not proof of failure.

## Loading treatments

- Acknowledge accepted input immediately with a legible state. A secondary spinner can appear later to avoid flashes if that acknowledgement is already clear.
- Reserve representative geometry for images and content. Skeletons should reflect the surface, not invent a hierarchy that the result will replace abruptly.
- Do not delay a fast result to let a loading animation finish. Avoid fake percentages, progress that reaches completion before confirmation, and loops implying work that has stopped.
- Keep the control stable during label changes. Avoid moving its target away from the pointer or collapsing surrounding layout.
- Prefer a static placeholder in reduced-motion mode. Preserve a pending label and relevant status semantics.

## Optimistic reconciliation

Use optimism for a small reversible operation only when rollback is defined. Record the affected entity and attempted change, not merely a whole-screen snapshot. If another action changes the same entity before an earlier failure arrives, reconcile the failed operation without overwriting the newer intent.

Keep purchase, transfer, deletion, permission, and commitment outcomes pending until the service confirms them. A local checkmark must not imply that a transaction completed remotely.

## Stream ownership and reading position

Store streamed content separately from its animated presentation. Coalesce renders with the framework's existing scheduling mechanism; never discard chunks to make the animation look calmer. Ensure terminal chunks and error events flush correctly.

Track whether the user is following the end. Preserve selection, scroll anchor, and keyboard focus when they read earlier content. Only follow new content automatically when appropriate to that existing mode. A visible latest-content control should restore following intentionally.

Announce a concise stage such as “Receiving response” or “Upload failed” through the product's status pattern. Keep the actual content available to assistive technology; avoid token-by-token live announcements. Do not fabricate a model's internal thought process or label waiting time as verified reasoning.

Generation, tool execution, approval, and server commit are different activities. Report each from real events. Keep partial results usable when safe and mark them incomplete after failure or interruption.

## Recovery checks

Verify out-of-order replies; retry after a lost response; cancellation during partial output; unmount during pending work; restored network; an expired session; rapid repeated submission; reduced motion switched during loading; and failure while a success exit animation from an earlier attempt is still present. No critical transition should require `animationend`, `transitionend`, or a fixed timeout.
