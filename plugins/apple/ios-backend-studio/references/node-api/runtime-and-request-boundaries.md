# Runtime inventory and request boundaries

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Inputs that change the implementation

Identify the backend root, actual entrypoint, framework and middleware order, package manager and lockfile, pinned Node runtime, deployment process and proxy/gateway. Separately identify the Swift app, generated client, widgets/extensions and any web client. A package.json used for an iOS build wrapper does not establish a JavaScript application. Preserve the existing stack unless the task needs a deliberate migration.

Read installed version/help and resolved dependencies before copying API examples. The live Node documentation inspected during research described a particular current documentation release; it does not set the runtime required by the user's host. Compiler support, Node runtime support, hosting limits and the iOS deployment target are separate constraints. Record unknowns rather than substituting a remembered latest version.

## Choose the boundary deliberately

Keep transport parsing, runtime validation, account/resource authorization and domain work recognizable in the code. A framework route type or generated TypeScript signature does not validate an attacker-controlled HTTP body. Likewise, a decoded token is not permission to operate on an arbitrary object ID. Prefer existing project validation and authorization mechanisms rather than introducing another framework to satisfy a guide.

Set request/header/body size and duration limits according to actual clients and proxy behavior. Node HTTP, HTTP/2, reverse proxies and serverless gateways expose different knobs. Inspect compressed input and streaming behavior as well as the final JSON size. Do not assume a reverse proxy is present or that its limits protect direct/internal routes. Return a consistent safe error without reflecting private request content.

## Implementation sequence

1. Trace one existing request from network entry through parser, validation, authorization, domain operation and response. Name which layer owns each failure.
2. Define success statuses, content types, body schema, domain error codes and a safe correlation identifier in the shared API contract. Check old-client expectations before changing them.
3. Implement the smallest route or adapter in the established framework. Preserve middleware ordering, especially raw-byte webhook verification and authentication context.
4. Bound CPU-heavy parsing/decoding and expensive downstream work. An async function is not evidence that synchronous work leaves the event loop; measure the actual hotspot before adding worker infrastructure.
5. Make server/proxy timeout behavior and client cancellation distinct. A disconnected client does not automatically reverse a completed transaction or cancel a provider request.
6. Keep connection/session lifecycle and shutdown policy appropriate to the hosting model. Do not add a background daemon or long-lived in-memory job queue to a function runtime that cannot support it.

## Failure matrix

| Condition | Required observation |
| --- | --- |
| Malformed body or wrong content type | Finite rejection through the public error contract; no stack/secret reflection |
| Oversized or slowly arriving input | Selected proxy/application limit fires without unbounded resource retention |
| Valid identity, wrong account/resource | Domain authorization denies the operation |
| Client disconnect after a write | Server records authoritative outcome and permits reconciliation |
| Dependency timeout | Error remains distinguishable from validation/conflict/auth failures |
| Graceful shutdown | New work stops according to policy; accepted durable work is not silently lost |

## Verification and handoff

Exercise the actual route boundary with controlled transport/domain dependencies. Include malformed JSON, oversized body, missing/wrong auth, a deliberately slow dependency and a disconnect after the mutation begins. A unit test that bypasses all middleware cannot establish parser or authorization ordering. Keep production identifiers and tokens out of fixtures and logs.

Report backend/app roots, runtime and framework versions, the ownership map, changed contract behavior and exact checks. Distinguish a localhost route test, a provider deployment health check and an iOS UI outcome. Retain only the bounded diagnostic output needed to explain a failure; tool installation and dependency resolution are not test results.

## Sources and applicability

- [HTTP | Node.js v26.12.1 Documentation](https://nodejs.org/api/http.html) — `src_nm_node_http`.
- [HTTP/2 | Node.js v26.12.1 Documentation](https://nodejs.org/api/http2.html) — `src_nm_node_http2`.
- [Process | Node.js v26.12.1 Documentation](https://nodejs.org/api/process.html) — `src_nm_node_process`.
- [Security Best Practices | Node.js Learn](https://nodejs.org/en/learn/getting-started/security-best-practices) — `src_nm_node_security`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
