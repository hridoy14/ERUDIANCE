# Multi-Agent Workflow Map

One master command: `erudiance_linkdin` (alias `erudience_linkdin`).
One master orchestrator: `core/gate_chain_v41.py` (17 stages) +
`core/chatgpt_bridge_v43.py` (durable checkpoints) +
`core/batch_guard_v45.py` (7-job batch).
One central policy: `config/production-policy-v33.json` +
`config/brand-policy-current.md`.
One canonical validation authority: `core/gate_chain_v41.py`.
Entry point: `skills/erudience/SKILL.md`.

## The 17 operational stages and the agent at each stage
| Stage | Producer agent | Reviewer agent | Gate |
|---|---|---|---|
| SOURCES | AG-01/AG-02/AG-03/AG-04 | — | SOURCE_PROVENANCE_REQUIRED |
| SOURCE_REVIEW | — | AG-12/AG-13 | reviewer ≠ producer, evidenced PASS |
| RESEARCH | AG-02/AG-03/AG-04 | — | provenance |
| RESEARCH_REVIEW | — | AG-12/AG-13 | reviewer ≠ producer |
| STRATEGY | AG-08 | — | 1 promotion, 7 slots |
| STRATEGY_REVIEW | — | AG-12 | reviewer ≠ producer |
| CONTENT | AG-10 | — | CONTENT_NOT_LOCKED |
| CONTENT_REVIEW | — | AG-12/AG-13 | reviewer ≠ producer |
| IMAGE_PLAN | AG-14 | — | PLAN_* (brand, dimensions, logo) |
| PLAN_REVIEW | — | AG-12/AG-16 | reviewer ≠ producer |
| IMAGE_BUILD | AG-15 | — | IMAGE_* (bytes, copy ledger, logo) |
| TECH_REVIEW | — | AG-16 | PNG valid 1080×1350 |
| VISUAL_REVIEW | — | AG-16 | pixel + mobile inspection |
| CONTENT_IMAGE_REVIEW | — | AG-12/AG-16 | topic + text match |
| BRAND_REVIEW | — | AG-16 | font/palette/footer/logo |
| FINAL_REVIEW | — | AG-12/AG-16 | image + plan hash match |
| DELIVERY | AG-17 | owner (human) | DELIVERY_NOT_VERIFIED |

Historical 13-stage controllers (`core/legacy/`) map onto these 17 stages
without losing enforcement: content hash locking, brief-to-content binding,
image-to-brief binding, image-byte hashing, independent review, failure-stage
recovery, downstream receipt invalidation, max 3 repairs, BLOCKED on 4th.
See `reports/consolidation/requirements-traceability.md`.

## Group map
- Research: AG-01 → AG-02/AG-03/AG-04 (parallel) → AG-05 → AG-06 → AG-07.
- Strategy: AG-07 → AG-08 → AG-09.
- Content: AG-09 → AG-10 → AG-11.
- Creative: AG-10 (locked) → AG-14 → AG-15.
- Review: AG-12, AG-13, AG-16 (independent; never self-review).
- Delivery: AG-17 → owner approval → AG-18 (after authorised publishing).

## Batch map (7 independent jobs)
One `erudiance_linkdin` run creates 7 distinct topics and 7 independent
jobs (`core/batch_guard_v45.py::initialise`). Each job runs its own 17-stage
chain; each produces its own PNG (1080×1350, 4:5, unique content ID, unique
image SHA256; reuse across IDs is rejected). The batch is
`READY_FOR_OWNER_REVIEW` only when all 7 jobs pass all 17 gates.
Re-running `initialise` on the same root raises `BATCH_ALREADY_EXISTS`.

## State, receipts and recovery
- State: `core/chatgpt_bridge_v43.py` (durable JSON checkpoints per job);
  `core/evidence_store.py` (provenance + `can_handoff()`).
- Receipt per stage: stage, content ID, artifact path, SHA256, producer,
  independent reviewer, timestamp, approval evidence, artifact existence.
- Failure: return to the owning stage, invalidate all downstream receipts,
  max 3 repairs, BLOCKED on the 4th failure.
- Terminal states: `READY_FOR_OWNER_REVIEW`, `OWNER_APPROVED` (explicit only),
  `BLOCKED`, `TEST_FIXTURE_PASS` (fixtures only, never production approval).

## What is NOT in this map
- No autonomous scheduler (trigger is manual unless separately authorised).
- No live research/writer/image/visual adapters (NOT_CONFIGURED).
- No publishing, scheduling, Social OS writes or LinkedIn writes.
- No agent is independently deployed; the 18 roles are logical roles
  executed by one orchestrator (see `references/system-architecture-v34.md`:
  "Logical roles can run in one orchestrator or separate agents").
