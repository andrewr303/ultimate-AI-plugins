# Cross-platform signals and safe correlation

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Define the question before collecting data

Identify the behavior to explain: client transport failure, auth rejection, stale conflict, queue lag, provider rejection, app decode failure or release regression. Distinguish operational metrics, diagnostic logs/traces and product analytics. More telemetry is not automatically better evidence, and an SDK mentioned by a source is not a configured collection/consent policy.

Map the path from the Swift request through Node handler, database/job and external provider callback. Select safe correlation and durable operation identifiers with explicit scope. Keep account/tenant authorization separate from correlation; an incoming request ID is not proof of identity and should not authorize lookup of private diagnostics.

## Signal model

Define when an operation starts, is admitted, is committed and reaches the user-visible outcome. Count retries and duplicates separately from business completions. For asynchronous jobs/webhooks, connect related work with meaningful context without pretending all events run in one synchronous request. Avoid treating provider acceptance as push display or HTTP success as a completed app action.

Use structured safe error codes, latency/result categories and relevant version/revision context. Do not put private payloads, tokens, device tokens, signed URLs or user text into span names/attributes. Cardinality and retention are design decisions: arbitrary identifiers in every metric label can create cost and privacy problems. Keep a deliberate diagnostic path for details that should not be broad telemetry.

## Implementation sequence

1. Establish the observable outcome and current signal gaps. Read existing logger/tracing/metric setup and configured exporter/provider before adding another SDK.
2. Define correlation propagation at trust boundaries. Validate or replace untrusted input where appropriate and avoid forwarding sensitive headers blindly to other origins.
3. Instrument the actual domain/transport boundary that answers the question. Preserve stable error categories across Swift and Node rather than flattening every failure into network-error.
4. Link durable job and provider-event identity to domain operation state. Keep receipt, retry and final success distinct in both logs and aggregate metrics.
5. Test a failed request, timeout after commit, duplicate event, stale result and a job retry. Check that correlation survives without inflating success counts or leaking content.
6. Record runtime/app/backend/schema revisions associated with captures so a result from an older build is not used as evidence for the current change.

## Failure cases

| Misleading signal | Correct interpretation |
| --- | --- |
| HTTP success counter rises | It may represent accepted/duplicate work, not distinct business success |
| Provider event timestamp order | Delivery can be duplicate or out of order; reconcile actual state |
| Same request ID across accounts | Correlation is not authorization or a globally trustworthy key |
| Trace exists | Exporter collection does not prove complete coverage or retention |
| No error logs | Sampling, missing instrumentation or shutdown can hide failures |
| Backend trace looks healthy | Client decode/UI/platform lifecycle may still fail |

## Verification and handoff

Inspect emitted records with synthetic data and known failure gates. Verify redaction and classification at the source and the actual configured sink when authorized. Keep instrumentation overhead claims grounded in comparable measurements. Static review can identify a potential high-volume attribute; it cannot prove a performance gain.

Return the diagnostic question, instrumented path, safe fields, test result and remaining blind spots. This reference does not provision an exporter, enable telemetry, or authorize sending app logs to external services.

## Sources and applicability

- [Node.js | OpenTelemetry](https://opentelemetry.io/docs/languages/js/getting-started/nodejs/) — `src_nm_otel_node`.
- [HTTP | Node.js v26.12.1 Documentation](https://nodejs.org/api/http.html) — `src_nm_node_http`.
- [Receive Stripe events in your webhook endpoint | Stripe Documentation](https://docs.stripe.com/webhooks) — `src_nm_stripe_webhooks`.
- [Running tests and interpreting results](https://developer.apple.com/tutorials/data/documentation/xcode/running-tests-and-interpreting-results.json) — `src_nm_xcode_results`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
