---
name: ios-design
description: "Design or polish native iOS layouts, semantic themes, typography, localization, resizable iPhone/iPad surfaces, or explicitly requested Liquid Glass. Use ios-accessibility for assistive semantics and ios-navigation for routing. Do not impose a new brand, fixed aesthetic, speculative device API, or Glass treatment on an ordinary feature request."
---

# Native interface design

Read the [operating contract](../ios-development/references/operating-contract.md) first. Establish the screen's purpose, primary action, important states, existing design tokens and supported environments before changing visual details.

## Workflow

1. Read the current view and nearby screens. Identify content hierarchy, interaction model, app theme and localization resources. Preserve recognizable product language and layout conventions.
2. Use [adaptive layout and theme](references/adaptive-layout-and-theme.md) to define how content behaves at narrow/wide widths, short heights, keyboard appearance, large text and safe-area changes. Prefer system layout and semantic controls where they fit.
3. Apply [content and localization](references/content-and-localization.md) to visible text, dates, numbers, symbols and resource selection. Preview expansion, right-to-left layout and missing data.
4. If the user requests Glass or the task fixes existing Glass, read [materials and Glass](references/materials-and-glass.md). Verify installed SDK declarations and runtime availability; provide a usable fallback. Keep material treatment aligned with the requested scope.
5. Implement a small reviewable change. Check primary, loading, empty, failed and disabled states as relevant. Route assistive behavior to [ios-accessibility](../ios-accessibility/SKILL.md).
6. Capture previews/screenshots only when supported, record the tested size/settings, and check interactions in a running app when layout changes affect reachability. Static source review is not visual validation.

## Required evidence and edge cases

- Name the intended improvement in hierarchy, legibility, reachability or consistency.
- Treat exact spacing, radii and font counts from examples as preferences; use project tokens and content needs.
- Do not infer screen space from a process-global display size or hardcoded device model.
- Content cannot disappear just because the layout becomes compact. Supply navigation or scrolling for overflow.
- A fallback should keep controls readable and usable, including reduced transparency or motion settings.

Return the resulting behavior, states/settings checked, changed files and material limits. Keep design choices distinguishable from correctness defects. See [source map](../../docs/source-map.md).
