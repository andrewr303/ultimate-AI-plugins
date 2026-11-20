---
name: backend-cross-platform-qa
description: "Use to verify shared iOS/Node/web API behavior, lifecycle and failure handling, old-client compatibility, or cross-platform release gates. Do not treat generated types, mock success, simulator discovery or plugin package checks as end-to-end application proof."
---

# Verify the same contract across execution surfaces

First read the [operating contract](../../references/operating-contract.md).

1. Define user-visible acceptance and the actual supported app, extension, web and server versions. Resolve the authoritative contract and the selected build/runtime configurations.
2. Build [shared wire fixtures](../../references/cross-platform-qa/shared-wire-fixtures.md) and run them through real server validation and consuming decoders. Separate schema, transport, domain authorization and persistence checks.
3. Exercise the relevant [lifecycle failure matrix](../../references/cross-platform-qa/lifecycle-failure-matrix.md) with controlled dependencies, readiness and clocks. Verify state and authoritative side effects after cancellation, duplicates, expired auth, account switching and process interruption.
4. Apply [release gates and evidence](../../references/cross-platform-qa/release-gates-and-evidence.md) to the exact candidate artifacts. Preserve compatibility with independently upgraded clients and decide schema/rollback sequencing deliberately.
5. Report observed results by execution surface, failure cases, commands and artifact identity. Route defects to the owning specialist and finish authorized repairs; keep unrelated work intact.

Use the original [Node contract examples](../../examples/node-contract-kit) when relevant to the requested seam, after reading their entrypoints. They are bounded examples, not an installed backend or full OpenAPI implementation. Local portable checks can run without Apple tools; Xcode, extension entitlements, real APNs and physical-device behavior need the appropriate environment. See the [source registry](../../research/sources/sources.jsonl) for evidence provenance.
