---
name: mac-research-and-debug
description: "Use to inspect a macOS, Node.js, web, or browser-extension project before implementation; research current Apple/runtime requirements; or diagnose build, IPC, permission, background-service, signing, performance, and crash failures."
---

# Research and diagnose from evidence

Use the agent's actual research, filesystem, and terminal tools. These scripts are
supporting utilities, not automatically available tools or a remote macOS machine.

## Inspect without executing the project

Read local instructions and `git status` first. Run:

```sh
python3 <skill-directory>/scripts/inspect_project.py /absolute/project/path
```

The report lists stack evidence and command names, not script bodies or secrets.
It is heuristic; read the actual package manifests, workspace configuration,
schemes, extension manifest, data model, existing tests, and packaging before
choosing an architecture. The scanner skips symlinks, hidden/dependency/build
directories, limits traversal and input size, and never invokes project commands.

Run its portable checks with `python3 <skill-directory>/scripts/test_inspect_project.py`.

On a Mac run `sh <skill-directory>/scripts/mac_environment.sh` to collect nonsecret
OS/CPU/Xcode/SDK evidence. Do not assume the Linux environment can compile AppKit,
exercise TCC, start login helpers, or prove Gatekeeper acceptance.

## Research before depending on platform facts

1. Check installed dependency versions, deployment target, Xcode and SDK. Verify
   official release notes and documentation for those versions, not just latest.
2. Use Apple documentation and SDK availability declarations for native APIs;
   Chrome/Safari official docs for extension behavior; Node, Electron and Tauri
   official docs for packaging/runtime behavior. Reopen sources when details are
   volatile, documentation conflicts, or a previously checked page is stale.
3. Save a small evidence table: claim, URL, checked date, relevant version, decision,
   and uncertainty. Separate current facts, project decisions, and hypotheses.
   Reconcile search snippets against opened source; avoid guessed flags or APIs.
4. If sources or an actual Mac are unavailable, continue with verifiable work,
   explain the concrete gap, and supply commands/acceptance steps for that gap.

## Diagnose the layer that fails

Reproduce a minimal failure, capture the first actionable error, form a hypothesis,
and change one causal factor. Add a regression test only when it prevents recurrence.

| Symptom | Inspect |
| --- | --- |
| Works in Terminal, fails as installed app | Bundle paths, executable permissions, cwd, environment/PATH, bundled runtime, signing, architecture, sandbox and resource access |
| Extension cannot reach app | Native host manifest and exact extension ID, absolute executable, executable bit, frame codec, stdout contamination, browser/profile-specific installation |
| Worker disappears | Window/app lifetime, process owner, exit status, service status, user login/background permission, bounded retries and logs |
| Screen/file access fails | Which process requests permission, relevant TCC category, entitlements/usage descriptions, denial recovery and user-selected access |
| App rejected or won't launch | Exact installed artifact, nested signatures, entitlements, Hardened Runtime, notarization log, quarantine and Gatekeeper assessment |
| CPU/memory/energy problem | Instruments Time Profiler/Allocations/Energy, task duration, event-driven wakeups, cancellation, image decode/downsample/OCR work off main actor |
| UI freezes or data races | Main actor blocking, concurrency boundaries, Swift strict-concurrency diagnostics for selected compiler, independent database writers |

Do not run broad reset commands such as TCC resets, delete a user's library,
disable SIP/Gatekeeper, or kill unrelated services as a diagnostic shortcut.
Use OSLog with privacy-aware fields, correlation IDs and bounded retention;
exclude screenshots, credentials, full URLs with secrets, and message payloads.

Load [background-services](../background-services/SKILL.md),
[browser-companion](../browser-companion/SKILL.md), or
[mac-release](../mac-release/SKILL.md) for detailed work at those layers.

Current source entry points and research policy are in
[source-map.md](references/source-map.md).
