# Install and use plugins on your agent

Start from a local checkout of [Ultimate AI Plugins](https://github.com/andrewr303/ultimate-AI-plugins). Commands that point to the checkout assume you ran them from its root. The [catalog](../README.md#plugin-catalog) gives the starting skill and requirements for each package.

## Codex and ChatGPT desktop

Use the native Codex catalog from the CLI.

```sh
codex plugin marketplace add "$PWD"
codex plugin list --marketplace ultimate-ai-plugins --available
codex plugin add doc-atlas@ultimate-ai-plugins
```

Start a new project session. Select the installed plugin or ask for the `repo-docs` skill. If the installed CLI has marketplace registration but lacks `plugin add`, install from the Plugins Directory in the desktop app.

For ChatGPT desktop, open the checkout as a project in Work or Codex and select **Ultimate AI Plugins** from the Plugins Directory source picker. The app reads the project’s [catalog](../.agents/plugins/marketplace.json). Restart the app after adding a source or updating its catalog. A new session picks up installed skills. [OpenAI plugin packaging and local marketplaces](https://developers.openai.com/plugins/build/plugins)

### ChatGPT web and hosted workspaces

For an eligible ChatGPT account with skill uploading enabled, go to **Plugins → Skills → Create → Upload from your computer**. Choose a standalone `.skill` artifact for a self-contained workflow. For example, [Ultimate Prose Universal 5.2.0](../artifacts/ultimate-prose-universal/ultimate-prose-universal-5.2.0.skill) bundles its own instructions, references, and scripts. Use the web skill name `ultimate-prose`. [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)

Workspace owners can use ChatGPT’s workspace plugin import or publishing options when enabled. Account eligibility, app registration, tool permissions, and execution location are determined by the workspace. Workflows involving a local MCP server, native SDK, browser, or shell need those capabilities in the selected execution environment. [Plugins in ChatGPT](https://help.openai.com/en/articles/20001256-plugins-in-chatgpt)

## Claude Code

To try one package, run this from the checkout root.

```sh
claude --plugin-dir ./plugins/documentation/doc-atlas
```

In a Claude Code session, add the marketplace with the checkout’s absolute path and install the entry.

```text
/plugin marketplace add /absolute/path/to/ultimate-AI-plugins
/plugin install doc-atlas@ultimate-ai-plugins
```

Use `/doc-atlas:repo-docs` or ask for the workflow by name. The [catalog](../.claude-plugin/marketplace.json) uses source folders. The `.plugin` files in `dist/` are a separate distribution format for eligible Claude upload surfaces. [Claude Code plugins](https://code.claude.com/docs/en/discover-plugins)

## Kimi Code

Use the current Kimi Code CLI. Run these slash commands from an interactive Kimi session, substituting your checkout path.

```text
/plugins marketplace /absolute/path/to/ultimate-AI-plugins/kimi.marketplace.json
/plugins install /absolute/path/to/ultimate-AI-plugins/plugins/documentation/doc-atlas
/reload
```

The first command browses the [catalog](../kimi.marketplace.json). The second installs Doc Atlas directly. Use one install method per plugin. Check `/plugins info doc-atlas` for the installed skill, then ask for `repo-docs`. Kimi copies the package into its managed plugin directory. Reinstall it when you want source changes from the checkout. [Kimi Code plugin documentation](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html)

## OpenCode, Gemini CLI and other Agent Skills hosts

Run this from the plugin checkout. The target project must exist and Python 3.9 or later must be on the path.

```sh
python3 scripts/plugin_catalog.py register-skill doc-atlas --project /absolute/path/to/project
```

The command prints the new `.agents/skills/ucp-doc-atlas/SKILL.md` path. Start a new session in the target project and ask for `ucp-doc-atlas`. The generated skill points to the canonical workflow in the local plugin checkout, so sibling skills, scripts, and references stay available. Recreate the generated file if you move the checkout. If the skill is absent from your host’s list, ask the agent to read the generated `SKILL.md` by its printed absolute path and follow it. You can also point the agent directly at a plugin’s canonical entry from the catalog. [OpenCode skills](https://opencode.ai/docs/skills), [Gemini CLI skills](https://geminicli.com/docs/cli/skills/)

## Host capabilities

- **Skills and scripts.** Use the named starting skill. When its examples refer to a plugin root, resolve it from the installed skill’s file location and leave the target project as the working tree being acted on.
- **Commands, hooks, and agent roles.** Slash syntax and lifecycle events depend on the host. Use the underlying skill to perform a workflow when a command alias is absent. A role brief can guide a supported worker. Independent review still requires an independent reviewer.
- **Connected apps.** Issue Assistant carries GitHub and Linear app bindings for supported OpenAI environments. Other hosts can supply their own authorized tracker tools. Its local Python helper validates supplied records.
- **Local MCP.** DeepSec requires Node.js 22+ and an explicit absolute `DEEPSEC_WORKSPACE_ROOT` in the host’s environment, or a bound configuration. Use the [DeepSec host guide](../plugins/quality/deepsec-agent/docs/HOSTS.md) for setup. Optional browser and scanner integrations are described in their respective plugin READMEs.
