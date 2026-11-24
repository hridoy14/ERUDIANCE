"""Erudiance Automation MCP server — Claude custom-connector front end.

Streamable HTTP MCP server (JSON-RPC 2.0 over POST /mcp) exposing the
SAME tools as the stdio MCP server (``mcp_server.py``): the 13 run-only
operations plus the 3 template-store tools (save/list/get_template)
plus the 3 competitor-research tools (list_competitors, get_competitor,
get_research_brief).
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
  GET  /mcp     SSE stream (text/event-stream) for the connector
  GET  /image/<content_id>.png  key-protected poster download
Anything else: 404. Errors never leak stack traces; logs carry
method + path + status only.
"""
import hashlib
import hmac
import json
import os
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

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
MAX_STREAM_SECONDS = 300  # max lifetime of one GET /mcp SSE stream
_IMAGE_ID_RE = re.compile(r"^ER-\d{8}-\d{3}$")  # poster file ids only

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
    def _drain_body(self):
        """Read and discard any request body, so leftover bytes cannot
        poison the next request on this keep-alive connection
        (HTTP/1.1). A client that sends a body with a GET — Claude's
        connector does this when it connects (an `initialize` JSON
        body on GET /mcp) — used to break the connection: the unread
        bytes were parsed as the next request line and the server
        answered 400/501, killing the connect flow. If the body is
        oversized, close the connection instead of leaving bytes
        behind."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return
        if length > MAX_BODY:
            self.close_connection = True
            return
        remaining = length
        while remaining > 0:
            chunk = self.rfile.read(min(65536, remaining))
            if not chunk:
                break
            remaining -= len(chunk)

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

    def _valid_download_token(self):
        """Check the signed ?token=&exp= on a /image/ URL.

        Token = HMAC-SHA256("<content_id>:<exp>", key=API_KEY).
        Valid only for the id in the path and while exp is in the
        future. Returns False for a missing/expired/tampered token.
        """
        parts = urlsplit(self.path)
        name = parts.path[len("/image/"):]
        if not name.endswith(".png"):
            return False
        content_id = name[:-len(".png")]
        if not _IMAGE_ID_RE.match(content_id):
            return False
        query = parse_qs(parts.query)
        tokens = query.get("token", [])
        exps = query.get("exp", [])
        if len(tokens) != 1 or len(exps) != 1:
            return False
        try:
            exp = int(exps[0])
        except ValueError:
            return False
        if exp <= int(time.time()):
            return False
        expected = hmac.new(
            API_KEY.encode(), ("%s:%d" % (content_id, exp)).encode(),
            hashlib.sha256).hexdigest()
        return hmac.compare_digest(tokens[0], expected)

    def _client_ip(self):
        return self.client_address[0]

    # -- routes ----------------------------------------------------------
    def do_GET(self):
        self._drain_body()
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
            self._handle_mcp_get_stream()
        elif path.startswith("/image/"):
            self._handle_image_download(path)
        else:
            self._send_json(404, {"error": "NOT_FOUND"})

    def _handle_mcp_get_stream(self):
        """GET /mcp opens the server-to-client SSE stream (MCP
        Streamable HTTP: the server MAY support it). Claude's
        connector opens this stream when it connects — answering 405
        left the connect flow without a stream, and the app reported
        the connection as failed. The server sends no unsolicited
        messages yet, so the stream carries only heartbeat comments
        until the client disconnects or MAX_STREAM_SECONDS elapses."""
        if not self._authed():
            self._send_json(401, {"error": "UNAUTHORIZED"})
            return
        if _rate_limited(self._client_ip()):
            self._send_json(429, {"error": "RATE_LIMITED",
                                  "message": "60 requests/minute per IP"})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        deadline = time.monotonic() + MAX_STREAM_SECONDS
        try:
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            while time.monotonic() < deadline:
                time.sleep(20)
                self.wfile.write(b": ping\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.close_connection = True

    def _handle_image_download(self, path):
        """GET /image/<content_id>.png — poster download.

        Auth is EITHER the X-Api-Key header OR a signed token in
        the query string (?token=<hmac>&exp=<unix>) — a plain tap
        in a browser cannot send a header, so the token is what
        makes the link Claude hands out actually openable. The
        token is HMAC-SHA256 of "<content_id>:<exp>" keyed by the
        API key, valid 24h; the key itself never appears in a URL.
        Only files named ER-<cycle>-<nnn>.png from the state dir
        are served (strict id pattern + resolved-path check), so
        no path traversal is possible. Note: on the free Render
        plan the state dir is ephemeral — a poster downloaded
        after a restart/redeploy is gone (404) and the run must
        be repeated.
        """
        if not (self._authed() or self._valid_download_token()):
            self._send_json(401, {"error": "UNAUTHORIZED"})
            return
        if _rate_limited(self._client_ip()):
            self._send_json(429, {"error": "RATE_LIMITED",
                                  "message": "60 requests/minute per IP"})
            return
        name = path[len("/image/"):]
        if not name.endswith(".png"):
            self._send_json(404, {"error": "NOT_FOUND"})
            return
        content_id = name[:-len(".png")]
        if not _IMAGE_ID_RE.match(content_id):
            self._send_json(404, {"error": "NOT_FOUND"})
            return
        state_dir = Path(mcp_server.STATE_DIR).resolve()
        file_path = (state_dir / (content_id + ".png")).resolve()
        if file_path.parent != state_dir or not file_path.is_file():
            self._send_json(404, {"error": "NOT_FOUND"})
            return
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition",
                         'inline; filename="%s.png"' % content_id)
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/mcp":
            self._drain_body()
            self._send_json(404, {"error": "NOT_FOUND"})
            return
        if not self._authed():
            self._drain_body()
            self._send_json(401, {"error": "UNAUTHORIZED"})
            return
        if _rate_limited(self._client_ip()):
            self._drain_body()
            self._send_json(429, {"error": "RATE_LIMITED",
                                  "message": "60 requests/minute per IP"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            if length > MAX_BODY:
                # Oversized body: do not leave bytes behind on the
                # keep-alive connection.
                self.close_connection = True
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
