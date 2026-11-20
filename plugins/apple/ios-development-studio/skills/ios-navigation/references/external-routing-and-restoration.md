# Deep links, external intents and restoration

## Parse into an intent

Treat inbound URLs, notification payloads, activities and restored state as untrusted data. Parse them into a small typed intent before mutating visible navigation. Inspect the actual entrypoints and entitlement/configuration setup; adding a URL scheme does not alone establish universal-link ownership or delivery.

Validate scheme, host, expected path shape, allowed query parameters and value lengths. Decode using platform URL components rather than string splitting. Reject malformed identifiers, conflicting repeated parameters and unsupported route versions according to a documented policy. Do not reinterpret arbitrary URL contents as code, file paths or command arguments.

Separate parsing from resolution:

1. Parse and validate the external representation.
2. Resolve required app context, such as account or workspace.
3. Check authentication and destination authorization through the normal service/domain boundary.
4. Fetch or resolve the identified content.
5. Choose a valid navigation transition.
6. Acknowledge or consume the intent to prevent duplicate handling.

Opening a screen must not bypass server authorization. A guessed ID or a restored route is not evidence of access. Avoid logging full tokens, private query values or payloads; report a redacted route category and outcome instead.

## Cold, warm and suspended entry

A cold-start link can arrive before dependencies, authentication or scene roots exist. Keep a bounded pending intent with explicit ownership rather than forcing navigation into an uninitialized hierarchy. A warm app may already show the destination or an unsaved editor. Define whether to reuse, replace, queue or ask about losing unsaved work based on the product's interaction contract.

When authentication is required, retain only the necessary route information, then revalidate after sign-in. Do not persist one-time secrets or an unlimited queue of private payloads. If the user switches accounts during sign-in, resolve access in the resulting account rather than assuming the original one.

Handle duplicate callbacks idempotently when practical. Receiving a universal link and a related lifecycle callback must not push two copies or execute a side effect twice. Route intents should describe navigation; privileged/destructive actions should retain their existing user-visible authorization flow.

## Restoration

Restored routes may refer to removed records, changed schemas, unavailable features or another account. Version the stored representation when needed, validate decoded data and use a safe fallback. Keep content reload separate from path decoding. A graceful root or not-found screen is preferable to restoring an invalid stack.

Store only appropriate lightweight state. Do not serialize live controllers, authentication credentials or full production records into route storage. Account-bound restoration should be scoped by account identity and cleared or revalidated on context changes.

Make restoration deterministic enough to test: the same serialized intent plus mocked repository responses should produce the same destination plan. Tests need not instantiate every view to verify parsing and policy.

## Test matrix

| Input/context | Expected outcome |
| --- | --- |
| Valid link while signed in | Authorized destination appears once |
| Same link during cold start | Deferred until dependencies exist, then consumed once |
| Link while signed out | Sign-in flow, then revalidation and intended destination |
| Unauthorized/missing record | Safe error/root flow without private cached content |
| Unknown host or malformed ID | Rejected without path mutation |
| Duplicate delivery | No duplicate push or repeated side effect |
| Editor has unsaved changes | Product-defined preservation/discard decision |
| Old restoration version | Supported migration or safe fallback |

Test parsing and resolution with deterministic fixtures, then use an actual simulator/device for platform delivery when available. A unit test for URL parsing does not establish entitlement correctness, associated-domain verification, or OS delivery.

## Provenance

Original guidance informed by `Skills-main.zip`, `swiftui-ui-patterns/references/deeplinks.md`, `navigationstack.md` and `app-wiring.md`; source examples are treated as architectural ideas, not a complete security or platform-delivery implementation. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
