---
description: Route a liquid glass style UI request through the liquid-glass-studio router skill and carry it through implementation and verification.
argument-hint: "<what to design, build, tune, port or fix, and where (file, component or screen)>"
---

# /glass

Request: $ARGUMENTS

Handle this request with the liquid-glass-studio plugin. "Liquid Glass" is Apple's name for its system material; this plugin is unaffiliated with Apple and builds liquid glass style surfaces that respect the platform, user settings and the product's brand.

## 1. Route

1. If the request above is empty, inspect the project for existing glass (`rg -n "backdrop-filter|glassEffect|UIGlassEffect|NSGlassEffectView" .` outside `node_modules` and build output) and ask one question: which surface and which outcome. Stop until answered.
2. Invoke the router skill `liquid-glass-studio:liquid-glass-studio` ([SKILL.md](../skills/liquid-glass-studio/SKILL.md)) and follow its "Start here": read the project's agent instructions, inspect the stack, installed versions and existing design tokens, and classify the request as design, implement, tune, port, debug or review.
3. Open only the specialist skills the router table selects, each through its own name, for example `liquid-glass-studio:glass-web`, `liquid-glass-studio:glass-design` or `liquid-glass-studio:glass-accessibility`. Read each SKILL.md before acting on it.
4. If the request is a review only, switch to `/review-glass` behavior: assess and report, do not edit.

## 2. Carry it through

- An implementation, tune, port or fix request ends with working code in the project and real checks, not with a plan or a spec.
- Build tiers in order: solid, then frost, then refraction. Each later tier falls back to the one below it. Refraction through `backdrop-filter: url()` is a Chromium-only enhancement gated by engine, never by `@supports` alone.
- Keep the change to the files the request needs. Do not add or upgrade dependencies, stage, commit, push, publish or deploy unless the user asked for that.
- For a larger job you may delegate bounded parts with the briefs described in [docs/agent-briefs.md](../docs/agent-briefs.md): one writer per file, reviewers stay read-only, and pass each worker the absolute plugin root.

## 3. Verify

`<plugin-root>` below is this plugin's install folder: two directories above the base directory a skill reports when it loads (Claude Code prints "Base directory for this skill"). If no skill reported one, find the folder that holds `scripts/glass_probe.mjs` with a filesystem search. Run the scripts from the user's project directory by path:

```sh
node --test <plugin-root>/tests/engine.test.mjs        # when the bundled engine is used or copied
node <plugin-root>/scripts/glass_probe.mjs --browsers chromium,firefox,webkit --json   # tier each engine actually renders
node <plugin-root>/scripts/glass_contrast.mjs --url <dev url> --selector "<glass surface>" --text-selector "<text elements on it>" --require auto --json
```

- Measure the text elements with `--text-selector`, never only the container: a container run compares one color with every pixel of the box, including buttons and icons with their own fills.

- Run the project's own lint, typecheck and tests.
- Start only your own dev server, on a free port, and stop it by the PID you captured.
- Take real-browser screenshots of each tier the user can reach: Chromium (refract), WebKit and Gecko (frost), and the solid tier under emulated `prefers-contrast: more` and `forced-colors: active`. Native work: newest SDK and lowest deployment target, with Reduce Transparency and Increase Contrast.
- `glass_contrast.mjs` and `glass_probe.mjs` need Playwright and never install it or its browsers. They look for it through `PLAYWRIGHT_MODULE`, the project, the plugin and the global npm root. If it is missing, do not add it to the user's project without asking; offer a scratch install (`npm i playwright --prefix <scratch>`, then `PLAYWRIGHT_MODULE=<scratch>/node_modules/playwright`) or a global one. Exit 2 means the check could not run; report it as not run, not as a pass.

## 4. Hand off

Report, in this order:

1. **Outcome:** what changed for the user, and which surfaces.
2. **Changes:** files and why.
3. **Validation:** each command or browser check as passed, failed, not run or not applicable, with the engine it ran in.
4. **Tiers:** the tier each engine or platform renders, with screenshot file names.
5. **Next:** remaining decisions or limits (engines, devices or preferences never opened), or "No action needed".
