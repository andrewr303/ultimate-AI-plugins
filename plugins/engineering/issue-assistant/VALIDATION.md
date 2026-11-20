# Validation

Source release 1.1.0 was validated on October 21, 2026 (America/Denver), using Python 3.12.14. Earlier account-specific observations are not reused as validation of this overhaul.

## Executed checks

- The offline unit/CLI suite passes all 71 tests. The previous 48 tests remain, with 23 additional regression and collection-coverage cases. Coverage includes canceled/not-planned/duplicate prerequisites, merged plan provenance, impossible/corrupt/unterminated journal histories, nested detail isolation, missing source intervals, caps/truncation, inaccessible sources, empty continuation pages, strict flags and CLI behavior.
- `python -B scripts/validate_package.py` passes: all five skill entrypoints, optional agent YAML, connected-app references, manifest fields, JSON/JSONL and contained Markdown links are valid. Generated Python caches are ignored for source checks; `--archive-ready` also rejects them in a prepared package. Package validation uses the maintainer environment's PyYAML; the helper and its unit suite remain standard-library-only.
- The manifest validates against the official Agent Plugins manifest JSON schema retrieved from its declared URL. Plugin name, exact connected-app bindings and the type/value/order of default prompts match the previous source revision.
- Boundary smoke checks reject an asset path escaping the package and malformed skill YAML.
- The documented collection-coverage fixture evaluates to `complete:true`. This validates its structure, not real provider collection.
- Changed source passes `git diff --check`. No commit, PR, account installation or publication was performed during these implementation checks; repository publication is recorded separately in the PR ledger.

From the plugin directory, reproduce the local checks:

```sh
python -B -m unittest discover -s tests -v
python -B scripts/validate_package.py
python skills/reconcile-issues/scripts/core.py coverage tests/fixtures/coverage-complete.json
```

## Research review

The overhaul report and ledgers record manually reviewed pinned GitHub sources, independent author support for the adopted abstract patterns, query discovery and default-branch changed-file screening. The optional automated research tooling was absent. No automated research PASS or `verified_claims.json` is claimed. Upstream tests were inspected as source and were not run; upstream code or prose was not copied into this implementation.

## Not executed

The 25 scenarios in tests/BEHAVIOR_SCENARIOS.md are documented host acceptance cases, not passing LLM tests. No live backlog mutation, provider write recovery, complete customer reconciliation, account ingestion, interview, scheduler activation or unattended run was executed for this source update. Local checks do not establish those behaviors. There is no available host plugin-validation CLI; the package validator is a local structural check, not host certification.

Offline gates rely on supplied assertions. They cannot prove semantic evidence, actual pagination completeness, remote authorization, distributed locking, deployment or manual acceptance. The local journal remains single-process and supplements rather than replaces durable hosted state.

## Release 1.1.1 (2026-11-10)

Adds the Claude Code manifest and a manifest-agreement check in the package validator. On 2026-11-10 the 71 unit tests, `scripts/validate_package.py`, the shared plugin lint and `claude plugin validate --strict` were run on this version and passed. The October 21 results above describe 1.1.0.
