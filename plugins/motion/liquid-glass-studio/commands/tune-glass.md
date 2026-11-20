---
description: Open the bundled Glass Lab to tune liquid glass style parameters live, compare variants, capture tier screenshots and export settings into the project.
argument-hint: "[surface to tune, or a preset query such as profile=lip&thickness=30]"
---

# /tune-glass

Goal: $ARGUMENTS

Tune glass in the liquid-glass-studio Glass Lab, a local page with no network requests that runs the same engine a project would ship.

## 1. Prepare

1. Invoke `liquid-glass-studio:glass-lab` ([SKILL.md](../skills/glass-lab/SKILL.md)) and follow its "Start here".
2. Check what the project renders glass with. The lab tunes the bundled engine; for another library, use it to explore the look, then map values with the name table in the optics reference.
3. Note the target surface's real size, corner radius and the content it floats over. If the goal above names a surface, read its component and tokens first.
4. If the goal above contains query keys (`profile`, `thickness`, `ior`, `tier` and the rest listed in the skill), use them as the starting preset.

## 2. Run the lab

The lab lives at `<plugin-root>/examples/glass-lab/`. `<plugin-root>` below is this plugin's install folder: two directories above the base directory a skill reports when it loads (Claude Code prints "Base directory for this skill"). If no skill reported one, find the folder that holds `scripts/glass_probe.mjs` with a filesystem search. Browsers block module imports from `file://`, so serve it:

```sh
cd <plugin-root>/examples/glass-lab
python3 -m http.server <free port> --bind 127.0.0.1
```

- Start the server yourself on a free port, capture its PID, and stop only that PID when done.
- Open `http://127.0.0.1:<port>/?<preset>` in Chromium for refraction. WebKit and Firefox show the frost tier by design; `?tier=frost` and `?tier=solid` force the lower tiers.
- Do not edit the lab to tune a product. Settings belong in the project.

## 3. Tune, compare, export

- Follow the skill's tuning loop: profile, then bezel width and thickness, then index of refraction, then strength; watch the fold guard readout; then tint, blur and saturation; then the rim.
- Compare variants at the same viewport, DPR and backdrop offset, changing one parameter at a time. Capture each finalist at default, `?tier=frost` and `?tier=solid`. Keep screenshots in a scratch or gitignored folder.
- Export by turning the final URL into engine options and CSS tokens, rescaled for the real component, with the lab URL in a comment.
- The lab's contrast note is an estimate. Re-measure the text elements on the product page, from the user's project directory:

```sh
node <plugin-root>/scripts/glass_contrast.mjs --url <product url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto --json
```

## 4. Report

The chosen lab URL, the exported options and tokens with the files they went into, screenshot paths per tier, checks run with results, and anything not measured on the real page.
