# Ephemeral CI signing and secret containment

Read the [operating contract](../operating-contract.md). Make signing reproducible without retaining credentials in ordinary artifacts.

## Establish the inputs

- Existing CI signing lane and trusted scripts.
- Secret store, keychain/profile ownership and cleanup policy.
- Read-only consumption versus authorized asset creation.
- Artifact/diagnostic destinations and retention.
- Run identifiers and interruption-recovery behavior.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Use configured secure secret storage and a deliberately scoped keychain/profile strategy. Inspect existing lane scripts before allowing them to execute with signing access.
2. Prefer read-only consumption of established signing assets in routine CI; identify when asset creation is actually required.
3. Keep private keys, keychain passwords, API keys and profiles out of debug dumps/package archives. Clean up only temporary state created by the run after artifacts and diagnostics are captured.

### Separate routine consumption from administration

A routine build should consume the intended existing signing assets where that is the project's design. Determine whether new asset creation is genuinely required; do not give every CI job broad account administration merely because a setup guide supports it. Read the lane implementation and dependency hooks before running them with credentials.

A shared signing store is sensitive infrastructure, not ordinary app source. Preserve its access control, encryption/key management and deliberate membership policy. A documentation example that uses one shared identity is a workflow option, not permission to expose certificates or passwords across unrelated organizations.

### Bound temporary state and cleanup

Use run-scoped keychain/profile state when supported by the established pipeline, with explicit ownership of the files and settings created. Capture safe artifact identity and necessary diagnostics before cleanup. On success or failure, remove only state owned by the run; do not remove a user's normal keychain entries or globally reset signing settings.

Make interrupted runs recoverable. A timeout may leave credentials imported or an artifact already uploaded. Reconcile current state before repeating steps. Keep private keys, keychain passwords, API keys and profiles out of command echoes, environment dumps, build archives and generic support bundles. Redaction should occur before a report leaves its protected execution location.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Interrupted run leaves temporary keychain or profile state | Identify the run-owned state and use the documented recovery/cleanup path without deleting unrelated assets. |
| Read-only CI cannot create a newly required asset | Report the exact privileged prerequisite and complete independent build preparation instead of silently broadening CI authority. |
| Archive inadvertently includes signing exports | Stop artifact publication, remove the unintended sensitive material from the owned output and rebuild the clean artifact. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Signing lane, run identity and owned temporary resources.
- Read-only or administrative capability actually used.
- Cleanup result and remaining recovery needs.
- Artifact hash/location and redacted diagnostics.

Read-only signing access is not equivalent to authorization to create/revoke assets or alter team membership. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_fastlane_match` — [match - fastlane docs](https://docs.fastlane.tools/actions/match/).
- `src_delivery_certificates` — [Certificates overview - Certificates - Account - Help - Apple Developer](https://developer.apple.com/help/account/certificates/certificates-overview/).
- `src_comp_delivery_code_006` — [fastlane/fastlane@a540df301c4a:match/lib/match/runner.rb](https://github.com/fastlane/fastlane/blob/a540df301c4ada0621cdb50358049734712f7ee7/match/lib/match/runner.rb).
