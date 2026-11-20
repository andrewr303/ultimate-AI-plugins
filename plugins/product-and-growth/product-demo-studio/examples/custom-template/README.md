# Independent custom-template fixture

Relay is an illustrative local composition with synthetic copy. It demonstrates the custom-template API and review surfaces, without Tandem IDs or a live application. Its evidence explicitly limits the sample claim to this authored state.

From the plugin root, after the normal dependency setup:

```sh
python scripts/studio.py render --job examples/custom-template/render-job.json --output relay-render
python scripts/check_receipt.py --plugin-root . --project examples/custom-template --render relay-render
```

Open `relay-render/video.mp4` and `relay-render/review/contact-sheet.jpg`. In `qa.json`, find the named “Review state appears” beat, its exact frame index and caption-transition samples. The manifest binds their hashes. Technical QA leaves visual review required.

The template exposes async `configure(job)` and independently seekable `seek(seconds)`, with `data-pds-role` targets for content, captions and CTA. Its job declares an explicit evidence file, review points and safe zone. Author a faithful product surface and current product evidence before adapting it for another product.
