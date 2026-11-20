# Deterministic async, persistence, UI, and performance checks

## Await real completion

Prefer calling an async production operation directly and awaiting its result. When production starts an owned task from a synchronous boundary, expose a meaningful completion/cancellation seam appropriate to the product rather than sleeping until a side effect seems likely.

For callback/event tests, establish listener readiness before producing the event. An explicit registration acknowledgement or controlled fake is evidence of readiness; Task.yield merely offers a scheduling opportunity. A timeout bounds a broken test; it should not determine the order of a successful one.

Framework confirmation/expectation APIs have their own lifecycle contracts. Verify when the confirmation scope ends and whether work must be awaited within it. Do not expect a scope to wait automatically for an unowned task. Use exactly the event count/order the behavior requires.

## Control concurrent scenarios

Use a dependency gate with separate “started” and “complete” controls. Ensure failure/cleanup paths release or cancel all held tasks. A test must not hang indefinitely because an assertion failed before a continuation was resumed.

| Regression | Controlled sequence | Product assertion |
| --- | --- | --- |
| Stale search success | A starts, B starts, B completes, A completes | Latest query's result remains visible |
| Stale search failure | A starts, B succeeds, A fails | Old error does not replace newer content |
| Cancellation ignored | Operation reaches dependency, cancel, dependency later completes | No invalid state write; resource lifetime meets contract |
| Retry behavior | Supply prescribed failures then success, advance injected clock | Correct attempt count/backoff and one final outcome |
| Callback bridge | Callback and cancellation race through controlled seam | Exactly one resolution and expected underlying cancellation |
| Stream teardown | Listener ready, emit, cancel/finish | Required values observed and producer registration released |

The test must exercise cancellation checks in production behavior, not merely assert that a test-created Task.checkCancellation throws. A clock abstraction should drive the production delay/debounce policy; advancing a test-only timer proves nothing about the app's path.

## Persistence integration

Choose the actual store behavior needed. In-memory fixtures can check ordinary object graph logic. Use temporary SQLite-backed stores for SQL predicate translation, batch/history or migration behavior when those depend on that backend. Await container/store readiness before using contexts.

Keep each fixture's directory and context ownership explicit. Assert save errors instead of discarding them. Refetch through a fresh context or reopen when durability is the contract. Test both relationship survivors and removed records after deletion.

For migration, create an old-version store, close it correctly, open with the new supported strategy, verify transformed values/relationships, and reopen again. Cover supported direct upgrades and sparse/conflicting legacy data. Never point tests at a developer's normal or production store. Cleanup may remove only resources the fixture owns.

Cloud delivery is a separate integration concern. A successful save or export event does not prove second-device import. Use an authorized isolated environment and bounded observations for real sync tests. Label tests that only replay synthetic events accordingly.

## UI and accessibility behavior

Select the intended app, test scheme and simulator/device. Use stable accessibility identifiers for automation where appropriate; identifiers do not replace user-facing labels. Wait for meaningful element/state conditions instead of arbitrary delays. Avoid making assertions depend on incidental animation duration or exact view hierarchy.

Exercise the changed user path, relevant error/empty/loading state, and semantic accessibility behavior affected by the change. Screen captures document appearance but do not prove dynamic type, focus order, VoiceOver or hit targets. Use supported inspection/manual device checks as required and report their limits.

Tests that need permission prompts or system state should control that fixture explicitly and restore only what they changed. Do not reset all simulators to obtain repeatability. Separate device-only capabilities from simulator coverage.

## Performance checks

Name the workload and metric before measuring: launch, scroll hitching, decode/import time, memory or network behavior. Record build configuration, device/OS, dataset and instrumentation. A debug simulator timing is not a production-device performance guarantee.

Use the framework's supported measurement API or Instruments trace when available. Warm/cold state, caching, thermal conditions and background work can affect comparisons. Preserve enough context to interpret a regression; do not introduce a numeric budget copied from an unrelated reference.

## Run and report

Run focused tests first, then required project checks. Record command, selected target/configuration, result bundle/artifact location and outcome. Investigate a failure before rerunning until green. Distinguish a flaky infrastructure failure, an assertion failure and an unsupported host.

Static inspection or generated test syntax does not establish runtime success. On a host without Apple tools, validate what is available and list the precise Xcode/simulator/device checks remaining. Do not fabricate passed tests or hide an unexecuted suite behind a generic “validated.”
