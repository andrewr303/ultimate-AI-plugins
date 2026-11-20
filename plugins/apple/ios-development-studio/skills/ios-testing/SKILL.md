---
name: ios-testing
description: "Use when designing, writing, diagnosing, or reviewing meaningful tests for Swift/iOS behavior, including Swift Testing or XCTest, deterministic async tests, persistence migrations, UI integration, and performance regressions. Do not add tests that only mirror private helpers or assert cosmetic implementation details."
---

# iOS testing

Read the [shared operating contract](../ios-development/references/operating-contract.md). Match verification to the changed behavior, available platform and project conventions.

## Workflow

1. Identify the product contract, regression/failure to catch, target/scheme, existing test framework, dependency boundaries and tool availability. Read related tests before creating infrastructure.
2. Use [test selection and contracts](references/test-selection.md) to choose the smallest test that can fail for the actual defect. Keep Swift Testing/XCTest according to existing capabilities; UI testing may require a different target/framework.
3. Use [async, stateful, and integration checks](references/async-and-integration.md) to control responses, clocks, storage and event readiness. Prefer explicit completion over sleeps, yield-based guesses or polling unrelated state.
4. Write tests that exercise the public behavior and meaningful failure paths. Give fixtures ownership/cleanup, make assertions specific, and avoid recreating the implementation inside the test.
5. Run the focused target/tests and required project checks. Investigate failures with evidence, then broaden only when the risk or new failure justifies it. Capture relevant result bundles/artifacts without sensitive data.

## Completion

State the regression protected, checks run, target/configuration and any unavailable device/simulator validation. Distinguish structural/static checks from executed behavior. Do not claim a generated test passed before running it.

## Provenance

Original workflow informed by supplied concurrency testing references, architecture evaluation concepts, Core Data/SwiftData testing guidance, and `Skills-main.zip`. See the [source map](../../docs/source-map.md). Upstream timing examples and framework-trait assertions are not copied as authority.
