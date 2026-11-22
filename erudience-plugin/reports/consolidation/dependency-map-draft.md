# Erudience Plugin — Dependency & Execution Map (DRAFT)

- **Repo:** `~/workspace/erudiance-plugin-work/ERUDIANCE/erudience-plugin/`
- **Baseline stated in task:** `main` merge commit `9e320fa60785f40142f37be9342b3df42fc47968` (v4.9.2, PR #1).
- **Baseline discrepancy (unresolved, not verified — no git commands were run):** the repo's own `reports/dependency-map.md` says its baseline is `main@c54e5b0`, and `README.md` says this copy is branch `maintenance/erudience-v4.9.2`, a release candidate "not yet merged to `main`". The task baseline commit could not be confirmed from file reads alone.
- **Method:** read-only file reads only. Every `.py` file under `scripts/` (35 files) and the root `tests_content_engine.py`, every file under `references/` (36 files), `skills/erudience/SKILL.md`, `agents/roles-v34.md`, `README.md`, `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and (as a cross-check only) `reports/dependency-map.md`. No commands were executed, so import behaviour and test results are reported from source inspection and from what `README.md` / `reports/` claim — they were **not** re-verified by running anything.
- **Files NOT read:** `.github/workflows/erudience-regression.yml` (outside the task's file list; its contents are quoted second-hand from `reports/dependency-map.md` below), the binary logo `assets/erudience-owner-approved-logo-2026-11-21.jpg` (binary; SHA-256 quoted from `README.md`, not recomputed), and `reports/` other than `dependency-map.md`.

## 1. Entry points and the SKILL.md execution paths

### 1.1 Declared entry point

`skills/erudience/SKILL.md` is the entry point (per `README.md` and the SKILL itself). It instructs the host/agent to:

1. Read `references/brand-policy-current.md` and `references/runtime-and-compatibility-v49.md` first; they supersede conflicting historical docs.
2. Read the only machine-readable brand settings from `references/production-policy-v33.json`.
3. Run command `erudiance_linkdin` (seven independent jobs) or `erudiance_linkdin --test --single-content ER-001` (exactly one).
4. Follow the 17 stages defined in `scripts/gate_chain_v41.py` — "the ONE canonical validation engine".
5. Treat `scripts/chatgpt_bridge_v43.py` and `scripts/batch_guard_v45.py` as orchestration adapters, not competing validators.
6. Treat `scripts/production_controller_v39.py` and `scripts/workflow_engine.py` as legacy only: "do not invoke as independent execution paths".

**Gap — the command string has no code implementation.** No script in `scripts/` parses `erudiance_linkdin`, `--test`, or `--single-content`. The string exists only in prose (`SKILL.md`, `references/one-command-v44.md`, `references/batch-production-v45.md`, `.codex-plugin/plugin.json` `defaultPrompt`). The closest executable equivalents are:

- `scripts/batch_guard_v45.py::initialise(root, topics, cycle)` — creates 7 jobs (manual Python call, no CLI).
- `scripts/chatgpt_bridge_v43.py` CLI — `start | next | submit | status` with `--state`, `--job`, `--stage`, `--adapter`, `--role`, `--receipt` (per-job, no 7-job or `--single-content` mode).

So the `erudiance_linkdin` command is **documented-only** as a command; its execution is manual host/ChatGPT-tool work driving the bridge CLI or Python functions.

### 1.2 The seven jobs

- `batch_guard_v45.py`: `SLOTS = 7`. `initialise()` requires exactly 7 distinct non-empty topics, creates `ER-{cycle}-{i:03d}` content IDs (`i` = 1..7), one `chatgpt_bridge_v43.start()` state file per job, plus `manifest.json`. `summary()` requires all 7 jobs `READY_FOR_OWNER_REVIEW` with 17 records each and 7 distinct verified 1080×1350 PNGs; anything else is `NOT_APPROVED` / `BLOCKED` / `IN_PROGRESS`.
- The "exactly one promotion" rule is **not** enforced by `batch_guard_v45.py` (it checks topic distinctness only). It is enforced by the disconnected validators: `workflow_engine.run()` (`EXACTLY_ONE_PROMOTION`), `validate_strategy_v33.validate()` (exactly one `promotion`), `content_engine.weekly_batch()`/`gate()` (via `validate_strategy`-style rules only in `validate_strategy_v33`; `content_engine` itself does not check promotion count). In the canonical 17-stage path there is no code that checks the promotion count — it would have to live in a STRATEGY/CONTENT adapter supplied by the host. **Classification: partially implemented** (rule exists in legacy validators, absent from the canonical path).
- `plugin.json` / `plugin.yaml` / `.app.json` descriptions all describe "seven-post" / "seven-content" workflow; no code wires the manifests to any script (manifests are host metadata only).

### 1.3 The 17 stages (canonical path)

`scripts/gate_chain_v41.py::STAGES` (in order):

```
SOURCES, SOURCE_REVIEW, RESEARCH, RESEARCH_REVIEW, STRATEGY, STRATEGY_REVIEW,
CONTENT, CONTENT_REVIEW, IMAGE_PLAN, PLAN_REVIEW, IMAGE_BUILD, TECH_REVIEW,
VISUAL_REVIEW, CONTENT_IMAGE_REVIEW, BRAND_REVIEW, FINAL_REVIEW, DELIVERY
```

- 9 stages end in `REVIEW` (`REVIEWS` set). Review stages require a reviewer-role adapter, `decision == 'PASS'`, non-empty `observations`, `subject_hash` matching the previous stage, and reviewer ≠ producer (`SELF_REVIEW_FORBIDDEN`).
- Every stage output must carry `upstream_hash` equal to the previous stage's hash (hash-chained lineage via `digest()` = SHA-256 of canonical JSON).
- Repair routing (`REPAIR` map): SOURCE_REVIEW→SOURCES, RESEARCH_REVIEW→RESEARCH, STRATEGY_REVIEW→STRATEGY, CONTENT_REVIEW→CONTENT, PLAN_REVIEW→IMAGE_PLAN, TECH_REVIEW/VISUAL_REVIEW/FINAL_REVIEW→IMAGE_BUILD, CONTENT_IMAGE_REVIEW/BRAND_REVIEW→IMAGE_PLAN; all other stages repair to themselves. Max 3 repairs (`limit=3` default); 4th failure → `BLOCKED`. Missing adapter → `BLOCKED` immediately.
- Terminal status: `READY_FOR_OWNER_REVIEW` (live mode) or `TEST_FIXTURE_PASS` (only when `job['mode'] == 'TEST_FIXTURE'`).
- Live-mode-only checks (skipped in `TEST_FIXTURE` mode): reviewer `inspection_evidence_path` must exist on disk with matching SHA-256; SOURCES must have `source_sha256` and `verified_at != 'fixture-only'`; IMAGE_BUILD must have a verified on-disk Sora font binary (`font_provenance[BRAND['heading']]`).
- IMAGE_PLAN checks: `content_id` match, `content_hash` == CONTENT hash, caption/topic match, `poster_text` headline + footer present, `dimensions == [1080, 1350]`, `brand == BRAND` (from `production-policy-v33.json`), `design_rationale` + `negative_constraints`, `logo_asset` in `(None, APPROVED_LOGO)`, `template_id` + `positioning` + `funnel_stage`.
- IMAGE_BUILD checks: `plan_hash` match, image file exists with matching SHA-256, PNG 1080×1350 RGB/RGBA, `copy_ledger_hash == digest(poster_text)`, font provenance present, logo present ⟺ planned (hash-checked against the bundled logo file) or absent ⟺ absent, `copy_rendered is True`.
- BRAND_REVIEW checks: `font_files_checked`, `palette_checked`, `footer_checked`, `original_logo_checked` (if logo planned) else `logo_absence_checked`, `positioning_checked`.
- DELIVERY requires all 16 prior stages present and image SHA match.
- **No publishing, no network calls, no side effects** — the module docstring and code confirm this; `external_writes` is always 0.
- **Adapters are not included.** `Chain(job, adapters)` requires the caller to supply one executable `Adapter(name, fn, role)` per stage. There is no research adapter, writer adapter, image-generation adapter, or visual-reviewer adapter anywhere in the repo. In live mode the chain BLOCKEDs on the first stage with no adapter (`test_gate_chain_v41.py::test_non_fixture_never_claims_live_without_adapters` asserts exactly this).

### 1.4 The bridge and batch adapters

- `scripts/chatgpt_bridge_v43.py` — durable checkpoint version of the same 17-stage chain for ChatGPT-tool execution. CLI: `start` (creates state file, refuses if it exists), `next` (returns current stage + upstream/content/plan/image hashes), `submit` (validates a receipt by reusing `Chain.verify()` with a throwaway `Chain(job, {}, limit=3)` whose `records` are replaced with the persisted records), `status`. State schema `erudience.chatgpt.v4.3`. Tools execute **outside** this process; the bridge only validates receipts submitted back. Same 3-repair cap, same terminal statuses. Imports: `gate_chain_v41` (`STAGES, REPAIR, Adapter, Chain, digest, GateFailure`).
- `scripts/batch_guard_v45.py` — 7-job wrapper over the bridge (`from chatgpt_bridge_v43 import start, load, next_step`). No CLI (`__main__` guard absent — it is import-only). Imports Pillow to verify each ready job's PNG is 1080×1350.
- Import chain (the only production import chain): `gate_chain_v41.py` ← `chatgpt_bridge_v43.py` ← `batch_guard_v45.py`. Plus `keyword_research.py` ← `linkedin_seo_validator.py`, and `website_brand_v38.py` ← `website_render_v38.py`. No circular imports (consistent with `reports/dependency-map.md`).
- `scripts/` has no `__init__.py`; cross-module imports resolve only when run from `scripts/` or with `sys.path` insertion (tests do `sys.path.insert(0, str(Path(__file__).parent))` or rely on CWD). `chatgpt_bridge_v43.py` and `batch_guard_v45.py` use bare `from gate_chain_v41 import ...` / `from chatgpt_bridge_v43 import ...`, so they fail to import when invoked from any other working directory without `sys.path` manipulation. **Environment-dependent.**

### 1.5 Legacy / competing execution paths (all disconnected from the canonical path)

| Path | Stages | Entry | Status per SKILL.md / runtime docs |
|---|---|---|---|
| `production_controller_v39.py` | 13: SOURCES, RESEARCH, STRATEGY, CONTENT, CONTENT_QA, BRIEF, BRIEF_QA, RENDER, TECH_QA, VISUAL_QA, CONTENT_MATCH_QA, BRAND_QA, DELIVERY | CLI `init/pass/fail/status`, atomic JSON state | Legacy only; do not invoke as independent path |
| `autonomous_pipeline_v40.py` | 13 (same stage names as v39) | `Controller(job, adapters).run()` (import-only, no CLI) | Superseded; "only supported" per its own doc v4.0, now historical |
| `workflow_engine.py` | 10: RESEARCH, KEYWORDS, STRATEGY, DRAFT, FACT_QA, SEO_QA, CREATIVE, VISUAL_QA, OWNER_APPROVAL, DELIVERY | `run(batch, receipts, approval, external_write)` (import-only) | Legacy; 7-slot batch validator |
| `content_engine.py` | 10: RESEARCH, EVIDENCE, CONTENT, CREATIVE_BRIEF, PROMPT, BRAND, RENDER, QA, OWNER_APPROVAL, SOCIAL_OS | CLI `--mode gate/calendar/weekly` | Disconnected; separate stage vocabulary |
| `production_gate.py` | 9: RESEARCH, KEYWORDS, STRATEGY, DRAFT, FACT_QA, SEO_QA, BRAND_QA, CREATIVE, VISUAL_QA | `validate(job, receipts, brand, root)` (import-only) | Disconnected receipt validator |
| `master-action-v31` / `workflow-v3` / `one-action-production-contract` (docs) | 20-action registry / 16-step pipeline / 15-stage state machine | Prose only, no code | Documented-only execution models |

The 13-stage vs 17-stage vs 10-stage vs 9-stage counts are **conflicting**, not complementary: the same job cannot traverse all of them, and the docs disagree about which is authoritative for a given version (v39 doc says v39 is authoritative; v40 doc says v40 is "the only supported" API; v41/SKILL.md say v41 is the one canonical engine; v42/v49 docs say v39/v40 are archived compatibility code). See duplicate-classification draft for the full conflict record. Do not silently resolve.

## 2. Per-script dependency table

Legend for "Called by": `canonical` = in the `gate_chain ← bridge ← batch_guard` chain; `test-only` = imported only by a test file; `CLI` = has `__main__`/argparse entry, no in-repo caller; `none` = no caller found in the repo.

### 2.1 Canonical and connected scripts

| Script | Imports (plugin / stdlib / 3rd-party) | Defines | Called by | Calls | Config / asset refs | Test file |
|---|---|---|---|---|---|---|
| `gate_chain_v41.py` | stdlib: `dataclasses, pathlib, hashlib, json, re`; Pillow `Image` | `STAGES, REVIEWS, REPAIR, POLICY, BRAND, APPROVED_LOGO, GateFailure, digest, filehash, require, Adapter, Chain` (`Chain.__init__/verify/run`) | `chatgpt_bridge_v43` (import); tests | Reads `references/production-policy-v33.json` **at import** (`_policy()`); reads bundled logo file at IMAGE_BUILD when a plan carries `logo_asset`; reads inspection-evidence files + font binaries in live mode | `production-policy-v33.json` (`brand`, `brand_assets.approved_logo_path` = `assets/erudience-owner-approved-logo-2026-11-21.jpg`) | `test_gate_chain_v41.py` (10 tests), `test_brand_policy_v49.py` (5 tests, exercises `Chain.verify` brand rules) |
| `chatgpt_bridge_v43.py` | `gate_chain_v41`; stdlib `argparse, json, os, tempfile, pathlib, hashlib` | `save, load, start, next_step, submit, main` | `batch_guard_v45` (import); CLI use | `Chain.verify` (via throwaway `Chain`); `digest` | State JSON files it creates (`schema: erudience.chatgpt.v4.3`) | `test_chatgpt_bridge_v43.py` (7 tests) |
| `batch_guard_v45.py` | `chatgpt_bridge_v43`; stdlib `pathlib, json`; Pillow `Image` | `SLOTS=7, initialise, summary` | Tests only (no production caller; no CLI) | `chatgpt_bridge_v43.start/load/next_step` | `manifest.json` + per-job state files under caller-supplied root | `test_batch_guard_v45.py` (5 tests) |

### 2.2 Renderers (all disconnected from the canonical path — no adapter in `gate_chain_v41` calls them)

| Script | Imports | Defines | Called by | Calls | Config / asset refs | Test file |
|---|---|---|---|---|---|---|
| `brand_render_v37.py` | stdlib `argparse, hashlib, json, pathlib`; Pillow | `COLORS` (#10B981 emerald), `sha, verify_assets, render` | CLI only (`--spec --output`) | — | Spec-supplied logo + Sora font files (path + SHA-256 + `source`); pins `brand_policy == 'social-os/BRAND.md:v1.1'` — **no such file exists in the repo** | `test_brand_render_v37.py` (4 tests, failure paths only — no successful render test) |
| `render_poster.py` | stdlib `argparse, pathlib, hashlib, json, sys`; Pillow | `W,H=1080,1350`, palette consts (#10B981), `STAGES` (6 fixed cards), `font, fit, drawfit, main` | CLI only (`--inter-bold --inter-semibold --dm-regular --dm-medium --brief --logo --output [--review-draft]`) | — | Inter/DM Sans font files (required CLI args); genuine logo PNG (required unless `--review-draft`); brief JSON (schema = `references/brief-schema-example.json`) | **No test file** |
| `website_render_v38.py` | `website_brand_v38` (`PALETTE`); stdlib `argparse, hashlib, json, pathlib`; Pillow | `sha, render` | CLI only (`--spec --output`) | `website_brand_v38.PALETTE` | Spec-supplied Inter/DM Sans font files (+ SHA-256), optional logo (+ SHA-256 + `logo_source`) | **No test file** |

Note the three renderers are mutually incompatible: `brand_render_v37` = Sora, 3–5 steps, logo mandatory; `render_poster` = Inter/DM Sans, exactly 6 cards, logo mandatory unless review-draft; `website_render_v38` = Inter/DM Sans, 3–5 steps, logo optional. None is invoked by the canonical chain; the IMAGE_BUILD adapter that would call one of them does not exist in the repo.

### 2.3 Brand-policy validators (all disconnected from the canonical path)

| Script | Imports | Defines | Called by | Calls | Config / asset refs | Test file |
|---|---|---|---|---|---|---|
| `brand_policy_v36.py` | stdlib `re` only | `ALLOWED_HASHTAGS, BANNED, PALETTE` (#10B981), `check_caption, check_poster_spec` | Tests only | — | `check_poster_spec` requires `font_family == 'Sora'`, `palette == PALETTE`, `authentic_logo_sha256`, `logo_source_commit`, `visual_inspection_receipt`, `orchestrator_execution_id` | `test_brand_policy_v36.py` (7 tests) |
| `website_brand_v38.py` | stdlib `re` only | `PALETTE` (#10B981), `HASHTAGS, BANNED, check, check_caption` | `website_render_v38` (import); tests | — | Requires Inter/DM Sans, `font_heading_sha256` + `font_body_sha256`, optional logo with provenance | `test_website_brand_v38.py` (5 tests) |

`gate_chain_v41` does **not** import either validator; its brand checks are inline in `Chain.verify` against `production-policy-v33.json` (Sora / #10B77F / logo optional). `brand_policy_v36` and `website_brand_v38` duplicate the caption rules (same 3 hashtags, same 7 banned words) but disagree on fonts/emerald/logo-required — see duplicate-classification draft.

### 2.4 Legacy controllers (disconnected, competing)

| Script | Imports | Defines | Called by | Calls | Config / asset refs | Test file |
|---|---|---|---|---|---|---|
| `production_controller_v39.py` | stdlib `argparse, hashlib, json, os, tempfile, pathlib`; Pillow imported lazily inside `commit` (TECH_QA) | `STAGES` (13), `REVIEW_STAGES, REPAIR_TARGET, MAX_REVISIONS=3, GateError, canonical, digest, initial, commit, fail, save, main` | CLI only (`init/status/pass/fail`) | — | Own JSON state files (atomic replace); `BRIEF` requires `brand_profile_version`; `BRAND_QA` requires `website_brand_verified is True` | `test_production_controller_v39.py` (14 tests) |
| `autonomous_pipeline_v40.py` | stdlib `hashlib, json, os, re, pathlib, dataclasses`; Pillow lazily in `Controller._check` (TECH_QA) | `STAGES` (13), `REPAIR, REVIEWS, PALETTE` (#10B981), `PipelineError, StageFailure, hashobj, sha, norm, assert_true, Adapter, Controller, deterministic_content_match, deterministic_brand_check` | Tests only (no CLI, no production caller) | — | Hardcodes `brand_profile == 'website-v38'`, `heading_font == 'Inter'`, `body_font == 'DM Sans'`, `PALETTE` — **does not read `production-policy-v33.json`** | `test_autonomous_pipeline_v40.py` (12 tests) |
| `workflow_engine.py` | stdlib `hashlib, json` | `STAGES` (10), `WorkflowError, run` | `integration_tests.py` only | — | None (pure function on caller-supplied batch + receipts) | `integration_tests.py` (4 of its 14 tests exercise `run`) |

### 2.5 Supporting / validation modules (disconnected except test edges)

| Script | Imports | Defines | Called by | Calls | Config / asset refs | Test file |
|---|---|---|---|---|---|---|
| `content_engine.py` | stdlib `argparse, hashlib, json, re, datetime, pathlib` | `CATEGORIES, FORMATS, PLATFORMS, STAGES` (10, different vocabulary), `REQUIRED, GateError, sha, validate, route, gate, calendar, weekly_batch, main` | CLI only (`--mode gate/calendar/weekly`); root `tests_content_engine.py` | — | None | `tests_content_engine.py` at plugin root (10 tests) |
| `keyword_research.py` | stdlib `re` | `TYPES (15), INTENTS (4), normalize, validate_cluster, map_content` | `linkedin_seo_validator` (import); `integration_tests.py` | — | None | `integration_tests.py` (3 tests) |
| `linkedin_seo_validator.py` | `keyword_research` (`validate_cluster, normalize`) | `review` | `integration_tests.py` only | `keyword_research.validate_cluster` | None | `integration_tests.py` (2 tests) |
| `competitor_monitor.py` | stdlib `datetime` | `TARGET` (15/10/10/10/5 = 50), `audit` | `integration_tests.py` only | — | None (operates on caller-supplied records) | `integration_tests.py` (2 tests) |
| `linkedin_analytics.py` | (none) | `summarize` | `integration_tests.py` only | — | None (operates on caller-supplied observed rows) | `integration_tests.py` (2 tests) |
| `evidence_store.py` | stdlib `sqlite3, json, hashlib, datetime, pathlib, argparse` | `SCHEMA, now, sha, init, evidence, gate, can_handoff` | **None** (no caller, no test) | — | Own SQLite DB file (caller-supplied path) | **No test file** |
| `batch_gate.py` | stdlib `hashlib, json, sys` | `digest, validate_batch` | CLI only (`sys.argv[1]` manifest path) | — | Caller-supplied batch manifest JSON | **No test file** |
| `brief_prompt_gate.py` | stdlib `argparse, hashlib, json, sys, pathlib` | `sha, validate, main` | CLI only (`brief prompt [--output]`) | — | Caller-supplied brief + prompt JSON | **No test file** |
| `production_gate.py` | stdlib `hashlib, json, re, pathlib` | `STAGES` (9), `digest, validate` | Tests only | — | Caller-supplied receipts + brand dict; verifies artifact files under caller-supplied root (with path-escape check) | `test_production_gate.py` (6 tests) |
| `validate_strategy_v33.py` | stdlib `json, sys, pathlib`; reads `references/production-policy-v33.json` at import into `P` | `validate` | CLI only (`sys.argv[1]` batch JSON) | — | Reads policy JSON at import but **`validate()` never references `P`** (dead config load — also noted in `reports/dependency-map.md`) | `test_strategy_v33.py` (8 tests) |
| `verify_output.py` | stdlib `argparse, json, hashlib, pathlib, sys`; Pillow | `check, main` | CLI only (`png [--require-logo]`) | — | PNG + sibling `.json` manifest (SHA-256 + `locked_stage_names` == the 6 Warm Enquiry stages) | `test_verify_output.py` (5 tests; v4.9.2 import-safety fix) |

### 2.6 Test files (13 in `scripts/` + 1 at root)

| Test file | Imports (plugin modules) | Covers |
|---|---|---|
| `test_gate_chain_v41.py` | `gate_chain_v41` | 17-stage fixture run, repair routing, retry exhaustion, reviewer role, live-mode block without adapters |
| `test_chatgpt_bridge_v43.py` | `chatgpt_bridge_v43` | start/next/submit, out-of-order, retries, reviewer receipt, persistence |
| `test_batch_guard_v45.py` | `batch_guard_v45`, `gate_chain_v41` | 7 distinct topics, no re-init, portrait-only, wrong content ID |
| `test_brand_policy_v49.py` | `gate_chain_v41` | Sora-only brand, logo optional/allowed/rejected, headline required |
| `test_brand_policy_v36.py` | `brand_policy_v36` | Caption, banned words, hashtags, Sora, logo provenance, orchestrator, visual QA |
| `test_brand_render_v37.py` | `brand_render_v37` | Empty assets, palette, policy pin, no output on failure (no successful-render test) |
| `test_production_controller_v39.py` | `production_controller_v39` | Order, source fail-closed, repair, reviewer, brief/render binding, revisions, delivery |
| `test_autonomous_pipeline_v40.py` | `autonomous_pipeline_v40` | Full 13-stage fixture, repair routing, self-review, brand violation, logo omission |
| `test_production_gate.py` | `production_gate` | Missing/fake receipts, self-review, unauthorized publish, path escape, uninspected image |
| `test_strategy_v33.py` | `validate_strategy_v33` | Promotion count, no deletion, employee requirement, pitch, image proof, write, unsupported claim |
| `test_verify_output.py` | `verify_output` (import + subprocess CLI) | Import safety, valid PNG pass, `--require-logo`, missing PNG, wrong dimensions |
| `test_website_brand_v38.py` | `website_brand_v38` | Logo optional, wrong fonts, missing identity, fake logo, missing inspection |
| `integration_tests.py` | `keyword_research, linkedin_seo_validator, competitor_monitor, linkedin_analytics, workflow_engine` | Cross-module contracts + negative cases (14 tests; filename does not start with `test_`, so `unittest discover -p 'test_*.py'` does not pick it up — per `reports/dependency-map.md`, CI runs it explicitly) |
| `tests_content_engine.py` (plugin root) | `content_engine` | gate/calendar/weekly_batch (10 tests) |

**Test-count discrepancy inside the repo (unresolved, not re-verified):** `README.md` "Testing" section says "107 tests passed … 83 in `scripts/test_*.py`, 10 in `tests_content_engine.py`, 14 in `scripts/integration_tests.py`", while its "Version history" says "112/112 tests passing". Counting test methods as read: 10 + 7 + 5 + 5 + 7 + 4 + 14 + 12 + 6 + 8 + 5 + 5 = 98 in `scripts/test_*.py`, + 10 + 14 = 122 total methods as read (method counts by inspection, not by execution). Neither README figure matches a hand count, and nothing was executed to settle it. Treat all three numbers as **unverified**.

**Modules with no test at all:** `evidence_store.py`, `batch_gate.py`, `brief_prompt_gate.py`, `website_render_v38.py`, `render_poster.py` (consistent with `reports/dependency-map.md`).

## 3. Config / asset / manifest references

| File | Version / content | Referenced by |
|---|---|---|
| `plugin.json` | v4.9.2, "…Sora typography, verified brand policy and optional authentic logo." | Host manifest; byte-identical to `.agent-plugin/plugin.json` and `.claude-plugin/plugin.json` |
| `.agent-plugin/plugin.json` | Byte-identical to `plugin.json` (per read; see duplicate-classification draft) | Host mirror |
| `.claude-plugin/plugin.json` | Byte-identical to `plugin.json` (per read) | Host mirror |
| `.codex-plugin/plugin.json` | v4.9.2, same description + extra `interface` (displayName, short/long description, developerName, category, capabilities `[]`, `defaultPrompt: "erudiance_linkdin"`) + `author` (Erudience, contact@erudience.com) | Host mirror, **not** byte-identical |
| `.app.json` | v4.9.2, different description ("…owner-approved original logo and brand palette.") | App manifest |
| `plugin.yaml` | v4.9.2, lists `skills: [skills/erudience/SKILL.md]` | Host manifest |
| `references/production-policy-v33.json` | v3.3.0; 14 modules; 7 planning slots; 1 promotion; 50-competitor target (15/10/10/10/5); `brand.heading/body: Sora`, emerald `#10B77F`, `brand_assets.approved_logo_path: assets/erudience-owner-approved-logo-2026-11-21.jpg`, `logo_optional: true`, `generated_logos_allowed: false`; timezone Asia/Dhaka; monthly cycle start day 21 | Read at import by `gate_chain_v41.py` (live) and `validate_strategy_v33.py` (dead load); cited as authoritative by `SKILL.md`, `brand-policy-current.md`, `README.md` |
| `assets/erudience-owner-approved-logo-2026-11-21.jpg` | Owner-approved logo; SHA-256 quoted in `README.md` as `58fe87fa…e40226` (not recomputed — no commands run) | Hash-checked by `gate_chain_v41.py` at IMAGE_BUILD when a plan carries `logo_asset` |
| `references/endpoint-registry.json` | v3.0.0; openai/anthropic/GSC `DOCUMENTED_PROVIDER_API_NOT_CONNECTED`; linkedin `REQUIRES_APPROVED_API_PRODUCT_AND_SCOPE`; social_os `UNVERIFIED_INTEGRATION`; research `CONNECT_AUTHORIZED_RESEARCH_PROVIDER`; image_renderer `LOCAL_SCRIPT_OR_AUTHORIZED_IMAGE_TOOL` | Referenced by `master-action-v31.md`, `workflow-v3.md`, `unified-system-v42.md`; **no code reads it** |
| `references/integration-registry-v34.json` | v3.4.0; all six integrations `NOT_CONFIGURED` (linkedin, supabase, research, image_renderer, scheduler, analytics); stages = the 10 `workflow_engine` stages | **No code reads it** |
| `references/brief-schema-example.json` | Warm Enquiry 6-stage brief (CAPTURE…OUTCOME) | Matches `render_poster.py` defaults and `verify_output.py` `locked_stage_names`; no code reads it |
| `agents/roles-v34.md` | 18 specialist roles with input/output/gate; non-negotiables (no fabrication, no secrets, independent review) | Referenced by `references/system-architecture-v34.md`; **no code maps roles to adapters** |
| `.github/workflows/erudience-regression.yml` | Not read (outside task scope). `reports/dependency-map.md` describes it as: on push touching `erudience-plugin/**`, Python 3.11, `pip install Pillow`, `compileall`, `unittest discover -s scripts -p 'test_*.py'`, `unittest tests_content_engine`, `scripts/integration_tests.py -v` | CI only |

**Third-party dependencies:** Pillow only (per `README.md`; no `requirements.txt`/`pyproject.toml` in the repo listing). Everything else is Python standard library (`sqlite3` in `evidence_store.py` only). No network libraries, no provider SDKs — consistent with `reports/dependency-map.md`.

**Fonts are not bundled.** Sora / Inter / DM Sans must be supplied as installed paths at render time; renderers fail closed without them (`README.md`, `brand_render_v37.verify_assets`, `website_render_v38.render`, `render_poster.font`). No font file exists in the repo listing.

## 4. Capability classification

Definitions: **implemented+connected** = code exists and is reachable from the canonical path (SKILL.md → gate_chain/bridge/batch_guard) or from a live caller; **implemented but disconnected** = code exists, tested or not, but no production caller; **documented only** = described in docs/registries with no code; **partially implemented** = code covers part of the documented behaviour; **conflicting** = two or more live code/docs paths implement incompatible versions; **environment-dependent** = works only given host tools, fonts, credentials, or CWD; **unavailable historical source** = references a repo/file/endpoint that is not in this repo and was not verified here.

| # | Capability | Classification | Evidence |
|---|---|---|---|
| 1 | 17-stage fail-closed gate (`gate_chain_v41`) | Implemented+connected | `Chain.verify/run` full logic; imported by bridge; tested (fixture mode) |
| 2 | Durable ChatGPT checkpoint bridge (`chatgpt_bridge_v43`) | Implemented+connected (logic); environment-dependent (execution) | Imports `gate_chain_v41`; CLI works; but stage execution happens in ChatGPT tools outside the process — no code invokes them |
| 3 | 7-job batch guard (`batch_guard_v45`) | Implemented+connected (logic); environment-dependent (invocation) | Imports bridge; no CLI; must be called from Python by the host |
| 4 | `erudiance_linkdin` command incl. `--test --single-content` | Documented only | No parser for it anywhere; see §1.1 |
| 5 | Seven jobs, exactly one promotion | Partially implemented | Batch count enforced by `batch_guard_v45`; promotion count enforced only by disconnected `workflow_engine` / `validate_strategy_v33`, not in the canonical path |
| 6 | Research / writer / planner adapters (live) | Documented only | `Chain` requires caller-supplied adapters; none exist in repo |
| 7 | Image generation / IMAGE_BUILD adapter (live) | Documented only | No adapter; the three renderers exist but are not wired to the chain |
| 8 | Independent visual reviewer adapter (live) | Documented only | Live mode requires an `inspection_evidence_path` file; no reviewer code produces one |
| 9 | Deterministic poster rendering | Implemented but disconnected + conflicting | Three renderers exist (`brand_render_v37`, `render_poster`, `website_render_v38`), CLI-only, mutually incompatible brand specs |
| 10 | Brand policy enforcement (canonical: Sora / #10B77F / logo optional) | Implemented+connected (in `gate_chain_v41` only); conflicting elsewhere | `brand_policy_v36` (#10B981, logo-required), `website_brand_v38` (Inter/DM Sans, #10B981), `autonomous_pipeline_v40` (hardcoded Inter/DM Sans/#10B981) disagree |
| 11 | Legacy 13-stage controllers (v39 CLI, v40 API) | Implemented but disconnected + conflicting | Both fully coded and tested; SKILL.md/runtime docs say do not invoke; v40 doc once claimed it was "the only supported" API |
| 12 | 10-stage batch workflow (`workflow_engine`) | Implemented but disconnected + conflicting | Tested via integration tests only; stage list differs from 13- and 17-stage paths |
| 13 | Content engine (validate/route/gate/calendar/weekly_batch) | Implemented but disconnected | CLI + root tests; its 10-stage vocabulary matches nothing else |
| 14 | Keyword research + LinkedIn SEO validation | Implemented but disconnected (test-only edge) | `keyword_research` ← `linkedin_seo_validator` ← `integration_tests` only; no production caller |
| 15 | Competitor monitoring (50-target audit) | Implemented but disconnected (test-only edge) | `competitor_monitor.audit` only exercised by integration tests; no dataset in repo; target is policy, not populated data |
| 16 | LinkedIn analytics (descriptive metrics) | Implemented but disconnected (test-only edge) | `linkedin_analytics.summarize` only exercised by integration tests; needs caller-supplied observed rows |
| 17 | Evidence ledger / owner approval + write authorisation (`evidence_store`) | Implemented but disconnected | Only module modelling separate `APPROVE` + `WRITE_AUTHORISE`; no caller, no test |
| 18 | Batch structural gate (`batch_gate`) | Implemented but disconnected | CLI only; overlaps `content_engine.weekly_batch` and `batch_guard_v45.summary` |
| 19 | Brief↔prompt structural gate (`brief_prompt_gate`) | Implemented but disconnected | CLI only; no test; no caller |
| 20 | Production receipt gate (`production_gate`) | Implemented but disconnected | Tested; no caller; 9-stage vocabulary |
| 21 | Strategy validation (`validate_strategy_v33`) | Implemented but disconnected | CLI + tests; reads policy JSON at import without using it |
| 22 | Mechanical PNG gate (`verify_output`) | Implemented but disconnected | CLI + tests; checks dimensions/mode/size/manifest; explicitly "cannot certify visual quality or logo provenance" |
| 23 | LinkedIn publishing / scheduling | Documented only | No code; endpoint-registry says `REQUIRES_APPROVED_API_PRODUCT_AND_SCOPE`; SKILL.md forbids publishing |
| 24 | Social OS draft/upload/read-back | Documented only | No code, no connector; endpoint-registry `UNVERIFIED_INTEGRATION`; integration-registry `NOT_CONFIGURED` |
| 25 | Supabase integration | Documented only (NOT_CONFIGURED) | integration-registry `NOT_CONFIGURED`; no code, no schema in repo |
| 26 | Scheduler / weekly autonomous execution | Documented only (NOT_CONFIGURED) | integration-registry `NOT_CONFIGURED`; SKILL.md: "Do not claim autonomous weekly research if execution or persistence is not configured"; batch-production-v45: "no autonomous background scheduling" |
| 27 | OpenAI / Anthropic / Google Search Console | Documented only (NOT_CONFIGURED) | endpoint-registry `DOCUMENTED_PROVIDER_API_NOT_CONNECTED`; integration-registry has no such entries; no SDKs, no credentials in repo |
| 28 | Research provider (live source fetching) | Documented only (NOT_CONFIGURED) | endpoint-registry `CONNECT_AUTHORIZED_RESEARCH_PROVIDER`; `content_engine`/`gate_chain` accept caller-supplied URLs but never fetch them |
| 29 | Weekly research refresh (first-run-of-week, previous/current values) | Documented only | `brand-policy-current.md` prescribes it; no code implements it; SKILL.md says mark NOT_CONFIGURED if unconfigured |
| 30 | 18 specialist roles (`agents/roles-v34.md`) | Documented only | Role table only; no code maps roles to adapters; `system-architecture-v34.md` repeats the same 18 roles |
| 31 | Monthly 30-day planning / 21st cycle anchor | Partially implemented | `content_engine.calendar()` implements a date grid; monthly strategy content is prose only (`monthly-weekly-social-os.md`, `smb-content-strategy-v32.md`, `strategy-playbook.md`) |
| 32 | Owner approval before delivery/publication | Partially implemented | Terminal status is `READY_FOR_OWNER_REVIEW` everywhere; `evidence_store.can_handoff` models approval + separate write authorisation but is disconnected; no approval UI/code path |
| 33 | Website brand profile (Inter/DM Sans/#10B981) | Conflicting | `website_brand_v38` + `website_render_v38` + `owner-approved-brand-v46` + `brand-template-contract-v47` vs canonical Sora/#10B77F; `unified-system-v42` once declared website-first canonical, `SKILL.md`/v49 now declare Sora canonical — unresolved |
| 34 | Logo-required vs logo-optional | Conflicting | Current: logo optional (`production-policy-v33.json`, `SKILL.md`, `gate_chain_v41`); v46/v47/website-profile: owner "requires" logo on new posters; `brand_render_v37`/`render_poster`: logo mandatory for final output |
| 35 | Historical sources (website repo `erudience-main` CSS/logo paths, Social OS `BRAND.md` v1.1, Supabase benchmark URL, `social.erudience.com`) | Unavailable historical source | Referenced by many docs (`brand-source-of-truth-v36`, `asset-and-font-policy`, `master-command-v6`, `one-action-production-contract`); none of these files/URLs exist in this repo and none were fetched (read-only task, no network verification) |
| 36 | 13-stage vs 17-stage stage counts | Conflicting | See §1.5; three live stage vocabularies + two more in docs (15-stage one-action machine, 20-action master registry) |

### Counts per connection status (capabilities, §4 table, 36 rows — single primary label per row)

| Status | Count | Rows |
|---|---|---|
| Implemented+connected | 1 | 1 |
| Implemented+connected (logic) / environment-dependent (execution) | 2 | 2, 3 |
| Implemented but disconnected | 10 | 13–22 |
| Documented only | 12 | 4, 6, 7, 8, 23–30 |
| Partially implemented | 3 | 5, 31, 32 |
| Conflicting | 7 | 9, 10, 11, 12, 33, 34, 36 |
| Unavailable historical source | 1 | 35 |
| **Total** | **36** | |

Secondary labels (not double-counted above): rows 9, 11, 12 are also disconnected; rows 2, 3 are also environment-dependent (host tools / no CLI / CWD-dependent imports, §1.4); row 10 is connected only inside `gate_chain_v41.py` and conflicting everywhere else.

### Live integrations — explicit record

Per the task instruction and the registries as read: **all live integrations are NOT_CONFIGURED and are recorded here as documented-only, never as working.** `references/integration-registry-v34.json`: linkedin, supabase, research, image_renderer, scheduler, analytics — all `"state": "NOT_CONFIGURED"`. `references/endpoint-registry.json`: openai, anthropic, google_search_console — `DOCUMENTED_PROVIDER_API_NOT_CONNECTED`; linkedin — `REQUIRES_APPROVED_API_PRODUCT_AND_SCOPE`; social_os — `UNVERIFIED_INTEGRATION`; research — `CONNECT_AUTHORIZED_RESEARCH_PROVIDER`; image_renderer — `LOCAL_SCRIPT_OR_AUTHORIZED_IMAGE_TOOL`. No code in the repo reads either registry file.

## 5. What this map does NOT establish

- Whether the test suite passes (nothing was executed; README's 107 vs 112 figures conflict — see §2.6).
- Whether the bundled logo bytes match the quoted SHA-256 (not recomputed).
- Whether any external URL/repo cited in the docs is live (nothing was fetched).
- Which brand policy is "really" current beyond what the files say: `SKILL.md` + `brand-policy-current.md` + `runtime-and-compatibility-v49.md` declare Sora/#10B77F/logo-optional authoritative, but `owner-approved-brand-v46.md` (dated 2026-11-21, "overrides any conflicting logo-optional … instructions") and `brand-template-contract-v47.md` (v4.7, "supersede legacy logo-optional, Sora-only") claim the opposite, and `gate-contract-v41.md` itself states Inter/DM Sans/#10B981. This is a genuine unresolved conflict, recorded in the duplicate-classification draft as CONFLICTING_POLICY, not resolved here.
- The task baseline commit `9e320fa…` vs the repo's own `main@c54e5b0` claim (§ header).

## 6. Files read (complete)

- Scripts (35): `autonomous_pipeline_v40.py`, `batch_gate.py`, `batch_guard_v45.py`, `brand_policy_v36.py`, `brand_render_v37.py`, `brief_prompt_gate.py`, `chatgpt_bridge_v43.py`, `competitor_monitor.py`, `content_engine.py`, `evidence_store.py`, `gate_chain_v41.py`, `integration_tests.py`, `keyword_research.py`, `linkedin_analytics.py`, `linkedin_seo_validator.py`, `production_controller_v39.py`, `production_gate.py`, `render_poster.py`, `test_autonomous_pipeline_v40.py`, `test_batch_guard_v45.py`, `test_brand_policy_v36.py`, `test_brand_policy_v49.py`, `test_brand_render_v37.py`, `test_chatgpt_bridge_v43.py`, `test_gate_chain_v41.py`, `test_production_controller_v39.py`, `test_production_gate.py`, `test_strategy_v33.py`, `test_verify_output.py`, `test_website_brand_v38.py`, `validate_strategy_v33.py`, `verify_output.py`, `website_brand_v38.py`, `website_render_v38.py`, `workflow_engine.py`. (Task brief said 36 scripts; the directory listing contains 35. The root `tests_content_engine.py` is a 36th Python test file but lives outside `scripts/`.)
- References (36): all files listed in §7 of the duplicate-classification draft. (Task brief said 35 references; the directory listing contains 36.)
- Other: `skills/erudience/SKILL.md`, `agents/roles-v34.md`, `README.md`, `plugin.json`, `plugin.yaml`, `.app.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `reports/dependency-map.md` (cross-check only).
- **Files that could not be read:** none of the in-scope files. Not read by design (out of scope / binary): `.github/workflows/erudience-regression.yml`, `assets/erudience-owner-approved-logo-2026-11-21.jpg` (binary, not text-readable).
