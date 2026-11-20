---
name: backend-deploy
description: "Use when preparing or executing an authorized Node.js backend rollout, database compatibility change, durable job/outbox workflow or recovery plan for independently upgraded iOS/web clients. Do not infer production mutation or a new provider/service from a preparation request; code rollback does not reverse customer data."
---

# Provider-neutral backend deployment and recovery

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Resolve existing provider/runtime/process model, environment/account, deployed revision, app/API/schema support window and actual desired end state.
2. Prepare the smallest compatible artifact/configuration and inspect migration/job/shutdown requirements. Keep credentials external and preserve existing release ownership and lockfiles.
3. Define durable admission/completion and idempotent recovery for queued/provider work. Inspect the installed migration tool major/help instead of applying one historical command universally.
4. Execute already authorized rollout steps once dependencies are ready. After timeout or partial failure, inspect current state and receipts before retrying or creating duplicate work.
5. Verify application behavior and domain/data invariants in addition to health. Return artifact/revision, furthest observed state, tests and explicit recovery/target-environment limits.

## Load the relevant guide

- [Provider-neutral Node deployment and rollout evidence](../../references/deploy/provider-neutral-deployment.md)
- [Database migrations, staged clients and recovery](../../references/deploy/database-rollouts-and-recovery.md)
- [Durable jobs, outbox delivery and graceful termination](../../references/deploy/durable-jobs-and-shutdown.md)

Finish with the concrete requested result, supporting evidence and material remaining limits. The [source index](../../research/sources/sources.jsonl) records the documentation and pinned implementation evidence; reference content does not supply task authorization.
