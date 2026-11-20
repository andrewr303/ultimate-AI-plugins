# Cross-platform wire fixtures and breaking-change checks

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Define an executable wire agreement

Collect synthetic request/response examples from the actual API contract, not private production logs. Make each fixture state whether it should be accepted, rejected or preserved as unknown on each supported client. Include the operation/status/content type and applicable contract revision. Keep fixtures small enough to review and deterministic enough to run on Node, Swift and optional other consumers.

Cross-platform consistency does not mean coercing every language into its default JSON behavior. Decide whether identifiers are opaque strings, whether large integer/decimal values need a lossless representation, which timestamps/time-zone offsets are accepted, and how missing differs from null. Test these choices directly. Do not infer that a JSON Schema format label performs runtime parsing in every selected validator/generator.

## Fixture catalogue

Cover normal payloads plus boundary examples: empty collections; optional fields absent; explicit null where legal; unknown fields; unknown enum/discriminator variants; malformed content; unsafe numeric precision; date offsets/fractional seconds; Unicode and right-to-left text; pagination start/terminal/expired cursors; stable error responses; expired auth; and an old supported payload. For uploads, include declared versus actual media type, size and interrupted transfer behavior without embedding private media.

Use a shared semantic expectation rather than comparing every generated-language object's textual dump. A fixture may require a lossless decoded identifier, a deliberate unknown case or a clear rejection. Keep documented platform differences visible. A Kotlin option that adds an enum fallback is not proof every serializer actually uses it.

## Change-check sequence

1. Tie each operation fixture set to the authoritative API document. Record its revision/digest alongside generated client versions.
2. Validate fixture syntax/schema using the project's actual runtime validator and supported schema dialect. Mark unsupported constructs unresolved rather than silently passing them.
3. Feed positive and negative fixtures through the real backend parser/serializer and client decoder, including transport status/content handling.
4. Run supported old-client/new-server combinations and the rollback/partial-rollout combinations the deployment plan permits.
5. Compare public semantic outcomes. Assert exact safe error codes and necessary headers, not incidental internal helper ordering or volatile timestamps.
6. Review a schema/client/fixture diff together. If a fixture changes, explain the intended behavior change; do not update snapshots merely to hide a regression.

## Failure cases

| Unexpected result | Action |
| --- | --- |
| Number silently rounded | Change the wire representation or explicitly limit the domain; test every consumer |
| Absent field becomes a destructive default | Repair mapping/requiredness and protect the existing stored state |
| New enum crashes one client | Preserve compatible server output or implement a verified fallback before rollout |
| Cursor resumes with duplicates/skips | Review ordering/tie-breakers/snapshot policy, not just page size |
| Static checker passes malformed runtime payload | Identify the untested boundary and add a real runtime assertion |
| Fixture contains private data | Replace it with synthetic data and inspect any persisted artifact exposure |

## Evidence and handoff

Report which languages/runtimes actually executed the fixture set, the exact supported versions and failures. Node tests on Linux do not establish a Swift/WidgetKit build or UI behavior. When the Apple environment is unavailable, retain ready-to-run fixture inputs and the precise Xcode target/test-plan prerequisite without fabricating a pass.

Breaking-change checks are guardrails with declared scope, not a substitute for product compatibility decisions. Keep one reviewed fixture authority and platform adapters thin enough that adding a new client does not require rebuilding the backend around its language defaults.

## Sources and applicability

- [OpenAPI Specification v3.1.1](https://spec.openapis.org/oas/v3.1.1.html) — `src_nm_openapi_spec`.
- [openapi-typescript | OpenAPI TypeScript](https://openapi-ts.dev/introduction) — `src_nm_openapi_typescript`.
- [Documentation for the kotlin Generator | OpenAPI Generator](https://openapi-generator.tech/docs/generators/kotlin/) — `src_nm_kotlin_generator`.
- [Test runner | Node.js v26.12.1 Documentation](https://nodejs.org/api/test.html) — `src_nm_node_test`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
