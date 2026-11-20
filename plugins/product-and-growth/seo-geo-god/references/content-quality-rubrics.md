<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: content-decay signals, composite decay score, refresh-versus-retire options and the auto-fix versus ask-first split re-expressed in our own words; republish-date rule corrected to keep datePublished; component scoring and missing-data handling added; CTR benchmarks removed; CORE-EEAT credited as a concept only, without item texts. See NOTICE.md. -->
# Content quality rubrics

How to judge, write and refresh page content for people first: a review checklist built on Google's "Who, How, Why" questions and E-E-A-T, calibration anchors so scores spread across the scale, the extra bar for YMYL and regulated topics, Google's position on AI-assisted content, what the deterministic content lint catches, content-decay signals with a heuristic composite, the refresh, rewrite or retire decision, date honesty, comparison-page fairness and the line between edits an agent may make alone and edits that need the owner. Used by [seo-content](../skills/seo-content/SKILL.md); passage-level rewrites for AI citability live in [citability-and-rewrite.md](citability-and-rewrite.md).

As of 2026-11-01. Facts are cited from [current-facts.md](current-facts.md). Every number in this file that is not cited to a fact is a heuristic (ours or adapted from the sources in NOTICE.md), not a Google rule. Rubric scores are structured judgment by the host agent; two runs may differ, so report them as judgment, never as measurement.

## How to use these rubrics

1. Run the deterministic layer first: `SG content-lint <files> --recursive` and, for built pages, `SG audit-build <dir> --base-url <origin>`. Those findings are reproducible.
2. Then apply the judgment layer below: the people-first checklist, the E-E-A-T signals and, when the user wants a number, the scoring sheet with calibration anchors.
3. Label every observation as measured (from the CLI or the user's data), user-provided, or judged. Unknown is not a failure: if author credentials cannot be checked from the repository, write "unknown", not "missing".
4. Never score off-page factors (links, mentions, brand demand) from the page itself.

## People-first checklist (Who, How, Why)

Our checklist, inspired by Google's "Who, How, Why" questions in its people-first content guidance (page linked under "Candidate facts"; it was not re-read in the 2026-11-01 pass). Helpful content is part of Google's core ranking systems since March 2024 ([F-T-35](current-facts.md#f-t-35)).

| Question | Look for in the repository | Weak signal |
| --- | --- | --- |
| **Who** made it? | A byline that links to an author page with real role and relevant experience; an organization page; an editor or reviewer where readers expect one | No author on a page where readers would ask; invented personas; stock "Editorial Team" on YMYL topics |
| **How** was it made? | First-hand testing, photos or data the site produced; methodology notes for reviews and comparisons; disclosure of automation where readers would ask | Rewrites of other pages; generic claims; AI drafts published without fact-checking |
| **Why** does it exist? | A page the site's audience would want even without search traffic | Pages made to target a keyword the business has no expertise in; padding to reach a word count; date bumps for freshness |

Ask also: does the page answer the main question near the top; would a reader need to search again; does it add something that pages already ranking do not (original data, experience, a clearer method); is every factual claim sourced or plainly the site's own observation?

## E-E-A-T signal checklist

E-E-A-T is a framework from Google's search quality rater guidelines, not a score Google computes. Use it to find what a page is missing, not to predict ranking.

| Signal | Evidence an agent can check in code or content |
| --- | --- |
| Experience | First-person process descriptions, original photos or screenshots, results the author measured, limitations encountered |
| Expertise | Author page with relevant role, qualifications stated only if true, correct terminology, depth appropriate for the audience |
| Authoritativeness | Citations to primary sources; the site's own research cited by others (off-page, only from user-supplied data) |
| Trust (the most important) | Accurate claims with sources, visible dates, contact and company details, editorial and corrections policy, disclosures of affiliate or sponsored relationships, HTTPS, no misleading UX |

Author and reviewer information is added only when it is true and the owner confirms it. Never invent a person, a credential, a quote or a review to satisfy this checklist.

## Calibration anchors

Use the full 0 to 10 range per dimension. Most pages are not a 5 to 7. Anchors (our wording of a common pattern):

| Score | What it looks like |
| --- | --- |
| 2 | Template text with a swapped name, no author, no unique facts, no sources, stock images |
| 5 | Covers the topic adequately, adds nothing new, basic metadata, no author information, few or no sources |
| 8 | Original examples or data, a credited author with relevant experience, clear structure, sourced claims, accurate structured data, useful internal links |
| 10 | The reference others cite: original research or unique data, expert authorship, nothing to fix technically |

### Review scoring sheet (optional)

Score each dimension 0 to 10 with one line of evidence; the weighted mean is Σ(weight × score) with weights summing to 1.0. Weights are opinionated defaults, adapted from the notfair-plugin page rubric (MIT).

| Dimension | Weight | Evidence to cite |
| --- | --- | --- |
| Intent fit | 0.20 | Page type and format match what ranks for the query (see [keyword-and-content-strategy.md](keyword-and-content-strategy.md#page-type-taxonomy-sxo)) |
| E-E-A-T signals | 0.20 | Table above |
| Depth and originality | 0.20 | What the page adds that ranking pages lack |
| On-page clarity | 0.15 | Title, H1 and description describe the page; headings structured ([HDG001](rule-catalog.md#hdg001) to [HDG003](rule-catalog.md#hdg003)) |
| Structure and readability | 0.15 | Answer near the top, scannable sections, tables for comparisons |
| Technical | 0.10 | Indexable, rendered in server HTML, no CLI errors |

A YMYL page that scores 7 is still a failing grade until the compliance gate passes. If any dimension is unknown, report the sheet without the weighted mean.

## YMYL and regulated topics

"Your money or your life" topics (health, finance, legal, safety, civic information, and anything where a wrong answer can hurt a person) need the highest bar:

- a named author or reviewer with relevant, verifiable qualifications, confirmed by the owner;
- primary sources for every rule, dose, rate, deadline or eligibility condition;
- visible dates and a review cadence the owner commits to;
- disclaimers that match the jurisdiction, written or approved by the owner (not legal advice from the agent).

## Compliance gate

Apply before publishing anything with official rules, deadlines or eligibility (travel and immigration documents, tax and filing, licensing, regulated products, benefits, health certificates). Adapted from the notfair-plugin content-writing guidance (MIT):

1. Link the current official source for each rule-making body involved.
2. Separate official requirements from advice; do not soften a mandatory step to "may be required" unless the official source defines exceptions.
3. State timing windows, exceptions and scope (which country, direction, program, product).
4. Add a freshness caveat telling readers to confirm with the official source before acting.
5. If the page has a calculator, estimator or checklist, encode the rules and caveats in the tool, not only in the prose.
6. Treat an unsourced compliance claim, an ambiguous requirement or a missing official link as a blocker, not a polish item.

## AI-assisted content policy

- Google allows AI-generated content that meets Search Essentials and the spam policies; mass generation without added value can be scaled content abuse; AI output must be fact-checked, including titles, descriptions, structured data and alt text ([F-T-37](current-facts.md#f-t-37)). Policy details: [search-policies.md](search-policies.md#ai-generated-content-guidance).
- Explain how content was produced where readers would reasonably ask (for example, a methodology note on a review).
- Style lint for filler and hype ([CONT002](rule-catalog.md#cont002), [CONT008](rule-catalog.md#cont008)) is a writing signal, never "AI detection". No tool reliably detects AI authorship or removes statistical watermarks; do not claim otherwise.
- Invisible-character cleanup ([CONT003](rule-catalog.md#cont003)) is for the user's own drafts. Decline requests to strip provenance markers from content the user does not own.

## What the content lint catches

| Rule | Catches | Typical fix |
| --- | --- | --- |
| [CONT001](rule-catalog.md#cont001) | Numbers, or appeals to unnamed studies or experts, without a nearby citation | Link the source, narrow the claim, or mark `[needs source]` for the owner |
| [CONT002](rule-catalog.md#cont002) | High density of filler phrases | Cut the phrase; say the thing |
| [CONT003](rule-catalog.md#cont003) | Zero-width, bidi-control or tag characters | Strip them (emoji sequences are preserved) |
| [CONT004](rule-catalog.md#cont004) | Leftover AI, editor or template artifacts (assistant self-references, `[INSERT …]`, `TODO:`, lorem ipsum) | Remove before publishing; this is an error |
| [CONT005](rule-catalog.md#cont005) | Stale years or an undated "updated" claim | Update the substance and the date, or remove the claim |
| [CONT007](rule-catalog.md#cont007) | Paragraphs opening with "it", "this" or "these" without a referent | Name the subject so the paragraph stands alone |
| [CONT008](rule-catalog.md#cont008) | Unsupported superlatives and hype | Replace with a specific, sourced claim or drop it |
| [CONT009](rule-catalog.md#cont009) | Citation markers with no target | Add the reference or remove the marker |
| [CONT010](rule-catalog.md#cont010) | Text addressed to AI systems with instructions | Remove; this is an error |
| [META012](rule-catalog.md#meta012) | Obsolete year in title or H1 | Update only if the content was updated for that year |
| [HDG001](rule-catalog.md#hdg001) to [HDG003](rule-catalog.md#hdg003) | Missing H1, skipped levels, content without headings | Fix the heading structure in the template or content |
| [CITE001](rule-catalog.md#cite001) to [CITE003](rule-catalog.md#cite003) | Low passage citability, unanswered question headings, no self-contained passages | Hand passage rewrites to [geo-citability](../skills/geo-citability/SKILL.md) |

[CONT006](rule-catalog.md#cont006) (thin content for page type) is planned. Google states no preferred word count; any word floor is a heuristic for "did we cover the topic", never a target.

## Decay signals and composite (heuristic)

A page is decaying when its own data shows a sustained decline, not when it is merely old. Detection runs on the user's exports through [search-data-analysis](../skills/search-data-analysis/SKILL.md): `SG gsc decay current.csv previous.csv` flags pages whose clicks fell by more than 30% between equal windows with at least 10 clicks in the earlier window (heuristic defaults in `data/thresholds.json`). Rule out seasonality (compare the same window a year earlier), tracking changes, technical regressions and update dates before calling it decay.

Component bands, each scored 0 (no signal) to 100 (strongest):

| Component | Weight | 0 | 25 | 50 | 75 | 100 |
| --- | --- | --- | --- | --- | --- | --- |
| Clicks change vs previous equal window | 0.30 | under 10% down | 10 to 20% | 20 to 40% | 40 to 60% | over 60% |
| Average position lost (impression-weighted) | 0.25 | under 1 | 1 to 3 | 3 to 5 | 5 to 10 | more than 10, or off page 1 |
| CTR change at a similar position | 0.15 | under 20% down | | 20 to 40% | | over 40% |
| Freshness of the substance | 0.15 | updated in the last 12 months, or evergreen | | 12 to 24 months on a time-sensitive topic | | over 24 months, or undated, on a time-sensitive topic |
| Competitive displacement (observed SERP) | 0.15 | no change | | a new result above the page | | the page lost its spot to several new results or to an answer feature |

Composite = Σ(weight × component). Compute it only when all five components are measured or observed; otherwise report the component table and decide with the rules in the next section. Stages: 0 to 20 healthy; 21 to 40 early decay (queue a refresh); 41 to 60 active decay (refresh now); 61 to 80 significant (refresh or rewrite); 81 to 100 terminal (rewrite, consolidate or retire). Very large drops across many pages at once point to a technical or sitewide cause, not decay: hand them to [seo-technical](../skills/seo-technical/SKILL.md) first.

Re-check cadence by content type (heuristic): statistics roundups and tool comparisons every 3 to 6 months; how-to guides yearly; evergreen guides every 12 to 18 months; news is not refreshed; case studies rarely.

## Refresh vs rewrite vs retire

| Decision | When | What to do in the repository |
| --- | --- | --- |
| Refresh | The URL ranked or earned links, the intent is unchanged, under half the content needs work | Update facts, sources, examples and missing sections in place; keep the URL |
| Rewrite | The intent behind the query changed, or more than half the content is wrong or missing, or it never ranked | Rewrite at the same URL when the topic is the same; otherwise treat it as a new page |
| Consolidate | Several weak pages on one topic split clicks (confirm with `SG gsc cannibalization`) | Merge the best parts into the strongest URL; 301 the others to it ([seo-migrations](../skills/seo-migrations/SKILL.md)) |
| Redirect | The page has links or residual traffic but no future | 301 to the closest equivalent page, never to the home page by default ([REDIR005](rule-catalog.md#redir005)) |
| Noindex | Needed by users (utility, internal) but not useful in search | Keep crawlable with `noindex` ([seo-technical](../skills/seo-technical/SKILL.md)) |
| Remove (410 or 404) | No value, no links, no traffic, no replacement | Return 410 or 404 and remove from sitemaps |

Redirects, noindex and removals need the owner's approval: they change traffic the agent cannot see.

## Date honesty

- Keep `datePublished` (and the visible "Published" date) as the date the piece first appeared. A refresh does not make an old article new.
- Change `dateModified`, the visible "Updated" date and the sitemap `lastmod` only for substantive changes to main content, facts, structured data or links. Typo fixes, styling and template changes do not count. Google uses `lastmod` only when it is consistently accurate ([F-T-27](current-facts.md#f-t-27)).
- Never bump a year in a title or H1 without updating the content for that year; Google may rewrite titles with obsolete dates ([F-T-38](current-facts.md#f-t-38)), and the CLI reports [META012](rule-catalog.md#meta012) and [CONT005](rule-catalog.md#cont005).
- Dates come from the content source (front matter, CMS fields), not from build time; uniform build-time dates are reported as [SMAP006](rule-catalog.md#smap006).

## Comparison-page fairness

For "X vs Y", "alternatives to X" and "best X" pages. Adapted from claude-seo (MIT) and aaron-marketing-skills (Apache-2.0):

- Disclose the relationship: a page about your own product versus competitors says so; affiliate or sponsored relationships are disclosed clearly, near the top, before the reader relies on the content. Requirements vary by market; the owner checks local consumer-protection rules.
- Every competitor fact (price, feature, limit) has a source link and an "as of" date; unknown facts are marked, not guessed.
- Acknowledge real competitor strengths and your own limitations; name who each option is best for.
- Plural "alternatives" pages list several real options, not just your product.
- Keep one competitor data file per competitor (YAML or JSON in the repository) and render every page from it, so a price change is fixed once.
- No Product, Review or AggregateRating markup describing competitors' products, and no ratings you did not collect ([structured-data-matrix.md](structured-data-matrix.md#policy-rules)).
- No defamatory or unverifiable claims about competitors.

## Auto-fix vs ask first

| An agent may fix alone (and list in the change table) | Ask the owner first |
| --- | --- |
| Lint-level issues: invisible characters, leftover artifacts, orphan citation markers, duplicate H2s, skipped heading levels | Changing claims, numbers, prices, quotes, author or reviewer information |
| Missing alt text where the image's content is obvious from context | H1 wording, page angle or tone |
| A title or description that is clearly truncated, duplicated or a framework default | Adding or removing more than a few paragraphs; changing page length substantially |
| Broken internal links with an obvious target | Redirects, noindex, deletions, URL changes |
| Adding `[needs source]` next to an unsourced claim | Adding sources the user has not seen or approved, or any statistic |

### Change table

Every content edit is reported as rows of: element, before, after, why, evidence (rule ID, export, source link). Use [change-record.md](../templates/change-record.md) when the edit is large.

## CORE-EEAT credit

The aaron-marketing-skills suite (Apache-2.0) publishes CORE-EEAT, an item-level content rubric developed in a separate upstream repository (https://github.com/aaron-he-zhu/core-eeat-content-benchmark). SEO-GEO-god credits it as a concept that informed the separation of content-body and author or site signals and the "unknown is not fail" discipline. Its item texts, thresholds and weights are not included here (the upstream licence was not verified); the checklists above are our own.

## Candidate facts without an ID

| Fact | Label | Source |
| --- | --- | --- |
| Google's people-first content page frames self-assessment around "Who, How, Why" | needs verification (not re-read in the 2026-11-01 pass) | https://developers.google.com/search/docs/fundamentals/creating-helpful-content |

## Needs verification

- The current wording of Google's people-first content page and of the quality rater guidelines (both change without changelog entries).
- Consumer-protection and disclosure rules for reviews, endorsements and affiliate links in the user's market.
- Every threshold in the decay table: calibrate against the site's own history before acting on a borderline score.
