# Credentials and local data

Begin with a concrete data-flow map: what the feature receives, where it stores data, which process/account can access it, when it is transmitted and how logout/deletion affects it. Review only the files needed for the task and never print credentials or full environment dumps. An identifier in a client configuration is not automatically a secret; classify it using the provider's actual contract.

## Keychain decisions

Apple Keychain services store small secrets in an encrypted database. Use an existing well-reviewed wrapper or a narrow SecItem-based adapter that exposes meaningful errors. Choose a stable service/account identity and access group only when the entitlement is present. Do not add cross-app sharing or synchronizable storage as a default convenience.

Select the accessibility policy from product requirements: access while unlocked, availability after first unlock for background work, device-bound storage and any user-presence constraint. Stronger restrictions can legitimately prevent background refresh. Document this tradeoff and verify on a locked device rather than assuming the simulator reproduces it.

Handle not-found, duplicate/update, interaction-not-allowed and entitlement/configuration errors separately. Never fall back to plaintext UserDefaults when Keychain access fails. Do not log the query's secret value or encode credentials into error messages. Preserve existing items during migrations until the new path is verified, then remove only the obsolete scoped items.

Account switching and logout must invalidate in-flight refresh results, clear the intended session and implement the provider's revocation policy where required. Deleting a local token does not revoke it remotely. Avoid destructive broad keychain deletion that affects other accounts or applications. Do not rely on uninstall as the product's credential-erasure strategy.

## Authentication boundaries

Use the app's configured provider and supported platform flow. ASWebAuthenticationSession is intended for authentication through a web service; follow the provider's public-client flow, redirect validation and anti-forgery requirements. Keep authorization state and code-verifier lifetime tied to one attempt, handle user cancellation and reject unexpected callback data. Treat returned tokens/codes as sensitive.

A mobile binary cannot safely keep a confidential server-side client secret. Route privileged signing or service credentials to a trusted server. Do not create a new backend/auth provider just to make a local feature example compile. Public configuration, redirect URLs and entitlements must match real registered values rather than plausible placeholders shipped into production.

## Local files and caches

Secrets belong in the appropriate secret store; larger private content may require file protection, retention and backup policy. Apple's FileProtectionType offers policies whose availability differs while locked/booting. Match policy to actual background needs and verify protected-file errors instead of treating them as corruption. A database or cache setting is not proof that every temporary export has the same protection.

Separate caches from durable user content. Track temporary media, exports, thumbnails, local notifications, app group files and extension access. Check whether account-scoped images at the same URL/path can reuse another account's cache entry. On logout or deletion, clear the intended private state and invalidate associated UI/request generations.

Use secure system-generated randomness and platform cryptographic APIs when needed; do not invent encryption or token generation. Encryption requires key lifecycle and recovery decisions. Avoid adding a cryptographic layer when a platform protection mechanism already meets the requirement.

## Verification

Test missing/expired/revoked credentials, account switching during refresh, restricted Keychain access, protected data while locked and background refresh. Verify secret redaction in successful and failing paths. Test the actual access group/entitlements in a signed build on device when relevant. Static code review cannot establish device lock behavior or certify security.

Sources inspected: Apple [Keychain services](https://developer.apple.com/documentation/security/keychain-services), [ASWebAuthenticationSession](https://developer.apple.com/documentation/authenticationservices/aswebauthenticationsession), [FileProtectionType](https://developer.apple.com/documentation/foundation/fileprotectiontype). This is original operational guidance, not a copied Keychain implementation. See [source map](../../../docs/source-map.md).
