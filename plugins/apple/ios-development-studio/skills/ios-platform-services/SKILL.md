---
name: ios-platform-services
description: Use for iOS WidgetKit extensions, App Intents, push notifications, background tasks, App Clips, app groups, and system lifecycle integration. Do not use for ordinary in-app routing, store submission, or unrestricted background execution promises.
---

# iOS platform services

Read [the operating contract](../ios-development/references/operating-contract.md). Discover the target/extension topology and verify the chosen API in the installed SDK before writing code.

1. Identify the user-visible system interaction, extension target, bundle identity, deployment support, entitlements and existing shared-state boundary. Inventory configuration rather than enabling capabilities indiscriminately.
2. Select the relevant [extension/intent](references/extensions-intents.md) or [notification/background](references/notifications-background.md) workflow. Follow the existing app's data and concurrency design.
3. Define behavior when signed out, offline, permission denied, data stale, process absent or the system declines scheduling. Build the useful fallback first.
4. Keep UI work, extension snapshots and background handlers short and bounded. Share immutable snapshots or deliberately coordinated storage; never assume shared process memory.
5. Test input routing, authorization, completion/expiration and repeated delivery. Build every affected target. Verify system behavior on an appropriate device; simulator evidence has limits.

Return targets/configuration changed, the event-to-handler path, accepted fallback behavior and test/device evidence. Do not claim a background task or widget refresh runs on a guaranteed clock.

Source basis: the supplied Expo app-clip/native-module and SwiftUI extension topics, augmented by official SDK verification. See [the source map](../../docs/source-map.md). The plugin does not bundle a push provider, signing identity or cloud scheduler.
