# Maintenance worksheets

Keep these records small and use the repository's established location when one exists.
They are working tools, not mandatory new public pages.

## Documentation impact map

| Changed behavior | Evidence | Reader misunderstanding | Owning docs | Dependent content | Action |
| --- | --- | --- | --- | --- | --- |
| Actual changed fact | Source diff/test/schema pointer | Specific wrong expectation | Canonical page or input | Example, locale, diagram, link | Repair, review, or no change |

An internal implementation change can legitimately have no public documentation impact.
Do not mark every changed file as requiring a new page.

## Freshness source map

| Fact or guide | Owning source | Reviewed revision | Known owner | Review trigger |
| --- | --- | --- | --- | --- |
| User-facing contract | File/symbol/schema | Actual inspected revision | Existing team/person or unknown | Contract, command, default, or release change |

Record only inspected revisions and actual owners. A timestamp without inspection does not refresh a guide.
Avoid storing secret configuration, personal credentials, or confidential source excerpts in a public map.

## Route compatibility plan

| Existing public route | New destination | Mechanism | Fragment behavior | Verification |
| --- | --- | --- | --- | --- |
| Actual old URL/path | Equivalent content | Existing host redirect/alias/forwarding page | Preserved or explicitly handled | Preview path tested or unavailable |

Check internal links and external entry paths separately.
A new sidebar entry does not preserve an old public URL.
When moving localized/versioned content, keep the same language/version destination where appropriate.

## Generated-content decision

1. Does the file declare that it is generated?
2. Which source, schema, template, or command owns it?
3. Does the command execute hooks, import project code, or access a remote service?
4. Are the expected generator version and dependencies available?
5. Can the change be verified safely within the task's environment?
6. Does the result include unrelated formatting, dependency, or version churn?
7. If the command cannot run, which exact output remains stale?

Do not run an upstream installer just because generation is blocked.
Do not silently present a hand-maintained output as reproducibly generated.

## Review record

```text
Scope: actual base/head revisions or a clearly stated bounded snapshot
Changed reader-facing facts: concise list
Canonical pages or inputs changed: paths
Dependent examples/locales/versions checked: paths and scope
Generated output: rebuilt, unchanged, or exact stale files
Compatibility: old/new routes and anchor behavior
Verification: actual commands and observable results
Remaining gaps: exact untested behavior or unresolved source conflict
```

## Safe finish questions

- Can a new reader still reach the first useful result?
- Do the docs describe the code or release actually in scope?
- Are required setup, configuration precedence, and failures still accurate?
- Did a page move break an inbound link, fragment, translation, or version route?
- Did generated output overwrite authored content or another person's changes?
- Did the update touch root agent instructions without a user request?
- Are any screenshots, benchmarks, examples, or freshness claims now misleading?
- Are untested checks recorded as untested rather than implied to have passed?
