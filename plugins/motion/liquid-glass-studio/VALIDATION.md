# Validation record

What was checked for version 1.0.0, on 2026-11-05 (UTC), in a Linux container with Node 22.23.4, Python 3.13, Claude Code 2.1.318 and Playwright 1.63.0 with Chromium 153. Each result below was observed in this environment; nothing here was run on macOS, Windows, iOS or Android.

## Package checks

| Check | Command (from the plugin root) | Result |
| --- | --- | --- |
| Offline package validator | `python3 scripts/validate_plugin.py .` | Pass, 0 errors, 0 warnings: 11 skills, 5 agents, 3 commands, every relative link and anchor, prose gate, research JSONL |
| Claude Code validator | `claude plugin validate .` | Pass, nothing to report |
| Marketplace manifest | `claude plugin validate .claude-plugin/marketplace.json` (repository root) | Pass |
| Node tests | `node --test` | 111 of 111 pass: engine math and lifecycle, filter markup, tier rules, contrast math, probe decisions and a Chromium end-to-end probe, docs drift |
| Python tests | `python3 -m unittest discover -s tests -p 'test_*.py'` | 40 of 40 pass: validator and archive checks |

`tests/docs_drift.test.mjs` fails when a skill, reference or README names an engine export, option, handle member or filter primitive that the engine does not have, and when `liquid-glass.d.ts` disagrees with the JavaScript exports. A mutation run with seven planted mistakes caught all seven.

## Browser evidence (Chromium only)

**Render probe.** `node <plugin-root>/scripts/glass_probe.mjs` measured an SVG displacement inside `backdrop-filter` shifting the backdrop by 8 px out of an expected 8 px with zero residual, and a backdrop blur reducing edge energy to 0.04% of the control. It recommended the refract tier, matching the engine's own engine detection. Firefox and WebKit were reported as unavailable because their browser builds are not installed here.

**Lab.** At device pixel ratios 1 and 2, with no console errors and no external requests:

- Comparing strength 1 against strength 0 changed only bezel pixels: 5,990 at 1x and 21,602 at 2x, with zero interior pixels changed.
- Setting `data-glass-surfaces="solid"` on `<html>` switched all five surfaces to solid live, and removing it restored refraction.
- The frost override produced `blur(14px) saturate(1.5)` from the engine's zero-specificity stylesheet, with no inline style.
- A uniform neutral map drifted 4 px without the 1/510 bias correction and 0 px with it (measured during the first build; the correction was not changed afterward).

**Contrast.** The lab's worst-case estimate for the card's body text with default settings was 4.97:1 in refract, 6.20:1 in frost and 11.40:1 in solid, measured during the first build, before the review fixes. Re-measure with `scripts/glass_contrast.mjs --text-selector` before relying on these numbers.

## Plugin evals

Run with `claude plugin eval . --case <name> --trust-plugin --max-cost-usd 5`, three runs per arm, with and without the plugin loaded. LLM graders used the default judge.

| Case | With plugin | Without plugin | Notes |
| --- | --- | --- | --- |
| safari-flat-glass | 3 of 3 pass, score 1.00; the skill fired in every run | 1 of 3 pass, mean score 0.83 | Baseline runs promised Safari refraction once and gated refraction on `@supports` alone once |
| negative-photo-blur | 3 of 3 pass; no glass skill fired | 3 of 3 pass | Confirms the skills stay out of an unrelated image task |

Total cost for both cases was about 0.88 USD. The other four cases (web-nav-glass, swiftui-toolbar, review-contrast, library-choice) passed `claude plugin validate` but were not run. To run one:

```sh
claude plugin eval . --case web-nav-glass --trust-plugin --max-cost-usd 5
```

## Review

Five independent read-only reviews covered library claims, platform facts, engine and script code, skill usability, and provenance. A separate verifier re-checked each finding. All 42 findings were confirmed and fixed, and a final recheck found every finding resolved and the shared contracts holding across the package. Apple API availability was checked against Apple's documentation data, including `GlassButtonStyle.init(_:)` at 26.1 and `NSGlassEffectView.effectIsInteractive` at macOS 27.0. These reviews used the same model family that wrote the plugin, so they do not count as a different-model review.

## Not verified

- Rendering in Safari, Firefox and on mobile devices. Run the probe where those engines are installed.
- Swift, Kotlin and Dart samples were checked against published signatures only, not compiled.
- Installation through each host's plugin manager beyond the Claude Code validator.
- Facts in `references/research-snapshot.md` can change; each row carries its source and check date.
