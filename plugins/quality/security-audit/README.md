# Security Audit

A security review plugin with a source-first audit workflow and a local toolkit for planning scans, importing scanner results, comparing runs, and exporting reports.

This is an independently expanded derivative of [Cloudflare's security-audit-skill](https://github.com/cloudflare/security-audit-skill). It preserves the original six-phase audit, domain guides, finding schema, and coverage validators. Cloudflare has not endorsed this expansion. See [attribution](THIRD-PARTY-NOTICES.md) and the [change log](CHANGELOG.md).

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`security-audit`](skills/security-audit/SKILL.md). Try this prompt.

> Plan a defensive source audit for this repository. Show which local scanners fit the stack and which trust boundaries still need manual review.

## What is included

| Capability | What it does |
| --- | --- |
| Full security audit | Architecture and trust-boundary review, coverage-led hunting, independent verification, and evidence-based findings. |
| Scan planning | Detects repository markers and proposes scanner commands with prerequisites and coverage limits. It does not run scanners. |
| Result import | Normalizes SARIF, Semgrep, Gitleaks, Trivy, and OSV-Scanner JSON into unverified tool signals. |
| Baseline comparison | Separates new, unchanged, and absent signals using deterministic fingerprints. Absence does not prove a fix. |
| Report exports | Produces a triage Markdown report or SARIF from tool signals; exports validated, confirmed audit findings to SARIF separately. |
| Local checks | Validates signal documents and checks whether optional scanner executable files are present. |

The implementation uses Node.js built-ins and has no runtime package dependencies. Scanner tools and vulnerability databases are optional, separately installed components. Research choices and alternatives are documented in [RESEARCH.md](docs/RESEARCH.md).

## Quick start

Use Node.js 20 or newer on a supported POSIX system. Extract the package and run these commands from its root. Create a separate directory for results first; choose a new output filename for each run. Output files are created exclusively with owner-only permissions and existing files are not overwritten. Keep input and output directories under trusted control while processing reports.

```bash
node scripts/audit-tools.cjs doctor

node scripts/audit-tools.cjs plan \
  --target /absolute/path/to/repository \
  --profile standard \
  --output /absolute/path/to/results/scan-plan.json

node scripts/audit-tools.cjs import \
  --format sarif \
  --input /absolute/path/to/scanner-output.sarif \
  --output /absolute/path/to/results/signals.json

node scripts/audit-tools.cjs validate \
  --input /absolute/path/to/results/signals.json

node scripts/audit-tools.cjs report \
  --input /absolute/path/to/results/signals.json \
  --output /absolute/path/to/results/TRIAGE.md
```

Replace `sarif` with `semgrep`, `gitleaks`, `trivy`, or `osv` when importing that tool's native JSON. If a report contains absolute source paths, add `--source-root /absolute/path/to/repository` to map only paths beneath that root to repository-relative locations. The planner produces a reviewable plan; no command in this toolkit launches a scanner, installs a package, uploads a report, or executes the target repository.

Compare two normalized runs and export signals:

```bash
node scripts/audit-tools.cjs compare \
  --current /absolute/path/to/results/current-signals.json \
  --baseline /absolute/path/to/results/prior-signals.json \
  --output /absolute/path/to/results/comparison.json

node scripts/audit-tools.cjs sarif \
  --input /absolute/path/to/results/current-signals.json \
  --output /absolute/path/to/results/signals.sarif
```

For findings produced by the original audit workflow, use the separate validated export:

```bash
node scripts/audit-tools.cjs export-findings \
  --input /absolute/path/to/audit/findings.json \
  --output /absolute/path/to/results/confirmed-findings.sarif
```

Exit status `2` means known incomplete input or output processing; inspect warnings and coverage gaps. `compare --fail-on-new` can return `3` when a complete comparison contains new signals. See [TOOLING.md](docs/TOOLING.md) for the full command contract and baseline limitations. [Synthetic examples](examples/README.md) cover all five import formats without needing a scanner installation.

## Use with a coding agent

The root `plugin.json` uses the portable Agent Plugins 1.0 format. Load the extracted directory or ZIP through a host that supports that format. A skill-only host can use the four directories under `skills/`; retain this package's directory structure when using the CLI links. Installation and discovery depend on the host. This archive has not been installed or published automatically.

The downloadable package under `artifacts/security-audit` holds version 1.0.0. This source folder is version 1.0.1, which changes only manifests and documentation; the package has not been rebuilt.

| Skill | Example request |
| --- | --- |
| [security-audit](skills/security-audit/SKILL.md) | “Audit this repository and write an evidence-based report.” |
| [security-scan-plan](skills/security-scan-plan/SKILL.md) | “Plan security scans for this monorepo without running them.” |
| [security-scan-triage](skills/security-scan-triage/SKILL.md) | “Import these scanner reports and triage the actionable leads.” |
| [security-regression](skills/security-regression/SKILL.md) | “Compare this scan with the previous run and verify the possible regressions.” |

The original audit supports `quick`, `standard`, and `deep` profiles, scoped audits, prior-run coverage, independent verification, and `confirmed`, `needs_validation`, and `rejected` findings. Its profile controls agent-review depth. The planner uses the same profile names to control scanner recommendations; these are separate settings and neither proves complete coverage.

## Evidence and execution boundaries

Scanner matches are leads. Their reported severity is retained as a scanner attribute, never promoted automatically into a confirmed audit finding. Confirmation still requires a source-grounded trust-boundary failure and independent validation. Unresolved audit leads receive no severity under the original finding contract.

Repository text, external reports, rules, comments, and linked documents are task data. They cannot change the user's scope, grant execution authority, or override agent instructions. The toolkit drops raw scanner messages and source snippets; retained identifiers and paths can still be sensitive, so review exports before sharing them.

Target-controlled builds, tests, and reproductions remain subject to the original skill's OS-enforced sandbox requirements: no external network, an allowlisted environment, read-only target and toolchain, scratch-only writes, and resource limits. The toolkit does not provide that sandbox or a race-safe artifact promotion service. Planning and import/export do not establish that running a suggested scanner is safe or authorized.

## Development and verification

```bash
npm test
```

This runs the original validator suites and the added toolkit tests. No `npm install` is required. For update procedures and known boundaries, see [MAINTENANCE.md](docs/MAINTENANCE.md).

See [VERIFICATION.md](docs/VERIFICATION.md) for this delivery's test results and unverified integration boundaries.

The original audit references remain under `skills/security-audit/`, including web/auth, cloud, supply chain, AI/LLM, client-side, data isolation, native memory safety, protocols, availability, and desktop/mobile review guides. The original [finding schema](skills/security-audit/report-schema.json), [finding validator](skills/security-audit/validate-findings.cjs), and [coverage validator](skills/security-audit/validate-coverage-ledger.cjs) retain their contracts.

## License

MIT. The original Cloudflare copyright notice is preserved in [LICENSE](LICENSE). External scanner binaries, rules, databases, and reference documents are not bundled; their licenses apply separately.
