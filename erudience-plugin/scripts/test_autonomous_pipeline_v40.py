import unittest,tempfile,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
from autonomous_pipeline_v40 import *

class PipelineTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.path=str(Path(self.temp.name)/'poster.png')
  self.job={'content_id':'crm-001','topic':'CRM lead follow-up','mode':'TEST_FIXTURE'}
  self.calls={}
 def adapters(self,mutate=None):
  mutate=mutate or {}
  def create(stage):
   def f(job,rec,prior):
    self.calls[stage]=self.calls.get(stage,0)+1
    if stage=='SOURCES':a={'verified_sources':['fixture://website-brand-v38']}
    elif stage=='RESEARCH':a={'evidence':['fixture: CRM lead follow-up workflow'],'source_sha256':rec['SOURCES']['hash']}
    elif stage=='STRATEGY':a={'topic':job['topic'],'research_sha256':rec['RESEARCH']['hash']}
    elif stage=='CONTENT':a={'topic':job['topic'],'caption':'CRM lead follow-up matters for sales teams.','keywords':['CRM lead follow-up'],'strategy_sha256':rec['STRATEGY']['hash']}
    elif stage=='BRIEF':a={'topic':job['topic'],'content_sha256':rec['CONTENT']['hash'],'poster_text':{'headline':'CRM lead follow-up','steps':['Capture','Assign','Review']},'brand_profile':'website-v38','heading_font':'Inter','body_font':'DM Sans','palette':PALETTE,'brand_name':'Erudience','footer':'erudience.com'}
    elif stage=='RENDER':
     Image.new('RGB',(1080,1350),'#F6F1E9').save(self.path)
     a={'brief_sha256':rec['BRIEF']['hash'],'image_path':self.path,'image_sha256':sha(self.path),'rendered_text_sha256':hashobj(rec['BRIEF']['artifact']['poster_text']),'font_provenance_verified':True}
    elif stage=='TECH_QA':a={'image_sha256':rec['RENDER']['artifact']['image_sha256']}
    elif stage=='CONTENT_MATCH_QA':a=deterministic_content_match(job,rec,prior)
    elif stage=='BRAND_QA':a=deterministic_brand_check(job,rec,prior)
    elif stage=='DELIVERY':a={'image_sha256':rec['RENDER']['artifact']['image_sha256']}
    else:a={'decision':'PASS','reviewer_id':'fixture-reviewer','observations':'TEST FIXTURE ONLY','subject_sha256':prior['hash']}
    if stage in ('VISUAL_QA',):a.update({'image_sha256':rec['RENDER']['artifact']['image_sha256'],'brief_sha256':rec['BRIEF']['hash']})
    if stage in mutate:a=mutate[stage](a,self.calls[stage])
    return a
   return f
  return {s:Adapter('fixture-producer' if s not in REVIEWS else 'fixture-qa-producer',create(s)) for s in STAGES}
 def test_fixture_full_path(self):
  r=Controller(self.job,self.adapters()).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(r['external_writes'],0);self.assertEqual(len(r['records']),13)
 def test_wrong_topic_returns_content(self):
  def break_once(a,n):
   if n==1:a['topic']='AI customer support'
   return a
  r=Controller(self.job,self.adapters({'CONTENT':break_once})).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(r['repairs'],1);self.assertEqual(self.calls['CONTENT'],2)
 def test_wrong_poster_copy_returns_brief(self):
  def break_once(a,n):
   if n==1:a['content_sha256']='bad'
   return a
  r=Controller(self.job,self.adapters({'BRIEF':break_once})).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['BRIEF'],2);self.assertEqual(self.calls['CONTENT'],1)
 def test_wrong_image_binding_returns_render(self):
  def break_once(a,n):
   if n==1:a['brief_sha256']='bad'
   return a
  r=Controller(self.job,self.adapters({'RENDER':break_once})).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['RENDER'],2)
 def test_missing_review_blocks(self):
  a=self.adapters();a.pop('VISUAL_QA');r=Controller(self.job,a).run();self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['repairs'],0)
 def test_self_review_blocks(self):
  def break_review(a,n):a['reviewer_id']='fixture-qa-producer';return a
  r=Controller(self.job,self.adapters({'BRIEF_QA':break_review}),max_repairs=1).run();self.assertEqual(r['status'],'BLOCKED')
 def test_wrong_topic_forever_blocks(self):
  def bad(a,n):a['topic']='AI customer support';return a
  r=Controller(self.job,self.adapters({'CONTENT':bad})).run();self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['repairs'],4)
 def test_brand_violation_returns_brief(self):
  def bad(a,n):
   if n==1:a['heading_font']='Sora'
   return a
  r=Controller(self.job,self.adapters({'BRIEF':bad})).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['BRIEF'],2)
 def test_visual_failure_returns_render(self):
  def bad(a,n):
   if n==1:a['decision']='FAIL'
   return a
  r=Controller(self.job,self.adapters({'VISUAL_QA':bad})).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['RENDER'],2)
 def test_copy_mismatch_rejected(self):
  def bad(a,n):
   if n==1:a['rendered_text_sha256']='bad'
   return a
  r=Controller(self.job,self.adapters({'RENDER':bad})).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['RENDER'],2)
 def test_delivery_missing_adapter_blocks(self):
  a=self.adapters();a.pop('DELIVERY');r=Controller(self.job,a).run();self.assertEqual(r['status'],'BLOCKED')
 def test_logo_optional(self):
  r=Controller(self.job,self.adapters()).run();self.assertNotIn('logo',r['records']['BRIEF']['artifact']);self.assertEqual(r['status'],'TEST_FIXTURE_PASS')
if __name__=='__main__':unittest.main(verbosity=2)
