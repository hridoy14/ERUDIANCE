# Erudience v3 — One action, multi-format evidence-first content production

## Scope and execution policy
Master action `@Erudience linkedin image` accepts optional `topic`, `category`, `month`, `platforms`, `formats`, `cadence`, `brand`, `model_preference`, `batch_size`, `approval_scope`, `output_mode`. Defaults are *proposals*, not evidence. No remote write without explicit authorization. For each input, validate schemas, source provenance, claims, account access and brand assets. Never claim perfect accuracy.

## Routing by category and format
Categories: buyer_pain, education, market_research, campaign, thought_leadership, case_study, trend, product_update. Formats: text, image, flowchart, carousel, document, campaign_poster, market_research_poster, trend_poster. Choose format from buyer intent and evidence density, not aesthetics alone. Brand variation may change layout, diagram, whitespace, typography scale, visual motif; never substitute unverified brand colours, fonts, logo or positioning.

## First-to-last pipeline
1. INPUT_SCHEMA: reject unknown categories/unsupported formats and malformed dates.
2. SOURCE_DISCOVERY: search only authorized public pages and connected first-party sources; store source_id, URL, publisher, published_at, retrieved_at, exact supported claim, credibility, limitations. No private scraping or platform bypass.
3. BUYER_INTELLIGENCE: map verbatim observations to buyer roles, pains, job-to-be-done, evidence strength (OBSERVED, CORROBORATED, VALIDATED_FOR_ICP). Do not infer market prevalence from anecdotes.
4. RESEARCH_CONTROLLER: reject fabricated/unlinked sources and unsupported statistics; NOT_VERIFIED blocks factual claims.
5. MONTHLY_CALENDAR: dates, platform(s), topic/title, pillar/funnel, primary format, derivatives, SEO and LinkedIn keyword targets, source references, CTA, status, campaign, UTM.
6. WEEKLY_REFRESH: recheck source freshness, policy, actual analytics if connected, schedule collisions; version plan. Seven scheduled slots in one session only when explicitly requested.
7. CONTENT_WRITER: OpenAI or Claude if authenticated, else connected available model; produce original draft and 1-3 hook variations. Model agreement is not evidence.
8. CONTENT_CONTROLLER: inspect buyer relevance, accuracy, evidence citations, originality, readability, brand voice, funnel fit and platform policies.
9. CREATIVE_BRIEF: for each approved content item, infer headline, visual thesis, hierarchy, composition, required brand assets, copy locks, accessible contrast and dimensions.
10. PROMPT_ENGINEER: build structured positive and negative instructions with source references and immutable copy; compare prompt hash to brief hash.
11. FORMAT_ROUTER: text-only -> no image; image/flowchart/poster -> renderer; carousel/document -> multi-page document pipeline, never claim a single PNG equals a carousel.
12. IMAGE_QA: mechanical checks, human/vision visual review, text accuracy, brand provenance, image-copy alignment; max 3 bounded repairs per stage then ESCALATE.
13. BATCH_CONTROLLER: all requested items must pass individually; batch failures cannot be hidden by average score.
14. OWNER_REVIEW: explicit per-item or enumerated batch approval; record exact hashes.
15. SOCIAL_OS_HANDOFF: require separate write permission and verified endpoint/connector. Create draft and media, then read back exact record. Scheduling requires separate explicit authorization. Do not guess URLs or credentials.
16. ANALYTICS_LOOP: only actual published metrics; measure qualified engagements, UTM clicks, enquiries and meetings; update next weekly hypotheses without fabricated outcomes.

## State machine
PLANNED -> RESEARCHED -> EVIDENCE_VERIFIED -> WRITTEN -> CONTENT_APPROVED -> BRIEF_APPROVED -> PROMPT_APPROVED -> RENDERED -> VISUAL_VERIFIED -> OWNER_APPROVED -> UPLOAD_AUTHORIZED -> REMOTE_VERIFIED -> SCHEDULED_VERIFIED (if separately authorized). Any failed gate -> BLOCKED; upstream mutation invalidates downstream hashes and approvals. For text-only, visual stages are NOT_APPLICABLE, never fake PASS.

## Failure logic
If missing buyer data, mark hypothesis and block ungrounded numerical claims. If missing research sources, research or ask owner for first-party records. If missing brand asset, output review draft only. If model API unavailable, use available model with provenance; do not claim provider use. If no Social OS adapter, produce export bundle and BLOCK remote state. If endpoint 401/403, stop; never bypass access. If rate-limited, back off; never spin indefinitely. If record mismatches on read-back, reject and require fresh approval for remote changes. Use idempotency key per content/version. Never silently publish.

## Required calendar record
`content_id`, `publish_date`, `platforms`, `topic`, `title`, `pillar`, `funnel_stage`, `primary_format`, `derivatives`, `keywords`, `buyer_pain`, `cta`, `sources`, `claims`, `copy`, `brand_id`, optional `category`, `campaign_id`, `utm`, `timezone`, `status`, `variations`, `analytics`. Research claims must reference existing source_ids. Week and monthly views derive from publish_date, not duplicate manually maintained calendars.

## Endpoints
Read `references/endpoint-registry.json`. External provider endpoints are contracts, not proof of account connectivity. Social OS paths intentionally null until verified from code/OpenAPI or live UI; endpoint discovery is a required implementation gate, not permission to invent routes.
