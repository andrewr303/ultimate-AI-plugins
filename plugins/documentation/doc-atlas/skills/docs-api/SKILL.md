---
name: docs-api
description: "Use when producing or improving API, SDK, CLI, or configuration reference from inspected schemas and source, with accurate examples and version-aware renderer integration."
---

# API and developer reference

Create reference that lets an integrator make a valid call, understand its result, and recover from failure.
Route a complete docs build through [Repo Docs](../repo-docs/SKILL.md).
Apply the shared [evidence and safety rules](../repo-docs/references/evidence-and-safety.md).
Use [the reference worksheets](references/templates.md) for planning and review.

## Select the source of truth

1. Inspect repository instructions and determine which API/product version is in scope.
2. Find OpenAPI, AsyncAPI, GraphQL, protobuf, JSON Schema, route declarations, or public SDK exports.
3. For a CLI, inspect command registration, option definitions, parser behavior, and help snapshots.
4. For configuration, inspect the parser/schema, validation, defaults, precedence, and examples.
5. Read representative integration tests and examples to understand real input/output behavior.
6. Identify generated files and their owning generator; inspect how the repository rebuilds them.
7. Compare schema and implementation for important mismatches; record each mismatch explicitly.
8. Keep the existing versioning, base path, naming, and reference-generation conventions.
9. Record the exact files or schema locations supporting each documented contract.
10. Identify material unknowns before writing reference prose.

A route name is not proof of authorization behavior, response shape, or error semantics.
Do not silently repair a schema to match an assumption about the implementation.
When sources disagree, document the discrepancy and repair only the authorized owning source.
Do not describe a planned endpoint, optional integration, or private symbol as a public supported contract.

## Choose a rendering adapter when needed

| Existing source or stack | Suitable starting point | Verify before changing it |
| --- | --- | --- |
| OpenAPI site | Existing Redoc, Scalar, Swagger UI, or framework integration | Installed version, schema support, base URL, security settings |
| TypeScript SDK | Existing TypeDoc or code-derived generator | Entry points, exports, compiler config, visibility and versions |
| Python package | Existing Sphinx/autodoc or project generator | Import side effects, environment, public objects and cross-references |
| .NET project | Existing DocFX or project generator | Target SDK, metadata inputs and build conventions |
| CLI or config | Source-derived Markdown/reference pages | Actual parser, aliases, defaults and precedence |

Preserve a functioning renderer before introducing a new one.
Check the repository's installed version and current official documentation before using adapter-specific syntax.
Do not paste a remembered configuration for another major version.
For a new renderer, choose the smallest compatible integration and state its dependency/build consequences.
Do not add hosted API tooling, analytics, a service account, or a publishing destination by default.

## Build an accurate contract

For each operation or public entry point, document only fields supported by evidence:

- Purpose and a concrete situation in which to use it.
- Name, method/path or symbol, version, and stability/deprecation status when established.
- Required authentication mechanism and authorization scope if actually specified.
- Inputs: location, name, type, required status, accepted values, defaults, and constraints.
- Success result: status/type, field meanings, optionality, and a realistic example.
- Failure results: known status/type, trigger, meaningful error fields, and recovery action.
- Pagination: real cursor/offset contract, ordering guarantees, and termination condition.
- Rate limits and retry behavior only where source, tests, or authoritative docs define them.
- Idempotency keys, replay behavior, timeouts, and partial failure semantics only when known.
- Compatibility notes and links to related concepts or tutorials.

Distinguish an omitted value from null, an empty collection, and a server-selected default.
Explain units and timestamp format where the source establishes them.
Avoid claiming atomicity, exactly-once processing, unlimited pagination, or safe retries without evidence.
Do not infer that all failures can be retried merely because the transport is HTTP.
Do not invent a standard error envelope for APIs whose operations return different shapes.

## Produce useful examples

1. Choose the smallest realistic operation that teaches the contract.
2. Match the documented version and actual SDK/package import path.
3. Use environment-variable references for credentials, never real token values.
4. Use clearly fictional non-sensitive example identifiers and data; keep them valid for the schema.
5. Show content types, required headers, and parameter encoding when relevant.
6. For shell examples, quote variables correctly and avoid a command that leaks a token in output.
7. Keep request and response examples consistent with one another.
8. Explain response fields that matter to the next decision.
9. Add a failure example only when the failure and recovery are known.
10. Prefer local fixture validation or mock tests over a live production request.

Do not send requests to a live API automatically, including an interactive renderer's Try It control.
Network access is not authorization to transmit credentials or create remote records.
Inspect existing examples rather than invoking undocumented remote endpoints to discover behavior.
If live verification is explicitly authorized, use the specified environment and report its limited scope.

## Integrate without drift

- Edit the source schema or generator template when the project declares the page generated.
- Keep generated output in sync using the repository's established command when safe to run.
- Separate generated mechanical contract fields from authored concepts and operational guidance.
- Keep one canonical definition for a parameter or model; cross-link repeated uses.
- Preserve stable operation anchors, version routes, redirects, and external inbound links.
- Mark deprecated operations with the actual replacement and policy only when established.
- Keep translated reference pages aligned or record which languages need follow-up.
- Preserve access controls; publishing internal schemas is outside an ordinary docs edit.

## Verify and deliver

Validate schema syntax and examples with available local tooling appropriate to the actual format.
Build the reference with the existing generator and inspect warnings and unresolved cross-references.
Check rendered navigation, code wrapping, copy controls, model tables, and narrow-screen behavior.
Check authentication descriptions, pagination termination, nullable fields, and known errors against source.
Confirm generated examples contain no credentials, real personal data, fabricated fields, or unfinished markers.
Check local links and anchors, then use the shared [quality bar](../repo-docs/references/quality-bar.md).
Report whether checks were schema-only, source-reviewed, mock-executed, built, visually reviewed, or live-tested.
Deliver the changed source, necessary generated output, and exact remaining contract discrepancies.
Do not call the entire API verified because one example or one schema validation succeeded.
