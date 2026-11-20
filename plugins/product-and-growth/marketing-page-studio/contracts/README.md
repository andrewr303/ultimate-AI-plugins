# Studio production contracts 1.0.0

These contracts travel with each plugin. They are independent local JSON schemas, not a hosted API. Read only the contract needed for the current task. The two plugins exchange the same objects without importing one another.

Install the validator dependency using `python -m pip install -r contracts/requirements.txt`, then run from the installed plugin:

```text
python contracts/validate.py --schema campaign-brief --input PROJECT/campaign-brief.json --root PROJECT --use ads
python contracts/validate.py --schema capture-manifest --input PROJECT/capture-manifest.json --root PROJECT --check-files
python contracts/validate.py --schema storyboard --input PROJECT/storyboard.json --root PROJECT --captures PROJECT/capture-manifest.json --use video
```

The validator prints JSON. Exit 0 means the requested mechanical checks passed, 1 means invalid data, and 2 means an input/setup error. Passing validation does not establish good design, persuasive storytelling, or product truth: inspect the product evidence and actual output.

| Contract selector | Purpose | Example |
| --- | --- | --- |
| `brand` | Identity, tokens, source, synthetic status | [brand](examples/brand.json) |
| `product-evidence` | Product revision, brief, source-backed claim registry and allowed uses | [evidence](examples/product-evidence.json) |
| `capture-job` | Explicit browser actions and capture size | [capture job](examples/capture-job.json) |
| `capture-manifest` | Captured files, modes, hashes, dimensions and rights links | [capture manifest](examples/capture-manifest.json) |
| `interactive-demo` | Purpose, states, transitions, keyboard and reduced motion | [interactive state model](examples/interactive-demo.json) |
| `campaign-brief` | Audience, promise, product proof and CTA | [campaign](examples/campaign-brief.json) |
| `storyboard` | Frame-based shot list, source assets, captions and safe zones | [storyboard](examples/storyboard.json) |
| `render-job` | Executable renderer configuration and optional source binding | [render job](examples/render-job.json) |
| `export-variants` | Composition dimensions, placement and deliverable paths | [exports](examples/export-variants.json) |
| `experiment-manifest` | Distinct hooks, bodies, hypotheses and bounded matrix | [experiments](examples/experiment-manifest.json) |
| `qa-results` | Actual checks, methods, statuses and evidence | [QA record](examples/qa-results.json) |
| `asset-manifest` | Rights, provenance, restrictions and redistribution decision | [asset rights](examples/asset-manifest.json) |

See [invariants and handoffs](docs/invariants.md), [host packaging evidence](docs/host-packaging.md), and [placement profiles](placement-profiles.json). Examples use a synthetic Tandem support inbox. All-zero hashes in templates are placeholders, never a claim of verification. Replace them with hashes of actual files before using `--check-files` or source-bound production checks.
