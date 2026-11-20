# Browser integration reference

Research checked 2026-11-03. Recheck official documentation and the installed browser/Xcode versions when implementing. Engineering recommendations below are design guidance, not browser guarantees.

## Verified Chrome native messaging facts

Chrome starts a separate host process. The host manifest uses `type: "stdio"`, an absolute executable `path` on macOS, and exact `allowed_origins` entries without wildcards. The extension needs `nativeMessaging`; content scripts must relay through extension pages or the worker. Messages are UTF-8 JSON, preceded by a four-byte native-endian byte count. Host-to-browser messages are limited to 1 MB; browser-to-host messages to 64 MiB. `connectNative` retains a host for the port lifetime; `sendNativeMessage` starts a host per request and uses its first reply. Keep logs off stdout.

Default user-specific manifest paths:

| Browser | Directory under `~/Library/Application Support/` |
| --- | --- |
| Google Chrome | `Google/Chrome/NativeMessagingHosts/` |
| Chrome for Testing, Chrome 146+ | `Google/ChromeForTesting/NativeMessagingHosts/` |
| Chromium | `Chromium/NativeMessagingHosts/` |

The filename is `<host-name>.json`. Custom browser user-data directories can change user-level lookup. Verify other browsers separately. Chrome for Testing before 146 used Chrome's locations. Production and unpacked extension IDs may differ.

Source: [Chrome native messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging), opened directly; page updated 2026-09-16.

## Manifest V3 durability

Service worker globals disappear when it terminates. Use durable storage rather than an in-memory queue. A native connection can extend worker lifetime, but disconnects and shutdown remain possible. Choose browser minimum versions explicitly and test restarts. Avoid keeping a worker alive solely to hide missing persistence.

Source: [Chrome service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle), opened directly.

## Capture and permissions

Use the existing capture method where possible. `captureVisibleTab` captures the visible tab, not an entire scrolling document. `activeTab` provides temporary host access following user invocation. Full-page capture needs a separately tested strategy for scrolling, sticky elements, lazy loading, zoom, multi-monitor scale and changing page content. Do not add broad site permissions just for convenience. Restricted pages and file URLs have distinct behavior; test rather than inventing support.

Source: [Chrome tabs API](https://developer.chrome.com/docs/extensions/reference/api/tabs#method-captureVisibleTab), opened directly. Native image import and native screen capture are different operations; verify the actual native capture API before adding TCC requirements.

## Installation design

Recommended implementation:

1. Put the native host executable inside the signed app or another stable, signed product location. Resolve actual installed paths; JSON cannot expand `~`, environment variables, or shell expressions.
2. Write the per-user host manifest as a deliberate user-facing integration action. Render JSON with a JSON library, not shell interpolation. Check the destination owner and file mode, use atomic writes and reject symlink surprises. Do not modify another product's host registration.
3. Reconcile the manifest when the app moves or upgrades. Running the host from a development checkout is not a release installation mechanism. Test app translocation, `/Applications` installation, spaces and Unicode in paths, upgrades and uninstall.
4. Maintain a small installation record listing files created by this product. Remove only those files on uninstall; preserve or offer export of captures. Do not erase browser profiles or all `NativeMessagingHosts` entries.
5. A sandboxed store app's ability to install external Chrome registrations needs a concrete supported installation design. Validate the selected distribution channel before implementation. Do not assume a sandbox exception, Safari App Group, or universal entitlement grants arbitrary access to Chrome's support folders.

Example manifest template, requiring real values before installation:

```json
{
  "name": "com.example.clipper",
  "description": "Clipper companion bridge",
  "path": "/Applications/Clipper.app/Contents/MacOS/ClipperNativeHost",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://REPLACE_WITH_VERIFIED_EXTENSION_ID/"]
}
```

This is a template, not an installable manifest. Do not use its placeholder identity.

## Receiver security and boundaries

Treat allowlists as browser routing restrictions, not proof against a hostile process running under the same user. Chromium documents that a locally loaded extension may reuse an ID and another binary may launch a native host. Define the threat model honestly; use additional pairing/authentication when the product's risk requires it. Never embed a reusable production secret in extension source or claim this defeats local account compromise.

Source: [Chromium extensions security FAQ](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/extensions/docs/security_faq.md), official source/search excerpts; recheck native messaging section when choosing an authentication design.

Recommended design: a narrow import API with schema/size validation; same-user service isolation; code-identity validation for a privileged or cross-process receiver; no command execution or general file browsing. Authorize sensitive operations independently. Keep capture bytes, URLs and page titles out of routine diagnostics.

If using loopback HTTP instead, provide explicit origin checks, anti-CSRF protections, short-lived pairing credentials, replay protection, strict body limits, and bind only the needed loopback addresses. Account for DNS rebinding, other local clients and browser permission changes. CORS alone is not authentication. Custom URL schemes are suitable for a bounded launch/deep-link flow, not large screenshots or embedded secrets. Prefer native messaging when it fits.

## Safari is a separate adapter

Apple's current packaging guide calls the tool `safari-web-extension-packager`; it was previously `safari-web-extension-converter`. Detect the available tool with `xcrun --find` and inspect its `--help` before choosing flags. Generate into a new destination and preserve the Chrome source/build. Assess unsupported APIs instead of deleting warnings. Keep browser-specific manifest transformations reproducible.

Sources: [Packaging a web extension for Safari](https://developer.apple.com/documentation/safariservices/packaging-a-web-extension-for-safari) and [Safari extensions](https://developer.apple.com/safari/extensions/). Apple's documentation HTML required JavaScript in this research tool; the tool rename was available in the official search excerpt. Verify exact flags against the installed tool.

Safari web extensions use an app extension handler and the containing app ecosystem for native messaging. Use the platform's actual APIs and App Groups where appropriate for entitled targets; do not install a Chrome native-host manifest for Safari. Preserve profile identity when segregating clips. Safari packaging gives a container app, but the organizer UI, receiver, persistence and background behavior still need implementation.

Source: [Messaging between the app and JavaScript in a Safari web extension](https://developer.apple.com/documentation/safariservices/messaging-between-the-app-and-javascript-in-a-safari-web-extension), official search excerpt; full Markdown fetch was unsupported by this research tool. Verify method signatures in Xcode documentation. Do not assume Chrome's wire format, transport limits, or host lifecycle apply to Safari.

## Diagnostic sequence

1. Confirm browser/version, extension ID, host name, manifest lookup path and JSON validity. Check the registered executable exists, is executable, is signed as intended and has the right architecture.
2. Connect from the extension worker, handle `runtime.lastError` or rejected promises and inspect disconnects. Report absent host, forbidden origin, host launch failure and incompatible protocol distinctly.
3. Test the framing codec against partial reads and Unicode byte lengths. Ensure every stdout byte belongs to a protocol frame. Write useful bounded, redacted diagnostics to stderr/unified logging.
4. Verify the receiver's readiness and durable commit separately from successful browser-host connection. Trace using request/item IDs, without capture content.
5. Reproduce with a clean browser profile and installed app. Developer IDs, local paths, Terminal environment and a running Xcode app can conceal release defects.
