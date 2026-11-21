# Unified Erudience Plugin v4.2 — Consolidated source of truth

This is a single-plugin merge, not multiple plugin installations. All pre-existing files remain in the same installed plugin. The merge unifies manifests, skill entry point, version policy, and authoritative execution path while retaining old modules for compatibility and auditability.

## Active modules
- Orchestration and all 17 reviewer gates: `scripts/gate_chain_v41.py` ONLY.
- Website brand contract: `references/website-brand-profile-v38.md` and `scripts/website_brand_v38.py`.
- Website-first image renderer: `scripts/website_render_v38.py` (only 3–5 cards; use another validated renderer for six-card content; do not truncate).
- Monthly planning and weekly refresh: `references/monthly-weekly-social-os.md` (owner's 21st start).
- Endpoint declarations: `references/endpoint-registry.json` (status is NOT connected).
- QA tests: `scripts/test_gate_chain_v41.py` plus legacy regression tests.

## Historical, not production approval paths
`workflow_engine.py`, `production_gate.py`, `production_controller_v39.py`, `autonomous_pipeline_v40.py`, `render_poster.py`, `brand_render_v37.py`, `brief_prompt_gate.py`, `verify_output.py` and older reference contracts are retained for regression/traceability, not entrypoints. They contain incompatible assumptions (e.g. mandatory logo, six fixed cards, Sora) and MUST NOT override website-first brand or v4.1 gate order.

## Gate ownership
SOURCES/SOURCE_REVIEW; RESEARCH/RESEARCH_REVIEW; STRATEGY/STRATEGY_REVIEW; CONTENT/CONTENT_REVIEW; IMAGE_PLAN/PLAN_REVIEW; IMAGE_BUILD/TECH_REVIEW/VISUAL_REVIEW/CONTENT_IMAGE_REVIEW/BRAND_REVIEW/FINAL_REVIEW; DELIVERY. Reviewers cannot be their immediate producer. All artifacts bind upstream hash, content-to-plan binds full caption, plan-to-build binds full poster copy ledger, image reviews bind image hash and plan hash.

## Failure paths
CONTENT_REVIEW -> CONTENT; PLAN_REVIEW -> IMAGE_PLAN; TECH_REVIEW or VISUAL_REVIEW or FINAL_REVIEW -> IMAGE_BUILD; CONTENT_IMAGE_REVIEW or BRAND_REVIEW -> IMAGE_PLAN. All dependent receipts invalidated and rerun. Maximum 3 repairs, fourth failure BLOCKED. Missing real adapter BLOCKED immediately.

## Unresolved live dependencies
Research endpoint adapter, LLM planner/writer adapters, verified font assets, real image rendering adapter, independently executed pixel/mobile reviewer, persistent job state/concurrency control, and end-to-end live run remain integration requirements. A manifest merge cannot provide credentials or make an unconnected endpoint operational. Do not misrepresent readiness.

## Prohibited actions
No posting, scheduling, Social OS writes or external mutations without separate owner approval.
