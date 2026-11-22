import unittest
from brand_policy_v36 import *
class TestBrandPolicy(unittest.TestCase):
 def test_valid_caption(self):self.assertEqual(check_caption('Small teams need clear workflows. #AIAutomation #WorkflowAutomation',audience='SMB',workflow='triage',handoff='human',cta='question'),[])
 def test_banned(self):self.assertIn('BANNED_BRAND_LANGUAGE',check_caption('Unlock results. #AIAutomation #WorkflowAutomation',audience='SMB',workflow='triage',handoff='human',cta='question'))
 def test_hashtags(self):self.assertIn('HASHTAG_POLICY',check_caption('Text #Random',audience='SMB',workflow='triage',handoff='human',cta='question'))
 def test_wrong_font(self):self.assertIn('SOCIAL_FONT_NOT_SORA',check_poster_spec({'font_family':'Inter'}))
 def test_missing_provenance(self):self.assertIn('LOGO_SOURCE_NOT_PINNED',check_poster_spec({'font_family':'Sora','authentic_logo_sha256':'abc'}))
 def test_no_orchestrator(self):self.assertIn('ORCHESTRATOR_NOT_EXECUTED',check_poster_spec({}))
 def test_no_visual_qa(self):self.assertIn('VISUAL_INSPECTION_REQUIRED',check_poster_spec({}))
if __name__=='__main__':unittest.main()
