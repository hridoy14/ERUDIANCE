import sys,unittest,tempfile,json,types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from keyword_research import validate_cluster
try:
    from chatgpt_bridge_v43 import parse_command,dispatch_command,op_get_system_status,start
except ImportError:
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"core"))
    from chatgpt_bridge_v43 import parse_command,dispatch_command,op_get_system_status,start
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

# ---------------------------------------------------------------------------
# Worker 1 additions: full command flow START -> STATUS -> TEST on a single
# job in a temp dir (fixture mode) + get_system_status honesty. Orchestrator
# and ledger are fakes (unittest doubles); no real network, no real
# approval, no writes into the repo.
# ---------------------------------------------------------------------------

def _restore_module(name, old):
    if old is None:
        sys.modules.pop(name, None)
    else:
        sys.modules[name] = old


def _install_fake_module(testcase, name, module):
    old = sys.modules.get(name)
    sys.modules[name] = module
    testcase.addCleanup(_restore_module, name, old)


class _FakeLedger:
    """In-memory stand-in for evidence_store (Worker 3). TEST_ONLY."""
    def __init__(self):
        self.events = []
    def init(self, path):
        return self
    def close(self):
        return None
    def record_event(self, db, job_id, kind, payload):
        self.events.append({"job_id": job_id, "kind": kind, "payload": payload})
        return "evt-%d" % len(self.events)
    def as_module(self):
        mod = types.ModuleType("evidence_store")
        for name in ("init", "close", "record_event"):
            setattr(mod, name, getattr(self, name))
        return mod


def _fake_run_batch(root, topics, cycle, strategy=None, mode="TEST_FIXTURE"):
    base = Path(root)
    base.mkdir(parents=True, exist_ok=True)
    jobs = []
    for i, topic in enumerate(topics, 1):
        cid = "ER-%s-%03d" % (cycle, i)
        p = base / ("%s.json" % cid)
        start(str(p), {"content_id": cid, "topic": topic, "cycle": cycle, "mode": mode})
        jobs.append({"content_id": cid, "state": str(p)})
    (base / "manifest.json").write_text(json.dumps({"cycle": cycle, "jobs": jobs}, indent=2), encoding="utf8")
    return {"cycle": cycle, "expected": 7, "ready": 0, "batch_status": "NOT_APPROVED", "mode": mode}


def _fake_run_job(state_path, adapters=None, mode="TEST_FIXTURE"):
    return {"status": "TEST_FIXTURE_PASS", "state_path": str(state_path), "mode": mode}


def _fake_batch_guard_module():
    mod = types.ModuleType("batch_guard_v45")
    mod.run_batch = _fake_run_batch
    mod.run_job = _fake_run_job
    mod.verify_batch_strategy = lambda root, strategy: {"valid": True, "strategy": strategy}
    mod.check_duplicate_images = lambda root: {"duplicates": [], "count": 0}
    mod.summary = lambda root: {"cycle": "C1", "expected": 7, "ready": 0, "batch_status": "NOT_APPROVED", "items": []}
    mod.AGENT_REGISTRY = {"AG-%02d" % i: {"role": "role-%02d" % i, "name": "Agent %02d" % i} for i in range(1, 19)}
    return mod


class CommandFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = _FakeLedger()
        _install_fake_module(self, "evidence_store", self.ledger.as_module())
        _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module())
    def tearDown(self):
        self.tmp.cleanup()
    def test_command_flow_start_status_test(self):
        topics = ",".join(["Voice AI", "Automation", "SaaS growth", "AI receptionist", "Workflow automation", "Lead generation", "Customer support"])
        parsed = parse_command('erudiance_linkdin start --topics "%s" --cycle C1 --test' % topics)
        self.assertTrue(parsed["ok"], parsed)
        out = dispatch_command(parsed["command"], parsed["args"], str(self.root), owner="operator-1")
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["status"], "STARTED")
        self.assertTrue((self.root / "manifest.json").is_file())
        parsed = parse_command("erudiance_linkdin status")
        self.assertTrue(parsed["ok"], parsed)
        out = dispatch_command(parsed["command"], parsed["args"], str(self.root))
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["result"]["job_count"], 7)
        parsed = parse_command("erudiance_linkdin test --single-content ER-C1-001")
        self.assertTrue(parsed["ok"], parsed)
        out = dispatch_command(parsed["command"], parsed["args"], str(self.root))
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["status"], "TEST_FIXTURE_PASS")
    def test_command_flow_alias_and_at_mention(self):
        parsed = parse_command("erudience_linkdin status")
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["command"], "erudiance_linkdin")
        parsed = parse_command("@Erudience status")
        self.assertTrue(parsed["ok"])
        out = dispatch_command(parsed["command"], parsed["args"], str(self.root))
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "JOB_NOT_FOUND")
    def test_get_system_status_honesty(self):
        out = op_get_system_status({})
        self.assertTrue(out["ok"])
        self.assertFalse(out["chatgpt"]["connected"])
        self.assertIn("Owner-side", out["chatgpt"]["blocker"])
        for status in out["providers"].values():
            self.assertIn(status["status"], ("NOT_CONFIGURED", "CONFIGURED", "ERROR"))
        self.assertNotIn("CONNECTED", json.dumps(out["providers"]))

if __name__=='__main__':unittest.main()
