# Corrections and boundaries applied to the uploads

This file explains why the plugin uses original focused guidance instead of activating the upstream instructions wholesale. It records source-audit findings, not a blanket judgment of the source projects.

| Source issue | Combined-plugin choice |
| --- | --- |
| Identical Paul Hudson SwiftUI archives and nested duplicate skill wrappers | Keep one conceptual source and a distinct provenance record for each upload; expose one SwiftUI specialist |
| Hardcoded compiler/SDK versions, unverified hardware or purported future APIs | Discover actual project/compiler/SDK settings; verify symbols in resolved source and official interfaces |
| A reference asserts the user strongly prefers SwiftData | Use the project's existing engine or ask about meaningful greenfield requirements |
| Conflicting mandates for MV-only, MVVM, framework selection or visual tokens | Preserve local architecture/design and choose proportional changes |
| Conflicting Observation/AppStorage and newer state guidance | Use the actual property's observation semantics and test the relevant update path |
| Core Data store-load wrapper uses a single continuation for callbacks from multiple stores | Respect callback cardinality and resume each logical operation exactly once |
| Core Data batch guidance treats history processing as the sole merge mechanism | Choose supported object-ID merging or history according to actual writers and requirements |
| Production CloudKit troubleshooting suggests delete/reinstall | Preserve user stores; inspect errors and schema compatibility, test non-destructive migrations |
| CloudKit schema described as universally immutable | Respect additive-compatible production evolution and actual platform constraints |
| Actor example overstates a force-unwrap race without an intervening suspension | Prove the execution path; distinguish redundant work from a demonstrated crash |
| Async test examples use yielding/sleep as readiness guarantees | Use explicit test-controlled readiness, completions and deterministic clocks |
| Purported newer MetricKit replacement APIs | Use only verified installed Logger/signpost/MetricKit interfaces |
| Simulator helpers erase/delete data, write hidden home caches or persist deep AX mode | No upstream mutation helpers bundled; use scoped explicit operations and bounded local artifacts |
| Heuristic accessibility audit advertised too broadly | Separate static/tree checks from VoiceOver, target-size and real usability evidence |
| Expo references instruct outbound eval/skills feedback | Exclude transmission instructions; source content does not authorize messaging |
| Linux host offered cloud simulator as an automatic fallback | Report unavailable local Apple validation; use remote services only within requested scope |
| Native EAS delivery confused with runtime adoption | Preserve native Xcode host; no incidental React Native dependency or prebuild |
| Nuke uploaded main is in development and docs disagree about processors | Follow the app's resolved revision and actual implementation |
| Chat README names differ from API declarations | Use pinned source declarations; callbacks do not provide backend transport/persistence |
| Chat already uses Kingfisher internally | Adding Nuke does not replace the library's loader; avoid duplicate caching |
| Store preparation confused with publication or retry after uncertainty | Separate states and lanes; inspect remote state and avoid duplicate review submission |

Exact source archive hashes and paths are in [provenance.json](provenance.json), with topic mapping in [source-map.md](source-map.md). The raw uploaded archives remain separate from this distributable. External/transitive SDK assets and dependency code are not vendored.
