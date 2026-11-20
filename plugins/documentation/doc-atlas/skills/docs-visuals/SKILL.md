---
name: docs-visuals
description: "Use when improving the visual design of README files or documentation sites, creating truthful diagrams/assets, and checking typography, hierarchy, responsive behavior, accessibility, light/dark themes, and renderer compatibility."
---

# Documentation visual design

Make technical documentation attractive through clear hierarchy, readable examples,
useful visuals, and a consistent product identity. Preserve factual accuracy and
the existing design system. Visual polish must help a reader understand or complete a task.

## 1. Inspect the actual canvas

Determine whether the output is GitHub README, plain Markdown, framework Markdown,
MDX, or a generated API site. Inspect how it actually renders before choosing components.
Read existing brand assets, theme tokens, typography, screenshots and representative pages.
Use supplied branding; write original layouts rather than copying another product's identity.

| Canvas | Reliable baseline | Constraints to check |
| --- | --- | --- |
| GitHub README | GFM headings, lists, tables, fenced code, links, supported Mermaid | Sanitized HTML, no custom CSS/JavaScript, theme-dependent surfaces, repository-relative assets |
| Portable Markdown | Semantic text, simple tables, images, ordinary code fences | No assumed callouts, tabs, Mermaid renderer, HTML or generated anchor algorithm |
| Framework site | Native theme components and semantic tokens | Installed component API, MDX imports, SSR/static rendering, base paths and theme behavior |

Use [visual recipes](references/visual-recipes.md) for composition choices.
Keep the README useful when images fail and the website useful without decorative motion.
Do not export a screenshot as a substitute for readable documentation text.

## 2. Define a restrained direction

Describe the visual direction in one sentence tied to the product and audience.
Choose a clear title treatment, neutral surfaces, a focused accent, readable body and
code type, and a consistent spacing rhythm. Reuse existing tokens before adding new ones.
On sites, define semantic tokens for text, muted text, surfaces, border, accent,
focus and code background. Verify foreground/background pairs in every theme and state.
Do not use color alone to distinguish warnings, versions, diagram categories or active items.

Use a comfortable reading width, strong heading contrast, and meaningful white space.
Maintain predictable spacing between sections, examples, captions and callouts.
Keep sidebars quieter than the page content. Limit cards to genuine navigation choices.
Use callouts for important decisions or consequences; avoid decorating every paragraph.
Keep long tables and code blocks usable on narrow screens without clipping the page.

## 3. Build hierarchy around content

The opening should identify the project and give readers a useful action quickly.
Use one clear primary title and an ordered heading structure.
Give each section a job; split large sections where the reader's task changes.
Use tables for compact comparisons or reference fields and lists for parallel steps/items.
Place prose near the visual or example it explains. Caption visuals with what the reader
should notice. Avoid vague headings such as “Magic” when a precise task name works.

Treat code as a primary visual element: label its language, keep the minimal working
example readable, provide filename/context where useful, and show expected outcomes.
Keep shell prompts separate from copyable commands. Mark placeholders explicitly.
Never make required values legible only in an image, hover state, or animation.

## 4. Create truthful diagrams and assets

Use a diagram when relationships, sequence, boundaries or data flow are clearer visually.
Derive nodes and arrows from repository evidence. Use conceptual labels when details are
unknown; do not invent an architecture to fill a layout.
Prefer supported Mermaid for small engineering diagrams. Keep labels short and provide
an adjacent textual summary containing the essential relationships and caveats.
Validate syntax with available tools and inspect the target renderer before declaring it done.
For renderers without Mermaid, provide a maintained exported image plus text fallback
or a simpler text/table explanation; do not leave an opaque fenced source block as the result.

For original SVG diagrams, use a viewBox, legible text, and explicit accessible naming
when inline (`role="img"`, linked title/description). When referenced as an image,
write meaningful Markdown/HTML alt text. Avoid scripts, remote resources and embedded
foreign HTML. Recheck contrast and scaling in both themes.
Use theme-specific image variants only when the target renderer supports them.

Use actual product screenshots captured from the relevant running version when available.
Show a useful task/result with enough context, crop deliberately and remove sensitive data.
Keep the editable text instructions nearby and record source/version when it matters.
Generated concepts and wireframes must be labeled illustrative; never present them as
captures of a working product. Do not fabricate dashboards, terminal output, metrics or badges.
Do not fetch private assets or send repository contents to an image service without authorization.

## 5. Check interaction and accessibility

Use native links/buttons with descriptive names and visible keyboard focus.
Verify keyboard access to navigation, theme controls, copy buttons, search and accordions.
Keep content available when an animation is disabled. Respect reduced-motion preferences
and avoid autoplay video, animated text, parallax or looping decoration by default.
If motion conveys status, provide a static text/state equivalent.

Check light and dark appearances where supported. Do not assume transparent logos,
diagram strokes, muted text or code highlights work on both backgrounds.
Check narrow phone, medium and desktop widths; inspect heading wraps, table/code overflow,
image scaling, sticky navigation overlap and the visibility of the primary action.
Use existing accessibility tooling where available, supplemented by browser inspection.

## 6. Verify the real renderer

Review the actual rendered README or built docs pages. Source formatting alone cannot
establish layout quality. Inspect at least the opening, a dense reference section,
a code block, a diagram/image, and the narrow layout.
Check asset links at the correct base path and ensure relative images still work from
their final document location. Verify alt text, captions, links and code after layout edits.
For GitHub content, avoid unsupported CSS and test HTML/Markdown combinations carefully.

## Handoff

Deliver complete scoped source/assets, describe the visual direction briefly, and name
the actual renderer, routes, themes and viewports inspected.
Report unrendered or untested behavior explicitly. A design preview or static image is
evidence of appearance only; it does not prove documentation accuracy or working interactions.
