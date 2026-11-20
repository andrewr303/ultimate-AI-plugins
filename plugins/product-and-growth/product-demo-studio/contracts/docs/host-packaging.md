# Host packaging evidence

Documentation and tooling were checked on October 22, 2026 (America/Denver). Source retrieval and parser checks establish packaging support; they do not establish that an unexecuted model session followed the skills correctly. Consult the delivered validation report for actual installation and host-session results.

## Codex

The installed CLI reports `codex-cli 0.159.2`. Its help exposes `codex plugin marketplace add`, `codex plugin list`, and `codex plugin add NAME@MARKETPLACE --json`. The [official Build plugins documentation](https://developers.openai.com/plugins/build/plugins) was retrieved successfully and describes the portable layout as canonical:

```text
plugin-root/
  plugin.json
  skills/entry-skill/SKILL.md
  scripts/
  contracts/
  references/
  examples/
```

Root `plugin.json` declares `$schema` exactly `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`, then the name, version and optional supported metadata. Portable skill discovery uses the root `skills/` directory. OpenAI metadata belongs under `extensions.com.openai`. An existing `.codex-plugin/plugin.json` is a compatibility fallback; the portable manifest does not need it. No MCP server is required for a skills-and-scripts plugin.

The [official Agent Plugins schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) was retrieved successfully and is bundled for local validation. Portable manifests do not accept arbitrary top-level fields such as `skills`, `tools`, or `interface`.

A Codex repo marketplace is a separate authoring/distribution wrapper, outside the one-plugin archive. The bundled `scripts/register_codex.py --repo REPO` helper copies its own plugin to the repo and creates or merges this catalog without installing anything or writing user-home state. It preserves existing entries and refuses conflicting names or destinations. `--dry-run` previews the action.

For manual setup, extract a plugin to `REPO/plugins/marketing-page-studio`, then add or merge this entry in `REPO/.agents/plugins/marketplace.json`:

```json
{
  "name": "studio-local",
  "plugins": [{
    "name": "marketing-page-studio",
    "source": {"source": "local", "path": "./plugins/marketing-page-studio"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Productivity"
  }]
}
```

The `source.path` resolves from `REPO`, not from `.agents/plugins`. Add the second plugin as another entry only when wanted. From a terminal, the installed CLI supports:

```text
codex plugin marketplace add REPO --json
codex plugin list --json
codex plugin add marketing-page-studio@studio-local --json
```

Start a new Codex session after installation and invoke the plugin's entry skill. In the desktop app, restart, choose the repo source in the Plugins Directory, and install there. Desktop UI behavior requires an actual desktop test; CLI installation does not prove it. Preserve existing marketplace entries rather than overwriting them.

## Claude Code

Claude Code is not installed in this execution environment. Direct requests to the current Claude documentation pages returned HTTP 403. Official source examples were nevertheless retrieved from Anthropic's own `claude-code` repository:

- [Official plugin README and layout](https://github.com/anthropics/claude-code/blob/main/plugins/README.md).
- [Official code-review plugin manifest](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/.claude-plugin/plugin.json).
- [Official plugin structure authoring skill](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/plugin-structure/SKILL.md).
- [Official manifest reference](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/plugin-structure/references/manifest-reference.md).

These examples confirm `.claude-plugin/plugin.json` with name, description, version and author, and root-level `skills/` alongside optional commands, hooks, agents and MCP configuration. Skills are not nested inside `.claude-plugin`. Runtime resources must resolve from the installed plugin, using the plugin root rather than the development checkout.

The package includes a minimal manifest in that format. For distribution, register a Claude plugin marketplace referencing the extracted directory, then use Claude's `/plugin` interface as described in the [official repository installation section](https://github.com/anthropics/claude-code/tree/main/plugins#installation). The exact installed version's local-loader flags and CLI skill execution remain untested here. Do not describe a manifest parser check as a successful Claude installation.

## Other agents and operating systems

The `skills/<name>/SKILL.md` files use standard YAML `name` and `description` frontmatter. An agent that supports portable skills can load the entry and resolve its supporting files from the package, subject to its own execution policy. No arbitrary host-specific browser tool names are required: scripts call local Python/Playwright.

Python and forward-slash paths are portable, but the executed integration tests were on Linux. Windows 11/PowerShell and macOS require their own dependency and browser-launch tests before claiming verified runtime support. Use `python` or the local Python launcher, install the documented dependencies, and run the plugin's doctor command first. None of the local production paths inherently requires WSL; a third-party adapter may have its own constraints.
