# Notice and provenance

## How this plugin was received

The plugin arrived as a ZIP upload on 2026-11-10 (SHA-256 `86bd91af97ae86822139f137f0d082820dffae8f34062c7b59ae4a5889f53b40`) and was committed unmodified except for macOS metadata files and symlinks.

## What the files state about their origin

- The manifests declare `"license": "MIT"` for the whole plugin.
- `skills/swiftui-ui-patterns/references/navigationstack.md` links to `https://github.com/Dimillian/AppRouter` as an example library. That is a link, not a statement of authorship.
- A reference file contained local paths under `/Users/dimillian/`, which suggests at least some skill text was written by a developer with that account name. The files do not say so, and this notice does not attribute authorship.
- Several skills ship `agents/openai.yaml` files, which indicates the skills were authored for the OpenAI Codex host as well.

## Not established

- The upload contains no LICENSE file, no copyright line and no upstream repository URL for any skill. The MIT declaration in the manifests is the only license statement, and the copyright holders are unknown. Confirm the upstream sources and add their license texts before redistributing this plugin outside this repository.
- `skills/macos-spm-app-packaging/assets/templates/` holds shell scripts and a Swift package skeleton with no header naming an author or license. Treat their license as unclear.
- `skills/swiftui-ui-patterns/references/` and `skills/swift-concurrency-expert/references/swiftui-concurrency-tour-wwdc.md` summarize Apple material (the latter by its name refers to a WWDC session). Apple documentation and session content remain Apple's.

## Changes made in this integration (version 1.3.0, 2026-11-10)

- Removed `skills/performance-profiling/demo/` (generated demo page, prompt and preview image).
- Removed two local absolute paths from `scroll-reveal.md`.
- Added contents lists to 10 reference files over 100 lines.
- Added `mkdir -p Scripts` to the SwiftPM packaging example.
- Added author, aligned descriptions and bumped the version in the four manifests and the router skill metadata.
- Rewrote README.md and added this file and CHANGELOG.md.
- The upload's `categories/` folder (symlinks only) is not part of this folder.

No hooks, MCP server declarations, installers or network downloads exist in the plugin. The shell scripts in `skills/` run only when a user or agent starts them.
