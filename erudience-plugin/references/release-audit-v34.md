# Release audit v3.4

## Confirmed pre-upgrade findings
- `scripts/validate_strategy_v33.py` had 8 policy tests, but tested only a narrow set of boolean fields and did not validate keyword clusters, intent, provenance, external integration or actual rendering.
- `scripts/content_engine.py` verifies selected fields and claim source IDs, but a supplied source URL is not independently fetched; `brand_verified` is a caller-provided flag and is not cryptographic evidence of brand authenticity.
- `scripts/render_poster.py` exists, but real rendering and visual QA have not been verified for the new release.
- Top 50 competitor research target existed as policy, not a populated verified dataset.
- `@Erudience` is a declared skill trigger, not proof that a scheduler, LinkedIn connector or cloud runtime is installed.
- Prior 35-file package contained a compiled `__pycache__` artifact; exclude it from future clean full builds when archive migration is available.

## Changes in v3.4 overlay
Five requested specialist modules plus an explicit local workflow engine, tests, role ownership and dependency documentation. Local tests include negative paths for fabricated metrics, missing provenance, duplicate keywords, unsupported writes and unverified receipts.

## Open deployment blockers
No connected production LinkedIn API adapter, live analytics readback, persistent job queue, real scheduler, authenticated research pipeline, complete 50-competitor dataset, confirmed brand assets, render inspection or live E2E verification. Therefore production readiness is NOT VERIFIED.
