# Insights provenance

Original synthesis informed by `app-store-connect-cli-skills-main.zip`:

- `skills/asc-analytics-reports/SKILL.md`: report discovery, segments and transfer verification.
- `skills/asc-crash-triage/SKILL.md`: TestFlight crashes/feedback and performance diagnostics.
- `skills/asc-build-lifecycle/SKILL.md` and `skills/asc-cli-usage/SKILL.md`: exact build IDs and paginated structured reads.

`skills-main (1).zip` `plugins/expo/skills/{eas-observe,eas-update-insights}/SKILL.md` informed the separation of instrumentation, update adoption and observed health; those service metrics are not assumed available for a native app.

No live analytics, crash counts, latency guarantee or causal result is supplied by this plugin. The runtime must gather its own evidence. Upstream notices are retained. [Source map](../../../docs/source-map.md).
