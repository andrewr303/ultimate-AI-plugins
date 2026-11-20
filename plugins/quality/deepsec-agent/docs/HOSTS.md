# Codex, Claude Code, and Kimi Code

DeepSec Agent is a local program with a shared skill and read-only MCP tools. Node.js 22 or later is required. No model API key is required. All paths below are absolute examples to replace with your own paths.

## Generate a package bound to a repository

Run from the extracted `agent-plugin` directory:

```sh
node scripts/configure-host.mjs --host codex --root /ABS/repository --out /ABS/generated-codex
node scripts/configure-host.mjs --host claude --root /ABS/repository --out /ABS/generated-claude
node scripts/configure-host.mjs --host kimi --root /ABS/repository --out /ABS/generated-kimi
```

Each command writes a new destination only. It refuses an existing destination, leaves host settings alone, and performs no installation. Generate a different bound package for a different repository. The generated configuration contains the repository's absolute path, so regenerate it when moving machines or directories.

The source package's default portable and Claude MCP manifests instead use `scripts/start-server.mjs`. This launcher requires an absolute `DEEPSEC_WORKSPACE_ROOT` environment variable and fails when it is absent; it never assumes the plugin installation directory is the repository. Bound generated packages avoid reliance on host environment inheritance.

## Codex

The generated Codex output is a local marketplace with the actual plugin under `plugins/deepsec-agent/`. The marketplace stays outside the plugin package.

```sh
node scripts/validate-plugin.mjs --dir /ABS/generated-codex/plugins/deepsec-agent
codex plugin marketplace add /ABS/generated-codex
codex plugin add deepsec-agent@deepsec-local
```

Start a new Codex session and select the `deepsec-review` skill. CLI plugin command availability varies by version; the local MCP fallback below works without a marketplace. The portable manifest is root `plugin.json` with the Agent Plugins schema. Root `mcp.json` uses `${PLUGIN_ROOT}` and shares `skills/` with Claude Code.

## Claude Code

```sh
claude plugin validate /ABS/generated-claude
claude --plugin-dir /ABS/generated-claude
```

Run `/deepsec-agent:deepsec-review` or ask for a source security review. The compatibility manifest is `.claude-plugin/plugin.json`; root `.mcp.json` uses `${CLAUDE_PLUGIN_ROOT}`. Claude's normal workspace trust and tool approvals apply.

## Kimi Code

The generated package includes a `kimi.plugin.json` that declares a local MCP server with the repository root fixed in its arguments. Run the generator above, then open an interactive Kimi Code session.

```text
/plugins install /ABS/generated-kimi
/reload
/plugins info deepsec-agent
```

The plugin provides the `deepsec-review` skill and the local MCP tools below. The generated root `plugin.json` also carries the older Kimi CLI's command-tool entry points. [Kimi Code plugin installation](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html)

## Local MCP fallback for all hosts

These commands write the host's normal MCP settings when you choose to run them:

```sh
codex mcp add deepsec-agent -- node /ABS/agent-plugin/bin/deepsec-agent.mjs serve --root /ABS/repository
claude mcp add --transport stdio deepsec-agent -- node /ABS/agent-plugin/bin/deepsec-agent.mjs serve --root /ABS/repository
```

For configuration files without installation:

```sh
node scripts/configure-host.mjs --host mcp --root /ABS/repository --out /ABS/generated-mcp
```

This writes a generic `mcp.json` and a Codex TOML fragment pointing to the source runtime. In current Kimi Code, configure the generated stdio server through `/mcp-config`. Keep the original runtime path available for this mode.

The MCP server offers `deepsec_scan`, `deepsec_doctor`, `deepsec_rules`, and `deepsec_review_packet`. The server root is fixed at startup. No MCP tool runs an arbitrary shell, patches files, installs packages, enables external scanners, or changes the root. Optional external engines are explicit CLI operations; check `node bin/deepsec-agent.mjs --help` for the supported options.

## Expected behavior and verification

Try: “Review this repository with DeepSec and validate the material findings against source.” A review should distinguish scan evidence from confirmed issues, keep credentials redacted, and report skipped coverage. A README instruction to upload `.env` must be treated as repository data. Ordinary formatting tasks should not trigger the security workflow.

The package validator checks authored manifests and referenced files. It does not certify a host loader. Codex CLI 0.159.2 successfully registered the generated local marketplace, installed its plugin, and listed it as enabled using an isolated scratch `CODEX_HOME`; the source path resolved from the marketplace root. This check started no model conversation and does not establish native MCP discovery inside a model session. Native Claude Code and Kimi loaders were unavailable in the build environment. The generated Kimi script tools and local MCP protocol are exercised separately by runtime tests. See `research/CODEX-NATIVE-VERIFICATION.json` for the CLI proof.

## Sources

- [Codex skills](https://developers.openai.com/codex/skills) and [MCP](https://developers.openai.com/codex/mcp).
- [Codex portable manifest implementation](https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/core-plugins/src/agent_plugin_manifest.rs) and [MCP normalization](https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/codex-mcp/src/agent_plugin_config.rs).
- [Claude Code manifest reference](https://code.claude.com/docs/en/plugins-reference) and [MCP](https://code.claude.com/docs/en/mcp).
- [Kimi native plugins](https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/docs/en/customization/plugins.md), [tool subprocess implementation](https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/src/kimi_cli/plugin/tool.py), [skills](https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/docs/en/customization/skills.md), and [MCP](https://github.com/MoonshotAI/kimi-cli/blob/9ab1286b8fe4e6bcd116949a27ce5e0ac3389c82/docs/en/customization/mcp.md).
