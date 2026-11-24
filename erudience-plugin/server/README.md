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
| `start_workflow` | Start a 7-job workflow (cycle; topics optional — omit to auto-generate 7 from Erudiance's verified website pages) | API key |
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
| `remove_content` | **DENIED — 403 `FORBIDDEN_OWNER_ONLY`** | n/a |

ChatGPT can **never**: approve or reject a post (only the owner decides,
via `op_submit_owner_decision` outside this server), remove a post (only
the owner removes, via `op_remove_content` outside this server), publish
or schedule anything, or change code, config, or brand policy. There is
no endpoint here that does any of those things. Neither
`submit_owner_decision` nor `remove_content` is in `openapi.json` at all,
and the server rejects both with 403 before any dispatch.

Other protections: `X-Api-Key` header checked with a constant-time
compare (missing/wrong → 401 `UNAUTHORIZED`); 60 requests/minute per
key (over → 429 `RATE_LIMITED`); every request logs method + path +
status only — never the key or payload contents; unexpected errors
return 500 `INTERNAL` with no stack trace. `/health` and
`/openapi.json` are public (no key) so ChatGPT can fetch the spec and
health-check the service; every `/ops/*` call needs the key.

## Auto-topic (owner order 2026-11-24)

`start_workflow` accepts topics as optional. When topics are omitted,
the server generates 7 distinct topics itself from Erudiance's verified
website pages (erudience.com service pages, all HTTP 200 on 2026-11-24),
rotating deterministically per cycle so consecutive cycles differ. Each
auto topic cites the homepage + its service page as sources
(USER_SUPPLIED provenance — no live fetch provider exists), and the
batch gets a default strategy (7 slots, exactly 1 promotion) plus fresh
research evidence, so a live run (`mode: "LIVE"`) passes the gates with
no caller-supplied topics. Jobs record `topic_source:
"server-generated"`. Explicit topics keep the caller's provenance:
pass `sources` (`{topic: [{url, verified_at}]}`) for the pages
actually read and those sources are attached (USER_SUPPLIED) with
fresh research evidence — without caller-supplied sources no sources
are invented and the live gates apply as before (RESEARCH_DUE /
LIVE_SOURCES_REQUIRED). Jobs record `topic_source: "user-supplied"`.
A default strategy (7 slots, exactly 1 promotion) is used whenever
the caller passes none.

## Plans — 1-day / 7-day / 1-month (owner order 2026-11-24)

`start_workflow` accepts `plan`: `1-day` (1 post, day 1), `7-day`
(7 posts, scheduled days 1..7, default), `1-month` (30 posts,
scheduled days 1..30, one per day). The tool description tells
Claude to ASK the user which plan they want first and wait for the
choice — never assume a plan — and, after the workflow finishes,
to generate one image in chat for EACH content and show it
alongside the server poster (the server poster is text-only; the
image is Claude's own). No gate is ever widened: the 7-day plan is
one verified 7-job batch (`run_batch`, 7 slots, exactly 1
promotion); the 1-day and 1-month plans run one single job per day,
each carrying the full 7-slot week strategy (its own slot is its
day within the week), so the live STRATEGY gate passes exactly as
for a batch job — the promotion falls on days 7, 14, 21, 28. Daily
jobs live flat in the plan root (`ER-<cycle>-<ddd>.json`); a
`plan.json` at the root records the plan and the job list, and
`get_batch_report` / `get_workflow_status` / `get_content_preview` /
`get_image_preview` all read daily jobs through it. Auto topics are
generated once (1 / 7 / 30 distinct from the 34-topic website
bank), so no topic repeats inside a plan. Each job records
`scheduled_day` and `scheduled_week` in its state. Explicit topics:
1 distinct for 1-day, 7 for 7-day, 30 for 1-month — pass `sources`
(`{topic: [{url, verified_at}]}`) for the pages actually read, or
the live run is refused (RESEARCH_DUE). Poster downloads serve the
flat `ER-<cycle>-<nnn>.png` ids (same signed-token auth).

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

# 4b. Denied op — owner removal is never available to ChatGPT either
curl -s -X POST $BASE/ops/remove_content -H "X-Api-Key: $KEY" \
  -H 'Content-Type: application/json' -d '{
    "owner": "owner-1", "content_id": "ER-20261124-001",
    "state_dir": "state"}'
# expect: HTTP 403 {"ok": false, "error": "FORBIDDEN_OWNER_ONLY", ...}

# 5. No key — unauthorized
curl -s -X POST $BASE/ops/get_system_status \
  -H 'Content-Type: application/json' -d '{}'
# expect: HTTP 401 {"ok": false, "error": "UNAUTHORIZED"}

# 6. Spec — no key needed
curl -s $BASE/openapi.json | python3 -m json.tool | head -20
# expect: valid OpenAPI 3.0.3, 13 /ops/* paths, no submit_owner_decision or remove_content
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
`submit_owner_decision` and `remove_content` are NOT tools and are
refused if called by name. State is shared with the HTTP server (same state dir), so a job
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
`get_batch_report`, unknown tool/method errors. The 3
competitor-research tools below are shared by both transports, so the
server now exposes 19 tools in total.

Note: claude.ai on the web uses remote MCP servers, which need a
public HTTPS URL — see the HTTP MCP server below.

## Claude — HTTP MCP server (`mcp_http.py`)

The same 19 tools over Streamable HTTP (POST `/mcp`) — this is what
claude.ai connects to as a **custom connector**. Same rules as the
stdio server, plus an API key (the process is remote, not local):
`ERUDIANCE_API_KEY` must be set or the server refuses to start.
Owner access rule (decisions.json `claude_access`): no repo access,
never change any code; only generate content and build images;
templates may be created and stored as data; all data stays on the
server. `submit_owner_decision` and `remove_content` are NOT tools and
are refused.

Template store: `save_template` / `list_templates` / `get_template`
store plain JSON template definitions under
`<state-dir>/templates/<slug>.json`. A template is data (name, kind,
version, blocks) — validated on write, never executed. The slug must
match `[a-z0-9][a-z0-9-]{0,63}` so no path can escape the store.

## Competitor research — Claude researches, then posts (auto)

`list_competitors` / `get_competitor` / `get_research_brief` read
`data/competitors.json` — the 83 verified direct competitors (website
URLs verified; 9 LinkedIn pages verified; tiers 12/61/10; client counts
only where the agency itself states one — 7 of 83; platforms only where
a profile was found in search). Read-only data, never changed by
Claude. Flow: Claude calls `get_research_brief` (Erudiance website
source pages + competitor summary + honesty rules), researches the
competitors with `list_competitors` / `get_competitor`, derives 7
distinct topics, then calls `start_workflow` with those topics and
mode `LIVE` — posts are built automatically from that research.
`get_research_brief` also lists the 9 verified Erudiance service pages
so Claude can cite real sources. Nothing here is in `openapi.json` —
these 3 tools are MCP-only, for Claude.

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
`TEST_FIXTURE_PASS`). Competitor tools tested separately
(`/tmp/test_mcp_competitors.py`, stdio + HTTP, 31/31 — the file was
later lost to a VM /tmp wipe; re-verified 2026-11-24 with the compact
`/tmp/test_mcp_smoke.py`, 14/14).

GET-body fix (2026-11-24): Claude's connector sends a GET /mcp
carrying an `initialize` JSON body when it connects. The server used
to answer 405 without reading that body, which poisoned the
keep-alive connection — the leftover bytes were parsed as the next
request line and the server answered 400/501, so the connect flow
failed. `do_GET` (and the early-return paths of `do_POST`) now drain
any request body first. Reproduced before the fix and verified after
with `/tmp/repro_get_body.py` (GET /mcp with body → 405, then
GET /health on the same connection → 200).

SSE stream for GET /mcp (2026-11-24): the full handshake check
against the live server showed initialize → 200,
notifications/initialized → 202, tools/list → 19 tools — but
GET /mcp still answered 405, and the connector still reported the
connection as failed. GET /mcp now opens a server-to-client SSE
stream (`text/event-stream`, `: connected` then a `: ping` heartbeat
every 20s, max 300s, closes on client disconnect). No unsolicited
messages are sent yet. Verified with `/tmp/test_mcp_sse.py`, 4/4:
stream → 200 with `: connected`, no key → 401, GET with JSON body
→ 200 stream (body drained), server healthy afterwards (19 tools).
The old `/tmp/repro_get_body.py` 405 expectation is superseded by
this test. Full plugin suite 247/247 + 48/48 OK after the change.

Live-run path-confinement fix (2026-11-24): a LIVE run on Render
blocked all 7 jobs at SOURCE_REVIEW with PATH_OUTSIDE_ALLOWED_ROOT
(4 repairs each). Root cause: the live gate (D-15) allows file
paths only under cwd, the plugin root, or the job's state/evidence
dir — and `run_job` never recorded the state dir on the job, so on
Render (server cwd = repo root, state dir = /tmp/erudiance-state)
the inspection-evidence path was outside every allowed root. Local
runs and tests had masked it because they run with cwd == batch
root. Fix (core/batch_guard_v45.py `run_job`): the state file's
parent is now recorded as job['state_dir'] and job['evidence_dir'].
Regression test test_run_batch_auto_topics_live_cwd_differs runs a
live auto batch WITHOUT chdir and passes only with the fix. Full
suite 248/248 + 48/48 OK after the fix.

Poster download (2026-11-24): `GET /image/<content_id>.png`
serves the poster PNG from the state dir. Auth is either the
X-Api-Key header or a signed token in the URL
(`?token=<hmac>&exp=<unix>`, HMAC-SHA256 of "<content_id>:<exp>"
keyed by ERUDIANCE_API_KEY, valid 24h) — a plain tap in a browser
cannot send a header, so the token is what makes the link Claude
hands out actually openable; the key itself never appears in a
URL. Only ids matching `ER-<cycle>-<nnn>.png` are served, so no
path traversal is possible; missing file → 404. `get_image_preview`
also returns a signed `download_url` for the poster when both
ERUDIANCE_PUBLIC_URL and ERUDIANCE_API_KEY are set (Render: the
URL is set in `render.yaml`; the key lives in the dashboard only),
so Claude can hand the user the link in chat; without those env
vars no link is added.
Verified with `/tmp/test_mcp_download.py`, 16/16: download with
key → 200 `image/png` (bytes match), no/wrong key → 401, bad ids
and traversal attempts → 404, missing file → 404, signed URL with
no header → 200, expired/tampered/wrong-id token → 401, preview
`download_url` present (signed) with the env vars and absent
without them.
Limit: on the free Render plan the state dir is ephemeral — a
poster is gone after a restart/redeploy (404) and the run must be
repeated. NOTE: `render.yaml` env vars are NOT always applied by
Render's blueprint sync — the first deploy had ERUDIANCE_PUBLIC_URL
missing from the running service even though render.yaml declared
it; it had to be added in the dashboard Environment tab (which
triggered a redeploy). Full plugin suite 247/247 + 48/48 OK after
the change.

## Deployment — LIVE

Deployed 2026-11-24 on Render (free plan):
`https://erudiance-mcp-http.onrender.com` — `/health` and `/mcp`.
Render auto-deploys from GitHub main. `openapi.json` already points
at the live URL. Free-plan disk is ephemeral, so job state and stored
templates do NOT survive a restart/redeploy. The first real Claude
request through the connector has not happened yet — the connector is
added and the tools are listed, but no workflow has run through it.

## Files

- `server.py` — stdlib-only ThreadingHTTPServer (13 allowed ops, 1
  explicit deny, key auth, rate limit, safe logging).
- `mcp_server.py` — stdlib-only MCP server over stdio (13 run ops + 3
  template-store tools + 3 competitor-research tools, no API key,
  owner decision denied). Tested 2026-11-24: 12/12 MCP client checks passed.
- `mcp_http.py` — stdlib-only MCP server over Streamable HTTP (POST
  `/mcp`, same 19 tools, X-Api-Key auth, 60 req/min). For claude.ai
  custom connectors. Tested 2026-11-24: 24/24 HTTP client checks passed.
- `data/competitors.json` — 83 verified direct competitors (website,
  LinkedIn where verified, HQ, services, tier, client count where
  stated, platforms where found). Read-only research data for the
  competitor tools.
- `openapi.json` — OpenAPI 3.0.3 spec for the 13 allowed ops.
- `decisions.json` — owner decisions record.
- `state/` — created at first start; job state lives here by default.
