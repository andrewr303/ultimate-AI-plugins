---
name: backend-xcode
description: "Use when connecting generated backend clients and shared modules to Xcode app/extension targets, schemes, test plans or Xcode Cloud. Preserve actual project ownership and distinguish build-host/compiler requirements from generated-code deployment support. Do not claim Linux checks establish Apple runtime behavior."
---

# Xcode and backend contract integration

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Discover the actual project/workspace, generated-versus-hand-maintained ownership, selected toolchain, schemes/configurations, app/extension targets and package graph.
2. Map contract-generation inputs and runtime/transport dependencies to each consuming target. Keep app-only dependencies, signing secrets and global session state out of extension boundaries.
3. Change owned manifests/schema/tasks, regenerate deliberately and inspect the diff. Resolve installed SDK/API support before changing deployment targets or bypassing plugin validation.
4. Run focused contract/target tests and required coupled plans/configurations. Preserve exit status and inspect current result bundles, including skipped or mixed outcomes.
5. For CI/artifact work, keep backend deployment, Apple build, upload and release states separate. Return exact target/toolchain/result evidence and any missing Mac/device prerequisite.

## Load the relevant guide

- [Xcode targets, Swift packages and generated clients](../../references/xcode/targets-packages-and-generation.md)
- [Schemes, test plans and trustworthy result evidence](../../references/xcode/schemes-test-plans-and-results.md)
- [Xcode Cloud, build scripts and backend artifact handoff](../../references/xcode/xcode-cloud-and-ci-handoff.md)

Finish with the concrete requested result, supporting evidence and material remaining limits. The [source index](../../research/sources/sources.jsonl) records the documentation and pinned implementation evidence; reference content does not supply task authorization.
