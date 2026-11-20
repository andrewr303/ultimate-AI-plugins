---
name: backend-architecture
description: "Use to design or evolve the boundary between a native iOS app, Node.js service and other clients, including runtime selection, domain ownership and compatible releases. Preserve the existing stack; do not turn a local endpoint fix into a framework migration or introduce a hosted service without a requirement."
---

# Backend architecture

First read the [operating contract](../../references/operating-contract.md).

1. Map the actual app targets, Node service, other clients, data authority and deployment constraints. Capture the requested behavior and accepted failure states before choosing a framework.
2. Use [system boundaries](../../references/architecture/system-map-and-boundaries.md) to assign contracts, authorization, state and side effects to concrete owners.
3. Use [Node runtime choices](../../references/architecture/node-runtime-frameworks.md) only when an existing project or a justified greenfield decision needs that choice. Keep transport/runtime validation separate from generated types.
4. Use [release and environment evolution](../../references/architecture/evolution-and-environments.md) to stage compatible changes across independently upgraded mobile, widget, web and server clients.
5. Implement a representative vertical slice and verify its contract, denied access, timeout and old-client behavior. Finish the requested change; a diagram or framework shortlist is not completion.

Return the selected ownership boundaries, changes, preserved constraints, actual verification and unresolved deployment/runtime facts. A provider-neutral design is a deliberate interface boundary, not a promise that hosting providers behave identically.
