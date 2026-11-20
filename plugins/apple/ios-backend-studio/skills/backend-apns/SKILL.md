---
name: backend-apns
description: "Use when implementing or debugging a Node.js APNs provider, device registration, token/topic/environment scope, notification jobs or delivery recovery for an iOS app. Keep Live Activity state specifics in backend-live-activities; do not use for generic web push, app-store submission or unrequested live sends."
---

# APNs provider and recipient lifecycle

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Resolve the app/team/topic/environment, current provider adapter, registration store and requested endpoint. Inspect actual transport/library versions and signing configuration without printing keys or addresses.
2. Separate the durable business event, notification job, provider attempt and any observed device action. Pick the proper notification kind, expiry, collapse behavior and retry policy.
3. Implement server-held credential/signing and compatible HTTP/2 pool handling, then an authenticated recipient-registration lifecycle. Keep app notification and ActivityKit token roles distinct.
4. Classify actual provider responses and uncertain completion before retry. Revalidate queued work against registration/account changes and preserve a foreground reconciliation path.
5. Test request serialization, token rotation, wrong scope, duplicates, expiry, outage and account switching using a controlled clock/transport. Use an already authorized sandbox/device lane only when relevant.

## Load the relevant reference

- [Provider transport and credentials](../../references/apns/provider-transport.md)
- [Device registration and account scope](../../references/apns/registration-and-account-scope.md)
- [Delivery and recovery state](../../references/apns/delivery-and-recovery.md)

## Complete with evidence

Return changed provider/client boundaries, exact topic/environment assumptions, classified job/receipt states, tests and the furthest delivery layer actually observed. Provider acceptance is not proof of display.

Source observations and availability are recorded in the references and [source registry](../../research/sources/sources.jsonl). Multiple Apple pages do not count as independent author corroboration.
