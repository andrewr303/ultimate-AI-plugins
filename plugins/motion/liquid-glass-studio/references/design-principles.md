# Design principles for liquid glass style UI

Use this reference to decide where glass belongs, how much of it a screen can carry, and how to keep it legible. It combines Apple's published guidance (the most mature source on this material) with what the five studied libraries do in code. Rules marked **our rule** are this plugin's recommendations, reasoned from those sources rather than quoted from them.

"Liquid Glass" is Apple's name for its system material. This plugin describes a "liquid glass style" and is not affiliated with Apple.

## Source keys

Apple guidance cites https://developer.apple.com/design/human-interface-guidelines/materials (HIG Materials, page added 2025-06-09, updated 2025-09-09) and https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass (Adopting), both checked 2026-11-05. Library claims cite `<library> <path>`: glasshq (paths under `packages/liquid-glass/`), simple-liquid-glass, liquidGL, ybouane, liquid-glass-react. **Inference** marks reasoning not confirmed by a source.

## 1. When glass helps and when it hurts

Glass earns its cost when a control must float over changing content and stay connected to it: the user sees that the content continues underneath, and the control reads as a separate layer without a hard opaque block.

| Glass helps | Glass hurts |
| --- | --- |
| Floating navigation: tab bars, toolbars, sidebars over scrolling content | Body text, long forms, tables, dense data |
| Transient controls over media: player controls, camera controls, map controls | Content cards, list rows, page backgrounds (Apple: content layer) |
| Menus and popovers that need to feel attached to their source | Every surface on a screen at once |
| A small number of prominent actions | Status that must be read at a glance in any lighting (alerts, errors, prices) |
| Hero moments with a rich, controlled backdrop | Backdrops you do not control (user photos, ads, third-party embeds) without a scrim |

Apple: "Use Liquid Glass effects sparingly" and, for custom controls, "Limit these effects to the most important functional elements in your app" (HIG Materials). The Nielsen Norman Group critique of iOS 26 found low text contrast, controls blending into content, and "Motion for motion's sake" (https://www.nngroup.com/articles/liquid-glass/, Raluca Budiu, Oct 10, 2025, checked 2026-11-05). Treat glass as a cost each surface must justify.

**Our rule:** if a surface would be equally clear as a solid or standard material, use the solid. Glass is for the few places where seeing through matters.

## 2. Two layers: controls float, content does not

Apple divides materials into two kinds. Liquid Glass "forms a distinct functional layer for controls and navigation elements, like tab bars and sidebars, that floats above the content layer", and standard materials provide differentiation within the content layer. The HIG states it directly: **"Don't use Liquid Glass in the content layer."** The one exception: transient interactive elements such as sliders and toggles take on the glass look while being activated (HIG Materials).

glasshq encodes the same split structurally: a `GlassScene` holds one `GlassContent` layer (the live backdrop) and glass surfaces above it; only the content layer is refracted (glasshq `README.md`, `src/react/scene.tsx`). Its slider and switch thumbs are solid at rest and mount a clear glass lens only while pressed (glasshq `src/react/control-thumb.tsx`), which mirrors Apple's exception.

Practical mapping:

| Layer | Examples | Material |
| --- | --- | --- |
| Functional (floats) | tab bar, toolbar, sidebar, floating action group, menu, popover, sheet chrome, media controls | glass |
| Content | cards, rows, article body, images, charts, page background | opaque surfaces or standard (frosted) materials |
| Transient | a slider thumb or toggle while dragged | glass only during the interaction |

## 3. Hierarchy and stacking limits

Apple: "Avoid overlaying or layering Liquid Glass elements on top of each other"; prefer standard spacing (Adopting). Glass on glass doubles the blur, muddies contrast and makes the depth order ambiguous.

How the libraries handle the cases they do allow:

- **glasshq** refracts nested glass less: a surface inside another gets `clamp(0.6 * inset, 0, 8)` px of refraction by default, because it "already sees its parent's refracted rim" (glasshq `src/dom/index.ts`, `README.md`). Dark nested clear glass adds a small light lift so stacked layers stay distinct (glasshq `src/dom/material-graph.ts`). Glass beneath that touches a lens is merged into its backdrop; glass that is merely near contributes only its rim overlay (glasshq `src/dom/index.ts`).
- **liquidGL** demos make the inner stacked lens "subtler so text stays crisp": very low refraction and no frost (liquidGL `demos/stacked-lenses.html`).
- **ybouane** refracts lower glass and its label into upper glass by compositing them into the scene (ybouane `README.md`, `src/LiquidGlass.ts`).
- **simple-liquid-glass** does not support glass through glass in its main WebGL path; an opt-in engine layer provides it (simple-liquid-glass `README.md`).

**Our rule:** at most one glass layer over any point of content. When a menu opens from a glass toolbar, it may overlap the toolbar briefly during the morph, then sits beside or above it, not as a third layer. If nesting is unavoidable (a selection lens inside a tab bar), the inner piece gets less refraction, no extra blur, and a clearly different role (selection, not container).

## 4. Regular, clear, and the dimming layer

| Variant | Apple's description (HIG Materials) | Use for |
| --- | --- | --- |
| Regular | "blurs and adjusts the luminosity of background content to maintain legibility"; most system components use it | text-heavy components: alerts, sidebars, popovers, menus, toolbars with labels |
| Clear | "highly translucent" | components floating over media (photos, video) where the media should stay visible |

- "Only use clear Liquid Glass for components that appear over visually rich backgrounds" (HIG Materials).
- **Dimming layer:** "If the underlying content is bright, consider adding a dark dimming layer of 35% opacity." It is not needed when the content is already dark or when video playback controls provide their own dimming (HIG Materials). SwiftUI's own example: `.glassEffect(.clear).background(.black.opacity(0.3))` (https://developer.apple.com/documentation/swiftui/glass, checked 2026-11-05).
- glasshq defaults its scene to `material="clear"` but menus to `"regular"` (glasshq `src/react/scene.tsx`, `src/react/menu.tsx`). Its clear material in light appearance adds only a 6% pale veil, so legibility over busy content is left to the author (glasshq `src/dom/material-graph.ts`). **Our rule:** default to regular; choose clear per surface, with a dimming layer and a worst-case contrast check ([accessibility.md](accessibility.md#2-worst-case-backdrop-contrast)).
- liquid-glass-react's `overLight` flag bundles a darker tint, more blur, less displacement and a stronger shadow for bright backdrops (liquid-glass-react `src/index.tsx`). It is set by hand; the example toggles it from a scroll range (liquid-glass-react `liquid-glass-example/src/pages/index.tsx`). Drive the equivalent from measured backdrop luminance instead.

## 5. Variant, appearance and dark mode

- Light and dark appearances need different constants, not a color swap. glasshq picks separate tone curves, frost mix (0.34 light, 0.65 dark) and light intensity per appearance, and dims the specular rim to 0.82 and the diffuse glow to 0.40 in dark (glasshq `src/core/materials.ts`, `src/dom/material-graph.ts`, `src/gpu/maps.wgsl`).
- Over dark content, a bright rim on every edge reads as a sticker outline. Keep rims thin and directional (top and bottom light, darker sides), as glasshq's overlay plane does (glasshq `src/gpu/maps.wgsl`).
- Apple asks for custom control colors with light and dark variants **and an increased contrast option for each** (Adopting).
- Text color must follow the appearance: glasshq uses `--lg-foreground` (#111113 light, #fff dark) (glasshq `src/styles.css`). Simple-liquid-glass states that material choice "does not choose text colors" (simple-liquid-glass `README.md`); neither library adapts text to the backdrop automatically.

## 6. Tint signals prominence, not brand

**Our rule:** tint glass only to mark the most important action or a selected state, the way `.glassProminent` relates to `.borderedProminent` in SwiftUI (https://developer.apple.com/documentation/swiftui/primitivebuttonstyle/glass, checked 2026-11-05). A whole bar tinted in a brand color stops reading as glass and competes with content.

- Tint colors the glass, not the text or icons on it (glasshq `README.md`). glasshq's tint lets luminance through ("Colored glass transmits luminance") so the backdrop still shows in the tinted body (glasshq `src/dom/material-graph.ts`).
- liquidGL treats tint alpha as dye strength and keeps highlights white (liquidGL `README.md`).
- For hover and pressed highlights, tint the existing material rather than covering it: glasshq uses `color-mix(in oklab, currentColor 8%, transparent)` (glasshq `src/styles.css`). That works as a highlight; it is too weak as a focus indicator ([accessibility.md](accessibility.md#8-focus-visibility)).
- One tinted element per region. Two tinted buttons side by side make neither prominent.

## 7. Shape language

- **Capsules for controls.** SwiftUI's default glass shape is a capsule (https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:), checked 2026-11-05). glasshq buttons, toolbars and tab lists default to `radius="capsule"`; icon buttons become circles (glasshq `src/react/button.tsx`, `src/react/toolbar.tsx`).
- **Concentric corners.** A shape inside another follows the parent's curve: inner radius = outer radius minus the inset (geometry). Apple provides `ConcentricRectangle` and `rect(corners:isUniform:)` in SwiftUI and `UICornerConfiguration` in UIKit (Adopting). glasshq computes child outlines as the parent's parallel curve and places corner controls with equal clearance (glasshq `src/core/concentric.ts`).
- **Continuous corners.** glasshq draws squircle corners (`smoothing: 0.8125`) and uses the same outline for the clip and the optics, so the material and the content edge agree (glasshq `src/core/shape.ts`). A CSS `border-radius` that differs from the radius the refraction map was built for shows as a seam ([gotchas.md](gotchas.md#g24-refraction-ignores-the-corner-radius)).
- **Sheets and large panels** get larger radii. Apple increased sheet corner radii in 26 and makes a sheet more opaque as it expands to full height (Adopting).
- Avoid sharp-cornered glass. Refraction concentrates at corners and tears there under strong displacement (simple-liquid-glass `CHANGELOG.md`).

## 8. Spacing and merging

- Groups of glass controls should be rendered together so nearby shapes can merge: SwiftUI `GlassEffectContainer(spacing:)`, UIKit `UIGlassContainerEffect.spacing`, AppKit `NSGlassEffectContainerView.spacing`. When container spacing exceeds the layout spacing, shapes blend at rest; otherwise they blend only while animating close together (https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views, checked 2026-11-05).
- Split a bar into groups with fixed spacers: SwiftUI `ToolbarSpacer(.fixed)`, UIKit `fixedSpace(_:)`, AppKit `space` (Adopting). glasshq mirrors this with toolbar spacers: fixed 8 px or flexible, each splitting a cluster into separate glass (glasshq `README.md`, `src/styles.css`).
- Do not mix text and icons in items that share one glass background (Adopting).
- **Our rule:** group by function (navigation, editing, sharing). Two to four controls per glass group; beyond that, a menu.

## 9. Legibility rules

1. Default to regular glass for anything with text.
2. Measure contrast against the worst backdrop the surface can sit on, not a screenshot of the happy case ([accessibility.md](accessibility.md#2-worst-case-backdrop-contrast)).
3. Use weight and size: medium or semibold labels survive busy backdrops better than regular weights. Apple warns against `quaternaryLabel` on thin materials because "contrast is too low" (HIG Materials).
4. Add a scrim or dimming layer under clear glass on bright content; a wide outline or halo around text counts as part of its background under WCAG (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, checked 2026-11-05).
5. Keep text off the refractive rim. glasshq bends only a 20 px band at the edge (glasshq `src/gpu/maps.wgsl`); pad content so glyphs never sit inside it.
6. Use scroll edge effects or progressive blur where content slides under floating bars, so text does not collide (SwiftUI `scrollEdgeEffectStyle`; glasshq `GlassScrollEdges`).
7. Provide a solid path for Reduce Transparency, Increase Contrast and forced colors ([accessibility.md](accessibility.md)).

## 10. Brand adaptation without copying Apple

- Name the material your own way ("glass", "lens", "frost"). Do not call your component "Liquid Glass" or imply Apple endorsement.
- Do not ship Apple assets (SF Symbols, system wallpapers, sounds) in web or Android products. Their license terms were not reviewed for this plugin; check them before any use.
- Choose your own constants. The numbers in this plugin (blur sigma, rim width, spring timing) are starting points from open-source libraries, not Apple measurements. glasshq's measured switch spring is described as a measurement of native behavior (glasshq `src/dom/control-motion.ts`), which is still not a license to clone the look pixel for pixel.
- Express brand through shape, motion personality, icon style, typography and one prominent tint, not through a fully colored glass chrome.
- On Android, respect Material conventions for navigation placement and back behavior; glass is a surface treatment, not a reason to move the navigation bar.

## 11. Anti-patterns

| Anti-pattern | Why it fails | Instead |
| --- | --- | --- |
| Glass cards in a content grid | Content layer glass; contrast varies card by card; cost scales with count | opaque cards; glass only on the floating filter bar |
| Glass on glass (menu over toolbar over hero) | double blur, ambiguous depth | one glass layer; menu beside the bar |
| Clear glass with white text over a bright photo | contrast collapses on bright regions | regular glass, or clear with a 35% dark dimming layer |
| Brand-tinted full navigation bar | stops reading as glass; tint loses meaning | neutral glass, tint the one primary action |
| Custom background behind system bars | fights the system material and scroll edge effect (Adopting) | remove it; use scroll edge styles |
| Removing the focus outline to keep the glass "clean" | fails focus visibility; glasshq does this, do not copy it | two-tone outline ([accessibility.md](accessibility.md#8-focus-visibility)) |
| Clickable `div` with glass | no keyboard or screen reader support (liquid-glass-react, ybouane) | real `<button>` or system button style |
| Large always-animating specular sweep | continuous rendering cost (liquidGL `specular: true`); distraction | static rim; light reacts only to interaction |
| Elastic stretch on large panels | heavy surfaces should barely move; glasshq limits large surfaces to edge give | stretch only small controls |
| Text inside the refractive rim | glyphs bend and smear | pad content past the bezel |
| Glass with no fallback | Safari and Firefox lack SVG backdrop refraction; WebGL can fail | design the frosted and solid tiers first |

## 12. Pre-flight checklist

Run this before building or approving a glass design.

- [ ] Each glass surface is in the functional layer (navigation, controls, transient UI). None sits in the content layer.
- [ ] No point on screen has more than one glass layer at rest.
- [ ] Regular is the default; every clear surface sits over rich media and has a dimming layer or a measured pass.
- [ ] Tint marks prominence only, at most one tinted element per group.
- [ ] Shapes are capsules or continuous-corner rectangles; nested shapes are concentric; CSS radius matches the refraction map radius.
- [ ] Related controls are grouped in one container with defined merge spacing.
- [ ] Text has measured worst-case contrast of 4.5:1 (3:1 large); control boundaries and focus indicators 3:1.
- [ ] Text sits outside the refractive rim.
- [ ] Light, dark, Increase Contrast, Reduce Transparency, forced colors and reduced motion variants are specified, with screenshots.
- [ ] A frosted tier and a solid tier exist for engines without refraction.
- [ ] Interactive glass uses real buttons or system controls, with a visible focus indicator.
- [ ] Motion is interruptible and has a reduced-motion version ([motion.md](motion.md)).
- [ ] The surface count fits the performance budget ([performance.md](performance.md#9-budgets)).
- [ ] Nothing is named or styled as Apple's product; no Apple assets.

## Related references

- [accessibility.md](accessibility.md), [motion.md](motion.md), [performance.md](performance.md)
- [native.md](native.md) for Apple, Android and Flutter APIs
- [optics.md](optics.md) for the parameters behind blur, rim and tint
