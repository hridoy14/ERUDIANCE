import unittest,tempfile,json
from pathlib import Path
from chatgpt_bridge_v43 import start,next_step,submit,load
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=str(Path(self.tmp.name)/'state.json');start(self.p,{'content_id':'t1','topic':'Voice AI','mode':'TEST_FIXTURE'})
 def tearDown(self):self.tmp.cleanup()
 def test_first_stage(self):self.assertEqual(next_step(load(self.p))['stage'],'SOURCES')
 def test_out_of_order(self):
  with self.assertRaisesRegex(ValueError,'OUT_OF_ORDER'):submit(self.p,'CONTENT','writer','producer',{})
 def test_source_pass(self):
  r=submit(self.p,'SOURCES','search','producer',{'sources':[{'url':'https://example.org','verified_at':'fixture-only'}]})
  self.assertEqual(r['next']['stage'],'SOURCE_REVIEW')
 def test_missing_source_retries(self):
  r=submit(self.p,'SOURCES','search','producer',{'sources':[]})
  self.assertEqual(r['next']['stage'],'SOURCES');self.assertEqual(r['repairs'],1)
 def test_fourth_failure_blocks(self):
  for _ in range(4):r=submit(self.p,'SOURCES','search','producer',{'sources':[]})
  self.assertEqual(r['status'],'BLOCKED')
 def test_reviewer_requires_real_receipt(self):
  submit(self.p,'SOURCES','search','producer',{'sources':[{'url':'https://example.org','verified_at':'fixture-only'}]})
  r=submit(self.p,'SOURCE_REVIEW','reviewer','reviewer',{'upstream_hash':next_step(load(self.p))['upstream_hash'],'reviewer':'reviewer','decision':'PASS','observations':[]})
  self.assertEqual(r['last']['event'],'FAIL');self.assertEqual(r['next']['stage'],'SOURCES')
 def test_state_persistence(self):self.assertEqual(load(self.p)['job']['content_id'],'t1')
if __name__=='__main__':unittest.main()
