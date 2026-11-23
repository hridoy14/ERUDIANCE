"""Erudiance Automation MCP server — Claude front end.

Stdio MCP server (JSON-RPC 2.0, newline-delimited) exposing the SAME 13
run-only operations as the ChatGPT HTTP server (``server.py``) to Claude
(Claude Desktop, Claude Code, or any MCP client), plus 3 template-store
tools (save/list/get_template — plain JSON data, never code):

- Allowed: the 13 run-only operations in TOOLS below.
- DENIED: ``submit_owner_decision`` (owner approval) is NOT a tool and
  is refused if called by name. Only the owner decides, in person.
  There is NO other write path: no tool here writes code, config,
  brand policy, or publishes/schedules anything.

Standard library only (no pip packages). This file does NOT import
``server.py`` — that module exits without ERUDIANCE_API_KEY, which an
MCP stdio server does not need: the process runs locally as the owner,
so there is no API key. The plugin repository is used read-only as an
import source; this server never writes into it. Job state lives in
the state dir (default ``<server-dir>/state``), shared with the HTTP
server, so a job started over MCP is visible over HTTP and vice versa.

Run (Claude Desktop config, Windows example — use YOUR repo path):
  {
    "mcpServers": {
      "erudiance": {
        "command": "python",
        "args": ["C:\\path\\to\\ERUDIANCE\\erudience-plugin\\server\\mcp_server.py"],
        "env": {"ERUDIANCE_STATE_DIR": "C:\\path\\to\\erudiance-state"}
      }
    }
  }
Optional env:
  ERUDIANCE_STATE_DIR   job state root (default: <server-dir>/state)
  ERUDIANCE_PLUGIN_ROOT plugin root override
                          (default: <server-dir>/.. = erudience-plugin)

Protocol: MCP 2024-11-05 (initialize, ping, tools/list, tools/call).
Logging goes to stderr only — stdout is the protocol.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path bootstrap — identical to server.py so the bridge's bare imports
# (gate_chain_v41, batch_guard_v45, ...) resolve.
# ---------------------------------------------------------------------------
SERVER_DIR = Path(__file__).resolve().parent
# The server lives inside the plugin (erudience-plugin/server/), so the
# plugin root is the server dir's parent. The env override is kept for
# setups where the plugin sits elsewhere.
DEFAULT_PLUGIN_ROOT = SERVER_DIR.parent
PLUGIN_ROOT = Path(os.environ.get("ERUDIANCE_PLUGIN_ROOT",
                                  str(DEFAULT_PLUGIN_ROOT))).resolve()
for _d in ("core", "core/legacy", "rendering",
           "modules/brand_claims_qa", "modules/creative_brief",
           "modules/competitor_intelligence", "modules/linkedin_copywriting",
           "modules/topic_intelligence", "modules/analytics_learning",
           "modules/marketing_strategy", "tests"):
    _p = str(PLUGIN_ROOT / _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import chatgpt_bridge_v43  # noqa: E402  (after sys.path bootstrap)

# ---------------------------------------------------------------------------
# Configuration.
# ---------------------------------------------------------------------------
STATE_DIR = Path(os.environ.get("ERUDIANCE_STATE_DIR",
                                str(SERVER_DIR / "state"))).resolve()
STATE_DIR.mkdir(parents=True, exist_ok=True)

SERVER_NAME = "erudiance-automation"
SERVER_VERSION = "4.9.2"
PROTOCOL_VERSION = "2024-11-05"

# ---------------------------------------------------------------------------
# Template store — data only, never code.
#
# A template is a plain JSON layout definition (name, kind, blocks, ...)
# stored as <state-dir>/templates/<slug>.json. Claude may CREATE a
# template and STORE it here (owner rule, 2026-11-24), and the renderer
# later reads the stored definition to draw the poster. Nothing stored
# here is executed: the file is JSON data, validated on write, and the
# slug is restricted so no path can escape the templates dir.
# ---------------------------------------------------------------------------
TEMPLATE_KINDS = {"tips", "promotion", "case-study", "comparison",
                  "announcement", "quote", "checklist", "myth-fact",
                  "testimonial", "event", "custom"}
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_TEMPLATE_KEYS = {"slug", "name", "kind", "version", "blocks",
                  "description", "colors", "created_by", "updated_at"}
_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _templates_dir(state_dir):
    d = Path(state_dir) / "templates"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _utcnow():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_template(data):
    """Check a template definition is plain data in the allowed shape.
    Returns (ok, error_message)."""
    if not isinstance(data, dict):
        return False, "template must be an object"
    extra = set(data) - _TEMPLATE_KEYS
    if extra:
        return False, "unknown template keys: %s" % sorted(extra)
    name = data.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > 120:
        return False, "name must be a non-empty string (max 120 chars)"
    if data.get("kind") not in TEMPLATE_KINDS:
        return False, "kind must be one of: %s" % sorted(TEMPLATE_KINDS)
    version = data.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        return False, "version must be an integer >= 1"
    blocks = data.get("blocks")
    if not isinstance(blocks, list) or not blocks or len(blocks) > 20:
        return False, "blocks must be a non-empty list (max 20)"
    for i, b in enumerate(blocks):
        if not isinstance(b, dict) or not isinstance(b.get("type"), str) \
                or not b["type"].strip():
            return False, "blocks[%d] must be an object with a non-empty 'type'" % i
    desc = data.get("description")
    if desc is not None and (not isinstance(desc, str) or len(desc) > 500):
        return False, "description must be a string (max 500 chars)"
    colors = data.get("colors")
    if colors is not None:
        if not isinstance(colors, dict):
            return False, "colors must be an object of hex strings"
        for k, v in colors.items():
            if not isinstance(v, str) or not _HEX_RE.match(v):
                return False, "colors[%s] must be a #RRGGBB hex string" % k
    return True, ""


def _save_template(arguments):
    slug = arguments.get("slug")
    if not isinstance(slug, str) or not _SLUG_RE.match(slug):
        return {"ok": False, "error": "INVALID_INPUT",
                "message": "slug must match [a-z0-9][a-z0-9-]{0,63}"}
    data = arguments.get("template")
    ok, err = _validate_template(data if isinstance(data, dict) else None)
    if not ok:
        return {"ok": False, "error": "INVALID_INPUT", "message": err}
    data = dict(data)
    data["slug"] = slug
    operator = arguments.get("operator")
    if isinstance(operator, str) and operator.strip():
        data["created_by"] = operator.strip()
    data["updated_at"] = _utcnow()
    target = _templates_dir(arguments["state_dir"]) / (slug + ".json")
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(target)  # atomic within the templates dir
    return {"ok": True, "slug": slug, "version": data["version"],
            "path": str(target)}


def _list_templates(arguments):
    d = _templates_dir(arguments["state_dir"])
    out = []
    for f in sorted(d.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        out.append({"slug": data.get("slug", f.stem),
                    "name": data.get("name"),
                    "kind": data.get("kind"),
                    "version": data.get("version"),
                    "updated_at": data.get("updated_at")})
    return {"ok": True, "templates": out, "count": len(out)}


def _get_template(arguments):
    slug = arguments.get("slug")
    if not isinstance(slug, str) or not _SLUG_RE.match(slug):
        return {"ok": False, "error": "INVALID_INPUT",
                "message": "slug must match [a-z0-9][a-z0-9-]{0,63}"}
    target = _templates_dir(arguments["state_dir"]) / (slug + ".json")
    if not target.exists():
        return {"ok": False, "error": "NOT_FOUND",
                "message": "no template named %r" % slug}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return {"ok": False, "error": "INTERNAL",
                "message": "stored template is unreadable: %s" % exc}
    return {"ok": True, "template": data}

# ---------------------------------------------------------------------------
# Operation allowlist / denylist (the owner's access rule).
# ---------------------------------------------------------------------------
ALLOWED_OPS = {
    "get_system_status": chatgpt_bridge_v43.op_get_system_status,
    "list_agent_capabilities": chatgpt_bridge_v43.op_list_agent_capabilities,
    "start_workflow": chatgpt_bridge_v43.op_start_workflow,
    "get_workflow_status": chatgpt_bridge_v43.op_get_workflow_status,
    "execute_authorized_step": chatgpt_bridge_v43.op_execute_authorized_step,
    "resume_workflow": chatgpt_bridge_v43.op_resume_workflow,
    "get_agent_report": chatgpt_bridge_v43.op_get_agent_report,
    "get_content_preview": chatgpt_bridge_v43.op_get_content_preview,
    "get_image_preview": chatgpt_bridge_v43.op_get_image_preview,
    "validate_content": chatgpt_bridge_v43.op_validate_content,
    "validate_image": chatgpt_bridge_v43.op_validate_image,
    "get_batch_report": chatgpt_bridge_v43.op_get_batch_report,
    "get_audit_report": chatgpt_bridge_v43.op_get_audit_report,
    # Template store (data only — see above). Claude may create and store
    # template definitions; it never writes code.
    "save_template": _save_template,
    "list_templates": _list_templates,
    "get_template": _get_template,
}
# Explicit deny, checked BEFORE any dispatch. Owner approval is never
# available to Claude; only the owner decides (op_submit_owner_decision
# is not imported, not routed, and not listed as a tool).
DENIED_OPS = {"submit_owner_decision"}

# ---------------------------------------------------------------------------
# Tool definitions (name, description, JSON Schema for arguments).
# ``state_dir`` is optional on every tool: when the caller omits it the
# server's own state dir is used, exactly like the HTTP server.
# ---------------------------------------------------------------------------
_STR = {"type": "string"}
_OPT_STATE_DIR = {"type": "string",
                  "description": "Job state directory. Omit to use the "
                                 "server's own state dir."}

TOOLS = [
    {"name": "get_system_status",
     "description": "Report gate/bridge/batch versions, provider statuses, "
                    "and approval state. Never claims CONNECTED.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "list_agent_capabilities",
     "description": "List the 18 specialist agent roles and what each can do.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "start_workflow",
     "description": "Start a 7-job content batch (7 distinct topics, one "
                    "cycle). Live mode needs 7 slots with exactly 1 promotion; "
                    "TEST_FIXTURE mode runs the same pipeline on fixtures.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "topics": {"type": "array", "items": _STR,
                                    "minItems": 7, "maxItems": 7,
                                    "description": "Exactly 7 distinct non-empty topics."},
                         "cycle": {"type": "string",
                                   "description": "Cycle id, e.g. 20261124."},
                         "operator": {"type": "string",
                                      "description": "Who runs it (a name). Required."},
                         "mode": {"type": "string",
                                  "description": "TEST_FIXTURE (default) or live mode."},
                         "strategy": {"type": "object",
                                      "description": "Optional strategy overrides."},
                         "state_dir": _OPT_STATE_DIR},
                     "required": ["topics", "cycle", "operator"],
                     "additionalProperties": False}},
    {"name": "get_workflow_status",
     "description": "Status of the current batch, or of one job by content_id.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "content_id": {"type": "string"},
                         "single_content": {"type": "boolean"},
                         "operator": {"type": "string"},
                         "state_dir": _OPT_STATE_DIR},
                     "additionalProperties": False}},
    {"name": "execute_authorized_step",
     "description": "Run one authorized step (DO) of a job. Never approves "
                    "or publishes anything.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "step": {"type": "string",
                                  "description": "Stage name to execute, e.g. CONTENT."},
                         "operator": {"type": "string",
                                      "description": "Who runs it (a name). Required."},
                         "content_id": {"type": "string"},
                         "single_content": {"type": "boolean"},
                         "strategy": {"type": "object"},
                         "state_dir": _OPT_STATE_DIR},
                     "required": ["step", "operator"],
                     "additionalProperties": False}},
    {"name": "resume_workflow",
     "description": "Resume a blocked or interrupted job by content_id.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "content_id": {"type": "string"},
                         "operator": {"type": "string",
                                      "description": "Who runs it (a name). Required."},
                         "mode": {"type": "string"},
                         "state_dir": _OPT_STATE_DIR},
                     "required": ["content_id", "operator"],
                     "additionalProperties": False}},
    {"name": "get_agent_report",
     "description": "Per-job agent report (status, stage, repairs), or the "
                    "whole batch summary when content_id is omitted.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "content_id": {"type": "string"},
                         "state_dir": _OPT_STATE_DIR},
                     "additionalProperties": False}},
    {"name": "get_content_preview",
     "description": "Caption, poster text and hashes for one job (metadata "
                    "only — never claims a preview was visually verified).",
     "inputSchema": {"type": "object",
                     "properties": {
                         "content_id": {"type": "string"},
                         "state_dir": _OPT_STATE_DIR},
                     "required": ["content_id"],
                     "additionalProperties": False}},
    {"name": "get_image_preview",
     "description": "Poster file path, hash and dimensions for one job "
                    "(metadata only — never claims a preview was visually verified).",
     "inputSchema": {"type": "object",
                     "properties": {
                         "content_id": {"type": "string"},
                         "state_dir": _OPT_STATE_DIR},
                     "required": ["content_id"],
                     "additionalProperties": False}},
    {"name": "validate_content",
     "description": "Run the content gate on one content item.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "item": {"type": "object",
                                  "description": "Content item to validate."},
                         "artifacts": {"type": "object"}},
                     "required": ["item"],
                     "additionalProperties": False}},
    {"name": "validate_image",
     "description": "Mechanically inspect a poster image (size, format, "
                    "hash). Visual verification is a separate human step.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "image_path": {"type": "string",
                                        "description": "Path to the PNG to inspect."}},
                     "required": ["image_path"],
                     "additionalProperties": False}},
    {"name": "get_batch_report",
     "description": "Summary report for the batch in the state dir.",
     "inputSchema": {"type": "object",
                     "properties": {"state_dir": _OPT_STATE_DIR},
                     "additionalProperties": False}},
    {"name": "get_audit_report",
     "description": "Read the evidence ledger (counts, latest approvals). "
                    "Reports honestly when no ledger exists.",
     "inputSchema": {"type": "object",
                     "properties": {"state_dir": _OPT_STATE_DIR},
                     "additionalProperties": False}},
    {"name": "save_template",
     "description": "Save a poster template definition (plain JSON data: "
                    "name, kind, version, blocks) under a slug, in the "
                    "server's template store. Templates are data, never "
                    "code — nothing stored here is executed.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "slug": {"type": "string",
                                  "description": "Lowercase letters, digits and "
                                                 "dashes, e.g. 'promo-offer'."},
                         "template": {"type": "object",
                                      "description": "Template definition: name, "
                                                     "kind, version, blocks."},
                         "operator": {"type": "string"},
                         "state_dir": _OPT_STATE_DIR},
                     "required": ["slug", "template"],
                     "additionalProperties": False}},
    {"name": "list_templates",
     "description": "List the stored poster templates (slug, name, kind, "
                    "version).",
     "inputSchema": {"type": "object",
                     "properties": {"state_dir": _OPT_STATE_DIR},
                     "additionalProperties": False}},
    {"name": "get_template",
     "description": "Read one stored poster template definition by slug.",
     "inputSchema": {"type": "object",
                     "properties": {
                         "slug": {"type": "string"},
                         "state_dir": _OPT_STATE_DIR},
                     "required": ["slug"],
                     "additionalProperties": False}},
]
_TOOLS_BY_NAME = {t["name"]: t for t in TOOLS}


def _log(msg):
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()


def _send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message}}


def _tool_result_text(payload):
    """One text block carrying the op result as JSON."""
    return {"content": [{"type": "text",
                         "text": json.dumps(payload, ensure_ascii=False)}],
            "isError": not (isinstance(payload, dict)
                            and payload.get("ok") is True)}


def _dispatch_tool(name, arguments):
    """Run one allowed op. Returns the MCP tools/call result object."""
    if name in DENIED_OPS:
        return _tool_result_text(
            {"ok": False, "error": "FORBIDDEN_OWNER_ONLY",
             "message": "Owner approval is never available to Claude; "
                        "only the owner decides."})
    fn = ALLOWED_OPS.get(name)
    if fn is None:
        return _tool_result_text(
            {"ok": False, "error": "UNKNOWN_OPERATION",
             "message": "unknown tool %r" % name})
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        return _tool_result_text(
            {"ok": False, "error": "INVALID_INPUT",
             "message": "arguments must be an object"})
    # Default state root when the caller does not name one, exactly
    # like the HTTP server.
    if "state_dir" not in arguments:
        arguments["state_dir"] = str(STATE_DIR)
    try:
        result = fn(arguments)
    except Exception as exc:  # never leak a stack trace
        _log("tool %s failed: %s" % (name, exc))
        return _tool_result_text({"ok": False, "error": "INTERNAL"})
    if not isinstance(result, dict):
        result = {"ok": False, "error": "INTERNAL"}
    return _tool_result_text(result)


def _handle(request):
    """Handle one JSON-RPC request. Returns the response object, or None
    for notifications (no reply)."""
    if not isinstance(request, dict):
        return _error(None, -32600, "Invalid Request")
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params") or {}
    if not isinstance(params, dict):
        return _error(req_id, -32602, "params must be an object")

    # Notifications have no id and get no reply.
    if req_id is None:
        return None

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME,
                                   "version": SERVER_VERSION}}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id,
                "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = params.get("name")
        if not isinstance(name, str) or not name:
            return _error(req_id, -32602, "tools/call requires a tool name")
        return {"jsonrpc": "2.0", "id": req_id,
                "result": _dispatch_tool(name, params.get("arguments"))}
    if method in ("resources/list", "prompts/list"):
        key = "resources" if method == "resources/list" else "prompts"
        return {"jsonrpc": "2.0", "id": req_id, "result": {key: []}}
    return _error(req_id, -32601, "Method not found: %s" % method)


def main():
    _log("Erudiance Automation MCP server listening on stdio\n"
         "plugin root: %s\nstate dir:   %s\n"
         "allowed tools: %d (submit_owner_decision DENIED)"
         % (PLUGIN_ROOT, STATE_DIR, len(TOOLS)))
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except ValueError:
            _send(_error(None, -32700, "Parse error"))
            continue
        try:
            response = _handle(request)
        except Exception as exc:  # never crash the loop on one request
            _log("request failed: %s" % exc)
            response = _error(request.get("id") if isinstance(request, dict) else None,
                              -32603, "Internal error")
        if response is not None:
            _send(response)


if __name__ == "__main__":
    main()
