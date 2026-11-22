# Erudience LinkedIn Content & Image Plugin — v4.9.2

## Status
88 files in this repository copy: 80 original text source files (89 on `main`, minus 9 deleted historical README stubs), plus the owner-approved JPG logo at `assets/erudience-owner-approved-logo-2026-11-21.jpg` (JPEG 1536×1536, SHA-256 `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226`, verified from the owner upload — see `reports/source-inventory.md`), plus 6 audit reports under `reports/` and 1 new regression test (`scripts/test_verify_output.py`). This branch (`maintenance/erudience-v4.9.2`) is the v4.9.2 release candidate for PR review; it is not yet merged to `main` and is not a published Plugin Creator release.

## Canonical runtime
`skills/erudience/SKILL.md` is the entrypoint. `scripts/gate_chain_v41.py` implements the 17-stage review gate. `scripts/chatgpt_bridge_v43.py` and `scripts/batch_guard_v45.py` support durable handoffs and seven independent 1080×1350 creatives, exactly one promotion. Historical 10-stage and 13-stage controllers remain for compatibility.

## Brand
`references/production-policy-v33.json` is authoritative: Sora typography, emerald `#10B77F`, optional authentic original logo only. Historical Inter/DM Sans and `#10B981` values are not current brand authority.

## Operational safety
External integrations remain NOT_CONFIGURED. No automatic publishing, account changes, fabricated sources, fabricated logos, or claims of production readiness. Owner approval is required before delivery/publication.

## Historical version notes (preserved from README-v*.md, deleted in v4.9.2 — see `reports/cleanup-evidence.md`)
v3.4: test locally in this order — `scripts/test_strategy_v33.py`, `tests_content_engine.py`, then `python scripts/integration_tests.py -v`; known blockers in `references/release-audit-v34.md`. v3.5: six negative-path tests (verified: the six methods in `scripts/test_production_gate.py`). v3.7: four tested brand-failure paths (verified: the four methods in `scripts/test_brand_render_v37.py`). v3.9: legacy gates remain historical and cannot be used as proof of v3.9 production success; real research/review/AI rendering adapters are not implemented for v3.9. The nine historical README-v*.md stubs (v33–v42, except v38 which never existed) were deleted in v4.9.2 after this preservation was verified; each had zero active references in code, docs, manifests, or CI.

## Testing
GitHub workflow: `.github/workflows/erudience-regression.yml`. Local full regression on 2026-11-22 (Python 3.12.3, Pillow 13.0.0, isolated venv): 107 tests passed, 0 failed — 83 in `scripts/test_*.py`, 10 in `tests_content_engine.py`, 14 in `scripts/integration_tests.py` — plus a 20-check offline end-to-end run (17-stage gate logo-present and logo-absent, 7-content batch, failure recovery, strategy validation, mechanical PNG gate), 20/20 passed. See `reports/regression-results.md`.

## Final folder structure
```
erudience-plugin/
  assets/          # owner-approved logo
  agents/
  references/
  scripts/
  skills/
  reports/
  .agent-plugin/   # platform manifest (visible, not hidden away)
  .claude-plugin/  # platform manifest (visible, not hidden away)
  .codex-plugin/   # platform manifest (visible, not hidden away)
  .app.json        # app manifest
  README.md
  plugin.json
  plugin.yaml
  tests_content_engine.py
```
Deletion finished locally: 9 historical README stubs deleted (README-v33, v34, v35, v36, v37, v39, v40, v41, v42.md) — their unique information is preserved above. Nothing else was deleted. GitHub `main` still shows them until the branch is pushed.

## Installation
1. Clone the repository and use branch `maintenance/erudience-v4.9.2` (v4.9.2 release candidate; `main` is still v4.9.1 until the PR is merged).
2. Create an isolated Python environment (Python 3.12 tested) and install the only third-party dependency: `pip install Pillow`.
3. No other packages are required — all other imports are Python standard library. No `requirements.txt` is bundled; Pillow is declared only in `.github/workflows/erudience-regression.yml`.
4. Place fonts as installed paths when rendering (Sora / Inter / DM Sans are not bundled; renderers fail closed without them). The owner-approved logo is already bundled at `assets/erudience-owner-approved-logo-2026-11-21.jpg`.

## Architecture overview
Entrypoint: `skills/erudience/SKILL.md`. Canonical runtime: `scripts/gate_chain_v41.py` (17-stage gate), `scripts/chatgpt_bridge_v43.py` (durable handoffs), `scripts/batch_guard_v45.py` (seven-content batch). Compatibility controllers (`scripts/production_controller_v39.py`, `scripts/workflow_engine.py`, `scripts/autonomous_pipeline_v40.py`) are preserved, not deleted. Brand and rendering: `scripts/brand_policy_v36.py`, `scripts/brand_render_v37.py`, `scripts/website_brand_v38.py`, `scripts/website_render_v38.py`, `scripts/render_poster.py`. Supporting systems: `scripts/content_engine.py`, `scripts/keyword_research.py`, `scripts/linkedin_seo_validator.py`, `scripts/evidence_store.py`, `scripts/competitor_monitor.py`. Canonical policy: `references/production-policy-v33.json` and `references/brand-policy-current.md`. Full analysis: `reports/architecture-audit.md` and `reports/dependency-map.md`.

## Workflow
17 stages, in order: SOURCES, SOURCE_REVIEW, RESEARCH, RESEARCH_REVIEW, STRATEGY, STRATEGY_REVIEW, CONTENT, CONTENT_REVIEW, IMAGE_PLAN, PLAN_REVIEW, IMAGE_BUILD, TECH_REVIEW, VISUAL_REVIEW, CONTENT_IMAGE_REVIEW, BRAND_REVIEW, FINAL_REVIEW, DELIVERY. Each stage has its own review gate; failure blocks, repairs, and re-checks — it does not skip ahead. Terminal status is `READY_FOR_OWNER_REVIEW`; owner approval is required before delivery/publication. Batch rule: 7 contents, exactly 1 promotional slot, independent creative briefs, images 1080×1350.

## Configuration
Manifests (all v4.9.2 in this branch): `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`. Hidden configuration and platform-specific manifest directories (`.agent-plugin/`, `.claude-plugin/`, `.codex-plugin/`) are preserved. Brand configuration is in `references/production-policy-v33.json` (Sora, `#10B77F`, logo optional, original logo only). External integrations (OpenAI / Anthropic / Google Search Console) are NOT_CONFIGURED — see `references/endpoint-registry.json`; do not claim them as working until configured and tested.

## Version history
- v4.9.2 (this branch, release candidate, not yet merged/published): 9 historical README stubs deleted after preservation, owner-approved logo bundled, `verify_output.py` import-safety fix + 5 new tests, all 6 manifests synced to 4.9.2, 112/112 tests passing, 20/20 offline E2E checks passing.
- v4.9.1 (current release on `main`, release `pluginrel_6b02013bf5b081918f297be6d12ce6db`): preserved until v4.9.2 is verified after publishing.
- v4.6.0: `plugin.yaml` and `.app.json` were stale at this version on `main` (synced to 4.9.2 in this branch).
- Earlier versions v33–v42: historical README notes preserved above under “Historical version notes”; see `reports/cleanup-evidence.md` for the per-file deletion evidence.
