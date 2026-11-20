# Identity and profile diagnosis

## Establish the signing contract

Record app and extension bundle identifiers, team/provider, platform, build configuration and purpose: development device, registered-device release testing, TestFlight/App Store or another explicitly requested method. Simulator and physical-device builds are different lanes. The display name, bundle identifier, opaque Bundle ID resource ID and App Store app ID are not interchangeable.

Inspect the active project, relevant xcconfig/includes, capabilities and entitlements. Do not “fix” signing by changing bundle identity, disabling a capability or removing an extension without relating that change to the user’s goal. Preserve manual versus automatic signing conventions unless the task calls for a migration.

Read-only diagnosis should answer:

- Is the selected team the one intended, and can the configured account/key access it?
- Does a usable signing identity include its private key, rather than only a certificate?
- Is the profile for the correct app/platform/type/team and still valid by actual expiration date?
- Do certificate association, device membership and entitlements match the artifact’s needs?
- Are extension profiles/identities configured as well as the main app?

A remote profile state alone may not establish current validity. A downloaded certificate alone does not provide a private signing key. A successful auth status does not prove authorization for every operation.

## Tool discovery and account safety

For an existing `asc` installation, discover commands without changing auth:

```sh
asc --help
asc auth --help
asc bundle-ids --help
asc certificates --help
asc profiles --help
asc signing --help
```

Inspect the exact leaf help and existing status/profile selectors before running a read or mutation. API-key auth, Apple Account web sessions, StoreKit server keys and Apple Ads are separate surfaces. Use the least necessary one; never start concurrent interactive logins for the same Apple Account or clear a cached session as routine preparation. Preserve credentials configured by the host.

When no supported API covers a capability, explain the verified gap and use an authorized portal/web-session/manual lane. Do not claim a web-only command is part of the public App Store Connect API.

## Repair in dependency order

Resolve identity and target first, then capability/entitlement configuration, then certificate/private key, then profiles, then signed archive/export. If a capability assignment changes, inspect which existing profiles need regeneration. Create a successor resource where appropriate rather than revoking a working shared identity.

Use a CSR and private key in an explicitly private location. Follow installed tool guidance for local profile directories; those locations vary with Xcode. Prefer explicit installation/output paths in automation. Never place key material or password files in sample templates, test fixtures, screenshots or ZIPs.

Keep receipts listing resource IDs and intended changes without secret contents. If remote creation times out, read the relevant resources before retrying to avoid duplicates. For rotation, determine the affected applications/CI lanes and migration order before revocation.
