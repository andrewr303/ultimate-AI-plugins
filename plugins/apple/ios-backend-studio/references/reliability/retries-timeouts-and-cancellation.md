# Bound retries without multiplying intent

## Classify the operation and outcome

Read the actual endpoint/provider contract and the caller's lifetime. Distinguish a safe read, an idempotent mutation with durable identity, an admission request and an operation whose outcome is unknown after sending. HTTP method alone is not enough if an existing route violates its expected semantics or triggers a domain effect.

Classify transport failure, explicit server rejection, authentication expiry, authorization denial, validation failure, conflict, throttling and dependency failure. Do not map all errors to “offline” or retry everything. A malformed payload or revoked permission does not become valid after waiting. A temporary failure may still require reconciliation if the server could have committed.

## Use finite budgets

Define an overall operation deadline, per-attempt timeout, maximum attempts and bounded delay/backoff. Respect a documented server retry hint when applicable, accounting for whether it is a duration or a date and how clocks are interpreted. Keep a maximum bound so malformed or extreme hints cannot park a worker indefinitely.

Use jitter and concurrency limits where they address synchronized load, rather than creating an unbounded retry fan-out. A retry budget can be scoped by account, route or provider according to the actual bottleneck. Do not retry a throttled account through different identities or credentials to evade a provider limit.

| Outcome | Typical next decision |
| --- | --- |
| Request never admitted and retry is safe | Retry within the declared budget |
| Outcome unknown after send | Reconcile or retry with the same durable operation identity |
| Expired authentication | Run the approved refresh/re-auth path, then re-evaluate safety |
| Domain authorization/validation rejection | Surface repair/denial; no blind retry loop |
| Version conflict | Refetch/merge according to domain policy |
| Persistent dependency failure | Preserve pending work and a useful user/operational status |

Choose a durable scheduled job when a retry must survive process termination. A Node timer or unawaited promise does not make a short-lived host continue running after its request ends. Conversely, do not add a queue merely to retry a simple foreground read that can safely fail and be tried again by the user.

## Cancellation and ownership

Connect cancellation to the task/request owner where the runtime supports it. Release response bodies, streams, sockets and other resources deliberately when work is abandoned. Keep a small failure/result state so a late completion cannot update a newer screen request or another account's state.

A native task being cancelled does not imply the server or provider rolled back. If a mutation may have committed, retain its logical identity and reconcile it. Do not immediately create a new operation ID because a URLSession request reported cancellation or timed out.

Token refresh is another owned asynchronous operation. Coalesce refresh work where appropriate, bind it to a session generation, and discard a completion after sign-out or account switch. An old refresh result must not restore credentials or populate a new account's cache. Avoid treating every unauthorized response as proof that refresh is the right action.

## Streaming and backpressure

Set size/time limits for buffered bodies and use supported streaming when the feature needs it. Generated Swift transports and hosting adapters can differ in buffering, redirect and replay behavior. A request body may be single-pass; automatic redirect/retry cannot always replay it. Decide how to reconstruct a safe request or reject a replay rather than assuming every stream can be consumed again.

Handle client disconnect and server shutdown with the actual framework/runtime hooks. A local abort signal cannot undo bytes already sent or a completed remote action. For long transfers, report progress and recovery based on actual persisted state rather than an invented percentage after a retry.

## Deterministic verification

Inject a transport and clock/scheduler at useful seams. Release controlled success/error responses in different orders, cancel at named boundaries and verify that obsolete outcomes are ignored. Test retry hints, budget exhaustion, re-auth failure, partial body, disconnect and a timeout after durable server commit.

Assert both attempt behavior and the domain result. A test that advances a timer and observes another request does not prove duplicate side effects are impossible. Do not use arbitrary sleep as readiness or cancellation evidence.

## Evidence and version cautions

`src_backend_repo_046` is the pinned [Swift URLSession cancellation test](https://github.com/apple/swift-openapi-urlsession/blob/c97e0f0187d95542b4a254f5bb4dc67f43bf73c9/Tests/OpenAPIURLSessionTests/TaskCancellationTests.swift); `src_backend_repo_047` covers [transport conversion/redirect tests](https://github.com/apple/swift-openapi-urlsession/blob/c97e0f0187d95542b4a254f5bb4dc67f43bf73c9/Tests/OpenAPIURLSessionTests/URLSessionTransportTests.swift). `src_nm_node_http` points to [Node HTTP lifecycle APIs](https://nodejs.org/api/http.html), and `src_backend_repo_081` to [queue retry guidance](https://github.com/taskforcesh/bullmq/blob/804fc03a84ca79453856ce287dfc66a6d6a6f01c/docs/gitbook/guide/retrying-failing-jobs.md). Verify the resolved transport, body replay and provider semantics using [source records](../../research/sources/sources.jsonl); no target network/runtime was exercised here.
