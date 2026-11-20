# Cancellation, bridges, streams, and deterministic verification

## Cancellation is an input to the operation

Cancellation requests cooperation. Check at safe boundaries in long-running CPU work and before obsolete results become visible. Awaiting another function does not guarantee that function responds to cancellation. Treat expected lifecycle cancellation separately from user-facing failure, including transport APIs that express it with their own error type.

Define the owner and outcome first. Replacement search may cancel the prior search; a committed purchase should follow its transaction rules rather than a screen's disappear event. A cancellation handler can run concurrently with the operation and must obey its synchronization/isolation contract. Keep it small; do not mutate actor-isolated UI state from an arbitrary callback.

For replacement work, protect both successful and failing state writes with the current request/generation identity when late completion is possible. “We called cancel” is insufficient evidence that an old result cannot win.

## Callback bridges

Before wrapping a callback API, determine whether it calls back once or multiple times, on which executor, and whether cancellation returns a handle. A checked continuation must resolve exactly once across every race:

1. normal success or failure;
2. cancellation before the legacy operation starts;
3. cancellation after start but before its handle is stored;
4. callback concurrent with cancellation;
5. a legacy API violating its callback contract.

Use one synchronized resolution state when those paths can race. Do not rely on an unsynchronized optional continuation. Cancel the underlying operation when supported and define the result when it cannot be cancelled. Do not invent a callback wrapper for a framework API that already exposes a suitable native async form.

Per-item callbacks need aggregation or a stream. For example, an API loading several stores may report one completion per store; resuming one continuation for every callback is a double-resume bug. Record expected completions and resolve the aggregate once.

## Streams

Decide whether the producer is finite or live, whether ordering matters, and whether dropping old or new values is acceptable. Select a bounded buffer for high-volume sources unless unbounded growth is justified. Inspect yield results when overflow or termination matters. Buffering is not full back-pressure by itself.

Retain the producer for the required lifetime. Finish finite streams on all terminal paths and release callback registrations/resources on termination. Stream continuation finish is not the same contract as one-shot continuation resume. Cancellation of a consumer should lead to the intended producer cleanup; verify that path rather than assuming every callback source stops automatically.

If a loop processes expensive synchronous work between awaits, check cancellation within that work where safe. A stream ending does not prevent code after the loop from running; explicitly choose completion versus cancellation behavior.

## Deterministic tests

Control the dependency, not the scheduler. A gate should acknowledge that production code reached a meaningful point, then let the test release the result. Task.yield and zero-duration sleep do not prove a listener registered or a request began.

| Scenario | Required ordering | Observable assertion |
| --- | --- | --- |
| Replaced search | A acknowledged, B acknowledged, B succeeds, A succeeds | B remains visible |
| Late failure | A acknowledged, B succeeds, A fails | Old failure does not replace B |
| Cooperative cancellation | Production operation acknowledged, cancel, release its dependency if needed | Production exit/cleanup contract occurs; no stale write |
| Callback/cancel race | Arrange both resolutions through a controlled bridge seam | One result, one resource cleanup, no continuation leak |
| Stream overflow | Produce beyond selected capacity while consumption is controlled | Documented items are dropped/retained and resources remain bounded |
| Stream termination | Consumer starts, then cancels or producer finishes | Registration/operation cleanup occurs as specified |

Await real completion or use the framework's bounded event mechanism. Timeouts detect hangs; they should not sequence a passing test. Ensure failed tests can still release gates and clean up tasks so the suite does not hang.

Run the affected target's compiler checks first. Sanitizers can help with unsafe interoperation and runtime races, but a clean sanitizer run does not prove the ownership design. Report the exact test environment and any unavailable Xcode/device validation.
