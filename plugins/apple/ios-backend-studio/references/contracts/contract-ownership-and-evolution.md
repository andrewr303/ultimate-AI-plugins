# Contract ownership and compatible API evolution

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Choose one authority

Find the actual API description, route schemas and generated clients. Decide which artifact owns the wire contract and which outputs are derived. Do not introduce an independent OpenAPI file that competes with a framework-generated description unless the task explicitly changes ownership. If a code-first service emits the contract, review the emitted description and generator configuration as part of the change.

Inventory supported mobile, widget, web and backend versions. Mobile clients can remain installed long after a server deployment, and extension snapshots may carry an older representation. “The latest app passed” is not a compatibility policy. Define the supported window, retirement signal and behavior of old requests before removing fields or changing semantics.

## Review the wire rather than language similarity

Give operations stable identities and explicit HTTP statuses, content types, request/response schemas and auth requirements. Decide absent versus null, default behavior, unknown values, numeric precision, identifiers and time representation intentionally. OpenAPI schema dialect and generator support must match; a newer schema feature may be valid in the specification while unsupported by one selected generator.

Generated TypeScript types do not check live data at runtime. Generated Swift clients still need a compatible runtime and transport plus app-specific authorization/error mapping. Kotlin library/serializer options can change decoding behavior. Avoid promising that a shared schema alone makes every platform behave identically.

## Change sequence

1. Capture representative supported requests/responses and the current generated outputs. Record generator/runtime versions and command ownership.
2. Express the proposed new behavior in the authority artifact. Review requiredness, enum changes, default behavior, authentication and error semantics as potentially breaking changes.
3. Prefer additive compatible server behavior when older clients must keep working. For renamed or changed data, define an overlap period and observable migration rather than silently repurposing a field.
4. Generate all affected language bindings through pinned project tasks. Review source changes and compile each consuming target; do not hand-edit derived files as the permanent fix.
5. Run shared positive/negative payload fixtures through runtime validation and each supported client decoder. Include old clients against new server and relevant new-client fallback against older server if rollout permits that pairing.
6. Deploy with explicit contract/version evidence and a recovery plan. Removing compatibility requires actual adoption/support-policy evidence, not a date guessed from a source guide.

## Compatibility review matrix

| Proposed change | Question before approval |
| --- | --- |
| Add a response field | Do supported decoders tolerate unknown fields and size growth? |
| Add an enum value | Is fallback behavior real for each chosen generator/serializer? |
| Make a field required | Can older producers, stored jobs or snapshots omit it? |
| Change null/default semantics | Do clients distinguish absence from an intentional cleared value? |
| Change pagination order/cursor | Can a resumed client duplicate, skip or reorder data? |
| Change auth scope/error status | Does the client misclassify it as retryable network failure? |

## Verification and handoff

Keep schema linting, generator checks, runtime validation and domain authorization as separate evidence. A custom checker should state its subset and unresolved constructs; it must not label an unsupported reference/dialect a full conformance pass. Record the exact contract digest/revision used by each generated output and fixture suite.

Return the before/after behavior, support window, source of truth, generated diff, tests and pending platform checks. The aim is less duplicated management, with explicit boundaries rather than a new abstraction layer for every platform.

## Sources and applicability

- [OpenAPI Specification v3.1.1](https://spec.openapis.org/oas/v3.1.1.html) — `src_nm_openapi_spec`.
- [Introducing Swift OpenAPI Generator | Swift.org](https://www.swift.org/blog/introducing-swift-openapi-generator/) — `src_nm_swift_openapi_intro`.
- [openapi-typescript | OpenAPI TypeScript](https://openapi-ts.dev/introduction) — `src_nm_openapi_typescript`.
- [Documentation for the kotlin Generator | OpenAPI Generator](https://openapi-generator.tech/docs/generators/kotlin/) — `src_nm_kotlin_generator`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
