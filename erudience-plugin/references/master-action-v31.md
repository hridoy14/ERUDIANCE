# Master action orchestration v3.1
Public trigger: `@Erudience` (also accept legacy `@Erudience linkedin image`). Default intent if no other words: produce next 7-day LinkedIn B2B research-backed content plan and drafts; no remote writes. Never ask user to paste a long command. Inputs optional: topic, category, platform, count, start_date, timezone, formats, model, brand, approval. Interpret user natural language.

## Action registry (internal only)
research.collect -> buyer.extract -> evidence.verify -> calendar.plan -> calendar.review -> content.write -> content.review -> creative.brief -> creative.review -> prompt.build -> prompt.review -> format.route -> assets.verify -> render.execute -> visual.verify -> batch.reconcile -> owner.review -> social_os.authorize -> social_os.upload -> social_os.readback -> analytics.feedback.
Each action contract: action_id, input_schema, output_schema, dependencies, guard, status, evidence_refs, content_id, input_hash, output_hash, timestamp, attempts. Status one of PASS, BLOCKED, NOT_VERIFIED, NOT_APPLICABLE. Guard forbids next action when prerequisite not PASS except explicit NOT_APPLICABLE branch. Missing external capability is NOT_VERIFIED, never PASS.

## Dispatcher and branches
- `plan` / `week` / default: collect research -> buyer pain -> evidence -> seven-item calendar -> 7 original drafts -> content QA -> format-appropriate creative briefs and prompts -> actual assets if supported -> final report.
- `month`: 30-day calendar, schedule only explicitly chosen cadence; create weekly drafts only if requested.
- `text`: skip image stages with NOT_APPLICABLE.
- `image`, `flowchart`, `campaign_poster`, `market_research_poster`, `trend_poster`: require verified brand assets and real render+QA.
- `carousel`, `document`: require true multipage output and per-page QA, not a single image substitute.
- `case_study`: demand explicit client approval and verified results; otherwise block case-study claims.
- `trend`: current dated research required; otherwise do not claim trend status.
- `social_os`: read-only by default; write only after explicit owner approval for exact records and operation; schedule/publish separate approval.
- `claude`: only claim Claude use when authenticated provider actually invoked; otherwise use available model with disclosure.

## Deterministic loop
For each content_id in ordered calendar: run dependency actions; for each failed repairable stage retry up to 3 with fresh validation and hashes; stop item after 3 and mark BLOCKED. Never auto-retry authorization, authentication, legal approval, or unavailable evidence. Reconcile batch, list each failed item, never imply complete if missing assets. Source changes invalidate downstream gates. Controller is independent from generator and must check actual artifacts, not self-reported success.

## Provider endpoints
Internal action names above are logical interfaces, not publicly reachable HTTP routes. Read `references/endpoint-registry.json` for known provider contracts. No made-up external endpoints. Before calling any provider, discover actual connected tool and verify scope, schema, credential, response and read-back. Local Python scripts are helper programs, not automatic cloud endpoints.

## Preservation and compatibility
Preserve and apply previous research, branding, source policy, controller, image production, monthly/weekly, Social OS and analytics reference files. This file supersedes only trigger ergonomics and action dispatch. Do not delete previous features. This plugin's packaged Python scripts do not execute automatically merely because a ChatGPT prompt mentions them: call actual runtime/tool when available; report capability gaps.
