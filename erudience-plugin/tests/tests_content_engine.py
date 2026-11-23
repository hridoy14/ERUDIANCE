import unittest,sys,copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'modules' / 'linkedin_copywriting'))
from content_engine import gate,calendar,weekly_batch,GateError,route,validate_business_registry,validate_buyer_evidence,plan_funnel,lock_content
BASE={'content_id':'e1','publish_date':'2026-12-01','platforms':['linkedin'],'topic':'Follow-up','title':'Who owns follow-up?','pillar':'education','funnel_stage':'awareness','primary_format':'flowchart','derivatives':['text'],'keywords':['lead follow-up'],'buyer_pain':'unclear ownership','cta':'Read checklist','sources':[{'source_id':'s1','url':'https://example.org/source','retrieved_at':'2026-11-21'}],'claims':[{'text':'Example claim','source_ids':['s1']}],'copy':'Original post copy','brand_id':'erudience','category':'education'}
ART={'brand_verified':True,'creative_brief_hash':'a','prompt_hash':'b','visual_qa_pass':True}
class Tests(unittest.TestCase):
 def test_ready(self): self.assertEqual(gate(BASE,ART)['decision'],'READY_FOR_OWNER_REVIEW')
 def test_missing(self):
  x=copy.deepcopy(BASE);del x['title'];self.assertEqual(gate(x,ART)['decision'],'REJECT')
 def test_unsupported_claim(self):
  x=copy.deepcopy(BASE);x['claims'][0]['source_ids']=['fake'];self.assertIn('UNSUPPORTED_CLAIM',gate(x,ART)['reason'])
 def test_no_sources(self):
  x=copy.deepcopy(BASE);x['sources']=[];x['claims']=[];self.assertEqual(gate(x,ART)['decision'],'NOT_VERIFIED')
 def test_no_brand(self):self.assertEqual(gate(BASE,{})['decision'],'BLOCKED')
 def test_case_permission(self):
  x=copy.deepcopy(BASE);x['category']='case_study';self.assertIn('CASE_PERMISSION',gate(x,ART)['reason'])
 def test_calendar(self):self.assertEqual(len(calendar([BASE],'2026-12-01')),30)
 def test_duplicate(self):
  with self.assertRaises(GateError):calendar([BASE,BASE],'2026-12-01')
 def test_batch(self):
  items=[];art={}
  for i in range(7):
   x=copy.deepcopy(BASE);x['content_id']=str(i);items.append(x);art[str(i)]=ART
  self.assertEqual(weekly_batch(items,art)['ready'],7)
  self.assertEqual(weekly_batch(items[:-1],art)['decision'],'REJECT')
 def test_format(self):
  x=copy.deepcopy(BASE);x['primary_format']='video';self.assertEqual(gate(x,ART)['decision'],'REJECT')
class BusinessRegistryTests(unittest.TestCase):
 def test_valid(self):
  reg={'services':[{'name':'Voice agents','description':'AI call handling','boundary':'automation'}],'claims':[{'text':'Calls answered 24/7','source_url':'https://example.org','verified_at':'2026-11-21','boundary':'automation'}],'boundaries':['automation']}
  self.assertEqual(validate_business_registry(reg),[])
 def test_service_name_required(self):
  reg={'services':[{'description':'No name here'}],'claims':[],'boundaries':[]}
  self.assertIn('SERVICE_NAME_REQUIRED',validate_business_registry(reg))
 def test_service_description_required(self):
  reg={'services':[{'name':'Voice agents'}],'claims':[],'boundaries':[]}
  self.assertIn('SERVICE_DESCRIPTION_REQUIRED',validate_business_registry(reg))
 def test_claim_source_required(self):
  reg={'services':[],'claims':[{'text':'A claim','verified_at':'2026-11-21'}],'boundaries':[]}
  self.assertIn('CLAIM_SOURCE_REQUIRED',validate_business_registry(reg))
 def test_claim_verified_at_required(self):
  reg={'services':[],'claims':[{'text':'A claim','source_url':'https://example.org'}],'boundaries':[]}
  self.assertIn('CLAIM_VERIFIED_AT_REQUIRED',validate_business_registry(reg))
 def test_outside_boundary(self):
  reg={'services':[{'name':'S','description':'d','boundary':'other'}],'claims':[{'text':'c','source_url':'https://example.org','verified_at':'2026-11-21','boundary':'other'}],'boundaries':['automation']}
  errors=validate_business_registry(reg)
  self.assertIn('SERVICE_OUTSIDE_BOUNDARY',errors);self.assertIn('CLAIM_OUTSIDE_BOUNDARY',errors)
 def test_invalid_registry(self):
  self.assertEqual(validate_business_registry('nope'),['INVALID_REGISTRY'])
 def test_sorted_unique(self):
  reg={'services':[{},{}],'claims':[],'boundaries':[]}
  errors=validate_business_registry(reg)
  self.assertEqual(errors,sorted(set(errors)))

class BuyerEvidenceTests(unittest.TestCase):
 def test_valid(self):
  ev=[{'buyer_pain':'Missed calls','job_to_be_done':'Answer every call','objection':'Cost','decision_criterion':'Reliability','source_url':'https://example.org'}]
  self.assertEqual(validate_buyer_evidence(ev),[])
 def test_missing_fields(self):
  errors=validate_buyer_evidence([{'buyer_pain':'Missed calls'}])
  self.assertIn('JOB_TO_BE_DONE_REQUIRED',errors);self.assertIn('OBJECTION_REQUIRED',errors)
  self.assertIn('DECISION_CRITERION_REQUIRED',errors);self.assertIn('BUYER_SOURCE_REQUIRED',errors)
 def test_invalid(self):
  self.assertEqual(validate_buyer_evidence('nope'),['INVALID_EVIDENCE'])

class FunnelTests(unittest.TestCase):
 def test_valid_allocation(self):
  items=[{'funnel_stage':'awareness','cta':'Read the guide','cta_destination':'none'},
         {'funnel_stage':'consideration','cta':'Compare plans','cta_destination':'https://example.org/compare','cta_type':'comparison'},
         {'funnel_stage':'decision','cta':'Book a demo','cta_destination':'https://example.org/demo','cta_type':'demo'},
         {'funnel_stage':'retention','cta':'Get support','cta_destination':'https://example.org/support','cta_type':'support'}]
  r=plan_funnel(items)
  self.assertEqual(r['status'],'PASS');self.assertEqual(r['errors'],[])
  self.assertEqual(r['allocation'],{'awareness':1,'consideration':1,'decision':1,'retention':1})
 def test_awareness_service_cta_mismatch(self):
  items=[{'funnel_stage':'awareness','cta':'Buy now','cta_destination':'https://example.org/buy','cta_type':'service'}]
  r=plan_funnel(items)
  self.assertEqual(r['status'],'BLOCKED');self.assertIn('CTA_STAGE_MISMATCH',r['errors'])
 def test_invalid_stage(self):
  r=plan_funnel([{'funnel_stage':'unknown','cta':'x','cta_destination':'none'}])
  self.assertIn('INVALID_FUNNEL_STAGE',r['errors'])
 def test_missing_destination(self):
  r=plan_funnel([{'funnel_stage':'awareness','cta':'Read'}])
  self.assertIn('CTA_DESTINATION_REQUIRED',r['errors'])

class LockContentTests(unittest.TestCase):
 def base(self):
  return {'content_id':'e1','topic':'Follow-up','caption':'Who owns follow-up?','keywords':['lead follow-up'],'poster_text':{'headline':'Who owns follow-up?','footer':'Erudience erudience.com'}}
 def test_lock_returns_record(self):
  locked=lock_content(self.base())
  self.assertEqual(locked['content_id'],'e1');self.assertEqual(locked['topic'],'Follow-up')
  self.assertEqual(len(locked['content_hash']),64)
 def test_hash_stable(self):
  self.assertEqual(lock_content(self.base())['content_hash'],lock_content(self.base())['content_hash'])
 def test_hash_changes_on_caption(self):
  a=self.base();b=self.base();b['caption']='Different caption'
  self.assertNotEqual(lock_content(a)['content_hash'],lock_content(b)['content_hash'])
 def test_hash_changes_on_keyword(self):
  a=self.base();b=self.base();b['keywords']=['other keyword']
  self.assertNotEqual(lock_content(a)['content_hash'],lock_content(b)['content_hash'])
 def test_hash_changes_on_poster_text(self):
  a=self.base();b=self.base();b['poster_text']={'headline':'Other headline','footer':'Erudience erudience.com'}
  self.assertNotEqual(lock_content(a)['content_hash'],lock_content(b)['content_hash'])
 def test_missing_headline_rejected(self):
  bad=self.base();bad['poster_text']={'footer':'Erudience erudience.com'}
  with self.assertRaises(GateError):lock_content(bad)
if __name__=='__main__':unittest.main()
