# Agent Registry — Erudience Plugin (canonical)

Branch: `architecture/erudience-unified-consolidation` (baseline `main@9e320fa`, v4.9.2).
Sources: `agents/roles-v34.md` (role table — the authoritative role spec),
`references/system-architecture-v34.md` §"18 specialist roles",
`references/orchestrator-v2.md` (strategy engine + build/controller steps 1–14).

Status key: DOCUMENTED_ONLY = logical role defined in docs, no code;
IMPLEMENTED_DISCONNECTED = code exists but is not wired into the master
workflow (`core/gate_chain_v41.py` / `core/chatgpt_bridge_v43.py`);
IMPLEMENTED_CONNECTED = code is wired into the master workflow.
No agent is claimed as an independently deployed autonomous service.

Non-negotiables (from `agents/roles-v34.md`): no fabricated competitor
metrics, buyer quotes, rankings, testimonials, ROI, service capability or
client results; no claims of successful remote action without readback;
never store secrets in files or logs; block unsupported external writes;
each agent records source IDs, output hash and uncertainty; the controller
validates rather than trusting agent self-certification. No agent may
self-certify its own production output.

## AG-01 — Business Intelligence Agent
- Purpose: derive the verified service map from the verified portfolio.
- Source: `agents/roles-v34.md`; module: business_service_intelligence.
- Input schema: verified business docs, offer readiness, service boundaries.
- Output schema: service and claim registry (scoped result + provenance).
- Allowed tools/modules: `core/evidence_store.py` (provenance); read-only evidence.
- Dependencies: owner-verified portfolio; no upstream agent.
- Routing: first in research; handoff to AG-02/AG-03 with the service map.
- Handoff contract: service map + provenance receipt (source IDs, output hash).
- Validation: independently check evidence, scope and owner policy; no invented offer.
- Evidence: source IDs, output hash, uncertainty recorded.
- Failure: missing/unverified offer → BLOCKED, return to SOURCES.
- Retry: max 3 repairs per stage, BLOCKED on 4th (`core/gate_chain_v41.py`).
- Output owner: Business Intelligence Agent; independent reviewer: AG-13 Fact Checker.
- Status: DOCUMENTED_ONLY (module has no code; see agent-implementation-status.md).

## AG-02 — Competitor Research Agent
- Purpose: build the 50-record competitor evidence dataset.
- Source: `agents/roles-v34.md`; module: competitor_intelligence.
- Input schema: public competitor URLs + dated observations.
- Output schema: 50-company evidence ledger with gaps (15 direct, 10 niche,
  10 platforms, 10 content benchmarks, 5 emerging); exact shortfall reported, never filled.
- Allowed tools/modules: `modules/competitor_intelligence/competitor_monitor.py`
  (accepts source-backed records; never scrapes or schedules itself).
- Dependencies: AG-01 service map; public sources.
- Routing: research group, parallel with AG-03/AG-04 after AG-01.
- Handoff contract: evidence ledger + coverage report → AG-07/AG-08.
- Validation: provenance and coverage; no copying competitor posts/images.
- Evidence: URL, date, format, hook, visible metrics, limitations per record.
- Failure: <50 verified → report exact count and missing coverage; unverified record → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Competitor Research Agent; independent reviewer: AG-13.
- Status: IMPLEMENTED_DISCONNECTED (code exists; integration-tests-only).

## AG-03 — Buyer Research Agent
- Purpose: build buyer personas and pain clusters from permitted signals.
- Source: `agents/roles-v34.md`; module: buyer_intelligence.
- Input schema: buyer questions, interviews, public pain evidence.
- Output schema: question/pain/objection clusters; hypothesis separated from evidence.
- Allowed tools/modules: none implemented; research contracts in `references/`.
- Dependencies: AG-01 service map; AG-02 competitor context.
- Routing: research group, parallel with AG-02/AG-04.
- Handoff contract: persona/pain clusters → AG-06/AG-07/AG-08.
- Validation: hypothesis separated from evidence; no invented buyer quotes.
- Evidence: source IDs per pain/question; uncertainty recorded.
- Failure: unsupported pain claim → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Buyer Research Agent; independent reviewer: AG-13.
- Status: DOCUMENTED_ONLY.

## AG-04 — Market Research Agent
- Purpose: dated market trend brief with geography and limitations.
- Source: `agents/roles-v34.md`; module: market_trends.
- Input schema: dated market studies, geographic scope.
- Output schema: dated insights with limitations; observed vs hypothesised distinguished.
- Allowed tools/modules: none implemented; spec in `references/strategy-playbook.md`.
- Dependencies: AG-01/AG-02/AG-03 findings.
- Routing: research group; feeds AG-07/AG-08.
- Handoff contract: trend brief → AG-08.
- Validation: freshness and geography; stale sources are not current claims.
- Evidence: source date, retrieval date, geography, sample, expiry/recheck status.
- Failure: stale or undated source used as current claim → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Market Research Agent; independent reviewer: AG-13.
- Status: DOCUMENTED_ONLY.

## AG-05 — Keyword Research Agent
- Purpose: typed keyword clusters with provenance.
- Source: `agents/roles-v34.md`; module: topic_intelligence.
- Input schema: topic + source data.
- Output schema: typed keyword cluster (primary/secondary/semantic/long_tail/
  problem/question/informational/commercial/transactional/branded/competitor/
  industry/geographic/entity/negative); exactly one primary per cluster.
- Allowed tools/modules: `modules/topic_intelligence/keyword_research.py`
  (`validate_cluster`, `map_content`, `normalize`); no volume/difficulty inference
  without an identified tool and source.
- Dependencies: AG-01 topic + AG-02/AG-03 evidence.
- Routing: research → strategy boundary; feeds AG-06 and AG-11.
- Handoff contract: cluster + validation status → AG-06/AG-08/AG-11.
- Validation: primary uniqueness and evidence; unsourced volume rejected.
- Evidence: term, type, intent, source, locale, platform, ICP, funnel, date.
- Failure: zero or multiple primaries, duplicate term, unsourced volume → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Keyword Research Agent; independent reviewer: AG-11 (SEO) + AG-13.
- Status: IMPLEMENTED_DISCONNECTED (code exists; integration-tests-only).

## AG-06 — Search Intent Agent
- Purpose: intent/funnel map from cluster + buyer question.
- Source: `agents/roles-v34.md`; module: topic_intelligence.
- Input schema: keyword cluster + buyer question.
- Output schema: intent/funnel map (informational/commercial/transactional/navigational).
- Allowed tools/modules: `modules/topic_intelligence/linkedin_seo_validator.py`
  (natural keyword inclusion, funnel and claim evidence; does not predict rankings).
- Dependencies: AG-05 cluster; AG-03 buyer questions.
- Routing: research → strategy; feeds AG-08/AG-09.
- Handoff contract: intent map → AG-09.
- Validation: relevance to buyer question and funnel stage.
- Evidence: cluster reference + buyer question source.
- Failure: intent unsupported by cluster → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Search Intent Agent; independent reviewer: AG-11.
- Status: IMPLEMENTED_DISCONNECTED.

## AG-07 — Topic Intelligence Agent
- Purpose: scored, versioned topic registry; never delete topic knowledge.
- Source: `agents/roles-v34.md`; module: topic_intelligence.
- Input schema: existing library + new ideas/evidence.
- Output schema: ranked enriched topic records (READY / ENRICH / RESEARCH_NEEDED / HOLD).
- Allowed tools/modules: `modules/topic_intelligence/keyword_research.py`;
  preservation enforced by `modules/marketing_strategy/validate_strategy_v33.py`
  (topic deletion forbidden) and `core/gate_chain_v41.py`.
- Dependencies: AG-02/AG-03/AG-04/AG-05 outputs.
- Routing: research → strategy; feeds AG-08.
- Handoff contract: scored topic records → AG-08.
- Validation: no destructive delete; duplicates are non-destructive links.
- Evidence: topic ID, history, provenance preserved per record.
- Failure: topic deletion attempted → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Topic Intelligence Agent; independent reviewer: AG-08.
- Status: IMPLEMENTED_DISCONNECTED (partial: validation code exists, no registry store).

## AG-08 — Content Strategy Agent
- Purpose: 7-slot weekly plan with exactly one promotion.
- Source: `agents/roles-v34.md`; module: marketing_strategy.
- Input schema: topics + constraints (ICP, offer map, research findings).
- Output schema: campaign hypotheses + measurement plan; seven-slot calendar.
- Allowed tools/modules: `modules/marketing_strategy/validate_strategy_v33.py`
  (7 slots, exactly 1 promotion, employee requirement on promotion,
  no direct pitch in educational slots, no unverified image).
- Dependencies: AG-07 topics; AG-05/AG-06; AG-04 trends.
- Routing: strategy group lead; feeds AG-09/AG-10.
- Handoff contract: approved 7-slot plan → AG-09.
- Validation: one promotion per complete week; partial weeks preserve the rule.
- Evidence: plan hash, slot allocation, promotion justification.
- Failure: promotion count ≠ 1, educational slot sells, missing employee
  requirement → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Content Strategy Agent; independent reviewer: AG-12.
- Status: IMPLEMENTED_DISCONNECTED (validator exists; no planner code).

## AG-09 — Funnel Planning Agent
- Purpose: TOFU/MOFU/BOFU allocation with stage/CTA consistency.
- Source: `agents/roles-v34.md`; module: funnel_planning.
- Input schema: personas + plan.
- Output schema: TOFU/MOFU/BOFU allocation; content formula per stage
  (Problem-Cause-Fix TOFU; Question-Answer-Evidence intent-led;
  Comparison-Tradeoff-Decision MOFU; Objection-Explanation-Next Step BOFU).
- Allowed tools/modules: funnel logic inside
  `modules/linkedin_copywriting/content_engine.py` (`funnel_stage`, `weekly_batch`).
- Dependencies: AG-08 plan; AG-03 personas; AG-06 intent map.
- Routing: strategy group; feeds AG-10.
- Handoff contract: funnel allocation → AG-10.
- Validation: stage/CTA consistency; formula never forced at clarity's cost.
- Evidence: stage per content ID.
- Failure: stage/CTA mismatch → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Funnel Planning Agent; independent reviewer: AG-12.
- Status: IMPLEMENTED_DISCONNECTED (logic inside content_engine, not a separate agent).

## AG-10 — Content Writer Agent
- Purpose: original LinkedIn caption from the approved brief.
- Source: `agents/roles-v34.md`; module: linkedin_copywriting.
- Input schema: approved brief, verified facts, buyer vocabulary.
- Output schema: LinkedIn copy + CTA variants (hook, direct answer, credible
  explanation, practical takeaway, limitations, one contextual CTA).
- Allowed tools/modules: `modules/linkedin_copywriting/content_engine.py`
  (`validate`, `route`, `gate`, `calendar`, `weekly_batch`); claim→source binding.
- Dependencies: AG-08 plan; AG-09 funnel; AG-13 evidence.
- Routing: content group; feeds AG-11/AG-12/AG-13.
- Handoff contract: draft + claim/source bindings → AG-12/AG-13.
- Validation: no unsupported claims; no fabricated clients/cases/pricing.
- Evidence: source IDs + source dates per claim; input SHA256.
- Failure: unsupported claim, missing evidence → BLOCKED (REJECT/NOT_VERIFIED).
- Retry: max 3, BLOCKED on 4th.
- Output owner: Content Writer Agent; independent reviewer: AG-12 + AG-13.
- Status: IMPLEMENTED_DISCONNECTED (offline workflow code exists; not wired to the gate).

## AG-11 — SEO Optimization Agent
- Purpose: natural-language revision; no keyword stuffing.
- Source: `agents/roles-v34.md`; module: topic_intelligence.
- Input schema: draft + keyword cluster.
- Output schema: revised draft with natural keyword inclusion.
- Allowed tools/modules: `modules/topic_intelligence/linkedin_seo_validator.py`.
- Dependencies: AG-10 draft; AG-05 cluster.
- Routing: content group, after AG-10, before AG-12.
- Handoff contract: revised draft → AG-12.
- Validation: no keyword stuffing; funnel and claim evidence preserved.
- Evidence: revision diff + cluster reference.
- Failure: stuffing or lost evidence → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: SEO Optimization Agent; independent reviewer: AG-12.
- Status: IMPLEMENTED_DISCONNECTED.

## AG-12 — Editorial Review Agent
- Purpose: clarity verdict — actionable and understandable.
- Source: `agents/roles-v34.md`; review group.
- Input schema: draft + target audience.
- Output schema: clarity verdict (PASS / REVISE / BLOCKED) with observations.
- Allowed tools/modules: review stages in `core/gate_chain_v41.py`
  (CONTENT_REVIEW, STRATEGY_REVIEW); reviewer role enforced.
- Dependencies: AG-10/AG-11 output.
- Routing: review group; gates AG-10 output before AG-14.
- Handoff contract: verdict + observations → AG-14 or back to AG-10.
- Validation: actionable and understandable; observations list non-empty.
- Evidence: reviewer identity, subject hash, timestamp.
- Failure: unclear draft → REVISE (max 3) then BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Editorial Review Agent; independent reviewer: AG-13 (facts) — AG-12 never reviews its own output.
- Status: IMPLEMENTED_CONNECTED (as gate review roles, not as a standalone service).

## AG-13 — Fact Checker Agent
- Purpose: evidence verdict from independent source checks.
- Source: `agents/roles-v34.md`; review group.
- Input schema: source registry + claims.
- Output schema: evidence verdict (PASS / BLOCKED / NOT_VERIFIED).
- Allowed tools/modules: `core/gate_chain_v41.py` review verification;
  `core/evidence_store.py` (provenance).
- Dependencies: AG-10 claims; AG-01/AG-02 source registry.
- Routing: review group; independent of AG-10/AG-11/AG-12.
- Handoff contract: verdict → AG-14 or back to AG-10.
- Validation: independent source checks; URL alone is not verification.
- Evidence: source IDs, verification dates, hashes.
- Failure: unsupported claim → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Fact Checker Agent; independent reviewer: none may review
  their own work — AG-13 verdicts are re-checked by the controller, not by AG-13.
- Status: IMPLEMENTED_CONNECTED (as gate review roles).

## AG-14 — Creative Director Agent
- Purpose: creative brief from verified copy + brand.
- Source: `agents/roles-v34.md`; module: creative_brief.
- Input schema: post message, brand tokens, chosen format.
- Output schema: format-specific creative specification (poster text, brand,
  template, funnel, positioning, content hash, dimensions 1080×1350).
- Allowed tools/modules: `modules/creative_brief/brief_prompt_gate.py`
  (brief SHA, exact-copy match, 1080×1350, logo SHA256 required, font files verified).
- Dependencies: AG-10 verified copy; AG-16 brand tokens; AG-08 plan.
- Routing: creative group lead; content must be locked before this stage.
- Handoff contract: brief + content hash binding → AG-15.
- Validation: brand constraints; brief binds to content artifact hash.
- Evidence: brief SHA, content hash, poster text.
- Failure: brief/caption mismatch, missing brand token → BLOCKED, return to IMAGE_PLAN.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Creative Director Agent; independent reviewer: AG-16.
- Status: IMPLEMENTED_DISCONNECTED (gate code exists, no test).

## AG-15 — Image Producer Agent
- Purpose: actual render file from brief + permitted assets.
- Source: `agents/roles-v34.md`; module: image_generation.
- Input schema: approved brief + licensed/permitted assets.
- Output schema: rendered PNG file (exactly 1080×1350, 4:5, RGB/RGBA) + copy ledger
  + image SHA256 + font provenance.
- Allowed tools/modules: `rendering/brand_render_v37.py` (Sora, production),
  `rendering/website_render_v38.py` (website-first), `rendering/render_poster.py`
  (deterministic review draft). No live image-generation adapter exists.
- Dependencies: AG-14 brief; AG-16 verified assets.
- Routing: creative group; feeds AG-16.
- Handoff contract: PNG + SHA256 + manifest → AG-16.
- Validation: file existence; dimensions; image bytes hash matches manifest;
  copy ledger matches brief poster text.
- Evidence: image path, SHA256, dimensions, copy ledger hash.
- Failure: missing/unverified asset, wrong size, copy mismatch → BLOCKED, return to IMAGE_BUILD.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Image Producer Agent; independent reviewer: AG-16.
- Status: PARTIALLY_IMPLEMENTED (renderers exist; no live image-generation adapter;
  production renderer pins `social-os/BRAND.md:v1.1`, a file not in this repo — see policy-conflicts.md C18).

## AG-16 — Brand QA Agent
- Purpose: inspection receipt — verified logo/fonts/readability.
- Source: `agents/roles-v34.md`; module: brand_claims_qa.
- Input schema: render + manifest.
- Output schema: inspection receipt (PASS / BLOCKED / NOT_VERIFIED).
- Allowed tools/modules: `modules/brand_claims_qa/brand_policy_v36.py`
  (caption + poster-spec checks) and `website_brand_v38.py` (website-first spec);
  `core/gate_chain_v41.py` BRAND_REVIEW.
- Dependencies: AG-15 render; `config/production-policy-v33.json` (Sora, #10B77F).
- Routing: review group; gates AG-15 output before AG-17.
- Handoff contract: receipt → AG-17.
- Validation: verified logo/fonts/readability; footer, palette, positioning checked;
  logo present → original-logo check, absent → absence check.
- Evidence: reviewer identity, image SHA256, plan hash, pixel + mobile inspection.
- Failure: brand mismatch → BLOCKED, return to IMAGE_PLAN.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Brand QA Agent; independent reviewer: AG-17 (delivery) — AG-16 never approves its own render.
- Status: IMPLEMENTED_CONNECTED (as gate review roles; note the two brand modules
  conflict — see policy-conflicts.md C12 — and are preserved as-is, not merged).

## AG-17 — Delivery Controller Agent
- Purpose: review package or authorized handoff from approvals + receipts.
- Source: `agents/roles-v34.md`; module: approval_distribution.
- Input schema: approvals + receipts (all 17 stages).
- Output schema: review package (`READY_FOR_OWNER_REVIEW`) or authorized handoff.
- Allowed tools/modules: `core/gate_chain_v41.py` (DELIVERY gate),
  `core/chatgpt_bridge_v43.py` (durable checkpoints),
  `core/batch_guard_v45.py` (7-job batch), `core/evidence_store.py` (`can_handoff()`).
- Dependencies: all upstream agents; owner approval (explicit, never assumed).
- Routing: delivery group; terminal stage.
- Handoff contract: package + all receipts → owner; external write only with
  separate explicit permission + readback.
- Validation: explicit scope, readback; `READY_FOR_OWNER_REVIEW` ≠ owner approval.
- Evidence: all stage hashes, delivery SHA256 binding.
- Failure: missing approval/receipt → BLOCKED.
- Retry: max 3, BLOCKED on 4th.
- Output owner: Delivery Controller Agent; independent reviewer: the owner (human).
- Status: IMPLEMENTED_CONNECTED (gate + bridge + batch guard wired; external
  writes remain NOT_CONFIGURED and blocked).

## AG-18 — Analytics Agent
- Purpose: descriptive report from observed permitted metrics only.
- Source: `agents/roles-v34.md`; module: analytics_learning.
- Input schema: observed platform/site metrics with attribution.
- Output schema: performance learning + experiment decisions.
- Allowed tools/modules: `modules/analytics_learning/linkedin_analytics.py`
  (descriptive metrics only from observed authorized exports).
- Dependencies: AG-17 delivery; actual publishing by an authorised user/system.
- Routing: analytics group; after delivery; feeds back to AG-07/AG-08.
- Handoff contract: report → AG-07/AG-08 (feedback loop).
- Validation: no invented attribution; no synthetic reach or leads; like-for-like windows.
- Evidence: metric source, time window, UTM/post tags.
- Failure: unattributed metric → excluded, not invented.
- Retry: n/a (reporting only).
- Output owner: Analytics Agent; independent reviewer: AG-08 (strategy).
- Status: IMPLEMENTED_DISCONNECTED (code exists; no live metrics source).
