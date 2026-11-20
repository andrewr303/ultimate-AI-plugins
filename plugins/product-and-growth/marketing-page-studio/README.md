# marketing-page-studio

Create product-centered marketing sites with responsive composition, bounded interactive demonstrations and reversible scroll stories. This is one independent, skills-and-local-scripts plugin. All required shared code is bundled here; the other Studio plugin is optional.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`marketing-page-studio`](skills/marketing-page-studio/SKILL.md). Try this prompt.

> Plan a responsive product page around this feature demo. Define the interaction and its keyboard and reduced-motion states before building.

## Quick start

Unpack the archive, open a terminal in this directory, and use Python 3.10 or later:

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/studio.py doctor --launch
python scripts/studio.py init --output project-site
python -m http.server 4173 --bind 127.0.0.1 --directory project-site
# In another terminal:
python scripts/studio.py web verify --site project-site --output site-review
```

Use a virtual environment for dependency isolation. A system Chromium can be selected with `STUDIO_BROWSER`. FFmpeg and ffprobe must be installed on PATH for video encoding and recording conversion. No browser or FFmpeg binary is distributed here.

The Tandem example is a local support-inbox product fixture with synthetic data and deterministic processing. It does not call a live AI service or present real customer evidence. Its source is editable and its behavior is the basis for example claims.

Release 1.0.1 moved the entry points from `bin/` to `scripts/` so claude.ai and Cowork can install the plugin. The downloadable ZIP in `artifacts/product-studios/` is the earlier 1.0.0 release and still uses `bin/`; the paths here apply to this source folder. See [CHANGELOG](CHANGELOG.md).

## Agent use

Start with the `marketing-page-studio` entry skill. Its specialist routing loads the relevant references only when needed. Find resources with `python scripts/studio.py index --query capture`.

[Host installation and evidence](docs/INSTALL.md) distinguish verified local Codex package installation from untested host/runtime combinations. [Execution guidance](references/execution.md) covers package-relative paths and operating modes. [Skills and resources](references/README.md) provide the focused catalog and ready prompts.

## Tools

| Command | Purpose |
|---|---|
| `doctor [--launch]` | Detect Python dependencies, browser, fonts, disk, media executables and optional host CLIs. |
| `discover --source PATH --output DIR` | Read a local repository or supplied file, inventory bounded relevant sources, extract CSS tokens, and create an honest draft product brief. |
| `discover --source URL --allow-network --output DIR` | Fetch the named public HTML source; never upload local files. |
| `init --output DIR` | Copy the independently runnable synthetic example to an empty directory. |
| `validate --schema NAME --input FILE --root DIR --use website\|video\|ads --check-files` | Validate a bundled contract with product evidence and current file hashes. |
| `index [--query TEXT]` | Find on-demand skills and references. |
| `handoff --from-dir DIR --output DIR` | Validate known handoff documents and copy their safe, referenced files with a hash receipt. |
| `campaign --brief FILE --output DIR` | Plan a bounded three-hook, two-body, two-ratio experiment matrix; proposals still require editorial review and representative previews. |
| `package-check` | Validate portable manifests, skill metadata, links, required resources and portable source paths. |

Specialist commands and exact input contracts appear in `--help` and the linked resources. Commands emit machine-readable reports and nonzero exit codes on failure. Run scripts with their full installed path when the working directory differs from this plugin; they resolve resources from their own file location.

## Production contracts and handoffs

[Contracts](contracts/README.md) document versioned brand, evidence, capture, interactive-state, campaign, storyboard, render, export, QA, rights and experiment records. [Examples](contracts/examples/) are illustrative records; their placeholder asset paths must be replaced or supplied before contextual/file validation. `discover` writes `product-evidence.draft.json` because inventory alone cannot verify a product claim. Promote it to a complete `product-evidence.json` only after checking the actual product and supplying the full required fields.

Actual capture, faithful replay and illustrative surfaces are distinct modes. Claims need sources, product revision, status and permitted uses. Renderer success does not certify design, truthfulness or editorial quality. Inspect browser screenshots and decoded final frames; keep technical QA separate from creative review.

No deployment, upload, external generation, credit spending or production-data write occurs by default. Local user-provided audio can be used when rights are recorded; optional services require explicit configuration and authorization.

## Provenance and limits

The [source integration audit](docs/source-audit/source-integration.md) and [file inventory](docs/source-audit/inventory.json) record archive hashes, implementation findings, license decisions and the two inaccessible sources. [Third-party notices](THIRD_PARTY_NOTICES.md) preserve applicable attribution. Upstream sample films, customer data, product brands and commercial audio are excluded.

[Dependencies and portability](docs/DEPENDENCIES.md) document the tested Linux environment, Windows commands, optional services and untested adapters. [Evaluation prompts](references/evaluation.md) describe realistic routing and behavior cases; a prompt corpus is distinct from a completed host-model evaluation.

## Local asset tools

`python scripts/assets.py --help` exposes screenshot optimization with explicit crops, safe alpha handling and hash receipts, plus capture-density checks against intended CSS width, DPR and zoom. It never enlarges or overwrites a source by default.
