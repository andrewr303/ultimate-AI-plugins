---
name: grill-issue
description: "Use to investigate or interview one named or highest-priority actionable Linear or GitHub issue, asking one necessary decision question at a time and producing a concrete next action."
---

# Grill one issue

Resolve the exact issue and authorized repository/tracker scope. Use the refreshed queue when the caller requested picking next; a named-issue request needs only that issue and relevant context, not a mandatory backlog audit. Read the issue, parents, blockers, linked PRs, current implementation and prior decisions before asking. Discover technical facts yourself when accessible code/docs can answer them.

State the issue ID/link, why it is active, what is known, and the single decision preventing progress. Ask **exactly one user-facing question** and wait. A question may offer two or three concise choices with a recommendation; do not bundle independent decisions. Use a supported one-question tool when available, otherwise plain text. Be direct and respectful.

Start with the most consequential uncertainty: user problem/outcome, required behavior, invariant, scope boundary, dependency, failure mode or acceptance. Ask follow-ups only when an answer exposes another necessary decision. Do not repeat a resolved question, request approval already granted, or invent unknowns merely to keep interviewing. Stop questioning when the issue is actionable.

Recognize direction in any wording:

- **Implement/fix:** confirm the target identity from available context, inspect repository instructions, implement the scoped change and run relevant checks. Report unavailable execution. Add a tracker handoff only when tracker writes are authorized. Keep acceptance status accurate; merge, deployment and review-comment remediation require their own applicable authorization.
- **Research/context:** investigate source, docs, PR history and available authorized sessions; return evidence and revised unknowns before asking again.
- **Split/subtasks:** follow [break-down-issue](../break-down-issue/SKILL.md), distinguishing a plan from a request to create. Resume the next necessary decision or implementation step.
- **Skip/defer:** preserve the reason and user-supplied resumption date/condition, then move to the next eligible issue. An undated deferral remains until the user revisits it or material new evidence changes its basis; do not guess a date or mark canceled.
- **Correct/reprioritize:** record clarified intent, explicitly supersede conflicting prior decisions, and refresh the queue without silently changing stored priority.

Persist the active issue identity, resolved decision/rationale, evidence, unresolved question, validation outcome and exact next action in authorized managed state. Preview proposes this handoff without writing. Preserve decision history and subsequent human edits; record when new evidence supersedes an earlier assumption.

A ready-to-code packet contains expected behavior, constrained in/out scope, verified entrypoints, acceptance checks, dependencies and explicit remaining unknowns. If no necessary question remains, deliver this packet or carry out an already requested implementation. Do not ask a ceremonial “shall I proceed?”

If the queue is empty, say so with actual coverage. If all work is blocked, identify the highest-priority actionable prerequisite or decision; unknown external dependencies and cycles are blocked, not ready-to-code. Ask one decision question only if the user can resolve it. In unattended mode do not invoke this skill; preserve decisions for the next interactive session.
