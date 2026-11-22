# Portfolio site architecture and checklist

Ideas below come from the research ledger (`clm_pf_*`); the code is written fresh for the freelancer's site.

## Routes

```text
app/
  layout.tsx                # metadataBase, title { default, template }, description, shared OG
  page.tsx                  # hero, services, featured case studies
  opengraph-image.tsx       # ImageResponse, 1200x630, image/png, explicit alt
  work/
    page.tsx                # case-study index
    [slug]/page.tsx         # generateStaticParams + dynamicParams = false; generateMetadata with canonical
    [slug]/opengraph-image.tsx
  about/page.tsx            # ProfilePage JSON-LD with mainEntity -> #person
  services/page.tsx
  contact/page.tsx          # PUBLIC build only; excluded entirely when SITE_MODE=proposal-safe
  sitemap.ts
  robots.ts
content/
  site.ts                   # typed single source: person, services, links (by mode), case-study index
  work/*.mdx                # case studies with frontmatter
mdx-components.tsx          # required by @next/mdx in the App Router
lib/
  schema.ts                 # JSON-LD @graph builder with stable @id nodes
  mode.ts                   # reads SITE_MODE, exposes isProposalSafe
```

## Case studies (MDX)

- `@next/mdx` needs `mdx-components.tsx` and does not parse frontmatter by default; use `remark-frontmatter` with `remark-mdx-frontmatter`, gray-matter, or `export const metadata` in each MDX file. (clm_pf_005)
- Frontmatter: `title`, `summary`, `role`, `stack`, `date`, `clientType` (anonymized), `confidential` (boolean), `cover`, `coverAlt`.
- Sections (H2 each): Overview, Problem, Approach and key decisions (two to five problem-and-solution pairs), Verification (for finance work: reconciliation against the source model, test scenarios), Outcome (real metrics only; otherwise what shipped), Role and stack. (clm_pf_013)

## Metadata and OG

- Set `metadataBase`, `title.default` and `title.template`, and `description` in the root layout; metadata exports only in Server Components. (clm_pf_003)
- Nested metadata objects such as `openGraph` are replaced, not merged, by child segments, so spread shared OG fields from a shared constant. (clm_pf_004)
- `opengraph-image.tsx` files with `ImageResponse` at 1200x630; static OG images must stay under the documented size limits or the build fails. (clm_pf_002)

## JSON-LD

- Render a native `<script type="application/ld+json">` in the layout or page, with `JSON.stringify(data).replace(/</g, "\\u003c")` to prevent script injection. (clm_pf_001)
- One `Person` node with a stable `@id` (`${SITE_URL}/#person`) referenced from `WebSite`, the About page's `ProfilePage.mainEntity`, and each case study's `CreativeWork`. (clm_pf_009, clm_pf_019)
- Person properties: `name`, `jobTitle`, `url`, `image`, `sameAs` (public build only for social profiles; the proposal-safe build lists only the Upwork profile), `knowsAbout`, `hasOccupation`, `makesOffer` (Offer of Service). Never `email`, `telephone`, or `address` in the proposal-safe build. Do not use the deprecated `ProfessionalService` type. (clm_pf_007, clm_pf_008)
- Mark up only visible content. (clm_pf_010)

## Mode switch

- `lib/mode.ts` reads `process.env.SITE_MODE` at build time. In proposal-safe mode: no `contact` route (exclude it from the build, not just from navigation), no footer email or social icons, no form components, no booking embeds, `sameAs` limited to the Upwork profile, and a "Let's continue on Upwork" call to action.
- The public build may add a contact form as a Server Action with validation, a honeypot field, and rate limiting. (clm_pf_020)
- CI: build both modes; run `contact_scan.py` on the proposal-safe output and fail on any finding.

## Quality bar

- Lighthouse-style budget: fast first load, optimized images with `next/image`, no layout shift from fonts or images.
- Accessibility: semantic headings, visible focus, keyboard navigation, alt text, color contrast, `prefers-reduced-motion` respected.
- Responsive at phone and desktop widths, checked in a real browser before handoff.

## Prior art (ideas only; see the research report for SHAs and licenses)

| Idea | Repository | License decision |
| --- | --- | --- |
| Feature checklist: MDX, sitemap, robots, JSON-LD, RSS, dynamic OG | vercel/examples `solutions/blog` (Portfolio Starter Kit) | Ideas only; note it skips JSON-LD escaping |
| MDX case studies under `/work`, per-project metadata, gated NDA pages | once-ui-system/magic-portfolio | CC BY-NC 4.0: ideas only, no code |
| JSON-LD `@graph` with stable `@id` nodes | mldangelo/personal-site | MIT, but its Person node exposes email; inverted here |
| Single data file driving content and OG | magicuidesign/portfolio | MIT, stale; idea only |
| Contact pages and mailers in stock templates | shubh73/devfolio, jirihofman/portfolio | Cited as what to strip |
