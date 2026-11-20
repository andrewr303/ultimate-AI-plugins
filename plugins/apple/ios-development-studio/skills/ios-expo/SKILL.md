---
name: ios-expo
description: "Use when the task explicitly involves Expo/EAS, an expo dependency, Expo native modules/brownfield integration or an authorized EAS delivery/cloud-simulator lane. Do not convert native SwiftUI/UIKit projects, prebuild maintained native hosts, provision cloud resources or send upstream feedback automatically."
---

# Develop iOS with Expo and EAS when selected

First read the [shared operating contract](../ios-development/references/operating-contract.md). Apply the user’s existing scope and authorization throughout this workflow.

Establish whether the goal is Expo app development, a native module/brownfield feature, EAS delivery of an existing app, OTA update work or an explicitly chosen remote simulator. Read installed Expo/React Native versions and lockfiles before API guidance. EAS delivery alone does not require an Expo runtime.

1. Preserve the existing app entry point, build ownership, package manager and SDK/deployment targets. New scaffolding and SDK upgrades must fit the actual request.
2. Choose a focused lane and consult version-matched official docs plus installed tool help. Do not copy broad permissions or automatic feedback instructions from source archives.
3. Implement and verify the requested feature in its real host; an isolated producer/Expo Go preview does not prove native integration.
4. For delivery/OTA/cloud services, establish the actual account/project/environment and existing session state. Prepare concrete artifacts/plans before authorized remote effects.
5. Report local/runtime/service results separately and clean up task-created sessions. If local Xcode or EAS access is absent, continue independent work and label the missing validation.

Read only the references needed for the current step:

- [Native, Expo and brownfield boundaries](references/native-and-expo-boundaries.md)
- [EAS delivery, OTA and remote sessions](references/eas-service-lanes.md)
- [Expo provenance](references/sources.md)

Provenance: [source map](../../docs/source-map.md). Source snapshots are reference material; installed tool help, the project’s versions and current official documentation determine executable details.
