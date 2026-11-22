# Agent-to-Module Mapping

Sources: `agents/roles-v34.md`, `references/system-architecture-v34.md`,
`references/orchestrator-v2.md`, `config/production-policy-v33.json`
(14 modules), `reports/consolidation/agent-registry.md`.

The 18 agents, 14 functional modules, 8 production capabilities and
17 validation stages are separate dimensions. One agent may serve one
module; one module may be served by several agents; a review agent may
serve no production module (it serves a gate instead).

| Agent | Module(s) | Production capabilities served |
|---|---|---|
| AG-01 Business Intelligence | business_service_intelligence | Freshness control, Audit trail |
| AG-02 Competitor Research | competitor_intelligence | Competitor monitoring, Freshness control, Audit trail |
| AG-03 Buyer Research | buyer_intelligence | Feedback loop, Audit trail |
| AG-04 Market Research | market_trends | Freshness control, Experimentation |
| AG-05 Keyword Research | topic_intelligence | Topic preservation, Audit trail |
| AG-06 Search Intent | topic_intelligence | Topic preservation |
| AG-07 Topic Intelligence | topic_intelligence | Topic preservation, Audit trail |
| AG-08 Content Strategy | marketing_strategy | Experimentation, Feedback loop, Audit trail |
| AG-09 Funnel Planning | funnel_planning | Experimentation |
| AG-10 Content Writer | linkedin_copywriting | Mobile readability, Audit trail |
| AG-11 SEO Optimization | topic_intelligence | Mobile readability |
| AG-12 Editorial Review | (gate role — CONTENT_REVIEW / STRATEGY_REVIEW) | Audit trail |
| AG-13 Fact Checker | (gate role — all review stages) | Freshness control, Audit trail |
| AG-14 Creative Director | creative_brief | Asset management, Mobile readability |
| AG-15 Image Producer | image_generation | Asset management, Mobile readability |
| AG-16 Brand QA | brand_claims_qa | Asset management, Mobile readability, Audit trail |
| AG-17 Delivery Controller | approval_distribution | Audit trail, Feedback loop |
| AG-18 Analytics | analytics_learning | Feedback loop, Experimentation |

## Modules with no agent code (documented only)
- business_service_intelligence (AG-01), buyer_intelligence (AG-03),
  market_trends (AG-04), image_generation as a live adapter (AG-15):
  the agent contract is preserved in the registry; implementation is a
  documented gap for a separate future phase. Do not mark them implemented.

## Modules served by more than one agent
- topic_intelligence: AG-05, AG-06, AG-07, AG-11.
- brand_claims_qa: AG-16 (production) — note the module holds two
  conflicting implementations (`brand_policy_v36.py` vs `website_brand_v38.py`,
  policy-conflicts.md C12); both preserved, neither merged.
- linkedin_copywriting carries funnel_planning logic (AG-09) inside
  `content_engine.py`; the funnel agent has no separate module file.

## Gate-only agents
AG-12 and AG-13 produce no production module output. They exist as
reviewer roles inside `core/gate_chain_v41.py` and
`core/chatgpt_bridge_v43.py`. Their separation from producers is the
enforcement mechanism for "no self-certification".
