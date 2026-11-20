# DeepSec Agent

Review repository source with a local scanner and turn its findings into evidence for defensive triage.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`deepsec-review`](skills/deepsec-review/SKILL.md). Try this prompt.

> Review the in-scope source for risky trust boundaries. Group candidate findings by affected component and cite the relevant lines and existing controls.

A local security plugin and scripting tool for **Codex, Claude Code, and Kimi Code**. It builds on the uploaded DeepSec app, preserves its broad matcher registry, and lets your current coding agent investigate candidates and implement requested fixes. The local engine needs **Node 22 or later**. Its built runtime requires no package installation, API key, model SDK, or paid background agent session.

## Local workflow

Run the CLI with Node.js 22 or later.

```sh
node bin/deepsec-agent.mjs doctor --root /absolute/path/to/repository
node bin/deepsec-agent.mjs scan --root /absolute/path/to/repository --out findings.json
node bin/deepsec-agent.mjs report --input findings.json --format markdown --out findings.md
node bin/deepsec-agent.mjs report --input findings.json --format sarif --out findings.sarif
node bin/deepsec-agent.mjs plan --input findings.json
```

Run those commands from this plugin directory, or use the absolute path to its entrypoint. **Findings are review candidates.** Pattern matches alone do not establish an exploitable vulnerability. All built-in candidates start at medium severity; the host agent should assess impact, reachability, existing controls, and evidence before confirming or fixing one.

## Connect your coding agent

The quickest shared path is a local MCP server bound to one repository. Replace both paths with absolute paths:

```sh
codex mcp add deepsec-agent -- node /ABS/deepsec-agent/bin/deepsec-agent.mjs serve --root /ABS/repository
claude mcp add --transport stdio deepsec-agent -- node /ABS/deepsec-agent/bin/deepsec-agent.mjs serve --root /ABS/repository
kimi mcp add --transport stdio deepsec-agent -- node /ABS/deepsec-agent/bin/deepsec-agent.mjs serve --root /ABS/repository
```

Native packages can be generated for each host without changing your settings:

```sh
node scripts/configure-host.mjs --host codex --root /ABS/repository --out /ABS/new-codex-marketplace
node scripts/configure-host.mjs --host claude --root /ABS/repository --out /ABS/new-claude-plugin
node scripts/configure-host.mjs --host kimi --root /ABS/repository --out /ABS/new-kimi-plugin
node scripts/configure-host.mjs --host mcp --root /ABS/repository --out /ABS/new-mcp-config
```

See [docs/HOSTS.md](docs/HOSTS.md) for installation and compatibility details. The generator refuses an existing output directory. Kimi uses a separate native manifest because its plugin format differs from the portable Codex manifest. The default portable/Claude MCP launchers require `DEEPSEC_WORKSPACE_ROOT`; generated packages bind the root explicitly. Nothing installs itself into a host or writes user settings during generation.

Ask your host agent: “Use DeepSec to review this repository, investigate the highest-priority candidates, and propose minimal fixes with regression checks.” The shared `skills/deepsec-review/SKILL.md` describes the workflow. MCP exposes only `deepsec_scan`, `deepsec_doctor`, `deepsec_rules`, and `deepsec_review_packet`; no shell or arbitrary execution endpoint is exposed.

## Optional complementary scanners

Separately installed scanners run only when explicitly selected in the CLI:

```sh
node bin/deepsec-agent.mjs scan --root /ABS/repository --engines deepsec,semgrep,gitleaks,bandit --out findings.json
node bin/deepsec-agent.mjs scan --root /ABS/repository --engines osv-scanner,trivy --allow-network --out dependencies.json
node bin/deepsec-agent.mjs import --engine gitleaks --input /ABS/native-gitleaks.json --root /ABS/repository --out imported.json
```

| Engine | Purpose | Behavior |
|---|---|---|
| DeepSec | Broad source/framework candidates | Built in; offline; no project code executed |
| Semgrep | Structural checks | Packaged original local rules; no registry rule downloads or metrics requested |
| Gitleaks | Secret detection | Directory mode, full redaction, raw secret/match fields discarded; git history excluded |
| Bandit | Python AST checks | Optional installed tool; its installed plugins are part of your trust boundary |
| OSV-Scanner | Dependency advisories | Explicit network opt-in; missing dependency sources stay visible |
| Trivy | Dependency and infrastructure checks | Explicit network opt-in for database/policy access |

External scanners receive a bounded temporary snapshot of regular files. Links and project scanner configuration are omitted. Source omission, output truncation, malformed reports, missing tools, and errors produce incomplete coverage. External binaries remain trusted local programs; this is **not an operating-system sandbox**. Network flags control selection and requested behavior, not network isolation. Their native versions can change output schemas; fixture parser tests are separate from live-engine validation. Dependency findings may be file-level and use line 1 as a placeholder.

## Scripting, baselines, and CI

```sh
node bin/deepsec-agent.mjs baseline --input findings.json --out baseline.json
node bin/deepsec-agent.mjs scan --root /ABS/repository --baseline baseline.json --fail-on medium --out current.json
node bin/deepsec-agent.mjs scan --root /ABS/repository --files src/server.ts,src/auth.ts
node bin/deepsec-agent.mjs workflow --config examples/workflow.json
sh scripts/audit.sh /ABS/repository
```

PowerShell: `./scripts/audit.ps1 -Root C:\source\project`. Its execution was not tested in the Linux build environment. Workflow configuration is declarative JSON: it selects engines, bounds and report formats; it never evaluates scripting text. Paths in a workflow resolve relative to its configuration file. Explicit file lists currently support only the DeepSec engine.

Exit codes: **0** complete scan, **1** a new finding meets `--fail-on`, **2** invalid input, failure, or incomplete coverage. Baselines suppress only matching fingerprints, and never hide engine failures. Built-in evidence fingerprints survive line shifts when the same matching line remains unchanged; they are not semantic program identities. Ignore a report's existing/new state only after reviewing its baseline provenance.

JavaScript scripting API:

```js
import { audit, renderReport } from './runtime/index.mjs';
const report = await audit('/absolute/repository', { engines: ['deepsec'], maxFiles: 500 });
console.log(renderReport(report, 'markdown'));
```

## Coverage and execution bounds

The uploaded registry contains **198 registered rules**. The default selects **115 non-noisy rules**; `--include-noisy` selects all registered rules. The bridge intentionally uses file patterns without upstream technology gates, and lowers gated-candidate confidence. It does not claim identical findings to the original full DeepSec processing pipeline.

Hard ceilings can be lowered: 2,000 files, 256 KiB per source file, 32 MiB of source bytes, 1,000 candidates, and a 30-second built-in worker deadline. MCP further caps returned candidates at 200. Built-in scans exclude dependency/build/state directories, credential/key/environment files, and unsupported types. Use the explicit Gitleaks adapter for credential scanning. A “complete” result means the selected engine finished within that policy; it never means a repository is free of vulnerabilities. Excluded policy counts and actual skips are included in coverage.

Reports omit raw source snippets, full filesystem roots, scanner stdout/stderr, and raw secret fields. Common credential patterns are defensively redacted; arbitrary prose can still contain sensitive information. Treat exported reports as sensitive. CLI-created report files use restrictive permissions where the platform supports them. Linux includes opened-file descriptor containment checks; other platforms use available realpath, symlink and inode checks. Concurrent filesystem mutation and native platform behavior are not an OS isolation guarantee.

## Verify or rebuild

```sh
npm test
npm run validate
# Optional rebuild of bundled registry and glob library:
npm ci --ignore-scripts
npm run build
```

The release already contains its built runtime. Build-only packages are pinned in `package-lock.json`; runtime modules use Node built-ins and bundled code. `vendor/deepsec-scanner` contains the uploaded matcher sources for rebuilding. Existing upstream DeepSec AI/cloud capabilities are preserved in the separate full-source distribution; they retain their original setup and cost behavior and are not started by this plugin.

`research/` records repository comparisons, pinned source provenance, host evidence, unresolved claims, and validation results. This is an original integration, not an official Vercel, OpenAI, Anthropic, or Moonshot product. See `LICENSE`, `NOTICE`, and `licenses/`.
