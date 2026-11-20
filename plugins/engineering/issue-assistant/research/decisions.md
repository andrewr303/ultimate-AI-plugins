# issue-assistant research decision report

This is a manual source-evidence review. No candidate was cloned, installed, executed, or copied. No automated research validator was available or invoked; there is no automated PASS and no verified_claims.json. The implementation should be original, using the inspected projects only for abstract workflow ideas.

The requested product combines retrospective backlog reconciliation, a priority-driven interview, and a separately scheduled unattended reconciliation. Linear and GitHub Issues should be alternative tracker backends, with an explicitly configured source of truth when both refer to the same work.

## Manually supported synthesis

- Use a normalized issue view with provider-native read and write adapters. Existing agent tools and tracker services expose that boundary (clm_001; src_032, src_023).
- Validate scope, configured targets, and fields, then verify remote mutation responses. An unsuccessful API response must never become a successful ledger entry (clm_002; src_018, src_013).
- Record scan coverage and exhaust pagination. SDK tests and tracker client code explicitly include paginated reads (clm_003; src_033, src_014).
- Rank actionable work with dependencies in view, retaining blocked work for investigation and splitting verifiable tasks when appropriate (clm_004; src_003, src_033).
- Make targeted, additive updates that preserve existing issue labels, project assignment, PR descriptions, and human decisions (clm_005; src_028, src_007).
- Preserve explicit links between issues, PRs, and provider records as evidence and cross-tracker identity (clm_006; src_028, src_032).

## Feature comparison and original-design decisions

| Requirement | Finalist consulted | Pinned evidence | Gap / boundary | License decision | Original implementation choice |
| --- | --- | --- | --- | --- | --- |
| Decision interview and issue splitting | mattpocock/skills | mattpocock/skills@5beb35b040e3de97e54fa9e386d7e42d15c295c2:skills/engineering/to-tickets/SKILL.md; src_grilling; clm_004 | Current protocol observation is single-org and in Unresolved; user explicitly requires one question at a time | No text or source copied; independent legal clearance unresolved | Ask exactly one decision question per turn; agent investigates retrievable facts; make independently verifiable child tasks |
| Linear issue hygiene | wrsmith108/linear-claude-skill | wrsmith108/linear-claude-skill@d61cd9ad05f1863a421d891d9319ec2405904488:SKILL.md; clm_005 | Hosted connector schema can differ from public skill examples; snapshot is outside preferred freshness screen | No source copied | Read current issue before changing it; preserve classification; discover duplicates before creation |
| Linear client behavior | linear/linear | linear/linear@9dd2ed80f93ae596f4f7fa21aa7cf80895c58514:packages/sdk/src/client.ts and packages/sdk/src/_tests/LinearClient.test.ts; clm_002, clm_003 | SDK is a building block, not a reconciliation policy | No SDK dependency or copied code required | Provider capability discovery; page coverage and explicit error outcomes |
| Unattended mutation boundaries | github/gh-aw | github/gh-aw@d5ecd72bf96d46d1e1eab8947146d97ab01293e0:actions/setup/js/linear_update_issue.cjs and linear_safe_outputs.test.cjs; clm_002 | Workflow engine is broader than this plugin | No source copied | Scope-bound write plan, evidence checks, read-after-write, durable action journal, uncertain outcome reconciliation |
| GitHub Issues backend | github/github-mcp-server | github/github-mcp-server@e3809fe91c7546633241006bf0b91f23b2595e28:pkg/github/issues.go and issue_dependencies_test.go; clm_001, clm_004 | Public MCP tool names are not proof of hosted connector capabilities | No server dependency or source copied | Discover available tools; use native children/dependencies only when exposed; otherwise record explicit linked tasks |
| Cross-tracker identity and content preservation | getsentry/skills | getsentry/skills@f57ada2d0b640406ea7e25b11d636c530e77c58b:skills/pr-link-issue/SKILL.md; clm_005, clm_006 | Linkback format is an ecosystem convention; verify provider URLs and identity | No source copied | Canonical issue identity with aliases; preserve user content; use managed evidence sections and semantic fingerprints |
| Stateful issue-driven orchestration | openai/symphony | openai/symphony@be10a1b79df723d6d7612b5651c8522704dafb2e:SPEC.md and elixir/lib/symphony_elixir/linear/client.ex; clm_001, clm_003, clm_004, clm_006 | Scheduler is not a retrospective backlog auditor; own acceptance-coverage policy needed | No source copied | Reconcile before interview; refresh status; retain scan cursor and write outcomes; stop stale or superseded actions |

## Additional product functionality

These are proposed original features, not factual claims about the candidate projects:

- Completion evidence matrix: one row per acceptance criterion, merged implementation proof, latest-code verification, relevant tests, and deployment evidence when the criterion requires deployment. A merged PR alone does not close an issue.
- Drift taxonomy: distinguish completed-but-open, partial completion, changed requirements, regression/revert, documentation debt, missing follow-up, and truly duplicate work.
- Cross-tracker deduplication: one authoritative record, validated aliases, and a search before every create. Do not mirror the same gap into both trackers by default.
- Recovery journal: fingerprint semantic findings and write intents, record pending/confirmed/uncertain results, and reconcile uncertain creates before retrying.
- Coverage manifest: report repositories, intervals, pages, PRs, documents, ledgers, and explicitly available agent sessions; inaccessible context remains unknown.
- Priority interview: urgent and blocking work first, unspecified priorities last; persist defer/snooze reasons and return after the configured point.
- Daily automation: reuses the reconciliation procedure with no interview, bounded writes, no guessed product decisions, an overlap window for delayed events, and a summary of confirmed changes and unresolved evidence.

## Discovery and maintenance review

Independent GitHub queries are recorded in artifacts/query_ladder.json. Candidate API metadata and inspected histories are in artifacts/candidates.json, raw/heads.json, and raw/trees_and_history.json. Curated-directory retrieval was attempted through awesome-repositories; it was noisy for this specialized combination, so direct repository source inspection drives these design decisions.

The snapshot histories were checked using the default-branch commit endpoint and its changed-file list, not pushed_at. The candidates that received full source review are preserved at the exact SHAs above. Recent head commits that changed only documentation do not establish recent implementation activity; maintenance confidence is recorded conservatively in the candidate screen. Task Master was retained only as adjacent historical context and was not used for synthesis. Archived probot/stale was excluded. The unavailable steveyegge/beads lookup remains unavailable, not a negative quality judgment.

## Unresolved

- clm_007 (src_002, src_grilling): source review shows the current grill-me wrapper delegates to a protocol that asks a whole frontier per round. This repo-specific observation has only one author organization; it is not independently corroborated. The user's explicit one-question-at-a-time requirement controls the new design.
- Per-repository license texts were inspected: MIT headings in the Matt Pocock, Linear skill, Linear SDK, gh-aw, and GitHub MCP snapshots; Apache headings in Sentry Skills and Symphony. Repository metadata alone is not legal clearance. Each license assessment has only its upstream organization and remains unresolved under the skill's independent-corroboration rule. No upstream source or skill prose is copied into the deliverable, and no runtime dependency on these candidates is proposed.
- Full maintenance qualification is incomplete for non-finalist candidates. Source-reviewed history is a snapshot, not a guarantee of ongoing maintenance. No project is described as current solely from pushed_at or directory metadata.
- Candidate tests were read, never run; no claims about passing upstream tests, quality, security, deployment behavior, or performance are made.
- Live customer Linear/GitHub coverage, session availability, issue permissions, and end-to-end behavior depend on the user's authenticated repository and tracker scope.
- The optional local research accelerator was not configured in this environment; the manual review cannot claim an automated research-gate result.

### Source-reviewed finalist snapshots (single-organization details remain provisional)

These observations document what was inspected; they are not independently corroborated product recommendations or legal clearance. Upstream tests were inspected as source and were not executed.

| Finalist snapshot | Implementation and test inspection | Dependency / platform boundary | History / maintenance qualification | License text inspected |
| --- | --- | --- | --- | --- |
| mattpocock/skills | grill-me wrapper, grilling protocol, to-tickets workflow; recursive tree contained no dedicated automated behavioral test suite for these interview skills | Markdown skills; package.json contains release/version tooling rather than a required interview runtime | Exact default-head commit changes skill source; recorded changed-file list, not pushed_at | LICENSE: MIT heading; reuse rights unresolved here |
| wrsmith108/linear-claude-skill | SKILL.md preservation guidance; retry helper; retry.test.ts covers retry conditions and injected waits | TypeScript helpers, Node engine constraint, @linear/sdk runtime dependency; bundled implementation will use host connectors instead | Default head outside the preferred freshness window; retained as labeled historical specialist reference | LICENSE: MIT heading; reuse rights unresolved here |
| linear/linear | SDK client option validation and wrapped GraphQL errors; LinearClient.test.ts covers auth, headers, chained access and pagination | SDK TypeScript package, typed-document-node dependency and Node engine constraints; adding SDK not required for a skills-first host integration | Default head changes generated SDK implementation and tests | LICENSE: MIT heading; reuse rights unresolved here |
| github/gh-aw | Configured-target mutation handler and explicit enabled fields; linear_safe_outputs.test.cjs includes staged/no-network and unsuccessful mutation cases | Go workflow engine plus JavaScript handlers and larger compiler/runtime dependency surface; no bundling proposed | Default-head changed Go implementation and tests | LICENSE: MIT heading; reuse rights unresolved here |
| github/github-mcp-server | issues.go provider operations; issue_dependencies_test.go exercises dependency reads, writes, malformed arguments and self-dependency rejection | Go MCP server; transport and SDK packages; hosted app tool capability must be discovered separately | Default-head changed Go label implementation and tests | LICENSE: MIT heading; reuse rights unresolved here |
| getsentry/skills | pr-link-issue skill appends/replaces references; skill-writer quick_validate.py checks skill structure; no dedicated pr-link-issue behavioral tests found in tree | Markdown workflow expects gh for that upstream skill; validation script declares Python and YAML support; plugin itself can use host connectors | Default-head changed skill instructions | LICENSE: Apache heading; reuse rights unresolved here |
| openai/symphony | SPEC.md model, Linear pagination/error normalization, GitHub adapter tests for normalization, pagination, filtering and errors | Elixir service with HTTP/JSON/template/web dependencies; a scheduler is beyond this plugin's needed runtime | Default-head is documentation-only; targeted Linear client history is outside preferred implementation freshness window | LICENSE: Apache heading; reuse rights unresolved here |

The original artifact should remain a portable skills bundle with a small deterministic helper. Live reads and writes belong to discoverable Linear/GitHub tools; the helper should operate on explicit JSON evidence and journal state. This preserves host authentication and avoids distributing upstream server or SDK implementations.

## Refuted

No checked source contradicted the narrowly worded, manually supported aggregate claims. The requested design intentionally rejects adopting a multiple-question interview as its behavior.
