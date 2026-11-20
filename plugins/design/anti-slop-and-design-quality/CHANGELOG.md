# Changelog

## 3.4.0 - 2026-11-10

- Removed the auto-starting MCP server from the Claude manifest. The skills work without it; the contrast MCP server is now an opt-in command documented in the README.
- Aligned manifests: `.claude-plugin/plugin.json`, `plugin.json` and `.codex-plugin/plugin.json` agree on name, version, description and author. Dropped the Cursor, Kimi, Cline, Oh My Pi and agents marketplace manifests, which named a different plugin (`antislop`) at version 3.2.26.
- Removed claims the files did not support: APCA contrast support, "six skills", install commands for `npx antislop-ai` and upstream marketplaces.
- Moved the 40 rules (R-01 to R-40) from the core `SKILL.md` into `skills/antislop/references/RULES.md`. The core skill drops from 717 to under 400 lines; rule numbers are unchanged.
- Sibling skills now point to the `antislop` skill instead of a missing `antislop.md` file.
- Removed the upstream installer CLI, first-run wizard and update instructions that downloaded code with `npx`, the upstream CI workflow and repository checks, community files, translated and long-form docs, images, and a duplicated pattern library and reference list.
- Added README, NOTICE and this changelog. Added `author`.
- Manifests now state `SEE LICENSE IN NOTICE.md` instead of `MIT`, because two skills have no confirmed license. README names the real marketplace repository.
