<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: evidence-type labels, the Unknown versus not-applicable distinction and the sample-by-template audit method re-expressed in our own words and tied to the bundled rule catalog, merged with MIT-licensed scoring caveats and evidence classes, with our own weights, penalties and thresholds. See NOTICE.md. -->
# Scoring and prioritization

How SEO-GEO-god turns findings into optional readiness scores and into an ordered fix plan: the scoring algorithm and weights, what "measured" means, the caveats every report must carry, rule evidence classes, metric provenance labels, Unknown versus not applicable, priority meanings, root-cause deduplication and the plan order used by [seo-geo-audit](../skills/seo-geo-audit/SKILL.md). Per-recommendation fields are in [recommendation-contract.md](recommendation-contract.md).

As of 2026-11-01. The numbers here (weights, penalties, the 70% coverage gate, scope steps) are our own opinionated heuristics stored in `data/rules.json`; they are not derived from a controlled study and not taken from any engine. `SG` means `python3 -I <plugin-root>/scripts/seo_geo.py`.

## What scores are and are not

Scores answer one narrow question: "of the deterministic checks that ran, how much did this build or crawl trip, weighted by severity, evidence strength and scope?" They are readiness heuristics. They are not a ranking, traffic, indexing or AI-citation prediction, and no engine computes or uses them. Findings, with their evidence and fix hints, are the real output; scores are a summary that can be switched off (`--scores none`, the default).

## Scores are optional and never gate

- Scores are produced only on request: `--scores seo`, `--scores geo` or `--scores both` on audit commands (`SG audit-build`, `SG audit-page`, `SG audit-url`).
- CI gates use severities, never scores: `--fail-on error` (or `warning`, `info`, `never`). A score threshold would let one new P0 hide behind many fixed infos.
- Compare scores only between runs with the same tool version, `rules_version`, profile, target type and base URL. A different rule set or coverage makes deltas meaningless; `SG drift findings OLD.json NEW.json` compares findings instead.

## Algorithm

For each category in [Category weights](#category-weights):

1. **Measured or not.** A category is measured when at least one check mapped to it ran (see [Coverage map](#coverage-map)). An unmeasured category scores `null`, never 0 and never 100.
2. **Penalty per rule, counted once.** Every rule that fired in the category adds one penalty, whatever the number of instances (root-cause deduplication): base penalty by the most severe instance, error 12, warning 4, info 0; multiplied by the evidence-class factor, A 1, B 1, C 0.5, D 0; multiplied by the scope factor.
3. **Scope factor.** Page-scope rules: 1.0 for one affected page, 1.5 for 2 to 9 pages, 2.0 for 10 or more. Site-scope rules (for example robots.txt or sitemap findings): always 2.0.
4. **Category score** = max(0, 100 minus the sum of penalties), rounded to an integer.
5. **Overall** = the weighted mean of measured categories, reported only when the measured categories carry at least 70% of the profile's total weight. Below that, `overall` is `null` and `overall_reason` says why, for example "measured weight 30% < 70%".
6. Findings from change monitoring (DRIFT rules) and from the rewrite fidelity check are never scored.

Never fill an unmeasured category with a default, an estimate or a previous run's value.

Worked example (profile `seo`, offline build):

| Category | Fired rules | Penalties | Score |
| --- | --- | --- | --- |
| crawl_index | CANON002 error, class A, 3 pages; LAUNCH003 error, class B, 14 pages | 12 × 1 × 1.5 = 18; 12 × 1 × 2.0 = 24 | 100 − 42 = 58 |
| metadata | META002 warning, class C, 12 pages; META011 info | 4 × 0.5 × 2.0 = 4; 0 | 96 |
| rendering | none | 0 | 100 |

If the same run had executed only `SG robots` and `llms-txt` checks, only `crawl_index` (22) and `ai_access` (8) would be measured: 30 of 100 weight, so `overall` is `null`.

## Category weights

| Category | Rule families | `seo` weight | `geo` weight |
| --- | --- | --- | --- |
| `crawl_index` | CRAWL, IDX, CANON, HTTP, REDIR, SPAM, LAUNCH | 22 | 15 |
| `rendering` | REND | 12 | 15 |
| `metadata` | META, HDG | 12 | 5 |
| `structured_data` | SD | 8 | 8 |
| `discovery` | SMAP, HREF | 10 | 5 |
| `architecture` | LINK, PSEO | 10 | 7 |
| `performance_media` | PERF, IMG, VID | 10 | 5 |
| `content` | CONT, CITE, LOCAL | 8 | 20 |
| `ai_access` | AI, AGENT | 8 | 20 |

The `geo` profile shifts weight toward rendering, content and AI access because those layers decide whether AI answer systems can fetch and quote a page at all. It does not measure citations; see [measurement-protocol.md](measurement-protocol.md#four-layers).

## Coverage map

Which check makes which category "measured" (from `data/rules.json`):

| Check (in `coverage.checks_run`) | Categories |
| --- | --- |
| `pages` | crawl_index, metadata, rendering, performance_media |
| `duplicates` | metadata |
| `links`, `pseo` | architecture |
| `robots` | crawl_index, ai_access |
| `ai-directives`, `llms` | ai_access |
| `sitemaps`, `hreflang` | discovery |
| `jsonld` | structured_data |
| `content`, `citability` | content |
| `perf` | performance_media |
| `launch`, `http`, `redirects` | crawl_index |
| `access` | ai_access, crawl_index |

"Measured" means some checks in the category ran, not that every rule could be evaluated. An offline build audit measures `crawl_index` without HTTP status, server headers or real redirects; those appear under `checks_skipped`, and the report must say so next to the score.

## Caveats

Print these with any score (the envelope's `scores.note` carries the short form):

- **Deterministic versus judged.** CLI findings are deterministic: the same input gives the same output. Content quality, E-E-A-T, intent fit and other judgments made by the host agent are not part of the score; when reported, they are labelled as judgment, and two runs may differ.
- **Opinionated weights.** Weights and penalties are design choices for prioritizing work, not measured effects.
- **Diagnostic, not a guarantee.** A perfect score does not mean a page will be indexed, ranked, shown as a rich result or cited; a low score does not mean it will not.
- **Structural, not semantic.** Structured-data checks validate syntax, structure and documented required properties; they cannot confirm that values are true or that the markup matches what people see (that needs review, and [SD016](rule-catalog.md#sd016) is planned).
- **Coverage-bound.** Scores describe only the pages, checks and data that were available. Field Core Web Vitals, indexing and AI visibility are never inferred from build output.
- **Heuristic rules.** Class C rules count half and class D rules never penalize; their thresholds are ours.

## Evidence classes

Every rule in [rule-catalog.md](rule-catalog.md) has one class:

| Class | Meaning | Score factor | Examples |
| --- | --- | --- | --- |
| A | Backed by official engine or standards documentation | 1.0 | [CANON002](rule-catalog.md#canon002) multiple canonicals, [AI004](rule-catalog.md#ai004) Googlebot blocked |
| B | Deterministic spec or structure check | 1.0 | [SD001](rule-catalog.md#sd001) malformed JSON-LD, [LINK001](rule-catalog.md#link001) broken internal link |
| C | Heuristic; the threshold is ours or folk wisdom, labelled as such | 0.5 | [REND002](rule-catalog.md#rend002) thin server HTML, [CITE001](rule-catalog.md#cite001) low passage citability |
| D | Experimental or optional; reported, never penalized | 0 | [AGENT001](rule-catalog.md#agent001) no llms.txt, [AGENT009](rule-catalog.md#agent009) llms-full.txt present |

A rule's class is about the evidence for the check, not about its impact: a class C rule can still be worth fixing first.

## Provenance labels

Every number in a report that is not a CLI finding carries one of these labels next to it:

| Label | Meaning | Example | May drive a decision? |
| --- | --- | --- | --- |
| `measured` | Observed directly, by a check in this session or in an export of observed data | GSC clicks for a window; CrUX p75 LCP; status codes from a consented crawl | Yes |
| `user-provided` | Stated by the user or their documents, not independently checked | Brand terms, target markets, revenue per lead | Yes, with the source named |
| `calculated` | Derived deterministically from other values; inherits the weakest input label | CTR from clicks and impressions; a Wilson interval; a period delta | As strong as its inputs |
| `estimated` | A model or third-party estimate | Keyword volume or difficulty from a paid tool; competitor traffic; a default CTR curve | Only as context, labelled "estimate" |
| `proxy` | A stand-in for the thing of interest | Citability score for citation likelihood; AI referral sessions for AI citations; lab LCP for field LCP | Only with the gap stated |
| `unknown` | Not available | Indexing status without Search Console data | No; report it as missing |

If a decision-critical input is `unknown`, the derived figure is `null` with the reason, never a guess. Example: without impressions data there is no click-potential figure for a page.

## Unknown versus not applicable

For any checklist or rubric, each item has one state:

- **Pass** and **Fail**: evaluated with evidence.
- **Unknown**: could have applied but the evidence was not available (no export, no live check, page not built). It is listed under "not measured", excluded from any ratio, and never counted as Fail or Pass.
- **Not applicable**: does not apply to this site or page (no locales, so no hreflang; no products, so no merchant listings). Excluded from the denominator and not listed as a gap.

Always report coverage next to a ratio ("7 of 9 evaluated items pass; 3 unknown: field data, indexing, AI access live check"). Turning Unknown into Fail punishes missing data; turning it into Pass hides risk.

## Priority meanings

| Priority | Meaning | When |
| --- | --- | --- |
| P0 | Blocks indexing, AI access or rich-result validity site-wide, or ships staging or localhost artifacts | Fix now, before other work |
| P1 | Suppresses visibility on important templates or many pages | This sprint |
| P2 | Hygiene and backlog | When touching the area |
| P3 | Optional, informational or experimental | Only with a reason |

Each rule has a catalog default. The CLI escalates a site-wide P1 to P0 only for the blocker set: [CRAWL004](rule-catalog.md#crawl004), [IDX001](rule-catalog.md#idx001) with `--expect-indexable`, [AI004](rule-catalog.md#ai004), [LAUNCH003](rule-catalog.md#launch003), [LAUNCH004](rule-catalog.md#launch004), [REND001](rule-catalog.md#rend001) on the home page, [SD012](rule-catalog.md#sd012), [CONT004](rule-catalog.md#cont004), [CONT010](rule-catalog.md#cont010) and [HTTP001](rule-catalog.md#http001) on the home page. Severity escalations: IDX001 becomes an error with `--expect-indexable`; the `launch` profile raises [CRAWL001](rule-catalog.md#crawl001) and [SMAP001](rule-catalog.md#smap001) to warnings; [SD007](rule-catalog.md#sd007) never exceeds info.

The agent may raise a priority when business context warrants it (the affected template carries most revenue) and must say why; it never lowers a P0 without the owner's decision.

## Root-cause deduplication

- One rule is one issue with N affected URLs, not N issues. Report the count and a sample.
- Group instances by the template or component that produces them: twelve product pages missing `priceCurrency` are one fix in one template.
- When several rules share one cause (a layout-wide canonical produces [CANON005](rule-catalog.md#canon005) on most pages and [DRIFT003](rule-catalog.md#drift003) against the baseline), report the cause once and list the rule IDs it clears.
- Symptoms downstream of a blocker wait for it: content findings on pages that are `noindex` or client-rendered are re-checked after the blocker is fixed.

Sample by template on large sites: group URLs by route pattern or template (from the build output paths or the router), audit every group with the CLI, and inspect two representative URLs per group by hand for judgment work. Treat a defect found in one sampled page as a template defect until the CLI shows otherwise (heuristic).

## Plan ordering

The fix plan is sorted by, in order:

1. **Priority**, P0 to P3.
2. **Dependency layer**, because later layers cannot pay off until earlier ones hold:

| Layer | Families | Question |
| --- | --- | --- |
| 1 Eligibility | CRAWL, IDX, CANON, HTTP, REDIR, SPAM, LAUNCH, REND, AI | Can search and AI crawlers fetch, render and index the right URL? |
| 2 Understanding | META, HDG, SD, SMAP, HREF | Do engines get correct titles, structured data, discovery and locale signals? |
| 3 Structure and experience | LINK, PSEO, PERF, IMG, VID | Is the site linked, deduplicated, fast and media-complete? |
| 4 Content and GEO | CONT, CITE, LOCAL, AGENT | Is the content trustworthy, quotable and agent-friendly? |

   DRIFT findings take the layer of the signal that changed (a new `noindex` is layer 1, a changed title layer 2).
3. **Impact**, the catalog's high, medium or low.
4. **Affected pages**, most first.
5. **Effort**, the catalog's S, M or L, smallest first.

Then apply judgment, and say so when you do: two items that can ship in either order are marked parallel; an item that needs data or an owner decision is marked blocked with the missing input. The top 3 to 5 items follow [recommendation-contract.md](recommendation-contract.md#recommendation-fields); deliberate deprioritizations go under [what to ignore](recommendation-contract.md#what-to-ignore).

## Profiles

`--profile` changes which checks run and how strict some rules are:

| Profile | Adds | Use for |
| --- | --- | --- |
| `default` | The standard checks | Most audits |
| `launch` | LAUNCH001, LAUNCH003 to LAUNCH005; CRAWL001 and SMAP001 raised to warnings | Pre-launch and post-migration checks |
| `programmatic` | PSEO checks (near-duplicates, templated sections) | Data-generated sections |
| `local` | LOCAL002 and LocalBusiness expectations | Businesses with premises or service areas |
| `ecommerce` | Stricter merchant-listing checks ([SD017](rule-catalog.md#sd017)) | Stores |
| `geo` | Citability analysis on content pages of 150 words or more; `geo` scores by default | GEO-focused audits |
