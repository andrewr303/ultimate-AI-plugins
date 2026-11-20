# Image lifecycle, memory and verification

Make the request identity visible in the app's data flow: content identifier, account, revision, dimensions and processor options. A view's stable identity should represent the same logical item, while a changed request must replace the previous state. Do not fix stale avatars by attaching random `.id(UUID())` values that defeat reuse and launch extra work.

## Cancellation and reuse

The uploaded LazyImage defaults to canceling on disappearance. Its onDisappear behavior can lower priority, cancel or be disabled. Use the pinned release's lifecycle surface rather than starting a second manual task in onAppear for the same URL. A late completion must not update the wrong row or account. State belongs to the request generation that initiated it.

For custom state, inspect FetchImage's actual isolation requirements. Its reset and cancel operations have different presentation effects: reset clears state while cancel preserves already displayed content in the documented snapshot. Define whether replacing an image should show the old content as a placeholder. Keeping old private content during an account switch is rarely appropriate.

Cancellation is normal control flow. Do not report it as a user-facing server error or automatically retry it. If an operation intentionally continues offscreen, it needs a bounded owner and priority rather than an unretained background task. Confirm this behavior when rapidly navigating and when the app enters the background.

## Prefetch deliberately

The inspected ImagePrefetcher owns its work and cancels outstanding tasks on deinitialization. Keep a retained instance at list/service scope. Bound the prefetch window, cancel items that move out of range and use the same pipeline/request variants as display. Prefetching every item in a large feed wastes bandwidth and memory.

Disk-only and decoded-memory destinations have different CPU/memory costs. Choose based on the measured bottleneck and cache configuration. Do not claim scrolling improvement based solely on adding a prefetch call. Observe cache hit rate, network count, decode time and peak memory under a realistic feed and device class.

## Large and private media

A compressed file's byte count is not its decoded memory footprint. Decode thumbnail variants, limit simultaneous large work and use server resize endpoints when the API provides them. Avoid holding large UIImage/Data copies in view state and persistence simultaneously. Animated media and video require their own budget and lifecycle checks.

Cache cleanup must respect scope: remove the intended account's private media without wiping unrelated app data. Verify logout, account switching, revoked media access and expiry behavior. Disk files may be purged by the operating system; cache presence cannot be a durable offline storage guarantee. Store required offline assets through an explicit persistence policy instead.

## Verification matrix

| Fixture | Expected observation |
| --- | --- |
| A row URL changes while old request is delayed | New request owns content; late old result cannot replace it |
| Nil URL then valid URL | No permanent stale error; valid request loads |
| Success followed by failed replacement | Policy for old content is explicit; no wrong-avatar residue |
| Memory cache hit | No unnecessary network request or placeholder flash |
| Rapid scroll away/back | Work follows chosen cancellation/priority behavior |
| Large photo and animated item | Decode and playback remain within measured memory budget |
| Same path, different signed-in user | Cache and displayed content remain isolated |
| Offline and expired HTTP cache | Behavior matches configured stale/cache policy |

Inject data loader/cache fixtures or use the package's supported test seam. Test state transitions at the app boundary; do not mirror all upstream internals. Uploaded `Tests/NukeUITests/LazyImageRequestLifecycleTests.swift` and `FetchImageStateTransitionTests.swift` provide inspected examples of nil requests, replacement, progress and cache-hit cases, but their tests were not executed here.

Use Instruments and real-device scrolling for performance conclusions. Simulator screenshots can validate presentation, not prove energy, low-memory behavior or network efficiency. Record device, OS, data set and before/after measurements when reporting a performance change.

Provenance: uploaded Nuke files above and Sources/Nuke/Prefetching/ImagePrefetcher.swift; original synthesis. See [source map](../../../docs/source-map.md).
