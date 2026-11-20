# Readiness evidence packet

Read the [operating contract](../operating-contract.md). Make submission readiness reviewable and tied to one build rather than a vague checklist.

## Establish the inputs

- Exact artifact identity and cryptographic hash when an artifact exists.
- Selected app/platform/version/build/submission relationships.
- Current policy URLs, observed date and applicability.
- Product facts supplied by an authorized owner.
- Build/test/access evidence and named unresolved dependencies.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Collect artifact identity, supported platforms/deployment targets, build/test results, current metadata and privacy/commercial declarations, review access instructions and outstanding blockers.
2. Classify each item as observed, supplied product fact, unresolved or not applicable. Retain source URL/as-of context for changing Apple requirements.
3. Bind the readiness packet to the exact app/version/build and invalidate affected checks when any bound input changes.

### Keep evidence attached to a release identity

A readiness packet is useful when another person or a later run can tell what was actually checked. Bind it to the app, platform, version and intended build. Include the artifact identity, meaningful test results and the current metadata/product facts used during the assessment. Avoid a single unqualified “compliant” checkbox: use satisfied by evidence, concrete blocker, unknown/needs evidence and not applicable with a reason.

Separate technical observations from declarations. Finding a usage-description key does not establish that permission is requested in the right context. Finding a privacy manifest does not establish the truth of every collection claim. Product, commerce, content-rights and encryption answers need actual feature/data-flow evidence and an identified owner when the tooling cannot determine them.

### Invalidate the right checks

When the build changes, reassess the checks affected by that change. A new embedded SDK, extension, entitlement, purchase flow, account-deletion implementation or supported platform can invalidate earlier privacy or review conclusions. A spelling-only metadata correction does not justify rerunning an unrelated full application test suite. State why a check is reused or repeated.

Treat unsigned local checkpoints and old reports as leads, not proof of current remote state. Read the app/build relationship and current submission before acting. A saved “ready” result must not suppress current readiness after a different artifact is attached or a relevant declaration changes.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| New artifact after an earlier readiness pass | Mark checks tied to the previous artifact stale and re-evaluate the affected behavior/resources. |
| Missing export-compliance answer with no owner evidence | Keep the answer unknown, identify the needed implementation or owner evidence, and block only the dependent action. |
| Accepted app item with another rejected submission item | Report the state of every selected item and the resulting submission blocker; do not call the app publicly released. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Artifact/version/build binding and assessment time.
- Per-check status, method, scope and evidence location.
- Unresolved fact, responsible owner and dependent action.
- Changes since the prior packet and selectively invalidated checks.

A static/local checklist is preparation evidence, not approval or an invitation to infer policy declarations. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_choose_build` — [Choose a build to submit - Manage builds - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-builds/choose-a-build-to-submit/).
- `src_delivery_submit_review` — [Submit an app - Manage submissions to App Review - App Store Connect - Help - Apple Developer](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/).
- `src_comp_delivery_code_012` — [rorkai/App-Store-Connect-CLI@ecad9f122524:internal/cli/release/checkpoint_binding.go](https://github.com/rorkai/App-Store-Connect-CLI/blob/ecad9f122524248749b6c44bb01e951734131889/internal/cli/release/checkpoint_binding.go).
