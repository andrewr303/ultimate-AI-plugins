# Validation record

Build environment: Linux x86_64, Node 24.19.0, npm 11.9.0, Codex CLI 0.159.2. Validation performed 2026-10-23.

- `npm test` in agent-plugin: 48 tests passed, no failures/skips. Covers source boundaries, worker limits, raw-secret removal, parser contracts, controlled subprocess deadlines/output limits, combined finding caps, baseline/CI behavior, JSON/Markdown/SARIF, real stdio MCP, and generated Codex/Claude/Kimi wrappers.
- Original uploaded matcher inline-example assertions: 1,848 passed, zero failed using an ephemeral assertion shim over the original example test file. This is not the full upstream Vitest suite.
- `npm run validate`: portable package and skill validation passed.
- Root plugin.json and mcp.json validated with downloaded official Agent Plugins schemas. Generated SARIF validated with the official SARIF schema. Authored YAML/frontmatter parsed successfully with PyYAML.
- `npm ci --ignore-scripts` and `npm run build`: bundled runtime rebuilt successfully from included source and pinned build-only dependencies.
- `npm audit --json`: no reported vulnerabilities in the plugin build dependency tree at the time of validation. The original monorepo dependency tree was not installed or audited by this check.
- Actual CLI example: vulnerable fixture yielded candidate findings; safe arithmetic fixture yielded zero; both finished within the selected coverage policy.
- Native Codex marketplace add, plugin add, and plugin list succeeded under an isolated scratch CODEX_HOME; proof in CODEX-NATIVE-VERIFICATION.json. No model session or account/global installation occurred.

Review findings resolved: external snapshot fd/inode checks and byte/time limits; source-config suppression; startup MCP root identity checks; worker CLI-flag isolation; preservation of incomplete coverage metadata; aggregate finding bounds; generated bundle licenses; Kimi partial results; CLI version output; doctor root scoping.

## Unresolved

Actual external Semgrep/Gitleaks/OSV/Bandit/Trivy binaries were absent. Adapter verification uses pinned upstream source contracts and controlled fixtures, not live tool execution. Native Claude Code and Kimi loaders were absent; generated copies and JSON-stdin wrappers were executed. A real Codex model conversation discovering/using MCP was not started; the MCP protocol itself was exercised by a subprocess client. Windows/macOS and the PowerShell wrapper were not run. The full original AI/cloud pipeline and upstream Vitest suite were not run.

Filesystem containment checks are not operating-system sandboxing or a race-proof isolation claim. External scanner network flags do not implement network isolation. Source technology gates are intentionally replaced by file-pattern selection and confidence metadata in this bridge.

## Refuted

No failing test or unresolved review issue is represented as a passed check.
