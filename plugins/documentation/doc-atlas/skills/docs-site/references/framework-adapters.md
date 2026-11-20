# Framework adapters

## Contents

- Stack table
- Starlight, Docusaurus, VitePress, Fumadocs, Nextra
- MkDocs and Docsify
- Existing Mintlify projects
- New framework decision record

This is an inspection checklist, not a generated configuration contract.
Discover the installed major and inspect the repository's actual files first.
Read the applicable official docs for that version before emitting uncertain API names.
Keep existing package managers, component overrides, content loaders, and hosting rules.

| Stack | Identify | Preserve / inspect | Verification target |
| --- | --- | --- | --- |
| Starlight | `@astrojs/starlight`, Astro config, content configuration | Content loader/schema, native sidebar groups, custom CSS, component overrides, locale setup | Production content build, Pagefind output when enabled, direct deep links and mobile sidebar |
| Docusaurus | `@docusaurus/core`, `docusaurus.config.*`, sidebars | Docs IDs, category metadata, frontmatter, versioned docs, i18n, `url` and `baseUrl`, theme plugins | Broken-link build checks, existing version/locale routes, sidebar expansion and search |
| VitePress | `vitepress`, `.vitepress/config.*`, Vue theme entrypoint | Theme config, sidebar route groups, base, Markdown extensions, Vue components and CSS variables | Production build, built search index/provider, nested routes and theme behavior |
| Fumadocs | `fumadocs-*`, source config/loaders, app routes | Framework/router variant, content loader, page tree, MDX mappings, layout/UI variant, search route | Type/build checks, loader route coverage, server/client boundaries and search |
| Nextra | `nextra`, theme package, Next config and route files | Installed major's App/Pages Router structure, metadata/page map, MDX mappings, theme layout, Pagefind output | Next production build, metadata consistency, built search assets and sidebar focus |
| MkDocs | `mkdocs.yml`, Python requirements/lockfile, theme | Existing theme and plugins, `nav`, Markdown extensions, site URL, strict mode, language/version tooling | Existing build/strict checks, warnings, generated search and relative asset paths |
| Docsify | `index.html`, `$docsify`, Markdown pages, sidebar/navbar | Existing CDN/version choices, aliases, relative paths, plugins and history/hash routing | Serve with the expected base, direct links/hash routing, missing-page behavior and search |
| Mintlify | Existing `docs.json` or legacy `mint.json`, MDX pages | Actual schema/version, navigation groups, theme and API configuration, existing snippets/components | Available local CLI checks/preview, actual routes, API spec resolution and managed-host limits |

## Starlight

Inspect whether the repository uses the current content loader configuration or a
legacy collection setup. Do not rewrite it merely to match a newer example.
Prefer native navigation, accessible sidebar composition, and existing expressive-code
features over custom controls. Search may depend on production build output.
Verify localized navigation and content fallback if locales are already configured.

Official starting points: <https://starlight.astro.build/getting-started/>,
<https://docs.astro.build/en/guides/content-collections/>.

## Docusaurus

Read the actual sidebars and frontmatter. Folder order, numerical filename prefixes,
category metadata, and document IDs may have distinct roles.
Retain existing stable docs and generated versions; author in the intended current
source rather than editing generated/version snapshots without a reason.
Check base URL and trailing-slash policy against the actual host.
Docusaurus code and documentation can have different licenses; do not copy either
without reviewing the relevant file terms and required attribution.

Official starting point: <https://docusaurus.io/docs>.

## VitePress

Use the installed version's `defineConfig` and theme extension pattern.
Prefer existing `--vp-*` semantic variables for brand and surface customization.
Distinguish local indexing from externally hosted search: configure only the provider
actually available and avoid adding third-party credentials or accounts.
Vue components in Markdown still need browser/server compatibility checks.
Verify links under subdirectory deployments and anchors containing punctuation.

Official starting point: <https://vitepress.dev/guide/getting-started>.

## Fumadocs

Identify the actual framework and source integration; it is not exclusively a single
Next.js scaffold. Inspect installed package exports before choosing imports.
Keep content loaders, route generation, MDX components, and search schema synchronized.
Upstream source directory names may differ from published package names and change
between versions. Do not prescribe a historical `packages/ui` path or transplant
repository internals into a consumer app.
Check static-export requirements separately from server-rendered API search routes.

Official starting point: <https://fumadocs.dev/docs>.

## Nextra

Read the existing Next configuration, route structure and theme layout to determine
the installed integration. Do not mix major-version examples.
Inspect the actual page-map/metadata mechanism and preserve hidden/grouped routes.
Pagefind-based search requires generated assets; a development placeholder is not
evidence that production search works. Validate against built output.
Choose Nextra for fit or an existing stack, not an unverified freshness claim.

Official starting point: <https://nextra.site/docs>.

## MkDocs and Docsify

Keep existing MkDocs plugins/extensions and inspect their installed versions before
using theme-specific content syntax. A Material feature is not a core MkDocs feature.
Read `use_directory_urls`, site URL and navigation structure before rewriting links.
For Docsify, distinguish client-rendered Markdown from prebuilt static HTML. Preserve
its actual routing mode and verify deep links on the intended static host.
Do not introduce remote script plugins merely to obtain decorative components.

Official starting points: <https://www.mkdocs.org/user-guide/>,
<https://docsify.js.org/>.

## Existing Mintlify projects

Validate the checked-in schema and component syntax against the installed CLI and
official docs. Preserve verified navigation/API entries and product branding.
Do not fabricate an account, deployment integration, API playground endpoint,
authentication configuration or permission to send private schemas to a service.
If the preview CLI or service access is unavailable, deliver the MDX/config changes
and report which managed behaviors remain unverified.

Official starting point: <https://www.mintlify.com/docs>.

## New framework decision record

Record the reader tasks, existing stack, expected content volume, version/localization
needs, hosting constraints, and the smallest suitable choice. Confirm a stable release
and runtime compatibility from current official sources; do not select a prerelease
because an upstream default-branch manifest happens to name it.
Explain any rejected integration in one sentence tied to a real requirement.
