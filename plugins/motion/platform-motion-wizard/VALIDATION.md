# Validation notes

This document describes the package's verification contract. The release evidence is recorded in validation/release-checks.json and validation/lab-results.json.

## What local validation checks

- Portable manifest, Claude compatibility identity, skill frontmatter and names, optional OpenAI metadata, assets, contained local references and files.
- Exact preservation of the supplied skill, transcript, original icon, and archived agent metadata using SHA-256 records.
- Source and claim ledger references, independent-author metadata, and explicit manual-mode status. This checks data integrity; source review is still a human/agent responsibility.
- Valid claim review status and risk classification; a supported executable claim requires confirmed execution proof. Unresolved observations cannot silently bypass the status contract.
- Routing fixture structure, unique IDs, required prompt/acceptance text and references to actual skill names. These checks do not execute agent routing.
- ZIP containment, traversal/symlink/duplicate entries, intended components and reproducible package contents.
- Regression fixtures with malformed packages, changed preserved bytes, bad metadata and unsafe archives.

The validation script is an authored structural checker, not an official host validator or an automated factual research gate. No verified_claims.json is produced.

## Executable controller evidence

The original scalar presentation controller has deterministic tests using Node's built-in runner and controllable animation handles. They deliver obsolete fulfillment and rejection after replacement, sample intermediate presentation before retargeting, establish an active effect before live reduction, and exercise immediate endpoints, failure, idempotent release and disposal without later presentation writes. Unexpected failures remain diagnostic; reporting callbacks must not mutate a captured view without their own ownership guard.

```sh
node --test tests/test_motion_lifecycle.cjs
```

These are state and ownership tests. They do not measure animation comfort, frame rate or native/framework integration. Node is an optional development tool, not a runtime dependency.

## Browser evidence

The lab is exercised using already-installed Playwright and Chromium on Linux. Checks cover pointer/keyboard selection; native dialog replay, Escape and focus return; active open/close/reopen retargeting; immediate details semantics; live reduced motion scoped to owned effects; actual delivered obsolete/canceled responses; failure and retry; bounded fixture queues; narrow dark/RTL layout; synthetic lifecycle cleanup; missing-WAAPI endpoints; and absence of script errors/external requests. Exact completed checks and limits are in [the browser record](validation/lab-results.json).

A portable copy of the browser check lives at tests/check_lab.py. It requires Playwright and an available Chromium browser; these are optional development tools and are not runtime dependencies of the plugin or lab. It does not install either one. Run it in an existing browser-test environment:

```sh
python tests/check_lab.py --output /absolute/path/to/evidence
```

Synthetic pagehide/pageshow events do not prove actual back-forward cache restoration. Stable screenshots were inspected for appearance; they are not timing evidence. The captured [desktop](validation/lab-desktop.png) and [narrow dark](validation/lab-mobile-dark.png) states are included for review.

Managed Chromium blocked direct file navigation with `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Direct `file://` loading is therefore unverified in this environment. The lab's documented localhost-server path was used for browser evidence; the navigation policy was not bypassed.

## Skill behavior fixtures

tests/skill-scenarios.json lists positive, mixed, negative and adversarial prompts with expected routing and acceptance. Structural validation checks those fixtures, including new delivered-stale-response, active-effect, disposal, missing-animation and package-family cases. They remain reviewer fixtures, not a claim that an agent-host evaluation was run. Inspect them after changing descriptions/router boundaries.

## Limits

The installed Codex CLI exposes plugin management but no package-validation command. No official host package validator, native SDK build, physical mobile device, assistive-technology session, production app integration, frame-rate benchmark, host plugin installation, or public submission was performed. Research used manual source review; no automated factual-gate PASS is claimed. The plugin is a ZIP/source deliverable. Implementation skills require the missing checks in the actual product when relevant.
