---
name: ios-navigation
description: "Implement or review iOS navigation paths, independent tab/scene histories, sheets, editor presentation, deep links, or state restoration in SwiftUI/UIKit. Use ios-swiftui for ordinary view composition and ios-design for visual layout. Do not introduce a global router, replace an established navigation framework, or add external link capabilities without a task need."
---

# Navigation and presentation

Read the [operating contract](../ios-development/references/operating-contract.md) first. Discover current navigation ownership, supported runtimes and the requested entry-to-destination behavior.

## Inputs

Find root tabs/scenes, path owners, presentation bindings, destination mapping, URL entrypoints and any restoration format. Identify authentication/account boundaries and unsaved editing state. State the expected Back, Cancel, Save and re-entry behavior before editing.

## Workflow

1. Model routes as lightweight stable data using [route and presentation state](references/route-and-presentation-state.md). Keep each path with the scene/tab/feature that owns its lifetime.
2. Wire destination mapping at the intended navigation boundary. Prefer the project's established approach, including UIKit coordinators when already in use. Add centralized routing only when distributed callers need it.
3. Present data-dependent sheets from their payload state. Define identity, dismissal, nested navigation and draft semantics. Avoid independent flags that allow contradictory presentations.
4. For URLs or restoration, use [external routing and restoration](references/external-routing-and-restoration.md). Validate input before changing the path; authorization belongs at the destination/service boundary as well as UI routing.
5. Test successful and rejected routes, back behavior, tab independence, account changes and unsaved edits. Verify runtime interactions on available Apple tools; otherwise label static checks and provide targeted remaining cases.

## Failures and outputs

- Reopening or switching a modal must show the correct payload rather than stale state.
- A route restored after logout must not reveal another account's cached content.
- Unknown or malformed external routes need a safe in-app fallback, not a crash or silent privileged action.
- Do not log full sensitive URLs, tokens or user payloads.
- Do not mistake a newly constructed view for a stable navigation identity.

Return the route contract, changed owners/callers, fixtures actually exercised and unresolved runtime behavior. See [source map](../../docs/source-map.md).
