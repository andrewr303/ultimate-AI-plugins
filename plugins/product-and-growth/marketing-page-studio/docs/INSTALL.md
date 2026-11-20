# Install the packaged plugin

Unpack this archive into its own directory. Install Python requirements and run the doctor as shown in the root README. The package includes both canonical portable plugin metadata and a minimal Claude compatibility manifest; no MCP process or account connection is required.

## Codex CLI

The official manifest schema and the installed Codex CLI 0.159.2 command surface were checked. Use the included helper to create a local repository marketplace outside this plugin:

```sh
python scripts/register_codex.py --repo ../studio-local
codex plugin marketplace add ../studio-local --json
codex plugin add PLUGIN_NAME@studio-local --json
codex plugin list --json
```

Replace `PLUGIN_NAME` with `marketing-page-studio`. The helper copies only this plugin into the marketplace, preserves existing entries and rejects an existing destination/conflicting identity. You can register the other plugin with its own helper and the same marketplace, but either operates independently. Do not put a marketplace wrapper inside the one-plugin ZIP.

For a clean installation test without changing user state, set `CODEX_HOME` to an empty task-local directory before running the CLI. This also isolates authentication, so package registration can succeed while an authenticated model session remains unavailable. See the delivery validation report for exact executed outcomes.

Start a new Codex session after installing and request this plugin's entry workflow. CLI package discovery does not establish desktop installation or skill routing behavior. The desktop app was not exercised here.

## Claude Code

The `.claude-plugin/plugin.json` and root `skills/` layout were verified against Anthropic's official plugin examples and manifest reference. The Claude CLI is unavailable in this environment, so installation and skill invocation remain untested. Register the extracted directory in a Claude plugin marketplace and install with Claude's `/plugin` interface, using the current official installation documentation for your version.

## Other compatible agents

Load `skills/marketing-page-studio/SKILL.md` from this installed package and follow its precise routing. The remaining skills and references are local resources, loaded on demand. The helper scripts resolve their own plugin root and can run from an unrelated working directory. Respect the host's execution policy.

## Verification and removal

Run `python scripts/studio.py package-check` after extraction and `python scripts/studio.py doctor --launch` after installing dependencies. For a website use the included browser verifier; for video reproduce a preview from an example job. Never treat static metadata parsing as a render or a visual-quality pass.

Remove installed entries through the host's supported plugin interface. No installer here changes user-global configuration or authentication automatically. Detailed source-backed packaging research is in [host packaging](../contracts/docs/host-packaging.md).
