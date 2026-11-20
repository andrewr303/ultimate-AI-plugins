# Changelog

## 1.1.1 (2026-11-10)

- Add `.claude-plugin/plugin.json` so Claude Code loads the plugin with its name, version and author. It matches the portable `plugin.json`.
- The package validator now fails when the two manifests disagree on name, version or description.

## 1.1.0

- Route named-issue interviews, research, splits and implementation directly to the relevant workflow. Backlog reconciliation remains the path for audits and choosing the next issue.
- Make preview fully read-only, bind writes to resolved provider identities, and refresh issue criteria and relevant repository heads before completion.
- Preserve remaining parent acceptance criteria in verifiable child slices, check dependency cycles, and recover partially created children.
- Keep canceled, not-planned and unresolved duplicate prerequisites from making dependent work look ready.
- Validate journal history on recovery and isolate persisted intent from mutable caller data.
- Retain evidence references when equivalent or conflicting findings are grouped into a plan.
- Add an offline collection-coverage gate, package validator, regression tests and host behavior scenarios.
- Refresh pinned GitHub research and record original-design decisions. Preserve app IDs, default prompts and all five skill identities.

Source update only. This release does not create a schedule, mutate a backlog, install the plugin into an account or publish it.
