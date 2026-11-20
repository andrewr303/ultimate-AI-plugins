<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: pre-migration playbook stages, redirect-map rules and STOP list re-expressed in our own words, numeric traffic and backlink thresholds made optional and data-dependent, tied to SEO-GEO-god CLI checks and Google facts. See NOTICE.md. -->
# Site migrations and URL changes

How to move URLs, domains or rendering stacks without losing search or AI-answer visibility: what to capture before anything changes, how to build and validate a redirect map, what to check on staging, the order of cutover steps, how to compare after launch, and which defects stop a launch. Used by [seo-migrations](../skills/seo-migrations/SKILL.md). HTTP redirect correctness outside a migration belongs to [seo-technical](../skills/seo-technical/SKILL.md); robots and canonical semantics are in [robots-and-directives.md](robots-and-directives.md).

As of 2026-11-01. Facts are cited from [current-facts.md](current-facts.md). Numbers marked "heuristic" are ours and should be tuned to the site's own data.

## Migration types

| Change | Typical cause | Main risks |
| --- | --- | --- |
| Rendering stack swap | Single-page app to server rendering or static generation; theme rewrite | Content or links missing from server HTML; head tags or JSON-LD dropped by the new layout; client-only routes returning 200 for unknown URLs |
| Framework or CMS replatform | Gatsby to Astro, WordPress to headless, Shopify to custom | Different URL rules (trailing slash, case, extensions); lost redirects; plugin-generated metadata and schema disappear |
| Path or slug restructure | New information architecture, dates removed from blog URLs | Unmapped URLs, redirect chains, internal links through redirects |
| Domain or host change | Rebrand, subdomain consolidation, HTTP to HTTPS | Old host stops redirecting; canonicals or sitemaps still on the old host |
| Locale restructure | New locale prefixes, ccTLD consolidation | hreflang sets pointing to old URLs; cross-language canonicals |
| Content consolidation | Merging or removing sections | Many URLs redirected to the home page; removed pages that should return 404 or 410 |

## Six stages

### Stage 1 baseline

Capture the current state before any code changes, so later comparisons are possible.

- Snapshot the current build: `SG drift snapshot old-dist --base-url https://example.com --output .seo-geo-god/baselines/2026-11-01-pre-migration.json`. Use the live site instead (`SG drift snapshot --url https://example.com --live --base-url https://example.com --output …`) only with the owner's consent; the live crawl is small and polite by design.
- Export the URL inventory: sitemap URLs (`SG sitemap old-dist --build-dir old-dist --base-url https://example.com`) plus every built page. Add URLs that exist only on the server (redirects, generated routes, files) from hosting config.
- Ask for performance data the owner already has: top pages by clicks from a Search Console export, top landing pages from analytics, and top linked pages from a backlink export. Treat any page with meaningful traffic or external links as high value and map it individually (no fixed threshold; choose one from the site's own distribution and write it down).
- Record per template: title pattern, H1, canonical, robots directives, JSON-LD types, hreflang, word count (the snapshot holds these).
- Save the robots.txt and every redirect rule currently in force.

### Stage 2 risk map

For each change, write down what could break, how you will detect it, and whether it blocks launch:

| Area | Question | Detection |
| --- | --- | --- |
| Templates | Does each new template emit title, description, one H1, self-canonical and the same JSON-LD types? | `SG drift compare` per page; [DRIFT005](rule-catalog.md#drift005), [DRIFT006](rule-catalog.md#drift006), [DRIFT010](rule-catalog.md#drift010) |
| Rendering | Is the main content and navigation in server HTML? | [REND001](rule-catalog.md#rend001), [REND002](rule-catalog.md#rend002); [F-T-22](current-facts.md#f-t-22) |
| URLs | Does every old URL have a mapped destination or a deliberate 404 or 410? | `SG redirects`; [REDIR006](rule-catalog.md#redir006) |
| Indexing controls | Could staging noindex or a staging robots.txt ship? | [LAUNCH004](rule-catalog.md#launch004), [CRAWL004](rule-catalog.md#crawl004) |
| Hosts | Do canonicals, `og:url`, hreflang, sitemaps and JSON-LD use the production host? | [LAUNCH003](rule-catalog.md#launch003) |
| Structured data | Do types change, and is the new type eligible for the same feature? | [structured-data-matrix.md](structured-data-matrix.md) |
| Locales | Do hreflang sets list the new URLs with return links? | `SG hreflang`; [international.md](international.md) |
| Internal links | Do links point at final URLs, not through redirects? | [LINK006](rule-catalog.md#link006), [LINK001](rule-catalog.md#link001) |

Write a go or no-go per area. A no-go on any STOP item blocks launch.

### Stage 3 redirect map

- One CSV is the single source of truth for every permanent move (format below). Commit it with the code (for example `seo/redirects.csv`; it is source, not a report, so it does not belong under `.seo-geo-god/`). Generate the host's redirect configuration from it; never maintain two lists by hand.
- Every old URL ends in exactly one state: redirected once to its closest equivalent, kept at the same URL, or deliberately removed with 404 or 410.
- Collapse chains: if A moved to B and B now moves to C, map A directly to C ([REDIR001](rule-catalog.md#redir001)).
- No loops ([REDIR002](rule-catalog.md#redir002)), no destinations missing from the new build ([REDIR003](rule-catalog.md#redir003)), no duplicate sources or malformed rows ([REDIR007](rule-catalog.md#redir007)).
- Do not send unrelated pages to the home page; Google may treat that as a soft 404 ([REDIR005](rule-catalog.md#redir005), [F-T-24](current-facts.md#f-t-24)).
- Validate: `SG redirects seo/redirects.csv --old-build old-dist --new-build dist --base-url https://example.com`.

### Stage 4 staging QA

- Audit the production build artifact, not the staging deployment: `SG audit-build dist --base-url https://example.com --expect-indexable --profile launch`. Staging may carry noindex or a blocking robots.txt; the artifact that will ship must not.
- Compare against the baseline: `SG drift compare .seo-geo-god/baselines/2026-11-01-pre-migration.json dist --base-url https://example.com`. Every error-level DRIFT finding is either explained as intended or fixed. Drift matches pages by URL: it is the main check where URLs stay the same, while for moved URLs the removed-page findings ([DRIFT001](rule-catalog.md#drift001)) are expected when the redirect map covers them.
- Discovery and locales: `SG sitemap dist --build-dir dist --base-url https://example.com` and `SG hreflang dist --base-url https://example.com`.
- Structured data: `SG jsonld dist`.
- Server-rendered apps: build, start the production server locally and crawl it: `SG audit-url http://localhost:3000 --live --allow-local localhost:3000 --max-pages 200 --expect-indexable`. This also observes server redirects and status codes the offline build cannot show.
- Pagination and facets keep self-canonical, crawlable pages ([F-T-25](current-facts.md#f-t-25), [F-T-26](current-facts.md#f-t-26)).

### Stage 5 cutover

Order matters. Present these as owner-operated steps; the agent prepares and verifies, the owner deploys.

1. Ship redirects together with, or before, the new routes, and before any DNS or robots.txt change. Old URLs must never serve a 404 between deploys.
2. Ship the production robots.txt and remove staging noindex in the same release.
3. Publish new sitemaps that list only final, canonical URLs; reference them from robots.txt. Submission is a hint, not an indexing request ([F-T-27](current-facts.md#f-t-27)).
4. Domain moves: keep the old host serving redirects (certificate renewed, DNS kept). The owner uses Search Console's change-of-address tool for the old property (see the last section).
5. Watch server logs or monitoring for spikes of 404 or 5xx on old URLs during the first hours, and keep a rollback plan for the redirect config.

Not migration tools: the Google Indexing API, which is only for JobPosting and livestream pages ([F-T-30](current-facts.md#f-t-30)), and IndexNow, in which Google does not participate ([F-AI-21](current-facts.md#f-ai-21)). IndexNow can notify Bing and other participants if the owner wants it.

### Stage 6 post-launch comparison

Fix the read-back dates before launch, for example T+1, T+7 and T+30 days, and keep them even if early numbers look good or bad.

- T+1: snapshot what is deployed (`SG drift snapshot --url https://example.com --live --base-url https://example.com --output .seo-geo-god/baselines/<date>-t1.json` with consent, or snapshot the deployed build artifact) and run `SG drift compare` against the baseline of the same source type (live against live, build against build). Check that a sample of old URLs answers with one redirect hop.
- T+7: compare the owner's Search Console page-indexing and performance exports against the baseline period ([search-data-analysis](../skills/search-data-analysis/SKILL.md)). A drop on specific URLs points to mapping or template defects; a uniform drop needs more time before conclusions.
- T+30: repeat the comparison; confirm the old URLs are being replaced by new ones in Search Console reports.
- For repeated audits, `SG drift findings old.json new.json` lists added, no-longer-observed and persisting findings. Absence of a finding is not proof of a fix.
- Compare only comparable snapshots: same tool major version, same source type and the same base URL ([DRIFT020](rule-catalog.md#drift020)).

## Redirect map CSV format

The CLI reads `old_url,new_url[,status]` with a header row:

```csv
old_url,new_url,status
https://example.com/category/blue-shoes/,https://example.com/shop/blue-shoes/,301
https://example.com/blog/2020/setup-tips/,https://example.com/blog/setup-tips/,301
```

- Use absolute URLs, written exactly as they are served (scheme, host, trailing slash, case).
- Write the status explicitly on every row: 301 or 308 for permanent moves. 302, 303 and 307 are weak signals for a permanent move and are reported by [REDIR004](rule-catalog.md#redir004) ([F-T-24](current-facts.md#f-t-24)).
- Keep deliberate removals (404 or 410) out of the redirect map, in a separate removals list keyed by `old_url`. `SG redirects` reports those URLs as [REDIR006](rule-catalog.md#redir006); every such finding must match a row in the removals list, and anything else is a mapping gap.
- Keep planning notes (reason, priority, owner) in a separate sheet keyed by `old_url`, so the CLI input stays minimal.

Where the generated configuration usually lives (confirm with `SG stack` and [framework-recipes.md](framework-recipes.md)): `_redirects` (Netlify, Cloudflare Pages), `vercel.json` `redirects`, `next.config.*` `redirects()`, `netlify.toml`, nginx `return 301` or `map` blocks, Apache `Redirect` rules, a WordPress redirect plugin, Shopify URL redirects. Prefer server or edge redirects over client-side redirects; meta refresh is reported by [SPAM002](rule-catalog.md#spam002).

## STOP list

Do not launch while any of these is true:

| STOP item | Why | How it shows up |
| --- | --- | --- |
| A redirect chain longer than one hop in the map | Signals and crawl time lost at each hop | [REDIR001](rule-catalog.md#redir001) |
| A redirect loop | Pages become unreachable | [REDIR002](rule-catalog.md#redir002) |
| A high-value old URL unmapped | Traffic and links lost | [REDIR006](rule-catalog.md#redir006) for any unmapped URL; high value from Stage 1 data |
| `Disallow: /` or site-wide noindex shipped from staging | The site drops out of Search and AI answers | [CRAWL004](rule-catalog.md#crawl004), [LAUNCH004](rule-catalog.md#launch004) |
| Canonicals, `og:url`, hreflang, sitemaps or JSON-LD pointing at the old, staging, preview or localhost host | Google is told the old or test URL is the real one | [LAUNCH003](rule-catalog.md#launch003) |
| A new page canonicalizing to its old URL | Contradicts the redirect | [DRIFT003](rule-catalog.md#drift003), [CANON004](rule-catalog.md#canon004) |
| Key templates losing H1, server-rendered content or JSON-LD types | Pages become thinner or lose features | [DRIFT006](rule-catalog.md#drift006), [DRIFT010](rule-catalog.md#drift010), [DRIFT015](rule-catalog.md#drift015), [REND001](rule-catalog.md#rend001) |
| A structured-data type changed without an eligibility check | Rich results lost silently | [structured-data-matrix.md](structured-data-matrix.md) |
| Many unrelated URLs redirected to the home page | Treated like soft 404s | [REDIR005](rule-catalog.md#redir005) |

## URL and index state matrix

What each kind of URL should return after the migration (our own rules, consistent with Google's status and canonical documentation, [F-T-21](current-facts.md#f-t-21), [F-T-24](current-facts.md#f-t-24)):

| URL kind | Status | Canonical | In sitemap | Notes |
| --- | --- | --- | --- | --- |
| Content page | 200 | self | yes | |
| Moved page | 301 or 308 to final URL | n/a | no | One hop; internal links updated to the final URL |
| Merged pages | 301 to the merged page | n/a | no | Only when the content really merged |
| Removed, no replacement | 404 or 410 | n/a | no | Do not redirect to the home page |
| Paginated page 2 and later | 200 | self | optional | Never canonical to page 1 ([CANON006](rule-catalog.md#canon006)) |
| Filter or sort variant | 200 with noindex, or not crawlable | base URL if a true duplicate | no | Choose one approach ([F-T-26](current-facts.md#f-t-26)) |
| Empty filter combination | 404 | n/a | no | |
| Tracking parameters | 200 | clean URL | no | |
| Draft or preview | behind authentication | n/a | no | Never public with noindex alone |
| Unknown path | 404 | n/a | no | Not a 200 shell ([REND005](rule-catalog.md#rend005)) |

`noindex` only works if the page can be crawled; never block a URL in robots.txt that you want removed with noindex ([CRAWL008](rule-catalog.md#crawl008)).

## Slug governance

- Renaming a title does not change a published slug. Slug changes are migrations of their own, with a redirect from every previous slug straight to the current one.
- One URL generator builds canonical, `og:url`, hreflang, sitemap entries, JSON-LD URLs and internal links. Templates never assemble URLs by hand.
- Normalize once: lowercase, hyphen-separated, one trailing-slash policy, percent-encoding for non-ASCII, no session or tracking parameters.
- Reserve top-level paths used by the platform (`/api`, `/admin`, `/assets`, `/robots.txt`, `/sitemap.xml`, `/llms.txt`) so new slugs cannot collide with them.
- Redirect targets come only from the map; never redirect to a URL taken from a request parameter.

## Cutover and post-launch checks

Before deploy (agent, offline): `SG redirects` clean; `SG audit-build dist --base-url https://example.com --expect-indexable --profile launch` with no errors; `SG drift compare` errors explained; robots.txt reviewed by the owner.

Right after deploy (owner, or agent with consent for a small live crawl): old URLs answer with one redirect hop to a 200; robots.txt and sitemaps are reachable on the production host; a sample of new pages returns 200 with the expected head tags; unknown URLs return 404.

Later (owner data): page-indexing and performance comparisons against the baseline at the fixed read-back dates; keep redirects in place long term (Google's site-move guidance asks for a long period; see "Needs verification").

State every result with its status: prepared (in the repository), deployed (observed on the live host), submitted (an owner action in a search engine tool) or measured (observed in data).

## Search Console change of address

For a domain move, the owner (a verified owner of both properties) uses Search Console's change-of-address tool on the old property after the redirects are live. It is a user action; the agent writes the steps and never claims it was done. Bing Webmaster Tools offers a comparable site-move setting. Both are user-operated; exact menu labels change, so tell the owner to follow the current help page.

## Needs verification

- How long Google recommends keeping redirects after a site move, and the current change-of-address requirements (Google's site-move documentation; no fact ID yet).
- Bing Webmaster Tools site-move feature name and behavior (no primary source checked in this pass).
- Typical recovery times after migrations are third-party observations, not documented behavior; do not quote numbers.
