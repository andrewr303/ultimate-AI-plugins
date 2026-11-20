# Visual recipes for technical documentation

Choose a recipe from the content and reader need. These are original composition
guidelines, not a borrowed theme or a requirement to add every element.

## Repository README

1. Project name and a plain-language sentence describing its actual purpose.
2. A restrained verified status line when useful; omit fabricated popularity badges.
3. One relevant screenshot/diagram only when it explains something the text cannot quickly show.
4. A compact working quickstart with prerequisites and expected result.
5. A few evidenced capabilities and links to deeper tasks/reference.
6. Contribution, support/security and license paths only when they actually exist.

Keep core information readable without HTML styling. Prefer ordinary Markdown over
layout tables and centered paragraphs used solely to imitate a landing page.
For a complex README, add a small table of contents only if it reduces navigation effort.
Do not turn every link into a badge. Verify badge targets and the truth of their labels.

## Documentation landing page

Use a precise title and value statement followed by a visible “get started” path.
Add grouped entry links for distinct audiences or tasks. Show the simplest real example
when it helps readers decide where to begin. Keep marketing claims out of technical facts.
The body should answer “where do I go next?” rather than present a grid of empty promises.

## Task guide

Use goal → prerequisites → steps → expected result → recovery → next task.
Keep commands near the explanations that make them safe and understandable.
A numbered list works well for sequential actions; a deep nesting of cards usually does not.
Use warnings only for actual consequences, placed before the relevant action.

## Reference page

Use consistent input/output field structure and stable anchors. Long parameter tables
may need smaller logical groups. Include units and defaults only when supported.
Code should preserve indentation and horizontal scroll without making the whole page scroll.
Use a clearly labeled copy action from an existing accessible component when available.

## Site token worksheet

Record semantic roles rather than arbitrary component colors:

| Role | Check |
| --- | --- |
| Body / secondary text | Readable against each intended surface |
| Background / raised surface | Hierarchy remains visible without excessive borders |
| Accent / active state | Meaning also conveyed by text, shape or semantics |
| Focus indicator | Clearly visible on links and controls in both themes |
| Code surface / syntax | Comments, strings and selected text stay readable |
| Warning / error / success | Icon or label accompanies color |
| Typography / measure | Body and code remain readable at narrow and enlarged sizes |
| Spacing | Consistent rhythm for page sections, examples and captions |

Map roles to existing framework variables. Verify with a contrast tool and actual
browser rendering; a pleasing palette in isolation is insufficient.

## Diagram decision

- Sequence: use a sequence diagram when order and handoffs matter.
- Relationship: use a small flowchart when ownership and paths matter.
- Comparison: use a table when exact attributes matter more than spatial relationships.
- Architecture: show only evidenced components and meaningful boundaries.

Every diagram needs a descriptive caption and nearby text that communicates its
essential information. Arrow direction, labels and boundaries should agree with source.
Keep the number of nodes small enough to read on the target viewport.

## Screenshot record

For each consequential screenshot, record the source route/task, product revision or
version if known, capture conditions and any redaction. Do not expose credentials,
personal data or internal hostnames. Label illustrative images in their caption.
Do not use screenshot text as the sole explanation of setup, errors or API values.

## Review evidence

Record the actual renderer/build, page routes, viewport sizes, themes and controls tested.
Check image failures, keyboard use and zoom. Record a limitation when a target renderer
cannot be inspected; do not describe a source-only review as a visual pass.
