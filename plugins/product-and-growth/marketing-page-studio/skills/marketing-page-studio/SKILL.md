---
name: marketing-page-studio
description: "Use when building or redesigning a product homepage, feature page or marketing website around accurate interfaces, meaningful interactive demonstrations and conversion. Also use for a complete product-led scroll storytelling site; do not activate for unrelated application bugs or standalone video exports."
---

# Marketing Page Studio

Create a runnable marketing site that explains a real product through its interface and gives visitors a clear next action. Complete implementation and browser repair; a page outline is not the deliverable.

## Start

Resolve this installed plugin's root from this skill. Read [execution](../../references/execution.md) for command/path conventions, then run `python scripts/studio.py doctor`. Read the user's repository, running app and supplied materials before asking for information. Apply [foundation](../../references/foundation.md) when the product is new or evidence changes.

Respect the existing stack. For a new small site, static HTML/CSS/JavaScript is a supported baseline. For React/Next.js, keep the same state models, composition rules and browser tests in the existing component system; do not introduce a second marketing engine.

## Route only the needed work

| Need | Skill | Supporting resource |
| --- | --- | --- |
| Audience, promise, proof, objections and page narrative | `mps-direction` | [direction](../../references/direction.md) |
| Repository/app discovery, capture and claim traceability | `mps-product-evidence` | [foundation](../../references/foundation.md) |
| Homepage layout and readable screenshot composition | `mps-composition` | [composition](../../references/composition.md) |
| Working sample surfaces, states and interface choreography | `mps-interactive-surfaces` | [interaction recipes](../../references/interactions.md) |
| Reversible scroll-controlled product story | `mps-scroll-story` | [scroll](../../references/scroll-story.md) |
| Benefit copy, feature pages, use cases and navigation | `mps-conversion-story` | [copy and pages](../../references/copy-and-pages.md) |
| Browser critique, responsive/accessibility/performance repair | `mps-browser-review` | [website QA](../../references/website-qa.md) |
| Runnable source, assets, reports and video handoff | `mps-delivery` | [delivery](../../references/delivery.md) |

Read one specialist and its relevant resources at a time. Search [the reference index](../../references/README.md) for deeper recipes; do not load the whole library.

## Complete the workflow

1. Write the concise product brief, evidence ledger and brand tokens. Separate actual captures, faithful replays and illustrative concepts.
2. Choose one defensible promise, one primary CTA and a narrative supported by the available product behavior. State assumptions; proceed autonomously unless essential information is missing.
3. Build the full page and useful supporting pages. Choose a distinct composition for this product, with readable interfaces and deliberately composed mobile states.
4. Implement a bounded demonstration whose interaction teaches something. Model its loading, result, empty, error, retry and reset states as relevant. Label synthetic data and deterministic AI samples.
5. Test the actual browser at representative widths, keyboard and reduced motion. Inspect meaningful screenshots, repair the most consequential defects and rerun affected checks.
6. Deliver source, preview instructions, optimized assets, validation results and a self-contained handoff. Deploy only when requested.

The bundled `examples/tandem` is a complete synthetic fixture, not a client brand or template identity. Use its working patterns and change content, branding and visual direction for the current product.

Example request: “Build a homepage for this app with a working product demo in the hero.” See [ready prompts and evaluations](../../references/evaluation.md).
