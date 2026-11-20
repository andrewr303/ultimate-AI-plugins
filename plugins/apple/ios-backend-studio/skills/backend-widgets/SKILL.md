---
name: backend-widgets
description: "Use when connecting WidgetKit timelines, snapshots, interactive widgets, shared app-group projections or widget deep links to a Node.js backend. Do not make widgets poll continuously, replace ordinary app UI or treat a reload request as guaranteed realtime delivery."
---

# Widgets backed by shared domain state

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Inspect target membership, supported families/runtime, existing app-group/persistence design, account scope and the authoritative backend resource.
2. Define a compact versioned read projection with useful placeholder, signed-out, stale and offline states. Generate timelines for predictable changes and keep system scheduling discretion explicit.
3. For actions, use a typed intent that invokes the same authorized domain service as the app. Reconcile optimistic UI with server acknowledgment/error and persist timeline-visible state before reporting completion.
4. Decode deep links as untrusted typed routes and recheck current entity/account access. Distinguish a native Mac widget from an iPhone widget displayed on Mac.
5. Test old snapshots, account changes, delayed/reversed responses, duplicate commands, missing entitlements and process interruption. Build affected targets and inspect native presentations where available.

## Load the relevant reference

- [Snapshots, freshness and refresh](../../references/widgets/snapshots-and-refresh.md)
- [Interactive commands and reconciliation](../../references/widgets/actions-and-reconciliation.md)
- [Shared state, routing and Mac context](../../references/widgets/shared-state-and-routing.md)

## Complete with evidence

Return the projection/command contract, cross-process ownership, refresh/fallback behavior, tests and any pending Apple-runtime checks. Do not promise a server-controlled exact refresh schedule.

Source observations and availability are recorded in the references and [source registry](../../research/sources/sources.jsonl). Multiple Apple pages do not count as independent author corroboration.
