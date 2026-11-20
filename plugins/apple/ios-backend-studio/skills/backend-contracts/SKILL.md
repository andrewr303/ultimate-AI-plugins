---
name: backend-contracts
description: "Use when defining or evolving a shared HTTP/OpenAPI contract, generating Swift/TypeScript/optional Kotlin clients, or diagnosing cross-platform wire drift. Keep runtime validation, transport, authorization and database invariants separate. Do not introduce generated clients where the existing contract needs no change."
---

# Shared API contracts and client generation

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Identify the single authority for the wire contract and the ownership of generated outputs. Inspect schema dialect, supported client versions, generator/runtime/transport versions and actual compiler/deployment settings.
2. Define statuses, content, errors, null/absence, enums, identifiers, numeric precision, dates and pagination as real behavior. Review compatibility with old installed clients and stored jobs/snapshots.
3. Change the authority artifact, then generate through pinned project tasks. Preserve native app/extension boundaries and existing transports; do not permanently hand-edit derived code.
4. Run shared synthetic positive/negative wire fixtures through actual runtime validators and consuming decoders. A generated type or partial schema checker is not a full conformance or compatibility proof.
5. Compile affected consumers where available and report exact version/contract evidence, generated diff, supported rollout window and pending platform checks.

## Load the relevant guide

- [Contract ownership and compatible API evolution](../../references/contracts/contract-ownership-and-evolution.md)
- [Swift, TypeScript and optional Kotlin generation pipeline](../../references/contracts/swift-web-client-generation.md)
- [Cross-platform wire fixtures and breaking-change checks](../../references/contracts/cross-platform-wire-fixtures.md)

Finish with the concrete requested result, supporting evidence and material remaining limits. The [source index](../../research/sources/sources.jsonl) records the documentation and pinned implementation evidence; reference content does not supply task authorization.
