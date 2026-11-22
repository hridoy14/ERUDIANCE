import unittest,tempfile
from pathlib import Path
from PIL import Image
from gate_chain_v41 import *
class GateTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.png=str(Path(self.temp.name)/'image.png');Image.new('RGB',(1080,1350)).save(self.png)
  self.job={'content_id':'voice-01','topic':'AI Voice Automation for Small Businesses','mode':'TEST_FIXTURE'}
  self.calls={};self.adapters={}
  for s in STAGES:
   def make(stage):
    def adapter(job,rec):
     self.calls[stage]=self.calls.get(stage,0)+1
     prev=STAGES[STAGES.index(stage)-1] if stage!='SOURCES' else None
     upstream={'upstream_hash':rec[prev]['hash']} if prev else {}
     if stage=='SOURCES':return {'sources':[{'url':'https://erudience.com','verified_at':'fixture-only'}]}
     if stage=='CONTENT':return dict(upstream,content_id=job['content_id'],topic=job['topic'],caption='AI Voice Automation for Small Businesses: human handoff matters.',keywords=['voice AI'])
     if stage=='IMAGE_PLAN':return dict(upstream,content_id=job['content_id'],topic=job['topic'],caption=rec['CONTENT']['artifact']['caption'],content_hash=rec['CONTENT']['hash'],poster_text={'headline':'Five call handling steps','steps':['answer','capture','respond','route','follow up'],'footer':'Erudience erudience.com'},dimensions=[1080,1350],brand=BRAND,design_rationale='Five-step workflow',negative_constraints=['no robots'],template_id='website',positioning='business automation',funnel_stage='awareness')
     if stage=='IMAGE_BUILD':return dict(upstream,content_id=job['content_id'],plan_hash=rec['IMAGE_PLAN']['hash'],image_path=self.png,image_sha256=filehash(self.png),copy_ledger_hash=digest(rec['IMAGE_PLAN']['artifact']['poster_text']),font_provenance={'Sora':'fixture-hash'},copy_rendered=True)
     if stage in REVIEWS:
      out=dict(upstream,decision='PASS',reviewer='review-'+stage,observations=['Fixture reviewer assertion'],subject_hash=rec[prev]['hash'])
      if stage in ('VISUAL_REVIEW','CONTENT_IMAGE_REVIEW','BRAND_REVIEW','FINAL_REVIEW'):out.update(image_sha256=filehash(self.png),plan_hash=rec['IMAGE_PLAN']['hash'])
      if stage=='VISUAL_REVIEW':out.update(pixel_inspection=True,mobile_inspection=True)
      if stage=='CONTENT_IMAGE_REVIEW':out.update(topic_match=True,text_match=True)
      if stage=='BRAND_REVIEW':out.update(font_files_checked=True,palette_checked=True,footer_checked=True,logo_absence_checked=True,positioning_checked=True)
      return out
     if stage=='DELIVERY':return dict(upstream,image_sha256=filehash(self.png))
     return dict(upstream,evidence='fixture')
    return adapter
   self.adapters[s]=Adapter(('review-'+s) if s in REVIEWS else ('build' if s=='IMAGE_BUILD' else 'produce-'+s),make(s),'reviewer' if s in REVIEWS else 'producer')
 def test_full_fixture(self):
  r=Chain(self.job,self.adapters).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(len(r['completed_stages']),17)
 def test_missing_adapter_blocks(self):
  del self.adapters['IMAGE_PLAN'];r=Chain(self.job,self.adapters).run();self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['trace'][-1]['reason'],'ADAPTER_MISSING')
 def test_wrong_plan_returns_to_content_plan(self):
  old=self.adapters['IMAGE_PLAN'];n=[0]
  def broken(j,r):
   x=old.fn(j,r);n[0]+=1
   if n[0]==1:x['caption']='wrong caption'
   return x
  self.adapters['IMAGE_PLAN']=Adapter(old.name,broken)
  r=Chain(self.job,self.adapters).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(r['repairs'],1);self.assertTrue(any(x.get('return_to')=='IMAGE_PLAN' for x in r['trace']))
 def test_visual_fail_rebuilds_and_rechecks(self):
  old=self.adapters['VISUAL_REVIEW'];n=[0]
  def bad(j,r):
   x=old.fn(j,r);n[0]+=1
   if n[0]==1:x['pixel_inspection']=False
   return x
  self.adapters['VISUAL_REVIEW']=Adapter(old.name,bad,'reviewer')
  r=Chain(self.job,self.adapters).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['IMAGE_BUILD'],2);self.assertEqual(r['repairs'],1)
 def test_content_image_fail_returns_to_plan(self):
  old=self.adapters['CONTENT_IMAGE_REVIEW'];n=[0]
  def bad(j,r):
   x=old.fn(j,r);n[0]+=1
   if n[0]==1:x['topic_match']=False
   return x
  self.adapters['CONTENT_IMAGE_REVIEW']=Adapter(old.name,bad,'reviewer')
  r=Chain(self.job,self.adapters).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['IMAGE_PLAN'],2)
 def test_brand_fail_returns_to_plan(self):
  old=self.adapters['BRAND_REVIEW'];n=[0]
  def bad(j,r):
   x=old.fn(j,r);n[0]+=1
   if n[0]==1:x['font_files_checked']=False
   return x
  self.adapters['BRAND_REVIEW']=Adapter(old.name,bad,'reviewer')
  r=Chain(self.job,self.adapters).run();self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(self.calls['IMAGE_PLAN'],2)
 def test_retries_exhausted(self):
  self.adapters['IMAGE_BUILD']=Adapter('builder',lambda j,r: (_ for _ in ()).throw(GateFailure('BUILD_FAILED')))
  r=Chain(self.job,self.adapters).run();self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['repairs'],4)
 def test_wrong_image_bytes(self):
  old=self.adapters['IMAGE_BUILD'];self.adapters['IMAGE_BUILD']=Adapter(old.name,lambda j,r:dict(old.fn(j,r),image_sha256='wrong'))
  r=Chain(self.job,self.adapters,limit=0).run();self.assertEqual(r['status'],'BLOCKED');self.assertIn('IMAGE_BYTES_MISMATCH',r['trace'][-1]['reason'])
 def test_reviewer_role(self):
  old=self.adapters['PLAN_REVIEW'];self.adapters['PLAN_REVIEW']=Adapter(old.name,old.fn,'producer')
  r=Chain(self.job,self.adapters,limit=0).run();self.assertEqual(r['status'],'BLOCKED')
 def test_non_fixture_never_claims_live_without_adapters(self):
  r=Chain({'content_id':'live','topic':'Voice AI'},{}).run();self.assertEqual(r['status'],'BLOCKED')
if __name__=='__main__':unittest.main(verbosity=2)
