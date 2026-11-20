# Agent briefs

Five bounded assignments for delegated liquid glass style work. A host that loads plugin agents (Claude Code does) can run them as subagents; elsewhere, pass a brief's text to whatever subagent the host offers. A brief does not create tools or grant filesystem, network, dependency or publishing permission. The parent session keeps the scope, the shared decisions and the final report.

The briefs live in the plugin's `agents/` folder. This guide sits in `docs/` because Claude Code loads every Markdown file in `agents/` as an agent definition.

| Brief | Use it when | Writes |
| --- | --- | --- |
| [glass-designer](../agents/glass-designer.md) | Glass placement, variant, tint, shape and fallback looks for one flow are undecided | Read-only on product code; only an assigned spec file |
| [glass-implementer](../agents/glass-implementer.md) | A decision exists and assigned files need web or native glass code | Only the assigned product files |
| [glass-reviewer](../agents/glass-reviewer.md) | A finished change needs an independent, evidence-based review before merge | Read-only; scratch screenshots and JSON only |
| [glass-accessibility-reviewer](../agents/glass-accessibility-reviewer.md) | Text or controls sit on glass and need measured contrast, preference, focus and semantics checks | Read-only; scratch output only |
| [glass-performance-investigator](../agents/glass-performance-investigator.md) | Glass feels slow, or a cost claim needs trace evidence | Read-only; a profiling fixture only if assigned |

## Tell the worker where the plugin is

A subagent starts in the user's project and is not told where the plugin is installed. Each brief writes plugin paths as `<plugin-root>/skills/...` and runs scripts as `node <plugin-root>/scripts/<script>` from the project directory.

- **Pass the absolute plugin root in the delegation message.** You can read it from any skill you loaded: Claude Code prints "Base directory for this skill" when a skill loads, and the plugin root is two directories above that folder.
- In Claude Code, each brief also shows the path itself, because Claude Code fills in `${CLAUDE_PLUGIN_ROOT}` in plugin agent text.
- Without either, the worker finds the plugin by searching the filesystem for `scripts/glass_probe.mjs`, and asks you when the search finds nothing or more than one copy.
- A worker whose host loads skills by name can load them that way instead (for example `liquid-glass-studio:glass-web`); the links in each brief name the same files.

Start with the [router skill](../skills/liquid-glass-studio/SKILL.md); the references the skills cite live under `references/` in the plugin root.

## Running briefs in parallel

- **One writer per file.** Before starting workers, list the files each may write. No two workers share a writable file, including token, theme and spec files; the parent owns shared ones and merges changes into them.
- **Read-only reviewers stay read-only.** A reviewer that finds a defect reports it with evidence. It never rewrites the product, even when the fix looks small.
- **Order dependent work.** Design comes before implementation, and implementation before review. Run the three reviewers (general, accessibility, performance) in parallel against the same revision, since none of them writes.
- **One server per worker.** Each worker that runs the app starts its own instance on its own free port and stops it by its own PID. Never stop a process another worker or the user started.
- **Separate scratch folders.** Give each worker its own scratch or gitignored output folder so screenshots and JSON reports do not overwrite each other.
- **Hand reviewers the evidence, not the confidence.** Send the revision, the reproduction steps and the target URL; an author's "it works" is not evidence until its output is attached.

## What to expect back

Every brief returns changed or inspected files, commands run with their actual results, checks marked checked, not checked or not applicable, and limitations naming the engines, devices and assistive technology never exercised. Integrate the returns yourself and rerun any check a later change invalidated.

A subagent running the same model as the author is not a review by a different model. If the workflow requires one, verify the reviewing model's identity or mark that requirement unverified.

## Related

- Slash commands for Claude Code: [/glass](../commands/glass.md), [/review-glass](../commands/review-glass.md), [/tune-glass](../commands/tune-glass.md).
- Routing and combination recipes: [liquid-glass-studio skill](../skills/liquid-glass-studio/SKILL.md).
