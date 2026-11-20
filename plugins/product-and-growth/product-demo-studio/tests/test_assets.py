"""Generated-image checks for immutable, proportionate screenshot processing."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "assets.py"
if not SCRIPT.is_file():
    SCRIPT = HERE / "assets.py"
spec = importlib.util.spec_from_file_location("studio_assets_under_test", SCRIPT)
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="studio-asset-test-")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.source = self.root / "source.png"
        Image.new("RGB", (600, 400), (12, 90, 125)).save(self.source)
        self.original_hash = assets.sha256(self.source)

    def test_resize_preserves_aspect_and_binds_exact_files(self):
        output = self.root / "small.webp"
        report = assets.optimize(self.source, output, max_width=300, quality=80)
        with Image.open(output) as image:
            self.assertEqual(image.size, (300, 200))
        receipt = json.loads((self.root / "small.webp.receipt.json").read_text())
        self.assertEqual(receipt["source"]["sha256"], self.original_hash)
        self.assertEqual(receipt["output"]["sha256"], assets.sha256(output))
        self.assertEqual(receipt["settings"]["quality"], 80)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(assets.sha256(self.source), self.original_hash)

    def test_larger_max_width_never_upscales_or_crops(self):
        output = self.root / "same.png"
        report = assets.optimize(self.source, output, max_width=1200)
        with Image.open(output) as image:
            self.assertEqual(image.size, (600, 400))
        self.assertFalse(report["settings"]["resized"])
        self.assertFalse(report["settings"]["upscaled"])
        self.assertIsNone(report["settings"]["crop"])

    def test_explicit_crop_then_resize_preserves_selected_geometry(self):
        output = self.root / "detail.png"
        report = assets.optimize(self.source, output, crop=(10, 20, 200, 160), max_width=100)
        self.assertEqual((report["output"]["width"], report["output"]["height"]), (100, 80))
        self.assertEqual(report["settings"]["crop"], [10, 20, 200, 160])

    def test_out_of_bounds_and_nonpositive_crop_fail_without_output(self):
        output = self.root / "bad.png"
        for crop in [(-1, 0, 10, 10), (0, 0, 0, 10), (590, 0, 20, 20), (0, 399, 20, 2)]:
            with self.subTest(crop=crop), self.assertRaisesRegex(ValueError, "Crop rectangle"):
                assets.optimize(self.source, output, crop=crop)
            self.assertFalse(output.exists())

    def test_source_and_existing_artifacts_are_never_overwritten(self):
        with self.assertRaisesRegex(ValueError, "source"):
            assets.optimize(self.source, self.source)
        target = self.root / "existing.png"
        target.write_bytes(b"keep me")
        with self.assertRaisesRegex(ValueError, "already exists"):
            assets.optimize(self.source, target)
        self.assertEqual(target.read_bytes(), b"keep me")
        self.assertEqual(assets.sha256(self.source), self.original_hash)

    def test_existing_receipt_does_not_allow_unbound_output(self):
        output = self.root / "asset.png"
        (self.root / "asset.png.receipt.json").write_text("existing evidence")
        with self.assertRaisesRegex(ValueError, "already exists"):
            assets.optimize(self.source, output)
        self.assertFalse(output.exists())

    def test_png_alpha_survives(self):
        source = self.root / "transparent.png"
        Image.new("RGBA", (50, 30), (90, 10, 20, 0)).save(source)
        output = self.root / "alpha.png"
        report = assets.optimize(source, output)
        with Image.open(output) as image:
            self.assertEqual(image.mode, "RGBA")
            self.assertEqual(image.getpixel((0, 0))[3], 0)
        self.assertTrue(report["settings"]["alphaPreserved"])

    def test_jpeg_alpha_requires_explicit_matte(self):
        source = self.root / "transparent.png"
        Image.new("RGBA", (50, 30), (90, 10, 20, 0)).save(source)
        output = self.root / "matte.jpg"
        with self.assertRaisesRegex(ValueError, "JPEG cannot preserve alpha"):
            assets.optimize(source, output)
        self.assertFalse(output.exists())
        report = assets.optimize(source, output, background="#ffffff", quality=100)
        with Image.open(output) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertTrue(all(channel >= 250 for channel in image.getpixel((0, 0))))
        self.assertFalse(report["settings"]["alphaPreserved"])
        self.assertEqual(report["settings"]["background"], "#ffffff")

    def test_exif_orientation_is_applied_and_exif_removed(self):
        source = self.root / "rotated.jpg"
        image = Image.new("RGB", (120, 80), (10, 20, 30))
        exif = Image.Exif()
        exif[274] = 6
        exif[270] = "Private source comment"
        image.save(source, exif=exif)
        output = self.root / "oriented.png"
        report = assets.optimize(source, output)
        with Image.open(output) as optimized:
            self.assertEqual(optimized.size, (80, 120))
            self.assertFalse(optimized.getexif())
        self.assertTrue(report["settings"]["orientationApplied"])
        self.assertEqual(report["source"]["encodedSize"], [120, 80])

    def test_density_accounts_for_dpr_and_maximum_zoom(self):
        report = assets.density(self.source, display_width=200, dpr=2, zoom=1.5)
        self.assertTrue(report["sufficient"])
        self.assertEqual(report["requiredNativeWidth"], 600)
        failed = assets.density(self.source, display_width=201, dpr=2, zoom=1.5)
        self.assertFalse(failed["sufficient"])
        self.assertEqual(failed["requiredNativeWidth"], 603)

    def test_density_uses_oriented_width(self):
        source = self.root / "rotated.jpg"
        image = Image.new("RGB", (120, 80))
        exif = Image.Exif()
        exif[274] = 6
        image.save(source, exif=exif)
        report = assets.density(source, display_width=100)
        self.assertFalse(report["sufficient"])
        self.assertEqual(report["availableNativeWidth"], 80)

    def test_density_rejects_invalid_and_overflowing_factors(self):
        for factors in [{"display_width": 0}, {"display_width": -1}, {"display_width": float("nan")},
                        {"display_width": 10, "dpr": 0}, {"display_width": 10, "zoom": float("inf")},
                        {"display_width": 1e308, "dpr": 1e308}]:
            with self.subTest(factors=factors), self.assertRaises(ValueError):
                assets.density(self.source, **factors)

    def test_unsupported_inputs_and_mismatched_output_fail(self):
        bmp = self.root / "unsupported.bmp"
        Image.new("RGB", (20, 10)).save(bmp)
        with self.assertRaisesRegex(ValueError, "Unsupported input"):
            assets.optimize(bmp, self.root / "converted.png")
        with self.assertRaisesRegex(ValueError, "extension"):
            assets.optimize(self.source, self.root / "wrong.png", format="jpeg")
        with self.assertRaisesRegex(ValueError, "quality applies"):
            assets.optimize(self.source, self.root / "wrong.png", quality=80)

    def test_animated_images_are_not_silently_flattened(self):
        animated = self.root / "animated.png"
        Image.new("RGB", (20, 10), "red").save(animated, save_all=True,
            append_images=[Image.new("RGB", (20, 10), "blue")], duration=100)
        with self.assertRaisesRegex(ValueError, "Animated"):
            assets.optimize(animated, self.root / "still.png")

    def test_cli_density_distinguishes_insufficient_and_invalid(self):
        command = [sys.executable, str(SCRIPT), "density", "--input", str(self.source), "--display-width"]
        failed = subprocess.run(command + ["1000"], capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(failed.stdout)["sufficient"])
        invalid = subprocess.run(command + ["0"], capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(json.loads(invalid.stderr)["status"], "failed")


if __name__ == "__main__":
    unittest.main()
