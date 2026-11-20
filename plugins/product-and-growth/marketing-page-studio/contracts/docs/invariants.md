# Contract invariants and handoffs

Every production object has `schemaVersion: "1.0.0"` and a stable, lowercase `id`. Unknown keys fail validation so misspelled fields cannot silently disappear. Schema identifiers use URNs and require no network. Additive or incompatible changes require a deliberate schema-version update and migration; do not mutate an old contract in place.

## Truth and identity

`product-evidence.json` names the product revision and separates verified, supplied, illustrative, and unsupported claims. A verified claim needs at least one source, each source needs a path or HTTP(S) URL, and repository/capture sources must name the same product revision. Unsupported claims may be listed only for internal planning. Do not convert a source's assertion into a verified claim without inspecting its support.

`allowedUses` is enforced for `--use website`, `video`, or `ads`. Default `internal` validates planning and copying without requiring an internal entry on otherwise supported claims. Production commands must specify the intended public use. The validator checks referenced IDs, permissions, and revisions; an agent must still inspect whether the cited source supports the claim.

A registry needs at least one claim and a concise brief. A context inventory that has not verified a claim must be saved as a draft document and must not masquerade as a schema-complete registry.

When `--root` is supplied for campaign briefs, storyboards, render jobs, or exports, the validator automatically loads the declared evidence locator or `product-evidence.json` in that project. Missing or malformed evidence fails. `--evidence FILE` supplies explicit context; it is itself schema-validated before any claim is checked.

## Paths and assets

All paths use forward slashes and are relative to the production project: no drive letters, absolute paths, credentials, URLs in path fields, or `..` traversal. Provenance URLs use HTTP(S) with a hostname and without embedded credentials. Asset IDs stay stable across capture, storyboard and export documents. The selected mode is `actual`, `replay`, or `illustrative`; executable render jobs use the explicit renderer labels `recorded`, `faithful-replay`, or `illustrative`.

`actual` means the pixels were captured from the product under test. A synthetic fixture can have actual captures: its product identity and data must remain labeled synthetic. `replay` means verified states reconstructed or reused for controlled presentation. `illustrative` means a concept/sample workflow and requires a visible sample/simulation label when it could imply live behavior.

Use `--check-files --root PROJECT` to verify capture/rights asset existence and hashes, local product-evidence source files (including automatically loaded contextual evidence), and declared renderer input files. URL sources remain references; validation does not fetch or certify remote sources. A hash is SHA-256 over the file bytes. Input paths resolve under the project, including symlinks; a symlink escape fails. Capture and asset manifests have separate responsibilities: the former describes what was shown; the latter documents permission to use and redistribute it. A capture asset's `rightsId` is the root `id` of its owning `asset-manifest.json` document. Within that document, select the record with the same asset `id`, then require its path and SHA-256 to match. With `--root`, the validator checks this linkage whenever the rights document exists; `--check-files` also requires the rights document to exist.

Asset rights with `permission: "unknown"` cannot be marked redistributable. This check does not grant rights. Keep unknown upstream implementations and media out of distributables until reuse is justified.

## State, frames and layout

A browser `wait-for` step may include `holdMs` from 0 to 10000 to preserve an explicit settled reading hold after locator readiness. Other actions cannot carry a hold; readiness and creative pacing remain separate.

Interactive demos declare their initial state, all relevant states, transitions, learning purpose, keyboard controls and reduced motion behavior. Transition targets must exist and every declared state must be reachable. Meaningful error, empty, retry, cancel and reset states belong in the model when the workflow supports them.

Storyboard shots use integer frame timing, ordered contiguous ranges, and explicit reading holds. A hold cannot exceed its shot. Caption bounds must fit within the composition's safe zone, and the safe zone must fit inside the frame. Render-job captions use seconds with `start < end <= duration`; encoded dimensions must be even for H.264 yuv420 output. Declared export aspect ratios must match their dimensions exactly. Pass `--captures` to reject unknown source asset IDs in a storyboard.

Safe zones in the bundled placement profiles are editable creative margins. They do not certify avoidance of every platform overlay. Confirm current platform-specific safe-area templates and test in the target uploader before publication.

## Source and configuration binding

A render report must identify the job configuration and source inputs used, plus the resulting encoded artifact hash. The renderer should compute these values at execution, rather than trusting a stale supplied report. `sourceHashes` maps relative source paths to actual SHA-256 values; supplying `--root` recomputes and compares them. QA documents carry the same binding, so changing a source file invalidates its older report.

If an executable render job includes `configHash`, compute SHA-256 of UTF-8 canonical JSON for the entire job with only the `configHash` key omitted: sorted keys, `separators=(",", ":")`, `ensure_ascii=False`. The validator recomputes this. A raw job-file SHA can be reported separately as `jobSha256`; it is a different value and includes file whitespace.

## Variants and QA

Experiments refer to declared hook and body IDs, and the hook/body/aspect combination must be unique. Distinct hooks need different text, angle and hypothesis. A 12-entry matrix can express three hooks, two bodies and two compositions; the aspect compositions are the same hypothesis adapted for placement. Keep uncontrolled variables stable when comparing a hook.

A QA record describes checks that actually ran. Status is `pass`, `fail`, `untested`, `blocked`, or `not-applicable`, each with method and details. A pass requires an evidence artifact path. Separate technical, visual, editorial, accessibility, package and host review categories. An unexecuted host session cannot become a pass because scripts worked.

## Exchange procedure

The website plugin exports brand, evidence, capture, campaign and rights documents with their referenced files. The video plugin validates the same objects, then creates storyboard, render, variants, QA, posters and caption files. A website can consume the resulting encoded video and poster as media assets without depending on the video plugin at runtime. Validate again after copying; preserve revisions, modes, source hashes and asset rights.
