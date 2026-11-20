# Production renderer

Load this when authoring a render job, changing an adapter, diagnosing a render or reviewing media. Strategy, shots and taste live in their focused references. This file describes commands that ship in this plugin.

## Primary path and installation

The primary path is Python Playwright → deterministic HTML frames → FFmpeg H.264. It derives every state from `seek(seconds)` and samples integer frame positions. It runs offline using self-contained HTML, with network requests blocked during rendering. A local FFmpeg installation must include `libx264`, `loudnorm`, `drawtext`, PNG and AAC support. FFmpeg builds have their own LGPL/GPL terms and are not redistributed here. Browser/FFmpeg binaries are dependencies, not bundled assets.

From the installed plugin root, in Bash, PowerShell or a compatible terminal:

```text
python -m pip install -r requirements.txt
python -m playwright install chromium
python scripts/studio.py doctor
python scripts/render.py --job examples/tandem/promo-vertical.json --output rendered/vertical --preview
python scripts/render.py --job examples/tandem/promo-vertical.json --output rendered/vertical-final
python scripts/render.py --job examples/tandem/promo-landscape.json --output rendered/landscape-final
python scripts/media.py inspect rendered/vertical-final/video.mp4 --job rendered/vertical-final/job.resolved.json --output rendered/vertical-final/qa-recheck.json --review-dir rendered/vertical-final/review-recheck
```

The runner prefers `STUDIO_BROWSER` when configured, otherwise detects an installed Chromium/Chrome/Edge, then tries Playwright's managed Chromium. An invalid explicit override fails instead of silently choosing another browser. Windows 11 is designed to use the same Python commands, a local Chromium installation and FFmpeg on PATH. Windows and macOS were not exercised in this delivery; neither primary path requires WSL by design.

## Job contract

Validate jobs with `python contracts/validate.py --schema render-job --input JOB --root PROJECT --use video --check-files`.

Required input fields are `schemaVersion`, `id`, `renderer`, `productRevision`, `visualMode`, `width`, `height`, `fps`, `duration`, `hook`, `promise`, `cta`, `brand`, `claimIds`, `captions` and `audio`. See the actual examples and `contracts/schemas/render-job.schema.json`. Use explicit `evidence` to locate the canonical product-evidence manifest; permitted claim IDs, evidence revision and source hashes are checked before rendering. The fixture jobs bind three shipped source files under `fixture/`. All names and requests in that fixture are synthetic.

Use relative, forward-slash paths contained in the job's project. The runner blocks parent traversal, absolute/drive paths and symlink escapes. Do not reference the other plugin or an original source ZIP. Put supplied fonts, audio, recordings and evidence inside the project. `sourceHashes` maps relative input paths to their SHA-256 values. `configHash`, when supplied, follows the canonical JSON hashing rule in the shared contracts documentation.

A custom `template` must be self-contained inline HTML with `window.configure(job)` and pure `window.seek(seconds)`. It must not require a web server, runtime network, timers or state accumulated from previous frames. Use the supplied composition as a working implementation, then replace its product UI with verified current components and states. The Tandem template is a clearly labeled sample and should not be passed off as another product. Default layouts include native 9:16, 16:9, 1:1 and 4:5 compositions. Feed layouts replace the initial request with a focused result rather than shrinking the full dashboard.

Both template functions may return a Promise. Rendering awaits each function, font readiness and image decoding before inspecting or capturing the state. `renderTimeoutMs` bounds this readiness wait (default 15000; supported range 100–120000). A rejected or pending function fails explicitly. Every `seek` must independently derive the complete requested state.

Custom templates declare their review surfaces. Mark elements with `data-pds-role="content"`, `data-pds-role="cta"`, and, when captions are authored, `data-pds-role="caption"`. Alternatively supply `layoutTargets: [{"selector":".product-panel","role":"content"},{"selector":".next-step","role":"cta"}]` (add a caption target when needed). Every declared selector must exist; content, CTA and authored captions must be covered. Multiple matching elements are all checked. Hidden ancestors suppress visibility; visible elements are checked for frame bounds and overflow, and caption/CTA targets for `safeZone`. Complete Tandem-derived templates keep their default targets. Declared surfaces do not prove all meaningful content was selected: inspect the encoded output. See the runnable [custom-template example](../examples/custom-template/README.md).

Optional `reviewPoints` names story beats as `[{"time":1.25,"label":"Result ready"}]`, with times inside this job's duration and at most 32 points. Bounds, styleframes and decoded review use the same frame plan: opening/ending, timeline quarters, authored beats and caption boundaries/neighbours/midpoints. Point times select the represented frame with `floor(time * fps)`; receipts record its exact frame/time and merge coincident labels. Captions are limited to 100 per job and total unique review frames to 512; split a longer review rather than dropping authored points. Preview points remain in seconds and resolve at preview fps.

For the supplied template, `body` supports `context`, `review`, and `before-after`. Context retains the original request alongside route and draft; review highlights the editable reply; before/after clears the original request after organization and enlarges the resulting draft. A hook change alone is a hook hypothesis; two identical bodies must not be counted as separate proof strategies.

Every caption interval must be sorted, nonoverlapping and inside the duration. The runner inspects the actual DOM at caption midpoints and key story beats for frame clipping. Optional `safeZone` is a pixel rectangle `{x,y,width,height}`; captions and CTA must fit within it. Placement profiles are editable recommendations, and platform upload rules need current official verification. Custom footage hooks/CTAs/captions are measured against the actual local font and rejected when they cannot fit. No mechanical check determines whether the copy persuades or the UI can be read comfortably on a phone.

## Outputs, caching and review

A successful run writes `video.mp4`, `poster.png`, `captions.srt`, `job.resolved.json`, `qa.json`, `render-manifest.json`, decoded `review/` frames/contact sheets and selected production styleframes. Preview is half the configured raster at 12fps and is explicitly labeled in its receipt. A final is rendered at the job's dimensions and frame rate. Source/configuration, dependency versions, resolved font fingerprints and final artifact hashes bind each receipt to the exact run. Receipts also bind each current decoded frame, contact sheet and styleframe/state sidecar. A changed source or missing/modified bound output causes a rerender; failed or modified QA cannot return a cached success. A started render invalidates a prior successful receipt before production begins.

The default HTML frame generator records representative cursor coordinates, scene labels and reading holds in styleframe JSON. It verifies no browser page errors. Source resolution for this path is vector DOM rendered at delivery pixels. Real footage records its input dimensions/crop and magnification, so enlargement is visible in the report. New custom templates must supply their own zoom/claim/cursor review where necessary.

Encoded-media inspection decodes the final MP4, verifies H.264/yuv420p, dimensions, frame rate, duration, exact frame count, black intervals and requested audio presence. It extracts actual encoded opening/action/result/approval/CTA frames for inspection. Audio, when present, is measured for integrated loudness and true peak. Intentional sound-off outputs have no audio and their report says so. These checks are separate from the required visual/editorial review. Inspect readable UI at phone size, source fidelity, cursor targeting, transitions and settled holds; watch the moving encoded file where a playback tool is available.

`seek` state and geometry are independent of evaluation order. Chromium may round a glyph antialiasing channel by one level as its cache warms; the browser regression allows that one-level raster difference while requiring exact semantic state. Different operating-system fonts, Chromium and FFmpeg builds may produce different pixels/bitstreams. Receipts identify the actual encoded artifact; cross-host bit identity is not promised.

## Actual-footage adapter

`renderer: footage` requires `visualMode: recorded` and `source: {path,start,audioPolicy}`. See `examples/tandem/footage-landscape.json` after installing this package. The bundled raw WebM records the actual local fixture: a request is organized, the result is inspected, and its draft is marked ready for review. It does not record a model call or send a message. The capture manifest preserves its revision and action provenance.

`source.crop: [x,y,width,height]` explicitly selects a semantic source region. It is validated against source pixels. The adapter preserves time, crops only as authored, scales to fit a native text/product layout and never stretches proportions. Portrait formats should use a narrow high-density capture or an authored meaningful crop, then inspect the result. A source shorter than the requested cut fails; it is never looped or held without instruction.

If the source has audio, `audioPolicy` must explicitly be `preserve` or `mute`. Preserved source audio together with external audio tracks is rejected; prepare an explicit mixed master before using that combination. This prevents silent loss of source narration. The adapter does not invent voiceover.

## Supplied audio and narration

`audio[]` entries name a local `path`, `role` (`music`, `narration`, `sfx`), `gainDb`, `start`, optional `duration`, and `rightsId`. Trims and offsets are applied before mixing. The shared mixer measures and applies two-pass normalization to -16 LUFS with a -1.5 dBTP target; encoded QA allows ±1.5 LU integrated and requires true peak at or below -1 dBTP. These are production defaults, not platform upload mandates. No track is purchased or generated through a paid API.

`python scripts/audio.py --output score.wav --duration 12` creates the original, quiet demonstration motif and a measured cue sheet. It is sample production material, not a claim that a generic soundtrack fits every campaign. Supplied licensed music and human narration are preferred when appropriate. Keep item-level rights and provenance in `asset-manifest.json`. The delivered music example uses only this original score; the vertical example is intentionally sound-off. Narration-to-picture alignment remains untested because no narration is supplied. Word timing and caption import are provided by `scripts/timing.py` when present; align complete thoughts with visible source evidence before approving a narrated delivery.

## Variants

Create a canonical campaign/experiment manifest with the shared campaign command, then materialize it:

```text
python scripts/variants.py --job examples/tandem/promo-vertical.json --manifest campaign/experiment-manifest.json --output campaign/jobs --limit 6
```

The compiler validates input contracts and IDs before writing, preserves hypotheses, resolves body references and copies referenced inputs into the new project. It never invents hooks for an unrelated product. It emits `render-jobs.json` plus the canonical experiment manifest. Render representative low-cost jobs first and inspect them; a planned matrix is not evidence that every creative has rendered. The delivered campaign demonstration includes three distinct angle hooks and a separate before/after body preview.

## Optional adapters and honest limits

| Adapter | Contract and dependencies | Availability behavior |
| --- | --- | --- |
| `html-playwright` | Self-contained template + Python Playwright + local Chromium + FFmpeg. Native DOM, sharp text, integer-frame motion. | Primary; exercised end to end. |
| `footage` | Local recording, authored trim/crop/audio policy + FFmpeg + readable local font/Pillow. | Exercised end to end on the fixture recording. |
| `remotion` | An already-installed, appropriately licensed Remotion project with `remotion.project`, `entry`, `composition`; adapter invokes its local CLI without `npx` downloads. | Missing CLI/project fails explicitly. Bridge is implemented but not rendered in this environment. Remotion carries separate commercial terms. |
| `hyperframes` | Caller-verified installed renderer argument vector in `hyperframes.command`; separate `{job}` and `{output}` arguments bind its input/output. | No CLI syntax is guessed. Missing executable or output fails explicitly. Caller integration is untested here. |

External adapters never fall back to HTML or remove requested narration. Their resulting MP4 still receives common media QA and source/output receipts. Their exact scene fidelity, licensing and tooling compatibility must be verified in the selected project before production. Passing a bridge's dependency check does not establish creative or host compatibility.

## Source lineage

The independent implementation takes useful techniques from MIT-licensed inspected sources: Launch Motion's pure seek/critical damping/connected actions, its working legacy timing pipeline's measured narration/overlap reasoning; Agentic Product Demo's frame-defined timing and element motion; Product Demo Director's evidence contracts, native capture density and exact encoded-media QA. No excluded sample films, stills, third-party logos, customer data or upstream soundtracks are bundled. Video Shotcraft and Brag could not be inspected because their supplied archives exceeded the transfer limit; no recipe is attributed to an uninspected implementation. See the source integration/attribution report for archive hashes, licenses and exclusions.
