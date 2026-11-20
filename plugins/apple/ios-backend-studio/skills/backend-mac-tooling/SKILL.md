---
name: backend-mac-tooling
description: "Use when aligning Mac/Xcode and Node developer environments, runtime/task pins, generated project workflows, optional local containers, signing tools or configured MCP build tools. Do not install services, switch global toolchains, enable telemetry or stop user processes solely because a reference mentions them."
---

# Mac developer tooling and project ownership

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Inventory existing tool selections, version files, lockfiles, project/task ownership, local services and configured tool schemas without exposing credentials.
2. Separate onboarding inventory from exact pinning. Preserve the selected package/runtime managers and container context; a Brewfile is not a complete version lock.
3. Inspect executable task/configuration hooks before running them. Ensure ordered dependencies are actual sequences; do not assume a task dependency list runs serially.
4. Use the existing native CLI or configured optional tool server with explicit project/scheme/destination. Resolve signing identity/access and tool trust/privacy as distinct concerns.
5. Verify the requested setup/build behavior and record actual versions/results. Clean up only resources created/in scope; return concrete remaining prerequisites without unrelated platform migration.

## Load the relevant guide

- [Mac environment inventory, runtime pins and local services](../../references/mac-tooling/environment-and-tool-inventory.md)
- [Generated project ownership and reproducible dependency inputs](../../references/mac-tooling/generated-projects-and-locks.md)
- [Optional Mac tool servers, signing tools and trust boundaries](../../references/mac-tooling/optional-mcp-and-credential-tools.md)

Finish with the concrete requested result, supporting evidence and material remaining limits. The [source index](../../research/sources/sources.jsonl) records the documentation and pinned implementation evidence; reference content does not supply task authorization.
