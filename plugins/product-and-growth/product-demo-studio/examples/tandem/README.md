# Tandem: one synthetic product, two visual modes

Tandem is an original deterministic local support triage fixture. It has three synthetic requests, a category/priority/owner suggestion, an editable reply, a ready-for-review confirmation and error/reset states. No external AI provider is called and nothing is sent. It has no asserted customers, integrations, pricing, traction or performance metrics.

`fixture/` is the complete runnable local product website. Serve it with `python -m http.server 8000 --directory examples/tandem/fixture` from the installed plugin root, then open `http://localhost:8000/app.html`. The same source files appear in the marketing plugin example, but this copy operates independently. Source revision `tandem-4f236886e8ed1dea` binds app.html, product.js and styles.css; `fixture/product-source.json` records exact hashes.

From the installed plugin root:

```text
python scripts/studio.py doctor
python scripts/render.py --job examples/tandem/promo-vertical.json --output rendered/vertical --preview
python scripts/render.py --job examples/tandem/promo-vertical.json --output rendered/vertical-final
python scripts/render.py --job examples/tandem/promo-landscape.json --output rendered/landscape-final
python scripts/render.py --job examples/tandem/footage-landscape.json --output rendered/actual-workflow
```

The promo jobs use a labeled faithful replay with verified request/route/draft/review states. The landscape includes a quiet original score, mixed to the documented loudness target; the vertical is intentionally sound-off. Neither has narration. Both render at 24fps for 12 seconds with native landscape/portrait composition.

The actual-footage job uses the bundled `capture/tandem-workflow.webm`, recorded from real interactions in this local product fixture. It cuts an explicit 11 seconds from the 11.44-second source without speed changes or added holds. The authored crop retains the request, organize button, routing context, draft and review control. It includes an external recording/synthetic-data label because the crop excludes the source window header. The original 1440×1080/25fps WebM and screenshots remain in `capture/`, with canonical capture and rights manifests. A captured screenshot may extend to document height1106 while the actual recording remains viewport1080; those are separate assets with explicit dimensions.

`asset-manifest.json` records original fixture capture and original score rights, paths and hashes. `product-evidence.json` records permitted claims and their limitations. The source fixture itself is the product being demonstrated; the examples do not establish behavior for an unrelated app.

`experiment-manifest.json` defines three angle hooks, two proof bodies and two placements. `campaign-jobs/` contains all twelve portable planned jobs and their required source files. Generate them again with:

```text
python scripts/variants.py --job examples/tandem/promo-vertical.json --manifest examples/tandem/experiment-manifest.json --output campaign/jobs --limit 12 --use ads
```

The delivered production evidence renders a bounded representative set: three hook previews plus a separate before/after body preview. The full twelve-cell matrix is planned and validated, not twelve final ads. Previews are half the configured dimensions at12fps and marked as previews in their receipts. Before/after focuses the result by replacing the original request after organization; context retains the original request with the result; review emphasizes the editable draft.

For another product, supply a verified custom composition with `template` in its render job. Changing the brand name alone is blocked from silently carrying Tandem UI into client work. See `references/renderer.md` for adapter contracts, dependencies, review requirements and untested host/renderer limits.
