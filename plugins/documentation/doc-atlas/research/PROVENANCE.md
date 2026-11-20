# Research and provenance

Doc Atlas is original agent guidance and helper code informed by public, pinned documentation implementations. Source code, README prose, logos, screenshots and theme assets from those projects are not bundled. The package's icon, banner and field guide are original assets.

## How research was performed

The Research-first Creator workflow used a curated directory for triage, filtered and unfiltered retrieval, then named lookups and repository evidence. Independent GitHub search queries covered documentation generators, MDX, docs-as-code, README design, API reference, diagrams, quality tools and agent skills. Candidate grades measure fit to this task; stars are not a quality score.

Finalist reviews inspected README, implementation, tests, dependencies, license text and release/history evidence at recorded commits. Activity screening used actual default-branch commit dates and nonzero changed-file evidence, not `pushed_at`. Dependency-only or documentation-only activity does not establish substantive feature development. Nextra was retained as an explicitly older incumbent; stale template repositories were not adopted as defaults.

No candidate was cloned, installed or executed. The optional local research accelerator was absent. This is a manual source review; no automated research verification PASS or `verified_claims.json` is claimed.

## Records

- [Decision report](research-report.md): supported cross-author patterns, comparison matrix, original design choices and unresolved observations.
- [Sources](sources.jsonl): source identities, pinned URLs, commit and path.
- [Claim ledger](claim-ledger.jsonl): manually supported claims and actual execution proofs when present.
- [Search ladder](discovery-queries.json): the independent discovery queries and retrieval outcomes.
- [Candidate screen](discovery-candidates.json): graded, time-bound observations with commit evidence.
- [Finalist evidence index](finalists.json): pinned implementation and test URLs.

The ledger distinguishes independently supported patterns from exact project observations that have only first-party evidence. A license filename or API field is not a legal clearance. For example, Docusaurus has separate documentation terms and Lychee's repository contains license alternatives that singular GitHub metadata does not fully represent. See the report's Unresolved annex before treating metadata as a verified conclusion.

## Design lineage

| Need | Abstract lesson | Original implementation |
| --- | --- | --- |
| Reader navigation | Docusaurus and Fumadocs model navigation separately from prose | Architecture workflow and content-map template |
| Rendered usability | Starlight and VitePress test rendered accessibility and search behavior | Audit rubric and site acceptance procedure |
| Markup boundaries | markdownlint and Vale distinguish markup semantics | Conservative offline preflight and explicit unsupported cases |
| API reference | Redoc and Scalar use schema-driven rendering | API workflow requiring real schema/source evidence |
| Visual meaning | Mermaid accessibility and Markdown image semantics need text context | Diagram recipes and prose-equivalent requirement |
| Stack fit | Astro, Vue and React frameworks expose different integration contracts | Version-aware framework inspection adapters |

These projects are independent research references, with no endorsement or compatibility guarantee implied. If a downstream agent integrates a library or copies a substantive upstream asset, it must review that exact release/file and retain required notices. This plugin does not grant additional upstream rights.

## Verification scope

Helper behavior is covered by the bundled standard-library tests. Package parsing, live schema validation, resource checks and final archive inspection are separate checks. A controlled agent exercise can verify one workflow without establishing automatic host invocation, every agent's behavior, or every framework integration. Scenario definitions in `evals/` are an evaluation plan until executed and recorded.
