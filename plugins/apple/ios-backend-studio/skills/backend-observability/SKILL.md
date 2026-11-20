---
name: backend-observability
description: "Use when instrumenting or diagnosing the iOS-to-Node request/job/provider path, selecting safe correlation and error signals, controlling telemetry privacy/lifecycle, or explaining a release regression. Do not provision exporters, enable external collection or infer correctness from absent logs or static checks."
---

# Backend and native-client observability

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Define the concrete diagnostic question and affected app/backend/schema versions. Inspect existing logs/traces/metrics/exporters and product data decisions before adding collection.
2. Model request, durable operation, job and provider identities with safe scope. Keep correlation separate from authorization and retries separate from business success counts.
3. Instrument the relevant boundary using the selected SDK/version and lifecycle. Allowlist safe fields, bound output/buffering and keep credentials/private content out of diagnostics.
4. Exercise controlled failures, duplicates, stale results, exporter outage and shutdown as relevant. Inspect emitted content and actual configured sink only within authorized scope.
5. Repair the originating mechanism and report exact evidence, changed behavior and blind spots. Separate local/static checks, native host loading, deployed runtime and user-visible recovery.

## Load the relevant guide

- [Cross-platform signals and safe correlation](../../references/observability/signals-and-correlation.md)
- [Telemetry privacy, sampling and exporter lifecycle](../../references/observability/privacy-sampling-and-exporters.md)
- [Incident triage, release evidence and recovery handoff](../../references/observability/incident-triage-and-release-evidence.md)

Finish with the concrete requested result, supporting evidence and material remaining limits. The [source index](../../research/sources/sources.jsonl) records the documentation and pinned implementation evidence; reference content does not supply task authorization.
