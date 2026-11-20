---
name: ios-chat
description: "Integrate and debug native SwiftUI chat screens, especially ExyteChat: domain mapping, pagination, draft sending, attachments and delivery state. Use for chat UI requests; route Expo chat to ios-expo, generic networking to ios-networking, and image pipelines to ios-images. Do not add a chat framework unless the task needs one."
---

# iOS chat

First read [the operating contract](../ios-development/references/operating-contract.md). Follow the user's existing framework and backend; this skill implements a chat feature, not an unsolicited service migration.

## Workflow

1. Inspect the target, deployment minimum, `Package.resolved`, current chat store and transport. Determine whether the app already uses ExyteChat, another UI library, or its own views. Read the resolved library declarations before using an API from the uploaded main snapshot.
2. Read [integration](references/integration.md) for package boundaries, exact APIs and attachment handling. Use [state and verification](references/state-and-verification.md) for ordering, optimistic updates, pagination and failure cases.
3. Define the app's source of truth, stable message identifiers, cursor contract, delivery states and draft upload policy before wiring the UI callback. Keep the UI adapter separate from transport and persistence.
4. Implement the smallest complete vertical slice: display, compose, send, server acknowledgment, error and retry. Add requested media types, replies, menus and older/newer history using the installed API.
5. Verify event ordering, duplicate delivery, failed uploads, offline behavior and scroll/keyboard accessibility. Use fixtures and a fake transport; report simulator/device coverage separately from inspected code.

## Boundaries and output

ExyteChat's send closure does not send data to a server. Adding Nuke does not replace ExyteChat's internal Kingfisher dependency. Do not insert API keys, new permissions, background location, analytics or external services without a feature requirement.

Finish with changes, backend assumptions, checks performed and any unavailable runtime checks. Treat fragments in references as source-reviewed examples, not precompiled applications. See [source map](../../docs/source-map.md) for archive identity and provenance.
