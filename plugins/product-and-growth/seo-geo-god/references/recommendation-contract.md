# Recommendation contract

What every SEO or GEO recommendation must contain before it reaches a user: the evidence it rests on, the mechanism with dated facts, its dependencies, the exact change, how to verify it, how it could be proven wrong, what to watch and when, how confident we are and what it costs. It also defines how a plan is sequenced as a dependency graph, how to say what to ignore, and the status words used in reports. [seo-geo-audit](../skills/seo-geo-audit/SKILL.md) applies it to the top items of every audit; focused skills apply the short form. Ordering rules are in [scoring-and-prioritization.md](scoring-and-prioritization.md#plan-ordering).

As of 2026-11-01. A finding says what is wrong; a recommendation says what to change, why it should help, and how we will know whether it did. A list of findings is not a plan.

## When the contract applies

| Situation | Fields required |
| --- | --- |
| Top 3 to 5 items of an audit or launch review | All fields below |
| A change that needs owner approval (robots policy, redirects, removals, publishing, submissions) | All fields, plus the rollback |
| A focused skill's fix in code | Short form: evidence, exact change, verification, falsifiability, state |
| Backlog items beyond the top 5 | Rule ID, affected count, one-line fix, layer, effort |

## Recommendation fields

| Field | What to write | Example |
| --- | --- | --- |
| ID and title | Stable plan ID and the outcome in plain words | R1: Per-route canonical on blog posts |
| Priority and layer | Catalog priority, or a raised one with the reason; dependency layer from [plan ordering](scoring-and-prioritization.md#plan-ordering) | P1, raised from the catalog's P2 because blog posts carry most organic sessions (`user-provided`); layer 1 |
| Evidence | Finding or rule IDs, affected count, two or three sample URLs or files, provenance labels for any number | [CANON005](rule-catalog.md#canon005) on 37 of 40 posts, all pointing to `https://example.com/blog/`; `app/layout.tsx:18` sets one canonical for every route; `measured` by `SG audit-build` |
| Mechanism | Why the defect costs visibility, citing fact IDs; no fact, no claim | Google treats `rel=canonical` as a strong canonicalization signal ([F-T-21](current-facts.md#f-t-21)), so 37 posts point at the blog index |
| Assumption | What the recommendation rests on that could be wrong | The posts are meant to be indexed separately (owner to confirm) |
| Dependency | What must be true first, and what this unblocks | After: none (layer 1). Unblocks R3 (metadata) and R5 (citability), which are pointless on non-canonical URLs |
| Exact change | File, component or config, and the smallest diff that fixes the root cause | Move canonical from `app/layout.tsx` to `generateMetadata` in `app/blog/[slug]/page.tsx`, built from the route |
| Verification | The command to re-run and the expected result | `SG audit-build out --base-url https://example.com --expect-indexable` shows no CANON005 on blog posts; `SG drift compare` shows canonical changes only on blog posts |
| Falsifiability | What observation would show the recommendation failed or was wrong | If URL Inspection (user-run) still reports "Google chose a different canonical" for sampled posts 28 days after deploy, another signal (redirects, internal links, sitemap) contradicts the tag |
| Leading indicator | The earliest signal that it is working, and its data source | Search Console page-indexing export: indexed blog-post count; impressions for `/blog/` URLs |
| Read-back window | Absolute dates for checking, from the deploy date | Deployed 2026-11-04; read back daily 2026-11-05 to 2026-11-11, then 2026-12-02 (technical-fix windows; heuristic) |
| Confidence | high, medium or low, with the reason | High: deterministic defect, documented mechanism |
| Effort | S, M or L, with who does it | S: one file, the developer |
| Owner and approval | Who decides, who acts, what needs approval | Developer implements; no external approval needed |
| State | One of the [status vocabulary](#status-vocabulary) words | Implemented locally |

Rules for the fields:

- Evidence comes from this session's commands or the user's exports. A claim without evidence becomes a question for the user or an item under "not measured", not a recommendation.
- Mechanisms cite [current-facts.md](current-facts.md) IDs. Where Google and community claims disagree, follow Google's documentation for Google Search and say which product the statement is about.
- Impact is stated through the catalog impact, affected pages and the layer. A click or traffic figure appears only when it is calculated from the user's own exports and labelled with its provenance; no generic CTR-uplift numbers.
- If the user tried the same change before without effect, say so and change the recommendation instead of repeating it.
- If a constraint cannot move (legal text, brand voice, a platform limit), the recommendation pivots to what is possible; it does not insist.
- Retract a recommendation explicitly when newer facts contradict it.

## Confidence and effort

Use these scales so readers can compare items across audits:

| Confidence | When to use it |
| --- | --- |
| High | Deterministic defect (rule class A or B) and a mechanism documented in a dated fact; the fix is verifiable locally |
| Medium | The defect is real but the mechanism rests on a heuristic (class C) or the size of the effect is unknown; or a fact is older than its re-check date |
| Low | Host-agent judgment only, a 3P or snippet-only claim, or a hypothesis from timing (an update overlap); say what evidence would raise it |

| Effort | Typical scope |
| --- | --- |
| S | One file or config value in one template, layout or route; no new dependency |
| M | Several files or one template family, a build or routing change, or content edits on a handful of pages |
| L | Cross-team or platform work: rendering mode changes, migrations, CMS model changes, new data sources, or work that needs owner decisions first |

Effort uses the catalog's S, M or L as the starting point and is adjusted to the repository actually inspected; say so when the adjustment is a guess.

## Assumption traps

Check each top recommendation against these before sending it:

- The home page is not the site; templates (product, article, location, category) usually carry the traffic.
- Low traffic does not mean low value; a niche page with high intent may matter more than a busy informational one.
- A CMS or framework limitation is often fixable in a theme, hook, middleware or build step; check before declaring it permanent.
- A finding from an older audit may be obsolete because engines changed; re-check the fact date.
- The analyst's "best practice" may conflict with the owner's goals, brand or legal constraints; surface the assumption so the owner can reject it.
- A symptom can survive its cause: thin-content or missing-citation findings on a client-rendered page are usually caused by rendering ([REND001](rule-catalog.md#rend001)), not by the copy.

## Dependency graph

The plan is a dependency graph, not a list. Write it as a table:

| ID | Item | Layer | After | Unblocks | Parallel with |
| --- | --- | --- | --- | --- | --- |
| R1 | Remove staging `noindex` from the production build | 1 | — | R2, R3, R4 | — |
| R2 | Server-render product descriptions | 1 | R1 | R4 | R3 |
| R3 | Fix broken merchant-listing offers | 2 | R1 | — | R2 |
| R4 | Answer-first intro sections on top guides | 4 | R1, R2 | — | — |

- The highest-leverage constraint (usually one eligibility defect that gates everything else) goes first, even when growth work looks more interesting.
- Mark items that can ship in either order as parallel so the team can split them; never imply an order that is not real.
- Items blocked on an owner decision or missing data say exactly what is missing ("blocked: owner's AI-training policy", "blocked: Search Console export").
- Combine findings across areas when they share one cause: a client-rendered shell explains missing content, missing links and missing JSON-LD at once; a layout-wide canonical explains duplicates and hreflang conflicts.

## Falsifiability and leading indicators

Every recommendation gets a "how would we know this failed?" line with a measurable check, so no bet is invisible.

| Kind of change | Verified locally by | Leading indicator after deploy | Failure signal |
| --- | --- | --- | --- |
| Crawl or index control | Re-run `SG audit-build` or the consented `SG audit-url`; `SG drift compare` | Search Console page-indexing counts, URL Inspection on samples (user-run) | Pages still excluded for the same reason after the read-back window |
| Rendering | Server HTML contains the content (`SG audit-page` on fetched or built HTML) | Indexed page counts, impressions on affected templates | Rendered-HTML checks in URL Inspection still miss content |
| Structured data | `SG jsonld` on source and build output; no SD errors | Search Console enhancement reports (user-run) | Items still invalid, or no eligible items after recrawl |
| AI crawler access | `SG robots FILE --bots ai`; consented `SG access-check` | Verified crawler hits in logs (`SG referrers FILE --log --bots`, counts "claimed" until checked against published IP lists) | Search indexers still absent from logs or still blocked at the edge |
| Citability rewrite | `SG fidelity` passes; `SG citability` before and after (heuristic) | Prompt-panel citations and AI referral sessions against a hold-out ([measurement-protocol.md](measurement-protocol.md#hold-outs-and-controls)) | No difference from the hold-out after the read-back window |

Read-back windows depend on the change type and are our heuristic defaults ([measurement-protocol.md](measurement-protocol.md#read-back-windows)): technical fixes daily for 7 days, then at 28 days; content changes at 7, 14, 28 and 56 days; new pages at 14, 28, 56 and 90 days. Write them as absolute dates. A movement that coincides with a Google update is a confounder to record, not proof ([F-T-36](current-facts.md#f-t-36)).

## What to ignore

Every audit names 2 or 3 things it deliberately does not recommend now, each with the reason and when to revisit. This protects the team's time and shows the prioritization was a choice. Typical entries:

- Informational hints with no documented effect, such as title-length hints ([META011](rule-catalog.md#meta011)) or `priority` and `changefreq` in sitemaps ([SMAP007](rule-catalog.md#smap007)): revisit when the template is touched anyway.
- A missing llms.txt ([AGENT001](rule-catalog.md#agent001)) when the site has no developer or agent audience; Google Search ignores the file ([F-AI-11](current-facts.md#f-ai-11)). Revisit if documentation users or coding agents become a goal.
- The lab-data-only notice ([PERF009](rule-catalog.md#perf009)) and tuning lab scores on a site without field data: revisit when CrUX or RUM data exists.
- Content and GEO work on templates blocked by a layer-1 defect: revisit after the blocker's read-back date.

## Status vocabulary

Use exactly these words for the state of each item, and never let one stand in for another (see [safety-and-honesty.md](safety-and-honesty.md#dry-run-is-not-a-receipt)):

| State | Means |
| --- | --- |
| Proposed | Recommended; nothing changed yet |
| Prepared | Diff, payload, draft or instructions ready; not applied |
| Implemented locally | Applied in the working tree |
| Verified locally | The same checks re-ran on a fresh build or local server and passed |
| Deployed | Live in production, confirmed by the owner or a consented live check |
| Submitted | Accepted by an external system (sitemap, IndexNow, removal, setting), with its response recorded |
| Measured | An outcome observed in data after the change, with window and comparison |
| Blocked | Waiting on a named decision, approval or data source |

## Narrow requests

A small fix does not need a plan document. It still needs: the evidence (rule ID or file), the exact change, the verification command with its result, one falsifiability line and the state. Keep it to a few lines in the final message.
