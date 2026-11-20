# Agent briefs

These five Markdown files define bounded assignments. A host may load them as native plugin agents; otherwise pass a brief explicitly to an available subagent. They do not create tools or grant filesystem, network, or publishing permission.

| Brief | Assignment | Changes |
| --- | --- | --- |
| [motion-designer](../agents/motion-designer.md) | Inspect friction; propose state/motion contracts | Read-only unless the task assigns specification files |
| [motion-implementer](../agents/motion-implementer.md) | Implement a bounded interaction contract | Only assigned product files |
| [motion-accessibility-reviewer](../agents/motion-accessibility-reviewer.md) | Check reduced paths, semantics, focus and input parity | Read-only |
| [motion-performance-investigator](../agents/motion-performance-investigator.md) | Reproduce and profile latency/rendering cost | Read-only; profiling fixtures only if assigned |
| [motion-reviewer](../agents/motion-reviewer.md) | Independently assess complete interaction behavior | Read-only |

Use [handoff template](../templates/agent-handoff.md). The parent owns scope, shared decisions, and final synthesis. Use a single writer per shared file. Send reviewers the actual revision and reproduction rather than an implementation author's confidence.

Run independent evidence reviews in parallel where it helps. Keep dependent design/implementation decisions sequential. A read-only review must not become an unsolicited rewrite. Runtime capabilities vary; report what was actually observed.
