# Codex, Claude Code, and Kimi Code

Keep the complete plugin tree when moving or installing it. The shared operating contract, cross-skill links, root scripts, documentation and notices are part of the package. Copying isolated SKILL.md files loses those dependencies. Normal workspace trust and tool permissions still apply.

## Codex and portable Agent Plugins

Root `plugin.json` keeps the Agent Plugins schema. The synchronized `.codex-plugin/plugin.json` compatibility overlay preserves the same identity, presentation, version and skill path. Select the installed `ios-development` router or a focused specialist. This source change does not publish or replace the separately saved private account release.

## Claude Code

The repository provides a marketplace outside the plugin package. With access to `andrewr303/environment-dev`, run in Claude Code:

```text
/plugin install ios-development-studio --marketplace andrewr303/environment-dev
```

For a local checkout, replace the absolute paths below. These shell commands register the local repository and install its plugin:

```bash
claude plugin marketplace add /absolute/path/to/environment-dev
claude plugin install ios-development-studio@environment-dev
```

For a single session without marketplace registration:

```bash
claude plugin validate /absolute/path/to/environment-dev/plugins/ios-development-studio
claude --plugin-dir /absolute/path/to/environment-dev/plugins/ios-development-studio
```

Use `/ios-development-studio:ios-development` or the matching specialist. `.claude-plugin/plugin.json` is a native metadata projection; it does not inherit OpenAI-only presentation fields. Claude discovers the conventional `skills/<name>/SKILL.md` directories. Optional `agents/openai.yaml` files are separate Codex metadata.

Commands in guides that say “from the plugin root” use the installed plugin directory, not the app's working directory. An agent should resolve the loaded skill's actual path and run the helper through its absolute path. The helpers find their own supporting files relative to `__file__` and receive the app path explicitly. Never replace the user's current project with the plugin directory.

See [Claude format evidence](compatibility/claude.md) and [verification results](validation-results.json). Native manifest validation does not exercise an iOS app or a model conversation.

## Kimi Code: current native plugin

The same complete package contains `kimi.plugin.json`, with its skill directory explicitly declared. In Kimi Code 2.x, use the client commands:

```text
/plugins install /absolute/path/to/environment-dev/plugins/ios-development-studio
/plugins info ios-development-studio
/reload
```

The success signal is an installed/enabled plugin with 26 discovered skills. Invoke the router as `/skill:ios-development-studio:ios-development` or select the relevant namespaced specialist. No model provider, native tool scripts or backend service is bundled.

The current native Kimi manifest has a distinct filename, so it coexists with portable, Codex and Claude metadata. There is no separate export to manage and no root router shim. Kimi's deprecated Python CLI used a different manifest and discovery contract; its `kimi plugin install` shell command is not the current client's installation path.

## Kimi Code: explicit skill directory

From the app's working directory, use the complete source package:

```bash
kimi --skills-dir /absolute/path/to/environment-dev/plugins/ios-development-studio/skills
```

This explicitly chooses the skills directory and replaces Kimi's auto-discovered user/project roots for that session. The flag can be repeated. The package's 26 specialists remain separate discoverable skills with all shared resources present. It does not install a plugin, change app dependencies or configure an external model provider. For additive configuration, use the current client's `extra_skill_dirs`, as explained in [the Kimi contract](compatibility/kimi.md).

Check the native Kimi contract locally with `python3 scripts/validate_kimi.py --json` from the plugin root. The general portable validator also checks the synchronized Kimi metadata. No Kimi-native tools are declared: the Python helpers remain explicit local commands rather than incorrectly advertised JSON-stdin tool implementations.

## Verification boundaries

Unit tests exercise synchronized host metadata, discovery fixtures, export completeness, link preservation, unsafe destinations and source preservation. Available native CLIs are checked with isolated task-local state, no model prompt and no provider credentials. Exact observed client versions/results are in [validation-results.json](validation-results.json). Xcode, simulator/device execution, model-invocation behavior and App Store authentication remain separate checks in the target environment.
