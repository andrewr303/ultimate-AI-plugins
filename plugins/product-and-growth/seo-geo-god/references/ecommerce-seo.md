# E-commerce SEO

How storefront code should handle product and merchant-listing markup, store-wide return and shipping policies, variants, category pages, faceted navigation, pagination and sorting, the availability lifecycle from in stock to discontinued, product images (including AI-generated ones), reviews, feed consistency and emerging agentic-commerce protocols. Used by [seo-ecommerce](../skills/seo-ecommerce/SKILL.md); property tables are in [structured-data-matrix.md](structured-data-matrix.md), crawl and canonical mechanics in [robots-and-directives.md](robots-and-directives.md), framework details in [framework-recipes.md](framework-recipes.md).

As of 2026-11-01. Facts are cited from [current-facts.md](current-facts.md). Platform file locations are typical defaults; themes and frameworks differ, so always read the installed version before editing.

## Platform map

| Platform (from `SG stack`) | Where product SEO lives | Facets, sort and pagination URLs |
| --- | --- | --- |
| Shopify Liquid theme | `layout/theme.liquid` (head, canonical via `canonical_url`), `sections/main-product.liquid`, `templates/product.json`, `snippets/` for meta and JSON-LD, `templates/robots.txt.liquid` for robots rules | Collection filters as `filter.*` query parameters, `sort_by=`, `?page=N`; products also reachable under `/collections/<c>/products/<p>` with a canonical to `/products/<p>` |
| WooCommerce (WordPress) | Theme overrides in `<theme>/woocommerce/` (`single-product.php`, `archive-product.php`, `content-product.php`); structured data often from WooCommerce itself or an SEO plugin (Yoast, Rank Math) | `orderby=`, layered-navigation `filter_<attribute>=`, `min_price`/`max_price`, `/page/N/` |
| BigCommerce Stencil | `templates/pages/product.html`, `templates/components/products/`, theme `config.json` | Faceted search parameters, `sort=`, `page=` |
| Magento / Adobe Commerce | Theme layout XML and templates for `Magento_Catalog`; SEO settings in the admin | Layered navigation parameters, `product_list_order=`, `p=` |
| Headless (Next.js, Remix or Hydrogen, Nuxt, Astro storefronts) | Product route (for example `app/products/[handle]/page.tsx` with `generateMetadata`), JSON-LD built in the page component from the commerce API | Defined by the app's router; check for client-only filters |

Data sources: product title, price, currency, availability, identifiers and images come from the commerce API or database. Markup must be generated from the same fields the page renders, never typed by hand.

## Product and merchant-listing markup

Two Google features read Product markup (tables in [structured-data-matrix.md](structured-data-matrix.md#gallery-features-and-properties); gallery in [F-T-01](current-facts.md#f-t-01)):

- **Product snippet**: `name` plus one of `review`, `aggregateRating` or `offers`.
- **Merchant listing** (pages where the product can be bought): `name`, a crawlable `image`, and `offers` as an `Offer` with a price greater than 0 (or `priceSpecification.price`) and `priceCurrency` ([F-T-63](current-facts.md#f-t-63)). The CLI reports a missing required property as [SD008](rule-catalog.md#sd008) and a zero or missing price or currency as [SD017](rule-catalog.md#sd017).

Code rules:

- `price` is a number or numeric string without a currency symbol (`"49.00"`, not `"$49"`); `priceCurrency` is ISO 4217; `availability` uses the full schema.org URL (`https://schema.org/InStock`).
- Use `Offer` for merchant listings. `AggregateOffer` (with `lowPrice` and `priceCurrency`) is for product snippets across sellers and is not eligible for price-drop display.
- Add identifiers you really have: `sku`, `gtin`/`gtin8`/`gtin12`/`gtin13`/`gtin14`, `mpn`, `brand.name`. Never fabricate a GTIN.
- Sale prices: a `UnitPriceSpecification` with `priceType` `https://schema.org/StrikethroughPrice` for the struck-through price, plus `validFrom` and `validThrough` or `priceValidUntil` in ISO 8601 ([SD014](rule-catalog.md#sd014)).
- `Product.category` accepts text or a `CategoryCode`; `hasAdultConsideration` is needed for adult-oriented products (needs verification, candidate fact below); member pricing (`validForMemberTier`) is beta ([F-T-64](current-facts.md#f-t-64)).
- Serialize JSON-LD with `<` escaped ([SD012](rule-catalog.md#sd012), [SD018](rule-catalog.md#sd018); patterns in [framework-recipes.md](framework-recipes.md#json-ld-escaping)).
- Mark up only what the page shows ([F-T-11](current-facts.md#f-t-11)); a price in markup that differs from the visible price is a defect.

Template: [product-merchant.json](../templates/jsonld/product-merchant.json) (Offer, shipping and return policy; no rating).

## Store-wide policies

- Google prefers return and shipping policies declared once on the `Organization` (`hasMerchantReturnPolicy`, `hasShippingService`), with Offer-level `hasMerchantReturnPolicy` or `shippingDetails` only where a product differs ([structured-data-matrix.md](structured-data-matrix.md#supporting-markup)).
- Emit the Organization node on the home page (or every page, with the same `@id`) from one config file; per-offer overrides come from product data, not template defaults.
- Policy values (return window, fees, countries, shipping rates and times) come from the owner's actual policy page; the markup must match it.

## Variants

- Group variants under a `ProductGroup` with `productGroupID`, `variesBy` and `hasVariant`; each variant is a `Product` with its own `sku`, offer and, where it has one, its own URL, linked back with `isVariantOf` or `inProductGroupWithID` (Google's product variants guidance; candidate fact below).
- URL strategy:
  - distinct variants that people search for separately (colors, models) can have their own URLs with self-referencing canonicals;
  - trivial variants (sizes) usually share one URL; a `?variant=` parameter should canonicalize to the main product URL.
- Never canonicalize all colors to one URL if each has its own images and demand; never let 30 size URLs each claim to be canonical.
- The selected variant's price and availability in markup must match what the page shows on load.

## Category pages

- Each category page has a unique title and H1, a short introduction that helps choose (not keyword filler), crawlable `<a href>` links to products, and breadcrumbs ([F-T-09](current-facts.md#f-t-09) for the breadcrumb display limit).
- Avoid near-duplicate categories ("Red Shoes" and "Shoes in Red"); merge them with a 301 and the owner's approval.
- Empty categories return 404 or are not linked; a 200 page with "no products found" is a soft 404 ([F-T-24](current-facts.md#f-t-24)).

## Faceted navigation

Google's options ([F-T-26](current-facts.md#f-t-26)):

1. **Facets that should not be crawled**: block them in robots.txt (patterns such as `Disallow: /*?*sort_by=`), or implement them so they do not create crawlable URLs (URL fragments or client state). Robots changes need the owner's approval and follow [seo-technical](../skills/seo-technical/SKILL.md).
2. **Facets that should be indexed** (a curated set with real demand, for example `/shoes/red/`): use `&` separators, a consistent parameter order, no duplicate filters, and HTTP 404 for empty or nonsensical combinations.

Rules:

- `noindex` on a URL that robots.txt blocks is never seen ([CRAWL008](rule-catalog.md#crawl008)); choose one mechanism per facet.
- Canonical tags and `nofollow` are weaker long-term controls than robots.txt or not creating the URLs.
- Indexable facet pages are real landing pages: unique title, H1 and intro, listed in the sitemap; non-indexable ones stay out of sitemaps ([SMAP008](rule-catalog.md#smap008)).
- Crawl budget matters mainly for very large or fast-changing catalogs ([F-T-29](current-facts.md#f-t-29)); for small stores, duplicate thin pages are the bigger problem.

## Pagination and sorting

- Each paginated page has its own URL (`?page=2`) and a self-referencing canonical; canonicalizing page 2 and later to page 1 is [CANON006](rule-catalog.md#canon006) and can drop products from the index ([F-T-25](current-facts.md#f-t-25)).
- Link pages with crawlable `<a href>` links; "load more" and infinite scroll need a paginated link fallback. Google does not use rel=next/prev.
- Sort orders are not separate content: disallow sort parameters in robots.txt or canonicalize sorted views to the default order, consistently.

## Availability lifecycle

| State | HTTP | Markup and page | Notes |
| --- | --- | --- | --- |
| In stock | 200 | `availability` InStock | |
| Temporarily out of stock, back order, pre-order | 200, indexable | `OutOfStock`, `BackOrder` or `PreOrder`; restock date if known; alternatives on the page | Do not noindex or 404 a product that will return ([IDX001](rule-catalog.md#idx001) with `--expect-indexable` catches accidental noindex) |
| Discontinued with a successor or close equivalent | 301 to that product | | Owner approval; [seo-migrations](../skills/seo-migrations/SKILL.md) for bulk maps |
| Discontinued without replacement | 404 or 410, removed from sitemaps and feeds | | Or keep a 200 page when it still serves owners (manuals, parts) and say so on the page |
| Seasonal | 200 all year | Availability reflects the season | Keep the URL; rebuilding it each season loses history |

Redirecting many retired products to the home page is a soft-404 risk ([REDIR005](rule-catalog.md#redir005), [F-T-24](current-facts.md#f-t-24)).

## Product images and AI-generated images

- Images are indexed from `<img src>` (including inside `<picture>`), not CSS backgrounds; supported formats include JPEG, PNG, WebP and AVIF; use the same URL for the same image ([F-T-41](current-facts.md#f-t-41)). Image sitemaps support only `image:image` and `image:loc` ([F-T-42](current-facts.md#f-t-42)).
- Markup images must be crawlable: do not block the CDN path in robots.txt ([CRAWL005](rule-catalog.md#crawl005)).
- Alt text describes the product and its distinguishing attribute ([IMG001](rule-catalog.md#img001), [IMG002](rule-catalog.md#img002)); the main product image is not lazy-loaded ([PERF002](rule-catalog.md#perf002)).
- AI-generated images in Merchant Center must carry IPTC `DigitalSourceType` `TrainedAlgorithmicMedia` metadata, and AI-generated product data must be labelled ([F-T-37](current-facts.md#f-t-37)). The IPTC value is the URI `http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia`. Embedding it is a user-run image-pipeline step (for example with the owner's existing metadata tool); this plugin installs nothing.
- Never present AI-generated or composited product images as photos of the real item.

## Reviews and ratings

- Product reviews and ratings may be marked up when they are real customer reviews of that product and visible on the page; counts and values must be consistent ([SD011](rule-catalog.md#sd011)).
- The store's own Organization or LocalBusiness does not get self-serving rating markup ([SD010](rule-catalog.md#sd010)).
- Disclose incentivized reviews; never seed sample reviews or import ratings for products the store did not collect ([search-policies.md](search-policies.md#structured-data-and-review-policies)).

## Feeds and Merchant Center (user-run)

- Merchant Center accounts, feeds and settings are operated by the owner. The agent may prepare feed files or attribute mappings in the repository; submitting them is the owner's action.
- Keep the feed, the landing page and the markup in agreement for price, currency, availability and identifiers. A quick offline check compares the feed with the built pages:

```python
import csv, re, sys
from pathlib import Path
from urllib.parse import urlsplit

# usage: python3 -I check_feed.py feed.csv dist   (feed columns include id, link, price)
feed, build = sys.argv[1], Path(sys.argv[2])
with open(feed, newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        rel = urlsplit(row["link"]).path.strip("/")
        candidates = [build / rel / "index.html", build / f"{rel}.html"] if rel else [build / "index.html"]
        page = next((p for p in candidates if p.is_file()), None)
        if page is None:
            print(row["id"], "page not in build:", rel or "/")
            continue
        html = page.read_text(encoding="utf-8", errors="replace")
        prices = re.findall(r'"price"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)', html)
        feed_price = re.sub(r"[^0-9.]", "", row["price"].split()[0]) if row["price"].strip() else ""
        if not (feed_price and any(float(p) == float(feed_price) for p in prices)):
            print(row["id"], "feed price", row["price"], "not found in page markup", prices)
```

  Treat the script's output as hints for the owner; it does not replace Merchant Center diagnostics.

## Agentic commerce (experimental)

Google's generative-AI optimization guide mentions the Universal Commerce Protocol (UCP) for agent-driven shopping ([F-AI-12](current-facts.md#f-ai-12)). Its profile format, versioning and adoption were not verified in the 2026-11-01 pass. Track it; do not add UCP files or promise any benefit until Google documents eligibility.

## Rules the ecommerce profile emphasizes

`SG audit-build <dir> --base-url <origin> --profile ecommerce` applies stricter merchant-listing checks ([SD017](rule-catalog.md#sd017)); read alongside [SD008](rule-catalog.md#sd008), [SD010](rule-catalog.md#sd010), [SD011](rule-catalog.md#sd011), [CANON006](rule-catalog.md#canon006), [IDX001](rule-catalog.md#idx001), [CRAWL008](rule-catalog.md#crawl008), [SMAP008](rule-catalog.md#smap008), [REDIR005](rule-catalog.md#redir005), [IMG001](rule-catalog.md#img001) and [PERF002](rule-catalog.md#perf002).

## Candidate facts without an ID

| Fact | Label | Source |
| --- | --- | --- |
| `hasAdultConsideration` is required for adult-oriented products | needs verification (Google lists it as a recommended merchant-listing property; its 2026-05-20 addition is [F-T-64](current-facts.md#f-t-64)) | Google merchant listing structured-data page (URL to confirm) |
| Product variants: `ProductGroup` with `hasVariant`, `variesBy` and `productGroupID`, variants linked with `isVariantOf` or `inProductGroupWithID` | needs verification (variants page not fetched in the 2026-11-01 pass) | https://developers.google.com/search/docs/appearance/structured-data/product-variants |

## Needs verification

- Platform file names and URL parameters for the installed theme or framework version.
- Whether shipping and return settings can be configured in Search Console without a Merchant Center account (reported by a source plugin, not re-verified).
- Merchant Center landing-page consistency policies and image requirements (minimum sizes are documented by Google, not re-read in this pass).
- UCP status and any Google eligibility rules for agent checkout.
