# Kimi Code 2.x

This package includes a native `kimi.plugin.json` alongside its portable, Claude Code and Codex manifests. Current Kimi Code reads this native manifest's `skills: "./skills/"` declaration and discovers the complete 26-skill collection. The source stays in one directory; no host export or generated bootstrap is needed.

The Python `kimi-cli` package is a legacy runtime with a different plugin format. Its `plugin.json`/`tools` conventions and `kimi plugin install` shell command are not the current Kimi Code contract. Use a current Kimi Code 2.x installation and inspect `kimi --version` and `kimi --help` before following these instructions.

## Install the plugin in current Kimi Code

Prerequisites: a current Kimi Code installation, this complete checkout on the same machine, and permission to install a per-user plugin. In a Kimi session, use the absolute path to this checkout's `plugins/ios-development-studio` directory:

```text
/plugins install /absolute/path/to/environment-dev/plugins/ios-development-studio
/plugins info ios-development-studio
/reload
```

Replace the absolute path with your real checkout location. `/plugins info` should identify the intended version and list the plugin's skills without manifest diagnostics. The plugin can also be inspected from the interactive `/plugins` manager.

Kimi copies local installations into `$KIMI_CODE_HOME/plugins/managed/<id>/`, normally beneath `~/.kimi-code`. Editing the original source after installation does not update that managed copy; reinstall deliberately after changing source. Installation is per-user and applies across projects. The scripts here do not install anything or modify Kimi settings automatically.

After installation and reload, invoke the router with:

```text
/skill:ios-development-studio:ios-development
```

Use the qualified plugin name for another specialist, for example:

```text
/skill:ios-development-studio:ios-concurrency
```

Current Kimi plugin skills use `<plugin-id>:<skill-name>` namespacing. A bare `/skill:ios-development` does not resolve to an installed plugin skill. The model can also select a specialist from its description. These workflows remain subject to the user's actual project, available tools and authorized scope.

## Load the skills without native installation

To use a direct skill directory for one session, run this from the repository root:

```bash
kimi --skills-dir "$PWD/plugins/ios-development-studio/skills"
```

The current CLI supports the repeatable `--skills-dir` flag. It overrides automatically discovered user/project skill roots, so this is an intentional session choice. Direct file skills use bare names such as `/skill:ios-development`; the plugin-qualified names above apply to native plugin installation.

The additive alternative is a top-level `extra_skill_dirs` entry in Kimi's existing `config.toml`:

```toml
extra_skill_dirs = ["/absolute/path/to/environment-dev/plugins/ios-development-studio/skills"]
```

Merge the real absolute path with existing configuration instead of replacing other values. Keep the whole plugin directory: copying only individual skill folders into a generic home skills directory can break sibling/shared links to docs, scripts and the operating contract. No package helper writes this configuration for you.

## Static validation

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 plugins/ios-development-studio/scripts/validate_kimi.py --json
```

The standard-library checker requires Python 3.10 or newer. It checks this package's skills-only Kimi profile: native manifest selection, identity/version/description synchronization, `./` path grammar and containment, complete directory-form discovery, metadata, shared support files and contained local Markdown references. It rejects legacy runtime fields such as `tools`, `inject` and `config_file` rather than silently claiming they work in current Kimi.

This is a package-specific check, not a validator for arbitrary Kimi MCP, hook or command plugins. The manifest intentionally declares none of those capabilities. The project discovery and routing helpers remain ordinary Python CLI programs; there are no bundled provider credentials, external servers, native tool wrappers or install hooks.

Static checks do not establish model invocation, account authentication, an iOS build or simulator behavior. Host discovery results, when executed, are recorded separately in the package's validation record.

## Isolated host checks

Current Kimi's supported data-root variable is `KIMI_CODE_HOME`, defaulting to `~/.kimi-code`. It relocates config, sessions, logs, credentials and managed plugins; Kimi-specific user skills live under that root too. Generic `~/.agents/skills` remains a shared source under the real OS home.

For an isolated smoke test, use a fresh work-directory `KIMI_CODE_HOME`, disable updates with `KIMI_CODE_NO_AUTO_UPDATE=1`, and disable telemetry with `KIMI_DISABLE_TELEMETRY=1`. Use explicit skill roots when inspecting direct discovery. No model/provider request or login is needed to validate package metadata and file discovery. Do not treat the legacy runtime's `KIMI_SHARE_DIR` as the current Kimi Code data-root switch.

## Official evidence

Current source was inspected at `MoonshotAI/kimi-code@8dabf4a10eaec7302344ba3060b7b3c69a5a76dc`:

- [Plugins](https://github.com/MoonshotAI/kimi-code/blob/8dabf4a10eaec7302344ba3060b7b3c69a5a76dc/docs/en/customization/plugins.md): native manifest locations, declared skill directories, installation/reload and qualified skill names.
- [Agent Skills](https://github.com/MoonshotAI/kimi-code/blob/8dabf4a10eaec7302344ba3060b7b3c69a5a76dc/docs/en/customization/skills.md): required directory-form metadata and current discovery roots.
- [Manifest parser](https://github.com/MoonshotAI/kimi-code/blob/8dabf4a10eaec7302344ba3060b7b3c69a5a76dc/packages/agent-core-v2/src/app/plugin/manifest.ts): `kimi.plugin.json` precedes `.kimi-plugin/plugin.json`, `./` paths remain inside the plugin, and legacy runtime fields produce diagnostics.
- [Plugin skill discovery](https://github.com/MoonshotAI/kimi-code/blob/8dabf4a10eaec7302344ba3060b7b3c69a5a76dc/packages/agent-core-v2/src/features/skill/workspace/pluginSkillSource.ts): enabled plugin skill roots enter the skill catalog.
- [Official native skill-directory example](https://github.com/MoonshotAI/kimi-code/blob/8dabf4a10eaec7302344ba3060b7b3c69a5a76dc/plugins/official/kimi-webbridge/kimi.plugin.json): `skills: "./skills/"` in an actual maintained package.
- [Environment variables](https://github.com/MoonshotAI/kimi-code/blob/8dabf4a10eaec7302344ba3060b7b3c69a5a76dc/docs/en/configuration/env-vars.md): `KIMI_CODE_HOME`, update control and telemetry control.
- [Migration guide](https://github.com/MoonshotAI/kimi-code/blob/8dabf4a10eaec7302344ba3060b7b3c69a5a76dc/docs/en/guides/migration.md): the Python legacy runtime is separate, and its plugins do not migrate automatically.
