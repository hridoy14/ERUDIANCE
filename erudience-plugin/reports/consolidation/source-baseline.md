# Erudience Plugin — Consolidation Source Baseline

- **Baseline commit actually used:** `9e320fa60785f40142f37be9342b3df42fc47968` — `main`, PR #1 merged 2026-11-22 06:30 +06, "Merge pull request #1 from hridoy14/maintenance/erudience-v4.9.2". Verified by `git fetch origin` (public read, no credentials) before the execution-risk block below. Original v4.9.1 baseline: `c54e5b01d0bcb9ca9a853b6b234580ec1b1fa958`.
- **Plugin version:** v4.9.2 (unchanged by this consolidation; no version increment).
- **Local clone:** `~/workspace/erudiance-plugin-work/ERUDIANCE`, branch at start of work: `maintenance/erudience-v4.9.2` with one uncommitted README edit (41 insertions, "Final folder structure" section). That edit is **not** on `main` and is **not** counted in this baseline.
- **File count in `erudience-plugin/` at baseline:** **88 files** (84 visible + 4 hidden). Breakdown: root 8, `agents/` 1, `assets/` 1, `references/` 36, `reports/` 6, `scripts/` 35, `skills/erudience/` 1. Note: the task brief said references 35 / scripts 36; the directory listing shows references 36 / scripts 35 — total still 88. The 36th Python file is root `tests_content_engine.py`.
- **Logo:** `assets/erudience-owner-approved-logo-2026-11-21.jpg`, owner-approved original, 1536×1536 JPEG, 55,210 bytes, SHA-256 `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226` (quoted from `reports/source-inventory.md` / README; **not recomputed in this task** — no hash command was run after the block).
- **No files were deleted in Phase 1.** No files were moved, renamed, or edited in the repo in this task.

## Execution block — read this first

After the `git fetch` that verified `9e320fa`, the runtime raised an execution-risk check on the repo content and prohibited running, cloning, checking out, extracting, building, testing, importing, loading, or running git/package-manager commands inside it, and prohibited copying/moving its files into a repository. Therefore:

- Branch `architecture/erudience-unified-consolidation` was **NOT created** (no checkout).
- **No consolidation file move was executed** in the repo. The migration map in `file-migration-map.md` is a **plan**, not an executed move. Files moved: 0. Files merged: 0. Files removed: 0.
- **No test was re-run** in this task. Test totals below are the **prior verified v4.9.2 results** from `reports/regression-results.md` (112/112, E2E 20/20), quoted, not re-measured. A hand-count of test methods in the drafts is 122, which conflicts with both README figures (107 and 112) — **unresolved without running the suite**.
- **No commit was made, nothing was pushed, no PR was created.**
- All consolidation work in this task was **read-only file inspection** by three parallel workers, plus synthesis in `~/workspace/erudiance-plugin-work/consolidation-staging/`. The 11 reports in `reports/consolidation/` are **prepared deliverables in staging**, not yet placed on a branch. To execute the moves/tests/commit, the user must give an explicit go-ahead for git + test execution on this repo, after which the plan can be applied as-is.

## File inventory (88 files)

### Root (8)
`README.md`, `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `tests_content_engine.py`
- Manifests: all v4.9.2. The three `plugin.json` copies (root, `.agent-plugin/`, `.claude-plugin/`) are byte-identical host mirrors — COMPATIBILITY_REQUIRED, not duplicates. `.codex-plugin/plugin.json` is a host-extended variant (`defaultPrompt: "erudiance_linkdin"`). `.app.json` and `plugin.yaml` are distinct shapes.

### agents/ (1)
`agents/roles-v34.md` — 18 specialist roles, input/output/gate table; no code maps roles to adapters.

### assets/ (1)
`assets/erudience-owner-approved-logo-2026-11-21.jpg` — see above. Only asset in the plugin.

### references/ (36)
`asset-and-font-policy.md`, `autonomous-execution-v40.md`, `batch-production-v45.md`, `brand-assets-manifest.md`, `brand-policy-current.md`, `brand-source-of-truth-v36.md`, `brand-template-contract-v47.md`, `brief-schema-example.json`, `chat-vision-audit-v35.md`, `chatgpt-runtime-v43.md`, `content-to-creative-brief-v21.md`, `endpoint-registry.json`, `execution-state-machine-v39.md`, `gate-contract-v41.md`, `gates-and-handoff.md`, `integration-registry-v34.json`, `master-action-v31.md`, `master-command-v6.md`, `monthly-weekly-social-os.md`, `one-action-production-contract.md`, `one-command-v44.md`, `orchestrator-v2.md`, `owner-approved-brand-v46.md`, `production-contract-v33.md`, `production-execution-v35.md`, `production-policy-v33.json`, `production-runtime-v37.md`, `release-audit-v34.md`, `release-compatibility-v48.md`, `runtime-and-compatibility-v49.md`, `smb-content-strategy-v32.md`, `strategy-playbook.md`, `system-architecture-v34.md`, `unified-system-v42.md`, `website-brand-profile-v38.md`, `workflow-v3.md`
- Canonical policy: `production-policy-v33.json` (policy version 3.3.0 — **not** the plugin version) and `brand-policy-current.md` (Sora / `#10B77F` / logo optional).

### reports/ (6)
`architecture-audit.md`, `cleanup-evidence.md`, `dependency-map.md`, `regression-results.md`, `release-verification.md`, `source-inventory.md` — all v4.9.2 audit evidence, preserved as-is.

### scripts/ (35)
`autonomous_pipeline_v40.py`, `batch_gate.py`, `batch_guard_v45.py`, `brand_policy_v36.py`, `brand_render_v37.py`, `brief_prompt_gate.py`, `chatgpt_bridge_v43.py`, `competitor_monitor.py`, `content_engine.py`, `evidence_store.py`, `gate_chain_v41.py`, `integration_tests.py`, `keyword_research.py`, `linkedin_analytics.py`, `linkedin_seo_validator.py`, `production_controller_v39.py`, `production_gate.py`, `render_poster.py`, `test_autonomous_pipeline_v40.py`, `test_batch_guard_v45.py`, `test_brand_policy_v36.py`, `test_brand_policy_v49.py`, `test_brand_render_v37.py`, `test_chatgpt_bridge_v43.py`, `test_gate_chain_v41.py`, `test_production_controller_v39.py`, `test_production_gate.py`, `test_strategy_v33.py`, `test_verify_output.py`, `test_website_brand_v38.py`, `validate_strategy_v33.py`, `verify_output.py`, `website_brand_v38.py`, `website_render_v38.py`, `workflow_engine.py`
- Third-party dependency: Pillow only. Everything else is Python stdlib. No network libraries, no provider SDKs. No `requirements.txt` / `pyproject.toml` in the plugin. Fonts are **not** bundled.
- 5 scripts have no test: `evidence_store.py`, `batch_gate.py`, `brief_prompt_gate.py`, `website_render_v38.py`, `render_poster.py`.

### skills/ (1)
`skills/erudience/SKILL.md` — master skill, entry point, command `erudiance_linkdin`.

## Gaps in source availability (explicit)
- `.github/workflows/erudience-regression.yml` (repo root, outside `erudience-plugin/`) was **not** read in this task; CI behaviour is quoted second-hand from `reports/dependency-map.md`.
- Logo bytes were **not** re-verified (binary, no hash command run after the block).
- External sources cited in docs (`erudience-main` / `erudience-social-os` repos, `social-os/BRAND.md` v1.1, Supabase benchmark URL, `social.erudience.com`) do **not** exist in this repo and were **not** fetched — UNVERIFIED.
- No original v4.9.1 archive beyond commit `c54e5b0` was available; history before that was not inspected in this task.

## Prior verified test results (quoted from v4.9.2, not re-run here)
- Baseline on `main@c54e5b0`: 107/107 (83 scripts + 10 content-engine + 14 integration).
- Final v4.9.2: **112/112** (88 + 10 + 14), 0 failed. Offline E2E 20/20 (synthetic fixtures only). Python 3.12.3, Pillow 13.0.0.
- These numbers are **not** re-confirmed by this consolidation task.

## Post-consolidation update (2026-11-22, branch architecture/erudience-unified-consolidation)
- Baseline verified again before migration: main `9e320fa`, 88 files, regression 112/112 (88 + 10 + 14) in an isolated venv (Python 3.12.3, Pillow 13.0.0).
- After migration: 88 original files preserved (38 moved, 50 kept, 0 deleted) + 23 compatibility shims + 12 package `__init__.py` files + 18 new consolidation reports (11 + 6 drafts + E2E script) + 7 agent reports = 148 files under `erudience-plugin/` (count verified by `find` at commit time; see final-verification.md).
- Owner logo unchanged: SHA-256 `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226`.
