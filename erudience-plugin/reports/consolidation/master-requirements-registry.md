# Erudience Plugin — Master Requirements Registry (Consolidation)

- Baseline: `main` `9e320fa60785f40142f37be9342b3df42fc47968` (v4.9.2). Method: read-only inspection of every file in `erudience-plugin/`. Full registry with per-requirement source, line/section reference, purpose, implementation, dependencies, canonical destination, verification method and status is in the working draft `~/workspace/erudiance-plugin-work/consolidation-staging/requirements-registry-draft.md` (197 rows). This report is the consolidated summary; the draft is the authoritative row-level record until the registry is placed on the consolidation branch.
- **Total unique requirements: 197.**
- **By status:** PRESERVED 95, DOCUMENTED_ONLY 81, CONFLICT_UNRESOLVED 8, NOT_VERIFIED 8, BLOCKED_BY_ENVIRONMENT 5.
- **By family:** BUS 5, COMP 9, BUY 6, MKT 6, TOP 6, STR 8, FUN 5, COPY 8, PROMO 16, CREATIVE 8, IMG 12, BRAND 16, QA 10, GATE 18, RECEIPT 8, HASH 8, RETRY 6, BATCH 8, APPROVAL 8, ANALYTICS 5, PROV 6, INT 6, COMPAT 6, SEC 3.
- Status key: PRESERVED = implemented in code and exercised by the prior regression suite; DOCUMENTED_ONLY = stated in docs, no live code path enforces it; CONFLICT_UNRESOLVED = in-repo sources contradict each other, owner decision required; NOT_VERIFIED = needs live/external evidence no test proves; BLOCKED_BY_ENVIRONMENT = cannot be exercised here (missing fonts, NOT_CONFIGURED integrations, no Plugin Creator / git-push access).

## Mandatory sets — all covered

### A. All 14 production modules (BUS/COMP/BUY/MKT/TOP/STR/FUN/COPY/CREATIVE/IMG/QA/APPROVAL/ANALYTICS/PROV)
1. Business intelligence — DOCUMENTED_ONLY (no dedicated module; partially `content_engine` + gate SOURCES).
2. Competitor intelligence — PRESERVED for the audit (50-target, gaps, provenance); collection itself DOCUMENTED_ONLY (no dataset in repo).
3. Buyer intelligence — DOCUMENTED_ONLY (no module).
4. Market trends — DOCUMENTED_ONLY, except the trend-without-sources block (PRESERVED).
5. Topic intelligence — PRESERVED for no-deletion + topic-swap block; scoring/ranking DOCUMENTED_ONLY.
6. Marketing strategy — DOCUMENTED_ONLY (only slot/promotion shape validated).
7. Funnel planning — PRESERVED (7 slots, 1 promotion, stage/CTA rules in `workflow_engine` / `content_engine`).
8. LinkedIn copywriting — PRESERVED for claim-source binding, keyword/stuffing, locked Warm Enquiry copy; draft-quality bar DOCUMENTED_ONLY.
9. Creative brief — PRESERVED for the 13-field structural gate and brief→prompt binding; 3-candidate scoring and 9-point brief review DOCUMENTED_ONLY.
10. Image generation — PRESERVED for IMAGE_BUILD binding (plan hash, PNG, copy ledger); live generation adapter DOCUMENTED_ONLY (none exists).
11. Brand and claims QA — PRESERVED (three-valued verdicts, negative-path tests).
12. Approval and distribution — DOCUMENTED_ONLY (only model is unwired `evidence_store.can_handoff()`).
13. Analytics and learning — PRESERVED for descriptive summarising only; feedback loop DOCUMENTED_ONLY.
14. Knowledge provenance — PRESERVED for hash/receipt records in the chain; full payload schema DOCUMENTED_ONLY.

### B. All 10 promotional fields (PROMO-01–16)
Exactly one promotion per full 7-slot week, HOLD if unverified, never substitute (PRESERVED). Field 8 (employee/human oversight) is enforced in code (PRESERVED). Fields 1–7, 9–10 and the conditions staff approval / fallback / privacy consent / telephony compliance / booking reconciliation (PROMO-11–15) are **DOCUMENTED_ONLY** — no validator checks them. Promo inside the 4 default published posts, never a 5th (PROMO-16) is DOCUMENTED_ONLY.

### C. All 8 production capabilities
Freshness (DOCUMENTED_ONLY as a weekly mechanism; SOURCES provenance PRESERVED), competitor monitoring 15+10+10+10+5=50 with honest shortfall reporting (PRESERVED as audit; dataset NOT_VERIFIED), topic preservation READY/ENRICH/RESEARCH_NEEDED/HOLD + `topic_delete_allowed: false` (PRESERVED), asset management (PRESERVED for the bundled logo), mobile readability (PRESERVED as inspection flags), experimentation (DOCUMENTED_ONLY — no code), feedback loop (DOCUMENTED_ONLY — no closed loop), audit trail (PRESERVED for chain/bridge receipts; timestamps missing in the chain — DOCUMENTED_ONLY).

### D. Receipt integrity (RECEIPT-01–08)
Stage, content ID, artifact path, SHA256, producer, independent reviewer, timestamp, approval evidence, artifact existence — PRESERVED as a protocol in `production_gate` + `gate_chain` records; full payload schema (schema_version, revision, timestamp_utc, failure_codes) is DOCUMENTED_ONLY; `evidence_store` and `batch_gate` models are DOCUMENTED_ONLY (unwired/untested). A PASS string alone is never sufficient — enforced in code.

### E. Rendering (IMG-01–12)
`brand_render_v37.py` is the only accepted deterministic final renderer per v3.7; `render_poster.py` is draft-only per the same doc — but the canonical chain calls **neither** (adapters missing), so IMG-05 is CONFLICT_UNRESOLVED. One standalone PNG 1080×1350, 4:5, no collage, deterministic text (PRESERVED in gate + mechanical gate). Rendered output vs independently reviewed approval are distinct (PRESERVED). Three mutually incompatible renderers exist (3–5 steps vs exactly 6 steps) — unresolved, see `policy-conflicts.md` C9/C19.

### F. Historical 13-stage rules (GATE-12–17, HASH-02–06, RETRY-01–02)
Content hash locking, brief-to-content binding, image-to-brief binding, image-byte hashing, independent review, failure-stage recovery, downstream receipt invalidation, max 3 repairs, BLOCKED on 4th, producer/reviewer separation — all PRESERVED in v39/v40 code and mapped to the 17-stage chain in `target-architecture.md` §8 (mapping is traceability-only; the 10/9/content-engine stage sets have no mapping and none was invented).

### G. Seven independent PNGs (BATCH-01–08, IMG-03/04)
7 distinct jobs, 7 independent PNGs, exactly 1080×1350, 4:5, no collage, unique IDs, caption/content/image hash binding, no reuse, per-job gates — PRESERVED in `batch_guard_v45` + gate chain. Batch READY only when all 7 pass (PRESERVED). `READY_FOR_OWNER_REVIEW` is distinct from owner approval (PRESERVED as semantics; approval recording itself is DOCUMENTED_ONLY). The `--test --single-content` form is DOCUMENTED_ONLY (no CLI implements it).

### H. Brand (BRAND-01–16)
Sora heading+body, emerald `#10B77F`, palette paper/ink/soft/deep/dark, footer Erudience + erudience.com, logo optional original-only (PRESERVED in the JSON + gate chain). The website-first profile (Inter/DM Sans/`#10B981`/logo-required) is CONFLICT_UNRESOLVED (BRAND-04/05/11/14/16). `brand_render_v37` pins `social-os/BRAND.md:v1.1`, a file that does not exist in this repo (BRAND-14, CONFLICT_UNRESOLVED).

## What is NOT in the registry
- No requirement was invented. Every row traces to a file actually read.
- Live integrations (LinkedIn, Supabase, research, image renderer, scheduler, analytics) are recorded as DOCUMENTED_ONLY / BLOCKED_BY_ENVIRONMENT (INT-01–06), never as implemented.
- The `erudiance_linkdin` command itself (BATCH-05/08) is DOCUMENTED_ONLY as a command — no parser exists in any script.

## Post-consolidation update (2026-11-22)
- Total still 197 unique requirements (PRESERVED 95, DOCUMENTED_ONLY 81, CONFLICT_UNRESOLVED 8, NOT_VERIFIED 8, BLOCKED_BY_ENVIRONMENT 5).
- Migrated-and-verified: 95 PRESERVED requirements now live in the consolidated layout; the 81 DOCUMENTED_ONLY requirements are preserved in docs (agent registry + module mapping), not silently dropped.
- 0 requirements removed. 8 conflicts (C1-C22 set, brand profile) remain UNRESOLVED pending owner decision.
