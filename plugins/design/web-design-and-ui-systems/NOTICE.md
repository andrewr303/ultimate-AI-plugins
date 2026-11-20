# Notice and provenance

## How this plugin was received

The plugin was received as a ZIP upload on 2026-11-10 (SHA-256 `7a6ec3ed64a3b94def2f982f379ee6dae3ba414f0f767af7e0c56c1297ae89d3`) and committed unmodified, apart from macOS metadata and symlinks. The version in this folder is the 2026-11-10 integration of that upload.

## Sources the files identify

- **ui-ux-pro-max (skill, data, scripts):** the upload's own metadata names https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (repository) and https://uupm.cc (homepage), by "NextLevelBuilder" / "Next Level Builder", MIT license, version 2.15.0. `LICENSE` in this folder is that license: "Copyright (c) 2024 Next Level Builder".
- **Other upstream skills (`design`, `brand`, `design-system`, `banner-design`, `slides`, `tailwindcss` and others):** the files do not state an author or source. A test file in the upload described sub-skills of the repository above, but did not list them. Treat their origin as unconfirmed.
- **Demo folders in the 21 aesthetic design-system skills:** nine `demo/source.json` files name Neuform (https://neuform.ai) page URLs as the source of the demo page. The other demos state no source.
- **Aesthetic and chrome skill text:** `thinking-orbs`, `liquid-metal-border`, `beam-glow-states` and similar skills describe third-party packages (`thinking-orbs`, `metal-fx`, `border-beam`) by name; those packages are not bundled.

## Licenses and open questions

- MIT (Next Level Builder): the repository code, scripts and data authored upstream.
- **Google Fonts metadata** (`skills/ui-ux-pro-max/data/google-fonts.csv`, `google-font-licenses.json`): lists family names, designers, dates and license names taken from https://github.com/google/fonts at revision `038b637da7b3fd956a4ed93ffc607c3d5e4ce172`. Per-family licenses recorded in the file: OFL for 1894 families, Apache 2.0 for 35, Ubuntu Font Licence for 5. No font files are bundled. The file does not state a license for the metadata compilation itself.
- **Phosphor icon catalog** (`skills/ui-ux-pro-max/data/phosphor-icons-upstream.json`): icon names and categories from `@phosphor-icons/core` 2.1.1 (https://github.com/phosphor-icons/core). No glyph files are bundled. The file does not state that package's license; check the package before redistributing the catalog beyond this plugin.
- **Neuform demo content** (`demo/index.html`, `demo/PROMPT.md`, `demo/source.json`, demo images in the aesthetic skills): no license text is stated in the files. Redistribution terms are unconfirmed.
- Identical demo images appear in more than one skill folder (for example `container-lines`, `css-border-gradient`, `nested-container-frames`). They were kept so each skill stays self-contained.

## Changes made in the 2026-11-10 integration

- Added `skills/ui-ux-pro-max/`. The upload had no folder for this skill. `SKILL.md` was rendered from the upload's `src/ui-ux-pro-max/templates/base/skill-content.md` and `quick-reference.md` using the Claude platform settings in `templates/platforms/claude.json`; the quick reference moved to `references/quick-reference.md` to keep `SKILL.md` near 500 lines, and the script path was made skill-relative. `data/` and `scripts/` were copied unchanged (the upload's test folder was left out because it depends on the upstream repository layout). `scripts/validate_data.py` passes on the copy when run from the `scripts` folder (`cd skills/ui-ux-pro-max/scripts && python3 validate_data.py`); it imports a sibling module, so it fails under `python3 -I` from another directory.
- Removed upstream repository scaffolding: `.github/`, `.releaserc.json`, `.gitattributes`, `.gitignore`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `skill.json`, the root `CLAUDE.md`, eight translated READMEs, `ORIGINAL_README.md`, `docs/` and `screenshots/`.
- Removed code and assets that no skill uses: `cli/` (a Node installer with a second copy of the data), `gallery/` (a Next.js app), `stack/` (a separate design-stack project whose setup script installs packages, and whose settings enable project MCP servers), `projects/`, `preview/`, `scripts/` (upstream maintenance scripts), `src/` (after its content moved into the skill) and the duplicate marketplace manifest. A search found no skill that referenced these folders.
- Removed the manifest entry `"commands": ["./stack/.claude/commands"]`.
- Rewrote `README.md`, rewrote `skills/web-design-router/SKILL.md`, and replaced all four host manifests with versions that agree on name, version and description. Skill count corrected from 61 to 43 member skills.
- Removed router and README references to 18 skills that the upload names but does not contain: blue-cloudy-clean-modern, book-serif-index, clean-minimal-beige-light-mode, dither-laser-dark-mode, editorial-portfolio-chapters, editorial-tech, image-first-grid-layout, skeuomorphic-ui, split-layout-technical, ui-styling, generate-reference-inspired-brand-worlds, company-logos, gooey-blob-system, marquee-loop, number-details, progressive-blur, solar-duotone-bold (and `ui-ux-pro-max`, which is now restored). No source for these was in the upload, so none were recreated.
- Skill-folder edits made in the same pass (details in `CHANGELOG.md`): "Use when" sentences added to 14 descriptions, empty Workflow headings removed, "Reference demo" sections added to the 21 aesthetic skills, nine duplicate `source-preview.jpg` files removed, references to absent skills replaced in `design`, `design-system` and `brand`, an approval step added before `design` calls a third-party image provider.
