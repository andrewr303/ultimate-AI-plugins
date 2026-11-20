# Content brief: [REPLACE: working title]

Fill every `[REPLACE: …]` field. Write "unknown" where data is missing; never estimate a number. Rules for each field: [keyword-and-content-strategy.md](../references/keyword-and-content-strategy.md#brief-anatomy). Quality bar for the draft: [content-quality-rubrics.md](../references/content-quality-rubrics.md).

| Field | Value |
| --- | --- |
| Brief ID | [REPLACE: brief-YYYYMMDD-slug] |
| Target URL | [REPLACE: existing URL to expand, or proposed new path] |
| Mode | [REPLACE: new page / expand existing / refresh / consolidate] |
| Owner and reviewer | [REPLACE: names or roles confirmed by the site owner] |
| Brief date | [REPLACE: YYYY-MM-DD] |
| Status | draft |

## 1. Queries and provenance

| Query | Role | Metric | Value | Label | Source and window |
| --- | --- | --- | --- | --- | --- |
| [REPLACE: primary query] | primary | impressions (90 days) | [REPLACE] | measured | [REPLACE: Search Console export file, date range, property] |
| [REPLACE: primary query] | primary | volume | [REPLACE or unknown] | user-provided | [REPLACE: tool, location, language, export date] |
| [REPLACE: secondary query] | secondary | position | [REPLACE] | measured | [REPLACE] |

- Search Console impressions are not search volume.
- Planner bucket (if any): [REPLACE: A striking distance / B unanswered / C CTR underperformer / D related expansion]; click potential [REPLACE] clicks per 90 days, [REPLACE] per 30 days (calculated, upper bound).
- Cannibalization check: [REPLACE: result of `SG gsc cannibalization` for these queries; pages that already rank].

## 2. Intent and format from ranking evidence

| Observation | Value |
| --- | --- |
| Engine, country, language, device | [REPLACE: e.g. Google, US, en, mobile] |
| Observed on | [REPLACE: YYYY-MM-DD; who observed it: user, host web search, provider export] |
| Dominant intent | [REPLACE: informational / navigational / commercial / transactional; mixed?] |
| Dominant page type in the top results | [REPLACE: article / comparison / product / tool / local / service / landing / hybrid] and share [REPLACE: e.g. 7 of 10] |
| Results-page features seen | [REPLACE: AI Overview, People also ask, video, local pack, shopping, none] |
| Our page type | [REPLACE] (mismatch? [REPLACE: none / medium / high / critical]) |

## 3. Audience and job

- Reader: [REPLACE: who, what they already know]
- Job: [REPLACE: what the reader must be able to do or decide after reading]
- Why this site can credibly answer: [REPLACE: product, service, first-hand experience, data the site owns]

## 4. Table stakes vs angle

- Table stakes (what every ranking page covers): [REPLACE: list]
- Differentiating angle (what none covers and this site can add): [REPLACE: original data, tested process, local knowledge, expert review]
- Out of scope (say so on the page if readers might expect it): [REPLACE]

## 5. Outline (each section says what it must say)

| Heading | Must say | Format | Evidence or source |
| --- | --- | --- | --- |
| H1: [REPLACE] | [REPLACE: the promise the page keeps] | | |
| Opening answer (first paragraph) | [REPLACE: the direct answer to the primary query in plain words] | 2 to 4 sentences | [REPLACE] |
| H2: [REPLACE] | [REPLACE] | [REPLACE: steps / table / list / prose] | [REPLACE] |
| H2: [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |
| H2: [REPLACE] | [REPLACE] | [REPLACE] | [REPLACE] |

## 6. Questions to answer

| Question | Where it came from | Section |
| --- | --- | --- |
| [REPLACE] | [REPLACE: People also ask observation (date), Search Console query, support ticket, sales call] | [REPLACE] |

## 7. Answer-first passage plan

For the two or three questions most likely to be quoted, plan a self-contained passage: the question as a heading, the answer in the first sentence, then the supporting detail. Detailed passage work is done with geo-citability after drafting.

| Question | Answer sentence plan | Supporting fact and source |
| --- | --- | --- |
| [REPLACE] | [REPLACE] | [REPLACE or `[needs source]`] |

## 8. Entities, facts and sources

| Claim or entity | Source URL | Verified by and date |
| --- | --- | --- |
| [REPLACE] | [REPLACE: primary source] | [REPLACE: name, YYYY-MM-DD, or `[needs source]`] |

No statistics, quotes, reviews or credentials without a source the owner accepts.

## 9. Trust signals

- Author: [REPLACE: real person and author page, confirmed by the owner, or "organization byline"]
- Reviewer (required for YMYL topics): [REPLACE or not applicable]
- Disclosures: [REPLACE: affiliate, sponsorship, own product in a comparison, AI assistance]
- Compliance gate needed: [REPLACE: yes or no; official sources if yes]

## 10. Internal links

| Direction | Page | Suggested anchor |
| --- | --- | --- |
| From this page to | [REPLACE: existing URL] | [REPLACE] |
| To this page from | [REPLACE: existing URL] | [REPLACE] |

Hub or spoke: [REPLACE]. Pillar page: [REPLACE or none].

## 11. Length and metadata guidance

- Length: about [REPLACE: median word count of ranking pages of the same type] words (heuristic; do not pad).
- Title idea: [REPLACE: describes the page; brand once; year only if the content is updated for it]
- Description idea: [REPLACE: what the page gives the reader]
- Structured data type: [REPLACE: e.g. Article, Product, LocalBusiness, none] (only for what the page shows)

## 12. Definition of done

- [ ] Draft follows the outline and answers the primary query in the opening paragraph.
- [ ] Every claim in section 8 is sourced or removed.
- [ ] `SG content-lint <file>` shows no errors and no unexplained warnings.
- [ ] Built page passes `SG audit-build <dir> --base-url <origin>` with no new errors.
- [ ] Owner reviewed claims, author information and disclosures.
