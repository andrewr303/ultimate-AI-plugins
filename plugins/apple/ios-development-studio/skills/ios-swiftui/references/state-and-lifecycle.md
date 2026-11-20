# State ownership and asynchronous screen state

Apply the [operating contract](../../ios-development/references/operating-contract.md). Pick ownership before a wrapper; no presentation architecture is mandatory.

## Ownership map

| Value | Usually appropriate | Review question |
| --- | --- | --- |
| Read-only input | Plain stored value | Must later parent changes appear? |
| View-owned value | Private `@State` | Should it survive reconstruction at this identity? |
| Child edits parent value | `@Binding` | Is mutation part of the child's contract? |
| Owned observable reference | `@State` with supported Observation model | Who creates and retains it? |
| Injected Observation model | Explicit property; `@Bindable` for bindings | Is this borrowing an existing instance? |
| Legacy observable reference | Owner `@StateObject`, injected `@ObservedObject` | Does the supported OS or existing code need it? |
| App-wide dependency | Environment injection | Is it truly shared and installed in presentations/previews? |
| Feature-local dependency | Initializer injection | Can lifetime and test replacement be seen at the call site? |

Observation does not choose an actor. UI mutable state needs isolation appropriate to its use and compiler settings. Do not annotate every model mechanically or move expensive work onto the UI actor to satisfy diagnostics.

## Seeds and identity

An initial value copied into state is a one-time seed for a view identity. When a parent selects another record, deliberately choose a contract:

- Pass the current input directly for display.
- Bind the parent's value for immediate edits.
- Keep a local draft for Save/Cancel semantics, defining what happens if selection changes.
- Replace identity only when replacing the entire local session is intended. `.id(UUID())` during reconstruction hides ownership problems and resets state.

Test cancellation, selection changes and reappearance. Making externally initialized state private can change the source API; check callers first.

Use domain identifiers for mutable or reorderable collections. Indices express position, not item identity. An index can suit a fixed immutable set whose position is its intended identity; identify the concrete failure before imposing a ban. Avoid IDs derived from mutable display content. Filter before a lazy list where practical, and keep row structure predictable.

## Task lifecycle

Use lifecycle work for work owned by a view. Restart when input identity changes and cancel when its owner disappears. Detached tasks have independent lifetime and cancellation; they are not a general isolation repair. Tasks can inherit UI isolation, so `async` alone does not prove computation runs elsewhere.

For search or selection requests:

1. Capture the input and request generation/token.
2. Define loading behavior, including whether old content stays visible.
3. Await debounce/service work without swallowing cancellation as success.
4. After suspension, check cancellation and confirm the generation/input still matches.
5. Publish only the current result. Distinguish empty data from failure.
6. Prevent old cleanup from resetting a newer request's loading state.

Cancellation is cooperative. A service may ignore cancellation or return successfully afterward; the generation check still prevents stale publication. If caching is intentional, define keys and which request may update visible state. Exclude secrets and raw server payloads from presented errors.

## Observation pitfalls

- Rows reading one broad collection may all depend on it. Pass actual row inputs before introducing a second synchronized model graph.
- A computed property still reads underlying dependencies; renaming a broad lookup does not narrow observation.
- Derived caches need every invalidating input identified and tested.
- Do not assume `@AppStorage`, `@Query`, or another dynamic property inside an Observation model preserves view-update behavior. Keep it in its intended SwiftUI context or bridge changes with a tested subscription.
- Nested reference models can be valid. Inspect observed properties and ownership rather than rejecting nesting categorically.

## Fixtures

| Fixture | Expected behavior |
| --- | --- |
| Input A changes to B before A responds | A and its cleanup cannot overwrite B |
| Leave while loading | No stale publication or cancellation error banner |
| Parent updates read-only input | Child reflects it without manual resets |
| Cancel and reopen editor | Persisted value unchanged; draft policy explicit |
| Reorder during image loading | Image remains associated with domain item |
| Preview failure state | No real service or store required |

## Provenance

Original synthesis informed by uploaded AvdLee `SwiftUI-Agent-Skill-main.zip`, `skills/swiftui-expert-skill/SKILL.md` and `references/state-management.md`; Paul Hudson variant, `swiftui-pro/SKILL.md` and `references/data.md`; and `Skills-main.zip`, `swiftui-ui-patterns/references/async-state.md` and `previews.md`. Conflicting wrapper claims, architecture mandates and unverified SDK assertions were excluded. See [source map](../../../docs/source-map.md).
