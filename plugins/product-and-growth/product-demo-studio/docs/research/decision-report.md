# Product Demo Studio: research and implementation decisions

This is a manually supported research report for the local plugin improvement.
No local research accelerator or automated claim gate was configured. No
`verified_claims.json` or automated research PASS is claimed. Research evidence
informs original implementation; no upstream source code, media, or branding
was imported in this change.

The process used separate GitHub query rungs and Awesome discovery. The GitHub
arm screened sixteen repository lookups and inspected seven finalists; fourteen
lookups supplied default-branch commit details with changed files. The remaining
lookups were retained as access/name-resolution limitations. These counts record
the work performed, not a claim of candidate quality or completeness.

[Discovery](discovery.json) records the query ladder, Awesome results and official
source access. [Screening](screening.json) records stars, commit identifiers,
changed-file observations and explicit activity flags. Repository activity was
checked from default-branch commit details, never inferred from `pushed_at`.
[Sources](sources.jsonl) and the [claim ledger](claim-ledger.jsonl) preserve the
identities behind the manually supported assertions below.

## Manually supported design evidence

Browser automation can wait for an authored page condition before continuing.
Playwright documents retried assertions; Puppeteer documents a page predicate.
This supports declarative readiness conditions. [clm_readiness;
[src_playwright_assertions](https://playwright.dev/python/docs/test-assertions);
[src_puppeteer_wait](https://pptr.dev/api/puppeteer.page.waitforfunction)]

Inspected renderers await seeking and rendering readiness before producing image
output. Remotion waits around frame assignment; Motion Canvas awaits seeking and
stage rendering. [clm_gh_001; clm_frame_boundary;
[src_remotion_seek](https://github.com/remotion-dev/remotion/blob/4bf07553bd5493307ad1ae21988a23e593730bcd/packages/renderer/src/seek-to-frame.ts);
[src_motioncanvas_frame](https://github.com/motion-canvas/motion-canvas/blob/7b91435c301d530351dcf5ebb91dd139c002e405/packages/core/src/app/Renderer.ts)]

Inspected tools resolve stills from authored timeline positions. Motion Canvas
converts a requested time to a frame; Explainroo resolves numeric and scene-based
review positions. [clm_gh_002;
[src_motioncanvas_frame](https://github.com/motion-canvas/motion-canvas/blob/7b91435c301d530351dcf5ebb91dd139c002e405/packages/core/src/app/Renderer.ts);
[src_gh_003](https://github.com/vincentsch/explainroo/blob/e95232c8d535ed2aa390e7b1caee0d1326dd9e83/src/qa.js)]

Frame extraction and subtitle ranges can follow an authored timeline. Explicit
timestamps occur in caption generation and frame encoding across inspected
implementations. [clm_authored_timeline; clm_gh_003;
[src_explainroo_render](https://github.com/vincentsch/explainroo/blob/e95232c8d535ed2aa390e7b1caee0d1326dd9e83/src/render.js);
[src_ffmpeg_filters](https://ffmpeg.org/ffmpeg-filters.html);
[src_gh_004](https://github.com/vincentsch/explainroo/blob/e95232c8d535ed2aa390e7b1caee0d1326dd9e83/src/subtitles.js);
[src_gh_005](https://github.com/microsoft/playwright/blob/f9a841f968dd9a4e315df2ec2930da1952971667/packages/playwright-core/src/server/videoRecorder.ts);
[src_gh_006](https://github.com/dmtrKovalenko/fframes/blob/c2927a8a335d6c208339cb28da8adc5e0549ee5d/fframes/src/renderer/segment_writer.rs)]

Caption timing belongs to the associated speech timeline. This is supported by
the W3C caption guidance and the inspected word-timed caption implementation.
[clm_caption_sync;
[src_w3c_captions](https://www.w3.org/WAI/media/av/captions/);
[src_explainroo_captions](https://github.com/vincentsch/explainroo/blob/e95232c8d535ed2aa390e7b1caee0d1326dd9e83/engine/captions.js)]

Inspected media tests decode encoded output to check image or video properties.
Their test source was reviewed; their upstream suites were not executed.
[clm_gh_004;
[src_gh_007](https://github.com/dmtrKovalenko/fframes/blob/c2927a8a335d6c208339cb28da8adc5e0549ee5d/fframes/src/renderer/tests/alpha_render_tests.rs);
[src_gh_008](https://github.com/microsoft/playwright/blob/f9a841f968dd9a4e315df2ec2930da1952971667/tests/library/video.spec.ts)]

## Implemented choices and provenance

These are observations of the changed local source, distinct from external
research claims. The existing Python, Chromium and FFmpeg architecture remains
the implementation surface; no new rendering framework was installed.

| Requirement | Adopted idea and research claim | Fresh implementation |
|---|---|---|
| Capture the intended product state | Declarative readiness; clm_readiness | [capture.py](../../scripts/capture.py) `wait_for_condition` supports element state, exact text and attribute conditions through bounded browser assertions. Legacy visibility waits remain supported. Receipt/error output excludes expected and observed assertion content. |
| Render products beyond the Tandem sample | Await frame readiness; clm_gh_001 | [render.py](../../scripts/render.py) `template_call` awaits `configure`/`seek`, fonts and image decoding with a bounded timeout. `layout_targets` accepts authored selectors or `data-pds-role` markers; built-in sample checks remain available. |
| Review the authored story and caption edges | Resolve timeline positions; clm_gh_002, clm_authored_timeline | [media.py](../../scripts/media.py) `review_samples` merges authored review points, caption boundaries and midpoints, opening/ending and distributed fallback positions into exact frame indices with labels. |
| Inspect what was encoded | Decode final output; clm_gh_004 | `extract_review` in [media.py](../../scripts/media.py) selects requested encoded frames in a decode pass and creates bounded contact-sheet pages. Full labels and hashes remain in QA records. |
| Keep review evidence bound to cached success | Exact-artifact evidence, derived from the local receipt contract | `receipt_assets_match` in [render.py](../../scripts/render.py) checks delivery sidecars and recorded review assets; missing or modified review output cannot return a cached success. |
| Preserve supplied audio alignment across variants | Explicit speech timeline; clm_caption_sync, clm_gh_003 | [variants.py](../../scripts/variants.py) `materialize` rejects automatic duration changes with supplied audio or preserved source audio. Silent variants scale captions/review points and refresh configuration hashes. |
| Preserve campaign inputs and existing output | Local preflight/staging decision; no upstream implementation copied | `materialize` validates jobs/references before publication, rejects symlink outputs and filename collisions, stages referenced inputs, and preserves populated destinations on failure. |

The new regression coverage is defined in
[custom-template tests](../../tests/test_custom_templates.py),
[media-review tests](../../tests/test_media_review.py),
[capture-condition tests](../../tests/test_capture_conditions.py), and
[variant tests](../../tests/test_variants.py). It exercises asynchronous template
readiness, a non-Tandem encode, clipping/missing targets, receipt tampering,
off-grid caption boundaries, decoded-frame identity, contact-sheet pagination,
delayed capture conditions, private assertion diagnostics, audio-duration guards,
portable input copying, collisions and failed-publication preservation. This
report does not substitute for a recorded test execution or host invocation.

## Unresolved

The matrix below contains source-reviewed, single-project observations for
comparison. They are not independently corroborated legal or maintenance
conclusions. Each finalist's README, implementation, dependency manifest, test
source, license text and release/history surface was inspected. Upstream tests
were not run. No code or assets were imported; license descriptions below are
observations of pinned text, not clearance to copy or distribute it.

| Requirement | Finalist / relevance | `repo@sha:path` evidence | Gap / rejected alternative | License observation and original-design decision |
|---|---|---|---|---|
| Awaited frame readiness | Remotion / strong | [remotion-dev/remotion@4bf07553bd5493307ad1ae21988a23e593730bcd:packages/renderer/src/seek-to-frame.ts](https://github.com/remotion-dev/remotion/blob/4bf07553bd5493307ad1ae21988a23e593730bcd/packages/renderer/src/seek-to-frame.ts) | React/Node lifecycle would replace the existing renderer. Retain the optional adapter. | LICENSE.md contains custom free/company terms; API identifies no SPDX assertion. Use only the abstract awaited-state idea. |
| Timestamped footage and assertions | Playwright / adjacent foundation | [microsoft/playwright@f9a841f968dd9a4e315df2ec2930da1952971667:packages/playwright-core/src/server/videoRecorder.ts](https://github.com/microsoft/playwright/blob/f9a841f968dd9a4e315df2ec2930da1952971667/packages/playwright-core/src/server/videoRecorder.ts) | Recording alone does not author a story or certify final review. Existing browser dependency is sufficient. | LICENSE reads Apache-2.0. Fresh declarative condition wrapper; no upstream code imported. |
| Explicit replay state | rrweb / adjacent | [rrweb-io/rrweb@339683f34bf2dd5df2e7cc18fe59fb924b65661b:packages/rrweb/src/record/index.ts](https://github.com/rrweb-io/rrweb/blob/339683f34bf2dd5df2e7cc18fe59fb924b65661b/packages/rrweb/src/record/index.ts) | Event replay differs from actual recorded footage and adds a new system. | LICENSE reads MIT. Preserve visual-mode distinctions; add no replay dependency. |
| Ordered frames and decoded assertions | fframes / strong framework | [dmtrKovalenko/fframes@c2927a8a335d6c208339cb28da8adc5e0549ee5d:fframes/src/renderer/segment_writer.rs](https://github.com/dmtrKovalenko/fframes/blob/c2927a8a335d6c208339cb28da8adc5e0549ee5d/fframes/src/renderer/segment_writer.rs) | Rust/GPU framework replacement is disproportionate to the verified gaps. | LICENSE.txt reads MIT. Fresh frame planner and encoded-output regression coverage; no performance claim adopted. |
| Editing masks and cursor control | Cap / adjacent application | [CapSoftware/Cap@d0aa6cb7ec0ea9ce46a42fa5d733965719dd1647:apps/desktop/src/routes/editor/masks.ts](https://github.com/CapSoftware/Cap/blob/d0aa6cb7ec0ea9ce46a42fa5d733965719dd1647/apps/desktop/src/routes/editor/masks.ts) | Desktop/cloud application and Rust/Tauri stack add unrelated product scope. No redaction capability is claimed for this change. | LICENSE names MIT exceptions for specified crate families and AGPLv3 elsewhere. No source or mask implementation imported. |
| Author-time still export | Motion Canvas / strong, relaxed activity screen | [motion-canvas/motion-canvas@7b91435c301d530351dcf5ebb91dd139c002e405:packages/core/src/app/Renderer.ts](https://github.com/motion-canvas/motion-canvas/blob/7b91435c301d530351dcf5ebb91dd139c002e405/packages/core/src/app/Renderer.ts) | Generator/canvas model differs from DOM templates. Latest checked branch change is outside the preferred activity window. | LICENSE reads MIT. Abstract frame/time position idea only; no framework migration. |
| Scene review and speech captions | Explainroo / match | [vincentsch/explainroo@e95232c8d535ed2aa390e7b1caee0d1326dd9e83:src/qa.js](https://github.com/vincentsch/explainroo/blob/e95232c8d535ed2aa390e7b1caee0d1326dd9e83/src/qa.js) | Local voice/model stack expands scope. Latest checked commit changes README, which does not establish recent implementation activity. | LICENSE reads MIT. Fresh review-point planner and explicit audio-duration policy; no models downloaded. |

Awesome's curated search returned no matching page. Filtered and unfiltered
repository searches were retained, and `get_repository` evidence informed
strong/match/adjacent relevance grades. Directory records for Revideo,
Hyperframes, Recordly, Remotion and Playwright retain `activity_verified=false`
and `license_verified=false`; those grades establish neither freshness nor
rights. A separate pinned GitHub check is recorded separately where performed.

The requested-name lookups `redotvideo/revideo` and
`hyperframes-kit/hyperframes` did not establish repositories under those names.
They must not be conflated with Awesome's differently owned results.
Motion Canvas and html-video require the relaxed activity screen; testreel is
outside it. MoviePy's checked recent change is documentation. Detailed dates,
changed-file counts and exclusions remain research observations in screening.

Remotion documentation requests returned HTTP 403. Pinned implementation was
inspected instead. The automated research gate was unavailable, so these claims
received manual source review; no failed gate was bypassed. Standalone
project-specific freshness, rights/import permission, candidate performance,
cross-platform behavior, optional Remotion/Hyperframes engines, and intended-host
skill invocation remain unverified. Technical rendering checks do not establish
product truth, editorial quality, privacy completeness or campaign performance.

## Refuted

No checked source contradicted the narrow cross-organization design claims.
The report makes no claim that all candidates are current, compatible,
permissively licensed, imported, or tested in this environment.
