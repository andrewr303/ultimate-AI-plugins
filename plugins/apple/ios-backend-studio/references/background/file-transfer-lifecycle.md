# Background uploads/downloads and durable file state

## Inputs and outputs

Inputs: transfer metadata, authorized remote resource, an owned file path, stable session identifier and an account-scoped persistence record. Outputs: a system-owned transfer, a reconciled local/server record and an accessible final file.

## Workflow

1. Use a small deliberate set of background URLSession configurations with stable identifiers. Recreate the matching session during relaunch to reconnect to transfers that the system still owns.
2. Supply the required delegate and retain the app/extension completion handler until all relevant events are handled. Complete on the expected UI lifecycle queue rather than casually assuming the callback executor.
3. Use a file-backed upload for work that must survive app exit. A Data/stream upload is not equivalent to a background file upload.
4. Move or persist a downloaded temporary file before its delegate callback returns if it must remain available. Commit the associated domain state only after validation and file handling succeed.
5. Use a matching shared-container configuration when an extension/app legitimately share transferred files. Keep session identifiers and transfer ownership distinct between processes.
6. Give Node endpoints compatible resumption, content validation, idempotency and authorization behavior. Consider expiry of signed URLs or access credentials when the system delays a transfer; avoid assuming the request begins immediately.

## Important limitations

Apple background transfers use a separate process and support HTTP/HTTPS with delegate delivery. The current article says redirects are followed without the normal task redirection callback; a background transfer must not rely on that callback as its only redirect policy boundary. User force-quit and ordinary system termination have different behavior: the background-configuration page explicitly says force-quit cancels transfers and prevents automatic relaunch until the user opens the app.

## Failure cases and tests

Test termination/relaunch, user force-quit, expired authorization, redirect targets, partial bytes, integrity failure, disk-full/move error and a completion handler reached through multiple paths. Distinguish the Node upload commit receipt from transfer progress and UI presentation. `earliestBeginDate` is not an exact start timer.

## Node endpoint and local file decisions

Define the upload/download resource, expected content identity, finalization semantics, access scope and how long authorization remains useful. A background session may start later than a foreground request. If signed URLs expire, provide a supported restart/resume path rather than logging or extending them indiscriminately.

A temporary download location is not durable app state. Verify content/size/integrity according to the product, move the file within the callback lifetime when retaining it, and record the durable association only after that operation succeeds. Keep app-group and per-process session ownership explicit when extensions also transfer files.

## Acceptance matrix

| Case | Expected outcome |
| --- | --- |
| System terminates app during transfer | Matching stable session reconnects when the platform relaunches it |
| User force-quits app | Product does not promise automatic restart |
| Authorization expires before actual start | Supported failure/re-auth/resume path |
| Redirect changes origin or resource scope | Endpoint design remains safe without relying solely on an unavailable redirect callback |
| Disk fills or file move fails | No false completed attachment/resource state |
| Two callbacks converge on completion | One owned completion signal and correct durable state |

Test file validation and state transitions independently. A successful server upload fixture cannot establish iOS background transfer or protected-file access behavior.

## Platform and verification boundary

`background(withIdentifier:)` metadata lists iOS/iPadOS 8 and macOS 10.10 introductions, with other platform entries in the source index. Its iOS termination semantics should not be extrapolated blindly to every platform/extension. Verify the actual SDK, target and delegate APIs.

## Primary evidence

- `src_backend_apple_023` — [Downloading files in the background](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background)
- `src_backend_apple_024` — [background(withIdentifier:)](https://developer.apple.com/documentation/foundation/urlsessionconfiguration/background(withidentifier:))
- `src_backend_apple_025` — [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)

These sources are Apple-authored primary evidence, not multiple independent organizations. A successful Node test cannot establish Apple device scheduling, target entitlements or UI behavior.


Read the [shared operating contract](../operating-contract.md) and use the [registered source records](../../research/sources/sources.jsonl) for provenance. Availability observations are source-specific; verify the selected SDK and runtime.
