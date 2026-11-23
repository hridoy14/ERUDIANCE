import unittest,tempfile,hashlib
from pathlib import Path
from production_controller_v39 import *
class ControllerTests(unittest.TestCase):
 def test_order(self):
  s=initial('id','CRM follow-up')
  with self.assertRaises(GateError):commit(s,'RENDER',{'x':1})
 def test_source_fail_closed(self):
  s=initial('id','CRM follow-up')
  with self.assertRaises(GateError):commit(s,'SOURCES',{'url':'fake'})
 def test_failure_returns_to_origin(self):
  s=initial('id','CRM follow-up');commit(s,'SOURCES',{'url':'real'},source_verified=True)
  fail(s,'RESEARCH','source inaccessible');self.assertEqual(s['stage'],'RESEARCH')
 def test_reviewer_required(self):
  s=initial('id','CRM follow-up');s['stage']='BRIEF_QA'
  with self.assertRaises(GateError):commit(s,'BRIEF_QA',{'decision':'PASS'},reviewer='same',producer='same')
 def test_brief_caption_mismatch(self):
  s=initial('id','CRM follow-up');s['stage']='BRIEF';s['records']['CONTENT']={'artifact':{'topic':'CRM follow-up','caption':'A'}}
  with self.assertRaises(GateError):commit(s,'BRIEF',{'topic':'CRM follow-up','caption_sha256':'fake','poster_text':'A','brand_profile_version':'v38'})
 def test_render_binding(self):
  s=initial('id','CRM follow-up');s['stage']='RENDER';s['records']['BRIEF']={'artifact':{'topic':'CRM follow-up'}}
  with self.assertRaises(GateError):commit(s,'RENDER',{'brief_sha256':'fake','image_sha256':'x','image_path':'x'})
 def test_image_mismatch(self):
  s=initial('id','CRM follow-up');s['stage']='CONTENT_MATCH_QA';s['records']['BRIEF']={'artifact':{'topic':'CRM follow-up'}};s['records']['RENDER']={'artifact':{'image_sha256':'expected'}}
  with self.assertRaises(GateError):commit(s,'CONTENT_MATCH_QA',{'decision':'PASS','observations':'wrong image','image_sha256':'other','brief_sha256':digest(s['records']['BRIEF']['artifact']),'topic_verified':True},reviewer='reviewer',producer='builder')
 def test_topic_review_required(self):
  s=initial('id','CRM follow-up');s['stage']='CONTENT_MATCH_QA';s['records']['BRIEF']={'artifact':{'topic':'CRM follow-up'}};s['records']['RENDER']={'artifact':{'image_sha256':'expected'}}
  with self.assertRaises(GateError):commit(s,'CONTENT_MATCH_QA',{'decision':'PASS','observations':'checked','image_sha256':'expected','brief_sha256':digest(s['records']['BRIEF']['artifact'])},reviewer='reviewer',producer='builder')
 def test_brand_review_required(self):
  s=initial('id','CRM follow-up');s['stage']='BRAND_QA';s['records']['BRIEF']={'artifact':{'topic':'CRM follow-up'}};s['records']['RENDER']={'artifact':{'image_sha256':'expected'}}
  with self.assertRaises(GateError):commit(s,'BRAND_QA',{'decision':'PASS','observations':'checked','image_sha256':'expected','brief_sha256':digest(s['records']['BRIEF']['artifact'])},reviewer='reviewer',producer='builder')
 def test_revision_invalidates_downstream(self):
  s=initial('id','CRM follow-up');s['stage']='CONTENT_MATCH_QA';s['records']={'SOURCES':{'artifact':{}},'BRIEF':{'artifact':{}},'RENDER':{'artifact':{}},'TECH_QA':{'artifact':{}}}
  fail(s,'CONTENT_MATCH_QA','topic mismatch');self.assertEqual(s['stage'],'BRIEF');self.assertNotIn('RENDER',s['records']);self.assertIn('SOURCES',s['records'])
 def test_max_revisions(self):
  s=initial('id','CRM follow-up')
  for _ in range(4):fail(s,'SOURCES','unavailable')
  self.assertEqual(s['status'],'BLOCKED')
 def test_delivery_blocked(self):
  s=initial('id','CRM follow-up');s['stage']='DELIVERY'
  with self.assertRaises(GateError):commit(s,'DELIVERY',{'image_sha256':'x'})
 def test_technical_image_real(self):
  s=initial('id','CRM follow-up');s['stage']='TECH_QA';s['records']['RENDER']={'artifact':{'image_path':'/nonexistent.png','image_sha256':'fake'}}
  with self.assertRaises(GateError):commit(s,'TECH_QA',{'checked':True})
 def test_no_external_writes(self):
  s=initial('id','CRM follow-up');self.assertEqual(s['external_writes'],0)
if __name__=='__main__':unittest.main()
