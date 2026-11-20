# Incremental migration playbook

## Define what must stay true

Capture public behavior, supported devices/OS versions, saved data schema, network contracts, account state, navigation restoration and build/release identity. Establish the current compiler, language mode, feature flags and resolved dependencies. Changing the compiler is distinct from enabling a newer language mode or raising deployment availability.

Choose a representative vertical slice and a small verification baseline. Record a reversible source checkpoint using the project's normal version-control workflow; do not discard unrelated work. Keep data backups/fixtures deliberate and access-controlled. Define rollback at the app/data/protocol level, not just git revert, because already-migrated user stores and remote actions may outlive a source change.

## Scope by migration type

- **SDK/API:** verify actual deprecation/replacement semantics, platform availability and fallback. Compile affected targets with the real SDK. Do not replace all stylistic older code during unrelated feature work.
- **Swift concurrency:** migrate one target/boundary at a time; fix ownership, Sendable transfer and isolation semantics before unsafe annotations. Compare app and package compiler settings. Use deterministic cancellation and stale-result tests.
- **Architecture:** preserve behavior while moving one responsibility at a time. Make dependency direction explicit; do not introduce multiple competing presentation patterns for the same feature. Framework adoption requires a concrete need and compatible resolved version.
- **Persistence:** route to Core Data/SwiftData. Keep old schema/model versions, migrate an on-disk copy, verify relationships/counts/invariants and repeated launch. Do not silently reset an incompatible production store. Assess compatibility with sync and rollback separately.
- **Expo/brownfield:** inspect actual SDK/lockfile/native ownership first. Keep manually maintained native directories and integration boundaries. Avoid `prebuild --clean` as generic cleanup.
- **Chat/media library:** inspect the resolved release API, internal dependencies and lifecycle. Main-branch documentation is not the app's contract. Preserve send/cache identity and account isolation through the change.

## Execute and verify

Change one slice, compile/test that slice, review the diff, then proceed. Match test breadth to changed contracts. Test both supported availability branches, cancellation during transition, malformed/old data and repeated operation where relevant. Run the project's required final checks after the last substantive edit, with no broad repeated tests absent a new reason.

If the Apple environment is missing, finish source/package checks and provide exact pending build/device validations; do not fabricate results or provision unrequested services. If a gate fails, diagnose the failure and keep independent work moving. End with the final behavior and evidence, not the abandoned approaches.

Source basis: architecture source selection/concurrency references, Core Data migration/testing, SwiftData schema guidance and Skills-main scoped refactor patterns. All version-sensitive syntax and library APIs need project-local verification.
