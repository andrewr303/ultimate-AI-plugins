# Use archive reports and repair invalid manifests deliberately

## Inspect the artifact that produced the finding

Privacy issues can appear only after packaging: a resource was omitted, a vendor shipped an invalid key, or a platform variant differs from the one inspected locally. Resolve the selected archive, build/version and component before repairing the source. A fresh source tree or a different Debug configuration is not evidence about the uploaded Release artifact.

Apple documents Xcode's privacy report as an aggregation of the included app and third-party manifests. Generate it from the relevant archive and use it to understand the declared collection and tracking. Compare that report with the data-flow inventory and App Store Connect answers. An aggregation can expose discrepancies, but it cannot certify that undeclared behavior does not exist.

## Evidence to collect

Record the build identifier, archive identity, Xcode/SDK used, relative manifest paths, resolved dependency versions, parser/validation findings and report generation result. If Apple sends a validation message, preserve the indicated file and path rather than paraphrasing the symptom as a generic privacy failure. Keep account information and customer payloads out of shared logs. A report artifact may itself disclose business data flows, so store and share it within the agreed evidence scope.

## Repair sequence

1. Reproduce the issue in the same artifact or a reproducibly equivalent archive.
2. Determine whether the problem is missing packaging, malformed plist structure, unsupported values, a stale vendor resource or a mismatch with real product facts.
3. Prefer a correct source/resource declaration or a supported vendor update. Preserve lockfile and release changes unless the repair actually needs an update.
4. When changing a dependency, check collection behavior and signature/origin continuity as well as the resource syntax.
5. Rebuild the affected target/variants, regenerate the report and verify the final artifact's identity and resources.
6. Resume the authorized distribution stage only after its concrete dependency is satisfied; continue independent diagnosis and preparation meanwhile.

## Read the documented workaround in context

The manifest packaging article describes fixing or removing an invalid manifest in an archive when a vendor update is unavailable, and notes that modifying the archive breaks its signature until Xcode re-signs it during distribution. This is a narrowly described recovery path, not blanket permission to remove a manifest that current listed-SDK or required-reason rules require. Do not hide a required component to get a green local parser result.

If that path is relevant, record why a supported update is unavailable, what exact requirement still applies, the intended archive mutation and how the final signing/resource checks will be repeated. Execute only within the user's authorized scope. Never strip a manifest silently or imply that a valid signature proves the edited declaration is true.

## Meaningful checks

Verify malformed key/value types are rejected; a required resource absent from a packaged variant stays a blocker; an unresolved vendor behavior stays unknown; and an unrelated target does not make the selected artifact fail without an applicability reason. A report generation failure is not a clean report. A repaired manifest should be checked in the resulting signed product, not only as an isolated file.

The handoff should separate “plist valid,” “resource present,” “privacy report generated,” “behavior reconciled,” “upload accepted” and “App Review approved.” State the furthest observed result. On a host without Xcode or the real app artifact, finish source-level checks and provide the exact pending archive/report validation rather than fabricating a runtime or submission pass.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_privacy_data` — [Describing data use in privacy manifests](https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests)
- `src_policy_adding_manifest` — [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- `src_policy_beta_release` — [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- `src_policy_sdk_requirements` — [Third-party SDK requirements - Support - Apple Developer](https://developer.apple.com/support/third-party-SDK-requirements/)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
