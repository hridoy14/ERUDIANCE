import unittest,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from brand_render_v37 import verify_assets,render,COLORS
class TestBrandRenderer(unittest.TestCase):
 def test_empty_assets_block(self):self.assertIn('UNVERIFIED_LOGO',verify_assets({}))
 def test_wrong_palette_block(self):self.assertIn('PALETTE_MISMATCH',verify_assets({'palette':{'paper':'#ffffff'}}))
 def test_unpinned_policy_block(self):self.assertIn('POLICY_NOT_PINNED',verify_assets({'palette':COLORS}))
 def test_no_output_on_failed_brand(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'poster.png';r=render({'copy':{'headline':'AI Support'}} ,target)
   self.assertEqual(r['status'],'BLOCKED');self.assertFalse(target.exists())
if __name__=='__main__':unittest.main()
