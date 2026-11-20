# Product surfaces and browser delivery

Load this resource when implementing an interactive product surface or reviewing a static marketing site. The executable reference is `../examples/tandem/`; avoid copying its brand into a client project.

## Choose the implementation

Preserve an existing React/Next.js application. Reuse its actual components where safe, isolate synthetic data and never call production mutation endpoints from a public demo. The static reference needs no build step. Its `DemoMachine` class and event boundaries can be transplanted into a React reducer; use the framework’s own state, routing and asset pipeline rather than embedding another framework or a second rendering engine. Clean up timers/observers when a component unmounts.

The sample custom element is intentionally one workspace per page; IDs are stable for captures and keyboard labels. For multiple independent instances, namespace the IDs and label associations at construction. Keep the original fixture unchanged as a reproducible test case.

## Pattern index

| Visitor learns | Working reference | Required states or fallback |
| --- | --- | --- |
| What one request becomes | `product.js` / `DemoMachine` | initial, input, loading, success, empty, error, retry, cancel, reset |
| How a reply remains under human review | Editable `#reply-output`, `#approve-button` | edited → draft; approval marks ready without sending |
| How to locate a request | `#inbox-search` | matching results, empty, clear, selected request retained |
| How the workflow is structured | `workflow.html` tabs | roving tabindex, arrow keys, Home/End; all panels visible without JS |
| What context the product adds | `#comparison-range` | native keyboard/touch range and updated percentage |
| What should be handled next | `[data-reorder]` | pointer drag/drop and named Up/Down buttons; boundaries disabled, order announced |
| What details matter | Native `details`/`summary` | keyboard behavior, real content, no animation dependency |
| What happens across a handoff | `story.js` | reversible state from real scroll, direct controls, explicit replay, offscreen stop |

`tandem:state` is a bubbling event with `detail.state`. Use it for local instrumentation or tests, not unrequested analytics. No network calls are made by the sample.

## State rules

Cancellation clears the in-flight timer before changing state; a cancelled operation must not show a late result. Reset restores source sample data and removes results. Error retains the input and offers retry. Empty input reports what is missing. A deterministic operation is labeled as such rather than presented as a live model call. A draft edit re-enables review. Bind actual application integration separately and document configuration, authorization and costs.

The fictional product cannot justify real pricing, integrations, customer proof or performance claims. Its own code proves only the explicitly implemented local behavior. Claims need a product revision and a verified source in `product-evidence.json` before appearing in client work.

## Screenshots and mobile compositions

Capture around the largest intended display. An image shown at 800 CSS pixels with a 1.5× zoom should be at least 1200 physical pixels wide, or 2400 at 2× display density. Keep aspect ratio with `height:auto`; use purposeful detail crops when a dashboard becomes unreadable. Record crop coordinates and mode in capture provenance.

Use a simple border and shadow to distinguish a product surface. Browser chrome and perspective are optional and must not reduce legibility. On phones, reorganize to one meaningful task rather than scaling the entire desktop interface to fit. The reference turns the sidebar into a compact request strip, stacks the input/result, and keeps native controls usable. Use real image alt text describing the visible state; decorative framing is hidden from assistive technology.

## Scroll mechanism

Scrollcraft’s semantic authored DOM, normalized reversible progress, independent mobile composition and actual frame inspection informed this implementation. The source license/attribution is retained in the package notices. Its full cinematic/video engine is intentionally unnecessary for this bounded product story.

`story.js` reads step bounds on scroll through one scheduled animation frame. An `IntersectionObserver` disables work while offscreen. No permanent animation loop runs. Direct stage controls preserve access on touch and with reduced motion. The reduced-motion presentation makes all result details visible and removes sticky placement. Do not equate a normal CSS animation with scroll-linked progress.

## Browser checks and critique

Run `python scripts/web.py verify --site examples/tandem --output evidence/website` to verify the supplied fixture. This is a known-fixture acceptance suite, not a universal accessibility scanner. For client projects, adapt selectors and assertions to the real workflows; do not claim generic checks passed when the fixture alone was tested. Use `capture.py` for generic URL/selector jobs.

Inspect screenshots at representative desktop and mobile widths and meaningful initial, action, result and error states. Review hierarchy, clarity of the promise/CTA, readable interface details, proportionate crops, focus and scroll transitions. Automation can detect overflow and verify operations, but cannot prove persuasive art direction or understandable copy.

`browser-qa.json` binds every run to the site’s file hashes and records actual passes/failures. The contact sheet is a review aid. Never present an older contact sheet or report as evidence for updated source. An imported video changes the site and requires a new targeted browser check. Check a decoded frame and the encoded file separately from renderer exit status.

## Capture and video handoff

`capture.py --job job.json --output project` accepts bounded actions from the capture-job schema. `wait-for` first waits for a visible selector; optional `holdMs` gives explicit settled reading time (0–10000ms). Record no private input in logs. A storage state file can select a local authenticated context without copying its credentials into the package. Captures and WebM assets have hashes, revision, rights ID and actual/replay/illustrative mode. A canonical `capture-manifest.json` lives at the project root so other plugins can resolve every asset relative to the same production project.

`web.py import-video --site site --package video-package [--variant ID]` accepts canonical export-variants JSON. It checks local paths and rejects traversal/symlink escape, runs the bundled schema and semantic validator with evidence/revision checks, and copies MP4/WebM, poster and caption assets. The production package must include valid product evidence. If an asset rights manifest is supplied, declared hashes are checked against actual files and selected assets with unknown redistribution rights are rejected. Missing or incomplete rights registrations are explicitly recorded as unverified or partial provenance. Copied byte hashes never imply that a newer renderer revision produced the video. Generic copy is used unless validated evidence identifies synthetic sample data.

Only after validation is a semantic, nonautoplay player added to the feature page. The base example works independently and requests no missing media. Review imported content, rights and revision consistency before shipping it.
