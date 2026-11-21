# Erudience v3.4 Architecture — implementation and boundaries

## Execution contract
Public trigger: `@Erudience`. Trigger is manual unless an actual scheduler is connected and separately authorized. No implicit LinkedIn, Supabase, GitHub, image generation, or web API access. Read-only default. Every external integration has a separately configured adapter, credential scope, error handling, rate limit, and readback verification; absent adapters are BLOCKED, not mocked.

## Workflow graph
RESEARCH -> KEYWORDS -> STRATEGY -> DRAFT -> FACT_QA -> SEO_QA -> CREATIVE -> VISUAL_QA -> OWNER_APPROVAL -> DELIVERY -> ANALYTICS. Each transition requires an independently recorded receipt with content ID, input hash, evidence references, output artifact path, reviewer, timestamp, and PASS/BLOCKED/NOT_VERIFIED. No stage self-certification. Preserve topic history and prior approved artifacts; revisions create new versions.

## 18 specialist roles (logical roles; not claimed as deployed autonomous services)
Business intelligence; competitor research; buyer research; market research; keyword research; search intent; topic intelligence; content strategist; funnel planner; content writer; SEO optimizer; editorial reviewer; fact checker; creative director; image producer; brand QA; delivery controller; analytics. See `agents/roles-v34.md` for detailed ownership and handoffs. Logical roles can run in one orchestrator or separate agents. Deterministic validators must not be replaced by model self-assessment.

## Connections and dependencies
- `scripts/competitor_monitor.py` accepts source-backed records; never scrapes or schedules itself. Output feeds research and strategy.
- `scripts/keyword_research.py` validates typed keyword clusters and provenance for any asserted volumes. Output feeds `scripts/linkedin_seo_validator.py` and copywriting.
- `scripts/linkedin_seo_validator.py` checks natural keyword inclusion, funnel and claim evidence. It does not predict LinkedIn rankings.
- `scripts/workflow_engine.py` enforces batch IDs, promotion limit, human oversight and stage receipts; it does not write remotely.
- `scripts/linkedin_analytics.py` computes descriptive metrics only from observed authorized exports; no synthetic reach or leads.
- `scripts/integration_tests.py` tests the local contracts and negative cases.
- Existing `scripts/content_engine.py`, `scripts/render_poster.py`, evidence and brand gates remain available; their functionality must be tested with real assets before a production claim.

## Keyword taxonomy
primary, secondary, semantic, long_tail, problem, question, informational, commercial, transactional, branded, competitor, industry, geographic, entity, negative. Each entry stores term, type, intent, source (if externally measured), locale, platform, ICP, funnel, validation status, date. Do not infer search volume or keyword difficulty without an identified tool and source. LinkedIn search is not equivalent to Google SEO.

## Content formula router
Problem-Cause-Fix for TOFU education; Question-Answer-Evidence for intent-led education; checklist and framework for actionable posts; Comparison-Tradeoff-Decision for MOFU; Objection-Explanation-Next Step for BOFU; PAS and AIDA only where genuinely helpful. Every output includes target role, buyer problem, primary keyword, semantic support, angle, evidence, limitations, CTA, format, version and status. Never force a formula at the cost of clarity.

## Weekly governance
Seven editorial planning slots, exactly one direct-service promotional slot; if readiness fails, hold the promotional slot and do not publish it. Four approved posts per week is the prior default publishing cadence, not a scheduled job. Monthly planning boundary Asia/Dhaka on the 21st. No topic deletion. No automatic external writes, scheduling or publication. Three repair cycles max per stage; block and report otherwise.

## External integration prerequisites
For LinkedIn: approved app permissions, OAuth, token lifecycle, API endpoint eligibility, rate limits, posting rights and readback. For Supabase: schema, RLS, least-privilege keys, migrations, secrets manager, idempotency and audit. For research: approved public sources and ToS-compliant retrieval. For images: verified logo, font rights, render engine, actual asset files and visual inspection. For scheduling: explicit scheduler service, timezone, deduplication and failure alerts. None of these are provisioned by adding a local file.

## Definition of done
All tests green, source registry verified, real end-to-end execution through each connected adapter, independent brand review, explicit approval, observed readback, incident recovery, logs, and documented operating procedures. Never state 100% readiness until evidence exists for every gate.
