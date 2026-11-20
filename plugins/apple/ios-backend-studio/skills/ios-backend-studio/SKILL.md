---
name: ios-backend-studio
description: "Use for end-to-end native iOS and Node.js backend integration, an unfamiliar multi-client project, or choosing the right specialist. Preserve existing frameworks and providers. Do not activate for unrelated frontend styling, an Android-only task, or generic Apple policy submission work."
---

# iOS Backend Studio

First read the [operating contract](../../references/operating-contract.md). Carry the user's requested behavior through implementation and relevant verification; discovery and planning support that result.

1. Establish the app/service/client boundaries and an observable acceptance condition using [intake and acceptance](../../references/studio/intake-and-acceptance.md). Inspect current changes, project instructions and supported versions before selecting tools.
2. Use `backend-discovery` when the actual topology, runtime or provider capabilities remain unknown. Keep unknown account/deployment facts explicit while continuing independent local work.
3. Assign wire, domain state, authentication, side-effect and release ownership using [ownership and handoffs](../../references/studio/ownership-and-handoffs.md). Choose one primary specialist below and a supporting skill only for a distinct concern.
4. Build a representative [vertical slice](../../references/studio/vertical-slice-delivery.md), including denied access, duplicate/stale work and old-client behavior where relevant. Preserve app, extension, server and other-client process boundaries.
5. Run meaningful checks with `backend-cross-platform-qa`, then report the completed behavior, exact evidence and remaining native/provider gates. Do not infer production success from static types or package checks.

| Actual concern | Primary specialist |
| --- | --- |
| Project topology, versions, configured providers and available execution surfaces | [backend-discovery](../backend-discovery/SKILL.md) |
| Cross-client behavior, failure cases and release evidence | [backend-cross-platform-qa](../backend-cross-platform-qa/SKILL.md) |
| Service/app/module ownership and staged architecture evolution | [backend-architecture](../backend-architecture/SKILL.md) |
| Server data integrity, transactions and durable domain state | [backend-data](../backend-data/SKILL.md) |
| Offline outboxes, reconciliation and conflict policy | [backend-offline-sync](../backend-offline-sync/SKILL.md) |
| Retry bounds, idempotence, recovery and job lifecycle | [backend-reliability](../backend-reliability/SKILL.md) |
| Signed provider events, ingress, ordering and acknowledgments | [backend-webhooks](../backend-webhooks/SKILL.md) |
| Upload/download, media authorization and object lifecycle | [backend-media](../backend-media/SKILL.md) |
| Node HTTP handlers, validation, errors and runtime behavior | [backend-node-api](../backend-node-api/SKILL.md) |
| Shared wire schema and generated Swift/TypeScript clients | [backend-contracts](../backend-contracts/SKILL.md) |
| Selected Xcode targets, schemes, results and native build failures | [backend-xcode](../backend-xcode/SKILL.md) |
| Mac toolchain/environment and optional developer tooling | [backend-mac-tooling](../backend-mac-tooling/SKILL.md) |
| Authorized deployment, rollout and recovery | [backend-deploy](../backend-deploy/SKILL.md) |
| Bounded logs, correlation and operational diagnosis | [backend-observability](../backend-observability/SKILL.md) |
| APNs provider delivery and token/environment handling | [backend-apns](../backend-apns/SKILL.md) |
| Widget projections, timelines and interaction | [backend-widgets](../backend-widgets/SKILL.md) |
| Siri/App Intents, entities and authenticated domain actions | [backend-app-intents](../backend-app-intents/SKILL.md) |
| Live Activity state and ActivityKit push integration | [backend-live-activities](../backend-live-activities/SKILL.md) |
| Background reconciliation and durable transfers | [backend-background](../backend-background/SKILL.md) |
| Native/server authentication and entity authorization | [backend-auth](../backend-auth/SKILL.md) |

Keep existing providers and adapters. A Node service cannot confer widget refresh, extension execution or account entitlements. The [source registry](../../research/sources/sources.jsonl) and [design review](../../research/outputs/design-decision.md) record provenance and limits.
