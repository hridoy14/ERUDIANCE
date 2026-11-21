# Erudience 4.1 Gate Contract

Stages in order: SOURCES -> SOURCE_REVIEW -> RESEARCH -> RESEARCH_REVIEW -> STRATEGY -> STRATEGY_REVIEW -> CONTENT -> CONTENT_REVIEW -> IMAGE_PLAN -> PLAN_REVIEW -> IMAGE_BUILD -> TECH_REVIEW -> VISUAL_REVIEW -> CONTENT_IMAGE_REVIEW -> BRAND_REVIEW -> FINAL_REVIEW -> DELIVERY.

Every output binds to immediate previous stage via upstream_hash. IMAGE_PLAN must also bind to the locked CONTENT hash and exact caption. IMAGE_BUILD must bind to the IMAGE_PLAN hash and copy ledger. Image QA must bind to actual image hash and plan hash. A reviewer must be registered as a reviewer adapter distinct from its subject's producer, and must provide observations, decision and exact subject hash. In live mode reviewer evidence must be a real file with verified SHA256; this does not itself authenticate a reviewer or prove semantic quality, so genuine independent review remains a required external integration.

Failure routes: SOURCE_REVIEW->SOURCES, RESEARCH_REVIEW->RESEARCH, STRATEGY_REVIEW->STRATEGY, CONTENT_REVIEW->CONTENT, PLAN_REVIEW->IMAGE_PLAN, TECH_REVIEW/VISUAL_REVIEW/FINAL_REVIEW->IMAGE_BUILD, CONTENT_IMAGE_REVIEW/BRAND_REVIEW->IMAGE_PLAN. Every rollback invalidates downstream records. Max three repairs; fourth failure BLOCKED. Missing adapter -> BLOCKED immediately. Only READY_FOR_OWNER_REVIEW after all 17 gates in non-fixture mode; never auto-publish.

Website brand: Inter headings, DM Sans body, paper #F6F1E9, ink #14120E, emerald #10B981, deep #0A6E3E, dark #0A100E, Erudience and erudience.com. Logo optional. The brand contract is checked at plan time, actual font binary provenance at render time and visual compliance by independent reviewer. Existing old Sora/mandatory-logo gates are historical only.

Endpoints: This package contains NO live API endpoints for research/LLM/image generation/visual reviewer. Those cannot be verified by unit tests. The plugin must not report production ready until adapters are registered and one real content-to-poster run passes, with independent visual review and real source evidence.
