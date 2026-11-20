---
name: ios-observability
description: "Use when adding or reviewing Apple-platform Logger/OSLog privacy, signposts and Instruments measurements, support-log export, MetricKit, crash/hang diagnostics, dSYM symbolication, or app network telemetry. Do not activate for generic analytics dashboards or collect production data merely because this skill exists."
---

# iOS observability

Read the [shared operating contract](../ios-development/references/operating-contract.md). Establish the diagnostic question, supported SDK and permitted data before emitting or exporting telemetry.

## Workflow

1. Identify the symptom, affected build/device/OS, reproducibility, current instrumentation and available artifacts. Keep a hypothesis separate from an observed event.
2. Choose a signal with [signal design and privacy](references/signals-and-privacy.md): discrete state/error logs, operation signposts, production metrics, or diagnostic stacks. Add only signals that answer the question.
3. Use [diagnostics and verification](references/diagnostics-and-verification.md) for MetricKit, symbolication, support logs and runtime checks. Verify symbols/availability in the actual SDK; source claims about new APIs are not sufficient.
4. Implement categorized, privacy-reviewed instrumentation with bounded volume, lifecycle cleanup and clear units. Do not add another crash SDK or a new backend by default.
5. Exercise success, failure and cancellation paths, inspect emitted/redacted artifacts, and verify release/device behavior where required. Profile the relevant workload before making performance claims.

## Boundaries

Never emit tokens, raw payloads or arbitrary error descriptions as public fields. OS redaction does not protect a separately rendered file or third-party event. Confirm the requested scope before export/upload, profile installation, SDK enablement or remote collection. Keep capture bounded and identify the target app/device.

## Completion

Report what signal now answers the question, its privacy/retention behavior, observed results and unavailable device/production validation. Keep measurement limitations explicit.

## Provenance

Original workflow informed by supplied `Observability-Agent-Skill-main.zip` (`observability` references), with version-sensitive statements independently gated. See the [source map](../../docs/source-map.md). Unverified alleged new SDK APIs are not baseline recommendations.
