# Example reports

These three files show what `audit-build` produces for a deliberately broken build. They are
synthetic: the input is the fixture `tests/fixtures/site-bad/`, a made-up static site on
`example.com` written to trigger as many page and site rules as possible. They are not real site
data, and the numbers in them describe only that fixture.

| File | Format | Use |
| --- | --- | --- |
| `audit-site-bad.json` | JSON result envelope | machine-readable findings, coverage, scores and data |
| `audit-site-bad.md` | Markdown report | human review, pull-request comments |
| `audit-site-bad.sarif` | SARIF 2.1.0 | code-scanning upload (paths are relative to the plugin root) |

The scores section (`--scores both`) is a readiness heuristic from deterministic checks. It is not a
ranking, traffic or citation prediction.

## Regenerate

Run these from the plugin root. `--now` pins the timestamp, so the output is byte-identical on every
run and on every supported Python version:

```sh
python3 -I scripts/seo_geo.py audit-build tests/fixtures/site-bad --base-url https://example.com --scores both --now 2026-11-01T00:00:00Z --format json --output examples/audit-site-bad.json --force
python3 -I scripts/seo_geo.py audit-build tests/fixtures/site-bad --base-url https://example.com --scores both --now 2026-11-01T00:00:00Z --format md --output examples/audit-site-bad.md --force
python3 -I scripts/seo_geo.py audit-build tests/fixtures/site-bad --base-url https://example.com --scores both --now 2026-11-01T00:00:00Z --format sarif --output examples/audit-site-bad.sarif --force
```

`tests/test_cli.py` regenerates all three and fails when they differ from the committed files. After
changing a rule, a module or the fixture, rerun the commands above and review the diff.

The audit runs with the default profile and without `--expect-indexable`, so the launch-only rules
(LAUNCH001, LAUNCH005) do not appear and IDX001 stays a warning. See
[`../references/cli-reference.md`](../references/cli-reference.md) for every option and
[`../references/rule-catalog.md`](../references/rule-catalog.md) for every rule.
