---
name: ios-build-debug
description: "Use for native iOS Xcode build or test failures, compiler diagnostics, xcresult inspection, runtime debugging, archives and exported artifacts. Do not use to submit a release, distribute to testers, or replace an Expo build pipeline."
---

# Build, test and debug native iOS

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Establish the actual workspace or project, scheme, configuration, dependency manager, deployment target, Xcode/Swift versions and requested destination. Preserve the repository’s build conventions. On a host without Xcode, finish source-level diagnosis and produce a reproducible Mac validation command; report runtime validation as unavailable.

1. Reproduce the smallest relevant failure with the existing command or scheme. Capture the command, exit status and first causal diagnostic.
2. Separate compiler/linker/dependency/signing failures from test failures and runtime failures. Read surrounding source and target settings before editing.
3. Make the smallest coherent repair. Preserve cancellation, actor isolation, app lifecycle and public behavior; route concurrency or persistence problems to their specialist skills.
4. Re-run the failing build or test, then the checks affected by the change. Retain a fresh result bundle for build/test evidence. Investigate failed, skipped and unexecuted tests separately.
5. Report the observed result, exact environment and remaining limitation. A successful compile does not prove simulator interaction, release signing or App Store processing.

Use `ios-signing` for certificate/profile issues, `ios-simulator` for device interaction and `ios-release` after an artifact is ready for delivery.

Read only the references needed for the current step:

- [Build and test evidence](references/build-evidence.md)
- [Failure diagnosis and runtime proof](references/debugging.md)
- [Build and debugging provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
