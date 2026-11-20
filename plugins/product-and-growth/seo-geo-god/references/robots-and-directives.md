# Robots, directives, canonicals and status codes

How search crawlers read robots.txt, robots meta tags, X-Robots-Tag headers, canonical links, HTTP status codes and redirects, and how to choose the right control for each URL state. This reference covers search-crawler mechanics for Google Search and Bing. AI-crawler policy (training versus grounding tokens, Content Signals, WAF rules) belongs to [geo-ai-access](../skills/geo-ai-access/SKILL.md) and [ai-crawlers.md](ai-crawlers.md); the rules here still apply to those files because they are parsed by the same robots.txt rules.

As of 2026-11-01. Facts cite [current-facts.md](current-facts.md). Thresholds marked "heuristic" are ours.

## RFC 9309 parsing rules

robots.txt is a plain-text file at the root of each origin (`https://example.com/robots.txt`). Each scheme, host and port combination has its own file; `https://www.example.com` and `https://example.com` are separate. Google follows RFC 9309 ([F-T-18](current-facts.md#f-t-18)).

| Rule | What it means in practice |
| --- | --- |
| Lines | Records end at CR, LF or CRLF. A UTF-8 byte-order mark at the start is ignored. Everything after `#` is a comment. |
| Fields | `field: value`, field names are case-insensitive. Google uses `user-agent`, `allow`, `disallow` and `sitemap`; any other field (`crawl-delay`, `noindex`, `host`, `clean-param`) is ignored by Google ([CRAWL003](rule-catalog.md#crawl003)). |
| Groups | One or more consecutive `user-agent` lines start a group; the rules that follow belong to all of them until the next `user-agent` line after a rule. A rule before any `user-agent` line belongs to no group ([CRAWL009](rule-catalog.md#crawl009)). |
| Agent matching | Product tokens are matched case-insensitively. A crawler obeys the single most specific group that names it; groups naming the same token are merged. It falls back to `User-agent: *` only when no group names it. Named groups do not inherit rules from `*`. |
| Path matching | Rules match the URL path plus query from the start. `*` matches any sequence, `$` anchors the end. The longest matching rule wins; on a tie Google applies the least restrictive rule (allow). |
| Empty values | `Disallow:` with no value allows everything. `Allow:` with no value is ignored. |
| Encoding | Use percent-encoding for non-ASCII characters and spaces in paths ([CRAWL007](rule-catalog.md#crawl007)); Google recommends it ([F-T-18](current-facts.md#f-t-18)). |
| Sitemap lines | `Sitemap:` takes an absolute URL and applies to the whole file, not to a group ([CRAWL006](rule-catalog.md#crawl006)). |

Worked example:

```text
User-agent: *
Disallow: /search
Allow: /search/help$

User-agent: Googlebot
User-agent: bingbot
Disallow: /cart/

Sitemap: https://example.com/sitemap.xml
```

Googlebot reads only its own group here, so `/search` is crawlable for Googlebot: named groups do not inherit `*` rules. If `/search` must stay blocked for everyone, repeat the rule inside the named group. `__usage_ai-training` is a policy token that `User-agent: *` must never be read as matching ([F-AI-17](current-facts.md#f-ai-17)).

## Google specifics

- Size: Google reads the first 500 KiB; rules after that are ignored ([F-T-18](current-facts.md#f-t-18), [CRAWL002](rule-catalog.md#crawl002)).
- Fetch results ([F-T-18](current-facts.md#f-t-18)):

| robots.txt response | Google's behavior |
| --- | --- |
| 2xx | Parse and obey. |
| 3xx | Followed for at least five hops ([F-T-57](current-facts.md#f-t-57)), then treated as not found. |
| 4xx other than 429 | No restrictions: everything may be crawled. A 401 or 403 does not block Google. |
| 429, 5xx, network error | Crawling stops for 12 hours, then the last cached copy is used for up to 30 days. |

- Caching: up to 24 hours, so a fix is not seen immediately ([F-T-18](current-facts.md#f-t-18)).
- `crawl-delay` does nothing for Google. Anthropic's crawlers honor it ([F-AI-04](current-facts.md#f-ai-04)); Apple and Amazon ignore it ([F-AI-35](current-facts.md#f-ai-35), [F-AI-37](current-facts.md#f-ai-37)).
- Blocking CSS, JavaScript or images that pages need for rendering can stop Google from seeing the content ([CRAWL005](rule-catalog.md#crawl005)); keep `/_next/`, `/assets/`, `/static/`, `/wp-content/` and `/wp-includes/` assets crawlable.
- Googlebot and Bingbot also feed AI features. Blocking Googlebot removes pages from Google Search, and AI Overviews and AI Mode use only indexed, snippet-eligible pages ([F-AI-11](current-facts.md#f-ai-11)); Bing applies its grounding preferences for Copilot answers to pages Bingbot crawls ([F-AI-19](current-facts.md#f-ai-19)). See [AI004](rule-catalog.md#ai004) and [ai-crawlers.md](ai-crawlers.md). Google-Extended does not control AI Overviews or AI Mode ([F-AI-06](current-facts.md#f-ai-06)).
- User-triggered Google fetchers such as Google-Agent generally ignore robots.txt ([F-AI-08](current-facts.md#f-ai-08)).

## Bing specifics

- Bing reads the same robots.txt grammar; its exact crawl-delay handling was not verified on 2026-11-01 (see [current-facts.md](current-facts.md#not-verified-third-party-only)).
- Bing supports `data-nosnippet` from 2025-10-15, which keeps marked text out of Bing snippets and Copilot answers while still indexing it ([F-T-51](current-facts.md#f-t-51)).
- Bing page-level AI preferences use `<meta name="Bingbot" content="ai-training:disallow">` and `ai-grounding:disallow` or `ai-grounding:disallowextended`, honored from 2027-02-01; NOARCHIVE and NOCACHE stop being AI signals after 2027-03-01 ([F-AI-19](current-facts.md#f-ai-19)). Policy decisions belong to [geo-ai-access](../skills/geo-ai-access/SKILL.md).
- Bing treats sitemap `lastmod` as a key signal and pairs sitemaps with IndexNow ([F-T-52](current-facts.md#f-t-52), [F-AI-21](current-facts.md#f-ai-21)).

## Robots meta and X-Robots-Tag directive table

Directives can be set in HTML (`<meta name="robots" content="...">`, or a crawler name such as `googlebot` or `bingbot` instead of `robots`) or as an HTTP header (`X-Robots-Tag: noindex`, `X-Robots-Tag: googlebot: nofollow`). The header is the only option for PDFs and other non-HTML files. Google honors robots meta tags placed in the body ([F-T-20](current-facts.md#f-t-20)); put them in `<head>` anyway so every consumer finds them.

| Directive | Effect in Google Search ([F-T-20](current-facts.md#f-t-20)) |
| --- | --- |
| `all` | Default; no restriction. |
| `noindex` | Do not show the page in results. The page must stay crawlable for the directive to be seen. |
| `nofollow` | Do not follow links on the page. |
| `none` | Same as `noindex, nofollow`. |
| `nosnippet` | No text snippet or video preview; also no use as direct input for AI Overviews and AI Mode ([F-AI-10](current-facts.md#f-ai-10)). |
| `max-snippet:[n]` | Limit snippet length to n characters (`0` equals `nosnippet`, `-1` no limit); also limits AI Overviews and AI Mode input. |
| `max-image-preview:[none\|standard\|large]` | Size of image previews. `none` here does not mean `noindex`. |
| `max-video-preview:[n]` | Seconds of video preview. |
| `notranslate` | No translation offered in results. |
| `noimageindex` | Images on the page are not indexed. |
| `unavailable_after:[date]` | Stop showing the page after the date (use ISO 8601); a past date acts like noindex ([IDX005](rule-catalog.md#idx005)). |
| `indexifembedded` | Allow indexing of content embedded through iframes despite `noindex` on the embedded URL. |
| `noarchive`, `nocache`, `nositelinkssearchbox` | Ignored by Google ([IDX003](rule-catalog.md#idx003)). For Bing, NOARCHIVE and NOCACHE carry AI meaning only until 2027-03-01 ([F-AI-19](current-facts.md#f-ai-19)). |

Combining rules:

- When several directives apply (robots meta, crawler-specific meta and header), the most restrictive wins ([IDX002](rule-catalog.md#idx002)). `index` never overrides `noindex`.
- Parse parameter values before splitting on commas: `max-image-preview: none` is a single directive.
- A platform header rule (`_headers`, `vercel.json`, nginx, Apache) can noindex whole paths without any visible tag in the HTML ([IDX004](rule-catalog.md#idx004)); check host config, not only templates.
- Google may skip rendering noindex pages, so JavaScript that removes a server-sent noindex may never run ([F-T-22](current-facts.md#f-t-22)). Send the final directive in the server response.

## Snippet controls

| Control | Scope | Google Search effect | Bing effect |
| --- | --- | --- | --- |
| `nosnippet` | Page | No snippet; no direct input to AI Overviews and AI Mode ([F-AI-10](current-facts.md#f-ai-10)) | Standard snippet control |
| `max-snippet:[n]` | Page | Caps snippet and AI input length | Standard snippet control |
| `data-nosnippet` attribute | Element (`span`, `div`, `section`) | Excludes the element's text from snippets and AI input; structured data inside stays usable | Excludes from snippets and Copilot answers ([F-T-51](current-facts.md#f-t-51)) |
| Search Console "Search generative AI" setting | Site or property | Excludes content from AI Overviews, AI Mode and Discover generative AI features; not a ranking signal elsewhere ([F-AI-09](current-facts.md#f-ai-09)) | n/a |

No file or meta tag replaces the Search Console setting; it is a Search Console action the owner performs. Snippet controls reduce visibility, so changing them is an owner decision.

## noindex vs disallow

| Goal | Use | Do not use |
| --- | --- | --- |
| Keep a crawlable page out of results | `noindex` (meta or header), page left crawlable | `Disallow` (Google then cannot see the noindex, [CRAWL008](rule-catalog.md#crawl008)) |
| Stop crawling of infinite or low-value URL spaces (internal search, sort orders, session URLs) | `Disallow` in robots.txt | `noindex` to save crawl budget ([F-T-29](current-facts.md#f-t-29)) |
| Remove a page that is gone | `404` or `410` | `noindex` on a page that no longer exists |
| Consolidate duplicates | `301`/`308` or `rel=canonical` | robots.txt or noindex ([F-T-21](current-facts.md#f-t-21)) |
| Keep private content private | Authentication, plus `noindex` and `Cache-Control: private, no-store` | robots.txt (it is public and advisory) |

A disallowed URL can still be indexed without its content if other pages link to it. Disallow controls crawling, not indexing.

## Canonical URLs

Google's signals, strongest first: redirects and `rel=canonical` (HTML `<link>` or HTTP `Link` header), then weaker signals such as sitemap inclusion ([F-T-21](current-facts.md#f-t-21)). A canonical is a strong hint, not a command.

- One absolute URL with scheme and host, from one place in the layout ([CANON002](rule-catalog.md#canon002), [CANON003](rule-catalog.md#canon003)). Use either the HTML link or the HTTP header, not both.
- Self-referencing on every indexable page; the target must return 200, be indexable and not redirect ([CANON001](rule-catalog.md#canon001), [CANON004](rule-catalog.md#canon004)).
- Same language as the page; inside an hreflang cluster each locale canonicalizes to itself ([CANON007](rule-catalog.md#canon007)).
- Prefer HTTPS URLs; Google prefers them when choosing canonicals ([F-T-21](current-facts.md#f-t-21)).
- Do not let JavaScript change the canonical from the server HTML ([F-T-21](current-facts.md#f-t-21), [F-T-22](current-facts.md#f-t-22)).
- Paginated pages self-canonicalize; never canonicalize page 2+ to page 1 ([CANON006](rule-catalog.md#canon006), [F-T-25](current-facts.md#f-t-25)). A "view all" page is the only valid alternative target.
- Strip tracking parameters (`utm_*`, `gclid`, `fbclid`) and session IDs from the canonical; build it from the route, not from the incoming request URL or `Host` header.
- Trailing slash: pick one form, redirect the other with 301/308, and keep canonicals, sitemaps and internal links on the chosen form ([CANON008](rule-catalog.md#canon008)).
- PDFs and other files: `Link: <https://example.com/guide.pdf>; rel="canonical"` header.

## Status codes and redirects

| Response | Google's handling ([F-T-24](current-facts.md#f-t-24)) | Use it for |
| --- | --- | --- |
| 200 | Eligible for indexing; not a guarantee | Live content |
| 201, 202, 204 | Limited wait for 202; 204 means no content | Not for pages |
| 301, 308 | Strong signal that the target is canonical | Permanent moves, host and protocol consolidation, trailing-slash normalization |
| 302, 303, 307 | Weak signal; source tends to stay indexed | Temporary moves only ([HTTP003](rule-catalog.md#http003)) |
| 304 | Google reuses its cached copy | Conditional requests (`If-Modified-Since`, ETag) |
| 401, 403 | Not a crawl-throttling tool | Real access control ([HTTP008](rule-catalog.md#http008)) |
| 404, 410 | Indexed URL removed over time, crawling slows | Removed or never-existing content |
| 429, 5xx | Crawling slows; persistent errors drop URLs | Overload and outages only ([HTTP001](rule-catalog.md#http001)) |

Redirect practice:

- Google follows up to 10 hops, but every hop costs crawl time; link and redirect straight to the final URL ([HTTP002](rule-catalog.md#http002), [REDIR001](rule-catalog.md#redir001)).
- Redirect each old URL to its closest equivalent. Mass redirects to the home page behave like soft 404s ([REDIR005](rule-catalog.md#redir005)).
- Prefer a server redirect over `<meta http-equiv="refresh">`; Google's meta tags page prefers a 301 ([F-T-40](current-facts.md#f-t-40), [SPAM002](rule-catalog.md#spam002)).
- Framework defaults differ: Next.js `permanent: true` and Vercel `"permanent": true` send 308; Laravel `Route::redirect` sends 302 unless told otherwise. See [framework-recipes.md](framework-recipes.md#hosting-and-server-config).
- Redirect maps for URL changes and migrations belong to [migrations.md](migrations.md) and [seo-migrations](../skills/seo-migrations/SKILL.md).
- HTTP and mixed content: serve every page over HTTPS and redirect HTTP to HTTPS with 301/308 ([HTTP007](rule-catalog.md#http007)).

## URL and index state matrix
<a id="url-index-state-matrix"></a>

Choose one state per URL class and implement it consistently in routing, templates, sitemap generation and internal links.

| URL class | Status | Robots | Canonical | Sitemap | Notes |
| --- | --- | --- | --- | --- | --- |
| Published content | 200 | indexable | self | listed | The default; `lastmod` from the real content change |
| Paginated list page 2+ | 200 | indexable | self | optional | Crawlable `<a href>` links between pages ([F-T-25](current-facts.md#f-t-25)) |
| Section that was never populated | 404 | n/a | n/a | not listed | Do not ship empty templates |
| Section temporarily empty | 200 | `noindex` | self | not listed | Remove `noindex` when content returns |
| Draft or preview | 401/403 behind auth (or 404) | `noindex` | none | not listed | Add `Cache-Control: private, no-store`; never rely on robots.txt |
| Staging or preview deploy | auth or `noindex` header site-wide | `noindex` | none | none | Must not reach production ([LAUNCH004](rule-catalog.md#launch004)) |
| Withdrawn content | 404 or 410 | n/a | n/a | not listed | 410 states intent more clearly; both remove the URL |
| Merged into another page | 301/308 to the merged page | n/a | n/a | target listed | One hop only |
| Tracking or session parameter variants | 200 | indexable | clean URL | clean URL only | Never link internally to the parameter form |
| Sort orders and low-value facets | 200 | crawl blocked by `Disallow` or use fragments | n/a | not listed | See [faceted navigation](#faceted-navigation) |
| Empty or nonsensical facet combination | 404 | n/a | n/a | not listed | [F-T-26](current-facts.md#f-t-26) |
| Internal site search results | 200 | `Disallow` the path, or `noindex` | n/a | not listed | Pick one; do not combine both |
| Out-of-stock product (returning) | 200 | indexable | self | listed | Mark availability; hand off to [seo-ecommerce](../skills/seo-ecommerce/SKILL.md) |
| Discontinued product with a successor | 301/308 to the successor | n/a | n/a | successor listed | Otherwise 404/410 |

## Faceted navigation

Faceted URLs (`?color=red&size=m`) can multiply into millions of crawlable combinations. Google's options ([F-T-26](current-facts.md#f-t-26)):

1. Facets that should not be crawled: block the parameter patterns in robots.txt (`Disallow: /*?*sort=`), or keep the filter state in a URL fragment (`#color=red`) that crawlers ignore. Canonical and `nofollow` work less well over time, and `nofollow` would have to be on every link.
2. Facets that should be indexable (for example a real "red dresses" landing page): use `&` separators, one consistent parameter order, no duplicate parameters, and return 404 for empty or nonsensical combinations and nonexistent page numbers.

In code: generate filter links in a canonical parameter order, render non-indexable filters as buttons or fragment links, and return the real 404 status from the server for empty results. Do not add `noindex` to a path you also disallow ([CRAWL008](rule-catalog.md#crawl008)).

## Pagination

- Each page gets its own URL (`?page=2` or `/page/2/`), its own self-canonical and a crawlable `<a href>` to the next and previous pages ([F-T-25](current-facts.md#f-t-25)).
- `rel=next/prev` is not used by Google ([F-T-40](current-facts.md#f-t-40)); other engines may read it, so existing tags are harmless but not a fix.
- "Load more" buttons and infinite scroll need a paginated link fallback that works without JavaScript.
- Pages in a series may share a title pattern; avoid exact duplicates by adding the page number.
- Return 404 for page numbers past the end.

## Soft 404s

A soft 404 is a 2xx response whose content signals an error or emptiness ([F-T-24](current-facts.md#f-t-24)). Common code causes:

- SPA fallbacks that serve `index.html` with 200 for every unknown path (`/* /index.html 200` in `_redirects`, nginx `try_files ... /index.html`, Apache `FallbackResource`, adapter `fallback: '200.html'`) ([HTTP004](rule-catalog.md#http004), [REND005](rule-catalog.md#rend005)).
- Catch-all routes that render "Not found" text without setting the status.
- Empty category, tag, search or facet pages returned with 200.
- Mass redirects of removed pages to the home page ([REDIR005](rule-catalog.md#redir005)).

Fixes in order of preference: return a real 404 from the server for unknown routes; for client-only routers, redirect to a server URL that returns 404, or inject `noindex` as Google's documented fallback ([F-T-22](current-facts.md#f-t-22)). Keep a custom `404.html` that returns status 404 and is not listed in the sitemap ([LAUNCH005](rule-catalog.md#launch005)). Verify with a consented `SG audit-url ... --live` probe; offline build checks cannot see status codes.

## Mobile parity

Google indexes the smartphone version of pages ([F-T-28](current-facts.md#f-t-28), snippet-only evidence, needs verification). Keep primary content, headings, links, structured data and metadata identical across responsive breakpoints and any separate mobile templates, and do not hide primary content behind interactions that only load it on demand ([F-T-58](current-facts.md#f-t-58)). A viewport meta tag is required for responsive rendering ([META009](rule-catalog.md#meta009)).

## Spam-risk code patterns

These patterns can trigger Google spam policies ([F-T-32](current-facts.md#f-t-32)). Flag them in code review; removing a third-party script may need owner approval.

| Pattern | Where to look | Rule |
| --- | --- | --- |
| `history.pushState` or `replaceState` on load without user navigation, `popstate` handlers that trap the back button, including in ad or analytics bundles | Layout scripts, tag managers, ad SDKs | [SPAM001](rule-catalog.md#spam001); enforced from 2026-06-15 ([F-T-33](current-facts.md#f-t-33)) |
| Meta refresh or JavaScript redirects to unrelated pages | Templates, middleware | [SPAM002](rule-catalog.md#spam002) |
| Serving different content when the user agent contains `Googlebot`, `bingbot` or an AI crawler name | Middleware, edge functions, inline scripts | [SPAM003](rule-catalog.md#spam003) (planned rule; check manually) |
| Hidden text, keyword blocks, doorway templates | Components and content | See [search-policies.md](search-policies.md) |

User-agent-based rendering is acceptable only when every client receives the same content, for example image format negotiation.

## Security headers as hygiene

HTTPS matters: serve all pages over HTTPS, redirect HTTP permanently and avoid mixed content ([HTTP007](rule-catalog.md#http007)); Google prefers HTTPS URLs as canonicals ([F-T-21](current-facts.md#f-t-21)). Security headers (`Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `X-Frame-Options` or CSP `frame-ancestors`, `Permissions-Policy`) protect users and the site. Treat them as hygiene, not ranking levers: no primary source in [current-facts.md](current-facts.md) ties them to rankings, so never promise a ranking effect ([HTTP006](rule-catalog.md#http006) is a planned, informational rule). Roll out CSP in report-only mode first, because a strict policy can break analytics, consent tools and embeds.

## Needs verification

- Bing's handling of `crawl-delay` and `rel=next/prev`.
- Whether other Google crawlers keep a 15 MB fetch limit (third-party).
- The mobile-first indexing completion post ([F-T-28](current-facts.md#f-t-28)).
