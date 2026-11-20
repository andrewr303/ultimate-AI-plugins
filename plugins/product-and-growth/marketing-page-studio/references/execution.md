# Execution, portability and resource loading

## Resolve the installed package

Find the plugin root relative to the loaded skill: from `skills/<name>/SKILL.md`, go up two directories to the directory containing `plugin.json` and `scripts/studio.py`. Resolve an absolute path at runtime, then execute commands from that directory or quote the full script path. Do not assume the caller's working directory is the installed package. Do not use development checkout paths or original attachments.

The commands below are cross-platform Python commands; in Windows 11 PowerShell, use `py -3` if `python` does not select Python 3.10+. Quote paths with spaces. The primary local workflows require no Bash, WSL, paid API or model-specific CLI. Optional adapters may have additional requirements; inspect their dependency report before selecting them.

## Capability detection

Run `python scripts/studio.py doctor` once per environment and after dependency changes. Read each reported capability, not only the exit code. Required capability depends on the selected task: browser capture needs Playwright and a usable Chromium; video encoding needs FFmpeg and ffprobe; instruction-only creative planning needs neither. Node 20+ is for optional JavaScript renderers. A font installed in one browser is not necessarily present in another.

If a dependency is missing, return its name, the failed action and the documented installation command. Complete independent preparation while it is unavailable. Do not silently replace an actual capture with fabricated UI, a narrated video with a silent file, or a selected renderer with a different visual approach. Use a configured browser path or Playwright's supported browser installation rather than assuming a host-specific browser tool name.

## Stable command interface

Run these from the plugin root. Paths are project-relative examples; use `--help` for optional arguments and exact accepted contract versions.

```text
python scripts/studio.py doctor
python scripts/studio.py discover --source PRODUCT_PATH --output PROJECT
python scripts/studio.py discover --source https://example.com --output PROJECT --allow-network
python scripts/studio.py init --output PROJECT --source PRODUCT_PATH
python scripts/studio.py validate --schema brand --input PROJECT/brand.json --root PROJECT
python scripts/studio.py index --query capture
python scripts/studio.py handoff --from-dir PROJECT --output HANDOFF
python scripts/studio.py package-check
```

Discovery summarizes context; it does not certify product claims. Review its findings and inspect the meaningful workflow. Schema validation establishes structure and implemented semantic checks, not persuasive quality or legal rights.

## Modes and review

Autonomous mode is the default: infer routine decisions, record material assumptions and complete the authorized work. Collaborative mode offers creative review at requested points. Template mode follows a chosen template while correcting unsupported claims and broken behavior. Do not insert mandatory pauses after every stage or demand a mode-selection interview.

Delegate bounded independent work when agents are available, with one writer per file and a concrete artifact to review. Keep coupled decisions and final validation with the lead. A team report does not replace opening the screenshots or checking encoded output.

## Costs, privacy and deterministic execution

Use local tools, supplied assets, preview sizes and cached captures first. An API key being present is not authorization to spend credits. Before significant paid generation, estimate calls, duration and expected cost, then follow the host's authorization rules. Providers for voice, music, images and visual judging are optional. Do not upload source code, private captures or customer data by default.

Use deterministic scripts for hashes, timing, schemas, manifests, capture and encoding. Use agent judgment for audience, narrative, art direction, copy and editorial critique. No automated score proves visual quality, conversion lift or campaign performance.

## Validation status language

Record `passed`, `failed`, `blocked` or `not-run` per named check and bind evidence paths and source hashes. Keep these scopes separate: static package checks; script execution; actual browser behavior; encoded-media measurements; visual/editorial inspection; intended-host skill invocation; publishing. Do not claim host routing worked merely because helper scripts ran. Do not turn unavailable playback or audio listening into a pass.

Fix the most consequential reproducible defects, rerun affected checks and rebuild archives after changes. A previously successful render is stale if source/configuration hashes differ. Keep delivery files distinct from scratch intermediates.
