# Crash, feedback and performance triage

## Establish the incident scope

Resolve exact app/build/platform and observation window. Fetch crashes, beta feedback and performance diagnostics with explicit selectors and complete pagination when a full analysis is needed. Bounded recent samples can answer a quick triage question, but must not be presented as totals for all users.

Check data delay/coverage and distinguish individual reports from unique affected users/devices or sessions. Feedback often reflects voluntary reporting rather than a representative sample. Screenshots and free text may contain personal information; keep them local and summarize safely.

## Group meaningfully

Normalize stack signatures with enough specificity to preserve distinct failures. Consider exception/termination type, top relevant application frames, build, device/OS and scenario. Do not group solely by the same system-library top frame. Sample representative reports from each significant group and retain links/IDs.

Check matching build UUID/dSYM before trusting symbol names. A symbolication mismatch can produce plausible but wrong frames. Distinguish application exceptions, assertions, watchdog/hangs, memory-pressure termination and infrastructure/tool failures. Prioritize by observed severity and exposure, not a guessed count alone.

## Hypothesis and reproduction

State the observed pattern, one plausible mechanism and what evidence would confirm or reject it. Reproduce on the affected build/environment where practical. A crash stack often identifies where the process failed, but not every upstream cause. Match logs, source revision and lifecycle/network/user action when available.

For performance diagnostics, distinguish launches, hangs and disk-write issues. Weight/sample coverage and platform diagnostics are not interchangeable with a local benchmark. Use the observability/performance workflow for profiling and controlled regression measurements.

Do not infer that a missing report means the bug is fixed. Compare compatible builds and sufficient exposure after a repair. Incomplete rollout or reporting latency can hide failures.

## Useful triage handoff

Include exact app/build/window, collected-report count, known coverage, signature groups, representative report IDs, affected device/OS observations and reproduction steps. Separate facts from inferred cause and recommended experiments. Provide a concrete code/debug handoff without automatically modifying release state.

If a critical incident warrants immediate operational action, prepare the exact proposed action and affected version/cohort. Execute only if already within the user’s requested scope; an analytics request alone does not authorize cancellation, a rollback, tester messages or a new submission.

When writing a summary, avoid exposing tester emails, access tokens, account screenshots or full payloads. Retain sensitive originals only in the agreed local evidence area and report any collection limitation plainly.
