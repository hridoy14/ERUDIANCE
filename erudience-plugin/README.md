# Erudience Plugin — Source Snapshot

This directory contains the v4.9.1 text source snapshot of the Erudience LinkedIn content and image plugin. **89 text files were copied from the plugin source; the approved JPG logo is not yet included.** The plugin's original binary logo must be preserved before treating this as a complete backup.

## Operating contract

The intended workflow is seven independently reviewed 1080×1350 LinkedIn creatives, including exactly one promotion. Original brand assets only; no fabricated logos. Production publication, account changes, or social-media posting require explicit owner authorization. A Python/Pillow runtime is required for local rendering and tests. External integrations are not automatically configured.

## Source organization

- `skills/erudience/SKILL.md`: user-facing skill entrypoint
- `scripts/gate_chain_v41.py`: staged gate controller
- `scripts/chatgpt_bridge_v43.py`, `scripts/batch_guard_v45.py`: orchestration and batch safeguards
- `scripts/test_*.py`, `scripts/integration_tests.py`, `tests_content_engine.py`: regression coverage
- `references/`: strategy, brand, runtime, contracts and history
- `README-v*.md`: historical notes retained until source-equivalence and regression checks pass

## Verification status

The GitHub Actions workflow is at `.github/workflows/erudience-regression.yml`. No successful run has yet been confirmed. A local test against an older v4.9 ZIP returned 7 failures out of 27; that is **not** an authoritative test result for this current source snapshot. Do not delete historical files or publish v4.9.2 before testing this exact checkout and reviewing unique content.

## Safety

This repository is public. Do not commit API keys, personal data, private credentials or unapproved customer assets.
