---
name: docs-maintain
description: "Use when code changes, releases, or stale guidance require a focused documentation update, impact review, link-preserving reorganization, or maintenance plan."
---

# Maintain documentation

Update the guidance a reader depends on when the underlying behavior or supported workflow changes.
Route a broad first documentation build through [Repo Docs](../repo-docs/SKILL.md).
Apply the shared [evidence and safety rules](../repo-docs/references/evidence-and-safety.md).
Use [the maintenance worksheets](references/templates.md) to record the scope and verification.

## Establish the change boundary

1. Read repository instructions, current documentation structure, and generation conventions.
2. Identify the requested base revision, release, changed subsystem, or stale page.
3. Inspect the actual diff and relevant source/tests; do not rely only on a commit title.
4. If the base is not known, use an explicit bounded review scope and state the assumption.
5. Check local modifications before editing and preserve work outside the requested scope.
6. Identify public behavior, defaults, supported versions, commands, and configuration affected.
7. Include renamed or deleted symbols, schema changes, and changed setup prerequisites.
8. Inspect the docs pages, examples, snippets, navigation, and translations referring to those facts.
9. Check whether the changes alter user-visible behavior or only implementation internals.
10. Record the evidence behind each proposed documentation change.

Use the available git revision and diff tools read-only to understand scope.
Do not reset, discard, stash, rebase, commit, or push the user's work as part of a docs update.
Do not invent a baseline hash or call a snapshot current when its source revision is unknown.

## Decide what a reader would misunderstand

For each affected fact, answer: what wrong action or expectation could the current guidance cause?

| Finding | Appropriate response |
| --- | --- |
| Documented behavior became false | Repair the owning page and dependent examples now |
| Public behavior changed but has no discoverable guidance | Add the smallest useful guidance in the owning section |
| Existing guidance remains accurate | Leave it in place and report the assessed scope |
| Source and docs conflict but authority is unclear | Record the conflict and inspect the owning source before editing |
| One-off local failure or temporary debugging state | Keep it out of durable docs unless asked to preserve it |
| Broad stale area outside the task | Record a specific follow-up without silently rewriting it |

Avoid cosmetic churn while fixing a behavioral mismatch.
A source filename change does not necessarily justify a public documentation rewrite.
A small internal change can require a docs fix if it changes a command, default, error, or supported version.

## Map impact before editing

- Identify the canonical owner of each fact: schema, reference page, tutorial, README, or runbook.
- Search exact names and likely old/new terminology across Markdown, MDX, config, and examples.
- Include shared snippets, generated reference inputs, screenshots, diagrams, and search metadata.
- Distinguish conceptual explanation from executable examples and mechanical reference fields.
- Check every supported version explicitly in scope rather than rewriting archived version docs.
- Preserve existing language coverage; identify translations affected by each changed fact.
- Track public URLs and anchors that external readers may already use.
- Keep an internal source map when it helps future review; reuse an existing map before adding one.
- Record source revision, owning docs paths, known owner, and a concrete freshness trigger.
- Do not invent a maintainer identity, release date, support promise, or review cadence.

A freshness date is meaningful only when someone actually rechecked the relevant facts.
Prefer a source-change trigger or owner responsibility over a misleading automatically refreshed timestamp.

## Update the owning content

1. Repair commands, defaults, response shapes, and support boundaries at their canonical source.
2. Update dependent tutorials and examples so their sequence still reaches the promised result.
3. Keep the user's established voice, terminology, hierarchy, and visual conventions.
4. Preserve useful caveats and troubleshooting information unless evidence invalidates them.
5. Change screenshots or diagrams when their content becomes misleading, not merely to refresh appearance.
6. Link to the canonical fact instead of duplicating an expanding table across pages.
7. Explain a migration or breaking change using the actual old/new behavior and supported action.
8. Include deprecation timing only when the project establishes that policy.
9. Keep unrelated docs, other supported languages, and historical version content intact.
10. Do not overwrite or insert root AGENTS.md, CLAUDE.md, or similar instruction files unless asked.

Documentation work does not authorize changing runtime behavior to make an example look correct.
If a discovered product defect blocks truthful docs, document the finding and keep its fix separately scoped.

## Respect generation and publication boundaries

- Inspect generated-file headers, build scripts, configuration, and contribution guidance.
- Edit a generator input or template when the output is declared generated.
- Run the established generator only when its behavior is safe and its dependencies are available.
- Review generated diffs for unrelated changes, version drift, and removed authored content.
- Do not hand-edit generated output when the owning workflow would overwrite it.
- If generation cannot run, deliver the source change and identify the exact stale generated artifacts.
- Treat build hooks and remote plugins as executable code; inspect before running unfamiliar commands.
- Keep preview and build work local unless deployment or publication was explicitly requested.

## Preserve links during reorganization

Keep a stable URL or explicit compatible redirect when moving a published page.
Inspect the actual framework's redirect and anchor support before using remembered syntax.
Prefer an alias, redirect, or concise forwarding page supported by the existing platform.
Update internal navigation, incoming relative links, image paths, and canonical metadata together.
Check case sensitivity, base paths, locale prefixes, trailing slashes, and versioned routes.
Keep useful section identifiers or compatible aliases when a heading changes.
Do not leave an apparently successful redirect that drops a meaningful fragment or sends readers to unrelated content.
When the host cannot preserve old links, disclose the affected public routes and use the supported mitigation.

## Verify and deliver

Check the repaired facts against source and rerun the relevant safe local examples or fixture checks.
Build the affected docs and inspect warnings, generated output, local links, anchors, and navigation.
For moved pages, test old and new paths in the actual preview when available.
Review affected pages at a narrow viewport and any relevant light/dark theme.
Check translations and versioned pages in the declared scope; identify any pending synchronization.
Review the final diff for content loss, unrelated churn, accidentally generated files, and changed root instructions.
Use the shared [quality bar](../repo-docs/references/quality-bar.md) for checks applicable to the change.
Deliver the changed docs, their source revision/scope, verification performed, and precise remaining gaps.
If no durable update was needed, state what was checked and why the existing guidance remains accurate.
