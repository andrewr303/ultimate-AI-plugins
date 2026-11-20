# Adaptive layout and semantic theme

## Start with content

List the content by importance: title/context, primary data, action, secondary details and optional decoration. Decide what must remain reachable at every supported size. Additional width can expose more of an existing hierarchy; a compact layout still needs access to the same task.

Use proposed container space and local environment values. Do not size from a global screen rectangle: an app may occupy a resizable window, sheet, split view or external display. Size classes are useful signals but do not replace content measurement. Device idiom and orientation alone cannot describe available space.

Use natural stacks, grids and system containers before manual coordinates. A layout that cannot fit vertically needs scrolling, a different composition or a documented fixed-canvas strategy. Avoid shrinking all text to fit or hiding actions at accessibility text sizes. Introduce custom layout only when constraints require it and the supported SDK supplies it.

## Safe areas and keyboard

Determine which ancestor already respects safe areas. Do not add measured safe-area insets again reflexively. When pinning real controls to an edge, choose a supported inset/bar/container mechanism that reserves content space. A pure overlay may cover content unless padding/insets are handled.

Test keyboard presentation on forms and editors. The focused field, validation message and primary action need a reachable path; not every element must remain simultaneously visible. Preserve system keyboard avoidance unless the design deliberately replaces it. Custom headers need an explicit relationship with navigation chrome and safe-area handling.

For a no-scroll editor, centralize region allocation: header, canvas, settings, toolbar. Share geometry between preview and exported output; separate pan/zoom math drifts at different scales. Coordinate tap, drag and pinch state rather than scattering independent flags. Test selection changes during a gesture.

## Theme and typography

Prefer existing tokens and semantic foreground/background roles. Semantic colors adapt to appearance and accessibility settings, but custom combinations still need contrast review. A brand color can remain when it works in both appearances; do not force every surface to black or white with arbitrary opacities.

Use semantic text styles for normal text. Scale custom fonts/metrics appropriately for the target. Weight, spacing and grouping can establish hierarchy without a proliferation of sizes. Fixed font sizes or line limits must have a content-driven reason and a tested large-text behavior.

Consistent spacing and shape language help scanning. A base grid can be useful; exceptions are valid when optical alignment or system components require them. A ten-point card radius, monospaced body font or particular stroke width is not a universal platform requirement.

Use system grouped forms/lists when they match the task. A custom card can serve the brand or interaction; judge clarity, hit targets, layout cost and accessibility rather than banning decoration. Avoid duplicating navigation titles, explanations and labels across every region.

## Coverage matrix

| Setting | Observe |
| --- | --- |
| Narrow width and short height | No clipped action or inaccessible overflow |
| Wide/resizable iPad window | Meaningful column behavior without stretched text |
| Largest supported text categories | Reflow, reading order and scroll reachability |
| Light/dark and contrast settings | Legible hierarchy and distinct control states |
| Keyboard visible | Focused field and completion action reachable |
| Long content, missing image, error | Stable layout with clear next action |

Record exact settings for visual evidence. Previews cover composition efficiently, but runtime testing remains necessary for keyboard, gestures and presentation.

## Provenance

Original synthesis informed by `swiftui-design-principles-main.zip`, `SKILL.md` sections on semantic colors, editor geometry and consistent hierarchy; Paul Hudson `SwiftUI-Agent-Skill-main.zip`, `swiftui-pro/references/design.md` and `resizability.md`; and AvdLee variant `skills/swiftui-expert-skill/references/layout-best-practices.md`. Rigid visual limits and unverified future device/API details were excluded. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
