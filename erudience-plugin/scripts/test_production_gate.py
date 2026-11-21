import tempfile,unittest,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from production_gate import validate,STAGES
class GateTests(unittest.TestCase):
 def test_missing_receipts(self):
  with tempfile.TemporaryDirectory() as d:
   x=validate({'content_id':'a'},{},{},d);self.assertEqual(x['status'],'BLOCKED');self.assertIn('BRAND_ASSET_UNVERIFIED:logo',x['errors'])
 def test_fake_receipt(self):
  with tempfile.TemporaryDirectory() as d:
   x=validate({'content_id':'a'},{'RESEARCH':{'content_id':'a','stage':'RESEARCH','status':'PASS','artifact_path':'missing','artifact_sha256':'a'*64,'reviewer':'qa','producer':'writer','reviewed_at':'today'}},{},d)
   self.assertIn('INVALID_STAGE_ARTIFACT:RESEARCH',x['errors'])
 def test_self_review(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,'evidence.json').write_text('{}');h=hashlib.sha256(b'{}').hexdigest()
   x=validate({'content_id':'a'},{'RESEARCH':{'content_id':'a','stage':'RESEARCH','status':'PASS','artifact_path':'evidence.json','artifact_sha256':h,'reviewer':'same','producer':'same','reviewed_at':'today'}},{},d)
   self.assertIn('INDEPENDENT_REVIEW_MISSING:RESEARCH',x['errors'])
 def test_unauthorized_publish(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertIn('EXTERNAL_WRITE_DISABLED',validate({'content_id':'a','publish':True},{},{},d)['errors'])
 def test_path_escape(self):
  with tempfile.TemporaryDirectory() as d:
   x=validate({'content_id':'a'},{'RESEARCH':{'content_id':'a','stage':'RESEARCH','status':'PASS','artifact_path':'../../etc/passwd','artifact_sha256':'a'*64,'reviewer':'qa','producer':'writer','reviewed_at':'today'}},{},d)
   self.assertIn('INVALID_STAGE_ARTIFACT:RESEARCH',x['errors'])
 def test_uninspected_image(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertIn('IMAGE_INSPECTION_MISSING',validate({'content_id':'a','image_generated':True},{},{},d)['errors'])
if __name__=='__main__':unittest.main()
