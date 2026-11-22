# Erudience Plugin — Duplicate Classification (DRAFT)

- **Repo:** `~/workspace/erudiance-plugin-work/ERUDIANCE/erudience-plugin/`
- **Baseline stated in task:** `main` merge commit `9e320fa60785f40142f37be9342b3df42fc47968` (v4.9.2, PR #1). Baseline commit not verified (no git commands run — read-only task).
- **Method:** read-only file reads of every file under `references/` (36 files — task brief said 35; the directory listing contains 36) and every file under `scripts/` (35 files — task brief said 36; the directory listing contains 35), plus `tests_content_engine.py` at the plugin root and the six manifests. Classification is by content comparison from reading, not by byte hashing (no commands run, so no hashes were computed except those quoted from files themselves).
- **Rules applied per the task:** the 3 byte-identical `plugin.json` copies are COMPATIBILITY_REQUIRED, not duplicates to delete; conflicting policies are CONFLICTING_POLICY, never silently resolved; every candidate lists what overlaps, what is unique, and what would be lost if removed.

## Classification labels used

- **EXACT_DUPLICATE** — byte-identical (or stated identical in the repo) content.
- **SEMANTIC_DUPLICATE** — different wording/file, same behaviour/content; one could replace the other with no loss.
- **PARTIAL_DUPLICATE** — substantial overlap plus unique content; removal would lose the unique part.
- **UNIQUE** — no meaningful overlap with any other file.
- **CONFLICTING_POLICY** — overlaps in subject matter but asserts incompatible rules; must not be silently resolved or merged.
- **COMPATIBILITY_REQUIRED** — duplication is intentional for host/platform compatibility.
- **HISTORICAL_UNIQUE** — the sole surviving record of a superseded version's contract/behaviour; archival value, not live.
- **DISCONNECTED** — code/doc with no live caller or live path (kept as a secondary flag in the notes, not used as a primary label here except where the file's only role is a dead path — in this draft no file takes DISCONNECTED as its primary label; disconnectedness is recorded per file in the dependency map).
- **UNVERIFIED** — content whose claims cannot be checked against anything in the repo (used once, see §5).

## 1. References (36 files)

### 1.1 CONFLICTING_POLICY (8)

| File | Overlaps with | What is unique | What would be lost if removed | Conflict in one line |
|---|---|---|---|---|
| `asset-and-font-policy.md` | `brand-source-of-truth-v36.md`, `website-brand-profile-v38.md`, `master-command-v6.md` (website fonts/logo candidates) | Sole statement that the package deliberately includes NO logo binary until verified; "website typography has owner-approved precedence"; candidate `logo-icon.jpg` unconfirmed | The only explicit "no bundled logo until verified" packaging rule and the unconfirmed-candidate warning | Website Inter/DM Sans precedence + emerald **#10B981** vs current Sora / **#10B77F** |
| `brand-source-of-truth-v36.md` | `brand-policy-current.md`, `production-policy-v33.json` (Sora, palette, caption rules) | Sole pointer to external authority `bishal-paul-git/erudience-social-os` `BRAND.md` v1.1 (2026-10-02/05); "fallback Inter only when explicitly permitted, mark NOT_EXACT_BRAND"; Mint HSL token | Provenance of the Sora rule (Social OS BRAND.md v1.1) and the explicit no-silent-substitution rule | Sora but emerald **#10B981**; logo from website repo `src/assets/logo-horizontal.png` / `erudience-icon.png` vs bundled `assets/erudience-owner-approved-logo-2026-11-21.jpg` |
| `brand-template-contract-v47.md` | `owner-approved-brand-v46.md` (logo, palette, fonts) | Sole "content brand marketing gate" (audience/ICP, buyer pain, linked capability, funnel stage) and "image plan gate" checklists; "Maximum three repairs" stated in a brand doc | The two brand gates as checklists; the v4.7 priority claim itself | Inter/DM Sans + **#10B981** + "supersede legacy logo-optional, Sora-only" vs current Sora / **#10B77F** / logo-optional |
| `gate-contract-v41.md` | `gate_chain_v41.py` (same 17 stages, repair map, reviewer rules) | Sole prose contract for v4.1: stage list, hash binding, repair routing, "Endpoints: this package contains NO live API endpoints" | The human-readable v4.1 contract; the explicit no-endpoints statement | States website brand as Inter/DM Sans, emerald **#10B981**, "Existing old Sora/mandatory-logo gates are historical only" — directly contradicts `production-policy-v33.json` (Sora / #10B77F), which the code it documents actually enforces |
| `master-command-v6.md` | `one-action-production-contract.md`, `render_poster.py`, `brief-schema-example.json` (Warm Enquiry locked copy, 6 stages) | Sole full V6 system command: `/VERIFY_OWNER_INSTRUCTION → … → /REQUEST_OWNER_APPROVAL` execution order; website font audit (Inter 800/700/600, DM Sans 400–500); approved benchmark Supabase URL + content-item ID; LinkedIn help URL | The only complete paste-into-ChatGPT V6 instruction set and the only record of the benchmark URL + `os_image_jobs` record ID | "Inter + DM Sans are mandatory … **Sora is excluded**" vs current Sora-required policy |
| `owner-approved-brand-v46.md` | `brand-assets-manifest.md`, `brand-template-contract-v47.md`, `website-brand-profile-v38.md` | Sole owner-approval record dated 2026-11-21 for the bundled JPEG; sampled JPEG pixel colours (#060807, #CEFDED, ~#04DF69); "do NOT recolour the authentic logo"; black-square background handling rule | The dated owner direction itself — the only evidence the bundled logo is owner-approved and the only pixel-level description of it | "Previous logo-optional rules are superseded" + **#10B981** + Inter/DM Sans vs current logo-optional / Sora / **#10B77F** |
| `production-runtime-v37.md` | `production-execution-v35.md`, `brand_render_v37.py` | Sole statement that `brand_render_v37.py` is "the only accepted local deterministic final-image renderer" and `render_poster.py` is "legacy draft-only"; "Source of truth: Social OS BRAND.md locked v1.1" | The v3.7 runtime authority claim and the renderer exclusivity rule | Sora locked v1.1 + brand_render-only vs current Sora/#10B77F (same font, different emerald) and vs `website_render_v38` / `render_poster` existence |
| `website-brand-profile-v38.md` | `owner-approved-brand-v46.md`, `brand-template-contract-v47.md`, `website_brand_v38.py` | Shortest website-first profile; "Read `owner-approved-brand-v46.md` first" pointer; "owner now explicitly requires the bundled authentic logo" | The explicit pointer chain v38 → v46 and the one-paragraph website-first summary | Inter/DM Sans + **#10B981** + logo-required vs current Sora / **#10B77F** / logo-optional |

### 1.2 HISTORICAL_UNIQUE (4)

| File | Overlaps with | What is unique | What would be lost if removed |
|---|---|---|---|
| `autonomous-execution-v40.md` | `execution-state-machine-v39.md` (same 13 stages, repair idea) | Sole v4.0 contract: `Controller(job, adapters).run()` as "the only supported" API; deterministic reviewer code paths (`deterministic_content_match`, `deterministic_brand_check`) described as validators not humans; "Runtime adapters still needed" list | The v4.0 acceptance boundary and the reviewer-trust-boundary wording; the only doc tying v40's test count (12 tests) to its contract |
| `chat-vision-audit-v35.md` | `release-audit-v34.md` (audit findings) | Sole defect register of the direct-image-generation failure (generic palette/logo wordmark, component-level PASS reported as production evidence); "REJECTED_FOR_PRODUCTION" verdict; deferred-items list (social.erudience.com storage, approval workflow) | The incident record explaining why v3.5 fail-closed gates exist; the only list of what was deferred by the owner at that point |
| `execution-state-machine-v39.md` | `autonomous-execution-v40.md`, `production_controller_v39.py` (same 13 stages) | Sole v3.9 prose contract; CLI usage (`init/pass/fail/status`); "six-step content must use a renderer that can display all six steps" rule; concurrency warning (external lock needed) | The v3.9 operator instructions and the six-step renderer rule, neither of which appears in v40/v41 docs |
| `release-audit-v34.md` | `chat-vision-audit-v35.md` | Sole v3.4 audit: pre-upgrade findings (validate_strategy narrowness, content_engine URL-not-fetched, `__pycache__` artifact note); "Open deployment blockers" list; v3.4 overlay change list | The only dated audit trail for the v3.4 overlay and its blocker list |

### 1.3 PARTIAL_DUPLICATE (16)

| File | Overlaps with | What is unique | What would be lost if removed |
|---|---|---|---|
| `batch-production-v45.md` | `one-command-v44.md` (trigger, 7 jobs, 17 gates), `chatgpt-runtime-v43.md` (bridge), `runtime-and-compatibility-v49.md` | Collage ban with reasoning; verified-local-resampling rule (legible/uncut + re-review); "request a standalone 4:5 portrait poster" per-item tool instruction; batch READY rule (7 distinct verified PNGs) | The batch-specific image rules; the resampling exception |
| `brand-assets-manifest.md` | `owner-approved-brand-v46.md` (same logo path, same priority) | Shortest asset pointer: "OWNER APPROVED LOGO (priority 1)" + "AUTHORITATIVE POLICY: references/owner-approved-brand-v46.md" in one page | A one-page asset lookup; nothing substantive beyond v46 except the explicit priority-1 label |
| `chatgpt-runtime-v43.md` | `unified-system-v42.md`, `runtime-and-compatibility-v49.md` (bridge/gate roles), `batch-production-v45.md` | Sole step-by-step ChatGPT procedure (start → next → execute with ChatGPT tools → save receipt → submit → repeat); evidence requirements per stage (live SOURCES need `source_sha256`; IMAGE_BUILD needs verified Inter/DM Sans font files) | The operator procedure for the bridge; the per-stage evidence list |
| `integration-registry-v34.json` | `endpoint-registry.json` (linkedin, research, image_renderer, scheduler, analytics named in both) | Sole state list: all six integrations `NOT_CONFIGURED` + `read_only` + `requires_approval`; sole copy of the 10 `workflow_engine` stage names as a "stages" array | The machine-readable NOT_CONFIGURED record; the workflow_engine stage list in JSON form |
| `master-action-v31.md` | `master-command-v6.md`, `workflow-v3.md`, `orchestrator-v2.md` (action registries/pipelines) | Sole 20-action registry (`research.collect → … → analytics.feedback`) with action-contract schema; dispatcher branches per format (carousel/document need true multipage; `case_study` needs client approval); `claude` branch rule | The action registry and per-format branching rules |
| `monthly-weekly-social-os.md` | `smb-content-strategy-v32.md` (21st cycle, 7-slot), `production-contract-v33.md` | Sole W0–W11 approval chain (PLANNED → … → SCHEDULED_VERIFIED); write-authorisation must name `social.erudience.com`, exact 7 IDs, workspace/channel, drafts-only vs scheduling, dates/times; remote read-back verification rules | The Social OS write/read-back contract and the 11-state approval chain |
| `one-action-production-contract.md` | `master-command-v6.md`, `orchestrator-v2.md` (15-stage machine, locked Warm Enquiry copy, benchmark URL) | Sole 15-stage machine `INIT → SOURCES → REFERENCE → RESEARCH → COPY_LOCK → DESIGN → RENDER → PIXEL_INSPECTION → CONTENT_QA → BRAND_QA → MOBILE_QA → TECH_QA → BENCHMARK_QA → DECISION → DELIVERY`; "hard verification gates (ALL must pass for APPROVE)"; P0–P4 improvement roadmap | The 15-stage machine, the hard-gates list, the roadmap |
| `one-command-v44.md` | `batch-production-v45.md` (nearly the whole content) | Shortest trigger doc; canonical spelling `erudiance_linkdin` + alias `erudience_linkdin`; Asia/Dhaka 21st anchor in one line; "deliver partial results and explicit BLOCKED status" | The canonical trigger-spelling statement; very little else — this is the closest references file to a pure duplicate of `batch-production-v45.md` |
| `orchestrator-v2.md` | `one-action-production-contract.md`, `master-action-v31.md`, `workflow-v3.md` | Sole 14-step build/controller list; sole terminal-states list (15 states incl. `SOCIAL_OS_STAGED`, `MEASUREMENT_PENDING`); 30-day planning schema row | The terminal-states list and the 14-step sequence |
| `production-contract-v33.md` | `production-policy-v33.json` (same 14 modules, 7-slot/1-promo, 50 competitors, 8 capabilities) | Prose module IO table (input/processing/output/gate/integration per module); 10-field promotion specification; "Weekly editorial hard rule" (4 posts/week default, promo is part of the four); acceptance-checks list | The module IO table and the promotion spec; the JSON alone does not carry them |
| `production-execution-v35.md` | `production-contract-v33.md`, `production-runtime-v37.md` (gates, brand-first, receipts) | Sole "8 mandatory gates" numbered list; "No fabricated autonomy: report each adapter as CONFIGURED/NOT_CONFIGURED and real tests as PASS/BLOCKED/NOT_TESTED"; pilot acceptance paragraph | The 8-gate list and the adapter-status reporting rule |
| `release-compatibility-v48.md` | `runtime-and-compatibility-v49.md`, `unified-system-v42.md` (preserve legacy, no silent bypass, single controller path) | Sole v4.8 update checklist (5 steps: inventory diff, tests, poster/logo checks, source/font evidence, one live review); "If DM Sans font binary is missing, final rendering and production approval are BLOCKED" | The v4.8 checklist; the DM Sans-missing rule (note: conflicts with canonical Sora font — see CONFLICTING_POLICY) |
| `smb-content-strategy-v32.md` | `production-contract-v33.md` (7-slot/1-promo, 50 competitors), `monthly-weekly-social-os.md` (21st cycle) | Sole ICP hypothesis (5–50 employees); sole candidate solution catalogue with launched-vs-upcoming labelling (push8, Extinde, Transcriber/Meetmigo upcoming); 1–5 scoring rubric (7 criteria); buyer-expectation gate questions | The ICP/catalogue/rubric — the strategy substance not present in the contract docs |
| `system-architecture-v34.md` | `production-contract-v33.md` (modules, workflow, governance), `agents/roles-v34.md` (18 roles) | Sole keyword taxonomy (15 types) with record fields; sole content-formula router (Problem-Cause-Fix, Question-Answer-Evidence, etc.); per-module "Connections and dependencies" mapping scripts to stages | The taxonomy, the formula router, the script-dependency mapping |
| `unified-system-v42.md` | `runtime-and-compatibility-v49.md`, `release-compatibility-v48.md` (merge/compat, single controller) | Sole merge statement ("single-plugin merge, not multiple plugin installations"); sole explicit "Historical, not production approval paths" list (9 files named); "Unresolved live dependencies" list | The explicit historical-paths list and the merge rationale |
| `workflow-v3.md` | `master-action-v31.md`, `orchestrator-v2.md`, `monthly-weekly-social-os.md` | Sole 16-step "First-to-last pipeline" with FORMAT_ROUTER (text-only → no image; carousel/document → multipage, never a single PNG); sole "Required calendar record" field list; state machine with `NOT_APPLICABLE` for text-only visual stages | The format router and the calendar-record schema |

### 1.4 UNIQUE (8)

| File | Why unique | Overlap note |
|---|---|---|
| `brand-policy-current.md` | Sole "current policy" pointer doc for v4.9.2: Sora/#10B77F/logo-optional + weekly-research rule + update rules (preserve files, edit in place, run regression, reject stale tokens) | Restates `production-policy-v33.json` brand values in prose; that restatement is the point (human-readable current policy) |
| `brief-schema-example.json` | Sole example brief JSON (Warm Enquiry, 6 stages) | Its content is duplicated in prose in `master-command-v6.md` and as defaults in `render_poster.py` — the *file* is the only JSON instance; the *copy* is triplicated (see §4) |
| `content-to-creative-brief-v21.md` | Sole 7-stage A–G pipeline (content intelligence → brief → brief controller → prompt engineering → prompt controller → image QA → final controller); sole definition of `render_spec.json` + `image_prompt.md` artifacts; sole per-stage payload schema (`schema_version, content_id, revision, source_sha256, …`) | No other doc defines the brief→prompt handoff; `brief_prompt_gate.py` implements only the structural check for it |
| `endpoint-registry.json` | Sole endpoint declarations (provider URLs, methods, credential env vars, per-provider status) | Overlaps `integration-registry-v34.json` on integration names only; different purpose (endpoints vs state). All statuses are NOT_CONNECTED variants — documented-only, never working |
| `gates-and-handoff.md` | Sole G00–G13 gate matrix; sole Social OS payload proposal (explicitly "proposed adapter, not asserted current schema"); sole 100-point independent quality rubric (brand 20 / buyer 20 / factual 20 / hierarchy 15 / mobile 10 / CTA 10 / technical 5) | The rubric numbers are repeated in `one-action-production-contract.md` and `master-command-v6.md` (same 20/20/20/15/10/10/5 split) — rubric triplicated, gate matrix unique |
| `production-policy-v33.json` | Sole machine-readable brand + policy config; read at import by `gate_chain_v41.py` | Prose restatements exist in `brand-policy-current.md` and `production-contract-v33.md`; the JSON is the only executable source |
| `runtime-and-compatibility-v49.md` | Sole v4.9 runtime/compat contract: "Do not create versioned replacement controllers"; release process (inventory diff, canonical import edges, bridge/batch/brand tests, logo-present + logo-absent plans); "ZIP update does not provision scheduler, API credentials, persistence or runtime automation" | Overlaps v42/v48 on preserve-legacy; the no-new-controllers rule and release process are unique |
| `strategy-playbook.md` | Sole 30-day day-by-day plan (Week 1 pain → Week 2 education → Week 3 solutions → Week 4 conversion/proof); sole growth-experiment list (A/B hypotheses); sole funnel with instrumented-transition requirement | No other file gives a dated 30-day topic plan |

### 1.5 References counts

| Classification | Count |
|---|---|
| EXACT_DUPLICATE | 0 |
| SEMANTIC_DUPLICATE | 0 |
| PARTIAL_DUPLICATE | 16 |
| UNIQUE | 8 |
| CONFLICTING_POLICY | 8 |
| COMPATIBILITY_REQUIRED | 0 |
| HISTORICAL_UNIQUE | 4 |
| DISCONNECTED (primary) | 0 |
| UNVERIFIED (primary) | 0 |
| **Total** | **36** |

Notes: no two reference files are byte-identical or fully semantically interchangeable — the closest pair (`one-command-v44.md` vs `batch-production-v45.md`) still differs by the collage/resampling/batch rules. DISCONNECTED is not used as a primary label for docs (their disconnectedness is a property of the code paths they describe; see dependency map). UNVERIFIED as a primary label is not used for references: several docs cite external repos/URLs that could not be verified from inside this repo (see §5), but the files themselves are internally coherent records.

## 2. Scripts (35 files)

### 2.1 CONFLICTING_POLICY (8)

| File | Overlaps with | What is unique | What would be lost if removed | Conflict in one line |
|---|---|---|---|---|
| `autonomous_pipeline_v40.py` | `production_controller_v39.py` (same 13 stages, same repair idea), `gate_chain_v41.py` (adapter/Chain pattern) | Sole deterministic reviewer functions (`deterministic_content_match`, `deterministic_brand_check`); sole `Controller` API taking `(job, adapters)` with `prior` passed to adapters; `job_hash` immutability | The only deterministic content/brand validators in the repo; the only adapter API that passes `prior` | Hardcodes Inter/DM Sans + palette **#10B981** + `brand_profile == 'website-v38'`; does not read `production-policy-v33.json`; conflicts with canonical Sora / **#10B77F** |
| `brand_policy_v36.py` | `website_brand_v38.py` (same caption rules, same hashtags/banned words) | Sole `check_poster_spec` requiring `orchestrator_execution_id` + `visual_inspection_receipt` + `logo_source_commit`; sole `SOCIAL_FONT_NOT_SORA` error code | The orchestrator-execution evidence requirement | Sora font check but palette **#10B981**; logo sha + source commit **required** vs current logo-optional |
| `brand_render_v37.py` | `render_poster.py`, `website_render_v38.py` (same poster layout: pill, headline, steps, takeaway, footer logo) | Sole Sora renderer; sole renderer that pins `brand_policy == 'social-os/BRAND.md:v1.1'`; sole renderer writing a `.json` receipt next to the PNG with `RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA` | The only Sora-based deterministic renderer | Sora + **#10B981** + logo **mandatory** (verify_assets fails without logo) vs current Sora / #10B77F / logo-optional; pins a policy file that does not exist in the repo |
| `production_controller_v39.py` | `autonomous_pipeline_v40.py`, `gate_chain_v41.py` (controller pattern, hash binding, repair cap) | Sole atomically-persisted controller (tempfile + fsync + os.replace); sole CLI controller (`init/pass/fail/status`); sole `source_verified` flag on SOURCES/RESEARCH commits | The only persistent-state controller; the only CLI-driven gate controller | 13 stages (BRIEF/BRIEF_QA/RENDER) vs canonical 17; `BRAND_QA` requires `website_brand_verified` (Inter/DM Sans era) |
| `render_poster.py` | `brand_render_v37.py`, `website_render_v38.py` (same layout family) | Sole 6-fixed-card renderer (exactly 2 headline lines + 6 stages, enforced); sole `--review-draft` mode (labelled draft without logo); sole renderer emitting `REVIEW_DRAFT` / `REQUIRES_VISUAL_AND_SOURCE_QA` + `locked_stage_names` payload | The only renderer for the locked Warm Enquiry 6-card template; the only review-draft escape hatch | Inter/DM Sans + **#10B981** + logo required for final vs current Sora / #10B77F / logo-optional; 6 fixed cards vs 3–5-step plans |
| `website_brand_v38.py` | `brand_policy_v36.py` (caption rules) | Sole `check()` requiring `font_heading_sha256` + `font_body_sha256` + `visual_inspection_receipt`; imported by `website_render_v38.py` | The website-brand check used by the website renderer | Inter/DM Sans + **#10B981** vs current Sora / **#10B77F** |
| `website_render_v38.py` | `brand_render_v37.py`, `render_poster.py` | Sole website-first renderer (Inter/DM Sans, logo optional with wordmark fallback "Erudience" text when no logo); 3–5 steps | The only renderer matching the website-brand profile; the only logo-absent fallback that still renders a branded footer | Inter/DM Sans + **#10B981** vs current Sora / #10B77F; 3–5 steps vs `render_poster` 6 cards |
| `workflow_engine.py` | `validate_strategy_v33.py`, `content_engine.weekly_batch`, `batch_gate.validate_batch` (7-slot / 1-promo rules) | Sole 10-stage batch runner with receipt checking (`STAGES[:8]` must be PASS per item); sole `EXPLICIT_SCOPED_APPROVAL_REQUIRED` + `NO_VERIFIED_WRITE_ADAPTER` refusal path (external write can never succeed) | The only batch runner that refuses fake delivery even with approval | 10 stages vs 13/17; `employee_requirement` promo rule lives only here and in `validate_strategy_v33` |

### 2.2 PARTIAL_DUPLICATE (7)

| File | Overlaps with | What is unique | What would be lost if removed |
|---|---|---|---|
| `batch_gate.py` | `content_engine.weekly_batch`, `batch_guard_v45.summary`, `workflow_engine.run` (7-item batch validation) | Sole `manifest_sha256` over the whole batch; sole per-item field list (`copy`, `creative_brief_hash`, `prompt_hash`, `image_sha256`, `qa_receipt`, `controller_decision == PASS`); sole CLI taking a manifest path, exit 2 on BLOCK | The manifest-hash + per-item artifact-field check; the only batch gate callable from a shell on a JSON file |
| `brief_prompt_gate.py` | `gate_chain_v41.py` IMAGE_PLAN/IMAGE_BUILD checks (exact copy, dimensions, logo/font verification) | Sole brief↔prompt binding check (`brief_sha256`, `render_spec.exact_copy == brief.exact_copy`, `image_prompt` + `negative_prompt` required); sole `STRUCTURAL_PASS_ONLY` verdict with explicit "not content/visual/factual/brand/owner approval" note | The prompt-artifact validation; gate_chain has no prompt stage at all |
| `content_engine.py` | `workflow_engine.py`, `validate_strategy_v33.py`, `batch_gate.py` (7-slot batch, gates) | Sole claim↔source binding (`claims[].source_ids ⊆ sources[].source_id` with URL + `retrieved_at`); sole `calendar()` 30-day date grid with duplicate/out-of-window rejection; sole category/format routing (`CATEGORIES` × `FORMATS`, case-study permission, trend source) | Claim-evidence binding and the calendar grid — neither exists in the canonical chain |
| `linkedin_seo_validator.py` | `keyword_research.map_content` (primary keyword must appear in copy) | Sole hook/body/cta completeness check; sole keyword-stuffing heuristic (`count > max(3, words//60+1)`); sole `evidence_verified` requirement when claims exist | The stuffing heuristic and the post-completeness check |
| `production_gate.py` | `gate_chain_v41.py`, `production_controller_v39.py` (receipt + artifact hash + independent review checks) | Sole path-escape guard (`is_relative_to(root)`); sole brand-asset verification from a caller-supplied brand dict (logo/font_heading/font_body with `approved_source` + sha + path); sole `EXTERNAL_WRITE_DISABLED` / `IMAGE_INSPECTION_MISSING` errors | The path-traversal guard and the brand-dict verification |
| `validate_strategy_v33.py` | `workflow_engine.run`, `content_engine.weekly_batch` (7 slots, 1 promo, no deletion, employee requirement) | Sole CLI strategy validator; sole rule "educational slot contains direct pitch" (`direct_sales_pitch` on non-promo); sole `claimed_image` without `render_verified` rule | The educational-pitch and unverified-image rules in CLI form |
| `verify_output.py` | `gate_chain_v41.py` TECH_REVIEW, `production_gate.py` (PNG format/size/mode checks) | Sole mechanical PNG gate as a CLI (`--require-logo`); sole `locked_stage_names` check (the 6 Warm Enquiry stages); sole `size_under_5mb` check; sole `PASS_MECHANICAL_ONLY` verdict with explicit `unverified` list | The manifest-based mechanical gate; the only verifier that names what it does *not* verify |

### 2.3 UNIQUE (20)

| File | Why unique |
|---|---|
| `batch_guard_v45.py` | Sole 7-job initialiser (`initialise`) + batch summary over bridge state files; sole collage/reused-image-path guards in code |
| `chatgpt_bridge_v43.py` | Sole durable checkpoint bridge (start/next/submit/status CLI + JSON state); sole reuse of `Chain.verify` outside `Chain.run` |
| `competitor_monitor.py` | Sole competitor coverage auditor (50-target counts + gaps); sole `retrieved_at` date validation |
| `evidence_store.py` | Sole SQLite evidence ledger; sole `can_handoff()` requiring separate `APPROVE` + `WRITE_AUTHORISE` rows; sole `receipts`/`approvals` schema |
| `gate_chain_v41.py` | Sole canonical 17-stage validator; sole reader of `production-policy-v33.json` for live brand enforcement |
| `keyword_research.py` | Sole keyword cluster validator (15 types, 4 intents, exactly-one-primary, unsourced-volume rule) |
| `linkedin_analytics.py` | Sole analytics summarizer (CTR from observed values only, `attribution: not_inferred`) |
| `integration_tests.py` | Sole cross-module integration test file (keyword → SEO → competitor → analytics → workflow_engine) |
| `test_autonomous_pipeline_v40.py` | Sole tests for `autonomous_pipeline_v40.py` (12 methods incl. deterministic reviewer tests) |
| `test_batch_guard_v45.py` | Sole tests for `batch_guard_v45.py` (5 methods) |
| `test_brand_policy_v36.py` | Sole tests for `brand_policy_v36.py` (7 methods) |
| `test_brand_policy_v49.py` | Sole tests for the canonical brand rules via `gate_chain_v41` (5 methods; note: despite the v49 name it tests v41 code, not a v49 module) |
| `test_brand_render_v37.py` | Sole tests for `brand_render_v37.py` (4 methods, failure paths only) |
| `test_chatgpt_bridge_v43.py` | Sole tests for `chatgpt_bridge_v43.py` (7 methods) |
| `test_gate_chain_v41.py` | Sole tests for `gate_chain_v41.py` (10 methods) |
| `test_production_controller_v39.py` | Sole tests for `production_controller_v39.py` (14 methods) |
| `test_production_gate.py` | Sole tests for `production_gate.py` (6 methods) |
| `test_strategy_v33.py` | Sole tests for `validate_strategy_v33.py` (8 methods) |
| `test_verify_output.py` | Sole tests for `verify_output.py` (5 methods incl. import-safety regression) |
| `test_website_brand_v38.py` | Sole tests for `website_brand_v38.py` (5 methods) |

Notes: the 12 `test_*.py` files are UNIQUE as test coverage, not production duplicates — each covers exactly one module, and no two test the same function. `test_brand_policy_v49.py` is the one naming trap: it tests `gate_chain_v41`, not a v49 module (no `brand_policy_v49.py` exists).

### 2.4 Scripts counts

| Classification | Count |
|---|---|
| EXACT_DUPLICATE | 0 |
| SEMANTIC_DUPLICATE | 0 |
| PARTIAL_DUPLICATE | 7 |
| UNIQUE | 20 |
| CONFLICTING_POLICY | 8 |
| COMPATIBILITY_REQUIRED | 0 |
| HISTORICAL_UNIQUE | 0 |
| DISCONNECTED (primary) | 0 |
| UNVERIFIED (primary) | 0 |
| **Total** | **35** |

Notes: no two scripts are byte-identical or fully interchangeable. HISTORICAL_UNIQUE is not used for scripts: `production_controller_v39.py`, `autonomous_pipeline_v40.py` and `workflow_engine.py` are historical in the docs' telling, but they are classified CONFLICTING_POLICY because they are still executable, still tested, and still assert incompatible rules — archiving them as "historical" would hide the live conflict. DISCONNECTED is not used as a primary label for the same reason as in references; per the dependency map, 12 of the 35 scripts have no production caller (see §3 below) — that is recorded here as a secondary property, not a duplicate class. Files with no test at all: `evidence_store.py`, `batch_gate.py`, `brief_prompt_gate.py`, `website_render_v38.py`, `render_poster.py`.

## 3. Root test file and manifests (outside `references/` / `scripts/`)

| File | Classification | Evidence |
|---|---|---|
| `tests_content_engine.py` (plugin root) | UNIQUE | Sole tests for `content_engine.py` (10 methods). Not counted in the scripts/ total (it lives at the plugin root). |
| `plugin.json` | COMPATIBILITY_REQUIRED | Byte-identical (as read) to `.agent-plugin/plugin.json` and `.claude-plugin/plugin.json`. Intentional host mirrors — see below. |
| `.agent-plugin/plugin.json` | COMPATIBILITY_REQUIRED | Byte-identical to `plugin.json` (as read). |
| `.claude-plugin/plugin.json` | COMPATIBILITY_REQUIRED | Byte-identical to `plugin.json` (as read). |
| `.codex-plugin/plugin.json` | COMPATIBILITY_REQUIRED | Same name/version/description as `plugin.json`, plus extra `interface` (displayName, short/long description, developerName, category, capabilities `[]`, `defaultPrompt: "erudiance_linkdin"`) and `author` blocks. Not byte-identical — a host-specific extension, not a duplicate to delete. |
| `.app.json` | UNIQUE (manifest) | Same name/version, different description ("…owner-approved original logo and brand palette."). Distinct app-manifest shape; not a copy of `plugin.json`. |
| `plugin.yaml` | UNIQUE (manifest) | Same name/version, different description and different shape (YAML, lists `skills: [skills/erudience/SKILL.md]`). Not a copy of `plugin.json`. |

**Manifest verdict:** the three identical `plugin.json` copies are intentional per-host mirrors (root / Agent plugin / Claude plugin) and must not be deduplicated by deletion — removing any one would break that host's discovery. `.codex-plugin/plugin.json` is a fourth, host-extended variant. `plugin.yaml` and `.app.json` are different formats/shapes, not duplicates. No manifest file is an EXACT_DUPLICATE in the deletable sense.

## 4. Cross-cutting duplication (content triplicated across files, not file-level duplicates)

These are the repeated *contents* a consolidation must handle as units, not by deleting single files:

1. **Warm Enquiry locked copy (6 stages CAPTURE…OUTCOME + headline/emphasis/support/takeaway/diagnostic/CTA):** appears in `references/brief-schema-example.json`, `references/master-command-v6.md` (COPY_LOCK), `references/one-action-production-contract.md` (locked topic fallback), `scripts/render_poster.py` (STAGES default), `scripts/verify_output.py` (`locked_stage_names` check). Five homes, one copy. Changing the copy requires changing all five; deleting any one file does not remove the copy from the others.
2. **Caption rules (3 hashtags #AIAutomation/#WorkflowAutomation/#VoiceAI; 7 banned words revolutionise/unlock/leverage/seamless/cutting-edge/game-changing/supercharge):** in `scripts/brand_policy_v36.py`, `scripts/website_brand_v38.py`, `references/brand-source-of-truth-v36.md`. Three homes.
3. **Poster layout (1080×1350, paper pill, headline ≤12 words, 3–5 steps or 6 cards, dark takeaway, footer logo + erudience.com):** in `scripts/brand_render_v37.py`, `scripts/render_poster.py`, `scripts/website_render_v38.py`, `references/brand-source-of-truth-v36.md`, `references/brand-template-contract-v47.md`, `references/master-command-v6.md`. Six homes, three incompatible font/emerald/logo variants.
4. **100-point rubric (20/20/20/15/10/10/5):** in `references/gates-and-handoff.md`, `references/one-action-production-contract.md`, `references/master-command-v6.md`. Same split, three homes.
5. **7 slots / exactly 1 promotion / employee oversight:** in `references/production-policy-v33.json`, `references/production-contract-v33.md`, `references/smb-content-strategy-v32.md`, `references/monthly-weekly-social-os.md`, `references/system-architecture-v34.md`, `scripts/workflow_engine.py`, `scripts/validate_strategy_v33.py`, `scripts/content_engine.py`, `scripts/batch_guard_v45.py` (count only). Nine homes; the promotion-count check exists only in the disconnected validators, not in the canonical path (see dependency map §1.2).
6. **50-competitor target (15/10/10/10/5):** in `references/production-policy-v33.json`, `references/production-contract-v33.md`, `references/system-architecture-v34.md`, `scripts/competitor_monitor.py` (TARGET). Four homes; no populated dataset exists anywhere in the repo.
7. **"No live endpoints / NOT_CONFIGURED" statements:** in `references/endpoint-registry.json`, `references/integration-registry-v34.json`, `references/gate-contract-v41.md`, `references/unified-system-v42.md`, `references/release-audit-v34.md`, `references/chat-vision-audit-v35.md`, `skills/erudience/SKILL.md`, `README.md`. The registries are the machine-readable record; the prose repeats it. Recorded as documented-only, never as working (see dependency map §4).
8. **Repair cap 3 / 4th failure BLOCKED:** in `scripts/gate_chain_v41.py`, `scripts/chatgpt_bridge_v43.py`, `scripts/production_controller_v39.py`, `scripts/autonomous_pipeline_v40.py`, and prose in `references/gate-contract-v41.md`, `references/execution-state-machine-v39.md`, `references/autonomous-execution-v40.md`, `references/batch-production-v45.md`, `references/one-command-v44.md`, `references/master-action-v31.md`, `references/monthly-weekly-social-os.md`, `references/workflow-v3.md`, `references/orchestrator-v2.md`, `references/content-to-creative-brief-v21.md`, `references/production-contract-v33.md`. Consistent everywhere — a genuine invariant, not a conflict.

## 5. UNVERIFIED items (single-flag notes, not primary classifications)

- `references/brand-source-of-truth-v36.md`, `references/asset-and-font-policy.md`, `references/master-command-v6.md`, `references/one-action-production-contract.md` cite external repos (`bishal-paul-git/erudience-main`, `bishal-paul-git/erudience-social-os`), files (`src/index.css`, `tailwind.config.ts`, `src/assets/logo-horizontal.png`, `BRAND.md` v1.1), and a Supabase benchmark URL. None of these exist in this repo and none were fetched (read-only task, no network verification). Their claims about current website CSS/logo bytes are therefore UNVERIFIED from inside this repo.
- `references/brand-template-contract-v47.md` says the palette/fonts come from a "previously inspected repository; revalidate on website changes" — the revalidation has no record in the repo.
- `scripts/brand_render_v37.py` pins `brand_policy == 'social-os/BRAND.md:v1.1'`; no `BRAND.md` file exists anywhere in the repo listing, so the pin can never verify against repo contents.
- `README.md` test figures conflict (107 vs 112; hand count of test methods as read is 122 — see dependency map §2.6). Unresolved without running the suite.

## 6. Combined counts (references + scripts + root test file + manifests)

| Classification | References | Scripts | Root test + manifests | Total |
|---|---|---|---|---|
| EXACT_DUPLICATE | 0 | 0 | 0 | **0** |
| SEMANTIC_DUPLICATE | 0 | 0 | 0 | **0** |
| PARTIAL_DUPLICATE | 16 | 7 | 0 | **23** |
| UNIQUE | 8 | 20 | 3 (`tests_content_engine.py`, `.app.json`, `plugin.yaml`) | **31** |
| CONFLICTING_POLICY | 8 | 8 | 0 | **16** |
| COMPATIBILITY_REQUIRED | 0 | 0 | 4 (`plugin.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`) | **4** |
| HISTORICAL_UNIQUE | 4 | 0 | 0 | **4** |
| DISCONNECTED (primary) | 0 | 0 | 0 | **0** |
| UNVERIFIED (primary) | 0 | 0 | 0 | **0** |
| **Total** | **36** | **35** | **7** | **78** |

Headline: **no exact or semantic duplicates exist** among the 71 classified content files; the duplication is partial (23) and conflictual (16). The 16 CONFLICTING_POLICY files are the consolidation risk: 8 reference docs and 8 scripts assert incompatible brand/controller rules, and the repo's own "current policy" docs disagree with each other (`gate-contract-v41.md` states Inter/DM Sans/#10B981 while the code it documents enforces Sora/#10B77F; `owner-approved-brand-v46.md` claims to supersede logo-optional while `SKILL.md` + `brand-policy-current.md` declare logo-optional authoritative). Nothing in this draft resolves those conflicts.

## 7. Files read (complete) / not read

- Read: all 36 files under `references/`, all 35 files under `scripts/`, `tests_content_engine.py`, `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, plus (for context) `skills/erudience/SKILL.md`, `agents/roles-v34.md`, `README.md`, `reports/dependency-map.md`.
- **Files that could not be read:** none of the in-scope files. Not read by design: the binary logo `assets/erudience-owner-approved-logo-2026-11-21.jpg` (binary) and `.github/workflows/erudience-regression.yml` (outside the task's file list).
