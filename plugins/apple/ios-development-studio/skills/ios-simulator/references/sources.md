# Simulator provenance

Original workflow synthesized from `ios-simulator-skill-main.zip`:

- `ios-simulator-skill/skills/ios-simulator-skill/SKILL.md`.
- Repository `references/{simctl_quick,idb_quick,test_patterns,troubleshooting,accessibility_checklist}.md`.
- Source-only review of `scripts/{navigator,screen_mapper,simctl_delete,simctl_erase,app_state_capture,appearance,localization_audit}.py` and `scripts/common/{device_utils,cache_utils,hang_sessions}.py`.

The upstream MIT notice belongs to Conor Luddy and is retained in the plugin’s third-party notices. No upstream helper is bundled or executed by this workflow. This avoids silently inheriting their home-directory caches, destructive batch behavior or platform/version assertions.

The uploaded accessibility auditor performs heuristics; its result is not evidence of complete WCAG or platform accessibility coverage. Consult installed Xcode/simctl/controller help and current Apple Simulator/testing documentation. [Source map](../../../docs/source-map.md).
