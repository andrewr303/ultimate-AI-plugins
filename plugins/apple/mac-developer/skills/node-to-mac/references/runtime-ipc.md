# Bundled runtimes and process boundaries

Research checked: 2026-11-03. Match all API/configuration examples to the selected installed major. The v2 Tauri permission identifiers below are v2-specific. The following boundary protocol is an application design, not a platform standard.

## Bundled Node

Choose one supported approach and prove it against the real dependency graph:

- Ship a supported Node executable plus a production JS bundle, assets, and required dependencies inside the `.app`. Include required license notices. Treat runtime patching as part of the app's update cycle.
- Evaluate Node Single Executable Applications (SEA) for a self-contained helper. Check the selected Node version's module, asset, native-addon, and code-cache support. Build and test the actual executable before committing to this path; a successful JS bundle is insufficient.
- Use Electron's own runtime in the correct Electron process when choosing Electron. A separate Node runtime is unnecessary unless a distinct host requirement justifies it.

Do not use abandoned `pkg` recipes as a default. Do not remove all signatures from an already completed release to make injection work: follow the selected SEA preparation steps, then produce the final proper signature after modifications. A Mac distribution artifact must include a compatible executable and native dependencies for every advertised architecture. Rebuild Electron native modules for its ABI and selected architecture; plain Node success does not prove Electron compatibility.

Find resources from `Bundle` APIs, Electron's packaging/resource APIs, or Tauri's resource resolver. Launch `Process.executableURL` with an argument array and pipe handles, not `sh -c` or a concatenated command. Set an intentional writable working directory and minimal environment. Do not pass secrets on a command line. In native code, a Node process is not automatically an NSXPC service: use a native XPC adapter or another explicit validated protocol.

## IPC contract for shared logic

For stdio, a reasonable starting contract is UTF-8 JSON with a documented framing scheme and a small application-specific maximum. Example logical payloads:

```json
{"v":1,"id":"request-uuid","method":"organizeClip","params":{"clipId":"clip-uuid"}}
{"v":1,"id":"request-uuid","ok":true,"result":{"collectionId":"inbox"}}
```

Choose one framing scheme and implement incremental parsing on both ends. Length-prefixed binary data and browser native messaging each have separate framing rules; do not conflate them with newline-delimited JSON. Validate version, method allowlist, field types, total bytes, nesting, and request identity before dispatch. Limit concurrent work and return structured errors with retryability. Separate protocol stdout from diagnostic stderr. Stream logs with privacy redaction. Handle partial reads, unexpected EOF, malformed responses, backpressure, timeout, cancellation, and repeated requests. Large screenshots should be attachments or bounded chunks with hashes, not unbounded JSON strings.

On process restart, recover from a persistent job queue and deduplicate logical operation IDs. A transport acknowledgement is not a durable database commit. Coordinate a single service owner and avoid spawning one worker per window. If the UI closes, define whether work stops, drains, or transfers to a user-enabled service; framework process defaults are not a background service contract.

Prefer local IPC over a server when sufficient. If a localhost server is necessary, bind only loopback, generate per-install/session authentication, validate Host and Origin as applicable, protect every endpoint, and impose body/concurrency/time limits. CORS is not authentication; loopback is reachable by other local processes and potentially web content. Use dynamic ports or a deliberate rendezvous rather than a shared hardcoded development port. Do not open a LAN listener merely to connect local components.

## Electron implementation

Use current maintained Electron with sandboxed renderers, `nodeIntegration: false`, and `contextIsolation: true`. Keep privileged logic in main or a narrowly scoped worker. A preload should expose one purpose-built function per capability through `contextBridge`, with validated inputs and validated IPC senders. Never expose raw `ipcRenderer`, a generic filesystem API, command execution, or event objects. Restrict navigation, new windows, permissions and external URL schemes; apply CSP. Treat captured websites and clipped HTML as untrusted. Persist plain data; sanitize previews and never load a screenshot's accompanying HTML into a privileged renderer.

Test the packaged file/resource paths, production CSP, deep links, menu/tray semantics, and instance policy. Keep background execution opt-in and use current macOS service APIs if execution must survive the application process.

## Tauri implementation

Use the installed major's generated schemas. In v2, declare each binary under `bundle.externalBin`, prepare correctly suffixed per-target executables, and constrain the shell plugin to that exact sidecar and allowed arguments. `shell:allow-execute` and `shell:allow-spawn` authorize different operations. Scope capabilities to the required window/webview and avoid arbitrary argument wildcards. Permissions from overlapping capabilities accumulate. Custom Rust commands also need validation and deliberate access scope; do not assume a narrow plugin capability secures every custom command. Never grant remote content broad native privileges.

## Official sources

- [Node release support](https://nodejs.org/en/about/previous-releases): select a currently supported production LTS and pin the chosen runtime.
- [Node SEA](https://nodejs.org/api/single-executable-applications.html): version-dependent packaging feature under active development; current docs include bundled script/assets and native-addon limitations.
- [Electron native modules](https://www.electronjs.org/docs/latest/tutorial/using-native-node-modules): Electron ABI can differ from standalone Node, requiring rebuilds.
- [Electron security](https://www.electronjs.org/docs/latest/tutorial/security) and [context isolation](https://www.electronjs.org/docs/latest/tutorial/context-isolation): privileged bridge exposure needs restraint and validation.
- [Tauri sidecars](https://v2.tauri.app/develop/sidecar/) and [capabilities](https://v2.tauri.app/security/capabilities/): bundle configuration and operation/window scope are explicit controls.
