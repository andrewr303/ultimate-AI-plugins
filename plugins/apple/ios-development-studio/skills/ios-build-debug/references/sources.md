# Build and debugging provenance

Original synthesis informed by these supplied archive paths:

- `ios-simulator-skill-main.zip`: `ios-simulator-skill/skills/ios-simulator-skill/scripts/build_and_test.py`, `scripts/xcode/{builder,config,reporter,xcresult}.py` and repository `references/test_patterns.md`.
- `app-store-connect-cli-skills-main.zip`: `skills/asc-xcode-build/SKILL.md` and `references/portable-ios.md`.
- `Skills-main.zip`: `ios-debugger-agent/SKILL.md` and associated debugging references.

These snapshots support the ideas of explicit scheme/destination discovery, structured build results and targeted runtime diagnosis. Their command examples are not pinned runtime guarantees. No upstream script is bundled or automatically executed by this skill. Narrow portable compilation in a prepared package must not be generalized to an arbitrary Xcode application on Linux.

Consult current Apple Xcode documentation and the installed `xcodebuild`/`xcresulttool` help for execution. See the plugin [source map](../../../docs/source-map.md) for archive hashes, license notices and retained-source decisions.
