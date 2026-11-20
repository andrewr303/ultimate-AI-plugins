# Separate notification consent, background work and review behavior

## Identify the exact notification and work lane

Separate visible alerts/sounds/badges, remote registration, silent notifications, a notification action, background transfer and scheduled processing. Their APIs, permissions and lifecycle guarantees differ. A generic “notifications enabled” flag cannot explain which capability the release actually uses or whether the user granted the relevant permission.

The reviewed notification article describes requesting visible-notification authorization in a useful feature context and explains that repeated authorization calls do not necessarily prompt again. Provisional delivery has distinct quiet behavior. The reviewed push guideline also says notifications must not be required for the app to function, should not contain sensitive/confidential information, and has explicit opt-in/opt-out conditions for promotional/direct-marketing use.

## Inputs and applicability

Inventory notification categories/actions, data payload classes, provider/account binding, user preferences, foreground presentation and any background processing. Confirm that the app's actual purpose supports the background modes it declares; background execution is not a license for indefinite work. A push token is a delivery address, not proof of account identity.

Determine which permissions and product consent are relevant. A system notification grant alone does not establish consent for every promotional message or unrelated use of personal data. Keep denied/revoked settings and account changes visible in the design. Do not place credentials or private health/financial details into a payload or shared review log.

## Workflow

1. Map each notification or job to the user task and current review/platform rule.
2. Request the actual supported authorization in context and provide an appropriate non-notification route to core functionality.
3. Bind registration/preferences to the intended authorized account and handle token replacement, logout and account switching.
4. Validate action/URL inputs and recheck access when opening content or executing a mutation.
5. Keep background handlers bounded, with explicit cancellation/expiration and exactly-once completion signaling for the relevant API.
6. Test state reconciliation when delivery is delayed, duplicated, coalesced or absent rather than promising an exact delivery/scheduling clock.

The device may suspend or terminate work, defer delivery, restrict refresh or make protected data unavailable while locked. The UI and server must remain coherent under those conditions. HealthKit is one example where locked/protected data and deliberately opaque permission results require careful interpretation; do not turn “no data” into a fabricated authorization fact.

## Test scenarios

Exercise initial permission, denied/restricted state, provisional delivery where supported, later revocation, signed-out account, duplicate payload, stale/deleted entity and a background expiration during work. For marketing notifications, test the actual explicit preference and in-app opt-out path. Verify that disabling notifications does not unnecessarily remove access to the app's unrelated core tasks.

A simulated notification can prove handler behavior but not production APNs provider delivery. A debugger-triggered background operation does not establish the OS will run it on a schedule. Record separate client, server/provider and device evidence. Use an actual authorized environment for external delivery tests; do not notify real users as a generic validation step.

## Outcome

A proven sensitive payload exposure, invalid account binding, unrelated background use or missing required consent/control is a blocker. Unverified provider or device behavior stays unknown. Not applicable identifies the absent capability and relevant rule scope. Satisfied evidence names the exact build, preference/permission states and cases tested. Keep that result distinct from App Review acceptance and avoid shipping a blanket compliance assertion in product UI.

## Source and applicability record

Observed **2026-10-26**. These are scoped observations of Apple primary documentation, not independent legal clearance or a promise of acceptance. Reopen the material source before acting and record the selected platform, storefront, distribution lane, agreement and effective date. Future announcements are not current defaults.

- `src_policy_review_guidelines` — [App Review Guidelines - Apple Developer](https://developer.apple.com/app-store/review/guidelines/)
- `src_policy_notification_permission` — [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- `src_policy_health_privacy` — [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- `src_policy_complete_review` — [Provide information for a complete review - Before submitting for review - App Review - Help - Apple Developer](https://developer.apple.com/help/app-review/before-submitting-for-review/complete-review)

Apply the [operating contract](../operating-contract.md). Source identities and retrieval records are in [the source ledger](../../research/sources/sources.jsonl).
