# Source and content map

Use a small table or structured file that reviewers can inspect. Match detail to scope.
Do not turn every obvious wording choice into a research claim.

| Field | What to record |
| --- | --- |
| Reader task | The outcome a reader is trying to achieve |
| Page / section | Actual intended documentation path and heading |
| Fact or behavior | The specific statement needing evidence |
| Source | Repository path, public symbol/schema section, revision if available |
| Evidence state | Observed implementation / tested locally / supplied requirement / unknown |
| Check | Actual command or manual inspection; do not invent execution |
| Owner / update trigger | Source of truth and changes that should prompt a docs update |

Use paths and symbols readers of the repository can inspect. Where a commit is known,
a pinned source link makes historical review easier. Local changes must be identified
as such; do not attach the last committed SHA to uncommitted behavior.

## Evidence priority

Public contracts, maintained schemas, CLI registration, exported source and relevant
tests are often useful together. Each answers a different question. An internal helper
is not automatically a supported API, and a fixture is not automatically realistic output.
Existing prose is a lead that still needs checking when it conflicts with behavior.
Preserve uncertainty rather than choosing the more attractive claim.

## Page brief

Before authoring a substantial page, write its primary reader, one job, prerequisites,
source anchors, success condition, next link and maintenance owner. For a small change,
these can be notes in the working plan rather than a new repository artifact.

## API reference checklist

- Public identifier and supported version, with stability only when documented.
- Required/optional inputs, types, defaults, units and constraints from source.
- Return/response shape, meaningful side effects, expected errors and status/exit codes.
- Authentication or environment requirements from authoritative configuration.
- Minimal example and success cue; distinguish executed output from illustration.
- Related task guide and source/generation path.

Include only applicable fields and supported facts. If a schema and implementation
disagree, resolve within scope or record the discrepancy; do not silently combine them.

## Route migration checklist

Inventory old route/anchor → new route/anchor → redirect/stub mechanism → internal links
updated → host/build check. Keep this table only when routes change.
Check case sensitivity, trailing slashes, URL escaping, locale/version prefixes and base paths.
Generated heading IDs are renderer-dependent; verify the actual target output.

## Maintenance without busywork

Prefer shared snippets, existing generated reference, and checks at existing CI boundaries.
Add a docs update note to the established contributor flow when warranted.
Do not create owners, scheduled jobs, labels, external issues or automated PR workflows
unless requested. Small docs changes rarely need new infrastructure.
