# Erudiance Automation API — ChatGPT custom-connector server

A small stdlib-only Python server that lets ChatGPT **run** the Erudiance
LinkedIn content-and-image workflow — and nothing else. It fronts the
plugin's ChatGPT bridge (`erudience-plugin/core/chatgpt_bridge_v43.py`)
as HTTP operations. The plugin repository is used read-only as an import
source; this server lives outside the repo and never writes into it.

## Access model — the owner's rule

ChatGPT may run automation only. It may **never** change anything.

| Operation | What it does | Auth |
|---|---|---|
| `get_system_status` | Bridge/gate/batch versions, provider statuses, approval state | API key |
| `list_agent_capabilities` | The 18 agent roles and their contracts | API key |
| `start_workflow` | Start a 7-job workflow (7 distinct topics, cycle) | API key |
| `get_workflow_status` | Status of a workflow / single job | API key |
| `execute_authorized_step` | Run one authorized workflow step | API key |
| `resume_workflow` | Resume from a checkpoint (gates are never skipped) | API key |
| `get_agent_report` | Per-agent report | API key |
| `get_content_preview` | Content metadata only (hash, caption, image path/sha) | API key |
| `get_image_preview` | Image metadata only (path, sha, dimensions) | API key |
| `validate_content` | Validate a content item, returns a decision | API key |
| `validate_image` | Pixel inspection of an image file | API key |
| `get_batch_report` | Report for a 7-job batch | API key |
| `get_audit_report` | Evidence-ledger and state audit report | API key |
| `submit_owner_decision` | **DENIED — 403 `FORBIDDEN_OWNER_ONLY`** | n/a |

ChatGPT can **never**: approve or reject a post (only the owner decides,
via `op_submit_owner_decision` outside this server), publish or schedule
anything, or change code, config, or brand policy. There is no endpoint
here that does any of those things. `submit_owner_decision` is not in
`openapi.json` at all, and the server rejects it with 403 before any
dispatch.

Other protections: `X-Api-Key` header checked with a constant-time
compare (missing/wrong → 401 `UNAUTHORIZED`); 60 requests/minute per
key (over → 429 `RATE_LIMITED`); every request logs method + path +
status only — never the key or payload contents; unexpected errors
return 500 `INTERNAL` with no stack trace. `/health` and
`/openapi.json` are public (no key) so ChatGPT can fetch the spec and
health-check the service; every `/ops/*` call needs the key.

## Run locally

```bash
cd ~/workspace/erudiance-plugin-work/ERUDIANCE/erudience-plugin/server
export ERUDIANCE_API_KEY=$(python3 -c "import secrets;print(secrets.token_urlsafe(32))")
# keep the printed key — it is the only copy; the server never generates one
python3 server.py
# listening on 0.0.0.0:8765 (override with PORT)
```

Optional env: `ERUDIANCE_STATE_DIR` (job state root, default
`<server-dir>/state`), `ERUDIANCE_PLUGIN_ROOT` (plugin root override),
`PORT` (default 8765). The server exits with a clear error if
`ERUDIANCE_API_KEY` is unset.

## Smoke tests (server running on port 8765)

```bash
export KEY='<the same ERUDIANCE_API_KEY>'
export BASE=http://127.0.0.1:8765

# 1. Health — no key needed
curl -s $BASE/health
# expect: {"ok": true, "service": "erudiance-automation", "chatgpt_connected": false}

# 2. Read op — system status
curl -s -X POST $BASE/ops/get_system_status -H "X-Api-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{}'
# expect: ok true, bridge/gate/batch versions, chatgpt.connected false

# 3. Execute op — start a TEST_FIXTURE workflow (no real work, no publish)
curl -s -X POST $BASE/ops/start_workflow -H "X-Api-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{
    "topics": ["AI voice agents for dental clinics", "AI receptionist for law firms",
      "Call automation for estate agents", "Support automation for e-commerce",
      "Workflow automation for accountants", "AI phone orders for Shopify stores",
      "After-hours call answering for vets"],
    "cycle": "20261124", "operator": "owner-smoke-test", "mode": "TEST_FIXTURE"}'
# expect: ok true with a dispatch result; state written under state/ (default)

# 4. Denied op — owner approval is never available to ChatGPT
curl -s -X POST $BASE/ops/submit_owner_decision -H "X-Api-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{
    "owner": "owner-1", "content_id": "ER-20261124-001",
    "decision": "APPROVE", "state_dir": "state"}'
# expect: HTTP 403 {"ok": false, "error": "FORBIDDEN_OWNER_ONLY", ...}

# 5. No key — unauthorized
curl -s -X POST $BASE/ops/get_system_status \
  -H 'Content-Type: application/json' -d '{}'
# expect: HTTP 401 {"ok": false, "error": "UNAUTHORIZED"}

# 6. Spec — no key needed
curl -s $BASE/openapi.json | python3 -m json.tool | head -20
# expect: valid OpenAPI 3.0.3, 13 /ops/* paths, no submit_owner_decision
```

## Connect in ChatGPT

1. Deploy the server to a public HTTPS URL first (see below).
2. In ChatGPT: create a custom GPT → **Configure** → **Actions** →
   **Import from URL** → paste `<deployed-url>/openapi.json`.
3. Set **Authentication** to **API Key**, header `X-Api-Key`, value = the
   `ERUDIANCE_API_KEY` used by the deployed server.
4. Save. In the GPT, ask for a workflow status or start a workflow;
   ChatGPT calls the operations above. It cannot approve anything — when
   a job reaches `READY_FOR_OWNER_REVIEW`, the owner decides outside
   ChatGPT.

## Claude — MCP server (`mcp_server.py`)

The same 13 run-only operations, as an MCP server over stdio — for
Claude Desktop, Claude Code, or any MCP client. No API key is needed:
the process runs locally as the owner. Same rule as the HTTP server:
`submit_owner_decision` is NOT a tool and is refused if called by
name. State is shared with the HTTP server (same state dir), so a job
started over MCP is visible over HTTP and vice versa.

Claude Desktop config (Windows — use YOUR repo path):

```json
{
  "mcpServers": {
    "erudiance": {
      "command": "python",
      "args": ["C:\\path\\to\\ERUDIANCE\\erudience-plugin\\server\\mcp_server.py"],
      "env": {"ERUDIANCE_STATE_DIR": "C:\\path\\to\\erudiance-state"}
    }
  }
}
```

Config file: `%APPDATA%\Claude\claude_desktop_config.json`. Restart
Claude Desktop after editing. Then ask Claude to list tools or run
`get_system_status` — the 13 `erudiance` tools appear.

Tested 2026-11-24 with a local MCP client (`/tmp/test_mcp.py`):
12/12 checks passed — initialize, ping, tools/list (16 tools: 13 run
ops + 3 template-store tools, no `submit_owner_decision`),
`get_system_status`, owner decision denied (`FORBIDDEN_OWNER_ONLY`),
`start_workflow` TEST_FIXTURE (7 jobs `TEST_FIXTURE_PASS`),
`get_batch_report`, unknown tool/method errors.

Note: claude.ai on the web uses remote MCP servers, which need a
public HTTPS URL — see the HTTP MCP server below.

## Claude — HTTP MCP server (`mcp_http.py`)

The same 16 tools over Streamable HTTP (POST `/mcp`) — this is what
claude.ai connects to as a **custom connector**. Same rules as the
stdio server, plus an API key (the process is remote, not local):
`ERUDIANCE_API_KEY` must be set or the server refuses to start.
Owner access rule (decisions.json `claude_access`): no repo access,
never change any code; only generate content and build images;
templates may be created and stored as data; all data stays on the
server. `submit_owner_decision` is NOT a tool and is refused.

Template store: `save_template` / `list_templates` / `get_template`
store plain JSON template definitions under
`<state-dir>/templates/<slug>.json`. A template is data (name, kind,
version, blocks) — validated on write, never executed. The slug must
match `[a-z0-9][a-z0-9-]{0,63}` so no path can escape the store.

Run locally:

```bash
ERUDIANCE_API_KEY=<key> python mcp_http.py   # port 8766, or $PORT
```

Connect in claude.ai (computer — Custom GPT / Connectors):
Customize → Connectors → Add custom connector → URL
`https://<your-deploy-url>/mcp`, No sign-in, Request header
`X-Api-Key: <key>`. Then just say `erudiance_linkdin` in chat.

Tested 2026-11-24 with a local HTTP client (`/tmp/test_mcp_http.py`):
24/24 checks passed — health, 405/404, 401 (no/wrong key),
initialize, ping, notification (202), tools/list (16 tools),
`get_system_status`, owner decision denied, unknown tool/method,
template save/list/get, bad slug/kind rejected, missing template
(NOT_FOUND), `start_workflow` TEST_FIXTURE (7 jobs
`TEST_FIXTURE_PASS`).

## Deployment — still pending

There is no deployed URL yet. `render.yaml` (repo root) defines the
free Render web service for `mcp_http.py`; after connecting the repo
on Render, set `ERUDIANCE_API_KEY` in the Render dashboard (same key
goes into the Claude custom connector). Free-plan disk is ephemeral,
so job state and stored templates do NOT survive a restart/redeploy.
Until the server is deployed and the first real Claude request
succeeds through it, nothing here claims a live connection. After
deployment, replace `https://REPLACE_WITH_DEPLOY_URL` in
`openapi.json` with the real URL and re-import the spec in ChatGPT.

## Files

- `server.py` — stdlib-only ThreadingHTTPServer (13 allowed ops, 1
  explicit deny, key auth, rate limit, safe logging).
- `mcp_server.py` — stdlib-only MCP server over stdio (13 run ops + 3
  template-store tools, no API key, owner decision denied). Tested
  2026-11-24: 12/12 MCP client checks passed.
- `mcp_http.py` — stdlib-only MCP server over Streamable HTTP (POST
  `/mcp`, same 16 tools, X-Api-Key auth, 60 req/min). For claude.ai
  custom connectors. Tested 2026-11-24: 24/24 HTTP client checks passed.
- `openapi.json` — OpenAPI 3.0.3 spec for the 13 allowed ops.
- `decisions.json` — owner decisions record.
- `state/` — created at first start; job state lives here by default.
