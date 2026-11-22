# Erudience Plugin — Dependency & Execution Map (Consolidation)

- Baseline: `main` `9e320fa6` (v4.9.2). Method: read-only inspection. Full per-script table is in `~/workspace/erudiance-plugin-work/consolidation-staging/dependency-map-draft.md`. This report is the consolidated summary.
- **Counts:** 36 capabilities classified; 35 scripts + root `tests_content_engine.py`; 36 references; 6 manifests.

## Canonical execution path (the only connected import chain)
`gate_chain_v41.py` (17 stages, hash-chained, max 3 repairs, `READY_FOR_OWNER_REVIEW` / `TEST_FIXTURE_PASS`) ← `chatgpt_bridge_v43.py` (durable checkpoint CLI: start/next/submit/status) ← `batch_guard_v45.py` (7 jobs, `ER-{cycle}-{i:03d}`).
Plus two single edges: `keyword_research` ← `linkedin_seo_validator`; `website_brand_v38` ← `website_render_v38`. No circular imports.
`scripts/` has no `__init__.py`; cross-module imports use bare names and resolve only from `scripts/` or with `sys.path` insertion — environment-dependent.

## The command has no code implementation
`erudiance_linkdin` (and `--test --single-content ER-001`) exists only in prose (`SKILL.md`, `one-command-v44.md`, `batch-production-v45.md`, `.codex-plugin/plugin.json` `defaultPrompt`). Nearest executables: `batch_guard.initialise()` (Python-only, no CLI) and the bridge CLI. Classification: **documented-only**.

## 17 stages (canonical)
SOURCES, SOURCE_REVIEW, RESEARCH, RESEARCH_REVIEW, STRATEGY, STRATEGY_REVIEW, CONTENT, CONTENT_REVIEW, IMAGE_PLAN, PLAN_REVIEW, IMAGE_BUILD, TECH_REVIEW, VISUAL_REVIEW, CONTENT_IMAGE_REVIEW, BRAND_REVIEW, FINAL_REVIEW, DELIVERY. 9 are `*_REVIEW` stages (reviewer ≠ producer, decision PASS, non-empty observations, `subject_hash` match). Every output carries `upstream_hash`. Repair map: SOURCE_REVIEW→SOURCES, RESEARCH_REVIEW→RESEARCH, STRATEGY_REVIEW→STRATEGY, CONTENT_REVIEW→CONTENT, PLAN_REVIEW→IMAGE_PLAN, TECH/VISUAL/FINAL_REVIEW→IMAGE_BUILD, CONTENT_IMAGE/BRAND_REVIEW→IMAGE_PLAN. Max 3 repairs; 4th failure → BLOCKED; missing adapter → BLOCKED immediately. No publishing, no network calls, no side effects; `external_writes` is always 0.
Known gaps (from `reports/architecture-audit.md` §2, carried forward): RESEARCH and STRATEGY have no stage-specific checks beyond hash binding; FINAL_REVIEW has no check beyond generic binding; TECH_REVIEW does not re-check `image_sha256`; live-mode font verification covers only the heading family; no timestamps in the chain; no owner-approval field/actor/timestamp in any engine.

## Competing execution paths (all disconnected from the canonical path)
| Path | Stages | Entry | Status |
|---|---|---|---|
| `production_controller_v39.py` | 13 | CLI init/pass/fail/status, atomic JSON state | Legacy only per SKILL.md |
| `autonomous_pipeline_v40.py` | 13 (same names) | `Controller(job, adapters).run()` | Superseded; once claimed "only supported" |
| `workflow_engine.py` | 10 | `run(batch, receipts, approval, external_write)` | Legacy 7-slot batch validator; only caller is integration tests |
| `content_engine.py` | 10 (different names) | CLI `--mode gate/calendar/weekly` | Disconnected; own stage vocabulary |
| `production_gate.py` | 9 | `validate(job, receipts, brand, root)` | Disconnected receipt validator |
| Docs only | 20-action / 16-step / 15-stage machines | Prose only | Documented-only |

"Exactly one promotion" is **not** enforced in the canonical path — only in disconnected `workflow_engine` / `validate_strategy_v33`.

## Renderers (all disconnected from the chain)
`brand_render_v37` (Sora, logo mandatory, pins non-existent `social-os/BRAND.md:v1.1`), `render_poster` (Inter/DM Sans, exactly 6 cards, logo required unless `--review-draft`), `website_render_v38` (Inter/DM Sans, 3–5 steps, logo optional). None is invoked by the chain; no IMAGE_BUILD adapter exists. 5 scripts have no test: `evidence_store`, `batch_gate`, `brief_prompt_gate`, `website_render_v38`, `render_poster`.

## Capability classification (36 capabilities)
- Implemented+connected: 1 (17-stage gate).
- Implemented+connected (logic) / environment-dependent (execution): 2 (bridge, batch guard).
- Implemented but disconnected: 10 (content engine, keyword/SEO, competitor monitor, analytics, evidence_store, batch_gate, brief_prompt_gate, production_gate, validate_strategy, verify_output).
- Documented only: 12 (command, live research/writer/image/visual adapters, publishing, Social OS, Supabase, scheduler, OpenAI/Anthropic/GSC, research provider, weekly refresh, 18 roles).
- Partially implemented: 3 (7 jobs + 1 promotion, monthly planning, owner approval).
- Conflicting: 7 (renderers, brand enforcement, legacy controllers, 10-stage workflow, website brand, logo rule, stage counts).
- Unavailable historical source: 1 (website repo, Social OS BRAND.md, Supabase URL, social.erudience.com).

## Config / asset / manifest references
- `production-policy-v33.json` (v3.3.0 policy version): read at import by `gate_chain_v41` (live); read but never used by `validate_strategy_v33` (dead load). Cited as authoritative by SKILL.md, brand-policy-current, README.
- `integration-registry-v34.json`: all six integrations NOT_CONFIGURED. `endpoint-registry.json`: providers DOCUMENTED_PROVIDER_API_NOT_CONNECTED / UNVERIFIED. **No code reads either registry.**
- Logo `assets/erudience-owner-approved-logo-2026-11-21.jpg`: hash-checked by `gate_chain_v41` at IMAGE_BUILD when planned.
- Fonts are not bundled; renderers fail closed without verified local font files.

## Test-count discrepancy (unresolved, not re-verified)
README says 107 tests in one section and 112 in another; a hand-count of test methods as read is 122. Nothing was executed in this task to settle it. Treat all three numbers as unverified; the prior executed result is 112/112 (see `regression-results.md`).

## Post-consolidation update (2026-11-22)
- Wiring improved by exactly one mechanism: `tests/__init__.py` now inserts the canonical module directories into `sys.path`, and `scripts/` holds 23 thin shims re-exporting the canonical modules. Test imports resolve; production imports unchanged in behaviour.
- Capability classification unchanged: implemented+connected 1 (17-stage gate); implemented but disconnected 10; documented-only 12; partially implemented 3; conflicting 7; unavailable historical source 1.
- The `erudiance_linkdin` command still has no code implementation (documentation only). No live adapters were created.
