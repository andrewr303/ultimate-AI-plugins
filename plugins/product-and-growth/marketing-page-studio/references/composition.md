# Readable product composition

## Start from one meaningful unit

Identify the smallest complete UI unit that demonstrates the promise: an inbox and selected case, a result with its source, a before/after pair, a complete chart with units, or a form and its output. Keep labels and consequences together. A cropped button without context is not proof.

Use type hierarchy to guide the eye from promise to interface to explanation to CTA. Choose line lengths and spacing from the actual text. Reserve image/video dimensions before load and avoid display changes that move the CTA after interaction.

## Screenshot treatments

| Treatment | Best use | Implementation and review |
| --- | --- | --- |
| Frameless surface | Native product card or familiar screen | Preserve borders/background needed to distinguish the surface from the page |
| Browser frame | Establish a real web context | Keep chrome light and noninteractive; do not expose private URLs |
| Device composition | Show actual mobile behavior | Use a genuine mobile layout; do not squeeze a desktop screen into a phone |
| Layered screenshots | Explain connected source and result | Show the relationship and maintain readable overlap; avoid occluding essential text |
| Detail crop | Full screen would be unreadable | Keep a complete semantic unit and give enough context to understand its place |
| Before/after | The transformation is the proof | Use comparable states, equal scale and clearly named differences |
| Perspective | A spatial accent helps the composition | Keep type readable; settle to a useful view before important information appears |

Use CSS `aspect-ratio`, `object-fit: contain` and intrinsic image dimensions to preserve screenshot proportions. `cover` is acceptable for an intentional crop with an inspected focal region; it is not a fix for mismatched geometry. Provide meaningful alt text and visible captions for mode/provenance where needed.

## Source density

Measure the largest intended display size and crop. Retain native pixel detail through encoding. A CSS transform can resample glyphs even when source dimensions are sufficient, so inspect the final browser output at 100%. Do not rely on file dimensions alone to claim sharpness.

For a full dashboard that becomes too small on mobile, change what is shown. A complete selected case can be more informative than every column. Keep the route to deeper detail clear; do not hide information needed to understand the promise.

## Responsive composition

At approximately 390px, plan a single reading axis, a compact complete product unit, useful control sizes and concise text wraps. At 768px, check the transition between stacked and split layouts. At 1024px, inspect nav collisions and awkward gaps. At 1440px, bound content width and prevent the interface from becoming a distant decoration.

Use content-driven breakpoints. A desktop hero can place text beside an operable preview; mobile may place the promise, one action, the result and supporting copy in order. Avoid horizontal page scroll. Product subregions may scroll only when clearly useful, keyboard reachable and visibly bounded.

## React and Next.js

Use existing design tokens and components; isolate the marketing demo so its sample state cannot mutate real application data. Use framework image/font facilities when already available. Preserve server-rendered semantic copy and navigation. Mark only interactive islands as client components. Keep the state machine and scroll controller small enough to inspect and test.

## Static pages

Use semantic authored HTML, CSS custom properties and a small progressive-enhancement script. Primary narrative and CTA should be useful before JavaScript runs. Prefer local assets and avoid adding a full framework for a bounded sample.

## Visual critique

Inspect native screenshots in meaningful states. Check hierarchy, accidental overlap, tiny labels, clipped focus rings, insufficient contrast, repetitive layout, inconsistent icon/text alignment and overly uniform section rhythm. Fix the most consequential defect before polishing micro-motion. Passing geometry checks does not decide whether the composition helps visitors understand the product.

## Local screenshot preparation

Use the bundled [asset helper](assets.md) for explicit crops, proportionate downscaling, metadata stripping and hash receipts. Its density command checks planned CSS width, DPR and maximum zoom without upscaling. Inspect actual bitmap detail and the composed page separately.
