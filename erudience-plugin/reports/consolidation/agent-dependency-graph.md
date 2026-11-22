# Agent Dependency Graph

Sources: `agents/roles-v34.md`, `references/system-architecture-v34.md`
(workflow graph), `references/orchestrator-v2.md` (steps 1–14),
`reports/consolidation/dependency-map.md`.

Notation: `A -> B` means B cannot start until A's handoff receipt exists.
`(parallel)` means the agents may run independently once their shared
input is ready. `(sequential)` means the dependency is strict.

## Research group (parallel after AG-01)
```
AG-01 Business Intelligence
  ├─(parallel)→ AG-02 Competitor Research ─┐
  ├─(parallel)→ AG-03 Buyer Research ──────┤
  └─(parallel)→ AG-04 Market Research ─────┤
                                           ▼
AG-05 Keyword Research ← AG-01 topic + AG-02/AG-03 evidence
  └─(sequential)→ AG-06 Search Intent ← AG-03 buyer questions
AG-07 Topic Intelligence ← AG-02 + AG-03 + AG-04 + AG-05
```

## Strategy group (sequential)
```
AG-07 → AG-08 Content Strategy → AG-09 Funnel Planning
AG-05/AG-06 ────────────────────→ AG-08 (keywords + intent feed the plan)
AG-04 ──────────────────────────→ AG-08 (trends feed the plan)
```

## Content group (sequential)
```
AG-08 plan + AG-09 funnel ─(sequential)→ AG-10 Content Writer
AG-10 ─(sequential)→ AG-11 SEO Optimization
```

## Creative group (sequential, content locked first)
```
AG-10 verified copy + AG-16 brand tokens ─(sequential)→ AG-14 Creative Director
AG-14 brief ─(sequential)→ AG-15 Image Producer
```

## Review group (independent of producers, sequential gates)
```
AG-12 Editorial Review ─┐
AG-13 Fact Checker ─────┤→ gate AG-10/AG-11 output before AG-14
AG-16 Brand QA ─────────┘→ gate AG-15 output before AG-17
Reviewers never share an adapter identity with the producer they review
(SELF_REVIEW_FORBIDDEN, enforced by core/gate_chain_v41.py).
```

## Delivery + analytics (sequential, then feedback)
```
AG-12 + AG-13 + AG-16 receipts ─(sequential)→ AG-17 Delivery Controller
AG-17 ─(sequential)→ owner approval (human, explicit, never assumed)
AG-17 ─(sequential, after authorised publishing)→ AG-18 Analytics
AG-18 ─(feedback)→ AG-07 Topic Intelligence + AG-08 Content Strategy
```

## Cross-cutting dependencies (all agents)
- `config/production-policy-v33.json` — brand + policy (read by the gate at import).
- `core/evidence_store.py` — provenance + `can_handoff()` (AG-17).
- `core/gate_chain_v41.py` — 17-stage validation authority (all review gates).
- `core/chatgpt_bridge_v43.py` — durable checkpoints (AG-17).
- `core/batch_guard_v45.py` — 7-job batch coordination (AG-17).
- `agents/roles-v34.md` — the role contracts themselves.

## Independent vs sequential summary
- Independent (parallel): AG-02/AG-03/AG-04 after AG-01; the 7 content jobs
  in a batch (each job runs its own 17-stage chain).
- Sequential: AG-01 → research; research → AG-07 → AG-08 → AG-09 → AG-10 →
  AG-11 → AG-12/AG-13 → AG-14 → AG-15 → AG-16 → AG-17 → owner → AG-18.
- Content is locked before image work; no stage may be skipped
  (`core/gate_chain_v41.py` enforces order + upstream hash chaining).
