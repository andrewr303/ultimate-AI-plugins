---
name: backend-live-activities
description: "Use when integrating ActivityKit lifecycle, Live Activity ContentState, rotating activity tokens or server APNs start/update/end jobs with a Node.js backend. Do not treat Live Activity UI as a network client, a widget timeline or a durable backend operation."
---

# Live Activity state and server updates

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Resolve the durable event, app/account, activity instance, current authorization, supported SDK/runtime and actual server push adapter.
2. Define static attributes and compact dynamic ContentState with matching Node/native JSON fixtures. Model stale and final states independently of whether the surface is visible.
3. Register the correct activity/update/start token or supported channel; observe asynchronous rotation and keep provider credentials server-side. Select the exact payload/header path supported by the target runtime.
4. Coalesce obsolete updates, preserve final state, and reconcile ongoing instances after app/server restarts. User dismissal must not silently cancel the underlying business event.
5. Test payload decoding, token rotation, start/update/end ordering, denied authorization, stale content and uncertain delivery. Separate transport tests from a real ActivityKit/device verification lane.

## Load the relevant reference

- [State, authorization and lifecycle](../../references/live-activities/state-and-lifecycle.md)
- [APNs wire contract and token roles](../../references/live-activities/push-contract-and-tokens.md)
- [Freshness, ending and recovery](../../references/live-activities/freshness-and-recovery.md)

## Complete with evidence

Return the state/token/job contract, lifecycle and freshness policy, exact observed provider/native state, tests and unsupported-runtime fallbacks. No native network access or timing guarantee is inferred.

Source observations and availability are recorded in the references and [source registry](../../research/sources/sources.jsonl). Multiple Apple pages do not count as independent author corroboration.
