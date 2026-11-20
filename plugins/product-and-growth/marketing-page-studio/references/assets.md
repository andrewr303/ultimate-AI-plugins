# Screenshot optimization and native density

Load this when preparing a captured screenshot for a marketing page or video detail. The shared helper is bundled independently as `scripts/assets.py` in both plugins. It uses local Pillow only; it makes no network or paid-service calls.

## Check density before enlarging

From the installed plugin root:

```text
python scripts/assets.py density --input captures/product.png --display-width 800 --dpr 2 --zoom 1.5
```

The minimum native width is `ceil(display CSS width × device pixel ratio × maximum zoom)`. This example needs 2400 native pixels. Width is measured after applying EXIF orientation. Exit 0 means sufficient pixel count, exit 1 means insufficient, and exit 2 means invalid input/dependency. The report includes the source hash and calculation.

Pixel count does not prove actual bitmap sharpness or target-size readability. Inspect glyph strokes at native size and the complete UI unit at its intended display size. A blurry source remains blurry after encoding. If density is insufficient, recapture at adequate retained resolution, use a smaller display/crop or choose a better complete detail. Do not upscale to manufacture a passing source.

## Create a new asset

```text
python scripts/assets.py optimize --input captures/product.png --output assets/product.webp --max-width 2400 --format webp --quality 85
python scripts/assets.py optimize --input captures/product.png --output assets/detail.png --crop 120,80,1000,700 --max-width 1000 --format png
```

Use a crop only after measuring a complete meaningful source region. `--crop` is x,y,width,height in EXIF-oriented source pixels, must fit inside the source, and is applied before resize. No hidden crop is performed. `--max-width` only reduces a larger image; it never upscales. Height follows aspect ratio. Crop and resize geometry are recorded separately.

Static PNG, WebP and JPEG inputs are supported. Animated inputs and unsupported color modes fail instead of silently flattening or changing appearance. Choose an output extension matching `--format`, or omit `--format` to infer it from `.png`, `.webp`, `.jpg` or `.jpeg`. PNG optimization is lossless and does not accept `--quality`; WebP/JPEG default to quality 85 and accept 1–100.

PNG/WebP preserve alpha. JPEG requires an explicit matte if the source has alpha:

```text
python scripts/assets.py optimize --input captures/transparent.png --output assets/product.jpg --format jpeg --background '#ffffff' --quality 90
```

No background color is silently assumed. The explicit `#RRGGBB` matte is a deliberate rendering decision. Other formats reject a background argument rather than ignore it.

## Immutable source and receipts

The helper never overwrites the source, an existing output or an existing receipt. Choose a new output name for another candidate. It applies EXIF orientation, removes EXIF/XMP/comments/text metadata and retains any ICC color profile needed for interpreting colors. It does not perform an unverified color-space conversion.

Each success writes `OUTPUT.receipt.json` with source/output SHA-256, dimensions, byte sizes, exact format/quality/crop/resize/orientation/alpha/matte settings and metadata treatment. The receipt uses basenames and hashes rather than development-machine paths. Source bytes are checked again before publishing the new image. Keep the receipt with the asset and update the capture/asset manifest to reference the actual optimized output hash.

Re-run density against the optimized asset at its planned display size and maximum zoom. Then inspect the actual page/video output: file geometry and successful encoding cannot certify visual quality. These image operations do not grant rights, verify claims or change visual provenance mode.
