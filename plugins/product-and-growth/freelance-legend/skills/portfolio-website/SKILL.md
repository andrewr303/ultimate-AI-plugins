---
name: portfolio-website
description: "Plan, build, and maintain Andrew Rodriguez's personal portfolio website in his own stack (Next.js App Router, TypeScript, Tailwind, MDX case studies, Vercel): information architecture, case-study pages, services, metadata, Open Graph images, JSON-LD Person markup, and two builds: a public site that may include contact options and a proposal-safe build with no email, phone, contact form, booking, or social links that can be linked from Upwork proposals. Includes an automated pre-publish contact scan. Use for 'build my portfolio site', 'add a case study page', 'make a page I can link on Upwork', 'improve my site SEO', or 'update my portfolio'. Not for writing the case-study text itself (case-studies) or marketplace profiles (profile-optimizer)."
---

# Portfolio website

Build a fast, credible portfolio that proves the finance-plus-software combination with real case studies, written from scratch in Andrew's own stack. Research for this skill is in `../../research/2026-11-04/` (claims `clm_pf_*`); `references/architecture.md` has the file layout and code-level checklist.

Read `../../references/andrew-profile.md` (claims, confidentiality), `<data-dir>/approved-proof.md` (the live approval record; `<plugin-root>` and `<data-dir>` are defined in the `freelance-legend` router), `../../references/platform-rules.md` (contact rules), and `../../references/voice.md` for page copy. For design work, use the repository's design skills (for example `ult-design`) if installed; for SEO depth, `seo-geo-god` if installed.

## Decisions already made

- **Stack:** Next.js App Router + TypeScript + Tailwind + MDX on Vercel, matching Andrew's stack. Use Vercel's Portfolio Starter Kit feature set (MDX, sitemap, robots, JSON-LD, RSS, dynamic OG images) as a checklist, not code to copy. (clm_pf_006)
- **Original code only.** Inspiration repositories were reviewed for ideas; several are non-commercial (CC BY-NC) or unlicensed, and none is vendored. (clm_pf_016, clm_pf_021)
- **Single source of truth:** one typed content file (person, services, approved links, case-study index) feeds pages, metadata, OG images, and JSON-LD. (clm_pf_017)
- **Two builds from one repository.** `SITE_MODE=public` may include a contact page and form; `SITE_MODE=proposal-safe` is a **separate deployment** (for example a second Vercel project on a subdomain) whose build contains no contact route at all. A same-domain route set is not enough, because a client could navigate from a safe page to the public contact page. Links inside Upwork proposals and pre-contract messages point only at the proposal-safe deployment, and only after Andrew approves the link in `<data-dir>/approved-proof.md`. (clm_up_008, clm_up_009, clm_pf_012, clm_pf_020)

## Workflow

1. **Inspect.** If a site repository exists, read its README, package manager, lockfile, and current routes before changing anything; follow that repository's own instructions. Otherwise scaffold with the official `create-next-app` and the current Tailwind setup.
2. **Content first.** Draft the content file and page copy from approved proof: hero line (problem-first, the combination stated plainly), services, two to four case studies (hand drafting to `case-studies`), an About page, and no fabricated logos, testimonials, client names, or metrics. Testimonials come only from the Testimonials table in `<data-dir>/approved-proof.md`, quoted exactly.
3. **Build** following `references/architecture.md`: routes, MDX case studies with frontmatter, metadata, OG images, JSON-LD, sitemap and robots, accessibility, and performance budget.
4. **Proposal-safe gate.** Build the safe variant and scan its output:
   ```bash
   SITE_MODE=proposal-safe npm run build
   python <plugin-root>/scripts/contact_scan.py out --allow "upwork.com/freelancers/"
   ```
   Use the static export folder (`out/`) or the built HTML under `.next/server/app`. `--allow` exempts only a matched token that is itself the allowed link (the URL or match text), never other contact details near it. The scan decodes HTML entities first, catches obfuscated emails and international phone numbers, and reports any `.vcf` or `.pdf` file as `file-review`: remove it from the safe build or confirm by hand that it holds no contact details. Any finding (email, `mailto:`, `tel:`, phone, `<form>`, booking or calendar links, messaging apps, social profile links, or contact properties in JSON-LD) fails the gate. Fix the source, rebuild, rescan. Add the scan to CI when the repository has CI.
5. **Verify in a browser.** Run the site locally, check the main pages at phone and desktop widths, keyboard navigation, reduced motion, and the OG image routes; validate JSON-LD with the Rich Results Test or validator.schema.org. Report what was and was not checked.
6. **Deploy only when Andrew asks.** Deployment, DNS, and publishing are his decisions. Give him the exact steps for the two Vercel projects and environment variables; do not deploy on your own.

## Copy rules for the site

- The proposal-safe build ends pages with "Let's continue on Upwork" and his Upwork profile link, never an email or form. (clm_up_009)
- Confidential work stays anonymized; private case studies (with written client permission only) can sit behind a server-checked password gate with rate limiting, marked `noindex` and excluded from the sitemap and JSON-LD. (clm_pf_015)
- Only mark up content that is visible on the page; rich results are never guaranteed. (clm_pf_010)
- HypeStake: describe what was built, never customers, revenue, or funding.

## Output

The changed files, the two build commands, the contact-scan result for the proposal-safe output, browser checks performed, and the deployment steps left for Andrew.
