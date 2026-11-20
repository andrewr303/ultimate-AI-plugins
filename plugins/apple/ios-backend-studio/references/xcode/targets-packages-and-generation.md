# Xcode targets, Swift packages and generated clients

Apply the [operating contract](../operating-contract.md). Load this guide for the concrete boundary it addresses; it does not authorize installs, production changes or external collection.

## Discover the target topology

Identify the Xcode project/workspace, shared schemes, build configurations, selected Xcode and Swift settings, package graph and actual app/extension targets. A WidgetKit extension, App Intents extension and main app may share domain values but run with different availability, process and entitlement boundaries. A successful shared package build does not prove every app target includes the generated client correctly.

Determine whether the project is hand-maintained, generated from XcodeGen/Tuist or primarily a Swift package. Change the owned source artifact. Do not patch a generated project as the lasting fix or run generation over a hand-maintained app just to match a reference. Preserve target identifiers, signing and project-specific build phases.

## Separate generator host and generated runtime

Inspect the resolved Swift OpenAPI generator/runtime/transport releases and their package manifests/documentation. The compiler needed to run a plugin, Swift language mode of a target, deployment availability of generated/runtime APIs and transport behavior are independent constraints. Main-branch examples or current website docs do not set the user's minimum OS/compiler.

Keep contract generation inputs and generated output clearly owned. Shared modules should expose only the domain/transport behavior each consumer needs. Avoid linking app UI, singleton session stores, credentials or long-lived services into an extension merely because the generated API type is convenient. Pass deliberate snapshots or purpose-specific adapters where extension lifecycle requires them.

## Implementation sequence

1. Map each API-consuming target to its generated code, runtime, transport, auth context and package product dependencies. Include configurations used in CI and release.
2. Change the authoritative API description or generator settings, not emitted declarations alone. Generate through the existing pinned task and review the diff.
3. Ensure target membership/product dependencies include the intended generated/runtime/transport modules. Keep duplicate generated declarations from leaking across modules.
4. Build the smallest affected target and then relevant app/extension combinations. Verify availability branches under the actual selected SDK instead of raising deployment targets to silence errors.
5. Run shared payload fixtures through the actual client adapter. Test unknown status/body, authorization loss and cancellation according to the consuming target's ownership.
6. Review scheme and test-plan coverage so a green package check cannot hide a failing extension or archive configuration.

## Failure matrix

| Symptom | Check |
| --- | --- |
| Generator cannot run | Build-host tools/plugin requirements and resolved release |
| Generated source compiles only in app | Extension deployment/settings, target membership or app-only dependency |
| Duplicate/ambiguous type | Generated output ownership and module imports |
| Debug works, archive fails | Release configuration, resource/product membership and signing boundaries |
| Widget reads wrong account | Shared storage/auth snapshot boundary rather than API type generation |
| Tool asks to skip plugin validation | Inspect the actual trust/configuration issue; do not disable validation as a routine fix |

## Verification and handoff

Record Xcode/compiler versions, language/settings candidates resolved for the selected target, package revisions and the generation command. Report separate outcomes for package compile, app target, extension target, integration tests and archive. Keep diagnostics bounded and omit credentials, signing material and private payloads.

If macOS/Xcode is unavailable, finish source/schema/generation checks that are portable and state the exact pending scheme/configuration/device check. Do not pretend a Linux package validation establishes Apple SDK behavior. The result should reduce repeated setup while preserving real target boundaries.

## Sources and applicability

- [Swift Package Manager](https://docs.swift.org/latest/data/documentation/packagemanagerdocs.json) — `src_nm_swift_package_json`.
- [Introducing Swift OpenAPI Generator | Swift.org](https://www.swift.org/blog/introducing-swift-openapi-generator/) — `src_nm_swift_openapi_intro`.
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/tutorials/data/documentation/xcode/organizing-tests-to-improve-feedback.json) — `src_nm_xcode_testplans_final`.
- [Projects · Features · Guides · Tuist](https://docs.tuist.dev/en/guides/develop/projects) — `src_nm_tuist_projects`.

The [registered source records](../../research/sources/sources.jsonl) preserve exact URLs, review scope and pinned repository revisions. This guide is original synthesis of the relevant sections, not a copied source document. Verify installed help, resolved code and the target environment before applying version-sensitive APIs or commands. Source inspection does not establish runtime success, platform availability, legal clearance or complete security coverage.
