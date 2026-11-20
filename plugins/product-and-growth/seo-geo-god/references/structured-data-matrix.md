# Structured data matrix

Which JSON-LD types to emit, which properties Google requires or recommends for each search feature, which types no longer produce a Google rich result, the policies that make markup ineligible, the entity graph pattern, safe serialization and the validation workflow. Used by [seo-structured-data](../skills/seo-structured-data/SKILL.md), [seo-ecommerce](../skills/seo-ecommerce/SKILL.md), [seo-local](../skills/seo-local/SKILL.md), [seo-media](../skills/seo-media/SKILL.md) and [geo-entity-authority](../skills/geo-entity-authority/SKILL.md). The CLI encodes the same data in `data/structured-data.json`; when the two disagree, re-verify against the primary source and fix both together.

As of 2026-11-01. Facts are cited by ID from [current-facts.md](current-facts.md). Property tables come from Google's per-feature pages linked from the Search Gallery ([F-T-01](current-facts.md#f-t-01), [F-T-61](current-facts.md#f-t-61)), fetched 2026-11-01; most of those pages show a 2026-09-08 refresh date. schema.org vocabulary version: 30.1, released 2026-09-16 ([F-T-12](current-facts.md#f-t-12)).

## How to read this matrix

- **Required** properties decide eligibility for a feature. **Recommended** properties improve quality and can affect how the feature is shown. Valid markup does not guarantee that any rich result appears ([F-T-11](current-facts.md#f-t-11)).
- CLI mapping (severities are fixed by the rule catalog): a missing Google-required property is [SD008](rule-catalog.md#sd008) (warning); a missing recommended property is [SD009](rule-catalog.md#sd009) (info); a type or feature with no Google rich result is [SD007](rule-catalog.md#sd007) (info, never higher).
- "No required properties" means exactly that: the CLI never reports a missing property for Article or Organization as an error.
- A schema.org type can stay valid vocabulary after Google stops showing a feature for it. Other consumers (Bing, Fact Check Explorer, Dataset Search, internal search, partners) may still read it, so removal is a choice, not a fix.

## Principles

1. Mark up only what a visitor can see on the page, and use the most specific type that fits ([F-T-11](current-facts.md#f-t-11)).
2. Use JSON-LD. Google also supports Microdata and RDFa and can read JSON-LD that JavaScript injects ([F-T-10](current-facts.md#f-t-10)). Our recommendation is still to render JSON-LD in the initial server HTML, so raw-HTML checks, other crawlers and AI fetchers see the same data.
3. Build the data from the same fields the template renders (CMS fields, props, database rows). Hard-coded copies drift away from the visible page.
4. Images referenced in markup must be crawlable and indexable, and marked-up pages must not be blocked by robots.txt or noindex ([F-T-11](current-facts.md#f-t-11)).
5. Structured data is not an AI-visibility lever. Google says AI features need no special schema ([F-AI-11](current-facts.md#f-ai-11)) and lists over-focus on structured data among misconceptions ([F-AI-12](current-facts.md#f-ai-12)).
6. A structured-data manual action removes rich-result eligibility; it does not change web ranking ([F-T-11](current-facts.md#f-t-11)). That is not permission to experiment with misleading markup.
7. Never emit a value you cannot point to on the page or in a verified source: no invented ratings, review counts, prices, dates, authors, awards or `sameAs` profiles.

## Gallery features and properties

The Search Gallery lists 25 feature cards ([F-T-01](current-facts.md#f-t-01)): Article, Breadcrumb, Carousel, Course list, Dataset, Discussion forum, Education Q&A, Employer aggregate rating, Event, Image metadata, Job posting, Local business, Math solver, Movie, Organization, Product, Profile page, Q&A, Recipe, Review snippet, Software app, Speakable, Subscription and paywalled content, Vacation rental and Video.

Seeded features (also in `data/structured-data.json`):

| Feature | Types | Required | Recommended (main ones) | Limits and notes |
| --- | --- | --- | --- | --- |
| Article | Article, NewsArticle, BlogPosting | none | author (name, url), dateModified, datePublished, headline, image | Never report a missing property as an error |
| Product snippet | Product | name, plus one of review, aggregateRating or offers | aggregateRating, offers, review; Offer: availability, priceCurrency, priceValidUntil | Offer needs price or priceSpecification.price; AggregateOffer needs lowPrice and priceCurrency and is ineligible for price-drop display; pros and cons need a Review with at least 2 positiveNotes or negativeNotes |
| Merchant listing | Product with Offer | name, crawlable image, offers (an Offer with price greater than 0 or priceSpecification.price, and priceCurrency) | brand.name, gtin family, mpn, sku, color, size, material, pattern, audience, category, hasAdultConsideration, isVariantOf, inProductGroupWithID; Offer: availability, itemCondition, hasMerchantReturnPolicy, shippingDetails, url, validFrom, validThrough | [SD017](rule-catalog.md#sd017); Organization-level return and shipping policies are preferred, Offer-level ones override; member pricing (`validForMemberTier`) is beta |
| Organization | Organization and subtypes | none | name, url, logo, sameAs, legalName, alternateName, description, address, contactPoint, email, telephone, foundingDate, identifiers (duns, leiCode, vatID, taxID, iso6523Code, naics, globalLocationNumber), numberOfEmployees, hasMerchantReturnPolicy, hasShippingService, hasMemberProgram | Put it on the home page or About page; entity facts belong to [geo-entity-authority](../skills/geo-entity-authority/SKILL.md) |
| Local business | LocalBusiness subtypes | address, name | geo, openingHoursSpecification, telephone, url, priceRange, menu, servesCuisine, department; aggregateRating and review only on sites that review other businesses | [SD010](rule-catalog.md#sd010) for self-serving reviews; details in [local-seo.md](local-seo.md) |
| Breadcrumb | BreadcrumbList | itemListElement; each ListItem: name, position, and item (except the last crumb) | none listed | Desktop only ([F-T-09](current-facts.md#f-t-09)) |
| Event | Event and subtypes | name, startDate, location, location.address | description, endDate, eventStatus, image, location.name, offers, organizer, performer, previousStartDate | Shown only in some countries ([F-T-62](current-facts.md#f-t-62)) |
| Recipe | Recipe | image, name | author, datePublished, description, recipeIngredient, recipeInstructions, recipeYield, cookTime, prepTime, totalTime, nutrition.calories, keywords, recipeCategory, recipeCuisine, video, aggregateRating | |
| Video | VideoObject | name, thumbnailUrl, uploadDate | contentUrl, embedUrl, description, duration, creator (added 2026-09-24), interactionStatistic, expires, hasPart, regionsAllowed, ineligibleRegion | Watch-page rules in [F-T-43](current-facts.md#f-t-43); Clip needs name, startOffset, url; LIVE badge needs BroadcastEvent with isLiveBroadcast, startDate, endDate |
| Software app | SoftwareApplication and subtypes | name, offers.price (0 if free), aggregateRating or review | applicationCategory, operatingSystem | Without a real rating or review the markup stays valid but the feature is not eligible; never invent one |
| Review snippet | Review | author, itemReviewed (unless nested), itemReviewed.name, reviewRating, reviewRating.ratingValue | datePublished, bestRating, worstRating | |
| Review snippet | AggregateRating | itemReviewed (unless nested) and its name, ratingCount or reviewCount, ratingValue | bestRating, worstRating | [SD011](rule-catalog.md#sd011); only for real, visible ratings |
| Job posting | JobPosting | datePosted, description, hiringOrganization, title, jobLocation (or applicantLocationRequirements for fully remote) | baseSalary, employmentType, identifier, validThrough, directApply, jobLocationType | One of the two page types the Indexing API is for ([F-T-30](current-facts.md#f-t-30)) |
| Profile page | ProfilePage | mainEntity (Person or Organization with name or alternateName) | dateCreated, dateModified; mainEntity: description, identifier, image, sameAs, interactionStatistic | |
| Discussion forum | DiscussionForumPosting | author, author.name, datePublished, one of text, image or video | author.url, comment, commentCount, dateModified, headline, url, isPartOf | Comment has the same required set |
| Q&A | QAPage | mainEntity (Question with name, answerCount, and acceptedAnswer or suggestedAnswer; Answer with text) | author, datePublished, upvoteCount, url | Use for Q&A-format forums; other forums use DiscussionForumPosting |
| Dataset | Dataset | name, description | creator, license, distribution (DataDownload with contentUrl and encodingFormat), temporalCoverage, spatialCoverage, identifier, url, version | Consumed by Dataset Search, not a Google Search rich result (needs verification) |

Other gallery features (Carousel, Course list, Education Q&A, Employer aggregate rating, Image metadata, Math solver, Movie, Speakable, Subscription and paywalled content, Vacation rental) are not seeded in the data file. Read Google's page for the feature before adding them, and record the page date in your report.

## Supporting markup

These are documented by Google but are not gallery cards ([F-T-01](current-facts.md#f-t-01)):

| Markup | What it does | Notes |
| --- | --- | --- |
| WebSite on the home page | Site names in results | Still used after the sitelinks search box removal ([F-T-08](current-facts.md#f-t-08)); `potentialAction` is not needed |
| Organization `logo`, `url` | Logo and organization details | No required properties |
| Organization `hasMerchantReturnPolicy`, `hasShippingService`, `hasMemberProgram` | Store-wide return, shipping and loyalty policies | Preferred over repeating policies on every Offer; see [ecommerce-seo.md](ecommerce-seo.md) |
| Merchant listing | Shopping surfaces for products | Stricter than product snippet: price greater than 0 and priceCurrency |
| Book actions | Read or buy actions for books | Not retired; limited to large book providers through an interest form ([F-T-05](current-facts.md#f-t-05)) |
| Fact check (ClaimReview) | Fact Check Explorer | Google Search support is being phased out ([F-T-06](current-facts.md#f-t-06)) |
| Paywalled content (`isAccessibleForFree`, `hasPart` with `cssSelector`) | Distinguishes paywalled content from cloaking | Part of the "Subscription and paywalled content" card |

## Types flagged as no rich result (SD007)

The CLI reports these as [SD007](rule-catalog.md#sd007) at info severity. This table must equal the `no_rich_result` list in `data/structured-data.json` (types and dates); a test enforces it.

| Type | Property | Feature | Since | Note | Fact |
| --- | --- | --- | --- | --- | --- |
| FAQPage | none | FAQ rich result | 2026-05-07 | No longer shown in Google Search; documentation removed 2026-06-15 | [F-T-02](current-facts.md#f-t-02) |
| HowTo | none | How-to rich result | 2023-09-14 | Deprecated on all devices | [F-T-03](current-facts.md#f-t-03) |
| SpecialAnnouncement | none | Special announcement | 2025-07-31 | Part of the June 2025 simplification | [F-T-04](current-facts.md#f-t-04) |
| ClaimReview | none | Fact check rich result | phasing out | Fact Check Explorer still supports it | [F-T-06](current-facts.md#f-t-06) |
| Occupation | none | Estimated salary | 2025-09-09 | Removed from Search Console reports and the Rich Results Test | [F-T-04](current-facts.md#f-t-04) |
| WebSite | potentialAction (SearchAction) | Sitelinks search box | 2024-11-21 | WebSite itself is still valid and used for site names | [F-T-08](current-facts.md#f-t-08) |

How to act on an SD007 finding:

- FAQ and HowTo markup no longer produce Google rich results; never promise them.
- Keep the markup if it is accurate and another consumer uses it; remove it if nothing does. Either way, it is not an error.
- A real question-and-answer page written by users can use QAPage; an FAQ section written by the site owner stays plain HTML (and still helps readers).
- When a time-bounded announcement needs markup, use Event only if it really is one event; otherwise Article or WebPage.

Retired features whose types stay in use, and therefore are **not** flagged:

| Retired feature | Type kept | Why it is not flagged |
| --- | --- | --- |
| Course info (2025-09-09) | Course | The Course list feature still exists ([F-T-04](current-facts.md#f-t-04)) |
| Learning video (2025-09-09) | VideoObject | Video features still exist |
| Vehicle listing (2025-09-09) | Vehicle, Car | Products and merchant listings still use them |
| Practice problems (docs removed 2026-01-06) | Quiz | Education Q&A still uses Quiz ([F-T-07](current-facts.md#f-t-07)) |
| Book actions (banner removed 2025-11-05) | Book | Not retired ([F-T-05](current-facts.md#f-t-05)) |

## Policy rules

Google's structured-data policies apply on top of syntax ([F-T-11](current-facts.md#f-t-11)). Breaking them makes markup ineligible or invites a manual action.

| Policy | What to do in code | Rule |
| --- | --- | --- |
| Visible content only | Generate every value from rendered fields; never mark up hidden tabs that are not in the DOM, or text added only for crawlers | [SD016](rule-catalog.md#sd016) (planned) |
| Self-serving reviews | No Review or AggregateRating on the LocalBusiness or Organization that publishes the site, including ratings imported from third-party widgets | [SD010](rule-catalog.md#sd010) |
| Fake or incentivized reviews | Only real reviews, with an author and a comment; disclose incentives on the page; never seed sample reviews | [SD011](rule-catalog.md#sd011) for broken counts |
| Ratings need reviews | Never emit AggregateRating unless the reviews it summarizes are real and visible on the page | [SD011](rule-catalog.md#sd011) |
| Internal scores | Editorial or AI-assisted scores never become `AggregateRating` or `Review` | own rule |
| Lists | `ItemList` items, order and count match the visible list | own rule |
| Events | `Event` only for a page about one real event with its own date and location; an events listing is not an Event | own rule |
| Competitor products | No Product, Review or rating markup describing competitors' products on comparison pages | own rule |
| Regions and devices | Event rich results appear only in some countries; breadcrumbs only on desktop ([F-T-09](current-facts.md#f-t-09)) | report as context, not as a defect |
| Prices | Merchant listings need a price greater than 0 and a currency; AggregateOffer cannot show a price drop | [SD017](rule-catalog.md#sd017) |
| URLs and dates | Absolute `https://` URLs in URL-valued properties; ISO 8601 dates and date-times | [SD013](rule-catalog.md#sd013), [SD014](rule-catalog.md#sd014) |
| Placeholders | No `[REPLACE: …]`, `YOUR_…`, lorem ipsum or `example.com` values on a real site | [SD006](rule-catalog.md#sd006) |

## Entity graph pattern

One `@graph` per page, with stable `@id` values that every page reuses. The entity facts themselves (legal name, logo, `sameAs`, founders) come from a verified entity file owned by [geo-entity-authority](../skills/geo-entity-authority/SKILL.md); this reference covers only the mechanics.

| Node | `@id` convention | Links to |
| --- | --- | --- |
| Organization | `https://example.com/#organization` | `logo`, `sameAs` (verified profiles only) |
| WebSite | `https://example.com/#website` | `publisher` → Organization |
| WebPage | `<page URL>#webpage` | `isPartOf` → WebSite, `breadcrumb` → BreadcrumbList |
| Article | `<page URL>#article` | `mainEntityOfPage` → WebPage, `author` → Person, `publisher` → Organization |
| Person | `https://example.com/authors/<slug>/#person` | `worksFor` → Organization, `sameAs` |
| BreadcrumbList | `<page URL>#breadcrumb` | items mirror the URL path |

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "Organization", "@id": "https://example.com/#organization", "name": "Example Co", "url": "https://example.com/"},
    {"@type": "WebSite", "@id": "https://example.com/#website", "url": "https://example.com/", "name": "Example Co", "publisher": {"@id": "https://example.com/#organization"}},
    {"@type": "WebPage", "@id": "https://example.com/guides/setup/#webpage", "url": "https://example.com/guides/setup/", "isPartOf": {"@id": "https://example.com/#website"}}
  ]
}
```

Rules for the graph:

- Members of `@graph` inherit the top-level `@context`; a node with no context at all is [SD003](rule-catalog.md#sd003), a node without `@type` is [SD004](rule-catalog.md#sd004).
- Reuse one Organization `@id` on every page. Two different entities sharing one `@id` across pages is [SD015](rule-catalog.md#sd015).
- Reference nodes by `{"@id": …}` instead of repeating full copies that can drift apart.
- Never merge two organizations or two people because their names look alike.
- Plugins (Yoast, Rank Math, All in One SEO, Shopify apps) often emit their own graph. Either configure the plugin to emit the entities you want, or disable its output for that type; never ship two competing Organization nodes.

## Framework serialization

Every JSON-LD block must escape `<` so page data cannot close the script element ([SD012](rule-catalog.md#sd012) on built HTML, [SD018](rule-catalog.md#sd018) on templates that call `JSON.stringify` without escaping). Serialize with the language's JSON encoder; never concatenate strings. Per-framework placement (layout, head API, plugin hooks) is in [framework-recipes.md](framework-recipes.md); read the installed version before editing.

| Stack | Serialization that escapes `<` | Verify |
| --- | --- | --- |
| React, Next.js, Remix, Gatsby | `dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}` on a `<script type="application/ld+json">` element | `SG jsonld` on built HTML |
| Astro | `<script type="application/ld+json" set:html={JSON.stringify(data).replace(/</g, "\\u003c")} />` | built HTML |
| Vue, Nuxt, Svelte, SvelteKit | Build the string with the same `JSON.stringify(...).replace(...)` and pass it to the framework's raw-HTML or head API | built HTML; head APIs differ by version |
| PHP, WordPress | `wp_json_encode( $data, JSON_HEX_TAG \| JSON_UNESCAPED_SLASHES )` (plain PHP: `json_encode` with the same flags) | rendered page from a local server |
| Python (Django, Flask, Jinja) | `json.dumps(data).replace("<", "\\u003c")`, then mark the result safe; Django's `json_script` emits `type="application/json"`, so it does not produce a JSON-LD block | rendered page |
| Ruby on Rails | `json_escape(data.to_json)` output inside the script element | rendered page |
| Hugo, Liquid and other template languages | Use the built-in JSON filter, then confirm in the built HTML that `<` inside values appears escaped | built HTML; filter behavior differs by version |

Template expressions (`{{ }}`, `{% %}`, `${ }`, `<?php`, `<%`, JSX `{value}`) inside a component's JSON-LD cannot be validated in source; the CLI skips those blocks with [SD019](rule-catalog.md#sd019). Validate the built or server-rendered output instead.

## Validation workflow

1. Source templates: `SG jsonld src --recursive` (component files such as `.tsx`, `.vue`, `.astro`, `.liquid`, `.php`); fix [SD018](rule-catalog.md#sd018) and note every [SD019](rule-catalog.md#sd019) skip for step 2.
2. Built output: `SG jsonld dist` (or the whole audit, `SG audit-build dist --base-url https://example.com`). Target: zero errors; every template emits the types you decided on.
3. Server-rendered apps without static output: build, start the production server locally and run `SG audit-url http://localhost:3000 --live --allow-local localhost:3000 --max-pages 50`.
4. Confirm the block is in the raw HTML that a crawler receives, not only in the browser DOM. For plugin-injected markup that only appears after rendering, confirm it in a rendered DOM before you call it missing or present.
5. User-run checks after deployment (never claim them yourself): Google's Rich Results Test at https://search.google.com/test/rich-results, the Schema Markup Validator at https://validator.schema.org/, and Search Console enhancement reports once Google recrawls.
6. Record which checks were observed by you, which were run by the user, and which are still pending.

## Needs verification

- Dataset scope. The 2025-11-05 changelog summary says Dataset markup serves Dataset Search only; the Dataset page does not say so explicitly (https://developers.google.com/search/updates).
- FAQ tooling. Reports that Search Console's FAQ report, filter and Rich Results Test support ended in June 2026 and API support in August 2026, and that existing FAQPage markup need not be removed, are third-party only.
- Serialization helpers. Escaping behavior of template filters (Hugo, Liquid, Nunjucks) and head APIs (Nuxt, SvelteKit) changes between versions; always confirm in built HTML.
