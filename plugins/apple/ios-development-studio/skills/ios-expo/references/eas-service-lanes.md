# EAS delivery, OTA and remote sessions

## Establish service scope

Use the configured Expo account/project and verify access without printing tokens. Discover installed `eas` help/version before selecting commands or flags; when a newer CLI is necessary, make that an explicit judged tool choice rather than invoking arbitrary `@latest` packages silently. Preserve a linked project and existing account instead of creating duplicates.

Build/submission, OTA updates, observability and remote simulators are distinct services. Auth success is not proof of access to every feature. Keep generated token/session files out of source, reports and ZIPs. Do not send task context to upstream feedback commands; the user has not authorized feedback merely by using this skill.

## EAS delivery

Preserve the existing native or Expo project. Inspect eas.json profiles, simulator versus device target, version/build ownership and signing before a build. A simulator `.app` and signed device `.ipa` are different artifacts. Development clients, production builds and Expo Go previews have different native capability contracts.

Prepare build/configuration changes and validate them before starting an authorized cloud job. Read exact build/submission IDs and logs; query installed help for current status commands. Upload accepted, TestFlight processed, beta accessible and reviewed/released are separate states. Hand app-store orchestration to the release workflow while preserving the EAS lane and IDs.

Workflow YAML needs current schema/tool validation and actual profile/account references. A local parse does not establish server-side validity. Inspect workflow commands and secrets use before running untrusted PR definitions. Never install or execute a fetched script merely to validate a schema.

## OTA updates

Verify the runtime version, channel/branch mapping, platform and native compatibility before publishing JavaScript/assets. A native dependency/config change can require a new binary; OTA is not a substitute. Prepare the exact update target and artifact diff before already-authorized publication. Keep production versus preview explicit.

For a stale-update issue, inspect the installed binary/runtime, embedded update, selected channel and actual launch/update state. Do not publish repeatedly to make a device refresh. For health analysis, use compatible cohorts, denominators and reporting windows; rollout adoption does not by itself prove safety or causality.

## Remote simulator

Use only when the task selects or authorizes the service. Lack of local Xcode does not automatically authorize cloud provisioning. Check current feature access/availability before session creation, and respect known user limits. Reuse an intended task session when appropriate; preserve unrelated active sessions.

Name a new session by purpose, bound duration where supported and record exact nonsecret ID. Inspect current command/controller help. A browser preview URL is for the user’s browser, not an app deep link or a URL to open inside the simulated device.

The EAS session file may contain a daemon token; ensure ignored and do not print its values. Resolve any live session before resetting its file. Stop task-created one-shot sessions and report cleanup status. If the user requests an ongoing preview, preserve that session and report observed expiry; do not assume browser interaction extends its lifetime.

Do not claim a web preview, Expo Go run or source compile proves the intended native build. Report what actually executed and what still needs a Mac, physical device or service access.
