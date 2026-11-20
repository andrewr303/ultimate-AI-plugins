# Product truth and brand foundation

Read this when starting from a new product, when evidence changes, or when importing another studio's handoff.

## Intake without an interview loop

Inspect the supplied repository, running app, screenshots, documents and brief first. Read route definitions, the relevant components, their data sources, brand tokens, package scripts and existing README. Prefer a local test environment with seeded data. Use a public URL only when relevant; discovery must not upload private files.

Write a short product brief containing audience and buyer, the actual problem, desired outcome, primary workflow, persuasive demonstrable behavior, shipped versus planned features, available evidence, brand, CTA and constraints. State ordinary assumptions. Ask one bundled question only when the answer changes the product promise, conversion destination, claim rights or ability to execute. Creative authority already delegated means proceed.

A repository proves that code exists; it does not prove that a feature is deployed. A marketing page is a source for positioning, not independent confirmation of its claims. A supplied screenshot proves a visible state; it does not prove the steps that produced it.

## Evidence ledger

Keep `product-evidence.json` with stable claim IDs, product revision, exact claim text, verification status, supporting sources and allowed uses. Validate against the bundled contract. Track these boundaries:

| Status | Meaning | Treatment |
| --- | --- | --- |
| verified | Inspected product behavior or independent source supports the precise claim | Use within scope and record source/revision |
| supplied | The user supplied the assertion; independent verification is absent | Attribute or qualify; request proof for high-impact quantitative claims |
| illustrative | An invented scenario or sample used to explain a bounded workflow | Label the sample and avoid implying live customer evidence |
| unsupported | No adequate supporting source | Omit from marketing copy and proof shots |

Do not manufacture customers, quotes, logos, integrations, pricing, security credentials, benchmarks or results. Sample inbox counts are fixture state, not a claim about customer performance. If a price or customer logo appears in an upstream example, remove it unless it belongs to the current product and is authorized.

Link every on-screen or page claim to its claim ID. Check the visible pixels as well as the ledger: a narration saying "all" contradicts a screen showing exceptions even when both have source references. A planned capability stays planned.

## Visual provenance

Record one of these modes per capture, demonstration or shot:

- `actual`: captured behavior from the running product revision. A seeded test account is still sample data and should be described as such.
- `replay`: a faithful reconstruction using verified states or native product components, with source and revision recorded. Label a replay where viewers might infer a new live run.
- `illustrative`: concept UI or synthetic workflow whose details do not establish product behavior. Label the concept visibly.

Never imply that a deterministic sample produces a live AI answer. Keep product action and resulting state in the correct order. A result visible before the initiating event cannot demonstrate causality.

## Capture and asset chain

Use `capture-manifest.json` for stable asset IDs, relative paths, mode, dimensions, hashes, product revision and rights IDs. Capture jobs should define viewport, device scale, actions, waits, important states and outputs. Validate file existence and hashes before editing. A filename such as `approved.png` is not approval evidence.

Choose resolution from the largest output crop. If a crop of 800 source pixels will occupy 1200 output pixels, recapture or reduce its size; an HD export cannot recover lost source detail. Device scale and video dimensions must both be checked. Inspect thin glyph strokes at native size, then judge the composition at its actual viewing size.

Prepare nonproduction fixture data before capture. Keep auth state outside the deliverable, never include tokens or cookies, and redact identifiers in the source environment. Recheck canvases, images, PDFs, tooltips, exports and navigation; DOM text replacement cannot redact bitmap contents.

## Brand adoption

Extract exact logo variants, color tokens, fonts and weights, radii, borders and representative component states. Record the file or URL from which each token came. Resolve `var()` references and light/dark context rather than copying a single hex out of unrelated CSS. Detect whether fonts actually load before capture. A named family without a bundled or installed font can silently change line wraps.

Copy only licensed assets and preserve relevant notices. In `asset-manifest.json`, record creator/source, rights basis, permitted usage, attribution and any expiry or restrictions. "Royalty-free" does not mean unrestricted. No license means obtain permission or independently implement the needed capability; do not relabel third-party material with this package's license.

## Shared handoff

A self-contained handoff contains `brand.json`, `product-evidence.json`, `capture-manifest.json`, `campaign-brief.json` where applicable, `asset-manifest.json` and all referenced assets. Paths remain relative and inside the handoff; reject parent traversal and broken references. Keep source hashes and revision stable across studios. A video can be consumed as an asset by a marketing page; captures can be consumed by the video studio. Neither plugin is required at the other's runtime.

Use `python scripts/studio.py handoff --from-dir PROJECT --output HANDOFF` from the plugin root after validating the project. Recheck imported objects against the current bundled schemas. Replacing a screenshot or brand token invalidates the previous hash and any review tied to it.
