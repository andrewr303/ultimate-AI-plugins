# Measurement plan: [REPLACE: short name of the change]

Fill this in and get the owner's agreement **before** the change ships. A plan written after looking at the results is exploratory, not a test. Method and vocabulary: [measurement-protocol.md](../references/measurement-protocol.md). Keep the filled copy under `.seo-geo-god/plans/` in the repository and record the experiment in the ledger (`SG ledger record .seo-geo-god/ledger --json experiment.json`).

| Field | Value |
| --- | --- |
| Plan ID | [REPLACE: exp-YYYY-MM-DD-slug] |
| Plan written on | [REPLACE: YYYY-MM-DD, before deployment] |
| Decision owner | [REPLACE: role of the person who decides Promote, Keep testing, Rollback or Unproven] |
| Facts as of | 2026-11-01 (re-check the dated facts the plan depends on) |

## 1. Hypothesis

[REPLACE: one sentence in the form "If we change X on pages Y, metric Z will move in direction D because of mechanism M (fact ID or evidence)". Name the measurement layer: 1 access, 2 citability proxy, 3 AI surfacing, 4 rankings and clicks.]

## 2. The change (exactly one)

- What changes: [REPLACE: one attributable change, or a clearly labelled batch that is evaluated only as a batch]
- Files and commit: [REPLACE: paths and the commit or PR that will ship it]
- Target pages: [REPLACE: URLs]
- Deployment date: [REPLACE: YYYY-MM-DD, filled in when it actually deploys; "prepared" is not "deployed"]
- Preconditions checked: [REPLACE: layer 1 access and server rendering pass for every target page, with the command and date]

## 3. Metric and denominator

| Item | Value |
| --- | --- |
| Primary metric | [REPLACE: for example citation rate = valid_present / (valid_present + valid_absent) per surface] |
| Denominator | [REPLACE: what counts; empty and error observations are excluded and reported separately] |
| Guardrail metrics | [REPLACE: for example organic clicks on the same pages, conversions, error rate] |
| Minimum change worth acting on | [REPLACE: an absolute difference agreed in advance] |

## 4. Data source

- [REPLACE: prompt panel `templates/prompt-panel.example.csv` copy, Search Console export, Bing Webmaster Tools AI Performance export, GA4 export, server access logs]
- Collection method and who runs it: [REPLACE: manual sessions, a user-owned collector following the collector contract, or an export schedule]
- Fixed conditions: [REPLACE: locale, device, logged-in state, region, model label if shown]

## 5. Baseline window

[REPLACE: dates of at least two baseline reads before deployment, and the number of samples per query per surface]

## 6. Control and hold-out

- Control pages: [REPLACE: unchanged pages of the same type and topic, read with the same panel]
- Hold-out queries: [REPLACE: query IDs never used to tune the changed pages]
- What else is changing in the same window: [REPLACE: other releases, campaigns, known engine updates; `SG updates --since YYYY-MM`]

## 7. Read-back dates (fixed now)

| Read-back | Date |
| --- | --- |
| +7 days | [REPLACE: YYYY-MM-DD] |
| +14 days | [REPLACE: YYYY-MM-DD] |
| +28 days | [REPLACE: YYYY-MM-DD] |
| +56 days | [REPLACE: YYYY-MM-DD] |

`SG ledger status .seo-geo-god/ledger` lists the read-backs that are due.

## 8. Decision rule

- **Promote** when: [REPLACE: primary metric beats control by at least the minimum change at the final read-back, guardrails hold, data quality intact]
- **Keep testing** when: [REPLACE: the registered continuation rule, for example "direction positive but interval includes zero; one more read-back at +56 days"]
- **Rollback** when: [REPLACE: a guardrail is breached, at any read-back]
- **Unproven** otherwise. No significant difference is not proof that nothing changed.

## 9. Risks and confounders

- [REPLACE: seasonality, engine model or interface changes, small samples, repeated samples from one session, referrer loss into Direct traffic]

## 10. What will not be measured

- [REPLACE: surfaces not sampled (write "not measured", never zero), clicks inside AI answers where no data exists, causal effect where no control exists]
