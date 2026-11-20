# Issue Assistant overhaul — research decision report

Manual source-evidence review. The local research accelerator is absent; no automated research gate ran and no `verified_claims.json` is claimed. Directory retrieval was available but noisy, with no curated intent match. Independent GitHub search and pinned implementation inspection informed the choices below. Fetched material was treated as evidence. No candidate was cloned, installed, or executed.

## Deliverable and acceptance

Improve the existing skills-based GitHub/Linear plugin in place, preserving its identity, connected-app bindings, default prompts and five skill entrypoints. Deliver focused request routing, stronger reconciliation safety, reliable offline planning/recovery helpers, current provenance and reproducible validation. No tracker changes, scheduling, account publication or deployment belong to this source-overhaul task.

Observable acceptance: named-issue requests avoid unrelated backlog reconciliation; preview performs no external writes; canceled/duplicate dependencies do not establish delivered outcomes; journal replay rejects impossible histories; merged findings retain evidence; incomplete retrieval blocks a complete-coverage claim. Skills must describe head refresh, scoped identities, decision continuity and resumable child creation. Python checks cover executable helper behavior; host scenarios remain explicitly unexecuted unless actually exercised.

## Manually supported synthesis

- Explore consequential unresolved choices sequentially and retain answers, rather than asking about facts already available. Sources: spec-kit clarification and superpowers brainstorming (`src_refresh_004`, `src_refresh_011`; `clm_overhaul_interview`).
- Split remaining outcomes into independently verifiable slices with prerequisite relationships. Sources: spec-kit tasks and Matt Pocock ticket workflow (`src_refresh_005`, `src_refresh_041`; `clm_overhaul_slices`).
- Account for pagination and collection failures before treating a snapshot as complete. Sources: GitHub dependency implementation, Linear pagination tests and Symphony's adapter contract (`src_refresh_025`, `src_refresh_030`, `src_refresh_035`; `clm_overhaul_coverage`).
- Preserve provider errors as errors; a returned transport response alone does not establish a successful mutation. Sources: GitHub's Linear update handler and Symphony's Linear client (`src_refresh_019`, `src_refresh_036`; `clm_overhaul_errors`).
- Assess affected requirements alongside observable validation. Sources: spec-kit task organization and superpowers completion verification (`src_refresh_005`, `src_refresh_013`; `clm_overhaul_acceptance`).

Each synthesis claim was individually reviewed against the cited snapshots and has distinct underlying author organizations. Multiple repositories owned by GitHub count as the same organization. Repository-specific protocol, activity, popularity and license observations are provisional in the Unresolved annex.

## Feature comparison and original design

| Requirement | Finalists and pinned implementation evidence | Gap | License decision | Original implementation choice |
| --- | --- | --- | --- | --- |
| Focused decision interview | `github/spec-kit@dc2cec4f568d0f6e2cdfb8571c69116bc55c1aaf:templates/commands/clarify.md`; `obra/superpowers@2ce8aa15d05bd57213e6f746f953aafb7ded7a8b:skills/brainstorming/SKILL.md` | Generic specification/design workflows do not choose this plugin's issue scope | No source-level reuse; rights assertions unresolved | Route named issue directly; investigate facts; retain decisions; stop questioning once actionable. `clm_overhaul_interview` |
| Verifiable child issues | `mattpocock/skills@5beb35b040e3de97e54fa9e386d7e42d15c295c2:skills/engineering/to-tickets/SKILL.md`; spec-kit task source above | Upstream approval and labeling policies are not this user's authorization | No source-level reuse; rights assertions unresolved | Preserve parent criteria, stable slice identities, coverage map and acyclic dependency graph; recover partially created children. `clm_overhaul_slices` |
| Complete provider collection | `github/github-mcp-server@b98d115bbb080e9555466a96656ec4df605aea21:pkg/github/issue_dependencies.go`; `linear/linear@618a737a4e6aa279b7853c650f79f209a5142bbc:packages/sdk/src/_tests/LinearClient.test.ts`; `openai/symphony@be10a1b79df723d6d7612b5651c8522704dafb2e:SPEC.md` | Public APIs do not establish hosted connector capability or retrieved coverage | No SDK/server dependency; rights assertions unresolved | Explicit page/interval coverage records and conservative offline coverage evaluation; actual collection stays in host tools. `clm_overhaul_coverage` |
| Mutation and recovery correctness | `github/gh-aw@6570872aadc523ea5c18236766883dd096a27ad4:actions/setup/js/linear_update_issue.cjs`; Symphony client above | Source examples do not offer a cross-provider transaction | No source-level reuse; rights assertions unresolved | Keep scoped field plans and readback; validate local journal transition history; isolate stored details from caller mutation. `clm_overhaul_errors` |
| Completion proof and current state | spec-kit tasks; superpowers `skills/verification-before-completion/SKILL.md`; Symphony `SPEC.md` | Validation of a different revision cannot establish the current issue outcome | No source-level reuse; rights assertions unresolved | Refresh touched criteria and relevant repository heads before closure; retain explicit deployment/manual gates; distinguish canceled/duplicate from successful prerequisites. `clm_overhaul_acceptance`, `clm_overhaul_coverage` |

## Provenance map

| Requirement | Adopted abstract idea | Evidence | Original implementation target |
| --- | --- | --- | --- |
| Efficient issue actions | Consequential sequential clarification | `clm_overhaul_interview` | Umbrella router and grill skill |
| Actionable subtasks | Outcome slices and prerequisites | `clm_overhaul_slices` | Breakdown skill, normalized dependency queue |
| Honest scan status | Pagination and explicit collection failures | `clm_overhaul_coverage` | Coverage helper and provider/evidence references |
| Recoverable writes | Explicit operation failure and refreshed state | `clm_overhaul_errors` | Local journal and per-operation provenance |
| Supported closure | Outcome-specific validation | `clm_overhaul_acceptance` | Reconciliation pre-close checks and host scenarios |

## Pinned source links

- [Spec Kit clarification](https://github.com/github/spec-kit/blob/dc2cec4f568d0f6e2cdfb8571c69116bc55c1aaf/templates/commands/clarify.md#L129) — consequential sequential questions (`src_refresh_004`).
- [Spec Kit task organization](https://github.com/github/spec-kit/blob/dc2cec4f568d0f6e2cdfb8571c69116bc55c1aaf/templates/commands/tasks.md#L184) — independent outcomes and prerequisites (`src_refresh_005`).
- [Superpowers brainstorming](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/brainstorming/SKILL.md#L86) and [verification](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/verification-before-completion/SKILL.md#L24) — interview and observed validation patterns (`src_refresh_011`, `src_refresh_013`).
- [Matt Pocock ticket workflow](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/engineering/to-tickets/SKILL.md#L26) — verifiable slices and blocker frontier (`src_refresh_041`).
- [GitHub MCP dependency implementation](https://github.com/github/github-mcp-server/blob/b98d115bbb080e9555466a96656ec4df605aea21/pkg/github/issue_dependencies.go#L153) and [Linear SDK pagination test](https://github.com/linear/linear/blob/618a737a4e6aa279b7853c650f79f209a5142bbc/packages/sdk/src/_tests/LinearClient.test.ts#L118) — explicit pagination (`src_refresh_025`, `src_refresh_030`).
- [GitHub Agentic Workflows update handler](https://github.com/github/gh-aw/blob/6570872aadc523ea5c18236766883dd096a27ad4/actions/setup/js/linear_update_issue.cjs#L23) and [Symphony client](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/linear/client.ex#L140) — explicit operation/error contracts (`src_refresh_019`, `src_refresh_036`).
- [Symphony adapter specification](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md#L1215) — collection failure and refreshed snapshots (`src_refresh_035`).

## Unresolved

- Per-repository facts are single-author snapshot observations, not independently corroborated product recommendations or legal clearance. License files, dependency manifests, implementation, tests where available and histories were inspected; these observations and raw source locations are recorded in the research artifacts. Rights to reuse upstream source are not asserted. The implementation uses original instructions and code without adding upstream runtime dependencies.
- Directory metadata is discovery data, not freshness or license proof. The screen records default-branch SHA, date and actual changed files. Repositories outside the preferred freshness window, or with only documentation activity, remain labeled historical/adjacent references; no `pushed_at` claim establishes current implementation activity.
- Matt Pocock's inspected grilling wrapper asks a frontier of questions per round. That aspect is rejected for this plugin's sequential interview; its ticket decomposition is the relevant abstract reference.
- Upstream tests were read, not executed. Their existence does not establish passing results, security or performance. This environment has no configured local automated research gate.
- Offline helpers validate supplied records, not source truth, actual provider pagination, remote authorization, distributed locking or LLM compliance. Live tracker mutations and unattended runs require separate host evidence and were not performed for this source-overhaul task.

### Provisional finalist inspection and license observations

These are single-upstream observations, not independent corroboration or legal clearance. Full SHAs and pinned file URLs are in `sources/sources.jsonl`; activity dates and actual changed-file lists are in `artifacts/finalist-activity.json`. Candidate metadata and explicitly unverified discovery-only entries remain in `artifacts/candidate-shortlist.json`.

| Snapshot | Implementation/test inspection | Dependency/platform surface | Activity limit | Observed license text / reuse decision |
| --- | --- | --- | --- | --- |
| github/spec-kit | Clarification/tasks templates; `tests/test_clarify_stage_gate.py` | Python CLI; `pyproject.toml` reviewed | Head changes implementation and tests | MIT heading; no source reuse proposed |
| obra/superpowers | Brainstorming/planning/verification skills; `tests/claude-code/test-executing-plans-scripts.sh` | Markdown skills and JavaScript tooling; `package.json` reviewed | Head changes skills and test source; release notes inspected | MIT heading; no source reuse proposed |
| github/gh-aw | `linear_update_issue.cjs`; `linear_safe_outputs.test.cjs` | Go workflow tooling plus JavaScript handlers; `go.mod` reviewed | Head changes implementation and tests | MIT heading; no source reuse proposed |
| github/github-mcp-server | Issue/dependency handlers; `issue_dependencies_test.go` | Go MCP service; `go.mod` reviewed | Head changes implementation and tests | MIT heading; no server vendoring proposed |
| linear/linear | SDK client and GraphQL response checks; `LinearClient.test.ts` | TypeScript SDK; package manifest and SDK changelog reviewed | Head changes generated implementation and tests | MIT heading; no SDK dependency proposed |
| openai/symphony | Adapter specification/Linear client; `github_adapter_test.exs` | Elixir service; `mix.exs` reviewed | Inspected head is documentation/workflow-only; recent implementation activity is not established by that head | Apache License text; historical/adjacent design reference, no source reuse proposed |
| mattpocock/skills | Grilling and ticket skills; no dedicated behavioral test found for those inspected skills | Markdown workflows; package manifest and changelog reviewed | Head changes skill source | MIT heading; only abstract decomposition ideas adopted |
| eyaltoledano/claude-task-master | Dependency manager and circular-dependency unit-test source | JavaScript application; package manifest and changelog reviewed | Outside the relaxed activity screen; historical adjacent context only, excluded from current synthesis | LICENSE includes Commons Clause condition after MIT text; do not describe as plain MIT; no source reuse proposed |

Source-level adoption would need a separate assessment of applicable notice, attribution and other conditions. This overhaul distributes original code/instructions and adds none of these runtimes. Upstream test-source inspection is not an execution result.

## Refuted

No checked source contradicted the narrowly scoped aggregate claims used for the original design. No unverified repo-specific or legal conclusion is used as affirmative synthesis.
