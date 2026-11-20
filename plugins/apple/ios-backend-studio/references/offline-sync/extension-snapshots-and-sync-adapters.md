# Extension snapshots and optional synchronization adapters

## Separate processes and workloads

Map which process writes authoritative local state and which surfaces consume snapshots: main app, widget extension, App Intent, Live Activity and any companion app. They can have different execution, entitlement, device-lock and authentication conditions. A backend or sync SDK does not make those conditions interchangeable.

Prefer a deliberately small, immutable presentation snapshot for a surface that only needs a few values. Include a representation version, account scope and freshness marker; omit access tokens, private provider payloads and data the surface should not show while locked. Define a safe empty, stale, signed-out and decoding-failure view. Do not let a previously rendered snapshot become proof of current backend permission.

## Shared storage is a contract

Use the actual app-group container and the existing persistence engine's supported coordination mechanism. Do not point several processes at an arbitrary SQLite path or share live managed objects across contexts. An actor in one process cannot coordinate a writer in another process. Verify target membership, entitlements, container resolution and data protection on the appropriate Apple environment.

Write snapshots atomically or through a store transaction so a reader does not decode a half-written file. If a representation evolves, test an older reader and a newer writer according to the supported release window. Keep path names and serialized types stable deliberately; a new app build may coexist with an older extension or cached timeline entry.

| Snapshot event | Required behavior |
| --- | --- |
| App receives new server state | Commit domain state, then publish the intended consistent snapshot |
| Device locks | Respect the chosen data-protection and visible-content policy |
| Account changes | Invalidate/re-scope the snapshot; ignore obsolete async completion |
| Store migrates | Preserve a readable fallback and coordinate the actual engine |
| Backend unavailable | Show accepted freshness/error behavior rather than an invented live value |

The app can request a refresh when data changes; that is not a promise that the system runs the extension at an exact time. Keep network work bounded and use platform-supported background opportunities only when the feature calls for them.

## Optional provider adapters

For an existing synchronization product, inspect its installed SDK, backend protocol, database requirements, authentication, upload completion and conflict handling. Preserve the current product unless a migration requirement justifies replacement. Identify service cost, self-hosting obligations, server/database compatibility and data handling before adding an optional service.

PowerSync is an inspected example of a connector boundary. Its Swift connector obtains sync credentials and uploads local changes to the app's backend. That does not mean the product owns the app's authorization or every business mutation. Upload acknowledgement and local completion still need the correct durable server outcome. Use the stable supported interface in the resolved release; a current main example may expose alpha checkpoint behavior or a deprecated base class.

If the backend applies uploads asynchronously, prove the adapter's checkpoint/causal contract before marking local work complete. An HTTP admission receipt and a checkpoint that establishes visibility are different concepts. Do not add an undocumented arbitrary delay and assume remote changes have converged.

For a custom adapter, keep transport, credentials, durable outbox and local projection as explicit seams. Server changes should be applied with a version/progress boundary and produce the same product behavior when duplicated or delivered late. Do not let an SDK-specific type leak throughout the domain solely to simplify an example.

## Verification and release checks

Test the main app and the relevant extension against absent, old and malformed snapshots; signed-out/account-switched state; device lock; store migration; and interrupted publication. Verify every affected target builds with actual entitlements and selected SDK. Use deterministic adapter fixtures for retry, duplicate and checkpoint transitions, then run authorized integration checks against a known test environment.

Portable source/package tests cannot prove real app-group access, system refresh scheduling or a provider's production sync behavior. Record which layer was tested. Give the consuming app a useful local fallback even when a remote service or entitlement is unavailable.

## Evidence and version cautions

`src_backend_apple_026` is Apple's [app-group container lookup](https://developer.apple.com/documentation/foundation/filemanager/containerurl(forsecurityapplicationgroupidentifier:)); `src_backend_apple_021` discusses [background strategy selection](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app). `src_backend_repo_073` is the pinned [PowerSync connector source](https://github.com/powersync-ja/powersync-swift/blob/b77dc2f00366db9540f2ecd3903cfefb63fc29e8/Sources/PowerSync/Protocol/PowerSyncBackendConnector.swift). These inform original lifecycle guidance; verify SDK availability and actual provider behavior using the [catalog](../../research/sources/sources.jsonl). No Apple entitlement or remote sync session was exercised by this source review.
