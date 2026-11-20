# Signal design, privacy, and measurement contracts

## Begin with a question

Name the behavior to observe and the decision the evidence should support. “Add logging everywhere” produces noise and may expose data without improving diagnosis. A useful question is narrower: which state transition failed, where a request spent time, whether a release changed launch behavior, or which shipped binary matches a crash.

| Question | Candidate signal | Required context |
| --- | --- | --- |
| What branch/state/error occurred? | Structured categorized Logger/OSLog event | Stable event meaning, release, safe fields |
| How long did one operation take locally? | Signpost interval and Instruments | Operation identity, start/end and workload |
| Which phase delayed a network request? | URLSession task metrics plus bounded classification | Request category, transport phases, reused connection |
| What do users experience across releases? | Available production metric/diagnostic pipeline | Build/device/OS, units, aggregation and coverage |
| Why did the app crash or hang? | Matching diagnostic and symbols | Binary UUID/build, stack, termination context |
| What can support recover from this app session? | Bounded authorized log export | Scope, privacy, retention and missing-data caveats |

These signals can complement each other. A log message is not automatically a statistically sound metric; a signpost is not a guaranteed fleet-wide analytics event.

## Logger design

Choose subsystem/category values that correspond to useful filtering boundaries. Reuse stable category loggers where appropriate. Use the native typed interpolation contract at call sites when possible. Pre-rendering a String loses per-field OSLog interpolation and privacy behavior. An autoclosure can defer work but does not restore typed per-field privacy.

Choose severity according to diagnostic meaning, cost and capture policy. Expected offline/retry/cancellation states should not become fault-level programmer errors. High-volume development traces should not flood release support logs. Verify actual persistence/capture settings; do not promise all levels will be retrievable indefinitely.

Log meaningful transitions, classified failures and bounded boundary information. Avoid per-frame/per-cell logs in hot UI paths. A stable error code/category is usually more useful and safer than a public raw error description. Keep enough context to distinguish failure classes without collecting user payloads.

## Review every data field

Classify each field before it leaves the process or enters a persisted diagnostic:

- secrets/authentication: omit; never record tokens, passwords, cookies or credential-bearing URLs;
- user/content identifiers: minimize, redact or use an intentionally scoped correlation scheme;
- request data/body/query: omit by default; retain only a sanitized classification needed by the diagnostic;
- error text: assume it may contain URLs, account information, payload excerpts or file paths;
- numeric values: review explicitly; a number can still identify a user or reveal private data;
- harmless enums/counts/build identifiers: mark public only after checking meaning and combinations.

A hashed identifier remains linkable data and may be susceptible to guessing. OSLog private annotations do not automatically sanitize a file, SDK breadcrumb, server event or screenshot built from the same values. Redact before each non-OSLog destination and test the resulting artifact.

Bound capture duration, event volume, local retention and export size. Support export should state its scope and avoid silently including other apps/device data. Use synthetic/redacted fixtures when demonstrating the pipeline.

## Signpost lifecycle

Give each concurrent operation an identity and use the matching begin/end contract. End intervals on success, throw and cancellation, using guaranteed cleanup appropriate to the API. Do not create an interval only on one branch and unconditionally end an unrelated one.

Choose operation boundaries corresponding to actual work, not arbitrary UI render cycles. Separate waiting, decoding, database work and rendering when the distinction answers the performance question. Check available instrumentation APIs and runtime availability before writing code.

Inspect the trace to verify interval pairing, overlap, labels and workload. An instrumented release build on the relevant device often gives different evidence from a debugger-driven simulator run. Report which environment was measured.

## Metric semantics

Record units at collection and export boundaries. Convert once deliberately. A histogram is bucketed aggregate information, not raw samples; a daily cumulative value is not an instantaneous gauge. Preserve sample/count/window metadata needed to interpret comparisons. Do not derive precise percentiles or averages from insufficient bucket information without explaining approximation.

Compare like workloads/releases and consider device/OS mix, sampling, missing reports and mixed-version windows. Do not attribute causality to a code change from one uncontrolled trace. Keep numeric thresholds specific to a verified tool/runtime and product objective.
