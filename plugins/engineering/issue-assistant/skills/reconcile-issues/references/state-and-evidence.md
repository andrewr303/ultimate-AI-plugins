# Evidence, queue and durable state

## Stable identity and recoverable operations

Concern identity combines the resolved provider/tracker/repository scope with a durable semantic concern key, such as `api-retry/cancel-leaves-job-running`. Exclude run timestamps, mutable titles, issue order and new evidence lists. Store a bounded marker such as `<!-- issue-assistant:concern:<fingerprint> -->` in an authorized managed section/comment. Each operation key combines concern identity, operation kind and canonical desired fields. Run ID and evidence revision are separate.

Search relevant open and closed issues, children, configured mirrors, concern markers, PR links and synonyms before creation. Identity collisions or plausible duplicates are findings to resolve, not permission to mark duplicate. After timeout or an unknown response, recover the exact remote outcome before retrying; inability to recover leaves the operation uncertain.

Journal run/scope, concern/operation key, target, desired fields, prior touched values, source references/revision, state, remote ID and readback. Retain evidence from every merged finding, including the same concern observed through different PRs. Keep transport errors distinct from a verified result. A state change and its audit text are separate operations: retry only the missing piece.

Use truthful transitions: planned intent precedes mutation, an applied result precedes successful readback, and only verified effects are receipts. Replay must reject impossible/corrupt histories rather than reconstructing success from a final flag. Keep recorded details isolated from later caller edits. Preserve prior field values for a proposed corrective patch; any undo must preserve subsequent human changes.

## Scope ownership and preview

Only one apply run should write a scope at a time. Hosted jobs load the scoped ledger's owner/expiry/version, acquire a lease with supported exact-match state replacement, verify ownership, renew during long work and recheck before writes. Skip a live competing lease. Without atomic provider comparison, leases are best-effort; skip contested writes and never claim distributed exactly-once execution or a cross-provider transaction.

Preview performs no external writes: no lease acquisition/renewal, remote ledger creation/update, issue mutation, comment or receipt persistence. It may read existing state and return proposed operations/state with blockers. Apply uses already granted scoped authorization; do not add a ceremonial approval gate.

## Hosted manifest and checkpoints

Use one authorized remote document/issue titled `Issue Assistant — reconciliation ledger`, discovered by exact scope marker. Its manifest includes schema version and revision, resolved scope/allowlist, per-source completed checkpoints, pinned heads, reviewed PR revisions, coverage intervals/gaps, pending/uncertain operations, verified receipts, decisions/deferrals, active interview and lease. Store neither secrets nor full transcripts.

Keep one uniquely delimited fenced JSON state section. Example layout (illustrative, not a complete schema):

````
<!-- issue-assistant:state:begin -->
```json
{"schema_version":1,"scope_id":"...","pending":[],"receipts":[]}
```
<!-- issue-assistant:state:end -->
````

Read full current content and patch only the exact prior state section. Preserve explanatory/human text and document parent. On conflict reread and merge verified receipts by operation key; never overwrite existing state with an empty ledger. Read back, parse and verify the result. If state is missing, recover remote markers and repeat the baseline. Do not issue new creates/state transitions until unknown outcomes and duplicate identity have been resolved.

Persist intent before mutation and verified receipts afterward. Temporary local journals are supplementary for hosted runs. Failure to persist required state blocks a complete-run claim and checkpoint advancement; preserve pending work and report the exact limitation. Do not assume an ephemeral workspace will exist next run.

Use fixed UTC half-open coverage intervals `[start, end)`. Record each source's page/partition completion, errors, truncation/caps, reviewed interval and unavailable histories. Advance only a fully reviewed contiguous interval with required verified operations. A later covered segment cannot bridge an earlier gap, and an unverified write cannot become a receipt merely to advance time. Retain completed per-item work and prior successful checkpoints after a partial failure. The offline coverage helper checks supplied records, not whether the host actually retrieved or reviewed them.

## Acceptance and head refresh

For every issue criterion retain actual source references, implementation at pinned revision and outcome-specific meaningful validation. Tests support only exercised behavior. PR text, title similarity, automatic closing and agent promises cannot pass completion. Distinguish code merged, behavior present at current head, validated, deployed and accepted.

Immediately before closure reread current issue scope/status and relevant default-branch heads. Inspect later changes when either differs; refresh affected criteria, reverts, contradictions and validation. Keep the issue open if relevant coverage remains incomplete. Unrelated unavailable history need not block supported work, but unavailable relevant code/checks/scope does. Require deployment/manual acceptance when the issue explicitly requires it.

A parent needs evidence for its own acceptance and required child outcomes. Closed/canceled, not-planned and duplicate children do not prove delivery; follow canonical duplicate targets or revised scope decisions where supported. A revert does not imply regression if current code delivers the outcome another way.

## Dependency-aware queue and decisions

Use refreshed native priority: urgent, high, medium, low, then unspecified. Explain actual incident/deadline overrides; never invent them or silently change stored priority. Promote actionable prerequisites needed by a higher-priority item and explain why. An unknown/external dependency, canceled prerequisite or unresolved cycle remains a blocker until its required outcome is evidenced or the dependency is explicitly changed. Do not rank a blocked item as ready to code.

Tie-break by verified deadline, supported impact and unresolved age; label inferred impact and unknown priority. Respect defer/snooze dates/conditions. An undated “not now” persists until user steering or material evidence changes its basis; it is not cancellation. Keep the active issue until resolved, skipped, explicitly delegated or deferred.

Retain answered decisions with rationale, evidence and scope. When corrected, mark the prior decision superseded rather than erasing it. Interview queue order may differ from tracker priority without mutating it. Stop asking once the issue is actionable and return the ready-to-code packet or perform the already requested implementation.
