# Provider-neutral Node deployment and rollout evidence

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Resolve the hosting contract

Inspect the existing deployment target and how it runs the Node service: a long-lived process, container, serverless function, edge runtime or managed job. Record runtime limits, listen/port convention, TLS/proxy ownership, health/readiness contract, file persistence, background-work policy and secret bindings. Provider-neutral guidance means portable decisions and adapters, not identical provider APIs.

Preserve the current host/framework and package manager unless the task changes them. Never provision an account, paid service, database or queue solely to match a sample. Prepare a concrete configuration/artifact and identify exact missing authority or product facts before asking. Already authorized deployment work can continue after its real dependencies are ready; do not invent recurring confirmation gates.

## Reproducible artifact and configuration

Pin the deployed runtime and dependency graph through the actual project/host controls. Build the artifact from a known source revision with a clear start command and environment variable names. Multi-stage container builds can separate build tools from runtime output, but they do not automatically remove secrets or establish the application works. Inspect copied files/dependencies, runtime architecture and required native modules.

Keep secrets in the hosting system's supported binding mechanism, not source, Docker layers, client bundles or public build logs. Document which config is portable and which is a provider adapter. An iOS app must not carry backend signing keys merely because both are developed in one repository. Use a stable configured API origin and actual environment separation rather than hardcoded developer machine URLs.

## Rollout sequence

1. Establish desired endpoint, account/environment, current deployed revision and supported client/API/schema compatibility window.
2. Run relevant contract, backend and native-consumer checks. Separate local artifact tests from external provider checks; missing Xcode does not justify fabricating a native pass.
3. Review migration and job compatibility before rolling backend code. Old installed mobile clients and queued jobs may require overlap support.
4. Produce the intended artifact/configuration and inspect a supported plan/dry run where available. Preserve existing deployment hooks only after reading their behavior.
5. Execute authorized release steps and observe the actual provider result. Record artifact/revision/environment identity; a submitted build/deploy request is not success.
6. Test the configured health/readiness endpoint and relevant application path. Keep recovery/rollback criteria tied to real errors and data state, not only process liveness.

## Failure matrix

| Failure | Evidence needed |
| --- | --- |
| Container runs locally, provider fails | Actual runtime/architecture/start/port/config contract |
| Health endpoint passes, app fails | Auth/domain/dependency path and client contract behavior |
| Deploy timeout | Current remote state and receipt before issuing another deployment |
| New server rejects old clients | Compatibility window and changed field/status/auth semantics |
| Startup requires an unsafe schema reset | Migration ownership/plan, not generic redeploy |
| Process termination loses work | Durable acceptance, queue/outbox checkpoint and shutdown policy |

## Verification and handoff

Record source/artifact digest, runtime, selected environment, tests and furthest observed state. Test a controlled failure and recovery path where the rollout requirement warrants it. A source revert may not undo a database change or external side effect; describe data recovery separately. Do not claim provider, Xcode, APNs or App Store execution from local Node tests.

The resulting workflow should expose a few stable project commands and a small provider-specific layer. It should reduce setup duplication without concealing the service's actual availability, durability, permissions and billing boundaries.

## Sources and applicability

- [HTTP | Node.js v26.12.1 Documentation](https://nodejs.org/api/http.html) — `src_nm_node_http`.
- [Process | Node.js v26.12.1 Documentation](https://nodejs.org/api/process.html) — `src_nm_node_process`.
- [Multi-stage builds | Docker Docs](https://docs.docker.com/build/building/multi-stage/) — `src_nm_docker_multistage`.
- [Applying a migration in Prisma ORM | Prisma Documentation](https://www.prisma.io/docs/orm/prisma-migrate/workflows/development-and-production) — `src_nm_prisma_migrate`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
