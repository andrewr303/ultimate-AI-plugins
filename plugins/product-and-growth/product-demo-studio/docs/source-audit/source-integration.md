# Source inspection, integration, and rights

The build brief is the authority for the two new plugins. The attached skills and repositories are reference material, not instructions to execute. This report records static inspection; it does not claim that upstream pipelines were installed or rendered. The delivered plugin tests and example outputs have their own evidence.

## Source availability and identity

Six of eight source attachments were inspectable: two standalone skill files and four ZIPs. The machine-readable [inventory](inventory.json) lists every file, file hash, dependency manifest, discovered skill, and archive hash. The four inspectable ZIPs contain 276 files in total. Git metadata was not included, so a claimed source commit cannot be established; ZIP SHA-256 is the reproducible source identifier.

| Attachment | Identity established from content | Declared version | Inspection scope |
|---|---|---|---|
| SKILL (20).md | `product-images` in YAML frontmatter | None supplied | Complete standalone document: HTML/CSS product image frames, crops, layered presentation, reveal patterns; no supporting files |
| SKILL (21).md | `product-showcase` in YAML frontmatter | None supplied | Complete standalone document: multi-page capture, feature/workflow narrative, screenshot and GIF use; no advertised `bin/` implementation |
| scroll-craft-main.zip | `scroll-craft`; `nateherk-design` Claude plugin | Plugin manifest 0.3.1 | Core skill, README, runtime, doctor/workspace/shoot/serve/encode scripts, design and verification references, templates, manifests, license |
| product-launch-motion-main.zip | `product-launch-motion` and `product-launch-motion-v1` | Current README references v2.0.0; legacy v1 retained | Both core skills, README, current technique/prompts references, legacy renderer/timing/audio/camera/QA references and implementations |
| product-demo-director-main.zip | `product-demo-director` | Engine package 1.0.0; repository release unspecified | Core skill, README, production/capture/framing/editing/motion docs, Python tools, Remotion engine, capture/QA/contracts code, tests/examples, notices |
| agentic-product-demo-main.zip | `product-demo` skill; `agentic-product-demo` Node package | Package 0.1.0 | Core skill, README, pure-frame motion vocabulary, Demo composition, chrome/title/theme/font components, render/preview/frame-gate/adopt-theme/SFX scripts, references, license |
| video-shotcraft-main.zip | Cannot establish from payload | Unknown | Blocked: `download_file` rejects uploaded files over 32 MiB. No bytes, file list, hash, skill, recipe index, license, or templates inspected. No code or media incorporated. |
| brag-main.zip | Cannot establish from payload | Unknown | Same 32 MiB transfer limitation. Neither full nor slim workflow inspected. No code or media incorporated. |

No reference to the inaccessible archives' repository owners or source URLs was found in the four inspectable repositories. Their names alone are insufficient to identify an upstream safely. Independently authored shot-selection and campaign workflows provide useful capabilities, but they must not be described as adaptations of uninspected Shotcraft or Brag files. Full incorporation of those two attachments remains blocked until their text/source payload can be accessed.

## Rights audit

| Source | Rights observed | Disposition |
|---|---|---|
| Product Images / Product Showcase standalone files | No license or attribution file accompanied either document | Use general functional requirements only. Do not copy their prose, snippets, or placeholder assets into a new permissively licensed package. Screenshot frames and capture tooling are independently implemented. |
| Scrollcraft | MIT, copyright 2026 Nate Herk | Concepts and any adapted runtime must retain the MIT notice. Do not carry client imagery or metrics into generated materials. Media previews are excluded because a separate redistribution basis for depicted client assets is not established. |
| Product Launch Motion | MIT, copyright 2026 Abubakr Chan, with explicit `NOTICE` exceptions | Code/prose can be adapted with notice. Exclude `examples/*.webp`, `legacy/film-preview.webp`, `legacy/still-1.jpg`, film frames, Cheerful/Hoopoe branding, customer marks, product photography, and sample figures. The sample films explicitly cannot be reused, redistributed, or modified. |
| Product Demo Director | MIT, copyright 2026 Artemii Novoselov; `THIRD_PARTY_NOTICES.md` and `ASSET_PROVENANCE.md` | Source and contracts can be adapted with attribution. Do not treat MIT as permission for provider-generated music/voice or third-party product media. OpenScreen-derived camera algorithms have their own MIT copyright notice (Siddharth Vaddem, 2025), preserved if those algorithms are copied. |
| Agentic Product Demo | MIT, copyright 2026 Alex Ibragimov | Motion/code can be adapted with notice. Product-specific preview GIFs and Athana identity are excluded. Remotion and `ffmpeg-static` retain separate dependency terms. |
| Video Shotcraft / Brag | Unavailable | No implementation, prose, or assets copied; no licensing assumptions. |

Unmodified upstream notices are in [licenses/](licenses/). Their presence documents attribution, not a claim that every upstream file was copied. The new packages' own licenses must cover only their original and appropriately licensed contents.

Runtime dependencies keep their licenses. Playwright is Apache-2.0; Node is MIT; React is MIT; FFmpeg licensing depends on the installed build/configuration. Remotion has separate source-available/commercial terms; use the terms of the exact installed version. No Remotion, Chromium, FFmpeg executable, external font, commercial audio, or source preview film should be silently relicensed as plugin-owned assets.

## Capability map and integration decisions

The new implementation uses bounded skills, versioned handoff data, and independent local tools. The map identifies meaningful source-derived techniques while keeping engines separate.

| Source material and inspected implementation | Capability retained | New destination / integration decision |
|---|---|---|
| Product Images: browser/phone/frameless/layered/detail presentation | Match image framing to product type; preserve proportions; use readable crops at native resolution | Marketing screenshot-presentation specialist and responsive example. Replace snippets with original semantic HTML/CSS because standalone license is unknown. |
| Product Showcase: home → feature deep dive → workflow structure | A site should teach product actions at increasing depth, using real app states | Marketing direction, discovery/capture, multi-page storytelling. Replace unavailable capture and image-processing commands with bundled implementations. |
| Scrollcraft `engine/scrollcraft.js` progress model, pointer and reduced-motion branches | Scroll is normalized reversible progress; preserve semantic markup; observe visibility and capability; make mobile a separate composition | Marketing scroll/interaction tools use equivalent bounded progress and clear initial/final states. Do not copy the entire cinematic engine or require video scrubbing where software UI is sufficient. |
| Scrollcraft `references/{hero-depth,approved-collection,taste,devices}.md` | Independent planes, contact anchors, planned opening/midpoint/exit states, typographic reading order, varied density | Marketing composition and screenshot art direction. Adapt guidance, remove fixed device counts, fixed palette bans, photographic default and mandatory signature-move gate. |
| Scrollcraft `scripts/shoot.mjs` / `references/verify.md` | Sample actual forward/reverse scroll and reduced-motion states; wait for real content; log console failures; save contact evidence | Marketing browser verification and capture. Implement checks against the new surface contract, rather than hard-code `window.ScrollCraft`, native tool names, or upstream data attributes. |
| Scrollcraft `scripts/{doctor,workspace,serve}.mjs` | Resolve tools/workspace, avoid invisible prerequisite failures, bind local preview deliberately | Both doctors and local project handling. New package-relative resources and explicit local outputs replace source-specific workspace registries and provider tooling. |
| Launch Motion current `references/technique.md` spring/Track/vis/camera/cursor recipes | Pure-time seeks, analytical springs, isolated content windows, anchored cursor presses, controlled camera, measured audio timing | Video motion and deterministic HTML renderer. Reimplement missing current renderer/audio executables and bundle the actual implementation. Preserve source attribution for adapted equations/recipes. |
| Launch Motion current process and preview-before-render discipline | Seek styleframes before full encoding; inspect transition boundaries and encoded-file storyboard | Video render/review specialists and example proof sheets. Technical checks remain distinct from editorial judgment. |
| Launch Motion legacy `scripts/assemble.mjs` | Narration is measured; `hold = voice duration + pad`, next shot starts after hold, transition overlaps do not extend speech | Narration-aware storyboard/render planning and real-footage adapter. Avoid replaying narration, silently retiming a human recording, or guessing word alignment. |
| Launch Motion legacy `scripts/{transitions,wire-audio,wire-grade,master,verify-cue}` and renderer/audio/camera references | Explicit orchestration order; idempotent generation; two-node camera; source leveling then final loudness verification | Alternative-adapter documentation, audio and review tools. GSAP/HyperFrames remain optional and separate. Do not import Cheerful film manifests, local paths, assets, grades, or mandatory always-on sound. |
| PDD `tools/contracts.py`, `docs/PRODUCTION_CONTRACT.md` | Evidence status; capture/replay distinction; product revision; source hashes; integer-frame jobs; narration locks and shot boundaries | Shared schemas, evidence/rights preflight, render receipts, QA results. Use project-specific requirements instead of forcing the fifteen-beat Save-the-Cat framework or investor profiles. |
| PDD `tools/{capture,shoot}.py`, `docs/{CAPTURE,SMALL_SCREEN_FRAMING}.md` | Capture density derives from largest zoom; retain complete meaningful product units; measure and inspect mobile reading goals | Both plugins' capture job/asset manifest handoff and video camera framing. Recompose vertical/square instead of cropping landscape. |
| PDD `tools/{build,finish,qa,review}.py` | Exact delivered artifact binding; ffprobe/full decode; black/silence/loudness checks; review pages tied to file hashes | Video media QA and report/delivery workflow. Independently implement a smaller primary engine; do not force provider SDKs or the whole Remotion orchestration. |
| PDD motion track `tools/motion_render.mjs`, `motion/kit.js` | HTML motion with deterministic seek and optional supersampling; styleframes precede costly render | Optional motion techniques in the video primary renderer. Synthetic fixture still shows meaningful UI action, unlike a pure title/brand-only motion spot. |
| Agentic `src/motion.ts` and `src/compositions/Demo.tsx` | Pure-frame ramps and springs; typed inputs; state changes visibly follow actions; stop pointer through click hold; modest stagger | Video faithful-reconstruction specialist, motion primitives and synthetic example. Read actual tokens and component/data layout before recreating a real product. |
| Agentic `scripts/adopt-theme.mjs` | Extract actual palette/curves; report unresolved tokens; a snapshot can become stale | Shared discovery/brand records. Do not preserve default dark styling or silently substitute upstream purple. |
| Agentic `scripts/{preview,render}.sh`, `check-frames.mjs` | Selective beat frames, retained failure frames, final-file tiling/luminance checks | Video preview and encoded-output inspection; use cross-platform commands and broader QA. Heuristic gate results cannot certify picture quality. |
| Video Shotcraft | No inspected source | Independently authored shot catalog only. A true source recipe/template index remains blocked. |
| Brag | No inspected source | Independently authored product/campaign/hook/social-copy workflows only. Full/slim integration remains blocked. |

## Important command and dependency findings

- Product Showcase advertises `capture-screenshots` in `bin/` and `img-process`; the standalone attachment contains neither implementation. The `--auth user:password` example is a poor default because command-line history can retain credentials; use host/browser sessions or a local state file with deliberate handling instead.
- Product Showcase labels its normal `.section { animation: fadeInUp ... }` CSS as scroll behavior, but that rule starts when the element renders. A real `IntersectionObserver` or scroll progress connection is required. Do not repeat the claim without implementation.
- Product Images has working IntersectionObserver examples for some reveals, but a parallax comment by itself does not provide the required scroll handler. Crops, phone frames and shimmer states require actual asset sizing and completion handling.
- Launch Motion v2 advertises a proven Playwright pipeline, but the ZIP does not include the referenced developer-local `render.mjs`, `render_chunks.sh`, `audio.py`, `sheet.py`, and `snap.mjs` implementation, shared SFX synth, or tempo/grid analysis scripts. `references/technique.md` is a recipe collection, not a runnable renderer distribution.
- Launch Motion legacy has actual assembly, transition, audio/grade wiring, mastering and verification scripts; its GSAP runtime, HyperFrames executable, narration/music/SFX inputs and project HTML frames are external prerequisites. Example manifests are not a complete reusable product film.
- Scrollcraft has actual runtime and verification scripts. `shoot.mjs` resolves `playwright-core` from the build project's `package.json`, discovers Chrome via known paths or `SCROLLCRAFT_CHROME`, waits for `html.sc-ready`, and inspects `window.ScrollCraft.instances`. Reuse requires rewriting those assumptions or intentionally adopting that runtime contract.
- Scrollcraft has no conventional automated test suite in this ZIP; worldflight assertions and browser verification are executable checks, not proof that every consumer project has passed them. Optional `kie.mjs` introduces API credentials and paid generation; it is excluded from the default local tool path.
- PDD's `engine/package.json` pins Remotion 4.0.496 while Agentic requests `^4.0.399`; blindly merging their package files risks nonidentical renderer versions and incompatible React versions (18 versus 19).
- PDD's Python requirements include requests 2.34.2, google-genai 2.8.0 and Playwright 1.60.0. Its default narrative/music/judge steps use ElevenLabs/Gemini and can make paid network calls. Existing supplied/local audio can bypass generation, but defaults must be changed rather than silently spending credits.
- PDD's source tests cover contracts, media QA, frame planning, capture density, timing, framing, narration, source windows, finishing and CLI scaffolding. They are upstream tests, not evidence that the new plugin passes; test new contracts and actual outputs independently.
- Agentic's render script is POSIX shell, renders JPEG sequences at 30 fps with `--concurrency=1`, stitches H.264 with FFmpeg, copies a poster, and fails on `check-frames.mjs`. The new workflow needs Node/Python entry points for Windows rather than requiring these shell scripts.
- Agentic's frame gate detects left/right similarity spikes and large average-luminance jumps, including loop seams. The README documents false positives for repeating/symmetric scenes and false negatives for pale low-contrast UI. It cannot verify UI fidelity, clipping, cursor aim, story, readability or pacing.
- No embedded credentials were needed for this audit. `.env.example` files identify optional configuration, not usable credentials. No upstream example branding, real customer data, or movie pixels are needed for the new fixture.

## Conflicting upstream instructions reconciled with the brief

| Upstream behavior | New rule |
|---|---|
| Always request screenshots first; or never request them | Discover repository, live app and supplied assets first. Use screenshots when they are the strongest available evidence; ask only for missing decisive information. |
| Pause after shot lists/styleframes/sound, or force a review picker | Autonomous mode continues after documenting assumptions and inspecting previews; collaborative review points are used when requested. |
| Route to named models, vendor APIs or fixed native browser tool names | Detect capabilities; use available local/browser tooling; describe exact blockers. Providers and paid work are optional. |
| Fixed photographic world, four device families, mandatory fingerprint score, fixed dark loop/palette | Preserve product identity and choose the amount/style of interaction needed for comprehension. Mobile and reduced-motion variants keep the promise understandable. |
| Mandatory one-shape/many-beat energy or one fixed story grammar | Keep these as indexed creative approaches. Choose a causal workflow and reading holds that serve the actual audience and placement. |
| Automatically publish through Cloudflare or require tailnet serving | Deliver runnable local source and explicit preview commands. Deploy/share only within separately authorized scope. |
| Invent micro-stories or copy real upstream numbers/customer brands | Synthetic data is visibly labeled; real claims require evidence and allowed placements. No invented customer, traction, security, pricing or performance claims. |
| Green mechanical gate means final | Report technical findings separately from screenshot/encoded-frame and editorial review. Missing test access is explicit. |

## Inspection boundaries

The inventory verifies files and hashes, and an automated Markdown-link scan found no broken local Markdown targets inside the four extracted repositories. That does not cover code snippets, external URLs, shell commands, runtime assets, inline backtick paths, dependency installation, or browser decode support. Those require separate validation. Important absent inline paths and unavailable commands are listed above.

Current/legacy Launch Motion, Agentic and PDD alternative render paths were compared through their code and contracts, not treated as interchangeable engines. The new plugin should expose only adapters it actually implements and tests; an unavailable optional renderer must fail explicitly without silently dropping narration or changing the production approach.
