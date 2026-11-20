# Signing identity and provisioning map

Read the [operating contract](../operating-contract.md). Diagnose the actual identity/profile/target relationship before recreating team resources.

## Establish the inputs

- App and every extension bundle identifier/team.
- Distribution channel and requested artifact kind.
- Certificate identity, validity and private-key availability.
- Selected provisioning profiles and their app/capability scope.
- Resolved build signing settings and actual signed entitlements.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Map app and extension bundle identifiers, team, distribution method, signing certificate/private-key availability, selected profile and requested entitlements.
2. Distinguish automatic from manual signing and inspect resolved build settings and exported artifact rather than source-file values alone.
3. Compare target capabilities with profiles and certificate validity. Repair only the owned mismatch; preserve unrelated team assets and existing automation.

### Diagnose the relationship rather than the filename

A signing certificate identifies a public credential; the corresponding private key must be available through the intended signing mechanism. A provisioning profile describes permitted app/team/capability relationships for a channel. An entitlement file is requested configuration, while the signed artifact contains the effective entitlements. Inspect those distinct surfaces before replacing anything.

Map every executable target, including extensions, widgets, App Clips and helpers relevant to the app. A correct app target does not compensate for an extension with a mismatched team or profile. Resolve actual build settings for the selected configuration and distinguish development signing, device distribution, App Store submission and Developer ID direct distribution.

### Preserve the established signing model

Determine whether the project uses automatic signing, manually managed profiles or a controlled shared-asset workflow. Keep its existing model unless a concrete defect or explicit migration requires change. Check expired/revoked identities, missing key access, bundle mismatch, capability mismatch and incorrect export method separately.

Do not start with certificate revocation, account switching or profile regeneration. Those changes can affect other apps, developers and CI runners. Identify the smallest owned repair, prepare its effect, and execute it only within existing authorization. Keep key material and profiles out of logs and package archives.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Certificate exists without usable private key | Report that the selected signing mechanism lacks its required key access; importing another public certificate is not a complete repair. |
| Extension has a different team or missing capability | Resolve the affected extension independently and rebuild/inspect the exported target set. |
| Distribution profile for a different bundle ID | Select or repair the profile for the actual identity/channel after verifying target ownership and capability requirements. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Per-target bundle/team/profile/signing map.
- Actual identity/key availability without key values.
- Specific mismatch and authorized repair performed.
- Resolved and exported entitlement/signature observations.

Revoking certificates, rotating secrets or replacing shared signing storage requires matching task scope; never default to destructive reset. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_certificates` — [Certificates overview - Certificates - Account - Help - Apple Developer](https://developer.apple.com/help/account/certificates/certificates-overview/).
- `src_delivery_app_store_profile` — [Create an App Store provisioning profile - Provisioning profiles - Account - Help - Apple Developer](https://developer.apple.com/help/account/provisioning-profiles/create-an-app-store-provisioning-profile/).
- `src_delivery_fastlane_match` — [match - fastlane docs](https://docs.fastlane.tools/actions/match/).
