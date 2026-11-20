# Primary source map

Checked 2026-11-03. Links are navigation aids; verify current version-specific
content when making an implementation decision. Search cache and live Apple
Support differed on patch releases during authoring, so no latest patch is pinned.

| Claim or question | Official source | Use |
| --- | --- | --- |
| Golden Gate is macOS 27; recent releases have different hardware support | [Apple OS versions](https://support.apple.com/en-us/109033), [Golden Gate compatibility](https://support.apple.com/en-us/127255) | Verify major/minor and supported hardware; choose the project's minimum separately |
| API changes by OS | [macOS release notes](https://developer.apple.com/documentation/macos-release-notes) | Open current selected release notes; verify SDK availability locally |
| Native app structure | [SwiftUI](https://developer.apple.com/documentation/swiftui), [AppKit](https://developer.apple.com/documentation/appkit) | Native UI and availability |
| Background helpers | [Service Management](https://developer.apple.com/documentation/servicemanagement), [SMAppService](https://developer.apple.com/documentation/servicemanagement/smappservice) | User-controlled helpers; details in background-services |
| Browser IPC | [Chrome Native messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging), [Safari web extensions](https://developer.apple.com/documentation/safariservices/safari-web-extensions) | Framing, host installation, Safari-specific packaging |
| Node runtime packaging | [Node SEA](https://nodejs.org/api/single-executable-applications.html) | Verify selected runtime's exact workflow and supported modules |
| Electron desktop security | [Electron security](https://www.electronjs.org/docs/latest/tutorial/security) | Verify current release; maintain isolation and narrow IPC |
| Tauri desktop architecture | [Tauri v2 sidecars](https://v2.tauri.app/develop/sidecar/) | Version-scoped example; detect repository major before choosing docs |
| Direct distribution | [Notarizing macOS software](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution) | Developer ID release verification |
| Store distribution | [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Current policy facts; do not equate notarization with App Store review |

For an unfamiliar API, consult its SDK declaration and compile a minimal use on
the selected Xcode SDK. A page fetched successfully is not evidence that a
particular code sample compiles or the installed app behaves correctly.
