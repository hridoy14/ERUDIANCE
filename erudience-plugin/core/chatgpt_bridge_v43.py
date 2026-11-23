"""ChatGPT tool handoff: durable, fail-closed 17-stage checkpoint controller.
Tools execute OUTSIDE this process; evidence receipts must be submitted back. No fake providers.

Command engine (v4.9.2 repair): the documented command words
``erudiance_linkdin`` (canonical), ``erudience_linkdin`` (legacy alias)
and ``@Erudience`` are now real, parsed by parse_command() and routed by
dispatch_command(). GO/DO never approve or publish; approval is only via
an explicit owner decision (op_submit_owner_decision) on a job in
READY_FOR_OWNER_REVIEW, recorded in the local evidence ledger.

No live ChatGPT connection: nothing in this module opens a ChatGPT
session. chatgpt_connection_status() always reports connected=False
until an owner installs/hosts and authenticates a ChatGPT integration.
"""
import argparse,json,os,shlex,socket,sqlite3,sys,tempfile,time
import urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from hashlib import sha256
from gate_chain_v41 import STAGES,REPAIR,Adapter,Chain,digest,GateFailure

def save(path,state):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile('w',dir=p.parent,delete=False,encoding='utf8') as f:
  json.dump(state,f,indent=2,ensure_ascii=False);tmp=f.name
 os.replace(tmp,p)
def load(path):return json.loads(Path(path).read_text(encoding='utf8'))
def start(path,job):
 if Path(path).exists():raise ValueError('JOB_ALREADY_EXISTS')
 if not job.get('content_id') or not job.get('topic'):raise ValueError('JOB_REQUIRED')
 state={'schema':'erudience.chatgpt.v4.3','job':job,'index':0,'records':{},'trace':[],'repairs':0,'status':'AWAITING_TOOL_EXECUTION','external_writes':0,'approval_status':'DRAFT'}
 save(path,state);return state
def next_step(state):
 if state['status']!='AWAITING_TOOL_EXECUTION':return {'status':state['status']}
 stage=STAGES[state['index']];previous=STAGES[state['index']-1] if state['index'] else None
 return {'status':state['status'],'stage':stage,'requires_independent_reviewer':stage.endswith('REVIEW'),'upstream_hash':state['records'][previous]['hash'] if previous else None,'content_hash':state['records'].get('CONTENT',{}).get('hash'),'plan_hash':state['records'].get('IMAGE_PLAN',{}).get('hash'),'image_sha256':state['records'].get('IMAGE_BUILD',{}).get('artifact',{}).get('image_sha256')}
def submit(path,stage,adapter_name,role,artifact):
 state=load(path)
 if state['status']!='AWAITING_TOOL_EXECUTION':raise ValueError('JOB_NOT_ACCEPTING_RECEIPTS')
 if STAGES[state['index']]!=stage:raise ValueError('OUT_OF_ORDER_STAGE')
 # Reuse the same production gate validators as the synchronous controller.
 c=Chain(state['job'],{},limit=3);c.records=state['records']
 try:
  c.verify(stage,artifact,Adapter(adapter_name,lambda *_:artifact,role))
  h=digest(artifact);state['records'][stage]={'artifact':artifact,'hash':h,'adapter':adapter_name}
  state['trace'].append({'stage':stage,'event':'PASS','sha256':h});state['index']+=1
  if state.get('approval_status') in (None,'DRAFT'):state['approval_status']='IN_PROGRESS'
  if state['index']==len(STAGES):
   state['status']='TEST_FIXTURE_PASS' if state['job'].get('mode')=='TEST_FIXTURE' else 'READY_FOR_OWNER_REVIEW'
   # W1-CONSISTENCY fix (2026-11-24): a fixture completion is not
   # owner-reviewable. Only a live READY_FOR_OWNER_REVIEW completion
   # may be approved via op_submit_owner_decision.
   if state['status']=='READY_FOR_OWNER_REVIEW':state['approval_status']='READY_FOR_OWNER_REVIEW'
 except Exception as e:
  target=e.repair_at if isinstance(e,GateFailure) and e.repair_at in STAGES and STAGES.index(e.repair_at)<=state['index'] else REPAIR[stage]
  state['repairs']+=1;state['trace'].append({'stage':stage,'event':'FAIL','reason':str(e),'return_to':target,'repair':state['repairs']})
  if state['repairs']>3:state['status']='BLOCKED'
  else:
   for s in STAGES[STAGES.index(target):]:state['records'].pop(s,None)
   state['index']=STAGES.index(target)
 save(path,state);return {'status':state['status'],'next':next_step(state),'repairs':state['repairs'],'last':state['trace'][-1]}
# ---------------------------------------------------------------------------
# Command engine, provider-neutral registry and ChatGPT operations.
# Worker 1, v4.9.2 one-pass repair. All additions are additive: the
# original start/next_step/submit/load/save functions above are unchanged
# except that start()/submit() now also maintain state['approval_status'].
#
# Circular-import rule: core/batch_guard_v45.py imports this module at
# top level, so this file MUST NOT import batch_guard_v45 (or
# evidence_store / verify_output / content_engine) at module top level.
# Those modules are imported lazily INSIDE the functions that need them.
# ---------------------------------------------------------------------------

BRIDGE_VERSION = "v43"
GATE_VERSION = "v41"
BATCH_VERSION = "v45"
PLUGIN_VERSION = "4.9.2"

CHATGPT_CONNECTION_BLOCKER = (
    "Owner-side ChatGPT installation/hosting/auth required; "
    "no live ChatGPT-to-ERUDIANCE request has succeeded."
)

# Canonical command word is "erudiance_linkdin" (audit D-27 / C20: the
# "erudience" spelling is a legacy alias, kept working, never canonical).
COMMAND_WORDS = ("erudiance_linkdin", "erudience_linkdin", "@Erudience")
CANONICAL_COMMAND = "erudiance_linkdin"

READ_ONLY_ACTIONS = ("STATUS", "READ", "TEST", "VALIDATE")
OPERATOR_ACTIONS = ("START", "RESUME", "DO", "GO", "WRITE", "RETRY", "CANCEL", "OWNER_REVIEW")
OWNER_ACTIONS = ("APPROVE", "REJECT")
ALL_ACTIONS = READ_ONLY_ACTIONS + OPERATOR_ACTIONS + OWNER_ACTIONS

APPROVAL_STATES = ("DRAFT", "IN_PROGRESS", "READY_FOR_OWNER_REVIEW",
                   "OWNER_APPROVED", "OWNER_REJECTED", "DELIVERED")

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PLUGIN_ROOT / "assets"

MAX_REPAIRS = 3
FETCH_RATE_LIMIT_PER_MINUTE = 10
FETCH_MAX_BYTES = 5 * 1024 * 1024
READ_MAX_BYTES = 5 * 1024 * 1024
READ_MAX_CHARS = 200000


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _trace_event(action, event, detail=None):
    entry = {"action": action, "event": event, "at": _now_iso()}
    if detail is not None:
        entry["detail"] = detail
    return entry


def _result(command, action, status, result, error, message, trace):
    return {"ok": error is None, "command": command, "action": action,
            "status": status, "result": result, "error": error,
            "message": message, "trace": trace}


def _audit_event(state_dir, job_id, kind, payload):
    """Best-effort append to the local evidence ledger.

    Returns {"ledger": "recorded"|"unavailable", ...}. The ledger is the
    local SQLite file <state_dir>/evidence.db, written via
    evidence_store.record_event (Worker 3). If that function is not
    present yet the miss is reported honestly in the returned dict and
    in the dispatch trace instead of failing the workflow or
    fabricating a ledger record.
    """
    try:
        import evidence_store
    except Exception as e:
        return {"ledger": "unavailable",
                "reason": "EVIDENCE_STORE_IMPORT_FAILED: %s" % e}
    record_event = getattr(evidence_store, "record_event", None)
    init = getattr(evidence_store, "init", None)
    if record_event is None:
        return {"ledger": "unavailable",
                "reason": "MISSING_EVIDENCE_FUNCTION: record_event"}
    if init is None:
        return {"ledger": "unavailable",
                "reason": "MISSING_EVIDENCE_FUNCTION: init"}
    db = None
    try:
        db = init(str(Path(state_dir) / "evidence.db"))
        event_id = record_event(db, job_id, kind, payload)
        return {"ledger": "recorded", "event_id": event_id}
    except Exception as e:
        return {"ledger": "unavailable",
                "reason": "EVIDENCE_WRITE_FAILED: %s" % e}
    finally:
        try:
            if db is not None:
                db.close()
        except Exception:
            pass


def _load_orchestrator_function(name):
    """Lazily import one orchestrator function from batch_guard_v45.

    Returns (func, error_dict|None). Fails LOUDLY (error dict naming
    the missing function) instead of silently falling back to a fake
    success. The import is lazy because batch_guard_v45 imports this
    module at top level; a top-level import here would be circular.
    """
    try:
        import batch_guard_v45
    except Exception as e:
        return None, {"error": "MISSING_ORCHESTRATOR_MODULE",
                      "message": "batch_guard_v45 could not be imported: %s" % e}
    func = getattr(batch_guard_v45, name, None)
    if func is None or not callable(func):
        return None, {"error": "MISSING_ORCHESTRATOR_FUNCTION",
                      "message": "batch_guard_v45.%s is not implemented yet "
                      "(Worker 2); refusing to fake success" % name}
    return func, None


def _load_evidence_function(name):
    """Lazily import one evidence-ledger function from evidence_store.

    Returns (func, error_dict|None). Fails LOUDLY naming the missing
    function instead of fabricating an approval or audit record.
    """
    try:
        import evidence_store
    except Exception as e:
        return None, {"error": "MISSING_EVIDENCE_MODULE",
                      "message": "evidence_store could not be imported: %s" % e}
    func = getattr(evidence_store, name, None)
    if func is None or not callable(func):
        return None, {"error": "MISSING_EVIDENCE_FUNCTION",
                      "message": "evidence_store.%s is not implemented yet "
                      "(Worker 3); refusing to fake an approval record" % name}
    return func, None


def authorize(action, owner):
    """Return (allowed: bool, reason: str).

    Read-only actions (STATUS, READ, TEST, VALIDATE) need no identity.
    State-changing workflow actions need an operator identity string.
    APPROVE/REJECT need an owner identity string (and, enforced by the
    caller, a job in READY_FOR_OWNER_REVIEW). Identity here is
    caller-asserted and audit-logged; true external owner
    authentication needs an identity provider and does not exist in
    this codebase.
    """
    if not isinstance(action, str):
        return False, "UNKNOWN_ACTION"
    action = action.upper()
    if action in READ_ONLY_ACTIONS:
        return True, "READ_ONLY_NO_IDENTITY_REQUIRED"
    if action in OWNER_ACTIONS:
        if isinstance(owner, str) and owner.strip():
            return True, "OWNER_IDENTITY_PRESENT"
        return False, "OWNER_IDENTITY_REQUIRED"
    if action in OPERATOR_ACTIONS:
        if isinstance(owner, str) and owner.strip():
            return True, "OPERATOR_IDENTITY_PRESENT"
        return False, "OPERATOR_IDENTITY_REQUIRED"
    return False, "UNKNOWN_ACTION"


_KNOWN_FLAGS = {"test", "single-content", "cycle", "topics", "state-dir",
                "state", "content-id", "job-id", "owner", "decision",
                "reason", "path", "step", "strategy", "mode"}


def parse_command(text):
    """Parse a command string into a dispatchable dict.

    Accepts the canonical command word ``erudiance_linkdin``, the legacy
    alias ``erudience_linkdin``, and ``@Erudience`` (with or without
    trailing words), followed by an action verb and flags (--test,
    --single-content <ID> and the other known --flags). The action verb
    defaults to START, matching SKILL.md: a bare command runs the seven
    independent jobs. Returns keys: ok, command (canonical word),
    command_word (as typed), action, args, flags, error, raw.
    Unknown command words/verbs/flags -> ok False, error UNKNOWN_COMMAND.
    """
    result = {"ok": False, "command": None, "command_word": None,
              "action": None, "args": {}, "flags": {}, "error": None,
              "raw": text}
    if not isinstance(text, str) or not text.strip():
        result["error"] = "UNKNOWN_COMMAND"
        return result
    try:
        tokens = shlex.split(text)
    except ValueError:
        result["error"] = "INVALID_INPUT"
        return result
    if not tokens:
        result["error"] = "UNKNOWN_COMMAND"
        return result
    word = tokens[0]
    if word.lower() not in ("erudiance_linkdin", "erudience_linkdin", "@erudience"):
        result["error"] = "UNKNOWN_COMMAND"
        return result
    result["command_word"] = word
    result["command"] = CANONICAL_COMMAND
    rest = tokens[1:]
    action = "START"
    positionals = []
    flags = {"test": False, "single_content": None}
    options = {}
    i = 0
    if rest and not rest[0].startswith("--"):
        action = rest[0].upper()
        i = 1
    if action not in ALL_ACTIONS:
        result["error"] = "UNKNOWN_COMMAND"
        return result
    while i < len(rest):
        tok = rest[i]
        if tok.startswith("--"):
            name = tok[2:]
            if "=" in name:
                name, value = name.split("=", 1)
                if name.lower() not in _KNOWN_FLAGS:
                    result["error"] = "UNKNOWN_COMMAND"
                    return result
                options[name.lower().replace("-", "_")] = value
            else:
                if name.lower() not in _KNOWN_FLAGS:
                    result["error"] = "UNKNOWN_COMMAND"
                    return result
                if name.lower() == "test":
                    flags["test"] = True
                else:
                    if i + 1 >= len(rest):
                        result["error"] = "INVALID_INPUT"
                        return result
                    i += 1
                    options[name.lower().replace("-", "_")] = rest[i]
        else:
            positionals.append(tok)
        i += 1
    if "single_content" in options:
        flags["single_content"] = options.pop("single_content")
    args = {"action": action}
    args.update(flags)
    args.update(options)
    if positionals:
        args["positionals"] = positionals
    if "content_id" not in args and flags.get("single_content"):
        args["content_id"] = flags["single_content"]
    result.update({"ok": True, "action": action, "args": args, "flags": flags})
    return result


def _job_state_path(state_dir, content_id):
    """Return (Path|None, error_code|None). Rejects separators/traversal."""
    if not isinstance(content_id, str) or not content_id.strip():
        return None, "INVALID_INPUT"
    cid = content_id.strip()
    if "/" in cid or "\\" in cid or ".." in cid:
        return None, "INVALID_INPUT"
    return Path(state_dir) / ("%s.json" % cid), None


def _resolve_allowed_path(path, state_dir):
    """Resolve `path` and check it stays inside an allowed root.

    Allowed roots: the plugin root, the given state_dir, and the assets
    dir. Returns (resolved_path|None, error_code|None). Rejects absolute
    paths outside the roots and any ".." traversal that escapes a root.
    """
    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = PLUGIN_ROOT / candidate
        resolved = candidate.resolve()
    except Exception:
        return None, "PATH_NOT_ALLOWED"
    roots = [PLUGIN_ROOT.resolve(), ASSETS_DIR.resolve()]
    if state_dir:
        try:
            roots.append(Path(state_dir).resolve())
        except Exception:
            pass
    for root in roots:
        try:
            if resolved.is_relative_to(root):
                return resolved, None
        except Exception:
            pass
    return None, "PATH_NOT_ALLOWED"


def _resolve_under_state_dir(path, state_dir):
    """Resolve `path` and require it to stay under state_dir (WRITE)."""
    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = Path(state_dir) / candidate
        resolved = candidate.resolve()
        root = Path(state_dir).resolve()
        if resolved.is_relative_to(root):
            return resolved, None
    except Exception:
        pass
    return None, "PATH_NOT_ALLOWED"


def _current_hashes(state):
    """Return (content_hash, image_hash) from a job state's records."""
    records = state.get("records", {}) or {}
    content_hash = records.get("CONTENT", {}).get("hash")
    build = records.get("IMAGE_BUILD", {}).get("artifact", {}) or {}
    image_hash = build.get("image_sha256") or records.get("IMAGE_BUILD", {}).get("hash")
    return content_hash, image_hash


def _validate_state(state):
    """Gate checks that do NOT advance state. Returns a checks list."""
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "status": "PASS" if ok else "FAIL",
                       "detail": detail})

    records = state.get("records", {}) or {}
    chk("status_not_cancelled", state.get("status") != "CANCELLED",
        str(state.get("status")))
    chk("repairs_within_limit", int(state.get("repairs", 0)) <= MAX_REPAIRS,
        str(state.get("repairs", 0)))
    bad = []
    for stage, rec in records.items():
        try:
            if rec.get("hash") != digest(rec.get("artifact")):
                bad.append(stage)
        except Exception:
            bad.append(stage)
    chk("record_hashes_match", not bad,
        "mismatched: %s" % ",".join(bad) if bad else "%d records" % len(records))
    chk("stage_order",
        set(records) <= set(STAGES) and len(records) == int(state.get("index", -1)),
        "index=%s records=%d" % (state.get("index"), len(records)))
    chk("approval_state_known",
        state.get("approval_status", "DRAFT") in APPROVAL_STATES,
        str(state.get("approval_status", "DRAFT")))
    return checks


def _dispatch_action(action, args, state_dir, owner, trace):
    """Execute one authorized action.

    Returns (status, result, error, message). Never approves or
    publishes on behalf of GO/DO/START/RESUME/TEST/VALIDATE/RETRY/
    CANCEL/READ/WRITE/STATUS/OWNER_REVIEW: only APPROVE/REJECT (which
    delegate to op_submit_owner_decision) can change approval_status
    to OWNER_APPROVED / OWNER_REJECTED.
    """
    content_id = args.get("single_content") or args.get("content_id") or args.get("job_id")

    if action == "START":
        topics = args.get("topics")
        if isinstance(topics, str):
            topics = [t.strip() for t in topics.split(",") if t.strip()]
        # topics=None means auto-topic: run_batch generates 7 topics
        # from Erudiance's verified website pages. Explicit topics
        # are still validated exactly as before.
        if topics is not None and (not isinstance(topics, list) or len(topics) != 7
                or len(set(topics)) != 7
                or any(not isinstance(t, str) or not t.strip() for t in topics)):
            return ("INVALID_INPUT",
                    {"detail": "START requires topics: a list of 7 distinct non-empty strings"},
                    "INVALID_INPUT", "START requires topics: 7 distinct non-empty strings")
        cycle = args.get("cycle")
        if not isinstance(cycle, str) or not cycle.strip():
            return ("INVALID_INPUT",
                    {"detail": "START requires cycle: a non-empty string"},
                    "INVALID_INPUT", "START requires cycle")
        run_batch, err = _load_orchestrator_function("run_batch")
        if err is not None:
            return (err["error"], {"detail": err["message"]}, err["error"], err["message"])
        try:
            out = run_batch(state_dir, topics, cycle.strip(),
                            strategy=args.get("strategy"),
                            mode=args.get("mode", "TEST_FIXTURE"))
        except Exception as e:
            return ("ORCHESTRATOR_ERROR", {"detail": "run_batch failed: %s" % e},
                    "ORCHESTRATOR_ERROR", "run_batch failed: %s" % e)
        resolved = out.get("topics", topics) if isinstance(out, dict) else topics
        trace.append(_trace_event(action, "BATCH_STARTED",
                                  {"cycle": cycle, "topics": resolved}))
        return ("STARTED", out if isinstance(out, dict) else {"result": out}, None, None)

    if action == "TEST":
        if not content_id:
            return ("INVALID_INPUT",
                    {"detail": "TEST requires --single-content <ID>"},
                    "INVALID_INPUT", "TEST requires --single-content <ID>")
        path, perr = _job_state_path(state_dir, content_id)
        if perr is not None or not path.is_file():
            return ("JOB_NOT_FOUND",
                    {"detail": "no state file for content_id %r" % content_id},
                    "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
        run_job, err = _load_orchestrator_function("run_job")
        if err is not None:
            return (err["error"], {"detail": err["message"]}, err["error"], err["message"])
        try:
            out = run_job(str(path), adapters=args.get("adapters"),
                          mode=args.get("mode", "TEST_FIXTURE"))
        except Exception as e:
            return ("ORCHESTRATOR_ERROR", {"detail": "run_job failed: %s" % e},
                    "ORCHESTRATOR_ERROR", "run_job failed: %s" % e)
        trace.append(_trace_event(action, "JOB_TESTED", {"content_id": content_id}))
        status = out.get("status", "OK") if isinstance(out, dict) else "OK"
        return (status, out if isinstance(out, dict) else {"result": out}, None, None)

    if action == "STATUS":
        if content_id:
            path, perr = _job_state_path(state_dir, content_id)
            if perr is not None or not path.is_file():
                return ("JOB_NOT_FOUND",
                        {"detail": "no state file for content_id %r" % content_id},
                        "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
            state = load(str(path))
            return (state.get("status", "UNKNOWN"),
                    {"content_id": content_id, "status": state.get("status"),
                     "approval_status": state.get("approval_status", "DRAFT"),
                     "stage": next_step(state).get("stage"),
                     "index": state.get("index"), "repairs": state.get("repairs"),
                     "state_path": str(path)}, None, None)
        manifest = Path(state_dir) / "manifest.json"
        if not manifest.is_file():
            return ("JOB_NOT_FOUND",
                    {"detail": "no manifest.json in state_dir and no content_id given"},
                    "JOB_NOT_FOUND", "no manifest.json in state_dir and no content_id given")
        try:
            data = json.loads(manifest.read_text(encoding="utf8"))
        except Exception as e:
            return ("STATE_ERROR", {"detail": "manifest.json unreadable: %s" % e},
                    "STATE_ERROR", "manifest.json unreadable: %s" % e)
        jobs = []
        for job in data.get("jobs", []):
            try:
                st = load(job["state"])
                jobs.append({"content_id": st["job"]["content_id"],
                             "status": st.get("status"),
                             "approval_status": st.get("approval_status", "DRAFT"),
                             "stage": next_step(st).get("stage"),
                             "index": st.get("index")})
            except Exception as e:
                jobs.append({"content_id": job.get("content_id"), "error": str(e)})
        return ("OK", {"cycle": data.get("cycle"), "jobs": jobs,
                       "job_count": len(jobs)}, None, None)

    if action == "VALIDATE":
        if not content_id:
            return ("INVALID_INPUT",
                    {"detail": "VALIDATE requires a content_id"},
                    "INVALID_INPUT", "VALIDATE requires a content_id")
        path, perr = _job_state_path(state_dir, content_id)
        if perr is not None or not path.is_file():
            return ("JOB_NOT_FOUND",
                    {"detail": "no state file for content_id %r" % content_id},
                    "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
        state = load(str(path))
        checks = _validate_state(state)
        valid = all(c["status"] == "PASS" for c in checks)
        result = {"content_id": content_id, "valid": valid, "checks": checks,
                  "status": state.get("status"),
                  "approval_status": state.get("approval_status", "DRAFT"),
                  "advanced": False}
        if args.get("strategy") is not None:
            verify_fn, err = _load_orchestrator_function("verify_batch_strategy")
            if err is not None:
                return (err["error"], {"detail": err["message"]}, err["error"], err["message"])
            try:
                result["strategy"] = verify_fn(state_dir, args["strategy"])
            except Exception as e:
                return ("ORCHESTRATOR_ERROR",
                        {"detail": "verify_batch_strategy failed: %s" % e},
                        "ORCHESTRATOR_ERROR", "verify_batch_strategy failed: %s" % e)
        trace.append(_trace_event(action, "VALIDATED",
                                  {"content_id": content_id, "valid": valid}))
        return (state.get("status", "UNKNOWN"), result, None, None)

    if action in ("RESUME", "GO"):
        if not content_id:
            return ("INVALID_INPUT",
                    {"detail": "%s requires a content_id" % action},
                    "INVALID_INPUT", "%s requires a content_id" % action)
        path, perr = _job_state_path(state_dir, content_id)
        if perr is not None or not path.is_file():
            return ("JOB_NOT_FOUND",
                    {"detail": "no state file for content_id %r" % content_id},
                    "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
        state = load(str(path))
        if state.get("status") == "BLOCKED":
            return ("JOB_BLOCKED",
                    {"detail": "job is BLOCKED; use RETRY to rewind it first (max 3 repairs per attempt)",
                     "approval_status": state.get("approval_status", "DRAFT")},
                    "JOB_BLOCKED", "job is BLOCKED; use RETRY to rewind it first")
        if state.get("status") == "CANCELLED":
            return ("JOB_CANCELLED",
                    {"detail": "job is CANCELLED and cannot be resumed",
                     "approval_status": state.get("approval_status", "DRAFT")},
                    "JOB_CANCELLED", "job is CANCELLED and cannot be resumed")
        if state.get("status") in ("READY_FOR_OWNER_REVIEW", "TEST_FIXTURE_PASS"):
            return (state["status"],
                    {"detail": "job already finished; nothing to resume",
                     "content_id": content_id,
                     "approval_status": state.get("approval_status", "DRAFT")},
                    None, None)
        run_job, err = _load_orchestrator_function("run_job")
        if err is not None:
            return (err["error"], {"detail": err["message"]}, err["error"], err["message"])
        try:
            out = run_job(str(path), adapters=args.get("adapters"),
                          mode=args.get("mode", "TEST_FIXTURE"))
        except Exception as e:
            return ("ORCHESTRATOR_ERROR", {"detail": "run_job failed: %s" % e},
                    "ORCHESTRATOR_ERROR", "run_job failed: %s" % e)
        trace.append(_trace_event(action, "JOB_RESUMED",
                                  {"content_id": content_id,
                                   "note": "validation gates were NOT skipped; "
                                           "GO/DO never approve or publish"}))
        status = out.get("status", "OK") if isinstance(out, dict) else "OK"
        result = dict(out) if isinstance(out, dict) else {"result": out}
        try:
            result["approval_status"] = load(str(path)).get("approval_status", "DRAFT")
        except Exception:
            pass
        return (status, result, None, None)

    if action == "RETRY":
        if not content_id:
            return ("INVALID_INPUT",
                    {"detail": "RETRY requires a content_id"},
                    "INVALID_INPUT", "RETRY requires a content_id")
        path, perr = _job_state_path(state_dir, content_id)
        if perr is not None or not path.is_file():
            return ("JOB_NOT_FOUND",
                    {"detail": "no state file for content_id %r" % content_id},
                    "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
        state = load(str(path))
        if state.get("status") == "CANCELLED":
            return ("JOB_CANCELLED",
                    {"detail": "job is CANCELLED and cannot be retried"},
                    "JOB_CANCELLED", "job is CANCELLED and cannot be retried")
        if state.get("status") == "BLOCKED":
            idx = state.get("index", 0)
            stage = STAGES[idx] if 0 <= idx < len(STAGES) else None
            state["repairs"] = 0
            state["status"] = "AWAITING_TOOL_EXECUTION"
            state.setdefault("trace", []).append(
                {"stage": stage, "event": "RETRY_REWIND", "repairs_reset_to": 0,
                 "at": _now_iso()})
            save(str(path), state)
            trace.append(_trace_event(action, "RETRY_REWIND",
                                      {"content_id": content_id, "stage": stage}))
            return ("AWAITING_TOOL_EXECUTION",
                    {"content_id": content_id, "stage": stage, "repairs": 0,
                     "detail": "BLOCKED job rewound with a fresh 3-repair budget; "
                               "re-attempt the failed stage only by submitting its "
                               "receipt via the bridge submit path"},
                    None, None)
        current = next_step(state).get("stage")
        return (state.get("status", "UNKNOWN"),
                {"content_id": content_id, "stage": current,
                 "repairs": state.get("repairs", 0),
                 "detail": "job is not BLOCKED; the current stage is already the "
                           "retry point; re-submit its receipt via the bridge submit path"},
                None, None)

    if action == "CANCEL":
        if not content_id:
            return ("INVALID_INPUT",
                    {"detail": "CANCEL requires a content_id"},
                    "INVALID_INPUT", "CANCEL requires a content_id")
        path, perr = _job_state_path(state_dir, content_id)
        if perr is not None or not path.is_file():
            return ("JOB_NOT_FOUND",
                    {"detail": "no state file for content_id %r" % content_id},
                    "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
        state = load(str(path))
        if state.get("status") == "CANCELLED":
            return ("ALREADY_CANCELLED",
                    {"detail": "job is already CANCELLED", "content_id": content_id},
                    "ALREADY_CANCELLED", "job is already CANCELLED")
        idx = state.get("index", 0)
        stage = STAGES[idx] if 0 <= idx < len(STAGES) else None
        state["status"] = "CANCELLED"
        state.setdefault("trace", []).append(
            {"stage": stage, "event": "CANCELLED", "at": _now_iso()})
        save(str(path), state)
        trace.append(_trace_event(action, "CANCELLED", {"content_id": content_id}))
        return ("CANCELLED",
                {"content_id": content_id,
                 "detail": "job marked CANCELLED; the state file was kept, never deleted"},
                None, None)

    if action == "OWNER_REVIEW":
        if not content_id:
            return ("INVALID_INPUT",
                    {"detail": "OWNER_REVIEW requires a content_id"},
                    "INVALID_INPUT", "OWNER_REVIEW requires a content_id")
        path, perr = _job_state_path(state_dir, content_id)
        if perr is not None or not path.is_file():
            return ("JOB_NOT_FOUND",
                    {"detail": "no state file for content_id %r" % content_id},
                    "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
        state = load(str(path))
        ready = (state.get("approval_status") == "READY_FOR_OWNER_REVIEW"
                 and state.get("status") == "READY_FOR_OWNER_REVIEW"
                 and state.get("index") == len(STAGES))
        return (state.get("status", "UNKNOWN"),
                {"content_id": content_id, "status": state.get("status"),
                 "approval_status": state.get("approval_status", "DRAFT"),
                 "ready_for_owner_review": ready,
                 "completed_stages": state.get("index"),
                 "total_stages": len(STAGES), "repairs": state.get("repairs"),
                 "detail": "Review-only report: this action never approves, "
                           "rejects, publishes or delivers."},
                None, None)

    if action in ("APPROVE", "REJECT"):
        decision = "APPROVE" if action == "APPROVE" else "REJECT"
        if args.get("decision") and str(args["decision"]).upper() != decision:
            return ("INVALID_INPUT",
                    {"detail": "decision %r does not match action %s" % (args.get("decision"), action)},
                    "INVALID_INPUT", "decision does not match action")
        payload = {"owner": owner,
                   "content_id": content_id,
                   "decision": decision,
                   "state_dir": state_dir}
        if args.get("reason"):
            payload["reason"] = args["reason"]
        out = op_submit_owner_decision(payload)
        if out.get("ok"):
            trace.append(_trace_event(action, "OWNER_DECISION_RECORDED",
                                      {"content_id": content_id,
                                       "decision": decision,
                                       "approval_id": out.get("approval_id")}))
            return (out.get("approval_status", decision), {"approval": out}, None, None)
        return (out.get("error", "ERROR"),
                {"detail": out.get("message", out.get("error"))},
                out.get("error", "ERROR"), out.get("message"))

    if action == "READ":
        rel = args.get("path")
        if not rel:
            return ("INVALID_INPUT", {"detail": "READ requires path"},
                    "INVALID_INPUT", "READ requires path")
        resolved, rerr = _resolve_allowed_path(rel, state_dir)
        if rerr is not None:
            return ("PATH_NOT_ALLOWED",
                    {"detail": "path %r is outside the allowed roots (plugin root, state_dir, assets)" % rel},
                    "PATH_NOT_ALLOWED", "path is outside the allowed roots")
        if not resolved.is_file():
            return ("FILE_NOT_FOUND", {"detail": "no such file: %s" % resolved},
                    "FILE_NOT_FOUND", "no such file")
        if resolved.stat().st_size > READ_MAX_BYTES:
            return ("FILE_TOO_LARGE",
                    {"detail": "file exceeds the 5 MB read cap"},
                    "FILE_TOO_LARGE", "file exceeds the 5 MB read cap")
        data = resolved.read_bytes()
        text = data.decode("utf8", errors="replace")
        truncated = len(text) > READ_MAX_CHARS
        if truncated:
            text = text[:READ_MAX_CHARS]
        return ("OK",
                {"path": str(resolved), "content": text, "truncated": truncated,
                 "bytes": len(data), "sha256": sha256(data).hexdigest()},
                None, None)

    if action == "DO":
        step = args.get("step")
        if not step:
            return ("INVALID_INPUT",
                    {"detail": "DO requires step: one of validate_job, summarize_batch, check_duplicates, verify_strategy"},
                    "INVALID_INPUT", "DO requires step")
        step = str(step)
        approval_status = None
        if content_id:
            try:
                p, _e = _job_state_path(state_dir, content_id)
                if p is not None and p.is_file():
                    approval_status = load(str(p)).get("approval_status", "DRAFT")
            except Exception:
                pass
        if step == "validate_job":
            if not content_id:
                return ("INVALID_INPUT",
                        {"detail": "DO validate_job requires a content_id"},
                        "INVALID_INPUT", "DO validate_job requires a content_id")
            p, perr = _job_state_path(state_dir, content_id)
            if perr is not None or not p.is_file():
                return ("JOB_NOT_FOUND",
                        {"detail": "no state file for content_id %r" % content_id},
                        "JOB_NOT_FOUND", "no state file for content_id %r" % content_id)
            state = load(str(p))
            checks = _validate_state(state)
            out = {"step": step, "content_id": content_id,
                   "valid": all(c["status"] == "PASS" for c in checks),
                   "checks": checks}
        elif step == "summarize_batch":
            fn, err = _load_orchestrator_function("summary")
            if err is not None:
                return (err["error"], {"detail": err["message"]}, err["error"], err["message"])
            try:
                out = {"step": step, "summary": fn(state_dir)}
            except Exception as e:
                return ("ORCHESTRATOR_ERROR", {"detail": "summary failed: %s" % e},
                        "ORCHESTRATOR_ERROR", "summary failed: %s" % e)
        elif step == "check_duplicates":
            fn, err = _load_orchestrator_function("check_duplicate_images")
            if err is not None:
                return (err["error"], {"detail": err["message"]}, err["error"], err["message"])
            try:
                out = {"step": step, "duplicates": fn(state_dir)}
            except Exception as e:
                return ("ORCHESTRATOR_ERROR",
                        {"detail": "check_duplicate_images failed: %s" % e},
                        "ORCHESTRATOR_ERROR", "check_duplicate_images failed: %s" % e)
        elif step == "verify_strategy":
            if args.get("strategy") is None:
                return ("INVALID_INPUT",
                        {"detail": "DO verify_strategy requires strategy"},
                        "INVALID_INPUT", "DO verify_strategy requires strategy")
            fn, err = _load_orchestrator_function("verify_batch_strategy")
            if err is not None:
                return (err["error"], {"detail": err["message"]}, err["error"], err["message"])
            try:
                out = {"step": step, "verification": fn(state_dir, args["strategy"])}
            except Exception as e:
                return ("ORCHESTRATOR_ERROR",
                        {"detail": "verify_batch_strategy failed: %s" % e},
                        "ORCHESTRATOR_ERROR", "verify_batch_strategy failed: %s" % e)
        else:
            return ("INVALID_INPUT",
                    {"detail": "unknown DO step %r" % step},
                    "INVALID_INPUT", "unknown DO step %r" % step)
        out["approval_changed"] = False
        out["approval_status"] = approval_status
        trace.append(_trace_event(action, "STEP_EXECUTED",
                                  {"step": step, "approval_changed": False}))
        return ("OK", out, None, None)

    if action == "WRITE":
        rel = args.get("path")
        content = args.get("content")
        if not rel or content is None:
            return ("INVALID_INPUT",
                    {"detail": "WRITE requires path and content"},
                    "INVALID_INPUT", "WRITE requires path and content")
        resolved, rerr = _resolve_under_state_dir(rel, state_dir)
        if rerr is not None:
            return ("PATH_NOT_ALLOWED",
                    {"detail": "WRITE is only allowed under the state_dir"},
                    "PATH_NOT_ALLOWED", "WRITE is only allowed under the state_dir")
        if resolved.name in ("evidence.db", "manifest.json"):
            return ("PROTECTED_FILE",
                    {"detail": "refusing to write protected file %s" % resolved.name},
                    "PROTECTED_FILE", "refusing to write protected file %s" % resolved.name)
        if resolved.suffix == ".py":
            return ("PROTECTED_FILE",
                    {"detail": "refusing to write executable file %s" % resolved.name},
                    "PROTECTED_FILE", "refusing to write executable file")
        if resolved.is_dir():
            return ("INVALID_INPUT", {"detail": "path is a directory"},
                    "INVALID_INPUT", "path is a directory")
        if isinstance(content, dict):
            data = json.dumps(content, indent=2, ensure_ascii=False).encode("utf8")
        elif isinstance(content, str):
            data = content.encode("utf8")
        else:
            return ("INVALID_INPUT",
                    {"detail": "content must be text or a JSON object"},
                    "INVALID_INPUT", "content must be text or a JSON object")
        resolved.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", dir=str(resolved.parent), delete=False) as f:
            f.write(data)
            tmp = f.name
        os.replace(tmp, resolved)
        trace.append(_trace_event(action, "WROTE_FILE",
                                  {"path": str(resolved), "bytes": len(data)}))
        return ("OK",
                {"path": str(resolved), "bytes_written": len(data),
                 "sha256": sha256(data).hexdigest()},
                None, None)

    return ("UNKNOWN_COMMAND", {"detail": "unhandled action %r" % action},
            "UNKNOWN_COMMAND", "unhandled action")


def dispatch_command(command, args, state_dir, owner=None):
    """Route one parsed command to its workflow action. Never raises.

    command is the command word (``erudiance_linkdin`` / alias) or an
    action verb; args carries at least ``action`` plus the action's
    inputs; state_dir is the directory holding job state files (and
    the local evidence.db ledger); owner is the caller-asserted
    operator/owner identity string. Every dispatched command returns
    {"ok", "command", "action", "status", "result", "error", "message",
    "trace"} and appends an audit trace entry via evidence_store
    (best effort; a missing ledger is reported, never fabricated).
    Unknown commands/flags return ok=False, error UNKNOWN_COMMAND.
    A generic GO or DO is NEVER interpreted as approval or publishing:
    only APPROVE/REJECT (via op_submit_owner_decision) change
    approval_status to OWNER_APPROVED / OWNER_REJECTED.
    """
    trace = []
    raw_command = command if isinstance(command, str) else ""
    args = dict(args) if isinstance(args, dict) else {}
    action = ""
    if isinstance(args.get("action"), str) and args["action"].strip():
        action = args["action"].strip().upper()
    elif raw_command.strip().upper() in ALL_ACTIONS:
        action = raw_command.strip().upper()
    if action not in ALL_ACTIONS:
        trace.append(_trace_event("UNKNOWN", "UNKNOWN_COMMAND",
                                  {"command": raw_command}))
        return _result(raw_command, action or "UNKNOWN", "UNKNOWN_COMMAND",
                       {"detail": "Unknown command or action: %r" % raw_command},
                       "UNKNOWN_COMMAND",
                       "Unknown command or action: %r" % raw_command, trace)
    if not isinstance(state_dir, str) or not state_dir.strip():
        trace.append(_trace_event(action, "INVALID_INPUT",
                                  {"reason": "state_dir is required"}))
        return _result(raw_command, action, "INVALID_INPUT",
                       {"detail": "state_dir is required"},
                       "INVALID_INPUT", "state_dir is required", trace)
    allowed, auth_reason = authorize(action, owner)
    trace.append(_trace_event(action, "AUTHORIZE",
                              {"allowed": allowed, "reason": auth_reason,
                               "owner_present": bool(owner)}))
    job_id = args.get("content_id") or args.get("single_content") or args.get("job_id") or ""
    if not allowed:
        audit = _audit_event(state_dir, job_id or "batch",
                             "dispatch:%s" % action,
                             {"command": raw_command, "action": action,
                              "ok": False, "error": "UNAUTHORIZED",
                              "auth": auth_reason})
        trace.append(_trace_event(action, "AUDIT_LEDGER", audit))
        return _result(raw_command, action, "UNAUTHORIZED",
                       {"detail": auth_reason},
                       "UNAUTHORIZED", auth_reason, trace)
    try:
        status, result, error, message = _dispatch_action(
            action, args, state_dir, owner, trace)
    except Exception as e:
        status, result, error, message = (
            "ERROR", {"detail": "dispatch failed: %s" % e},
            "DISPATCH_ERROR", "dispatch failed: %s" % e)
        trace.append(_trace_event(action, "DISPATCH_ERROR", {"reason": str(e)}))
    audit = _audit_event(state_dir, job_id or "batch",
                         "dispatch:%s" % action,
                         {"command": raw_command, "action": action,
                          "ok": error is None, "error": error,
                          "auth": auth_reason})
    trace.append(_trace_event(action, "AUDIT_LEDGER", audit))
    return _result(raw_command, action, status, result, error, message, trace)


# ---------------------------------------------------------------------------
# Provider-neutral registry
# ---------------------------------------------------------------------------

class ProviderRegistry:
    """Provider-neutral registry: metadata only, never credential values.

    Default state: no provider registered, so every fetch returns
    NOT_CONFIGURED and no evidence is fabricated. A registered provider
    is CONFIGURED only when its named credential env var is present and
    non-empty (presence check only -- the value is never read, logged
    or returned). fetch_source() performs a real read-only GET (stdlib
    urllib only) only for a CONFIGURED provider; the credential value
    is never attached to the request because no provider API contract
    exists in this codebase.
    """

    def __init__(self):
        self._providers = {}
        self._request_times = {}

    def register_provider(self, name, kind, base_url=None, credential_env=None):
        if not isinstance(name, str) or not name.strip():
            return {"ok": False, "error": "INVALID_INPUT",
                    "message": "provider name is required"}
        if not isinstance(kind, str) or not kind.strip():
            return {"ok": False, "error": "INVALID_INPUT",
                    "message": "provider kind is required"}
        self._providers[name] = {"name": name, "kind": kind,
                                 "base_url": base_url,
                                 "credential_env": credential_env}
        return {"ok": True, "name": name, "kind": kind,
                "base_url": base_url, "credential_env": credential_env,
                "status": self.provider_status(name)}

    def provider_status(self, name):
        info = self._providers.get(name)
        if info is None:
            return "NOT_CONFIGURED"
        base_url = info.get("base_url")
        if base_url is not None and not (
                isinstance(base_url, str)
                and base_url.startswith(("http://", "https://"))):
            return "ERROR"
        env = info.get("credential_env")
        if not env:
            return "NOT_CONFIGURED"
        return "CONFIGURED" if os.environ.get(env) else "NOT_CONFIGURED"

    def validate_credentials(self, name):
        """Check ONLY whether the named env var is present/non-empty.

        Never reads, logs or returns the credential value itself.
        """
        info = self._providers.get(name)
        if info is None:
            return {"ok": False, "name": name, "status": "NOT_CONFIGURED",
                    "credential_env": None, "credential_present": False,
                    "error": "UNKNOWN_PROVIDER"}
        env = info.get("credential_env")
        present = bool(env and os.environ.get(env))
        status = self.provider_status(name)
        return {"ok": present, "name": name, "status": status,
                "credential_env": env, "credential_present": present,
                "error": None if present else "CREDENTIAL_NOT_CONFIGURED"}

    def list_providers(self):
        return {"providers": {
            name: {"kind": info["kind"], "base_url": info.get("base_url"),
                   "credential_env": info.get("credential_env"),
                   "status": self.provider_status(name)}
            for name, info in self._providers.items()},
            "count": len(self._providers)}

    def _rate_limited(self, name):
        now = time.monotonic()
        window = [t for t in self._request_times.get(name, [])
                  if now - t < 60]
        if len(window) >= FETCH_RATE_LIMIT_PER_MINUTE:
            self._request_times[name] = window
            return True
        window.append(now)
        self._request_times[name] = window
        return False

    def fetch_source(self, url, provider=None, timeout=10):
        """Read-only GET of a source URL, or an honest NOT_CONFIGURED.

        Returns {"status": "LIVE_VERIFIED"|"NOT_CONFIGURED"|"ERROR",
        "url", "retrieved_at", "sha256", "provider", "error"}. No
        provider registered (or provider not CONFIGURED) means
        NOT_CONFIGURED, never fabricated evidence. A CONFIGURED
        provider gets a real GET with 2 retries (backoff), a
        10-requests/minute per-provider in-memory token bucket, and
        error classification into TIMEOUT / RATE_LIMITED / HTTP_ERROR
        / NETWORK_ERROR / INVALID_URL / RESPONSE_TOO_LARGE.
        """
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            return {"status": "ERROR", "url": url, "retrieved_at": None,
                    "sha256": None, "provider": provider, "error": "INVALID_URL"}
        if provider is not None:
            if provider not in self._providers:
                return {"status": "ERROR", "url": url, "retrieved_at": None,
                        "sha256": None, "provider": provider,
                        "error": "UNKNOWN_PROVIDER"}
            if self.provider_status(provider) != "CONFIGURED":
                return {"status": "NOT_CONFIGURED", "url": url,
                        "retrieved_at": None, "sha256": None,
                        "provider": provider, "error": "PROVIDER_NOT_CONFIGURED"}
        else:
            if not self._providers:
                return {"status": "NOT_CONFIGURED", "url": url,
                        "retrieved_at": None, "sha256": None,
                        "provider": None, "error": "NO_PROVIDER_REGISTERED"}
            return {"status": "NOT_CONFIGURED", "url": url,
                    "retrieved_at": None, "sha256": None,
                    "provider": None, "error": "PROVIDER_REQUIRED"}
        if self._rate_limited(provider):
            return {"status": "ERROR", "url": url, "retrieved_at": None,
                    "sha256": None, "provider": provider, "error": "RATE_LIMITED"}
        last_error = "NETWORK_ERROR"
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url, method="GET",
                    headers={"User-Agent": "erudience-bridge/4.9.2"})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = resp.read(FETCH_MAX_BYTES + 1)
                    if len(body) > FETCH_MAX_BYTES:
                        return {"status": "ERROR", "url": url,
                                "retrieved_at": None, "sha256": None,
                                "provider": provider,
                                "error": "RESPONSE_TOO_LARGE"}
                    if resp.status != 200:
                        return {"status": "ERROR", "url": url,
                                "retrieved_at": None, "sha256": None,
                                "provider": provider, "error": "HTTP_ERROR"}
                    return {"status": "LIVE_VERIFIED", "url": url,
                            "retrieved_at": _now_iso(),
                            "sha256": sha256(body).hexdigest(),
                            "provider": provider, "error": None}
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    return {"status": "ERROR", "url": url,
                            "retrieved_at": None, "sha256": None,
                            "provider": provider, "error": "RATE_LIMITED"}
                return {"status": "ERROR", "url": url, "retrieved_at": None,
                        "sha256": None, "provider": provider,
                        "error": "HTTP_ERROR"}
            except TimeoutError:
                last_error = "TIMEOUT"
            except urllib.error.URLError as e:
                if isinstance(getattr(e, "reason", None), TimeoutError):
                    last_error = "TIMEOUT"
                else:
                    last_error = "NETWORK_ERROR"
            except (socket.timeout, OSError):
                last_error = "NETWORK_ERROR"
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
        return {"status": "ERROR", "url": url, "retrieved_at": None,
                "sha256": None, "provider": provider, "error": last_error}


_PROVIDER_REGISTRY = None


def get_provider_registry():
    """Return the module-level ProviderRegistry singleton."""
    global _PROVIDER_REGISTRY
    if _PROVIDER_REGISTRY is None:
        _PROVIDER_REGISTRY = ProviderRegistry()
    return _PROVIDER_REGISTRY


def chatgpt_connection_status():
    """Honest ChatGPT connection state: never claims CONNECTED.

    No live ChatGPT-to-ERUDIANCE request has succeeded; the blocker is
    owner-side ChatGPT installation/hosting/auth.
    """
    return {"connected": False, "blocker": CHATGPT_CONNECTION_BLOCKER}


# ---------------------------------------------------------------------------
# ChatGPT operations: one function per operation, op_<name>(payload).
# ---------------------------------------------------------------------------

def _op_error(error, message):
    return {"ok": False, "error": error, "message": message}


def _op_invalid_if_missing(payload, fields):
    missing = [f for f in fields
               if f not in payload or payload[f] in (None, "")]
    if missing:
        return _op_error("INVALID_INPUT",
                         "missing required field(s): %s" % ", ".join(missing))
    return None


def _op_identity(payload, field):
    """Identity check: missing key -> INVALID_INPUT; blank -> UNAUTHORIZED."""
    if field not in payload or payload[field] is None:
        return _op_error("INVALID_INPUT", "missing required field(s): %s" % field)
    if not isinstance(payload[field], str) or not payload[field].strip():
        return _op_error("UNAUTHORIZED", "%s identity is required" % field)
    return None


def _op_audit(payload, kind, ok, extra=None):
    state_dir = payload.get("state_dir") if isinstance(payload, dict) else None
    if not state_dir:
        return {"ledger": "unavailable", "reason": "NO_STATE_DIR"}
    job_id = payload.get("content_id") or payload.get("job_id") or "batch"
    merged = {"ok": ok}
    if extra:
        merged.update(extra)
    return _audit_event(state_dir, job_id, kind, merged)


def op_get_system_status(payload):
    """Report gate/bridge/batch versions, provider statuses, approval
    state. Never claims CONNECTED."""
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    registry = get_provider_registry()
    providers = registry.list_providers()["providers"]
    return {"ok": True,
            "bridge_version": BRIDGE_VERSION,
            "gate_version": GATE_VERSION,
            "batch_version": BATCH_VERSION,
            "plugin_version": PLUGIN_VERSION,
            "stages": list(STAGES),
            "stage_count": len(STAGES),
            "providers": providers,
            "provider_count": len(providers),
            "chatgpt": chatgpt_connection_status(),
            "approval": {"required": True, "states": list(APPROVAL_STATES),
                         "note": "READY_FOR_OWNER_REVIEW is never "
                                 "OWNER_APPROVED; approval needs an explicit "
                                 "owner decision recorded in the evidence ledger."},
            "error": None}


def op_list_agent_capabilities(payload):
    """Return the 18 roles from batch_guard_v45.AGENT_REGISTRY (Worker 2).

    Fails loudly naming AGENT_REGISTRY if it is missing instead of
    inventing capabilities.
    """
    if payload is not None and not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    try:
        import batch_guard_v45
    except Exception as e:
        return _op_error("MISSING_ORCHESTRATOR_MODULE",
                         "batch_guard_v45 could not be imported: %s" % e)
    registry = getattr(batch_guard_v45, "AGENT_REGISTRY", None)
    if not isinstance(registry, dict):
        return _op_error("MISSING_ORCHESTRATOR_FUNCTION",
                         "batch_guard_v45.AGENT_REGISTRY is not implemented yet "
                         "(Worker 2); refusing to fake agent capabilities")
    return {"ok": True, "agents": dict(registry), "count": len(registry),
            "error": None}


def op_start_workflow(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["cycle", "state_dir"])
    if err:
        return err
    err = _op_identity(payload, "operator")
    if err:
        return err
    # topics is optional: omitted/None means auto-topic (the server
    # generates 7 topics from Erudiance's verified website pages).
    topics = payload.get("topics")
    if topics is not None and (not isinstance(topics, list) or len(topics) != 7
            or len(set(topics)) != 7
            or any(not isinstance(t, str) or not t.strip() for t in topics)):
        return _op_error("INVALID_INPUT",
                         "topics must be a list of 7 distinct non-empty strings")
    if not isinstance(payload["cycle"], str) or not payload["cycle"].strip():
        return _op_error("INVALID_INPUT", "cycle must be a non-empty string")
    out = dispatch_command(CANONICAL_COMMAND,
                           {"action": "START", "topics": topics,
                            "cycle": payload["cycle"],
                            "strategy": payload.get("strategy"),
                            "mode": payload.get("mode", "TEST_FIXTURE")},
                           payload["state_dir"], owner=payload["operator"])
    out["operation"] = "start_workflow"
    return out


def op_get_workflow_status(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir"])
    if err:
        return err
    args = {"action": "STATUS"}
    if payload.get("content_id"):
        args["content_id"] = payload["content_id"]
    if payload.get("single_content"):
        args["single_content"] = payload["single_content"]
    out = dispatch_command(CANONICAL_COMMAND, args, payload["state_dir"],
                           owner=payload.get("operator"))
    out["operation"] = "get_workflow_status"
    return out


def op_execute_authorized_step(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir", "step"])
    if err:
        return err
    err = _op_identity(payload, "operator")
    if err:
        return err
    args = {"action": "DO", "step": payload["step"]}
    if payload.get("content_id"):
        args["content_id"] = payload["content_id"]
    if payload.get("single_content"):
        args["single_content"] = payload["single_content"]
    if payload.get("strategy") is not None:
        args["strategy"] = payload["strategy"]
    out = dispatch_command(CANONICAL_COMMAND, args, payload["state_dir"],
                           owner=payload["operator"])
    out["operation"] = "execute_authorized_step"
    return out


def op_resume_workflow(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir", "content_id"])
    if err:
        return err
    err = _op_identity(payload, "operator")
    if err:
        return err
    out = dispatch_command(CANONICAL_COMMAND,
                           {"action": "RESUME",
                            "content_id": payload["content_id"],
                            "mode": payload.get("mode", "TEST_FIXTURE")},
                           payload["state_dir"], owner=payload["operator"])
    out["operation"] = "resume_workflow"
    return out


def op_get_agent_report(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir"])
    if err:
        return err
    state_dir = payload["state_dir"]
    content_id = payload.get("content_id")
    if content_id:
        path, perr = _job_state_path(state_dir, content_id)
        if perr is not None or not path.is_file():
            return _op_error("JOB_NOT_FOUND",
                             "no state file for content_id %r" % content_id)
        state = load(str(path))
        return {"ok": True, "content_id": content_id,
                "status": state.get("status"),
                "approval_status": state.get("approval_status", "DRAFT"),
                "stage": next_step(state).get("stage"),
                "index": state.get("index"), "repairs": state.get("repairs"),
                "records": len(state.get("records", {})),
                "trace_events": len(state.get("trace", [])), "error": None}
    summary_fn, err2 = _load_orchestrator_function("summary")
    if err2 is not None:
        return _op_error(err2["error"], err2["message"])
    try:
        report = summary_fn(state_dir)
    except FileNotFoundError as e:
        return _op_error("BATCH_NOT_FOUND",
                         "no batch manifest in state_dir: %s" % e)
    except Exception as e:
        return _op_error("ORCHESTRATOR_ERROR", "summary failed: %s" % e)
    return {"ok": True, "report": report, "error": None}


def op_get_content_preview(payload):
    """Metadata only: file paths + hashes + metadata. Never claims a
    preview was visually verified."""
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir", "content_id"])
    if err:
        return err
    state_dir = payload["state_dir"]
    content_id = payload["content_id"]
    path, perr = _job_state_path(state_dir, content_id)
    if perr is not None or not path.is_file():
        return _op_error("JOB_NOT_FOUND",
                         "no state file for content_id %r" % content_id)
    state = load(str(path))
    records = state.get("records", {}) or {}
    content = records.get("CONTENT", {}).get("artifact", {}) or {}
    plan = records.get("IMAGE_PLAN", {}).get("artifact", {}) or {}
    build = records.get("IMAGE_BUILD", {}).get("artifact", {}) or {}
    return {"ok": True, "content_id": content_id, "state_path": str(path),
            "status": state.get("status"),
            "approval_status": state.get("approval_status", "DRAFT"),
            "stage": next_step(state).get("stage"),
            "topic": state.get("job", {}).get("topic"),
            "content_hash": records.get("CONTENT", {}).get("hash"),
            "caption": content.get("caption"),
            "plan_hash": records.get("IMAGE_PLAN", {}).get("hash"),
            "poster_text": plan.get("poster_text"),
            "image_path": build.get("image_path"),
            "image_sha256": build.get("image_sha256"),
            "visually_verified": False,
            "note": "Metadata only: no preview was visually verified.",
            "error": None}


def op_get_image_preview(payload):
    """Metadata only: file path + hash + dimensions. Never claims a
    preview was visually verified."""
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir", "content_id"])
    if err:
        return err
    state_dir = payload["state_dir"]
    content_id = payload["content_id"]
    path, perr = _job_state_path(state_dir, content_id)
    if perr is not None or not path.is_file():
        return _op_error("JOB_NOT_FOUND",
                         "no state file for content_id %r" % content_id)
    state = load(str(path))
    records = state.get("records", {}) or {}
    plan = records.get("IMAGE_PLAN", {}).get("artifact", {}) or {}
    build = records.get("IMAGE_BUILD", {}).get("artifact", {}) or {}
    return {"ok": True, "content_id": content_id, "state_path": str(path),
            "status": state.get("status"),
            "approval_status": state.get("approval_status", "DRAFT"),
            "image_path": build.get("image_path"),
            "image_sha256": build.get("image_sha256"),
            "dimensions": plan.get("dimensions"),
            "visually_verified": False,
            "note": "Metadata only: no preview was visually verified.",
            "error": None}


def op_validate_content(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["item"])
    if err:
        return err
    item = payload["item"]
    if not isinstance(item, dict):
        return _op_error("INVALID_INPUT", "item must be an object")
    artifacts = payload.get("artifacts") or {}
    if not isinstance(artifacts, dict):
        return _op_error("INVALID_INPUT", "artifacts must be an object")
    try:
        import content_engine
    except Exception as e:
        return _op_error("MISSING_VALIDATOR",
                         "content_engine could not be imported: %s" % e)
    gate = getattr(content_engine, "gate", None)
    if gate is None or not callable(gate):
        return _op_error("MISSING_VALIDATOR",
                         "content_engine.gate is not implemented")
    try:
        decision = gate(item, artifacts)
    except Exception as e:
        return _op_error("VALIDATION_ERROR",
                         "content_engine.gate failed: %s" % e)
    if not isinstance(decision, dict):
        return _op_error("VALIDATION_ERROR",
                         "content_engine.gate returned a non-object")
    return {"ok": True, "content_id": decision.get("content_id"),
            "decision": decision.get("decision"),
            "reason": decision.get("reason"),
            "input_sha256": decision.get("input_sha256"),
            "gate": decision, "error": None}


def op_validate_image(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["image_path"])
    if err:
        return err
    image_path = payload["image_path"]
    if not isinstance(image_path, str) or not image_path.strip():
        return _op_error("INVALID_INPUT",
                         "image_path must be a non-empty string")
    try:
        import verify_output
    except Exception as e:
        return _op_error("MISSING_VALIDATOR",
                         "verify_output could not be imported: %s" % e)
    inspect = getattr(verify_output, "inspect_image", None)
    if inspect is None or not callable(inspect):
        return _op_error("MISSING_VALIDATOR",
                         "verify_output.inspect_image is not implemented yet "
                         "(Worker 3); refusing to fake an image inspection")
    try:
        inspection = inspect(image_path)
    except Exception as e:
        return _op_error("VALIDATION_ERROR",
                         "verify_output.inspect_image failed: %s" % e)
    return {"ok": True, "image_path": image_path, "inspection": inspection,
            "visually_verified": False,
            "note": "Mechanical inspection only: no preview was visually verified.",
            "error": None}


def op_get_batch_report(payload):
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir"])
    if err:
        return err
    summary_fn, err2 = _load_orchestrator_function("summary")
    if err2 is not None:
        return _op_error(err2["error"], err2["message"])
    try:
        report = summary_fn(payload["state_dir"])
    except FileNotFoundError as e:
        return _op_error("BATCH_NOT_FOUND",
                         "no batch manifest in state_dir: %s" % e)
    except Exception as e:
        return _op_error("ORCHESTRATOR_ERROR", "summary failed: %s" % e)
    return {"ok": True, "report": report, "error": None}


def op_submit_owner_decision(payload):
    """The ONLY path to approval.

    Requires {owner, content_id, decision APPROVE|REJECT, state_dir}
    (optional reason) AND the job state READY_FOR_OWNER_REVIEW. The
    decision is recorded in the evidence ledger via
    evidence_store.record_approval, then confirmed by a round-trip
    ledger verification via evidence_store.verify_approval (with a
    latest_approval fallback for REJECT decisions, which
    verify_approval may not count as valid). Only after verification
    is the job's approval_status set to OWNER_APPROVED /
    OWNER_REJECTED. READY_FOR_OWNER_REVIEW never equals OWNER_APPROVED.
    """
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["content_id", "decision", "state_dir"])
    if err:
        return err
    err = _op_identity(payload, "owner")
    if err:
        return err
    owner = payload["owner"]
    content_id = payload["content_id"]
    decision = payload["decision"]
    if decision not in ("APPROVE", "REJECT"):
        return _op_error("INVALID_INPUT", "decision must be APPROVE or REJECT")
    if not isinstance(content_id, str) or not content_id.strip():
        return _op_error("INVALID_INPUT", "content_id must be a non-empty string")
    state_path, perr = _job_state_path(payload["state_dir"], content_id)
    if perr is not None or not state_path.is_file():
        return _op_error("JOB_NOT_FOUND",
                         "no state file for content_id %r" % content_id)
    state = load(str(state_path))
    if state.get("approval_status") != "READY_FOR_OWNER_REVIEW":
        return {"ok": False, "error": "JOB_NOT_READY_FOR_OWNER_REVIEW",
                "message": "approval_status is %r, not READY_FOR_OWNER_REVIEW; "
                           "READY_FOR_OWNER_REVIEW never equals OWNER_APPROVED"
                           % (state.get("approval_status"),),
                "approval_status": state.get("approval_status"),
                "content_id": content_id}
    content_hash, image_hash = _current_hashes(state)
    if not content_hash or not image_hash:
        return {"ok": False, "error": "JOB_NOT_READY_FOR_OWNER_REVIEW",
                "message": "content/image hashes are missing from the job records; "
                           "cannot approve an unverified job",
                "approval_status": state.get("approval_status"),
                "content_id": content_id}
    record_approval, verr = _load_evidence_function("record_approval")
    if verr is not None:
        return _op_error(verr["error"], verr["message"])
    verify_approval, verr = _load_evidence_function("verify_approval")
    if verr is not None:
        return _op_error(verr["error"], verr["message"])
    latest_approval, _ = _load_evidence_function("latest_approval")
    try:
        import evidence_store
        db = evidence_store.init(str(Path(payload["state_dir"]) / "evidence.db"))
        try:
            record = record_approval(
                db, job_id=content_id, content_id=content_id,
                content_hash=content_hash, image_hash=image_hash,
                actor=owner, decision=decision, scope="owner_review",
                reason=payload.get("reason"))
            verification = verify_approval(
                db, job_id=content_id, content_id=content_id,
                content_hash=content_hash, image_hash=image_hash)
            latest = None
            if latest_approval is not None:
                try:
                    latest = latest_approval(db, job_id=content_id,
                                             content_id=content_id)
                except Exception:
                    latest = None
        finally:
            try:
                db.close()
            except Exception:
                pass
    except Exception as e:
        return _op_error("EVIDENCE_WRITE_FAILED",
                         "evidence ledger write/verification failed: %s" % e)
    verified = bool(isinstance(verification, dict) and verification.get("valid"))
    if (not verified and isinstance(latest, dict)
            and latest.get("decision") == decision
            and latest.get("content_hash") == content_hash
            and latest.get("image_hash") == image_hash):
        verified = True
    if not verified:
        return {"ok": False, "error": "APPROVAL_VERIFICATION_FAILED",
                "message": "ledger verification did not confirm the recorded "
                           "decision (verify_approval returned %r); approval NOT applied"
                           % (verification,),
                "content_id": content_id}
    state["approval_status"] = ("OWNER_APPROVED" if decision == "APPROVE"
                                else "OWNER_REJECTED")
    state.setdefault("trace", []).append(
        {"stage": "DELIVERY", "event": "OWNER_" + decision, "actor": owner,
         "at": _now_iso()})
    save(str(state_path), state)
    _op_audit(payload, "owner_decision:%s" % decision, True,
              {"content_id": content_id, "decision": decision})
    return {"ok": True, "content_id": content_id, "decision": decision,
            "approval_status": state["approval_status"],
            "approval_id": record.get("approval_id") if isinstance(record, dict) else None,
            "verified": True, "error": None}


def op_get_audit_report(payload):
    """Read the evidence ledger (if present) and bridge state files.

    If no ledger exists it reports that honestly instead of inventing
    audit history.
    """
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return _op_error("INVALID_INPUT", "payload must be an object")
    err = _op_invalid_if_missing(payload, ["state_dir"])
    if err:
        return err
    state_dir = Path(payload["state_dir"])
    ledger_path = state_dir / "evidence.db"
    ledger = {"exists": ledger_path.is_file(), "path": str(ledger_path),
              "counts": {}, "latest_approvals": []}
    if ledger["exists"]:
        try:
            conn = sqlite3.connect("file:%s?mode=ro" % ledger_path, uri=True)
            try:
                for table in ("evidence", "receipts", "approvals"):
                    try:
                        row = conn.execute(
                            "SELECT COUNT(*) FROM %s" % table).fetchone()
                        ledger["counts"][table] = row[0] if row else 0
                    except Exception:
                        ledger["counts"][table] = None
                try:
                    rows = conn.execute(
                        "SELECT job_id, content_hash, actor, decision, scope, "
                        "created_at FROM approvals ORDER BY created_at DESC "
                        "LIMIT 20").fetchall()
                    ledger["latest_approvals"] = [
                        {"job_id": r[0], "content_hash": r[1], "actor": r[2],
                         "decision": r[3], "scope": r[4], "created_at": r[5]}
                        for r in rows]
                except Exception:
                    pass
            finally:
                conn.close()
        except Exception as e:
            ledger["error"] = str(e)
    states = []
    if state_dir.is_dir():
        for p in sorted(state_dir.glob("*.json")):
            if p.name == "manifest.json":
                continue
            try:
                s = load(str(p))
                states.append({"content_id": s.get("job", {}).get("content_id"),
                               "status": s.get("status"),
                               "approval_status": s.get("approval_status", "DRAFT"),
                               "stage": s.get("index"),
                               "state_path": str(p)})
            except Exception as e:
                states.append({"state_path": str(p), "error": str(e)})
    return {"ok": True, "ledger": ledger, "states": states,
            "chatgpt": chatgpt_connection_status(), "error": None}


# ---------------------------------------------------------------------------
# Owner approval states: delivery handover and revalidation.
# ---------------------------------------------------------------------------

def mark_delivered(state_path, owner):
    """Set approval_status to DELIVERED, ONLY if it is OWNER_APPROVED
    and evidence_store.verify_approval confirms the approval still
    matches the current content/image hashes. Otherwise ok=False and
    nothing changes."""
    if not isinstance(owner, str) or not owner.strip():
        return {"ok": False, "error": "UNAUTHORIZED",
                "message": "owner identity is required"}
    try:
        state = load(str(state_path))
    except Exception as e:
        return {"ok": False, "error": "JOB_NOT_FOUND",
                "message": "state file unreadable: %s" % e}
    if state.get("approval_status") != "OWNER_APPROVED":
        return {"ok": False, "error": "JOB_NOT_READY_FOR_OWNER_REVIEW",
                "message": "approval_status is %r; only OWNER_APPROVED jobs "
                           "can be marked DELIVERED" % (state.get("approval_status"),),
                "approval_status": state.get("approval_status")}
    content_hash, image_hash = _current_hashes(state)
    if not content_hash or not image_hash:
        return {"ok": False, "error": "JOB_NOT_READY_FOR_OWNER_REVIEW",
                "message": "content/image hashes are missing from the job records",
                "approval_status": state.get("approval_status")}
    verify_approval, err = _load_evidence_function("verify_approval")
    if err is not None:
        return {"ok": False, "error": err["error"], "message": err["message"]}
    content_id = state.get("job", {}).get("content_id")
    state_dir = str(Path(state_path).parent)
    try:
        import evidence_store
        db = evidence_store.init(str(Path(state_dir) / "evidence.db"))
        try:
            verification = verify_approval(
                db, job_id=content_id, content_id=content_id,
                content_hash=content_hash, image_hash=image_hash)
        finally:
            try:
                db.close()
            except Exception:
                pass
    except Exception as e:
        return {"ok": False, "error": "EVIDENCE_WRITE_FAILED",
                "message": "evidence ledger verification failed: %s" % e}
    if not (isinstance(verification, dict) and verification.get("valid")):
        return {"ok": False, "error": "APPROVAL_VERIFICATION_FAILED",
                "message": "stored approval no longer matches current "
                           "content/image hashes: %r" % (verification,),
                "approval_status": "OWNER_APPROVED"}
    state["approval_status"] = "DELIVERED"
    state.setdefault("trace", []).append(
        {"stage": "DELIVERY", "event": "DELIVERED", "actor": owner,
         "at": _now_iso()})
    save(str(state_path), state)
    _audit_event(state_dir, content_id, "mark_delivered",
                 {"ok": True, "approval_status": "DELIVERED"})
    return {"ok": True, "content_id": content_id,
            "approval_status": "DELIVERED", "error": None}


def revalidate_approval(state_path):
    """Recompute current content/image hashes and call verify_approval.

    If the approval is invalid, reset approval_status to
    READY_FOR_OWNER_REVIEW and return {"valid": False, ...}. Jobs with
    no active OWNER_APPROVED approval return valid False with reason
    NO_ACTIVE_APPROVAL and change nothing.
    """
    try:
        state = load(str(state_path))
    except Exception as e:
        return {"ok": False, "valid": False, "error": "JOB_NOT_FOUND",
                "message": "state file unreadable: %s" % e}
    current = state.get("approval_status", "DRAFT")
    content_id = state.get("job", {}).get("content_id")
    if current != "OWNER_APPROVED":
        return {"ok": True, "valid": False, "reason": "NO_ACTIVE_APPROVAL",
                "approval_status": current, "content_id": content_id}
    content_hash, image_hash = _current_hashes(state)
    verify_approval, err = _load_evidence_function("verify_approval")
    if err is not None:
        return {"ok": False, "valid": False, "error": err["error"],
                "message": err["message"], "approval_status": current}
    state_dir = str(Path(state_path).parent)
    try:
        import evidence_store
        db = evidence_store.init(str(Path(state_dir) / "evidence.db"))
        try:
            verification = verify_approval(
                db, job_id=content_id, content_id=content_id,
                content_hash=content_hash, image_hash=image_hash)
        finally:
            try:
                db.close()
            except Exception:
                pass
    except Exception as e:
        return {"ok": False, "valid": False, "error": "EVIDENCE_WRITE_FAILED",
                "message": "evidence ledger verification failed: %s" % e,
                "approval_status": current}
    if isinstance(verification, dict) and verification.get("valid"):
        return {"ok": True, "valid": True, "approval_status": "OWNER_APPROVED",
                "content_id": content_id}
    state["approval_status"] = "READY_FOR_OWNER_REVIEW"
    save(str(state_path), state)
    return {"ok": True, "valid": False,
            "reason": verification.get("reason", "APPROVAL_NO_LONGER_MATCHES")
                      if isinstance(verification, dict) else "APPROVAL_NO_LONGER_MATCHES",
            "approval_status": "READY_FOR_OWNER_REVIEW",
            "content_id": content_id}


def main(argv=None):
    """CLI entry point.

    Legacy form (unchanged): start/next/submit/status with
    --state/--job/--stage/--adapter/--role/--receipt. --test forces
    TEST_FIXTURE mode on start; --single-content resolves --state when
    it points at a directory of job files.

    Command-word form: ``erudiance_linkdin <action> [flags]`` (also
    accepts the ``erudience_linkdin`` alias and ``@Erudience``), where
    <action> is one of START/RESUME/STATUS/TEST/VALIDATE/RETRY/CANCEL/
    OWNER_REVIEW/APPROVE/REJECT/READ/DO/GO/WRITE. Flags: --state-dir
    (required), --topics (comma-separated, 7 for START; omit to
    auto-generate 7 topics), --cycle,
    --content-id, --owner/--operator, --decision, --reason, --path,
    --step, --strategy, --mode, --test (fixture mode), --single-content
    <ID>. Prints the dispatch result as JSON; exit code 1 on failure.
    """
    raw = list(sys.argv[1:] if argv is None else argv)
    command_word = None
    if raw and raw[0].lower() in ("erudiance_linkdin", "erudience_linkdin", "@erudience"):
        command_word = raw.pop(0)
    if command_word is not None:
        p = argparse.ArgumentParser(prog=command_word)
        p.add_argument("action", nargs="?", default="START")
        p.add_argument("--state-dir", default=None)
        p.add_argument("--state", default=None)
        p.add_argument("--topics", default=None)
        p.add_argument("--cycle", default=None)
        p.add_argument("--content-id", default=None)
        p.add_argument("--owner", default=None)
        p.add_argument("--operator", default=None)
        p.add_argument("--decision", default=None)
        p.add_argument("--reason", default=None)
        p.add_argument("--path", default=None)
        p.add_argument("--step", default=None)
        p.add_argument("--strategy", default=None)
        p.add_argument("--mode", default="TEST_FIXTURE")
        p.add_argument("--test", action="store_true")
        p.add_argument("--single-content", default=None)
        a = p.parse_args(raw)
        state_dir = a.state_dir or a.state
        if not state_dir:
            p.error("--state-dir is required for command-word invocations")
        owner = a.owner or a.operator
        args = {"action": a.action.upper()}
        if a.topics:
            args["topics"] = [t.strip() for t in a.topics.split(",") if t.strip()]
        if a.cycle:
            args["cycle"] = a.cycle
        if a.content_id:
            args["content_id"] = a.content_id
        if a.single_content:
            args["single_content"] = a.single_content
            args.setdefault("content_id", a.single_content)
        if a.decision:
            args["decision"] = a.decision
        if a.reason:
            args["reason"] = a.reason
        if a.path:
            args["path"] = a.path
        if a.step:
            args["step"] = a.step
        if a.strategy:
            args["strategy"] = a.strategy
        args["mode"] = a.mode
        args["test"] = bool(a.test)
        out = dispatch_command(command_word, args, state_dir, owner=owner)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["start", "next", "submit", "status"])
    p.add_argument("--state", required=True)
    p.add_argument("--job")
    p.add_argument("--stage")
    p.add_argument("--adapter")
    p.add_argument("--role", default="producer")
    p.add_argument("--receipt")
    p.add_argument("--test", action="store_true")
    p.add_argument("--single-content", default=None)
    a = p.parse_args(raw)
    state_path = a.state
    if a.single_content and Path(state_path).is_dir():
        state_path = str(Path(state_path) / ("%s.json" % a.single_content))
    if a.command == "start":
        job = load(a.job)
        if a.test:
            job["mode"] = "TEST_FIXTURE"
        out = start(state_path, job)
    elif a.command == "next":
        out = next_step(load(state_path))
    elif a.command == "status":
        out = load(state_path)
    else:
        if not all([a.stage, a.adapter, a.receipt]):
            p.error("submit requires --stage --adapter --receipt")
        out = submit(state_path, a.stage, a.adapter, a.role, load(a.receipt))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0
if __name__=='__main__':sys.exit(main())
