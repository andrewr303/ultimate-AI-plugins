# Screenshot clipper companion: reference implementation design

## Contents

topology; contract envelope; bounded transfer; idempotence and acknowledgement; MV3 outbox behavior; native organizer behavior; coexistence acceptance matrix.

This is an original design recommendation, not an implemented complete app or a platform protocol. Adapt it to the existing product and version the agreed contract before shipping.

## Topology and independent operation

```text
Browser capture -> durable extension outbox -> transport adapter
                                                |
                                       signed native host
                                                |
                                   bounded receiver / durable inbox
                                                |
                                      native organizer UI
```

Keep browser capture/export working without the Mac app. The companion adds native organization. Put shared schemas, fixture bytes, and pure domain logic in reusable modules; keep browser permissions and capture APIs in the extension. A small Swift host can reuse the app's native repository implementation; a Node adapter needs a bundled signed runtime and an explicitly supported receiver API. Do not manipulate an undocumented native framework database.

The receiver may be a background agent, an app service, or a deliberately coordinated on-demand import host. Make a decision based on whether receiving must continue after the UI quits. A browser-held native messaging port alone cannot guarantee availability after the browser exits. If the UI and import host share a database, use an explicit shared location, verified access rights, one schema/migration owner, transactional access and cross-process concurrency tests.

## Contract envelope

Use validated JSON with bounded fields and enumerated message types. Example negotiation request:

```json
{
  "protocol": "mac-clipper",
  "version": 1,
  "type": "hello",
  "requestId": "GENERATED_UUID",
  "payload": {"supportedVersions": [1], "capabilities": ["chunked-clips", "resume"]}
}
```

Negotiate a supported version, receiver readiness, maximum serialized frame bytes, total attachment bytes, image dimensions and in-flight transfers. A reply is correlated with `requestId`. Unknown required capabilities or unsupported versions produce explicit non-success responses; retain the outbox. Older releases must reject new required behavior safely. Do not negotiate authentication away.

Capture metadata should include a generated immutable `clipId`, a persisted `installationId`, source URL, title, UTC capture time, MIME type, actual byte length, pixel dimensions and SHA-256 checksum. Each attachment has its own ID. Decide whether to strip URL query parameters, fragments or location metadata; preserve original source only when consistent with the product's privacy choices. Never upload to a cloud service by default merely to bridge local components.

Recommended message family:

| Message | Receiver action |
| --- | --- |
| `hello` | Negotiate capabilities and limits; no storage mutation |
| `beginClip` | Validate metadata, reserve bounded transfer, return missing chunks or committed status |
| `clipChunk` | Decode bounded bytes, validate index and checksum, persist a chunk idempotently |
| `commitClip` | Verify byte count and full checksum; atomically create clip and import record |
| `getClipStatus` | Return durable status for a lost reply or resume |
| `cancelClip` | Remove only this transfer's temporary data, respecting authorization |

This command set is illustrative. Implement request and response schemas and fixtures in both languages; do not leave it as prose only during an app build.

## Bounded transfer

Conservative starting application limits: 256 KiB raw chunks, one active transfer per extension instance, 50 MiB per clip and a finite pending byte budget. These are product defaults, not browser limits. Negotiate smaller limits and keep serialized frame bytes below the receiver limit in **both** directions. Base64 adds about one third plus JSON overhead; measure encoded bytes, not JavaScript string length. Small acknowledgements should never echo screenshot data.

Reject length headers before allocating large memory. Decode and validate JSON with limits before processing; check type, required fields, integers, lengths, MIME, checksum and supported version. Reject invalid base64, conflicting duplicate chunks and impossible counts. Check image signatures and decoded dimensions; cap decompression/pixel memory. Generate storage names internally. Do not accept arbitrary paths, symlinks, SQL, code, unbounded URLs or file reads from the browser.

Write incoming bytes into private, quota-controlled temporary storage. Persist enough state for a bounded resume window; expire abandoned transfers predictably. Finalization verifies all bytes and commits the record, attachment and deduplication key durably before replying with `committed`. Crash recovery must reconcile temporary files and database transactions. If attachment storage is separate, use a crash-safe staging/finalization strategy and test every crash point. Never acknowledge a queued UI event as a completed import.

## Idempotence and acknowledgement

Persist `(installationId, clipId)` as a unique import key. The same key with matching immutable content returns the existing result. The same key with different bytes is a conflict. A separate duplicate-content feature may use checksums, but must not silently collapse intentional repeated captures. Store `clipId` before the first attempt; never generate a new ID just because a connection dropped.

Normal flow:

1. Capture and durably store bytes plus metadata in the extension's outbox.
2. Negotiate, send metadata, send bounded chunks with backpressure, request commit.
3. Receiver verifies and durably commits once, then returns the canonical item ID.
4. Extension persistently marks delivered before reclaiming attachment storage according to retention policy.

When the commit reply is lost, reconnect and query status or resend the same ID. Promise **at-least-once attempts with idempotent import**, not magical exactly-once delivery. Preserve pending data until a verified commit or explicit user discard. Surface storage-full states immediately; do not silently evict pending clips. Expiration, discard and export need clear user behavior.

## MV3 outbox behavior

Use IndexedDB for transactional metadata and binary blobs when appropriate; use extension storage for small settings. Do not place large screenshots in sync storage. Persist state changes before asynchronous delivery. Reload pending work on worker startup, reconnect and explicit retry. Bound retries with exponential backoff and jitter, and distinguish retryable receiver-unavailable/disk-full conditions from permanent invalid input/protocol mismatch. Resume without relying on globals or long timers. Avoid concurrent outbox drains with a serialized transactional lease or equivalent.

Do not send incognito/private-window captures into the regular library without an explicit product choice and disclosure. Scope installation/profile identity deliberately so work and personal browser profiles do not accidentally merge. Keep on-device pending data recoverable through an export route when the helper is absent for a long time.

## Native organizer behavior

Show imported clips immediately after the canonical store commits. Decode thumbnails and perform OCR/indexing on bounded workers; cancellation and retry must not create duplicate imports. Retain originals and store derived files separately. Collections/tags, source links, search, preview, delete/restore, export and backup should use stable item identities. Show failed indexing independently of successful import so users do not lose captured images when OCR fails.

## Coexistence acceptance matrix

| Scenario | Required observation |
| --- | --- |
| Mac app absent | Original capture/export works; companion delivery is visibly unavailable/pending |
| App UI closed, receiving enabled | Clip reaches durable inbox; opening UI reveals the same item |
| Receiving explicitly disabled | No hidden helper restart to override user choice; outbox remains recoverable |
| Browser/worker killed mid-transfer | Partial transfer can resume/retry without losing original bytes |
| Receiver killed before commit | No success reply; recovery can retry the same ID |
| Receiver committed, reply lost | Retry returns same canonical item, exactly one imported row |
| Disk or browser quota exhausted | Actionable error; no false success or silent pending-data eviction |
| Huge or corrupted image | Bounded rejection; no memory spike, crash or arbitrary file creation |
| Out-of-order/duplicate/conflicting chunk | Defined response, consistent transfer state, no corrupted final clip |
| Unsupported protocol version | Clear incompatibility; pending clip preserved; original extension works |
| App N with extension N-1 and reverse | Explicit tested compatibility or safe rejection |
| Native messaging host path changed | Integration repair works or gives actionable error |
| Two browser profiles / private window | Storage and privacy behavior matches documented scope |
| Network disconnected | Local transfer/import works; remote enrichment queues separately |
| App/extension removed or upgraded | Original data preserved; owned registrations cleaned/repaired only |
| Chrome production ID vs unpacked ID | Expected allowlist behavior; no development identity in release |
| Safari port, if supplied | Its native adapter and manifest are tested independently |

Use real Chrome/Safari and the installed signed app on a Mac for final integration evidence. Parser tests, mocks and a Linux build validate narrower claims. Record browser, OS, SDK, architecture, app/extension versions, steps, screenshots/log IDs and the actual observed result. Never describe the full system as verified when only its wire codec was exercised.
