# Native media transfer without losing ownership or local files

## Map the native lifetime

Inspect how the app acquires the file, its sandbox/provider access, the selected networking library, foreground/background requirements and the server's upload-session contract. A temporary picker URL or in-memory buffer may not remain available after the initiating view disappears or the process is suspended.

Copy or otherwise retain the approved input through the app's supported storage/access mechanism for as long as the transfer needs it. Keep a stable local transfer identity linked to the backend session and account. Respect device-lock/data-protection and privacy requirements. Do not turn an arbitrary user-selected path into a server storage key or embed a provider signing key in the app.

## Choose the supported transfer path

For a foreground request, use the existing transport with cancellation, body size and progress handling. For an actual background-transfer requirement, inspect the selected Apple API's file-backed upload, delegate, configuration-identifier and relaunch requirements. Do not assume a Data or stream upload automatically survives process termination, or that a generated HTTP transport supplies background execution by itself.

Keep backend API requests separate from storage-capability requests. The latter should send only the method/headers/body required by the signed transfer contract. A global Authorization/cookie middleware must not forward the app's backend session to a storage host. Handle redirects according to the signed operation and transport policy; do not casually replay credentials or a single-use body to an unexpected host.

| Transfer state | Durable app state | User-visible behavior |
| --- | --- | --- |
| Preparing | Account, local file and intended session linked | Clear preparation/cancellation outcome |
| Uploading | Transfer/session identity and progress source retained | Observed progress, not an invented completion estimate |
| Interrupted/unknown | Input and reconciliation state remain available | Retry/resume according to actual provider support |
| Bytes received | Server object may exist but is not necessarily approved | Finalization/processing state shown separately |
| Ready | Verified domain asset result stored | Presentation consumes the approved representation |
| Rejected/expired | Repair/cleanup decision preserved | Actionable retry/reselect/auth state |

## Expiration, retries and finalization

A signed URL can expire while the app waits for network or background execution. Refresh access through the authorized backend session flow only if the upload is still admissible. Keep the logical asset/session identity stable where the protocol permits it. Do not create a new domain record for every network retry.

When an upload reports success, ask the backend to verify/finalize the expected owned object or reconcile the session result. A timeout during finalization can leave a committed asset with a lost response; recover by session/operation identity. For a resumable/multipart protocol, retain the exact provider state needed by that protocol and verify its integrity/expiry behavior; a generic retry flag is not resumability.

Cancellation should stop work the app owns and update a recoverable state. It does not prove already-uploaded bytes or a backend effect were rolled back. Cleanup local files and abandoned remote objects only under the selected session/retention policy, avoiding deletion of a file still needed by another owned transfer.

## Account and extension boundaries

Bind every asynchronous completion to the initiating account/session generation. After sign-out or account switch, an old transfer must not associate its result with the new account, refresh old credentials or repopulate the new user's cache. Preserve or remove unsent data according to the actual product/privacy policy rather than silently dropping it for convenience.

An extension can have a different process/container/lifetime. Use the intended app-group container and supported background-transfer configuration when sharing work is required. Do not reuse a configuration identifier or mutable in-memory task owner across processes without verifying platform behavior. Widgets should consume a small approved snapshot/variant rather than owning an unbounded media pipeline.

## Acceptance checks

Test app/view disappearance, temporary-source loss, process interruption, device lock, network changes, expired capability, wrong upload headers, a lost finalization response, duplicate finalization and sign-out during progress. Verify that private URLs/tokens do not enter logs, screenshots or analytics. Check loading/error/retry behavior and accessible progress separately from network correctness.

Run real device/appropriate simulator tests for background callbacks, file protection and relaunch behavior. Portable package tests or an inspected Swift source fragment cannot establish those Apple runtime paths. Record exact target, OS/SDK, transfer mode and provider environment when reporting success.

## Evidence and version cautions

`src_backend_apple_023` and `src_backend_apple_024` identify Apple's [background file-transfer guide](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background) and [background URLSession configuration](https://developer.apple.com/documentation/foundation/urlsessionconfiguration/background(withidentifier:)). `src_backend_repo_045` is the inspected [generated-client URLSession transport](https://github.com/apple/swift-openapi-urlsession/blob/c97e0f0187d95542b4a254f5bb4dc67f43bf73c9/Sources/OpenAPIURLSession/URLSessionTransport.swift); `src_backend_extra_s3_presigned` is [capability-expiry guidance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html). See [source records](../../research/sources/sources.jsonl). Preserve the app's resolved SDK/library and verify its actual background-transfer contract; these sources do not establish a completed device test.
