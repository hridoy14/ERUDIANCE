"""Erudiance Automation API server — ChatGPT custom-connector front end.

Read-only gateway to the Erudiance plugin's ChatGPT bridge
(``core/chatgpt_bridge_v43.py``). ChatGPT may RUN automation through this
server and NOTHING else:

- Allowed: the 13 run-only operations in ALLOWED_OPS below.
- DENIED: ``submit_owner_decision`` (owner approval) — 403, before any
  dispatch. There is NO other write path: no endpoint here writes code,
  config, brand policy, or publishes/schedules anything.

Standard library only (no pip packages). The plugin repository is used
read-only as an import source; this server lives outside the repo and
never writes into it.

Run:
  ERUDIANCE_API_KEY='<secret>' python3 server.py
Optional env:
  ERUDIANCE_STATE_DIR   job state root (default: <server-dir>/state)
  ERUDIANCE_PLUGIN_ROOT plugin root override
                          (default: ../erudiance-plugin-work/ERUDIANCE/erudience-plugin)
  PORT                  listen port (default 8765)
"""
import hashlib
import hmac
import json
import os
import sys
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ---------------------------------------------------------------------------
# Path bootstrap — identical to erudience-plugin/tests/__init__.py so the
# bridge's bare imports (gate_chain_v41, batch_guard_v45, ...) resolve.
# ---------------------------------------------------------------------------
SERVER_DIR = Path(__file__).resolve().parent
# The server lives inside the plugin (erudience-plugin/server/), so the
# plugin root is the server dir's parent. The env override is kept for
# deployments where the plugin sits elsewhere.
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
# Configuration — fail loudly instead of inventing a key.
# ---------------------------------------------------------------------------
API_KEY = os.environ.get("ERUDIANCE_API_KEY")
if not API_KEY:
    sys.stderr.write(
        "ERROR: ERUDIANCE_API_KEY is not set. Refusing to start.\n"
        "Set it to a long random secret, e.g.:\n"
        "  export ERUDIANCE_API_KEY=$(python3 -c "
        "\"import secrets;print(secrets.token_urlsafe(32))\")\n")
    sys.exit(2)

STATE_DIR = Path(os.environ.get("ERUDIANCE_STATE_DIR",
                                str(SERVER_DIR / "state"))).resolve()
STATE_DIR.mkdir(parents=True, exist_ok=True)

PORT = int(os.environ.get("PORT", "8765"))
MAX_BODY_BYTES = 1_000_000
RATE_LIMIT_PER_MINUTE = 60

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
}
# Explicit deny, checked BEFORE any dispatch. Owner approval is never
# available to ChatGPT; only the owner decides (op_submit_owner_decision
# is not imported, not routed, and not present in openapi.json).
DENIED_OPS = {"submit_owner_decision"}

# Rate limit: timestamps of accepted /ops calls in the last 60 seconds.
_request_times = deque()


def _rate_limited():
    now = time.monotonic()
    while _request_times and _request_times[0] <= now - 60:
        _request_times.popleft()
    if len(_request_times) >= RATE_LIMIT_PER_MINUTE:
        return True
    _request_times.append(now)
    return False


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # -- helpers ---------------------------------------------------------
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _log(self, status):
        # Method + path + status ONLY. Never the key or payload contents.
        sys.stderr.write("%s %s -> %s\n" % (self.command, self.path, status))
        sys.stderr.flush()

    def _check_auth(self):
        """Constant-time API-key check. Returns True when authorized."""
        supplied = self.headers.get("X-Api-Key")
        if not supplied:
            return False
        return hmac.compare_digest(supplied, API_KEY)

    def _read_json_body(self):
        """Returns (payload, error_response). error_response is None on ok."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None, (400, {"ok": False, "error": "INVALID_REQUEST"})
        if length > MAX_BODY_BYTES:
            return None, (413, {"ok": False, "error": "PAYLOAD_TOO_LARGE"})
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}, None
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None, (400, {"ok": False, "error": "INVALID_JSON"})
        if not isinstance(payload, dict):
            return None, (400, {"ok": False,
                                "error": "INVALID_REQUEST",
                                "message": "JSON body must be an object"})
        return payload, None

    # -- routes ----------------------------------------------------------
    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"ok": True,
                                  "service": "erudiance-automation",
                                  # Honest until a real ChatGPT request
                                  # succeeds through this server.
                                  "chatgpt_connected": False})
            self._log(200)
            return
        if self.path == "/openapi.json":
            spec_path = SERVER_DIR / "openapi.json"
            try:
                data = spec_path.read_bytes()
            except OSError:
                self._send_json(500, {"ok": False, "error": "INTERNAL"})
                self._log(500)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            self._log(200)
            return
        if self.path.startswith("/ops/"):
            self._send_json(405, {"ok": False, "error": "METHOD_NOT_ALLOWED"})
            self._log(405)
            return
        self._send_json(404, {"ok": False, "error": "NOT_FOUND"})
        self._log(404)

    def do_POST(self):
        if not self.path.startswith("/ops/"):
            self._send_json(404, {"ok": False, "error": "NOT_FOUND"})
            self._log(404)
            return
        if not self._check_auth():
            self._send_json(401, {"ok": False, "error": "UNAUTHORIZED"})
            self._log(401)
            return
        if _rate_limited():
            self._send_json(429, {"ok": False, "error": "RATE_LIMITED"})
            self._log(429)
            return
        op_name = self.path[len("/ops/"):].split("?", 1)[0].strip("/")
        # Owner-only deny, BEFORE any dispatch.
        if op_name in DENIED_OPS:
            self._send_json(403, {
                "ok": False,
                "error": "FORBIDDEN_OWNER_ONLY",
                "message": "Owner approval is never available to ChatGPT; "
                           "only the owner decides."})
            self._log(403)
            return
        fn = ALLOWED_OPS.get(op_name)
        if fn is None:
            self._send_json(404, {"ok": False, "error": "UNKNOWN_OPERATION"})
            self._log(404)
            return
        payload, err = self._read_json_body()
        if err is not None:
            self._send_json(err[0], err[1])
            self._log(err[0])
            return
        # Default state root when the caller does not name one. A caller
        # supplied state_dir is passed through unchanged; the bridge/gate
        # enforces its own live-mode path confinement.
        if "state_dir" not in payload:
            payload["state_dir"] = str(STATE_DIR)
        try:
            result = fn(payload)
        except Exception:
            # Never leak a stack trace (or payload) in the response.
            self._send_json(500, {"ok": False, "error": "INTERNAL"})
            self._log(500)
            return
        if not isinstance(result, dict):
            result = {"ok": False, "error": "INTERNAL"}
        self._send_json(200, result)
        self._log(200)

    def log_message(self, fmt, *args):
        # Suppress default access logging (it would print full paths only,
        # but _log above is the single controlled log line per request).
        pass


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    sys.stderr.write(
        "Erudiance Automation API listening on 0.0.0.0:%d\n"
        "plugin root: %s\nstate dir:   %s\n"
        "allowed ops: %d (submit_owner_decision DENIED)\n"
        % (PORT, PLUGIN_ROOT, STATE_DIR, len(ALLOWED_OPS)))
    sys.stderr.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
