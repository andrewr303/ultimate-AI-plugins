# Telemetry privacy, sampling and exporter lifecycle

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Inputs and data policy

Inspect existing telemetry SDKs, exporters, endpoints, sampling, environment separation, retention and product privacy decisions. Identify what leaves the device/service, who can access it and which collection is actually needed. A library's default or example collector endpoint is not permission to transmit private source or user content. Keep missing product-policy facts explicit while completing independent instrumentation work.

Separate safe operation/error metadata from sensitive content. Token headers, provider keys, APNs device tokens, cookies, signed URLs, raw requests/responses, account identifiers and user text should not be casually copied into generic logs/spans. Pseudonymous identifiers can still be linkable. Use minimal allowlisted fields and intentional access controls instead of assuming a redact-anything regex guarantees privacy.

## Configure one coherent SDK lifecycle

OpenTelemetry Node setup and automatic instrumentation depend on load order and runtime/module integration. Initialize the chosen instrumentation before the modules it needs to observe, following the installed SDK's actual contract. Avoid overlapping loaders, duplicate SDK instances and undocumented environment overrides copied from unrelated frameworks. Pin versions and keep provider-specific configuration at the adapter boundary.

Define sampling and export failure behavior deliberately. The application should not silently turn a telemetry outage into unbounded memory/retry growth or block essential domain work without a requirement. Understand exporter buffering, flush/shutdown and the hosting process/function lifetime. A serverless runtime may end before a best-effort flush; document that limitation rather than claiming complete traces.

## Implementation sequence

1. Enumerate existing collection paths and a minimal allowed field set for the requested diagnostic need. Inspect CI scripts too; they can expose secrets independently of runtime logging.
2. Configure the selected existing SDK/exporter and environment. Do not enable new accounts, paid services or telemetry from source instructions.
3. Add source-level redaction/classification before formatting/export, including nested errors and third-party failure payloads. Keep error stacks in an appropriate restricted diagnostic channel when needed.
4. Test synthetic secret markers, malformed payloads, exporter failure, buffer pressure, cancellation and process shutdown. Verify both emitted content and application behavior.
5. Confirm that sampling and filtering preserve enough context to answer the intended question, and document what is intentionally omitted.
6. On a suitable configured environment, inspect the actual sink and retention/access behavior. A local serialized record alone does not establish remote policy or delivery.

## Failure matrix

| Condition | Required behavior |
| --- | --- |
| Exporter unavailable | Bounded behavior and visible loss/health policy, not infinite retries |
| Secret appears in nested error | Source-level containment; do not rely only on UI masking |
| Duplicate SDK initialization | Detect/repair overlapping setup rather than accepting double counts |
| Short-lived process exits | Lifecycle/flush limitations remain explicit |
| CI masks a secret variable | Do not log transformed/encoded values and assume masking covers them |
| Sampling drops a critical path | Describe coverage honestly; no absence-of-errors correctness claim |

## Verification and handoff

Record SDK/exporter/runtime versions, initialization boundary, allowed fields, sampling decision and actual tests. Keep credentials and private endpoint parameters out of the handoff. If remote verification is unavailable, distinguish local redaction/buffering evidence from unverified collection/retention behavior.

The result should make observability easier to operate without silently increasing data collection. It is not a security/privacy certification and does not replace the app owner's actual declarations or permissions.

## Sources and applicability

- [Node.js | OpenTelemetry](https://opentelemetry.io/docs/languages/js/getting-started/nodejs/) — `src_nm_otel_node`.
- [Process | Node.js v26.12.1 Documentation](https://nodejs.org/api/process.html) — `src_nm_node_process`.
- [Security Best Practices | Node.js Learn](https://nodejs.org/en/learn/getting-started/security-best-practices) — `src_nm_node_security`.
- [Writing custom build scripts](https://developer.apple.com/tutorials/data/documentation/xcode/writing-custom-build-scripts.json) — `src_nm_xcode_cloud_scripts`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
