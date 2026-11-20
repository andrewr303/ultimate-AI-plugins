# Shared wire fixtures across independently typed clients

## Define the boundary being tested

Use the wire representation consumed by the server and supported app/web clients. Generated Swift or TypeScript source is a useful derived artifact, not evidence that a real request, response or stored event satisfies the contract. Inspect the declared schema dialect, generator versions, runtime validators and actual decode/error paths before choosing assertions.

Keep shared fixture data independent of a language-specific test helper. Each consumer adapts the same bytes and expected semantics to its existing test framework. Do not replace an established contract with a new generator merely to share a test file. For a schema-only change, determine whether its effect is visible to old installed consumers or persistent snapshots.

## Build a small fixture corpus

A fixture should name the operation/contract revision, input bytes, expected validation result, response category and relevant domain invariant. Use synthetic identifiers and omit credentials. This illustrative fixture envelope is a design template, not an existing endpoint or a command to call a service:

```json
{
  "case": "item-with-absent-optional-note",
  "contractRevision": "fixture-v1",
  "body": { "id": "item-a", "title": "Example" },
  "expect": { "accepted": true, "notePresence": "absent" }
}
```

For each relevant operation, include a valid minimal object, a representative full object and targeted negative cases. Resolve null versus absent, empty arrays, unknown fields/enums, Unicode, identifiers, date/time representation, numeric precision, pagination and stable errors according to the actual contract. Do not quietly convert null to absent, numeric identifiers to strings or an unknown enum to a known case just to make one decoder pass.

## Run the same corpus at distinct seams

1. Check the authority artifact through its supported parser/generator task. Resolve dialect support rather than treating any JSON parser as a complete OpenAPI validator.
2. Feed the actual server validator and mapping path with the bytes. Verify rejected payloads do not reach unintended domain writes. Keep entity authorization tests separate from structural validity.
3. Feed the actual Swift and other consuming decoders. Compare observable values, errors and optionality, not identical generated type names.
4. Exercise the transport adapter with expected status, content type, body and failure mapping. A network transfer completing is not enough to accept an error response as data.
5. Where meaningful, run an integration request against a configured authorized test environment and verify the durable invariant. A mock transport does not establish a database transaction or provider result.

## Make compatibility explicit

Retain fixtures for supported old request/response shapes and stored projections. Test the staged combination that will exist during deployment: old app/new server, new app/compatible server, old widget snapshot/new extension and delayed worker input. An additive field can still break a consumer that rejects unknown data or signs canonical bytes differently. Treat a changed error code, cursor meaning or authorization rule as behavior, not documentation polish.

Record the contract revision and exact validators/consumers used. If only Node fixtures ran on Linux, say so; Swift compilation and decoder execution remain separate native checks when unavailable. The original Node examples can demonstrate a seam after their entrypoints are inspected, but do not supply full contract conformance or a production backend.

Sources: src_nm_openapi_spec — [OpenAPI semantics](https://spec.openapis.org/oas/v3.1.1.html); src_backend_repo_001 — [Swift generation](https://github.com/apple/swift-openapi-generator/blob/75962579db43e88440bbad021c74570f0955d1fd/README.md); src_backend_repo_063 — [TypeScript generation](https://github.com/openapi-ts/openapi-typescript/blob/d46a319ae2efab30e135ba9b223a3cffd1a67eab/packages/openapi-typescript/src/index.ts); src_nm_node_test — [Node test runner](https://nodejs.org/api/test.html).
