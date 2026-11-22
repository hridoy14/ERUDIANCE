# Target Architecture — Erudience Plugin (DRAFT, UNRESOLVED CONFLICTS OPEN)

- Baseline: `main` merge commit `9e320fa60785f40142f37be9342b3df42fc47968` (v4.9.2, PR #1), repo copy at `~/workspace/erudiance-plugin-work/ERUDIANCE/erudience-plugin/`.
- Method: read-only file inspection only. No exec / git / python / test / install commands were run for this draft.
- Files counted in the plugin tree: **88** (84 visible + 4 hidden: `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`). See `file-migration-map-draft.md` for the full 88-row count.
- Files individually read for this draft: `skills/erudience/SKILL.md`, `references/brand-policy-current.md`, `references/production-policy-v33.json`, `references/gate-contract-v41.md`, `references/runtime-and-compatibility-v49.md`, `references/release-compatibility-v48.md`, `references/brand-assets-manifest.md`, `references/brand-source-of-truth-v36.md`, `references/owner-approved-brand-v46.md`, `references/brand-template-contract-v47.md`, `references/website-brand-profile-v38.md`, `references/master-command-v6.md`, `references/unified-system-v42.md`, `references/orchestrator-v2.md`, `references/execution-state-machine-v39.md`, `references/autonomous-execution-v40.md`, `references/one-command-v44.md`, `references/asset-and-font-policy.md`, `scripts/gate_chain_v41.py`, `scripts/chatgpt_bridge_v43.py`, `scripts/batch_guard_v45.py`, `scripts/production_controller_v39.py`, `scripts/autonomous_pipeline_v40.py`, `scripts/workflow_engine.py`, `scripts/brand_render_v37.py`, `scripts/render_poster.py`, `scripts/website_render_v38.py`, `scripts/brand_policy_v36.py`, `scripts/website_brand_v38.py`, `scripts/content_engine.py`, `scripts/evidence_store.py`, `scripts/production_gate.py`, `scripts/batch_gate.py`, `scripts/brief_prompt_gate.py`, `agents/roles-v34.md`, `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `README.md`, `reports/architecture-audit.md`, `reports/cleanup-evidence.md`, `reports/dependency-map.md`, `tests_content_engine.py`.
- Files NOT individually read (relied on `reports/architecture-audit.md`, `reports/dependency-map.md`, `reports/cleanup-evidence.md`, and filenames): `references/batch-production-v45.md`, `references/brief-schema-example.json`, `references/chat-vision-audit-v35.md`, `references/chatgpt-runtime-v43.md`, `references/content-to-creative-brief-v21.md`, `references/endpoint-registry.json`, `references/gates-and-handoff.md`, `references/integration-registry-v34.json`, `references/master-action-v31.md`, `references/monthly-weekly-social-os.md`, `references/one-action-production-contract.md`, `references/production-contract-v33.md`, `references/production-execution-v35.md`, `references/production-runtime-v37.md`, `references/release-audit-v34.md`, `references/smb-content-strategy-v32.md`, `references/strategy-playbook.md`, `references/system-architecture-v34.md`, `references/workflow-v3.md`, `reports/regression-results.md`, `reports/release-verification.md`, `reports/source-inventory.md`, `scripts/keyword_research.py`, `scripts/competitor_monitor.py`, `scripts/linkedin_analytics.py`, `scripts/linkedin_seo_validator.py`, `scripts/validate_strategy_v33.py`, `scripts/verify_output.py`, `scripts/integration_tests.py`, and all `scripts/test_*.py` files except as summarised in `reports/dependency-map.md`. No claim in this draft depends on an unread file alone; where a mapping is inferred from a filename or a report summary, it is marked as such.
- Status: **DRAFT for owner review. Nothing here is decided by version number alone.** Every policy conflict in `policy-conflicts-draft.md` is UNRESOLVED unless the owner has decided it.

## 0. Design rules applied

1. One master command, one central policy, one master orchestrator, one canonical validation engine. No second live controller.
2. No empty placeholder modules. A `modules/<name>/` directory is created only for a module that already has real code, a real reference spec, or both. Modules with no existing implementation are listed in §5 as **GAP — not created**, not as empty stubs.
3. Preserve plugin packaging and mandatory platform paths. `skills/erudience/SKILL.md` (referenced by `plugin.yaml`), `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` stay exactly where they are. No manifest is moved, renamed, or deleted.
4. Preserve the stable import path `scripts/gate_chain_v41.py` named in `references/runtime-and-compatibility-v49.md`. Any move of the canonical engine is done with a thin re-export shim left at the old path (a new file, not one of the 88), and only after the regression suite passes against the new layout.
5. Legacy controllers are archived, not deleted and not invoked as live paths (per SKILL.md and `reports/architecture-audit.md` §3): they hold unique functionality the canonical chain lacks (v39 atomic persisted state; v40 deterministic validators; `workflow_engine` 7-slot batch rules exercised by integration tests; `evidence_store` the only owner-approval/write-authorisation model).
6. No publishing, scheduling, external writes, or Social OS / LinkedIn writes in any target path. Terminal status stays `READY_FOR_OWNER_REVIEW`; owner approval is a separate, recorded act, not implied by a gate PASS.

## 1. Master command

- **One command: `erudiance_linkdin`** (spelling as written in `skills/erudience/SKILL.md`, `references/one-command-v44.md`, and `.codex-plugin/plugin.json` `defaultPrompt`). Alias `erudience_linkdin` is recorded in `references/one-command-v44.md` only; whether the alias is a supported trigger in the target is UNRESOLVED (see policy-conflicts C20).
- Entry point: `skills/erudience/SKILL.md` (KEEP, unchanged location). It already names the first reads (`references/brand-policy-current.md`, `references/runtime-and-compatibility-v49.md`), the 7-job rule, the `--test --single-content ER-001` single-job form, and the canonical engine.
- Behaviour (as read, not redesigned): 7 independent jobs per weekly batch; exactly 1 dedicated service-promotion slot per full 7-slot week, held (not substituted) if the service/readiness is unverified (`references/production-policy-v33.json` `promotion_policy`); plan content and lock approved caption + poster copy BEFORE generating imagery; no auto-publish.
- Monthly anchor: 21st of the month, timezone `Asia/Dhaka` (`production-policy-v33.json`; `references/one-command-v44.md`). Weekly research refresh rule is as stated in `brand-policy-current.md` (first run of each calendar week, with source URL / verification date / previous value / current value / review status; reuse within the week; mark NOT_CONFIGURED if no scheduler/executor/persistence is configured — never claim research ran).

## 2. Central production policy

- **One central policy file: `config/production-policy-v33.json`** (moved from `references/production-policy-v33.json`; filename and `"version": "3.3.0"` — the *policy* version, not the plugin version — kept verbatim). It is the only machine-readable brand configuration (SKILL.md, `brand-policy-current.md`).
- **One current human-readable policy: `config/brand-policy-current.md`** (moved from `references/brand-policy-current.md`). Together these two files are the target's single source of truth for brand + production rules.
- Owner-approved current policy as stated in those two files (and SKILL.md): **Sora for heading and body; emerald `#10B77F`; logo optional** — if used, only the unchanged original `assets/erudience-owner-approved-logo-2026-11-21.jpg`; never generate, redraw, or replace a logo; footer must contain `Erudience` and `erudience.com`; palette paper `#F6F1E9`, ink `#14120E`, soft `#615B4C`, deep `#0A6E3E`, dark `#0A100E`.
- **This is contested, not settled.** `references/owner-approved-brand-v46.md` (dated 2026-11-21, claiming to override logo-optional for NEW posters), `references/brand-template-contract-v47.md`, `references/website-brand-profile-v38.md`, and `references/master-command-v6.md` (recording an explicit owner choice of website fonts Inter + DM Sans over Sora) state the opposite profile: Inter headings / DM Sans body, emerald `#10B981`, logo required for new branded posters. All of those are UNRESOLVED (policy-conflicts C1–C3, C5, C13). The target adopts the Sora / `#10B77F` / logo-optional profile **only as the stated current policy in `brand-policy-current.md` + `production-policy-v33.json`**, pending an explicit owner decision; it does not delete or rewrite the website-first profile. See §9.
- All active controllers, renderers, and tests must read brand values from the central JSON (per `brand-policy-current.md`). Today only `scripts/gate_chain_v41.py` does so (it reads the JSON at import); `scripts/validate_strategy_v33.py` loads it at import and never uses it (per `reports/architecture-audit.md` §6). In the target, the move to `config/` requires updating those two import-time paths and re-running regression — a planned code change, not a silent file move.
- Historical policy documents stay in `references/` as archival specs, explicitly superseded where the current policy says so. They are not deleted (per `reports/cleanup-evidence.md`: no reference file was deleted in v4.9.2).

## 3. Master orchestrator (1)

One orchestrator, layered — not three competing controllers:

| Layer | Target location | Source today | Role |
|---|---|---|---|
| Canonical validation engine | `core/gate_chain_v41.py` (+ thin re-export shim left at `scripts/gate_chain_v41.py`) | `scripts/gate_chain_v41.py` | The ONE 17-stage fail-closed validator. `STAGES`, `REVIEWS`, `REPAIR`, `GateFailure`, `Adapter`, `Chain.verify()/run()`, `digest()`, `filehash()`. Loads brand from the central JSON at import. No publishing, network calls, or side effects. |
| Durable handoff / checkpoint adapter | `core/chatgpt_bridge_v43.py` (+ shim at `scripts/chatgpt_bridge_v43.py`) | `scripts/chatgpt_bridge_v43.py` | Durable JSON state machine over the same 17 stages (`start/load/next_step/submit/save`, atomic replace). Tools execute outside the process; evidence receipts are submitted back. Reuses `Chain.verify()` — not a competing validator. |
| Batch adapter | `core/batch_guard_v45.py` (+ shim at `scripts/batch_guard_v45.py`) | `scripts/batch_guard_v45.py` | 7 independent jobs, each a bridge state file + batch `manifest.json`. `SLOTS=7`; `initialise()` requires 7 distinct topics; `summary()` requires `READY_FOR_OWNER_REVIEW` + valid individual 1080×1350 PNG + 17 records/job; rejects duplicate IDs and reused image paths; never treats a collage as a deliverable. |

- Legacy orchestrators (archived, not live): `core/legacy/production_controller_v39.py` (13-stage, atomically persisted state — the only persisted controller), `core/legacy/autonomous_pipeline_v40.py` (13-stage, deterministic content/brand validators), `core/legacy/workflow_engine.py` (10-stage, 7-slot batch rules, `EXACTLY_ONE_PROMOTION` + `EMPLOYEE_OVERSIGHT_REQUIRED`), `core/legacy/production_gate.py` (9-stage file-receipt acceptance), `core/legacy/batch_gate.py` (structural batch gate). Each keeps its filename so its test still resolves via the shim/import path; none is invoked as an independent execution path.
- No new versioned controller files in future releases (SKILL.md). The canonical engine is updated in place.
- Known gaps in the canonical engine, recorded in `reports/architecture-audit.md` §2 and carried into the target as open work (not silently fixed here): (a) `RESEARCH` and `STRATEGY` have no stage-specific checks beyond upstream-hash binding; (b) `FINAL_REVIEW` has no check beyond generic image/plan binding and `TECH_REVIEW` does not re-check `image_sha256`; (c) live-mode font verification covers only the heading family — the body font binary is never verified at build time; (d) no owner-approval field/actor/timestamp exists in any stage engine.

## 4. The 14 modules

From `references/production-policy-v33.json` `"modules"` (verbatim order). Each module maps to the real code/spec that exists today; a module with no real implementation is a GAP, not a stub directory.

| # | Module (policy name) | Target home | Real source today | Status |
|---|---|---|---|---|
| 1 | `business_service_intelligence` | **GAP — not created** | `agents/roles-v34.md` role "Business intelligence" (verified portfolio → service map); `references/orchestrator-v2.md` strategy engine step 1. No dedicated script. | No code. Do not invent a stub. |
| 2 | `competitor_intelligence` | `modules/competitor_intelligence/competitor_monitor.py` | `scripts/competitor_monitor.py` (unread individually; integration-tests-only per `reports/dependency-map.md`). Target: 50-record dataset (15 direct / 10 niche / 10 platforms / 10 benchmarks / 5 emerging) per `production-policy-v33.json`. | Exists, thin. |
| 3 | `buyer_intelligence` | **GAP — not created** | `agents/roles-v34.md` role "Buyer research" (persona and pain clusters; hypothesis separated from evidence); `references/orchestrator-v2.md` step 3 (buyer map). No dedicated script. | No code. Do not invent a stub. |
| 4 | `market_trends` | **GAP — not created** | `agents/roles-v34.md` role "Market research" (dated sources → trend brief); `references/strategy-playbook.md` (unread). No dedicated script. | No code. Do not invent a stub. |
| 5 | `topic_intelligence` | `modules/topic_intelligence/` — `keyword_research.py`, `linkedin_seo_validator.py` | `scripts/keyword_research.py` imports `scripts/linkedin_seo_validator.py` (the only non-canonical import edge in `reports/dependency-map.md`). Topic statuses READY / ENRICH / RESEARCH_NEEDED / HOLD; `topic_delete_allowed: false` (policy JSON). | Exists. |
| 6 | `marketing_strategy` | `modules/marketing_strategy/validate_strategy_v33.py` | `scripts/validate_strategy_v33.py` (+ `scripts/test_strategy_v33.py` → `tests/`). Loads the policy JSON at import, value unused (audit §6) — flagged, not fixed here. | Exists. |
| 7 | `funnel_planning` | `modules/funnel_planning/` — funnel logic inside `content_engine.py` (moved as a whole; see #8) | `scripts/content_engine.py` (`funnel_stage` awareness/consideration/decision/retention; `weekly_batch` 7-item rule); `agents/roles-v34.md` "Funnel planner" (TOFU/MOFU/BOFU). No standalone funnel script. | Partial — lives inside content_engine. |
| 8 | `linkedin_copywriting` | `modules/linkedin_copywriting/content_engine.py` | `scripts/content_engine.py` (offline content workflow; 10 differently-named stages RESEARCH/EVIDENCE/CONTENT/CREATIVE_BRIEF/PROMPT/BRAND/RENDER/QA/OWNER_APPROVAL/SOCIAL_OS; `gate()`/`calendar()`/`weekly_batch()`; claim→source binding; case-study permission gate). Test: `tests_content_engine.py` → `tests/`. | Exists. |
| 9 | `creative_brief` | `modules/creative_brief/brief_prompt_gate.py` | `scripts/brief_prompt_gate.py` (brief→prompt structural gate: brief SHA, exact-copy match, 1080×1350, logo SHA required, font-files-verified). Spec: `references/content-to-creative-brief-v21.md` + `references/brief-schema-example.json` (both unread individually; stay in `references/`). | Exists. |
| 10 | `image_generation` | **GAP — not created** | No live image-generation adapter exists in the repo. `references/endpoint-registry.json` (unread individually; per audit: OpenAI/Anthropic/Google Search Console all `DOCUMENTED_PROVIDER_API_NOT_CONNECTED`). `references/gate-contract-v41.md`: "This package contains NO live API endpoints for research/LLM/image generation/visual reviewer." Rendering (deterministic Pillow) is in `rendering/` (§7), not generation. | No code. Do not invent a stub or claim a generator. |
| 11 | `brand_claims_qa` | `modules/brand_claims_qa/` — `brand_policy_v36.py`, `website_brand_v38.py`, `verify_output.py` | `scripts/brand_policy_v36.py` (Sora check + `#10B981` palette + mandatory logo — mixed profile, see C12), `scripts/website_brand_v38.py` (Inter/DM Sans + `#10B981`), `scripts/verify_output.py` (mechanical PNG gate: decode, 1080×1350, ≤5 MB, sibling manifest + SHA256, locked 6-step stage names). | Exists — but internally conflicting (C12). |
| 12 | `approval_distribution` | **GAP as a module — not created**; its only real code is `core/evidence_store.py` | `scripts/evidence_store.py` is the *only* owner-approval + write-authorisation model (`can_handoff()` requires separate `APPROVE` + `WRITE_AUTHORISE` rows; SQLite evidence/receipts/approvals tables). No caller and no test (per `reports/dependency-map.md`). No distribution/sending code exists anywhere; external writes are disabled by policy. | Partial — storage only, unwired. |
| 13 | `analytics_learning` | `modules/analytics_learning/linkedin_analytics.py` | `scripts/linkedin_analytics.py` (unread individually; integration-tests-only per `reports/dependency-map.md`). `agents/roles-v34.md` "Analytics" (descriptive report only; no invented attribution). | Exists, thin. |
| 14 | `knowledge_provenance` | `core/evidence_store.py` (shared infra, also serves #12) | `scripts/evidence_store.py` (deterministic receipt IDs; `evidence()` / `gate()` / `can_handoff()`). Nothing imports it today (per `reports/dependency-map.md`). | Exists, unwired. |

Result: **9 of 14 modules have real code** (2, 5, 6, 7/8, 9, 11, 13, 14, and 12-partial via evidence_store); **4 have no code at all** (1, 3, 4, 10) and are NOT created as directories. Creating them as empty `__init__.py` / stub files would violate the no-placeholder rule and would falsely imply implemented capability.

## 5. The 8 capabilities

From `references/production-policy-v33.json` `"production_capabilities"` (verbatim). Each capability is a behaviour of the orchestrator/modules above, not a separate module.

| Capability | Where it lives in the target | Evidence today |
|---|---|---|
| `freshness_control` | `core/gate_chain_v41.py` (SOURCES provenance) + `config/brand-policy-current.md` weekly-research rule | SOURCES requires URL + `verified_at`; live mode also `source_sha256` and rejects `fixture-only`. Weekly reuse rule in `brand-policy-current.md`. No scheduler exists — research is NOT_CONFIGURED unless an executor is configured. |
| `competitor_monitoring` | `modules/competitor_intelligence/competitor_monitor.py` | `scripts/competitor_monitor.py`; research target 50 competitors (policy JSON). |
| `topic_preservation` | `modules/topic_intelligence/` + policy JSON | `topic_delete_allowed: false`; statuses READY/ENRICH/RESEARCH_NEEDED/HOLD; `agents/roles-v34.md` "no destructive delete". |
| `asset_management` | `assets/` + `references/brand-assets-manifest.md` | Single bundled asset: `assets/erudience-owner-approved-logo-2026-11-21.jpg`, SHA-256 `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226` (per `README.md` / `reports/source-inventory.md`, unread). No other assets are bundled; font binaries are NOT bundled by design. |
| `mobile_readability` | `core/gate_chain_v41.py` VISUAL_REVIEW | Requires `pixel_inspection is True` and `mobile_inspection is True`. Renderers use 64px-class safe margins (see `rendering/`). |
| `experimentation` | **Weakest capability — no dedicated code found.** `references/orchestrator-v2.md` §4 mentions "experiment hypothesis" in the 30-day plan schema; `agents/roles-v34.md` has no experimentation role. | Recorded as a gap, not a module. |
| `feedback_loop` | `modules/analytics_learning/linkedin_analytics.py` + owner review (see §8) | Analytics script exists (thin, integration-tests-only). No closed-loop code that feeds results back into topic/strategy was found. |
| `audit_trail` | `core/gate_chain_v41.py` trace/records + `core/chatgpt_bridge_v43.py` state + `core/evidence_store.py` receipts | Every stage records artifact + SHA256 + adapter; trace records PASS/FAIL, reason, return-to, revision. Bridge state is a JSON file (temp + `os.replace`, no fsync/locking per audit §2); v39 controller has atomic save with fsync. No timestamps are recorded in the chain (audit §2). |

## 6. Research + strategy

- **Research:** SOURCES → SOURCE_REVIEW → RESEARCH → RESEARCH_REVIEW (stages 1–4 of the 17). Each observation requires source URL, verification date, previous value, current value, and review status (`brand-policy-current.md`). Competitor target 50 (15/10/10/10/5 split). First-run-of-week rule; reuse within the week. If no scheduler, research executor, or persistence is configured, mark NOT_CONFIGURED — never claim research ran (SKILL.md). No live research endpoint exists (`gate-contract-v41.md`); adapters must be registered by the operator.
- **Strategy:** STRATEGY → STRATEGY_REVIEW (stages 5–6). 7-slot weekly plan; exactly 1 promotion slot; funnel allocation TOFU/MOFU/BOFU (`agents/roles-v34.md`); topic statuses and no-delete rule (§4 #5). `validate_strategy_v33.py` is the only strategy-validation code; its policy-JSON load is unused (audit §6).
- Gap: the canonical chain has no stage-specific checks for RESEARCH or STRATEGY beyond upstream-hash binding (audit §2 gap 1), while `autonomous_pipeline_v40.py` does require research evidence + source SHA256 and strategy/research hash binding. Whether to port those checks into the canonical engine is an owner decision, not made here.

## 7. Content + promotion, creative brief + rendering

- **Content + promotion:** CONTENT → CONTENT_REVIEW (stages 7–8). CONTENT locks `content_id`, `topic`, `caption`, `keywords` (gate chain). Caption rules (hashtags `#AIAutomation` / `#WorkflowAutomation` / `#VoiceAI`, 2–3; banned words revolutionise, unlock, leverage, seamless, cutting-edge, game-changing, supercharge) live in `brand_policy_v36.py` / `website_brand_v38.py` — both hard-code the website-first palette, so caption checks and brand checks are currently entangled with the unresolved font/palette conflict (C12). Promotion: exactly 1 slot/week; HOLD, never invent (policy JSON). `workflow_engine.py` additionally requires `employee_requirement` on the promo item and forbids deleted/unsupported-claim items — a rule present in no other controller (see C16).
- **Creative brief:** IMAGE_PLAN → PLAN_REVIEW (stages 9–10). IMAGE_PLAN must bind to the locked CONTENT hash and exact caption; must carry `poster_text` (headline + footer), dimensions `[1080, 1350]`, `brand == BRAND` (central JSON), `design_rationale`, `negative_constraints`, `template_id`, `positioning`, `funnel_stage`; `logo_asset` ∈ {None, approved logo path}. `brief_prompt_gate.py` is the structural brief→prompt gate (see §4 #9).
- **Rendering (1 canonical renderer to be chosen; 3 exist today — UNRESOLVED, C9):**

| Renderer | Target | Fonts / palette / logo as coded | Notes |
|---|---|---|---|
| `brand_render_v37.py` | `rendering/brand_render_v37.py` | Sora (regular+bold files required); palette emerald `#10B981`; logo **mandatory** (verified asset); pins `brand_policy == 'social-os/BRAND.md:v1.1'` (no such file in repo — audit §4) | 3–5 steps; headline ≤12 words. |
| `website_render_v38.py` | `rendering/website_render_v38.py` | Inter heading / DM Sans body (files + SHA256 required); palette `#10B981`; logo **optional** (wordmark `Erudience` text if absent) | 3–5 steps only; per `unified-system-v42.md`, use another validated renderer for six-card content, do not truncate. |
| `render_poster.py` | `rendering/render_poster.py` | Inter/DM Sans (4 font files, CLI-required); palette `#10B981`; logo **required** for final (unless `--review-draft`, which labels the output `REVIEW DRAFT — LOGO NOT VERIFIED`) | Fixed 6-step template; exactly 2 headline lines + 6 cards; its manifest format is what `verify_output.py` expects. |

  All three render one standalone PNG 1080×1350 per content ID, no collages, exact approved poster text rendered deterministically after illustration generation (SKILL.md). The target has ONE rendering directory but does NOT pick a winner: picking Sora vs Inter/DM Sans, `#10B77F` vs `#10B981`, and logo-optional vs logo-required is the owner decision in C1–C3/C9. Until then all three renderers are preserved, each labelled with the profile it implements, and none is called "canonical" for brand.
- Font binaries are NOT bundled in any target layout (per `references/orchestrator-v2.md` step 7 and `asset-and-font-policy.md`: do not redistribute fonts in the plugin archive). Renderers fail closed without verified local font files.

## 8. Canonical validation engine — 17 stages + mapped 13-stage rules

- **Canonical: 17 stages** in `core/gate_chain_v41.py` (from `scripts/gate_chain_v41.py:11`, restated in `references/gate-contract-v41.md` and SKILL.md):
  `SOURCES → SOURCE_REVIEW → RESEARCH → RESEARCH_REVIEW → STRATEGY → STRATEGY_REVIEW → CONTENT → CONTENT_REVIEW → IMAGE_PLAN → PLAN_REVIEW → IMAGE_BUILD → TECH_REVIEW → VISUAL_REVIEW → CONTENT_IMAGE_REVIEW → BRAND_REVIEW → FINAL_REVIEW → DELIVERY`
  8 of the 17 are `*_REVIEW` stages. Reviewers must be a registered reviewer adapter distinct from the producer (`SELF_REVIEW_FORBIDDEN`), provide observations + decision `PASS` + exact `subject_hash`; live mode additionally requires a real inspection-evidence file with verified SHA256. Every output binds to its immediate previous stage via `upstream_hash`. IMAGE_PLAN binds to locked CONTENT hash + exact caption; IMAGE_BUILD binds to IMAGE_PLAN hash + copy ledger; image QA binds to actual image hash + plan hash.
- **Mapped 13-stage rules (legacy, for traceability only — no live mapping is executed):**

| 17-stage (canonical) | 13-stage v39 / v40 (legacy) | Mapping note |
|---|---|---|
| SOURCES | SOURCES | Same name; v39/v40 require `source_verified` / `verified_sources`; v41 requires URL + `verified_at` (+ live `source_sha256`). |
| SOURCE_REVIEW | — (no separate stage) | **No counterpart.** v39/v40 fold source review into SOURCES/RESEARCH. |
| RESEARCH | RESEARCH | v40 requires `evidence` + `source_sha256 == SOURCES hash`; v41 has no stage-specific RESEARCH check (gap, §3). |
| RESEARCH_REVIEW | — (no separate stage) | **No counterpart.** |
| STRATEGY | STRATEGY | v40 requires topic + `research_sha256` binding; v41 has no stage-specific STRATEGY check (gap, §3). |
| STRATEGY_REVIEW | — (no separate stage) | **No counterpart.** |
| CONTENT | CONTENT | Both lock topic + caption; v41 also requires `content_id` + `keywords`. |
| CONTENT_REVIEW | CONTENT_QA | v39/v40: independent reviewer, decision PASS + observations; failure → CONTENT. v41: same, failure → CONTENT. |
| IMAGE_PLAN | BRIEF | v39/v40 BRIEF binds to content hash, requires `poster_text` + `brand_profile_version` (v39) / `brand_profile == 'website-v38'` + Inter/DM Sans + `#10B981` (v40). v41 IMAGE_PLAN binds to content hash + exact caption, requires `brand == BRAND` (central JSON: Sora / `#10B77F`). **Brand payload differs — C1/C2.** |
| PLAN_REVIEW | BRIEF_QA | v39/v40 failure → BRIEF; v41 failure → IMAGE_PLAN. |
| IMAGE_BUILD | RENDER | v39/v40 RENDER binds to brief hash + real image bytes; v41 IMAGE_BUILD binds to plan hash + copy-ledger hash + font provenance + logo provenance iff planned. |
| TECH_REVIEW | TECH_QA | Both re-open the PNG (1080×1350, PNG, RGB/RGBA). v41 TECH_REVIEW does not re-check `image_sha256` (gap, §3). Failure → IMAGE_BUILD / RENDER. |
| VISUAL_REVIEW | VISUAL_QA | v41 requires pixel + mobile inspection; v40 requires a real registered adapter opening the poster at full and mobile sizes. Failure → IMAGE_BUILD / RENDER. |
| CONTENT_IMAGE_REVIEW | CONTENT_MATCH_QA | v41 requires topic + text match; v40 deterministic matcher requires topic + copy-ledger verified. Failure: v41 → IMAGE_PLAN; v39/v40 → BRIEF. **Repair target differs — C8.** |
| BRAND_REVIEW | BRAND_QA | v41 checks fonts/palette/footer/logo-or-absence/positioning against central JSON; v40 checks Inter/DM Sans + `#10B981` + `website_brand_verified`. Failure: v41 → IMAGE_PLAN; v39/v40 → BRIEF. **Repair target differs — C8.** |
| FINAL_REVIEW | — (no separate stage) | **No counterpart.** v41 has no check beyond generic image/plan binding (gap, §3). |
| DELIVERY | DELIVERY | Both require all prior stages + image SHA256 match. Terminal status `READY_FOR_OWNER_REVIEW` in both. |

  The 10-stage `workflow_engine` (RESEARCH/KEYWORDS/STRATEGY/DRAFT/FACT_QA/SEO_QA/CREATIVE/VISUAL_QA/OWNER_APPROVAL/DELIVERY) and 9-stage `production_gate` (RESEARCH/KEYWORDS/STRATEGY/DRAFT/FACT_QA/SEO_QA/BRAND_QA/CREATIVE/VISUAL_QA) and 10-stage `content_engine` (different names again) have **no mapping** in the repo today (audit §3 contradiction 1). No mapping for them is invented here; they are archived as legacy and their stage names are recorded in the migration map, not merged.
- Failure / retry / recovery: max 3 repairs; 4th failure → BLOCKED; missing adapter → BLOCKED immediately; every rollback invalidates downstream records (gate chain `REPAIR` map: SOURCE_REVIEW→SOURCES, RESEARCH_REVIEW→RESEARCH, STRATEGY_REVIEW→STRATEGY, CONTENT_REVIEW→CONTENT, PLAN_REVIEW→IMAGE_PLAN, TECH/VISUAL/FINAL_REVIEW→IMAGE_BUILD, CONTENT_IMAGE/BRAND_REVIEW→IMAGE_PLAN). `submit()` is fail-safe, not idempotent (replay of a passed stage raises `OUT_OF_ORDER_STAGE`); `start()`/`initialise()` refuse existing state (`JOB_ALREADY_EXISTS` / `BATCH_ALREADY_EXISTS`).

## 9. SHA256 binding / receipts / independent QA / retry / recovery

- **SHA256 binding:** `digest()` (canonical JSON, sorted keys) for every artifact; `filehash()` for files. Chain: job → SOURCES → … → DELIVERY via `upstream_hash`; content → plan via `content_hash`; plan → build via `plan_hash` + `copy_ledger_hash` (`digest(poster_text)`); build → reviews via `image_sha256` + `plan_hash`; delivery re-verifies `image_sha256` + all 16 prior stages. Logo, when planned, is bound by `logo_sha256 == filehash(approved logo)`; when absent, build must carry no `logo_asset`/`logo_sha256` (`UNPLANNED_LOGO_FORBIDDEN`).
- **Receipts:** per-stage records `{artifact, hash, adapter}` + trace `{stage, event, sha256/reason, return_to, revision}` in the chain; durable JSON state files in the bridge (atomic replace); batch `manifest.json` in the batch guard; SQLite receipts in `evidence_store` (`receipts` table: input/output hash, upstream JSON, verdict PASS/REJECT/NOT_VERIFIED). No timestamps are recorded in the chain (audit §2).
- **Independent QA:** reviewer ≠ producer, reviewer-role adapter, `decision == PASS`, non-empty `observations`, exact `subject_hash`; live mode requires a real inspection-evidence file with matching SHA256. A reviewer PASS without real independent inspection is prohibited (v39 doc; v40 doc: passing a `reviewer_id` string alone is not proof of independence). SHA256 evidence authenticates a file, not a reviewer or semantic quality (`gate-contract-v41.md`).
- **Retry / recovery:** §8 repair map; max 3 repairs; BLOCKED on exhaustion or missing adapter; downstream invalidation on every rollback; no gate bypass by manual "force pass" (`orchestrator-v2.md` step 11).
- **Owner review:** terminal status is `READY_FOR_OWNER_REVIEW` — ready *for*, not approved *by*, the owner. No stage engine records an owner approval (audit §2). The only approval model is `evidence_store.can_handoff()` (separate `APPROVE` + `WRITE_AUTHORISE` rows for the same `content_hash`), currently unwired. `workflow_engine`/`content_engine` name an `OWNER_APPROVAL` stage but never enforce it (audit §2 gap 4). Owner approval recording is therefore a target gap, not a solved component.

## 10. Seven independent jobs, batch verification + owner review

- `core/batch_guard_v45.py`: 7 distinct topics → 7 jobs (`ER-<cycle>-001` … `ER-<cycle>-007`), each an independent bridge state file; one manifest. `summary()` marks a job READY only if status is `READY_FOR_OWNER_REVIEW` AND its PNG is a real 1080×1350 file AND it has 17 records; batch status is READY only if all 7 are ready; duplicate content IDs and reused image paths are rejected.
- Owner review is the batch gate: no job and no batch is approved by the system. Publishing/scheduling/external writes remain disabled (`external_writes: 0` everywhere; `workflow_engine` returns `BLOCKED / NO_VERIFIED_WRITE_ADAPTER` even with approval).

## 11. Evidence / provenance / analytics / feedback

- **Evidence:** `core/evidence_store.py` (SQLite: `evidence`, `receipts`, `approvals` tables; deterministic receipt IDs). It is the only evidence ledger; nothing imports it today — wiring it to the bridge is target work, not assumed done.
- **Provenance:** source URL + `verified_at` + `source_sha256` (live); font provenance (path + SHA256, heading family only in live mode — body gap, §3); logo provenance (approved path + SHA256); copy ledger hash; image SHA256. `verify_output.py` (→ `core/verify_output.py`) is the mechanical output gate (PNG decode, 1080×1350, ≤5 MB, sibling manifest + SHA256, locked 6-step stage names — note: it expects `render_poster.py`'s 6-step manifest format, which is renderer-specific).
- **Analytics:** `modules/analytics_learning/linkedin_analytics.py` (descriptive only; no invented attribution per `agents/roles-v34.md`). No live LinkedIn metrics connection exists; integrations are NOT_CONFIGURED.
- **Feedback:** no closed feedback-loop code was found (see §5 `feedback_loop`). The target records this as a gap: analytics output has no defined path back into topic/strategy. Do not claim a loop exists.

## 12. Physical layout (target)

Folders that **already exist** in the plugin tree: `skills/`, `references/`, `scripts/`, `agents/`, `assets/`, `reports/` — plus mandatory hidden platform dirs `.agent-plugin/`, `.claude-plugin/`, `.codex-plugin/` (kept, untouched).
Folders that are **new**: `config/`, `core/`, `modules/`, `rendering/`, `tests/`.
Folders that are **NOT created** (no placeholder): per-module directories for modules 1, 3, 4, 10 (§4); no `social-os/` directory (referenced by `brand_render_v37.py`'s `social-os/BRAND.md:v1.1` pin, which names a file that does not exist in this repo — C18).

```
erudience-plugin/
  README.md                         # KEEP (root)
  plugin.json  plugin.yaml  .app.json   # KEEP — mandatory manifests, root
  .agent-plugin/plugin.json         # KEEP — mandatory platform manifest
  .claude-plugin/plugin.json        # KEEP — mandatory platform manifest
  .codex-plugin/plugin.json         # KEEP — mandatory platform manifest
  skills/erudience/SKILL.md       # KEEP — entry point; plugin.yaml points here
  config/
    production-policy-v33.json      # NEW folder; moved from references/ (canonical policy)
    brand-policy-current.md         # NEW folder; moved from references/ (current policy)
  core/
    gate_chain_v41.py               # NEW folder; moved from scripts/ (canonical engine)
    chatgpt_bridge_v43.py           # NEW folder; moved from scripts/
    batch_guard_v45.py              # NEW folder; moved from scripts/
    evidence_store.py               # NEW folder; moved from scripts/
    verify_output.py                # NEW folder; moved from scripts/
    legacy/
      production_controller_v39.py  # moved from scripts/ (archived)
      autonomous_pipeline_v40.py    # moved from scripts/ (archived)
      workflow_engine.py            # moved from scripts/ (archived)
      production_gate.py            # moved from scripts/ (archived)
      batch_gate.py                 # moved from scripts/ (archived)
  modules/
    competitor_intelligence/competitor_monitor.py
    topic_intelligence/keyword_research.py
    topic_intelligence/linkedin_seo_validator.py
    marketing_strategy/validate_strategy_v33.py
    linkedin_copywriting/content_engine.py
    creative_brief/brief_prompt_gate.py
    brand_claims_qa/brand_policy_v36.py
    brand_claims_qa/website_brand_v38.py
    analytics_learning/linkedin_analytics.py
    # (no directories for business_service_intelligence, buyer_intelligence,
    #  market_trends, image_generation, approval_distribution — GAP, §4)
  rendering/
    brand_render_v37.py             # moved from scripts/
    website_render_v38.py           # moved from scripts/
    render_poster.py                # moved from scripts/
  references/                       # KEEP — all remaining 34 reference files stay here as archival specs
  agents/roles-v34.md               # KEEP
  assets/erudience-owner-approved-logo-2026-11-21.jpg   # KEEP — never move/replace
  tests/                            # NEW folder; all test files moved here (see migration map)
    test_*.py  integration_tests.py  tests_content_engine.py
  scripts/                          # KEEP as a folder, but only for thin re-export shims
                                    # (new files, not part of the 88) preserving the old
                                    # import paths: gate_chain_v41, chatgpt_bridge_v43,
                                    # batch_guard_v45 (+ legacy shims as needed by tests/CI)
  reports/                          # KEEP — all 6 reports stay here
```

- **Import-path consequences (must be done as code changes, not by moving files alone):** `gate_chain_v41.py` reads `references/production-policy-v33.json` via `Path(__file__).parent.parent / 'references' / ...` at import, and `validate_strategy_v33.py` does the same; both paths must be updated to `config/` and the full regression suite re-run (CI: `.github/workflows/erudience-regression.yml`, repo root — outside the plugin tree, not counted in the 88, not moved). `scripts/` has no `__init__.py` today; cross-module imports resolve only when run from `scripts/` or with `sys.path` insertion (audit §6) — the target layout must solve this explicitly (package vs. path insertion) before any move is executed; this draft does not choose the mechanism.
- **What is NOT in the target:** no `requirements.txt` / `pyproject.toml` was found in the plugin (Pillow is declared only in CI); none is invented here. No font binaries are bundled. No live API endpoints, credentials, scheduler, or persistence are provisioned by a file move (per `runtime-and-compatibility-v49.md`: a ZIP update does not provision them).

## 13. Open decisions for the owner (summary — see policy-conflicts-draft.md)

1. Brand profile: Sora / `#10B77F` / logo-optional (current policy files) vs Inter+DM Sans / `#10B981` / logo-required-for-new-posters (v46/v47/v38/master-command-v6). (C1–C3, C5, C13)
2. Canonical renderer: `brand_render_v37` vs `website_render_v38` vs `render_poster` (3-step vs 6-step templates). (C9, C19)
3. Canonical controller claim: v41 vs v39 vs v40. (C6)
4. Whether to port v40's RESEARCH/STRATEGY checks and v39's atomic persisted state into the canonical engine, and how owner approval is recorded. (C14, §3 gaps)
5. Whether the `erudience_linkdin` alias is supported. (C20)
6. Whether the 10-stage / 9-stage / content-engine stage sets get a mapping at all, or stay archived unmapped. (C7)
