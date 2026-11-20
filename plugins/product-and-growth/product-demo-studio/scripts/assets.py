#!/usr/bin/env python3
"""Local screenshot optimization and source-density checks. No network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    Image = ImageOps = None


FORMATS = {"png": "PNG", "webp": "WEBP", "jpeg": "JPEG"}
SUFFIXES = {".png": "png", ".webp": "webp", ".jpg": "jpeg", ".jpeg": "jpeg"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_pillow() -> None:
    if Image is None:
        raise ValueError("Pillow is unavailable; run python -m pip install -r requirements.txt from the installed plugin root")


def load_oriented(path: Path):
    require_pillow()
    if not path.is_file():
        raise ValueError("Input image does not exist or is not a regular file")
    with Image.open(path) as source:
        if source.format not in FORMATS.values():
            raise ValueError("Unsupported input image; use a static PNG, WebP or JPEG")
        if getattr(source, "n_frames", 1) != 1:
            raise ValueError("Animated images are unsupported; select and export a deliberate still first")
        if source.mode not in {"1", "L", "LA", "P", "RGB", "RGBA"}:
            raise ValueError("Unsupported image color mode; convert to a verified sRGB screenshot first")
        source.load()
        original_size = source.size
        orientation = source.getexif().get(274, 1)
        has_alpha = "A" in source.getbands() or "transparency" in source.info
        image = ImageOps.exif_transpose(source).convert("RGBA" if has_alpha else "RGB")
        # ICC-bearing sources need color management; stripping profiles silently can change colors.
        # Keep their color profile while dropping location/camera/text metadata.
        icc_profile = source.info.get("icc_profile")
    image.info.clear()
    return image, original_size, orientation, icc_profile


def parse_crop(value: str | None):
    if value is None:
        return None
    try:
        values = tuple(int(x.strip()) for x in value.split(","))
    except (ValueError, AttributeError) as exc:
        raise argparse.ArgumentTypeError("Crop must be x,y,width,height in oriented source pixels") from exc
    if len(values) != 4:
        raise argparse.ArgumentTypeError("Crop must have four integer values: x,y,width,height")
    return values


def optimize(input_path, output_path, *, max_width=None, format=None, quality=None, crop=None, background=None):
    """Write a new image and hash-bound sidecar; never overwrite existing files."""
    source = Path(input_path).resolve()
    output = Path(output_path).absolute()
    receipt_path = output.with_name(output.name + ".receipt.json")
    if output.resolve() == source:
        raise ValueError("Output must differ from the source; source images are never overwritten")
    if output.exists() or output.is_symlink() or receipt_path.exists() or receipt_path.is_symlink():
        raise ValueError("Output or receipt already exists; choose a new output filename")
    output_format = format or SUFFIXES.get(output.suffix.lower())
    if output_format not in FORMATS:
        raise ValueError("Unsupported output format; use webp, png or jpeg")
    if SUFFIXES.get(output.suffix.lower()) != output_format:
        raise ValueError("Output filename extension must match its chosen PNG, WebP or JPEG format")
    if max_width is not None and (isinstance(max_width, bool) or not isinstance(max_width, int) or max_width < 1):
        raise ValueError("max-width must be a positive integer")
    if quality is not None and (isinstance(quality, bool) or not isinstance(quality, int) or not 1 <= quality <= 100):
        raise ValueError("quality must be an integer between 1 and 100")
    if output_format == "png" and quality is not None:
        raise ValueError("quality applies to WebP/JPEG; PNG uses lossless optimization")
    if background is not None and (output_format != "jpeg" or not re.fullmatch(r"#[0-9a-fA-F]{6}", background)):
        raise ValueError("background applies only to JPEG and must be an explicit #RRGGBB matte")

    before_hash = sha256(source) if source.is_file() else None
    image, encoded_size, orientation, icc_profile = load_oriented(source)
    oriented_size = image.size
    if crop is not None:
        if not isinstance(crop, (tuple, list)) or len(crop) != 4 or any(isinstance(x, bool) or not isinstance(x, int) for x in crop):
            raise ValueError("Crop must be four integers: x,y,width,height")
        x, y, width, height = crop
        if x < 0 or y < 0 or width < 1 or height < 1 or x + width > image.width or y + height > image.height:
            raise ValueError("Crop rectangle must fit entirely within the oriented source image")
        image = image.crop((x, y, x + width, y + height))
    cropped_size = image.size
    if max_width is not None and max_width < image.width:
        height = max(1, round(image.height * max_width / image.width))
        image = image.resize((max_width, height), Image.Resampling.LANCZOS)

    alpha_preserved = image.mode == "RGBA" and output_format != "jpeg"
    if output_format == "jpeg" and image.mode == "RGBA":
        if background is None:
            raise ValueError("JPEG cannot preserve alpha; specify --background '#ffffff' or another explicit #RRGGBB matte")
        rgb = tuple(int(background[n:n + 2], 16) for n in (1, 3, 5))
        matte = Image.new("RGB", image.size, rgb)
        matte.paste(image, mask=image.getchannel("A"))
        image = matte

    effective_quality = quality if quality is not None else (85 if output_format in {"jpeg", "webp"} else None)
    options = {"icc_profile": icc_profile} if icc_profile else {}
    if output_format == "png":
        options.update(optimize=True)
    elif output_format == "webp":
        options.update(quality=effective_quality, method=6)
    else:
        options.update(quality=effective_quality, optimize=True, progressive=True)

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="studio-assets-", dir=output.parent) as scratch:
        staged = Path(scratch) / ("image" + output.suffix.lower())
        image.save(staged, format=FORMATS[output_format], **options)
        if sha256(source) != before_hash:
            raise ValueError("Source changed during optimization; no output was published")
        receipt = {
            "schemaVersion": "1.0.0",
            "tool": "studio-assets",
            "operation": "optimize",
            "source": {"fileName": source.name, "sha256": before_hash, "bytes": source.stat().st_size,
                       "encodedSize": list(encoded_size), "orientedSize": list(oriented_size)},
            "output": {"fileName": output.name, "sha256": sha256(staged), "bytes": staged.stat().st_size,
                       "width": image.width, "height": image.height, "format": output_format},
            "settings": {"exifOrientation": orientation, "orientationApplied": orientation != 1,
                         "crop": list(crop) if crop is not None else None, "cropSpace": "oriented-source-pixels",
                         "croppedSize": list(cropped_size), "maxWidth": max_width,
                         "resized": image.size != cropped_size, "upscaled": False,
                         "quality": effective_quality, "background": background,
                         "alphaPreserved": alpha_preserved, "iccProfilePreserved": bool(icc_profile),
                         "metadataStripped": ["EXIF", "XMP", "comments", "text"]},
        }
        published = False
        try:
            with output.open("xb") as destination, staged.open("rb") as ready:
                published = True
                shutil.copyfileobj(ready, destination)
            with receipt_path.open("x", encoding="utf-8") as sidecar:
                json.dump(receipt, sidecar, indent=2)
                sidecar.write("\n")
        except Exception:
            if published:
                output.unlink(missing_ok=True)
            raise
    return {**receipt, "receiptFile": receipt_path.name, "status": "passed"}


def density(input_path, *, display_width, dpr=1, zoom=1):
    values = {"display-width": display_width, "dpr": dpr, "zoom": zoom}
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0 for v in values.values()):
        raise ValueError("display-width, dpr and zoom must be finite positive numbers")
    source = Path(input_path).resolve()
    image, encoded_size, orientation, _ = load_oriented(source)
    native_target = display_width * dpr * zoom
    if not math.isfinite(native_target):
        raise ValueError("Combined display-width, dpr and zoom exceed a finite pixel target")
    required = math.ceil(native_target)
    enough = image.width >= required
    return {"schemaVersion": "1.0.0", "tool": "studio-assets", "operation": "density",
            "status": "passed" if enough else "failed", "sufficient": enough,
            "source": {"fileName": source.name, "sha256": sha256(source), "encodedSize": list(encoded_size),
                       "orientedSize": list(image.size), "exifOrientation": orientation},
            "displayWidthCssPixels": display_width, "devicePixelRatio": dpr, "maximumZoom": zoom,
            "requiredNativeWidth": required, "availableNativeWidth": image.width,
            "nativeToRequiredRatio": round(image.width / required, 6),
            "scope": "Pixel density only; inspect actual bitmap sharpness and target-size readability separately"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    op = commands.add_parser("optimize", help="Create a new screenshot asset and hash-bound receipt")
    op.add_argument("--input", required=True)
    op.add_argument("--output", required=True)
    op.add_argument("--max-width", type=int)
    op.add_argument("--format", choices=FORMATS)
    op.add_argument("--quality", type=int)
    op.add_argument("--crop", type=parse_crop, help="x,y,width,height in EXIF-oriented source pixels")
    op.add_argument("--background", help="Explicit JPEG alpha matte as #RRGGBB")
    check = commands.add_parser("density", help="Check whether native pixels cover planned display density and zoom")
    check.add_argument("--input", required=True)
    check.add_argument("--display-width", type=float, required=True)
    check.add_argument("--dpr", type=float, default=1)
    check.add_argument("--zoom", type=float, default=1)
    args = parser.parse_args(argv)
    try:
        if args.command == "optimize":
            report = optimize(args.input, args.output, max_width=args.max_width, format=args.format,
                              quality=args.quality, crop=args.crop, background=args.background)
        else:
            report = density(args.input, display_width=args.display_width, dpr=args.dpr, zoom=args.zoom)
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "passed" else 1
    except (ValueError, OSError, Image.DecompressionBombError if Image else ValueError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
