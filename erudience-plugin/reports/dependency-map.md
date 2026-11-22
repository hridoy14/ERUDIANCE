# Erudience Plugin — Dependency Map (v4.9.2)

- Baseline: `main@c54e5b0`; branch `maintenance/erudience-v4.9.2`. Derived from import inspection + test execution (all imports resolve; full suite passes — see `reports/regression-results.md`).
- External dependencies: **Python standard library + Pillow only.** No `requirements.txt`/`pyproject.toml`; Pillow is declared only in `.github/workflows/erudience-regression.yml` (`pip install Pillow`, Python 3.11). Tested here on Python 3.12.3 / Pillow 13.0.0 in an isolated venv. No network libraries, no provider SDKs.

## Production import graph

```
gate_chain_v41.py ──imports──▶ chatgpt_bridge_v43.py ──imports──▶ batch_guard_v45.py
        ▲ (STAGES, REPAIR, Adapter, Chain, digest, GateFailure)
        │  reads at import: references/production-policy-v33.json
        │  reads at runtime: assets/erudience-owner-approved-logo-2026-11-21.jpg
        │                    (only when a plan carries logo_asset; hash-checked)
        │
website_brand_v38.py ──imports──▶ website_render_v38.py   (PALETTE)
keyword_research.py ──imports──▶ linkedin_seo_validator.py (validate_cluster, normalize)
```

Standalone production modules (import **no** other plugin module):
`production_controller_v39.py`, `workflow_engine.py`, `autonomous_pipeline_v40.py`,
`brand_policy_v36.py`, `brand_render_v37.py`, `render_poster.py`, `content_engine.py`,
`evidence_store.py`, `competitor_monitor.py`, `production_gate.py`, `batch_gate.py`,
`brief_prompt_gate.py`, `validate_strategy_v33.py`, `verify_output.py`, `linkedin_analytics.py`.

- **Circular imports:** none. The production graph is a DAG (one linear chain + two single edges); the only shared module, `keyword_research`, imports nothing itself.
- **Pillow users:** `gate_chain_v41` (PNG open/verify), `batch_guard_v45` (PNG verify), `brand_render_v37`, `website_render_v38`, `render_poster`, `verify_output`, and lazily inside `production_controller_v39` / `autonomous_pipeline_v40` (TECH_QA).
- **SQLite user:** `evidence_store.py` only (stdlib `sqlite3`).

## Test-only edges

| Test file | Imports (plugin modules) |
|---|---|
| `scripts/test_gate_chain_v41.py` | `gate_chain_v41` |
| `scripts/test_chatgpt_bridge_v43.py` | `chatgpt_bridge_v43` |
| `scripts/test_batch_guard_v45.py` | `batch_guard_v45`, `gate_chain_v41` |
| `scripts/test_brand_policy_v49.py` | `gate_chain_v41` |
| `scripts/test_brand_policy_v36.py` | `brand_policy_v36` |
| `scripts/test_brand_render_v37.py` | `brand_render_v37` |
| `scripts/test_production_controller_v39.py` | `production_controller_v39` |
| `scripts/test_production_gate.py` | `production_gate` |
| `scripts/test_strategy_v33.py` | `validate_strategy_v33` |
| `scripts/test_website_brand_v38.py` | `website_brand_v38` |
| `scripts/test_autonomous_pipeline_v40.py` | `autonomous_pipeline_v40` |
| `scripts/test_verify_output.py` (new, v4.9.2) | `verify_output` |
| `scripts/integration_tests.py` | `keyword_research`, `linkedin_seo_validator`, `competitor_monitor`, `linkedin_analytics`, `workflow_engine` |
| `tests_content_engine.py` (plugin root) | `content_engine` |

## Unimported modules (no production caller)

`evidence_store`, `batch_gate`, `brief_prompt_gate`, `verify_output`, `render_poster`,
`website_render_v38`, `brand_policy_v36`, `brand_render_v37`, `production_controller_v39`,
`autonomous_pipeline_v40`, `production_gate`, `validate_strategy_v33`, `content_engine`,
`batch_guard_v45` (test only), `competitor_monitor` / `linkedin_analytics` / `linkedin_seo_validator`
(integration-tests only). "Unimported" means no live caller — most are still exercised by the
regression suite. Modules with **no test at all**: `evidence_store`, `batch_gate`,
`brief_prompt_gate`, `website_render_v38`, `render_poster` (and `verify_output` before v4.9.2).

Preserved deliberately: `evidence_store` is the only module modelling owner approval +
write authorisation (`can_handoff()` requires separate `APPROVE` + `WRITE_AUTHORISE` rows);
`production_controller_v39` is the only atomically-persisted controller; `autonomous_pipeline_v40`
holds the only deterministic content/brand validators. None of these capabilities exist in the
canonical chain, so none of these modules was deleted (see `reports/cleanup-evidence.md`).

## Data / file dependencies

| Consumer | Reads |
|---|---|
| `gate_chain_v41` | `references/production-policy-v33.json` (at import); approved logo file (at IMAGE_BUILD, only if planned); inspection-evidence files (live mode only) |
| `validate_strategy_v33` | `references/production-policy-v33.json` (at import; value unused — see architecture audit §6) |
| `brand_render_v37` | Logo + Sora font files named in the spec (path + SHA256 + source); pins `brand_policy == 'social-os/BRAND.md:v1.1'` (no such file in repo) |
| `render_poster` / `website_render_v38` | Inter/DM Sans font files passed on the CLI / in the spec |
| `verify_output` | PNG + sibling `.json` manifest (SHA256 + `locked_stage_names`) |
| `chatgpt_bridge_v43` / `batch_guard_v45` / `production_controller_v39` | Their own JSON state/manifest files (atomic replace) |
| `evidence_store` | Its own SQLite database file |

## Manifest / CI dependencies

- `plugin.json` = `.agent-plugin/plugin.json` = `.claude-plugin/plugin.json` (byte-identical host mirrors) + `.codex-plugin/plugin.json` (same version/description + `interface`/`author`) + `plugin.yaml` + `.app.json` — all version **4.9.2** after this release.
- `.github/workflows/erudience-regression.yml` (repo root): on push touching `erudience-plugin/**`, Python 3.11, `pip install Pillow`, `compileall`, `unittest discover -s scripts -p 'test_*.py'`, `unittest tests_content_engine`, `scripts/integration_tests.py -v`. Note: discover does not pick up `integration_tests.py` (name does not start with `test_`), which is why CI runs it explicitly.
- `skills/erudience/SKILL.md` references `references/brand-policy-current.md`, `references/runtime-and-compatibility-v49.md`, `references/production-policy-v33.json`, `scripts/gate_chain_v41.py`, `scripts/chatgpt_bridge_v43.py`, `scripts/batch_guard_v45.py` — all present.
- No `scripts/__init__.py`: scripts are not a package; cross-module imports resolve only when run from `scripts/` or with `sys.path` insertion (as the tests and CI do).
