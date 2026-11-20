# Artifact inventory and identity reconciliation

Apply the [operating contract](../operating-contract.md). Use the app’s actual facts, selected lane and current authoritative sources.

## Inspect the product that will be distributed

Identify selected scheme/configuration, archive/export process, app/platform/version/build and distribution target. Inventory the main app, extensions, embedded frameworks/executables, resources and resolved direct/transitive SDKs. A source file's presence does not prove it exists in the final bundle, and a simulator artifact is not a signed device distribution artifact.

Preserve the original artifact and unrelated work. Use bounded read-only inspection before proposing any repair. Resolve real paths and avoid following links outside the intended artifact. Logs and extracted contents may contain private data or credentials; retain only necessary protected evidence. Do not mutate a vendor binary or remove a manifest solely to silence an upload error.

## Built identity versus store identity

Compare actual bundle identifier, marketing version, build version, platform and embedded-target values with the intended App Store Connect record/lane. Signing identity, private-key availability, profile, entitlements and team role are separate checks. A matching bundle identifier is necessary evidence but does not validate any of those other inputs.

Use the selected Xcode/tools' supported inspection and validation commands where available. Refresh current upload/toolchain requirements for the intended submission time; an announced future requirement is not today's deployment minimum. Do not fix identity by indiscriminately rewriting every target or replacing a complete Info.plist with a small sample.

## Safe helper use

scripts/readiness.py can add bounded artifact observations with `--artifact` pointing at a real app/archive directory. It reads selected plist files and skips unsafe/unreadable/oversized entries within its limits. It reports allowed identity values, usage-description key names, encryption-declaration presence and privacy-entry counts. It does not report the encryption answer, prove manifest semantics or inspect signatures.

The helper can block a declared expected app identifier that contradicts observed APPL bundle identity. No interpretable app identity yields needs-evidence. Matching identity is an observation only. Scan truncation/warnings or unexamined nested products must remain visible in the human inventory; do not turn partial coverage into a complete audit.

## Inventory sequence

1. Resolve the exact build artifact and scope without altering it. If an IPA needs extraction, do that as a separate controlled operation and preserve the original.
2. Inventory product/extension/framework boundaries and compare actual identity/platform values with intended records.
3. Inspect bundled privacy resources, SDK origins/signatures and relevant usage-description placement. Reconcile the inventory with resolved dependencies and runtime behavior.
4. Route signing/capability discrepancies to signing-entitlements, privacy resources to privacy-manifests and native/system behavior to the relevant specialist.
5. Validate affected targets/artifact with the actual Apple toolchain and record exact results when available. Linux plist inspection is not Xcode validation.
6. Rebuild and re-inspect after a substantive source/resource fix. A repaired source tree does not prove the distributed artifact changed.

## Verification and handoff

Test wrong/missing identity, an omitted extension resource and a malformed/partial scan in controlled fixtures. Record toolchain, scheme/configuration, artifact revision, inspected products and warnings. Keep unknown signatures, team access and App Store state separate. The deliverable is a traceable inventory tied to the actual candidate artifact, not an assertion that an archive is approved or legally compliant.

## Sources and checked scope

- [src_policy_beta_release](https://developer.apple.com/tutorials/data/documentation/xcode/distributing-your-app-for-beta-testing-and-releases.json)
- [src_policy_adding_manifest](https://developer.apple.com/tutorials/data/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk.json)
- [src_policy_sdk_requirements](https://developer.apple.com/support/third-party-SDK-requirements/)
- [src_delivery_upload_builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/)

The [source index](../../research/sources/sources.jsonl) records identity and observation scope. These are original workflow notes, not a full policy mirror or a legal/approval certification. Refresh material applicability before the requested external action.

Helper behavior is defined by the local [readiness implementation](../../scripts/readiness.py); its structural assertions and artifact observations do not authenticate product facts.
