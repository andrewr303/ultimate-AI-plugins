# Project inventory without changing the platform

## Establish scope before scanning

Start from the requested repositories and affected feature. Read their instructions and current changes, then inspect the shortest set of files that identifies the app, service and contract. Do not recursively inspect home directories, dependency trees, credential files or unrelated repositories. A repository map is useful when it answers who owns a concrete behavior; it is not an excuse to collect private source or environment dumps.

Record paths and evidence for the following inventory:

| Area | Evidence to inspect |
| --- | --- |
| Native app | Project/workspace, target membership, shared schemes, app/extension entrypoints, resolved dependency files |
| Compiler and platform | Declared language mode, concurrency flags, deployment target and CI-selected toolchain; distinguish candidates from resolved settings |
| Node service | Package manifest, chosen lockfile, runtime constraints, start/build/test tasks and actual handler entrypoints |
| Other clients | Their contract consumer, transport, release/version constraints and shared fixture location |
| Wire authority | OpenAPI/schema/router source, generated-output policy, generation task and checked-in derived artifacts |
| Domain data | Store/migration owner, entity/tenant association, outbox or job tables and transaction boundary |
| Deployment | Environment/configuration references, build image, artifact selection and existing release workflow |
| Native surfaces | Widget/intent/Live Activity/background targets, app groups, entitlements and shared snapshot readers/writers |

Read a dynamic configuration file as source first. Importing a JavaScript config, invoking a package task or resolving a Swift manifest can execute code or initiate downloads. An initial inventory should not run installation hooks, generate a new project or provision a service merely to learn its name.

## Trace one request

Follow a representative operation from the native call site through the client transport and server handler to authorization and durable state. Record how errors and identifiers cross that path. If a web client consumes the same contract, inspect its actual decoder/call site rather than assuming matching TypeScript names imply matching wire behavior.

Inspect an extension independently. Identify its target dependencies, auth context, data container, snapshot format and fallback when the main app has not run. Do not assume it can instantiate the main app's service graph or access server credentials. Mark a missing path as unknown, not as an implicit opportunity to add a provider or framework.

## Distinguish declarations from resolved facts

Text build settings and package runtime ranges are inventory candidates. The selected build, actual process and deployment runtime establish effective behavior. A lockfile pins dependencies but does not prove they were installed or compiled. A configured account alias is not evidence of access; use the host's intended authentication without reading or printing its secret value.

For tool presence, use ordinary version/help calls only when the executable is already available and the call is appropriate to the task. Start with the repository's documented workflow. Do not silently substitute a different package manager, default branch, global CLI or new SDK. Resolve ambiguity only when it changes the implementation or an external target.

## Output and failure handling

Return a compact table of owner, path, observed value, confidence and unresolved check. Include the accepted behavior and next code seam. If tooling is absent, continue source/portable checks and identify the actual pending native/provider gate. If an imported task fails, inspect its implementation and error before retrying or changing environment settings.

Sources: src_nm_node_process — [Node process/runtime information](https://nodejs.org/api/process.html); src_nm_openapi_spec — [OpenAPI authority](https://spec.openapis.org/oas/v3.1.1.html); src_nm_xcode_cloud_scripts — [Xcode Cloud build-script context](https://developer.apple.com/tutorials/data/documentation/xcode/writing-custom-build-scripts.json); src_backend_apple_025 — [App-group configuration](https://developer.apple.com/documentation/xcode/configuring-app-groups).
