# Erudience v3.3 — executable strategy contract

## Scope and precedence
This contract is mandatory for every `@Erudience` LinkedIn content or image action and supplements v3.2 without deleting prior skills, scripts, topics, records or source assets. Explicit user requests for other work do not silently grant external write permission. If older rules conflict, v3.3 wins for promotion frequency, topic preservation, research and QA. Display name is descriptive; preserve plugin identity and `@Erudience` invocation.

## Module IO, processing, quality gates and integrations
| Module | Input | Processing | Output | Quality gate | Integration |
|---|---|---|---|---|---|
| 01 business_service_intelligence | verified business docs, offer readiness, service boundaries | validate inputs → derive scoped result → record provenance | service and claim registry | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 02 competitor_intelligence | public competitor URLs and dated observations | validate inputs → derive scoped result → record provenance | 50-company evidence ledger with gaps | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 03 buyer_intelligence | buyer questions, interviews and public pain evidence | validate inputs → derive scoped result → record provenance | question/pain/objection clusters | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 04 market_trends | dated market studies and geographic scope | validate inputs → derive scoped result → record provenance | dated insights with limitations | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 05 topic_intelligence | preserved topic registry, new evidence | validate inputs → derive scoped result → record provenance | ranked enriched topic records | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 06 marketing_strategy | ICP, offer map, research findings | validate inputs → derive scoped result → record provenance | campaign hypotheses and measurement plan | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 07 funnel_planning | buyer stage, topic score, cadence | validate inputs → derive scoped result → record provenance | seven-slot calendar with one promotion slot | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 08 linkedin_copywriting | approved brief, verified facts, buyer vocabulary | validate inputs → derive scoped result → record provenance | LinkedIn copy and CTA variants | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 09 creative_brief | post message, brand tokens, chosen format | validate inputs → derive scoped result → record provenance | format-specific creative specification | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 10 image_generation | approved creative brief and licensed assets | validate inputs → derive scoped result → record provenance | rendered assets or BLOCKED receipt | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 11 brand_claims_qa | draft, sources, visual, brand references | validate inputs → derive scoped result → record provenance | independent PASS/BLOCKED/NOT_VERIFIED gates | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 12 approval_distribution | approved content ID and owner permission | validate inputs → derive scoped result → record provenance | approval receipt and optional authorized handoff | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 13 analytics_learning | observed platform/site metrics with attribution | validate inputs → derive scoped result → record provenance | performance learning and experiment decisions | independently check evidence, scope and owner policy | read-only stage receipt → next module |
| 14 knowledge_provenance | source registry, versions, run receipts | validate inputs → derive scoped result → record provenance | immutable audit/provenance record | independently check evidence, scope and owner policy | read-only stage receipt → next module |

## Eight production capabilities
1. Freshness control: record source date, retrieval date, geography, sample and expiry/recheck status. Stale sources are not current claims.
2. Competitor monitoring: target 50 unique relevant entities (15 direct, 10 niche, 10 platforms, 10 content benchmarks, 5 emerging); verify names and source links, audit positioning, target buyer, service, actual public LinkedIn examples, creative patterns, objections and content gaps. If fewer than 50 verified, report exact count and missing coverage; never fill with invented competitors. No copying competitor posts or images.
3. Topic preservation: no destructive deletes; preserve ID, history and provenance. READY, ENRICH, RESEARCH_NEEDED or HOLD; duplicate suggestions are non-destructive links, not deletion.
4. Asset management: use verified Erudience logo, approved color/font and licensed imagery; unknown assets block branded rendering, do not invent visual identity.
5. Mobile readability: test hierarchy, legibility, safe margins, accessible contrast and image/caption complementarity; captions must not be pasted in full on posters.
6. Experimentation: test one variable (hook, format, CTA) at a time where practical; log hypothesis and measured results, no fake A/B outcomes.
7. Feedback loop: distinguish impressions, engagement, meaningful replies, qualified enquiries and booked calls; avoid attribution beyond measured evidence.
8. Audit trail: preserve source IDs, drafts, versions, approval receipts, render receipts, status and authorized publishing outcomes.

## Weekly editorial hard rule
Seven planning slots are not seven mandated publications. Reserve EXACTLY ONE promotional slot per complete editorial week, tied to ONE service category, ONE niche and ONE narrow problem. Other six slots must be educational, Q&A, buyer pain, practical problem solving, AI skills, evidence-based insights, decision education or workflow ideas, with no direct service pitch. Existing Social OS default is four actual posts/week unless owner changes it; the promotional slot is part of those four when approved, never an additional fifth post. If the selected promotion lacks readiness or evidence, status HOLD (do not quietly create a second promotional post). Partial weeks preserve the calendar's single-promotion rule without inventing missing posts.

## Promotion specification (10 fields)
Service category; niche and buyer role; one small verified/hypothesized problem clearly labeled; root cause; manual baseline; proposed workflow and integration dependencies; exact automated actions; employee/human oversight requirement (never claim no employee needed universally); expected qualitative value and limitations (no fabricated ROI); one truthful CTA. Must identify when staff approval, fallback, privacy consent, telephony compliance, or booking reconciliation is necessary. Human involvement is context-dependent and must be explicitly answered.

## Research → content → creative pipeline
Resolve ICP and offer truth → collect buyer questions and public evidence → research top-50 competitor set with source ledger and coverage → preserve/enrich all existing topics → score relevance, practical value, evidence, novelty and funnel coverage → allocate 7 slots/1 promotion → draft original professional LinkedIn content (specific hook, direct answer, credible explanation, practical takeaway, limitations, one contextual CTA) → brief for poster/carousel/diagram → render using verified assets → inspect text/brand/format and independently fact-check → owner approval → only separately authorized scheduling/publishing → actual metrics feedback. Do not imply browsing, source collection, asset rendering, API calls, schedules or posts occurred if they did not.

## Content deliverables and blocking
Every content ID: date, pillar, persona, niche, problem/question, root-cause hypothesis, unique angle, buyer intent, funnel stage, service mapping (internal), source IDs and source dates, hook, answer, caption, CTA, visual format, creative brief, asset paths only if real, QA PASS/BLOCKED/NOT_VERIFIED, promotion flag, approval status, measured outcome if available. Every stage has independent controller and max three bounded revisions. No fabricated clients, case studies, pricing, guarantees or competitors. Block unsupported claims and unverified service offers; report precise gaps and manual work needed.

## Integration contracts
Website and Social OS GitHub are read-only evidence until verified live. Supabase schema documents do not establish live database state. External Social OS changes, posting, scheduling, contact outreach or analytics access require supported connections, explicit scoped authorization and read-back receipts. Local scripts are helper files, not live services. For image creation use actual available rendering capability and verify output; text prompts alone are not generated images.

## Acceptance checks
Fail if promotional count != 1 for a complete seven-slot plan, if any of six educational slots directly sells, if a topic is deleted, if 50 competitors are claimed without 50 grounded records, if employee requirement missing from promotion, if an image is claimed without render proof, if missing evidence passes QA, or if external writes occur without permission. PASS only for independently verifiable artifacts; otherwise NOT_VERIFIED or BLOCKED.
