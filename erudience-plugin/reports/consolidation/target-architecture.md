# Erudience Plugin — Target Architecture (Consolidation)

- Baseline: `main` `9e320fa6` (v4.9.2). Status: **PLAN — not executed**. No file was moved in this task (see `source-baseline.md` for the execution block). Full draft: `~/workspace/erudiance-plugin-work/consolidation-staging/target-architecture-draft.md`.
- Design rules: one master command, one central policy, one master orchestrator, one canonical validation engine, no second live controller, no empty placeholder modules, preserve plugin packaging and mandatory platform paths, no publishing/scheduling/external writes, terminal status stays `READY_FOR_OWNER_REVIEW`.

## 1. One master command
`erudiance_linkdin` (spelling as in SKILL.md, `one-command-v44.md`, `.codex-plugin/plugin.json` `defaultPrompt`). Entry: `skills/erudience/SKILL.md` (KEEP). 7 independent jobs per weekly batch; exactly 1 promotion, HOLD if unverified; lock caption + poster copy before imagery. Alias `erudience_linkdin` is UNRESOLVED (policy-conflicts C20). Monthly anchor: 21st, timezone Asia/Dhaka.

## 2. Central production policy
`config/production-policy-v33.json` (moved from `references/`, filename and policy version 3.3.0 kept verbatim) + `config/brand-policy-current.md` (moved from `references/`). Together the single source of truth. Stated current policy: **Sora heading+body, emerald `#10B77F`, logo optional** (original logo only, never generated/redrawn/replaced), footer Erudience + erudience.com, palette paper #F6F1E9 / ink #14120E / soft #615B4C / deep #0A6E3E / dark #0A100E. This is **contested** (C1–C3, C5, C13) and is adopted here only as the stated current policy, pending an explicit owner decision; the website-first profile is preserved, not deleted or rewritten. Only `gate_chain_v41` reads the JSON today; `validate_strategy_v33` loads it and never uses it — the move requires updating both import-time paths and re-running regression.

## 3. One master orchestrator (layered, not three controllers)
| Layer | Target | Source today |
|---|---|---|
| Canonical validation engine | `core/gate_chain_v41.py` (+ thin re-export shim at `scripts/gate_chain_v41.py`) | `scripts/gate_chain_v41.py` |
| Durable handoff / checkpoint adapter | `core/chatgpt_bridge_v43.py` (+ shim) | `scripts/chatgpt_bridge_v43.py` |
| Batch adapter | `core/batch_guard_v45.py` (+ shim) | `scripts/batch_guard_v45.py` |
Legacy (archived in `core/legacy/`, never invoked as live paths): `production_controller_v39.py` (only atomically persisted controller), `autonomous_pipeline_v40.py` (only deterministic content/brand validators), `workflow_engine.py` (only 7-slot batch rules with employee-oversight), `production_gate.py`, `batch_gate.py`. No new versioned controller files in future releases (SKILL.md).

## 4. The 14 modules
9 of 14 have real code; 4 have none and are **NOT created** as directories (no empty placeholders):
- `business_service_intelligence` — GAP, no code.
- `competitor_intelligence` — `modules/competitor_intelligence/competitor_monitor.py` (thin, 50-target).
- `buyer_intelligence` — GAP, no code.
- `market_trends` — GAP, no code.
- `topic_intelligence` — `modules/topic_intelligence/keyword_research.py` + `linkedin_seo_validator.py`.
- `marketing_strategy` — `modules/marketing_strategy/validate_strategy_v33.py`.
- `funnel_planning` — funnel logic inside `content_engine.py` (partial).
- `linkedin_copywriting` — `modules/linkedin_copywriting/content_engine.py`.
- `creative_brief` — `modules/creative_brief/brief_prompt_gate.py`.
- `image_generation` — GAP, no code; no live generator exists. Rendering is in `rendering/`, not generation.
- `brand_claims_qa` — `modules/brand_claims_qa/brand_policy_v36.py` + `website_brand_v38.py` + `verify_output.py` (internally conflicting, C12 — moved as-is).
- `approval_distribution` — GAP as a module; only real code is `core/evidence_store.py` (unwired).
- `analytics_learning` — `modules/analytics_learning/linkedin_analytics.py` (thin).
- `knowledge_provenance` — `core/evidence_store.py` (shared infra, unwired).

## 5. The 8 capabilities
Freshness (SOURCES provenance + weekly rule; no scheduler — NOT_CONFIGURED), competitor monitoring (50-target), topic preservation (`topic_delete_allowed: false`), asset management (`assets/` + manifest), mobile readability (VISUAL_REVIEW pixel+mobile inspection), experimentation (**weakest — no code found, gap**), feedback loop (analytics only, no closed loop — gap), audit trail (chain trace + bridge state + evidence_store receipts; no timestamps in the chain).

## 6. Research + strategy
SOURCES → SOURCE_REVIEW → RESEARCH → RESEARCH_REVIEW → STRATEGY → STRATEGY_REVIEW. Weekly research with source URL / verification date / previous / current / review status; reuse within the week; mark NOT_CONFIGURED if unconfigured. Gap: RESEARCH and STRATEGY have no stage-specific checks in the canonical chain beyond hash binding (v40 has them — porting is an owner decision).

## 7. Content + promotion, creative brief + rendering
CONTENT → CONTENT_REVIEW (lock content_id, topic, caption, keywords). IMAGE_PLAN → PLAN_REVIEW (bind to CONTENT hash + exact caption, poster_text headline+footer, [1080,1350], brand == BRAND, template/positioning/funnel, logo ∈ {None, approved}). Rendering: **one directory, three preserved renderers, no winner chosen** (C9): `brand_render_v37` (Sora, `#10B981`, logo mandatory, 3–5 steps), `website_render_v38` (Inter/DM Sans, `#10B981`, logo optional, 3–5 steps), `render_poster` (Inter/DM Sans, `#10B981`, logo required unless review-draft, exactly 6 steps). Choosing one requires deciding C1–C3 first. Font binaries are never bundled; renderers fail closed without them.

## 8. Canonical validation engine — 17 stages + mapped 13-stage rules
17 stages (see `dependency-map.md`). 17↔13 mapping (traceability only): SOURCES→SOURCES, RESEARCH→RESEARCH, STRATEGY→STRATEGY, CONTENT→CONTENT, CONTENT_REVIEW→CONTENT_QA, IMAGE_PLAN→BRIEF (brand payload differs — C1/C2), PLAN_REVIEW→BRIEF_QA, IMAGE_BUILD→RENDER, TECH_REVIEW→TECH_QA, VISUAL_REVIEW→VISUAL_QA, CONTENT_IMAGE_REVIEW→CONTENT_MATCH_QA (repair target differs — C8), BRAND_REVIEW→BRAND_QA (repair target differs — C8), DELIVERY→DELIVERY. No counterparts for SOURCE_REVIEW, RESEARCH_REVIEW, STRATEGY_REVIEW, FINAL_REVIEW. The 10/9/content-engine stage sets have **no mapping** and none was invented.
Failure/retry: max 3 repairs, BLOCKED on 4th, missing adapter → BLOCKED immediately, downstream records invalidated on every rollback, `submit()` fail-safe not idempotent, `start()`/`initialise()` refuse existing state.

## 9. SHA256 binding / receipts / independent QA / retry / recovery
`digest()` (canonical JSON) + `filehash()` (file bytes); upstream_hash chain; content→plan, plan→build (copy_ledger_hash), build→reviews (image_sha256 + plan_hash), delivery re-verifies all 16 prior stages. Logo bound by SHA256 when planned, forbidden when unplanned. Reviewer ≠ producer, decision PASS, non-empty observations, exact subject_hash; live mode requires a real inspection-evidence file with matching SHA256. Owner review: terminal status is `READY_FOR_OWNER_REVIEW` — ready *for*, not approved *by*, the owner. No engine records an owner approval; the only model (`evidence_store.can_handoff()`, separate APPROVE + WRITE_AUTHORISE rows) is unwired — a target gap.

## 10. Seven independent jobs, batch verification + owner review
`batch_guard_v45`: 7 distinct topics → 7 jobs (`ER-<cycle>-001`…`007`), each a bridge state file + manifest. `summary()` READY only if all 7 are READY + valid individual 1080×1350 PNG + 17 records each; duplicate IDs and reused image paths rejected. No publishing/scheduling/external writes (`external_writes: 0`).

## 11. Evidence / provenance / analytics / feedback
Evidence: `core/evidence_store.py` (SQLite, unwired — wiring is target work, not assumed done). Provenance: source URL + verified_at + source_sha256, font provenance (heading only — body gap), logo provenance, copy ledger, image SHA256. Analytics: descriptive only, no invented attribution, no live connection. Feedback: **no closed loop found — gap**.

## 12. Physical layout (target)
Existing folders kept: `skills/`, `references/`, `scripts/` (shims only), `agents/`, `assets/`, `reports/`, hidden platform dirs. New folders: `config/`, `core/`, `core/legacy/`, `modules/`, `rendering/`, `tests/`. Not created: per-module dirs for modules 1, 3, 4, 10; no `social-os/` dir (the pinned file does not exist). Import-path prerequisites: policy-JSON paths in `gate_chain_v41` / `validate_strategy_v33` must move `references/` → `config/`; `website_render` → `website_brand` becomes a cross-directory import; `tests/` import resolution (no `__init__.py` today) must be defined before any move; CI (`.github/workflows/erudience-regression.yml`, repo root) must be updated to the new `tests/` locations. No `requirements.txt` / `pyproject.toml` is invented; no font binaries bundled; no live endpoints, credentials, scheduler, or persistence provisioned by a file move.

## 13. Open decisions for the owner
1. Brand profile (C1–C3, C5, C13). 2. Canonical renderer (C9, C19). 3. Canonical controller claim (C6). 4. Port v40 RESEARCH/STRATEGY checks + v39 atomic state into the canonical engine; how owner approval is recorded (C14). 5. Alias `erudience_linkdin` supported? (C20). 6. Map or archive the 10/9/content-engine stage sets (C7).

## Post-consolidation update (2026-11-22)
- Target architecture executed as planned: 38 moves, 50 keeps, 0 deletes. No competing controller was created; `core/gate_chain_v41.py` remains the single canonical validation engine; legacy controllers live in `core/legacy/` only.
- All 3 renderers preserved in `rendering/`; none declared canonical by deleting the others.
- 14 modules: 9 have code, 4 have none (business, buyer, market, image generation as a live adapter) — no empty folders were created for them.
