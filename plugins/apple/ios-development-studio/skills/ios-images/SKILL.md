---
name: ios-images
description: "Implement and diagnose image loading in native iOS apps: Nuke/NukeUI integration, image sizing, request lifecycle, caches, prefetching and scrolling correctness. Use for image delivery or memory issues, not image generation or a default dependency replacement. Route general HTTP clients to ios-networking."
---

# iOS image loading

First read [the operating contract](../ios-development/references/operating-contract.md).

## Workflow

1. Inspect deployment targets, resolved package versions, existing image loader, image dimensions and scrolling behavior. Reuse an established loader unless the user requests a change or the requirement cannot be met.
2. Read [pipeline integration](references/pipeline-integration.md) for Nuke APIs, release boundaries and cache choices. Read [lifecycle and verification](references/lifecycle-and-verification.md) when diagnosing reuse, memory, stale images, offline handling or prefetching.
3. Make request identity, account isolation, display size and placeholder/error states explicit. Size decoding/processing for the destination and keep work out of view body evaluation.
4. Implement shared ownership of the pipeline and requested caching behavior. Connect cancellation and state replacement to row/view identity; use a retained prefetcher only when it serves a measured need.
5. Verify rapid reuse, changed URLs, missing data, failures, cache hits and large media. Measure real-device memory/scroll performance when available. Static inspection cannot prove memory or smoothness.

## Boundaries and output

Uploaded Nuke main is a development snapshot, not a verified release recommendation. Check the pinned API; source declarations override stale README prose. ExyteChat already uses Kingfisher internally, so adding Nuke only supplies an additional pipeline unless integration is changed deliberately.

Do not turn private media into public URLs, bypass certificate validation, or log signed query strings. Finish with behavior, package assumptions, validation and unmeasured performance. See [source map](../../docs/source-map.md).
