# Core Web Vitals and performance

What Core Web Vitals measure, how to read field and lab data, how to diagnose LCP, INP and CLS in code, what the bundled static checks can and cannot tell you, and how to read Lighthouse, PageSpeed Insights and CrUX exports without unit mistakes. Used by [seo-performance](../skills/seo-performance/SKILL.md) and, for media weight and image loading, by [seo-media](../skills/seo-media/SKILL.md).

As of 2026-11-01. Facts cite [current-facts.md](current-facts.md). Numbers marked "heuristic" are ours or common practice, not Google thresholds.

## Thresholds

| Metric | Good | Needs improvement | Poor | What it measures |
| --- | --- | --- | --- | --- |
| LCP (Largest Contentful Paint) | 2.5 s or less | above 2.5 s up to 4.0 s | above 4.0 s | When the largest content element in the viewport rendered |
| INP (Interaction to Next Paint) | 200 ms or less | above 200 ms up to 500 ms | above 500 ms | Latency from user input to the next frame, across the visit |
| CLS (Cumulative Layout Shift) | 0.1 or less | above 0.1 up to 0.25 | above 0.25 | Unexpected layout movement (unitless score) |

- Source: [F-T-13](current-facts.md#f-t-13). A page or origin passes when the 75th percentile of real-user visits is "good" for all three, assessed separately for phone and desktop.
- Rating rule used by `SG perf` and `data/thresholds.json`: value at or below the good bound is good, at or below the poor bound is needs improvement, otherwise poor.
- INP replaced FID on 2024-03-12 ([F-T-14](current-facts.md#f-t-14)). FID is not a current metric; never report or target it.
- FCP (1.8 s / 3.0 s) and TTFB (0.8 s / 1.8 s) ratings are web.dev diagnostic guidance, not Core Web Vitals, and were not re-verified on 2026-11-01 (needs verification; listed as a candidate fact in [current-facts.md](current-facts.md#candidate-facts-without-an-id-yet)).
- Ranking: Google Search's Core Web Vitals page says good scores align with what its core ranking systems seek to reward, without calling them a direct ranking factor ([F-T-54](current-facts.md#f-t-54)). Treat good Core Web Vitals as a user-experience goal and one of many inputs, never as a guaranteed ranking lever.

## Field vs lab

| | Field data | Lab data |
| --- | --- | --- |
| Source | Real Chrome users (CrUX), shown in Search Console's Core Web Vitals report, the CrUX API and CrUX History API | Lighthouse in DevTools, the Lighthouse CLI, PageSpeed Insights lab section, WebPageTest |
| Window | Rolling 28 days, about two days behind ([F-T-16](current-facts.md#f-t-16)) | One synthetic load on throttled hardware |
| Measures INP | Yes | No; Total Blocking Time is only a lab proxy |
| Good for | Deciding whether there is a real problem and proving a fix | Diagnosing causes and checking a change before deploy |
| Limits | Needs enough traffic; low-traffic URLs fall back to origin data or have none | Does not represent real devices or networks; scores vary run to run |

Rules:

- Decide from field data when it exists. Use lab data to find causes, not to declare a pass.
- A Lighthouse performance score is a lab summary, not a Core Web Vital and not a value Google Search documents as a ranking input. Do not promise ranking changes from it.
- A field-data improvement can be confirmed only after a new 28-day window that contains mostly post-deploy traffic. Before that, report "deployed, field effect not yet measurable".
- When only lab data exists, say so ([PERF009](rule-catalog.md#perf009)) and do not label the page as passing Core Web Vitals.

## LCP subparts

LCP breaks into four sequential phases. CrUX reports them for image LCP elements (added to the CrUX API in the January 2025 release, [F-T-56](current-facts.md#f-t-56)).

| Subpart | Starts | Ends | Typical causes | Code levers |
| --- | --- | --- | --- | --- |
| Time to first byte | Navigation | First HTML byte | Slow server rendering, no caching, redirects, cold functions | Cache HTML at the edge, SSG or ISR, remove redirect hops, stream HTML |
| Resource load delay | First byte | LCP resource request starts | Image discovered late (CSS background, JavaScript-inserted, lazy-loaded) | Put the image in server HTML as `<img>`, `fetchpriority="high"`, `<link rel="preload">` for CSS or JS-discovered images, never `loading="lazy"` on it ([PERF002](rule-catalog.md#perf002), [PERF003](rule-catalog.md#perf003)) |
| Resource load duration | Request starts | Resource downloaded | Oversized files, no responsive sizes, slow CDN | `srcset` and `sizes`, AVIF or WebP, correct intrinsic size, CDN caching |
| Element render delay | Resource downloaded | Element painted | Render-blocking CSS or JS, web fonts for text LCP, hydration before paint, client-side rendering | Inline critical CSS, `defer` scripts ([PERF004](rule-catalog.md#perf004)), `font-display`, server-render the LCP element |

Diagnosis heuristic (heuristic, from claude-seo's subpart tool): a subpart whose p75 is at least 40% of p75 LCP is the one to fix first. The four p75 values do not add up to p75 LCP, because percentiles are computed separately; compare shares, not sums. When the LCP element is text, the image subparts do not apply: look at TTFB, render-blocking resources and font loading.

## INP and long tasks

INP is driven by main-thread work that runs when a user clicks, taps or types: input delay (the thread is busy), processing time (event handlers) and presentation delay (rendering the next frame).

Common causes in code and the fix to try first:

| Cause | Fix |
| --- | --- |
| Long tasks from large hydration or bundle evaluation | Split bundles by route, hydrate less (islands, server components, `client:visible`-style directives), defer non-critical widgets |
| Heavy event handlers (filtering large lists, synchronous state updates) | Yield to the main thread (`await scheduler.yield()` where supported, `setTimeout` fallback), React `startTransition` or `useDeferredValue`, move work to a Web Worker |
| Third-party scripts (tag managers, chat, A/B testing) | Load after interaction or idle, remove unused tags; changing marketing tags may need owner approval |
| Layout thrashing (read-then-write loops on layout properties) | Batch DOM reads and writes, use `requestAnimationFrame` |
| Very large DOM | Paginate or virtualize long lists, `content-visibility: auto` for off-screen sections |

The 50 ms "long task" boundary is the browser's long-task definition used by tooling; treat any specific INP budget per handler as a heuristic. Static HTML checks cannot measure INP; only field data (or lab interaction traces) can.

## CLS sources
<a id="cls"></a>

CLS sums unexpected layout shifts within the worst session window (shifts less than 1 s apart, window at most 5 s; [F-T-55](current-facts.md#f-t-55)). Shifts that follow a user input within 500 ms are excluded (web.dev definition; needs verification, listed as a candidate fact in [current-facts.md](current-facts.md#candidate-facts-without-an-id-yet)).

| Source | Fix in code | Static check |
| --- | --- | --- |
| Images and video without dimensions | `width` and `height` attributes or CSS `aspect-ratio`; framework image components usually add them | [PERF001](rule-catalog.md#perf001) |
| Ads, embeds and iframes | Reserve space with `min-height` or `aspect-ratio` on the container | Not detected offline |
| Late banners (cookie consent, promotions) inserted above content | Overlay them (`position: fixed`) or reserve space | Not detected offline |
| Web fonts swapping metrics | `font-display: swap` or `optional`, `size-adjust` and metric overrides on the fallback, preload the main font file | Not detected offline |
| Content injected after hydration (client-only components replacing server placeholders) | Render the same markup on the server, or give placeholders the final size | Partly visible as client-only roots ([seo-rendering](../skills/seo-rendering/SKILL.md)) |

## Static risk signals and their limits

`SG perf <dir-or-file>` reads built HTML only. It finds risk signals, not measurements.

| Rule | Signal | Why it matters | Limit |
| --- | --- | --- | --- |
| [PERF001](rule-catalog.md#perf001) | `<img>` without `width`/`height` or `aspect-ratio` | CLS risk | CSS outside the HTML may already size the image |
| [PERF002](rule-catalog.md#perf002) | Likely LCP image has `loading="lazy"` | Delays LCP | "Likely LCP" is a guess: first large image in the first part of the document |
| [PERF003](rule-catalog.md#perf003) | Likely LCP image without `fetchpriority="high"` or preload | Resource load delay | Same guess; text LCP pages are unaffected |
| [PERF004](rule-catalog.md#perf004) | Synchronous `<script src>` in `<head>` without `defer`, `async` or `type="module"` | Render delay | Small, cached scripts may be harmless |
| [PERF005](rule-catalog.md#perf005) | `unload` or `beforeunload` listener in inline scripts | Can block the back/forward cache | External bundles are not scanned |
| [PERF006](rule-catalog.md#perf006) | `<link rel="prerender">` | Deprecated hint | Speculation rules replace it |
| [PERF007](rule-catalog.md#perf007) | HTML document over 1 MB (heuristic) | Parse and transfer cost | Different from the 2 MB Googlebot limit ([HTTP005](rule-catalog.md#http005), [F-T-19](current-facts.md#f-t-19)) |
| [PERF008](rule-catalog.md#perf008) | Field metric needs improvement or poor (from `--crux` or `--lighthouse` field data) | Real-user problem | Only as current as the export |
| [PERF009](rule-catalog.md#perf009) | Only lab data available | Pass/fail cannot be claimed | Supply a CrUX export to close it |

The checks never see JavaScript bundles, CSS files, server timing, fonts loaded from CSS or third-party tags injected at runtime.

## bfcache and speculation rules

These improve navigation speed for users; no primary source says they are ranking inputs.

- Back/forward cache: avoid `unload` handlers (use `pagehide` or `visibilitychange`), close open connections on `pagehide`, and do not send `Cache-Control: no-store` on public HTML unless the page is truly private. Chrome's handling of `no-store` pages is evolving; check Chrome's bfcache documentation before asserting it blocks the cache.
- Speculation rules: `<script type="speculationrules">{"prerender":[{"where":{"href_matches":"/*"},"eagerness":"moderate"}]}</script>` (or the `Speculation-Rules` header) prefetches or prerenders likely next pages in supporting browsers. Exclude logout, add-to-cart and other state-changing URLs, and remember analytics may count prerenders unless they wait for activation.
- `<link rel="prerender">` is deprecated ([PERF006](rule-catalog.md#perf006)); replace it with speculation rules or `<link rel="prefetch">`.

## CrUX and PSI usage and units
<a id="crux-psi-usage-and-units"></a>

The plugin never calls these APIs. The user runs them with their own key from an environment variable and saves the JSON for `SG perf --crux FILE` or `SG perf --lighthouse FILE`. Never paste a key into chat or commit it.

| Source | Endpoint and limits | Field data | Notes |
| --- | --- | --- | --- |
| CrUX API | `POST https://chromeuxreport.googleapis.com/v1/records:queryRecord`; API key required; 150 queries per minute per project; 28-day window ([F-T-16](current-facts.md#f-t-16)) | Yes, p75 and histograms per metric, origin or URL, per form factor | Preferred field source. A 404 means not enough Chrome traffic for that URL or origin. |
| CrUX History API | Weekly time series of the same metrics | Yes | Use for trends after a deploy |
| PageSpeed Insights API v5 | `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`; key optional but recommended | Included as of 2026-11-01, but Google plans to stop including it ([F-T-17](current-facts.md#f-t-17)) | Use for Lighthouse lab data |
| Lighthouse JSON (LHR) | Local CLI or DevTools export | No | Lab only; category scores can be null and must be skipped, not counted as 0 |

User-run example (the key stays in the environment):

```bash
curl -s -X POST "https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=${CRUX_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{"origin": "https://example.com", "formFactor": "PHONE"}' > crux-origin-phone.json
```

Unit gotchas:

| Value | CrUX API | PSI `loadingExperience` | Lighthouse audits |
| --- | --- | --- | --- |
| CLS p75 | String, for example `"0.05"` | Integer CLS x 100 in `CUMULATIVE_LAYOUT_SHIFT_SCORE` (10 means 0.10) | Float `numericValue` |
| LCP, INP | Milliseconds (number) | Milliseconds | Milliseconds (lab LCP; no INP) |
| Form factor | `PHONE`, `DESKTOP`, `TABLET` or omitted for all | `strategy=mobile` or `desktop` | Emulated device setting |

Metric names in CrUX responses include `largest_contentful_paint`, `interaction_to_next_paint`, `cumulative_layout_shift` and, for image LCP subparts, `largest_contentful_paint_image_time_to_first_byte`, `..._resource_load_delay`, `..._resource_load_duration` and `..._element_render_delay`. Check the CrUX API page for the current names before parsing a new export.

## Experimental metrics

- CrUX soft-navigation variants of LCP, INP and CLS for single-page apps (September 2026 release, [F-T-15](current-facts.md#f-t-15)). Report them as experimental and informational; they are not pass/fail inputs.
- CrUX experimental ad metrics (count, density, CPU and network weight) are listed on the CrUX API page; their launch date is third-party only.
- A possible Search Console switch to soft-navigation metrics in 2027 is third-party only ([current-facts.md](current-facts.md#not-verified-third-party-only)).
- Lighthouse's Agentic Browsing category is experimental and reports a pass ratio, not a score ([F-AI-27](current-facts.md#f-ai-27)); it belongs to [geo-agent-readiness](../skills/geo-agent-readiness/SKILL.md).

## Framework levers

| Stack | LCP image | Fonts | Scripts | Recipe |
| --- | --- | --- | --- | --- |
| Next.js | `next/image` with the priority or preload option on the hero; `sizes` for responsive images | `next/font` (self-hosted, metric fallbacks) | `next/script` `strategy` (`afterInteractive`, `lazyOnload`) | [Next.js App Router](framework-recipes.md#nextjs-app-router) |
| Nuxt | `<NuxtImg preload fetchpriority="high">` | `@nuxt/fonts` or self-hosted with `font-display` | `useScript` or deferred plugins | [Nuxt](framework-recipes.md#nuxt) |
| Astro | `<Image>` from `astro:assets` with `loading="eager"` and `fetchpriority="high"` on the hero | Self-hosted `@font-face` with `font-display` | Islands load only where `client:*` is used | [Astro](framework-recipes.md#astro) |
| SvelteKit | `<enhanced:img>` (enhanced-img plugin) or `<img>` with dimensions | Self-hosted, preload in `+layout.svelte` | Route-level code splitting by default | [SvelteKit](framework-recipes.md#sveltekit) |
| Angular | `NgOptimizedImage` with the `priority` attribute | Font inlining in production builds | `@defer` blocks for heavy components | [Angular SSR](framework-recipes.md#angular-ssr) |
| Gatsby | `gatsby-plugin-image` with `loading="eager"` on the hero | Self-hosted | Gatsby `Script` component `strategy` | [Gatsby](framework-recipes.md#gatsby) |
| WordPress | Remove lazy loading from the hero (core skips the first content image; plugins may override); `fetchpriority` support since WordPress 6.3 | Theme `font-display` in `@font-face` | Defer plugin scripts; audit plugin-added assets | [WordPress](framework-recipes.md#wordpress) |
| Shopify | `image_url` with `width` and `image_tag` with `loading: 'eager'`, `fetchpriority: 'high'` on the hero section | `font_face` filter with `font_display: 'swap'` | Limit app embeds | [Shopify Liquid themes](framework-recipes.md#shopify-liquid-themes) |

Framework option names change between major versions; confirm each against the installed version before editing.

## Anti-hallucination list

Never write or accept any of these:

- No "Core Web Vitals 2.0", no "Visual Stability Index" and no new 2025 or 2026 thresholds: none exist; thresholds are unchanged ([F-T-13](current-facts.md#f-t-13)).
- No FID as a current metric or target; INP replaced it ([F-T-14](current-facts.md#f-t-14)).
- No "LCP must be under 2.0 s" or any other invented threshold.
- No Lighthouse score presented as a Core Web Vital, a ranking factor or a "penalty".
- No claim that poor Core Web Vitals get a site penalized, and no promise that good Core Web Vitals lift rankings.
- No TTFB, FCP, Speed Index or Total Blocking Time presented as Core Web Vitals.
- No pass rates or percentages of sites passing without a dated CrUX source.
- No claim that speculation rules, preloads or bfcache are ranking inputs.
