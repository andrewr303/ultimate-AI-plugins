# Local tooling guide

The toolkit processes local data. It does not launch external scanners, execute the target, install dependencies, access the network, provide a sandbox, or upload results.

Run it from the extracted package with Node.js 20 or newer. File processing requires POSIX `O_NOFOLLOW` and `O_NONBLOCK` support; native Windows file processing is not supported when those controls are unavailable. `doctor` reports available file controls and scanner file presence without executing the binaries.

## Commands

```text
node scripts/audit-tools.cjs plan --target DIR [--profile quick|standard|deep] --output FILE
node scripts/audit-tools.cjs import --format sarif|semgrep|gitleaks|trivy|osv --input FILE --output FILE [--source-root DIR]
node scripts/audit-tools.cjs compare --current FILE --baseline FILE --output FILE [--fail-on-new]
node scripts/audit-tools.cjs report --input FILE --output FILE.md
node scripts/audit-tools.cjs sarif --input FILE --output FILE.sarif
node scripts/audit-tools.cjs export-findings --input FILE --output FILE.sarif
node scripts/audit-tools.cjs validate --input FILE
node scripts/audit-tools.cjs doctor
```

| Command | Accepted input | Result |
| --- | --- | --- |
| `plan` | Local repository directory | Filename inventory and reviewable scanner recipes. |
| `import` | A supported scanner report | Normalized `tool-signals` JSON. |
| `compare` | Two compatible `tool-signals` files | `signal-comparison` JSON with new, unchanged, and absent identities. |
| `report` | Signals or a signal comparison | Markdown triage report that states uncertainty and completeness. |
| `sarif` | Normalized signals | SARIF 2.1.0 with unverified review results. |
| `export-findings` | Original audit `findings.json` | SARIF containing only validated `confirmed` findings. |
| `validate` | Signals or a signal comparison | Structural and semantic validation; no output artifact. |
| `doctor` | Current executable search path | Presence checks for Node and optional scanner binaries; no version or readiness verification. |

Every `--output` creates a new file with owner-only permissions. The parent directory must already exist, must not be a symlink, and must remain under trusted control. Existing output paths are rejected. Plan output must be outside the target. Choose outside-target paths for all other artifacts as well.

| Exit status | Meaning |
| --- | --- |
| `0` | Operation succeeded. This is not a security verdict. |
| `1` | Invalid arguments, invalid or unsupported input, or I/O failure. |
| `2` | Known incomplete processing or inventory; an output artifact may still have been written. Inspect it. |
| `3` | `compare --fail-on-new` found new identities in a complete comparison. |

Incomplete data takes precedence over the new-signal gate. Do not discard an exit status of `2` or convert it to a passing scan in CI. Use `validate` on retained signal/comparison artifacts before consuming them elsewhere.

## Planning coverage

The planner inspects file and directory names and sizes; it does not parse manifests, load repository code, resolve dependencies, or calculate a source revision. It detects common dependency markers for JavaScript, Python, Go, Rust, Java, .NET, Ruby, and PHP; container and IaC markers; GitHub Actions workflows; and common agent configuration filenames.

| Profile | Recipes |
| --- | --- |
| `quick` | Semgrep and Gitleaks; OSV-Scanner when dependency markers are present. |
| `standard` | Quick recipes, plus Trivy for relevant dependency/container/IaC markers and zizmor for GitHub Actions. |
| `deep` | Standard recipes, plus a Syft CycloneDX inventory plan. |

These profiles select scanner breadth. The original audit's agent-review profiles are separate. Deep planning does not perform a deep audit.

Inventory limits are 50,000 files, 10,000 directories, depth 40, and 512 MiB of aggregate inventoried regular-file sizes. File contents are not read toward that byte count. Symlinks, unsafe entries, unreadable directories, and exceeded limits produce omissions. Common dependency/generated directories are excluded by name, including `.git`, `node_modules`, `vendor`, `.venv`, `dist`, `build`, and `.terraform`; the exact list is in every plan. `complete` describes discovery within these stated limits, not coverage of every repository file or security property.

Filename detection misses custom manifests and generic Kubernetes or CloudFormation YAML. Git history, deployed IAM, production headers, external identity settings, runtime behavior, and live endpoints are outside the inventory. Use the original domain guides to identify manual work and source visibility gaps.

Each recipe contains an argument array, expected import format, prerequisites, output location, exit-code guidance, and limitations. Keep argument arrays separate; do not concatenate target paths into shell commands. Resolve placeholders to trusted paths before any later execution task. All recipes remain `not_run`.

## Scanner prerequisites

The selected projects and source links are documented in [RESEARCH.md](RESEARCH.md). Recipes reflect reviewed documentation, not an assertion that every installed version supports the flags.

| Scanner | Required preparation and limits |
| --- | --- |
| Semgrep | Provide trusted local rules, record their identity and language coverage, and verify the installed CLI options. The recipe disables metrics and version checks; OS network confinement remains necessary. Engine and rule-set licenses differ. |
| Gitleaks | Review configuration and exclusions. The directory recipe uses redacted JSON and checks the working tree, not Git history. Review logs without publishing raw matches. |
| OSV-Scanner | Use the documented v2 source mode and pre-provisioned offline advisory data. The recipe disables dependency resolution and Go/Rust call analysis. Missing lockfiles and stale or missing advisory data are coverage gaps. A connected alternative needs separate scope and data-exposure review. |
| Trivy | Pre-provision applicable vulnerability, Java, and misconfiguration data. The recipe combines offline scanning with separate update and telemetry controls. Flags alone are not network confinement; missing databases or checks are blocked coverage. |
| zizmor | The recipe uses offline SARIF collection for GitHub Actions. Capture stdout through the execution API. Offline mode cannot perform every audit needing remote data. |
| Syft | The deep profile proposes a directory SBOM in CycloneDX JSON. An SBOM is inventory, not a vulnerability report. This package does not import Syft SBOMs as signals. |

Do not let a trusted scanner execute unreviewed repository plugins, external rule loaders, package scripts, build tools, or network-backed configuration. Review tool behavior and use the original audit workflow's sandbox for execution. Database provisioning, installation, authentication, and connected scans are separate tasks; this toolkit performs none of them.

## Import contracts

The importer accepts these report families:

| Format | Expected family | Main imported signal types |
| --- | --- | --- |
| `sarif` | SARIF 2.1.0 `runs` with result and rule metadata | Results from SARIF-producing static analysis tools. |
| `semgrep` | Native JSON with `results` | Rule matches. |
| `gitleaks` | Native JSON array | Secret detector matches, without secret values or source matches. |
| `trivy` | Native JSON `Results` | Vulnerabilities, misconfigurations, and secret detector matches. |
| `osv` | OSV-Scanner native source report `results` | Package/advisory matches. |

Malformed or unsupported structures fail; they are not converted into a successful empty report. Recognized scan errors, skipped analysis, suppressed results, unsupported result categories, and unsafe locations can mark the import incomplete. The adapters are intentionally strict about metadata and structure. Keep the original report for review when a newer producer adds a shape the adapter does not support.

SARIF results marked historically absent are excluded and produce a warning; external result files are never fetched. Explicit source-root mapping can resolve supported local file URIs and URI bases. Trivy reports with omitted empty `Results` need identifying artifact fields; license, cryptographic and modified-result categories are coverage gaps. OSV license/deprecation categories are also flagged as unsupported. OSV CVSS vectors are not recomputed; available numeric group scores or severity labels are used, otherwise severity remains unknown.

Raw scanner prose, descriptions, source snippets, secret matches, and producer-supplied fingerprints are not copied. Titles are generated from the tool format and rule identifier. Metadata fields can still reveal private paths, package names, or identifiers; normalization is not a guarantee that an export is free of confidential information.

Safe repository-relative paths are retained. Traversal, unsafe URI/path syntax, and locations outside an explicit source root are omitted with a warning. `--source-root` only maps report paths; it does not read the corresponding source, establish repository identity, or verify that a file exists. Do not set it to a broad ancestor simply to eliminate warnings.

## Normalized signal data

`tool-signals` contains:

```text
schema_version: "1.0.0"
kind: "tool-signals"
tool: sarif | semgrep | gitleaks | trivy | osv
complete: boolean
warnings: supported, non-secret warning messages
signals: sorted, unique signal records
```

Each record contains `fingerprint`, `tool`, `rule_id`, generated `title`, `path`, `line`, `severity`, `package`, `version`, and `advisory`. Location, package, version, and advisory can be `null`. Severity is the scanner-reported level normalized to `critical`, `high`, `medium`, `low`, `info`, or `unknown`; it is not a confirmed audit severity.

Fingerprints are SHA-256 identities over the normalized tool, rule, path, line, package, version, and advisory. Exact duplicates collapse deterministically; the higher scanner severity is retained for a duplicate identity. Fingerprints are recomputed during validation. The contract does not support arbitrary extra metadata keys; store provenance in a separate companion record.

The separate original audit schema accepts `confirmed`, `needs_validation`, and `rejected` records with stronger evidence requirements. The importer never writes that schema and never makes those verdict decisions.

## Provenance and baseline interpretation

Retain a companion record for each scan with at least:

- Repository identity, exact source revision, dirty state, scope, and excluded paths.
- Scanner name and version, verified binary source, command arguments, rules/configuration identity, and database snapshot or freshness.
- Actual execution status, report time, report hash, sandbox limits, and known omissions.
- Import format, source-root mapping, toolkit version, normalized artifact hash, and import completeness.

The toolkit does not infer or attest to these facts. Do not record credentials or the ambient environment in provenance. A structurally complete import means no recognized import/scan issue was represented in the supplied report; missing error metadata or a truncated run can still require external evidence.

Comparison requires compatible envelope versions and import formats. It matches identities exactly and returns `new`, `unchanged`, and `absent`. When either input is incomplete, absence results are withheld because missing observations cannot establish disappearance. Even with complete inputs, `absent` never means fixed. Line shifts, moved files, changed tools or rules, scope differences, ignore changes, and changed advisory data can produce new/absent pairs without a vulnerability change.

Before calling a change a regression, verify the current source path and relevant diff. Before calling a vulnerability fixed, verify the security invariant and a bounded equivalent reproduction under the original audit workflow. An unchanged fingerprint also requires current-source revalidation when conditions change.

## Reporting and SARIF

Markdown reports label signals as unverified and include completeness and warnings. Comparison reports identify the three groups and the limitations above. They are triage artifacts, not replacements for the original audit's final report and coverage ledger.

`sarif` exports unverified signals as review results and retains scanner severity as metadata. `export-findings` first validates the complete original findings document using the original validator, then exports only `confirmed` records. Unresolved and rejected records are counted in run properties rather than exported as confirmed vulnerabilities. Schema validation is necessary, but does not itself prove that a human or independent agent performed the source verification represented by the records.

No export command uploads to GitHub or another service. Review the intended audience and export contents before a separately requested upload. Downstream consumers can interpret SARIF differently; verify their display and gating policies before using it as a release gate.

## File handling and limits

JSON inputs must be regular, singly linked files with valid UTF-8 and no symlinked path components. Input and output are limited to 20 MiB; JSON nesting is limited to 64 levels and individual arrays to 50,000 items. Import processing applies additional bounded record limits. Unsupported or oversized data fails with a diagnostic that does not include the report payload.

Input/output parent directories must be trusted and stable. Checks reject known unsafe links and changed files, but this utility is not the original audit's descriptor-based, race-safe promotion procedure for target-controlled scratch artifacts. Do not point it at directories actively controlled or mutated by an adversarial process. Use the original promotion procedure to retain target-generated evidence, then process trusted retained files.
