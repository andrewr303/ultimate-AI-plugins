---
name: mac-distribution
description: "Use for Mac App Store versus Developer ID distribution, Hardened Runtime/App Sandbox, notarization diagnostics and stapling. Do not treat a notary ticket as App Store approval, copy Electron entitlements into unrelated apps, or generalize this lane to iOS review."
---

# Prepare the selected Mac distribution lane

First read the [operating contract](../../references/operating-contract.md). The user's current scope and authorization govern every step.

Identify the actual Mac channel, runtime/helper topology and final artifact. Verify the relevant signing/control lane, preserve notarization identity and complete authorized ticket/packaging checks with honest Mac-runtime limits.

## Workflow

1. Inspect relevant project instructions, current app/account/artifact state and the requested endpoint. Preserve unrelated changes and existing tool/provider choices.
2. Choose only the reference needed below. Resolve current official source applicability and installed help before using changing policy or command examples.
3. Prepare concrete inputs, findings and a reviewable plan; implement reversible corrections and execute operations already authorized once their dependencies are ready. Do not ask for the same authority again.
4. On a failure, classify the cause and inspect current state before retrying any uncertain mutation. Continue independent authorized work while a dependent prerequisite is missing.
5. Verify the relevant behavior and report exact target identifiers, changes/actions, evidence, furthest observed state and material unknowns. Static checks, native loader discovery and real Apple runtime outcomes are different evidence.

## Focused references

- [Choose the Mac App Store or direct distribution lane](../../references/mac-distribution/choose-distribution-lane.md) — Keep code signing and policy requirements attached to the actual delivery channel.
- [Notary submission, wait and diagnostics](../../references/mac-distribution/notary-submit-and-diagnostics.md) — Submit the intended signed artifact and interpret the service result correctly.
- [Staple and verify the actual final distribution artifact](../../references/mac-distribution/staple-verify-final-artifact.md) — Complete offline ticket availability and preserve artifact identity after packaging.

## Completion boundary

Return concrete findings or completed authorized work, not a generic checklist. Keep private keys, profiles, review credentials, tester records and raw personal payloads out of public logs and commits. Never claim acceptance, certification or legal clearance beyond observed evidence. Source identifiers map to the [research source records](../../research/sources/sources.jsonl).
