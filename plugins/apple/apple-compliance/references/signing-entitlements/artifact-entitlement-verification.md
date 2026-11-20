# Verify the signed artifact and extension capabilities

Read the [operating contract](../operating-contract.md). Tie compliance analysis to what was actually signed and exported.

## Establish the inputs

- Final .app/.ipa/.pkg/archive and intended recipient/channel.
- Resolved bundle/version/build/platform identifiers.
- Executable/extension/helper inventory.
- Signature identity, embedded profile and effective entitlements.
- Comparison with required app features and approved capabilities.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Inspect resolved bundle identifiers, versions, executable architectures, platforms, signature identity and embedded profile/entitlements in the actual exported app.
2. Compare app and extension capabilities, app groups/keychain access, background/notification features and target membership with the product design.
3. Keep development, simulator, ad-hoc, enterprise, App Store and Developer ID artifacts distinct; explain the intended recipient and channel.

### Inspect what users will receive

Source settings describe an intention; an exported artifact is the object distributed. Inspect the actual bundle metadata and signed executable targets, including embedded extensions and helpers. Keep the artifact's hash/path bound to the result so a later repackaging step cannot silently substitute a different binary.

Distinguish a simulator app from a device-signed IPA, an Xcode archive from an exported distribution artifact, and an installer container from the app inside it. Determine whether the selected platform and export method match the intended distribution lane. Do not infer compatibility from an .ipa or .app filename alone.

### Compare capability scope per executable

For each target, compare actual entitlements and profile scope with app groups, keychain groups, notifications, background work, account access and other requested features. Investigate mismatches without granting broad permissions to make validation pass. Different targets can legitimately require different capabilities; preserve least relevant scope rather than copying the app's entire entitlement set everywhere.

Framework examples need context. Electron helper/JIT requirements and signing order demonstrate one runtime's packaging constraints; they are not blanket entitlements for a native Swift app. Verification of nested signatures is distinct from indiscriminate deep re-signing. If signing changes content, inspect the final rebuilt artifact again.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Simulator .app mistaken for a device-signed IPA | Report the artifact kind/platform mismatch and use the correct build/export path; do not attempt to distribute a simulator artifact to device users. |
| Source entitlement differs from the signed artifact | Treat the exported values as the release evidence and diagnose why source/resolved settings diverged. |
| A development-only permission slips into release packaging | Remove or justify the release capability through the actual feature requirement, then rebuild and verify the signed output. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Final artifact identity/hash and distribution lane.
- Per-target effective signature/profile/entitlement observations.
- Feature-to-capability comparison and unresolved mismatches.
- Post-repair artifact checks and platform limits.

Electron helper/JIT defaults are framework-specific examples, not generic entitlements for native Swift apps. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_app_store_profile` — [Create an App Store provisioning profile - Provisioning profiles - Account - Help - Apple Developer](https://developer.apple.com/help/account/provisioning-profiles/create-an-app-store-provisioning-profile/).
- `src_delivery_certificates` — [Certificates overview - Certificates - Account - Help - Apple Developer](https://developer.apple.com/help/account/certificates/certificates-overview/).
- `src_comp_delivery_code_066` — [electron/osx-sign@442870619b4c:src/sign.ts](https://github.com/electron/osx-sign/blob/442870619b4cbf932facc8a4dd458003fe8b90c4/src/sign.ts).
