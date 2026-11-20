# Choose the Mac App Store or direct distribution lane

Read the [operating contract](../operating-contract.md). Keep code signing and policy requirements attached to the actual delivery channel.

## Establish the inputs

- Mac App Store, Developer ID direct distribution or another selected channel.
- Framework/runtime and app/helper/installer topology.
- Certificate/profile/signing mechanism and capability needs.
- App Sandbox/Hardened Runtime requirements for the selected lane.
- Parallel platform releases and their independent statuses.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. Identify whether the app targets Mac App Store review, Developer ID direct distribution, or another explicitly selected channel.
2. Inventory native framework/runtime, sandbox, hardened runtime, installer/helper topology and required entitlements before selecting certificates or tools.
3. Keep Mac App Store sandbox/review separate from direct-distribution notarization and Gatekeeper checks. Preserve a parallel iOS release lane rather than assuming one approval covers both.

### Identify the channel before choosing controls

Mac App Store distribution and Developer ID direct distribution have different review, signing and packaging concerns. Determine the actual channel and supported operating-system targets before selecting certificate types or applying a command recipe. A notary ticket for a directly distributed app is not an App Store review result, and an approved iOS version does not cover a Mac release.

Inspect the app's framework/runtime and executable topology. A native Swift app, Electron app, helper service and installer can need different capability and signing treatment. Use current Apple documentation for the selected channel and the actual exported artifact as evidence. Keep sandbox and hardened runtime as distinct mechanisms rather than using their names interchangeably.

### Preserve deliberate capability scope

Inventory app groups, file access, keychain groups, network behavior, helpers and other requested capabilities. Grant only what the real feature and channel require. Electron JIT/helper examples illustrate that runtime's needs; copying their entitlement defaults into unrelated native apps can broaden access without solving the actual issue.

Retain a separate per-platform readiness map if the product ships on iOS and macOS. The shared backend or source repository does not eliminate platform-specific identifiers, artifacts, permissions and review requirements. Finish each lane with its observed evidence and limitations rather than a single undifferentiated shipping status.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Developer ID certificate used for an App Store workflow | Select the certificate/signing lane appropriate to the actual channel after inspecting current project configuration. |
| Electron JIT entitlement copied to an unrelated Swift app | Remove the unsupported default and derive capability requirements from the native feature/runtime evidence. |
| Notary ticket treated as App Store approval | Report the notarization result narrowly and perform the separate App Store review work if that is the intended channel. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Selected channel and platform-specific artifact identities.
- Runtime/helper topology and capability map.
- Required signing/sandbox/runtime controls with current sources.
- Independent release states and material unverified behavior.

One platform/channel passing does not establish another platform/channel is ready. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_developer_id` — [Developer ID certificates - Certificates - Account - Help - Apple Developer](https://developer.apple.com/help/account/certificates/create-developer-id-certificates/).
- `src_delivery_app_sandbox` — [App Sandbox](https://developer.apple.com/tutorials/data/documentation/security/app-sandbox.json).
- `src_delivery_hardened_runtime` — [Hardened Runtime](https://developer.apple.com/tutorials/data/documentation/security/hardened-runtime.json).
- `src_comp_delivery_code_066` — [electron/osx-sign@442870619b4c:src/sign.ts](https://github.com/electron/osx-sign/blob/442870619b4cbf932facc8a4dd458003fe8b90c4/src/sign.ts).
