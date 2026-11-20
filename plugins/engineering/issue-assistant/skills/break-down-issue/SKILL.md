---
name: break-down-issue
description: "Use when the user wants a Linear or GitHub issue planned or split into smaller verifiable outcomes with acceptance coverage, explicit dependencies and recoverable subtask creation."
---

# Break down an issue

Resolve parent identity and authorized tracker/repository scope. Read original acceptance, existing children, current implementation, relevant PRs and recorded decisions. Plan only the remaining outcome; do not recreate delivered work. Use independently verifiable vertical behavior slices rather than a ticket per technical layer. A prerequisite schema/migration change may be separate when needed.

For each slice record a stable semantic key, observed problem, expected outcome, in/out scope, source links, verified code entrypoints, acceptance checks, dependencies, risks and unknowns. Map every remaining parent criterion to one or more slices and identify where combined integration evidence is required. Do not invent estimates, assignees, dates or product decisions.

Include a research spike only for a concrete uncertainty that prevents a useful implementation slice. Define its question, evidence/output artifact and stopping condition. Do not turn unanswered preference into an invented requirement.

Before creating or linking:

1. Search existing open/closed issues and children by outcome, synonyms, links and stable markers. Reuse the canonical matching child; slice keys must not depend on title, order or run ID.
2. Check that every required remaining criterion has an owner slice, every slice serves the parent scope, prerequisites are explicit, and the graph is acyclic. Existing unknown or out-of-scope dependencies remain visible blockers. Do not create contradictory/circular relationships.
3. Respect the requested mode. “Plan”, “preview” or “dry run” returns a reviewable map with zero external writes, including ledger/lease changes. A request to split/create authorizes supported subtask writes in the resolved scope without another approval.

Use [state and evidence](../reconcile-issues/references/state-and-evidence.md) for intent, stable concern/operation markers and readback. Create/reuse prerequisites first, persist each returned ID, then link dependent slices. After a timeout recover that slice by marker before retrying. Partial creation is a partial result: retain verified children and retry only missing children/relationships; do not recreate the whole batch.

Use discovered native Linear parent/blocker relationships. For GitHub use native sub-issue/dependency APIs only when available and authorized; otherwise upsert a linked parent checklist and child backlinks, explicitly identifying the fallback. Preserve human text and existing relationships, reread touched fields and verify all created links. A dependency link does not establish that a prerequisite outcome is complete.

Report child links, criterion coverage, dependency order, first actionable slice and any failed/pending writes. Keep the parent open until its own acceptance is evidenced; canceled, duplicate or not-planned children are not proof of delivery. If one material choice prevents decomposition, ask one question in interactive mode while completing independent planning. Unattended mode records the unknown and creates only supported independent work. Return to the caller's requested workflow.
