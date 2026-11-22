import unittest,tempfile
from pathlib import Path
from PIL import Image
from batch_guard_v45 import initialise,summary
from gate_chain_v41 import Chain,Adapter,GateFailure
class BatchTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=self.tmp.name
 def tearDown(self):self.tmp.cleanup()
 def test_seven_independent_jobs(self):
  x=initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121');self.assertEqual(len(x['items']),7);self.assertEqual(x['ready'],0);self.assertEqual(len({r['content_id'] for r in x['items']}),7)
 def test_no_duplicate_topics(self):
  with self.assertRaisesRegex(ValueError,'SEVEN_DISTINCT'):initialise(self.root,['Same']*7,'20261121')
 def test_no_reinitialisation(self):
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  with self.assertRaisesRegex(ValueError,'BATCH_ALREADY'):initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
 def test_image_must_be_portrait(self):
  p=Path(self.root)/'collage.png';Image.new('RGB',(2100,1350)).save(p)
  c=Chain({'content_id':'ER-1','topic':'T','mode':'TEST_FIXTURE'},{});c.records={'IMAGE_PLAN':{'hash':'plan','artifact':{'poster_text':'hello'}},'PLAN_REVIEW':{'hash':'review'}}
  from gate_chain_v41 import filehash,digest
  with self.assertRaises(GateFailure) as cm:c.verify('IMAGE_BUILD',{'content_id':'ER-1','plan_hash':'plan','upstream_hash':'review','image_path':str(p),'image_sha256':filehash(p),'copy_ledger_hash':digest('hello'),'font_provenance':{'Sora':1,'Sora':1}},Adapter('builder',None))
  self.assertEqual(str(cm.exception),'INDIVIDUAL_PORTRAIT_PNG_REQUIRED')
 def test_wrong_content_id_rejected(self):
  c=Chain({'content_id':'ER-1','topic':'T'},{});c.records={'CONTENT':{'hash':'h','artifact':{'topic':'T','caption':'caption'}},'CONTENT_REVIEW':{'hash':'review'}}
  with self.assertRaisesRegex(GateFailure,'PLAN_CONTENT_ID_MISMATCH'):c.verify('IMAGE_PLAN',{'content_id':'ER-2','upstream_hash':'review'},Adapter('planner',None))
if __name__=='__main__':unittest.main()
