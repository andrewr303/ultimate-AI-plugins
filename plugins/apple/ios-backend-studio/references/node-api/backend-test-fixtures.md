# Behavioral backend tests and cross-client fixtures

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Test the contract that the client consumes

Start from the requested observable behavior and the existing test runner. Preserve the project's framework and package scripts; using Node's built-in runner is an option, not a reason to replace an established suite. Inspect the actual Node version before adopting mock-timer/module APIs from current documentation. Keep test setup bounded and deterministic, with no implicit production endpoint or provider credentials.

Use separate levels deliberately: pure domain tests for state transitions; route tests for middleware/status/body behavior; database integration tests for constraints and transaction semantics; provider contract tests against an authorized sandbox; and native client decode/UI checks for platform behavior. Passing one level does not establish another. A generated type that compiles is not a response validator, and a unit mock cannot reproduce a database isolation policy.

## Fixtures that reduce platform drift

Store small synthetic golden requests/responses for the API surfaces shared by Swift, web and other clients. Include success, stable domain error, missing optional field, explicit null where allowed, unknown enum values, large identifiers, decimal amounts, date/time offsets, empty and terminal pages, and incompatible content types. Keep fixture ownership linked to the API description and review generated changes. Avoid private production payload dumps.

Define whether each fixture is expected to accept, reject or preserve unknown data on each supported platform. An unknown enum fallback must be a real supported decoder behavior, not a generator option assumed to work with every serializer. Document a deliberate platform divergence rather than hiding it behind a broad cross-platform pass.

## Implementation sequence

1. Reproduce the reported defect or define the intended new route outcome before changing code. Identify the seam that can control it meaningfully.
2. Inject transport, clock, randomness/identifier generation and job completion only where the behavior needs control. Avoid exposing private implementation details solely for tests.
3. For async ordering, explicitly hold/release responses or transactions and observe readiness. Yielding or arbitrary sleeps do not prove a subscription, listener or transaction is ready.
4. Exercise old success after new success, old failure after new success, cancellation, duplicate admission and account switch. Check public state and domain effects, not internal helper call counts alone.
5. Run the smallest relevant checks, then the project's required integration/build checks. Use real SQLite/Postgres or equivalent when the issue depends on store-specific behavior.
6. Feed shared response fixtures through the actual Swift generated/transport decoder and relevant Xcode test plan when the Apple environment is available.

## Failure and environment boundaries

| Test shortcut | What it fails to establish |
| --- | --- |
| Route handler called directly | Parser/auth middleware ordering and HTTP response behavior |
| Stubbed transaction wrapper | Concurrent database constraint/isolation behavior |
| Wall-clock sleep | Reliable lifecycle ordering or readiness |
| In-memory idempotency table | Restart persistence or multiple-worker behavior |
| Current generated client compilation | Compatibility with installed older app versions |
| Linux Node suite | Xcode target, entitlement, widget or physical-device correctness |

## Completion evidence

Record command, runtime, selected test inputs and actual result. If a service is missing, keep independent local checks moving and identify the precise remaining prerequisite. Do not manufacture a green run from skipped provider/device checks. Test failure output should preserve safe identifiers and the relevant assertion without dumping tokens or full user content.

A useful handoff states which behavior is protected against recurrence, which boundaries used test doubles and which were exercised end to end. Keep fixture updates reviewable; updating a snapshot to match an unintended response is not a fix.

## Sources and applicability

- [Test runner | Node.js v26.12.1 Documentation](https://nodejs.org/api/test.html) — `src_nm_node_test`.
- [OpenAPI Specification v3.1.1](https://spec.openapis.org/oas/v3.1.1.html) — `src_nm_openapi_spec`.
- [PostgreSQL: Documentation: 18: 13.2. Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — `src_nm_postgres_isolation`.
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/tutorials/data/documentation/xcode/organizing-tests-to-improve-feedback.json) — `src_nm_xcode_testplans_final`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
