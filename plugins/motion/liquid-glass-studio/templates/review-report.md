# Glass review report: {product or feature}

Fill this report while running the `glass-review` skill. Replace each `{placeholder}`. Keep evidence files (screenshots, probe and contrast JSON, traces) in one folder next to the report, outside tracked paths unless the team asked for them in the repository. Use synthetic or masked data in any image that leaves the team.

## 1. Summary

- **Result:** {N Blocker, N Major, N Minor, N Note}, or "no findings in the checked scope"
- **Most important finding:** {one sentence, or none}
- **Request type:** {assessment only, or assessment and fixes}
- **Reviewer and date:** {name, YYYY-MM-DD, timezone}

## 2. Scope

- **Repository, branch and commit:** {repo}, {branch}, {commit}
- **Surfaces reviewed:** {IDs from the glass spec, or a list}
- **Out of scope:** {surfaces, platforms or flows not reviewed, and why}
- **Spec reviewed against:** {path to glass-spec.md, or none}

## 3. Environment

| Item | Value |
| --- | --- |
| App start command and URL | {command}, {url} |
| Browsers and versions | {Chromium x, Firefox x, WebKit x} |
| Devices and simulators | {device, OS, DPR, refresh rate} |
| Assistive technology | {VoiceOver version, NVDA version, none} |
| Plugin tools used | {glass_probe.mjs, glass_contrast.mjs, engine tests, docs drift test} |

## 4. Evidence states

Every check ends in exactly one state. "Not checked" names the reason (no access, out of time, tool missing) and is never counted as a pass.

| Area | Check | State | Evidence |
| --- | --- | --- | --- |
| Inventory | Surfaces and layers listed | {checked, not checked, not applicable} | {section 2 above} |
| Static scan | Detection patterns GR1 to GR13 run | | {search commands used} |
| Engines | Cross-engine probe | | {probe/probe.json} |
| Engines | Screenshots per tier | | {list in section 6} |
| Contrast | Worst-case text contrast | | {contrast JSON files} |
| Contrast | Boundary and focus ring contrast | | |
| Preferences | Reduced transparency (query and in-product toggle) | | |
| Preferences | More contrast | | |
| Preferences | Forced colors | | |
| Preferences | Reduced motion, at load and mid-animation | | |
| Keyboard | Reach, operate, visible unclipped ring | | |
| Screen reader | Roles, names, silent decorative layers | | |
| Motion | Press, reverse, reopen at normal speed | | |
| Performance | Trace and frame pacing (only when jank is visible or claimed) | | |
| Native | Newest SDK and lowest deployment target builds | | |
| Native | Reduce Transparency, Increase Contrast, Reduce Motion | | |
| Docs | Drift check (`node --test <plugin-root>/tests/docs_drift.test.mjs` for plugin docs, or claims compared with code) | | |

## 5. Findings

Ordered by severity. Evidence type is one of: observed (seen in a running build), measured (script or trace output), static (read in code), inferred (reasoned risk with no observed effect).

| ID | Pattern | Severity | Location | Repro steps | Expected | Observed | Evidence (type and file) | Smallest fix and owning skill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | {GR6 focus removed} | {Blocker} | {src/Toolbar.css:42} | {1. open page 2. press Tab until the toolbar} | {visible ring with 3:1 contrast} | {no ring} | {observed, toolbar-chromium-focus.png} | {restore a two-tone ring; glass-accessibility} |
| F2 | | | | | | | | |

Severity scale: **Blocker** crashes, fails to build, hides content, traps focus or leaves text unreadable in a tested state. **Major** fails a stated requirement on a common path or breaks a supported engine. **Minor** is a reproducible defect with a workable path, or a measurable cost inside budget. **Note** is polish or an inferred risk.

**Candidates dismissed as false positives:** {pattern, location, reason}

## 6. Screenshots

One line per file: `{surface}-{engine}-{state}.png`, what it shows, and whether it is a capture of the running app or a recreation.

| File | Surface | Engine | Tier or preference | Shows |
| --- | --- | --- | --- | --- |
| {s1-chromium-refract-light.png} | S1 | Chromium {version} | refract, light | {refraction at the rim, label legible} |

## 7. Measurements

| Surface and text | State | Engine and DPR | Minimum ratio | Required | Pass |
| --- | --- | --- | --- | --- | --- |
| {S1 tab label} | {scroll 0, dark} | {Chromium, 2} | {4.81} | {4.5} | {yes} |

Probe results per engine (from `node <plugin-root>/scripts/glass_probe.mjs --json`, run from the project directory):

| Engine | Refraction renders | Backdrop blur renders | Matches the tier plan |
| --- | --- | --- | --- |
| chromium | | | |
| firefox | | | |
| webkit | | | |

## 8. Limitations

- {Engines, devices or settings not checked, and why}
- The contrast method judges the minimum over rendered pixels. It is an engineering inference from WCAG 1.4.3 and 1.4.11, not a conformance test, and one run covers one scroll position and animation moment.
- {Headless rendering differences, for example blur under-rendered without a GPU, if observed}
- {Anything inferred rather than observed}

## 9. Next steps

| Action | Owner | Blocks release |
| --- | --- | --- |
| {fix F1, then rerun the keyboard check} | {name} | {yes} |
