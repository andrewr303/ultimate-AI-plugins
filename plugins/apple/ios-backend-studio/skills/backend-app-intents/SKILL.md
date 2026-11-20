---
name: backend-app-intents
description: "Use when exposing existing app/backend actions or entities through App Intents, Siri, Shortcuts or optional Apple Intelligence schemas. Preserve stable saved-shortcut contracts and server authorization; do not invoke for a generic chatbot, cosmetic Siri button design or unsupported schema adoption."
---

# App Intents and Siri domain adapters

First read the [operating contract](../../references/operating-contract.md).

## Workflow

1. Identify the real domain action, typed inputs/entity lookup, existing account/session service, selected SDK and execution target before choosing protocols or schema macros.
2. Keep stable entity IDs and localized intent metadata separate from internal persistence/UI objects. Use permission-aware query and perform paths, with deliberate ambiguity/missing-entity behavior.
3. Call the same domain service as app UI, then enforce current backend authorization and idempotency where needed. Local device authentication and intent discovery do not grant server privileges.
4. Adopt optional schemas only when the domain meaning and SDK match. Preserve older saved shortcuts through compatible parameters or an intentional staged transition.
5. Test denied/expired auth, account switches, stale entity suggestions, duplicate/cancelled actions and UI-required execution. Verify generated metadata and actual Siri/Shortcuts behavior in the appropriate environment.

## Load the relevant reference

- [Typed commands and service adapters](../../references/app-intents/typed-domain-commands.md)
- [Entities, discovery and schemas](../../references/app-intents/entities-and-discovery.md)
- [Execution, authentication and cancellation](../../references/app-intents/execution-and-authorization.md)

## Complete with evidence

Return the intent/entity-to-endpoint map, process and authorization choices, compatibility/fallback behavior, tests and native invocation limits. A build or mocked perform test does not establish a Siri conversation.

Source observations and availability are recorded in the references and [source registry](../../research/sources/sources.jsonl). Multiple Apple pages do not count as independent author corroboration.
