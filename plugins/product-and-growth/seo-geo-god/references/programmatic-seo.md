<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: page-pattern table, data defensibility tiers, guardrail checklist and remediation ladder re-expressed in our own words; semantic-variant cycling removed; thresholds relabelled as heuristics and tied to SEO-GEO-god rules and Google spam-policy facts. See NOTICE.md. -->
# Programmatic SEO

How to generate many pages from structured data so that each page is worth indexing on its own: tests a dataset must pass first, how defensible different data sources are, page patterns and what makes each one unique, guardrails with labelled heuristic thresholds, index management, phased rollout, provenance labels and the patterns that are spam. Used by [seo-programmatic](../skills/seo-programmatic/SKILL.md); policy background is in [search-policies.md](search-policies.md).

As of 2026-11-01. Facts are cited from [current-facts.md](current-facts.md). Every threshold below is a heuristic (ours or adapted from the sources in NOTICE.md), not a Google number. Google publishes no page-count or similarity limit.

## Why this needs care

Google's spam policies define scaled content abuse as generating many pages primarily to manipulate search rankings, however they are produced ([F-T-32](current-facts.md#f-t-32)). Its generative-AI optimization guide adds that mass-producing pages for query variations to manipulate generative AI responses can be scaled content abuse ([F-AI-12](current-facts.md#f-ai-12)). AI-written content is allowed when it is helpful and fact-checked; mass generation without added value is the risk ([F-T-37](current-facts.md#f-t-37)). Programmatic pages are fine when every page answers a real need with real, page-specific data.

## Value tests

Answer these before generating anything. One "no" stops the build until it is fixed.

1. **Real per-row data.** Does every row carry specific facts a visitor wants (prices, specifications, schedules, measurements, setup steps, inventory, local details), not only a name?
2. **Value beyond substitution.** Would two pages still differ in substance if the row's name were removed from both?
3. **Standalone value.** Would this page be worth publishing even if no sibling pages existed?
4. **Demand evidence.** Is there evidence people look for these pages (the owner's Search Console queries, internal site search, keyword-tool exports, sales questions)? Never invent search volumes.
5. **Ownership.** Who keeps the data accurate, and how often does it change?
6. **Empty cases.** What happens when a row lacks the fields that make it useful? (Answer: the page is not generated, or returns 404.)

## Data defensibility tiers

The more of the data only this business can produce, the less the pages resemble everyone else's:

| Tier | Source | Example | Risk |
| --- | --- | --- | --- |
| 1 | Produced by the product itself | Rendered templates, generated previews, conversion results | Lowest, when each URL shows distinct output |
| 2 | Derived from the business's own aggregated data | Benchmarks or usage statistics computed from owned data, aggregated and anonymized | Low, if aggregation and privacy rules are met |
| 3 | Contributed by users or customers | Moderated reviews, submissions, portfolios | Medium; needs moderation, consent and real authorship |
| 4 | Licensed or partner data | Partner feeds, licensed datasets | Medium; contract scope, attribution, trademarks |
| 5 | Public or scraped data | Directory listings, generic facts everyone has | Highest; needs a real editorial layer, analysis or tool on top, or should not become pages |

Tier 5 alone with nothing added (no synthesis, calculator, comparison or editorial judgment) is commodity content: do not generate the URL set.

## Page patterns

Each pattern names what must differ per page. A pattern with only the name changing fails the value tests.

| Pattern | URL shape (example) | What must be unique on each page |
| --- | --- | --- |
| Templates or assets | `/templates/<type>/` | A usable asset, variations, instructions |
| Curated lists | `/best/<category>/` | Stated evaluation criteria, dated updates, real evaluation per item |
| Converters or calculators | `/convert/<from>-to-<to>/` | A working tool, correct current data, related conversions |
| Comparisons | `/compare/<a>-vs-<b>/` | Real feature data with dates and sources, balanced assessment, disclosure of affiliation |
| Examples or galleries | `/examples/<type>/` | Real examples with analysis |
| Locations | `/<service>/<city>/` | Actual local facts: staff, hours, service area, local prices, directions; never a city-name swap. Single-business location pages also follow [local-seo.md](local-seo.md) |
| Audiences | `/for/<audience>/` | Features, workflows and proof specific to that audience |
| Integrations | `/integrations/<product>/` | Real setup steps, supported actions, limits; nothing that does not exist |
| Glossary | `/glossary/<term>/` | An accurate definition, examples, related terms |
| Translations | `/<locale>/<page>/` | Reviewed translation and localization with hreflang ([international.md](international.md)) |
| Directories | `/directory/<category>/` | Complete, current listings with useful detail and filtering |
| Profiles | `/people/<name>/` | Sourced, accurate facts and an aggregation not available elsewhere |

URL rules: lowercase, hyphenated slugs built from stable data fields; unique slugs enforced at generation time; no query parameters for primary pages; one trailing-slash policy; keep URLs readable rather than stuffed with modifiers.

## Guardrails

| Guardrail | Heuristic threshold or practice | How it is checked |
| --- | --- | --- |
| Human review before scale | 100 or more new pages: review a sample of generated pages before publishing | Owner sign-off recorded in the report |
| Hard stop | 500 or more pages without per-page data: stop and require a written justification from the owner | Agent gate |
| Near-duplicates | Text similarity of 0.85 or more between pages of a section | [PSEO001](rule-catalog.md#pseo001) |
| Shared phrases | A phrase appearing on more than 30% of a section's pages | [PSEO002](rule-catalog.md#pseo002) (planned; agent check until then) |
| Thin sections | Many short templated pages in one section | [PSEO003](rule-catalog.md#pseo003) (planned; agent check) |
| Duplicate metadata | Same title or description on several pages | [META003](rule-catalog.md#meta003), [META005](rule-catalog.md#meta005) |
| Templated metadata | One generated title or description shape on every page | [META006](rule-catalog.md#meta006) |
| Evidence block | Every page shows the row's distinguishing facts in server HTML, with a source and date where they change | Template review, sample pages |
| Conditional sections | Sections whose fields are empty are omitted, not filled with "N/A" or generic filler | Template review |
| Empty combinations | Not generated, or 404 | `SG audit-build`, route code |
| Numbers and claims | Generated text never introduces numbers, ratings, reviews, quotes or citations that are not in the row data | Sample review; [CONT001](rule-catalog.md#cont001) |

How to measure similarity sensibly: compare the main content only (exclude shared header, footer and navigation), but count template boilerplate inside the main content, because that is what makes pages interchangeable. Score metadata separately from body text.

## Index management

- Index only rows that pass the value tests. Low-value variants get `noindex` (and stay crawlable so the directive can be seen, [CRAWL008](rule-catalog.md#crawl008)) or are not generated at all.
- Keep noindexed and non-canonical pages out of sitemaps ([SMAP008](rule-catalog.md#smap008)). Segment sitemaps per section so indexing can be followed per section; respect the 50,000 URL and 50 MB limits ([F-T-27](current-facts.md#f-t-27)).
- `lastmod` is the time the row's data really changed, not the build time ([SMAP006](rule-catalog.md#smap006)).
- Every page has a self-referencing canonical. If a hand-written page covers the same need, it is the canonical and the generated one is removed or redirected.
- Filters and sorts on generated listings follow the faceted-navigation options ([F-T-26](current-facts.md#f-t-26)); paginated listings keep self-canonical pages with crawlable links ([F-T-25](current-facts.md#f-t-25)).
- Crawl budget only becomes a concern on very large or fast-changing sites ([F-T-29](current-facts.md#f-t-29)); index bloat from thin pages is a quality problem long before it is a crawl problem.
- Link generated pages from hub pages and from related pages that share real attributes; no orphaned sets ([LINK002](rule-catalog.md#link002)).

## Rollout

1. Build a preview set (for example 20 to 50 representative rows, including the thinnest ones) and audit it with `SG audit-build dist --base-url https://example.com --profile programmatic`.
2. Have a person review a sample against the value tests; record who reviewed and when.
3. Publish a first batch. Batch size is a choice; small enough that problems can be traced to one batch.
4. Watch indexing for that section in the owner's Search Console exports before the next batch. Waiting periods are heuristics; weeks, not days, is a reasonable default.
5. Expand only while indexed share and engagement hold up; stop and fix templates when they do not.

## Provenance and freshness labels

- Store the source and retrieval date per field, not only per dataset.
- Show "as of" dates on the page for values that change (prices, availability, ratings from a named source, schedules).
- Set a freshness window per field type (for example prices more often than descriptions); the windows are the owner's decision and should be written down.
- When data expires and is not refreshed, hide the value instead of showing a stale one.

## AI-assisted generation

- AI may shape phrasing, section order and explanations from the row's data. It never invents numbers, ratings, reviews, citations, quotes, people or availability.
- Fact-check AI output, including titles, descriptions, structured data and alt text, before publishing ([F-T-37](current-facts.md#f-t-37)).
- Label how content is produced when that helps readers understand it.
- Prompts and generated text never contain instructions aimed at AI systems ([CONT010](rule-catalog.md#cont010)).

## Prohibited patterns

- City-name or product-name swaps over identical text (doorway pages).
- Rewording, synonym rotation or sentence shuffling to slip past duplicate detection. Fix duplication by adding real differences or by not generating the page.
- Pages generated for query variations to capture AI answers or rankings without new value ([F-AI-12](current-facts.md#f-ai-12), [F-T-32](current-facts.md#f-t-32)).
- Scraped or lightly rewritten third-party content.
- Third-party content hosted to exploit the host's ranking signals; Google's site reputation policy applies, with manual actions having no effect for EEA users since 2026-08-30 but still applying elsewhere ([F-T-34](current-facts.md#f-t-34)).
- Review or rating markup on generated aggregate pages without real, visible reviews ([structured-data-matrix.md](structured-data-matrix.md)).

## Remediation ladder

For sections already live and interchangeable:

| Priority | Situation | Action |
| --- | --- | --- |
| P0 | Pages with no page-specific information | Remove (404 or 410), merge into a hub, or noindex until real data exists |
| P1 | Correct data but formulaic delivery | Rewrite the template around the row's distinguishing facts; add the evidence block |
| P2 | Repeated phrases or boilerplate inflating similarity | Cut shared boilerplate; move shared explanations to one hub page and link to it |

Fix one section at a time, re-run `SG audit-build` with `--profile programmatic` after each round, and record the before and after counts.

## Needs verification

- Google has not published thresholds for page counts, similarity or rollout speed; all numbers here are heuristics and should be calibrated on the site's own indexing data.
- Reports of specific enforcement waves against programmatic sites are third-party only.
