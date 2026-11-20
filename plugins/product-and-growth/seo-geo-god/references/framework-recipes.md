# Framework recipes

Where SEO surfaces live in each common web stack, how to change them with the smallest correct edit, and how to audit the result with the bundled CLI. Each recipe covers detection, head metadata, canonical, per-route robots, JSON-LD, sitemap, robots.txt, headers and redirects, rendering modes and pitfalls, build output and audit path, internationalization and images. Used by [seo-technical](../skills/seo-technical/SKILL.md), [seo-rendering](../skills/seo-rendering/SKILL.md), [seo-metadata](../skills/seo-metadata/SKILL.md), [seo-sitemaps](../skills/seo-sitemaps/SKILL.md), [seo-performance](../skills/seo-performance/SKILL.md), [seo-media](../skills/seo-media/SKILL.md) and the other implementation skills.

As of 2026-11-01. Search-engine facts cite [current-facts.md](current-facts.md). Framework APIs change between major versions: every recipe states the versions it assumes, and you must verify against the installed version before editing.

## How to use these recipes

1. Run `SG stack` (`SG` is `python3 -I <plugin-root>/scripts/seo_geo.py`). Its `recipe_anchors` list names the sections below that apply; a repository can match several (for example Astro docs plus a Next.js app).
2. Read the installed version: `package.json` and the lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`), `Gemfile.lock`, `composer.lock`, `requirements.txt` or `poetry.lock`, `go.mod` for Hugo modules. Then read the framework's own documentation for that version (the package README or docs shipped in `node_modules/<package>/`, the changelog, or the official site). When this file and the installed version disagree, the installed version wins; note the difference in your report.
3. Find the real files before editing. Search for the existing mechanism (`rg -n "generateMetadata|useSeoMeta|svelte:head|<title" src app`) and change it in one place; never add a second source of titles, canonicals or JSON-LD.
4. Audit the output, not the source: static output with `SG audit-build <out-dir> --base-url https://example.com`; server-rendered apps by starting the production server locally and running `SG audit-url http://localhost:3000 --live --allow-local localhost:3000` (only with the user's consent to run it; it touches only that local origin).

Common SEO surfaces and the skill that owns each:

| Surface | Owner skill | Notes |
| --- | --- | --- |
| `<title>`, meta description, Open Graph, X cards, `og:site_name`, `<html lang>`, viewport | [seo-metadata](../skills/seo-metadata/SKILL.md) | Site names also come from WebSite structured data on the home page (`name`, `url`, optional `alternateName`), domain or subdomain level only ([F-T-59](current-facts.md#f-t-59)) |
| Canonical, robots meta, X-Robots-Tag, status codes, redirects, robots.txt for search crawlers | [seo-technical](../skills/seo-technical/SKILL.md) | Mechanics in [robots-and-directives.md](robots-and-directives.md) |
| Rendering mode, client-only content, hash routes, SPA fallbacks | [seo-rendering](../skills/seo-rendering/SKILL.md) | |
| Sitemaps, `lastmod`, IndexNow payloads | [seo-sitemaps](../skills/seo-sitemaps/SKILL.md) | |
| Image components, fonts, scripts, Core Web Vitals | [seo-performance](../skills/seo-performance/SKILL.md), [seo-media](../skills/seo-media/SKILL.md) | |
| JSON-LD design and validation | [seo-structured-data](../skills/seo-structured-data/SKILL.md) | This file only shows where to inject it safely |
| hreflang clusters | [seo-international](../skills/seo-international/SKILL.md) | |
| AI-crawler groups in robots.txt | [geo-ai-access](../skills/geo-ai-access/SKILL.md) | |

## JSON-LD escaping

Every stack below needs the same safety rule: serialized JSON-LD must not contain a raw `<`, or a value such as `</script><script>` breaks out of the script element ([SD012](rule-catalog.md#sd012), [SD018](rule-catalog.md#sd018)). Replace `<` with `\u003c` after serializing; JSON parsers read it back as `<`.

```js
const json = JSON.stringify(data).replace(/</g, '\\u003c');
```

Server-render the block whenever possible: Google can read JSON-LD injected by JavaScript ([F-T-10](current-facts.md#f-t-10)), but other consumers that do not run JavaScript never see it. Validate both the template and the built HTML with `SG jsonld`; template expressions are skipped in component files ([SD019](rule-catalog.md#sd019)), so the built output is the real test.

## Next.js App Router
<a id="nextjs"></a><a id="next-js-app-router"></a>

Assumes Next.js 14 to 16 with the `app/` directory. Verify with `npm ls next`.

- **Detect:** `next` dependency; `app/` or `src/app/` containing `layout.tsx`; `next.config.(js|mjs|ts)`.
- **Head metadata:** `export const metadata: Metadata` or `export async function generateMetadata({ params })` in `layout.tsx` and `page.tsx`. Set `metadataBase: new URL('https://example.com')` in the root layout so relative URLs resolve to absolute ones. Use `title: { default: 'Brand', template: '%s | Brand' }` in the root layout and plain `title` strings in pages. In Next.js 15 and later, `params` is a Promise (`const { slug } = await params`). Client Components (`'use client'`) cannot export metadata. `<html lang>` lives in the root `layout.tsx`.
- **Streaming metadata:** from Next.js 15.2, async `generateMetadata` output can be streamed after the initial HTML, and user agents not matched by the `htmlLimitedBots` setting may receive the tags in `<body>`. If [META001](rule-catalog.md#meta001) or [CANON001](rule-catalog.md#canon001) appear only on pages with async metadata, inspect where the tags landed before changing code, and prefer a static `metadata` export where the data allows it.
- **Canonical:** `alternates: { canonical: '/blog/my-post' }` per page. Never set `alternates.canonical` in the root layout: metadata is inherited, so every child page that does not override it canonicalizes to the same URL.
- **Robots meta:** `robots: { index: false, follow: true }` per route. A site-wide `noindex` gated on an environment variable must default to indexable in production ([LAUNCH004](rule-catalog.md#launch004)).
- **JSON-LD:** in a Server Component, `<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />`.
- **Sitemap:** `app/sitemap.ts` default export returning `MetadataRoute.Sitemap` (`url`, `lastModified`, `alternates.languages`, `images`). Set `lastModified` from the content's real update time, never `new Date()` ([SMAP006](rule-catalog.md#smap006)); `changeFrequency` and `priority` are ignored by Google and Bing ([F-T-27](current-facts.md#f-t-27), [F-T-52](current-facts.md#f-t-52)). Large sites use `generateSitemaps()`; check whether your version also emits a sitemap index, and add one if it does not.
- **robots.txt:** `app/robots.ts` returning `MetadataRoute.Robots` (`rules`, `sitemap`), or a static `public/robots.txt`. Use one, not both.
- **Headers and redirects:** `next.config` `async headers()` (for example `X-Robots-Tag: noindex` on `/drafts/:path*`) and `async redirects()`; `permanent: true` sends 308, `false` sends 307. In Server Components, `permanentRedirect()` (308) and `redirect()` (307) from `next/navigation`; `notFound()` renders `not-found.tsx` with status 404. Request-time logic lives in `middleware.ts` (renamed `proxy.ts` in Next.js 16; check your version).
- **Rendering and pitfalls:** Server Components and Client Components are both rendered to HTML on the server. Content is missing from the HTML when it is fetched in `useEffect`, loaded with `dynamic(() => import('./X'), { ssr: false })`, or rendered only after a client-side auth check. `loading.tsx` and Suspense streaming are fine: the content still arrives in the same response. `output: 'export'` produces static files in `out/` and drops `headers()`, `redirects()` and middleware, so move those rules to host config.
- **Build output and audit:** `next build`; static export: `SG audit-build out --base-url https://example.com`; otherwise `next start -p 3000` and `SG audit-url http://localhost:3000 --live --allow-local localhost:3000`. Do not treat `.next/` as a static site.
- **i18n:** no built-in i18n routing in the App Router; use an `app/[lang]/` segment with middleware. Emit hreflang with `alternates.languages` (include `x-default`) and set `<html lang={lang}>` in `app/[lang]/layout.tsx`.
- **Images:** `next/image` writes `width` and `height` (or use `fill` with `sizes`). Mark the hero with `priority` (Next.js 15 and earlier) or the replacement option your version documents.

## Next.js Pages Router

Assumes Next.js 12 to 16 with a `pages/` directory (can coexist with `app/`).

- **Head metadata:** `import Head from 'next/head'` in each page; give repeated tags a `key` (`<meta name="description" key="description" content="..." />`) so later definitions replace earlier ones instead of duplicating them ([META007](rule-catalog.md#meta007)). `pages/_document.tsx` sets `<Html lang="en">`; with the `i18n` config, Next sets `lang` per locale.
- **Canonical:** build from a known origin and the route path; `router.asPath` includes the query string, so strip it before use.
- **Data and status:** `getStaticProps` or `getServerSideProps` return `{ notFound: true }` (404) or `{ redirect: { destination: '/new', permanent: true } }` (308). `fallback: 'blocking'` renders unknown static paths on the server.
- **Sitemap and robots:** a `pages/sitemap.xml.ts` route that writes XML in `getServerSideProps`, or the `next-sitemap` package as a `postbuild` script; static `public/robots.txt`.
- **i18n:** `i18n: { locales, defaultLocale }` in `next.config`; add hreflang `<link rel="alternate">` tags yourself in `<Head>`.
- Everything else (headers, redirects, JSON-LD, images, audit) follows the App Router recipe above.

## Nuxt

Assumes Nuxt 3 or 4 (Nuxt 4 places source under `app/`). Verify with `npx nuxi info`.

- **Detect:** `nuxt` dependency; `nuxt.config.ts`; `pages/` or `app/pages/`.
- **Head metadata:** `useSeoMeta({ title, description, ogTitle, ogDescription, ogImage, twitterCard: 'summary_large_image' })` in pages; defaults and `titleTemplate` in `nuxt.config` `app.head`. `useHead({ htmlAttrs: { lang: 'en' } })` or `app.head.htmlAttrs` for the language.
- **Canonical:** `useHead({ link: [{ rel: 'canonical', href: siteUrl + route.path }] })` with `siteUrl` from `useRuntimeConfig().public`. The Nuxt SEO modules (`@nuxtjs/seo`, `@nuxtjs/sitemap`, `@nuxtjs/robots`, `nuxt-schema-org`) can generate canonicals, sitemaps and robots rules; if one is installed, change its config instead of adding tags.
- **Robots meta:** `useSeoMeta({ robots: 'noindex, follow' })`, or `routeRules` with the robots module.
- **JSON-LD:** `useHead({ script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(data).replace(/</g, '\\u003c') }] })`, or `nuxt-schema-org`.
- **Headers, redirects, rendering rules:** `routeRules` in `nuxt.config`: `'/old': { redirect: { to: '/new', statusCode: 301 } }` (set the status explicitly), `'/drafts/**': { headers: { 'X-Robots-Tag': 'noindex' } }`, `'/blog/**': { prerender: true }`, `'/dashboard/**': { ssr: false }`.
- **Errors:** `throw createError({ statusCode: 404, statusMessage: 'Not Found' })` in page setup or server routes so the server response is 404.
- **Rendering and pitfalls:** SSR by default. `ssr: false` in `nuxt.config` turns the whole site into a client-rendered shell ([REND001](rule-catalog.md#rend001)). Content inside `<ClientOnly>` and data fetched in `onMounted` are missing from server HTML; `useFetch` and `useAsyncData` run on the server.
- **Build output and audit:** `nuxi generate` writes static files to `.output/public` (`SG audit-build .output/public --base-url ...`); `nuxi build` then `node .output/server/index.mjs` (port 3000 by default) for `SG audit-url http://localhost:3000 --live --allow-local localhost:3000`.
- **i18n:** `@nuxtjs/i18n` with `baseUrl` set; `useLocaleHead()` returns `htmlAttrs.lang` and hreflang links.
- **Images:** `@nuxt/image` (`<NuxtImg>`, `<NuxtPicture>`) with `width`, `height`, `sizes`; `preload` and `fetchpriority="high"` on the hero only.

## Astro

Assumes Astro 4 or 5 (Astro 5 removed `output: 'hybrid'`; static output with per-page `export const prerender = false` replaces it).

- **Detect:** `astro` dependency; `astro.config.(mjs|ts)`; `src/pages/`.
- **Head metadata:** a layout such as `src/layouts/BaseLayout.astro` owns `<head>` and takes `title`, `description` and `image` props; `<html lang="en">` sits in the same layout.
- **Canonical:** `new URL(Astro.url.pathname, Astro.site)`; requires `site: 'https://example.com'` in the config. `trailingSlash` and `build.format` change the URL form; keep canonicals, sitemap and internal links on the same form.
- **Robots meta:** a `noindex` prop on the layout that renders `<meta name="robots" content="noindex">`.
- **JSON-LD:** `<script type="application/ld+json" set:html={JSON.stringify(data).replace(/</g, '\\u003c')} />`. `set:html` does not escape anything.
- **Sitemap:** `@astrojs/sitemap` (requires `site`) writes `sitemap-index.xml` and `sitemap-0.xml`; use `filter` to drop noindex, draft and 404 pages and `serialize` to set `lastmod` from content dates; its `i18n` option adds hreflang.
- **robots.txt:** `public/robots.txt`, or `src/pages/robots.txt.ts` returning a `Response` that builds the `Sitemap:` line from `site`.
- **Redirects and status:** config `redirects: { '/old': '/new' }` becomes a meta-refresh HTML page in static output unless the adapter or host turns it into an HTTP redirect ([SPAM002](rule-catalog.md#spam002)); prefer host redirects (`_redirects`, `vercel.json`). In on-demand pages, `return Astro.redirect('/new', 301)` and `return new Response(null, { status: 404 })`. `src/pages/404.astro` builds `404.html`.
- **Rendering and pitfalls:** static HTML by default. Islands with `client:load`, `client:idle` or `client:visible` are rendered on the server and hydrated; `client:only` components are not rendered on the server at all ([REND002](rule-catalog.md#rend002)).
- **Build output and audit:** `astro build` writes `dist/` (`SG audit-build dist --base-url ...`). With the Node adapter, `node ./dist/server/entry.mjs`, or `astro preview` (port 4321), then `SG audit-url http://localhost:4321 --live --allow-local localhost:4321`.
- **i18n:** built-in `i18n` routing (`locales`, `defaultLocale`); emit hreflang through the sitemap integration or `<link rel="alternate">` in the layout.
- **Images:** `<Image>` and `<Picture>` from `astro:assets` add dimensions and lazy loading; on the hero set `loading="eager"` and `fetchpriority="high"` (newer versions offer a single priority option; check yours).

## SvelteKit

Assumes SvelteKit 2 with Svelte 4 or 5.

- **Detect:** `@sveltejs/kit`; `svelte.config.js`; `src/routes/`.
- **Head metadata:** `<svelte:head>` in `+page.svelte` and `+layout.svelte`, with values from `load` in `+page.server.ts` or `+page.ts`. `<html lang="en">` is in `src/app.html`; for per-locale values, put a placeholder such as `%lang%` there and replace it in `handle` with `transformPageChunk` in `src/hooks.server.ts`.
- **Canonical:** `<link rel="canonical" href={new URL(page.url.pathname, PUBLIC_SITE_URL).href} />` using `page` from `$app/state` (or `$page` from `$app/stores` in older releases).
- **JSON-LD:** inside `<svelte:head>`: ``{@html `<script type="application/ld+json">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>`}``.
- **Sitemap and robots:** `src/routes/sitemap.xml/+server.ts` and `src/routes/robots.txt/+server.ts` returning `Response` objects with the right `Content-Type`; add `export const prerender = true` to emit them at build time; or a static `static/robots.txt`.
- **Headers, redirects, status:** `setHeaders({ 'X-Robots-Tag': 'noindex' })` in `load`, or headers in the `handle` hook; `redirect(301, '/new')` and `error(404, 'Not found')` from `@sveltejs/kit`.
- **Rendering and pitfalls:** SSR by default. `export const ssr = false` in a `+layout.ts` or `+page.ts` makes those routes client-rendered shells ([REND001](rule-catalog.md#rend001)). With `adapter-static`, a `fallback` page (`200.html` or `index.html`) serves unknown routes as an SPA with status 200 ([REND005](rule-catalog.md#rend005)); prerender public routes instead.
- **Build output and audit:** `npm run build`; `adapter-static` writes `build/` (`SG audit-build build --base-url ...`); `adapter-node` runs with `node build` (port 3000); `vite preview` uses port 4173.
- **i18n:** route-based locales (for example `src/routes/[lang]/`) with hreflang links in the layout.
- **Images:** `@sveltejs/enhanced-img` (`<enhanced:img>`) or `<img>` with explicit dimensions.

## Remix and React Router framework mode
<a id="remix"></a><a id="react-router"></a><a id="remix-react-router"></a>

Assumes Remix v2 (Vite) or React Router v7 in framework mode (the successor to Remix).

- **Detect:** `@remix-run/*`, or `react-router` with `@react-router/dev`; `react-router.config.ts` or `remix.config.js`; `app/root.tsx` and `app/routes/`.
- **Head metadata:** `export const meta: MetaFunction = ({ data }) => [{ title: data.title }, { name: 'description', content: data.description }, { tagName: 'link', rel: 'canonical', href: data.canonical }]`, rendered by `<Meta />` and `<Links />` in `root.tsx`; `<html lang>` is in `root.tsx`. The deepest matching route's `meta` replaces its parents' meta rather than merging, so a child route that defines `meta` must repeat anything it should keep (it can read parent values from `matches`). React 19 also allows `<title>` and `<meta>` inside components; use one approach.
- **JSON-LD:** a `{ 'script:ld+json': data }` meta descriptor, or a script element with escaped `JSON.stringify`; check the built HTML with `SG jsonld`.
- **Sitemap and robots:** resource routes such as `app/routes/sitemap[.]xml.ts` and `app/routes/robots[.]txt.ts` whose `loader` returns `new Response(body, { headers: { 'Content-Type': 'application/xml' } })`.
- **Headers, redirects, status:** `export const headers` per route; `redirect('/new', 301)` from a `loader`; throw a 404 response from the loader (`throw new Response('Not Found', { status: 404 })`, or `throw data(null, { status: 404 })` in React Router v7) and render it in the `ErrorBoundary`.
- **Rendering and pitfalls:** server-rendered by default. React Router v7 `ssr: false` in `react-router.config.ts` is SPA mode, which ships one `index.html` shell ([REND001](rule-catalog.md#rend001)); `prerender: ['/', '/pricing']` (or an async function) writes static HTML for listed paths. Data loaded only in `clientLoader` is missing from server HTML.
- **Build output and audit:** `react-router build` (or `remix vite:build`) writes `build/client` and `build/server`; `react-router-serve ./build/server/index.js` (or `remix-serve`) on port 3000 for `SG audit-url`; fully prerendered sites: `SG audit-build build/client`.

## Gatsby

Assumes Gatsby 5.

- **Head metadata:** the Head API, `export const Head = ({ location }) => (<><title>...</title><meta name="description" content="..." /><link rel="canonical" href={siteUrl + location.pathname} /></>)` in pages and templates (replaces `react-helmet`). `<html lang>` through `onRenderBody({ setHtmlAttributes })` in `gatsby-ssr.js`. `siteMetadata.siteUrl` in `gatsby-config.js` is the origin.
- **JSON-LD:** a script element inside `Head` with escaped `JSON.stringify` (`dangerouslySetInnerHTML`); verify the built HTML.
- **Sitemap and robots:** `gatsby-plugin-sitemap` (uses `siteUrl`; `excludes` and `serialize` for `lastmod`); `static/robots.txt`.
- **Redirects and headers:** `createRedirect({ fromPath, toPath, isPermanent: true })` in `gatsby-node.js` becomes an HTTP redirect only with a host adapter or plugin; without one it is client-side. Headers through the adapter's config or host files.
- **Rendering and pitfalls:** static generation by default; `getServerData` makes a page server-rendered; data fetched in `useEffect` is client-only.
- **Build output and audit:** `gatsby build` writes `public/` (`SG audit-build public --base-url ...`); `gatsby serve` uses port 9000. `src/pages/404.js` builds `404.html`.
- **Images:** `gatsby-plugin-image` (`StaticImage`, `GatsbyImage`) with `loading="eager"` on the hero.

## Angular SSR
<a id="angular"></a>

Assumes Angular 17 to 20 with `@angular/ssr`; server routes with render modes arrived in Angular 19.

- **Detect:** `@angular/core`, `angular.json`, `@angular/ssr`, `server.ts`, `app.routes.server.ts`.
- **Head metadata:** `Title` and `Meta` services from `@angular/platform-browser` (`title.setTitle()`, `meta.updateTag({ name: 'description', content })`), or the route `title` property with a custom `TitleStrategy`. `<html lang>` is in `src/index.html` (localized builds set it per locale).
- **Canonical and JSON-LD:** inject `DOCUMENT` and use `Renderer2` in a service that runs during server rendering to create `<link rel="canonical">` and a `<script type="application/ld+json">` whose text is the escaped `JSON.stringify` output. Build URLs from configuration, never from `window.location`.
- **Status codes:** with server routes, `{ path: '**', renderMode: RenderMode.Server, status: 404 }` in `app.routes.server.ts`, or set `status` on the injected `RESPONSE_INIT` (Angular 19 and later) in the not-found component. Older versions set the status through the Express response in `server.ts`.
- **Rendering and pitfalls:** `RenderMode.Prerender` writes static HTML, `RenderMode.Server` renders per request, `RenderMode.Client` serves the `<app-root>` shell ([REND001](rule-catalog.md#rend001)). Without `@angular/ssr` the whole app is a client-rendered shell. Router `redirectTo` may not produce an HTTP redirect on the server in your version: check the response status, and put permanent redirects in `server.ts` or host config.
- **Sitemap and robots:** no built-in generator; a build script or an Express route in `server.ts`; `robots.txt` as a static asset (`public/` in Angular 18 and later, `src/` assets before).
- **Build output and audit:** `ng build` writes `dist/<app>/browser` (prerendered HTML) and `dist/<app>/server/server.mjs`; run `node dist/<app>/server/server.mjs` (port 4000 by default) for `SG audit-url`, or `SG audit-build dist/<app>/browser` when every public route is prerendered.
- **Images:** `NgOptimizedImage` (`ngSrc`, `width`, `height`, `priority` on the hero).

## Vite SPA and Create React App
<a id="vite-spa"></a><a id="spa-vite"></a><a id="react-spa"></a><a id="vue-spa"></a><a id="create-react-app"></a><a id="cra"></a>

Assumes a client-rendered app built with Vite (React, Vue, Svelte, Solid, Preact) or Create React App, which the React team deprecated in 2025 (verify for your project).

- **Detect:** `vite` without an SSR framework, or `react-scripts`; an `index.html` whose body is `<div id="root"></div>` or `<div id="app"></div>`.
- **What crawlers receive:** the static `index.html` shell. Head managers such as `react-helmet-async`, `@unhead/vue` or `vue-meta` change tags only after JavaScript runs. Google renders JavaScript in a queue ([F-T-22](current-facts.md#f-t-22)); many other fetchers, including AI fetchers, are reported not to (third-party, needs verification).
- **Fix ladder (smallest correct change first):**
  1. Prerender public routes at build time: `vite-ssg` for Vue; React Router v7 framework mode with `prerender`; Vike prerendering for React or Vue. Check that any headless-browser prerender tool is maintained before adopting it.
  2. Move the public part to an SSR or SSG framework from this file and keep the SPA for logged-in screens.
  3. Dynamic rendering only as a temporary workaround ([F-T-23](current-facts.md#f-t-23)).
- **Minimum fixes even without prerendering:** real `<a href="/path">` links with the History API, not `#/` routes ([REND004](rule-catalog.md#rend004), [LINK004](rule-catalog.md#link004)); a meaningful default title and description in `index.html` instead of "Vite + React" or "React App" ([META002](rule-catalog.md#meta002)); unknown routes answered with a server 404 or, as Google's documented fallback, a JavaScript-injected `noindex` ([F-T-22](current-facts.md#f-t-22)).
- **Build output and audit:** `vite build` writes `dist/` (CRA: `build/`). `SG audit-build dist --base-url ...` usually reports [REND001](rule-catalog.md#rend001) on every route; that is the evidence for the fix, and the same command proves it.
- **Host fallbacks:** `_redirects` `/* /index.html 200`, `vercel.json` catch-all rewrites, nginx `try_files ... /index.html` and Apache `FallbackResource` all turn unknown URLs into 200 responses ([REND005](rule-catalog.md#rend005)); see [Hosting and server config](#hosting-and-server-config).

## Docusaurus

Assumes Docusaurus 3.

- **Config:** `docusaurus.config.(js|ts)` `url`, `baseUrl`, `trailingSlash`; `noIndex: true` adds `noindex` to every page (staging only, [LAUNCH004](rule-catalog.md#launch004)); `themeConfig.metadata` for global tags; `headTags` for extra head elements.
- **Per page:** front matter `title`, `description`, `image`, `slug`; MDX pages can use `<Head>` from `@docusaurus/Head`. Front matter `keywords` renders a meta keywords tag, which Google ignores ([F-T-40](current-facts.md#f-t-40), [META013](rule-catalog.md#meta013)).
- **Sitemap:** the classic preset's `sitemap` options (`lastmod: 'date'` where your version supports it, `changefreq: null`, `priority: null`, `ignorePatterns` for tag and pagination pages). Accurate `lastmod` needs full git history in CI (shallow clones give every page the same date, [SMAP006](rule-catalog.md#smap006)).
- **robots.txt:** `static/robots.txt`.
- **i18n:** built-in `i18n` config emits hreflang alternates and per-locale `<html lang>`.
- **Build output and audit:** `docusaurus build` writes `build/` (`SG audit-build build --base-url ...`); `docusaurus serve` uses port 3000.

## VitePress

Assumes VitePress 1.x.

- **Config:** `.vitepress/config.(m)ts` `title`, `description`, `lang`, `head`, `cleanUrls`, `lastUpdated`, `sitemap: { hostname: 'https://example.com' }`; the `transformHead` hook adds per-page canonical and Open Graph tags.
- **Per page:** front matter `title`, `description` and `head`.
- **robots.txt:** `public/robots.txt`.
- **Build output and audit:** `vitepress build docs` writes `docs/.vitepress/dist` (`SG audit-build docs/.vitepress/dist --base-url ...`); `vitepress preview` uses port 4173.

## Hugo

Assumes Hugo 0.120 or later; the template lookup and embedded template names changed in 0.146. Verify with `hugo version`.

- **Detect:** `hugo.(toml|yaml|json)` or `config.toml`; `layouts/`, `themes/`, `content/`.
- **Config:** `baseURL = 'https://example.com/'`, `languageCode`, `title`, `enableRobotsTXT = true`, `enableGitInfo = true` (git commit dates for `.Lastmod`).
- **Head metadata:** a head partial included from `baseof.html` (`layouts/partials/head.html`, or `layouts/_partials/` in newer releases): `<title>{{ if .IsHome }}{{ site.Title }}{{ else }}{{ .Title }} | {{ site.Title }}{{ end }}</title>`, `{{ with .Description }}<meta name="description" content="{{ . }}">{{ end }}`, `<link rel="canonical" href="{{ .Permalink }}">`, `<html lang="{{ site.Language.LanguageCode }}">`. Hugo's embedded Open Graph and X card templates exist under names that depend on the version.
- **Robots meta and sitemap exclusion:** a front matter parameter such as `robots: noindex` rendered by the head partial; front matter `sitemap` settings for exclusion (per-page disabling exists only in some Hugo releases; check yours).
- **JSON-LD:** `<script type="application/ld+json">{{ $data | jsonify }}</script>`; Go templates escape values in script context, but confirm with `SG jsonld public/`.
- **robots.txt:** `layouts/robots.txt` when `enableRobotsTXT` is set.
- **Redirects:** front matter `aliases` generate meta-refresh pages ([SPAM002](rule-catalog.md#spam002)); prefer host redirects.
- **Build output and audit:** `hugo --minify` writes `public/` (`SG audit-build public --base-url ...`). Do not audit `hugo server` output: it injects live-reload scripts and uses `localhost` URLs.
- **i18n:** multilingual config; loop over `.AllTranslations` in the head partial for hreflang; the sitemap becomes an index per language.
- **Images:** image processing (`.Resize`, `.Process`) and emit `width` and `height` from the processed resource.

## Jekyll

Assumes Jekyll 4 (GitHub Pages builds with 3.x; check `Gemfile.lock`).

- **Config:** `_config.yml` `url`, `baseurl`, `title`, `description`; plugins `jekyll-seo-tag` (`{% seo %}` in `<head>` outputs title, description, canonical, Open Graph and JSON-LD), `jekyll-sitemap`, `jekyll-redirect-from` (meta-refresh pages, [SPAM002](rule-catalog.md#spam002)).
- **Per page:** front matter `title`, `description`, `sitemap: false`, `canonical_url`.
- **robots.txt:** a root `robots.txt` with empty front matter (`---` lines) so Liquid can insert `{{ site.url }}`.
- **Build output and audit:** `bundle exec jekyll build` writes `_site/` (`SG audit-build _site --base-url ...`).

## Eleventy
<a id="11ty"></a>

Assumes Eleventy 2 or 3 (3.x uses ESM `eleventy.config.js`).

- **Config:** `eleventy.config.js` or `.eleventy.js`; output `_site/` by default; layouts in `_includes/`; site data such as `_data/site.json` with `url`.
- **Head metadata:** a base layout (`_includes/base.njk`) with `<title>{{ title }} | {{ site.name }}</title>`, `<meta name="description" content="{{ description }}">`, `<link rel="canonical" href="{{ site.url }}{{ page.url }}">`.
- **JSON-LD:** Nunjucks `{{ data | dump | safe }}` does not escape `<`; add a filter that applies the escaping above.
- **Sitemap:** a `sitemap.xml.njk` template with `permalink: /sitemap.xml` and `eleventyExcludeFromCollections: true` that loops over `collections.all` and skips noindex pages. Use `date: git Last Modified` (or real content dates) for `lastmod`; file modification times are identical on fresh CI checkouts ([SMAP006](rule-catalog.md#smap006)).
- **Build output and audit:** `npx @11ty/eleventy` writes `_site/` (`SG audit-build _site --base-url ...`).
- **Images:** `@11ty/eleventy-img` outputs `width` and `height`.

## WordPress
<a id="wordpress-themes"></a>

Assumes WordPress 6.x with a classic or block theme.

- **Detect:** a theme `style.css` header, `functions.php`, `theme.json` and `templates/*.html` (block themes), `wp-content/`.
- **Head metadata:** classic themes must call `wp_head()` in `header.php` (block themes get it from core); `add_theme_support( 'title-tag' )` lets core print `<title>`, adjustable with the `document_title_parts` and `document_title_separator` filters; `<html <?php language_attributes(); ?>>`.
- **SEO plugins own the head when active:** Yoast SEO, Rank Math, All in One SEO and SEOPress print title, description, canonical, Open Graph, JSON-LD and sitemaps. Do not add theme-level duplicates ([CANON002](rule-catalog.md#canon002), [META007](rule-catalog.md#meta007)); change the plugin settings, or its filters (Yoast `wpseo_title`, `wpseo_metadesc`, `wpseo_canonical`, `wpseo_robots`; Rank Math `rank_math/frontend/title`, `rank_math/frontend/description`, `rank_math/frontend/canonical`, `rank_math/frontend/robots`).
- **Field names (read-only analysis data):** Yoast post meta `_yoast_wpseo_title`, `_yoast_wpseo_metadesc`, `_yoast_wpseo_canonical`, `_yoast_wpseo_meta-robots-noindex` and REST `yoast_head_json`; Rank Math `rank_math_title`, `rank_math_description`, `rank_math_robots`, `rank_math_canonical_url`.
- **Core behavior:** `rel_canonical()` prints canonicals on singular views; robots meta through the `wp_robots` filter; Settings > Reading > "Discourage search engines from indexing this site" adds a site-wide `noindex` ([LAUNCH004](rule-catalog.md#launch004) when shipped to production); core sitemaps at `/wp-sitemap.xml` (filters `wp_sitemaps_post_types`, `wp_sitemaps_add_provider`), replaced by SEO plugin sitemaps such as Yoast's `/sitemap_index.xml`; the virtual robots.txt comes from the `robots_txt` filter, and a physical `robots.txt` file overrides it.
- **JSON-LD:** `wp_json_encode( $data, JSON_HEX_TAG | JSON_UNESCAPED_SLASHES )` escapes `<` and `>`.
- **Redirects and status:** `wp_safe_redirect( $url, 301 ); exit;` on `template_redirect`; changing the permalink structure without redirects breaks every URL (owner approval).
- **Where to edit:** a child theme's `functions.php` or a must-use plugin in `wp-content/mu-plugins/`; never edit core or third-party plugin files.
- **Rendering:** PHP renders server-side; page builders and optimization plugins can wrap content in `#app`-style containers or delay scripts, which is fine when the content is in the HTML.
- **Local audit:** a local copy with synthetic or copied data (never the production database): `npx @wordpress/env start` (port 8888) or `wp server` (port 8080), then `SG audit-url http://localhost:8888 --live --allow-local localhost:8888`.
- **Images:** `wp_get_attachment_image()` outputs `srcset`, `sizes` and dimensions; core adds lazy loading and, since 6.3, `fetchpriority="high"` on the likely hero image; check that themes or plugins do not lazy-load the hero.

## Shopify Liquid themes
<a id="shopify"></a>

Assumes an Online Store 2.0 theme (Dawn or derived). Run `shopify theme check` for Liquid errors.

- **Detect:** `layout/theme.liquid`, `config/settings_schema.json`, `sections/`, `snippets/`, `templates/*.json`.
- **Head metadata:** `layout/theme.liquid` prints `<title>{{ page_title }}...</title>`, `<meta name="description" content="{{ page_description | escape }}">`, `<link rel="canonical" href="{{ canonical_url }}">` and the required `{{ content_for_header }}`; Dawn keeps Open Graph and X tags in `snippets/meta-tags.liquid`. `<html lang="{{ request.locale.iso_code }}">`.
- **Values are store data:** SEO titles and descriptions are edited per product, collection and page in the Shopify admin ("Search engine listing"). Changing store data is an owner action; the theme only decides how values print.
- **Robots meta:** conditional `<meta name="robots" content="noindex">` in the head for templates such as search; a per-resource `seo.hidden` metafield set to 1 hides a resource from search and the sitemap (verify for your store).
- **JSON-LD:** `{{ product | structured_data }}` prints Product markup; custom blocks `<script type="application/ld+json">{{ data | json }}</script>`; confirm in the rendered HTML that values cannot break out of the script ([SD012](rule-catalog.md#sd012)).
- **Sitemap:** generated automatically at `/sitemap.xml` (an index of product, collection, page and blog sitemaps); themes cannot edit it.
- **robots.txt:** `templates/robots.txt.liquid` customizes it; keep the default groups loop and add rules inside it, because deleting the defaults exposes cart, checkout and filter URLs.
- **Redirects:** URL redirects are store data managed in the admin (handle changes can create them automatically); owner-operated.
- **Local preview and audit:** `shopify theme dev` serves `http://127.0.0.1:9292` backed by the real store's data, so run `SG audit-url http://127.0.0.1:9292 --live --allow-local 127.0.0.1:9292` only with the owner's consent and a small `--max-pages`.
- **Markets and hreflang:** Shopify Markets prints hreflang alternates for market domains and subfolders; do not add manual duplicates.
- **Images:** `{{ image | image_url: width: 1600 | image_tag: widths: '400, 800, 1200, 1600', sizes: '100vw', loading: 'lazy' }}`; the hero section uses `loading: 'eager'` and `fetchpriority: 'high'`.

## Generic server-rendered apps
<a id="generic-ssr"></a>

The same rules apply to Django, Rails, Laravel, Express, Flask, ASP.NET, Phoenix and similar stacks: the base layout template owns `<head>`; controllers set status codes; middleware sets `X-Robots-Tag`; a library or route builds the sitemap. Build canonical and sitemap URLs from a configured origin, never from the request `Host` header (alternate hostnames create duplicate canonicals). Audit a production-like local server started with the project's documented command, with synthetic or copied data and without real credentials.

### Django

Assumes Django 4.2 to 5.x.

- **Head metadata:** `templates/base.html` with `{% block title %}` and `{% block meta_description %}`; `{% get_current_language as LANGUAGE_CODE %}` and `<html lang="{{ LANGUAGE_CODE }}">`.
- **Canonical:** the configured site origin (a setting or `django.contrib.sites`) plus `request.path`.
- **Sitemap:** `django.contrib.sitemaps` (`Sitemap` subclasses with `items()`, `location()`, `lastmod()`; `i18n = True`, `alternates = True` and `x_default = True` for hreflang); the sitemap index view for large sites.
- **robots.txt:** `path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'))`.
- **Redirects and status:** `redirect(target, permanent=True)` (301); `django.contrib.redirects` for database redirects; `APPEND_SLASH` issues 301s to slash URLs; `raise Http404` or `get_object_or_404` (the custom `404.html` renders only with `DEBUG = False`).
- **JSON-LD:** `json.dumps(data).replace('<', '\\u003c')` marked safe in the template; the `json_script` filter escapes correctly but emits `type="application/json"`, not `application/ld+json`.
- **Local audit:** production-like settings (`DEBUG = False`, `localhost` in `ALLOWED_HOSTS`) with the project's documented server command, for example a local `gunicorn` bound to `127.0.0.1:8000`, then `SG audit-url http://127.0.0.1:8000 --live --allow-local 127.0.0.1:8000`.

### Rails
<a id="ruby-on-rails"></a>

Assumes Rails 7 or 8.

- **Head metadata:** `app/views/layouts/application.html.erb` with `<title><%= content_for?(:title) ? yield(:title) : "Brand" %></title>` and `<% content_for :title, "..." %>` in views, or the `meta-tags` gem (`set_meta_tags`, `display_meta_tags`); `<html lang="<%= I18n.locale %>">`.
- **Sitemap:** the `sitemap_generator` gem (`config/sitemap.rb`); use its no-ping refresh task, because search-engine ping endpoints are retired (long-standing, not re-verified on 2026-11-01).
- **robots.txt:** `public/robots.txt` or a controller route for per-environment rules.
- **Redirects and status:** `get "/old", to: redirect("/new")` in routes sends 301; `redirect_to path, status: :moved_permanently` in controllers (the controller default is 302); `ActiveRecord::RecordNotFound` renders 404 in production.
- **JSON-LD:** `data.to_json` escapes `<`, `>` and `&` while `ActiveSupport.escape_html_entities_in_json` is true (the Rails default); confirm in the rendered HTML.
- **Local audit:** the project's documented production-mode command (for example `RAILS_ENV=production bin/rails server -p 3000` after asset precompilation), using local-only placeholder secrets, never real credentials.

### Laravel

Assumes Laravel 10 to 12.

- **Head metadata:** `resources/views/layouts/app.blade.php` with `<title>@yield('title', config('app.name'))</title>` and `@stack('meta')`; `<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">`.
- **Canonical:** `url()->current()` drops the query string but uses the request root; pin the root to `APP_URL` (for example `URL::forceRootUrl(config('app.url'))`) so canonicals never carry an alternate host.
- **Sitemap:** `spatie/laravel-sitemap` or a route returning an XML view.
- **Redirects and status:** `Route::permanentRedirect('/old', '/new')` sends 301, while `Route::redirect()` sends 302 unless you pass a status; `abort(404)` and `findOrFail()` for missing records.
- **Headers:** middleware calling `$response->headers->set('X-Robots-Tag', 'noindex')` for non-production environments.
- **JSON-LD:** `json_encode($data, JSON_HEX_TAG | JSON_UNESCAPED_SLASHES)` printed with `{!! !!}`, or Blade `@json` after checking its escaping in your version.
- **Local audit:** `php artisan serve --port=8000` with `APP_ENV=production` and `APP_DEBUG=false`; it does not apply nginx or Apache rules, so check those separately.

## Plain static HTML
<a id="static-html"></a>

- Every `.html` file has its own `<head>`: look for copy-paste duplicates of titles and descriptions ([META003](rule-catalog.md#meta003), [META005](rule-catalog.md#meta005)) and leftover template text.
- `robots.txt` and `sitemap.xml` are hand-written files at the root; headers and redirects come from the host.
- Audit the folder directly: `SG audit-build site --base-url https://example.com`.

## Hosting and server config
<a id="hosting"></a>

Host rules override framework intentions: check them whenever an audit shows unexpected status codes, headers or redirects.

### Netlify and Cloudflare Pages

`_headers` (both hosts):

```text
/drafts/*
  X-Robots-Tag: noindex
/*.pdf
  X-Robots-Tag: noindex
```

`_redirects` (both hosts):

```text
/old-page   /new-page   301
/blog/*     /articles/:splat   301
# /*  /index.html  200   <- SPA fallback: every unknown URL returns 200 (soft 404 risk)
```

- Netlify also reads `[[redirects]]` and `[[headers]]` tables in `netlify.toml`. A top-level `404.html` is served with status 404 for unmatched paths.
- Cloudflare Pages treats a project without a top-level `404.html` as a single-page app and serves the root page for unknown paths (verify in current Pages docs); ship a `404.html`. Workers static assets with `not_found_handling = "single-page-application"` behave the same way.

### Vercel

```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "redirects": [{ "source": "/old-page", "destination": "/new-page", "permanent": true }],
  "headers": [{ "source": "/drafts/(.*)", "headers": [{ "key": "X-Robots-Tag", "value": "noindex" }] }]
}
```

- `"permanent": true` sends 308, `false` sends 307. A catch-all `rewrites` entry to `/index.html` is an SPA fallback (soft 404 risk).
- Preview deployments normally receive an `X-Robots-Tag: noindex` header from Vercel (verify in current Vercel docs); the production domain must not.

### nginx

```nginx
server {
  listen 443 ssl;
  server_name example.com;
  error_page 404 /404.html;
  location / { try_files $uri $uri/ =404; }        # not: try_files $uri /index.html (soft 404)
  location /drafts/ { add_header X-Robots-Tag "noindex" always; }
  location = /old-page { return 301 https://example.com/new-page; }
}
server {
  listen 80;
  server_name example.com www.example.com;
  return 301 https://example.com$request_uri;
}
```

An `add_header` inside a `location` block replaces all `add_header` directives inherited from the server block; repeat security headers there or use an include.

### Apache

```apache
<IfModule mod_headers.c>
  <FilesMatch "\.pdf$">
    Header set X-Robots-Tag "noindex"
  </FilesMatch>
</IfModule>
Redirect 301 /old-page https://example.com/new-page
ErrorDocument 404 /404.html
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
# FallbackResource /index.html   <- SPA fallback: unknown URLs return 200 (soft 404 risk)
```

Server and CDN rule changes (redirects, headers, WAF) affect production traffic: prepare them as a diff and get owner approval before deploying.

## Verify after any change

1. Rebuild with the project's documented build command.
2. Re-run the same checks that found the problem, for example `SG audit-build dist --base-url https://example.com --expect-indexable --format md`, plus `SG sitemap dist --build-dir dist --base-url https://example.com` and `SG jsonld dist --recursive` when those surfaces changed.
3. For server-rendered apps, re-run `SG audit-url http://localhost:3000 --live --allow-local localhost:3000` against the rebuilt local server.
4. Compare with the baseline: `SG drift compare .seo-geo-god/baselines/<date>.json dist --base-url https://example.com`.
5. Report the framework version you verified against, the files changed, and which checks ran with their results; deployment and indexing are separate, later states.
