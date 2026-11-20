# Diagnostics, symbolication, and verification

## Select the existing pipeline

Inventory native logging/MetricKit, Organizer diagnostics, existing crash SDKs and backend telemetry before adding anything. Identify who owns collection, consent/privacy settings, symbol upload, retention and release attribution. Do not install competing crash handlers or a second SDK merely to obtain a different dashboard.

Use official documentation and the installed SDK interface for the selected OS/framework version. Uploaded references can describe APIs absent from the project toolchain, including alleged replacement MetricKit APIs or future frameworks. Keep those claims unverified until actual symbols and availability are established. Do not invent names or treat a source's publication date as SDK proof.

## MetricKit lifecycle

For the verified API in use, identify subscriber/manager lifetime, launch registration, callback isolation, payload format and export ownership. Retain the collection object as required. Keep callbacks bounded, avoid UI work on an unspecified/background delivery context, and persist or enqueue sanitized payloads through a safe lifecycle.

Production metrics and diagnostics are asynchronous and incomplete. Delivery timing, device eligibility, application lifecycle and supported metrics vary. A synthetic payload checks parsing/subscription/export plumbing; it does not prove real production delivery or realistic performance. Separate those tests in the report.

Review aggregation windows and version metadata before comparing releases. Keep cumulative/histogram units intact. If forwarding to an existing backend, preserve privacy controls and retry/idempotency semantics so a retry does not count the same window repeatedly.

## Crash and hang triage

Identify app version/build, OS/device, process/extension, exception or termination category and binary images. Check whether the artifact describes a crash, watchdog, memory-pressure termination, hang or sampled diagnostic. Absence of a normal crash report is not proof no termination occurred.

For a hang, inspect the relevant thread and whether it is busy or blocked. CPU-heavy work, lock/I/O waits and priority problems need different evidence. Use the appropriate trace rather than recommending optimization from a single stack snapshot. Reproduce under a realistic launch/lifecycle when investigating watchdog behavior; debugger attachment can change system behavior.

Do not call a source-level suspicion the confirmed root cause. State the evidence that would distinguish competing causes and collect the smallest relevant next artifact.

## Symbolication

Locate the exact shipped archive/dSYM and binary image identity. Verify UUID matching before symbolicating; a matching marketing version is insufficient when multiple builds exist. Preserve architecture, image load/offset context and tooling output needed to interpret the stack. Resolve inlined/demangled frames using supported tools for that artifact.

Keep symbols for every shipped build according to the project's release process. A successful upload command is not proof that the downstream service has processed symbols; observe the service's status if that is within the authorized task. Do not upload private symbols to a new service from an embedded recipe.

## Network diagnostics

Separate cancellation, expected connectivity conditions, server response failures, decoding and domain-validation failures. Aggregate noisy connectivity categories; retain a bounded safe diagnostic for contract breaks. Avoid placing every failure under one generic error string that collapses distinct problems.

Use task metrics to distinguish DNS, connection, TLS, request/response and reused connections where the API provides them. Do not derive a server-only latency from end-to-end duration without evidence. Sanitize endpoint categories; full URLs/query strings often contain sensitive values.

## Verification cases

| Instrumentation change | Check |
| --- | --- |
| New log fields | Exercise synthetic sensitive values, inspect output/export, confirm omissions/redaction |
| Logger wrapper | Confirm typed interpolation/privacy semantics and no unnecessary eager formatting |
| Signpost interval | Trace success, throw and cancellation; verify matching identifiers and no dangling interval |
| Support export | Bound scope/size, inspect artifact, ensure no secrets or unrelated process data |
| Metric parsing/export | Replay supported sanitized fixture; validate units/window/version and retry handling |
| Metric collection | Use available supported device test, then label real-delivery validation separately |
| Symbolication | Match binary UUID and inspect meaningful resolved frames |
| Performance hypothesis | Repeat relevant controlled workload with trace/evidence, without overstating causality |

On a non-Apple host, source review and artifact parsing may be possible while Instruments, device capture and Xcode validation remain unavailable. State the exact gap. Never report simulator/device/production success from a static review.
