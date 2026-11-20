---
name: backend-background
description: "Use when designing bounded iOS background refresh/processing, background URLSession transfers or offline reconciliation with a Node service, including an existing CloudKit sync boundary. Do not create indefinite phone workers, promise OS scheduling or introduce a second authoritative data plane without a requirement."
---

# Background transfer and offline reconciliation

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Identify the user-visible work, current persistence/session, server authority and the actual Apple execution mechanism. Keep processing, transfer, silent push and finite foreground continuation distinct.
2. Specify durable operation identity, checkpoint/cursor, expiry, authorization and exactly what local/server state commits together. Choose useful offline and missed-wakeup behavior.
3. Implement cooperative expiration/cancellation and one owned completion signal. Use stable background session identifiers, file lifetimes and supported upload/download paths when transferring files.
4. If CloudKit exists, preserve its account/database semantics and persisted engine state. Define one authoritative owner and explicit conflict/recovery policy rather than assuming an atomic Node/CloudKit transaction.
5. Test partial progress, duplicate wakeups, expired credentials, account switching, force-quit versus system termination and recovery. Use actual device checks for scheduling, protection and transfer behavior.

## Load the relevant reference

- [Bounded work, expiration and recovery](../../references/background/bounded-reconciliation.md)
- [Background file-transfer lifecycle](../../references/background/file-transfer-lifecycle.md)
- [CloudKit and Node ownership](../../references/background/cloudkit-and-node-ownership.md)

## Complete with evidence

Return the work/checkpoint state machine, authoritative data boundary, expiration/retry behavior, tests and exact remaining Apple-runtime verification. A background request or push send is not evidence the app ran.

Source observations and availability are recorded in the references and [source registry](../../research/sources/sources.jsonl). Multiple Apple pages do not count as independent author corroboration.
