# End-to-end workflow examples

These are execution plans for a project-aware agent, not pre-authorized external operations or synthetic test results.

## A new offline-capable SwiftUI list

Inspect deployment target and existing persistence. Define acceptance for empty, loading, loaded, stale/offline, retry and error states. Choose the existing Core Data/SwiftData engine when one is present; for a greenfield choice explain model/migration/sync requirements before deciding. Keep service and persistence boundaries testable without imposing layered boilerplate. Implement a stable-ID list and detail route. Cancel work with its owner; check stale-response behavior independently. Test mapping, ordering, failed fetch, cancellation and persistence round-trip. Build the actual selected scheme and test destination where available. Check large text, VoiceOver and RTL separately from unit tests.

Primary skills: architecture or SwiftUI according to scope. Supporting skills: persistence, networking, tests, accessibility. Do not start store upload or add a third-party architecture framework as a side effect.

## A scrolling avatar defect

Reproduce reuse with known accounts, record request/image identifiers without private URLs, inspect resolved image library and existing loader. Verify that view identity follows item identity and request/cache keys distinguish user and variant. Avoid adding Nuke to replace another loader without an actual integration requirement. Test slow and out-of-order responses, cache hits and logout/account switch. For performance claims capture a reproducible baseline and comparable result; a visual fix alone is not proof of lower memory use.

Primary: images. Supporting: performance or networking only if evidence requires them.

## A production crash after a store migration

Resolve app version/build, symbol UUIDs, stack and store/model versions. Preserve the affected store and avoid logs that expose record content. Distinguish model migration failure, context confinement, backend sync conflict and unrelated crashes. Reproduce on a copied on-disk fixture with relevant prior schema. Make the smallest compatible migration or recovery path. Test counts, relationships, constraints and repeated launches. Do not erase customer data or rebuild the whole architecture as diagnosis.

Primary: existing persistence engine. Supporting: observability and tests. Release submission is a separate requested action.

## A native app built through EAS

Resolve the actual Xcode host/scheme/configuration and existing EAS project. Preserve the native project. Inspect the configured build image, lifecycle hooks, credential selection, versioning and artifact type. Do not add React Native or run prebuild to make a Swift app fit a reference layout. Execute only the authorized build lane, then inspect the resulting artifact metadata and observed cloud state. Simulator .app output and device-signed IPA output are different.

Primary: Expo/EAS. Supporting: build/signing/release according to the requested state. Keep remote logs and service tokens out of plugin archives.

## A prepared App Store release

Resolve account, app/platform, version, exact build and current submission. Validate metadata, screenshots, privacy and digital goods with evidence supplied by the product owner. Prepare changes and inspect a supported dry-run plan. Execute already authorized staging/upload/submission steps; ask only for genuinely missing authority or product facts. After a timeout, read the remote state before retry. Report whether the build was uploaded, processed, distributed, submitted, approved or released; never collapse these into “shipped.”

Primary: release. Supporting: metadata, signing or commerce for concrete blockers. Automatic tester invitations, promotional submissions or ad spending do not follow from generic release preparation.
