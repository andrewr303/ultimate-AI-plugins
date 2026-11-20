# Changelog

## 1.0.1 - 2026-11-10

- Moved the command-line entry points from `bin/` to `scripts/` (`studio.py`, `assets.py`, `register_codex.py`). A top-level `bin/` directory stops claude.ai and Cowork from installing a plugin. Every documented command now reads `python scripts/studio.py ...`; the commands take the same arguments as before.
- Added `author` to both manifests.
- Updated tests and docs for the new paths and regenerated `PACKAGE-CONTENTS.json`.
- The downloadable ZIP under `artifacts/product-studios/` is the 1.0.0 release and still uses `bin/`.
