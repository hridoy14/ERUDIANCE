# Agent Input/Output Contracts

Source of each contract: `agents/roles-v34.md` (input/output/gate table).
Field-level detail is taken from the module specs in
`references/production-contract-v33.md`, `references/orchestrator-v2.md`
(input contract + 30-day planning schema) and the implementing modules
where code exists. Where no code exists, the contract is documented-only
and marked as such — the schema is preserved, not implemented.

## AG-01 Business Intelligence
- In: `{verified_docs[], offer_readiness, service_boundaries}`.
- Out: `{service_map, claim_registry[], provenance{source_ids[], output_hash}}`.
- Gate: no invented offer. Status: DOCUMENTED_ONLY.

## AG-02 Competitor Research
- In: `{competitor_urls[], dated_observations[]}`.
- Out: `{ledger[50]{name, url, date, format, hook, metrics, limitations}, gaps[], coverage{verified_count, missing[]}}`.
- Gate: provenance + coverage; shortfall reported exactly. Status: IMPLEMENTED_DISCONNECTED.

## AG-03 Buyer Research
- In: `{buyer_questions[], interviews[], public_pain_evidence[]}`.
- Out: `{personas[], pain_clusters[], objections[], hypotheses[] (labelled as hypotheses)}`.
- Gate: hypothesis separated from evidence. Status: DOCUMENTED_ONLY.

## AG-04 Market Research
- In: `{dated_studies[], geographic_scope}`.
- Out: `{trend_brief, insights[{text, date, geography, limitations}], observed_vs_hypothesised}`.
- Gate: freshness + geography. Status: DOCUMENTED_ONLY.

## AG-05 Keyword Research
- In: `{topic, source_data}`.
- Out: `{keywords[{term, type, intent, source, locale, platform, icp, funnel, validation_status, date}]}` — exactly one `type=primary`.
- Gate: primary uniqueness + evidence; unsourced volume rejected.
- Code: `modules/topic_intelligence/keyword_research.py::validate_cluster` returns
  `[]` when valid, else error codes (`EXACTLY_ONE_PRIMARY`, `UNSOURCED_VOLUME`, …).
- Status: IMPLEMENTED_DISCONNECTED.

## AG-06 Search Intent
- In: `{keyword_cluster, buyer_question}`.
- Out: `{intent_map[{keyword, intent, funnel_stage}]}`.
- Gate: relevance. Status: IMPLEMENTED_DISCONNECTED.

## AG-07 Topic Intelligence
- In: `{topic_library[], new_ideas[], evidence[]}`.
- Out: `{topics[{id, score, status: READY|ENRICH|RESEARCH_NEEDED|HOLD, history[], provenance}]}`.
- Gate: no destructive delete. Status: IMPLEMENTED_DISCONNECTED (partial).

## AG-08 Content Strategy
- In: `{topics[], constraints, icp, offer_map, research_findings}`.
- Out: `{plan{slots[7], promotion_slot (exactly 1)}, hypotheses[], measurement_plan}`.
- Gate: one promotion per complete week.
- Code: `modules/marketing_strategy/validate_strategy_v33.py::validate` returns
  error list (`Seven planning slots required`, `Exactly one promotional slot required`, …).
- Status: IMPLEMENTED_DISCONNECTED.

## AG-09 Funnel Planning
- In: `{personas[], plan}`.
- Out: `{allocation{content_id, funnel_stage: TOFU|MOFU|BOFU, formula, cta}}`.
- Gate: stage/CTA consistency. Status: IMPLEMENTED_DISCONNECTED.

## AG-10 Content Writer
- In: `{approved_brief, verified_facts[], buyer_vocabulary}`.
- Out: `{caption, cta_variants[], hook, answer, explanation, takeaway, limitations}`.
- Gate: no unsupported claims; every claim carries `source_ids[]`.
- Code: `modules/linkedin_copywriting/content_engine.py::gate` returns
  `{decision: READY_FOR_OWNER_REVIEW|REJECT|NOT_VERIFIED|BLOCKED, input_sha256}`.
- Status: IMPLEMENTED_DISCONNECTED.

## AG-11 SEO Optimization
- In: `{draft, keyword_cluster}`.
- Out: `{revised_draft}` (natural inclusion; evidence preserved).
- Gate: no keyword stuffing. Status: IMPLEMENTED_DISCONNECTED.

## AG-12 Editorial Review
- In: `{draft, target_audience}`.
- Out: `{verdict: PASS|REVISE|BLOCKED, observations[] (non-empty), reviewer, subject_hash, timestamp}`.
- Gate: actionable + understandable; reviewer ≠ producer.
- Code: review stages in `core/gate_chain_v41.py`. Status: IMPLEMENTED_CONNECTED (as gate role).

## AG-13 Fact Checker
- In: `{source_registry, claims[{text, source_ids[]}]}`.
- Out: `{verdict: PASS|BLOCKED|NOT_VERIFIED, evidence[]}`.
- Gate: independent source checks; a URL alone is not verification.
- Code: review stages in `core/gate_chain_v41.py`. Status: IMPLEMENTED_CONNECTED (as gate role).

## AG-14 Creative Director
- In: `{post_message, brand_tokens, format}`.
- Out: `{brief{content_id, content_hash, poster_text{headline, footer}, dimensions:[1080,1350], brand, template_id, positioning, funnel_stage, design_rationale, negative_constraints}}`.
- Gate: brand constraints; brief binds to content hash.
- Code: `modules/creative_brief/brief_prompt_gate.py`. Status: IMPLEMENTED_DISCONNECTED.

## AG-15 Image Producer
- In: `{approved_brief, permitted_assets[]}`.
- Out: `{image_path, image_sha256, dimensions:[1080,1350], format:PNG, mode:RGB|RGBA, copy_ledger_hash, font_provenance{}}`.
- Gate: file existence; bytes hash matches manifest; copy ledger matches brief.
- Code: `rendering/brand_render_v37.py`, `rendering/website_render_v38.py`,
  `rendering/render_poster.py`. Status: PARTIALLY_IMPLEMENTED (no live image-gen adapter).

## AG-16 Brand QA
- In: `{render_path, manifest}`.
- Out: `{receipt: PASS|BLOCKED|NOT_VERIFIED, image_sha256, plan_hash, checks{font, palette, footer, logo, positioning}}`.
- Gate: verified logo/fonts/readability; logo present → original-logo check,
  absent → absence check.
- Code: `modules/brand_claims_qa/brand_policy_v36.py`, `website_brand_v38.py`;
  `core/gate_chain_v41.py` BRAND_REVIEW. Status: IMPLEMENTED_CONNECTED (as gate role).

## AG-17 Delivery Controller
- In: `{approvals[], receipts[17 stages]}`.
- Out: `{package: READY_FOR_OWNER_REVIEW, delivery_sha256} | {handoff (only with separate explicit permission + readback)}`.
- Gate: explicit scope + readback; `READY_FOR_OWNER_REVIEW` ≠ owner approval.
- Code: `core/gate_chain_v41.py` DELIVERY; `core/chatgpt_bridge_v43.py`;
  `core/batch_guard_v45.py`; `core/evidence_store.py::can_handoff`.
- Status: IMPLEMENTED_CONNECTED (external writes NOT_CONFIGURED and blocked).

## AG-18 Analytics
- In: `{observed_metrics[], attribution, time_window, post_tags[]}`.
- Out: `{report{impressions, reach, saves, comments, clicks, enquiries, meetings, conversions, missing_fields[], confounders[]}, learnings[], decisions[]}`.
- Gate: no invented attribution; no synthetic reach/leads.
- Code: `modules/analytics_learning/linkedin_analytics.py`. Status: IMPLEMENTED_DISCONNECTED.
