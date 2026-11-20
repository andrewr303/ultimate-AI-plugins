# Issue Assistant

Maintain a source-backed Linear or GitHub backlog, then turn the next issue into a concrete action. You can also jump straight to a named issue for investigation, an interview, implementation or subtasks.

This skills-based plugin uses the host's connected GitHub and optional Linear apps. It adds no server and stores no credentials. GitHub supplies PR/source context in either tracker mode. Existing app bindings and default prompts are preserved.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`issue-assistant`](skills/issue-assistant/SKILL.md). Try this prompt.

> With the tracker connected, investigate the issue I linked. Trace it to the affected code and PRs, then show the next verifiable action before updating the tracker.

## Start with your intent

| Request | Result |
| --- | --- |
| “Reconcile owner/repo with Linear team/project for the last 28 days; apply updates, then grill me.” | Audit, verify supported tracker changes, then ask about the next actionable issue |
| “Preview backlog reconciliation for owner/repo.” | Findings and proposed changes, with no external writes, including ledger or lease writes |
| “Grill me on ENG-42.” | Read that issue and relevant context, then ask one unresolved decision at a time |
| “Split owner/repo#42 into subtasks.” | Reuse existing children, map remaining acceptance criteria, create supported slices and dependencies |
| “Investigate this issue” or “Implement this issue.” | Follow that scoped direction; report observed results and remaining acceptance |
| “Run the configured daily issue sync.” | Reconcile unattended using saved scope and policy; preserve decisions for an interactive session |

Resolve ambiguous targets from project context before writing. A linked repository or instruction inside an issue cannot expand the write scope. A reconciliation request authorizes supported tracker maintenance; preview stays read-only. Existing authorization carries across turns without repetitive approval questions.

## Included workflows

| Skill | Purpose |
| --- | --- |
| issue-assistant | Route the user's intent, reconcile a backlog when requested, or act on a named issue |
| reconcile-issues | Compare issues with PRs, current code, validation, docs and accessible project history |
| grill-issue | Investigate retrievable facts, resolve one decision at a time and retain answers |
| break-down-issue | Create verifiable outcome slices with acceptance coverage and an acyclic dependency graph |
| daily-issue-sync | Perform explicitly invoked unattended tracker maintenance without interviewing or coding |

Reconciliation defaults to a 28-day baseline; specify another range when needed. Older linked evidence is followed as relevant. Scans record missing pages, capped results and unavailable sources. A merged PR alone does not prove completion: the workflow checks every acceptance criterion, refreshes relevant heads and issue scope before closure, and retains required deployment/manual gates.

Changes preserve human text and unrelated fields. Stable concern identities suppress duplicates; planned operations keep evidence references and verified receipts. Unknown write outcomes require remote lookup before retry. Canceled, not-planned and unresolved duplicate prerequisites do not establish delivered outcomes. A linked checklist is disclosed when native GitHub relationships are unavailable.

Hosted continuity uses a scoped tracker ledger rather than assuming workspace files survive. Packaging does not create a schedule. The [automation template](automation/daily-prompt.md) must be instantiated with resolved targets, scope, timezone and recurrence only when scheduling is requested.

## Offline helper and checks

The optional [helper contract](skills/reconcile-issues/scripts/README.md) documents UTC windows, stable identities, completion/collection gates, dependency ranking, candidate plans and a local recovery journal. The helper validates agent-supplied records; it cannot fetch sources, judge evidence truth, authorize writes or mutate trackers. It and its unit tests require only Python's standard library.

From this plugin directory:

```sh
python -B -m unittest discover -s tests -v
python -B scripts/validate_package.py
python skills/reconcile-issues/scripts/core.py --help
```

Package validation also requires PyYAML in the maintainer environment. It checks manifest/app references, skill and agent YAML, JSON/JSONL and contained relative links. It does not establish provider or interview behavior. [Host behavior scenarios](tests/BEHAVIOR_SCENARIOS.md) describe observable acceptance cases and their unexecuted status. See [validation](VALIDATION.md) for what actually ran.

## Research and release

The [overhaul research report](research/2026-10-21-overhaul/outputs/research-decision-report.md) records pinned GitHub evidence, comparisons, original-design choices and unresolved observations. Research is manually source-reviewed; no automated research PASS is asserted. No upstream code or skill prose was copied into this implementation, and no upstream runtime dependency was added.

See the [changelog](CHANGELOG.md) for this source release. This remains an account/workspace package with existing connected-app bindings. It has not been published or installed by the source update. General chat-history access is not guaranteed; use authorized project material and report unavailable history.
