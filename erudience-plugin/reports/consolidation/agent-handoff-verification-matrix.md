# Agent Handoff and Verification Matrix

Each row is one handoff between agents. "Verified by" is the mechanism
that enforces it in code (or the gap where none exists).

| # | From → To | Handoff artifact | Verified by |
|---|---|---|---|
| H-01 | AG-01 → AG-02/AG-03 | service map + provenance receipt | DOCUMENTED_ONLY (no code) |
| H-02 | AG-02 → AG-07 | 50-record ledger + coverage report | `competitor_monitor.py` (disconnected); gate SOURCES |
| H-03 | AG-03 → AG-06/AG-07 | persona/pain clusters | DOCUMENTED_ONLY |
| H-04 | AG-04 → AG-08 | trend brief | DOCUMENTED_ONLY |
| H-05 | AG-05 → AG-06 | typed keyword cluster | `keyword_research.validate_cluster` |
| H-06 | AG-05 → AG-11 | typed keyword cluster | `linkedin_seo_validator.review` |
| H-07 | AG-06 → AG-09 | intent/funnel map | DOCUMENTED_ONLY |
| H-08 | AG-07 → AG-08 | scored topic records | `validate_strategy_v33` (no-delete rule) |
| H-09 | AG-08 → AG-09 | 7-slot plan, 1 promotion | `validate_strategy_v33` |
| H-10 | AG-09 → AG-10 | funnel allocation | `content_engine.funnel_stage` |
| H-11 | AG-10 → AG-11 | draft + claim/source bindings | `content_engine.gate` |
| H-12 | AG-11 → AG-12 | revised draft | DOCUMENTED_ONLY |
| H-13 | AG-10/AG-11 → AG-12 | draft for clarity verdict | `core/gate_chain_v41.py` CONTENT_REVIEW |
| H-14 | AG-10 → AG-13 | claims + source registry | `core/gate_chain_v41.py` review stages |
| H-15 | AG-12/AG-13 → AG-10 | verdict + observations (REVISE) | gate repair routing (max 3, BLOCKED 4th) |
| H-16 | AG-10 → AG-14 | verified copy + brand tokens | `core/gate_chain_v41.py` IMAGE_PLAN (content lock) |
| H-17 | AG-14 → AG-15 | creative brief + content hash | `brief_prompt_gate` + IMAGE_PLAN binding |
| H-18 | AG-15 → AG-16 | PNG + SHA256 + manifest | `core/gate_chain_v41.py` IMAGE_BUILD |
| H-19 | AG-16 → AG-17 | inspection receipt | `core/gate_chain_v41.py` BRAND_REVIEW |
| H-20 | AG-17 → owner | review package (17 receipts) | `core/gate_chain_v41.py` DELIVERY |
| H-21 | owner → AG-17 | explicit APPROVE/REJECT + timestamp + hash | `core/evidence_store.py::can_handoff` (model only) |
| H-22 | AG-17 → AG-18 | delivered content IDs + metrics source | DOCUMENTED_ONLY (no live metrics) |
| H-23 | AG-18 → AG-07/AG-08 | performance learnings | DOCUMENTED_ONLY |

## Verification rules enforced on every handoff
1. Upstream hash chaining: each stage output carries `upstream_hash` equal to
   the previous stage record hash (`core/gate_chain_v41.py::verify`).
2. Reviewer ≠ producer (`SELF_REVIEW_FORBIDDEN`); review artifacts carry
   `reviewer`, `decision=PASS`, non-empty `observations`, `subject_hash`.
3. Content hash locking: IMAGE_PLAN binds to CONTENT hash; IMAGE_BUILD binds
   to IMAGE_PLAN hash; reviews bind to image + plan hashes.
4. Downstream receipt invalidation on any failure; max 3 repairs; BLOCKED on 4th.
5. A `PASS` string alone never passes; artifact existence + SHA256 are checked.
6. No external write at any handoff without separate explicit permission + readback.
