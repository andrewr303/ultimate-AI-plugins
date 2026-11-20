# International SEO and hreflang

How to tell search engines which language and regional versions of a page exist, how to route locales in code without hiding versions from crawlers, how hreflang interacts with canonicals and sitemaps, and how to check that localized pages are real equivalents rather than template copies. Used by [seo-international](../skills/seo-international/SKILL.md); sitemap mechanics are in [seo-sitemaps](../skills/seo-sitemaps/SKILL.md) and canonical policy in [robots-and-directives.md](robots-and-directives.md).

As of 2026-11-01. Google's localized-versions page was updated 2026-09-21 ([F-T-31](current-facts.md#f-t-31)). Thresholds marked "heuristic" are ours, not Google's.

## hreflang rules

These follow Google's documentation ([F-T-31](current-facts.md#f-t-31)) and map to CLI rules:

| Rule | Detail | CLI rule |
| --- | --- | --- |
| Valid codes | ISO 639-1 language, optionally a script subtag (ISO 15924) and an ISO 3166-1 alpha-2 region, joined by hyphens; or `x-default` | [HREF001](rule-catalog.md#href001) |
| Self-reference | Every version lists itself as well as every alternate | [HREF002](rule-catalog.md#href002) |
| Return links | If page A lists page B, page B must list page A; a pair that does not point both ways is ignored | [HREF003](rule-catalog.md#href003) |
| Fallback | `x-default` names the page for users whose language matches no version (often a selector or the main version); recommended, not required | [HREF004](rule-catalog.md#href004) |
| Absolute URLs | Fully qualified with protocol; cross-domain alternates are allowed | [HREF005](rule-catalog.md#href005) |
| Real targets | Each alternate is an indexable, canonical page that returns 200 | [HREF006](rule-catalog.md#href006) |
| One URL per code | A page's set never lists the same code twice | [HREF007](rule-catalog.md#href007) |
| Language attribute | `<html lang>` matches the page's own hreflang code (hygiene; Google does not use `lang`, [F-T-40](current-facts.md#f-t-40)) | [HREF008](rule-catalog.md#href008) |
| Canonical | Each version canonicalizes to itself, in its own language; never to another language | [CANON007](rule-catalog.md#canon007) |

Two points that are often overstated:

- A missing return link causes **that pair** to be ignored. It does not, by Google's wording, void the whole cluster. Report it as an error because the pair loses its benefit, not because "everything is ignored".
- hreflang is a hint for choosing which version to show, not a ranking boost and not a directive. It does not consolidate signals the way a canonical does.

## Code table and invalid examples

| Code | Valid | Reason |
| --- | --- | --- |
| `en` | yes | Language only |
| `en-GB` | yes | Language plus region |
| `pt-BR` | yes | Language plus region |
| `zh-Hant`, `zh-Hans` | yes | Script subtags are supported |
| `zh-Hans-US` | yes | Language, script and region |
| `x-default` | yes | Fallback value |
| `en-UK` | no | `UK` is a reserved code; the United Kingdom is `GB` |
| `es-419` | no | Numeric UN M.49 regions are not supported |
| `en-EU`, `fr-UN` | no | `EU` and `UN` are reserved, not countries |
| `GB`, `be` used as a country | no | Region-only codes are invalid (`be` is the Belarusian language code) |
| `en_US` | no | Underscore instead of hyphen |
| `eng`, `jp` | no | ISO 639-2 code, and a country-style code instead of `ja` |
| `es-LA` | no | Latin America is not a country; list the countries you serve |

Writing convention (ours): lowercase language, title-case script, uppercase region (`zh-Hant-TW`). Generate codes from one locale table rather than typing them in templates.

## Methods with samples

The three methods are equivalent; one is enough, and mixing them only creates more places to disagree ([F-T-31](current-facts.md#f-t-31)).

HTML, in the `<head>` of every version (best for HTML pages):

```html
<link rel="alternate" hreflang="en" href="https://example.com/guide/" />
<link rel="alternate" hreflang="de" href="https://example.com/de/anleitung/" />
<link rel="alternate" hreflang="fr-CA" href="https://example.com/fr-ca/guide/" />
<link rel="alternate" hreflang="x-default" href="https://example.com/guide/" />
```

HTTP `Link` header (for PDFs and other non-HTML files):

```
Link: <https://example.com/files/guide.pdf>; rel="alternate"; hreflang="en", <https://example.com/de/files/anleitung.pdf>; rel="alternate"; hreflang="de"
```

XML sitemap (practical for many versions or cross-domain sets; each `<url>` lists every alternate including itself):

```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/guide/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://example.com/guide/" />
    <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/anleitung/" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/guide/" />
  </url>
  <url>
    <loc>https://example.com/de/anleitung/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://example.com/guide/" />
    <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/anleitung/" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/guide/" />
  </url>
</urlset>
```

Sitemap limits still apply: 50,000 URLs or 50 MB uncompressed per file ([F-T-27](current-facts.md#f-t-27)). Alternates in sitemaps must list canonical, indexable URLs, the same as in HTML ([SMAP004](rule-catalog.md#smap004), [SMAP008](rule-catalog.md#smap008)).

## One helper for all alternates

Most hreflang defects come from each template building its own list. Generate the set once, from the route table that also builds URLs, and use it in the head, the sitemap and the language switcher:

```ts
// One source of truth: locale -> path builder. Codes are validated once here.
const LOCALES = { en: "", de: "/de", "fr-CA": "/fr-ca" } as const;
type Locale = keyof typeof LOCALES;

export function alternates(origin: string, slugs: Partial<Record<Locale, string>>, fallback: Locale = "en") {
  const links = Object.entries(slugs).map(([code, slug]) => ({
    hreflang: code,
    href: new URL(`${LOCALES[code as Locale]}/${slug}/`.replace(/\/+/g, "/"), origin).href,
  }));
  const def = links.find((l) => l.hreflang === fallback);
  return def ? [...links, { hreflang: "x-default", href: def.href }] : links;
}
```

Rules for the helper: only versions that exist and are indexable are listed (translations still in draft are left out of every set); every version gets the same list; URLs are absolute and match each page's canonical exactly, including the trailing slash.

## x-default

- Point it at a language selector or at the version you want unmatched users to see.
- One `x-default` per set; every version lists the same one.
- It is a fallback for language matching, not a redirect target and not a substitute for a missing translation.

## Canonical interplay

- Each localized page has a self-referencing canonical in its own language ([F-T-21](current-facts.md#f-t-21)). A German page that canonicalizes to the English page tells Google the German page is a duplicate, and its hreflang pair is lost ([CANON007](rule-catalog.md#canon007)).
- Regional variants with nearly identical text (en-US and en-GB) can each keep a self-canonical when hreflang connects them; Google may still pick one as canonical. Make the differences real (currency, spelling, shipping, legal details).
- Do not use robots.txt or noindex to handle duplicate locales; that removes the page instead of relating it ([F-T-21](current-facts.md#f-t-21)).
- URLs in canonical, hreflang, sitemap, `og:url` and JSON-LD must all agree; build them from the same helper.

## Routing patterns

| Pattern | Example | Strengths | Costs |
| --- | --- | --- | --- |
| Subdirectories | `example.com/de/` | One host, simplest to run, shared authority | Needs clean locale routing in one app |
| Subdomains | `de.example.com` | Separate hosting per market possible | More hosts to configure and verify |
| Country domains | `example.de` | Clear country signal to users | Separate domains to maintain; cross-domain hreflang needs return links on both sides |
| URL parameters | `example.com/?lang=de` | Easy to bolt on | Fragile: parameters are often dropped or canonicalized away; avoid for new work |

Locale routing in code:

- Every locale version must be reachable at its own URL without cookies, headers or JavaScript. Crawlers usually do not send a language preference.
- Do not force automatic redirects by IP address or `Accept-Language` (our rule; see "Needs verification"). Suggest the matching version with a dismissible banner or a selector, and keep the requested URL working.
- If the root URL must choose a locale, prefer a selector page marked as `x-default`, or a server redirect that crawlers and users can bypass through links to every version.
- Middleware that rewrites paths (`middleware.ts`, Nuxt route rules, SvelteKit `reroute` hooks, Django `LocaleMiddleware`, Rails route scopes) must not change the canonical or drop alternates on the server-rendered page.

Where locale configuration usually lives (read the installed version and [framework-recipes.md](framework-recipes.md) before editing):

| Stack | Locale routes | Where alternates are emitted |
| --- | --- | --- |
| Next.js App Router | `app/[locale]/…` plus `middleware.ts` | `generateMetadata` returning `alternates.languages` and `alternates.canonical` |
| Next.js Pages Router | `i18n` block in `next.config.*` | `next/head` in a shared layout |
| Nuxt | i18n module options in `nuxt.config.*` | the module's locale head helper, or `useHead` |
| Astro | `i18n` in `astro.config.*` | layout `<link rel="alternate">` tags; the sitemap integration has an `i18n` option |
| SvelteKit | `[[lang]]` route parameter plus hooks | `<svelte:head>` in the root layout |
| Hugo | `languages` in the site config | templates looping over translations; the built-in sitemap template |
| Docusaurus | `i18n` in the site config | the framework adds alternates for configured locales; confirm in built HTML |
| VitePress | `locales` in the site config | not added automatically in the versions we know of; add them through head config or a head-transform hook, then confirm in built HTML |
| Django, Rails, Laravel | `i18n_patterns`, `scope "(:locale)"`, route prefixes | base layout template |
| WordPress | multilingual plugin settings | the plugin's head output; confirm it is not duplicated by the theme |
| Shopify | Markets and languages settings | theme layout; confirm in rendered HTML |

## Parity checklist

Localized versions must be equivalents, not shells. Check these per template on a sample of clusters (thresholds are heuristics):

| Dimension | Check | Signal of a problem |
| --- | --- | --- |
| Existence | Every locale declared in hreflang has the page | Alternates pointing to 404s or the home page |
| Main content | Same sections and facts, translated | A localized page missing sections, or noticeably shorter than its source after allowing for language length differences |
| Metadata | Title and description translated | Source-language title on a translated page |
| Structured data | Same types and key properties; `inLanguage` matches | Missing or untranslated JSON-LD values |
| Commerce details | Local currency, units, shipping, taxes | Source-market prices on another market's page |
| Legal and compliance | Local terms, privacy and consumer law references | Another jurisdiction's law cited |
| Media | Images present with translated `alt` text | Missing images or source-language alt text |
| Freshness | Translation updated after the source changed | Source edited long after the translation (track by content hash or modified date) |
| Navigation | Menus, breadcrumbs and internal links stay in the same locale | Links that jump back to the source language |

## Machine translation quality signals

Machine translation is acceptable when people review it and it adds value; publishing many unreviewed translated pages is a scaled-content risk ([F-T-32](current-facts.md#f-t-32)). On 2025-06-11 Google stopped advising robots.txt blocks for automatically translated pages ([F-T-60](current-facts.md#f-t-60)); handle low-value translations with `noindex` (which needs the page to stay crawlable) or by not publishing them.

Signals worth flagging (all heuristic):

- Bodies identical across locales except navigation chrome: the content was never translated.
- `<html lang>` disagrees with the body language, or is missing.
- Untranslated buttons, alt text, JSON-LD values or error messages on a translated page.
- A client-side translation widget producing the only localized text (nothing localized exists in server HTML).
- Locale pages generated for markets the business does not serve.

Do not flag clearly labelled machine translations that the owner chose to publish, or interface strings that are internationalization rather than content.

## Locale formats

Format values from the locale, not by hand; the examples show the expected shape.

| Locale | Number | Date (2026-11-01) | Currency |
| --- | --- | --- | --- |
| en-US | 1,234.56 | 11/1/2026 | $1,234.56 |
| en-GB | 1,234.56 | 01/11/2026 | £1,234.56 |
| de-DE | 1.234,56 | 1.11.2026 | 1.234,56 € |
| fr-FR | 1 234,56 | 01/11/2026 | 1 234,56 € |
| ja-JP | 1,234.56 | 2026/11/1 | ￥1,235 |

In JavaScript use `Intl.NumberFormat` and `Intl.DateTimeFormat`; in other stacks use the framework's localization helpers. Machine-readable values in JSON-LD stay locale-neutral (ISO 8601 dates, `priceCurrency` codes, dot decimals).

## Per-cluster report

Report hreflang results as one row per page in each cluster:

| Cluster | Page | Code | Self | Return links | Code valid | Target 200 and indexable | Canonical same language | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| guide | https://example.com/guide/ | en | yes | 2 of 2 | yes | yes | yes | |
| guide | https://example.com/de/anleitung/ | de | yes | 1 of 2 | yes | yes | yes | missing return link from fr-CA |

Add the parity notes per cluster underneath, and state which checks were offline (build output) and which need a deployed site or Search Console.

## Needs verification

- Locale-adaptive redirects: Google's multi-regional guidance (https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites) is the usual source for "avoid automatic redirection by perceived language"; re-read it before quoting Google on this.
- Framework helpers and their option names (Nuxt i18n, Astro sitemap `i18n`, Hugo sitemap translations) change between major versions; confirm in built HTML.
- Region-specific Search features (for example aggregator units in the EEA) may change how results look per market; not covered here.
