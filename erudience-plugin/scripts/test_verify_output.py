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

if __name__ == "__main__":
    unittest.main(verbosity=2)
