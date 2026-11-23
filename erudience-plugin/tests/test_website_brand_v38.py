import unittest
from website_brand_v38 import check,PALETTE
class Tests(unittest.TestCase):
 def base(self):return dict(heading_font='Sora',body_font='Sora',palette=PALETTE,dimensions=[1080,1350],brand_name='Erudience',footer='erudience.com',headline='A practical support hand-off workflow',font_heading_sha256='abc',font_body_sha256='def',visual_inspection_receipt='reviewed')
 def test_logo_optional(self):self.assertEqual(check(self.base()),[])
 def test_wrong_fonts(self):
  x=self.base();x['heading_font']='Inter';self.assertIn('WEBSITE_FONT_MISMATCH',check(x))
 def test_missing_identity(self):
  x=self.base();x['footer']='example.com';self.assertIn('BRAND_IDENTITY_MISSING',check(x))
 def test_fake_logo_unverified(self):
  x=self.base();x['logo']='fake.png';self.assertIn('LOGO_PROVENANCE_MISSING',check(x))
 def test_missing_inspection(self):
  x=self.base();x.pop('visual_inspection_receipt');self.assertIn('VISUAL_INSPECTION_MISSING',check(x))
class WebsiteProfileMatchesCanonical(unittest.TestCase):
 """Brand phase 2026-11-24 (verified website tokens): the website profile is
 now Sora-only with emerald #10B77F — the same as the canonical brand — so
 the website checker and the canonical checker agree. The old Inter/DM Sans
 profile is rejected by both, and the old #10B981 emerald is rejected by
 the canonical checker."""
 def test_website_profile_passes_canonical_check(self):
  from brand_policy_v36 import check_canonical_brand
  out=check_canonical_brand({'brand':{'heading':'Sora','body':'Sora'},'palette':{'emerald':'#10B77F'},'logo_asset':None,'footer':'erudience.com'})
  self.assertEqual(out,[])
 def test_old_inter_profile_fails_website_check(self):
  self.assertIn('WEBSITE_FONT_MISMATCH',check(dict(heading_font='Inter',body_font='DM Sans',palette=PALETTE,dimensions=[1080,1350],brand_name='Erudience',footer='erudience.com',headline='A practical support hand-off workflow',font_heading_sha256='abc',font_body_sha256='def',visual_inspection_receipt='reviewed')))
 def test_old_emerald_rejected_by_canonical_check(self):
  from brand_policy_v36 import check_canonical_brand
  out=check_canonical_brand({'brand':{'heading':'Sora','body':'Sora'},'palette':{'emerald':'#10B981'},'logo_asset':None,'footer':'erudience.com'})
  self.assertIn('BRAND_PALETTE_MISMATCH',out)
 def test_website_check_sora_profile(self):
  self.assertEqual(check(dict(heading_font='Sora',body_font='Sora',palette=PALETTE,dimensions=[1080,1350],brand_name='Erudience',footer='erudience.com',headline='A practical support hand-off workflow',font_heading_sha256='abc',font_body_sha256='def',visual_inspection_receipt='reviewed')),[])
if __name__=='__main__':unittest.main()
