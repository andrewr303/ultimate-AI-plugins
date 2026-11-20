---
name: mac-release
description: "Use when building, testing, signing, notarizing, packaging, updating, or troubleshooting distribution of a native, Electron, Tauri, or Node-backed macOS app."
---

# Build and release a Mac app

Read [release procedure](references/release-procedure.md). Inspect the repository's actual targets, schemes, entitlements, signing configuration, helper executables, packaging tools, and current distribution channel. Preserve existing team IDs and bundle IDs. Never invent certificates, profiles, release evidence, or App Store approval.

## Establish the compatibility and distribution contract

Record minimum macOS, tested OS versions, CPU architectures, Xcode/SDK and dependency versions, identifiers, channel, and expected service lifecycle. The latest SDK and deployment target are different decisions. Verify the current Apple naming/version/compatibility documents rather than guessing from a codename. macOS 27 Golden Gate targets Apple silicon; x86_64 support is a separate decision for compatible earlier systems. Include each helper/runtime/native module in the architecture inventory.

Use Developer ID and notarization for direct distribution. Use Mac App Store signing, sandbox, packaging, and review rules for Store distribution. Evaluate a Chrome native-host installer, root daemon, runtime download, external updater, or shared-location installation against the selected channel before promising it. Do not claim an outside-Store design will pass Store review unchanged. Do not publish, submit, change account/legal metadata, or distribute a release beyond the user's authorization.

## Build the real artifact

Discover schemes/destinations and use the project's established build tools. Run meaningful core/protocol/persistence checks, then macOS integration and UI checks covering the promised feature. Validate the packaged app from Finder, outside the source directory, without development environment variables. Keep checks proportionate to the implementation and preserve original-product regressions for companion conversions.

Sign nested code in the correct order with appropriate identities and per-executable entitlements, then the outer app. Audit embedded runtimes, frameworks, XPC services, login items, agents and browser native hosts. Use Hardened Runtime for notarized executables and justify each exception. Do not disable Gatekeeper, TCC, sandboxing, or library validation broadly to make a build pass. Package only after the signed app is complete; submit the intended artifact to notarization when authorized, inspect its result and log, staple where supported, and test the final download/install path.

## Validate what users receive

Check architecture, signing, Gatekeeper/notarization, helper registration, first-run permissions, background toggle and service removal, offline relaunch, upgrade and rollback/migration behavior. For screenshot companions, test app absent, UI quit, old/new extension versions and duplicate delivery. Provide a clean uninstall path without deleting user data silently. Signed updates must verify authenticity and handle running helpers and data schema changes coherently.

If this environment lacks macOS/Xcode/signing access, complete portable source and check work, add a reproducible Mac verification path, and report the remaining platform checks accurately. A Linux unit test, unsigned `.app` directory, successful upload request, or accepted notarization alone does not prove a working Mac release. Deliver exact artifact path, version/hash, check evidence, and material limitations.
