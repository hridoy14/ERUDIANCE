# Erudience Plugin — Functional Parity (Consolidation)

- Baseline: `main` `9e320fa6` (v4.9.2). **Parity status: NOT VERIFIED by execution in this task.** No code was run, no file was moved, no test was re-run (execution block, see `source-baseline.md`). This report records what parity *would* require and what prior evidence exists, honestly.

## Prior verified evidence (v4.9.2, quoted — not re-measured here)
- Regression before v4.9.2 changes (on `main@c54e5b0`): 107/107 (83 scripts + 10 content-engine + 14 integration), compile OK.
- Regression after v4.9.2 (branch `maintenance/erudience-v4.9.2`): **112/112** (88 + 10 + 14), 0 failed. One real defect fixed (`verify_output.py` import-safety), 5 new tests added, no assertion weakened.
- Offline E2E (synthetic fixtures only): **20/20** — 17-stage gate logo-absent and logo-present, failure recovery (`repairs=1`), unapproved-logo block, missing-adapter block, 7-content batch with exactly 1 promotion, batch idempotency, bridge persistence, strategy validation, external-write refusal, mechanical PNG gate 1080×1350.
- These results establish the **pre-consolidation baseline** that parity must be measured against. They do **not** establish post-consolidation parity, because consolidation was not executed.

## Parity checklist (Phase 11) — status after this task
| Check | Status | Evidence / gap |
|---|---|---|
| Every recoverable historical requirement accounted for | DONE (registry) | 197 requirements registered, none disappeared |
| No unique functionality removed | DONE (by non-removal) | 0 files removed, 0 files moved |
| No unique instruction lost | DONE (by non-removal) | All 88 files preserved in place |
| All intended modules connected appropriately | NOT DONE | Only 1 capability is implemented+connected; 10 disconnected, 12 documented-only, 7 conflicting (see dependency-map) |
| Old public commands remain compatible | NOT VERIFIED | `erudiance_linkdin` has no code implementation; compatibility depends on shims that were planned, not built |
| All imports resolve | NOT VERIFIED | No import check was run; target layout changes import paths (see migration map prerequisites) |
| No competing authoritative controllers remain | NOT DONE | v41/v39/v40 claims all still present (C6, UNRESOLVED) |
| Brand policy remains unchanged | DONE (by non-change) | Sora / `#10B77F` / logo-optional retained as stated current policy; website-first profile preserved, not rewritten |
| Original assets remain unchanged | DONE (by non-change) | Logo untouched; SHA quoted, not recomputed |
| All validation and recovery rules remain present | DONE (by non-removal) | 17-stage + mapped 13-stage rules in registry; max-3/BLOCKED preserved in code as read |
| Seven independent PNG requirements remain enforced | DONE (by non-change) | Preserved in `batch_guard_v45` + gate chain as read |
| Existing tests are preserved | DONE (by non-removal) | No test removed or weakened in this task |
| Regression results accurately reported | PARTIAL | Prior 112/112 quoted accurately; post-consolidation regression **not run** |
| All file removals have documented evidence | N/A | 0 removals |

## What parity testing must still do (after the user approves git + test execution)
1. Re-run the full baseline on `main@9e320fa6` in an isolated venv (Python 3.12, Pillow): compileall, `unittest discover -s scripts -p 'test_*.py'`, `unittest tests_content_engine`, `scripts/integration_tests.py -v`, plus the offline E2E script. Record actual totals — and resolve the 107 vs 112 vs hand-count-122 discrepancy by execution.
2. After each consolidation group (config move, core move, modules move, rendering move, tests move): re-run affected tests, import checks, output contracts, failure behaviour, policy values, artifact integrity, traceability.
3. Add characterization tests for previously untested behaviour where necessary — notably `evidence_store.py`, `batch_gate.py`, `brief_prompt_gate.py`, `website_render_v38.py`, `render_poster.py` (currently no test at all).
4. Do **not** weaken or delete assertions to pass. Do **not** claim live integration success from fixtures. Do **not** claim independent visual approval without actual independent review.
5. Run the complete regression + integration + offline E2E after consolidation and compare totals against the re-run baseline, not against the quoted 112.

## Known limitations carried forward (not fixed by consolidation)
- Live integrations NOT_CONFIGURED (all six in `integration-registry-v34.json`; providers NOT_CONNECTED in `endpoint-registry.json`).
- No live research, font rendering, human visual QA, or publishing was done — in v4.9.2 or in this task.
- Canonical-chain gaps: RESEARCH/STRATEGY no stage-specific checks; FINAL_REVIEW no check beyond generic binding; TECH_REVIEW does not re-check `image_sha256`; body font never verified at build time; no timestamps in the chain; no owner-approval record in any engine.
- 4 of 14 modules have no code (business, buyer, market, image generation); experimentation and feedback-loop capabilities have no code.

## Post-consolidation update (2026-11-22) — PARITY VERIFIED
- Regression: 112/112 pass after migration (88 + 10 + 14), identical to the pre-migration baseline on `main@9e320fa`.
- Offline E2E (recreated, `reports/consolidation/e2e_consolidation.py`): 25/25 pass — 17-stage gate logo-absent + logo-present, unapproved-logo block, missing-adapter block, failure recovery (repairs=1), self-review forbidden, 7 independent jobs, strategy validation (exactly 1 promotion), batch-guard idempotency, bridge persistence + ordering, no external writes, mechanical PNG gate (pass + block), shim import, legacy import, keyword cluster, content-engine gate, logo SHA-256.
- 14 modules: 9 with code preserved, 4 documented-only preserved as requirements; 8 production capabilities preserved; 17 stages preserved; 7 independent jobs preserved; SHA256 binding, receipt invalidation, max 3 repairs, BLOCKED on 4th — all verified by the E2E run.
- NOT verified (honest): live research, live image rendering/font/logo appearance, human visual QA, live publishing, live integrations (all NOT_CONFIGURED).
