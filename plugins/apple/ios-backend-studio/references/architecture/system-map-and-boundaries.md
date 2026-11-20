# Map the system before changing it

## Inputs and the first useful artifact

Inspect the native app's targets and extensions, the Node service's package and lockfile, API descriptions, persistence configuration, deployment manifests and the changed behavior. Record which facts are observed and which remain unknown. An `expo` configuration key, a tooling-only package.json or a generated Swift file does not establish the application's runtime architecture.

Produce a small map with these columns: component, runtime/process, account scope, state it owns, interface it consumes, secrets it can access and verification method. Include the main app, widgets, App Intents, any web client, the HTTP service, workers and external providers that actually exist. A diagram helps when a request crosses several boundaries; a table is enough for a small feature.

The Node service should own authoritative domain authorization and server-side secrets. The native app owns its presentation and local interaction state. An extension consumes an intentionally limited snapshot or performs a bounded authorized action; it is not another permanently running backend worker. Describe where cached data can be stale and how the product communicates that state.

## Choose one authority for each contract

| Concern | Authority to identify | Common mistake |
| --- | --- | --- |
| HTTP payload shape | Reviewed API description or equivalent tested contract | Treat TypeScript inference as a Swift wire contract |
| Account/entity access | Server authorization and stored ownership | Trust an account ID supplied by a public client |
| Business mutation | Authoritative database transaction | Let the client declare that a purchase or upload is complete |
| Event delivery | Durable event identity and processing state | Use a request log ID as duplicate protection |
| Client snapshots | Versioned local persistence boundary | Share mutable in-process objects across app/extension processes |
| Release compatibility | Supported client/server contract policy | Assume mobile clients update when the server deploys |

An authority is not necessarily a new service or repository. Keep an existing monolith when its boundaries are adequate. A small module with an injected transport can be easier to manage than separate services with distributed transactions. Split deployment or storage only for a concrete ownership, scaling, isolation or lifecycle need.

## Implement a vertical slice

Start with one operation that exercises the real boundary: authenticated request, validation, domain authorization, transaction and typed response. Define its failure envelope and client fallback alongside success. Keep transport parsing, domain policy and storage operations separate enough to test without requiring a framework for every layer.

For an OpenAPI lane, decide which reviewed description is authoritative, how server validation is derived or checked, and how Swift/web clients are regenerated. Pin compatible generator/runtime/transport releases. Keep generated source out of hand-maintained domain modules, and decide whether builds regenerate it or CI verifies committed output. Generated types do not establish that a live response, authorization check or database migration is correct.

For an existing hand-written client, do not replace it solely to introduce a generator. Compare maintenance cost, supported wire features, custom authentication, streaming, error handling and the size of a safe first slice. Preserve stable public interfaces while introducing a test seam.

## Failure cases to design explicitly

- The main app is signed in while a widget snapshot belongs to a prior account. Scope and invalidate the snapshot; never let its stored account ID grant server access.
- A new backend field appears before an older mobile client updates. Test the older client's actual decoder and behavior; do not assume every language handles unknown or absent fields identically.
- A request is cancelled after the server commits. Reconcile the authoritative operation result instead of reporting that cancellation rolled back the mutation.
- An auth refresh succeeds after sign-out or an account switch. Bind results to the session generation and discard obsolete updates.
- A deployment's HTTP route succeeds but its worker or schema is incompatible. Treat API acceptance, durable admission and completed business work as distinct states.

## Verification and handoff

Exercise the slice through the actual runtime where available, plus dependency-controlled tests for invalid payload, denied access, duplicate operation and unavailable dependency. Record the app target, service runtime and selected environment. If Apple tools are absent, identify the pending Xcode/device path without calling portable checks an iOS runtime pass.

Before finishing, check that every new abstraction has an owner and an observable reason to exist. Explain what changed, what remains authoritative, how client/server compatibility was verified and which service or platform assumptions still need confirmation.

## Evidence and version cautions

The original design draws on `clm_backend_shared_contract`, `clm_backend_transport_seam` and `clm_backend_auth_seam`. Sources include `src_backend_repo_034`, the [Swift generator build plugin](https://github.com/apple/swift-openapi-generator/blob/75962579db43e88440bbad021c74570f0955d1fd/Plugins/OpenAPIGenerator/plugin.swift), and `src_backend_repo_060`, the [TypeScript fetch factory](https://github.com/openapi-ts/openapi-typescript/blob/d46a319ae2efab30e135ba9b223a3cffd1a67eab/packages/openapi-fetch/src/index.js). Exact records are in the [source catalog](../../research/sources/sources.jsonl). Source main branches and examples do not set the consuming app's toolchain or architecture.
