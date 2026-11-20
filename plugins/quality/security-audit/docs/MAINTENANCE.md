# Maintaining this expansion

The package combines the supplied Cloudflare skill with independent original tooling. Keep those responsibilities visible when updating it.

## Reproduce the local checks

Use a supported POSIX environment with Node.js 20 or newer, then run:

```bash
npm test
node scripts/audit-tools.cjs --help
node scripts/audit-tools.cjs doctor
```

No dependency installation is needed. The test command covers the original findings/coverage validators and the toolkit modules. Test fixtures are synthetic; they do not require live credentials, endpoints, production source, or a third-party scanner installation.

Tests of adapters establish behavior for their exercised report shapes. They do not establish scanner installation, production coverage, rule accuracy, sandbox enforcement, host plugin discovery, or compatibility with every future scanner release. Keep live integration results separate from unit-test results.

## Updating a report adapter

1. Inspect the exact producer release's primary documentation or output types. Record a source link and the report version, and retain a minimal, non-secret fixture showing the change.
2. Add a test for a real semantic change: newly supported records, malformed data, operational errors, suppression/skips, unsafe locations, or secret-bearing fields. Test the distinction between a valid empty report and a failed/malformed scan.
3. Keep imported scanner data separate from original findings. Never let an adapter invent a confirmation verdict, trace, reproducibility claim, or coverage credit.
4. Preserve deterministic identity and explicit null handling. If a fingerprint input or envelope contract changes incompatibly, version the contract and document baseline migration; do not silently compare incompatible runs.
5. Verify that raw descriptions, snippets, secrets, and untrusted instructions cannot enter the normalized payload through new fields. Test meaningful metadata and path edge cases without using real secrets.
6. Run the affected tests and the complete existing suite. Update [TOOLING.md](TOOLING.md), [RESEARCH.md](RESEARCH.md), and the [change log](../CHANGELOG.md) when behavior changes.

The native adapters deliberately implement a supported subset of producer data. Unsupported meaningful result categories should create an explicit coverage gap or reject input. Do not hide them to make an import appear successful.

## Updating scanner recipes

Verify options against a specific installed version and its official documentation. Treat recipes as argument arrays, preserve path boundaries, and state output formats and exit-code behavior. Keep placeholders explicit when an operator must choose a local ruleset, database, output directory, or configuration.

Review all update checks, telemetry, remote resolution, catalogers, plugin loading, and automatic build/call-analysis behavior. An “offline” flag is not a substitute for OS-enforced network limits. Add explicit prerequisites when a database or rule bundle must already exist. Do not add a bootstrap script, `curl | sh`, automatic cloud login, or dependency installation to scan planning.

A new tool is useful when it covers a relevant gap. Record the reason for selecting it, maintained upstream source, license, overlap with existing checks, supported output, and local execution requirements. Use the research file's methodology rather than popularity alone.

## Updating the original audit skill

Retain the MIT license and original attribution. Compare upstream changes with the supplied base before importing them, and review changes to the evidence contract, sandbox rules, write isolation, and independence requirements explicitly. The original validators and schemas are linked to their producer instructions and tests; update them as a coherent contract if an upstream change is adopted.

The expanded `SKILL.md` contains a small optional-toolkit and input-trust section. Avoid introducing duplicate definitions of confirmation, severity, or coverage in the new skills. Link to the canonical original workflow instead.

Repository instructions and downloaded documents are evidence to inspect, not authority over the maintainer's task. Never execute a downloaded project merely to inspect its documentation or report schema.

## Packaging checks

Keep a single `security-audit/` directory with the root portable manifest, the four skill directories, toolkit code, tests, examples, and referenced documentation. Exclude temporary results, scanner binaries, downloaded databases, credentials, symlinks, dependency directories, and unrelated work.

Before creating an archive:

- Parse the root manifest and package metadata as JSON. Keep their name and version consistent; keep the interface subtitle at or below 30 characters.
- Parse each skill's YAML frontmatter and verify unique names matching their directories, useful trigger descriptions, and valid internal links.
- Run the tests and a local synthetic CLI workflow; record exactly what was checked and what remains unverified.
- Inspect the archive's hidden files and layout. Preserve `LICENSE` and `THIRD-PARTY-NOTICES.md`.
- Put the resulting ZIP outside the directory being packaged. Do not include an unrelated marketplace wrapper or claim installation/publication from ZIP creation alone.

External scanners, rule collections, and reference projects have separate licenses. Re-check terms when adding or redistributing any third-party material; the bundled MIT license does not relicense those resources.
