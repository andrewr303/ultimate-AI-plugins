# Website delivery and studio handoff

Deliver runnable source with exact local preview instructions, dependencies, optimized assets and the routes included. A source archive should not require the original attachment locations, development absolute paths or the video plugin.

## Required project evidence

Include a concise brief and assumptions; brand, evidence, capture and rights manifests; actual browser report; meaningful screenshots at tested widths/states; known limitations; and a short map of product claims to their sources. Exclude private browser storage state, credentials, temporary recordings and caches.

Run the site from a clean copied/extracted directory. Verify routes, navigation, assets and controls there. Run package validation on the final source and rebuild any archive after changes. Record exactly which host installations and primary-skill invocations were tested separately from helper scripts.

## Incoming video package

Accept the final video, poster, caption file, export metadata, rights/provenance and source/configuration hashes. Confirm its product revision and claims agree with the site. Choose a video with enough source resolution for its displayed area. Use a poster and reserved aspect ratio to avoid layout shift. Provide playback controls or a useful alternative, reduced-motion behavior and muted inline autoplay only where appropriate. The page promise and CTA cannot depend on every visitor watching.

## Outgoing capture package

A capture handoff contains the brand and product evidence objects, capture manifest, rights manifest and all relative referenced media. Keep actual, replay and illustrative modes attached to individual assets. Include capture event timing for video editing and note source resolution/max planned zoom. Verify hashes after copying.

Use the bundled handoff command from the plugin root. It validates/copies files; it does not grant rights, publish media or install another plugin.

## Final message

Link the runnable source and preview instructions, show the most useful evidence, name what passed and identify material remaining limitations. Keep detailed reports in files. Deployment, publication, account installation or third-party upload require the user's requested scope; source delivery alone does not imply them.

## Validated video embedding

Use `python scripts/studio.py web import-video --site SITE --package VIDEO_PACKAGE` to validate and copy a video handoff into the workflow page. The default manifest is `export-variants.json`; inspect `--help` for selecting a variant. Inspect the resulting page, poster, captions, aspect ratio and provenance. The import does not certify the video's creative quality or grant asset rights.

## Optimized image evidence

Keep original captures immutable. Produce page assets with the [screenshot optimization helper](assets.md), retain its hash-bound receipt, and update capture/rights manifests for the derived file. Check native density at the largest intended display/zoom and inspect the final browser output.
