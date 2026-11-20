# Reference library

Choose the specialist that owns the task, then read the focused cards below. Each card records inputs, decisions, implementation/recovery steps, verification and source citations. Check current applicability using the [operating contract](operating-contract.md) and [source index](source-index.md).

## Skill entrypoints

- [backend-apns](../skills/backend-apns/SKILL.md): Use when implementing or debugging a Node.js APNs provider, device registration, token/topic/environment scope, notification jobs or delivery recovery for an iOS app. Keep Live Activity state specifics in backend-live-activities; do not use for generic web push, app-store submission or unrequested live sends.
- [backend-app-intents](../skills/backend-app-intents/SKILL.md): Use when exposing existing app/backend actions or entities through App Intents, Siri, Shortcuts or optional Apple Intelligence schemas. Preserve stable saved-shortcut contracts and server authorization; do not invoke for a generic chatbot, cosmetic Siri button design or unsupported schema adoption.
- [backend-architecture](../skills/backend-architecture/SKILL.md): Use to design or evolve the boundary between a native iOS app, Node.js service and other clients, including runtime selection, domain ownership and compatible releases. Preserve the existing stack; do not turn a local endpoint fix into a framework migration or introduce a hosted service without a requirement.
- [backend-auth](../skills/backend-auth/SKILL.md): Use when integrating Node.js authentication/session/resource authorization with native iOS, widgets or App Intents, including Sign in with Apple verification and Keychain scope. Preserve the existing provider; do not confuse Apple token roles, invent privacy declarations or substitute local device unlock for backend permission.
- [backend-background](../skills/backend-background/SKILL.md): Use when designing bounded iOS background refresh/processing, background URLSession transfers or offline reconciliation with a Node service, including an existing CloudKit sync boundary. Do not create indefinite phone workers, promise OS scheduling or introduce a second authoritative data plane without a requirement.
- [backend-contracts](../skills/backend-contracts/SKILL.md): Use when defining or evolving a shared HTTP/OpenAPI contract, generating Swift/TypeScript/optional Kotlin clients, or diagnosing cross-platform wire drift. Keep runtime validation, transport, authorization and database invariants separate. Do not introduce generated clients where the existing contract needs no change.
- [backend-cross-platform-qa](../skills/backend-cross-platform-qa/SKILL.md): Use to verify shared iOS/Node/web API behavior, lifecycle and failure handling, old-client compatibility, or cross-platform release gates. Do not treat generated types, mock success, simulator discovery or plugin package checks as end-to-end application proof.
- [backend-data](../skills/backend-data/SKILL.md): Use for authoritative Node-side schemas, tenant ownership, transactions, migrations, pagination and cache consistency consumed by iOS or other clients. Preserve the installed database/ORM; do not replace a native persistence engine or run destructive production repairs as a default.
- [backend-deploy](../skills/backend-deploy/SKILL.md): Use when preparing or executing an authorized Node.js backend rollout, database compatibility change, durable job/outbox workflow or recovery plan for independently upgraded iOS/web clients. Do not infer production mutation or a new provider/service from a preparation request; code rollback does not reverse customer data.
- [backend-discovery](../skills/backend-discovery/SKILL.md): Use to inspect an unfamiliar native app/Node.js/multi-client project, resolve runtime and dependency constraints, or prepare a provider-neutral implementation plan. Do not install frameworks, provision services, print credentials or turn a narrow endpoint fix into a platform migration.
- [backend-live-activities](../skills/backend-live-activities/SKILL.md): Use when integrating ActivityKit lifecycle, Live Activity ContentState, rotating activity tokens or server APNs start/update/end jobs with a Node.js backend. Do not treat Live Activity UI as a network client, a widget timeline or a durable backend operation.
- [backend-mac-tooling](../skills/backend-mac-tooling/SKILL.md): Use when aligning Mac/Xcode and Node developer environments, runtime/task pins, generated project workflows, optional local containers, signing tools or configured MCP build tools. Do not install services, switch global toolchains, enable telemetry or stop user processes solely because a reference mentions them.
- [backend-media](../skills/backend-media/SKILL.md): Use for authorized media upload/download sessions, signed storage capabilities, validation/processing, native transfer recovery and asset ownership against a Node backend. Preserve the selected storage provider; do not add image generation, public hosting, a media service or broad bucket cleanup without a task need.
- [backend-node-api](../skills/backend-node-api/SKILL.md): Use when implementing or diagnosing the Node.js HTTP API consumed by native iOS, widgets, web or other clients: request validation, resource authorization, mutation outcomes, retries and route tests. Do not replace an established framework, provision a host, or treat static types as runtime validation.
- [backend-observability](../skills/backend-observability/SKILL.md): Use when instrumenting or diagnosing the iOS-to-Node request/job/provider path, selecting safe correlation and error signals, controlling telemetry privacy/lifecycle, or explaining a release regression. Do not provision exporters, enable external collection or infer correctness from absent logs or static checks.
- [backend-offline-sync](../skills/backend-offline-sync/SKILL.md): Use to implement or debug native offline writes, durable outboxes, replay, conflicts, cursors and app/extension snapshots against a Node backend. Preserve the existing persistence/sync provider; do not promise exact background scheduling, silently discard pending edits or add a managed sync service by default.
- [backend-reliability](../skills/backend-reliability/SKILL.md): Use for durable idempotency, duplicate writes, retry budgets, timeouts, cancellation, background jobs and recovery across iOS clients and Node replicas. Distinguish admission from completion; do not call an in-memory demo, queue job ID or client cancellation a production exactly-once guarantee.
- [backend-webhooks](../skills/backend-webhooks/SKILL.md): Use for authenticated incoming provider webhooks, raw-body signature handling, replay resistance, durable event inboxes, ordering and safe recovery in a Node backend. Follow the actual provider protocol; do not treat arbitrary HMAC, decoded JWTs or a successful delivery response as proof of an authorized completed domain action.
- [backend-widgets](../skills/backend-widgets/SKILL.md): Use when connecting WidgetKit timelines, snapshots, interactive widgets, shared app-group projections or widget deep links to a Node.js backend. Do not make widgets poll continuously, replace ordinary app UI or treat a reload request as guaranteed realtime delivery.
- [backend-xcode](../skills/backend-xcode/SKILL.md): Use when connecting generated backend clients and shared modules to Xcode app/extension targets, schemes, test plans or Xcode Cloud. Preserve actual project ownership and distinguish build-host/compiler requirements from generated-code deployment support. Do not claim Linux checks establish Apple runtime behavior.
- [ios-backend-studio](../skills/ios-backend-studio/SKILL.md): Use for end-to-end native iOS and Node.js backend integration, an unfamiliar multi-client project, or choosing the right specialist. Preserve existing frameworks and providers. Do not activate for unrelated frontend styling, an Android-only task, or generic Apple policy submission work.

## Focused guides

### Apns

- [APNs delivery, recovery and product state](apns/delivery-and-recovery.md)
- [Node.js APNs provider boundary and operational policy](apns/provider-transport.md)
- [Notification device registration and account-safe delivery](apns/registration-and-account-scope.md)

### App Intents

- [Siri, Apple Intelligence and controlled entity exposure](app-intents/entities-and-discovery.md)
- [Intent execution, authentication and cancellation](app-intents/execution-and-authorization.md)
- [App Intents, App Shortcuts and a shared Node command layer](app-intents/typed-domain-commands.md)

### Architecture

- [Evolve independently released clients safely](architecture/evolution-and-environments.md)
- [Choose a Node lane from actual constraints](architecture/node-runtime-frameworks.md)
- [Map the system before changing it](architecture/system-map-and-boundaries.md)

### Auth

- [Sign in with Apple: identity verification and application sessions](auth/apple-identity-verification.md)
- [Credentials usable by the right app or extension only](auth/device-and-extension-credentials.md)
- [Application sessions, account changes and authorization](auth/sessions-and-authorization.md)

### Background

- [Bounded background work and recoverable server reconciliation](background/bounded-reconciliation.md)
- [CloudKit sync and a Node backend without accidental dual ownership](background/cloudkit-and-node-ownership.md)
- [Background uploads/downloads and durable file state](background/file-transfer-lifecycle.md)

### Contracts

- [Contract ownership and compatible API evolution](contracts/contract-ownership-and-evolution.md)
- [Cross-platform wire fixtures and breaking-change checks](contracts/cross-platform-wire-fixtures.md)
- [Swift, TypeScript and optional Kotlin generation pipeline](contracts/swift-web-client-generation.md)

### Cross Platform Qa

- [Lifecycle and failure tests that expose real integration defects](cross-platform-qa/lifecycle-failure-matrix.md)
- [Release gates tied to the candidate artifact](cross-platform-qa/release-gates-and-evidence.md)
- [Shared wire fixtures across independently typed clients](cross-platform-qa/shared-wire-fixtures.md)

### Data

- [Authoritative schemas and tenant ownership](data/authoritative-schema-and-tenancy.md)
- [Migrations that tolerate old clients and overlapping servers](data/migrations-and-rollouts.md)
- [Transactions, stable reads and cache scope](data/transactions-pagination-and-caches.md)

### Deploy

- [Database migrations, staged clients and recovery](deploy/database-rollouts-and-recovery.md)
- [Durable jobs, outbox delivery and graceful termination](deploy/durable-jobs-and-shutdown.md)
- [Provider-neutral Node deployment and rollout evidence](deploy/provider-neutral-deployment.md)

### Discovery

- [Project inventory without changing the platform](discovery/project-inventory.md)
- [A provider-neutral plan with concrete owners](discovery/provider-neutral-plan.md)
- [Runtime capability evidence](discovery/runtime-capabilities.md)

### Live Activities

- [Live Activity freshness, end states and recovery](live-activities/freshness-and-recovery.md)
- [ActivityKit APNs tokens, payloads and update ordering](live-activities/push-contract-and-tokens.md)
- [Live Activity state, lifecycle and stale content](live-activities/state-and-lifecycle.md)

### Mac Tooling

- [Mac environment inventory, runtime pins and local services](mac-tooling/environment-and-tool-inventory.md)
- [Generated project ownership and reproducible dependency inputs](mac-tooling/generated-projects-and-locks.md)
- [Optional Mac tool servers, signing tools and trust boundaries](mac-tooling/optional-mcp-and-credential-tools.md)

### Media

- [Native media transfer without losing ownership or local files](media/native-transfer-and-lifecycle.md)
- [Authorize an upload session, then verify the owned object](media/upload-sessions-and-capabilities.md)
- [Keep untrusted media quarantined until the required checks pass](media/validation-and-processing.md)

### Node Api

- [Behavioral backend tests and cross-client fixtures](node-api/backend-test-fixtures.md)
- [Mutation lifecycle, idempotency and stable errors](node-api/mutation-lifecycle-and-errors.md)
- [Runtime inventory and request boundaries](node-api/runtime-and-request-boundaries.md)

### Observability

- [Incident triage, release evidence and recovery handoff](observability/incident-triage-and-release-evidence.md)
- [Telemetry privacy, sampling and exporter lifecycle](observability/privacy-sampling-and-exporters.md)
- [Cross-platform signals and safe correlation](observability/signals-and-correlation.md)

### Offline Sync

- [Conflicts, tombstones and resynchronization](offline-sync/conflicts-and-convergence.md)
- [Extension snapshots and optional synchronization adapters](offline-sync/extension-snapshots-and-sync-adapters.md)
- [A durable local outbox with an explicit acknowledgement contract](offline-sync/local-outbox-protocol.md)

### Reliability

- [Durable idempotency is a domain and storage contract](reliability/durable-idempotency.md)
- [Durable jobs, bounded concurrency and recovery](reliability/jobs-backpressure-and-recovery.md)
- [Bound retries without multiplying intent](reliability/retries-timeouts-and-cancellation.md)

### Studio

- [Intake that leads to an implementable outcome](studio/intake-and-acceptance.md)
- [Ownership across the app, extensions and server](studio/ownership-and-handoffs.md)
- [Deliver a representative vertical slice](studio/vertical-slice-delivery.md)

### Webhooks

- [Durable receipt is separate from domain processing](webhooks/inbox-processing-and-ordering.md)
- [Version changes, rotation and recovery for webhook consumers](webhooks/provider-change-and-operations.md)
- [Verify the actual signature over the actual signed input](webhooks/signatures-and-raw-bodies.md)

### Widgets

- [Interactive widget commands and acknowledgment reconciliation](widgets/actions-and-reconciliation.md)
- [Deep links and iPhone widgets shown on Mac](widgets/shared-state-and-routing.md)
- [Widget snapshots, timelines and backend read projections](widgets/snapshots-and-refresh.md)

### Xcode

- [Schemes, test plans and trustworthy result evidence](xcode/schemes-test-plans-and-results.md)
- [Xcode targets, Swift packages and generated clients](xcode/targets-packages-and-generation.md)
- [Xcode Cloud, build scripts and backend artifact handoff](xcode/xcode-cloud-and-ci-handoff.md)

## Provenance and evidence

- [Source and claim records](../research/outputs/design-decision.md)
- [Validation](../docs/validation.md)
- [Native host evidence](../docs/native-host-verification.json)
