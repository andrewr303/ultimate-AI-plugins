---
name: signing-entitlements
description: "Use for Apple signing identity/profile/entitlement mismatches, exported-artifact verification and controlled CI signing. Do not revoke shared assets, rotate credentials, broaden capabilities or change distribution channels as routine cleanup."
---

# Verify signing and entitlements

First read the [operating contract](../../references/operating-contract.md). The user's current scope and authorization govern every step.

Map each executable target to its app/team/profile/capabilities and inspect the actual exported artifact. Diagnose the smallest signing mismatch, preserve the existing automatic/manual model and verify any authorized repair without exposing key material.

## Workflow

1. Inspect relevant project instructions, current app/account/artifact state and the requested endpoint. Preserve unrelated changes and existing tool/provider choices.
2. Choose only the reference needed below. Resolve current official source applicability and installed help before using changing policy or command examples.
3. Prepare concrete inputs, findings and a reviewable plan; implement reversible corrections and execute operations already authorized once their dependencies are ready. Do not ask for the same authority again.
4. On a failure, classify the cause and inspect current state before retrying any uncertain mutation. Continue independent authorized work while a dependent prerequisite is missing.
5. Verify the relevant behavior and report exact target identifiers, changes/actions, evidence, furthest observed state and material unknowns. Static checks, native loader discovery and real Apple runtime outcomes are different evidence.

## Focused references

- [Signing identity and provisioning map](../../references/signing-entitlements/signing-identity-and-profiles.md) — Diagnose the actual identity/profile/target relationship before recreating team resources.
- [Ephemeral CI signing and secret containment](../../references/signing-entitlements/ephemeral-ci-signing.md) — Make signing reproducible without retaining credentials in ordinary artifacts.
- [Verify the signed artifact and extension capabilities](../../references/signing-entitlements/artifact-entitlement-verification.md) — Tie compliance analysis to what was actually signed and exported.

## Completion boundary

Return concrete findings or completed authorized work, not a generic checklist. Keep private keys, profiles, review credentials, tester records and raw personal payloads out of public logs and commits. Never claim acceptance, certification or legal clearance beyond observed evidence. Source identifiers map to the [research source records](../../research/sources/sources.jsonl).
