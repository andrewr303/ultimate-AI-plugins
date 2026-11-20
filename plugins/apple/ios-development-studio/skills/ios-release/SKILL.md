---
name: ios-release
description: "Use for iOS release preparation, artifact upload, TestFlight distribution, review submission, status recovery and release orchestration. Keep prepare-only requests local/read-only remotely; do not infer tester invitations, review submission or public release from an upload request."
---

# Prepare and execute an iOS release

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Resolve the user’s requested endpoint: prepared artifacts, uploaded/processed build, selected beta groups, review submission or public release. Track these as distinct states. Preserve existing task authorization and carry verified IDs/state across specialist handoffs.

1. Establish app/team/platform/version/build and inspect current remote state. Select one authoritative release lane.
2. Produce the concrete release plan and local artifacts first, then run help-supported dry-run/readiness checks. Validate metadata, screenshots, privacy/review declarations, signing and digital goods as applicable.
3. Execute the stages already authorized once their dependencies are ready. A failed gate blocks dependent actions; continue diagnosis and repairs within scope.
4. On partial failure or timeout, inspect completed receipts and remote state before retrying. Reuse an appropriate existing draft/submission instead of creating duplicates.
5. Report the furthest verified state, exact IDs/artifacts, mutations and remaining blockers. Approval, review acceptance and public availability require their own evidence.

Use `ios-signing` for identity repair, `ios-store-metadata` for listing content, `ios-commerce` for digital goods and `ios-store-insights` for beta diagnostics.

Read only the references needed for the current step:

- [Release states and execution](references/release-state-machine.md)
- [Release recovery and handoff](references/recovery-and-handoff.md)
- [Release provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
