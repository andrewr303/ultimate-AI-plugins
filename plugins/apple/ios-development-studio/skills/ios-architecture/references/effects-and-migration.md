# Effects, incremental migration, and verification

## Define an effect contract

For each asynchronous intent, record its input, result, owner, lifetime, cancellation policy and permitted state writes. A refresh may replace the previous refresh; an upload may need explicit user cancellation; independent downloads may coexist. “Cancel everything on disappear” can lose work the product expects to continue.

Choose structured async work when the caller owns the lifetime. A SwiftUI `.task` can await an async model method; a model method that immediately spawns its own unstructured task breaks that ownership chain. If an independently owned task is required, store/manage its handle and expose the appropriate lifecycle operation. A weak capture alone does not define cancellation behavior.

Treat normal cancellation as a lifecycle result. Map domain failures to product state at the presentation boundary and preserve technical diagnostics privately. Do not display raw error strings by default. Loading, empty, offline, retryable failure, partial success and stale content may need distinct behavior; model only states the feature can actually exhibit.

## Guard state after suspension

Cancellation is cooperative. A dependency can finish normally after cancellation, and two requests can complete out of order. Before a result changes state, establish whether it still belongs to the current intent. A generation/request identity is often sufficient for replacement work. Check both success and error paths so an old failure cannot replace a newer success.

An actor protects access to state but permits interleaving at suspension points. It does not automatically prevent duplicate effects, stale results or an invalid multi-step transition. Where an operation must be atomic at the domain level, use an explicit pending state/transaction, validate after await, or choose a dedicated operation owner. Do not hold a synchronous lock across suspension.

## Migrate one slice at a time

1. Capture current behavior in a focused test or a reproducible scenario. Include a failure mode relevant to the change.
2. Choose a seam with an observable contract: a repository call, feature action/render loop, route event or persistence operation.
3. Introduce an adapter at that seam if needed. Preserve callers until the new path is proven. Avoid two writable models representing the same entity without a reconciliation policy.
4. Move one behavior with its state, errors and effect lifetime. Remove obsolete ownership once callers have moved.
5. Check lifecycle and integration behavior, then proceed to the next slice only if the task needs it.

For persistence changes, route to the engine-specific skill before changing schemas or store ownership. For a concurrency diagnostic, route to concurrency before moving code between modules. A compilation failure is not evidence that the entire architecture is wrong.

## Test through the feature boundary

Use injected dependencies to control outcomes, not to mirror every implementation method. A useful replacement-intent test starts request A, waits for an explicit dependency acknowledgement, starts request B, completes B, then completes A. Assert the visible state still represents B. Do not make this order depend on sleeps or Task.yield.

For navigation, exercise the event that triggers routing, observe the destination/path, complete or cancel the child flow, and verify ownership ends. Deep-link tests should cover valid input plus invalid/missing prerequisites. A retained coordinator test is useful only when lifecycle behavior is part of the feature's risk.

For a reducer, assert important state transitions and effect outcomes at its public action boundary. For a view model/presenter, assert rendered/product state after a public intent. For layered domains, test business policy independently and one integration path through the adapter. Avoid tests that only restate private helper calls or file layout.

## Review failure cases

| Symptom | Inspect before prescribing a pattern |
| --- | --- |
| Duplicate navigation | Multiple route owners, repeated subscriptions, replayed events, missing completion reset |
| Stuck loading | Cancellation/error paths that never leave the pending state, unawaited task, missed callback |
| Old search results | Completion order, missing request identity, cancellation ignored by dependency |
| Retained screen | Task/subscription capture graph, coordinator ownership, callback lifecycle |
| Hard-to-test behavior | Hidden global dependencies, uncontrolled time/randomness, no observable completion contract |
| Error details in UI | Transport error leaking across the presentation boundary |

## Completion evidence

Record what behavior changed and the smallest checks that demonstrate it. State target/configuration and tool availability. If only static review was possible, identify the runtime scenario still needing verification. Do not claim an illustrative snippet builds, or a diagram proves lifecycle correctness.
