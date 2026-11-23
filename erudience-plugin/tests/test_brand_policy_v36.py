import unittest
from brand_policy_v36 import *
class TestBrandPolicy(unittest.TestCase):
 def test_valid_caption(self):self.assertEqual(check_caption('Small teams need clear workflows. #AIAutomation #WorkflowAutomation',audience='SMB',workflow='triage',handoff='human',cta='question'),[])
 def test_banned(self):self.assertIn('BANNED_BRAND_LANGUAGE',check_caption('Unlock results. #AIAutomation #WorkflowAutomation',audience='SMB',workflow='triage',handoff='human',cta='question'))
 def test_hashtags(self):self.assertIn('HASHTAG_POLICY',check_caption('Text #Random',audience='SMB',workflow='triage',handoff='human',cta='question'))
 def test_wrong_font(self):self.assertIn('SOCIAL_FONT_NOT_SORA',check_poster_spec({'font_family':'Inter'}))
 def test_missing_provenance(self):self.assertIn('LOGO_SOURCE_NOT_PINNED',check_poster_spec({'font_family':'Sora','authentic_logo_sha256':'abc'}))
 def test_no_orchestrator(self):self.assertIn('ORCHESTRATOR_NOT_EXECUTED',check_poster_spec({}))
 def test_no_visual_qa(self):self.assertIn('VISUAL_INSPECTION_REQUIRED',check_poster_spec({}))
class TestCanonicalBrand(unittest.TestCase):
 """check_canonical_brand: expected values are read from config at call time.
 Website-verified 2026-11-24: module PALETTE and canonical config now agree
 (Sora-only, emerald #10B77F)."""
 def _spec(self,**over):
  import json
  from pathlib import Path
  cfg=json.loads((Path(__file__).resolve().parent.parent/'config'/'production-policy-v33.json').read_text())
  spec={'brand':{'heading':cfg['brand']['heading'],'body':cfg['brand']['body']},'palette':{'emerald':cfg['brand']['palette']['emerald']},'logo_asset':None,'footer':'erudience.com'}
  spec.update(over);return spec
 def test_valid(self):self.assertEqual(check_canonical_brand(self._spec()),[])
 def test_wrong_font(self):self.assertIn('BRAND_FONT_MISMATCH',check_canonical_brand(self._spec(brand={'heading':'Inter','body':'DM Sans'})))
 def test_wrong_palette(self):self.assertIn('BRAND_PALETTE_MISMATCH',check_canonical_brand(self._spec(palette={'emerald':'#10B981'})))
 def test_missing_footer(self):self.assertIn('BRAND_FOOTER_MISSING',check_canonical_brand(self._spec(footer='example.com')))
 def test_unapproved_logo(self):self.assertIn('UNAPPROVED_LOGO',check_canonical_brand(self._spec(logo_asset='fake.png')))
 def test_approved_logo_ok(self):
  import json
  from pathlib import Path
  cfg=json.loads((Path(__file__).resolve().parent.parent/'config'/'production-policy-v33.json').read_text())
  self.assertEqual(check_canonical_brand(self._spec(logo_asset=cfg['brand_assets']['approved_logo_path'])),[])
if __name__=='__main__':unittest.main()
