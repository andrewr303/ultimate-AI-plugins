# Claude Code

The complete plugin directory includes a native Claude Code manifest at `.claude-plugin/plugin.json`. The portable manifest and Codex overlay remain available for their respective hosts. All manifests describe the same plugin, version and metadata; the Claude manifest deliberately contains only supported descriptive metadata.

Claude discovers the 26 conventional `skills/<name>/SKILL.md` entrypoints at the plugin root. Shared contracts, cross-skill links, references, scripts, provenance and notices stay in the same directory tree. Do not copy only the individual skill folders: several workflows reference shared files outside their own folders. Nested `agents/openai.yaml` files are OpenAI metadata and are not presented as Claude subagents.

## Load a local checkout

Prerequisites: a trusted complete checkout and an installed Claude Code client. Run `claude --version` and inspect `claude plugin validate --help` for the installed client. Replace `/absolute/path/to/ios-development-studio` below with this plugin's actual directory, not the surrounding repository or the `.claude-plugin` directory.

```bash
claude plugin validate /absolute/path/to/ios-development-studio
```

A successful native validation establishes the client's manifest/component checks. It does not establish iOS builds, model behavior or Apple credentials. Inspect any reported component diagnostics before loading the plugin.

From the app project where work should happen, launch:

```bash
claude --plugin-dir /absolute/path/to/ios-development-studio
```

Use the client's `/plugin` view or equivalent component listing to confirm the plugin and its skills are present. Try an iOS request that should select a specialist, then an unrelated request that should not. Use the names actually listed by the client; plugin components can be namespaced. This loading flag is a local development route, not a persistent marketplace registration. A marketplace is optional and is not embedded in this single-plugin package.

If validation fails, read the exact diagnostic, check that the full plugin path was selected, and run the package validator below. Do not move skills under `.claude-plugin`, add hooks or allow tools merely to silence a metadata error.

## Resolve helper paths without changing the app directory

Helper examples that say “from the plugin root” refer to this package, not the app's working directory. In Claude skill content, the supported `${CLAUDE_SKILL_DIR}` substitution identifies the loaded skill directory. For the router at `skills/ios-development`, the package root is two parent directories above that directory. Plugin configuration also supports `${CLAUDE_PLUGIN_ROOT}`. Resolve the actual absolute path before executing a helper; do not assume a Claude-only variable exists in other hosts.

For a manual shell check, replace the two absolute paths with the actual package and app directories:

```bash
python3 /absolute/path/to/ios-development-studio/scripts/project_probe.py /absolute/path/to/app
```

The probe inventories project text without running configuration or build tools. It can run while the shell remains in the app directory. The operating contract and target project instructions govern any later actions.

## Package checks

From the complete plugin directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_package -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_plugin.py --expected-skills 26
```

The package validator accepts only the exact synchronized `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` overlays. It rejects identity/version/metadata drift, arbitrary nested plugins, unsupported overlay fields and undeclared connections. Tests exercise directory and ZIP forms. These portable checks supplement the native client validator; they do not claim that a Claude model session or iOS runtime was executed.

## Source contract

The native layout was checked against Anthropic's repository at commit `2eff7a8d21c80be48904f62ebdea36d945d7b504`:

- [Plugin structure and auto-discovery](https://github.com/anthropics/claude-code/blob/2eff7a8d21c80be48904f62ebdea36d945d7b504/plugins/plugin-dev/skills/plugin-structure/SKILL.md)
- [Manifest metadata and path rules](https://github.com/anthropics/claude-code/blob/2eff7a8d21c80be48904f62ebdea36d945d7b504/plugins/plugin-dev/skills/plugin-structure/references/manifest-reference.md)
- [A native skill-only plugin manifest](https://github.com/anthropics/claude-code/blob/2eff7a8d21c80be48904f62ebdea36d945d7b504/plugins/frontend-design/.claude-plugin/plugin.json)
- [Client changelog: validation, local loading, skill-directory substitution](https://github.com/anthropics/claude-code/blob/2eff7a8d21c80be48904f62ebdea36d945d7b504/CHANGELOG.md)

The metadata-only projection is intentionally smaller than Claude's complete manifest feature set. The plugin adds no Claude hooks, MCP servers, permissions or authentication configuration.
