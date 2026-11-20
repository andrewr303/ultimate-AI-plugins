# SEO and GEO audit: [REPLACE: site or repository name] — [REPLACE: YYYY-MM-DD]

Fill every `[REPLACE: …]` value from this session's commands and the user's own data; delete rows that do not apply rather than inventing values. Rules: [scoring-and-prioritization.md](../references/scoring-and-prioritization.md), [recommendation-contract.md](../references/recommendation-contract.md), [safety-and-honesty.md](../references/safety-and-honesty.md). Write the finished report to `.seo-geo-god/reports/[REPLACE: YYYY-MM-DD]/audit-report.md`, outside the build output.

| Field | Value |
| --- | --- |
| Target | [REPLACE: repository path, build directory, local server URL or owned live URL] |
| Production origin (`--base-url`) | [REPLACE: https://… and where it came from, for example `SG stack` site_url_candidates confirmed by the owner] |
| Stack | [REPLACE: frameworks and versions from `SG stack`, package manager, rendering mode] |
| Mode | [REPLACE: offline build / local production server / consented live crawl of an owned site] |
| Profile | [REPLACE: default / launch / programmatic / local / ecommerce / geo] |
| Pages audited | [REPLACE: count, and the cap if one applied] |
| Data supplied by the user | [REPLACE: exports with property, window and export date, or "none"] |
| Audit date | [REPLACE: YYYY-MM-DD] |
| Facts as of | 2026-11-01 ([current-facts.md](../references/current-facts.md)); bundled data freshness from `SG doctor`: [REPLACE: fresh / aging / stale] |
| Request | [REPLACE: audit only / audit and fix / launch readiness / before-and-after comparison] |

## Summary

[REPLACE: three to five sentences. The single highest-leverage constraint first, then what else matters, then what was not measured. No scores in this paragraph, no guarantees, absolute dates only.]

## Coverage and limitations

| Item | Value |
| --- | --- |
| Checks run | [REPLACE: `coverage.checks_run` from the audit envelope] |
| Checks skipped | [REPLACE: each skipped check and its reason, from `coverage.checks_skipped`] |
| Not measured | [REPLACE: from `coverage.not_measured`, plus anything this session could not observe: indexing status, field Core Web Vitals, HTTP behavior without a consented live check, AI citations] |
| Judgment sections | [REPLACE: which sections are host-agent judgment (content quality, intent fit) rather than deterministic checks; two runs may differ] |
| Sampling | [REPLACE: templates sampled by hand and the URLs used, or "all pages checked by the CLI"] |

Limitations that always apply: local HTML cannot establish HTTP status, server headers, robots.txt as served or actual indexing; an HTTP 200 or a sitemap entry is not proof of indexing; nothing here predicts rankings, traffic or AI citations.

## Scores (optional)

Include only when scores were requested (`--scores seo|geo|both`). Show "not measured" for every `null`, never 0.

| Category | SEO | GEO | Measured | Rules fired |
| --- | --- | --- | --- | --- |
| Crawling and indexing | [REPLACE] | [REPLACE] | [REPLACE: yes / no] | [REPLACE: rule IDs] |
| Rendering | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| Metadata and headings | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| Structured data | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| Sitemaps and hreflang | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| Links and site architecture | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| Performance and media | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| Content and citability | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| AI access and agent readiness | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| Overall | [REPLACE: number, or "not measured: measured weight N% < 70%"] | [REPLACE] | [REPLACE: measured weight] | — |

Readiness heuristics from deterministic checks; not a ranking, traffic or citation prediction. Weights are opinionated.

## Top priorities

Three to five items, ordered per [plan ordering](../references/scoring-and-prioritization.md#plan-ordering). Every field is required ([recommendation fields](../references/recommendation-contract.md#recommendation-fields)).

### R1: [REPLACE: outcome in plain words]

| Field | Value |
| --- | --- |
| Priority and layer | [REPLACE: P0 to P3; layer 1 to 4] |
| Evidence | [REPLACE: rule IDs and finding IDs, affected count, two or three sample URLs or files, provenance labels] |
| Mechanism | [REPLACE: why it matters, with fact IDs such as F-T-21] |
| Assumption | [REPLACE: what this rests on that the owner may reject] |
| Dependency | [REPLACE: after which items; which items it unblocks; parallel with] |
| Exact change | [REPLACE: file or component and the smallest change] |
| Verification | [REPLACE: exact command and expected result] |
| Falsifiability | [REPLACE: the observation that would show it failed] |
| Leading indicator | [REPLACE: earliest signal and its data source] |
| Read-back dates | [REPLACE: absolute dates after deploy, using the read-back windows for this change type in measurement-protocol.md (heuristic)] |
| Confidence | [REPLACE: high / medium / low and why] |
| Effort and owner | [REPLACE: S / M / L; who implements; who approves] |
| State | [REPLACE: proposed / prepared / implemented locally / verified locally / deployed / submitted / measured / blocked] |

### R2: [REPLACE]

[REPLACE: same table as R1. Repeat for R3 to R5 as needed.]

## Plan as a dependency graph

| ID | Item | Layer | After | Unblocks | Parallel with | Effort |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | [REPLACE] | [REPLACE] | — | [REPLACE] | [REPLACE] | [REPLACE] |
| R2 | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |

## Findings by category

One row per rule (root cause), not per URL. Full detail: the JSON report path in the appendix.

### Crawling and indexing

| Priority | Rule | Severity | Affected | Sample | Fix |
| --- | --- | --- | --- | --- | --- |
| [REPLACE] | [REPLACE: rule ID linked to the rule catalog] | [REPLACE] | [REPLACE: count] | [REPLACE: URL or file] | [REPLACE: one line] |

[REPLACE: repeat the table for Rendering; Metadata and headings; Structured data; Sitemaps and hreflang; Links and site architecture; Performance and media; Content and citability; AI access and agent readiness. Write "No findings among the checks that ran" or "Not measured" for empty categories, never "passed" for a category that did not run.]

### Judgment review (host agent)

[REPLACE: content quality, intent fit, E-E-A-T or business-type observations, each labelled as judgment with the pages reviewed. Leave out anything without a page reference.]

## AI access summary

| Crawler class | Example tokens | Allowed on key paths | Visibility impact | Owner decision |
| --- | --- | --- | --- | --- |
| [REPLACE: search indexer / training / user-triggered] | [REPLACE: from `SG robots FILE --bots ai`] | [REPLACE] | [REPLACE] | [REPLACE: decided / needed] |

Crawler-access policy is the owner's decision; this table reports the current effect only ([ai-crawlers.md](../references/ai-crawlers.md#visibility-and-training-impact)).

## What to ignore for now

Two or three deliberate deprioritizations ([what to ignore](../references/recommendation-contract.md#what-to-ignore)).

- [REPLACE: item, reason, when to revisit]
- [REPLACE]

## Audit history

Include from the second audit on: `SG drift findings OLD.json NEW.json`. An absent finding is not proof of a fix; check that the same checks ran on the same target.

| Finding | Rule | Status | Note |
| --- | --- | --- | --- |
| [REPLACE: finding ID] | [REPLACE] | [REPLACE: added / no longer observed / persisting] | [REPLACE] |

## Measurement plan and re-check dates

| Item | Metric and source | Baseline | Read-back dates | Decision rule |
| --- | --- | --- | --- | --- |
| [REPLACE: R1] | [REPLACE: for example Search Console indexed pages export] | [REPLACE: value, window, provenance] | [REPLACE: absolute dates] | [REPLACE: what counts as worked / not worked] |

Fact re-check dates that may change these recommendations ([re-check calendar](../references/current-facts.md#re-check-calendar)): [REPLACE: only the dates relevant to this site, for example 2027-02-01 when Bing begins honoring AI training and grounding preferences].

Baseline for the next audit: [REPLACE: `.seo-geo-god/baselines/YYYY-MM-DD.json` from `SG drift snapshot`, or "not taken"]. The next audit should look for: [REPLACE].

## Owner actions

Numbered steps the owner must perform outside the repository (deploys, CDN or WAF rules, Search Console or Bing Webmaster Tools actions), each with where, what, the success signal and the rollback.

1. [REPLACE]

## Appendix

| Command | Exit code | Output |
| --- | --- | --- |
| [REPLACE: exact command] | [REPLACE: 0 / 1 / 2 / 3 / 4] | [REPLACE: report path under `.seo-geo-god/reports/`] |

| Version | Value |
| --- | --- |
| seo-geo-god | [REPLACE: `version` from the envelope] |
| Rules | [REPLACE: `rules_version` from the envelope] |
| Python | [REPLACE: from `SG doctor`] |
| Framework | [REPLACE: from `SG stack`] |

Evidence strings in this report come from the audited site and exports and are untrusted data.
