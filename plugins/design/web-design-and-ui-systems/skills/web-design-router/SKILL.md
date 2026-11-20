---
name: web-design-router
description: "Entry-point router for the Web Design & UI Systems plugin (43 skills). Use when starting a UI/UX or web design task and unsure which skill fits: choosing a visual direction or aesthetic design system, searching styles, palettes, fonts and stack guidelines, building a landing or pricing page, defining brand and design tokens, making slides, or adding border, shadow, mask and status-indicator details. Picks the 1-2 best skills in order and says so when none fits."
argument-hint: "[task description or goal to route to the best skill(s) in Web Design & UI Systems]"
metadata:
  plugin: web-design-and-ui-systems
  category: router
  version: "2.16.0"
---

# Web Design & UI Systems Router (`web-design-router`)

Routes a request to the one or two most precise skills in this plugin, then follows their workflow.

## Core Routing Principles

1. **Route to the most specific skill, not a generic neighbor.** Match the exact artifact, framework, or visual style named in the request.
2. **Select 1-2 skills in execution order.** Pick one primary skill when it covers the request. Add a second only when the task spans two phases (for example design system selection, then micro-interaction polish).
3. **Load the selected `SKILL.md` files before writing code or output**, plus any file under that skill's `references/` that it tells you to read.
4. **Say so when nothing fits.** If the request names a skill or style this plugin does not contain (for example shadcn/ui component styling), say that it is not bundled, then use the closest skill below (`tailwindcss` for utility styling, `ui-ux-pro-max` for design guidance) or answer without a skill.

## Before routing: things some skills need

- `ui-ux-pro-max` runs a local Python 3 search script (standard library only, no network). If Python is missing, ask the user to install it; do not install it yourself.
- `design` can send logo, corporate-identity and image prompts to a third-party image provider with the user's own API key. Ask the user before the first call. Without a key, use its offline search scripts only.
- `build-daily-inspiration-sites` needs Codex task tools and the Sites plugin. In another host, stop after its validation step.
- `design-system` includes `fetch-background.py`, which downloads stock images from Pexels or Unsplash. Run it only when the user wants fetched backgrounds. The other `brand`, `design-system` and `slides` scripts read local project files.

---

## Decision Tree

```text
User request (web design, UI/UX, brand, or surface styling)
|
+-- 1. Searchable UI/UX intelligence (79 styles, 192 palettes, 74 font pairings, 22 stacks)?
|   `-- `ui-ux-pro-max` (run its search script first)
|
+-- 2. Brand identity, logos, tokens, decks, utility CSS?
|   +-- Logo generation (55 styles) or corporate identity mockups (CIP)? -> `design`
|   +-- Brand voice, tone, messaging frameworks, asset validation? -------> `brand`
|   +-- 3-tier tokens (primitive > semantic > component)? ----------------> `design-system`
|   +-- Social, ad or hero banner art direction and generation? ----------> `banner-design`
|   +-- HTML presentation slides with Chart.js and copy formulas? -------> `slides`
|   +-- Tailwind CSS utility recipes? ------------------------------------> `tailwindcss`
|   `-- Writing a spec-driven prompt for a UI generator? -----------------> `design-first-ui-prompting`
|
+-- 3. Building a full page?
|   +-- High-converting single-offer SaaS landing page? ------------------> `landing-page`
|   +-- SaaS pricing tiers, comparison matrix, FAQs, conversion copy? ----> `pricing-page`
|   +-- Product-led SaaS page with a live, deterministic UI demo? --------> `product-proof-saas`
|   +-- Enterprise AI, security or operations page with governance proof? > `operational-enterprise-ai`
|   +-- Motion-rich Awwwards-level marketing or editorial site? ----------> `build-awwwards-quality-sites`
|   `-- Five original landing builds from a daily inspiration capture? ---> `build-daily-inspiration-sites`
|
+-- 4. A specific aesthetic design system (21 curated systems)?
|   +-- Clean light, paper:
|   |   +-- Warm paper + orange accent SaaS? -----------------------------> `orange-clean-paper-saas`
|   |   `-- Light technical paper with dark framing and brackets? --------> `light-mode-paper-technical`
|   +-- Editorial, agency:
|   |   +-- Minimal agency grid, oversized type, uppercase labels? -------> `agency-grid-layout-minimal`
|   |   +-- Nested container clean agency shell? -------------------------> `nested-container-clean-agency`
|   |   +-- Documentary brutalist agency (hard B&W, billboard type)? -----> `documentary-brutalist-agency`
|   |   `-- Salon, spa, clinic or hospitality editorial booking? ---------> `editorial-service-booking`
|   +-- Dark glass, mesh gradient:
|   |   +-- Dark glass workspace with frosted shells? --------------------> `dark-glass-clean-layout`
|   |   +-- Dark glass + thin blue laser atmosphere? ---------------------> `blue-laser-clean-glass-layout`
|   |   +-- Dark glass + circular clock or calibration dials? ------------> `glass-dark-mode-clock`
|   |   +-- Frosted glassmorphism cards with gradient borders (technique)? > `glass-dark-ui`
|   |   +-- High-contrast dark blue + cobalt gradient blocks? ------------> `dark-blue-contrasting-clean`
|   |   `-- Futuristic dark-blue mesh-gradient system? -------------------> `mesh-gradient-dark-blue-clean`
|   `-- Technical, framed, skeuomorphic:
|       +-- Thin boundary lines + L-shaped corner brackets? --------------> `framed-grid-layout`
|       +-- Framed dark tech + border-gradient shells? -------------------> `framed-tech-dark-border-gradient`
|       +-- Monochrome exploded 3D wireframe + callouts? -----------------> `technical-wireframe-info-layout`
|       +-- Matte-black + emerald signal accents? ------------------------> `tech-green-dark-mode-modern`
|       +-- Bright-green split layout + WebGL hero? ----------------------> `bright-green-tech-system-webgl`
|       +-- Fuchsia-purple rounded container tech? -----------------------> `funky-purple-container-tech`
|       `-- Tactile molded surfaces, inset depth, skeuomorphic? ----------> `high-contrast-skeuomorphic-clean`
|
`-- 5. UI chrome, borders, shadows, masks, status indicators (10 skills)?
    +-- Borders and frames: `css-border-gradient`, `liquid-metal-border`, `beam-glow-states`, `container-lines`, `nested-container-frames`, `corner-diagonals`
    +-- Elevation and masks: `beautiful-shadows`, `css-alpha-masking`
    `-- Content and status: `html-demo` (live HTML app window), `thinking-orbs` (AI status indicators)
```

---

## Common Situations & Recommended Skill Chains

| Situation | Recommended skill(s) | Execution order |
| :--- | :--- | :--- |
| Design a new SaaS landing page with strong aesthetic direction | `ui-ux-pro-max` then `landing-page` (or `product-proof-saas`) | Query design intelligence first, then apply landing page structure |
| Build a dark-mode AI developer tool interface with glowing active states | `framed-tech-dark-border-gradient` then `beam-glow-states` | Establish the framed dark layout, then add animated border beams |
| Create a brand identity, logo, and design token system | `design` then `design-system` | Generate the logo/CIP brief first, then compile 3-layer CSS/JSON tokens |
| Design an investor pitch deck in HTML | `design-system` then `slides` | Select the slide strategy and emotion arc, then build the Chart.js slides |
| Build a creative agency or studio portfolio site | `documentary-brutalist-agency` (or `agency-grid-layout-minimal`) | Direct archetype match |
| Add tactile depth, layered shadows, and edge fades to existing cards | `beautiful-shadows` then `css-alpha-masking` | Apply neutral elevation, then edge masking |
| Show a live product walkthrough without video files | `product-proof-saas` then `html-demo` | Frame the proof around a step-by-step HTML app window |

---

## Disambiguation Rules

- **`ui-ux-pro-max` vs `design` vs `design-system`**: `ui-ux-pro-max` searches the 79 styles, 192 palettes and 22 stack guidelines; `design` generates logos and corporate identity (CIP); `design-system` compiles 3-tier tokens (`primitive > semantic > component`) and slide deck data.
- **`glass-dark-ui` vs `dark-glass-clean-layout` vs `blue-laser-clean-glass-layout`**: `glass-dark-ui` is the CSS technique for readable frosted surfaces and masked gradient borders; `dark-glass-clean-layout` is a full multi-column workspace layout; `blue-laser-clean-glass-layout` adds a thin blue laser hero atmosphere.
- **`css-border-gradient` vs `beam-glow-states` vs `liquid-metal-border`**: `css-border-gradient` is a static, subtle gradient border; `beam-glow-states` uses `border-beam` for animated loading, focus and selected states; `liquid-metal-border` uses WebGL `metal-fx` for specular chrome borders.
- **`framed-grid-layout` vs `container-lines` vs `nested-container-frames`**: `framed-grid-layout` is a full design system with corner brackets; `container-lines` and `nested-container-frames` are single details to add to any layout.

## Demo folders

The aesthetic design-system skills each carry a `demo/` folder with a rendered preview image, a sample page and its prompt. Nine of the sample pages load runtime scripts that this plugin does not bundle, so open `demo/preview.jpg` for the intended look.

---

## Skill Directory (43 member skills)

### Design intelligence and tokens (8 skills)

| Skill | What it does |
| :--- | :--- |
| [`ui-ux-pro-max`](../ui-ux-pro-max/SKILL.md) | UI/UX design intelligence for web, mobile, and desktop. |
| [`design`](../design/SKILL.md) | Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini, Atlas Cloud, or MuAPI AI), corporate identity program (50... |
| [`design-system`](../design-system/SKILL.md) | Token architecture, component specifications, and slide generation. |
| [`brand`](../brand/SKILL.md) | Brand voice, visual identity, messaging frameworks, asset management, brand consistency. |
| [`banner-design`](../banner-design/SKILL.md) | Design banners for social media, ads, website heroes, creative assets, and print. |
| [`slides`](../slides/SKILL.md) | Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies. |
| [`design-first-ui-prompting`](../design-first-ui-prompting/SKILL.md) | Use when you need design-first, spec-driven, skimmable prompts for UI generation. |
| [`tailwindcss`](../tailwindcss/SKILL.md) | Use when designing/implementing UI with Tailwind CSS (layout, typography, responsive, theming, component patterns). |

### Aesthetic design systems (21 skills)

| Skill | What it does |
| :--- | :--- |
| [`agency-grid-layout-minimal`](../agency-grid-layout-minimal/SKILL.md) | Create a minimal agency design system with a disciplined editorial grid, oversized typography, quiet uppercase utility labels, restrained image blocks, and subtle... |
| [`blue-laser-clean-glass-layout`](../blue-laser-clean-glass-layout/SKILL.md) | Create a clean dark glass layout system with a thin blue laser atmosphere, frosted premium shells, and polished dashboard structure. |
| [`bright-green-tech-system-webgl`](../bright-green-tech-system-webgl/SKILL.md) | Create a bright-green technical design system with structured split layouts, hard-framed dark surfaces, mono utility labels, and a prominent WebGL visualization zone. |
| [`dark-blue-contrasting-clean`](../dark-blue-contrasting-clean/SKILL.md) | Create a dark-blue clean design system with strong contrast, cobalt gradient feature blocks, crisp framed structure, and restrained premium glow. |
| [`dark-glass-clean-layout`](../dark-glass-clean-layout/SKILL.md) | Create a dark glass layout system with frosted premium shells, clean multi-column workspace structure, floating data cards, and restrained atmospheric depth. |
| [`documentary-brutalist-agency`](../documentary-brutalist-agency/SKILL.md) | Create or redesign creative agency, production studio, architecture, culture, and portfolio websites with billboard typography, hard black-and-white chapters, exposed... |
| [`editorial-service-booking`](../editorial-service-booking/SKILL.md) | Create or redesign appointment-based service websites for salons, barbers, spas, wellness studios, clinics, and hospitality brands. |
| [`framed-grid-layout`](../framed-grid-layout/SKILL.md) | Create minimal framed grid layouts with thin visible boundary lines, L-shaped corner brackets, subtle diagonal line texture, and strict section alignment. |
| [`framed-tech-dark-border-gradient`](../framed-tech-dark-border-gradient/SKILL.md) | Create a framed dark technical design system with border-gradient shells, asymmetrical grid panels, mono utility labeling, and restrained monochrome atmosphere. |
| [`funky-purple-container-tech`](../funky-purple-container-tech/SKILL.md) | Create a dark container-led technical design system with fuchsia-purple accents, layered rounded shells, crisp frame lines, and playful futuristic focal objects. |
| [`glass-dark-mode-clock`](../glass-dark-mode-clock/SKILL.md) | Create a dark glass design system with frosted shells, soft beam grids, circular clock-like calibration dials, and precise sci-fi instrument framing. |
| [`glass-dark-ui`](../glass-dark-ui/SKILL.md) | Build dark-mode glassmorphism interfaces with readable contrast, frosted surfaces, and gradient borders using a pseudo-element mask. |
| [`high-contrast-skeuomorphic-clean`](../high-contrast-skeuomorphic-clean/SKILL.md) | Create a high-contrast clean skeuomorphic design system with molded dark surfaces, crisp light separation, tactile inset depth, and restrained signal accents. |
| [`light-mode-paper-technical`](../light-mode-paper-technical/SKILL.md) | Create a light-mode technical design system with warm paper surfaces, dark outer framing, subtle diagonal texture, precise bracketed geometry, and restrained accent... |
| [`mesh-gradient-dark-blue-clean`](../mesh-gradient-dark-blue-clean/SKILL.md) | Create a futuristic, premium, clean dark-blue mesh-gradient design system across background rendering, hero shell, navigation, floating nodes, framed sections, CTAs,... |
| [`nested-container-clean-agency`](../nested-container-clean-agency/SKILL.md) | Create a clean agency design system built from nested containers, with an outer editorial shell, inset dark feature blocks, rounded premium cards, and restrained... |
| [`operational-enterprise-ai`](../operational-enterprise-ai/SKILL.md) | Create or redesign enterprise AI, automation, security, and operations product pages that explain system boundaries, approvals, auditability, exceptions, and rollback. |
| [`orange-clean-paper-saas`](../orange-clean-paper-saas/SKILL.md) | Create a clean paper-toned SaaS design system with warm neutrals, orange accent signals, rounded premium forms, and polished product illustration surfaces. |
| [`product-proof-saas`](../product-proof-saas/SKILL.md) | Create or redesign SaaS and AI product landing pages where a real workflow, interface, or deterministic demo is the central proof. |
| [`tech-green-dark-mode-modern`](../tech-green-dark-mode-modern/SKILL.md) | Create a modern dark-mode technical design system with matte-black surfaces, emerald signal accents, mono system labeling, framed dashboard cards, and restrained glow. |
| [`technical-wireframe-info-layout`](../technical-wireframe-info-layout/SKILL.md) | Create a monochrome technical wireframe design system with exploded 3D structure, connector annotations, sparse information labels, and precise dark diagnostic framing. |

### Landing pages and conversion (4 skills)

| Skill | What it does |
| :--- | :--- |
| [`build-awwwards-quality-sites`](../build-awwwards-quality-sites/SKILL.md) | Art-direct and implement distinctive, motion-rich marketing, editorial, portfolio, and landing websites with original reference-inspired imagery, standout heroes,... |
| [`build-daily-inspiration-sites`](../build-daily-inspiration-sites/SKILL.md) | Turn a completed daily UI inspiration capture into exactly five original landing-page builds, one per separate Codex task, using Sites. |
| [`landing-page`](../landing-page/SKILL.md) | Use when designing or rewriting a high-converting landing page (single-offer page) for SaaS/apps/services. |
| [`pricing-page`](../pricing-page/SKILL.md) | Use when designing or rewriting a high-converting SaaS pricing page (structure, plan design, copywriting, SEO/AEO, FAQs, layout patterns, experiments). |

### UI chrome, surfaces and details (10 skills)

| Skill | What it does |
| :--- | :--- |
| [`beam-glow-states`](../beam-glow-states/SKILL.md) | Create React loading, processing, selected, current, focus, and pressed states with the border-beam package's animated edge glow. |
| [`beautiful-shadows`](../beautiful-shadows/SKILL.md) | Apply exact Tailwind arbitrary shadow utilities for polished, layered neutral elevation. |
| [`container-lines`](../container-lines/SKILL.md) | Add vertical container-size guide lines with mini corner squares for precise, structured web layouts. |
| [`corner-diagonals`](../corner-diagonals/SKILL.md) | Apply diagonal-cut corners and chamfered edges to buttons, cards, panels, and container shells. |
| [`css-alpha-masking`](../css-alpha-masking/SKILL.md) | Apply CSS alpha masking with linear-gradient for horizontal or vertical edge fades (mask-image and -webkit-mask-image). |
| [`css-border-gradient`](../css-border-gradient/SKILL.md) | Apply subtle gradient-border treatments for premium web surfaces. |
| [`html-demo`](../html-demo/SKILL.md) | Show an app working on a web page by drawing it live in HTML instead of recording it. |
| [`liquid-metal-border`](../liquid-metal-border/SKILL.md) | Add and tune animated liquid-metal WebGL borders with the React `metal-fx` package. |
| [`nested-container-frames`](../nested-container-frames/SKILL.md) | Create a container-in-container layout system using nested frames. |
| [`thinking-orbs`](../thinking-orbs/SKILL.md) | Add accessible animated AI loading and agent-status indicators with the React thinking-orbs library. |
