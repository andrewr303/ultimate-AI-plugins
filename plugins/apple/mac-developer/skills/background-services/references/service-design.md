# Service design, bundle layout, and verification

## Contents

decision table; bundled agent example; durable worker protocol; IPC, privilege, and storage boundaries; lifecycle acceptance and diagnostics.

Research checked 2026-11-03 against Apple sources. Compile samples with the project's actual SDK and test signed installed artifacts. These are adaptation patterns, not a complete installer.

## Decision table

| Requirement | Candidate | Lifecycle limit |
| --- | --- | --- |
| Finish import while windows are open | App-owned task | Ends with its process; persist before acknowledging |
| Quick commands from menu bar | SwiftUI MenuBarExtra/AppKit status item | Does not itself survive app Quit |
| Launch main app after user login | `SMAppService.mainApp` | Launch-at-login setting, not independent worker |
| Independent user-session helper | Embedded login item or `SMAppService.agent` | Does not establish work before login or after logout |
| On-demand process isolation | Bundled XPC service | System manages lifetime; persist durable work elsewhere |
| Required privileged/system service | `SMAppService.daemon` | Requires admin approval; no ordinary user UI from daemon |
| Deferrable in-process maintenance | `NSBackgroundActivityScheduler` | Opportunistic timing; not a replacement for launch service |

Apple distinguishes user login items, user-session agents, and system daemons. Login items persist until logout/manual quit; agents work for the logged-in user. System daemons use low-level IPC rather than interacting directly with a user's UI. [Service Management](https://developer.apple.com/documentation/servicemanagement/).

`SMAppService` is available from macOS 13. New app-associated jobs use the API rather than writing shared launchd directories. An ordinary per-user organizer should not acquire root simply to keep running. Legacy installers may remain appropriate for supported existing products; document why. [SMAppService](https://developer.apple.com/documentation/servicemanagement/smappservice).

## Bundled agent example

```text
ClipLibrary.app/
  Contents/
    MacOS/ClipLibrary
    MacOS/ClipWorker
    Library/LaunchAgents/com.example.clip-library.worker.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.example.clip-library.worker</string>
  <key>BundleProgram</key><string>Contents/MacOS/ClipWorker</string>
  <key>RunAtLoad</key><true/>
</dict></plist>
```

Replace identifiers and the executable with real project values. `BundleProgram` is relative to the `.app` root; it is not a shell command. Put Mach-O workers in a supported code location such as `Contents/MacOS`, not among ordinary resource files. Verify layout using [Apple bundle placement guidance](https://developer.apple.com/documentation/bundleresources/placing-content-in-a-bundle). Keep `RunAtLoad` only if the worker should start at service bootstrap. For a long-running worker, choose and validate the appropriate `KeepAlive` policy from the target's `launchd.plist(5)` rather than copying unconditional restart behavior that defeats explicit quit or creates a crash loop. A native bridge host started by Chrome is not automatically this agent.

Use `Contents/Library/LaunchDaemons` for an SMAppService daemon plist and `Contents/Library/LoginItems/Helper.app` for a login-item app. Sign the shipped nested code and containing bundle. Do not mutate the plist inside a signed bundle at runtime. [Migration and bundle paths](https://developer.apple.com/documentation/servicemanagement/updating-helper-executables-from-earlier-versions-of-macos), [agent initializer](https://developer.apple.com/documentation/servicemanagement/smappservice/agent(plistname:)).

Minimal registration wrapper, called by app UI and tested against its deployment target:

```swift
import ServiceManagement

@MainActor
final class WorkerService {
    private let service = SMAppService.agent(
        plistName: "com.example.clip-library.worker.plist"
    )

    var status: SMAppService.Status { service.status }

    func setEnabled(_ enabled: Bool) throws {
        if enabled {
            if service.status != .enabled && service.status != .requiresApproval {
                try service.register()
            }
        } else if service.status != .notRegistered {
            try service.unregister()
        }
    }

    func showApprovalSettings() {
        SMAppService.openSystemSettingsLoginItems()
    }
}
```

Read status again after errors and when the app returns to foreground; reconcile concurrent changes instead of blindly repeating registration. `.enabled` means eligible to run, not proof that IPC is responding. `.requiresApproval` needs a user action, `.notFound` signals a missing/misconfigured service, and `.notRegistered` is a separate state. Add a heartbeat/health check and report authorization and runtime health independently. [Status](https://developer.apple.com/documentation/servicemanagement/smappservice/status-swift.enum).

A registered embedded login item can start immediately and on future logins; a main-app service launches at later logins. An agent is bootstrapped for the current user and subsequent logins; registration for multiple users must occur in each user's context. A daemon waits for admin approval and then participates in boot. Do not promise registering from one user's UI configures every other user. [Registration semantics](https://developer.apple.com/documentation/servicemanagement/smappservice/register()).

## Durable worker protocol

A proposed clip pipeline is `receive → validate → stage → commit → acknowledge → enrich`. Acknowledge only after the original image and metadata are durable. OCR/search/thumbnail enrichment may retry independently; failure there must not lose the source image. Add unique `(sender, captureID)` constraints and transactional insert/check behavior. Crash at every boundary in a fault-injection test; replaying the same capture should return its existing receipt.

Separate process restart from job retry. Retry transient failures with capped backoff; quarantine poison jobs with a visible repair/export action. Persist attempt counts and next-attempt times. On sleep/wake, reevaluate outstanding leases and network state. Do not rely on in-memory timers or a browser port as the durable record. Respect user cancellation, resource pressure, and shutdown; avoid aggressive polling.

Use scoped QoS and activity assertions for real work, and balance activity lifetimes. Use deferrable scheduling for maintenance. Do not keep a machine awake continuously to hide lifecycle defects. [Process activity](https://developer.apple.com/documentation/foundation/processinfo/beginactivity(options:reason:)), [background scheduler](https://developer.apple.com/documentation/foundation/nsbackgroundactivityscheduler).

## IPC, privilege, and storage boundaries

Prefer narrow XPC methods carrying typed values, stable IDs, and explicit errors. Enforce an intended code-signing requirement on incoming peers before serving operations. Validate both sides where helper impersonation matters. Use target-supported APIs such as `NSXPCListener.setConnectionCodeSigningRequirement(_:)` or per-connection requirements; inspect installed headers and availability. If an older API path uses audit tokens, obtain them from the connection's supported mechanism, never from the caller's message or a PID lookup vulnerable to process reuse. [XPC signing requirement](https://developer.apple.com/documentation/foundation/nsxpclistener/setconnectioncodesigningrequirement(_:)).

Even an authenticated app cannot ask a privileged helper to run arbitrary shell text, open arbitrary paths, or overwrite arbitrary files. Authorize operations and validate paths in the helper. Pass scoped bookmarks when needed; an App Group is for configured native targets and cannot authorize a Chrome extension by itself. Avoid storing user secrets or image data in world-readable temporary locations. Use Keychain for pairing secrets, app/container support directories for queues, and explicit redaction in logs.

## Lifecycle acceptance and diagnostics

| Action | Evidence to collect |
| --- | --- |
| Enable/disable background setting | Observed SMAppService status, process/heartbeat, pending queue behavior |
| Close all windows / choose Quit | Behavior matches disclosed contract; no orphan/relaunch loop |
| Kill worker mid-commit | Transaction recovers, no acknowledged loss or duplicate |
| Stop browser / restart extension | Import queue survives; reconnect does not duplicate |
| Logout/login / reboot | Only approved service restarts in expected session |
| Sleep/wake / lose network | Work resumes with bounded retry; UI reports delay |
| Update app / relocate / uninstall | Registration points to intended version; migrations controlled; jobs removed |
| System Settings disables helper | App reflects change and does not override user choice |

Use Console/unified logs, `launchctl print gui/<uid>/<label>` for an agent when available, and the target OS's `man launchctl`/`man launchd.plist`. `sfltool dumpbtm` helps inspect background-item registration; do not use system-wide reset commands as a routine app repair. Capture errors before changing installation state. Unregister only this app's services in cleanup; preserve user data unless deletion is explicitly selected. Apple's installer sample demonstrates packaging and XPC testing, but its broad sample cleanup commands are not a production uninstaller. [Apple service installer sample](https://developer.apple.com/documentation/servicemanagement/updating-your-app-package-installer-to-use-the-new-service-management-api).
