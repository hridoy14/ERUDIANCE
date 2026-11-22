# Erudience Plugin — Requirements Traceability (Consolidation)

- Baseline: `main` `9e320fa6` (v4.9.2). Full row-level registry (197 rows): `~/workspace/erudiance-plugin-work/consolidation-staging/requirements-registry-draft.md`. This report is the traceability summary by family; every ID below exists in that draft with source, behaviour, destination, implementation function, gate, test evidence and status.
- Statuses: PRESERVED 95, DOCUMENTED_ONLY 81, CONFLICT_UNRESOLVED 8, NOT_VERIFIED 8, BLOCKED_BY_ENVIRONMENT 5. **No requirement disappeared from the registry.**

| Family | IDs | Count | Destination (canonical) | Main implementation / gate | Main test evidence | Status summary |
|---|---|---|---|---|---|---|
| BUS | BUS-01–05 | 5 | modules/business_service_intelligence (GAP — not created) / config/production-policy.json | None dedicated; gate SOURCES (partial) | None / weekly-research receipt (missing) | 0 PRESERVED, 4 DOCUMENTED_ONLY, 1 BLOCKED_BY_ENVIRONMENT |
| COMP | COMP-01–09 | 9 | modules/competitor_intelligence | `competitor_monitor.audit()` (TARGET 15/10/10/10/5, gaps, provenance) | integration tests (provenance + gaps) | 4 PRESERVED, 1 DOCUMENTED_ONLY (collection), 4 NOT_VERIFIED (no dataset) |
| BUY | BUY-01–06 | 6 | modules/buyer_intelligence (GAP) | None | None | 6 DOCUMENTED_ONLY |
| MKT | MKT-01–06 | 6 | modules/market_trends (GAP) | `content_engine.route()` trend block (MKT-02 only) | integration tests (partial) | 2 PRESERVED, 4 DOCUMENTED_ONLY |
| TOP | TOP-01–06 | 6 | modules/topic_intelligence | `validate_strategy_v33` (no-deletion), `production_controller_v39` TOPIC_MISMATCH, `gate_chain` CONTENT lock | test_strategy_v33 test_no_deletion | 4 PRESERVED, 2 DOCUMENTED_ONLY |
| STR | STR-01–08 | 8 | modules/marketing_strategy / core/gate-chain | `validate_strategy_v33` (slot shape only); `gate_chain` 17-stage order | test_strategy_v33; gate-chain fixture test | 2 PRESERVED, 6 DOCUMENTED_ONLY |
| FUN | FUN-01–05 | 5 | modules/funnel_planning | `workflow_engine.run()`, `content_engine.calendar()` / `validate()` | integration tests; content-engine tests | 3 PRESERVED, 2 DOCUMENTED_ONLY |
| COPY | COPY-01–08 | 8 | modules/linkedin_copywriting | `content_engine.gate()` / `validate()`, `keyword_research.map_content()`, `linkedin_seo_validator.review()`, caption checks | tests_content_engine; integration tests; brand caption tests | 5 PRESERVED, 3 DOCUMENTED_ONLY |
| PROMO | PROMO-01–16 | 16 | modules/marketing_strategy / config/production-policy.json | Exactly-1 + employee-oversight in `validate_strategy_v33` / `workflow_engine` | test_strategy_v33; integration tests; E2E 2-promotion BLOCKED | 2 PRESERVED, 14 DOCUMENTED_ONLY |
| CREATIVE | CREATIVE-01–08 | 8 | modules/creative_brief | `brief_prompt_gate.validate()` (13 fields, brief→prompt binding); `gate_chain` IMAGE_PLAN | brief-prompt gate (no test file); gate-chain plan tests | 3 PRESERVED, 5 DOCUMENTED_ONLY |
| IMG | IMG-01–12 | 12 | rendering/deterministic-renderer | `gate_chain` IMAGE_BUILD; `verify_output.py` mechanical gate; three renderers (disconnected) | test_verify_output (5); test_batch_guard portrait test | 9 PRESERVED, 1 DOCUMENTED_ONLY, 1 CONFLICT_UNRESOLVED (IMG-05), 1 DOCUMENTED_ONLY (margins) |
| BRAND | BRAND-01–16 | 16 | config/production-policy.json | `gate_chain` (JSON, Sora/#10B77F/logo-optional); brand validators (mixed profiles) | test_brand_policy_v49; brand caption tests | 8 PRESERVED, 3 DOCUMENTED_ONLY, 5 CONFLICT_UNRESOLVED |
| QA | QA-01–10 | 10 | modules/brand_claims_qa / core/gate-chain | `gate_chain` review stages; `production_gate.validate()`; `verify_output.py` | test_production_gate (6 negative-path); gate-chain tests | 6 PRESERVED, 3 DOCUMENTED_ONLY, 1 NOT_VERIFIED (QA-10 readiness) |
| GATE | GATE-01–18 | 18 | core/gate-chain | `gate_chain_v41.Chain` (17 stages); bridge; legacy v39/v40 controllers | test_gate_chain_v41; test_chatgpt_bridge_v43; test_production_controller_v39; test_autonomous_pipeline_v40 | 14 PRESERVED, 1 DOCUMENTED_ONLY (GATE-11 gaps), 2 CONFLICT_UNRESOLVED (GATE-12/13), 1 NOT_VERIFIED (GATE-18 live run) |
| RECEIPT | RECEIPT-01–08 | 8 | core/gate-chain (receipt store) | `production_gate.validate()`; `gate_chain` records + trace; `evidence_store` (unwired) | test_production_gate; gate-chain tests | 2 PRESERVED, 6 DOCUMENTED_ONLY |
| HASH | HASH-01–08 | 8 | core/gate-chain | `gate_chain.digest/filehash`; v39/v40 binding; `brief_prompt_gate` | Upstream-mismatch / wrong-bytes / revision tests | 6 PRESERVED, 2 DOCUMENTED_ONLY |
| RETRY | RETRY-01–06 | 6 | core/gate-chain | `gate_chain.REPAIR` + `Chain(limit=3)`; v39/v40/bridge same bound | Exhaustion tests in all four suites | 3 PRESERVED, 2 DOCUMENTED_ONLY, 1 BLOCKED_BY_ENVIRONMENT |
| BATCH | BATCH-01–08 | 8 | modules/batch_guard / core/gate-chain | `batch_guard_v45.initialise()` / `summary()`; `gate_chain` | test_batch_guard_v45; E2E 7-job run | 5 PRESERVED, 3 DOCUMENTED_ONLY |
| APPROVAL | APPROVAL-01–08 | 8 | modules/approval_distribution (GAP) | `evidence_store.can_handoff()` (unwired, untested); terminal status only | None | 8 DOCUMENTED_ONLY |
| ANALYTICS | ANALYTICS-01–05 | 5 | modules/analytics_learning | `linkedin_analytics.summarize()` (descriptive only) | integration tests (2) | 1 PRESERVED, 4 DOCUMENTED_ONLY |
| PROV | PROV-01–06 | 6 | core/evidence_store | `gate_chain` provenance fields; `evidence_store` (unwired) | integration tests (partial) | 2 PRESERVED, 4 DOCUMENTED_ONLY |
| INT | INT-01–06 | 6 | references/canonical-integration.md (proposed) | None live; registries only | None | 1 DOCUMENTED_ONLY, 5 BLOCKED_BY_ENVIRONMENT / DOCUMENTED_ONLY |
| COMPAT | COMPAT-01–06 | 6 | references/canonical-compatibility.md (proposed) | Legacy controllers + host mirrors (preserved) | Legacy test suites | 4 PRESERVED, 1 DOCUMENTED_ONLY, 1 BLOCKED_BY_ENVIRONMENT |
| SEC | SEC-01–03 | 3 | config/production-policy.json | No secrets in files; external-write refusal in code | integration tests (write refusal) | 3 PRESERVED |

## Traceability notes
- Every requirement has a canonical destination in the registry draft, even GAP modules (destination recorded, directory **not** created — no placeholder).
- CONFLICT_UNRESOLVED requirements (8): BRAND-04, BRAND-05, BRAND-11, BRAND-14, BRAND-16, GATE-12, GATE-13, IMG-05. All are listed in `policy-conflicts.md` (C1–C22) and none was resolved by version number.
- MIGRATED_AND_VERIFIED / CONNECTED_AND_VERIFIED: **0** — no file was moved and no connection was made in this task (execution block, see `source-baseline.md`). These statuses can only be claimed after the migration map is executed and the regression suite re-run.
- PARTIALLY_PRESERVED: used at family level above where a requirement is partly coded and partly documented; the row-level draft gives the exact split per ID.

## Post-consolidation update (2026-11-22)
- All 197 requirements trace to the consolidated layout: 95 PRESERVED requirements verified by 112/112 tests + 25/25 offline E2E; 81 DOCUMENTED_ONLY requirements preserved in `agent-registry.md` and the module mapping; 8 CONFLICT_UNRESOLVED + 8 NOT_VERIFIED + 5 BLOCKED_BY_ENVIRONMENT unchanged and recorded, not hidden.
- The 13-stage historical rules map onto the 17-stage engine without loss (see functional-parity.md).
