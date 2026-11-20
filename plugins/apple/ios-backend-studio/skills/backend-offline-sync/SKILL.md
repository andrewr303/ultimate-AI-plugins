---
name: backend-offline-sync
description: "Use to implement or debug native offline writes, durable outboxes, replay, conflicts, cursors and app/extension snapshots against a Node backend. Preserve the existing persistence/sync provider; do not promise exact background scheduling, silently discard pending edits or add a managed sync service by default."
---

# Offline state and synchronization

First read the [operating contract](../../references/operating-contract.md).

1. Identify the local store, authoritative backend, account lifecycle, sync adapter and supported old payloads. Define what accepted, committed and synchronized mean for the feature.
2. Use [the outbox protocol](../../references/offline-sync/local-outbox-protocol.md) for durable operation identity, admission and acknowledgement.
3. Use [conflicts and convergence](../../references/offline-sync/conflicts-and-convergence.md) to handle stale edits, tombstones, reset cursors and invalid work without losing pending intent.
4. Use [extension snapshots and adapters](../../references/offline-sync/extension-snapshots-and-sync-adapters.md) for app groups, bounded system surfaces and optional sync products.
5. Verify process death, lost responses, duplicates, out-of-order delivery, sign-out and old snapshots using controlled completion and a real persistent store where needed.

Return the state/acknowledgement contract, implementation, recovery behavior and actual evidence. A queued request, successful HTTP transfer, backend admission and durable domain commit are different observations.
