# Release gates tied to the candidate artifact

## Identify what is actually being released

Resolve the source revision, contract revision, service artifact/image, native target/scheme/configuration, supported client versions and intended environment. Keep build identity and deployment identity distinct. A file called production, an installed CLI or a green check for an earlier revision is not enough to establish the current candidate's readiness.

Use existing release automation after inspecting its inputs and side effects. Do not replace the package manager, runtime image, signing path or deployment provider merely to match a reference. Preserve unrelated changes. Preparation, dry run and readiness review do not authorize deployment or production data changes.

## Apply the gates that protect changed contracts

| Gate | Evidence to retain |
| --- | --- |
| Source and dependencies | Candidate revision, relevant diff, selected lockfiles/runtime and generated changes |
| Shared wire behavior | Fixture corpus/revision and results from actual server validators and supported consumers |
| Domain safety | Denied access, invalid data, duplicate/concurrent work and durable-state assertions |
| Node/service build | Actual build/test commands, environment and artifact identity |
| Native build | Selected Xcode/SDK, app and affected extension targets, configuration, test plan and result bundle |
| Rollout compatibility | Old-client/snapshot/event cases and migration sequence |
| Operational recovery | Bounded health/readiness evidence, correlation, rollback or forward-repair plan |
| External action | Exact authorized account/environment, action and observed post-action state |

Avoid turning unrelated project-wide checks into mandatory ceremony for a documentation change. For a shared wire, auth, data or lifecycle change, broaden verification to the consumers and invariants it can affect. Reuse passed evidence only while its code/configuration/dependencies remain applicable. Run required final checks after the last substantive edit.

## Plan forward and rollback compatibility

Independently deployed clients can outlive a server rollout. Define which old payloads remain accepted and which new fields or behaviors can be enabled safely. Sequence database changes with the service/client compatibility window; a source revert cannot automatically reverse a migrated store, already-published event or completed remote effect.

When a migration or deployment is required, describe the reversible source step separately from data recovery and provider actions. Test the intended sequence in the available test environment. Do not assert a rollback is safe merely because a previous image exists. Preserve the ability to observe current state and reconcile uncertain work before retrying.

## Keep readiness states precise

Report implementation, local checks, hosted CI, native/runtime checks, independent review, deployment and observed production behavior separately. A plugin's metadata validation or host skill discovery is not application validation. A simulator build is not device signing or physical-device lifecycle evidence. A successful upload is not public availability.

On a Linux host, complete Node/Python/example and package checks that are relevant. Identify the pending Xcode, simulator/device, signing, real APNs or provider gate by exact target and purpose. Use existing authorized remote infrastructure where appropriate; do not fabricate results or provision a substitute automatically.

## Final handoff

Lead with the concrete behavior delivered. Include candidate identity, changed ownership boundary, relevant observed checks, material limits and the next action/owner. If an external mutation was authorized and executed, report its receipt and furthest verified state. A timeout calls for inspecting remote state before another attempt, not assuming either success or failure.

Sources: src_nm_xcode_results — [Interpreting native test results](https://developer.apple.com/tutorials/data/documentation/xcode/running-tests-and-interpreting-results.json); src_nm_xcode_testplans_final — [Organizing native test plans](https://developer.apple.com/tutorials/data/documentation/xcode/organizing-tests-to-improve-feedback.json); src_nm_xcode_cloud — [Xcode Cloud workflow configuration](https://developer.apple.com/tutorials/data/documentation/xcode/configuring-your-first-xcode-cloud-workflow.json); src_nm_node_test — [Node test runner](https://nodejs.org/api/test.html).
