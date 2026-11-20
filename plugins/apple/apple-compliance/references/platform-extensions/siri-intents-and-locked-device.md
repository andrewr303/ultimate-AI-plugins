# Verify Siri and App Intent actions at the authentication boundary

## Define the action people expect

Describe the user-visible task, inputs, output and account state for each Siri/Shortcuts/App Intent integration. The reviewed SiriKit and Shortcuts guideline expects relevant intents that the app can handle, vocabulary related to the app, and a direct route to fulfillment without inserted advertising. It is not permission to register unrelated phrases or route every request through marketing screens.

Inspect the actual intent type and installed SDK. SiriKit and App Intents APIs are not interchangeable simply because both can surface through Siri. Use the implementation and current documentation for the selected platform rather than copying an unavailable symbol or old plist recipe from another integration.

## Authentication is explicit

The reviewed AppIntent `authenticationPolicy` documentation says its default allows execution without authentication, including when the device is locked. Evaluate whether each action or returned value is appropriate in that state. A sensitive action needs a deliberate supported policy and domain/backend authorization; opening the main app's login screen somewhere else is not proof that the intent action is protected.

Collect the action's side effects, data sensitivity, account/tenant mapping, required permissions, current session and lock-state behavior. Distinguish device authentication from server access. A successful local authentication does not grant access to another account's data, and a cached token does not establish that the action is still authorized.

## Workflow

1. Map every registered action and phrase to an actual supported app task.
2. Validate parameters and entity lookup, including deleted or inaccessible entities.
3. Choose the supported authentication/foreground policy appropriate to the action and output; verify it in the actual SDK and runtime.
4. Recheck account/domain authorization at execution time, including after sign-out, revocation or account switching.
5. Bound background/network work and expose an honest recoverable result when the task cannot finish.
6. Provide review instructions that show how the intended action, authentication and fallback can be exercised.

A public, harmless query may appropriately work while locked; do not require authentication universally if the product and supported platform semantics do not need it. Conversely, avoid treating the default policy as evidence that private data or destructive operations are safe to expose. Base the choice on the actual operation and constraints.

## Verification matrix

Test unlocked and locked execution, no account, expired/revoked session, wrong account/tenant, a deleted entity, denied permission, missing network and repeated invocation. Use controlled synthetic state. A backend mutation should handle duplicate or uncertain execution according to its real idempotency/reconciliation design; a timeout does not prove nothing happened.

Verify vocabulary and disambiguation reflect actual functionality. Do not ask a clarifying question or open a promotional page merely to increase engagement. A response that claims success while the authorized server action failed is a defect, even if Siri accepted the intent invocation.

## Record the result

Document the SDK/platform, action, policy, expected lock-state behavior, domain check and observed outcome. A demonstrated unauthenticated sensitive action, wrong-account access or misleading result is a blocker. Unknown covers untested runtime policy or unresolved sensitivity/authorization facts. Not applicable requires an actual absence of this action/surface. Satisfied means the particular integration was demonstrated, not that all voice or platform behavior is certified.

Keep tokens, voice transcripts and private action parameters out of public evidence. Source or static tests can establish parameter/handler logic, but only suitable platform evidence can establish actual lock-state presentation and authentication behavior.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_appintent_authentication` — [authenticationPolicy](https://developer.apple.com/documentation/appintents/appintent/authenticationpolicy)
- `src_policy_purpose_strings` — [5.1.1(ii) - Write clear purpose strings - Guideline reference - App Review - Help - Apple Developer](https://developer.apple.com/help/app-review/guideline-reference/5-1-1-purpose-strings)
- `src_policy_complete_review` — [Provide information for a complete review - Before submitting for review - App Review - Help - Apple Developer](https://developer.apple.com/help/app-review/before-submitting-for-review/complete-review)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
