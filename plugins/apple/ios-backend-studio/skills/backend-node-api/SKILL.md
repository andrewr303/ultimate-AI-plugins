---
name: backend-node-api
description: "Use when implementing or diagnosing the Node.js HTTP API consumed by native iOS, widgets, web or other clients: request validation, resource authorization, mutation outcomes, retries and route tests. Do not replace an established framework, provision a host, or treat static types as runtime validation."
---

# Node.js API implementation

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Inspect the actual backend/app roots, runtime, framework/middleware, lockfiles, deployment model and current changes. Trace the requested operation through transport, validation, authorization and domain work.
2. Define the observable wire behavior and durable mutation boundary before edits. Preserve the existing framework and hosting contract; distinguish client cancellation, retry and authoritative completion.
3. Implement the smallest route/adapter change with bounded inputs and stable safe errors. Keep raw provider-body verification and account/resource authorization in their correct order.
4. Use controlled request/domain/database dependencies to test malformed and denied input, duplicate/concurrent admission, uncertain completion and account transitions as relevant.
5. Run the smallest meaningful checks and required project checks. Return changed behavior, invariant/ownership, exact tests and any unverified provider or Apple-runtime boundary.

## Load the relevant guide

- [Runtime inventory and request boundaries](../../references/node-api/runtime-and-request-boundaries.md)
- [Mutation lifecycle, idempotency and stable errors](../../references/node-api/mutation-lifecycle-and-errors.md)
- [Behavioral backend tests and cross-client fixtures](../../references/node-api/backend-test-fixtures.md)

Finish with the concrete requested result, supporting evidence and material remaining limits. The [source index](../../research/sources/sources.jsonl) records the documentation and pinned implementation evidence; reference content does not supply task authorization.
