---
name: backend-discovery
description: "Use to inspect an unfamiliar native app/Node.js/multi-client project, resolve runtime and dependency constraints, or prepare a provider-neutral implementation plan. Do not install frameworks, provision services, print credentials or turn a narrow endpoint fix into a platform migration."
---

# Discover the integration boundary

First read the [operating contract](../../references/operating-contract.md).

1. Identify the requested outcome and actual repository roots. Follow [project inventory](../../references/discovery/project-inventory.md) to inspect instructions, worktree changes, app targets, service entrypoints, lockfiles, contract files, CI and data ownership without evaluating imported configuration.
2. Use [runtime capabilities](../../references/discovery/runtime-capabilities.md) to distinguish configured intent, executable/tool presence, supported runtime behavior and authenticated access. Record unknowns without guessing.
3. Produce a small [provider-neutral plan](../../references/discovery/provider-neutral-plan.md) that maps the user's requirement onto existing components. Resolve only the facts that change correctness or authorized actions; continue independent reversible work.
4. Select the specialist for implementation: `backend-contracts` for wire ownership, `backend-node-api` for handlers, `backend-auth` for credentials/authorization, and the relevant native or data workflow for its actual boundary.
5. Hand off exact paths, versions, account-safe environment identifiers, accepted failure behavior and the smallest reproducible validation command. Do not confuse an inventory or plan with completion of an implementation request.

Output a concise system map, an evidence-backed capability table, material unknowns and a concrete next change. Distinguish the backend's runtime from its build runtime and the app's compiler from deployment availability. No service, MCP binding, account, secret or paid tool is implied by this plugin's references. See the [source registry](../../research/sources/sources.jsonl).
