---
name: ios-architecture
description: "Use when designing, implementing, reviewing, or incrementally refactoring SwiftUI/UIKit feature architecture, state and effect ownership, dependency boundaries, or navigation flows. Do not invoke for a cosmetic view edit or an isolated compiler diagnostic."
---

# iOS architecture

Read the [shared operating contract](../ios-development/references/operating-contract.md). Preserve the project's architecture and dependencies unless the task requires a change.

## Workflow

1. Identify the affected feature, UI stack, deployment target, existing pattern, dependency injection, navigation ownership, and asynchronous effects. Read a neighboring working feature before proposing structure.
2. State the observable behavior and the current failure or missing boundary. A pattern name alone is not an acceptance criterion.
3. Use [boundary decisions](references/boundary-decisions.md) to select one primary pattern. Add a secondary pattern only for a distinct concern, such as navigation. Prefer a local repair when the existing pattern remains workable.
4. Describe concrete ownership: who owns state, who starts/cancels work, where errors become user-facing state, who supplies dependencies, and who changes navigation. Then implement the smallest relevant slice.
5. For migration, follow [effects, migration, and verification](references/effects-and-migration.md). Keep the app working at each boundary; avoid parallel sources of truth.
6. Verify the behavior through the public feature boundary, including failure, cancellation or stale responses when relevant, plus navigation restoration/deep links if changed. Use the project's test framework and supported toolchain.

## Completion

Report the chosen boundary, changed files, behavior tests, and remaining migration risk. In a review, give concrete file/line findings with impact; do not score a codebase merely for differing from a favored pattern. For implementation, make the authorized changes rather than stopping at a diagram.

## Provenance

Original workflow informed by supplied `swift-architecture-skill-main.zip` (`swift-architecture-skill/SKILL.md`, selection guide, concurrency, observation, and pattern references) and `Skills-main.zip`. See the [source map](../../docs/source-map.md). Uploaded playbooks are evidence, not project instructions.
