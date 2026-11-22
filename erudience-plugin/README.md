# Erudience LinkedIn Content & Image Plugin — v4.9.2

## Status
v4.9.2 consolidated layout (branch `architecture/erudience-unified-consolidation`, not yet merged to `main`): the 88 v4.9.2 files are preserved — 38 moved into `config/`, `core/`, `modules/`, `rendering/` and `tests/`, 50 kept in place, 0 deleted — plus 23 thin compatibility shims in `scripts/` (and `tests/verify_output.py`) preserving historical import paths, 12 package `__init__.py` files, 25 consolidation report files under `reports/consolidation/`, and a `.gitignore` keeping `__pycache__`/`.pyc` out of the repo. Owner-approved JPG logo at `assets/erudience-owner-approved-logo-2026-11-21.jpg` (JPEG 1536×1536, SHA-256 `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226`, verified from the owner upload — see `reports/source-inventory.md`). This is an architecture consolidation only: no version change (still v4.9.2), no branding change, no published Plugin Creator release.

## Canonical runtime
`skills/erudience/SKILL.md` is the entrypoint. `core/gate_chain_v41.py` implements the 17-stage review gate. `core/chatgpt_bridge_v43.py` and `core/batch_guard_v45.py` support durable handoffs and seven independent 1080×1350 creatives, exactly one promotion. Historical 10-stage and 13-stage controllers remain for compatibility in `core/legacy/`. Historical `scripts/<name>.py` import paths still work via thin compatibility shims.

## Brand
`config/production-policy-v33.json` is authoritative: Sora typography, emerald `#10B77F`, optional authentic original logo only. Historical Inter/DM Sans and `#10B981` values are not current brand authority.

## Operational safety
External integrations remain NOT_CONFIGURED. No automatic publishing, account changes, fabricated sources, fabricated logos, or claims of production readiness. Owner approval is required before delivery/publication.

## Historical version notes (preserved from README-v*.md, deleted in v4.9.2 — see `reports/cleanup-evidence.md`)
v3.4: test locally in this order — `tests/test_strategy_v33.py`, `tests/tests_content_engine.py`, then `python -m unittest tests.integration_tests -v`; known blockers in `references/release-audit-v34.md`. v3.5: six negative-path tests (verified: the six methods in `tests/test_production_gate.py`). v3.7: four tested brand-failure paths (verified: the four methods in `tests/test_brand_render_v37.py`). v3.9: legacy gates remain historical and cannot be used as proof of v3.9 production success; real research/review/AI rendering adapters are not implemented for v3.9. The nine historical README-v*.md stubs (v33–v42, except v38 which never existed) were deleted in v4.9.2 after this preservation was verified; each had zero active references in code, docs, manifests, or CI.

## Testing
GitHub workflow: `.github/workflows/erudience-regression.yml`. Local full regression after consolidation on 2026-11-22 (Python 3.12.3, Pillow 13.0.0, isolated venv): 112 tests passed, 0 failed — 88 in `tests/test_*.py`, 10 in `tests/tests_content_engine.py`, 14 in `tests/integration_tests.py` — plus a 25-check offline end-to-end run (17-stage gate logo-present and logo-absent, 7-content batch, failure recovery, strategy validation, bridge persistence, mechanical PNG gate, shim imports), 25/25 passed. See `reports/consolidation/regression-results.md` and `reports/consolidation/functional-parity.md`.

## Final folder structure
```
erudience-plugin/
  assets/          # owner-approved logo
  agents/          # 18 specialist agent roles (roles-v34.md)
  config/          # central policy: production-policy-v33.json, brand-policy-current.md
  core/            # canonical gate, bridge, batch guard, evidence store, verify_output
  core/legacy/     # historical 10/13-stage controllers (compatibility only)
  modules/         # 14 functional modules (9 with code, 5 documented-only)
  rendering/       # 3 renderers (production + website + draft)
  references/      # canonical + historical reference docs
  reports/         # v4.9.2 audit reports
  reports/consolidation/  # consolidation evidence (11 reports + 7 agent reports)
  scripts/         # thin compatibility shims preserving historical import paths
  skills/          # master skill (SKILL.md entrypoint)
  tests/           # all regression + integration tests
  .agent-plugin/   # platform manifest (visible, not hidden away)
  .claude-plugin/  # platform manifest (visible, not hidden away)
  .codex-plugin/   # platform manifest (visible, not hidden away)
  .app.json        # app manifest
  README.md
  plugin.json
  plugin.yaml
```
Deletion finished locally: 9 historical README stubs deleted (README-v33, v34, v35, v36, v37, v39, v40, v41, v42.md) — their unique information is preserved above. Nothing else was deleted. GitHub `main` still shows them until the branch is pushed.

## Installation
1. Clone the repository and use branch `architecture/erudience-unified-consolidation` (v4.9.2 consolidation; `main` is v4.9.2 since PR #1 was merged).
2. Create an isolated Python environment (Python 3.12 tested) and install the only third-party dependency: `pip install Pillow`.
3. No other packages are required — all other imports are Python standard library. No `requirements.txt` is bundled; Pillow is declared only in `.github/workflows/erudience-regression.yml`.
4. Place fonts as installed paths when rendering (Sora / Inter / DM Sans are not bundled; renderers fail closed without them). The owner-approved logo is already bundled at `assets/erudience-owner-approved-logo-2026-11-21.jpg`.

## Architecture overview
Entrypoint: `skills/erudience/SKILL.md`. Canonical runtime: `core/gate_chain_v41.py` (17-stage gate), `core/chatgpt_bridge_v43.py` (durable handoffs), `core/batch_guard_v45.py` (seven-content batch). Compatibility controllers (`core/legacy/production_controller_v39.py`, `core/legacy/workflow_engine.py`, `core/legacy/autonomous_pipeline_v40.py`) are preserved, not deleted. Brand and rendering: `modules/brand_claims_qa/brand_policy_v36.py`, `rendering/brand_render_v37.py`, `modules/brand_claims_qa/website_brand_v38.py`, `rendering/website_render_v38.py`, `rendering/render_poster.py`. Supporting systems: `modules/linkedin_copywriting/content_engine.py`, `modules/topic_intelligence/keyword_research.py`, `modules/topic_intelligence/linkedin_seo_validator.py`, `core/evidence_store.py`, `modules/competitor_intelligence/competitor_monitor.py`. Canonical policy: `config/production-policy-v33.json` and `config/brand-policy-current.md`. Full analysis: `reports/architecture-audit.md`, `reports/dependency-map.md` and `reports/consolidation/`.

## Workflow
17 stages, in order: SOURCES, SOURCE_REVIEW, RESEARCH, RESEARCH_REVIEW, STRATEGY, STRATEGY_REVIEW, CONTENT, CONTENT_REVIEW, IMAGE_PLAN, PLAN_REVIEW, IMAGE_BUILD, TECH_REVIEW, VISUAL_REVIEW, CONTENT_IMAGE_REVIEW, BRAND_REVIEW, FINAL_REVIEW, DELIVERY. Each stage has its own review gate; failure blocks, repairs, and re-checks — it does not skip ahead. Terminal status is `READY_FOR_OWNER_REVIEW`; owner approval is required before delivery/publication. Batch rule: 7 contents, exactly 1 promotional slot, independent creative briefs, images 1080×1350.

## Configuration
Manifests (all v4.9.2 in this branch): `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`. Hidden configuration and platform-specific manifest directories (`.agent-plugin/`, `.claude-plugin/`, `.codex-plugin/`) are preserved. Brand configuration is in `config/production-policy-v33.json` (Sora, `#10B77F`, logo optional, original logo only). External integrations (OpenAI / Anthropic / Google Search Console) are NOT_CONFIGURED — see `references/endpoint-registry.json`; do not claim them as working until configured and tested.

## Version history
- v4.9.2 consolidation (this branch, not yet merged/published): 38 files moved into `config/`/`core/`/`modules/`/`rendering/`/`tests/`, 50 kept, 0 deleted, 23 compatibility shims added; 112/112 tests passing, 25/25 offline E2E checks passing. No version change, no branding change. See `reports/consolidation/final-verification.md`.
- v4.9.2 (merged to `main` via PR #1, commit `9e320fa`): 9 historical README stubs deleted after preservation, owner-approved logo bundled, `verify_output.py` import-safety fix + 5 new tests, all 6 manifests synced to 4.9.2, 112/112 tests passing, 20/20 offline E2E checks passing.
- v4.9.1 (current release on `main`, release `pluginrel_6b02013bf5b081918f297be6d12ce6db`): preserved until v4.9.2 is verified after publishing.
- v4.6.0: `plugin.yaml` and `.app.json` were stale at this version on `main` (synced to 4.9.2 in this branch).
- Earlier versions v33–v42: historical README notes preserved above under “Historical version notes”; see `reports/cleanup-evidence.md` for the per-file deletion evidence.
