# Research method and boundaries

This package was built with the explicitly invoked Research First Creator workflow, using a manual source-review path because its optional local accelerator and automated report gates were not configured.

- The directory arm used Awesome curated-intent search, taxonomy lookup, filtered/unfiltered repository retrieval, named lookups, and full evidence records.
- The independent GitHub arm executed separate queries recorded in artifacts/query-ladder.json.
- Candidates were screened against the requested rolling month, September 21–October 21, 2026.
- Default branch, commit detail, committer date, and nonempty changed files were inspected; pushed_at was insufficient.
- Source-path history distinguished actual implementation updates from docs, dependency, sponsor and release activity.
- Finalists were inspected at pinned revisions: README, implementation, tests, package manifest, history and license. Tests were read, not executed.
- sources/sources.jsonl and artifacts/claim_ledger.jsonl preserve the main review. native/ retains the supplementary native review.
- Broad manually supported synthesis uses at least two independent author identities. Single-source/API/date/legal observations remain qualified under the reports' Unresolved headings.
- Structural ledger validation is not a factual verification gate, legal clearance, or runtime test.
- Only original prose/code and user-supplied material are packaged. Fetched upstream source trees remain outside the deliverable.

Public repository queries contained generic domain terms. No private app code, credentials, account integration, or unrequested upstream execution was needed.

The [1.1 overhaul review](overhaul/outputs/research-decision-report.md) is a separate manual-review session. Its ledgers use distinct identifiers and preserve the earlier records. It adds source-quality observations, including disabled or weak upstream tests, and records those as limits rather than runtime proof. Original local tests exercise deliberately delivered stale callbacks; upstream tests were only read.
