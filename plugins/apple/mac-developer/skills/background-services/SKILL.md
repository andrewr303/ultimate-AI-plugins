---
name: background-services
description: Implement, migrate, or debug macOS login items, SMAppService helpers, launch agents, daemons, XPC services, and reliable background workers for native or Node.js-based apps.
---

# Implement macOS background work

Read [service design and examples](references/service-design.md) before selecting or editing a service. Inspect existing launchd jobs, bundle structure, target signing, deployment target, and worker lifecycle. Preserve the user's existing CLI/server behavior while adding a separate Mac adapter.

## Match the process to the requirement

1. Write a lifecycle contract: whether work continues after window close, app Quit, browser close, logout, reboot, or sleep; who starts it; who stops it; and where pending work persists.
2. Use an app process for tasks needed only while the app runs. A menu bar app is still an app. Use a short-lived bundled XPC service for on-demand isolation, not as a promise of continuous execution.
3. For macOS 13+, prefer `SMAppService` for app-associated login items, per-user agents, or justified system daemons. Use `mainApp` for launching the app at login, `loginItem(identifier:)` for an embedded helper app, and `agent(plistName:)` for a per-user worker. Reserve a root daemon for an actual system-wide/privileged requirement; screenshot organization normally belongs to the user session.
4. Use legacy launchd installation only when deployment or an existing supported installer requires it. Do not install both a legacy job and a new service that run the same worker. Do not assume an `SMAppService` plist should be copied into `~/Library/LaunchAgents`.

## Implement with visible control

- Bundle helpers and their plists at documented paths; sign nested executable code, preserve bundle integrity, and use a stable installed location. Runtime files and logs live outside the signed app bundle.
- Provide opt-in launch/background controls with a plain explanation of continued work and an accessible stop action. Register in response to the intended user choice. Query `status` on activation and after changes; distinguish eligible, needs approval, missing, and unregistered states from the live worker health.
- Handle registration errors and external changes in System Settings. Offer the documented Login Items settings action when approval is needed. Disabling service must stop new work, checkpoint/drain according to policy, unregister the service, and update UI after observing the result. Respect user disablement and explicit Quit.
- For Node workers, bundle the chosen runtime/dependencies; resolve them relative to the bundle, without relying on Homebrew, nvm, shell startup files, npm, or a login shell. Route errors to structured logs and use authenticated, bounded IPC. Keep privileges minimal.
- Design a durable queue with job IDs, transactional acknowledgement, deduplication, bounded retries/backoff, cancellation, crash recovery, and version negotiation. One process owns each migration and mutable queue lease. Browser messages and XPC requests are untrusted inputs.
- Authenticate XPC peers with a documented code-signing requirement or supported peer audit mechanism; require the intended identity and operation authorization. A PID or caller-supplied bundle ID is not authentication. Bound request sizes, method scope, and concurrency.

## Validate on a real Mac

Build and test the installed signed app, not only a helper from Terminal. Verify enable/disable, pending approval, denied registration, first launch, window close, Quit, browser disconnect, crash, repeated launch, logout/login, reboot, sleep/wake, offline recovery, stale app location, update, and uninstall. Show service registration status and worker heartbeat separately. Record which lifecycle cases were actually exercised; Linux static checks do not verify `launchd` or `SMAppService` behavior.

Do not claim background execution is uninterrupted during sleep, logout, shutdown, or user disablement. Use checkpoints and resume semantics instead. Finish with exact build/test results and any platform or signing checks still required.
