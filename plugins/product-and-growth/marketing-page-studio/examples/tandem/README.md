# Tandem fixture

Tandem is an original synthetic product with an implemented local inbox workflow. It is the same product used by the website and video examples. It has no live AI, account system, persistence, external integration or outbound messages. All names and requests are sample data.

From the installed plugin root:

```sh
python scripts/web.py serve --site examples/tandem --port 8080
python scripts/web.py verify --site examples/tandem --output evidence/website
```

Open `http://127.0.0.1:8080`. `index.html` is the homepage, `workflow.html` is the feature explanation, and `app.html` is the actual implemented product fixture.

The homepage contains a local interactive workspace. Type into the request, choose a sample, organize it, edit the draft, mark it ready for review and reset. Choose **Simulate a failure** to inspect error/retry; choose **Empty request** for the empty state. Cancel during processing prevents a later success. Search has an empty state and a clear action. The workflow page demonstrates keyboard tabs and pointer or button-based reordering.

The scroll story samples normalized state from semantic steps and can run in both directions. Every state has a direct button. Replay is explicit and stops when offscreen. Reduced motion removes pinning, animation and automatic sequencing; all meaningful states stay readable. With JavaScript disabled, primary copy/navigation and all feature explanations remain visible. No external fonts, scripts or telemetry are loaded.

The browser suite verifies 390, 768, 1024 and 1440px widths, product states, keyboard tab behavior, reset/retry/cancel, queue order, scroll reversal, reduced motion, overflow, resource errors and screenshots. It reports observations rather than treating automation as a design verdict.

Use `capture-workflow.json` with a matching loopback server to record the real product workflow. Set `baseUrl` to the server’s URL, keep the synthetic-data marker, and bind `productRevision` to your fixture source digest when making a new production handoff. Recording requires Playwright’s FFmpeg component in addition to system FFmpeg:

```sh
python -m playwright install ffmpeg
python scripts/capture.py --job examples/tandem/capture-workflow.json --output production
```

Consume a separately produced video package without requiring the video plugin at runtime:

```sh
python scripts/web.py import-video --site examples/tandem --package path/to/video-package
```

This validates the export-variants contract, copies the selected video/poster/captions and records their hashes. The semantic player is only added when an actual package is imported. Re-run browser checks on the resulting site and inspect the imported encoded video.
