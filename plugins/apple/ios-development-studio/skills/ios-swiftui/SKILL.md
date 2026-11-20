---
name: ios-swiftui
description: "Build, review, or refactor SwiftUI views, state ownership, async screen state, previews, or focused UIKit bridges. Use ios-navigation for routes, ios-accessibility for assistive behavior, and ios-performance for measured runtime issues. Do not replace an existing architecture or migrate deployment targets as incidental cleanup."
---

# SwiftUI implementation

Read the [operating contract](../ios-development/references/operating-contract.md) first. Use the project's current architecture, minimum OS, language mode, SDK and dependencies.

## Inputs and scope

Find the screen/component, a nearby example, its state owner, callers and relevant tests. Establish expected behavior and the smallest useful acceptance case. Inspect project settings instead of assuming a source guide's newest API exists. Keep reviews read-only; carry authorized edits through available validation.

## Workflow

1. Map inputs, owned state, bindings, services and side effects using [state and lifecycle](references/state-and-lifecycle.md). Give each mutable value one owner. Keep derived values derived unless measurement justifies explicit caching.
2. Implement a coherent view tree with semantic controls, stable collection identity and narrow inputs. Preserve presentation and dependency conventions; route changes to [ios-navigation](../ios-navigation/SKILL.md).
3. Define loading, loaded, empty, failed and retry behavior. Tie view-owned work to lifecycle tasks, treat cancellation normally, and prevent stale results from replacing current input. Do not start work from `body`.
4. Use [composition and bridges](references/composition-and-bridges.md) for extraction or UIKit wrapping. Define ownership, synchronization and teardown.
5. Add deterministic preview fixtures for meaningful states. Check long content and resizable widths; use [ios-accessibility](../ios-accessibility/SKILL.md) for assistive checks.
6. Build the affected target with available Apple tools. Test state/lifecycle behavior changed by the patch. Record target, command and result. When tools are absent, finish source-level work and name outstanding checks.

## Edge cases and evidence

- Parent input changes must propagate intentionally; an initializer seed is not a live binding.
- Reusing a row for another item must invalidate its previous work.
- Previews must not require production stores, accounts or live networks.
- Runtime guards cannot make an old SDK recognize unknown declarations.
- Do not silence ownership/isolation errors with arbitrary wrappers or unchecked sendability.

Return implemented behavior, changed files, meaningful checks and material limitations. Separate actual defects from optional modernization. See [source map](../../docs/source-map.md).
