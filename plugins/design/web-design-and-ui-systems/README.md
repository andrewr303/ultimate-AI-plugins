# Web Design & UI Systems

Version 2.16.0. 43 skills for designing and building web interfaces, plus a router skill that picks the right one. Start with `web-design-router` when you are not sure which skill fits.

Skills cover a searchable UI/UX database (79 styles, 192 palettes, 74 font pairings, 22 stack guideline sets), 21 aesthetic design systems with demo pages, landing and pricing pages, brand voice, design tokens and slides, and 10 CSS and React detail skills (borders, shadows, masks, status indicators).

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`web-design-router`](skills/web-design-router/SKILL.md). Try this prompt.

> Propose a palette, type pairing, and pricing-page layout for a bookkeeping product. Show how the choices map to reusable tokens and components.

## Install

Claude Code, from this repository's marketplace:

```sh
claude plugin marketplace add andrewr303/ultimate-AI-plugins
claude plugin install web-design-and-ui-systems@ultimate-ai-plugins
```

Codex and Cursor read `.codex-plugin/plugin.json` and `.cursor-plugin/plugin.json`; all manifests carry the same version.

## What runs on your machine

Nothing runs automatically: the plugin has no hooks, no MCP servers and no installers. Some skills ship scripts that run only when the skill's instructions call them:

- `ui-ux-pro-max`: Python 3 search over bundled CSV data. Standard library only, no network.
- `design`: logo and corporate-identity generation scripts. They send prompts to a third-party image provider (Gemini, Atlas Cloud or MuAPI) using your own API key, and the skill asks for your approval before the first call. The search scripts work offline.
- `design-system`: `fetch-background.py` downloads stock images from Pexels or Unsplash when asked.
- `brand`, `design-system`, `slides`: Node and Python scripts that read and write local project files.
- `build-daily-inspiration-sites`: needs Codex task tools and the Sites plugin. In other hosts it stops after validation.

Nine aesthetic skills include a demo page that loads runtime scripts (Tailwind CDN runtime, GSAP, iconify-icon) from a folder this plugin does not ship. Open `demo/preview.jpg` in those skills to see the intended look.

## Related plugins

- `plugins/design-variations`: ten interactive design variations per round, with iteration on your picks. This plugin gives one direction per skill and does not generate variant rounds.
- `plugins/marketing-page-studio`: builds product marketing sites with working demonstrations and browser evidence. `landing-page` and `pricing-page` here are guidance skills for page structure and copy.
- `plugins/liquid-glass-studio`: liquid glass interfaces (refraction, rim light, native glass APIs, a live lab). `glass-dark-ui` and the dark glass systems here are CSS glassmorphism styles.

## Routing skill

[`web-design-router`](skills/web-design-router/SKILL.md) holds the decision tree, common skill chains and disambiguation rules.

## Skills: Design intelligence and tokens (8 skills)

| Skill | What it does |
| :--- | :--- |
| [`ui-ux-pro-max`](skills/ui-ux-pro-max/SKILL.md) | UI/UX design intelligence for web, mobile, and desktop. |
| [`design`](skills/design/SKILL.md) | Design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini, Atlas Cloud, or MuAPI AI), corporate identity program (50... |
| [`design-system`](skills/design-system/SKILL.md) | Token architecture, component specifications, and slide generation. |
| [`brand`](skills/brand/SKILL.md) | Brand voice, visual identity, messaging frameworks, asset management, brand consistency. |
| [`banner-design`](skills/banner-design/SKILL.md) | Design banners for social media, ads, website heroes, creative assets, and print. |
| [`slides`](skills/slides/SKILL.md) | Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies. |
| [`design-first-ui-prompting`](skills/design-first-ui-prompting/SKILL.md) | Use when you need design-first, spec-driven, skimmable prompts for UI generation. |
| [`tailwindcss`](skills/tailwindcss/SKILL.md) | Use when designing/implementing UI with Tailwind CSS (layout, typography, responsive, theming, component patterns). |

## Skills: Aesthetic design systems (21 skills)

| Skill | What it does |
| :--- | :--- |
| [`agency-grid-layout-minimal`](skills/agency-grid-layout-minimal/SKILL.md) | Create a minimal agency design system with a disciplined editorial grid, oversized typography, quiet uppercase utility labels, restrained image blocks, and subtle... |
| [`blue-laser-clean-glass-layout`](skills/blue-laser-clean-glass-layout/SKILL.md) | Create a clean dark glass layout system with a thin blue laser atmosphere, frosted premium shells, and polished dashboard structure. |
| [`bright-green-tech-system-webgl`](skills/bright-green-tech-system-webgl/SKILL.md) | Create a bright-green technical design system with structured split layouts, hard-framed dark surfaces, mono utility labels, and a prominent WebGL visualization zone. |
| [`dark-blue-contrasting-clean`](skills/dark-blue-contrasting-clean/SKILL.md) | Create a dark-blue clean design system with strong contrast, cobalt gradient feature blocks, crisp framed structure, and restrained premium glow. |
| [`dark-glass-clean-layout`](skills/dark-glass-clean-layout/SKILL.md) | Create a dark glass layout system with frosted premium shells, clean multi-column workspace structure, floating data cards, and restrained atmospheric depth. |
| [`documentary-brutalist-agency`](skills/documentary-brutalist-agency/SKILL.md) | Create or redesign creative agency, production studio, architecture, culture, and portfolio websites with billboard typography, hard black-and-white chapters, exposed... |
| [`editorial-service-booking`](skills/editorial-service-booking/SKILL.md) | Create or redesign appointment-based service websites for salons, barbers, spas, wellness studios, clinics, and hospitality brands. |
| [`framed-grid-layout`](skills/framed-grid-layout/SKILL.md) | Create minimal framed grid layouts with thin visible boundary lines, L-shaped corner brackets, subtle diagonal line texture, and strict section alignment. |
| [`framed-tech-dark-border-gradient`](skills/framed-tech-dark-border-gradient/SKILL.md) | Create a framed dark technical design system with border-gradient shells, asymmetrical grid panels, mono utility labeling, and restrained monochrome atmosphere. |
| [`funky-purple-container-tech`](skills/funky-purple-container-tech/SKILL.md) | Create a dark container-led technical design system with fuchsia-purple accents, layered rounded shells, crisp frame lines, and playful futuristic focal objects. |
| [`glass-dark-mode-clock`](skills/glass-dark-mode-clock/SKILL.md) | Create a dark glass design system with frosted shells, soft beam grids, circular clock-like calibration dials, and precise sci-fi instrument framing. |
| [`glass-dark-ui`](skills/glass-dark-ui/SKILL.md) | Build dark-mode glassmorphism interfaces with readable contrast, frosted surfaces, and gradient borders using a pseudo-element mask. |
| [`high-contrast-skeuomorphic-clean`](skills/high-contrast-skeuomorphic-clean/SKILL.md) | Create a high-contrast clean skeuomorphic design system with molded dark surfaces, crisp light separation, tactile inset depth, and restrained signal accents. |
| [`light-mode-paper-technical`](skills/light-mode-paper-technical/SKILL.md) | Create a light-mode technical design system with warm paper surfaces, dark outer framing, subtle diagonal texture, precise bracketed geometry, and restrained accent... |
| [`mesh-gradient-dark-blue-clean`](skills/mesh-gradient-dark-blue-clean/SKILL.md) | Create a futuristic, premium, clean dark-blue mesh-gradient design system across background rendering, hero shell, navigation, floating nodes, framed sections, CTAs,... |
| [`nested-container-clean-agency`](skills/nested-container-clean-agency/SKILL.md) | Create a clean agency design system built from nested containers, with an outer editorial shell, inset dark feature blocks, rounded premium cards, and restrained... |
| [`operational-enterprise-ai`](skills/operational-enterprise-ai/SKILL.md) | Create or redesign enterprise AI, automation, security, and operations product pages that explain system boundaries, approvals, auditability, exceptions, and rollback. |
| [`orange-clean-paper-saas`](skills/orange-clean-paper-saas/SKILL.md) | Create a clean paper-toned SaaS design system with warm neutrals, orange accent signals, rounded premium forms, and polished product illustration surfaces. |
| [`product-proof-saas`](skills/product-proof-saas/SKILL.md) | Create or redesign SaaS and AI product landing pages where a real workflow, interface, or deterministic demo is the central proof. |
| [`tech-green-dark-mode-modern`](skills/tech-green-dark-mode-modern/SKILL.md) | Create a modern dark-mode technical design system with matte-black surfaces, emerald signal accents, mono system labeling, framed dashboard cards, and restrained glow. |
| [`technical-wireframe-info-layout`](skills/technical-wireframe-info-layout/SKILL.md) | Create a monochrome technical wireframe design system with exploded 3D structure, connector annotations, sparse information labels, and precise dark diagnostic framing. |

## Skills: Landing pages and conversion (4 skills)

| Skill | What it does |
| :--- | :--- |
| [`build-awwwards-quality-sites`](skills/build-awwwards-quality-sites/SKILL.md) | Art-direct and implement distinctive, motion-rich marketing, editorial, portfolio, and landing websites with original reference-inspired imagery, standout heroes,... |
| [`build-daily-inspiration-sites`](skills/build-daily-inspiration-sites/SKILL.md) | Turn a completed daily UI inspiration capture into exactly five original landing-page builds, one per separate Codex task, using Sites. |
| [`landing-page`](skills/landing-page/SKILL.md) | Use when designing or rewriting a high-converting landing page (single-offer page) for SaaS/apps/services. |
| [`pricing-page`](skills/pricing-page/SKILL.md) | Use when designing or rewriting a high-converting SaaS pricing page (structure, plan design, copywriting, SEO/AEO, FAQs, layout patterns, experiments). |

## Skills: UI chrome, surfaces and details (10 skills)

| Skill | What it does |
| :--- | :--- |
| [`beam-glow-states`](skills/beam-glow-states/SKILL.md) | Create React loading, processing, selected, current, focus, and pressed states with the border-beam package's animated edge glow. |
| [`beautiful-shadows`](skills/beautiful-shadows/SKILL.md) | Apply exact Tailwind arbitrary shadow utilities for polished, layered neutral elevation. |
| [`container-lines`](skills/container-lines/SKILL.md) | Add vertical container-size guide lines with mini corner squares for precise, structured web layouts. |
| [`corner-diagonals`](skills/corner-diagonals/SKILL.md) | Apply diagonal-cut corners and chamfered edges to buttons, cards, panels, and container shells. |
| [`css-alpha-masking`](skills/css-alpha-masking/SKILL.md) | Apply CSS alpha masking with linear-gradient for horizontal or vertical edge fades (mask-image and -webkit-mask-image). |
| [`css-border-gradient`](skills/css-border-gradient/SKILL.md) | Apply subtle gradient-border treatments for premium web surfaces. |
| [`html-demo`](skills/html-demo/SKILL.md) | Show an app working on a web page by drawing it live in HTML instead of recording it. |
| [`liquid-metal-border`](skills/liquid-metal-border/SKILL.md) | Add and tune animated liquid-metal WebGL borders with the React `metal-fx` package. |
| [`nested-container-frames`](skills/nested-container-frames/SKILL.md) | Create a container-in-container layout system using nested frames. |
| [`thinking-orbs`](skills/thinking-orbs/SKILL.md) | Add accessible animated AI loading and agent-status indicators with the React thinking-orbs library. |

## Provenance and license

MIT licensed (see `LICENSE`). Sources, bundled-data licenses, demo-content terms and the list of changes made to the uploaded files are in [`NOTICE.md`](NOTICE.md). Release history is in [`CHANGELOG.md`](CHANGELOG.md).
