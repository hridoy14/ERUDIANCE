# Erudience Plugin — Duplicate Removal Evidence (Consolidation)

- Baseline: `main` `9e320fa6` (v4.9.2). Full classification: `~/workspace/erudiance-plugin-work/consolidation-staging/duplicate-classification-draft.md`.
- **Files removed in this task: 0. No file met all 10 Phase-10 conditions, because no move, test re-run, or verification of the new layout was executed (execution block, see `source-baseline.md`). This report records the classification and what would still be required before any removal.**

## Classification counts (78 files: 36 references + 35 scripts + 1 root test + 6 manifests)
| Classification | References | Scripts | Root test + manifests | Total |
|---|---|---|---|---|
| EXACT_DUPLICATE | 0 | 0 | 0 | **0** |
| SEMANTIC_DUPLICATE | 0 | 0 | 0 | **0** |
| PARTIAL_DUPLICATE | 16 | 7 | 0 | **23** |
| UNIQUE | 8 | 20 | 3 | **31** |
| CONFLICTING_POLICY | 8 | 8 | 0 | **16** |
| COMPATIBILITY_REQUIRED | 0 | 0 | 4 | **4** |
| HISTORICAL_UNIQUE | 4 | 0 | 0 | **4** |
| DISCONNECTED (primary) | 0 | 0 | 0 | 0 |
| UNVERIFIED (primary) | 0 | 0 | 0 | 0 |

Headline: **no exact or semantic duplicates exist.** The duplication is partial (23) and conflictual (16). No file is removable on duplicate grounds alone.

## The 16 CONFLICTING_POLICY files (never delete, never silently merge)
References (8): `asset-and-font-policy.md`, `brand-source-of-truth-v36.md`, `brand-template-contract-v47.md`, `gate-contract-v41.md`, `master-command-v6.md`, `owner-approved-brand-v46.md`, `production-runtime-v37.md`, `website-brand-profile-v38.md`.
Scripts (8): `autonomous_pipeline_v40.py`, `brand_policy_v36.py`, `brand_render_v37.py`, `production_controller_v39.py`, `render_poster.py`, `website_brand_v38.py`, `website_render_v38.py`, `workflow_engine.py`.
Each asserts an incompatible brand/controller/renderer rule; what would be lost if removed is recorded per file in the draft (e.g. v46 is the only dated owner-approval record for the bundled logo; `gate-contract-v41.md` is the only prose 17-stage contract; `autonomous_pipeline_v40.py` holds the only deterministic content/brand validators).

## The 4 COMPATIBILITY_REQUIRED files (never delete)
`plugin.json`, `.agent-plugin/plugin.json`, `.claude-plugin/plugin.json` (byte-identical host mirrors — removing one breaks that host's discovery) and `.codex-plugin/plugin.json` (host-extended variant). `.app.json` and `plugin.yaml` are distinct shapes, UNIQUE.

## The 4 HISTORICAL_UNIQUE files (archive, do not delete)
`autonomous-execution-v40.md`, `chat-vision-audit-v35.md`, `execution-state-machine-v39.md`, `release-audit-v34.md` — sole surviving records of their version's contract/audit, including the direct-image-generation failure record that justifies the fail-closed gates.

## The 23 PARTIAL_DUPLICATE files
References (16): `batch-production-v45.md`, `brand-assets-manifest.md`, `chatgpt-runtime-v43.md`, `integration-registry-v34.json`, `master-action-v31.md`, `monthly-weekly-social-os.md`, `one-action-production-contract.md`, `one-command-v44.md`, `orchestrator-v2.md`, `production-contract-v33.md`, `production-execution-v35.md`, `release-compatibility-v48.md`, `smb-content-strategy-v32.md`, `system-architecture-v34.md`, `unified-system-v42.md`, `workflow-v3.md`.
Scripts (7): `batch_gate.py`, `brief_prompt_gate.py`, `content_engine.py`, `linkedin_seo_validator.py`, `production_gate.py`, `validate_strategy_v33.py`, `verify_output.py`.
Each overlaps substantially but carries unique content (e.g. `production-contract-v33.md` alone carries the module IO table and the 10-field promotion spec; `brief_prompt_gate.py` alone carries the brief↔prompt binding check). Removal would lose that unique part — so **keep** until the unique part is registered, preserved in a canonical destination, and verified by tests.

## Cross-cutting triplicated content (merge as units, not by deleting files)
1. Warm Enquiry locked copy — 5 homes (brief-schema JSON, master-command-v6, one-action contract, `render_poster.py`, `verify_output.py`).
2. Caption rules (3 hashtags, 7 banned words) — 3 homes.
3. Poster layout — 6 homes, 3 incompatible font/emerald/logo variants.
4. 100-point rubric (20/20/20/15/10/10/5) — 3 homes.
5. 7 slots / exactly 1 promotion / employee oversight — 9 homes; the count check exists only in disconnected validators.
6. 50-competitor target (15/10/10/10/5) — 4 homes; no populated dataset anywhere.
7. "No live endpoints / NOT_CONFIGURED" — 8 homes; registries are the machine-readable record.
8. Repair cap 3 / 4th failure BLOCKED — 15+ homes; a genuine invariant, not a conflict.

## Phase-10 checklist per file
For every candidate, all 10 conditions were assessed as **NOT MET** for removal in this task: (1) content inspected — yes; (2) unique requirements registered — yes (197 in registry); (3) unique functions/instructions preserved in a canonical destination — **no, destinations are planned, not built**; (4) canonical destination exists — **no**; (5) dependencies migrated — **no**; (6) public interfaces remain compatible — **not verified**; (7) relevant tests pass — **not re-run**; (8) original source recoverable — yes on `main` (baseline commit recorded); (9) no unresolved unique content — **no, conflicts are open**; (10) deletion recorded — n/a, nothing deleted.
**Conclusion: keep every file. Do not delete any file merely to reduce the file count.**

## Post-consolidation update (2026-11-22)
- Duplicate removal result: 0 files removed. Classification stands: EXACT_DUPLICATE 0, SEMANTIC_DUPLICATE 0, PARTIAL_DUPLICATE 23, UNIQUE 31, CONFLICTING_POLICY 16, COMPATIBILITY_REQUIRED 4, HISTORICAL_UNIQUE 4.
- The 3 byte-identical `plugin.json` copies were kept (host mirrors; deleting one breaks that host's discovery).
- The 23 shims are intentional compatibility files, not duplicates: each re-exports one canonical module and contains no business logic.
