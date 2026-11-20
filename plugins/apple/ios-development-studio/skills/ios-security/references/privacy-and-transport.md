# Privacy, permissions and transport

Declarations must describe actual product behavior. Establish which data is collected/transmitted, purposes, retention, tracking relationships and relevant third-party SDK behavior. A code search finds evidence but cannot decide a business-policy fact that only the product owner/provider knows. Record the missing fact precisely; do not fill it with a reassuring default.

## Privacy manifest work

Apple documents the required filename `PrivacyInfo.xcprivacy`, a property-list resource. Inspect manifests from the app and dependencies and confirm target/resource inclusion. Merely creating a file beside Package.swift does not prove it is included in an app archive. Review the actual built resources and generated privacy report where the toolchain supports it.

Separate collected-data declarations, tracking/domain declarations and required-reason API declarations. Use current official categories and approved reasons and tie each entry to observed API use and a legitimate permitted purpose. Do not copy a generic list of reasons into every app, invent a code, or assume a dependency's manifest covers the app's own usage. A valid plist is a syntax check, not proof of truthful disclosures.

Third-party SDK requirements and signatures can change. Inspect the installed dependency version and current Apple requirements when preparing a release. Adding a manifest or SDK does not automatically update App Store privacy answers or the privacy policy. Those surfaces must agree with product behavior; route actual release automation to the delivery skills.

## Permissions and capabilities

Add permission purpose strings, entitlements and background modes only for requested APIs/features. Use concrete localized explanations: what the app needs and why. Do not request all permissions at startup merely because a library can access those resources. Prefer the least broad supported access and handle denial, limitation, revocation and unavailable hardware.

Camera, microphone, media library and location flows need their own checks. A photo picker may have a different access model from direct library enumeration; inspect the chosen API rather than adding broad library permissions automatically. Static location display does not imply background location. Long-running live location is a product capability with an explicit stop path and device/background tests.

App Tracking Transparency requirements depend on actual tracking behavior. Do not infer a true/false declaration from a dependency name, and do not add tracking prompts just because analytics code exists. Verify current platform guidance and obtain the missing product facts when they change the declaration.

## ATS and server trust

Apple's App Transport Security defaults protect connections made through the URL loading system. Prefer HTTPS and fix an insecure server configuration. Do not resolve a TLS failure by accepting all certificates, suppressing trust evaluation or adding a broad NSAllowsArbitraryLoads exception. Diagnose hostname, trust chain, expiry and server protocol configuration with the authorized endpoint.

If a legitimate legacy integration requires an exception, scope it to the smallest supported domain/policy, document the actual need and verify behavior on the target OS. ATS does not automatically secure every lower-level networking API; using Network/BSD sockets shifts responsibility to the implementation. Keep system TLS verification enabled.

Certificate/public-key pinning is optional architecture, not a baseline change. It can prevent legitimate connections during rotations and recovery. Implement only for an explicit requirement with backup/rotation strategy, test coverage, correct trust evaluation and a documented recovery plan. Never substitute pinning for authorization or secure credential storage.

## Practical verification

- Parse modified Info.plist/privacy manifests and verify target resource membership.
- Inspect signed entitlements and archived privacy resources for the actual configuration.
- Exercise denied/limited/revoked permissions and app settings changes.
- Confirm logs and diagnostics redact tokens, personal payloads and signed URLs.
- Test valid TLS and expected rejection paths using an authorized controlled endpoint.
- Verify logout/account changes clear only the intended private caches and requests.

Report evidence and remaining policy facts separately. Do not claim App Store approval, legal compliance or a complete security audit from these checks.

Sources inspected: Apple [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files), [Preventing insecure network connections](https://developer.apple.com/documentation/security/preventing-insecure-network-connections), and the uploaded Chat permission/media integration documentation. Fresh policy details must be verified at release time. See [source map](../../../docs/source-map.md).
