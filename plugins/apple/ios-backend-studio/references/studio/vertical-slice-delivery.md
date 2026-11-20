# Deliver a representative vertical slice

## Choose a slice that crosses the real boundary

Select one useful operation from the requested feature: a list read, an authenticated change, a widget projection or an event-driven update. Define its supported clients and failure behavior first. Do not scaffold an entire replacement platform to demonstrate a narrow integration. Keep the chosen framework, transport, provider and dependency locks unless the task specifically needs a change.

A read-only slice should include the server's real response validation/mapping and an actual consumer decode. A write slice also needs entity authorization, domain constraints and recovery after an uncertain result. An extension slice needs a separate projection/action boundary; it is not completed by adding a view to the main app.

## Execute in dependency order

1. Inspect the existing authority artifact and call sites. Define statuses, stable error shape, identifiers, null/absence and operation identity where required. Decide which old requests and responses remain supported.
2. Implement or adjust the Node handler and its useful dependency seams. Validate input, authenticate and authorize, then perform the durable effect. Keep request errors distinguishable from infrastructure failures without exposing secrets.
3. Generate or update consumer bindings through the project's pinned task. Review generated changes and preserve transport/middleware integration. Do not permanently hand-edit derived source as the primary fix.
4. Integrate the native app's owned state and cancellation. Reject stale completion independently of cancellation, since cancelled work can already have reached the server. Map uncertain write outcomes to reconciliation rather than unconditional retry or success.
5. Add the extension/web adapter when requested. Share a compact, versioned projection and domain command contract; keep process, auth and scheduling constraints visible.
6. Verify the slice with controlled wire fixtures and failure cases before broadening it. Run required project checks once the final relevant edit is complete.

## Exercise recovery, not just the happy path

For a write, interrupt after the server commits but before the client receives its response. Repeat the same operation through the supported recovery policy and verify one intended durable effect. An operation key is useful only if its scope, concurrent claims, payload conflicts, retention and recorded outcome are implemented in the authoritative store.

For a read, force response A to finish after a newer response B; verify that the client retains the right state. For an event, duplicate and reorder deliveries and stop a worker after an acknowledged or committed stage. For a projection, read an older snapshot after the app has upgraded; verify the intended compatible fallback.

Keep retries bounded, use readiness/completion controls rather than sleeps, and assert authoritative state. A queue finishing once is not proof that its domain effect happened exactly once. Mocked transport tests and a real database transaction test establish different facts.

## Finish with reviewable evidence

Return the user-visible result, owner-to-owner path, contract revision and changed files. Name exact checks and candidate configurations, including old-client cases. Separate Node/Python evidence from Xcode compilation, device/extension execution, signing and provider delivery. If the Apple environment is absent, complete independent work and state the pending native check precisely.

Sources: src_backend_repo_001 — [Swift generator entrypoint](https://github.com/apple/swift-openapi-generator/blob/75962579db43e88440bbad021c74570f0955d1fd/README.md); src_backend_repo_063 — [TypeScript generator entrypoint](https://github.com/openapi-ts/openapi-typescript/blob/d46a319ae2efab30e135ba9b223a3cffd1a67eab/packages/openapi-typescript/src/index.ts); src_backend_repo_080 — [Idempotent job design](https://github.com/taskforcesh/bullmq/blob/804fc03a84ca79453856ce287dfc66a6d6a6f01c/docs/gitbook/patterns/idempotent-jobs.md); src_nm_node_test — [Node tests](https://nodejs.org/api/test.html).
