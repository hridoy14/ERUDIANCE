# Erudience Plugin — File Migration Map (Consolidation, PLAN ONLY)

- Baseline: `main` `9e320fa6` (v4.9.2). **Status: PLAN — no file was moved in this task.** Full 88-row draft: `~/workspace/erudiance-plugin-work/consolidation-staging/file-migration-map-draft.md`.
- **Total: 88 files. Proposed moves: 38. Keeps: 50. Deletions: 0.**
- Moves: `config/` 2 + `core/` 5 + `core/legacy/` 5 + `modules/` 9 + `rendering/` 3 + `tests/` 14 = 38. Keeps: root 7, agents 1, assets 1, references 34, reports 6, skills 1 = 50.

## Moves (38)
| Current | Proposed |
|---|---|
| `references/brand-policy-current.md` | `config/brand-policy-current.md` |
| `references/production-policy-v33.json` | `config/production-policy-v33.json` |
| `scripts/gate_chain_v41.py` | `core/gate_chain_v41.py` |
| `scripts/chatgpt_bridge_v43.py` | `core/chatgpt_bridge_v43.py` |
| `scripts/batch_guard_v45.py` | `core/batch_guard_v45.py` |
| `scripts/evidence_store.py` | `core/evidence_store.py` |
| `scripts/verify_output.py` | `core/verify_output.py` |
| `scripts/autonomous_pipeline_v40.py` | `core/legacy/autonomous_pipeline_v40.py` |
| `scripts/batch_gate.py` | `core/legacy/batch_gate.py` |
| `scripts/production_controller_v39.py` | `core/legacy/production_controller_v39.py` |
| `scripts/production_gate.py` | `core/legacy/production_gate.py` |
| `scripts/workflow_engine.py` | `core/legacy/workflow_engine.py` |
| `scripts/brand_policy_v36.py` | `modules/brand_claims_qa/brand_policy_v36.py` |
| `scripts/website_brand_v38.py` | `modules/brand_claims_qa/website_brand_v38.py` |
| `scripts/brief_prompt_gate.py` | `modules/creative_brief/brief_prompt_gate.py` |
| `scripts/competitor_monitor.py` | `modules/competitor_intelligence/competitor_monitor.py` |
| `scripts/content_engine.py` | `modules/linkedin_copywriting/content_engine.py` |
| `scripts/keyword_research.py` | `modules/topic_intelligence/keyword_research.py` |
| `scripts/linkedin_seo_validator.py` | `modules/topic_intelligence/linkedin_seo_validator.py` |
| `scripts/validate_strategy_v33.py` | `modules/marketing_strategy/validate_strategy_v33.py` |
| `scripts/linkedin_analytics.py` | `modules/analytics_learning/linkedin_analytics.py` |
| `scripts/brand_render_v37.py` | `rendering/brand_render_v37.py` |
| `scripts/render_poster.py` | `rendering/render_poster.py` |
| `scripts/website_render_v38.py` | `rendering/website_render_v38.py` |
| `tests_content_engine.py` (root) | `tests/tests_content_engine.py` |
| `scripts/integration_tests.py` | `tests/integration_tests.py` |
| `scripts/test_autonomous_pipeline_v40.py` | `tests/test_autonomous_pipeline_v40.py` |
| `scripts/test_batch_guard_v45.py` | `tests/test_batch_guard_v45.py` |
| `scripts/test_brand_policy_v36.py` | `tests/test_brand_policy_v36.py` |
| `scripts/test_brand_policy_v49.py` | `tests/test_brand_policy_v49.py` |
| `scripts/test_brand_render_v37.py` | `tests/test_brand_render_v37.py` |
| `scripts/test_chatgpt_bridge_v43.py` | `tests/test_chatgpt_bridge_v43.py` |
| `scripts/test_gate_chain_v41.py` | `tests/test_gate_chain_v41.py` |
| `scripts/test_production_controller_v39.py` | `tests/test_production_controller_v39.py` |
| `scripts/test_production_gate.py` | `tests/test_production_gate.py` |
| `scripts/test_strategy_v33.py` | `tests/test_strategy_v33.py` |
| `scripts/test_verify_output.py` | `tests/test_verify_output.py` |
| `scripts/test_website_brand_v38.py` | `tests/test_website_brand_v38.py` |

## Keeps (50)
- Root (7): `README.md`, `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` — mandatory packaging/platform paths, must not move.
- `agents/roles-v34.md` (1), `assets/erudience-owner-approved-logo-2026-11-21.jpg` (1 — never move/replace).
- `references/` (34 of 36) — all except the two moved to `config/`; kept as archival specs, conflicts recorded, not rewritten.
- `reports/` (6) — all v4.9.2 audit evidence stays.
- `skills/erudience/SKILL.md` (1) — entry point; `plugin.yaml` points here.

## Prerequisites before executing this map (not yet done)
1. Thin re-export shims (new files, not in the 88) at `scripts/gate_chain_v41.py`, `scripts/chatgpt_bridge_v43.py`, `scripts/batch_guard_v45.py` (and legacy shims as needed) to preserve the stable import path named in `runtime-and-compatibility-v49.md`.
2. Update policy-JSON paths in `gate_chain_v41.py` and `validate_strategy_v33.py` from `references/` to `config/`; update the `website_render` → `website_brand` cross-directory import; define how `tests/` resolves `core/` / `modules/` / `rendering/` imports (no `__init__.py` exists today).
3. Update SKILL.md / README.md pointers to the new `config/` / `core/` paths (or to the shims).
4. Update CI (`.github/workflows/erudience-regression.yml`, repo root, not read in this task) to the new `tests/` locations.
5. Run the full regression suite against the new layout before committing any move.
6. No empty placeholder modules are created by this map (modules 1, 3, 4, 10 and standalone approval_distribution get no directory).

## Post-consolidation update (2026-11-22)
- All 38 planned moves executed via `git mv` on branch `architecture/erudience-unified-consolidation`. 50 files kept. 0 files deleted.
- New files (not in the 88): 23 compatibility shims (`scripts/` × 22 + `tests/verify_output.py`), 12 package `__init__.py` files, 25 consolidation report files.
- Import/path updates applied: `core/gate_chain_v41.py` and `modules/marketing_strategy/validate_strategy_v33.py` now read `config/production-policy-v33.json`; `rendering/website_render_v38.py` resolves `website_brand_v38` from `modules/brand_claims_qa/`; `tests/tests_content_engine.py` points at `modules/linkedin_copywriting/`; SKILL.md + README.md pointers updated; CI updated to `discover -s tests -p 'test_*.py' -t .`.
