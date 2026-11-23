import unittest,tempfile,json,os,sys,types,hashlib,urllib.error
from pathlib import Path
from unittest import mock
from PIL import Image
from gate_chain_v41 import STAGES,REVIEWS,BRAND,digest,filehash
from chatgpt_bridge_v43 import start,next_step,submit,load,save
from chatgpt_bridge_v43 import parse_command,dispatch_command,authorize
from chatgpt_bridge_v43 import get_provider_registry,ProviderRegistry
from chatgpt_bridge_v43 import chatgpt_connection_status,mark_delivered,revalidate_approval
from chatgpt_bridge_v43 import op_get_system_status,op_list_agent_capabilities
from chatgpt_bridge_v43 import op_start_workflow,op_get_workflow_status
from chatgpt_bridge_v43 import op_execute_authorized_step,op_resume_workflow
from chatgpt_bridge_v43 import op_get_agent_report,op_get_content_preview
from chatgpt_bridge_v43 import op_get_image_preview,op_validate_content
from chatgpt_bridge_v43 import op_validate_image,op_get_batch_report
from chatgpt_bridge_v43 import op_submit_owner_decision,op_get_audit_report
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.p=str(Path(self.tmp.name)/'state.json');start(self.p,{'content_id':'t1','topic':'Voice AI','mode':'TEST_FIXTURE'})
 def tearDown(self):self.tmp.cleanup()
 def test_first_stage(self):self.assertEqual(next_step(load(self.p))['stage'],'SOURCES')
 def test_out_of_order(self):
  with self.assertRaisesRegex(ValueError,'OUT_OF_ORDER'):submit(self.p,'CONTENT','writer','producer',{})
 def test_source_pass(self):
  r=submit(self.p,'SOURCES','search','producer',{'sources':[{'url':'https://example.org','verified_at':'fixture-only'}]})
  self.assertEqual(r['next']['stage'],'SOURCE_REVIEW')
 def test_missing_source_retries(self):
  r=submit(self.p,'SOURCES','search','producer',{'sources':[]})
  self.assertEqual(r['next']['stage'],'SOURCES');self.assertEqual(r['repairs'],1)
 def test_fourth_failure_blocks(self):
  for _ in range(4):r=submit(self.p,'SOURCES','search','producer',{'sources':[]})
  self.assertEqual(r['status'],'BLOCKED')
 def test_reviewer_requires_real_receipt(self):
  submit(self.p,'SOURCES','search','producer',{'sources':[{'url':'https://example.org','verified_at':'fixture-only'}]})
  r=submit(self.p,'SOURCE_REVIEW','reviewer','reviewer',{'upstream_hash':next_step(load(self.p))['upstream_hash'],'reviewer':'reviewer','decision':'PASS','observations':[]})
  self.assertEqual(r['last']['event'],'FAIL');self.assertEqual(r['next']['stage'],'SOURCES')
 def test_state_persistence(self):self.assertEqual(load(self.p)['job']['content_id'],'t1')

# ---------------------------------------------------------------------------
# Worker 1 additions: command parser / dispatch / provider registry /
# ChatGPT operations. All state lives in TemporaryDirectory; no real
# approval is ever created (TEST_ONLY fixture ledgers in temp dirs);
# providers are mocked (unittest.mock), no real network is used.
# ---------------------------------------------------------------------------

_TOPICS = ["Voice AI", "Automation", "SaaS growth", "AI receptionist",
           "Workflow automation", "Lead generation", "Customer support"]


def _restore_module(name, old):
    if old is None:
        sys.modules.pop(name, None)
    else:
        sys.modules[name] = old


def _install_fake_module(testcase, name, module):
    old = sys.modules.get(name)
    sys.modules[name] = module
    testcase.addCleanup(_restore_module, name, old)


class _FakeResponse:
    def __init__(self, body=b"hello", status=200):
        self._body = body
        self.status = status
    def read(self, n=-1):
        return self._body if n is None or n < 0 else self._body[:n]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


class _FakeLedger:
    """In-memory stand-in for evidence_store (Worker 3). TEST_ONLY."""
    def __init__(self):
        self.approvals = []
        self.events = []
    def init(self, path):
        return self
    def close(self):
        return None
    def record_event(self, db, job_id, kind, payload):
        self.events.append({"job_id": job_id, "kind": kind, "payload": payload})
        return "evt-%d" % len(self.events)
    def record_approval(self, db, job_id, content_id, content_hash, image_hash, actor, decision, scope="owner_review", reason=None):
        rec = {"approval_id": "appr-%d" % (len(self.approvals) + 1), "job_id": job_id, "content_id": content_id, "content_hash": content_hash, "image_hash": image_hash, "actor": actor, "decision": decision, "scope": scope, "reason": reason, "created_at": "2026-11-24T00:00:00+00:00", "record_hash": "rh", "prev_hash": "0"}
        self.approvals.append(rec)
        return rec
    def verify_approval(self, db, job_id, content_id, content_hash, image_hash):
        for rec in reversed(self.approvals):
            if rec["job_id"] == job_id and rec["content_id"] == content_id:
                if rec["decision"] == "APPROVE" and rec["content_hash"] == content_hash and rec["image_hash"] == image_hash:
                    return {"valid": True, "reason": "MATCH", "approval": rec}
                return {"valid": False, "reason": "HASH_OR_DECISION_MISMATCH", "approval": rec}
        return {"valid": False, "reason": "NO_APPROVAL", "approval": None}
    def latest_approval(self, db, job_id, content_id):
        for rec in reversed(self.approvals):
            if rec["job_id"] == job_id and rec["content_id"] == content_id:
                return rec
        return None
    def as_module(self):
        mod = types.ModuleType("evidence_store")
        for name in ("init", "close", "record_event", "record_approval", "verify_approval", "latest_approval"):
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


def _fake_batch_guard_module(with_run_job=True, with_registry=True, summary_error=None):
    mod = types.ModuleType("batch_guard_v45")
    mod.run_batch = _fake_run_batch
    if with_run_job:
        mod.run_job = _fake_run_job
    mod.verify_batch_strategy = lambda root, strategy: {"valid": True, "strategy": strategy}
    mod.check_duplicate_images = lambda root: {"duplicates": [], "count": 0}
    if summary_error is not None:
        def _summary(root):
            raise summary_error
        mod.summary = _summary
    else:
        mod.summary = lambda root: {"cycle": "C1", "expected": 7, "ready": 0, "batch_status": "NOT_APPROVED", "items": []}
    if with_registry:
        mod.AGENT_REGISTRY = {"AG-%02d" % i: {"role": "role-%02d" % i, "name": "Agent %02d" % i} for i in range(1, 19)}
    return mod


def _make_ready_state(path, content_id="ER-T-001"):
    """Synthetic TEST_ONLY job state in READY_FOR_OWNER_REVIEW.

    Fix-round 2026-11-24: DispatchTests/ChatGPTOpsTests setUp already
    creates the state file via start(), so re-calling start() here raised
    JOB_ALREADY_EXISTS (start()'s guard is correct and untouched).
    Reuse the existing state when the file is already there; only
    create it when it is missing. All 10 call sites use the same
    content_id the setUp created, so the loaded job matches.
    """
    if not Path(path).exists():
        start(path, {"content_id": content_id, "topic": "Voice AI", "mode": "LIVE"})
    state = load(path)
    state["index"] = 17
    state["status"] = "READY_FOR_OWNER_REVIEW"
    state["approval_status"] = "READY_FOR_OWNER_REVIEW"
    state["records"] = {
        "CONTENT": {"artifact": {"content_id": content_id, "caption": "Hello", "topic": "Voice AI"}, "hash": "c" * 64, "adapter": "writer"},
        "IMAGE_BUILD": {"artifact": {"content_id": content_id, "image_sha256": "i" * 64, "image_path": "/tmp/fake.png"}, "hash": "b" * 64, "adapter": "renderer"},
    }
    save(path, state)
    return state


class CommandParserTests(unittest.TestCase):
    def test_parse_canonical(self):
        out = parse_command("erudiance_linkdin start")
        self.assertTrue(out["ok"])
        self.assertEqual(out["command"], "erudiance_linkdin")
        self.assertEqual(out["action"], "START")
    def test_parse_alias(self):
        out = parse_command("erudience_linkdin status")
        self.assertTrue(out["ok"])
        self.assertEqual(out["command"], "erudiance_linkdin")
        self.assertEqual(out["command_word"], "erudience_linkdin")
        self.assertEqual(out["action"], "STATUS")
    def test_parse_at_erudience(self):
        out = parse_command("@Erudience status")
        self.assertTrue(out["ok"])
        self.assertEqual(out["action"], "STATUS")
        out = parse_command("@Erudience")
        self.assertTrue(out["ok"])
        self.assertEqual(out["action"], "START")
    def test_parse_flags(self):
        out = parse_command("erudiance_linkdin --test --single-content ER-001")
        self.assertTrue(out["ok"])
        self.assertTrue(out["flags"]["test"])
        self.assertEqual(out["flags"]["single_content"], "ER-001")
        self.assertEqual(out["args"]["content_id"], "ER-001")
        out = parse_command("erudiance_linkdin test --single-content=ER-002")
        self.assertEqual(out["flags"]["single_content"], "ER-002")
    def test_parse_unknown_command(self):
        for bad in ("", "   ", "do something", "erudiance_linkdin frobnicate", "hello world"):
            out = parse_command(bad)
            self.assertFalse(out["ok"], bad)
            self.assertEqual(out["error"], "UNKNOWN_COMMAND", bad)
    def test_parse_unknown_flag(self):
        out = parse_command("erudiance_linkdin start --bogus-flag x")
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "UNKNOWN_COMMAND")
    def test_parse_default_action(self):
        out = parse_command("erudiance_linkdin")
        self.assertTrue(out["ok"])
        self.assertEqual(out["action"], "START")


class AuthorizeTests(unittest.TestCase):
    def test_read_only_no_owner(self):
        for action in ("STATUS", "READ", "TEST", "VALIDATE"):
            allowed, _ = authorize(action, None)
            self.assertTrue(allowed, action)
    def test_operator_requires_identity(self):
        for action in ("START", "RESUME", "DO", "GO", "WRITE", "RETRY", "CANCEL", "OWNER_REVIEW"):
            allowed, reason = authorize(action, None)
            self.assertFalse(allowed, action)
            self.assertEqual(reason, "OPERATOR_IDENTITY_REQUIRED", action)
            allowed, _ = authorize(action, "op-1")
            self.assertTrue(allowed, action)
    def test_owner_requires_identity(self):
        for action in ("APPROVE", "REJECT"):
            allowed, reason = authorize(action, None)
            self.assertFalse(allowed, action)
            self.assertEqual(reason, "OWNER_IDENTITY_REQUIRED", action)
            allowed, _ = authorize(action, "owner-1")
            self.assertTrue(allowed, action)
    def test_unknown_action(self):
        allowed, reason = authorize("FROBNICATE", "owner-1")
        self.assertFalse(allowed)
        self.assertEqual(reason, "UNKNOWN_ACTION")


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state_path = str(self.root / "ER-T-001.json")
        start(self.state_path, {"content_id": "ER-T-001", "topic": "Voice AI", "mode": "TEST_FIXTURE"})
        self.ledger = _FakeLedger()
        _install_fake_module(self, "evidence_store", self.ledger.as_module())
        _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module())
    def tearDown(self):
        self.tmp.cleanup()
    def test_dispatch_start_happy(self):
        out = dispatch_command("erudiance_linkdin", {"action": "START", "topics": list(_TOPICS), "cycle": "C1"}, str(self.root), owner="op-1")
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["status"], "STARTED")
        self.assertTrue((self.root / "manifest.json").is_file())
        for i in range(1, 8):
            self.assertTrue((self.root / ("ER-C1-%03d.json" % i)).is_file())
    def test_dispatch_start_auto_topics(self):
        import importlib
        sys.modules.pop("batch_guard_v45", None)
        try:
            importlib.import_module("batch_guard_v45")
        except Exception as e:
            self.skipTest("real batch_guard_v45 not importable: %s" % e)
        try:
            out = dispatch_command("erudiance_linkdin", {"action": "START", "cycle": "C1"}, str(self.root), owner="op-1")
        finally:
            _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module())
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["status"], "STARTED")
        self.assertTrue((self.root / "manifest.json").is_file())
        for i in range(1, 8):
            self.assertTrue((self.root / ("ER-C1-%03d.json" % i)).is_file())
    def test_dispatch_start_bad_topics(self):
        out = dispatch_command("erudiance_linkdin", {"action": "START", "topics": ["only", "two"], "cycle": "C1"}, str(self.root), owner="op-1")
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "INVALID_INPUT")
    def test_dispatch_start_no_operator(self):
        out = dispatch_command("erudiance_linkdin", {"action": "START", "topics": list(_TOPICS), "cycle": "C1"}, str(self.root), owner=None)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "UNAUTHORIZED")
    def test_dispatch_status_job(self):
        out = dispatch_command("erudiance_linkdin", {"action": "STATUS", "content_id": "ER-T-001"}, str(self.root))
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["result"]["status"], "AWAITING_TOOL_EXECUTION")
        self.assertEqual(out["result"]["approval_status"], "DRAFT")
    def test_dispatch_test_happy(self):
        out = dispatch_command("erudiance_linkdin", {"action": "TEST", "single_content": "ER-T-001"}, str(self.root))
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["status"], "TEST_FIXTURE_PASS")
    def test_dispatch_test_missing_run_job(self):
        _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module(with_run_job=False))
        out = dispatch_command("erudiance_linkdin", {"action": "TEST", "single_content": "ER-T-001"}, str(self.root))
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "MISSING_ORCHESTRATOR_FUNCTION")
        self.assertIn("run_job", out["message"])
    def test_dispatch_test_real_run_job_if_available(self):
        import importlib
        sys.modules.pop("batch_guard_v45", None)
        try:
            real = importlib.import_module("batch_guard_v45")
        except Exception as e:
            self.skipTest("real batch_guard_v45 not importable: %s" % e)
        if not callable(getattr(real, "run_job", None)):
            self.skipTest("real batch_guard_v45.run_job not implemented yet (Worker 2)")
        out = dispatch_command("erudiance_linkdin", {"action": "TEST", "single_content": "ER-T-001"}, str(self.root))
        self.assertIsInstance(out, dict)
        self.assertNotEqual(out.get("error"), "MISSING_ORCHESTRATOR_FUNCTION")
    def test_dispatch_go_never_approves(self):
        out = dispatch_command("erudiance_linkdin", {"action": "GO", "content_id": "ER-T-001"}, str(self.root), owner="op-1")
        self.assertTrue(out["ok"], out)
        self.assertNotEqual(load(self.state_path).get("approval_status"), "OWNER_APPROVED")
        self.assertEqual(load(self.state_path).get("approval_status"), "DRAFT")
    def test_dispatch_do_never_approves(self):
        out = dispatch_command("erudiance_linkdin", {"action": "DO", "step": "validate_job", "content_id": "ER-T-001"}, str(self.root), owner="op-1")
        self.assertTrue(out["ok"], out)
        self.assertFalse(out["result"]["approval_changed"])
        self.assertEqual(load(self.state_path).get("approval_status"), "DRAFT")
    def test_dispatch_read_rejects_traversal(self):
        for bad in ("../../etc/passwd", "/etc/passwd", "../secret.txt"):
            out = dispatch_command("erudiance_linkdin", {"action": "READ", "path": bad}, str(self.root))
            self.assertFalse(out["ok"], bad)
            self.assertEqual(out["error"], "PATH_NOT_ALLOWED", bad)
    def test_dispatch_read_allowed(self):
        target = self.root / "note.txt"
        target.write_text("hello", encoding="utf8")
        out = dispatch_command("erudiance_linkdin", {"action": "READ", "path": str(target)}, str(self.root))
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["result"]["content"], "hello")
    def test_dispatch_approve_no_owner(self):
        out = dispatch_command("erudiance_linkdin", {"action": "APPROVE", "content_id": "ER-T-001"}, str(self.root), owner=None)
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "UNAUTHORIZED")
    def test_dispatch_approve_not_ready(self):
        out = dispatch_command("erudiance_linkdin", {"action": "APPROVE", "content_id": "ER-T-001"}, str(self.root), owner="owner-1")
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "JOB_NOT_READY_FOR_OWNER_REVIEW")
    def test_dispatch_approve_happy(self):
        _make_ready_state(self.state_path)
        out = dispatch_command("erudiance_linkdin", {"action": "APPROVE", "content_id": "ER-T-001", "reason": "looks good"}, str(self.root), owner="owner-1")
        self.assertTrue(out["ok"], out)
        self.assertEqual(load(self.state_path)["approval_status"], "OWNER_APPROVED")
        self.assertEqual(len(self.ledger.approvals), 1)
    def test_dispatch_reject_happy(self):
        _make_ready_state(self.state_path)
        out = dispatch_command("erudiance_linkdin", {"action": "REJECT", "content_id": "ER-T-001", "reason": "not yet"}, str(self.root), owner="owner-1")
        self.assertTrue(out["ok"], out)
        self.assertEqual(load(self.state_path)["approval_status"], "OWNER_REJECTED")
    def test_dispatch_cancel(self):
        out = dispatch_command("erudiance_linkdin", {"action": "CANCEL", "content_id": "ER-T-001"}, str(self.root), owner="op-1")
        self.assertTrue(out["ok"], out)
        self.assertEqual(load(self.state_path)["status"], "CANCELLED")
        self.assertTrue(Path(self.state_path).is_file())
    def test_dispatch_validate_fresh(self):
        out = dispatch_command("erudiance_linkdin", {"action": "VALIDATE", "content_id": "ER-T-001"}, str(self.root))
        self.assertTrue(out["ok"], out)
        self.assertTrue(out["result"]["valid"])
        self.assertFalse(out["result"]["advanced"])
    def test_dispatch_retry_rewinds_blocked(self):
        for _ in range(4):
            submit(self.state_path, "SOURCES", "search", "producer", {"sources": []})
        self.assertEqual(load(self.state_path)["status"], "BLOCKED")
        out = dispatch_command("erudiance_linkdin", {"action": "RETRY", "content_id": "ER-T-001"}, str(self.root), owner="op-1")
        self.assertTrue(out["ok"], out)
        state = load(self.state_path)
        self.assertEqual(state["status"], "AWAITING_TOOL_EXECUTION")
        self.assertEqual(state["repairs"], 0)
    def test_dispatch_unknown_never_raises(self):
        out = dispatch_command("nonsense_command", {}, str(self.root))
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "UNKNOWN_COMMAND")
        out = dispatch_command(None, None, str(self.root))
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "UNKNOWN_COMMAND")
    def test_dispatch_write_draft_ok(self):
        out = dispatch_command("erudiance_linkdin", {"action": "WRITE", "path": "drafts/note.txt", "content": "draft"}, str(self.root), owner="op-1")
        self.assertTrue(out["ok"], out)
        self.assertEqual((self.root / "drafts" / "note.txt").read_text(encoding="utf8"), "draft")
    def test_dispatch_write_protected(self):
        for bad in ("evidence.db", "manifest.json", "evil.py", "../escape.txt"):
            out = dispatch_command("erudiance_linkdin", {"action": "WRITE", "path": bad, "content": "x"}, str(self.root), owner="op-1")
            self.assertFalse(out["ok"], bad)
            self.assertIn(out["error"], ("PROTECTED_FILE", "PATH_NOT_ALLOWED"), bad)


class ProviderRegistryTests(unittest.TestCase):
    def test_default_not_configured(self):
        reg = ProviderRegistry()
        self.assertEqual(reg.provider_status("anything"), "NOT_CONFIGURED")
        out = reg.fetch_source("https://example.org/page", provider=None)
        self.assertEqual(out["status"], "NOT_CONFIGURED")
        self.assertIsNone(out["sha256"])
        self.assertIsNone(out["retrieved_at"])
    def test_register_and_validate_unset_env(self):
        reg = ProviderRegistry()
        out = reg.register_provider("search", "research", base_url="https://example.org", credential_env="ERUDIANCE_TEST_MISSING_ENV_VAR_XYZ")
        self.assertTrue(out["ok"])
        self.assertEqual(reg.provider_status("search"), "NOT_CONFIGURED")
        cred = reg.validate_credentials("search")
        self.assertFalse(cred["credential_present"])
        self.assertFalse(cred["ok"])
        self.assertEqual(cred["status"], "NOT_CONFIGURED")
        self.assertEqual(set(cred.keys()), {"ok", "name", "status", "credential_env", "credential_present", "error"})
    def test_fetch_live_verified_mocked(self):
        reg = ProviderRegistry()
        with mock.patch.dict(os.environ, {"ERUDIANCE_TEST_FAKE_KEY": "fake-value"}):
            reg.register_provider("prov-live", "research", base_url="https://example.org", credential_env="ERUDIANCE_TEST_FAKE_KEY")
            self.assertEqual(reg.provider_status("prov-live"), "CONFIGURED")
            with mock.patch("urllib.request.urlopen", return_value=_FakeResponse(b"hello")):
                out = reg.fetch_source("https://example.org/page", provider="prov-live")
        self.assertEqual(out["status"], "LIVE_VERIFIED")
        self.assertEqual(out["sha256"], hashlib.sha256(b"hello").hexdigest())
        self.assertIsNotNone(out["retrieved_at"])
    def test_fetch_rate_limited(self):
        reg = ProviderRegistry()
        with mock.patch.dict(os.environ, {"ERUDIANCE_TEST_FAKE_KEY2": "x"}):
            reg.register_provider("prov-rl", "research", base_url="https://example.org", credential_env="ERUDIANCE_TEST_FAKE_KEY2")
            with mock.patch("urllib.request.urlopen", return_value=_FakeResponse(b"hello")):
                results = [reg.fetch_source("https://example.org/p", provider="prov-rl") for _ in range(11)]
        self.assertEqual([r["status"] for r in results[:10]], ["LIVE_VERIFIED"] * 10)
        self.assertEqual(results[10]["status"], "ERROR")
        self.assertEqual(results[10]["error"], "RATE_LIMITED")
    def test_fetch_429_rate_limited(self):
        reg = ProviderRegistry()
        with mock.patch.dict(os.environ, {"ERUDIANCE_TEST_FAKE_KEY3": "x"}):
            reg.register_provider("prov-429", "research", base_url="https://example.org", credential_env="ERUDIANCE_TEST_FAKE_KEY3")
            err = urllib.error.HTTPError("https://example.org/p", 429, "Too Many Requests", {}, None)
            with mock.patch("urllib.request.urlopen", side_effect=err):
                out = reg.fetch_source("https://example.org/p", provider="prov-429")
        self.assertEqual(out["status"], "ERROR")
        self.assertEqual(out["error"], "RATE_LIMITED")
    def test_fetch_network_error(self):
        reg = ProviderRegistry()
        with mock.patch.dict(os.environ, {"ERUDIANCE_TEST_FAKE_KEY4": "x"}):
            reg.register_provider("prov-net", "research", base_url="https://example.org", credential_env="ERUDIANCE_TEST_FAKE_KEY4")
            with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("boom")):
                out = reg.fetch_source("https://example.org/p", provider="prov-net")
        self.assertEqual(out["status"], "ERROR")
        self.assertEqual(out["error"], "NETWORK_ERROR")
    def test_list_providers_no_values(self):
        reg = ProviderRegistry()
        with mock.patch.dict(os.environ, {"ERUDIANCE_TEST_FAKE_KEY5": "super-secret-value"}):
            reg.register_provider("prov-list", "llm", base_url="https://example.org", credential_env="ERUDIANCE_TEST_FAKE_KEY5")
            listed = reg.list_providers()
        self.assertEqual(listed["providers"]["prov-list"]["status"], "CONFIGURED")
        self.assertNotIn("super-secret-value", json.dumps(listed))
    def test_singleton(self):
        self.assertIs(get_provider_registry(), get_provider_registry())


class ChatGPTOpsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state_path = str(self.root / "ER-T-001.json")
        start(self.state_path, {"content_id": "ER-T-001", "topic": "Voice AI", "mode": "TEST_FIXTURE"})
        self.ledger = _FakeLedger()
        _install_fake_module(self, "evidence_store", self.ledger.as_module())
        _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module())
    def tearDown(self):
        self.tmp.cleanup()
    def test_get_system_status_honesty(self):
        out = op_get_system_status({})
        self.assertTrue(out["ok"])
        self.assertFalse(out["chatgpt"]["connected"])
        self.assertIn("Owner-side", out["chatgpt"]["blocker"])
        self.assertTrue(out["approval"]["required"])
        self.assertIn("READY_FOR_OWNER_REVIEW", out["approval"]["states"])
        self.assertEqual(out["stage_count"], 17)
    def test_chatgpt_connection_status(self):
        out = chatgpt_connection_status()
        self.assertFalse(out["connected"])
        self.assertIn("no live ChatGPT-to-ERUDIANCE request has succeeded", out["blocker"])
    def test_list_agent_capabilities(self):
        out = op_list_agent_capabilities({})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["count"], 18)
        self.assertEqual(len(out["agents"]), 18)
    def test_list_agent_capabilities_missing(self):
        _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module(with_registry=False))
        out = op_list_agent_capabilities({})
        self.assertFalse(out["ok"])
        self.assertIn("AGENT_REGISTRY", out["message"])
    def test_ops_invalid_input(self):
        ops = [op_start_workflow, op_get_workflow_status, op_execute_authorized_step, op_resume_workflow, op_get_agent_report, op_get_content_preview, op_get_image_preview, op_validate_content, op_validate_image, op_get_batch_report, op_submit_owner_decision, op_get_audit_report]
        for fn in ops:
            with self.subTest(op=fn.__name__):
                out = fn({})
                self.assertFalse(out["ok"], fn.__name__)
                self.assertEqual(out["error"], "INVALID_INPUT", fn.__name__)
    def test_ops_unauthorized(self):
        out = op_start_workflow({"topics": list(_TOPICS), "cycle": "C1", "state_dir": str(self.root), "operator": "  "})
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "UNAUTHORIZED")
        out = op_execute_authorized_step({"state_dir": str(self.root), "step": "validate_job", "content_id": "ER-T-001", "operator": ""})
        self.assertEqual(out["error"], "UNAUTHORIZED")
        out = op_submit_owner_decision({"owner": "", "content_id": "ER-T-001", "decision": "APPROVE", "state_dir": str(self.root)})
        self.assertEqual(out["error"], "UNAUTHORIZED")
        out = op_resume_workflow({"state_dir": str(self.root), "content_id": "ER-T-001", "operator": None})
        self.assertEqual(out["error"], "INVALID_INPUT")
    def test_op_start_workflow(self):
        out = op_start_workflow({"topics": list(_TOPICS), "cycle": "C1", "state_dir": str(self.root), "operator": "op-1"})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["operation"], "start_workflow")
        self.assertTrue((self.root / "manifest.json").is_file())
    def test_op_start_workflow_auto_topics(self):
        import importlib
        sys.modules.pop("batch_guard_v45", None)
        try:
            importlib.import_module("batch_guard_v45")
        except Exception as e:
            self.skipTest("real batch_guard_v45 not importable: %s" % e)
        try:
            out = op_start_workflow({"cycle": "C1", "state_dir": str(self.root), "operator": "op-1"})
        finally:
            _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module())
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["operation"], "start_workflow")
        self.assertTrue((self.root / "manifest.json").is_file())
    def test_op_get_workflow_status(self):
        out = op_get_workflow_status({"state_dir": str(self.root), "content_id": "ER-T-001"})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["result"]["approval_status"], "DRAFT")
    def test_op_resume_workflow(self):
        out = op_resume_workflow({"state_dir": str(self.root), "content_id": "ER-T-001", "operator": "op-1"})
        self.assertTrue(out["ok"], out)
    def test_op_execute_authorized_step(self):
        out = op_execute_authorized_step({"state_dir": str(self.root), "content_id": "ER-T-001", "step": "validate_job", "operator": "op-1"})
        self.assertTrue(out["ok"], out)
        self.assertFalse(out["result"]["approval_changed"])
    def test_op_get_agent_report_job(self):
        out = op_get_agent_report({"state_dir": str(self.root), "content_id": "ER-T-001"})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["status"], "AWAITING_TOOL_EXECUTION")
    def test_op_get_batch_report(self):
        out = op_get_batch_report({"state_dir": str(self.root)})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["report"]["batch_status"], "NOT_APPROVED")
    def test_op_get_batch_report_missing(self):
        _install_fake_module(self, "batch_guard_v45", _fake_batch_guard_module(summary_error=FileNotFoundError("no manifest")))
        out = op_get_batch_report({"state_dir": str(self.root)})
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "BATCH_NOT_FOUND")
    def test_submit_owner_decision_happy(self):
        _make_ready_state(self.state_path)
        out = op_submit_owner_decision({"owner": "owner-1", "content_id": "ER-T-001", "decision": "APPROVE", "reason": "good", "state_dir": str(self.root)})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["approval_status"], "OWNER_APPROVED")
        self.assertTrue(out["verified"])
        self.assertIsNotNone(out["approval_id"])
        self.assertEqual(load(self.state_path)["approval_status"], "OWNER_APPROVED")
    def test_submit_owner_decision_reject(self):
        _make_ready_state(self.state_path)
        out = op_submit_owner_decision({"owner": "owner-1", "content_id": "ER-T-001", "decision": "REJECT", "state_dir": str(self.root)})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["approval_status"], "OWNER_REJECTED")
        self.assertEqual(load(self.state_path)["approval_status"], "OWNER_REJECTED")
    def test_submit_owner_decision_not_ready(self):
        out = op_submit_owner_decision({"owner": "owner-1", "content_id": "ER-T-001", "decision": "APPROVE", "state_dir": str(self.root)})
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "JOB_NOT_READY_FOR_OWNER_REVIEW")
        self.assertEqual(load(self.state_path)["approval_status"], "DRAFT")
    def test_submit_owner_decision_missing_ledger_function(self):
        _make_ready_state(self.state_path)
        bare = types.ModuleType("evidence_store")
        bare.init = lambda path: None
        _install_fake_module(self, "evidence_store", bare)
        out = op_submit_owner_decision({"owner": "owner-1", "content_id": "ER-T-001", "decision": "APPROVE", "state_dir": str(self.root)})
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "MISSING_EVIDENCE_FUNCTION")
        self.assertIn("record_approval", out["message"])
        self.assertEqual(load(self.state_path)["approval_status"], "READY_FOR_OWNER_REVIEW")
    def test_mark_delivered(self):
        _make_ready_state(self.state_path)
        op_submit_owner_decision({"owner": "owner-1", "content_id": "ER-T-001", "decision": "APPROVE", "state_dir": str(self.root)})
        out = mark_delivered(self.state_path, "owner-1")
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["approval_status"], "DELIVERED")
        self.assertEqual(load(self.state_path)["approval_status"], "DELIVERED")
    def test_mark_delivered_not_approved(self):
        out = mark_delivered(self.state_path, "owner-1")
        self.assertFalse(out["ok"])
        self.assertEqual(load(self.state_path)["approval_status"], "DRAFT")
    def test_revalidate_valid(self):
        _make_ready_state(self.state_path)
        op_submit_owner_decision({"owner": "owner-1", "content_id": "ER-T-001", "decision": "APPROVE", "state_dir": str(self.root)})
        out = revalidate_approval(self.state_path)
        self.assertTrue(out["ok"], out)
        self.assertTrue(out["valid"])
        self.assertEqual(out["approval_status"], "OWNER_APPROVED")
    def test_revalidate_invalid_resets(self):
        _make_ready_state(self.state_path)
        op_submit_owner_decision({"owner": "owner-1", "content_id": "ER-T-001", "decision": "APPROVE", "state_dir": str(self.root)})
        state = load(self.state_path)
        state["records"]["IMAGE_BUILD"]["artifact"]["image_sha256"] = "0" * 64
        save(self.state_path, state)
        out = revalidate_approval(self.state_path)
        self.assertTrue(out["ok"], out)
        self.assertFalse(out["valid"])
        self.assertEqual(out["approval_status"], "READY_FOR_OWNER_REVIEW")
        self.assertEqual(load(self.state_path)["approval_status"], "READY_FOR_OWNER_REVIEW")
    def test_validate_content_op(self):
        item = {"content_id": "ER-T-001", "publish_date": "2026-11-24", "platforms": ["linkedin"], "topic": "Voice AI", "title": "T", "pillar": "automation", "funnel_stage": "awareness", "primary_format": "text", "derivatives": [], "keywords": ["voice"], "buyer_pain": "missed calls", "cta": "Learn more", "sources": [{"source_id": "s1", "url": "https://example.org", "retrieved_at": "2026-11-24"}], "claims": [{"text": "c", "source_ids": ["s1"]}], "copy": "Hello", "brand_id": "erudience"}
        out = op_validate_content({"item": item, "artifacts": {}})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["decision"], "BLOCKED")
        self.assertEqual(out["reason"], "BRAND_NOT_VERIFIED")
        out = op_validate_content({"item": item, "artifacts": {"brand_verified": True, "creative_brief_hash": "x", "prompt_hash": "y", "visual_qa_pass": True}})
        self.assertTrue(out["ok"], out)
        self.assertEqual(out["decision"], "READY_FOR_OWNER_REVIEW")
    def test_validate_image_op_missing_inspector(self):
        bare = types.ModuleType("verify_output")
        _install_fake_module(self, "verify_output", bare)
        out = op_validate_image({"image_path": "/tmp/does-not-exist.png"})
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "MISSING_VALIDATOR")
        self.assertIn("inspect_image", out["message"])
    def test_validate_image_op_with_fake_inspector(self):
        mod = types.ModuleType("verify_output")
        mod.inspect_image = lambda path: {"verdict": "PASS_MECHANICAL_ONLY", "path": path}
        _install_fake_module(self, "verify_output", mod)
        out = op_validate_image({"image_path": "/tmp/fake.png"})
        self.assertTrue(out["ok"], out)
        self.assertFalse(out["visually_verified"])
        self.assertEqual(out["inspection"]["verdict"], "PASS_MECHANICAL_ONLY")
    def test_get_audit_report_no_ledger(self):
        out = op_get_audit_report({"state_dir": str(self.root)})
        self.assertTrue(out["ok"], out)
        self.assertFalse(out["ledger"]["exists"])
        self.assertEqual(len(out["states"]), 1)
        self.assertFalse(out["chatgpt"]["connected"])
    def test_get_content_preview(self):
        _make_ready_state(self.state_path)
        out = op_get_content_preview({"state_dir": str(self.root), "content_id": "ER-T-001"})
        self.assertTrue(out["ok"], out)
        self.assertFalse(out["visually_verified"])
        self.assertEqual(out["content_hash"], "c" * 64)
        self.assertEqual(out["image_sha256"], "i" * 64)
    def test_get_image_preview(self):
        _make_ready_state(self.state_path)
        out = op_get_image_preview({"state_dir": str(self.root), "content_id": "ER-T-001"})
        self.assertTrue(out["ok"], out)
        self.assertFalse(out["visually_verified"])
        self.assertEqual(out["image_sha256"], "i" * 64)

class SubmitApprovalStatusTests(unittest.TestCase):
 """W1-CONSISTENCY regression (2026-11-24): a TEST_FIXTURE chain completion
 must NOT become READY_FOR_OWNER_REVIEW. Only a live completion may be
 approved via op_submit_owner_decision. Drives submit() through all 17
 stages with the same fixture artifacts as GateTests."""
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  self.png=str(self.root/'image.png');Image.new('RGB',(1080,1350)).save(self.png)
  self.job={'content_id':'ER-T-001','topic':'Voice AI','mode':'TEST_FIXTURE'}
  self.state_path=str(self.root/'ER-T-001.json')
  start(self.state_path,self.job)
 def _artifact(self,stage,records):
  prev=STAGES[STAGES.index(stage)-1] if stage!='SOURCES' else None
  upstream={'upstream_hash':records[prev]['hash']} if prev else {}
  if stage=='SOURCES':return {'sources':[{'url':'https://example.org','verified_at':'fixture-only'}]}
  if stage=='CONTENT':return dict(upstream,content_id=self.job['content_id'],topic=self.job['topic'],caption='Voice AI for small business.',keywords=['voice AI'])
  if stage=='IMAGE_PLAN':return dict(upstream,content_id=self.job['content_id'],topic=self.job['topic'],caption=records['CONTENT']['artifact']['caption'],content_hash=records['CONTENT']['hash'],poster_text={'headline':'Five call handling steps','steps':['answer','capture','respond','route','follow up'],'footer':'Erudience erudience.com'},dimensions=[1080,1350],brand=BRAND,design_rationale='Five-step workflow',negative_constraints=['no robots'],template_id='website',positioning='business automation',funnel_stage='awareness')
  if stage=='IMAGE_BUILD':return dict(upstream,content_id=self.job['content_id'],plan_hash=records['IMAGE_PLAN']['hash'],image_path=self.png,image_sha256=filehash(self.png),copy_ledger_hash=digest(records['IMAGE_PLAN']['artifact']['poster_text']),font_provenance={'Sora':'fixture-hash'},copy_rendered=True)
  if stage in REVIEWS:
   out=dict(upstream,decision='PASS',reviewer='review-'+stage,observations=['Fixture reviewer assertion'],subject_hash=records[prev]['hash'])
   if stage in ('VISUAL_REVIEW','CONTENT_IMAGE_REVIEW','BRAND_REVIEW','FINAL_REVIEW'):out.update(image_sha256=filehash(self.png),plan_hash=records['IMAGE_PLAN']['hash'])
   if stage=='VISUAL_REVIEW':out.update(pixel_inspection=True,mobile_inspection=True)
   if stage=='CONTENT_IMAGE_REVIEW':out.update(topic_match=True,text_match=True)
   if stage=='BRAND_REVIEW':out.update(font_files_checked=True,palette_checked=True,footer_checked=True,logo_absence_checked=True,positioning_checked=True)
   return out
  if stage=='DELIVERY':return dict(upstream,image_sha256=filehash(self.png))
  return dict(upstream,evidence='fixture')
 def _drive(self):
  for stage in STAGES:
   records=load(self.state_path)['records']
   name=('review-'+stage) if stage in REVIEWS else ('build' if stage=='IMAGE_BUILD' else 'produce-'+stage)
   role='reviewer' if stage in REVIEWS else 'producer'
   out=submit(self.state_path,stage,name,role,self._artifact(stage,records))
   self.assertEqual(out['last']['event'],'PASS',out)
  return load(self.state_path)
 def test_fixture_completion_is_not_owner_reviewable(self):
  state=self._drive()
  self.assertEqual(state['status'],'TEST_FIXTURE_PASS')
  self.assertEqual(state['approval_status'],'IN_PROGRESS')
  self.assertNotEqual(state['approval_status'],'READY_FOR_OWNER_REVIEW')

if __name__=='__main__':unittest.main()
