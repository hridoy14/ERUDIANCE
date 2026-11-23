"""Regression tests for verify_output.py (added v4.9.2).

Covers the v4.9.2 fix: the module must be safely importable (previously its
top-level argparse + sys.exit() ran on import), and its CLI behaviour —
exit 0 on a valid 1080x1350 PNG + matching manifest, exit 2 otherwise —
must be unchanged.
"""
import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

class VerifyOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.png = self.root / "poster.png"
        from PIL import Image
        Image.new("RGB", (1080, 1350)).save(self.png)
        meta = {"sha256": hashlib.sha256(self.png.read_bytes()).hexdigest(),
                "locked_stage_names": ["CAPTURE", "ACKNOWLEDGE", "QUALIFY", "ROUTE", "NEXT ACTION", "OUTCOME"],
                "logo_provided": True, "logo_sha256": "abc"}
        (self.root / "poster.json").write_text(json.dumps(meta))

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "verify_output.py"), *args],
                              capture_output=True, text=True)

    def test_import_does_not_exit(self):
        import verify_output  # must not parse sys.argv or call sys.exit()
        self.assertTrue(callable(verify_output.main))

    def test_valid_png_passes(self):
        r = self.run_cli(str(self.png))
        self.assertEqual(r.returncode, 0)
        self.assertIn("PASS_MECHANICAL_ONLY", r.stdout)

    def test_require_logo_passes_when_declared(self):
        r = self.run_cli("--require-logo", str(self.png))
        self.assertEqual(r.returncode, 0)

    def test_missing_png_blocks(self):
        r = self.run_cli(str(self.root / "nope.png"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("BLOCK missing PNG", r.stdout)

    def test_wrong_dimensions_block(self):
        from PIL import Image
        bad = self.root / "bad.png"
        Image.new("RGB", (800, 600)).save(bad)
        (self.root / "bad.json").write_text(json.dumps(
            {"sha256": hashlib.sha256(bad.read_bytes()).hexdigest(),
             "locked_stage_names": ["CAPTURE", "ACKNOWLEDGE", "QUALIFY", "ROUTE", "NEXT ACTION", "OUTCOME"]}))
        r = self.run_cli(str(bad))
        self.assertEqual(r.returncode, 2)
        self.assertIn("BLOCK", r.stdout)

class InspectImageTests(unittest.TestCase):
    """Real pixel inspection (D-08/D-21): values are measured from pixels,
    never from bare boolean inputs. Uses temp dirs only."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def _poster(self, name="poster.png", size=(1080, 1350), draw_text=True):
        from PIL import Image, ImageDraw
        p = self.root / name
        im = Image.new("RGB", size, (246, 241, 233))
        if draw_text:
            d = ImageDraw.Draw(im)
            d.rectangle((64, 64, 1016, 300), fill=(20, 18, 14))
            d.text((80, 90), "Five call handling steps", fill=(246, 241, 233))
            d.text((80, 200), "Answer every enquiry fast", fill=(20, 18, 14))
            for i in range(5):
                y = 360 + i * 140
                d.rectangle((64, y, 1016, y + 110), outline=(180, 170, 150), width=2)
                d.text((90, y + 30), "Step %d route the enquiry" % (i + 1), fill=(20, 18, 14))
            d.rectangle((64, 1100, 1016, 1190), fill=(10, 16, 14))
            d.text((90, 1120), "Keep a person responsible", fill=(246, 241, 233))
            d.text((64, 1270), "erudience.com", fill=(97, 91, 76))
        im.save(p)
        return p

    def test_pass_poster(self):
        import verify_output
        r = verify_output.inspect_image(self._poster())
        self.assertTrue(r["passed"], r)
        self.assertEqual(r["format"], "PNG")
        self.assertEqual(r["size"], (1080, 1350))
        self.assertEqual(r["mode"], "RGB")
        m = r["measurements"]
        self.assertGreater(m["ink_coverage"], 0.02)
        self.assertLess(m["ink_coverage"], 0.85)
        self.assertEqual(len(m["dominant_colors"]), 5)
        self.assertGreaterEqual(m["margin_clearance_px"], 0)
        self.assertTrue(m["mobile_legibility"]["readable_proxy"])
        self.assertTrue(any(s.startswith("ink_coverage=") for s in r["evidence"]))

    def test_wrong_dimensions_fail(self):
        import verify_output
        r = verify_output.inspect_image(self._poster("bad.png", size=(800, 600)))
        self.assertFalse(r["passed"])
        self.assertEqual(r["size"], (800, 600))

    def test_blank_fails(self):
        import verify_output
        r = verify_output.inspect_image(self._poster("blank.png", draw_text=False))
        self.assertFalse(r["passed"])
        self.assertLess(r["measurements"]["ink_coverage"], 0.02)

    def test_missing_file_no_raise(self):
        import verify_output
        r = verify_output.inspect_image(self.root / "nope.png")
        self.assertFalse(r["passed"])
        self.assertIn("error", r)

    def test_for_gate_topic_text_none(self):
        import verify_output
        g = verify_output.inspect_image_for_gate(self._poster())
        self.assertTrue(g["pixel_inspection"])
        self.assertTrue(g["mobile_inspection"])
        self.assertIsNone(g["topic_match"])
        self.assertIsNone(g["text_match"])
        self.assertTrue(any("REQUIRES_HUMAN_OR_OCR" in e for e in g["evidence"]))

    def test_for_gate_missing_file(self):
        import verify_output
        g = verify_output.inspect_image_for_gate(self.root / "nope.png")
        self.assertFalse(g["pixel_inspection"])
        self.assertFalse(g["mobile_inspection"])
        self.assertIsNone(g["topic_match"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
