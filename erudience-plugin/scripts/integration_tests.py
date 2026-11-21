import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from keyword_research import validate_cluster
from linkedin_seo_validator import review
from competitor_monitor import audit
from linkedin_analytics import summarize
from workflow_engine import run,WorkflowError
class IntegrationTests(unittest.TestCase):
 def batch(self):return [{'content_id':str(i),'promotion':i==6,'employee_requirement':'staff review' if i==6 else None} for i in range(7)]
 def cluster(self):return {'keywords':[{'term':'AI receptionist','type':'primary','intent':'commercial'},{'term':'salon calls','type':'secondary','intent':'informational'}]}
 def test_keywords(self):self.assertEqual(validate_cluster(self.cluster()),[])
 def test_duplicate_keyword(self):
  x=self.cluster();x['keywords'].append(x['keywords'][0]);self.assertIn('DUPLICATE_KEYWORD',validate_cluster(x))
 def test_volume_provenance(self):
  x=self.cluster();x['keywords'][0]['volume']=100;self.assertIn('UNSOURCED_VOLUME',validate_cluster(x))
 def test_seo(self):self.assertEqual(review({'hook':'AI receptionist for salons','body':'How to handle enquiries','cta':'Read more','funnel_stage':'consideration'},self.cluster())['status'],'PASS')
 def test_seo_missing_keyword(self):self.assertIn('PRIMARY_KEYWORD_MISSING',review({'hook':'Salon calls','body':'A workflow','cta':'Read more','funnel_stage':'awareness'},self.cluster())['errors'])
 def test_competitor_missing(self):self.assertEqual(audit([])['gaps']['direct'],15)
 def test_competitor_provenance(self):self.assertIn('MISSING_PROVENANCE',audit([{'name':'Example','group':'direct','retrieved_at':'2026-11-21'}])['errors'])
 def test_analytics_no_invention(self):self.assertIsNone(summarize([{'content_id':'1','source':'export','observed_at':'2026-11-21','impressions':10}])['records'][0]['ctr_pct'])
 def test_analytics_negative(self):self.assertEqual(summarize([{'content_id':'1','source':'export','observed_at':'2026-11-21','clicks':-1}])['status'],'BLOCKED')
 def test_workflow_no_receipts(self):self.assertEqual(run(self.batch(),{})['status'],'BLOCKED')
 def test_workflow_valid_receipts(self):
  from workflow_engine import STAGES
  b=self.batch();r={x['content_id']:{s:'PASS' for s in STAGES[:8]} for x in b}
  self.assertEqual(run(b,r)['status'],'READY_FOR_OWNER_REVIEW')
 def test_workflow_rejects_unapproved_write(self):
  with self.assertRaises(WorkflowError):run(self.batch(),{},external_write=True)
 def test_workflow_rejects_two_promotions(self):
  b=self.batch();b[0]['promotion']=True
  with self.assertRaises(WorkflowError):run(b,{})
 def test_workflow_refuses_fake_delivery(self):
  from workflow_engine import STAGES
  b=self.batch();r={x['content_id']:{s:'PASS' for s in STAGES[:8]} for x in b}
  d=run(b,r)['batch_sha256'];self.assertEqual(run(b,r,{'approved':True,'scope':'external_write','batch_sha256':d},True)['reason'],'NO_VERIFIED_WRITE_ADAPTER')
if __name__=='__main__':unittest.main()
