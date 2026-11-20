# Version 1.1 validation

Local validation completed on October 27, 2026 (America/Denver), using Linux, Python 3.12.14, system Chromium and FFmpeg/ffprobe 7.1.5. In version 1.1.1 the command scripts moved from `bin/` to `scripts/`; the rows below record 1.1.0 under the old `bin/` paths and were not rerun as written. This records executed checks, separate from the behavioral prompt specifications and upstream-source observations.

| Check | Observed result |
|---|---|
| `python -m unittest discover -s tests -v` | 104 passed, no failures or skips |
| `python -m unittest discover -s contracts/tests -v` | 30 passed, no failures or skips |
| Custom-template suite after final awaited-error handling change | 7 passed |
| `python bin/studio.py package-check` | Passed: manifests, skill metadata, links, paths and required resources |
| `python bin/studio.py doctor` | Required dependencies passed; reports plugin 1.1.0 |
| Browser launch | Initial doctor launch and actual browser render/capture tests passed |
| `git diff --check` | Passed |

The full script suite includes real Chromium capture conditions and custom rendering; real FFmpeg frame extraction/color assertions; source/output tampering; invalid readiness/timing inputs; safe variant output, collision and interrupted-copy cases; and the existing seek/layout/audio/asset regressions. After the full run, the final renderer error wrapper was checked with the affected custom-template suite and both real renders were regenerated.

| Real render | Encoded output | Technical QA |
|---|---|---|
| Tandem vertical preview | 540 × 960, 12 fps, 144 frames; authored captions produce 32 decoded review frames and two sheets | Passed |
| Independent Relay custom-template final | 640 × 360, 12 fps, 36 frames; named story beats and caption edges produce 12 decoded review frames and one sheet | Passed |

Both current renders were rechecked with `scripts/check_receipt.py` against current source, configuration, dependencies and output hashes. The Relay decoded contact sheet and Tandem decoded poster were visually inspected. Those observations are still-image evidence; normal-speed playback and audio listening are not claimed. The Relay example is sound-off and illustrative, with its scope recorded in product evidence.

No new runtime dependencies were added. Optional Remotion and Hyperframes engines, Windows/macOS execution, desktop installation and model-driven skill invocation were not exercised. CLI help exposes plugin installation/listing commands without a standalone package validator; user installation and account state were not changed. Evaluation prompts remain `not-run` until an actual host session evaluates them.

Research received manual source review, including independent author identities, pinned GitHub implementations and official documentation. No automated research gate or legal clearance is claimed. See the [research decisions](research/decision-report.md) and its unresolved annex.

This document records local validation. Commit, PR and CI status are recorded separately in repository history and the PR ledger; this validation does not establish deployment.
