# Schemes, test plans and trustworthy result evidence

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Inputs and intended feedback

Identify the shared scheme, its product/test targets, active test plan, build configuration, destination, runtime and required project checks. Ask what observable behavior changed: wire decoding, account state, widget data, background work or full UI. Test-plan selection should reflect that boundary rather than running an arbitrary broad suite and inferring coverage from duration.

Apple's testing material distinguishes development-time focused checks from broader target/configuration checks. A scheme selects targets/actions; a test plan configures which tests run and how. Keep individual app/extension targets visible where useful and an intentional whole-product lane for release. Verify installed Xcode support before using tags or command flags from newer documentation.

## Plan the matrix deliberately

Use a small fast lane for domain/contract unit tests; integration tests for real client/server/store behavior; UI tests for actual user and system surfaces; and performance checks only with comparable scenarios. Include supported language/locale/accessibility configuration when it changes behavior. Do not turn every ordinary change into a full device farm run, but do not omit a touched extension merely because app tests pass.

Keep Node and native fixture results linked to the same contract revision. A generated Swift decoder success and a Node route success can disagree about null/default/error semantics; use shared semantic assertions. Physical-device behaviors, entitlements and OS scheduling remain distinct from simulator or pure-package results.

## Execution sequence

1. Read project instructions and current scheme/test-plan configuration. Inspect installed xcodebuild help and available destinations when a command example may vary by version.
2. Resolve the exact project or workspace, scheme, configuration and destination. Avoid ambiguous simulator names or choosing an unrelated booted device.
3. Run the smallest affected behavioral checks with an intentional result location. Preserve command exit status; a log formatter's success must not hide xcodebuild failure.
4. Inspect the result bundle and summary for failed, skipped, expected-failure and mixed outcomes. Do not collapse a mostly green navigator into all-tests-passed.
5. Run required coupled target/configuration checks after the last substantive change. Match reported evidence to the actual revision and test plan.
6. Keep safe artifacts sufficient to reproduce the failure, then scope cleanup to the paths/processes this task owns. Do not routinely erase all simulators or delete customer stores.

## Failure cases

| Observation | Honest interpretation |
| --- | --- |
| All selected tests pass | Only the selected tests/configuration passed |
| Target absent from scheme | No coverage of that target is established |
| Skipped or expected-failure tests | Preserve that status; do not count as ordinary successful assertions |
| Stale result bundle | Evidence may belong to an earlier revision/run |
| Simulator test passes | Device-specific capability or entitlement behavior remains separate |
| Node suite passes | Backend behavior tested there; no automatic native UI/platform conclusion |

## Handoff and remaining checks

Provide the command, toolchain, scheme/test plan/configuration/destination, actual result and relevant artifact path. State what used mocks, a real local server/store, a simulator or a physical device. If the host lacks Apple tools, give the precise remaining prerequisite while completing portable checks.

Avoid arbitrary sleeps for asynchronous test readiness. Use controlled completion signals and dependencies for network/job ordering. Performance claims require a comparable before/after capture and defined scenario; source inspection alone yields a hypothesis. This keeps the workflow fast without confusing convenient evidence with the product behavior it needs to establish.

## Sources and applicability

- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/tutorials/data/documentation/xcode/organizing-tests-to-improve-feedback.json) — `src_nm_xcode_testplans_final`.
- [Running tests and interpreting results](https://developer.apple.com/tutorials/data/documentation/xcode/running-tests-and-interpreting-results.json) — `src_nm_xcode_results`.
- [Test runner | Node.js v26.12.1 Documentation](https://nodejs.org/api/test.html) — `src_nm_node_test`.
- [Configuring your first Xcode Cloud workflow](https://developer.apple.com/tutorials/data/documentation/xcode/configuring-your-first-xcode-cloud-workflow.json) — `src_nm_xcode_cloud`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
