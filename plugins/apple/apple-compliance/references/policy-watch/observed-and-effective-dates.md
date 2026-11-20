# Observed dates, effective dates and future requirements

Apply the [operating contract](../operating-contract.md). Use the app’s actual facts, selected lane and current authoritative sources.

## Keep the dates separate

Record when a source was observed, when an announcement was published, when a requirement takes effect and the date of the intended action. These can differ. A future SDK/device/asset requirement must not become a present universal default, and a current guide may still describe a transition period or conditional eligibility. Preserve the source's stated timezone/region; if it is absent, do not invent precision.

Also separate technical version dimensions. A required upload SDK/build-host toolchain, the app's deployment minimum, supported device behavior and a third-party library's compiler floor are different constraints. Do not raise an app's minimum supported OS merely because an announced upload requirement names a newer SDK. Verify the selected Xcode/toolchain and actual artifact against the applicable requirement.

## Build an applicability timeline

For a material rule, retain: selected platform/channel/storefronts; current observed rule; announced change and exact effective date when supplied; transition/exception conditions; planned upload/submission/release date; app/tooling changes needed; evidence owner; and status for the requested stage. Avoid a hardcoded global device/fee/SDK table in the plugin. Use the live selected source and app facts at execution time.

A publication date, HTTP Last-Modified header or repository commit date is not automatically the policy effective date. A screenshot specification and a review guideline can have different scope and timing. When the source is ambiguous, record unknown/needs evidence and continue unaffected technical preparation rather than guessing a favorable deadline.

## Decision sequence

1. Resolve the intended external action and time, not merely the app version name. Upload, submission and release may be subject to different workflow conditions.
2. Read the authoritative requirement and any linked announcement/transition material. Preserve conditions and the exact date wording in a concise source note.
3. Compare today's/current action requirements with announced future requirements. Keep separate current readiness and future work items.
4. Inspect the actual selected SDK/build configuration, artifact and store assets. A developer machine's installed newest Xcode is not proof the archive used it.
5. Plan the smallest compatible change and relevant native/asset tests when the upcoming rule affects this app. Preserve deployment targets and existing support policy unless the task changes them.
6. Refresh material evidence immediately before the authorized external stage when timing, source or account state changed; update the packet without carrying stale satisfied assertions forward.

## Failure cases

| Inference | Missing distinction |
| --- | --- |
| Announced requirement already blocks every app | Effective date, scope and transition terms |
| New SDK requirement means drop old OS users | Build SDK versus deployment availability |
| Page observed today means rule starts today | Observation versus publication/effective date |
| New screenshots in one specification apply globally | Platform/device/storefront and submission timing |
| Tool main branch says latest supported | Installed released version and actual artifact configuration |
| No date visible means no requirement | Current applicability still needs a primary-source check |

## Evidence and handoff

Report current-stage status and future action items separately, with sources, dates and owner. A future item is not a completed migration, and an unknown deadline must not be silently treated as a pass. Do not make legal, fee or eligibility claims beyond the reviewed source and owner facts. The readiness helper records asserted policy_scope evidence; it does not fetch sources or decide date applicability for the app.

## Sources and checked scope

- [src_policy_submitting](https://developer.apple.com/app-store/submitting/)
- [src_delivery_screenshot_specs](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/)
- [src_policy_review_guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [src_policy_sdk_requirements](https://developer.apple.com/support/third-party-SDK-requirements/)

The [source index](../../research/sources/sources.jsonl) records identity and observation scope. These are original workflow notes, not a full policy mirror or a legal/approval certification. Refresh material applicability before the requested external action.
