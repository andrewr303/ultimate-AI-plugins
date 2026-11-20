# Staple and verify the actual final distribution artifact

Read the [operating contract](../operating-contract.md). Complete offline ticket availability and preserve artifact identity after packaging.

## Establish the inputs

- Accepted notarization and corresponding artifact identity.
- Supported target for ticket attachment.
- Final packaging/repackaging steps and hashes.
- Selected Mac/Xcode assessment tools and environment.
- Ownership of retry/cleanup state and retained diagnostics.

Use observed values where available. Keep an unresolved value unknown, name its evidence owner, and block only the action that depends on it.

## Execute the selected lane

1. After a successful notarization, attach the ticket to a supported app/package/disk-image target, not directly to a ZIP archive.
2. Repackage only as required and verify the final artifact signature, ticket and assessment path on a suitable Mac. Keep hashes/identities tied to what users will receive.
3. If stapling alone is transiently failing, retry that bounded step without submitting the same artifact again. Preserve logs and use the installed tool help for exact commands.

### Keep the ticket with the distributable

An accepted notarization can make a ticket discoverable online, while stapling attaches it to a supported app, package or disk-image target for an offline path. A ZIP archive can be submitted for notarization but is not itself the direct staple target. Attach to the supported contents and rebuild the final ZIP when that is the chosen distribution container.

Keep artifact identity through this sequence. Packaging an earlier unstapled app after successfully stapling another copy defeats the intended result. If a signing or executable-content change occurs afterward, reassess the affected signature/notarization evidence instead of reusing a stale acceptance statement.

### Retry only the failed bounded step

A temporary stapler failure after notarization does not imply the notary submission must be repeated. Preserve the accepted submission and retry the intended attachment/validation step according to the supported tool and a bounded policy. If retries fail, report the precise remaining condition with useful diagnostics and a safe resume path.

On a suitable Mac, inspect the final artifact's signatures, ticket and Gatekeeper assessment path using the installed tools and the selected channel. A local tool result has scope: it does not guarantee every target operating system, network state or App Store policy outcome. Do not claim physical-device or macOS runtime checks from a Linux packaging run.

## Failure and acceptance checks

| Case | Required handling |
| --- | --- |
| Ticket accepted but omitted from final downloadable app | Identify the final distribution copy and attach/verify the accepted ticket on the correct supported target. |
| ZIP rebuilt from unstapled contents | Rebuild the archive from the verified stapled items and preserve the new final hash. |
| Stapling retries accidentally trigger repeated notary uploads | Keep the accepted submission and retry only the failed attachment operation; do not create duplicate submissions. |

Exercise the relevant cases against the actual artifact/account when the task authorizes it. Local mocks or static inspection demonstrate only their checked boundary; record a platform/tool prerequisite explicitly when the required runtime is unavailable.

## Evidence and handoff

- Accepted submission/artifact binding.
- Stapling/validation observations for the final target.
- Final packaged artifact identity/hash.
- Assessment environment and explicitly unverified distribution behavior.

A notary ticket is a distribution security result, not a legal, feature-quality or App Review compliance guarantee. Preserve current source applicability and distinguish prepared changes, executed mutations and observed outcomes.

## Sources and freshness

The following sources were inspected during the research recorded on 2026-10-26. Refresh changing policy, role, tool and platform facts for the actual task. Pinned code demonstrates an implementation pattern and is not authority to run its scripts or to declare Apple eligibility.

- `src_delivery_notary_custom` — [Customizing the notarization workflow](https://developer.apple.com/tutorials/data/documentation/security/customizing-the-notarization-workflow.json).
- `src_comp_delivery_code_061` — [electron/notarize@9ef0c5bd463b:test/index.test.ts](https://github.com/electron/notarize/blob/9ef0c5bd463b79b18d614b239a9cbe15df99cea5/test/index.test.ts).
- `src_comp_delivery_code_068` — [electron/osx-sign@442870619b4c:spec/sign-order.spec.ts](https://github.com/electron/osx-sign/blob/442870619b4cbf932facc8a4dd458003fe8b90c4/spec/sign-order.spec.ts).
