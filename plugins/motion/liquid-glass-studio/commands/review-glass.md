---
description: Run the evidence-based glass-review workflow on a path, URL, branch or PR and report findings with severity, repro and evidence, without editing the product.
argument-hint: "<path, URL, branch or PR> [engines, e.g. chromium,firefox,webkit] [fix]"
---

# /review-glass

Target: $ARGUMENTS

Review the liquid glass style surfaces in the target above with the liquid-glass-studio plugin.

## 1. Bound the review

1. If the target is empty, review the glass surfaces changed in the current working tree diff; if there is no diff, ask which path, URL or PR to review and stop until answered.
2. This is an assessment. It authorizes reading code and running the app, not editing product files. Apply fixes only if the arguments include `fix` or the user asks; then rerun each failing check after its fix.
3. Note the engines and platforms to cover. Default: Chromium, Firefox and WebKit for web; newest SDK and lowest deployment target for native.

## 2. Run the workflow

Invoke `liquid-glass-studio:glass-review` ([SKILL.md](../skills/glass-review/SKILL.md)) and follow its phases in order: bound the scope, inventory surfaces, static scan with detection patterns GR1 to GR13 and their false-positive list, runtime evidence, triage, report.

- For a URL, use it read-only. For a path or branch, start the app with its documented dev command on a free port and stop it by the PID you captured. Never drive production or someone else's running instance.
- Runtime evidence comes from the plugin's scripts, run from the user's project directory by path. `<plugin-root>` below is this plugin's install folder: two directories above the base directory a skill reports when it loads (Claude Code prints "Base directory for this skill"). If no skill reported one, find the folder that holds `scripts/glass_probe.mjs` with a filesystem search. Output paths resolve against the current directory.

```sh
node <plugin-root>/scripts/glass_probe.mjs --browsers chromium,firefox,webkit --out <scratch>/probe --json
node <plugin-root>/scripts/glass_contrast.mjs --url <url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto --screenshot <scratch>/<name>.png --json
```

- Measure text elements with `--text-selector` (for example `--selector 'nav.site' --text-selector 'nav.site a, nav.site span'`), never a whole container.

- Capture screenshots per surface for refract, frost and solid; light and dark; emulated `prefers-contrast: more`, `forced-colors: active` and reduced motion; and the in-product solid toggle (`data-glass-surfaces="solid"` on `<html>`).
- Keep screenshots, probe and contrast JSON in a scratch or gitignored folder, never a tracked path. Use synthetic or masked data.
- Accessibility and performance passes can run in parallel with the read-only briefs [glass-accessibility-reviewer](../agents/glass-accessibility-reviewer.md) and [glass-performance-investigator](../agents/glass-performance-investigator.md) ([how to delegate](../docs/agent-briefs.md)). Pass each the absolute plugin root, and integrate their findings yourself.

## 3. Report

Fill a scratch copy of [review-report.md](../templates/review-report.md).

- Findings first, ordered Blocker, Major, Minor, Note. Each has pattern ID, location, repro, expected versus observed, evidence file and type (observed, measured, static, inferred), and the smallest fix with the owning skill.
- Every check is marked checked, not checked or not applicable. A missing engine, device or assistive technology is "not checked", never a pass.
- List artifact paths and limitations. "No findings in the checked scope" is a valid result, not a certification.
- Do not post PR comments, resolve review threads or message anyone unless the user asked.
