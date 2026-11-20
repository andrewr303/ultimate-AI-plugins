# Runnable synthetic examples

Every report in `reports/` is an authored fixture. None represents a real scan,
credential, advisory, vulnerable dependency, or confirmed finding. No scanner is
needed to try the import, comparison and reporting utilities.

From the package root, choose a new directory outside any repository being audited:

```bash
mkdir ../audit-example-results
node scripts/audit-tools.cjs import --format gitleaks --input examples/reports/gitleaks.json --output ../audit-example-results/current.json
node scripts/audit-tools.cjs import --format gitleaks --input examples/reports/gitleaks-empty.json --output ../audit-example-results/baseline.json
node scripts/audit-tools.cjs validate --input ../audit-example-results/current.json
node scripts/audit-tools.cjs compare --current ../audit-example-results/current.json --baseline ../audit-example-results/baseline.json --output ../audit-example-results/comparison.json
node scripts/audit-tools.cjs report --input ../audit-example-results/comparison.json --output ../audit-example-results/comparison.md
node scripts/audit-tools.cjs sarif --input ../audit-example-results/current.json --output ../audit-example-results/signals.sarif
```

Expected: one new **unverified** signal, no retained `Secret` or `Match` value,
and SARIF results marked as review notes. Repeat the import with the other format
names and matching input files to exercise every adapter. Each output must use a
new filename; existing outputs are never overwritten.

To exercise the optional CI signal-change gate, add `--fail-on-new` to `compare`
and select a new output. This example exits `3` because it has one new signal.
That exit code does not establish a vulnerability. Incomplete data exits `2` and
takes precedence over the signal-change gate.
