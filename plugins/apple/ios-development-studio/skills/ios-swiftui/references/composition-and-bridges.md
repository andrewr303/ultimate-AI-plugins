# Composition, previews and UIKit boundaries

## Extract for a reason

Give a section its own view when it has meaningful responsibility, independent inputs, state, async work, reuse or useful isolated previews. Pass only consumed inputs. A large shared model can make a small component depend on unrelated changes.

A computed view helper can suit a small stateless fragment. A dedicated view gives a clearer boundary for observation, lifecycle or independent previewing. Line count alone is not a defect. Keep local style where it supports readability.

Keep `body` a UI description. Move business policy into the existing model/service boundary and call small actions from controls. Thin lifecycle orchestration is normal. Do not add a view model merely to rename a Boolean or remove an established one as cleanup.

Use native semantic controls for normal actions. Name icon actions meaningfully and hide decorative images from assistive output. Stable structure helps when the same content changes style; intentional conditional content is valid for different UI. Invisible overlays can still affect accessibility and hit testing, so handle both explicitly.

## UIKit bridging

Bridge when supported SwiftUI APIs lack the capability, the project has a suitable UIKit implementation, or the user requests integration. Prefer a small adapter. Do not make an incidental SDK upgrade a prerequisite.

Define the contract before implementation:

| Concern | Required decision |
| --- | --- |
| Ownership | Who creates/retains the view or controller? |
| Direction | Which inputs flow to UIKit and which callbacks return? |
| Identity | Which changes update the instance versus replace it? |
| Delegation | Who owns delegates, subscriptions and tokens? |
| Isolation | Which callbacks require UI isolation? |
| Cleanup | What stops when the bridge is dismantled? |
| Presentation | Who controls dismissal and navigation state? |

Create in the creation method; make updates idempotent and current. Do not allocate another controller, observer or delegate on every update. Ensure the coordinator uses current configuration rather than a stale wrapper copy.

Compare values before echoing an update through delegate callbacks to prevent loops. Do not defer every mutation to an arbitrary queue just to hide warnings; understand callback timing. Preserve delegate callbacks required by the underlying component.

On teardown, remove observers, invalidate timers and stop resources owned by the adapter. Do not cancel work shared by unrelated consumers. Check keyboard/focus changes, resizing, repeated presentation and rapid item replacement.

## Preview and test design

Preview meaningful states: loaded, loading, empty, failed, editing or disabled. Inject dependencies directly with small fixtures and disposable/in-memory persistence. Do not depend on real accounts or app-global initialization.

Previews demonstrate layout and wiring; keyboard, focus, accessibility and lifecycle need running-app checks. A bridge rendering once may still leak observers after repeated presentation. A screenshot does not prove bindings propagate.

Focused checks:

- Reconstruct a parent with the same child identity: intended editing state survives.
- Replace bridge input twice: callbacks refer to the latest item.
- Present/dismiss repeatedly: resources return to baseline.
- Cancel loading: no stale callback changes a dismissed screen.
- Exercise the oldest supported runtime when optional APIs have fallbacks.

## Failures

After extraction, inspect generic constraints, builder return types, actor isolation and initializer access before adding `AnyView` or weakening types. For preview crashes, inspect missing environment dependencies and fixture initialization before making required dependencies optional. Report source inspection as source inspection when Apple builds cannot run.

## Provenance

Original guidance informed by `Skills-main.zip`, `swiftui-view-refactor/SKILL.md` and `swiftui-ui-patterns/references/previews.md`; uploaded AvdLee `SwiftUI-Agent-Skill-main.zip`, `skills/swiftui-expert-skill/references/view-structure.md` and `modifier-patterns.md`. Architecture preferences became ownership-based choices. UIKit adapter checklist is original. See [source map](../../../docs/source-map.md) and [operating contract](../../ios-development/references/operating-contract.md).
