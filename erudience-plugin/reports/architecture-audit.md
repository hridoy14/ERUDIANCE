# Erudience Plugin — Architecture Audit (v4.9.2)

- Repo: `hridoy14/ERUDIANCE`, baseline `main@c54e5b0`; working branch `maintenance/erudience-v4.9.2`.
- Audit date: 2026-11-22. Method: read-only file inspection + actual test execution (see `reports/regression-results.md`). No Python was executed for the audit itself except the regression/E2E runs.
- Entry point: `skills/erudience/SKILL.md` (command `erudiance_linkdin`; `--test --single-content ER-001` runs exactly one job).

## 1. Canonical system

| Component | Role | Evidence |
|---|---|---|
| `scripts/gate_chain_v41.py` | **The one canonical 17-stage fail-closed validator.** `STAGES`, `REVIEWS`, `REPAIR`, `GateFailure`, `Adapter`, `Chain.verify()/run()`, `digest()`, `filehash()`. Loads brand from `references/production-policy-v33.json` at import. | SKILL.md: "the ONE canonical validation engine, updated in place"; `runtime-and-compatibility-v49.md` |
| `scripts/chatgpt_bridge_v43.py` | Durable checkpoint/state machine over the 17 stages (JSON state file, atomic replace). `start/load/next_step/submit/save`. | Imports `gate_chain_v41`; SKILL.md: "orchestration adapter, not competing validator" |
| `scripts/batch_guard_v45.py` | Seven independent jobs, each a bridge state file + batch `manifest.json`. `SLOTS=7`, `initialise()`, `summary()` (requires `READY_FOR_OWNER_REVIEW` + valid individual 1080×1350 PNG + 17 records/job; rejects reused image paths / duplicate IDs). | Imports `chatgpt_bridge_v43` |
| `references/production-policy-v33.json` | **Only machine-readable brand settings.** Sora heading+body, emerald `#10B77F`, logo optional, approved logo `assets/erudience-owner-approved-logo-2026-11-21.jpg`. | SKILL.md, `brand-policy-current.md` |
| `references/brand-policy-current.md`, `references/runtime-and-compatibility-v49.md` | Current policy + compatibility contract; supersede historical docs. | SKILL.md: "read these first" |
| Manifests | `plugin.json` + `.agent-plugin/`, `.claude-plugin/`, `.codex-plugin/` copies, `plugin.yaml`, `.app.json` — all now **4.9.2** (see §5). | — |

## 2. 17-stage workflow verification

Stage list is defined in exactly one place in code: `gate_chain_v41.py:11`
`STAGES = (SOURCES, SOURCE_REVIEW, RESEARCH, RESEARCH_REVIEW, STRATEGY, STRATEGY_REVIEW, CONTENT, CONTENT_REVIEW, IMAGE_PLAN, PLAN_REVIEW, IMAGE_BUILD, TECH_REVIEW, VISUAL_REVIEW, CONTENT_IMAGE_REVIEW, BRAND_REVIEW, FINAL_REVIEW, DELIVERY)` — 8 of them are `*_REVIEW` stages. Restated in `references/gate-contract-v41.md` and SKILL.md.

Verified by execution (E2E, 20/20 checks — see regression report):

- **Transitions:** strictly sequential (`Chain.run()` walks the index; `chatgpt_bridge.submit()` raises `OUT_OF_ORDER_STAGE`; `production_controller.commit()` raises `OUT_OF_ORDER_OR_BLOCKED`). No stage skipping.
- **Validation:** upstream hash binding every stage (`UPSTREAM_HASH_MISMATCH`); reviews require reviewer-role adapter, `decision == PASS`, non-empty `observations`, `subject_hash` match, and reviewer ≠ producer (`SELF_REVIEW_FORBIDDEN`); stage-specific checks for SOURCES (URL + `verified_at`; live mode also `source_sha256`), CONTENT (ID/topic/caption/keywords locked), IMAGE_PLAN (content binding, poster text, `[1080,1350]`, `brand == BRAND`, logo ∈ {None, approved}), IMAGE_BUILD (plan hash, real PNG file + SHA256, PNG 1080×1350 RGB/RGBA, copy-ledger hash, font provenance, logo provenance iff planned, `copy_rendered is True`), TECH_REVIEW (re-opens PNG), VISUAL_REVIEW (pixel + mobile inspection), CONTENT_IMAGE_REVIEW (topic + text match), BRAND_REVIEW (fonts/palette/footer/logo-or-absence/positioning), DELIVERY (all 16 prior stages + image SHA256).
- **Failure / retry / repair:** `Chain(limit=3)`; failure pops records from `REPAIR[stage]` and restarts there (`SOURCE_REVIEW→SOURCES`, `RESEARCH_REVIEW→RESEARCH`, `STRATEGY_REVIEW→STRATEGY`, `CONTENT_REVIEW→CONTENT`, `PLAN_REVIEW→IMAGE_PLAN`, `TECH/VISUAL/FINAL_REVIEW→IMAGE_BUILD`, `CONTENT_IMAGE/BRAND_REVIEW→IMAGE_PLAN`); revisions > limit → `BLOCKED`; missing adapter → `BLOCKED` (`ADAPTER_MISSING`). Verified: visual-review failure once → rebuild + recheck, `repairs == 1`, `TEST_FIXTURE_PASS`; retries exhausted → `BLOCKED`; unapproved logo → `BLOCKED`; missing adapter → `BLOCKED`.
- **Evidence:** in-memory `records` (artifact + SHA256 + adapter) and `trace` (PASS/FAIL, reason, return-to, revision). Live mode (non-`TEST_FIXTURE`) additionally requires independent inspection-evidence files with matching SHA256 and live source/font provenance. No timestamps are recorded in the chain.
- **Review requirements:** all 8 review stages enforced as above; self-review forbidden.
- **State persistence:** `chatgpt_bridge_v43` JSON state file (temp + `os.replace`, no fsync/locking); `batch_guard_v45` batch manifest; `production_controller_v39` atomic save (`mkstemp` + `fsync` + `os.replace`). `gate_chain_v41` and `autonomous_pipeline_v40` are in-memory only (no resume). `submit()` is fail-safe, not idempotent (replay of a passed stage raises `OUT_OF_ORDER_STAGE`); `start()`/`initialise()` refuse existing state (`JOB_ALREADY_EXISTS` / `BATCH_ALREADY_EXISTS`). The only idempotent-ish store is `evidence_store.py` (SQLite, deterministic receipt IDs) — and nothing imports it (see §4).
- **Idempotency:** batch re-initialisation rejected; duplicate topics rejected (`SEVEN_DISTINCT_TOPICS_REQUIRED`); duplicate content IDs and reused image paths rejected by `summary()`.
- **Output integrity:** every image is hash-bound (plan hash, copy-ledger hash, image SHA256) and re-opened with Pillow at TECH_REVIEW; `verify_output.py` mechanical gate (PNG decode, 1080×1350, ≤5 MB, sibling manifest + SHA256, locked 6-step stage names) passes on a valid fixture.
- **Owner approval:** no stage engine records an owner approval — terminal status is `READY_FOR_OWNER_REVIEW` (ready *for*, not approved *by*, the owner). Publishing/external writes are always blocked (`external_writes: 0`; `workflow_engine` returns `BLOCKED / NO_VERIFIED_WRITE_ADAPTER` even with approval; `run(..., external_write=True)` raises `WorkflowError`). The only explicit owner-approval model is `evidence_store.can_handoff()` (requires separate `APPROVE` + `WRITE_AUTHORISE` rows) — currently unwired.

**Gaps found (documented, not silently fixed):**
1. `RESEARCH` and `STRATEGY` have no stage-specific checks in `gate_chain_v41` beyond upstream-hash binding (contrast `autonomous_pipeline_v40`, which requires research evidence + source SHA256 and strategy/research hash binding).
2. `FINAL_REVIEW` has no check beyond generic image/plan binding; `TECH_REVIEW` does not re-check `image_sha256`.
3. Live-mode font verification covers only the heading family (`for family in (BRAND['heading'],)`); body font binary is never verified at build time.
4. No owner-approval field/actor/timestamp anywhere in the stage engines; `workflow_engine`/`content_engine` name an `OWNER_APPROVAL` stage but never enforce it (`workflow_engine` only checks `STAGES[:8]`).

## 3. Compatibility layers vs historical references

**Compatibility (retained, exercised by the regression suite, explicitly NOT active production paths — do not invoke as independent execution paths):**
- `production_controller_v39.py` — older 13-stage single-item controller (`MAX_REVISIONS=3`, atomic save). Only caller is its test.
- `workflow_engine.py` — older 10-stage 7-slot orchestrator. Only caller is `integration_tests.py`.
- `autonomous_pipeline_v40.py` — 13-stage in-memory coordinator with deterministic validators (explicitly not human/model review). Only caller is its test.
- `production_gate.py` (9-stage file-receipt acceptance), `content_engine.py` (offline content workflow, 10 differently-named stages), `keyword_research.py`, `linkedin_seo_validator.py`, `competitor_monitor.py`, `linkedin_analytics.py` — regression/traceability helpers.
- `website_brand_v38.py` / `website_render_v38.py` — website-first brand spec/renderer (Inter/DM Sans + `#10B981`). `unified-system-v42.md` calls them the active website brand contract, which conflicts with the canonical JSON (see §4) — treated as a compatibility profile, not canonical.

**Historical-reference only (no production caller):**
`brand_policy_v36.py`, `brand_render_v37.py` (Sora + mandatory authenticated logo + pinned `social-os/BRAND.md:v1.1`), `render_poster.py` (fixed 6-step draft renderer; its manifest format is what `verify_output.py` expects), `verify_output.py`, `brief_prompt_gate.py`, `batch_gate.py`, `validate_strategy_v33.py` (CLI helpers), `evidence_store.py` (no caller, no test — but the *only* owner-approval/write-authorisation model; preserved for that unique functionality).

**Contradictions found (documented, not resolved by deletion):**
1. Stage counts/names differ across controllers: 17 (v41/bridge) vs 13 (v39/v40) vs 10 (workflow_engine, different names) vs 9 (production_gate) vs 10 differently-named (content_engine). No mapping exists between them.
2. Three mutually exclusive "authoritative controller" claims: SKILL.md + runtime-v49 + unified-v42 say `gate_chain_v41` only; `execution-state-machine-v39.md` says v39 is authoritative; `autonomous-execution-v40.md` says v40's `Controller` is the only supported new controller API.
3. Brand split: gate chain enforces JSON (Sora / `#10B77F` / logo optional); v39/v40 enforce Inter/DM Sans + `#10B981` + `brand_profile == 'website-v38'`; workflow/production-gate/content-engine enforce no brand tokens at all. `gate-contract-v41.md`'s own brand paragraph (Inter/DM Sans / `#10B981`) contradicts the `gate_chain_v41.py` code it documents.
4. Repair targets differ accordingly (e.g. v39/v40 `CONTENT_MATCH_QA`/`BRAND_QA → BRIEF` vs v41 `CONTENT_IMAGE_REVIEW`/`BRAND_REVIEW → IMAGE_PLAN`; v41 has no `BRIEF`/`RENDER` stages).

**Decision:** no review stage was collapsed and no legacy controller was deleted. SKILL.md + runtime-v49 are followed as canonical; the contradictions are recorded here and in `reports/release-verification.md` as known limitations requiring an owner decision. Deleting any controller would remove unique functionality (e.g. v39's atomic persisted state, v40's deterministic validators, `evidence_store`'s approval model) that the canonical chain does not provide.

## 4. Brand consistency (summary; full scan in `reports/regression-results.md` §Brand)

- Canonical (machine-readable): Sora, `#10B77F`, logo optional — `production-policy-v33.json`, enforced only by `gate_chain_v41` (the only module that reads the JSON).
- Website-first profile (deliberate, test-encoded): Inter/DM Sans, `#10B981` — hard-coded in `autonomous_pipeline_v40.py`, `brand_policy_v36.py`, `brand_render_v37.py`, `website_brand_v38.py`, `render_poster.py`, and in `test_website_brand_v38.py` / `test_autonomous_pipeline_v40.py` fixtures. `brand_policy_v36` mixes the two (Sora font check + `#10B981` palette) by design of v36.
- Logo: optional in JSON / gate chain / website-v38; **mandatory** in `brand_policy_v36` (`LOGO_NOT_AUTHENTICATED`), `brand_render_v37`, `render_poster` (unless `--review-draft`), `brief_prompt_gate`, `production_gate`. `owner-approved-brand-v46.md` additionally says the owner logo should be used for all *new* branded posters, superseding logo-optional for new posters — while `brand-policy-current.md` keeps logo-optional as the standing rule. Both are preserved; the conflict is an owner decision, not something to resolve by editing code.
- **No active-code brand correction was made.** Rewriting `#10B981` → `#10B77F` or Inter/DM Sans → Sora in the website-first renderers would contradict their own reference docs (v38/v40/v47) and break their deliberately-encoded tests; the task rule "never weaken assertions merely to make tests pass" also forbids re-encoding those tests to match a rewrite. The only brand change in v4.9.2 is bundling the real approved logo (previously missing), which *unblocks* the logo-present path in `gate_chain_v41` (verified by E2E: `gate17_logo_present` now `TEST_FIXTURE_PASS`).
- `brand_render_v37.verify_assets()` pins `brand_policy == 'social-os/BRAND.md:v1.1'`; no `social-os/` directory or `BRAND.md` exists in this repo, so that check is a string comparison against a file that cannot be verified here — recorded as a known limitation.

## 5. Version inconsistencies found and fixed

| Location | Before | After (v4.9.2) |
|---|---|---|
| `plugin.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` | 4.9.1 | **4.9.2** |
| `plugin.yaml`, `.app.json` | 4.6.0 (stale) | **4.9.2** |
| `skills/erudience/SKILL.md` heading, `references/brand-policy-current.md` heading, `README.md` | v4.9.1 | **v4.9.2** |
| `references/production-policy-v33.json` `"version": "3.3.0"` | — | Unchanged: that is the *policy* version, not the plugin version |
| `README.md` "89 text source files" / "27 passed" subset claim | stale | Corrected to 90 files (incl. logo) and full-suite results |

## 6. Other findings

- **Duplicates:** `plugin.json` = `.agent-plugin/plugin.json` = `.claude-plugin/plugin.json` (MD5 `0d09c47750d0ae0af6452ba0465aca36`) — intentional host mirrors, one manifest per plugin-host location; deleting any would break that host's discovery. No other duplicate files.
- **Missing on `main`, resolved on this branch:** the approved logo (see `reports/source-inventory.md`). Still missing by design: font binaries (Sora/Inter/DM Sans — renderers require installed paths and fail closed), and any dependency manifest (`requirements.txt`/`pyproject.toml` — Pillow is declared only in CI).
- **No tests for:** `evidence_store`, `batch_gate`, `brief_prompt_gate`, `verify_output` (before v4.9.2 — now covered, see below), `website_render_v38`, `render_poster`. CI runs `discover -s scripts -p 'test_*.py'` + `tests_content_engine` + `integration_tests.py` (needed because discover does not pick up `integration_tests.py`).
- **Code defect fixed in v4.9.2:** `verify_output.py` ran argparse + checks + `sys.exit()` at module top level (no `__main__` guard), so importing it parsed `sys.argv` and exited. Fixed by moving execution into `main(argv)` with an `if __name__ == '__main__'` guard; CLI behaviour, checks, output and exit codes unchanged. New regression test `scripts/test_verify_output.py` (5 tests) covers import safety + CLI pass/block paths.
- **Noted wart, intentionally unchanged:** `validate_strategy_v33.py` loads `production-policy-v33.json` into `P` at import and never uses it (a missing/corrupt JSON would break import for no functional reason). Left as-is under the minimal-change rule; recorded here.
- **No `scripts/__init__.py`:** scripts are not a package; cross-module imports work only when run from `scripts/` or with `sys.path` insertion, as the tests do. Not changed.
- **No network code:** no `requests`/`urllib`/`socket`/provider SDKs in `scripts/*.py`. External integrations are NOT_CONFIGURED (`endpoint-registry.json`: OpenAI/Anthropic/Google Search Console all `DOCUMENTED_PROVIDER_API_NOT_CONNECTED`). No secrets found in the plugin tree.
- **Spelling baked in:** command `erudiance_linkdin` (sic) in SKILL.md and `.codex-plugin/plugin.json` default prompt; `batch-production-v45.md` lists it as the trigger with `erudience_linkdin` as alias. Left unchanged (renaming would break the documented trigger).
