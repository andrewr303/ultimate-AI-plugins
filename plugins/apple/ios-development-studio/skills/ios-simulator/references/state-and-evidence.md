# Simulator state, scope and evidence

## Bound mutations

Booting, launching and interacting with a simulator are reversible operations within an authorized test. Erase/delete/uninstall, clearing photos, wiping app containers and revoking permissions may remove important test state. A broad “fix the simulator” request does not establish scope to erase every simulator. Inspect and prepare a concrete scoped remedy first; execute when existing authorization covers that remedy, and ask only if the necessary destructive effect is outside it.

Avoid `all`, every-booted or device-type batch selectors for routine work. Resolve exact devices and data affected. Existing approval for one test device does not cover another project’s device. An upstream script’s `--yes` or `--confirm` flag is a mechanism, not evidence of user intent.

Do not routinely delete DerivedData, reset keychain/privacy state or kill all controller companions. First inspect the failure. Select the task’s process or device and retain logs needed to explain it. If cleanup is necessary, preserve the user’s source, signing assets and unrelated devices.

## Temporary environment changes

Appearance, locale, region, Dynamic Type, contrast, orientation, location, notification and privacy settings affect later tests. Record their previous values when practical; apply the minimum needed and restore afterwards unless the user wanted a persistent change. Use the installed `simctl`/controller help to determine which settings can be read, changed and restored reliably.

Changing app launch language arguments differs from changing system-wide locale. Check actual app text after relaunch; do not report language change from command status alone. App foreground/background state affects notification presentation, so test the state required by the scenario.

Some controller deep accessibility modes modify device automation settings. Treat that as a state change and document inability to restore it. Simulator support for camera, sensors, purchases, keychain and notifications may differ from real hardware; use a physical-device check when the capability requires it.

## Sensitive capture

Sandbox exports, UserDefaults dumps, images, clipboard, push payloads, network logs and raw system logs can contain sensitive material. Keep local artifacts in the task’s agreed output location, use synthetic data when possible, redact the handoff and never package secrets. Exporting an entire container is rarely necessary for a narrow bug.

Bound log capture by app/time and artifact size; stop log or sampling workers created during the test. Retain the actual failure instead of repeatedly refreshing into a clean state. A detached worker still running is part of the handoff, not completed cleanup.

## Test matrix and honest completion

Choose a small matrix based on the feature: supported minimum/current runtime, relevant size class, light/dark, accessibility text size, RTL, offline or permissions. Do not run every combination mechanically. Report each scenario actually exercised and any untested requirement.

A successful UI interaction is not full accessibility compliance. Tree heuristics can suggest missing labels and suspicious targets, but a complete assessment needs semantic intent, focus order, VoiceOver/manual checks and platform audits. Decorative images do not always need spoken labels; automation IDs do not replace user-facing labels.

Completion evidence identifies the app/build/device, scenario, assertions, artifacts and final state. If only static review occurred, say so. Stop and clean up only task-owned sessions; preserve a preview explicitly requested to remain running and report its known expiry when applicable.
