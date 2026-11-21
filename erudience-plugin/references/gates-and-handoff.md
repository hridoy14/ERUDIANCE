# Fail-closed quality gates and Social OS handoff

## Receipt protocol
Each stage receives: `{job_id,content_id,version,input_hash,upstream_receipt_ids,requested_action,scope}`. It returns `{gate_id,stage,verdict:PASS|REJECT|NOT_VERIFIED,checks:[{id,expected,observed,evidence_ref,status}],output_hash,created_at,reviewer,reason,repair_owner}`. Only PASS + matching input/output hashes permits the next stage. Missing or stale receipt = DENY. A changed upstream payload invalidates dependent receipts. No '100%' badge if any mandatory check is NOT_VERIFIED.

## Gate matrix
G00 INPUT: content ID, objective, audience, user-approved or clearly draft copy.
G01 SOURCE: current repo brand, website fonts, logo provenance, platform policy sources checked; record access limits.
G02 RESEARCH: dated evidence ledger; competitor samples, observations vs hypotheses, source quality.
G03 STRATEGY: ICP, awareness stage, problem, offer, funnel, CTA, realistic measurable objective.
G04 CONTENT: factual claims backed; UK English; no fabricated results; approved source copy or draft label.
G05 PLAN: layout, hierarchy, mobile dimensions, CTA, exact copy and original visual strategy.
G06 ASSETS: actual official logo bytes and hash; Inter/DM Sans verified; correct usage rights; no altered logo.
G07 RENDER: actual PNG file exists, exact size, readable mode, deterministic copy ledger, safe margins.
G08 QA: automated tests + independent native/mobile visual review, text and link fidelity.
G09 BENCHMARK: if comparison claimed, both files visually inspected and scores evidenced; otherwise comparison NOT VERIFIED and do not claim superiority.
G10 CONTROLLER: all mandatory upstream gates PASS; score/risk report; deliver for owner review.
G11 OWNER: explicit approve/reject for exact content hash and version; no implicit approval.
G12 HANDOFF: schema compatibility and idempotency validated; *separate* explicit write permission and target record, allowed operation draft-only, read-after-write receipt.
G13 ANALYTICS: source-backed measurements after real publication; missing data not imputed.

## Approval policy
`controller=APPROVE_FOR_OWNER_REVIEW` is NOT owner approval. Owner approval is NOT Social OS write authorisation. Social OS draft creation is NOT scheduling or publishing. For any external write, confirm target repository/project/table, record and operation; stop if permissions or credentials are unavailable. If rejected, route to failed gate, apply correction, invalidate downstream receipts, rerun and resubmit. Do not auto-approve rejected work.

## Social OS payload (proposed adapter, not asserted current schema)
`{external_content_id,version,topic,channel:'linkedin',format:'single_image',caption_draft,image_sha256,image_file_or_url,brand_receipt_id,qa_receipt_id,owner_approval_receipt_id,status:'draft',idempotency_key}`. Before write, read actual schema, mapping, and permitted API, and show field-level mapping. If no compatible safe draft endpoint exists, output handoff JSON for manual review; do not invent one. No secrets stored in package.

## Independent quality rubric
Brand fidelity 20; buyer relevance 20; workflow/factual correctness 20; hierarchy 15; mobile readability 10; CTA 10; technical export 5. Critical blocker overrides score. Claim of Social OS superiority requires side-by-side audited original and new output plus meaningful real-world outcome data for performance superiority.
