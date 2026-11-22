# File Migration Map — Erudience Plugin (DRAFT)

- Baseline: `main` merge commit `9e320fa60785f40142f37be9342b3df42fc47968` (v4.9.2, PR #1), repo copy at `~/workspace/erudiance-plugin-work/ERUDIANCE/erudience-plugin/`.
- Method: read-only file inspection only. No exec / git / python / test / install commands were run.
- **Total files counted: 88.** Count verified by directory listing: root 8 (4 visible + 1 hidden `.app.json` + 3 hidden platform manifests) + `agents/` 1 + `assets/` 1 + `references/` 36 + `reports/` 6 + `scripts/` 35 + `skills/erudience/` 1 = **88**. This matches `README.md` ("88 files in this repository copy").
- **Moves: 38. KEEPs: 50.** All moves are out of `scripts/` (33 files), `references/` (2 files), and the plugin root (1 test file, `tests_content_engine.py`); every other file KEEPs its current path. (An earlier draft of this header said 35/53; the recount in the Totals section supersedes it — see there for the arithmetic.)
- New folders in the target: `config/`, `core/`, `core/legacy/`, `modules/<name>/`, `rendering/`, `tests/`. Existing folders: `skills/`, `references/`, `scripts/`, `agents/`, `assets/`, `reports/`, `.agent-plugin/`, `.claude-plugin/`, `.codex-plugin/`.
- `scripts/` is KEPT as a folder but holds only thin re-export shims in the target (new files, not part of the 88) preserving old import paths — see notes after the table. No original file is deleted in this map; legacy files are moved to `core/legacy/`, not deleted.
- Files individually read for this draft are listed in `target-architecture-draft.md` §0. Files NOT individually read (filename / report-summary basis only) are marked `*` in the table below: all `references/` files except the ones listed in the architecture draft, all `scripts/test_*.py` files, `scripts/integration_tests.py`, `scripts/keyword_research.py`, `scripts/competitor_monitor.py`, `scripts/linkedin_analytics.py`, `scripts/linkedin_seo_validator.py`, `scripts/validate_strategy_v33.py`, `scripts/verify_output.py`, and `reports/regression-results.md`, `reports/release-verification.md`, `reports/source-inventory.md`. Their proposed paths follow the same rule as the read files (by role, not by content guess) and are marked accordingly.
- "Reason" uses these codes: PACKAGING = mandatory plugin/platform path, must not move; ENTRY = skill entry point referenced by `plugin.yaml`; CANON = canonical engine/adapter, moves to `core/`; LEGACY = archived controller/gate, moves to `core/legacy/`; MODULE = real code for one of the 14 policy modules, moves to `modules/<module>/`; RENDER = renderer, moves to `rendering/`; CONFIG = central/current policy, moves to `config/`; TEST = test file, moves to `tests/`; KEEP-ARCHIVE = historical reference/report, stays; KEEP-ASSET = owner-approved asset, never move/replace.

## Root (8 files)

| # | Current path | Proposed path | Reason |
|---|---|---|---|
| 1 | `README.md` | KEEP | Root readme; documents the 88-file count, canonical runtime, and historical notes. No move. |
| 2 | `plugin.json` | KEEP | PACKAGING — mandatory plugin manifest, v4.9.2. Must stay at root. |
| 3 | `plugin.yaml` | KEEP | PACKAGING — mandatory manifest; references `skills/erudience/SKILL.md`. Must stay at root. |
| 4 | `.app.json` | KEEP | PACKAGING — mandatory app manifest, v4.9.2 (hidden file; counted in the 88). Must stay at root. |
| 5 | `.agent-plugin/plugin.json` | KEEP | PACKAGING — mandatory platform manifest (byte-identical host mirror per `reports/architecture-audit.md` §6; deleting breaks that host's discovery). |
| 6 | `.claude-plugin/plugin.json` | KEEP | PACKAGING — mandatory platform manifest, same as #5. |
| 7 | `.codex-plugin/plugin.json` | KEEP | PACKAGING — mandatory platform manifest; also carries `interface.defaultPrompt: "erudiance_linkdin"` and author `contact@erudience.com`. Same version/description as the others. |
| 8 | `tests_content_engine.py` | `tests/tests_content_engine.py` | TEST — root-level test for `content_engine` (10 tests per `README.md`); `reports/dependency-map.md` shows it imports `content_engine` via `sys.path.insert(0,'scripts')`. Moving it to `tests/` requires updating that path insertion to the new module location. |

## agents/ (1 file)

| # | Current path | Proposed path | Reason |
|---|---|---|---|
| 9 | `agents/roles-v34.md` | KEEP | Role table for all 18 specialist roles (business/competitor/buyer/market/keyword/intent/topic/strategist/funnel/writer/SEO/editorial/fact-check/creative/image/brand-QA/delivery/analytics). It is the spec the 14 modules are staffed against; no code to move. |

## assets/ (1 file)

| # | Current path | Proposed path | Reason |
|---|---|---|---|
| 10 | `assets/erudience-owner-approved-logo-2026-11-21.jpg` | KEEP | KEEP-ASSET — owner-approved original logo, owner-uploaded 2026-11-21, JPEG 1536×1536, SHA-256 `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226` (per `README.md`). Never move, replace, redraw, or recolour. Referenced by `references/production-policy-v33.json` `brand_assets.approved_logo_path` and by `references/brand-assets-manifest.md`. |

## references/ (36 files)

| # | Current path | Proposed path | Reason |
|---|---|---|---|
| 11 | `references/asset-and-font-policy.md` * | KEEP | KEEP-ARCHIVE — website-first asset/font policy (Inter/DM Sans, `#10B981`, no bundled logo until verified). Historical spec; conflicts with current policy (see policy-conflicts C1–C5). Kept as archive, not deleted. |
| 12 | `references/autonomous-execution-v40.md` | KEEP | KEEP-ARCHIVE — v40 controller contract; claims `autonomous_pipeline_v40.Controller` is "the only supported new controller API" (conflicts with v41 canonical claim, C6). Kept as the archived spec for `core/legacy/autonomous_pipeline_v40.py`. |
| 13 | `references/batch-production-v45.md` * | KEEP | KEEP-ARCHIVE — batch-production spec for `batch_guard_v45.py`. (Not individually read; path follows its named script.) |
| 14 | `references/brand-assets-manifest.md` | KEEP | KEEP-ARCHIVE — current brand asset manifest; names the owner-approved logo (priority 1) and `references/owner-approved-brand-v46.md` as authoritative policy. Stays in `references/`; the asset itself stays in `assets/`. |
| 15 | `references/brand-policy-current.md` | `config/brand-policy-current.md` | CONFIG — the current human-readable brand policy (Sora, `#10B77F`, logo optional). Moves with the central policy JSON into the new `config/` folder so the two current-policy files live together. SKILL.md's "read these first" pointer must be updated to the new path. |
| 16 | `references/brand-source-of-truth-v36.md` | KEEP | KEEP-ARCHIVE — v3.6 brand source of truth (Sora 400–800 for posters; Inter/DM Sans for website UI only; palette emerald `#10B981`; logo from website repo `src/assets/logo-horizontal.png` / `erudience-icon.png`). Historical spec; its palette conflicts with the current JSON (C2). |
| 17 | `references/brand-template-contract-v47.md` | KEEP | KEEP-ARCHIVE — v4.7 brand/template contract (Inter/DM Sans, `#10B981`, logo required, original logo composited after generation). Competing owner-approved profile (C1–C3, C5). Kept, not rewritten. |
| 18 | `references/brief-schema-example.json` * | KEEP | KEEP-ARCHIVE — example brief schema for the creative-brief module. (Not individually read.) |
| 19 | `references/chat-vision-audit-v35.md` * | KEEP | KEEP-ARCHIVE — chat-vision audit spec. (Not individually read.) |
| 20 | `references/chatgpt-runtime-v43.md` * | KEEP | KEEP-ARCHIVE — runtime spec for the ChatGPT bridge. (Not individually read.) |
| 21 | `references/content-to-creative-brief-v21.md` * | KEEP | KEEP-ARCHIVE — content-to-brief spec for `modules/creative_brief/`. (Not individually read.) |
| 22 | `references/endpoint-registry.json` * | KEEP | KEEP-ARCHIVE — endpoint declarations; per `reports/architecture-audit.md` all providers are NOT_CONFIGURED (`DOCUMENTED_PROVIDER_API_NOT_CONNECTED`). (Not individually read.) |
| 23 | `references/execution-state-machine-v39.md` | KEEP | KEEP-ARCHIVE — v3.9 state-machine contract; claims `production_controller_v39.py` is authoritative (conflicts with v41, C6) and records the website-first profile (Inter/DM Sans, logo optional). Kept as the archived spec for `core/legacy/production_controller_v39.py`. |
| 24 | `references/gate-contract-v41.md` | KEEP | KEEP-ARCHIVE — the 17-stage gate contract for the canonical engine. Its own brand paragraph (Inter/DM Sans, `#10B981`) contradicts the `gate_chain_v41.py` code it documents (C10); kept verbatim, conflict recorded, not silently corrected. |
| 25 | `references/gates-and-handoff.md` * | KEEP | KEEP-ARCHIVE — gates/handoff spec. (Not individually read.) |
| 26 | `references/integration-registry-v34.json` * | KEEP | KEEP-ARCHIVE — integration registry; per SKILL.md the external integration registry may remain NOT_CONFIGURED without blocking manual ChatGPT-based draft production. (Not individually read.) |
| 27 | `references/master-action-v31.md` * | KEEP | KEEP-ARCHIVE — master-action spec (v31). (Not individually read.) |
| 28 | `references/master-command-v6.md` | KEEP | KEEP-ARCHIVE — master system command v6; records an explicit owner choice of website fonts (Inter + DM Sans) over Sora "for this independent draft" and "Do not ask the user again to choose between Sora and website fonts" (C13 — scope of that choice is UNRESOLVED). Kept verbatim. |
| 29 | `references/monthly-weekly-social-os.md` * | KEEP | KEEP-ARCHIVE — monthly (21st anchor) / weekly planning spec, named active by `references/unified-system-v42.md`. (Not individually read.) |
| 30 | `references/one-action-production-contract.md` * | KEEP | KEEP-ARCHIVE — one-action production contract. (Not individually read.) |
| 31 | `references/one-command-v44.md` | KEEP | KEEP-ARCHIVE — one-command runtime v4.4; canonical trigger `erudiance_linkdin`, alias `erudience_linkdin`; 7 distinct weekly pairs, 17 gates, 3 repairs, no scheduled background execution. |
| 32 | `references/orchestrator-v2.md` | KEEP | KEEP-ARCHIVE — one-action orchestration v2; 14-step strategy/build/controller flow, 30-day planning schema, terminal states including `OWNER_APPROVED` / `SOCIAL_OS_DRAFT_CREATED`. No code implements most of these states (see architecture draft §9). |
| 33 | `references/owner-approved-brand-v46.md` | KEEP | KEEP-ARCHIVE — owner-approved branding, authoritative from 2026-11-21 per its own header; claims to override logo-optional for NEW posters and states website fonts Inter/DM Sans + `#10B981` (C3, C5). Kept verbatim; the conflict is UNRESOLVED. |
| 34 | `references/production-contract-v33.md` * | KEEP | KEEP-ARCHIVE — production contract v33 (companion to the v33 policy JSON). (Not individually read.) |
| 35 | `references/production-execution-v35.md` * | KEEP | KEEP-ARCHIVE — production execution v35. (Not individually read.) |
| 36 | `references/production-policy-v33.json` | `config/production-policy-v33.json` | CONFIG — the ONLY machine-readable brand configuration (Sora heading+body, emerald `#10B77F`, logo optional, approved logo path, 14 modules, 8 capabilities, 7 planning slots, 1 promotion slot, 50-competitor research target). Moves to the new `config/` folder; filename and `"version": "3.3.0"` kept verbatim. Code that reads it at import (`gate_chain_v41.py`, `validate_strategy_v33.py`) must have its path updated from `references/` to `config/` and regression re-run. |
| 37 | `references/production-runtime-v37.md` * | KEEP | KEEP-ARCHIVE — production runtime v37. (Not individually read.) |
| 38 | `references/release-audit-v34.md` * | KEEP | KEEP-ARCHIVE — release audit v34; cited by `README.md` historical notes for known blockers. (Not individually read.) |
| 39 | `references/release-compatibility-v48.md` | KEEP | KEEP-ARCHIVE — v4.8 compatibility / no-silent-bypass policy; claims `gate_chain_v41.py` enforces v4.7 logo/content-to-poster requirements and that a missing DM Sans binary BLOCKS final rendering (the code does neither — C11). Kept verbatim, conflict recorded. |
| 40 | `references/runtime-and-compatibility-v49.md` | KEEP | KEEP-ARCHIVE — runtime/compatibility contract v4.9; names `scripts/gate_chain_v41.py` the single canonical validator (stable import path) and `production_controller_v39.py` / `workflow_engine.py` archived compatibility code. This file is the authority for the shim requirement in the notes below. |
| 41 | `references/smb-content-strategy-v32.md` * | KEEP | KEEP-ARCHIVE — SMB content strategy v32. (Not individually read.) |
| 42 | `references/strategy-playbook.md` * | KEEP | KEEP-ARCHIVE — strategy playbook (market-trends module spec, by filename). (Not individually read.) |
| 43 | `references/system-architecture-v34.md` * | KEEP | KEEP-ARCHIVE — system architecture v34. (Not individually read.) |
| 44 | `references/unified-system-v42.md` | KEEP | KEEP-ARCHIVE — unified plugin v4.2; names `gate_chain_v41.py` the only orchestration/gates module AND `website-brand-profile-v38.md` + `website_brand_v38.py` the website brand contract — i.e. it pairs the Sora-JSON gate with the Inter/DM Sans brand profile (C13). Kept verbatim. |
| 45 | `references/website-brand-profile-v38.md` | KEEP | KEEP-ARCHIVE — website-first brand profile (owner override 2026-11-21 per its header; Inter/DM Sans, `#10B981`, logo required on new branded images). Competing profile (C1–C3). Kept verbatim. |
| 46 | `references/workflow-v3.md` * | KEEP | KEEP-ARCHIVE — workflow v3. (Not individually read.) |

## reports/ (6 files)

| # | Current path | Proposed path | Reason |
|---|---|---|---|
| 47 | `reports/architecture-audit.md` | KEEP | KEEP-ARCHIVE — v4.9.2 architecture audit; the source for the canonical-system table, the 17-stage verification, the compatibility-vs-historical split, and the brand-consistency summary used by this draft. |
| 48 | `reports/cleanup-evidence.md` | KEEP | KEEP-ARCHIVE — v4.9.2 cleanup evidence (9 README stubs deleted; brand-correction decision NOT applied, pending owner decision). |
| 49 | `reports/dependency-map.md` | KEEP | KEEP-ARCHIVE — v4.9.2 dependency map; the source for the production import graph (linear chain + 2 edges), test-only edges, and the unimported-modules list used by this draft. |
| 50 | `reports/regression-results.md` * | KEEP | KEEP-ARCHIVE — regression results (107→112 tests, 20/20 E2E per `README.md`). (Not individually read.) |
| 51 | `reports/release-verification.md` * | KEEP | KEEP-ARCHIVE — release verification; per `reports/architecture-audit.md` §3 it records the controller/brand contradictions as known limitations requiring an owner decision. (Not individually read.) |
| 52 | `reports/source-inventory.md` * | KEEP | KEEP-ARCHIVE — source inventory; per `README.md` it verifies the owner-approved logo SHA-256 from the owner upload. (Not individually read.) |

## scripts/ (35 files)

| # | Current path | Proposed path | Reason |
|---|---|---|---|
| 53 | `scripts/autonomous_pipeline_v40.py` | `core/legacy/autonomous_pipeline_v40.py` | LEGACY — 13-stage in-memory coordinator with the only deterministic content/brand validators (`deterministic_content_match`, `deterministic_brand_check`); enforces Inter/DM Sans + `#10B981` + `brand_profile == 'website-v38'`. Archived, not a live path (SKILL.md, runtime-v49). Test: `tests/test_autonomous_pipeline_v40.py`. |
| 54 | `scripts/batch_gate.py` | `core/legacy/batch_gate.py` | LEGACY — local structural batch gate (count, duplicate IDs, copy/brief/prompt/image-SHA/QA-receipt per item, `controller_decision == PASS`). No test (per dependency-map). Archived. |
| 55 | `scripts/batch_guard_v45.py` | `core/batch_guard_v45.py` | CANON — batch adapter over the bridge (7 jobs, manifest, `summary()`). Imports `chatgpt_bridge_v43`. Moves with the orchestrator layer; old path kept as a shim (see notes). |
| 56 | `scripts/brand_policy_v36.py` | `modules/brand_claims_qa/brand_policy_v36.py` | MODULE — brand_claims_qa: caption checks (hashtag allow-list, banned words) + poster-spec checks. Mixed profile: Sora font check + `#10B981` palette + mandatory logo (`LOGO_NOT_AUTHENTICATED`) — see C12. Moved as-is; conflict not rewritten. |
| 57 | `scripts/brand_render_v37.py` | `rendering/brand_render_v37.py` | RENDER — Sora renderer; mandatory verified logo + Sora font files; pins `brand_policy == 'social-os/BRAND.md:v1.1'` (file does not exist in repo — C18); 3–5 steps. Moved as-is. |
| 58 | `scripts/brief_prompt_gate.py` | `modules/creative_brief/brief_prompt_gate.py` | MODULE — creative_brief: brief→prompt structural gate (brief SHA, exact-copy match, 1080×1350, `logo_sha256` required, `font_files_verified`). No test (per dependency-map). |
| 59 | `scripts/chatgpt_bridge_v43.py` | `core/chatgpt_bridge_v43.py` | CANON — durable checkpoint adapter over the 17 stages; imports `gate_chain_v41`. Moves with the orchestrator layer; old path kept as a shim. |
| 60 | `scripts/competitor_monitor.py` * | `modules/competitor_intelligence/competitor_monitor.py` | MODULE — competitor_intelligence. (Not individually read; integration-tests-only per dependency-map.) |
| 61 | `scripts/content_engine.py` | `modules/linkedin_copywriting/content_engine.py` | MODULE — linkedin_copywriting (also carries funnel_planning logic: `funnel_stage`, `weekly_batch`). Offline workflow, 10 differently-named stages, claim→source binding, case-study permission gate. Test: `tests_content_engine.py` → `tests/`. |
| 62 | `scripts/evidence_store.py` | `core/evidence_store.py` | CANON (shared infra) — knowledge_provenance + the only owner-approval/write-authorisation model (`can_handoff()`). SQLite, no caller, no test (per dependency-map). Moved to `core/` as shared infrastructure, not to a single module, because it serves provenance, receipts, and approval. |
| 63 | `scripts/gate_chain_v41.py` | `core/gate_chain_v41.py` | CANON — the ONE canonical 17-stage validation engine. Reads `references/production-policy-v33.json` at import (path must change to `config/`); reads the approved logo at IMAGE_BUILD only if planned. Old path kept as a thin re-export shim — this is required by `references/runtime-and-compatibility-v49.md` ("stable import path"). |
| 64 | `scripts/integration_tests.py` * | `tests/integration_tests.py` | TEST — integration tests importing `keyword_research`, `linkedin_seo_validator`, `competitor_monitor`, `linkedin_analytics`, `workflow_engine` (per dependency-map). CI runs it explicitly because `unittest discover -p 'test_*.py'` does not pick it up (per dependency-map). Moving it to `tests/` requires the same explicit CI invocation against the new path. |
| 65 | `scripts/keyword_research.py` * | `modules/topic_intelligence/keyword_research.py` | MODULE — topic_intelligence; imports `linkedin_seo_validator` (the only non-canonical production import edge). (Not individually read.) |
| 66 | `scripts/linkedin_analytics.py` * | `modules/analytics_learning/linkedin_analytics.py` | MODULE — analytics_learning. (Not individually read; integration-tests-only per dependency-map.) |
| 67 | `scripts/linkedin_seo_validator.py` * | `modules/topic_intelligence/linkedin_seo_validator.py` | MODULE — topic_intelligence; imported by `keyword_research.py`. Moves with it so the import edge stays intra-module. (Not individually read.) |
| 68 | `scripts/production_controller_v39.py` | `core/legacy/production_controller_v39.py` | LEGACY — 13-stage single-item controller, atomically persisted state (mkstemp + fsync + os.replace); the only persisted controller. Only caller is its test. Archived, not a live path. |
| 69 | `scripts/production_gate.py` | `core/legacy/production_gate.py` | LEGACY — 9-stage file-receipt acceptance gate (RESEARCH/KEYWORDS/STRATEGY/DRAFT/FACT_QA/SEO_QA/BRAND_QA/CREATIVE/VISUAL_QA); requires verified logo + heading/body font assets + palette/voice approval; external writes disabled. Archived. |
| 70 | `scripts/render_poster.py` | `rendering/render_poster.py` | RENDER — deterministic review-draft renderer; Inter/DM Sans (4 CLI font files); fixed 6-step template (exactly 2 headline lines + 6 cards); logo required for final unless `--review-draft`. Its manifest format is what `verify_output.py` expects. No test (per dependency-map). Moved as-is. |
| 71 | `scripts/test_autonomous_pipeline_v40.py` * | `tests/test_autonomous_pipeline_v40.py` | TEST — 12 fixture-backed tests per `references/autonomous-execution-v40.md`. Import target moves to `core/legacy/autonomous_pipeline_v40.py` (via shim or updated import). |
| 72 | `scripts/test_batch_guard_v45.py` * | `tests/test_batch_guard_v45.py` | TEST — imports `batch_guard_v45` and `gate_chain_v41` (per dependency-map). |
| 73 | `scripts/test_brand_policy_v36.py` * | `tests/test_brand_policy_v36.py` | TEST — imports `brand_policy_v36`. |
| 74 | `scripts/test_brand_policy_v49.py` * | `tests/test_brand_policy_v49.py` | TEST — imports `gate_chain_v41` (current-brand policy regression). |
| 75 | `scripts/test_brand_render_v37.py` * | `tests/test_brand_render_v37.py` | TEST — imports `brand_render_v37`; 4 brand-failure-path tests per `README.md` historical notes. |
| 76 | `scripts/test_chatgpt_bridge_v43.py` * | `tests/test_chatgpt_bridge_v43.py` | TEST — imports `chatgpt_bridge_v43`. |
| 77 | `scripts/test_gate_chain_v41.py` * | `tests/test_gate_chain_v41.py` | TEST — imports `gate_chain_v41`; 10 tests per `reports/cleanup-evidence.md`. |
| 78 | `scripts/test_production_controller_v39.py` * | `tests/test_production_controller_v39.py` | TEST — imports `production_controller_v39`; 14 methods per `reports/cleanup-evidence.md`. |
| 79 | `scripts/test_production_gate.py` * | `tests/test_production_gate.py` | TEST — 6 negative-path tests per `README.md` historical notes. |
| 80 | `scripts/test_strategy_v33.py` * | `tests/test_strategy_v33.py` | TEST — imports `validate_strategy_v33`. |
| 81 | `scripts/test_verify_output.py` * | `tests/test_verify_output.py` | TEST — new in v4.9.2; imports `verify_output`; 5 tests (import safety + CLI pass/block) per `reports/cleanup-evidence.md`. |
| 82 | `scripts/test_website_brand_v38.py` * | `tests/test_website_brand_v38.py` | TEST — imports `website_brand_v38`; encodes the website-first profile (Inter/DM Sans, `#10B981`). |
| 83 | `scripts/validate_strategy_v33.py` * | `modules/marketing_strategy/validate_strategy_v33.py` | MODULE — marketing_strategy. Loads the policy JSON at import and never uses it (per `reports/architecture-audit.md` §6) — flagged, not fixed by the move. (Not individually read.) |
| 84 | `scripts/verify_output.py` * | `core/verify_output.py` | CANON (mechanical gate) — PNG decode / 1080×1350 / ≤5 MB / sibling manifest + SHA256 / locked 6-step stage names. Moved to `core/` (not `modules/`) because it gates orchestrator output, and because its expected manifest format is `render_poster.py`-specific (6 steps) — see C19. (Not individually read; fixed in v4.9.2 with a `__main__` guard per `reports/cleanup-evidence.md`.) |
| 85 | `scripts/website_brand_v38.py` | `modules/brand_claims_qa/website_brand_v38.py` | MODULE — brand_claims_qa: website-first brand spec (Inter/DM Sans, `#10B981`, logo optional if provenance supplied, font SHA256s required, visual-inspection receipt required). Moved as-is; conflicts with `brand_policy_v36.py` in the same module (C12) — recorded, not merged. |
| 86 | `scripts/website_render_v38.py` | `rendering/website_render_v38.py` | RENDER — website-first renderer; Inter/DM Sans files + SHA256; palette `#10B981`; logo optional (text wordmark if absent); 3–5 steps only. Imports `website_brand_v38` (`PALETTE`). Both move, so this import edge becomes cross-directory (`rendering/` → `modules/brand_claims_qa/`) and must be updated or shimmed — see notes. No test (per dependency-map). |
| 87 | `scripts/workflow_engine.py` | `core/legacy/workflow_engine.py` | LEGACY — 10-stage 7-slot orchestrator (RESEARCH/KEYWORDS/STRATEGY/DRAFT/FACT_QA/SEO_QA/CREATIVE/VISUAL_QA/OWNER_APPROVAL/DELIVERY); requires exactly 1 promotion with `employee_requirement`; external writes always BLOCKED (`NO_VERIFIED_WRITE_ADAPTER`). Only caller is `integration_tests.py`. Archived. |

## skills/ (1 file)

| # | Current path | Proposed path | Reason |
|---|---|---|---|
| 88 | `skills/erudience/SKILL.md` | KEEP | ENTRY — the skill entry point; `plugin.yaml` lists `skills/erudience/SKILL.md`. Moving it would break plugin packaging. Its internal references to `references/brand-policy-current.md`, `references/runtime-and-compatibility-v49.md`, `references/production-policy-v33.json`, and `scripts/gate_chain_v41.py` etc. must be updated to the new `config/` / `core/` paths (or resolved via the shims) as part of the move — a documentation change, not a file move. |

## Totals

- Counted: **88** (root 8, agents 1, assets 1, references 36, reports 6, scripts 35, skills 1).
- KEEP: **53** (root 7, agents 1, assets 1, references 34, reports 6, skills 1, scripts 0 — every `scripts/` file moves).
- MOVE: **38** — `config/` 2 (#15, #36) + `core/` 5 (#55, #59, #62, #63, #84) + `core/legacy/` 5 (#53, #54, #68, #69, #87) + `modules/` 9 (#56, #58, #60, #61, #65, #66, #67, #83, #85) + `rendering/` 3 (#57, #70, #86) + `tests/` 14 (#8, #64, #71–#82). 2 + 5 + 5 + 9 + 3 + 14 = 38.
- KEEP: **50** — root 7, agents 1, assets 1, references 34, reports 6, skills 1. 38 + 50 = 88. ✓
- No file is deleted in this map. The 9 historical README stubs deleted in v4.9.2 (see `reports/cleanup-evidence.md`) are already gone from the baseline and are not part of the 88.

## Notes / prerequisites for executing this map (not part of the file count)

1. **Shims (new files, not in the 88):** thin re-export shims must be left at `scripts/gate_chain_v41.py`, `scripts/chatgpt_bridge_v43.py`, and `scripts/batch_guard_v45.py` (and legacy shims as needed by tests/CI) to preserve the stable import path named in `references/runtime-and-compatibility-v49.md` and the import edges recorded in `reports/dependency-map.md`. A shim is a new file; it does not change the 88-file count of the baseline.
2. **Import-path updates required by the moves:** `gate_chain_v41.py` and `validate_strategy_v33.py` read the policy JSON via a path relative to their own file (`parent.parent / 'references' / 'production-policy-v33.json'`); both must point at `config/` after the move. `website_render_v38.py` imports `website_brand_v38` (PALETTE); after the moves that import crosses from `rendering/` to `modules/brand_claims_qa/`. `keyword_research.py` imports `linkedin_seo_validator` — both move together into `modules/topic_intelligence/`, so that edge stays intra-module. `chatgpt_bridge_v43.py` imports `gate_chain_v41`; `batch_guard_v45.py` imports `chatgpt_bridge_v43` — both move together into `core/`, so that chain stays intra-directory. Test files import by bare module name and rely on `sys.path` insertion / running from `scripts/` (there is no `scripts/__init__.py` — per `reports/architecture-audit.md` §6); the target must define how `tests/` resolves `core/`, `modules/`, and `rendering/` imports before any move is executed. This draft does not choose the mechanism.
3. **SKILL.md / README.md pointer updates:** `skills/erudience/SKILL.md` and `README.md` cite the old `references/` and `scripts/` paths; both must be updated to `config/` / `core/` (or to the shims) as documentation changes.
4. **CI (outside the 88, not moved):** `.github/workflows/erudience-regression.yml` lives at the repo root, not in `erudience-plugin/`; it runs `unittest discover -s scripts -p 'test_*.py'`, `unittest tests_content_engine`, and `scripts/integration_tests.py -v`. All three invocations must be updated to the new `tests/` locations. This file was not read for this draft.
5. **No empty placeholder modules are created by this map.** Modules with no existing code (`business_service_intelligence`, `buyer_intelligence`, `market_trends`, `image_generation`, and `approval_distribution` as a standalone module) get no directory. See `target-architecture-draft.md` §4.
