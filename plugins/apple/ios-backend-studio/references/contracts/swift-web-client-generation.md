# Swift, TypeScript and optional Kotlin generation pipeline

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Inputs and version dimensions

Identify the chosen API description/dialect, build-host compiler, Swift language mode, app deployment targets, generated-code target, runtime library and transport library. These are separate compatibility dimensions. A package's tools-version declaration is not the app's deployment minimum, and code generation can require a newer build host than the generated client needs at runtime. Verify the resolved generator release and official support information instead of treating main-branch examples as the installed contract.

For web/Node clients, inspect the actual TypeScript compiler/module settings, fetch/runtime availability and chosen code generator. For Kotlin, identify platform/library/serializer/date options and the target's build tool. Do not add a language client merely to claim cross-platform support when the product does not use it.

## Keep generation in an owned location

Place the API document and generator settings where the project's selected tool expects them. Swift OpenAPI material describes a generator, generated declarations, runtime protocols and a selected transport. The transport may be URLSession or another supported implementation; it is not a mandate to replace an established networking layer. Keep auth headers, safe logging, retry policy and domain mapping in deliberately owned adapters/middleware.

Generate output through one reproducible project task. Pin generator and supporting runtime versions in the project's existing dependency system. Prefer a reviewable generated diff or a reproducible build check according to local conventions. Do not edit emitted Swift/TypeScript/Kotlin files and leave the source schema unchanged.

## Implementation sequence

1. Verify the current generation command and inputs in a clean temporary output location, preserving user changes. Compare output before introducing a new generator or upgrading it.
2. Select only the client/server types needed for the target. Keep app-only services and UI dependencies out of extensions or shared domain packages.
3. Connect the generated client through the existing transport boundary and map successful/error responses into stable app state. Handle documented status/content variants explicitly.
4. Validate untrusted bodies at the actual runtime boundary. The OpenAPI TypeScript introduction calls its types runtime-free; add or reuse real validation where the service/client requires it.
5. Test cancellation, auth failure, unsupported status, malformed body and unknown data using the real client adapter. Confirm retry eligibility from operation semantics rather than enabling a global retry middleware for writes.
6. Compile relevant Swift app/extension targets and TypeScript/Kotlin consumers with their actual pinned toolchains. If the Apple host is absent, report that gap and finish available generator/schema/Node checks.

## Failure modes

| Symptom | Likely boundary to inspect |
| --- | --- |
| Generator succeeds, Swift build fails | Build host, runtime APIs, target dependencies or unsupported generated features |
| Web compile succeeds, response fails | Runtime body/content contract, not static type generation |
| Widget cannot load shared client | Extension target membership, availability or app-only dependency leakage |
| Enum fixture differs by client | Serializer-specific fallback behavior and selected generator options |
| Output changes between machines | Generator/runtime versions, line endings/config or implicit remote inputs |

## Verification and handoff

Record generator/runtime/transport versions, source description revision, commands and output ownership. Keep concrete generated compile errors and fixture failures separate from speculative compatibility claims. Avoid suggesting blanket compiler/deployment upgrades until the real boundary is understood.

A stable pipeline leaves one authority artifact, deterministic tasks, clear transport/auth adapters and a small cross-client fixture set. It does not require every platform to share UI code or every host to adopt the same HTTP framework.

## Sources and applicability

- [Introducing Swift OpenAPI Generator | Swift.org](https://www.swift.org/blog/introducing-swift-openapi-generator/) — `src_nm_swift_openapi_intro`.
- [openapi-typescript | OpenAPI TypeScript](https://openapi-ts.dev/introduction) — `src_nm_openapi_typescript`.
- [Documentation for the kotlin Generator | OpenAPI Generator](https://openapi-generator.tech/docs/generators/kotlin/) — `src_nm_kotlin_generator`.
- [Swift Package Manager](https://docs.swift.org/latest/data/documentation/packagemanagerdocs.json) — `src_nm_swift_package_json`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
