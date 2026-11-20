# DeepSec repository research decision report

Status: manually source-reviewed design evidence. No local automated research gate was configured or run. No candidate repository was cloned, installed, or executed. This report does not claim a scanner integration test passed.

The recommended design keeps the uploaded DeepSec engine as the baseline and adds original report normalization and optional external scanner adapters. Repository research informs the design; it does not replace the requested program. The plugin should use local source files, host-mediated review, and a fixed allowlist of scanner commands. No discovered repository instructions were treated as commands.

## Evidence and discovery

The directory search was used as independent category corroboration, followed by direct public GitHub source inspection. `queries.json` and `raw/query-*.json` record separate searches for literal static application security, secret scanners, SAST topics, software composition analysis, IaC security, Claude security review, syntax-aware matching, and dependency vulnerability scanning. Candidate metadata and actual default-branch commit details are recorded separately. Retrieval scores and `pushed_at` were not used as relevance or source-change proof.

All affirmative external capability statements below correspond to manually supported claims in `artifacts/claim_ledger.jsonl`. Each category claim has direct repository evidence and an independent Awesome Repositories source. Exact CLI field-level contracts are pinned implementation observations in `ADAPTER-CONTRACTS.md`; host-installed versions still require integration tests.

## Feature-by-feature decision matrix

| Requirement | Finalist / grade | Pinned implementation evidence | Gap or cost | License decision | Original design choice |
|---|---|---|---|---|---|
| Source code security rules | semgrep/semgrep / strong | [`semgrep/semgrep@087e93b3a1fd:cli/src/semgrep/commands/scan.py`](https://raw.githubusercontent.com/semgrep/semgrep/087e93b3a1fdf44f97bc92b5b9c2ba221cb2488b/cli/src/semgrep/commands/scan.py) (src_003) [clm_001] | Limited rule selection; local CE coverage is not an exhaustive security proof. | External executable only; Semgrep identification discrepancy remains unresolved. | Original bundled local rules; disable metrics/version calls; normalize JSON. |
| Secret detection | gitleaks/gitleaks / match | [`gitleaks/gitleaks@8d1f98c7967e:cmd/directory.go`](https://raw.githubusercontent.com/gitleaks/gitleaks/8d1f98c7967eb1e79cb44ac6241a124e145d2165/cmd/directory.go) (src_010) [clm_002] | Actual code freshness screen did not qualify; directory mode does not scan history. | External executable only; observed MIT identification manually supported [clm_009]. | Optional mature scanner; force full redaction; allowlist metadata fields. |
| Dependency vulnerabilities | google/osv-scanner / match | [`google/osv-scanner@0c8f9eb4570f:cmd/osv-scanner/scan/source/command.go`](https://raw.githubusercontent.com/google/osv-scanner/0c8f9eb4570f6e5a8d8fcc9a9fc3c41255d46115/cmd/osv-scanner/scan/source/command.go) (src_017) [clm_003] | Dependency sources/database access may require networking; no packages is not clean coverage. | External executable only; observed Apache-2.0 identification manually supported [clm_010]. | Explicit network opt-in; source/package/advisory normalization; no automatic upgrades. |
| Filesystem and IaC coverage | aquasecurity/trivy / match | [`aquasecurity/trivy@0231990f702f:pkg/types/report.go`](https://raw.githubusercontent.com/aquasecurity/trivy/0231990f702f626e6981afaafcb0c97d43be28c7/pkg/types/report.go) (src_025) [clm_004] | Vulnerability DB and policy fetching need an explicit network/cache policy. | External executable only; observed Apache-2.0 identification manually supported [clm_011]. | Optional filesystem adapter for vulnerabilities and misconfigurations; source-located results when available. |
| Python AST security checks | PyCQA/bandit / match | [`PyCQA/bandit@92ae8b82fb42:bandit/formatters/json.py`](https://raw.githubusercontent.com/PyCQA/bandit/92ae8b82fb422a639f0ed8d99e96cea769594e08/bandit/formatters/json.py) (src_032) [clm_005] | Python-only; actual code freshness screen did not qualify; installed plugins form part of trust. | External executable only; observed Apache-2.0 identification manually supported [clm_012]. | Optional mature scanner; map confidence/CWE and retain scan errors. |
| Additional IaC specialist | bridgecrewio/checkov / match | [`bridgecrewio/checkov@359a05bc488f:checkov/common/output/report.py`](https://raw.githubusercontent.com/bridgecrewio/checkov/359a05bc488f9db9e36ae060f3665b9bf324df4c/checkov/common/output/report.py) (src_037) [clm_006] | Overlaps Trivy in the initial release and has a larger Python application surface. | Do not vendor; observed Apache-2.0 identification manually supported [clm_013]. | Defer extra adapter; use its graph-aware IaC design as an abstract extension direction. |
| Syntax-aware extensibility | ast-grep/ast-grep / adjacent | [`ast-grep/ast-grep@58283ad60626:crates/cli/src/run.rs`](https://raw.githubusercontent.com/ast-grep/ast-grep/58283ad606265eb8ea466705f7e6cc8d83fecc56/crates/cli/src/run.rs) (src_041) [clm_007] | Structural search building block rather than a comprehensive security scanner. | Do not vendor; observed MIT identification manually supported [clm_014]. | Defer parser dependency; original DeepSec rules plus optional Semgrep supply initial pattern coverage. |
| Common finding schema | Scanner JSON implementations / match | [`gitleaks/gitleaks@8d1f98c7967e:report/json.go`](https://raw.githubusercontent.com/gitleaks/gitleaks/8d1f98c7967eb1e79cb44ac6241a124e145d2165/report/json.go) (src_012); [`google/osv-scanner@0c8f9eb4570f:internal/output/machinejson.go`](https://raw.githubusercontent.com/google/osv-scanner/0c8f9eb4570f6e5a8d8fcc9a9fc3c41255d46115/internal/output/machinejson.go) (src_018); [`aquasecurity/trivy@0231990f702f:pkg/report/json.go`](https://raw.githubusercontent.com/aquasecurity/trivy/0231990f702f626e6981afaafcb0c97d43be28c7/pkg/report/json.go) (src_026) [clm_015] | External formats and errors differ. | Original adapter code only. | One finding model; stable identifiers, redacted output, explicit engine coverage, JSON/Markdown/SARIF exporters. |
| Host-mediated investigation | Trail of Bits workflow / adjacent, ideas-only | [`trailofbits/skills@db5393caf5dd:plugins/static-analysis/workflows/semgrep-scan.js`](https://raw.githubusercontent.com/trailofbits/skills/db5393caf5ddc0e158849199930be78ad9539ebb/plugins/static-analysis/workflows/semgrep-scan.js) (src_060); [`trailofbits/skills@db5393caf5dd:plugins/static-analysis/skills/semgrep/scripts/test_merge_sarif.py`](https://raw.githubusercontent.com/trailofbits/skills/db5393caf5ddc0e158849199930be78ad9539ebb/plugins/static-analysis/skills/semgrep/scripts/test_merge_sarif.py) (src_061) [clm_016 supports Semgrep location mapping only] | Host/API variation; no automatic claim that every host supports the same plugin format. | Copy no workflow text or code; rights are not cleared here. | Original workflows that distinguish candidate from confirmed issue; require source evidence and recheck after edits. |

## Inspected implementation surfaces

The inspected artifacts include README and manifest/dependency files, root LICENSE, command handling, serializers, output tests, and release/commit history. `files.json` records successes and missing-path responses rather than concealing failed retrievals. No missing-path response was counted as inspected code. Representative test evidence:

- [`semgrep/semgrep@087e93b3a1fd:cli/tests/default/e2e/test_output.py`](https://raw.githubusercontent.com/semgrep/semgrep/087e93b3a1fdf44f97bc92b5b9c2ba221cb2488b/cli/tests/default/e2e/test_output.py) (src_047)
- [`gitleaks/gitleaks@8d1f98c7967e:report/json_test.go`](https://raw.githubusercontent.com/gitleaks/gitleaks/8d1f98c7967eb1e79cb44ac6241a124e145d2165/report/json_test.go) (src_013)
- [`google/osv-scanner@0c8f9eb4570f:internal/output/machinejson_test.go`](https://raw.githubusercontent.com/google/osv-scanner/0c8f9eb4570f6e5a8d8fcc9a9fc3c41255d46115/internal/output/machinejson_test.go) (src_019)
- [`aquasecurity/trivy@0231990f702f:pkg/report/json_test.go`](https://raw.githubusercontent.com/aquasecurity/trivy/0231990f702f626e6981afaafcb0c97d43be28c7/pkg/report/json_test.go) (src_027)
- [`PyCQA/bandit@92ae8b82fb42:tests/unit/formatters/test_json.py`](https://raw.githubusercontent.com/PyCQA/bandit/92ae8b82fb422a639f0ed8d99e96cea769594e08/tests/unit/formatters/test_json.py) (src_033)
- [`bridgecrewio/checkov@359a05bc488f:integration_tests/test_checkov_json_report.py`](https://raw.githubusercontent.com/bridgecrewio/checkov/359a05bc488f9db9e36ae060f3665b9bf324df4c/integration_tests/test_checkov_json_report.py) (src_058)
- [`ast-grep/ast-grep@58283ad60626:crates/cli/tests/run_test.rs`](https://raw.githubusercontent.com/ast-grep/ast-grep/58283ad606265eb8ea466705f7e6cc8d83fecc56/crates/cli/tests/run_test.rs) (src_059)
- [`trailofbits/skills@db5393caf5dd:plugins/static-analysis/skills/semgrep/scripts/test_merge_sarif.py`](https://raw.githubusercontent.com/trailofbits/skills/db5393caf5ddc0e158849199930be78ad9539ebb/plugins/static-analysis/skills/semgrep/scripts/test_merge_sarif.py) (src_061)

Dependency surfaces were inspected rather than installed: Semgrep packages Python plus a native core; Gitleaks/OSV/Trivy use Go modules; Bandit/Checkov are Python applications with plugin/configuration surfaces; ast-grep is a Rust workspace. This motivates separately installed optional executable adapters and a small core runtime, not importing all upstream dependency trees into the plugin. This paragraph is a direct source observation; exact runtime versions are not promised.

## Original implementation acceptance criteria

- The uploaded matcher engine works offline without any external scanner installed.
- Each optional adapter uses fixed executable/argv construction without shell interpolation. Missing executable, timeout, output limit, malformed JSON, unsupported schema and scanner-reported errors produce visible incomplete coverage.
- JSON, Markdown and SARIF omit secret values and raw scanner stdout/stderr. Report baselines suppress only matching stable findings and do not disguise engine failure.
- Scanners that use advisory APIs or update databases require explicit network opt-in; configuration does not execute arbitrary scripts.
- Host skills produce evidence-backed review plans and remediation instructions. A finding is not represented as confirmed solely because a pattern matched.
- The packaged plugin contains manifests for their documented host formats, with a separate skill/MCP configuration path when a host does not support the same plugin package.

## Rejected or deferred candidates

The initial plugin intentionally avoids a large collection of overlapping scanners. These candidates remain in `candidates.json`, with their actual source-change records, rather than being padded into recommended dependencies.

| Candidate | Decision |
|---|---|
| TruffleHog | Defer to avoid overlapping secret-engine scope and adding detector verification/network behavior to the initial local workflow. No code copied. |
| Yelp/detect-secrets | Defer; located code changes failed the requested freshness screen and Gitleaks already covers the selected initial secret adapter. |
| Microsoft DevSkim | Defer an additional general rule engine while retaining the uploaded matcher engine and Semgrep integration. |
| Bearer | Defer another application scanner and unresolved project licensing details; no source incorporated. |
| GitHub CodeQL | Defer database extraction, build tracing and CLI licensing/entitlement complexity from the zero-dependency local baseline. |
| OWASP dep-scan | Defer overlapping dependency scanning; OSV supplies the initial narrower adapter. |
| Anthropic Claude Code security review | Ideas-only incumbent example; located code-change freshness failed the requested screen and its GitHub Action workflow is not the requested cross-host local artifact. |

These are scope decisions, not claims that the deferred projects are inferior. No effectiveness or performance benchmark was performed.

## Unresolved

- Semgrep license identification differs across checked sources: root text/directory identify LGPL-2.1 while the pinned GitHub license API returned NOASSERTION. `clm_008` remains unresolved. This report establishes no redistribution clearance. The adapter must vendor neither Semgrep code nor upstream rules.
- Exact scanner output fields and arguments were read at pinned commits. They have not been executed in the user environment. Keep contract fixtures and actual external integration checks distinct.
- Kimi/Codex/Claude host installation behavior is being researched separately; repository research alone does not prove host support.
- Commit dates and counts below are direct primary-source observations with no independent author corroboration. They support a transparent screening record, not a promise of maintenance quality. Gitleaks and Bandit are deliberate optional mature-tool exceptions to the freshness requirement; do not describe them as current by the research screen.

| Candidate | Source code commit observed | Date observed | Changed files in inspected commit | Screen |
|---|---|---|---:|---|
| semgrep/semgrep | [087e93b3a1fd](https://github.com/semgrep/semgrep/commit/087e93b3a1fdf44f97bc92b5b9c2ba221cb2488b) | 2026-10-22T02:08:25Z | 15 | preferred-30-day; activity_verified=true |
| gitleaks/gitleaks | [8d1f98c7967e](https://github.com/gitleaks/gitleaks/commit/8d1f98c7967eb1e79cb44ac6241a124e145d2165) | 2026-02-21T13:30:12Z | 2 | stale; activity_verified=true |
| google/osv-scanner | [0c8f9eb4570f](https://github.com/google/osv-scanner/commit/0c8f9eb4570f6e5a8d8fcc9a9fc3c41255d46115) | 2026-10-22T23:12:51Z | 14 | preferred-30-day; activity_verified=true |
| aquasecurity/trivy | [0231990f702f](https://github.com/aquasecurity/trivy/commit/0231990f702f626e6981afaafcb0c97d43be28c7) | 2026-10-22T12:42:59Z | 3 | preferred-30-day; activity_verified=true |
| PyCQA/bandit | [92ae8b82fb42](https://github.com/PyCQA/bandit/commit/92ae8b82fb422a639f0ed8d99e96cea769594e08) | 2026-02-23T04:42:18Z | 1 | stale; activity_verified=true |
| bridgecrewio/checkov | [359a05bc488f](https://github.com/bridgecrewio/checkov/commit/359a05bc488f9db9e36ae060f3665b9bf324df4c) | 2026-10-20T12:47:04Z | 2 | preferred-30-day; activity_verified=true |
| ast-grep/ast-grep | [58283ad60626](https://github.com/ast-grep/ast-grep/commit/58283ad606265eb8ea466705f7e6cc8d83fecc56) | 2026-10-22T20:53:57Z | 6 | preferred-30-day; activity_verified=true |
| anthropics/claude-code-security-review | [25e460eb0a12](https://github.com/anthropics/claude-code-security-review/commit/25e460eb0a12077f0c6a1934d5dbae2f50785dda) | 2025-11-25T21:10:44Z | 3 | stale; activity_verified=true |
| trailofbits/skills | [db5393caf5dd](https://github.com/trailofbits/skills/commit/db5393caf5ddc0e158849199930be78ad9539ebb) | 2026-10-22T13:35:52Z | 4 | preferred-30-day; activity_verified=true |
| trufflesecurity/trufflehog | [d6ea4a52e3f4](https://github.com/trufflesecurity/trufflehog/commit/d6ea4a52e3f4705989210e60e9f0da0deafe84bf) | 2026-10-23T05:09:10Z | 2 | preferred-30-day; activity_verified=true |
| Yelp/detect-secrets | [34efc5f6db2a](https://github.com/Yelp/detect-secrets/commit/34efc5f6db2ae615d3eb9c919caf0dbca6acb7f7) | 2024-12-20T19:39:31Z | 3 | stale; activity_verified=true |
| microsoft/DevSkim | [bd81f6967d84](https://github.com/microsoft/DevSkim/commit/bd81f6967d84b3ef1dbce9e466dc28e124f56289) | 2026-10-09T00:09:35Z | 72 | preferred-30-day; activity_verified=true |
| bearer/bearer | [884b4245ec9f](https://github.com/Bearer/bearer/commit/884b4245ec9fb80260fd83d8439d41ace45247e2) | 2026-07-31T14:53:29Z | 4 | relaxed-180-day; activity_verified=true |
| github/codeql | [9b72529516ca](https://github.com/github/codeql/commit/9b72529516caf831cfce2a1e2562e9ed717ab067) | 2026-10-23T07:59:49Z | 2 | preferred-30-day; activity_verified=true |
| owasp-dep-scan/dep-scan | [d82c6d80dd12](https://github.com/owasp-dep-scan/dep-scan/commit/d82c6d80dd12452a98786e8494f7612d3c0e25a6) | 2026-10-09T12:05:50Z | 39 | preferred-30-day; activity_verified=true |

- Trail of Bits root license text reads Attribution-ShareAlike; this is a primary-source-only observation. No workflow text, skill text, implementation, or rules are copied.
- Tool presence does not guarantee trustworthiness: separately installed scanners and the host may load their own configuration/plugins. This design is not a process sandbox.

## Refuted

No factual capability claim in the affirmative matrix was contradicted by the sources checked. The proposition that recent repository metadata proves recent source-code activity was rejected during screening; default-branch changed-file details were inspected instead.

## Source registry

See `sources/sources.jsonl` for the complete machine-readable registry and local evidence paths. `artifacts/claim_ledger.jsonl` records the manual support status and executed legal counter-checks. There is no `verified_claims.json` or automated PASS artifact.
