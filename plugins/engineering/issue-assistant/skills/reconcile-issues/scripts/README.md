# Offline helper contract

`core.py` uses only the Python standard library. It computes review windows,
checks collection coverage and structured completion records, ranks issue snapshots,
produces candidate plans, and stores local operation intents. It never reads credentials, calls a
provider, writes an issue, finds session history, or schedules work. No packages
need to be installed.

The coding agent must collect the evidence, review its meaning, resolve provider
fields, and verify every actual remote write. A passing helper result does not
establish that supplied evidence assertions are true. `write_candidate:true` is
a candidate for the agent's policy and scope checks, not automatic authorization.

## Command line

From the plugin root:

```sh
python skills/reconcile-issues/scripts/core.py window --now 2026-10-19T12:00:00Z
python skills/reconcile-issues/scripts/core.py window --now 2026-10-19T12:00:00Z --checkpoint 2026-08-01T12:00:00Z --days 28 --overlap-hours 48
python skills/reconcile-issues/scripts/core.py gate work/completion.json
python skills/reconcile-issues/scripts/core.py coverage work/coverage.json
python skills/reconcile-issues/scripts/core.py rank work/issues.json
python skills/reconcile-issues/scripts/core.py fingerprint work/identity.json
python skills/reconcile-issues/scripts/core.py plan work/findings.json
python -m unittest discover -s tests -q
```

Use `-` as a filename to read JSON from stdin. Results are JSON on stdout.
Exit `0` means evaluation succeeded; it does **not** mean `eligible:true`, `complete:true`, or
that a write is permitted. Parse the result. Invalid arguments or unreadable
inputs exit `2` with a short error on stderr. All commands are offline.

## UTC windows

`scan_window(now, checkpoint=None, days=28, overlap_hours=48)` returns
`{"start": ISO_UTC, "end": ISO_UTC}`. Inputs accept timezone-aware ISO 8601
strings or aware Python datetimes; naive times and future checkpoints fail.
`days` must be a positive integer and overlap a nonnegative integer.

Start is `now - days`, or the earlier of that and `checkpoint - overlap`.
Every run retains deep rolling context and downtime expands the window without
silently skipping a gap. Paginate the complete resulting interval; the helper
cannot detect a truncated API response. Use provider inclusive/exclusive bounds
carefully, deduplicate results, and advance a checkpoint only after the agent's
required collection and reconciliation steps complete. An overlap is not a
substitute for recovering uncertain writes.

## Collection coverage

`coverage_gate(record)` returns `{"complete": bool, "reasons": [strings]}`.
CLI `coverage` evaluates the same record. This evaluates the agent's supplied
collection assertions; it cannot discover omitted sources, check provider truth,
or establish that an issue's acceptance criteria are met. The completion gate's
`coverage` field remains a separate assessment of relevant evidence categories.

Use a fixed, timezone-aware window and an explicit allowlist of required source
IDs. Every source must provide covered partitions with ordered page observations:

```json
{
  "window": {"start": "2026-10-01T00:00:00Z", "end": "2026-10-22T00:00:00Z"},
  "required_sources": ["github:prs:owner/repo"],
  "sources": [
    {
      "id": "github:prs:owner/repo",
      "accessible": true,
      "partitions": [
        {
          "start": "2026-10-01T00:00:00Z",
          "end": "2026-10-22T00:00:00Z",
          "accessible": true,
          "capped": false,
          "truncated": false,
          "pages": [
            {"item_count": 0, "has_next_page": true},
            {"item_count": 5, "has_next_page": false}
          ]
        }
      ]
    }
  ]
}
```

Source IDs must be unique. Include scope and collection kind in actual IDs;
split repositories or independently queried collections into distinct sources.
The caller declares the required sources before collection and must retain
inaccessible ones. A required source cannot be omitted to obtain a passing result.

Intervals are half-open `[start,end)` after conversion to UTC. Each partition
must lie within the fixed window and have positive duration. Their union must
cover the entire window for every source. Partition order and overlap do not
matter; uncovered intervals fail. Adapt inclusive provider query bounds and
deduplicate records during collection. A provider cap requires smaller
partitions and complete retrieval before asserting `capped:false`.

Every source and partition requires literal `accessible:true`; every partition
requires literal `capped:false` and `truncated:false`. Each partition needs a
nonempty ordered `pages` list. Page `item_count` is a nonnegative integer and
`has_next_page` is an explicit boolean: true on every page except the final
page, which must be false. An empty page with a continuation does not establish
exhaustion. Record continuation from the provider's actual pagination metadata,
not from the item count. Retain provider cursors and errors in the evidence
ledger; the helper does not validate or fetch them.

Missing, inaccessible, malformed, capped, truncated, or unexhausted collection
records return `complete:false`. Invalid JSON/CLI inputs exit `2`. A passing
record is structural evidence only and never advances a remote checkpoint by
itself. A reproducible complete example is in
`tests/fixtures/coverage-complete.json` relative to the plugin root.

## Stable identities

`fingerprint(scope, concern_key)` returns `ia1:` followed by a SHA-256 digest.
`operation_key(scope, concern_key, kind, desired)` returns `iao1:` plus a digest
of the concern, operation type, and exact desired fields.

`scope` is a nonempty string or object containing canonical provider namespace
IDs. For example:

```json
{
  "scope": {"provider": "linear", "workspace_id": "workspace-id", "team_id": "team-id"},
  "concern_key": "hypestake:auth:refresh-token-expiry",
  "kind": "update",
  "desired": {"title": "Handle expired refresh tokens"}
}
```

The GitHub equivalent should include `provider:"github"`, a stable repository
ID, and organization/owner where needed. Include repository identity in the
concern key when a Linear team spans repositories. Never use a short issue
number alone as a global scope. Use a stable semantic concern key across
subsequent observations; new PR numbers, session IDs, dates, and run IDs do not
create new concerns.

JSON object ordering and Unicode NFC differences do not affect hashes.
Concern-key whitespace is collapsed, operation names are lowercased, and scope
strings are trimmed. Case and meaningful desired text whitespace are retained;
list order is retained. Use canonical provider IDs and avoid display-name
aliases. `desired` must contain only fields intentionally being changed: keep
observation times, run IDs, and separate evidence collections outside it.
Changing actual desired text, including an evidence link intentionally written
in a body, correctly changes the operation key. Hashes aid deduplication; remote
lookup and semantic equivalence checks remain necessary.

## Completion gate

`completion_gate(record)` returns `{"eligible": bool, "reasons": [strings]}`.
Only explicit booleans pass; absent checks and truthy substitutes fail closed.
Use this schema:

```json
{
  "explicit_link": true,
  "pr_merged": true,
  "current_head_verified": true,
  "contradiction": false,
  "reverted": false,
  "coverage": {
    "complete": true,
    "required": ["code", "tests", "docs", "ledger"],
    "reviewed": ["code", "tests", "docs", "ledger"],
    "inaccessible": []
  },
  "criteria": [
    {"id": "AC1", "met": true, "evidence_refs": ["code-1", "test-1"]}
  ],
  "evidence": [
    {"id": "code-1", "kind": "code", "ref": "repo@commit:path#L20", "accessible": true, "verified": true},
    {"id": "test-1", "kind": "test", "ref": "check/123@commit", "accessible": true, "verified": true}
  ],
  "deploy_required": false,
  "manual_acceptance_required": false
}
```

The agent establishes the explicit issue/PR relation and verifies the merged
change still exists at the current relevant head, with no later contradiction
or revert. Coverage lists refer to all relevant sources for this issue; do not
label coverage complete when scoped sources are inaccessible or unreviewed.
Acceptance criteria and evidence IDs must be nonempty and unique. Every
criterion must be met and reference known evidence, with at least one direct
proof item. The record also requires accessible verified `code` and `test` or
`check` evidence. Proof kinds are `code`, `test`, `check`, `docs`, `deployment`,
and `acceptance`. Session notes and `pr_prose` may corroborate these items but
cannot satisfy a criterion alone.

If `deploy_required:true`, also supply `deployment_verified:true` and a verified,
accessible `deployment` evidence item. If `manual_acceptance_required:true`,
supply `manual_acceptance_verified:true` and equivalent `acceptance` evidence.
Both requirement flags must be explicitly assessed. Any unverified,
inaccessible, reference-free, or duplicate evidence entry blocks completion.
Documentation-only or discovery work lacking this software completion proof
remains for agent/user review; this strict helper does not silently relax the
gate. Human review must assess evidence freshness and criterion correspondence.

## Ranking and readiness

`rank_issues(issues)` accepts a list of objects with unique canonical `id`,
`priority` (`1` urgent, `2` high, `3` normal, `4` low, `0` unspecified), optional
`state`, optional `state_reason`, and optional `blocked_by:[canonical_id]`. Normalize GitHub labels and
provider states before passing them; do not invent priorities when no configured
mapping exists. The helper defaults absent priority to `0` and state to `open`.
It returns copied active records with:

- `effective_priority`: highest explicit dependent priority inherited through
  prerequisite chains; the stored `priority` is retained.
- `ready`, `unresolved_blockers`, `blocks_active`, and readable `rank_reason`.

Completed, closed, canceled, duplicate, deferred, and snoozed records are
excluded from the queue. Only `done`, `completed`, or `closed` dependencies
resolve a block, and `state_reason` values `not_planned`, `canceled`, `cancelled`,
or `duplicate` prevent resolution. Legacy `closed` snapshots without a reason
retain their prior behavior; preserve the provider's actual reason whenever
available. Canceled, duplicate, deferred, and unknown dependencies remain
unresolved. Resolve a duplicate to its canonical outcome before replacing a
dependency; do not assume the duplicate itself delivered the work. Dependency
cycles remain unready.
Sort uses the explicit tuple `(effective priority order 1,2,3,4,0; unready;
nonblocker; canonical ID)`. There is no synthetic confidence or urgency score.
Select the first `ready:true` issue for the next interview. When none is ready,
investigate the leading dependency or cycle rather than calling blocked work
ready. Provider relationship normalization and actual state truth are external
responsibilities.

## Findings to plans

`plan_findings(scope, findings, existing)` returns deterministic candidate plans
sorted by concern fingerprint. CLI `plan` accepts an object with these three
keys. `existing` maps stable concern keys to canonical issue IDs or `{id:...}`.
The agent must build it from scoped remote lookup, fingerprints, and semantic
duplicate review; an empty mapping is not proof that no duplicate exists.

Each finding is:

```json
{
  "concern_key": "hypestake:auth:refresh-token-expiry",
  "kind": "create",
  "desired": {"title": "Handle expired refresh tokens"},
  "duplicate_search_complete": true,
  "evidence_refs": ["pr/123"]
}
```

`kind` is `create`, `update`, or `complete`. Completion findings additionally
carry a `completion` record using the gate schema. Updates and completions
require an existing canonical target. Creates require every grouped observation
to assert complete duplicate search. An existing canonical issue turns a create
into `review_existing`, requiring the agent to decide whether a scoped update is
needed. An absent target, incomplete duplicate search, or rejected completion
becomes `review`; conflicting desired operations for the same concern become
`review_conflict`. These plans have `write_candidate:false`.

Equivalent observations of one concern/desired operation collapse into one
candidate regardless of evidence order or observation time. Any failed gate in
a group prevents completion. Optional finding `evidence_refs` must be lists of
distinct nonempty strings. Every plan, including a conflict, retains their
sorted union as `evidence_refs`; new references do not change operation identity.
These references remain agent-supplied, rather than verified by the planner.
The planner does not choose winners among
conflicting desired changes, merge bodies, enforce provider field ownership,
write issues, or bypass the agent's write policy.

## Local journal and recovery

`Journal(path)` is an optional append-only JSONL intent log for a **single
process** in one workspace. `begin(operation_key, detail=None)` persists
`planned` and returns true only for a previously unseen operation. Any prior
entry returns false, including a persisted `planned` entry after a crash.
`record(key, status, detail=None)` records permitted transitions, and
`latest(key)` returns the most recent entry.

Permitted transitions are `planned -> applied|uncertain|verified`,
`applied -> uncertain|verified`, and `uncertain -> verified`. Initial entries
must be `planned`. `verified` is terminal for that exact operation. The agent
alone may mark verified after fresh remote readback confirms the desired fields.
A successful HTTP/tool response permits `applied`, not an assumed verification.

After a timeout, record `uncertain`; after a crash, treat prior `planned` as
uncertain too. Search by the concern/operation marker and fetch the canonical
issue to resolve the result. Never blindly replay a create after a timeout. A
verified equivalent issue may complete recovery without another remote write.
When the remote result is demonstrably absent and a retry is warranted, retain
the old intent and make an explicit recovery decision in the agent ledger; this
helper deliberately does not offer a reset that bypasses recovery. Corrupted or
truncated journal lines raise an error instead of silently resetting state.
An unterminated last line also fails, even if its JSON parses, to prevent the
next append from concatenating two records.
Reload also validates the full transition history, including interleaved
operations, and rejects an initial verified state or any transition that could
not be recorded normally. Details must be JSON objects; omitted legacy details
are allowed when reading. Stored details and `latest()` snapshots are isolated
from caller mutation, so nested edits cannot change an already recorded intent.

The log uses flushed local writes but provides no interprocess lock, provider
transaction, distributed compare-and-swap, or exactly-once guarantee. Do not run
concurrent instances against one journal. Remote target re-fetch, collision
checks, uncertainty recovery, field ownership checks, and actual scheduling all
remain coding-agent/provider responsibilities.
