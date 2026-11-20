---
name: ios-concurrency
description: "Use when implementing or debugging Swift async/await, actor isolation, Sendable diagnostics, task lifetime and cancellation, async streams, or callback bridges in an Apple-platform project. Do not invoke for ordinary synchronous edits or non-Swift concurrency."
---

# Swift concurrency for iOS

Read the [shared operating contract](../ios-development/references/operating-contract.md). Diagnose the actual compiler/settings and ownership boundary before changing annotations.

## Workflow

1. Capture the failing behavior or complete diagnostic, source location, affected targets, Swift compiler/language modes, default actor isolation and relevant concurrency feature settings. Include dependency module settings when the boundary crosses a package.
2. Use [isolation and task ownership](references/isolation-and-ownership.md) to map mutable state, actor boundaries, task parentage and lifecycle. Separate async I/O from CPU work; async alone is not an offloading contract.
3. Choose the smallest structural fix: preserve isolation, transfer an immutable value/identifier, move work to its proper owner, or change the API contract. Do not silence a race with `@unchecked Sendable`, unsafe isolation or a detached task.
4. For cancellation, callbacks, streams or reentrant state, use [lifecycle and verification](references/lifecycle-and-verification.md). Check cleanup and success/error paths after suspension.
5. Run the relevant compiler checks and deterministic behavior tests. Use explicit readiness and dependency-controlled completion for cancellation/stale-response races. Add sanitizer coverage when unsafe interoperation warrants it and the host supports it.

## Completion

Explain which ownership/isolation contract changed, why it fixes the observed issue, and which checks ran. Reviews should identify actual incorrect behavior or diagnostics with locations; avoid treating every Task or GCD call as a defect.

## Provenance

Original workflow informed by supplied `Swift-Concurrency-Agent-Skill-main.zip` (`swift-concurrency-pro/references/`), `swift-architecture-skill-main.zip` and concurrency guidance in `Skills-main.zip`. See the [source map](../../docs/source-map.md). Source defaults for compiler version and framework adoption do not apply to the user's project.
