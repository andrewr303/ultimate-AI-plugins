---
name: mps-product-evidence
description: "Use when discovering a product from a repository, app, website, screenshots or documentation, capturing its states, and building evidence-backed assets for marketing pages."
---

# Product evidence and capture

Read [foundation](../../references/foundation.md) and the capture section of [website QA](../../references/website-qa.md).

Run discovery from the plugin root with `python scripts/studio.py discover --source PRODUCT_PATH --output PROJECT`; add `--allow-network` for a public URL. Inspect meaningful components and the running workflow rather than accepting extracted text as verification.

1. Read available routes, component labels, data sources, brand tokens and shipped documentation. Record the revision or a source-tree digest.
2. Select important initial, input, processing, result, empty and error states. Prepare labeled sample data and a reproducible capture job. Keep auth outside the output.
3. Capture the entire workflow and detail views with sufficient native resolution. Use `python scripts/studio.py capture --job JOB.json --output CAPTURES` after checking its `--help` and the bundled capture-job example.
4. Inspect captures for clipped labels, loading failures, secrets, incorrect data and softness. Hash the actual files and record their mode, rights and product revision in the capture manifest.
5. Build the evidence ledger and a handoff. A screenshot-only task can use only the states visible in supplied screenshots; additional transitions are illustrative until verified.

For authenticated products, use the app's documented test account/session flow; do not guess credentials. For unavailable browsers, complete discovery and capture planning, report the precise dependency failure, and do not substitute invented screenshots.

Acceptance: every capture file resolves from its manifest, dimensions and hashes agree, and page claims are no stronger than the evidence. Export to Product Demo Studio through files, not a runtime dependency.
