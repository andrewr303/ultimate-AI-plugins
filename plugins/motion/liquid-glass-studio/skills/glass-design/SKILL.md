---
name: glass-design
description: 'Decide where liquid glass style surfaces belong in a product, how many a screen can carry, and how they look: functional versus content layer, stacking, regular versus clear with a dimming layer, tint for prominence, capsule and concentric shapes, grouping, light and dark constants, brand adaptation, and a written decision record. Use when the user asks "where should glass go", "add liquid glass to our app", "glassmorphism redesign", "frosted glass navbar or cards?", "make it feel like Apple glass", "glass effect design system", or wants a glass spec before code. Do not use for tuning refraction math (glass-optics), writing the implementation (glass-web or glass-native), or a pre-merge audit of shipped glass (glass-review).'
---

# Design where glass belongs

Turn a request for "glass" into a short set of decisions an implementer can follow: which surfaces get glass, which variant, what tint, what shape, and what each surface falls back to. Glass is a cost each surface must justify. The usual right answer is a few floating controls in glass and everything else opaque.

## Start here

1. Inspect the real product: screens, navigation structure, the components that float (bars, toolbars, menus, sheets, media controls) and the content under them (feeds, photos, video, maps, documents).
2. Read the existing design tokens: surface colors, radii, elevation, blur, focus ring, motion. Note light, dark and high-contrast variants if they exist.
3. Inventory backdrops honestly. Content you control (illustration, brand gradient) is easy; user photos, video, ads and third-party embeds are the worst case and set the contrast budget.
4. Identify the platforms. Native Apple targets get system glass through [glass-native](../glass-native/SKILL.md); web targets need a tier plan from [glass-web](../glass-web/SKILL.md).
5. Apply the sections below, then write the decision record.

## Layer test

Ask of each candidate surface: does the user need to see that content continues underneath it, while the surface itself stays a separate control?

| Verdict | Surfaces | Material |
| --- | --- | --- |
| Glass | tab bar, toolbar, sidebar over scrolling content, floating action group, menu, popover, sheet chrome, player or camera controls | glass (regular by default) |
| Not glass | cards, list rows, article body, tables, forms, charts, page background, alerts with critical status | opaque, or a standard frosted material inside the content layer |
| Glass only while active | slider thumb or toggle knob during a drag | glass during interaction, solid at rest |

Apple's guidance puts its material in a functional layer that floats above content and says not to use it in the content layer (row A3 in [research-snapshot.md](../../references/research-snapshot.md)). The same split works on the web and on Android. If a surface would be equally clear as a solid, make it solid.

## Stacking and hierarchy

- At most one glass layer over any point of content at rest. A menu opened from a glass toolbar sits beside or below it once its transition ends.
- When nesting cannot be avoided (a selection lens inside a tab bar), the inner piece gets less refraction, no extra blur and a distinct role. See [design-principles.md section 3](../../references/design-principles.md#3-hierarchy-and-stacking-limits).
- Group related controls into one glass container: two to four controls per group, split by function (navigation, editing, sharing). More than that becomes a menu.
- Do not mix text and icon items inside one shared glass background.

## Variant: regular, clear and dimming

- **Regular** is the default for anything with text: menus, toolbars with labels, sidebars, popovers.
- **Clear** only over visually rich media (photo viewer, video, camera) where the media must stay visible.
- Clear glass over bright content needs a dark dimming layer; Apple suggests 35% opacity (row A6). Decide its color and opacity per appearance, then confirm it with a measured contrast pass in [glass-accessibility](../glass-accessibility/SKILL.md).
- Light and dark appearances need separate constants (tint, frost mix, rim strength), not a color inversion. Keep rims thin and directional in dark mode so edges do not read as sticker outlines.

## Tint

- Tint marks prominence or selection, not brand. One tinted element per group: the primary action or the selected tab.
- Tint the glass, not the text on it. Text color follows the appearance and must pass contrast on every tier.
- Hover and pressed highlights mix a little of the current color into the existing material; they are too faint to serve as focus indicators.
- A fully brand-colored glass bar stops reading as glass and competes with content. Express brand through shape, typography, icon style, motion personality and the one tinted action.

## Shape

- Capsules for controls and buttons; circles for icon-only buttons; larger radii for sheets and big panels.
- Concentric corners: inner radius = outer radius minus the inset, clamped at zero. Give every nested shape this rule in tokens so it holds at every size.
- The radius used for the refraction map must equal the CSS clip radius, or a seam appears at corners ([gotchas.md G24](../../references/gotchas.md#g24-refraction-ignores-the-corner-radius)).
- No sharp-cornered glass. Refraction concentrates at corners and tears there.
- Keep text and icons inside the flat interior, padded past the refracting bezel, so glyphs never bend.

## Fallback design is part of the design

Specify three looks per surface before anyone writes code:

| Tier | What the user sees | Who gets it |
| --- | --- | --- |
| Solid | opaque surface with a visible border, full-contrast text | forced colors, reduced transparency, more contrast, no `backdrop-filter`, failures |
| Frost | blur, saturation, tint, rim and a top-lit gradient | Safari, Firefox, any engine without SVG backdrop refraction |
| Refract | frost plus edge refraction and a rim light | Chromium (web), or system glass (native) |

Safari users see frost by default, so frost must look finished on its own, not like a degraded refract tier.

## Brand adaptation

- Name the material your own way ("glass", "lens", "frost"). Do not call a component "Liquid Glass".
- No Apple assets: SF Symbols, wallpapers, sounds. Choose your own constants rather than cloning Apple's look pixel for pixel.
- On Android, keep Material navigation placement and back behavior; glass is a surface treatment.

## Decision record

Write a short record (in the PR, the design doc, or `templates/glass-spec.md` when the plugin provides it) with:

1. Surfaces that get glass, each with its layer verdict and the backdrop it floats over.
2. Variant per surface (regular or clear), dimming layer if clear, and the tint rule.
3. Radii tokens, including the concentric rule and the bezel padding for content.
4. Solid, frost and refract looks per surface, light and dark.
5. Accessibility commitments: worst-case contrast targets, focus indicator style, reduced-transparency and forced-colors behavior, reduced-motion alternative.
6. Budget: maximum visible refractive surfaces per screen (start at 3 to 6, see [performance.md section 9](../../references/performance.md#9-budgets)).
7. Rejected options and why (for example "glass cards in the feed: content layer, contrast varies per card").

## Rules

- Glass only on the navigation and control layer. A glass card grid is a finding, not a style.
- Regular by default; clear needs rich media underneath and a dimming layer or a measured pass.
- No glass on glass at rest.
- A designed solid tier exists for every glass surface.
- Never trade away the focus outline for a cleaner look.
- Do not invent Apple guidance. Quote it from [research-snapshot.md](../../references/research-snapshot.md) with its check date, and re-check rows marked moving.

## Verify

`<plugin-root>` is two directories above this skill's base directory (Claude Code prints "Base directory for this skill" when the skill loads). Run plugin scripts from the user's project directory by path; output paths resolve against the current directory.

- Run the pre-flight checklist in [design-principles.md section 12](../../references/design-principles.md#12-pre-flight-checklist) against the decision record.
- Mock or screenshot each surface over its worst backdrop (brightest photo, busiest region, white page) in light and dark, and over the solid tier.
- When a prototype exists, measure text contrast on it, text element by text element rather than the whole container: `node <plugin-root>/scripts/glass_contrast.mjs --url <prototype url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto`.
- Use the lab to show stakeholders the three tiers side by side: `cd <plugin-root>/examples/glass-lab && python3 -m http.server 8000 --bind 127.0.0.1` (pick another free port if 8000 is taken, and stop only the server you started), then open `?tier=solid`, `?tier=frost` and the default.

## References

- [design-principles.md](../../references/design-principles.md): layers, variants, tint, shape, spacing, anti-patterns, checklist
- [accessibility.md](../../references/accessibility.md): contrast method and preference modes
- [native.md](../../references/native.md): system components and containers on each platform
- [motion.md](../../references/motion.md) and [performance.md](../../references/performance.md): budgets that limit the design
- [research-snapshot.md](../../references/research-snapshot.md): Apple guidance rows A3 to A10 with dates
