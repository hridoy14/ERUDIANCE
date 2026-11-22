import unittest,sys,copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'modules' / 'linkedin_copywriting'))
from content_engine import gate,calendar,weekly_batch,GateError,route
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
if __name__=='__main__':unittest.main()
