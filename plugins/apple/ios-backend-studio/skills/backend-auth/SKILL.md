---
name: backend-auth
description: "Use when integrating Node.js authentication/session/resource authorization with native iOS, widgets or App Intents, including Sign in with Apple verification and Keychain scope. Preserve the existing provider; do not confuse Apple token roles, invent privacy declarations or substitute local device unlock for backend permission."
---

# Identity, sessions and extension authorization

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Inspect existing provider/session format, trusted issuer/audiences where relevant, account/tenant model, signed targets, credential storage and current API authorization before selecting a change.
2. Keep provider identity verification, app-session validation and resource authorization separate. A bearer credential need not be a JWT; use the actual configured trust mechanism.
3. For Apple identity, verify against the current provider metadata/JWKS and request binding. Keep identity tokens, client-secret JWTs, APNs provider JWTs and app session credentials as distinct roles.
4. Give app/extensions only the required client credential through supported Keychain/session boundaries. Handle lock/protected-data states without placing server secrets in clients or shared projections.
5. Test wrong issuer/audience/signature, expired/revoked sessions, key rotation, replay, concurrent refresh, account switches and denied resources. Preserve product-specific linking/deletion decisions and verify real device/provider paths when applicable.

## Load the relevant reference

- [Apple identity and server verification](../../references/auth/apple-identity-verification.md)
- [Device/extension credential scope](../../references/auth/device-and-extension-credentials.md)
- [Sessions, account changes and authorization](../../references/auth/sessions-and-authorization.md)

## Complete with evidence

Return the trust/authorization and storage changes, explicit token-role map, failure/recovery behavior, tests and remaining device/provider checks. Do not claim authentication correctness from parsing a token or passing a local unlock.

Source observations and availability are recorded in the references and [source registry](../../research/sources/sources.jsonl). Multiple Apple pages do not count as independent author corroboration.
