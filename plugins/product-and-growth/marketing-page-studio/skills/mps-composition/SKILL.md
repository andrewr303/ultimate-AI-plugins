---
name: mps-composition
description: "Use when implementing a product homepage layout or presenting accurate screenshots through browser frames, detail crops, mobile compositions, layered surfaces or responsive page sections."
---

# Homepage and product composition

Read [composition](../../references/composition.md). Use the actual brand and product surface; the fixture's colors and copy are examples.

1. Choose a reading hierarchy: product promise, one meaningful UI unit, short supporting explanation, clear CTA. Build a complete page with semantic headings and real navigation.
2. Decide whether each product view should be frameless, in browser chrome, in a device shell, layered or cropped. The treatment must clarify its role, preserve proportions and keep essential labels readable.
3. Capture enough source pixels for the maximum crop. Replace a tiny full dashboard with a focused complete detail when appropriate. Never enlarge a blurry source and call the export sharp.
4. Compose 390px mobile independently: choose the useful product unit, reorder text and controls deliberately, shorten the visual path and preserve touch targets. Check 768, 1024 and 1440px too.
5. Apply typography, spacing and contrast tokens; reserve dimensions for assets. Keep section rhythm appropriate to the content instead of repeating the same reveal everywhere.
6. For React/Next.js, use existing components, design tokens and image facilities. For static pages, use the bundled example's minimal patterns. Do not duplicate engines.

Review native screenshots and the actual browser. A screenshot frame must not masquerade as a clickable product; if it includes controls, either make them work or present it as an image. Load `mps-interactive-surfaces` for operable demonstrations and `mps-browser-review` before delivery.
