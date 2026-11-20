---
name: motion-async
description: "Use when improving pending, loading, refreshing, progress, success, error, optimistic, streaming, or AI-agent activity feedback. Implement truthful state transitions and interruption-safe responses. Pair with motion-controls for submit buttons; use motion-gestures for direct manipulation."
---

# Async feedback and streaming

Make the product acknowledge input immediately and tell the truth about its work. Animation never owns the request lifecycle. Read [async feedback](../../references/async-feedback.md) and load [accessibility](../../references/accessibility.md) when changing announcements or live content.

## Establish the contract

1. Inspect the actual request, cache, mutation, router, and stream implementation. Locate server acknowledgement, terminal events, retry policy, and cancellation support.
2. Record whether an action is read-only, reversible, destructive, financial, or otherwise consequential. Separate local acceptance from remote completion.
3. Capture the current empty, populated, refreshing, partial, unavailable, and failed surfaces. Preserve useful input and previously confirmed content.
4. Identify the operation's identity and the owner's lifetime: component, route, document, background job, or durable server task.
5. Reuse the product's status, error, and toast primitives. Determine how keyboard users and assistive technology find progress and recovery.

Produce one compact table: event → business state → visible acknowledgement → available actions → terminal evidence → reduced-motion path. Then implement it when code changes are requested.

## Implement business state before animation

1. Define the states actually required: `idle`, `pending`, `partial`, `success`, `error`, and `cancelled`. Refreshing may coexist with confirmed data; partial is not success.
2. Change to pending on accepted input and begin the real operation independently. Never await an entrance transition or artificial spinner minimum.
3. Give each attempt an identity. Only an attempt that still owns its target may commit its result, error, animation completion, or rollback.
4. Abort superseded work when supported; also ignore stale results. An abort request alone does not establish that remote work stopped.
5. Keep duplicate protection in operation state. A fading button, disabled CSS style, or animation timer is not a mutation lock.
6. Commit success only from the defined confirmation. Preserve the previous confirmed state on failure, show recovery beside the affected content, and keep user input.
7. On cancellation, distinguish “stopped locally,” “cancellation requested,” and “server confirmed cancellation” where the distinction matters.
8. Handle unmount, route changes, offline recovery, expired credentials, retries, and responses that arrive after timeout. Prevent obsolete callbacks from replacing newer status.

## Choose a restrained presentation

- Keep the control's hit target and label legible; reserve space for its pending treatment.
- Use a static pending label immediately. Delay a secondary spinner only when another acknowledgement is already visible; do not delay work or success.
- Use measured progress only when a meaningful numerator and denominator exist. For unknown duration, show a truthful stage or indeterminate state.
- Reserve useful content geometry with a representative placeholder. Avoid shimmer when it adds no information; use a static reduced-motion treatment.
- Keep safe stale data during refresh and label its state. Never present outdated prices, permissions, or other consequential information as current.
- Keep errors available until resolved or intentionally dismissed. A departing toast cannot be the only recovery surface.
- Confirm success quietly and preserve next actions. Do not replay celebration on remount, polling, cache revalidation, or every streamed chunk.

## Streaming and agent activity

1. Identify actual events supplied by the system: queued, receiving output, tool running, waiting for input, completed, failed, or interrupted. Do not invent hidden reasoning or completed work.
2. Coalesce frequent chunks with the existing rendering scheduler. Keep logical content complete; avoid mounting an independently animated element for each token.
3. Preserve selection and reading position. Follow the stream only while the reader is already following its end; otherwise offer a “Jump to latest” control and indicate new content.
4. Keep cancel, retry, copy, and relevant recovery actions usable. Label incomplete output and preserve it when useful after interruption.
5. Announce meaningful stage changes through the existing status pattern. Do not read every token or repeatedly announce decorative progress.
6. Mark completion only when the protocol supplies a terminal event. A pause in tokens or a finished visual pulse is not completion.
7. If generated content can run code or make changes, keep its execution status separate from generation status. A completed answer does not establish a successful tool operation.

## Optimistic work

Use optimism only for an explicitly reversible action with a defined reconciliation path. Capture operation-specific rollback information, reconcile server canonical data, and avoid undoing a newer user action when an older request fails. Keep consequential outcomes pending until confirmed. Retry mutations only with the application's established idempotency strategy; do not silently replay a possibly committed transaction.

## Verify and deliver

Exercise fast and slow success, failure before and after partial output, duplicate input, retry, cancel, out-of-order completion, route departure, and offline recovery where supported. Repeat relevant flows with reduced motion enabled and changed during work. Confirm that zero animation events still produce terminal state and cleanup.

Use focused state tests for the concrete race or mutation risk; reuse existing integration checks. If runtime is unavailable, identify every unexercised behavior.

Force the obsolete completion to arrive: start A, replace with B, deliver B, then deliver A and assert B remains current. Repeat for an obsolete rejection and local cancellation. Clearing A's timer or aborting its mock before delivery does not exercise the stale-result guard. The [executable recipes](../../references/executable-recipes.md#deliver-the-stale-result-in-the-test) and local lab demonstrate the distinction; keep production reconciliation with the actual data owner.

Deliver working changes plus the state table, changed acknowledgement/recovery behavior, exact verification evidence, and remaining service limitations. Route jank investigations to [motion-performance](../motion-performance/SKILL.md) and independent assessment to [motion-review](../motion-review/SKILL.md).
