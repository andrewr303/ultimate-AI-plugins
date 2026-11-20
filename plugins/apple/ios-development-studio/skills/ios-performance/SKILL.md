---
name: ios-performance
description: "Investigate iOS hangs, scrolling hitches, excessive SwiftUI updates, CPU/memory pressure, launch latency, or supplied Instruments evidence. Use ios-observability for instrumentation systems and ios-swiftui for ordinary implementation. Do not claim measured improvements from source review, treat heuristics as proof, or run unbundled upstream trace scripts."
---

# Performance investigation

Read the [operating contract](../ios-development/references/operating-contract.md) first. Start with a concrete symptom, reproducible interaction and the environment in which it occurs.

## Workflow

1. Collect the scenario, device/simulator, OS, build configuration, dataset and baseline. Use [measurement and evidence](references/measurement-and-evidence.md) to choose an appropriate bounded capture. Prefer an existing supplied trace over a speculative rewrite.
2. Review the implicated code using [diagnosis and remediation](references/diagnosis-and-remediation.md). Rank hypotheses by observed impact and confidence; source smells identify candidates, not measured root causes.
3. Inspect available tools and installed capture/export help. Use native Apple tooling only where available or an existing authorized remote workflow. Never imply a parser/script is bundled merely because a source guide mentioned it.
4. Correlate expensive work with the user-visible interval. Distinguish CPU work, waiting, invalidation, layout, image decoding and memory retention. Check what invalidates an expensive view, not only which view is expensive.
5. Make the smallest authorized fix with a clear causal hypothesis. Preserve behavior and avoid broad architecture/cache changes without evidence.
6. Repeat the same representative scenario under comparable conditions. Record actual before/after results and regressions. If runtime verification is unavailable, report a source-backed proposal and exact remaining validation.

## Output

Provide the symptom and scenario, evidence used, ranked finding with source/capture location, change or proposed remedy, observed comparison, and remaining uncertainty. Include a small metrics table only when real comparable measurements exist.

Do not invent frame-time, memory, battery or speedup numbers. Simulator behavior cannot establish physical-device performance. Redact captures and logs that contain private app data; bound duration, process and output location. See [source map](../../docs/source-map.md).
