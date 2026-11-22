# Erudience Plugin — Cleanup Evidence (v4.9.2)

- Branch: `maintenance/erudience-v4.9.2` (from `main@c54e5b0`). Method per item: search all source references, test references, manifest references, dynamic imports, compatibility dependencies; confirm equivalent functionality remains; regression before removal; remove; regression after.
- Regression before removal: **112 passed / 0 failed** (88 scripts + 10 content-engine + 14 integration) + E2E 20/20. Regression after removal: **112 passed / 0 failed** + E2E 20/20 (rerun 2026-11-22, Python 3.12.3 / Pillow 13.0.0). No functionality lost.

## Deleted files (9) — historical README stubs

All nine had **zero active references**: whole-repo grep for `README-v` finds only `README.md:16` (generic glob mention, now updated) and the files themselves; no code, test, manifest, or CI file references any individual filename. No dynamic imports touch them (they are Markdown). Deletion impact: documentation only.

| Candidate | Unique info found | Destination of preserved info | Active refs | Dependency impact | Decision |
|---|---|---|---|---|---|
| `README-v33.md` (1 line, 31 words) | None — 14 modules / 8 capabilities enumerated in `production-policy-v33.json`; read-only default in same JSON + README.md safety section | Already in `production-policy-v33.json` + `README.md` | 0 | None | **DELETE** |
| `README-v34.md` (5 lines, 54 words) | Local test invocation **order** (`test_strategy_v33.py`, `tests_content_engine.py`, then `integration_tests.py -v`) + pointer to `references/release-audit-v34.md` for known blockers | Ported into `README.md` "Historical version notes" section | 0 | None | **DELETE** (after port) |
| `README-v35.md` (1 line, 41 words) | "Six negative-path tests" — count exists nowhere else; **verified**: the six methods in `scripts/test_production_gate.py` | Ported into `README.md` with verification note | 0 | None | **DELETE** (after port + verification) |
| `README-v36.md` (2 lines, 55 words) | None — Inter/DM Sans vs Sora conflict recorded in `references/brand-source-of-truth-v36.md` + `README.md` brand section; checks live in `brand_policy_v36.py` + its test | Already in references + `README.md` | 0 | None | **DELETE** |
| `README-v37.md` (1 line, 30 words) | "Four tested brand-failure paths" — count exists nowhere else; **verified**: the four methods in `scripts/test_brand_render_v37.py` | Ported into `README.md` with verification note | 0 | None | **DELETE** (after port + verification) |
| `README-v39.md` (2 lines, 42 words) | v3.9-specific non-proof warning ("Legacy gates remain historical and cannot be used as proof of v3.9 production success"; "Real research/review/AI rendering adapters are not implemented"). "14 regression tests" corroborated by `test_production_controller_v39.py` (14 methods) | Warning ported into `README.md` | 0 | None | **DELETE** (after port) |
| `README-v40.md` (8 lines, 71 words) | None — "12 fixture-backed tests" verbatim in `references/autonomous-execution-v40.md:17` and corroborated by 12 methods in `test_autonomous_pipeline_v40.py`; retries/invalidation in same reference; legacy isolation in SKILL.md + runtime-v49 | Already in references + SKILL.md | 0 | None | **DELETE** |
| `README-v41.md` (1 line, 26 words) | None — 17-stage gate in `README.md`; rollback in `references/gate-contract-v41.md:7`; "10 tests" corroborated by 10 methods in `test_gate_chain_v41.py`; adapters-not-included in `README.md` safety section | Already in `README.md` + references | 0 | None | **DELETE** |
| `README-v42.md` (2 lines, 41 words) | None — unified entrypoint in `README.md`; deprecation in `references/unified-system-v42.md:14` + runtime-v49; unconnected endpoints in `README.md` safety section | Already in `README.md` + references | 0 | None | **DELETE** |

Notes: there is no `README-v38.md` in the repo — nothing to decide for v38 (`README.md` covers "v3.6–v3.8 brand experiments"). The README.md:16 gate ("retained until complete source-specific regression checks and review establish they can be safely deleted") is satisfied by the full 112-test regression + 20-check E2E recorded in `reports/regression-results.md`.

## Considered and NOT deleted

| Candidate | Why kept |
|---|---|
| `plugin.json` / `.agent-plugin/plugin.json` / `.claude-plugin/plugin.json` (byte-identical) | Intentional host mirrors — one manifest per plugin-host location; deleting any breaks that host's discovery. |
| `production_controller_v39.py`, `workflow_engine.py`, `autonomous_pipeline_v40.py` | Legacy controllers with unique functionality the canonical chain lacks (v39: atomically persisted state; v40: deterministic content/brand validators; workflow_engine: 7-slot batch rules exercised by integration tests). SKILL.md + runtime-v49 say "do not remove without checking all callers". |
| `evidence_store.py` | No caller and no test, but the *only* owner-approval + write-authorisation model (`can_handoff()` needs separate `APPROVE` + `WRITE_AUTHORISE` rows). Deleting it would remove unique functionality. |
| `brand_policy_v36.py`, `brand_render_v37.py`, `render_poster.py`, `website_brand_v38.py`, `website_render_v38.py`, `production_gate.py`, `batch_gate.py`, `brief_prompt_gate.py`, `validate_strategy_v33.py`, `verify_output.py`, `content_engine.py`, `keyword_research.py`, `linkedin_seo_validator.py`, `competitor_monitor.py`, `linkedin_analytics.py` | Each is exercised by the regression suite and/or holds unique checks (e.g. `verify_output`'s mechanical PNG gate, `brief_prompt_gate`'s brief→prompt binding). No equivalent functionality elsewhere. |
| All `references/*.md` / `*.json` | Historical references are archival by design; several are cited by SKILL.md/README.md. No reference file was deleted. |
| Owner-approved logo `assets/erudience-owner-approved-logo-2026-11-21.jpg` | Owner-approved original asset — must never be deleted or replaced. |

## Brand-correction decision (NOT applied in v4.9.2 — pending owner decision)

Full scan found two mutually exclusive brand profiles, both documented as authoritative by different in-repo sources:
- **Canonical JSON profile:** Sora, `#10B77F`, logo optional (`production-policy-v33.json`, SKILL.md, `brand-policy-current.md`, README.md). Enforced only by `gate_chain_v41.py`.
- **Website-first profile:** Inter/DM Sans, `#10B981`, logo required for new posters (`owner-approved-brand-v46.md`, `brand-template-contract-v47.md`, `release-compatibility-v48.md`, `master-command-v6.md` — which records an explicit owner choice of website fonts over Sora — plus the website renderers and their tests).

The 8-item correction list that would follow from adopting the JSON profile (rewrite `#10B981`→`#10B77F` and Inter/DM Sans→Sora in `autonomous_pipeline_v40.py`, `brand_policy_v36.py`, `brand_render_v37.py`, `render_poster.py`, `website_brand_v38.py`, `website_render_v38.py`; make logo conditional in `brief_prompt_gate.py` and `production_gate.py`; plus rewrites of `test_website_brand_v38.py`, `test_autonomous_pipeline_v40.py`, `test_brand_policy_v36.py`, `test_brand_render_v37.py`) was **not applied**, because:
1. Those renderers' website-first values are deliberate, test-encoded unique functionality — rewriting them deletes the website-brand profile the owner explicitly chose for website-matched posters.
2. The task's non-negotiables forbid weakening/re-encoding assertions merely to make tests pass; the correction would require exactly that in 4 test files.
3. The conflict is genuinely unresolved in-repo (v46/v47/v48 claim to supersede the JSON profile; SKILL.md claims the reverse; `release-compatibility-v48.md` even claims `gate_chain_v41` enforces logo-required, which the code does not).
4. No file uses a third font or third emerald — there is no *unambiguous* active inconsistency to correct.

What v4.9.2 *did* change on brand: bundled the real approved logo (previously missing), which unblocks the logo-present path in `gate_chain_v41.py` (E2E-verified). The pending correction list and the full conflict analysis are recorded in `reports/architecture-audit.md` §4 and `reports/release-verification.md` (Known limitations) for the owner to decide.

## Code change in v4.9.2 (non-deletion)

- `scripts/verify_output.py`: moved top-level argparse/checks/`sys.exit()` into `main(argv)` with an `if __name__ == '__main__'` guard — the module was previously un-importable (importing it parsed `sys.argv` and exited). CLI behaviour, checks, output, and exit codes unchanged. New test `scripts/test_verify_output.py` (5 tests) covers import safety + CLI pass/block paths. Before/after regression: 107 → 112 tests, all passing.
