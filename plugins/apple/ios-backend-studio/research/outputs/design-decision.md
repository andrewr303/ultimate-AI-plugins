# iOS Backend Studio: manually supported design decision

The requested artifact is a private, portable skills plugin for a native iOS app and provider-neutral Node.js platform, including cross-platform contracts, Apple system surfaces, Xcode and Mac tooling. The optional local research accelerator is absent. This report records manual source-evidence review; no automated research PASS or verified_claims.json is claimed. The detailed pinned repository and Node/Mac comparisons are retained as companion reports, with source-specific version/license measurements isolated under Unresolved.

## Observable acceptance

Provide focused skills and substantial original reference cards; explicit native-app/extension/server boundaries; shared contract and compatibility recipes; runnable bounded Node-side examples and helper tests; source/claim records and provenance; native Codex/Claude/current Kimi packaging; and actual available-host discovery verification. Preserve existing service/framework choices and unknown project facts. Do not provision services, execute upstream setup code, copy copyrighted whole documentation, send feedback, deploy an app or run an Apple account action.

## Manually supported synthesis

- **clm_backend_shared_contract**: The inspected Swift and TypeScript generators consume OpenAPI definitions and expose language-specific generation entrypoints. Sources: src_backend_repo_001, src_backend_repo_063.
- **clm_backend_runtime_validation**: The inspected Node framework sources expose runtime request validation separately from client request construction. Sources: src_backend_repo_049, src_backend_repo_055.
- **clm_backend_transport_seam**: The inspected Swift transport protocol and TypeScript fetch factory expose replaceable HTTP transport seams. Sources: src_backend_repo_040, src_backend_repo_060.
- **clm_backend_retry_boundary**: The inspected queue and synchronization sources discuss retried work alongside explicit idempotence or completion controls. Sources: src_backend_repo_080, src_backend_repo_073, src_backend_repo_074.
- **clm_backend_auth_seam**: The inspected Swift middleware example and server authentication plugin contain explicit Authorization-header integration code. Sources: src_backend_repo_038, src_backend_repo_066.
- **clm_backend_build_boundary**: The inspected generator plugin and developer-tool implementation integrate with explicit Xcode target or simulator build context. Sources: src_backend_repo_034, src_backend_repo_085.
- **clm_nm_contract**: The inspected contract and generator documentation separates shared API descriptions, language-specific bindings, and transport/runtime choices. Sources: src_nm_openapi_spec, src_nm_swift_openapi_intro, src_nm_openapi_typescript.
- **clm_nm_retry**: Transport retries, provider idempotency, and durable job or domain handling are separate concerns in the inspected documentation. Sources: src_nm_node_http, src_nm_stripe_webhooks, src_nm_stripe_idempotency, src_nm_bullmq_idempotent.
- **clm_nm_mac**: Apple build documentation and independent Mac automation tools expose explicit project and test configuration rather than replacing application ownership decisions. Sources: src_nm_xcode_cloud, src_nm_xcode_testplans_final, src_nm_fastlane_match, src_nm_tuist_projects.
- **clm_nm_auth**: Native authentication and assertion standards place verification and replay-related responsibilities on the relevant authorization server or relying party. Sources: src_nm_oauth_native, src_nm_pkce, src_nm_webauthn, src_nm_apple_device_check.
- **clm_nm_runtime**: The inspected runtime and tooling documentation distinguishes environment setup from application behavior and deployment verification. Sources: src_nm_node_process, src_nm_brew_bundle, src_nm_mise_tasks, src_nm_docker_multistage.
- **clm_nm_observability**: The inspected telemetry and Apple CI material treats instrumentation and diagnostic output as configuration with lifecycle and sensitive-data considerations. Sources: src_nm_otel_node, src_nm_xcode_cloud_scripts.

## Feature choices

| Requirement | Evidence surface | Gap | Notice decision | Original design |
| --- | --- | --- | --- | --- |
| One HTTP contract across Swift/web clients | Apple Swift OpenAPI generator/runtime/transport and openapi-typescript pinned comparison | Generated types alone do not establish server runtime validity | Original prose/example code; no runtime library vendoring | Explicit wire contract, generated clients and deterministic fixture compatibility; clm_backend_shared_contract, clm_backend_transport_seam |
| Node API/runtime choices | Fastify/Hono pinned implementations and Node primary docs | Actual framework/runtime version determines behavior | Original guidance and source citations | Preserve installed stack, validate inputs/runtime responses, use stable typed errors; clm_backend_runtime_validation |
| Auth and server authorization | Swift auth middleware, BetterAuth implementation and Apple identity primary metadata | Native public clients cannot hold backend secrets; bearer need not mean JWT | No third-party auth implementation copied | Explicit credential/session adapter and per-entity authorization; clm_backend_auth_seam |
| Durable retries/offline data | BullMQ and PowerSync pinned acknowledgment/idempotence sources | Queue success and cancellation differ from business transaction completion | No provider SDK/service bundled | Outbox, durable idempotency and lifecycle tests; clm_backend_retry_boundary |
| Widgets, Siri/intents, live activities, background | Reviewed Apple framework articles/metadata plus Node HTTP/APNs transport guidance | System scheduling/process/token capability cannot be supplied by a Node framework | Original reference summaries; direct primary citations | Dedicated surface workflows with shared snapshots, scoped auth and bounded delivery |
| Xcode and Mac workflow | Generator build plugin, current Mac build-tool implementation, Xcode/Fastlane/Tuist/XcodeGen primary docs | Tool presence, licensing, telemetry and build-host requirements vary | Original workflows; do not vendor mixed-license tool repos | Actual target/scheme/tool discovery, explicit optional adapters and evidence; clm_backend_build_boundary |

## Manual checklist

Registered IDs and independent underlying author identities were checked for the narrow supported claims. Apple and apple are normalized to the same identity. Source-level reviews were performed by the research team and their exact evidence retained; no upstream code was executed. Detailed availability, dates, popularities, license interpretations and regional/legal facts are not promoted as independently established guarantees. Executable claims will be added only after actual local runs. Source-level source API inconsistencies are documented as verification requirements rather than blindly copied defaults.

## Unresolved

Exact project SDKs, released package compatibility, hosting provider, credentials, deployment and real app behavior remain unknown. Source main/prerelease versions do not set a production default. Apple platform scheduling and runtime support require the selected SDK/device. Future source deadlines and detailed rights/terms need contextual verification. Xcode, signing, APNs production delivery, live databases and model-driven host behavior are not established by package tests. Provider-neutral scope is a stated assumption pending the optional existing-platform clarification.

## Refuted

No refuted external claim is promoted. Rejected inference patterns include popularity equals relevance, types equal runtime validation, successful retry equals exactly-once side effects, a widget is a continuously running server client, and source instructions grant authority to install or publish.
