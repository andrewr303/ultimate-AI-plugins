# Diagnose a cost, then change its cause

## SwiftUI invalidation and identity

Find the observed expensive view and ask which inputs invalidate it. Broad environment or model reads, rapidly changing values, collection lookups inside every row and redundant publication can amplify updates. Pass narrow inputs or move observation closer to the affected region before inventing an additional synchronized state layer.

Check identity when state resets, animations restart, requests repeat or scrolling jumps. Mutable content IDs, newly generated IDs, or positional IDs in reorderable data can recreate work. Fix identity to match domain lifetime. Do not add an arbitrary ID or cache to mask the symptom.

Stable modifier values can preserve identity when the same content changes appearance. Different content can legitimately use branches. Lazy rows should have predictable top-level structure; filtering inside row builders can create avoidable discovery work. Verify the actual impact before restructuring every branch.

## Main-actor work and waits

Inspect formatting, sorting, parsing, image decoding, persistence and synchronous I/O in view construction or UI callbacks. Move expensive policy into the existing service/model boundary and choose an isolation/execution strategy supported by the toolchain. An async function or `Task` is not automatically background execution.

For a hang with low CPU, inspect locks, synchronous cross-thread calls, blocking I/O and dependency waits. Moving unrelated calculation off the UI actor will not fix a lock cycle. Avoid introducing detached tasks simply to remove a compiler diagnostic; preserve cancellation, ordering and ownership.

For repeated async work, check task IDs, reappearance behavior, cancellation, debounce and stale-result suppression. A cache is not a substitute for lifecycle correctness. Requests completing out of order need a publication policy even if their underlying service ignores cancellation.

## Images and media

Decode/downsample for the displayed pixel size where the loader supports it. Track display scale locally and avoid decoding a full-resolution source for a small thumbnail unnecessarily. Inspect existing cache/pipeline ownership before adding another image library or cache.

Cancellation for disappearing/reused rows should affect only that consumer. Verify cache keys include relevant transformations and private-account separation. Compare scrolling with representative image data and cache states, not just empty placeholders.

## Layout and rendering

Look for geometry/preference feedback loops, repeated measurement, unbounded nested stacks, excessive offscreen effects or costly layer compositions during the measured interval. Simplify the implicated region while preserving dynamic layout and accessibility.

Fixed sizes can reduce work but also clip localization or large text. `equatable` optimizations require correct equality that covers rendered and interactive behavior; an overly broad equality can suppress necessary updates. Type erasure and extra containers can be appropriate, so do not remove them solely because a checklist dislikes them.

## Memory and retention

Reproduce repeated enter/leave cycles. Distinguish temporary peak allocations, expected caches and objects that remain unexpectedly retained. Inspect subscription/task/delegate/closure ownership before labeling a memory leak. Use weak references only where the ownership graph warrants them; they can introduce missing work if applied mechanically.

Bound caches, buffers and pagination state according to product needs. Do not clear every cache on each warning or delete persisted stores. A memory reduction that causes repeated downloads or broken offline behavior needs a tradeoff explanation and measurement.

## Finding format

For each prioritized issue, record:

1. User-visible symptom and reproduction.
2. Observed evidence with time interval/source location.
3. Root-cause hypothesis and confidence.
4. Smallest proposed change and behavior preserved.
5. Validation that would confirm or refute the hypothesis.
6. Actual result when a comparable run exists.

If code review is all that is available, label findings as source-backed risks. Do not estimate a speedup or assert the original defect occurs on all devices.

## Fixtures

- Broad timer update with one changing label: unrelated rows do not redo expensive work after the targeted fix.
- Reorder while loading images: identity and cancellation remain correct.
- Repeat presentation: retained resources return to the expected baseline.
- Large-text layout after optimization: controls remain visible/reachable.
- Warm-cache improvement: cold-cache/offline behavior remains correct.

## Provenance

Original synthesis informed by `Skills-main.zip`, `swiftui-performance-audit/references/code-smells.md`, `swiftui-ui-patterns/references/performance.md`; both uploaded `SwiftUI-Agent-Skill-main.zip` variants, their performance references. No diagnosis or measured improvement is asserted without app-specific evidence. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
