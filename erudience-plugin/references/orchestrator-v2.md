# One-action execution orchestration — v2

## Input contract
`content_id`, `topic`, `source_article_or_brief`, `audience`, `offer`, `market`, `objective`, `channel=LinkedIn`, `format=single_image`, `brand=Erudience`, `owner`, `status=DRAFT`, `requested_batch_size` (default 1). If content calendar supplied, each item is independently versioned and processed. Do not silently invent claims or customer cases. If a topic is missing, propose a topic grounded in research and label it PROPOSED, not approved.

## Strategy engine
1. Verify brand and business source hierarchy, website CSS, official logo, current LinkedIn documentation and approved reference (read-only). Record fetched URL, timestamp, source version/commit if available, hash for binaries, and evidence status. Recheck at each run; cached copies are not 'current'.
2. Research current buyer pains, service-business sales operations, RevOps, response accountability; use public competitor examples with URL, date, format, hook, visible metrics and limitations. Trend classification must distinguish observed from hypothesised; never infer conversions from likes.
3. Build buyer map (ICP, buying role, pain, trigger, objection, desired outcome), positioning, educational offer, conversion path, lead qualification, funnel stages and tracking design. Verify any factual claim.
4. Build calendar: 30-day rolling plan with day, theme, awareness stage, hook, evidence, visual style, CTA, target buyer, funnel step, owner, status and experiment hypothesis. No posting cadence claimed optimal without data. User-supplied content plan → produce one image per content item after each gate.
5. Pick visual treatment: process, audit checklist, comparison, decision tree, diagnostic, myth-vs-fact, or research explainer. Check brand fit and current observed examples. Avoid copying protected layouts verbatim; use original compositions.
6. Produce locked copy and 1080x1350 creative brief. Review for truthful claims, buyer utility, legibility and CTA. Controller must approve the plan before render.

## Build and controller
7. Obtain original logo bytes (approved asset only) and approved fonts available locally or downloaded from authorised official sources. Do not redistribute fonts in plugin archive. Verify image/logo dimensions, alpha, file hash, permitted use. If no logo bytes, block brand-approved final; a draft without logo may still be made and labelled.
8. Render PNG with deterministic text/layout; optionally use image generation for an authorised illustrative element, never for exact logo or copy. Save source manifest, dimensions, colour mode, checksum and copy ledger.
9. Technical QA: decode PNG, exact dimensions, RGB/RGBA, file size, margins, OCR or direct text-layout audit, asset hashes, colour tokens, missing fields. Visual QA: inspect actual pixels at native size and mobile downsample, contrast, clipped text, grid and spacing. Automated checks supplement but do not replace human visual inspection.
10. Benchmark with real Social OS approved image only if downloaded and inspected. Use identical criteria; no invented scores. Controller issues APPROVE_FOR_OWNER_REVIEW, REVISE or BLOCK with gate receipts.
11. If REVISE: identify failed stage, revise that stage, invalidate all downstream gate receipts and rerun downstream stages; max three render attempts per item. If BLOCK: stop and state required remedy. No gate bypass by manual 'force pass'.
12. Owner reviews preview; record explicit APPROVE or REJECT with timestamp and content hash. On rejection, collect reason, repair, rerun gates, and request approval again. Owner approval is never assumed.
13. Social OS handoff: prepare an idempotent payload and read-only compatibility check first. After *separate* explicit permission, write only authorised draft record(s) using connected official tools/API; verify resulting record ID and read-after-write. Never auto-publish, auto-schedule, mutate approval flags, or change live workflows. On failure, stop and reconcile rather than blindly retry.
14. Analytics after actual publishing by authorised user/system: pull LinkedIn impressions, unique reach if available, saves, meaningful comments, website/profile clicks, qualified enquiries, meetings and conversions where permitted. Tag by post and UTM; compare like-for-like time windows; report missing fields, confounders and no guaranteed growth.

## 30-day planning schema
`day | publish_window_hypothesis | buyer | funnel_stage | pillar | verified_source | hook | format | CTA | content_id | status | image_file | gate_receipt | performance_id`.
Content pillars: lead response, sales handoff, CRM hygiene, service operations, AI automation governance, implementation checklists, case studies ONLY with approved proof, buyer objections, diagnostic audits.

## Allowed terminal states
`DRAFT`, `RESEARCH_BLOCKED`, `PLAN_REJECTED`, `RENDERED_UNVERIFIED`, `QA_REVISE`, `QA_BLOCKED`, `READY_FOR_OWNER_REVIEW`, `OWNER_REJECTED`, `OWNER_APPROVED`, `SOCIAL_OS_STAGED`, `SOCIAL_OS_WRITE_AUTHORISED`, `SOCIAL_OS_DRAFT_CREATED`, `MEASUREMENT_PENDING`. No status implies publishing.
