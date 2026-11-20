<!-- Portions adapted from aaron-marketing-skills (Apache-2.0, Copyright 2024 Aaron He Zhu). Modified for SEO-GEO-god on 2026-11-01: canonical NAP record, listing audit order and location-page plan re-expressed in our own words; ranking-lever and character-count claims removed; tied to SEO-GEO-god rules, a project-local entity file and dated Google facts. See NOTICE.md. -->
# Local SEO

How local businesses appear in Google Search and Maps, and what a coding agent can change in the website: the documented ranking factors, business-type detection, one canonical name, address and phone record, consistency checks, LocalBusiness subtypes and properties, the multi-location entity graph, location and service-area pages that are not doorways, a user-run Google Business Profile checklist with retired features, review policy, other listings, and geo-grid math for users who already have a rank-data provider. Used by [seo-local](../skills/seo-local/SKILL.md); markup mechanics are in [structured-data-matrix.md](structured-data-matrix.md).

As of 2026-11-01. Facts are cited from [current-facts.md](current-facts.md). Numbers not cited to a fact are heuristics. Local-ranking factor studies from SEO vendors are opinion surveys; this file does not reproduce their percentages.

## Fundamentals

- Google ranks local results on relevance, distance and prominence, and there is no way to request or pay for a better local ranking ([F-T-44](current-facts.md#f-t-44)). Prominence draws on information about the business across the web, including links and reviews.
- The Business Profile is managed in Google's own interface by the owner; a website change cannot edit it. The website supports it with consistent business facts, useful location pages and accurate markup.
- Structured data helps Google understand business details; it does not create a map-pack ranking by itself and does not guarantee any rich result ([F-T-11](current-facts.md#f-t-11)).
- In the EEA, Google's aggregator units also cover local business queries ([F-T-74](current-facts.md#f-t-74); the EEA scope needs verification, see below); note this for businesses serving those markets.

## Business type detection

| Type | Signals in the site | Consequences |
| --- | --- | --- |
| Storefront | Street address in the footer or contact page, opening hours, map embed, "visit us" | Full address on pages and markup; map and directions on location pages |
| Service-area business | No public address, "we come to you", service area lists, `areaServed` without a street address | Hide the street address where the owner hides it in the Business Profile; describe the service area; no map pin |
| Hybrid | A showroom plus service areas | One location page per real premises plus service-area pages only where the business actually works |
| Multi-location brand | Store locator, `/locations/` routes, several addresses | One page and one LocalBusiness node per real location, all linked to the brand Organization |

Detect the vertical (restaurant, healthcare, legal, home services, real estate, automotive, retail) from page content and existing markup to choose the schema subtype.

## Canonical NAP record

One agreed record per location is the source of truth for the footer, contact page, location pages, JSON-LD and every listing. Keep it in the project-local entity file `.seo-geo-god/entity.json` (based on [entity.example.json](../templates/entity.example.json)); add a `locations` list, which is our extension:

```json
{
  "locations": [
    {
      "id": "downtown",
      "name": "Example Dental Downtown",
      "street": "[REPLACE: street and number]",
      "locality": "[REPLACE: city]",
      "region": "[REPLACE: state or region]",
      "postal_code": "[REPLACE: postal code]",
      "country": "[REPLACE: ISO 3166-1 alpha-2]",
      "phone": "[REPLACE: E.164, e.g. +15550100]",
      "url": "https://example.com/locations/downtown/",
      "hidden_address": false,
      "service_area": [],
      "hours_source": "[REPLACE: where hours are maintained]",
      "verified_by": "[REPLACE: owner name or role]",
      "verified_on": "[REPLACE: YYYY-MM-DD]"
    }
  ]
}
```

- Decide formats once: legal suffixes ("LLC", "Inc."), "Street" versus "St.", suite notation, local versus tracking phone numbers. Store the phone in E.164 for markup and render it in the local display format.
- Every field is `user-provided` by the owner or `measured` from the owner's own Business Profile export. Never infer an address, phone number or hours from third-party directories.
- Render NAP from one data source (a config file, CMS fields or the entity file) instead of hard-coding it in several components.

## NAP consistency check

[LOCAL001](rule-catalog.md#local001) (consistency across pages and LocalBusiness markup) is planned and not emitted yet, so the agent runs the check:

1. Find every place NAP appears: footer and header components, contact page, location pages, `tel:` links, map embeds, JSON-LD builders, email templates that link to the site.
2. Compare each against the canonical record after normalizing: case, punctuation and whitespace for names; abbreviations for addresses; digits only for phones (keep the country code).
3. Severity (heuristic): a different business name is critical; a different address is high; a different phone is medium; formatting-only differences are informational.
4. Fix the source of truth, not each page. Report remaining third-party listings as a user-run task.

## LocalBusiness subtypes and required properties

- Google requires `name` and `address` for the local business feature; `geo`, `openingHoursSpecification`, `telephone`, `url`, `priceRange`, `department`, `menu` and `servesCuisine` are recommended ([structured-data-matrix.md](structured-data-matrix.md#gallery-features-and-properties)). The CLI reports a missing required property as [SD008](rule-catalog.md#sd008).
- Use the most specific schema.org subtype that is true ([F-T-11](current-facts.md#f-t-11)): `Restaurant`, `CafeOrCoffeeShop`, `Bakery`, `Dentist`, `MedicalClinic`, `Physician`, `Pharmacy`, `LegalService`, `Plumber`, `Electrician`, `HVACBusiness`, `RoofingContractor`, `GeneralContractor`, `Locksmith`, `MovingCompany`, `RealEstateAgent`, `AutoDealer`, `AutoRepair`, `Store` and its subtypes. Prefer `LegalService` with a `Person` for lawyers over the older `Attorney` type.
- `geo` coordinates come from the owner or a geocoder the owner approves, with enough precision to identify the entrance (five decimal places is a common heuristic).
- `openingHoursSpecification` must match the hours the business publishes elsewhere, including special and seasonal hours where the site shows them.
- Service-area businesses that hide their address in the Business Profile should not publish a street address in markup; use `areaServed` with named places (schema.org vocabulary; not part of Google's listed properties).
- No `review` or `aggregateRating` about the business on its own site ([SD010](rule-catalog.md#sd010)); Google allows ratings on LocalBusiness only on sites that review other businesses ([F-T-65](current-facts.md#f-t-65)).
- Templates: [local-business.json](../templates/jsonld/local-business.json) ships every value as a `[REPLACE: …]` token, which the CLI reports as [SD006](rule-catalog.md#sd006) until filled.

## Multi-location graph

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.com/#organization",
      "name": "Example Dental",
      "url": "https://example.com/"
    },
    {
      "@type": "Dentist",
      "@id": "https://example.com/locations/downtown/#localbusiness",
      "name": "Example Dental Downtown",
      "url": "https://example.com/locations/downtown/",
      "parentOrganization": { "@id": "https://example.com/#organization" },
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "[REPLACE: street]",
        "addressLocality": "[REPLACE: city]",
        "addressRegion": "[REPLACE: region]",
        "postalCode": "[REPLACE: postal code]",
        "addressCountry": "[REPLACE: country code]"
      },
      "telephone": "[REPLACE: +15550100]"
    }
  ]
}
```

- One LocalBusiness node per location page, with a stable `@id` on that page's URL; the brand Organization keeps one `@id` site-wide (from [geo-entity-authority](../skills/geo-entity-authority/SKILL.md)).
- Link locations to the brand with `parentOrganization`. Older markup often uses `branchOf`, which schema.org lists as superseded (verify before changing existing markup). Departments inside one premises (a pharmacy inside a store) use `department`.
- URL pattern: `/locations/<city-or-neighborhood>/` (or `/locations/<id>/` when several sites share a city), linked from a crawlable locations index. Store locators that only render results with client-side JavaScript need server-rendered location pages too ([seo-rendering](../skills/seo-rendering/SKILL.md)).

## Location and service-area pages

A location page earns its place with facts only that location has. Content per page:

- the canonical NAP for that location, hours, directions or parking, accessibility, and a map for storefronts;
- staff or practitioners who actually work there (with the owner's and their consent), services offered at that site, local photos the business took;
- local proof that is real: projects completed in the area, local partnerships, events; never invented testimonials.

**Swap test** (from local SEO practice, adapted from claude-seo, MIT): replace the city name with another city. If the page still reads as true, it is a doorway page in the making; add real local facts or do not publish it. Generating many such pages from a dataset is programmatic SEO: apply the gates in [programmatic-seo.md](programmatic-seo.md) and the doorway and scaled-content policies in [search-policies.md](search-policies.md).

Service-area pages exist only for areas the business really serves, with area-specific information (response times, local regulations, typical jobs). A long list of town names in the footer is keyword stuffing, not a service-area page.

Titles and H1s may combine service and place when true (`Emergency plumber in [city] | [Brand]`); the CLI reports duplicates ([META003](rule-catalog.md#meta003)) and templated patterns ([META006](rule-catalog.md#meta006)).

## Google Business Profile checklist (user-run)

The owner performs these in the Business Profile interface; the agent prepares a checklist and the matching website changes. No API writes from this plugin.

- Correct business name (no keyword stuffing), primary category that describes the core business, secondary categories only where true.
- Address for storefronts, or a hidden address with defined service areas for service-area businesses.
- Hours, including holiday and special hours; phone; website link to the matching location page (not always the home page).
- Description, services or products, attributes, and real photos the business took.
- Verified status, and duplicate profiles merged or removed.
- The website URL in the profile resolves with 200 to a canonical page.

### Retired features

| Feature | Status | Fact |
| --- | --- | --- |
| Chat and call history | Removed 2024-07-31 | [F-T-45](current-facts.md#f-t-45) |
| Business Profile websites (business.site) | Turned off in 2024 (third-party reporting) | [F-T-46](current-facts.md#f-t-46) |
| Q&A API | Discontinued 2025-11-03, no replacement | [F-T-47](current-facts.md#f-t-47) |

Links on the site to retired chat or business.site pages are reported as [LOCAL002](rule-catalog.md#local002). Other 2026 Business Profile changes reported by third parties (public Q&A removal, new review rules, messaging changes) are unverified ([current-facts.md](current-facts.md#not-verified-third-party-only)); do not build features on them.

## Reviews policy

- Ask every customer the same way; do not filter who gets asked based on expected sentiment (review gating).
- Never write, buy, swap or incentivize reviews without clear disclosure; consumer-protection law in many markets prohibits fake and undisclosed incentivized reviews (the owner verifies the rules for the market).
- Respond to reviews, especially negative ones, without disclosing private information (healthcare and legal businesses have extra confidentiality duties).
- Reviews shown on the site are real, attributed and dated; markup rules are above ([SD010](rule-catalog.md#sd010), [SD011](rule-catalog.md#sd011)).
- Signs of fake reviews worth reporting to the owner (heuristic): bursts of five-star reviews, near-identical text, reviewers with no history, reviews from far outside the service area.

## Other listings

Keep the same NAP on other map and directory listings the business uses (for example Apple Business Connect, Bing Places, Yelp, industry directories, data aggregators in the market). Order: fix wrong existing listings first, then add missing ones that matter for the vertical. Claims that particular AI assistants draw local data from a specific listing service are not documented by the vendors; treat them as unverified.

## Geo-grid math (optional provider)

A geo-grid samples local rankings at points around the business. It needs a rank-data provider the user already has (for example a maps SERP API) and costs money per point, so follow the spend guard in [connectors.md](connectors.md#spend-guard-for-paid-apis) before any request. The math (adapted from claude-seo, MIT):

```text
step_km      = (2 × radius_km) / (grid_size - 1)
center_index = (grid_size - 1) / 2
for row i, column j:
  dy_km   = (i - center_index) × step_km
  dx_km   = (j - center_index) × step_km
  lat_ij  = center_lat + dy_km / 111.32
  lng_ij  = center_lng + dx_km / (111.32 × cos(center_lat in radians))
points    = grid_size²   (cost = points × keywords × the provider's unit price)
```

- Typical choices (heuristic): 5 × 5 within 3 km for dense urban areas, 7 × 7 within 5 km as a default, 9 × 9 or larger for suburban and rural service areas.
- Share of local visibility (a third-party metric) = points where the business ranks in the top 3 ÷ total points × 100. Report average rank only over points where the business appears, and count "not found" points separately.
- Store results as `{business, keyword, date, grid_size, radius_km, center, ranks: [[...]]}` with ranks row by row from north-west to south-east and `null` where not found. Rankings vary by device, time and account; one grid is a snapshot, not a trend.

## Candidate facts without an ID

| Fact | Label | Source |
| --- | --- | --- |
| Aggregator units cover local business queries in the EEA specifically | needs verification ([F-T-74](current-facts.md#f-t-74) confirms the 2026-09-18 changelog entry but names no region) | https://developers.google.com/search/updates |

## Needs verification

- Whether schema.org currently marks `branchOf` as superseded by `parentOrganization` (check schema.org before rewriting existing markup).
- Business Profile interface labels and the 2026 changes reported by third parties.
- Review and endorsement law for the business's market.
- Geo-grid provider prices and terms; never quote a price from memory.
