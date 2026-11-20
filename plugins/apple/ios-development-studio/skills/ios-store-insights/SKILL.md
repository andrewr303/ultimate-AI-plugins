---
name: ios-store-insights
description: "Use for App Store Connect analytics, TestFlight crash/feedback triage, build performance diagnostics and source-backed store reports. Do not use to infer missing denominators, causality, real-time completeness or automatic release/campaign changes."
---

# Analyze store health and beta evidence

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Define the question, app/build/version, observation window, timezone, territory/cohort and available sources. Fetch only the data needed using verified read-only tools and exact IDs. Preserve downloaded evidence locally with nonsecret provenance.

1. Establish report availability, processing delay, pagination and coverage.
2. Verify segment completeness/schema and distinguish raw counts from rates with denominators.
3. Group crashes/feedback by meaningful signature and inspect representative evidence. Match symbols/builds before attributing a root cause.
4. Separate observed facts, hypotheses and recommended next checks. Compare compatible cohorts/windows and disclose uncertainty.
5. Deliver findings linked to artifacts and exact scope; hand reproducible bugs to build/debug or observability. An analysis request does not authorize release cancellation, tester messaging or commercial changes.

Read only the references needed for the current step:

- [Analytics collection and data quality](references/analytics-quality.md)
- [Crash, feedback and performance triage](references/crashes-feedback.md)
- [Insights provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
