---
name: mps-interactive-surfaces
description: "Use when building bounded interactive product previews, deterministic AI demonstrations, editable results, search/filter, reordering, before/after or replayable workflows inside a marketing page."
---

# Interactive product surfaces

Read [interaction recipes](../../references/interactions.md). Reuse real product components where feasible. Otherwise isolate a faithful sample and label it. Every control needs an observable purpose.

1. Write one sentence describing what the visitor learns by interacting. Define the sample inputs, state model, allowed transitions and reset boundary.
2. Select the smallest pattern that demonstrates the claim: tabs, input/result, search/filter, comparison, workflow progression, reordering, editable output or expandable detail. Do not add every pattern to each page.
3. Model relevant `initial`, `input`, `loading`, `success`, `empty`, `error`, `retry` and `cancel/reset` states. Prevent a late pending operation from overwriting a cancelled/reset result.
4. Implement semantic controls, keyboard equivalence, persistent focus, status announcements and clear recovery. Prefer deterministic local samples without expensive services; never label sample generation as a live AI call.
5. Choreograph changes around product meaning. Connect an initiating action to the result, retain reading time, and honor reduced motion without hiding information.
6. Exercise actual behavior including empty input, invalid input, loading cancel, failed attempt, retry, edit and reset. Confirm the page works after repeated use, not just the first pass.

A fake search field or unresponsive tab is a defect. If a real integration is requested, detect configuration, explain any spending, obey host authorization and show failures honestly. Keep the local sample useful when the service is deliberately disabled; never silently pretend a network response occurred.
