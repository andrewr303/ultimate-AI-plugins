# Research behind the expansion

Researched October 30, 2026. This shortlist is selected for the uploaded Cloudflare security-audit skill: it adds practical scanner interoperability and coverage to an existing evidence-first audit workflow. It is not a universal ranking or a benchmark of detection quality.

## Selection method

GitHub and web discovery were followed by inspection of the projects' own repository metadata, READMEs, licenses, and command/output documentation. Selection considered complementary coverage, maintained source, structured output, local operation, clear licensing, and integration cost. Stars were not a selection score. All 14 repositories below were unarchived when checked; maintenance timestamps and exact source links are recorded in [research-sources.json](research-sources.json).

The expansion keeps the original MIT-licensed Cloudflare workflow and validators. Scanner observations enter as **unverified signals**: a tool match is not enough to establish reachability, exploitability, or a verified audit finding. The current implemented commands and adapters are documented in [TOOLING.md](TOOLING.md); the broader shortlist below also includes reference-only opportunities.

## First-choice scanner companions

| Repository | Why it fits | Interoperability and limits | License checked |
| --- | --- | --- | --- |
| [Semgrep CE](https://github.com/semgrep/semgrep) | Configurable static analysis across many languages; useful for generating focused hypotheses and variant searches. | Native JSON/SARIF. Use trusted local rules. CE's analysis scope is narrower than the commercial engine; do not infer cross-file reachability from a match. | [LGPL-2.1 engine](https://github.com/semgrep/semgrep/blob/develop/LICENSE). Rules have separate terms. |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Dedicated secret detection in files and Git history, with redaction and baseline support. | JSON/SARIF. A working-directory scan does not inspect historical commits. Omit secret values and source snippets from normalized reports. | [MIT](https://github.com/gitleaks/gitleaks/blob/master/LICENSE). |
| [OSV-Scanner](https://github.com/google/osv-scanner) | Dependency/advisory matching from supported source artifacts, lockfiles and SBOMs. | JSON/SARIF. Preserve package identity, advisory aliases and unknown severity. Vulnerable version presence alone does not establish application reachability. | [Apache-2.0](https://github.com/google/osv-scanner/blob/main/LICENSE). |
| [Trivy](https://github.com/aquasecurity/trivy) | Broad filesystem coverage across dependency vulnerabilities, IaC misconfiguration and secrets. | Native JSON/SARIF. Explicit scanner selection matters: misconfiguration scanning is not part of the documented default filesystem scanner set. | [Apache-2.0](https://github.com/aquasecurity/trivy/blob/main/LICENSE). |
| [zizmor](https://github.com/zizmorcore/zizmor) | Specialized CI/CD checks for injection, excessive permissions and dangerous workflow patterns. | Prefer SARIF for the generic import path; its JSON v1 uses zero-based rows. Offline mode skips checks that require GitHub access. | [MIT](https://github.com/zizmorcore/zizmor/blob/main/LICENSE). |
| [Syft](https://github.com/anchore/syft) | Captures dependency inventory as a reusable artifact instead of losing package context after a scan. | CycloneDX, SPDX and Syft JSON. An SBOM is an inventory, not a vulnerability report; preserve it separately. | [Apache-2.0](https://github.com/anchore/syft/blob/main/LICENSE). |

## Complementary projects and reference opportunities

| Repository | Useful expansion | Boundary |
| --- | --- | --- |
| [Grype](https://github.com/anchore/grype) | Scan existing SBOMs, filesystems and images; its documented output includes vulnerability prioritization context and VEX support. | Optional follow-on to Syft. No native Grype JSON adapter is claimed by this package. [Apache-2.0](https://github.com/anchore/grype/blob/main/LICENSE). |
| [Checkov](https://github.com/bridgecrewio/checkov) | Deeper IaC graph/policy review for Terraform, Kubernetes, CloudFormation and other formats. | Optional alternative/complement to Trivy. JSON and SARIF are documented, but this package does not claim a native Checkov JSON adapter. [Apache-2.0](https://github.com/bridgecrewio/checkov/blob/main/LICENSE). |
| [actionlint](https://github.com/rhysd/actionlint) | Validate workflow syntax, expressions, action inputs and reusable workflows; complements security-focused CI analysis. | A valid workflow can still be insecure. It can invoke installed ShellCheck/pyflakes integrations. [MIT](https://github.com/rhysd/actionlint/blob/main/LICENSE.txt). |
| [OpenSSF Scorecard](https://github.com/ossf/scorecard) | Supply-chain posture evidence such as token permissions and repository security practices. | Optional repository-level review; some checks need remote access. Scores are not proof of code security. [Apache-2.0](https://github.com/ossf/scorecard/blob/main/LICENSE); API data has separate terms documented upstream. |
| [OWASP ASVS](https://github.com/OWASP/ASVS) | Versioned application-security requirements for coverage and evidence mapping. | Reference-only; use versioned identifiers, verify each mapping, and do not claim compliance or certification from scanner output. [CC-BY-SA-4.0](https://github.com/OWASP/ASVS/blob/master/LICENSE.md). |
| [OWASP pytm](https://github.com/OWASP/pytm) | A model for assets, data flows, trust boundaries, threats and review artifacts. | Reference-only. Its Python model scripts and threat expressions are executable input, not inert documents. [MIT plus CAPEC notices](https://github.com/OWASP/pytm/blob/master/LICENSE). |
| [Trail of Bits skills](https://github.com/trailofbits/skills) | Useful audit, variant-analysis, static-analysis and evidence-validation workflow patterns. | Reference-only; no third-party skill text is vendored or automatically activated. [CC-BY-SA-4.0](https://github.com/trailofbits/skills/blob/main/LICENSE). |
| [OWASP Secure Agent Playbook](https://github.com/OWASP/secure-agent-playbook) | AI-agent threat modeling and review of tool permissions, prompt-injection surfaces and data flow. | Reference-only; model and tool outputs still require independent assessment. [CC-BY-4.0](https://github.com/OWASP/secure-agent-playbook/blob/main/LICENSE.md). |

## Verified command contracts

These are documented command shapes for **reviewed plans**, not evidence that any external scanner was installed or run here. Substitute paths deliberately, pin the selected binary version, record its version and configuration, and check that version's help output. The planner emits arguments as data and does not execute them.

- **Semgrep:** `semgrep scan --config /trusted/rules.yml --metrics off --disable-version-check --json --output /reports/semgrep.json /repo`. The [CLI reference](https://docs.semgrep.dev/cli-reference) confirms local YAML config, JSON output and metrics controls. Avoid registry auto-selection when local-only rules are intended; builds and autofix are separate capabilities.
- **Gitleaks:** `gitleaks dir /repo --redact=100 --report-format json --report-path /reports/gitleaks.json`. The [README](https://github.com/gitleaks/gitleaks/blob/master/README.md) distinguishes `dir` from `git` and documents report/redaction flags. Capture process errors separately from findings; a missing output file is not an empty successful report.
- **OSV-Scanner v2:** `osv-scanner scan source --recursive --format json --output-file /reports/osv.json --offline --no-call-analysis=go,rust --no-resolve /repo`. [Source usage](https://github.com/google/osv-scanner/blob/main/docs/scan-source.md), [shared usage](https://github.com/google/osv-scanner/blob/main/docs/usage.md), and [flag definitions](https://github.com/google/osv-scanner/blob/main/cmd/osv-scanner/internal/helper/flags.go) support this shape. Offline mode needs previously provisioned databases; call analysis may build code, so it is disabled in this bounded recipe. Disabled manifest resolution reduces coverage.
- **Trivy:** `trivy fs --scanners vuln,misconfig,secret --format json --output /reports/trivy.json --offline-scan --skip-db-update --skip-java-db-update --skip-check-update --skip-version-check --disable-telemetry /repo`. The [filesystem CLI reference](https://github.com/aquasecurity/trivy/blob/main/docs/guide/references/configuration/cli/trivy_filesystem.md) documents these controls. Cached databases/checks are required. `--offline-scan` alone only disables dependency-identification API calls; it does not disable database updates.
- **zizmor:** `zizmor --offline --format sarif --strict-collection /repo`. [Usage documentation](https://github.com/zizmorcore/zizmor/blob/main/docs/usage.md) confirms these options. SARIF mode deliberately does not use finding-based nonzero exit codes; parse the report rather than interpreting exit zero as no findings.
- **Syft:** `syft --from dir /repo -o cyclonedx-json=/reports/sbom.cdx.json`. [Target documentation](https://oss.anchore.com/docs/guides/sbom/scan-targets/) distinguishes directory scans from registry pulls. [Configuration documentation](https://oss.anchore.com/docs/reference/syft/configuration/) documents `SYFT_CHECK_FOR_APP_UPDATE=false`; inspect cataloger/configuration behavior before asserting network isolation.

Scanner flags are not an operating-system sandbox. Config files, environment variables, caches, ignore files and executable versions can affect behavior. Record them in scan provenance. A denied network request, missing database, parse failure, timeout, unsupported artifact or skipped file must remain a coverage gap, not a clean bill of health.

## Output-contract findings that shaped implementation

The current [OSV model definitions](https://github.com/google/osv-scanner/blob/main/pkg/models/results.go) are more precise than the illustrative JSON in its output guide: groups use `experimental_analysis` and `max_severity`, and empty vulnerability collections may be omitted. Grouped advisory aliases must not multiply into independent verified vulnerabilities. Unknown or unsupported CVSS vectors should remain unknown rather than become zero severity.

Generic SARIF is a useful common intake for additional tools, but compatibility is bounded by the supported SARIF structures. Missing locations, invalid line numbers, unsupported external property files, tool execution errors and unknown severities need explicit handling. Native scanner JSON remains useful when it carries package identity, fix information or error details that SARIF may represent differently.

Baseline comparison is evidence of a changed observation set. It is not proof that a missing finding was fixed: rules, scope, tool version, ignore configuration and scanner failures can all change the set. Keep those limitations visible alongside new, persisting and absent observations.

## Licensing and provenance

No third-party scanner source, ruleset, binary or referenced skill text is bundled by this expansion. Preserve the original Cloudflare license and attribution. Fetching a repository for research does not adopt its instructions as authority.

The [Semgrep rules repository license](https://github.com/semgrep/semgrep-rules/blob/develop/LICENSE) identifies **Semgrep Rules License v1.0**, separate from the LGPL-2.1 engine. Do not assume engine licensing applies to downloaded rules or commercial products. Local rules should be supplied under terms appropriate to their use.

ASVS and Trail of Bits documentation use share-alike licenses; Secure Agent Playbook uses attribution terms. Linking to them and writing original implementation guidance avoids silently importing a differently licensed corpus. GitHub's automatic license field was inconclusive for pytm and Secure Agent Playbook; their actual license files were inspected to resolve the distinction. Logos and other assets can also have separate terms.

## Verification boundary

Repository existence, maintenance metadata, capabilities, licenses and the documented command/output contracts were checked against primary sources. No detection-quality comparison, full external-scanner compatibility suite, live cloud security scan, active network scan or public plugin installation is implied by this research. Local package tests and validation results should be reported separately from these source checks.
