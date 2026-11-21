# Erudience v3.5 — execution and release contract

## Goal and boundaries
Create research-backed, buyer-relevant, SEO-conscious, on-brand LinkedIn captions and original branded creatives. Single action `@Erudience` must orchestrate research → evidence → keyword/intent → funnel/topic strategy → draft → factual/editorial/SEO review → verified creative brief → brand assets → render → visual inspection → delivery package. Do not treat a tool-generated image or LLM-written caption as evidence of plugin execution. The owner has explicitly deferred Social OS writes, approval portal integration, scheduling, and LinkedIn publishing. No such actions are authorized.

## Mandatory gates
1. Brand-first: load actual current website and Social OS brand rules; validate original logo bytes, font paths/rights, palette, brand voice and service claims before creative work. A brand name rendered as text is not a verified logo. No fake assets.
2. Research: source IDs, URLs, retrieval date, quotes/claim mapping; independent verification is required. A URL field alone is not verification.
3. Keywords: primary, secondary, semantic, intent, ICP, funnel and platform; do not invent search volume, difficulty or ranking guarantees.
4. Content: distinct buyer problem, service relevance, original insight, useful steps, suitable CTA, human oversight, no unsubstantiated metrics. Education-first; one planned service promotion per seven slots, hold if service readiness unverified.
5. Creative: enforce matching caption and creative brief; verified assets, exact copy, readable mobile typography, actual render file, inspection receipt, independent brand QA. If logo/fonts absent, block branded final and label any exploratory draft UNVERIFIED_DRAFT.
6. Receipts: stage, content_id, artifact path and SHA256, producer, independent reviewer, timestamp; production_gate.py validates file integrity and missing approvals. A PASS string alone never passes.
7. No fabricated autonomy: file-based scripts do not equal deployed agents, connected data providers, scheduler or image generation service. Report each adapter as CONFIGURED/NOT_CONFIGURED and real tests as PASS/BLOCKED/NOT_TESTED.
8. Handoff: deliver local files and audit report only; no Social OS, LinkedIn, Supabase or GitHub writes without new explicit permission.

## Acceptance
For each pilot, prove actual research provenance, content quality, exact branding, image output, independent QA, negative-path tests, repeatable execution. Current deployment cannot be called 100% production-ready until real external connectors and runtime are configured and end-to-end exercised. Preserve existing historical files and versioned records.
