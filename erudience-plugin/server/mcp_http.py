"""Erudiance Automation MCP server — Claude custom-connector front end.

Streamable HTTP MCP server (JSON-RPC 2.0 over POST /mcp) exposing the
SAME tools as the stdio MCP server (``mcp_server.py``): the 13 run-only
operations plus the 3 template-store tools (save/list/get_template).
This is what claude.ai connects to as a custom connector
(Customize -> Connectors -> Add custom connector -> URL + API key).

Owner access rule (2026-11-24, decisions.json: claude_access):
- NO repo access, NEVER change any code.
- Only generate content and build images; templates may be created and
  stored as data; all data stays on the server.
- ``submit_owner_decision`` (owner approval) is NOT a tool and is
  refused if called by name. Only the owner decides, in person.
  There is NO other write path: no tool here writes code, config,
  brand policy, or publishes/schedules anything.

Standard library only (no pip packages). The plugin repository is used
read-only as an import source; this server never writes into it. Job
state and templates live in the state dir (default ``<server-dir>/state``,
or ERUDIANCE_STATE_DIR), shared with the stdio MCP server and the
ChatGPT HTTP server.

Auth: X-Api-Key header, key from env ERUDIANCE_API_KEY only. The
server exits (code 2) if the key is unset — it never generates or
hardcodes one. 60 requests/minute per IP, then 429.

Run:
  ERUDIANCE_API_KEY=<key> python mcp_http.py        # port 8766, or $PORT
  ERUDIANCE_STATE_DIR=/path/to/state python mcp_http.py
Endpoints:
  POST /mcp     JSON-RPC 2.0 (single JSON response; notifications get 202)
  GET  /health  public, no key: {"ok": true, ...}
  GET  /mcp     405 (this endpoint takes POST only)
Anything else: 404. Errors never leak stack traces; logs carry
method + path + status only.
"""
import hmac
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SERVER_DIR))
import mcp_server  # noqa: E402  (reuses its tools, dispatch, template store)

API_KEY = os.environ.get("ERUDIANCE_API_KEY")
if not API_KEY:
    sys.stderr.write(
        "ERUDIANCE_API_KEY is not set; refusing to start.\n"
        "Set it to a secret key (the same key goes into the Claude "
        "custom connector as the X-Api-Key request header).\n")
    sys.exit(2)

PORT = int(os.environ.get("PORT", "8766"))
RATE_LIMIT = 60          # requests per IP per minute
RATE_WINDOW = 60.0       # seconds
MAX_BODY = 1_000_000     # bytes

_hits = {}               # ip -> [timestamps]
_hits_lock = threading.Lock()


def _rate_limited(ip):
    now = time.monotonic()
    with _hits_lock:
        stamps = [t for t in _hits.get(ip, []) if now - t < RATE_WINDOW]
        if len(stamps) >= RATE_LIMIT:
            _hits[ip] = stamps
            return True
        stamps.append(now)
        _hits[ip] = stamps
        return False


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # keep stdout clean
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))
        sys.stderr.flush()

    # -- helpers ---------------------------------------------------------
    def _send_json(self, status, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        key = self.headers.get("X-Api-Key")
        return bool(key) and hmac.compare_digest(key, API_KEY)

    def _client_ip(self):
        return self.client_address[0]

    # -- routes ----------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send_json(200, {
                "ok": True, "transport": "mcp-streamable-http",
                "server": mcp_server.SERVER_NAME,
                "version": mcp_server.SERVER_VERSION,
                "protocol": mcp_server.PROTOCOL_VERSION,
                "tools": len(mcp_server.TOOLS),
                "owner_decision_exposed": False})
        elif path == "/mcp":
            self._send_json(405, {"error": "METHOD_NOT_ALLOWED",
                                  "message": "/mcp takes POST only"})
        else:
            self._send_json(404, {"error": "NOT_FOUND"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/mcp":
            self._send_json(404, {"error": "NOT_FOUND"})
            return
        if not self._authed():
            self._send_json(401, {"error": "UNAUTHORIZED"})
            return
        if _rate_limited(self._client_ip()):
            self._send_json(429, {"error": "RATE_LIMITED",
                                  "message": "60 requests/minute per IP"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self._send_json(400, {"jsonrpc": "2.0", "id": None,
                                  "error": {"code": -32600,
                                            "message": "Invalid Request"}})
            return
        try:
            request = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"jsonrpc": "2.0", "id": None,
                                  "error": {"code": -32700,
                                            "message": "Parse error"}})
            return
        if not isinstance(request, dict):
            self._send_json(400, {"jsonrpc": "2.0", "id": None,
                                  "error": {"code": -32600,
                                            "message": "Invalid Request"}})
            return
        try:
            response = mcp_server._handle(request)
        except Exception as exc:  # never leak a stack trace
            sys.stderr.write("mcp request failed: %s\n" % exc)
            sys.stderr.flush()
            self._send_json(500, {"jsonrpc": "2.0",
                                  "id": request.get("id"),
                                  "error": {"code": -32603,
                                            "message": "Internal error"}})
            return
        if response is None:
            # Notification (e.g. notifications/initialized): no reply.
            self.send_response(202)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self._send_json(200, response)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    sys.stderr.write(
        "Erudiance Automation MCP (Streamable HTTP) listening on :%d\n"
        "endpoint:   POST /mcp  (JSON-RPC 2.0, X-Api-Key required)\n"
        "health:     GET  /health\n"
        "plugin root: %s\nstate dir:   %s\n"
        "tools: %d (submit_owner_decision DENIED)\n"
        % (PORT, mcp_server.PLUGIN_ROOT, mcp_server.STATE_DIR,
           len(mcp_server.TOOLS)))
    sys.stderr.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
