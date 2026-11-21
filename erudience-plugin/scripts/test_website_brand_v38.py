import unittest
from website_brand_v38 import check,PALETTE
class Tests(unittest.TestCase):
 def base(self):return dict(heading_font='Inter',body_font='DM Sans',palette=PALETTE,dimensions=[1080,1350],brand_name='Erudience',footer='erudience.com',headline='A practical support hand-off workflow',font_heading_sha256='abc',font_body_sha256='def',visual_inspection_receipt='reviewed')
 def test_logo_optional(self):self.assertEqual(check(self.base()),[])
 def test_wrong_fonts(self):
  x=self.base();x['heading_font']='Sora';self.assertIn('WEBSITE_FONT_MISMATCH',check(x))
 def test_missing_identity(self):
  x=self.base();x['footer']='example.com';self.assertIn('BRAND_IDENTITY_MISSING',check(x))
 def test_fake_logo_unverified(self):
  x=self.base();x['logo']='fake.png';self.assertIn('LOGO_PROVENANCE_MISSING',check(x))
 def test_missing_inspection(self):
  x=self.base();x.pop('visual_inspection_receipt');self.assertIn('VISUAL_INSPECTION_MISSING',check(x))
if __name__=='__main__':unittest.main()
