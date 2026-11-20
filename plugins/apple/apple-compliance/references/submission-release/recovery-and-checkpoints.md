# Recover after partial mutation or timeout

Read the [operating contract](../operating-contract.md). Resume from authenticated remote facts rather than trusting local completion flags.

## Establish the inputs

- Original request, selected identities and prior receipt IDs.
- Current authenticated version/build/submission relationships.
- Local checkpoint provenance and completed-step assertions.
- Changed metadata/artifacts/policy facts since earlier checks.
- Operation-specific retry/idempotency and cancellation behavior.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Read current version/build/submission relationships after a timeout or resumed run. Treat local checkpoint JSON as untrusted state.
2. Revalidate metadata inputs and readiness affected by changed app, platform, build or files; remove unjustified local completion assumptions.
3. Retry the smallest missing safe step, using an existing appropriate submission when possible. Preserve receipts and explain uncertainty if remote state cannot be read.

### Treat local state as untrusted evidence

A checkpoint can contain a real-looking app, version, build or submission ID and arbitrary completion flags. Matching a user-facing version string does not prove the other IDs belong to that app and platform. Re-establish the relationship from current authenticated API state before resuming dependent mutations.

Revalidate checks that are point-in-time observations rather than durable server facts. Readiness can become stale after metadata, routing coverage, a product item or the attached build changes. A local completed flag must not suppress those checks. Preserve the original receipts and report which assertions were authenticated, discarded or still uncertain.

### Retry the missing step, not the whole release

A timeout may occur after the server completed a write. Inspect current state and determine the smallest missing action before resubmitting. A local error is not proof that no remote mutation occurred, and cancellation does not undo every earlier effect. Avoid creating a duplicate submission or replacing a correct build merely to rerun a wrapper.

If the service cannot be read, retain the uncertainty and a concrete resume command/identifier. Complete independent work instead of repeatedly sending the same request. Cancellation, removal of review items and changing release policy are separate mutations whose authority must match the task; do not use them as invisible script cleanup.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Checkpoint binds another app/version | Reject the checkpoint binding for the dependent action and resolve the intended identities from the selected account. |
| Checkpoint says submitted but remote state does not | Discard the local completion assertion and inspect the current server state/receipts before choosing a retry. |
| Second submit attempted after the first request actually succeeded | Reuse the verified existing submission or report its status; do not create another review request automatically. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Prior receipts and current authenticated target binding.
- Checkpoint assertions accepted or invalidated with reason.
- Smallest missing action and actual retry result.
- Remaining uncertainty and safe resume/monitoring identifiers.

Cancellation and retries are real mutations; do not silently cancel a live review to make a script easier to rerun. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_comp_delivery_code_012` — [rorkai/App-Store-Connect-CLI@ecad9f122524:internal/cli/release/checkpoint_binding.go](https://github.com/rorkai/App-Store-Connect-CLI/blob/ecad9f122524248749b6c44bb01e951734131889/internal/cli/release/checkpoint_binding.go).
- `src_comp_delivery_code_013` — [rorkai/App-Store-Connect-CLI@ecad9f122524:internal/cli/release/checkpoint_binding_test.go](https://github.com/rorkai/App-Store-Connect-CLI/blob/ecad9f122524248749b6c44bb01e951734131889/internal/cli/release/checkpoint_binding_test.go).
- `src_comp_delivery_code_004` — [fastlane/fastlane@a540df301c4a:deliver/lib/deliver/submit_for_review.rb](https://github.com/fastlane/fastlane/blob/a540df301c4ada0621cdb50358049734712f7ee7/deliver/lib/deliver/submit_for_review.rb).
