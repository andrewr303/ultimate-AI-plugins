<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: intent signal words, funnel tags, opportunity and priority formulas, content-gap segments and topic-cluster linking re-expressed in our own words; the priority formula's erroneous division by 5 removed; the gap quick-win effort sign fixed; conversion-rate ranges, CTR benchmarks and CTR-uplift figures removed; every metric tied to provenance labels. See NOTICE.md. -->
# Keyword and content strategy

How to decide which pages to create or improve from real demand data: provenance rules for every metric, intent classification with signal words, funnel tags, fixed opportunity and priority formulas, SERP-overlap clustering, content-gap segments, the Search Console planner buckets with their units, the CTR curve, cannibalization-safe planning, the anatomy of a brief, page-type matching to what ranks, and a short title-pattern list. Used by [seo-keyword-strategy](../skills/seo-keyword-strategy/SKILL.md) and the brief template [content-brief.md](../templates/content-brief.md).

As of 2026-11-01. Facts are cited from [current-facts.md](current-facts.md). All weights, thresholds and bands below are heuristics (ours or adapted from the sources named in NOTICE.md), not search-engine rules.

## Data provenance rules

Every number in a plan carries one label: `measured` (the site's own Search Console, GA4 or logs), `user-provided` (a keyword-tool export the user supplied, with tool, location, language and date), `calculated` (derived by a formula from labelled inputs), `estimated`, `proxy` or `unknown`.

- Never invent search volume, keyword difficulty, CPC, traffic or rankings. If no tool export exists, list keywords without numbers and say why.
- Search Console impressions are not search volume. They count how often the site was shown; a query with 12 impressions may have large demand where the site barely appears.
- Volumes and difficulty from different tools are not comparable; never mix them in one formula.
- An unknown decision-critical input makes a derived score `null`, not zero.
- SERP observations (what ranks, which features show) are recorded with date, engine, country, language and device. They change daily; label them observed, not measured.
- Third-party metrics about competitors are estimates; say so next to the number.

## Intent taxonomy and signal words

Classify each query by its dominant intent, then confirm against the live results when an observation is available; the results page is the ground truth, the words are only a first guess.

| Intent | The searcher wants to | Signal words (first guess) | Formats that usually fit |
| --- | --- | --- | --- |
| Informational | Learn or fix something | what, how, why, guide, tutorial, examples, tips, definition, checklist, steps, troubleshooting phrases | Explainers, tutorials, checklists, reference pages |
| Navigational | Reach a known site or page | brand or product names, login, sign in, docs, support, download, official | Home, product, docs and support pages |
| Commercial investigation | Compare before choosing | best, top, vs, compare, review, alternative, worth it, features, for [audience] | Comparisons, reviews, buying guides, category pages |
| Transactional | Act now | buy, price, pricing, discount, coupon, free trial, demo, sign up, book, hire, near me | Product, pricing, signup, booking and local service pages |

### Mixed intent and common misclassifications

- "best [thing]" is commercial, not informational; "how much does [product] cost" is commercial or transactional; "[service]" alone is often transactional and local; "[brand] blog" is navigational.
- Broad heads ("project management software") are usually mixed: check which page types rank before choosing a format.
- When intent is mixed, answer the dominant need first and link to the page that serves the secondary one; do not cram two page types into one.
- Navigational queries for other brands are not targets, except honest comparison or alternatives pages.

## Funnel tags

A simple, regex-friendly tag for planning (not a metric): **BOFU** for commercial or transactional queries and those containing pricing, best, vs, alternative, review, buy, hire, demo; **MOFU** for how-to, guide, case study, comparison of approaches; **TOFU** for pure informational queries. Use the tag to balance the calendar, never as a conversion estimate.

## Opportunity and priority formulas

### Opportunity score

`opportunity = (volume × intent_value) / difficulty`

- Inputs: `volume` and `difficulty` from one user-provided keyword-tool export (same tool, location and date); `intent_value` 1 informational, 1 navigational, 2 commercial, 3 transactional.
- Compute only when both volume and difficulty are present and difficulty is greater than 0; otherwise the score is `null` with the reason.
- The result ranks keywords inside one export. It is not a traffic forecast and it is not comparable across tools.

### Priority score (weighted)

`priority = Σ(weight × score)`, each factor scored 1 to 5, weights summing to 1.0, so the result stays on the 1 to 5 scale (there is no further division):

| Factor | Weight | Score 1 | Score 5 |
| --- | --- | --- | --- |
| Demand (labelled volume or measured impressions) | 0.20 | low for this site | high for this site |
| Ease (inverse of difficulty) | 0.25 | very hard | easy |
| Business relevance | 0.30 | tangential | core offer |
| Intent match | 0.15 | informational only | commercial or transactional fit |
| Trend | 0.10 | declining | rising |

Bands: P0 4.0 to 5.0; P1 3.0 to 3.9; P2 2.0 to 2.9; P3 1.0 to 1.9. If a factor is unknown, report "not scored" for that keyword instead of filling a default.

### Gap quick-win score (effort sign fixed)

For gaps scored 1 to 5 on demand, business relevance, ease of creation (5 = quick to make) and openness (5 = no competitor covers it):

`quick_win = (demand + relevance) - (effort_cost + coverage)`, where `effort_cost = 6 - ease` and `coverage = 6 - openness`.

Range -8 to +8: 4 or more strong; 2 to 3 moderate; 0 to 1 weak; negative avoid. A quick, uncovered, relevant, in-demand topic scores high; a slow topic every competitor already covers scores low.

## SERP-overlap clustering

Group keywords by how many of the same URLs rank for both in the top 10, not by text similarity:

| Shared top-10 URLs | Decision |
| --- | --- |
| 7 to 10 | Same page: one primary keyword, the other becomes secondary |
| 4 to 6 | Same cluster: separate pages may be justified when intent or demand differs; interlink them |
| 2 to 3 | Adjacent clusters: cross-link only |
| 0 to 1 | Separate topics |

Thresholds adapted from claude-seo (MIT). Rules:

- Compare result sets for the same engine, country, language and device, collected the same day.
- Drop domains that appear for almost every query (large encyclopedias, forums, marketplaces) before counting, or count them separately; they inflate overlap.
- For 3 or 4 shared URLs, break ties with intent (same intent leans toward one cluster) and with demand (a keyword with much larger demand usually earns its own page).
- Pre-group by head term and intent so you do not need every pair; spot-check a sample of skipped pairs.
- Different results-page features (local pack vs a product grid) usually mean different page types even with moderate URL overlap.

## Content-gap segments

Compare the site's keyword set (Search Console export, `measured`) with one or more competitor keyword exports (`user-provided`, estimates):

| Segment | Meaning | Action |
| --- | --- | --- |
| Only you rank | Moat | Protect: keep fresh, strengthen internal links |
| Both rank, competitor at least 5 positions ahead | Battleground (behind) | Improve the existing page before creating anything |
| Both rank, you ahead | Battleground (ahead) | Monitor |
| Only competitor ranks (top 20) | Gap | Create or extend a page if it fits the business |
| Nobody ranks | Untapped | Validate demand before investing |

Drop competitor brand terms unless the owner wants honest comparison pages, which are planned separately ([content-quality-rubrics.md](content-quality-rubrics.md#comparison-page-fairness)). Every gap names the competitor that covers it and the evidence row.

## Planner buckets A to E

`SG gsc buckets query_page.json --dimensions query,page` reads query-by-page rows covering about 90 days and assigns buckets with these heuristic defaults (from `data/thresholds.json`, adapted from the notfair-plugin planning method, MIT):

| Bucket | Condition | Planned action |
| --- | --- | --- |
| A Striking distance | Average position 5 to 20, at least 100 impressions in the window, intent fits content | New page or substantial refresh aimed at the exact query |
| B Unanswered | Average position numerically over 20, at least 50 impressions, no page of the site in the top 20 | New page, only if the topic fits the business |
| C CTR underperformer | Position 1 to 10, at least 500 impressions, CTR below half of the expected CTR at that position | Title, description and snippet work first ([seo-metadata](../skills/seo-metadata/SKILL.md)), body refresh second |
| D Related expansions | Related queries from the same query-by-page cluster as an A or B parent | Secondary keywords and H2 candidates on the parent, not their own pages |
| E Cannibalization warning | Same query at an average position numerically under 20 for two or more pages, each with at least 20 impressions | Do not plan new content for it; resolve which page owns it first |

### Click potential (units)

For A and B rows the planner reports an upper-bound estimate:

```text
click_potential_90d     = impressions_90d × seasonality × expected_ctr(target position 3) - clicks_90d
click_potential_monthly = click_potential_90d / (window_days / 30)
```

- Units: clicks per 90-day window and clicks per 30 days. The monthly figure is the 90-day figure divided by 3 for a 90-day export; never label a 90-day number "monthly".
- `seasonality` is 1.0 unless the site's own year-over-year data supports another value; state it when used.
- `expected_ctr` comes from the site-calibrated curve when available (next section), otherwise from the heuristic default.
- Label the result `calculated`, upper bound, not a forecast. Ties within 10%: prefer refreshes over new pages, then commercial fit, then topics where the site already has authority.

## CTR curve (site-calibrated, heuristic default)

- Prefer the site's own curve: `SG gsc ctr pages.csv --calibrate` computes expected CTR by rounded position from the export (positions with too few impressions are skipped).
- Without calibration the CLI uses a default curve stored in `data/thresholds.json`, labelled "heuristic default"; it is adapted from published informational-intent medians and pre-AI-Overview-era studies may overstate CTR.
- AI summaries change click behavior: Pew found users clicked a result in 8% of Google visits with an AI summary versus 15% without one (independent research, March 2025 data) ([F-AI-33](current-facts.md#f-ai-33)). AI Mode traffic is included in Search Console totals ([F-T-50](current-facts.md#f-t-50)). A low CTR may be an answer feature, not a bad title.
- Never quote CTR-uplift percentages for title tricks; no reliable source supports them.

## One primary keyword per page

- Each planned page owns one primary keyword and a few secondary ones; a primary keyword appears once in the whole plan.
- Before adding a page, check `SG gsc cannibalization query_page.json --dimensions query,page`: if two pages already split a query, the plan consolidates or differentiates them; it never adds a third.
- Prefer expanding an existing page that half-covers a topic over creating a new one.
- Do not create one page per phrasing; Google warns that mass pages for query variants can be scaled content abuse ([F-AI-12](current-facts.md#f-ai-12)).

## Topic clusters and internal links

- A pillar page covers the topic broadly and links to every cluster page; each cluster page links back to the pillar and to two or three siblings, with descriptive anchors in the body text.
- Build order: pillar, then the quickest wins from bucket A, then the highest-demand cluster pages, then the long tail; refresh the pillar as clusters ship.
- A pillar is viable when there are enough distinct subtopics the business can write about credibly (roughly eight or more, heuristic); otherwise make one strong page.
- Link mechanics and orphan checks belong to [seo-site-architecture](../skills/seo-site-architecture/SKILL.md).

## Brief anatomy

A brief ([content-brief.md](../templates/content-brief.md)) is good enough to write from when it has:

1. Target and secondary queries, each with source and label.
2. Intent and format inferred from what ranks, with the observation's date, engine, country and device.
3. An outline in which every section has a one-line note on what it must say.
4. Questions to answer (from People also ask observations, Search Console question queries, support tickets).
5. Table stakes (what every ranking page covers) and the differentiating angle (what none covers and the site can credibly add).
6. Entities, facts and sources to cite, each verified or marked `[needs source]`.
7. Internal links: three to five existing pages with suggested anchors, and whether the page is a hub or a spoke.
8. Length guidance: roughly the median of ranking pages of the same type, as a heuristic; do not pad.
9. An answer-first passage plan for the questions most likely to be quoted (hand detailed passage work to [geo-citability](../skills/geo-citability/SKILL.md)).
10. A relevance check: every heading is something this site can deliver; remove sections borrowed from competitors that the business does not offer.

## Page-type taxonomy (SXO)

Classify the target page and each ranking result into one type; when several apply, use this priority: tool or calculator, local, comparison, product, landing page, service page, hybrid, article (adapted from claude-seo SXO method, MIT).

| Type | Primary signals |
| --- | --- |
| Tool | A working calculator, checker or generator above the fold |
| Local | Address, map, hours, service area |
| Comparison | Comparison table, "vs" framing, several options |
| Product | Price, add-to-cart or buy button, specifications |
| Landing page | One offer, prominent call to action, little navigation |
| Service page | Service description, process, case studies, contact or quote form |
| Hybrid | Educational content with a strong commercial call to action |
| Article | Byline, date, long-form explanation |

Consensus: if more than 60% of the top results share a type, match it; 40 to 60% is mixed; below 40% is fragmented. Mismatch severity: an article targeting a query where products rank is critical; an article where comparisons rank is high; a landing page where tools rank is high; a service page where local results dominate is medium. Fix a mismatch by building the right page type, not by adding words.

## Title pattern list

Short patterns that describe the page (no CTR-uplift claims; Google truncates titles to the device width and states no character limit, [F-T-38](current-facts.md#f-t-38)):

- `[Topic]: [specific outcome or scope]`
- `How to [task] ([constraint or audience])`
- `[A] vs [B]: [the real difference]`
- `[N] [items] for [audience or use case]` (only when the page lists exactly N)
- `[Product or service] in [city] | [Brand]` (only for a real location)
- `[Product]: [key attribute] | [Brand]`

Brand once, with a delimiter. Use a year only when the content is updated for that year ([META012](rule-catalog.md#meta012)). Emission mechanics belong to [seo-metadata](../skills/seo-metadata/SKILL.md).

## Calendar rules

- Default cadence is what the team can actually produce; padding the calendar with weak topics is worse than a short list. A three-month plan rarely needs more than about a dozen topics (heuristic).
- P0 topics (highest click potential or priority) go first; refreshes can run in parallel with new pages.
- Record per entry: id, title, primary keyword, secondary keywords, intent, type (new, refresh, consolidate), bucket, evidence (position, impressions, clicks, window, labels), click potential with units, target URL, status `planned`, `in-progress`, `ready-for-review`, `published`. The agent never sets `published`; the owner does after it goes live.
- Store plans under `.seo-geo-god/plans/` (gitignored unless the team wants them committed).

## Needs verification

- Keyword-tool volumes and difficulty scales differ by vendor and change methodology; record the export date and tool version.
- Whether a given query shows an AI Overview or AI Mode entry point changes by day, location and account; observations are point-in-time.
- The default CTR curve's origin data predates widespread AI Overviews; calibrate on the site's own export before trusting click potential.
