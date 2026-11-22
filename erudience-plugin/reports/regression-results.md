# Erudience Plugin — Regression Results (v4.9.2)

- Date: 2026-11-22 (Asia/Dhaka). Baseline: `main@c54e5b0` (89 files, logo absent). Final: branch `maintenance/erudience-v4.9.2` (90 files, logo bundled).
- Environment: isolated venv `/tmp/erud-venv` (ephemeral, removed after use is not required — it lives outside the repo), **Python 3.12.3, Pillow 13.0.0** (`pip install Pillow`). No `requirements.txt` exists in the repo; Pillow is the only third-party dependency, declared only in `.github/workflows/erudience-regression.yml` (which pins Python 3.11). No other packages were installed. No network access was used by any test.
- Commands run exactly as specified in the task (plus the CI's explicit `integration_tests.py -v` form).

## Baseline (before any change, `main`)

| Suite | Command | Result |
|---|---|---|
| Compile | `python -m compileall -q scripts tests_content_engine.py` | **OK** (no output, exit 0) |
| Scripts unit tests | `python -m unittest discover -s scripts -p 'test_*.py' -v` | **83 ran, 83 passed, 0 failed, 0 errors, 0 skipped** (1.154 s) |
| Content engine | `python -m unittest tests_content_engine -v` | **10 ran, 10 passed** |
| Integration | `python scripts/integration_tests.py -v` | **14 ran, 14 passed** |
| **Baseline total** | | **107 passed / 0 failed** |

## Code defect found and fixed

**`scripts/verify_output.py` — unsafe import (real defect, found by inspection, confirmed by the child audit).**
The module ran `argparse` parsing, all PNG checks, and `sys.exit()` at module top level with no `if __name__ == '__main__'` guard, so merely importing it parsed the importer's `sys.argv` and exited. Fix (v4.9.2): execution moved into `main(argv)` returning an exit code, with `if __name__ == '__main__': sys.exit(main())`. CLI behaviour, checks, output format, and exit codes are unchanged. No other production-code defect was found: no test failed on the baseline, and no assertion was weakened or re-encoded at any point. In particular, **no test encoding a brand value was changed** — the Sora/`#10B77F` vs Inter/DM Sans/`#10B981` split is a documented dual-profile conflict (see `reports/architecture-audit.md` §4), not a test bug.

New regression test `scripts/test_verify_output.py` (5 tests): import does not exit; valid PNG passes (exit 0, `PASS_MECHANICAL_ONLY`); `--require-logo` passes when declared; missing PNG blocks (exit 2, `BLOCK missing PNG`); wrong dimensions block (exit 2).

## Final regression (after all changes, incl. version sync + logo + fix)

| Suite | Result |
|---|---|
| Compile | **OK** |
| Scripts unit tests (`discover -s scripts -p 'test_*.py'`) | **88 ran, 88 passed** (83 baseline + 5 new) |
| Content engine | **10 passed** |
| Integration | **14 passed** |
| **Final total** | **112 passed / 0 failed / 0 errors / 0 skipped** |

Comparison vs baseline: +5 tests (all new, all passing); 0 regressions; 0 tests removed or weakened.

## Other test entrypoints (executed)

| Entrypoint | Result |
|---|---|
| `python scripts/validate_strategy_v33.py /tmp/strat_valid.json` (7 slots, 1 promotion + employee requirement) | `{"status": "PASS", "errors": []}`, exit 0 |
| `python scripts/validate_strategy_v33.py /tmp/strat_bad.json` (2 promotions) | `{"status": "BLOCKED", "errors": ["Exactly one promotional slot required", "Promotion missing employee requirement", ...]}`, exit 1 |
| `python scripts/verify_output.py --require-logo <1080x1350 PNG + manifest>` | `PASS_MECHANICAL_ONLY`, exit 0 |
| `python scripts/render_poster.py --help` | Usage shown (requires 4 Inter/DM Sans font paths, optional `--logo`, `--review-draft`); not executed to render — no verified font binaries exist in the repo, and rendering without them would be a fabricated brand claim |
| `python scripts/brand_render_v37.py` (no args) | Usage error (requires `--spec` + `--output`); not executed to render — no verified Sora font binaries or spec exist in the repo |
| `python scripts/integration_tests.py -v` | Covered above (14 passed) |

## End-to-end offline workflow test (synthetic fixtures only, `/tmp/e2e_erud.py`)

20 checks, run in the same venv. No live accounts, no network, no external publishing; all fixtures are synthetic (blank 1080×1350 PNG, fixture-only sources, fixture reviewer names). First run: **15/17 passed**; the 2 failures were bugs in *my test script*, not in plugin code — (a) the logo-present fixture omitted `original_logo_checked`, which `gate_chain_v41` BRAND_REVIEW requires when a logo is planned; (b) the workflow check expected an exception where `workflow_engine.run()` returns a `BLOCKED` dict. Both were corrected in the script (and 3 strategy-validation checks added), and the corrected run passed **20/20**:

| Check | Result |
|---|---|
| Logo file exists at canonical path, 55,210 bytes | PASS |
| Logo dimensions 1536×1536 JPEG | PASS |
| 17-stage gate, logo-absent → `TEST_FIXTURE_PASS`, 17 stages | PASS |
| 17-stage gate, logo-present → `TEST_FIXTURE_PASS`, 17 stages | PASS (this path was unexercisable before the logo was bundled — `ORIGINAL_LOGO_PROVENANCE_REQUIRED` needs the real file) |
| Failure recovery: VISUAL_REVIEW fails once → rebuild + recheck, `repairs == 1`, `IMAGE_BUILD` called twice, still `TEST_FIXTURE_PASS` | PASS |
| Unapproved logo (`assets/fake-logo.png`) → `BLOCKED` | PASS |
| Missing adapter (`IMAGE_PLAN` removed) → `BLOCKED` | PASS |
| Batch guard: 7 distinct topics → 7 jobs, all `IN_PROGRESS` | PASS |
| Batch re-initialisation rejected (`BATCH_ALREADY_EXISTS`) | PASS |
| Duplicate batch topic rejected (`SEVEN_DISTINCT_TOPICS_REQUIRED`) | PASS |
| Bridge state persistence (`ER-2026-W47-001.json`, next stage `SOURCES`) | PASS |
| `weekly_batch` with 7 items | PASS |
| Workflow with no receipts → `BLOCKED` | PASS |
| Two promotions → `WorkflowError` | PASS |
| `external_write=True` → `WorkflowError` (no external writes) | PASS |
| Strategy valid (7 slots, exactly 1 promotion) → `[]` | PASS |
| Strategy two promotions → `Exactly one promotional slot required` | PASS |
| Strategy topic deletion → `Topic deletion forbidden` | PASS |
| `verify_output.py --require-logo` mechanical gate → `PASS_MECHANICAL_ONLY` | PASS |

Not verified (and not claimed): live research/source validation against real URLs, real Sora/Inter/DM Sans font rendering, human visual QA of a real poster, any external integration (all NOT_CONFIGURED), and Plugin Creator publishing (no integration available — see `reports/release-verification.md`).

## Brand consistency (regression scope)

- No production file's brand tokens were rewritten. `gate_chain_v41` enforces the canonical JSON (Sora / `#10B77F`); website-first renderers keep Inter/DM Sans / `#10B981` as their tests and reference docs encode them. Full rationale in `reports/architecture-audit.md` §4.
- Secrets scan of `erudience-plugin/`: no credentials/tokens/keys found (only documentation wording and credential env-var *names* in `endpoint-registry.json`, all `NOT_CONNECTED`).
- No external writes occurred during any test run (tests use `tempfile` dirs under `/tmp`; the only repo writes were the deliberate source edits and the logo copy).
