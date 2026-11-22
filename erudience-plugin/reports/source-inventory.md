# Erudience LinkedIn Content & Image Plugin — Source Inventory (v4.9.2 baseline)

- Repository: `hridoy14/ERUDIANCE`, branch `main`, commit `c54e5b0` ("docs: consolidate Erudience source policy and verification status")
- Working branch: `maintenance/erudience-v4.9.2` (created from `main`, no history rewritten)
- Inventory date: 2026-11-22 (Asia/Dhaka)
- Scope: `erudience-plugin/` only. No other repository directory was modified.

## Totals

| Item | Count |
|---|---|
| Total files in `erudience-plugin/` (main baseline) | 89 |
| Total files after logo placement (this branch) | **90** |
| Total files at v4.9.2 release (after README cleanup + new reports/test) | **88** (80 original text files + 1 logo + 6 reports + 1 new test) |
| Directories | 8 (`erudience-plugin/`, `.agent-plugin/`, `.claude-plugin/`, `.codex-plugin/`, `agents/`, `references/`, `scripts/`, `skills/erudience/`, plus new `assets/`) |
| Python modules (`scripts/*.py` + `tests_content_engine.py`) | 36 (23 non-test modules + 12 test modules in `scripts/` + 1 root test module; `integration_tests.py` counted in the 23) |
| Test modules | 13 (`scripts/test_*.py` × 11, `scripts/integration_tests.py`, `tests_content_engine.py`) |
| Plugin manifests | 6 (`plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`) |
| Documentation (Markdown) | 46 (README.md + 9 historical README-v*.md + `agents/roles-v34.md` + 35 files under `references/`) |
| Reference JSON | 5 (`brief-schema-example.json`, `endpoint-registry.json`, `integration-registry-v34.json`, `production-policy-v33.json`, plus `references/` JSON counted here) |
| Brand assets (binary) | 1 — the owner-approved JPG logo (see below) |
| Total lines (text files, `wc -l`) | 2,516 (excluding the binary logo) |

## File listing (88 files at release; 90 immediately after logo placement, before the 9 README deletions and the addition of 6 reports + 1 test)

### Root (14)
`.agent-plugin/plugin.json`, `.app.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`,
`README-v33.md`, `README-v34.md`, `README-v35.md`, `README-v36.md`, `README-v37.md`,
`README-v39.md`, `README-v40.md`, `README-v41.md`, `README-v42.md`, `README.md`,
`plugin.json`, `plugin.yaml`, `tests_content_engine.py`
(`agents/roles-v34.md` under `agents/`)

### `assets/` (1, new in this branch)
`erudience-owner-approved-logo-2026-11-21.jpg`

### `references/` (35)
`asset-and-font-policy.md`, `autonomous-execution-v40.md`, `batch-production-v45.md`,
`brand-assets-manifest.md`, `brand-policy-current.md`, `brand-source-of-truth-v36.md`,
`brand-template-contract-v47.md`, `brief-schema-example.json`, `chat-vision-audit-v35.md`,
`chatgpt-runtime-v43.md`, `content-to-creative-brief-v21.md`, `endpoint-registry.json`,
`execution-state-machine-v39.md`, `gate-contract-v41.md`, `gates-and-handoff.md`,
`integration-registry-v34.json`, `master-action-v31.md`, `master-command-v6.md`,
`monthly-weekly-social-os.md`, `one-action-production-contract.md`, `one-command-v44.md`,
`orchestrator-v2.md`, `owner-approved-brand-v46.md`, `production-contract-v33.md`,
`production-execution-v35.md`, `production-policy-v33.json`, `production-runtime-v37.md`,
`release-audit-v34.md`, `release-compatibility-v48.md`, `runtime-and-compatibility-v49.md`,
`smb-content-strategy-v32.md`, `strategy-playbook.md`, `system-architecture-v34.md`,
`unified-system-v42.md`, `website-brand-profile-v38.md`, `workflow-v3.md`

### `scripts/` (34)
Non-test (22): `autonomous_pipeline_v40.py`, `batch_gate.py`, `batch_guard_v45.py`,
`brand_policy_v36.py`, `brand_render_v37.py`, `brief_prompt_gate.py`, `chatgpt_bridge_v43.py`,
`competitor_monitor.py`, `content_engine.py`, `evidence_store.py`, `gate_chain_v41.py`,
`keyword_research.py`, `linkedin_analytics.py`, `linkedin_seo_validator.py`,
`production_controller_v39.py`, `production_gate.py`, `render_poster.py`,
`validate_strategy_v33.py`, `verify_output.py`, `website_brand_v38.py`,
`website_render_v38.py`, `workflow_engine.py`, plus `integration_tests.py` (test runner, counted as test below).

Test (12): `integration_tests.py`, `test_autonomous_pipeline_v40.py`,
`test_batch_guard_v45.py`, `test_brand_policy_v36.py`, `test_brand_policy_v49.py`,
`test_brand_render_v37.py`, `test_chatgpt_bridge_v43.py`, `test_gate_chain_v41.py`,
`test_production_controller_v39.py`, `test_production_gate.py`, `test_strategy_v33.py`,
`test_website_brand_v38.py`

### `skills/erudience/` (1)
`SKILL.md` (plugin entrypoint)

## Logo verification (the 90th file)

- Owner upload (this chat): `workspace/user/files/1000167983_0_1tk2.jpg` — **untouched original**; only copied, never edited, recoloured, regenerated or renamed in place.
- Placed copy: `erudience-plugin/assets/erudience-owner-approved-logo-2026-11-21.jpg`
- Format: JPEG (JFIF 1.01, baseline), RGB, **1536 × 1536 px**, 55,210 bytes.
- SHA-256 (upload and placed copy identical): `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226`
- Visual check (human-eyes): near-black background, circular emerald-green + pale-mint circuit-node mark with black circuit nodes/lines — matches `references/owner-approved-brand-v46.md` ("1536x1536 JPEG with near-black background and circular neon green / pale mint circuit mark") exactly.
- Expected path confirmed in: `references/brand-assets-manifest.md`, `references/brand-policy-current.md`, `references/owner-approved-brand-v46.md`, `references/brand-template-contract-v47.md`, and machine-readable `references/production-policy-v33.json` (`brand_assets.approved_logo_path`). The upload filename (`1000167983_0_1tk2.jpg`) is the chat-upload name, not the canonical name; the canonical name above is the copy target, recorded here.
- Verification status, stated honestly: verified from the owner upload in this chat (bytes + dimensions + visual inspection), **not** from GitHub — the file was absent from `main` (hence 89 files there) and is added only on the `maintenance/erudience-v4.9.2` branch for PR review.

## Manifests and version inconsistencies (baseline, `main`)

| Manifest | Version (baseline) | Notes |
|---|---|---|
| `plugin.json` | 4.9.1 | Canonical name `erudience` |
| `.agent-plugin/plugin.json` | 4.9.1 | Byte-identical to `plugin.json` (host mirror, intentional) |
| `.claude-plugin/plugin.json` | 4.9.1 | Byte-identical to `plugin.json` (host mirror, intentional) |
| `.codex-plugin/plugin.json` | 4.9.1 | Same version/description + extra `interface`/`author` blocks |
| `plugin.yaml` | **4.6.0 — stale** | Must sync to 4.9.2 |
| `.app.json` | **4.6.0 — stale** | Must sync to 4.9.2 |

## Dependencies and imports

- No `requirements.txt`, `setup.py`, or `pyproject.toml` in the repository. The only third-party dependency is **Pillow**, per `.github/workflows/erudience-regression.yml` (`pip install Pillow`, Python 3.11). All other imports are Python standard library (`json`, `hashlib`, `argparse`, `pathlib`, `sqlite3`, `re`, `dataclasses`, `datetime`, `tempfile`, `unittest`).
- Tested environment (this audit): Python 3.12.3, Pillow 13.0.0, isolated venv at `/tmp/erud-venv` (ephemeral; repo has no requirements file to pin against — see regression report).
- Internal imports resolve within `scripts/` (e.g. `gate_chain_v41`, `chatgpt_bridge_v43`, `batch_guard_v45`, `workflow_engine`, `content_engine`, `brand_render_v37`, `website_brand_v38`, `keyword_research`, `linkedin_seo_validator`, `competitor_monitor`, `linkedin_analytics`, `evidence_store`, `production_controller_v39`, `autonomous_pipeline_v40`, `brand_policy_v36`, `production_gate`, `validate_strategy_v33`).
- No network imports in `scripts/*.py` (no `requests`/`urllib`/`socket`/provider SDKs). External integrations are documented as NOT_CONFIGURED (`references/endpoint-registry.json`: OpenAI/Anthropic/Google Search Console all `DOCUMENTED_PROVIDER_API_NOT_CONNECTED`).

## Missing / broken / duplicate findings (baseline)

- **Missing on `main`, now resolved on this branch:** `assets/erudience-owner-approved-logo-2026-11-21.jpg` (the 90th file). Every other file the manifests, SKILL.md, and `production-policy-v33.json` reference exists.
- **Missing (not in repo, by design):** Sora / Inter / DM Sans font binaries — renderers require installed font paths and fail closed without them (`render_poster.py`, `brand_render_v37.py`). No font files are bundled; do not invent them.
- **Missing:** dependency manifest (`requirements.txt`/`pyproject.toml`) — Pillow is only declared in CI. Recorded, not invented.
- **Broken references:** none found in active code paths — all `scripts/` imports resolve (compile + 107 tests pass, see regression report). Historical references cite external repos (`bishal-paul-git/erudience-main`, `erudience-social-os`) and provider APIs that are documented as NOT_CONFIGURED, not as broken local links.
- **Duplicates (byte-identical):** `plugin.json` = `.agent-plugin/plugin.json` = `.claude-plugin/plugin.json` (MD5 `0d09c47750d0ae0af6452ba0465aca36`). These are **intentional host mirrors** (one manifest per plugin host location), not redundant files — deleting any would break that host's discovery. No other duplicate files (no other repeated MD5).
- **Version inconsistencies:** `plugin.yaml` and `.app.json` at 4.6.0 vs 4.9.1 everywhere else (to sync to 4.9.2). `production-policy-v33.json` is version `3.3.0` — that is the *policy* version, not the plugin version; not an inconsistency. `README.md` baseline text said "89 text source files" and "Local subset tests: 27 passed" — both stale (see regression report: full suite is 107 tests, all passing; file count is now 90 with the logo).
- **Secrets scan:** no credentials, tokens, or private keys found in `erudience-plugin/` (grep for `api_key|password|secret|token|bearer|private_key` returns only documentation wording and credential *env-var names* in `endpoint-registry.json`, all with `NOT_CONNECTED` status).
