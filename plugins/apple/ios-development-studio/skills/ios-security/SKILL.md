---
name: ios-security
description: "Review and implement iOS credential storage, Keychain access, authentication boundaries, app permissions, privacy manifests, data protection and transport security. Use for concrete app security/privacy tasks; do not invent data declarations, add permissions or enable certificate pinning by default. This is not an App Store submission workflow."
---

# iOS security and privacy

First read [the operating contract](../ios-development/references/operating-contract.md).

## Workflow

1. Inspect the requested feature, local data flows, configured services, entitlements, Info.plist files, privacy manifests and dependency inventory. Read existing credential handling without printing secrets.
2. Read [credentials and data](references/credentials-and-data.md) for session, Keychain and protection decisions; read [privacy and transport](references/privacy-and-transport.md) for evidence-based declarations, permissions, ATS and verification.
3. Define the concrete exposure and desired behavior. Make the smallest fix that preserves authentication and background requirements. Use platform storage and trust behavior; document any intentional tradeoff.
4. Update code, actual target resources and tests together. Tie declarations to observed collection/API use and declared product behavior. When a policy fact is missing, identify it precisely and continue independent code work; do not fabricate a claim.
5. Verify success and denied/expired/revoked paths, device lock/background behavior where relevant, log redaction and packaged resources. Separate static review from device results and from legal/compliance judgments.

## Boundaries and output

Do not store server secrets in a client, disable TLS validation to fix a connection, invent an approved required-reason API code, or infer tracking practices from an SDK name. Certificate pinning is an explicit design choice with rotation and recovery obligations, not a default hardening step.

Use the user's existing provider and authorization scope. This skill does not certify security or guarantee App Store approval. Finish with the actual fix, supporting evidence, checks and remaining product-policy decisions. See [source map](../../docs/source-map.md).
