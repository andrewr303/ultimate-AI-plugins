# Analytics collection and data quality

## Define the measurement contract

Record app/platform/version/build selectors, metric definition, period, timezone, territory, source and reporting granularity. Clarify whether the question concerns downloads, installations, active devices, sessions, launches, sales, proceeds, crashes or feedback. These units are not interchangeable and different sources may use different inclusion criteria.

Discover actual report requests/instances/segments through the available API/CLI. Inspect current installed help and official field definitions before designing a query. Pagination, segmentation, privacy thresholds, processing latency and retention can affect coverage. No report available is different from a zero-valued report.

## Collect reproducibly

Select reports by the documented processing/instance dates and granularity, not by an ambiguous filename. Download every required segment and record source IDs, observed timestamps and file metadata without secrets. When the service provides sizes/checksums, verify them against the actual downloaded bytes. A checksum match establishes transfer consistency, not business correctness.

Preserve raw evidence read-only when practical; transform into separate task-local artifacts. Validate parsing, types, encoding, headers, null markers, units and schema drift. Inspect duplicate keys/rows, segment overlap and missing periods. Do not silently turn missing values into zeros or discard bad rows without reporting the effect.

Avoid downloading entire tester/customer datasets for a narrow aggregate question. Redact personal fields in analysis and chat. Do not transmit exports to another service or feedback endpoint merely because an upstream reference suggests it.

## Metrics and denominators

Report counts with their actual unit and sample size. A crash count is not a crash rate without an appropriate denominator over the same cohort/window. When denominators are missing, present counts and state the missing measure. Do not compare device-based rates to session-based rates as if equivalent.

For before/after release comparisons, align cohort exposure, date window, version, geography and device mix as far as data supports. Separate rollout adoption from outcome change. A correlated increase after release suggests investigation; it does not establish the release caused the change.

Small cohorts, delayed data and privacy thresholds can make apparent movement unstable. Avoid invented precision, rank claims and revenue projections. Use a range or qualified observation when the source supports one; label assumptions explicitly.

## Reproducible output

Keep a source-to-result trail: query/selector, report/instance/segment IDs, downloaded artifact, transformations and metric definitions. A report should contain question, scope, quality findings, measured results, uncertainty and next action. Link only user-appropriate artifacts; keep raw personal/customer details private.

Read-only findings can inform release decisions, but do not automatically change availability, pricing, marketing or review state. If follow-up action is requested later, carry the observed scope and evidence into that workflow.
