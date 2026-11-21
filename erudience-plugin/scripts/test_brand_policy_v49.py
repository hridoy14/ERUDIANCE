import unittest,tempfile
from pathlib import Path
from gate_chain_v41 import Chain,Adapter,BRAND,GateFailure,digest
class PolicyTests(unittest.TestCase):
 def setUp(self):
  self.c=Chain({'content_id':'ER-001','topic':'Enquiries'},{}); self.content={'topic':'Enquiries','caption':'Approved','keywords':['AI'],'content_id':'ER-001'};self.c.records['CONTENT']={'artifact':self.content,'hash':digest(self.content),'adapter':'writer'}
 def plan(self,logo=None):
  p={'upstream_hash':'x','content_id':'ER-001','content_hash':digest(self.content),'topic':'Enquiries','caption':'Approved','poster_text':{'headline':'Stop losing enquiries','footer':'Erudience erudience.com'},'dimensions':[1080,1350],'brand':BRAND,'design_rationale':'buyer clarity','negative_constraints':['no collage'],'template_id':'website','positioning':'business automation','funnel_stage':'awareness'}
  if logo:p['logo_asset']=logo
  return p
 def test_sora_only(self):self.assertEqual(BRAND['body'],'Sora')
 def test_logo_optional(self):
  self.c.records['CONTENT_REVIEW']={'hash':'x','adapter':'reviewer'}
  self.c.verify('IMAGE_PLAN',self.plan(),Adapter('planner',None))
 def test_original_logo_allowed(self):
  self.c.records['CONTENT_REVIEW']={'hash':'x','adapter':'reviewer'}
  self.c.verify('IMAGE_PLAN',self.plan('assets/erudience-owner-approved-logo-2026-11-21.jpg'),Adapter('planner',None))
 def test_fabricated_logo_rejected(self):
  self.c.records['CONTENT_REVIEW']={'hash':'x','adapter':'reviewer'}
  with self.assertRaisesRegex(GateFailure,'UNAPPROVED_LOGO'):self.c.verify('IMAGE_PLAN',self.plan('fake.png'),Adapter('planner',None))
 def test_empty_headline_rejected(self):
  self.c.records['CONTENT_REVIEW']={'hash':'x','adapter':'reviewer'}
  p=self.plan();p['poster_text']['headline']=''
  with self.assertRaisesRegex(GateFailure,'POSTER_COPY_INCOMPLETE'):self.c.verify('IMAGE_PLAN',p,Adapter('planner',None))
if __name__=='__main__':unittest.main()
