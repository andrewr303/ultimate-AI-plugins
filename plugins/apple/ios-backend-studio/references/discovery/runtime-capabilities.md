# Runtime capability evidence

## Treat readiness as a set of separate observations

Before selecting an integration, distinguish what configuration requests, what tools can execute, what the runtime supports, what authentication can access and what a real operation has demonstrated. These are separate facts. A service SDK in a lockfile cannot prove account readiness; a successful token parse cannot prove access to an entity; a recent upstream commit cannot set the app's deployment target.

Use an explicit capability record:

| Capability | Minimum useful evidence | What it does not establish |
| --- | --- | --- |
| Node executable | Actual version/help in the selected environment | Production image or framework compatibility |
| Service framework | Resolved package/version and current entrypoint | That middleware or routes are registered correctly |
| HTTP transport | Actual adapter and protocol configuration | Automatic retry safety or all provider protocol requirements |
| Database/worker | Existing binding plus a scoped authorized check | Durable domain semantics after crash/retry |
| Apple build | Selected Xcode, SDK, scheme, configuration and result | Physical-device behavior or provider delivery |
| Extension capability | Target membership, entitlements and device/runtime support | Guaranteed scheduling or access while locked |
| Provider/account | Intended account/environment plus observed scoped access | Permission for an unrelated mutation or billable resource |

Keep observations narrow. If only a declaration is available, say “configured” or “declared.” If an operation ran, identify the exact environment and outcome. Do not label unknown, skipped or unavailable evidence as ready.

## Inspect the selected runtime

Read the project's runtime policy and lockfiles, then check the executable already chosen for that project. Ordinary local discovery can include `node --version` and the installed tool's help. Never print `process.env` or run a broad configuration dump. A build-time Node process and the deployed service process can differ; inspect the actual image or configured runtime before relying on a feature.

Verify protocol behavior at the adapter seam. HTTP/1 and HTTP/2 are different interfaces; an API named “fetch” is not proof of a required provider transport. Confirm request limits, connection lifecycle, timeout, cancellation and response/error mapping from the chosen runtime and provider contract. A timeout means the result can be uncertain, especially after a remote write.

## Verify native availability at the correct layer

Separate compiler syntax support, framework/API availability, app deployment support and runtime/user authorization. Compile against the selected SDK where available and provide a supported fallback instead of raising targets to avoid a diagnostic. Widgets, App Intents and background APIs have their own registration and lifecycle; they cannot inherit execution privileges from a Node backend.

The Linux package-build environment can run relevant portable examples and tests. It cannot establish Xcode build success, signing, extension entitlements, physical-device background behavior or real APNs delivery. Keep these as named pending checks, or use existing authorized remote infrastructure. Do not create a paid cloud simulator or a new account as an automatic substitute.

## Turn a missing capability into a bounded next step

Identify the missing fact, its affected behavior and an independent action that can continue. For example, an unavailable Mac leaves native compilation pending while wire-fixture and server authorization tests proceed. Missing production credentials should not block a local fake-transport test. Execute an external readiness check only within its account and authorization scope, and retain redacted receipts rather than credential values.

Sources: src_nm_node_process — [Node process](https://nodejs.org/api/process.html); src_nm_node_http — [Node HTTP](https://nodejs.org/api/http.html); src_nm_node_http2 — [Node HTTP/2](https://nodejs.org/api/http2.html); src_backend_apple_021 — [Background strategy selection](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app); src_nm_xcode_results — [Native test results](https://developer.apple.com/tutorials/data/documentation/xcode/running-tests-and-interpreting-results.json).
