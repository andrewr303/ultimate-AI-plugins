# Reproducible Mac release procedure

Research checked: 2026-11-03. Recheck Apple release requirements and the repository's selected framework/SDK documentation at release time. Commands below are templates: replace paths, scheme names, and keychain profile with verified project values. Do not replace signing placeholders with invented identities or print secrets.

## Channel constraints

| Decision | Direct distribution | Mac App Store |
| --- | --- | --- |
| Identity and acceptance | Developer ID signature; notarization and Gatekeeper checks | Store distribution signing/provisioning and App Review |
| Background execution | Explicit user control and correctly registered service | Also satisfy Store consent, sandbox and packaging requirements |
| Chrome native host | User-scoped host manifest/installer may be designed and verified | Shared-location/native-host installation requires a concrete permitted design; do not assume it fits a self-contained sandboxed app |
| Privileged daemon | Only if capability requires privilege, with explicit authorization and secure IPC | Store rules prohibit requesting root escalation |
| Updates | Authenticated signed updater or user-managed replacement | Store update mechanism |

These constraints are a design screen, not a legal or App Review approval. A Node runtime is not automatically forbidden in a Store app, but executable placement, sandbox behavior, added/downloaded code, and external installation must meet actual rules. Choose the channel before introducing an architecture that depends on privileges or writing elsewhere.

## Baseline inventory

Read the current Apple compatibility pages and capture `sw_vers`, `uname -m`, `xcodebuild -version`, selected SDK, deployment target, schemes, architectures and signing settings on the Mac builder. Avoid dumping entire environments. Query only the required nonsecret fields. Apple's current Golden Gate compatibility page covers Apple silicon; the Tahoe compatibility list includes certain Intel machines. Building a universal app is optional when the product intentionally supports earlier Intel Macs. A universal outer executable is insufficient if an embedded runtime, `.node`, dylib, helper, or binary asset lacks its slice. Never promise Rosetta support indefinitely.

Example discovery, with actual project paths:

```sh
xcodebuild -list -project apps/macos/Product.xcodeproj
xcodebuild -showdestinations -project apps/macos/Product.xcodeproj -scheme Product
xcodebuild -project apps/macos/Product.xcodeproj -scheme Product -configuration Debug build
```

Choose `-workspace` for a real workspace instead of `-project`; do not pass both indiscriminately. Use an available destination for the selected scheme's tests. For Electron/Tauri use the repository's pinned package manager and documented package/build script, not a global latest tool. Build native modules and assets for the selected target. An unsigned compile check can be useful during development but must be labeled as such and kept separate from release signing.

## Sign deliberately

Inventory every executable and Mach-O library before packaging, including frameworks, Node, XPC services, login items and agent executables. Use the framework's supported signing integration where available. With custom signing, sign the innermost items first, each with the correct identity, bundle identifier and minimal entitlements, then enclosing bundles. Put code in supported bundle locations. Avoid `codesign --deep` as a signing strategy: it can miss misplaced code or apply inappropriate entitlements. `--deep` is useful during verification.

For a Developer ID release, apply Hardened Runtime and secure timestamp to the relevant executables. Remove development `get-task-allow`. Validate any JIT, executable memory, or library validation exceptions against the actual Node/Electron version; never copy a large entitlement list blindly. Sandbox and Hardened Runtime are distinct. An App Store helper's sandbox inheritance and entitlements require their own design.

After the final content/signature is complete, run on macOS:

```sh
codesign --verify --deep --strict --verbose=2 dist/Product.app
codesign --display --entitlements :- dist/Product.app
file dist/Product.app/Contents/MacOS/Product
lipo -archs dist/Product.app/Contents/MacOS/Product
```

Inspect entitlements and architectures for embedded code too; the outer app check does not document every helper's settings. Keep entitlement output to public metadata and avoid logging identity private keys. Never modify code, plist, assets or entitlements after signing without rebuilding and signing again.

## Notarize and package

Use current `notarytool` rather than legacy `altool`. Credentials must be set up through the user's approved keychain/CI secret mechanism; use an existing verified keychain profile without echoing its secrets. If absent, report the missing credential setup and preserve the built artifact. A development/ad hoc certificate is not a substitute for Developer ID distribution.

One app ZIP workflow after signing:

```sh
ditto -c -k --keepParent dist/Product.app dist/Product-notary.zip
xcrun notarytool submit dist/Product-notary.zip --keychain-profile product-notary --wait
xcrun stapler staple dist/Product.app
xcrun stapler validate dist/Product.app
```

Require accepted status before stapling. For rejection, retrieve the notary log using the returned submission ID, identify the specific nested item and fix it. Preserve the submission ID and result. Recreate the user-facing ZIP from the stapled app. ZIP itself cannot be stapled. For a DMG/PKG workflow, use the channel's correct identities and notarize the actual intended container; apply Apple's outermost-container guidance. Do not sign installer packages with a Developer ID Application identity in place of Developer ID Installer.

Assess direct-distribution app policy on a supported Mac using the currently available tool:

```sh
syspolicy_check distribution dist/Product.app
spctl --assess --type execute --verbose=4 dist/Product.app
```

Use `syspolicy_check` where supported; `spctl` is supplementary policy evidence, not a runtime test. Test a genuinely downloaded/quarantined final artifact on a clean account or clean Mac using normal install steps. Do not strip quarantine, disable Gatekeeper, or tell users to bypass security as the release fix. Check app translocation/path assumptions, runtime/helper execution, permissions, offline launch, service registration and actual user operations.

## Release and update evidence

Record artifact version and SHA-256, bundle IDs, source revision, builder/SDK, dependency lockfiles, architectures, OS test matrix, commands and results, signing/notary status, unresolved issues and reproduction. Leave credentials out. Give an explicit list of checks not run. Confirm original app/CLI/extension checks when converting a product.

For updates, preserve stable identities and service labels, verify downloaded update signatures before execution, stop/drain helpers, perform recoverable data migrations, replace the app atomically through supported tooling, restart appropriate services, and support rollback only when the data format permits it. Avoid two installed copies competing for the same service/database. Uninstall should unregister background components, remove only this product's host manifests/helpers, offer data export, and clearly separate removing app binaries from deleting user data.

## Official sources

- [Golden Gate compatibility](https://support.apple.com/en-us/127255) and [Tahoe compatibility](https://support.apple.com/en-ie/122867): platform/CPU support must be tied to a specific OS.
- [Creating distribution-signed Mac code](https://developer.apple.com/documentation/xcode/creating-distribution-signed-code-for-the-mac): signing identities, executable treatment and nested-code handling.
- [Notarizing Mac software](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution) and [notarization issues](https://developer.apple.com/documentation/security/resolving-common-notarization-issues): requirements and failure diagnostics.
- [Packaging Mac software](https://developer.apple.com/documentation/xcode/packaging-mac-software-for-distribution): artifact/container workflow.
- [TN3161 code signing certificates](https://developer.apple.com/documentation/technotes/tn3161-inside-code-signing-certificates): verification and direct-distribution policy assessment.
- [App Review Guidelines 2.4.5](https://developer.apple.com/app-store/review/guidelines/#hardware-compatibility): Mac sandbox, self-contained installation, consent, privilege and update rules.
- [Electron signing](https://www.electronjs.org/docs/latest/tutorial/code-signing): supported Electron signing/notarization integration on macOS.
- [Tauri macOS signing](https://v2.tauri.app/distribute/sign/macos/): use matching installed-major tooling and configured secrets.
