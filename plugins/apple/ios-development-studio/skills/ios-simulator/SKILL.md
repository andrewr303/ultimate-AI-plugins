---
name: ios-simulator
description: "Use for local iOS Simulator discovery, boot/install/launch, accessibility-driven UI interaction, screenshots, permissions, locale and scoped runtime reproductions. Do not use for physical devices, cloud provisioning, App Store submission or unrestricted simulator cleanup."
---

# Operate and verify an iOS simulator

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Resolve the available Mac toolchain, installed runtimes, target app and exact simulator. Prefer semantic accessibility interaction with stable identifiers; use screenshots for visual verification. Keep a reproducible starting state and verify each meaningful action’s observable result.

1. Discover devices and select one in scope. Preserve another task’s running simulator or session.
2. Build or obtain a matching simulator `.app`, install and launch that app with resolved bundle identity.
3. Read the accessibility tree, perform a focused interaction and read back the resulting state. Do not claim a tap succeeded solely because the automation command exited successfully.
4. Capture the necessary screenshot, tree and bounded logs for evidence. Record locale, text size, appearance and app build.
5. Restore temporary settings where practical and stop only processes/sessions created for this task.

When local simulator execution is unavailable, continue useful source checks and report that limitation. Use the explicit EAS lane in `ios-expo` only when the task authorizes that service; do not create a cloud session simply because this host runs Linux.

Read only the references needed for the current step:

- [Local simulator workflow](references/local-workflow.md)
- [Simulator state, scope and evidence](references/state-and-evidence.md)
- [Simulator provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
