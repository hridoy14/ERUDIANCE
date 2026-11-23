import unittest,tempfile,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from brand_render_v37 import verify_assets,render,COLORS,render_production_poster
class TestBrandRenderer(unittest.TestCase):
 def test_empty_assets_block(self):self.assertIn('UNVERIFIED_LOGO',verify_assets({}))
 def test_wrong_palette_block(self):self.assertIn('PALETTE_MISMATCH',verify_assets({'palette':{'paper':'#ffffff'}}))
 def test_unpinned_policy_block(self):self.assertIn('POLICY_NOT_PINNED',verify_assets({'palette':COLORS}))
 def test_no_output_on_failed_brand(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'poster.png';r=render({'copy':{'headline':'AI Support'}} ,target)
   self.assertEqual(r['status'],'BLOCKED');self.assertFalse(target.exists())
class TestProductionRenderer(unittest.TestCase):
 """render_production_poster (D-12/D-13): no external BRAND.md pin, Pillow
 default-font fallback recorded honestly, temp logo verified by file hash."""
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
 def _spec(self,**over):
  spec={'copy':{'headline':'Five call handling steps','category':'SUPPORT AUTOMATION','support':'A practical workflow with a clear human hand-off.','steps':['Answer the call','Capture the enquiry','Route to an owner','Follow up on time'],'takeaway':'Keep a person responsible for exceptions.'}}
  spec.update(over);return spec
 def test_production_fallback_fonts(self):
  from PIL import Image
  target=self.root/'poster.png'
  r=render_production_poster(self._spec(),target)
  self.assertEqual(r['status'],'RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA')
  self.assertTrue(target.exists())
  with Image.open(target) as im:self.assertEqual(im.size,(1080,1350))
  self.assertEqual(r['font_source'],'pillow-default-fallback')
  self.assertFalse(r['font_verified'])
  self.assertIn('NOT_PINNED_EXTERNALLY',r['brand_policy'])
  self.assertIsNone(r['logo_sha256']);self.assertTrue(r['logo_absence_checked'])
  receipt=json.loads((self.root/'poster.json').read_text())
  self.assertEqual(receipt['sha256'],r['sha256'])
 def test_production_palette_from_config(self):
  cfg=json.loads((Path(__file__).resolve().parent.parent/'config'/'production-policy-v33.json').read_text())
  r=render_production_poster(self._spec(),self.root/'p2.png')
  self.assertEqual(r['status'],'RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA')
  self.assertEqual(r['palette'],cfg['brand']['palette'])
 def test_production_with_temp_logo(self):
  from PIL import Image
  import hashlib
  logo=self.root/'logo.png';Image.new('RGB',(200,60),(16,110,62)).save(logo)
  logo_sha=hashlib.sha256(logo.read_bytes()).hexdigest()
  r=render_production_poster(self._spec(logo={'path':str(logo),'sha256':logo_sha}),self.root/'p3.png')
  self.assertEqual(r['status'],'RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA')
  self.assertEqual(r['logo_sha256'],logo_sha);self.assertFalse(r['logo_absence_checked'])
 def test_production_logo_sha_mismatch_blocked(self):
  from PIL import Image
  logo=self.root/'logo.png';Image.new('RGB',(200,60)).save(logo)
  target=self.root/'p4.png'
  r=render_production_poster(self._spec(logo={'path':str(logo),'sha256':'0'*64}),target)
  self.assertEqual(r['status'],'BLOCKED');self.assertFalse(target.exists())
 def test_production_bad_headline_blocked(self):
  spec=self._spec();spec['copy']['headline']='word '*13
  r=render_production_poster(spec,self.root/'p5.png')
  self.assertEqual(r['status'],'BLOCKED');self.assertFalse((self.root/'p5.png').exists())
if __name__=='__main__':unittest.main()
