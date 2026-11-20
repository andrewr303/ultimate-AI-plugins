# Screenshots and asset validation

## Plan the evidence

Use the actual app build and supported device/runtime. Select representative screens that demonstrate implemented behavior, with synthetic account/data and no secrets. Record app version, locale, appearance, text size and capture device for reproducibility. Reusing a screenshot from an unrelated build can misrepresent the release.

Discover current required screenshot sizes/device families through the available CLI and current App Store specifications; do not rely on a fixed list from an archive. Confirm frame-device choice independently from upload screenshot category. A decorative frame does not establish Apple accepted dimensions or content compliance.

Use a capture plan with named steps, starting state, navigation and expected screen. Accessibility identifiers support robust navigation; take visual evidence after verifying the intended state. Avoid unconditional sleeps when a stable observable state can be awaited. Empty/error/loading placeholders should be intentional rather than captured accidentally.

## Capture without disturbing other work

Select an exact simulator UDID. Prefer dedicated devices per locale if parallel capture is needed. Change only task-scoped settings and restore them where practical. Verify language after relaunch rather than treating a launch flag as sufficient evidence. Keep previews, deep links and simulator browser URLs in their correct surfaces.

Inspect installed controller and screenshot command help. An uploaded pipeline may mention AXe, idb or Koubou; availability and syntax must be checked, and no extra integration is assumed. Avoid installing pinned frame tools automatically. If framing is optional or unavailable, deliver valid raw captures plus clear pending composition work.

## Inspect and validate

Check exact pixel dimensions, file format, color/rendering, clipping, text legibility, locale consistency, status bars, selected tab, device frame and the intended product claim. Do not stretch a screenshot to satisfy dimensions. When resizing is appropriate, preserve aspect ratio and understand whether padding/cropping changes the represented app.

Generated composites should retain provenance to raw capture and show only features in the app. Validate actual files, not just filenames. Do not claim full screenshot quality from a size validator alone. Include a contact sheet or review index when that materially helps inspect multiple locales/screens.

Store screenshots and preview video may have separate requirements. The pipeline should not upload a photo of a device or a framed composite into the wrong asset slot. Check current constraints rather than relying on a remembered upload type.

## Upload and resume

If upload is requested, prepare an asset/localization plan with current remote counts/order. Keep append versus replacement/deletion explicit and preserve unrelated screenshots. A batch upload can partially complete; inspect receipts and remote state before retrying. Read back resulting asset references/order and report any processing uncertainty.

Do not invoke bulk “approve all” merely because a source example does so. Review generated artifacts first, then execute any already-authorized upload based on concrete evidence. If the task is preparation only, deliver the local assets, manifest and validation results without remote mutation.
