# Lifecycle and failure tests that expose real integration defects

## Select cases from the changed behavior

Do not create every possible failure test for a narrow edit. Identify the owning state machine and durable effects, then choose the cases that can violate its acceptance criteria. Control request completion, time and worker readiness at a useful seam. A sleep, a yield or a successful callback count does not prove a listener is ready or a durable effect is correct.

| Trigger | Required observation |
| --- | --- |
| Invalid body or cursor | Stable rejection and no unintended write |
| Valid identity, wrong tenant/entity | Server denial without another account's data |
| Session expires during a request | Scoped refresh/sign-in behavior without unsafe write replay |
| Account changes while data loads | Old completion cannot publish data into the new account |
| Request A finishes after newer B | Current UI/projection retains the intended result |
| Client cancels after server commit | Honest uncertain/pending state, then authoritative reconciliation |
| Duplicate operation or concurrent retry | Intended durable deduplication or explicitly documented repeat effect |
| Same operation key, different payload | Defined conflict behavior; no silent reuse of a different outcome |
| Worker stops after an effect | Retry/recovery does not corrupt authoritative state |
| Duplicate or reordered provider event | Verified event handling and current domain state |
| App/extension process is absent | Useful snapshot or fallback, no assumed shared in-memory owner |
| Background expiration or provider outage | Bounded stop/retry, durable checkpoint and clear pending state |

Each row describes an outcome to verify, not a promise that the current application already implements it. If the contract intentionally permits a repeated action, document and test that behavior rather than imposing a different business rule.

## Control ordering and uncertainty deliberately

Expose a test seam for the relevant transport, store, clock or worker acknowledgment. Arrange a readiness signal, trigger the operation, hold the completion at the point that matters, make the competing state change, then release completion. Assert the final visible and authoritative state. In asynchronous tests, wait for a meaningful completion or explicit idle state with a bounded test timeout; avoid arbitrary delays.

For cancellation, test more than whether a task was cancelled. The remote operation may have committed already. Simulate an accepted write with a lost response, then exercise the actual reconciliation/idempotency policy. Verify operation-key scope and domain invariants in the durable store, including concurrent callers. An in-memory map can illustrate a seam but cannot establish cross-process atomicity or recovery after a real crash.

For event/job flows, separate provider receipt, signature acceptance, durable enqueue, job acknowledgment and domain effect. Inject a stop between the relevant stages. Record which stage is retried and who owns poison-work, expiration and dead-letter handling. Do not label a queue's completed state as exactly-once business execution.

## Exercise native boundaries separately

Run main-app lifecycle and extension/process cases using the actual targets when available. Test stale app-group snapshots, denied access, device-lock behavior, expired activities and unsupported availability paths as relevant. A simulated push can demonstrate a handler path; it does not establish production provider delivery, entitlement correctness or when the OS will schedule work.

Keep artifacts bounded and synthetic: contract revision, operation identifier alias, stage, expected outcome and observed result. Redact raw tokens, account identifiers, private content and signed media URLs. Report unit/mock, durable-store integration, provider and native-device evidence as separate results.

Sources: src_backend_repo_080 — [Idempotent worker design](https://github.com/taskforcesh/bullmq/blob/804fc03a84ca79453856ce287dfc66a6d6a6f01c/docs/gitbook/patterns/idempotent-jobs.md); src_nm_node_test — [Controlled Node tests](https://nodejs.org/api/test.html); src_backend_apple_002 — [Widget update lifecycle](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date); src_backend_apple_022 — [Background maintenance](https://developer.apple.com/documentation/backgroundtasks/refreshing-and-maintaining-your-app-using-background-tasks).
