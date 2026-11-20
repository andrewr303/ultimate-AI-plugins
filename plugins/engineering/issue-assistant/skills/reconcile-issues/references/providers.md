# Provider contracts

Discover actual tool names, schemas and permissions at runtime. The packaged GitHub and optional Linear app bindings identify existing integrations; they do not guarantee every capability below in every host. Hosted authentication belongs to the host. Keep credentials out of prompts, files, ledgers, issues and logs.

## Scope and capability map

Before writes, record repository host/owner/name and native IDs, permitted base branches, tracker workspace/team/project or issue-repository IDs, and the canonical primary issue per concern. Map explicit mirrors and which tracker owns status; never infer write permission from a fetched link. Keep read-only context outside the write allowlist clearly labeled.

Issue identity includes provider/host and repository or workspace plus native ID. A GitHub `#42` needs its repository; Linear display IDs are not UUIDs. Validate linked PR repository, merge state and base branch before using it as delivery evidence. A cross-repository closing reference is a relationship lead, not proof that either issue may be changed or is complete.

Check capabilities separately: issue retrieval, complete listing/search pagination, code/patch retrieval, create/update, normal issue comments, status transitions, native hierarchy/dependencies, and durable state. Tool errors, permission failures, partial results and transport success with an error payload are not success. Use supported fallbacks only; report missing capability without switching tracker or scope. Preview must not invoke any external write, including a ledger/lease update.

## Linear

Observed integrations have exposed workspace/team/project discovery, issue/status/comment retrieval, issue writes and document reads/writes. Resolve the actual tools and team conventions rather than relying on names. Follow cursors and `hasNextPage`, including an empty page that continues; a failed page leaves coverage incomplete.

Where `save_issue` exists, inspect whether omission of `id` creates and supplying it updates. Resolve native IDs and required fields. Read the current schema for parent, blockers, related links, labels and description patches. Prefer additive labels/relations when available. Replacement fields require rereading and preserving the entire existing set; never clear relationships accidentally. Verify final fields and native hierarchy by readback.

Native Linear priority uses 0 for unspecified, then 1 urgent, 2 high, 3 medium and 4 low. Unspecified is unknown, not urgent. Discover state categories: canceled or duplicate is terminal without proving delivery. Do not rewrite tracker priority merely to match the interview queue.

Use a scoped ledger document only where authorized document access exists. Discover it by exact scope marker before creating. A provider-supported exact-match content patch can protect the prior state section; it is not a transaction over issues or other services. Preserve its parent and human text. Discover the actual parent rules on creation rather than guessing an attachment ID.

## GitHub

Hosts may expose PR/issue search, metadata, patches/file lists, source retrieval, issue updates, comments and dependency operations under different names. PR metadata is not the code diff. Inspect returned pagination/truncation and retrieve relevant source for missing/binary patches. A closed PR must be checked for `merged_at` and target branch. REST issue lists can include PRs: exclude records with `pull_request` when collecting issues.

When a search exposes a count cap or `topn` without a cursor, partition disjoint UTC intervals or use a supported paginated list endpoint. Follow page/link continuation and compare counts where available. A full capped page with no established continuation is unresolved coverage, not the final page. Deduplicate overlapping retrieval by repository and native ID. Handle rate-limit/authentication errors as gaps; do not treat a failed page as an empty list.

For issue updates, `body`, `labels` and `assignees` may replace the whole field. Reread, merge and omit unrelated fields. Use bounded managed body sections when supported. A tool named “add issue comment” may actually support only PR conversation comments; inspect its schema and description before using ordinary issue numbers. If normal issue-comment mutation is unavailable, use the verified managed-body fallback rather than guessing a PR endpoint.

Distinguish state and state reason. Closed/completed can indicate delivered work; closed/not-planned or duplicate does not. Map actual project labels/milestones/conventions for priority and blocked state; do not invent a numeric issue-priority API. A closing keyword or automatic closure cannot replace acceptance verification.

Use native sub-issue/dependency operations only when exposed and authorized. Otherwise upsert linked child checklists/backlinks with stable markers and disclose that these are links rather than native dependencies. Preserve human checklist entries. Do not create silent Linear/GitHub twins or synchronize an explicit mirror against its configured status ownership.

## Session and coding access

There is no guaranteed general session-history connector. Use authorized project-local logs, supplied exports, PR/session links and repository ledgers; report unavailable history. Summarize the minimum actionable context, respect target visibility and keep private transcripts/credentials out of public issues.

Reconciliation authorizes tracker maintenance only within the user's resolved scope. Named implementation authorizes scoped coding; add tracker results only when writes are authorized. Merge, deployment, access changes, outreach and PR review remediation follow their own authorization and repository policy. Unattended sync does tracker maintenance only.
