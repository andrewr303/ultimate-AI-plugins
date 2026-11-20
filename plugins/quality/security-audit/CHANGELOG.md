# Change log

## 1.0.1 - 2026-11-10

- Added `.claude-plugin/plugin.json` so Claude Code reads the plugin manifest from its standard location; it agrees with the root `plugin.json`.
- Added author information to both manifests.
- README states that the downloadable package in `artifacts/security-audit` holds version 1.0.0, not this source version.
- No change to scripts, skills, or tests; `npm test` still passes 124 tests.

## 1.0.0 — expanded plugin package

The supplied archive was a standalone security-audit skill without a plugin version. This is the first version of the expanded portable plugin, not an upstream Cloudflare release.

### Added

- Portable plugin manifest and three focused skills for scan planning, scanner triage, and security regression review.
- A Node.js toolkit with no runtime dependencies: bounded repository discovery, scanner planning, normalized report imports, signal validation, baseline comparison, Markdown reports, and SARIF exports.
- Native report adapters for Semgrep, Gitleaks, Trivy, and OSV-Scanner, plus generic SARIF input.
- Separate SARIF export for confirmed findings that pass the original findings validator.
- GitHub research notes, tool selection rationale, usage documentation, maintenance guidance, and regression tests.

### Preserved

- Original six-phase audit, domain-specific reference guides, source evidence requirements, and independent verification.
- Original findings schema, coverage contract, validators, and their tests.
- Original MIT license and copyright notice.

### Boundaries

- The toolkit does not execute scanners, install dependencies, provision a sandbox, or publish results.
- Imported tool signals remain unverified. Baseline disappearance is not evidence of remediation.
- Runtime integrations require the user's separately installed scanner versions and appropriate local rules or databases. Planner recipes must be checked against those versions.
