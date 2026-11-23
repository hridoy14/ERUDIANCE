import unittest,tempfile
import evidence_store
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
class LiveGateTests(unittest.TestCase):
 """Live-mode gate checks (D-14/D-15/D-16/D-22/D-23). All files live under the
 job's state_dir so path confinement passes; every review carries a real
 inspection-evidence file with a matching sha256. Fixture-mode tests above
 are untouched."""
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
  self.png=self.root/'image.png';Image.new('RGB',(1080,1350),(246,241,233)).save(self.png)
  self.font=self.root/'font.ttf';self.font.write_bytes(b'fake-font-bytes')
  self.evidence=self.root/'inspection.txt';self.evidence.write_text('Independent human review: headline, steps and footer checked against the brief.')
  self.job={'content_id':'voice-01','topic':'AI Voice Automation for Small Businesses','state_dir':str(self.root),'evidence_dir':str(self.root)}
  self.research=[{'url':'https://erudience.com','verified_at':'2026-11-24T00:00:00Z','evidence_label':'LIVE_VERIFIED','provider':'fetch','retrieved_at':'2026-11-24T00:00:00Z','source_sha256':'a'*64}]
  self.strategy={'slots':7,'promotion_count':1,'promotion':{'employee_requirement':'A named employee must own the promoted service.'},'unsupported_claim':False,'unauthorised_write':False}
  self.final_checklist={'content_locked':True,'image_verified':True,'brand_checked':True,'approval_pending':True}
  self.adapters=self._build_adapters()
 def _build_adapters(self):
  adapters={}
  for s in STAGES:
   def make(stage):
    def adapter(job,rec):
     prev=STAGES[STAGES.index(stage)-1] if stage!='SOURCES' else None
     upstream={'upstream_hash':rec[prev]['hash']} if prev else {}
     if stage=='SOURCES':return {'sources':[{'url':'https://erudience.com','verified_at':'2026-11-24T00:00:00Z','source_sha256':'b'*64}]}
     if stage=='RESEARCH':return dict(upstream,research_evidence=list(self.research))
     if stage=='STRATEGY':return dict(upstream,strategy=dict(self.strategy))
     if stage=='CONTENT':return dict(upstream,content_id=job['content_id'],topic=job['topic'],caption='AI Voice Automation for Small Businesses: human handoff matters.',keywords=['voice AI'])
     if stage=='IMAGE_PLAN':return dict(upstream,content_id=job['content_id'],topic=job['topic'],caption=rec['CONTENT']['artifact']['caption'],content_hash=rec['CONTENT']['hash'],poster_text={'headline':'Five call handling steps','steps':['answer','capture','respond','route','follow up'],'footer':'Erudience erudience.com'},dimensions=[1080,1350],brand=BRAND,design_rationale='Five-step workflow',negative_constraints=['no robots'],template_id='website',positioning='business automation',funnel_stage='awareness')
     if stage=='IMAGE_BUILD':return dict(upstream,content_id=job['content_id'],plan_hash=rec['IMAGE_PLAN']['hash'],image_path=str(self.png),image_sha256=filehash(self.png),copy_ledger_hash=digest(rec['IMAGE_PLAN']['artifact']['poster_text']),font_provenance={'Sora':{'path':str(self.font),'sha256':filehash(self.font)}},copy_rendered=True)
     if stage in REVIEWS:
      out=dict(upstream,decision='PASS',reviewer='review-'+stage,observations=['Live reviewer assertion'],subject_hash=rec[prev]['hash'],inspection_evidence_path=str(self.evidence),inspection_evidence_sha256=filehash(self.evidence),inspection_evidence_kind='human_review')
      if stage in ('VISUAL_REVIEW','CONTENT_IMAGE_REVIEW','BRAND_REVIEW','FINAL_REVIEW'):out.update(image_sha256=filehash(self.png),plan_hash=rec['IMAGE_PLAN']['hash'])
      if stage=='VISUAL_REVIEW':out.update(pixel_inspection=True,mobile_inspection=True)
      if stage=='CONTENT_IMAGE_REVIEW':out.update(topic_match=True,text_match=True)
      if stage=='BRAND_REVIEW':out.update(font_files_checked=True,palette_checked=True,footer_checked=True,logo_absence_checked=True,positioning_checked=True)
      if stage=='FINAL_REVIEW' and self.final_checklist is not None:out.update(final_checklist=dict(self.final_checklist))
      return out
     if stage=='DELIVERY':return dict(upstream,image_sha256=filehash(self.png))
     return dict(upstream,evidence='live')
    return adapter
   adapters[s]=Adapter(('review-'+s) if s in REVIEWS else ('build' if s=='IMAGE_BUILD' else 'produce-'+s),make(s),'reviewer' if s in REVIEWS else 'producer')
  return adapters
 def _run(self):return Chain(self.job,self.adapters).run()
 def _has_reason(self,r,code):return any(code in str(x.get('reason','')) for x in r['trace'])
 def test_live_full_chain_passes(self):
  r=self._run();self.assertEqual(r['status'],'READY_FOR_OWNER_REVIEW');self.assertEqual(len(r['completed_stages']),17)
 def test_live_research_empty_blocked(self):
  self.research=[];r=self._run();self.assertEqual(r['status'],'BLOCKED');self.assertTrue(self._has_reason(r,'RESEARCH_EVIDENCE_REQUIRED'))
 def test_live_research_live_verified_missing_provider_blocked(self):
  self.research=[{'url':'https://erudience.com','verified_at':'2026-11-24T00:00:00Z','evidence_label':'LIVE_VERIFIED'}]
  r=self._run();self.assertEqual(r['status'],'BLOCKED');self.assertTrue(self._has_reason(r,'RESEARCH_EVIDENCE_INVALID'))
 def test_live_research_user_supplied_passes(self):
  self.research=[{'url':'https://example.com/guide','verified_at':'2026-11-24T00:00:00Z','evidence_label':'USER_SUPPLIED'}]
  r=self._run();self.assertEqual(r['status'],'READY_FOR_OWNER_REVIEW')
 def test_live_strategy_promotion_count_2_blocked(self):
  self.strategy['promotion_count']=2;r=self._run();self.assertEqual(r['status'],'BLOCKED');self.assertTrue(self._has_reason(r,'STRATEGY_PROMOTION_INVALID'))
 def test_live_strategy_valid_passes(self):
  r=self._run();self.assertEqual(r['status'],'READY_FOR_OWNER_REVIEW')
 def test_live_final_review_without_checklist_blocked(self):
  self.final_checklist=None;r=self._run();self.assertEqual(r['status'],'BLOCKED');self.assertTrue(self._has_reason(r,'FINAL_CHECKLIST_INCOMPLETE'))
 def test_live_path_confinement_blocked(self):
  outside=tempfile.TemporaryDirectory();self.addCleanup(outside.cleanup)
  outside_png=Path(outside.name)/'outside.png';Image.new('RGB',(1080,1350)).save(outside_png)
  old=self.adapters['IMAGE_BUILD']
  def build(j,r):
   x=old.fn(j,r);x['image_path']=str(outside_png);x['image_sha256']=filehash(outside_png);return x
  self.adapters['IMAGE_BUILD']=Adapter(old.name,build)
  r=self._run();self.assertEqual(r['status'],'BLOCKED');self.assertTrue(self._has_reason(r,'PATH_OUTSIDE_ALLOWED_ROOT'))
 def test_live_body_font_both_families(self):
  # BRAND heading and body are both 'Sora' in the frozen config, so the live
  # loop over {heading, body} collapses to one entry today; prove the loop
  # really covers the body family by patching BRAND to diverge them.
  import gate_chain_v41 as gc
  old_brand=gc.BRAND
  try:
   gc.BRAND={'heading':'Sora','body':'OtherBody'}
   chain=Chain(self.job,{})
   plan_artifact={'poster_text':{'headline':'Five call handling steps','footer':'Erudience erudience.com'}}
   chain.records['IMAGE_PLAN']={'artifact':plan_artifact,'hash':digest(plan_artifact),'adapter':'planner'}
   chain.records['PLAN_REVIEW']={'artifact':{},'hash':digest({}),'adapter':'review-PLAN_REVIEW'}
   out={'upstream_hash':chain.records['PLAN_REVIEW']['hash'],'content_id':'voice-01','plan_hash':digest(plan_artifact),'image_path':str(self.png),'image_sha256':filehash(self.png),'copy_ledger_hash':digest(plan_artifact['poster_text']),'font_provenance':{'Sora':{'path':str(self.font),'sha256':filehash(self.font)}},'copy_rendered':True}
   with self.assertRaisesRegex(GateFailure,'LIVE_FONT_BINARY_NOT_VERIFIED'):
    chain.verify('IMAGE_BUILD',out,Adapter('build',None))
   out['font_provenance']['OtherBody']={'path':str(self.font),'sha256':filehash(self.font)}
   chain.verify('IMAGE_BUILD',out,Adapter('build',None))
  finally:gc.BRAND=old_brand
 def test_repair_at_forward_trace(self):
  def boom(j,r):raise GateFailure('BOOM',repair_at='DELIVERY')
  self.adapters['CONTENT']=Adapter('produce-CONTENT',boom)
  r=Chain(self.job,self.adapters,limit=0).run()
  self.assertEqual(r['status'],'BLOCKED')
  self.assertTrue(any(x.get('event')=='REPAIR_AT_IGNORED' and x.get('reason')=='REPAIR_AT_FORWARD' for x in r['trace']))
  fail=[x for x in r['trace'] if x.get('event')=='FAIL']
  self.assertTrue(fail and fail[0].get('return_to')=='CONTENT')
class TestEvidenceStoreLedger(unittest.TestCase):
 """Approval-ledger tests (D-04). No dedicated evidence_store test file exists
 and creating a new test file is prohibited for this repair, so the ledger
 tests live with the gate tests that consume approvals. All approvals here
 use scope='test_only' in temp DBs; no real approval is ever recorded."""
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.db=evidence_store.init(str(Path(self.temp.name)/'ledger.db'))
  self.job='job-1';self.content='content-1';self.ch='c'*64;self.ih='i'*64
 def tearDown(self):
  try:self.db.close()
  except Exception:pass
 def _approve(self,**kw):
  args={'db':self.db,'job_id':self.job,'content_id':self.content,'content_hash':self.ch,'image_hash':self.ih,'actor':'owner','decision':'APPROVE','scope':'test_only'}
  args.update(kw);return evidence_store.record_approval(**args)
 def test_record_and_verify_approval(self):
  rec=self._approve(reason='looks good')
  self.assertEqual(rec['approval_id'],rec['record_hash']);self.assertEqual(rec['prev_hash'],'GENESIS')
  v=evidence_store.verify_approval(self.db,self.job,self.content,self.ch,self.ih)
  self.assertTrue(v['valid']);self.assertEqual(v['reason'],'OK');self.assertEqual(v['approval']['decision'],'APPROVE')
 def test_second_approval_chains_prev_hash(self):
  first=self._approve();second=self._approve()
  self.assertEqual(second['prev_hash'],first['record_hash'])
  self.assertNotEqual(second['record_hash'],first['record_hash'])
 def test_invalid_decision_raises(self):
  with self.assertRaises(ValueError):self._approve(decision='MAYBE')
 def test_image_hash_mismatch(self):
  self._approve()
  v=evidence_store.verify_approval(self.db,self.job,self.content,self.ch,'0'*64)
  self.assertFalse(v['valid']);self.assertEqual(v['reason'],'IMAGE_HASH_MISMATCH')
 def test_tamper_detected(self):
  self._approve()
  self.db.execute('UPDATE approvals SET record_hash=? WHERE job_id=?',('0'*64,self.job));self.db.commit()
  v=evidence_store.verify_approval(self.db,self.job,self.content,self.ch,self.ih)
  self.assertFalse(v['valid']);self.assertEqual(v['reason'],'TAMPER_DETECTED')
 def test_reject_supersedes_approve(self):
  self._approve()
  self._approve(decision='REJECT',reason='not ready')
  v=evidence_store.verify_approval(self.db,self.job,self.content,self.ch,self.ih)
  self.assertFalse(v['valid']);self.assertEqual(v['reason'],'NOT_APPROVED')
  self.assertEqual(evidence_store.latest_approval(self.db,self.job,self.content)['decision'],'REJECT')
 def test_latest_approval_none_when_empty(self):
  self.assertIsNone(evidence_store.latest_approval(self.db,self.job,self.content))
 def test_record_handoff_and_event(self):
  rid=evidence_store.record_handoff(self.db,self.job,'CONTENT','writer','reviewer','in-hash','out-hash')
  self.assertTrue(rid)
  row=self.db.execute('SELECT verdict,stage FROM receipts WHERE id=?',(rid,)).fetchone()
  self.assertEqual(row,('PASS','HANDOFF:CONTENT'))
  key=evidence_store.record_event(self.db,self.job,'NOTE',{'text':'hello'})
  self.assertTrue(key)
  row=self.db.execute('SELECT stage FROM evidence WHERE id=?',(key,)).fetchone()
  self.assertEqual(row[0],'NOTE')
 def test_old_db_migration(self):
  import sqlite3
  path=str(Path(self.temp.name)/'old.db')
  old=sqlite3.connect(path);old.executescript(evidence_store.SCHEMA);old.commit();old.close()
  db2=evidence_store.init(path)
  try:
   cols={r[1] for r in db2.execute('PRAGMA table_info(approvals)')}
   for c in ('content_id','reason','image_hash','record_hash','prev_hash'):self.assertIn(c,cols)
   rec=evidence_store.record_approval(db2,self.job,self.content,self.ch,self.ih,'owner','APPROVE',scope='test_only')
   self.assertEqual(rec['prev_hash'],'GENESIS')
  finally:db2.close()
if __name__=='__main__':unittest.main(verbosity=2)
