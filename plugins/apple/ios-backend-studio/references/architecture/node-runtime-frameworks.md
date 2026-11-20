# Choose a Node lane from actual constraints

## Inspect before selecting

Read the service's package manager lockfile, module format, runtime version, framework version, entrypoints, middleware order and hosting model. Determine whether it is a long-running Node process, a short-lived function, an edge runtime or a mixed deployment. A framework with adapters for several runtimes does not make their filesystem, sockets, process lifecycle or background execution contracts equivalent.

Preserve an installed framework and database when they meet the task. For a greenfield choice, compare only the capabilities the product needs: request validation, response serialization, streaming, authentication integration, observability, startup/shutdown behavior, testing and deployment compatibility. Do not pick a framework because its repository has more stars or its README advertises a benchmark.

## Useful choices and their boundaries

| Existing or justified lane | What to inspect | Boundary to keep explicit |
| --- | --- | --- |
| Fastify | Route schemas, plugins, hooks, encapsulation and serializer configuration | Compiled schemas are application code; validation may coerce/remove/default input |
| Hono | Runtime adapter, request validators, context bindings and fetch behavior | Inferred TypeScript client types are not a native Swift schema |
| Express/Nest or another established stack | Current middleware/DI, error pipeline and test conventions | Add contract checks without rewriting the application around another framework |
| Node core HTTP | Routing/body limits, timeouts, lifecycle and error handling the app owns | A small example server is not a production framework or durable service |

Choose an interface first, then prove the selected runtime can implement it. For example, a background job that must survive process termination needs durable admission and processing. Starting an unawaited promise after an HTTP response is not a hosting-independent work queue.

## Keep validation, authorization and serialization distinct

Validate the request's allowed content type, body size and shape before expensive work. Runtime validation should reject or normalize according to the published contract; test whether coercion, defaults or removal of extra properties changes what the native app intended to send. An ID that parses correctly still needs account/entity authorization.

Treat compiled schema definitions as reviewed application code. Do not accept arbitrary tenant-provided schemas into a compiler that evaluates generated JavaScript. Keep database authorization and other asynchronous policy checks in the framework's appropriate post-validation phase, with finite dependency timeouts. Source examples that compile a schema or call a database are not a reason to combine both in the initial parser.

Define a response contract for each relevant status and content type. Return a stable machine-readable error code, safe message and correlation identifier; do not expose stack traces, SQL errors, tokens or internal provider responses. A successful transport with a non-success HTTP status is still an application outcome the Swift client must handle. Empty responses need an explicit contract as well.

## Runtime and dependency management

Keep the service's chosen supported Node release and package manager pinned through its normal project convention. Resolve native modules, ESM/CommonJS, minimum runtime requirements and lockfile behavior before upgrading. A current repository main can be a prerelease, while another package in the same organization remains stable. A monorepo's latest release may belong to a different subpackage.

Use the deployment platform's documented readiness, shutdown, health and request limits. Verify what happens to open requests and jobs on termination. Keep readiness distinct from liveness when the platform supports both. Avoid making a health endpoint depend on an expensive full-system check or allowing it to leak configuration.

## Acceptance cases

Exercise malformed JSON, an unsupported media type, oversized bodies, absent versus null fields, wrong scalar types, auth failure, domain denial and dependency timeout. Confirm that errors pass through the intended safe envelope. For coercion, compare the raw request with the handler's value and verify the documented behavior deliberately.

Test cancellation and disconnect behavior at the actual runtime boundary. A client dropping a connection does not necessarily abort a domain transaction. If streaming is required, test backpressure, disconnect, partial output and the chosen provider's buffering behavior. Use injected transports and explicit readiness signals in tests rather than arbitrary sleeps.

## Evidence and version cautions

Source IDs `src_backend_repo_049`, `src_backend_repo_052` and `src_backend_repo_055` support the inspected runtime-validation concerns. Read the pinned [Fastify validation implementation](https://github.com/fastify/fastify/blob/5df959f3af698823dd582f1c3661f3e80df0b5da/lib/validation.js), [Fastify validation/serialization guide](https://github.com/fastify/fastify/blob/5df959f3af698823dd582f1c3661f3e80df0b5da/docs/Reference/Validation-and-Serialization.md), and [Hono validator](https://github.com/honojs/hono/blob/bac5c4a8bcd76b165428ce757e1185753c7935bd/src/validator/validator.ts). `src_nm_node_http` identifies the [Node HTTP documentation](https://nodejs.org/api/http.html). Verify exact resolved versions through the [source catalog](../../research/sources/sources.jsonl); the source review did not execute these frameworks or endorse their main branches as production defaults.
