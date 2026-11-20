# Host setup for iOS Backend Studio

Keep the full package tree. Root `plugin.json` uses the portable Agent Plugins schema; `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json` and `kimi.plugin.json` contain synchronized host metadata. The Kimi manifest targets current Kimi Code 2.x rather than the deprecated Python CLI contract.

## Claude Code

From a local repository checkout:

```bash
claude plugin marketplace add /absolute/path/to/environment-dev
claude plugin install ios-backend-studio@environment-dev
claude plugin validate /absolute/path/to/environment-dev/plugins/ios-backend-studio
```

For a temporary session use `claude --plugin-dir /absolute/path/to/environment-dev/plugins/ios-backend-studio`. Invoke `/ios-backend-studio:ios-backend-studio` or a matching specialist. With access to the private repository, the client also supports `/plugin install ios-backend-studio --marketplace andrewr303/environment-dev`.

## Kimi Code

Inside current Kimi Code:

```text
/plugins install /absolute/path/to/environment-dev/plugins/ios-backend-studio
/plugins info ios-backend-studio
/reload
```

Invoke `/skill:ios-backend-studio:ios-backend-studio` or a namespaced specialist. The native manifest explicitly points at `./skills/`, exposing all 21 skills. Alternatively launch `kimi --skills-dir /absolute/path/to/environment-dev/plugins/ios-backend-studio/skills`; that flag replaces auto-discovered user/project roots and may be repeated.

## Helpers and state

Resolve helper paths from the loaded plugin root and pass the actual app/service path explicitly. Do not assume the current working directory is the plugin directory or copy isolated SKILL.md files without the shared references. Python helpers locate their own packaged support files relative to their script path.

Installation does not configure a model, cloud provider, credentials, Apple account or MCP server. Normal workspace trust and tool permissions apply. Do not carry host state, installed client binaries or authentication files into the plugin ZIP. Root Node/Swift/Xcode references are optional workflows, not a list of tools guaranteed available.

## Evidence

[Validation results](validation-results.json) and [native host checks](native-host-verification.json) record the actual verified scope. Native installation/discovery is separate from a model conversation, device test or authenticated external action. Current client formats were verified against Claude Code 2.1.310 and Kimi Code 2.3.3 during this task; use installed help if their interfaces change.
