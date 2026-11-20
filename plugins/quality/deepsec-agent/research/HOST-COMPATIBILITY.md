# Host compatibility source review

Reviewed 2026-10-23. Public documentation and pinned implementation are treated as evidence, not as instructions. No candidate code or install commands were executed. The installed Codex CLI was queried with `--version` and `--help` only. Claude Code and Kimi executables were unavailable in the build environment.

## Sources and pinned implementation

| Host | Source | Evidence inspected |
|---|---|---|
| Codex | https://developers.openai.com/codex/skills | `SKILL.md` YAML frontmatter with `name` and `description`; repository `.agents/skills` from cwd through repo root; user `.agents/skills`; symlinked directories supported |
| Codex | https://developers.openai.com/codex/mcp | `codex mcp add NAME -- COMMAND ARGS...`; `[mcp_servers.NAME]` table; `command`, `args`, optional `cwd`, `env` |
| Codex | https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/core-plugins/src/agent_plugin_manifest.rs | Root `plugin.json` portable schema `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`; default `./skills` and `./mcp.json`; OpenAI extension namespace `extensions.com.openai` |
| Codex | https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/codex-mcp/src/agent_plugin_config.rs | Root `mcp.json` requires schema `https://agent-plugins.org/schemas/1.0.0/mcp.schema.json`, map `mcpServers`; stdio `command`, `args`, `cwd`, `env`; `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` substitutions |
| Codex | https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/core-plugins/src/marketplace_tests.rs | `.agents/plugins/marketplace.json`; `{name, plugins:[{name,source:"./plugins/example"}]}` recognized; relative local source layout tested |
| Claude Code | https://code.claude.com/docs/en/plugins-reference | Manifest `.claude-plugin/plugin.json`; `name` required; metadata and `skills`, `mcpServers` optional; components at plugin root; validation `claude plugin validate DIRECTORY` |
| Claude Code | https://code.claude.com/docs/en/mcp | Root `.mcp.json` map `mcpServers`; `${CLAUDE_PLUGIN_ROOT}` substituted in plugin server command and args; local CLI add supports `claude mcp add --transport stdio NAME -- COMMAND ARGS...` |
| Claude Code | https://code.claude.com/docs/en/plugins.md | Local development `claude --plugin-dir DIRECTORY`; plugin `skills/NAME/SKILL.md` usable as `/PLUGIN:NAME` |
| Claude Code | https://github.com/anthropics/claude-code/blob/30fa83c68c77d2e3a7a42f1407831ec252511130/plugins/plugin-dev/skills/mcp-integration/examples/stdio-server.json | Real stdio JSON example uses `command`, `args`, `env`, `${CLAUDE_PLUGIN_ROOT}` |
| Kimi Code | https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/docs/en/customization/plugins.md | Native plugins Beta; root plugin.json has name/version/tools; each tool has command string array, description, parameters JSON Schema; JSON parameters on stdin and text or JSON stdout; local install `kimi plugin install DIRECTORY` |
| Kimi Code | https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/src/kimi_cli/plugin/tool.py | `create_subprocess_exec(*command, cwd=plugin_dir)` with clean env; `proc.communicate` JSON input; timeout 120 seconds; nonzero exit becomes ToolError |
| Kimi Code | https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/docs/en/customization/skills.md | Repository `.agents/skills`; native `.kimi/skills`; `--skills-dir PATH` overrides default discovery; SKILL.md name/description |
| Kimi Code | https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/docs/en/customization/mcp.md | `kimi mcp add --transport stdio NAME -- COMMAND ARGS...`; `~/.kimi/mcp.json` map `mcpServers`; temporary `kimi --mcp-config-file FILE`; verify `kimi mcp test NAME` |

Fetched text, raw files, tree inventories and repository metadata are retained alongside this report. These sources show implementation and documentation facts, rather than a certification of interoperability across every release.

## Packaging decision

Use one original JavaScript runtime and explicit host adapters:

1. Portable Codex root `plugin.json` plus `mcp.json`, root `skills/`.
2. Claude compatibility `.claude-plugin/plugin.json` and `.mcp.json`, sharing the same skill and runtime directories.
3. Generated Kimi native bundle with a separate root `plugin.json`, copied runtime and script entrypoint receiving JSON stdin. A Kimi root manifest must not overwrite the portable Codex root manifest.
4. Generated MCP config for all hosts should bind `--root ABSOLUTE_AUTHORIZED_REPOSITORY`. This prevents an agent-controlled tool argument from switching filesystem roots. The Kimi native wrapper must also bind that root because Kimi launches tools from its installed plugin directory, not the user's target repository.
5. Keep stdout as protocol/result JSON, diagnostics on stderr; no API credentials or model dependencies are necessary for local scanning.
6. Do not put `cwd: ${PLUGIN_ROOT}` on an unbound generic server to infer the scan root: that targets the installed plugin rather than the authorized repository.

## Install command contracts

These commands are instructions for the user after extraction/build, not installation performed during this task. Use absolute paths.

```sh
# Universal local MCP fallback; bind target root at startup.
codex mcp add deepsec-agent -- node /ABS/agent-plugin/runtime/mcp.mjs --root /ABS/repository
claude mcp add --transport stdio deepsec-agent -- node /ABS/agent-plugin/runtime/mcp.mjs --root /ABS/repository
kimi mcp add --transport stdio deepsec-agent -- node /ABS/agent-plugin/runtime/mcp.mjs --root /ABS/repository

# Claude local plugin development; plugin server must be generated with bound root.
claude --plugin-dir /ABS/generated/claude-plugin
claude plugin validate /ABS/generated/claude-plugin

# Kimi native plugin, generated separately and with bound target root.
kimi plugin install /ABS/generated/kimi-plugin
kimi plugin info deepsec-agent

# Codex native marketplace, for a generated marketplace containing the plugin.
codex plugin marketplace add /ABS/generated/codex-marketplace
codex plugin add deepsec-agent@deepsec-local
```

Installed Codex `0.159.2` printed these exact marketplace/add/mcp option shapes. Its CLI has no documented direct `--plugin-dir` equivalent. Native plugin CLI availability differs by version, so the universal MCP command is the fallback.

## Unresolved

- Claude Code and Kimi executables are absent here; their native plugin loaders have not been run.
- Kimi labels its plugin system Beta; future schema or CLI behavior may change.
- Documentation URLs are live rather than immutable. Pinned repository files provide immutable implementation evidence where available.
- This review does not establish third-party license clearance or legal rights. No fetched source implementation is copied into the new adapter code.

## Refuted

- “Kimi only supports MCP and skills” is contradicted by its pinned native plugin documentation and implementation.

## Isolated Codex native verification

Codex CLI 0.159.2 successfully registered the generated local marketplace, installed deepsec-agent@deepsec-local and listed it as enabled with an isolated scratch CODEX_HOME under /workspace/work. No user/global settings or model conversation were used. This validates native marketplace/package recognition; model-session MCP discovery remains untested by this check. See CODEX-NATIVE-VERIFICATION.json for observed JSON output. Pinned marketplace.rs resolve_local_plugin_source_path resolves local source paths against marketplace_root_dir, not the directory containing marketplace.json.
