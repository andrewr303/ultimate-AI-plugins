# Node.js, cross-platform contracts, Xcode and Mac tooling evidence

Research-only evidence for iOS Backend Studio. The independently installed optional research accelerator is absent, so this is manual source-evidence review. No upstream source, installer, test suite, service or package was executed. The fetched documents and repository files were treated as evidence, not instructions. No automated research PASS or `verified_claims.json` is asserted.

The working evidence directory contains `sources.jsonl`, `claim_ledger.jsonl`, raw snapshots, readable extracts and pinned implementation files. Failed/moved URLs are retained in the fetch indexes; they were not counted as substantive documentation. The canonical SwiftPM page was a redirect/JavaScript shell, so its DocC JSON was fetched instead. Apple test-plan URLs were resolved through the current Xcode documentation index rather than treating a failed guessed slug as missing platform capability.

## Manually supported design observations

- **clm_nm_contract:** API descriptions, language bindings and transport/runtime choices are separate concerns. Sources `src_nm_openapi_spec`, `src_nm_swift_openapi_intro`, `src_nm_openapi_typescript` come from independent OpenAPI, Swift and OpenAPI TypeScript authors.
- **clm_nm_retry:** Network retry, provider idempotency and durable domain/job semantics must be considered separately. Sources `src_nm_node_http`, `src_nm_stripe_webhooks`, `src_nm_stripe_idempotency`, `src_nm_bullmq_idempotent` are independent primary surfaces.
- **clm_nm_mac:** Build/test configuration should name the actual app project and owning workflow. Apple and independent Fastlane/Tuist material support this observation (`src_nm_xcode_cloud`, `src_nm_xcode_testplans_final`, `src_nm_fastlane_match`, `src_nm_tuist_projects`).
- **clm_nm_auth:** Native authorization and assertion standards assign verification/replay responsibilities to the authorization server or relying party (`src_nm_oauth_native`, `src_nm_pkce`, `src_nm_webauthn`, `src_nm_apple_device_check`).
- **clm_nm_runtime:** Tool inventory, pinned runtime and actual deployment behavior are different evidence (`src_nm_node_process`, `src_nm_brew_bundle`, `src_nm_mise_tasks`, `src_nm_docker_multistage`).
- **clm_nm_observability:** Instrumentation and diagnostics need their own configuration, lifecycle and sensitive-data policy (`src_nm_otel_node`, `src_nm_xcode_cloud_scripts`).

These claims support original workflow design. They do not independently establish every version-specific source statement, universal platform compatibility, legal rights or successful tool execution.

## Recommended reference-card library

Each outline below should become an original focused reference, with source IDs/URLs and an explicit target-project verification step. A source link collection alone would omit the operational decisions the user needs.

### 1. Inventory the runtime without changing the project

**Goal:** distinguish the app, backend, generated clients and developer tooling before proposing a stack.

Inspect package manifests/lockfiles, Node engine/tool files, HTTP framework, deployment entrypoint, environment-name contract, Swift package graph, Xcode shared schemes and extension targets. Classify a Node tooling wrapper separately from an actual JavaScript application. Identify which commands are reads and which install, generate, migrate, sign or deploy. Keep unknown version/provider facts unknown.

Prefer the established runtime/package manager and deployment host. Document the minimum supported runtime from actual code/dependencies; do not substitute the current website's Node documentation version. Treat local SDK/tool presence as a prerequisite observation, not a successful app build. Preserve user configuration and use separate explicit app/backend roots in helpers.

**Failure checks:** missing lockfile, development and deployed Node mismatch, generated files owned by a different command, Swift package build mistaken for whole iOS app build, simulator artifact mistaken for device IPA.

**Sources:** `src_nm_node_process`, `src_nm_mise_tasks`, `src_nm_brew_bundle`, `src_nm_swift_package_json`, `src_nm_xcode_cloud`.

### 2. One HTTP contract, generated platform bindings

**Goal:** maintain the API once while retaining native Swift, TypeScript and optional Kotlin clients.

Choose the existing API description as the source of truth; do not run multiple code generators against competing hand-maintained definitions. Review operation identities, explicit statuses/content types, request/response bodies, null versus absent fields, dates/time zones, large identifiers/decimal values, authentication and pagination. Pin each generator/runtime/transport version and record generation commands as deterministic project tasks. Generate into a clearly owned location, then compile both producer and consumers.

Swift OpenAPI material separates generated declarations, runtime protocols and a selected client transport. OpenAPI TypeScript provides runtime-free types; it does not validate untrusted network bodies merely because the compiler accepts the caller. Kotlin options differ by selected library and serializer; do not assume every generator handles unknown enum values or date types equivalently.

**Acceptance:** shared golden payloads decode on every supported client; changed enum, optionality and status cases are exercised; a generated diff is reviewed before release.

**Sources:** `src_nm_openapi_spec`, `src_nm_swift_openapi_intro`, `src_nm_openapi_typescript`, `src_nm_kotlin_generator`.

### 3. Transport lifecycle and consistent error envelopes

**Goal:** expose predictable native app behavior without coupling the UI to a Node framework.

Define transport errors separately from rejected HTTP responses and domain errors. Preserve a stable safe code, correlation ID and recoverability hint while keeping stack traces, tokens and raw provider payloads server-side. Bound request/header/body durations and payload sizes. Configure reverse proxy limits and application limits together. Define owner-driven cancellation and finite timeouts in the Swift client; cancellation does not undo a mutation already committed remotely.

Keep generated API types at the transport seam and map to app/domain state rather than exposing raw response unions everywhere. Test delayed/out-of-order responses, disconnects during writes, malformed error bodies and account switches. Use actual provider runtime semantics; serverless and long-lived process shutdown have different guarantees.

**Sources:** `src_nm_node_http`, `src_nm_node_http2`, `src_nm_node_process`, `src_nm_openapi_spec`, `src_nm_swift_openapi_intro`.

### 4. Native authorization and token custody

**Goal:** integrate an existing identity provider while preserving a native public-client boundary.

Map issuer, audience, redirect routes, scopes and token ownership. Use the provider's supported authorization-code/PKCE flow and native external-user-agent integration; never treat an embedded client secret as confidential. Bind request/state/nonce/verifier to one authorization attempt, validate callback routing, and prevent a stale login response from replacing a newer session. Keep refresh coordination single-flight within the owning account/session boundary.

The server validates access tokens and authorizes the actual resource operation; a client login screen or decoded JWT is not authorization. Store only appropriate small credential material in platform-protected storage with deliberate access/lock behavior. Account switch/logout must invalidate in-flight work and isolate caches, widgets and push registrations.

**Acceptance:** wrong issuer/audience, replayed callback, expired/revoked token, simultaneous refresh, cancellation and logout while a request is pending.

**Sources:** `src_nm_oauth_bcp`, `src_nm_oauth_native`, `src_nm_pkce`, `src_nm_keychain_services`.

### 5. Passkeys and App Attest solve different problems

**Goal:** avoid replacing server authorization with a device-generated assertion.

WebAuthn credentials authenticate possession according to the relying party's registered credential and policy. App Attest helps a server assess an app-instance assertion. Neither by itself grants access to a user's arbitrary domain object. Use maintained verification libraries where appropriate; do not synthesize cryptographic verification from a short code fragment.

Issue and expire server challenges deliberately, bind them to the intended operation/session and reject replay. For WebAuthn, inspect expected relying-party/origin/type/challenge and authenticator verification policy. Keep actual native-platform response fixtures instead of assuming a browser-only origin representation. Signature counter anomalies need the current standard's risk handling; a simplistic “counter must always increase” assertion is not a universal passkey rule. For App Attest, verify the server-side attestation/assertion chain and app identity per current Apple documentation, with an explicit unsupported-device/availability policy.

**Sources:** `src_nm_webauthn`, `src_nm_apple_device_check`, `src_nm_oauth_native`.

### 6. Webhook ingress: authenticate bytes, persist receipt, process safely

**Goal:** accept asynchronous provider events without trusting delivery order or doing slow work before acknowledgement.

Preserve the exact raw request body required by the provider's signature verifier before JSON/body middleware transforms it. Bound size and verification time. Use the actual endpoint secret/key and documented tolerance/rotation behavior; never embed provider secrets in the iOS app. Validate the event type/schema and target account/object.

Make receipt persistence and deduplication explicit. A fast success response should mean the event is durably accepted for processing, not merely placed in ephemeral process memory. Process a supported event set with idempotent domain operations, reconcile authoritative provider state when ordering is uncertain, and retain safe identifiers for debugging. Do not use coarse event timestamps as a total ordering key.

**Acceptance:** duplicate event ID, semantically duplicated distinct events, out-of-order delivery, signature failure, crash after receipt/before acknowledgement and crash after mutation/before job acknowledgement.

**Sources:** `src_nm_stripe_webhooks`, `src_nm_stripe_idempotency`, `src_nm_bullmq_idempotent`, `src_nm_postgres_isolation`.

### 7. Domain idempotency for mobile retries and offline writes

**Goal:** let unreliable mobile networks retry safely without implying exactly-once transport.

Assign an operation identity before the client sends a mutating request and preserve it through reconnect, background execution and process restart as the product requires. Bind the server idempotency record to the authenticated principal, operation and relevant payload fingerprint. Return the existing result for a valid duplicate; reject key reuse for a different operation rather than silently executing it.

Define lifetime, concurrent in-progress handling and durable result storage from the app's business requirements. Provider-specific idempotency policies are not automatically the app's global policy. A database transaction/constraint can protect the domain mutation, but an external API call still needs a recovery/reconciliation design. Avoid sensitive user data inside externally visible keys.

**Acceptance:** concurrent duplicate requests, timeout after commit, key/payload mismatch, server restart, expired record, account switch and duplicate downstream webhook.

**Sources:** `src_nm_stripe_idempotency`, `src_nm_postgres_isolation`, `src_nm_bullmq_idempotent`, `src_nm_node_http`.

### 8. Concurrent edits, optimistic versions and transaction retries

**Goal:** preserve domain invariants when the same account writes from iOS, web and background workers.

Model the actual invariant in the database with appropriate constraints and transaction boundaries. Choose a version/ETag or conflict policy when user edits can be concurrent; last-writer-wins is a product choice, not a consequence to hide. Explain read snapshot behavior for the deployed database/isolation mode. Do not infer serializable behavior from a transaction wrapper.

Retry a complete eligible transaction when its isolation failure requires that, with a finite policy and safe external side effects. A partial statement retry may observe a different snapshot or duplicate a provider call. Test concurrent update, deletion, uniqueness collision, stale version and a worker racing a foreground request. Surface a useful conflict state to every platform instead of mapping all failures to a generic network retry.

**Sources:** `src_nm_postgres_isolation`, `src_nm_postgres_alter`, `src_nm_openapi_spec`, `src_nm_bullmq_idempotent`.

### 9. Expand/contract database changes across staggered app releases

**Goal:** support old installed iOS clients while deploying a new Node backend and schema.

Inventory deployed backend and client contract versions, database engine and migration tool major before selecting commands. Prefer additive compatible schema/API changes, deploy code that can handle both representations, backfill observably, then retire old behavior only after the actual support policy permits it. Make migration lock/scan duration and failed partial progress explicit.

Review production migration SQL or tool plan; keep development reset/drift-repair commands out of ordinary production deployment. Test a realistic prior schema/data fixture, repeated application, concurrent writers and rollback/recovery assumptions. A source revert does not revert customer data. Database backup existence is not proof of a restore; define and test the recovery procedure within authorized scope.

Current Prisma documentation has changed its migration model and commands relative to older guides. Preserve the installed project's supported workflow rather than writing one universal Prisma command into the skill.

**Sources:** `src_nm_postgres_alter`, `src_nm_postgres_isolation`, `src_nm_prisma_migrate`.

### 10. Durable outbox and small retryable jobs

**Goal:** synchronize domain commits and background work without losing work between a database write and queue publish.

Document what “accepted” and “completed” mean. For transactional domain work, consider a durable outbox/receipt in the same database transaction, then deliver to the selected existing job system. Keep jobs small enough to understand partial progress. Include operation and account identity, avoid raw secrets, and make job execution idempotent under redelivery.

Choose queue persistence, acknowledgement and recovery deliberately. Redis persistence modes have different durability/latency tradeoffs; an in-memory queue is not a durable acceptance guarantee. Bound retries/backoff, classify permanent errors and define dead-letter/reconciliation visibility. Do not add Redis/BullMQ to a simple app without a demonstrated requirement; an existing managed job service can implement the same boundary.

**Acceptance:** crash before enqueue, crash after external mutation, duplicate delivery, worker termination, persistence failure and poison payload.

**Sources:** `src_nm_bullmq_idempotent`, `src_nm_redis_persistence`, `src_nm_postgres_isolation`, `src_nm_stripe_webhooks`.

### 11. Node HTTP/2 provider transport for APNs

**Goal:** keep Apple push-specific policy separate from the reusable Node transport lifecycle.

Use current Apple provider documentation for authentication, topic/environment, push type, priority, expiry and payload constraints. Node HTTP/2 supplies sessions/streams; it does not supply Apple entitlement policy or app-user authorization. Keep provider signing material on the trusted backend. Scope device-token registrations to the correct app/environment/account and support token replacement and logout.

Handle per-stream responses, errors and GOAWAY separately from the whole connection. Manage connection reuse, concurrency and bounded reconnect/retry with actual delivery semantics. A provider acceptance response is not proof the user saw a notification or that an OS background handler ran. Reconcile stale tokens based on authoritative responses without treating the token as user identity.

**Acceptance:** refused stream, connection loss after write, invalid/expired auth, wrong topic/environment, duplicate event and user account transition. Coordinate the final card with the Apple-source APNs evidence arm.

**Sources:** `src_nm_node_http2`, `src_nm_node_process`; current Apple APNs sources from the separate platform-doc arm.

### 12. Trace the contract path without leaking client data

**Goal:** connect a Swift request, backend handler, database/job and provider callback using safe correlation.

Choose consistent request/operation identifiers and a documented propagation policy. Do not put access tokens, device tokens, signed URLs, personal content or full provider payloads in span names/attributes. Separate product analytics, operational metrics and diagnostic traces. Configure SDK/exporter lifecycle, sampling and retention according to actual services and user consent/product policy.

OpenTelemetry initialization order affects automatic instrumentation; avoid conflicting loaders and multiple SDK instances. Pin packages and inspect the actual framework/runtime integration. Test that a failed request, retried job and duplicate webhook remain distinguishable without inflating a business-success count. Stop exporters gracefully where the hosting lifecycle permits it, and disclose serverless flushing limitations.

**Sources:** `src_nm_otel_node`, `src_nm_node_process`, `src_nm_xcode_cloud_scripts`, `src_nm_stripe_webhooks`.

### 13. Provider-neutral backend deployment with compatible artifacts

**Goal:** support a normal deployable Node service while keeping hosting adapters optional.

Inspect whether the target is a long-lived server, serverless function or managed job runtime. Define port/listen contract, environment variable names, health/readiness behavior, reverse proxy/TLS termination, graceful shutdown and background work ownership. Build and test with the same pinned runtime/dependency graph used in deployment. Never infer that a container local pass proves a provider deployment or domain/TLS change succeeded.

Use multi-stage container builds where they fit, copying the necessary runtime output and production dependencies deliberately. Keep build credentials out of final layers and application code. Declare safe rollout and migration ordering, record the deployed revision, test a real configured health endpoint when authorized, and avoid treating a scheduled deploy request as completion.

**Sources:** `src_nm_docker_multistage`, `src_nm_node_http`, `src_nm_node_process`, `src_nm_prisma_migrate`.

### 14. Xcode contract generation and target-aware test plans

**Goal:** update the API binding once and verify the app plus each relevant extension target.

Identify ownership of the API description, generator configuration, generated Swift directory and target dependencies. Keep generation deterministic and inspect the diff; do not edit generated files as the permanent fix. Confirm app, widget and other extensions use the intended shared client/domain module without dragging app-only dependencies into extension execution.

Use existing shared schemes and test plans, selecting a fast contract/unit plan during local development and relevant target/integration/UI coverage before release. Record scheme/configuration/destination and result-bundle identity. A package-only Swift test does not prove the whole iOS product builds. Compare golden payload behavior on both Swift and Node clients, including old/new API compatibility.

**Sources:** `src_nm_swift_openapi_intro`, `src_nm_swift_package_json`, `src_nm_xcode_testplans_final`, `src_nm_xcode_results`, `src_nm_node_test`.

### 15. Xcode Cloud scripts and artifact handoff

**Goal:** make CI repeatable while keeping Apple signing and backend deployment as explicit lanes.

Inspect the product/scheme, Xcode/macOS build image, start conditions, selected actions and postactions. Use the project's existing CI ownership. Keep custom build scripts small, deterministic, bounded and failure-signaling; read them as code before execution. Scope artifacts and log retention and keep secret values out of output even when a CI service offers masking.

Coordinate a contract-generation check and backend compatibility fixtures with the Apple build. Preserve signed artifact identity and build number; do not infer that a backend deploy authorizes App Store submission or that a cloud build implies release. Separate cache restoration from dependency resolution and fail when a required prerequisite is unavailable.

**Sources:** `src_nm_xcode_cloud`, `src_nm_xcode_cloud_scripts`, `src_nm_xcode_results`, pinned Fastlane implementation/test files.

### 16. Fastlane signing and CI without routine credential mutation

**Goal:** reuse a configured Apple automation lane with a known identity and state.

Inspect Gemfile/lockfile, Fastfile and lane imports; these are executable Ruby configuration. Resolve actual team, bundle IDs, profile type, private-key availability and target. Preserve the existing credential storage model. The `match` documentation's readonly mode limits certificate/profile creation; it can still download/decrypt/install local signing material, so do not call it side-effect-free.

Separate build/test/archive/export from upload/distribution/submission. Read installed action options and Xcode help before applying examples from a snapshot. Record exact scheme/configuration/destination and build artifact identity. Do not revoke/repair all credentials or distribute new testers as generic troubleshooting. Link the lane's completion to observed resulting state.

**Sources:** `src_nm_fastlane_ci`, `src_nm_fastlane_match`, `fastlane/fastlane@a540df301c4ada0621cdb50358049734712f7ee7:fastlane/lib/fastlane/actions/xcodebuild.rb`, `...:fastlane/lib/fastlane/actions/run_tests.rb`, `...:fastlane/spec/actions_specs/xcodebuild_spec.rb`.

### 17. Generated Xcode projects: preserve the declared source of truth

**Goal:** lower project-file maintenance where the app already uses generation, without forcing migration.

Identify whether the project is hand-maintained, XcodeGen-owned, Tuist-owned or a Swift package. For generated projects, change the manifest/spec and regenerate through the pinned existing command; do not patch the produced project and pretend the fix will survive regeneration. Preserve custom settings, signing, targets, package dependencies and test schemes. Review generated diffs and build affected targets.

XcodeGen's inspected generator composes PBX project, workspace and scheme generation; Tuist's inspected service explicitly checks whether the configured project is generated or a Swift package. Those are evidence for respecting ownership, not reasons to introduce either tool to every app. Inspect cache/cloud behavior before enabling it, and keep its account and licensing requirements separate from a local generator.

**Sources:** `src_nm_tuist_projects`; pinned `yonaskolb/XcodeGen@783a19e863ff906e042d061aa0a1d569d3c52ffa:Sources/XcodeGenKit/ProjectGenerator.swift` and tests; `tuist/tuist@5c73f508f6367877751be4d730715e3a1ed82d8c:cli/Sources/TuistKit/Services/GenerateService.swift` and tests.

### 18. Mac tool inventory, runtime pins and local containers

**Goal:** make onboarding reproducible without silently changing an existing workstation.

Read a Brewfile as a tool inventory, then inspect what the proposed install would change. Homebrew Bundle explicitly does not provide a Brewfile lockfile and can upgrade packages. Use appropriate project runtime pinning/lockfiles for Node, Ruby and other tools, and choose the actual Xcode installation independently. A task runner can expose a common `check`/`contract`/`build` interface, but task dependencies may run concurrently; use an explicit ordered sequence when one action must finish first.

If local containers are required, reuse the selected engine/context. Colima startup manages a VM/runtime and Docker client prerequisites; do not automatically start/stop/resize the user's VM or switch contexts. Separate local database disposable state from customer/production data. Record where services listen and how to stop only the services the task created.

**Sources:** `src_nm_brew_bundle`, `src_nm_mise_tasks`, `src_nm_colima`, `src_nm_docker_multistage`, `src_nm_keychain_services`.

### 19. Optional Mac tool servers and MCP boundaries

**Goal:** use an existing tool server where available without inventing a connection or broad command permissions.

Discover the configured tool names/schema and actual toolchain. The inspected simulator build tool validates mutually exclusive project/workspace and simulator ID/name choices, then delegates to build execution. Preserve explicit target selection and error reporting rather than substituting a guessed device or framework version. Inspect result state: tool acceptance or queued work is not completed build success.

The current repository README discusses MobileBuildMCP branding and telemetry/privacy, despite the XcodeBuildMCP repository path. Verify the selected release/CLI and privacy controls before setup. Do not register an MCP server, enable telemetry, launch a paid/remote service or run an unknown package installer merely because a reference mentions it. Native Xcode CLI remains a valid lane when no tool server exists.

**Sources:** `getsentry/XcodeBuildMCP@2998ac77ebbca59544e88a27f34bfb830db9d924:src/mcp/tools/simulator/build_sim.ts`, its test file and README; `src_nm_xcode_results`.

### 20. Failure runbook and safe operational handoff

**Goal:** make cross-platform backend incidents diagnosable without routine destructive repair.

Classify the failure first: client decode/version mismatch, expired auth, stale resource conflict, transport disconnect, queue delay, migration failure, provider rejection or Apple lifecycle limitation. Preserve safe correlation identifiers and exact deployed app/backend/schema versions. Reproduce against controlled fixtures before running broad cleanup or rotating credentials.

For deployable Node processes, understand signal and shutdown behavior for the actual runtime/host. Drain accepted work or checkpoint it, stop accepting new work intentionally, and bound termination. Define backups and restore/reconciliation procedures for data and job state. A passing health check does not prove migration integrity, push delivery or correct app UI. End with verified state and the smallest pending check, not an unearned “all platforms work.”

**Sources:** `src_nm_node_process`, `src_nm_node_http`, `src_nm_postgres_isolation`, `src_nm_redis_persistence`, `src_nm_xcode_results`.

## Pinned Mac implementation comparison

| Requirement | Source evidence | Observed fit | Gap and original choice |
| --- | --- | --- | --- |
| Existing CI and signing lanes | `fastlane/fastlane@a540df301c4ada0621cdb50358049734712f7ee7:fastlane/lib/fastlane/actions/xcodebuild.rb`, `run_tests.rb`, action specs | Explicit project/workspace/scheme/configuration/result-bundle options and scan delegation | Installed action/Xcode versions and actual lane code still determine execution; preserve existing automation |
| Declarative project generation | `yonaskolb/XcodeGen@783a19e863ff906e042d061aa0a1d569d3c52ffa:Sources/XcodeGenKit/ProjectGenerator.swift`, `Docs/ProjectSpec.md`, tests | Generator composes native Xcode project/workspace/scheme outputs | Do not rewrite hand-maintained projects or make generated-file edits the source of truth |
| Generated project orchestration | `tuist/tuist@5c73f508f6367877751be4d730715e3a1ed82d8c:cli/Sources/TuistKit/Services/GenerateService.swift`, command/tests | Project-type assertion, generation/cache/metadata orchestration | Optional existing workflow; cloud/cache/licensing are separate decisions |
| Tool-driven simulator builds | `getsentry/XcodeBuildMCP@2998ac77ebbca59544e88a27f34bfb830db9d924:src/mcp/tools/simulator/build_sim.ts`, tests and manifest | Typed mutually exclusive target/destination inputs | Do not fabricate availability, setup command or completed build; inspect actual tool/server release and privacy |

## Unresolved

- Exact runtime/generator/SDK/CLI version requirements must be verified in the consuming project. Live Node API pages identified a particular current documentation version; that is not the user's deployment default. SwiftPM docs also carry newer compiler/build-system statements that are not adopted as universal project assumptions.
- Current Prisma documentation describes a migration interface that differs from older Prisma guides. This source review does not establish the correct command for an uninspected installed major; use its actual supported contract.
- Actual repository license files were read, but there is no blanket rights clearance. Fastlane, XcodeGen and XcodeBuildMCP license texts contain MIT terms. Tuist's root notice states mixed licensing and is internally inconsistent about the `kura/` subdirectory: the opening summary calls it MPL, while its later specific section calls it AGPL. Do not vendor that monorepo or assert all components are MIT. Original workflow ideas and source links avoid relying on a broad legal inference.
- WebAuthn verification review is scoped to registration/assertion and signature-counter considerations. It is not a full conformance/security assessment of the entire specification or any implementation. Native Apple passkey fixtures must be checked against actual platform APIs and the chosen relying-party library.
- Neither examples, tests nor CI source presence establishes successful execution. No Apple toolchain, local VM/container, provider service, database migration or backend application was run.
- Some official URLs moved or failed. Failure indexes preserve those observations; replacement source URLs were inspected where found. Website errors do not establish that a capability is unavailable.

## Refuted

- A generated static type is not evidence that an untrusted network response was runtime-validated.
- A Brewfile is not a complete exact-version lockfile.
- A provider acceptance response is not proof of app/device-visible delivery.
- A readonly signing action is not necessarily free of local Keychain/profile installation side effects.
- Existence of tests or a recently modified repository is not proof the consuming app or workflow passes.

These are rejected synthesis assumptions, with the relevant source boundaries documented above; they are not substitute test results or legal conclusions.
