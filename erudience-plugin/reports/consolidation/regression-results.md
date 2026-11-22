# Erudience Plugin — Regression Results (Consolidation)

- Baseline: `main` `9e320fa6` (v4.9.2). **No test was run in this consolidation task** (execution block, see `source-baseline.md`). All numbers below are prior verified v4.9.2 results quoted from `reports/regression-results.md`, or explicitly marked unverified. Nothing here is a new measurement.

## Prior verified results (v4.9.2, executed 2026-11-22, isolated venv Python 3.12.3, Pillow 13.0.0)
| Suite | Command (as run then) | Result |
|---|---|---|
| Compile | `python -m compileall -q scripts tests_content_engine.py` | OK (exit 0) |
| Scripts unit tests | `python -m unittest discover -s scripts -p 'test_*.py' -v` | Baseline 83 passed; final **88 passed** (83 + 5 new) |
| Content engine | `python -m unittest tests_content_engine -v` | 10 passed |
| Integration | `python scripts/integration_tests.py -v` | 14 passed |
| **Total** | | **Baseline 107/107 → final 112/112, 0 failed** |
| Offline E2E (synthetic fixtures) | `/tmp/e2e_erud.py` (20 checks) | **20/20** (17-stage gate logo-absent/present, recovery repairs=1, unapproved-logo block, missing-adapter block, 7-content batch 1 promotion, idempotency, bridge persistence, strategy validation, external-write refusal, mechanical PNG gate) |
| Strategy validation | `validate_strategy_v33.py` (7 slots 1 promotion + employee requirement) | PASS, exit 0; 2-promotion batch BLOCKED, exit 1 |
| Mechanical PNG gate | `verify_output.py --require-logo` (1080×1350 PNG + manifest) | `PASS_MECHANICAL_ONLY`, exit 0 |

## Discrepancy — unresolved, must be settled by execution
- README "Testing" section says 107 tests; README "Version history" says 112/112; a hand-count of test methods as read in this task is **122** (98 in `scripts/test_*.py` + 10 content-engine + 14 integration). No execution was done to settle which figure is correct. The 112 figure is the last *executed* total; the 122 figure is a *read* count and may double-count or misread parametrised/looped tests. **Do not quote 122 as a test result.**

## Consolidation regression — NOT RUN
- Baseline re-run on `main@9e320fa6`: **not run** (blocked).
- After each consolidation group: **not run** (no groups executed).
- Full regression + integration + offline E2E after consolidation: **not run**.
- Import compatibility checks: **not run**.
- Characterization tests for untested modules (`evidence_store`, `batch_gate`, `brief_prompt_gate`, `website_render_v38`, `render_poster`): **not added** (adding them requires running them).
- Tests removed or weakened in this task: **0**. Assertions changed: **0**.

## What must be run (in order, after user go-ahead for git + test execution)
1. Baseline re-run on `main@9e320fa6` in a fresh isolated venv (Python 3.12, Pillow only): compileall, discover, content-engine, integration, E2E. Record actual totals and resolve the 107/112/122 discrepancy.
2. Re-run after each migration group; stop and restore on any failure.
3. Final full run after all moves; compare against the re-run baseline (not the quoted 112).

## Post-consolidation run (2026-11-22, isolated venv, Python 3.12.3, Pillow 13.0.0)
- `python -m compileall -q core modules rendering tests scripts config` — OK.
- `python -m unittest discover -s tests -p 'test_*.py' -t .` — 88 tests, OK.
- `python -m unittest tests.tests_content_engine` — 10 tests, OK.
- `python -m unittest tests.integration_tests` — 14 tests, OK.
- Total: 112/112 pass, 0 failed — identical to the pre-migration baseline (112/112 on `main@9e320fa`).
- Offline E2E (recreated script, `reports/consolidation/e2e_consolidation.py`): 25/25 pass.
- Two real defects found and fixed during migration (not test-weakening): (1) `tests/__init__.py` bootstrap did not run under plain `discover -s tests` — CI updated to add `-t .`; (2) `modules/marketing_strategy/validate_strategy_v33.py` used `parents[1]` which resolves to `modules/` after the move — corrected to `parents[2]`; (3) shims initially failed on `@dataclass` modules (spec name not in `sys.modules`) and on CLI use (`__name__ == '__main__'`) — both fixed in the shim template.
- No assertion was weakened or deleted.
