# Failure diagnosis and runtime proof

## Classify the first failure

Compiler errors often cascade: identify the earliest meaningful diagnostic and the code/settings that produced it. For linkage, inspect target membership, product/module names, package versions and architecture before adding flags. For dependency resolution, preserve the lockfile and package manager; do not upgrade dependencies or remove a lockfile to mask the cause. For signing, inspect the intended platform and bundle/team identity, then use the signing workflow.

For a failing test, read the assertion and fixture setup before changing production code. Check whether the failure is deterministic, isolated to a destination, affected by time/locale or caused by asynchronous lifetime. Avoid blanket delays, skipped tests and broad retries. A useful regression test exercises the externally meaningful failure; it should not merely assert the implementation’s new shape.

## Runtime diagnosis loop

Write one concrete reproduction: starting state, action, expected behavior and actual result. Select an app process and simulator explicitly. Launch or attach a debugger only within the requested scope. Reproduce before editing, collect a targeted stack/log/exception, form one hypothesis, and change the smallest code that can test it.

For crashes, distinguish symbolicated application frames from system termination, watchdog, memory-pressure and assertion reports. Check build UUIDs and matching dSYMs before trusting symbols. For hangs, capture what the main thread is waiting on, task/lock ownership and a bounded time window. Repeated stack samples can support a hypothesis; one sample does not establish causality.

Use structured logging with privacy defaults. Do not dump auth headers, keychain values, app database contents or tester data into chat. Prefer sanitized examples and targeted fields. Stop detached log readers or sampling processes created for the task. Broad simulator-global logs may include other apps; keep their capture scoped in time and local.

## Checks appropriate to change

- Pure transformation: focused unit examples and edge cases, then package checks if available.
- SwiftUI state/lifecycle: compile plus the relevant navigation, refresh or dismissal scenario; verify loading/error/cancellation as applicable.
- Persistence: temporary/in-memory fixtures plus migration or concurrency checks when changed; never erase a real store to obtain a pass.
- Platform integration: simulator or physical device evidence for the actual capability; disclose simulator limitations.
- Build settings: relevant target/configuration and the CI lane affected; a Debug simulator pass does not establish Release archive behavior.

Once the necessary checks pass, stop repeating them unless new changes or uncertainty justify more work. Report changes and tests together with their practical limit.

## Handoff record

Record resolved source revision, Xcode and Swift versions, scheme/configuration/destination, commands and statuses, result bundle, first causal error, repair and checks. If execution was unavailable, label proposed commands as pending validation. Never turn a locally inspected source or a generated command into an execution claim.

Use other specialists for root causes: actor transfer/cancellation to concurrency, context/store constraints to persistence, layout/identity to SwiftUI, and profiling to performance/observability. Keep the same task, evidence and authorization across the handoff.
