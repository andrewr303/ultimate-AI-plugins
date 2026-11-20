# Notice and provenance

## Receipt

This plugin was received as a ZIP upload on 2026-11-10 (SHA-256 `a1dbf99f055c540740c0abfdf82d8936fc0580f1f21e4e9bac86a7027c8a60a7`). It was committed unmodified at 6a6540d, except for macOS metadata files and symlinks, and then integrated as described below.

## Upstream sources the files identify

| Material | Identified source | License |
| :--- | :--- | :--- |
| `antislop`, `antislop-ui`, `antislop-copywriting`, `antislop-layoutmobile`, `antislop-human`, `antislop-code`, the contrast scripts | "antislop" by Miqdad Badjuber, `https://github.com/miqdadbadjuber/anti-slop` (named in the upstream manifests and README) | MIT, `LICENSE` in this folder ("Copyright (c) 2026 Miqdad Badjuber (antislop)") |
| `skills/antislop-ui/references/` and `skills/antislop-human/references/` | "web-quality-skills" by Addy Osmani, `https://github.com/addyosmani/web-quality-skills`, as stated in each file's header | MIT, `LICENSE-web-quality-skills` in each skill folder ("Copyright (c) 2026 Addy Osmani") |
| `no-ai-design-slop`, `audit-ai-design-slop` | Not stated. `ARTICLE.md` says it combines "the Impeccable slop catalog, the DesignCode anti-slop workflow, and the recurring principles in Meng's design skills". `skills/no-ai-design-slop/REFERENCES.md` lists public links (including `https://github.com/Leonxlnx/taste-skill`, `https://github.com/petergyang/no-ai-slop`, `https://github.com/MengTo/Skills`). | **Unclear.** The files carry no license or author line. They are not covered by the MIT `LICENSE` above on the evidence of the files alone. Confirm the origin before redistributing these two skills. |

The copyright holder and license of the two unclear skills were not guessed.

## What this integration changed

- Removed the MCP server declaration from the Claude manifest (it started a local Python process on enable). The launcher moved to `scripts/contrast-mcp-launcher.mjs` and is opt-in; its server version string now reads 3.4.0.
- Removed upstream scaffolding: `.github/`, `cli/` (an npm installer package, its lockfile and smoke tests), `scripts/check-repo.mjs` and `scripts/skill-index.mjs` (checks for the upstream repository layout), `rules/`, `package.json`, the Cursor, Kimi, Cline, Oh My Pi and agents manifests, the nested marketplace files, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `GUIDE.md`, `ROADMAP.md`, `ORIGINAL_README.md`, `assets/` (banner and comparison images), and the empty `categories/` tree (replaced by the skill table in the README).
- Removed the generated-from-source standalone file `antislop.md` (the core is now only `skills/antislop/SKILL.md`), the `VERSION` file, the duplicate `ARTICLE.md` and `REFERENCES.md` under `audit-ai-design-slop`, and the first-run install and update sections of the core skill, which pointed to `npx` downloads.
- Moved rules R-01 to R-40 to `skills/antislop/references/RULES.md`; corrected the router table and manifests (no APCA, eight skills).
- Set `author` to Andrew Rodriguez and bumped the version to 3.4.0.

Original upstream files were kept in the upload archive and are not otherwise available here.
