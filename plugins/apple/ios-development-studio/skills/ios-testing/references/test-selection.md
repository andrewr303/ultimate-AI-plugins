# Select tests from the behavior contract

## State what must change

Write a concrete before/after scenario: trigger, relevant starting state, controlled dependency outcome and observable result. An effective regression test fails against the defect for the intended reason and passes after the fix. Do not equate more test files or line coverage with stronger evidence.

For a reversible low-impact edit, existing checks or a focused manual validation may be sufficient. Add a test when it protects meaningful behavior, a recurring defect, a boundary with failure modes, or required project policy. Avoid adding assertions that only preserve a chosen private helper name or view nesting.

## Choose the smallest useful level

| Behavior | Useful level | What a passing check establishes |
| --- | --- | --- |
| Domain calculation/validation | Focused value-level test | Defined inputs produce required outputs/errors |
| Screen state after an intent | Model/presenter/reducer test | Public action and controlled effect produce product state |
| Adapter/serialization | Boundary test with representative fixture | Format/contract is mapped correctly |
| Database operation/migration | Integration test with appropriate temporary store | Actual backend supports operation and preserves required data |
| Navigation/accessibility interaction | UI test or focused app integration | Relevant user action reaches correct visible/semantic state |
| Launch/scroll/resource regression | Supported measured workload | Behavior under recorded device/configuration/workload |
| End-to-end cloud/release flow | Authorized controlled environment | Observed remote/device stages, within stated coverage |

Use multiple levels only when they cover distinct risks. A mocked repository test cannot prove a SQL predicate translates; a screenshot cannot prove VoiceOver order or persistence durability.

## Choose the framework already supported

Inspect the target's existing Swift Testing/XCTest use, available toolchain, discovery and CI runner. Keep tests in the appropriate target and follow established async/isolation conventions. New framework adoption is a separate decision from fixing one behavior test.

Swift Testing supports direct async test bodies and expression expectations. XCTest supports async tests and expectation-based callback mechanisms. UI automation commonly has separate XCTest/XCUITest requirements; do not assume a unit framework replaces the UI runner. Verify current APIs and parallelization traits in the installed version rather than copying a source's trait folklore.

Do not place await inside unsupported assertion autoclosures. Await the operation/result in a supported way, then assert or use the framework's documented asynchronous assertion API. Keep actor access valid in tests; do not add unsafe production accessors just to bypass isolation.

## Good seams and doubles

Inject dependencies the behavior actually needs: a network/repository boundary, clock, randomness, identifier source or storage adapter. A double should control outcomes and expose meaningful readiness/completion. It should not duplicate the production algorithm so both can share the same mistake.

Prefer narrowly scoped fakes/stubs over a universal mock framework for a small feature. Assert externally relevant calls only when they are part of the contract, such as “send once” or “do not persist on validation failure.” Do not assert every internal method invocation or an arbitrary order with no product consequence.

Use representative fixtures with boundary values: empty/optional data, malformed payloads, decoding changes, duplicated identity, deleted relationships and expected errors. Keep secrets/user payloads out of committed fixtures. If redaction changes the bug, make a synthetic fixture preserving the relevant shape and document the limitation.

## Isolation and parallel execution

Tests should own their mutable dependencies, temporary directories, containers, defaults domains and task lifetimes. A shared global singleton can make two individually passing tests fail in parallel. Fix ownership first; serialize only when a genuinely shared resource requires it and the framework's trait/runner semantics are verified.

Mark the needed actor boundary explicitly when the code under test requires it. Do not put every test on MainActor merely to hide isolation errors, and do not force main-actor tests onto arbitrary background work. Test target default isolation can differ from the app target; inspect both.

## Review checklist

Can the test fail for the actual bug? Does it assert the product result and a relevant failure path? Does it use a real backend when backend behavior matters? Can it finish and clean up after assertion failure? Is the environment recorded? Are remaining unsupported/device behaviors named honestly? If those answers are unclear, improve the test contract before adding more cases.
