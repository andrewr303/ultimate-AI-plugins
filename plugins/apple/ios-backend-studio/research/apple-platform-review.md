# Apple system integration: source review and reference plan

This pass inspected 35 current official Apple DocC sources plus the public Sign in with Apple OIDC discovery and JWKS surfaces. Raw snapshots, extracted reading copies, exact URLs, content hashes, retrieval timestamps and source-specific availability metadata remain under this research directory. The plugin should include original summaries and links, not wholesale copyrighted Apple documentation or sample credentials.

This is primary-source review, not an automated research gate verdict or runtime test. All these sources have Apple as the underlying author; separate files or service surfaces must not be counted as independent organizations. Parent synthesis can combine these observations with independently reviewed Node/OpenAPI/repository evidence.

## Deliverable inventory

- [source index](../references/source-index.md): 35 documentation sources and two auxiliary public auth surfaces.
- `sources.jsonl`: normalized source records ready for the parent evidence registry.
- `sources.json`: full DocC metadata, reviewed-content scope and snapshot hashes.
- `auxiliary-auth-sources.json`: actual OIDC/JWKS metadata source records.
- `failed-fetches.json`: initially guessed 404 paths and their replacements discovered from official framework references.
- `cards/`: 16 substantial original reference-card outlines, approximately 56 KB total.
- `raw/`, `read/`, `prose/`: task-local evidence and reading artifacts. Do not ship these mirrors wholesale.

The inventory counts were checked by executing local standard-library scripts over the fetched files. No Apple sample, upstream executable, project code, installer, live APNs request, model prompt or provider credential was executed or used in this pass.

## Original reference-card plan

| Card | Primary source IDs | Backend integration choice |
| --- | --- | --- |
| System/backend boundaries (research outline; final workflow cards are indexed in the reference library) | 006, 011, 021, 033 | One durable Node domain with surface-specific Apple execution adapters |
| Widget read projections (research outline; final workflow cards are indexed in the reference library) | 001–003 | Small cached account-scoped projections, timelines and explicit stale state |
| Interactive widget reconciliation (research outline; final workflow cards are indexed in the reference library) | 004, 007, 010 | Typed intent action, backend acknowledgment and optimistic-state correction |
| Widget routing and Mac (research outline; final workflow cards are indexed in the reference library) | 004–006, 025–026 | Validated deep links and correct handling of remote iPhone-widget execution |
| App Intent domain adapters (research outline; final workflow cards are indexed in the reference library) | 007–010 | Stable entities and one authorized command service across UI and Siri |
| Siri content/schema exposure (research outline; final workflow cards are indexed in the reference library) | 009, 031–032 | Optional SDK-gated schemas with permission-aware entity/context disclosure |
| Live Activity state/lifecycle (research outline; final workflow cards are indexed in the reference library) | 011, 013–014 | Separate static/dynamic state, authorization, stale and final states |
| ActivityKit APNs protocol (research outline; final workflow cards are indexed in the reference library) | 012, 015–016 | Distinct token roles and wire-state contract, not a persistent client socket |
| Node APNs provider (research outline; final workflow cards are indexed in the reference library) | 015–017 | Server-held keys, scoped reusable HTTP/2 pools and classified receipts |
| Device-token lifecycle (research outline; final workflow cards are indexed in the reference library) | 017–020 | Opaque registrations scoped to account, app, environment and lifecycle |
| Background reconciliation (research outline; final workflow cards are indexed in the reference library) | 019, 021–022 | Bounded resumable work, explicit expiration and durable server state |
| Background file transfer (research outline; final workflow cards are indexed in the reference library) | 023–025 | Stable sessions, file ownership, delegate completion and delayed auth handling |
| App Group projections (research outline; final workflow cards are indexed in the reference library) | 025–026, 030 | Minimal cross-process shared data and verified actual entitlements |
| CloudKit versus Node (research outline; final workflow cards are indexed in the reference library) | 027–028, 033 | Explicit authoritative data plane and account/conflict ownership |
| Extension credential scope (research outline; final workflow cards are indexed in the reference library) | 010, 029–030, 034 | Narrow client credentials and correct local versus server authentication |
| Sign in with Apple server (research outline; final workflow cards are indexed in the reference library) | 034–037 | Verify provider identity, then manage an application-owned session |

The table uses the numeric suffixes of the registered Apple source IDs. Final cards contain the full source IDs and exact links.

## Material observations for implementation

1. **WidgetKit is a snapshot/timeline system.** The extension is not kept continually active. Reload budgets and scheduling vary; `after` is not a reliable backend polling interval. A Node service should tolerate synchronized clients and expose a compact stale-aware projection.
2. **Widget interactions have two kinds of truth.** A toggle may present optimistic state before its intent finishes. Persist/acknowledge the outcome that the timeline reads and show an error/rollback state when synchronization fails. Parameter and process ownership must be explicit.
3. **Live Activities cannot independently network from their display sandbox.** Use app ActivityKit updates or eligible server APNs. Display dismissal does not cancel the underlying backend operation.
4. **APNs token roles differ.** Ordinary device notification tokens, activity update tokens, push-to-start tokens and channel IDs are not interchangeable. Observe rotation and invalidate the proper association. Keep provider keys on the server and production logs free of raw tokens.
5. **Best effort is a real product constraint.** APNs may coalesce/reorder notifications, background pushes are not guaranteed, and background scheduling depends on system conditions. App launch/foreground reconciliation must heal missed work.
6. **Account identity spans several boundaries.** A native Apple identity, an app session, an iCloud account, Keychain access, local device authentication and domain resource authorization are distinct. Do not use an unlocked device or a delivery token as a backend permission grant.
7. **App Group path behavior differs on Mac.** The FileManager article says macOS can return a URL-shaped result for an invalid group; verify actual usable access. iOS returns no URL for an invalid group. Do not construct private filesystem paths.
8. **CloudKit does not remove app sync responsibilities.** CKSyncEngine needs persisted state and delegate-provided changes, uses an indeterminate schedule and leaves application-specific conflicts/account data handling to the app. Its public-database exclusion is explicit. Production schema changes are additive-compatible; deleting stores is not the routine repair.
9. **Newer Siri/Apple Intelligence integration is optional and SDK-specific.** Stable App Intent adapters can work independently. Do not force every existing intent into the newest schema or break saved shortcuts as a side effect.

## Availability handling

Availability was copied as source metadata into the source registry, not turned into plugin-wide minimums. Examples include the AppIntent/AppEntity family metadata listing iOS 16/macOS 13, ActivityAttributes/ActivityAuthorizationInfo listing iOS 16.1, and CKSyncEngine listing iOS 17/macOS 14. Article or sample metadata is not proof that every symbol mentioned by that article is available at the same minimum. Build settings, generated interfaces and runtime capabilities must be inspected in the target project.

Several current Apple articles mention newer devices, controls, widget push APIs, scheduling APIs or schema features. These were not adopted as universal defaults. Cards require verification of each selected API and retain a useful baseline path.

## Unresolved

- No Xcode build, simulator/device run, capability signing, APNs provider send, system scheduling, Siri conversation, keychain lock-state test or production sync operation was performed.
- Device/system timing, budgets and capability behavior cannot be established by Node/fixture tests. Numeric examples in source articles are not an SLA.
- Apple-specific facts here have primary and sometimes multiple same-author surfaces, but not independent organization corroboration under the strict research ledger rule. They should remain source observations unless combined with appropriate independent evidence.
- Apple’s `Verifying a user` prose says “JWS E256”, while actual official OIDC discovery and JWKS advertise RS256 identity-token verification. The current public protocol metadata is the safer integration contract; verify it again at implementation time. Do not apply the APNs ES256 provider-signing algorithm to every Apple token role.
- AppIntents’ `openAppWhenRun` appears in a deprecated section of the current overview, while older target code may still rely on it. A blanket rewrite is not supported without checking the actual SDK/target.
- The background-download article’s prose ordering around completion/delegate callbacks is not used as a new implementation recipe. Use the actual delegate contracts: preserve temporary files before callback return and finish the stored background-event handler after required events are handled.

## Refuted

The following design assumptions are rejected by the reviewed primary sources: a widget remains continually running; Live Activity UI can directly network; an APNs acceptance proves delivery/display; a background push is a durable event log; a macOS App Group URL alone proves valid access; CKSyncEngine creates one atomic transaction with a separate Node database; an Apple JWT role implies the same algorithm/key/claims as another role.

## Suggested skill boundaries

The parent can use six focused specialists: Apple push provider/device lifecycle; widgets and shared projections; App Intents/Siri adapters; Live Activities; background/offline reconciliation; and identity/session/extension credentials. CloudKit selection and App Group coordination can be focused reference branches rather than mandatory dependencies. Keep Xcode/Mac tooling and cross-platform contract generation in their own parent-owned specialists.
