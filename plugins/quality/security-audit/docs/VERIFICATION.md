# Verification record

Verified October 30, 2026 on Linux with Node.js 24.19.0. The package requires
Node.js 20 or newer; other Node versions and operating systems were not exercised
in this delivery environment.

## Automated tests

`npm test` passed **124 tests**, with **0 failures and 0 skips**:

| Area | Tests |
| --- | ---: |
| Original findings and coverage-ledger validators | 65 |
| Scanner adapters and normalized signal validation | 21 |
| Baselines, Markdown and SARIF reporting | 15 |
| Read-only repository planner | 12 |
| Bounded and exclusive file I/O | 6 |
| CLI workflows and exit behavior | 5 |

The new tests exercise meaningful failure cases as well as successful imports:
malformed reports, scanner errors, unsupported result categories, secret-bearing
fields, unsafe paths, Unicode controls, SARIF historical/external results,
rule-identity collisions, incomplete baselines, exclusive output creation,
symlinks, hard links, FIFOs, size/depth limits, and a fake scanner that must never
execute during `doctor`.

## End-to-end acceptance

**28 CLI invocations** passed expected-exit-code checks using the authored
synthetic reports in `examples/reports/`:

- Every supported format imported one signal, passed normalized validation,
  rendered Markdown, and exported SARIF.
- The Gitleaks fixture's `Secret` and `Match` value was absent from normalized
  output and reports.
- A comparison against an empty baseline produced one new signal and exit `3`
  with `--fail-on-new`; its saved comparison validated and rendered successfully.
- A synthetic repository selected 3, 5, and 6 scanner recipes for quick,
  standard, and deep profiles. Every recipe remained `not_run`.
- An empty original findings document exported without inventing findings.
  The unit suite separately exercises confirmed, unresolved and rejected records.

Six generated SARIF documents passed the
[SARIF 2.1.0 JSON schema](https://json.schemastore.org/sarif-2.1.0.json) using Python
`jsonschema` during delivery verification. Python is not a runtime dependency.

## Package checks

- The root manifest passed the
  [Agent Plugins 1.0 schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json).
- All four skill frontmatters parsed as YAML and matched their directory names.
- Relative Markdown documentation links resolved within the package.
- The original MIT license, domain companions, schema, validator code and
  validator tests were retained byte-for-byte. The original main skill received
  the documented optional-toolkit and input-trust additions; README was expanded.
- The archive was checked for a single package root, unwanted files and symlinks,
  and its contents were compared with the verified source.

## Limits of these results

No Semgrep, Gitleaks, Trivy, OSV-Scanner, zizmor or Syft binary was present in the
delivery environment, and none was installed or executed. Scanner recipes and
report structures were researched against primary documentation and exercised
with synthetic fixtures. That is not a live compatibility or detection-quality
benchmark, and future producer versions may require adapter updates.

No target-controlled builds, live endpoint scans, cloud changes, database updates,
GitHub uploads, host plugin installation, account saving or public publication
were performed. The toolkit does not provide a sandbox. Source-evidence claims
and complete audit coverage still require the original independent audit workflow.
