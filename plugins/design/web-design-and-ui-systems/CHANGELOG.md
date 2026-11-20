# Changelog

## 2.16.0 - 2026-11-10

Integration of the uploaded ZIP into an installable plugin.

- Added the `ui-ux-pro-max` skill with its data and search scripts (it was named by the README and router but missing from the upload).
- Fixed counts: 43 member skills, not 61. Rewrote the README and the `web-design-router` skill so every named skill exists; removed 17 references to skills that are not in the upload.
- Added a "What runs on your machine" section and a "Related plugins" section to the README. The plugin has no hooks, MCP servers or installers.
- Aligned all four host manifests (`.claude-plugin`, root `plugin.json`, `.codex-plugin`, `.cursor-plugin`) on name, version, description and author. Removed the manifest pointer to a commands folder from the unrelated `stack/` project.
- Removed upstream scaffolding, translated READMEs, the Node installer (`cli/`), the Next.js gallery, the `stack/` project, sample projects and screenshots. The folder dropped from 27 MB to about 18 MB.
- Skills: 14 descriptions gained a "Use when" sentence, empty Workflow headings were removed, the 21 aesthetic skills link their demo files, `design` asks for approval before calling a third-party image provider, and references to absent `ui-styling` and `ui-ux-pro-max` were replaced with bundled skills.
- Banner and social-photo routes in `design` point at the bundled `ui-ux-pro-max` skill again; the routing table no longer states script and reference counts; 30 long reference files gained a Contents list.
- Added `NOTICE.md` with sources, licenses and open license questions.
