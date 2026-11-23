# Auth Validation Rules — Gates, Approval, Endpoints, Compatibility, ChatGPT Runtime

Consolidated 2026-11-24 (Worker C, Erudiance references consolidation, owner-authorized).
Merged from: gate-contract-v41.md [v41], gates-and-handoff.md [gates],
release-audit-v34.md [v34], release-compatibility-v48.md [v48],
runtime-and-compatibility-v49.md [v49], chatgpt-runtime-v43.md [v43],
chat-vision-audit-v35.md [v35], and the gate/auth/validation sections of
master-command-v6.md [v6-gate]. Every rule below carries its source tag.
Conflicting rules are kept side by side with a CONFLICT note; the owner
decides later. Nothing was silently rewritten or dropped.

## 1. Verified brand tokens used in this file

1.1. [v41] Verified live erudience.com, 2026-11-24: Sora headings and body
(Sora only), paper #F6F1E9, ink #14120E, emerald #10B77F, deep #0C8D62,
dark #080C0B, Erudience and erudience.com. Logo optional; only the original
owner-approved JPG logo may be used, unchanged.

1.2. [v41] The brand contract is checked at plan time, actual font binary
provenance at render time, and visual compliance by independent reviewer.

1.3. [v41] Existing old Inter / DM Sans / #10B981 gates are historical only.

1.4. STALE-TOKEN RULE (merge rule, Worker C): wherever a source file in this
merge still says Inter, DM Sans, or #10B981, the text is carried verbatim
with a [STALE — superseded by verified website tokens 2026-11-24] note. It
was not silently rewritten. See rules 9.3, 9.4, 10.4, 15.5 and CONFLICT C1.

## 2. The 17-stage gate chain

2.1. [v41] Stages in order: SOURCES -> SOURCE_REVIEW -> RESEARCH ->
RESEARCH_REVIEW -> STRATEGY -> STRATEGY_REVIEW -> CONTENT -> CONTENT_REVIEW
-> IMAGE_PLAN -> PLAN_REVIEW -> IMAGE_BUILD -> TECH_REVIEW -> VISUAL_REVIEW
-> CONTENT_IMAGE_REVIEW -> BRAND_REVIEW -> FINAL_REVIEW -> DELIVERY.

2.2. [v41] Only READY_FOR_OWNER_REVIEW after all 17 gates in non-fixture
mode; never auto-publish.

2.3. [v43] Repeat stages until READY_FOR_OWNER_REVIEW, TEST_FIXTURE_PASS,
or BLOCKED. A failed gate rewinds, invalidates downstream records, and
demands re-execution. Never bypass failure by editing receipt text.

2.4. [v43] A test fixture's terminal status is TEST_FIXTURE_PASS, never
production approval. [v48] Never call a mock fixture a live integration test.

2.5. [v35] Seven planning slots, four previously planned publishing slots
subject to approval. (Slot counts are planning slots, not a publishing
mandate; see also rule 7.4.)

## 3. Receipt protocol and hash binding

3.1. [gates] Each stage receives: `{job_id, content_id, version, input_hash,
upstream_receipt_ids, requested_action, scope}`. It returns: `{gate_id,
stage, verdict: PASS | REJECT | NOT_VERIFIED, checks: [{id, expected,
observed, evidence_ref, status}], output_hash, created_at, reviewer, reason,
repair_owner}`.

3.2. [gates] Only PASS + matching input/output hashes permits the next
stage. Missing or stale receipt = DENY. A changed upstream payload
invalidates dependent receipts.

3.3. [gates] No '100%' badge if any mandatory check is NOT_VERIFIED.

3.4. [v41] Every output binds to its immediate previous stage via
upstream_hash. IMAGE_PLAN must also bind to the locked CONTENT hash and
exact caption. IMAGE_BUILD must bind to the IMAGE_PLAN hash and copy ledger.
Image QA must bind to actual image hash and plan hash.

3.5. [v41] A reviewer must be registered as a reviewer adapter distinct from
its subject's producer, and must provide observations, decision, and exact
subject hash.

3.6. [v41] In live mode reviewer evidence must be a real file with verified
SHA256; this does not itself authenticate a reviewer or prove semantic
quality, so genuine independent review remains a required external
integration.

3.7. [v43] Live SOURCES require actual URL, verified_at, source_sha256.
Every reviewer requires a separate inspected evidence file and its real
SHA256.

3.8. [v43] IMAGE_BUILD needs real 1080x1350 PNG hash, exact plan and poster
ledger hash, and verified font files (see rule 9.4 and CONFLICT C1).

3.9. [v35] Receipt PASS without file integrity is a defect, not evidence.
Weak self-asserted brand_verified is a defect.

## 4. Gate matrix G00–G13

4.1. [gates] G00 INPUT: content ID, objective, audience, user-approved or
clearly draft copy.

4.2. [gates] G01 SOURCE: current repo brand, website fonts, logo provenance,
platform policy sources checked; record access limits.

4.3. [gates] G02 RESEARCH: dated evidence ledger; competitor samples,
observations vs hypotheses, source quality.

4.4. [gates] G03 STRATEGY: ICP, awareness stage, problem, offer, funnel,
CTA, realistic measurable objective.

4.5. [gates] G04 CONTENT: factual claims backed; UK English; no fabricated
results; approved source copy or draft label.

4.6. [gates] G05 PLAN: layout, hierarchy, mobile dimensions, CTA, exact copy
and original visual strategy.

4.7. [gates] G06 ASSETS: actual official logo bytes and hash; Inter / DM Sans
verified [STALE — superseded by verified website tokens 2026-11-24; see
CONFLICT C1]; correct usage rights; no altered logo.

4.8. [gates] G07 RENDER: actual PNG file exists, exact size, readable mode,
deterministic copy ledger, safe margins.

4.9. [gates] G08 QA: automated tests + independent native/mobile visual
review, text and link fidelity.

4.10. [gates] G09 BENCHMARK: if comparison claimed, both files visually
inspected and scores evidenced; otherwise comparison NOT VERIFIED and do not
claim superiority.

4.11. [gates] G10 CONTROLLER: all mandatory upstream gates PASS; score/risk
report; deliver for owner review.

4.12. [gates] G11 OWNER: explicit approve/reject for exact content hash and
version; no implicit approval.

4.13. [gates] G12 HANDOFF: schema compatibility and idempotency validated;
*separate* explicit write permission and target record, allowed operation
draft-only, read-after-write receipt.

4.14. [gates] G13 ANALYTICS: source-backed measurements after real
publication; missing data not imputed.

4.15. CONFLICT C2 — gate-system count: [v41] and [v43] define a 17-stage
chain (section 2), while [gates] defines a 14-gate matrix G00–G13 (this
section). Both are carried as written; they are different gate systems, not
a typo. Owner decides which is canonical. (The historical 13-stage v39/v40
chain is a third system, recorded in execution-state-machine-v40 sources
held by other workers, not merged here.)

## 5. Failure routes, repairs, BLOCKED

5.1. [v41] Failure routes: SOURCE_REVIEW -> SOURCES, RESEARCH_REVIEW ->
RESEARCH, STRATEGY_REVIEW -> STRATEGY, CONTENT_REVIEW -> CONTENT,
PLAN_REVIEW -> IMAGE_PLAN, TECH_REVIEW / VISUAL_REVIEW / FINAL_REVIEW ->
IMAGE_BUILD, CONTENT_IMAGE_REVIEW / BRAND_REVIEW -> IMAGE_PLAN. Every
rollback invalidates downstream records.

5.2. [v41] Max three repairs; fourth failure BLOCKED. Missing adapter ->
BLOCKED immediately.

5.3. [v43] All gates are fail-closed. Do not fabricate a source, tool
execution, review, or image metadata.

5.4. [v48] Every update must: (1) list prior file paths and compare with
post-update inventory, (2) execute tests for bridge, gate, batch guard and
current brand, (3) reject incomplete poster_text or logo provenance,
(4) verify real source and font evidence, (5) perform one live
content-to-image review before production approval.

5.5. [v49] Release process: list plugin files before/after, preserve omitted
assets, assert canonical import edges, run bridge, batch and brand-policy
regression tests, test both logo-present and logo-absent plans, check
mandatory poster copy, and test missing fonts / reviewer evidence blocks.

5.6. [v6-gate] Failure handling — no blind retries: GitHub inaccessible ->
identify repository/path, continue with verified known instructions, mark
current-source audit incomplete. Original logo inaccessible -> no invented
logo; review draft only; brand approval BLOCKED. DM Sans unavailable -> seek
authorised source; if still missing, render labelled fallback and block
exact-font approval. [STALE — superseded by verified website tokens
2026-11-24; see CONFLICT C1.] Benchmark download fails -> report precise
HTTP/tool error; do not pretend visual comparison. Image generator
unavailable -> use deterministic renderer if possible; do not stop at prompt.
Text overflows -> reflow, resize within readability thresholds, or adjust
layout; do not omit stages. CTA verification fails -> retain user-supplied
URL but mark link verification pending. Market research blocked -> use
labelled hypothesis, no fabricated demand claims. Export/inspection fails ->
do not provide fabricated attachment or dimensions.

5.7. [v6-gate] Do not repeatedly fetch the same inaccessible resource without
a changed retrieval method. (Carried from one-action-production-contract
gate practice via [v6-gate] execution order; see rule 5.6.)

## 6. Reviewer independence and evidence

6.1. [v41] A reviewer must be registered as a reviewer adapter distinct from
its subject's producer (rule 3.5). In live mode reviewer evidence must be a
real file with verified SHA256 (rule 3.6).

6.2. [v43] A model-generated receipt alone does not prove independent review.
Visual reviewer must inspect image pixels at full and mobile scale. Image
plan must match locked caption exactly and website brand spec.

6.3. [v35] Observed failure: assistant used direct image generation outside
the plugin orchestrator, produced generic palette/logo wordmark, then
reported component-level PASS. This is not plugin E2E evidence. Correct
status: REJECTED_FOR_PRODUCTION.

6.4. [v35] Mitigation: v3.5 adds fail-closed independent artifact integrity
and brand gate, authoritative skill policy, explicit execution and acceptance
contracts, negative tests. Existing v3.4 modules remain, but live external
automation remains unverified.

6.5. [v35] Defects register (all still open as defects unless a later gate
closes them): weak self-asserted brand_verified; receipt PASS without file
integrity; logo/font path not verified; competitor target 50 but dataset
absent; keyword validator is not live research; analytics is not connected;
scheduler and Social OS handoff not configured; visual QA not executed; no
live content-image pipeline.

6.6. [v6-gate] Verify exact words against the exported image, not only
source code. For every issue record defect, severity, correction, and
reinspection result. If blocked, provide usable review draft and transparent
status; never falsely mark APPROVED.

6.7. [v6-gate] Inspect real output bytes: PNG signature, width=1080,
height=1350, RGB/RGBA, sRGB profile if available, file size,
transparent/opaque background as intended, safe margins, logo fidelity, font
metadata, visual hierarchy, and mobile-width screenshot. Provide only actual
measurements. Do not call an uninspected render "pixel-perfect".

## 7. Approval policy — controller vs owner vs Social OS

7.1. [gates] `controller=APPROVE_FOR_OWNER_REVIEW` is NOT owner approval.
Owner approval is NOT Social OS write authorisation. Social OS draft
creation is NOT scheduling or publishing.

7.2. [gates] For any external write, confirm target repository/project/table,
record and operation; stop if permissions or credentials are unavailable.

7.3. [gates] If rejected, route to failed gate, apply correction, invalidate
downstream receipts, rerun and resubmit. Do not auto-approve rejected work.

7.4. [v41] READY_FOR_OWNER_REVIEW does not imply publishing. [v43] Do not
auto-publish.

7.5. [v6-gate] Status remains REVIEW DRAFT until owner approval and all
critical checks pass. Request owner approval before any publication. Do not
claim that a system command has been installed or a task has been completed
without evidence.

7.6. [v6-gate] Delivery: show actual generated image directly in chat first,
then provide a clickable link to the verified local PNG when file support
permits. After image provide: selected design direction; verified
filename/dimensions/format/file size; website font evidence and exact
installed fonts; genuine logo provenance or blocker; source checks; six-stage
copy check; mobile QA; original-vs-new comparison with NOT VERIFIED where
appropriate; all critical issues; status `APPROVE`, `REVISE`, or `BLOCK`.

7.7. [v6-gate] `APPROVE` means ready for owner's review, not permission to
publish. No claim of 100% market success.

## 8. Social OS handoff and write authorisation

8.1. [gates] Social OS payload (proposed adapter, not asserted current
schema): `{external_content_id, version, topic, channel: 'linkedin', format:
'single_image', caption_draft, image_sha256, image_file_or_url,
brand_receipt_id, qa_receipt_id, owner_approval_receipt_id, status: 'draft',
idempotency_key}`. Before write, read actual schema, mapping, and permitted
API, and show field-level mapping. If no compatible safe draft endpoint
exists, output handoff JSON for manual review; do not invent one. No secrets
stored in package.

8.2. [gates] G12 HANDOFF (rule 4.13): schema compatibility and idempotency
validated; *separate* explicit write permission and target record, allowed
operation draft-only, read-after-write receipt.

8.3. [v35] Deferred: social.erudience.com existing storage, approval workflow
and LinkedIn auto-publishing. Do not create tables or modify portal until
owner provides mapping and authorizes it.

8.4. [v43] Later Supabase / Social OS integration is a separate authorized
adapter project.

8.5. [v6-gate] Post-publication test is OPTIONAL ONLY: suggest a future
consent-based performance evaluation, but do not publish or schedule:
compare qualified enquiries, website clicks, meaningful comments, saves,
impressions, and reach over comparable audiences/time windows, with tracked
links where appropriate. Account for caption, timing, audience, and
distribution confounders. Never invent a benchmark or guarantee results.

## 9. Brand validation at gates

9.1. [v41] Website brand (verified live erudience.com, 2026-11-24): Sora
headings and body (Sora only), paper #F6F1E9, ink #14120E, emerald #10B77F,
deep #0C8D62, dark #080C0B, Erudience and erudience.com. Logo optional; only
the original owner-approved JPG logo may be used, unchanged.

9.2. [v48] The logo is optional; if a logo is used, the exact original
owner-approved logo must be composited unchanged after illustration
generation. If the Sora font binary is missing, final rendering and
production approval are BLOCKED; a fallback preview must be explicitly
labelled DRAFT.

9.3. [v6-gate] CONFLICT C1 — fonts: [v6-gate] mandates Inter + DM Sans for
the website-matched poster ("Sora is excluded", "No Sora on this
website-matched poster", Inter ExtraBold 800 headline, Inter Bold 700
section headings, Inter SemiBold 600 CTA, DM Sans 400–500 support copy,
DM Sans 600 category label) and states the user explicitly chose the
Erudience WEBSITE font system (Inter + DM Sans) over Sora. [STALE —
superseded by verified website tokens 2026-11-24: Sora only, emerald
#10B77F.] The [v6-gate] text is carried verbatim below in rules 9.3a–9.3d
because the merge rule forbids dropping a conflicting rule; the verified
tokens in rule 9.1 govern until the owner decides.

9.3a. [v6-gate] Website CSS previously inspected from
`erudience-main/src/index.css` contains Google Fonts imports for DM Sans and
Inter; the body uses `font-family: 'DM Sans', 'Inter', sans-serif`; headings
h1–h6 use `font-family: 'Inter', sans-serif`. `tailwind.config.ts`
similarly defines `sans: ['DM Sans','Inter','sans-serif']` and `heading:
['Inter','sans-serif']`. Recheck current files before claiming this is still
live. [STALE — superseded by verified website tokens 2026-11-24.]

9.3b. [v6-gate] If exact DM Sans is unavailable locally, obtain a
legitimately served font from the official Google Fonts CSS endpoint or
another trusted authorised source; if retrieval fails, use Inter temporarily
and label FONT FIDELITY BLOCKED, not final. Inspect font metadata; don't
infer the font from appearance or filename alone. No font substitution,
synthetic italic, text raster artefacts, stretched letters, or unsupported
glyphs. [STALE — superseded by verified website tokens 2026-11-24.]

9.3c. [v6-gate] If a genuine font file cannot be accessed, stop exact-font
approval and disclose the fallback. Never label a fallback as exact.
[STALE — font family superseded by verified website tokens 2026-11-24; the
no-silent-fallback principle itself is retained.]

9.3d. [v6-gate] Source priority / conflict resolution: (1) explicit current
owner instruction in this conversation; (2) verified current website font
implementation for THIS independent website-matched poster; (3)
owner-approved Social OS BRAND.md and related agent guidelines for non-font
identity rules; (4) verified genuine assets from the website repository;
(5) current primary-source platform documentation; (6) evidence-based market
examples and design judgment. If a conflict arises, name it and state the
applied precedence. Do not silently blend font systems. [STALE as to font
choice — superseded by verified website tokens 2026-11-24; the precedence
procedure itself is retained.]

9.4. [v43] IMAGE_BUILD needs verified Inter / DM Sans font files. [STALE —
superseded by verified website tokens 2026-11-24: Sora only. See CONFLICT
C1.] The same sentence in [gates] G06 (rule 4.7) carries the same STALE note.

9.5. [v6-gate] Brand palette lock as stated in [v6-gate]: Paper #F6F1E9; Ink
#14120E; Emerald #10B981; Deep Green #0A6E3E; Ink Soft #615B4C;
Near-Black Green #0A100E; Mint `hsl(158 64% 72%)`. [STALE as to Emerald
#10B981 — superseded by verified emerald #10B77F, 2026-11-24; the other
tokens match the verified set except Deep Green, which the verified set
records as #0C8D62 — see CONFLICT C3.]

9.6. CONFLICT C3 — Deep Green: [v6-gate] and [gates]-era sources record Deep
Green #0A6E3E; [v41] verified deep is #0C8D62. Both carried; verified token
(#0C8D62) governs until owner decides.

9.7. [v6-gate] Original logo / asset provenance: read genuine website
repository assets at `src/assets/logo-horizontal.png`,
`src/assets/erudience-icon.png`, and verify `src/assets/logo-icon.jpg`
before assuming it exists. Download/inspect binary and preserve aspect
ratio, colour, transparency, sharpness, clear space. Use the official
horizontal logo in footer only if accessible. Do not regenerate, redraw,
approximate, recolour, distort, or invent a brand logo. If genuine binary is
unavailable, create a clearly labelled REVIEW DRAFT without fake logo; final
brand approval BLOCKED.

9.8. CONFLICT C4 — logo required vs logo optional: [v6-gate] (rule 9.7) and
[v6-gate] visual-QA blockers treat a missing/fabricated logo presented as
final as a critical blocker and brand approval BLOCKED. [v41] (rule 9.1) and
[v48] (rule 9.2) state the logo is OPTIONAL; if used, only the original
owner-approved logo, unchanged. Both carried; owner decides. (Note:
owner-approved-brand-v46, held by another worker, separately states the
owner now requires the bundled logo on new posters — that rule lives in the
brand target file, not here.)

9.9. [v35] Nonnegotiable: authentic Erudience website branding in BOTH copy
and visual, human oversight, no invented ROI/cases, topical preservation,
explicit provenance, no unauthorized external changes.

9.10. [v35] Vision: Erudience SMB-first LinkedIn content intelligence and
image production; original, research-led, keyword- and buyer-intent-aligned,
educational content with one weekly promotion; seven planning slots, four
previously planned publishing slots subject to approval.

## 10. Render and image validation

10.1. [gates] G07 RENDER (rule 4.8): actual PNG file exists, exact size,
readable mode, deterministic copy ledger, safe margins. G08 QA (rule 4.9):
automated tests + independent native/mobile visual review, text and link
fidelity.

10.2. [v43] Image plan must match locked caption exactly and website brand
spec. Visual reviewer must inspect image pixels at full and mobile scale.

10.3. [v6-gate] Render pipeline (gate/auth-relevant parts only; creative and
copy parts belong to the content/image targets): render using a deterministic
design engine (e.g. SVG+headless browser, Pillow, Canvas, or Canva) for
exact text and original assets. An image-generation model may propose a
decorative visual direction but MUST NOT be trusted to spell the workflow,
reproduce logo, or match exact fonts. Export independent PNG to a verified
actual path; never claim a path exists until the file is written and checked.
Inspect the exported image visually and programmatically. Re-render as
needed. Never mutate Social OS or publish.

10.4. [v6-gate] Load actual Inter and DM Sans files. Measure line lengths
and adjust text boxes, not the copy. [STALE — superseded by verified
website tokens 2026-11-24: Sora only. See CONFLICT C1.]

10.5. [v6-gate] LinkedIn platform / official specs: verify current official
LinkedIn image requirements at
https://www.linkedin.com/help/linkedin/answer/a527229/share-photos-or-videos?lang=en
. Target 1080×1350, PNG, sRGB/RGB, 4:5; aim under 5MB if appropriate but
don't claim this is the only allowable format or size. Validate export
dimensions, file signature, profile, file size, crop, safe margins, and
mobile preview.

10.6. [v6-gate] Critical visual-QA blockers: missing or fabricated logo
presented as final; wrong website font without disclosure; wrong brand
colours; missing/duplicate/out-of-order stages; text misspelling;
clipped/overlapping text; illegible mobile copy; broken CTA; fake
performance claim; wrong file dimensions/format. (Logo blocker subject to
CONFLICT C4; font blocker subject to CONFLICT C1.)

10.7. [v6-gate] Never substitute a description, mock link, or generated
prompt for an actual image. Mark every unperformed verification as
NOT VERIFIED.

## 11. Benchmark and comparison validation

11.1. [gates] G09 BENCHMARK (rule 4.10): if comparison claimed, both files
visually inspected and scores evidenced; otherwise comparison NOT VERIFIED
and do not claim superiority.

11.2. [v6-gate] Approved benchmark: download, inspect actual bytes,
dimensions and image contents of the original approved Social OS poster URL
recorded in [v6-gate]; if blocked, mark BENCHMARK VISUAL COMPARISON
UNVERIFIED, without inventing scores. Metadata does not prove visual quality.

11.3. [v6-gate] Comparison rubric (same rubric for both images): Brand
identity 20; Buyer relevance 20; Workflow accuracy 20; Visual hierarchy 15;
Mobile readability 10; CTA 10; Technical quality 5 (total 100). Score only
what was inspected and explain each criterion with visible evidence. If
benchmark inaccessible, mark original NOT VERIFIED and do not invent a
comparative total. A higher subjective design score does not prove better
impressions, qualified leads, or conversions.

11.4. [gates] Claim of Social OS superiority requires side-by-side audited
original and new output plus meaningful real-world outcome data for
performance superiority.

11.5. [v6-gate] Market research: do not infer lead conversion from likes or
claim algorithm preference without credible evidence. If access is
unavailable, label MARKET DEMAND UNVERIFIED and proceed with a clearly
identified hypothesis.

## 12. Release audit findings and open blockers

12.1. [v34] Confirmed pre-upgrade findings: `scripts/validate_strategy_v33.py`
had 8 policy tests, but tested only a narrow set of boolean fields and did
not validate keyword clusters, intent, provenance, external integration or
actual rendering.

12.2. [v34] `scripts/content_engine.py` verifies selected fields and claim
source IDs, but a supplied source URL is not independently fetched;
`brand_verified` is a caller-provided flag and is not cryptographic evidence
of brand authenticity.

12.3. [v34] `scripts/render_poster.py` exists, but real rendering and visual
QA have not been verified for the new release.

12.4. [v34] Top 50 competitor research target existed as policy, not a
populated verified dataset.

12.5. [v34] `@Erudience` is a declared skill trigger, not proof that a
scheduler, LinkedIn connector or cloud runtime is installed.

12.6. [v34] Prior 35-file package contained a compiled `__pycache__`
artifact; exclude it from future clean full builds when archive migration is
available.

12.7. [v34] Changes in v3.4 overlay: five requested specialist modules plus
an explicit local workflow engine, tests, role ownership and dependency
documentation. Local tests include negative paths for fabricated metrics,
missing provenance, duplicate keywords, unsupported writes and unverified
receipts.

12.8. [v34] Open deployment blockers: no connected production LinkedIn API
adapter, live analytics readback, persistent job queue, real scheduler,
authenticated research pipeline, complete 50-competitor dataset, confirmed
brand assets, render inspection or live E2E verification. Therefore
production readiness is NOT VERIFIED.

## 13. Compatibility and no-silent-bypass policy

13.1. [v48] Preserve all legacy files and original binary assets during
overlay updates. File preservation is NOT runtime compatibility: older
scripts may still import or call legacy validators.

13.2. [v48] The canonical gate_chain_v41.py now enforces the current
logo-optional brand policy and content-to-poster requirements;
chatgpt_bridge_v43.py imports it directly, so the same checks apply at
bridge submission. batch_guard_v45.py imports chatgpt_bridge_v43.py,
preserving the single controller path.

13.3. [v48] Legacy scripts may remain for compatibility but are not
independently authoritative. Do not delete or rename their import paths
without a migration and tests. A ZIP overlay cannot itself create background
automation or persistent connectors.

13.4. [v49] Single canonical validator: `scripts/gate_chain_v41.py` (stable
import path). Do not create versioned replacement controllers.
`scripts/chatgpt_bridge_v43.py` imports `gate_chain_v41`;
`scripts/batch_guard_v45.py` imports `chatgpt_bridge_v43`. Old
`production_controller_v39.py` and `workflow_engine.py` are archived
compatibility code, NOT active paths. Do not remove them without checking all
callers; no promise of active integration for every historical script.

13.5. [v49] The ZIP update does not provision scheduler, API credentials,
persistence or runtime automation.

13.6. [v49] One-content command may run without any external integration
configured, using available ChatGPT tools and local rendering. It must still
distinguish a draft from fully validated 17-stage production approval.

13.7. [v49] Live production approval requires real research, actual poster
and independent visual evidence.

## 14. Canonical runtime paths and imports

14.1. [v49] Canonical import edges (assert in release process, rule 5.5):
gate_chain_v41 <- chatgpt_bridge_v43 <- batch_guard_v45. [v48] Same edges,
stated as: chatgpt_bridge_v43.py imports gate_chain_v41 directly;
batch_guard_v45.py imports chatgpt_bridge_v43.py.

14.2. [v48] The canonical gate_chain_v41.py enforces the current
logo-optional brand policy (subject to CONFLICT C4) and content-to-poster
requirements.

14.3. [v34] Local tests include negative paths for fabricated metrics,
missing provenance, duplicate keywords, unsupported writes and unverified
receipts (rule 12.7).

## 15. ChatGPT runtime contract

15.1. [v43] ChatGPT is the external tool orchestrator.
`scripts/chatgpt_bridge_v43.py` is the durable local checkpoint/state
machine, and `scripts/gate_chain_v41.py` is the authoritative gate validator.
ChatGPT tool calls are not callable directly from installed Python scripts.
Never imply that installing a plugin ZIP creates a permanent service,
autonomous background process, or API credentials.

15.2. [v43] Execution steps: (1) Start job with
`python scripts/chatgpt_bridge_v43.py start --state JOB.json --job
JOB_INPUT.json`. (2) Call `next --state JOB.json`; inspect the stage and its
hashes. (3) Execute the actual stage with ChatGPT tools: web/research for
SOURCES; reasoning/writing for strategy/content/plan; image_gen or
deterministic renderer for IMAGE_BUILD; independent actual pixel inspection
for visual QA. (4) Save tool output with real evidence/provenance to
RECEIPT.json. Submit `submit --state JOB.json --stage STAGE --adapter NAME
--role producer|reviewer --receipt RECEIPT.json`. (5) Repeat until
READY_FOR_OWNER_REVIEW, TEST_FIXTURE_PASS or BLOCKED.

15.3. [v43] This update implements the checkpoint bridge and tests, not
automatic invocation of ChatGPT tools from Python. Connected providers must
be used through ChatGPT's supported tool calls in the live session. A real
end-to-end run is not established by local tests. No persistent unattended
runtime is promised.

15.4. [v43] Evidence requirements (see also section 3): live SOURCES require
actual URL, verified_at, source_sha256; every reviewer requires separate
inspected evidence file and its real SHA256; IMAGE_BUILD needs real
1080x1350 PNG hash, exact plan and poster ledger hash, and verified font
files.

15.5. [v43] IMAGE_BUILD font requirement as written in [v43]: "verified
Inter/DM Sans font files". [STALE — superseded by verified website tokens
2026-11-24: Sora only. See CONFLICT C1.]

15.6. [v43] Boundaries: do not auto-publish. No persistent unattended runtime
is promised. Later Supabase/Social OS integration is a separate authorized
adapter project (rule 8.4).

15.7. [v6-gate] Permissions / read-only / no side effects: treat GitHub,
Supabase, Social OS workflows, image jobs, content, approval records, and
published assets as READ-ONLY. No commit, push, DB update, deployment,
publishing, scheduling, or approval-state change. Create independent output
files only. Never upload credentials or expose private tokens. No silent side
effects.

15.8. [v6-gate] Execution order: `/VERIFY_OWNER_INSTRUCTION` ->
`/VERIFY_WEBSITE_FONTS` -> `/VERIFY_SOCIAL_OS_BRAND` ->
`/FETCH_OFFICIAL_LOGO` -> `/FETCH_APPROVED_BENCHMARK` ->
`/VERIFY_LINKEDIN_SPECS` -> `/RESEARCH_MARKET` -> `/DEFINE_BUYER_JOB` ->
`/SELECT_STYLE` -> `/LOCK_COPY` -> `/LOAD_INTER_DM_SANS` -> `/LAYOUT` ->
`/RENDER_REAL_PNG` -> `/VERIFY_FILE_BYTES` -> `/VISUAL_INSPECTION` ->
`/MOBILE_QA` -> `/CORRECT_AND_RERENDER` -> `/COMPARE_WITH_BENCHMARK` ->
`/SHOW_IMAGE_IN_CHAT` -> `/ATTACH_VERIFIED_PNG` -> `/QA_REPORT` ->
`/REQUEST_OWNER_APPROVAL`. (Step names carried verbatim, including
`/LOAD_INTER_DM_SANS` and `/VERIFY_WEBSITE_FONTS`; the font steps are
subject to CONFLICT C1 / STALE note in rule 9.3.)

## 16. Endpoints, integrations, and compatibility status

16.1. [v41] Endpoints: this package contains NO live API endpoints for
research / LLM / image generation / visual reviewer. Those cannot be verified
by unit tests. The plugin must not report production ready until adapters are
registered and one real content-to-poster run passes, with independent visual
review and real source evidence.

16.2. [v43] ChatGPT tool calls are not callable directly from installed
Python scripts (rule 15.1). Connected providers must be used through
ChatGPT's supported tool calls in the live session.

16.3. [v48] A ZIP overlay cannot itself create background automation or
persistent connectors (rule 13.3). [v49] The ZIP update does not provision
scheduler, API credentials, persistence or runtime automation (rule 13.5).

16.4. Endpoint registry status (merge note, Worker C): the endpoint and
integration registries stay as JSON — `references/endpoint-registry.json`
and `references/integration-registry-v34.json` — and are NOT merged into this
file, because code reads them by path. Recorded honestly from the
coordinator's grep evidence: no code file loads `endpoint-registry.json`
(grep for "endpoint-registry" outside reports/ finds only docs; registry/JSON
loads in core/, modules/, rendering/, server/ find only state files and the
in-code ProviderRegistry / AGENT_REGISTRY, not the JSON files). It is kept by
parent instruction and because README.md references it, NOT by a code load.
`integration-registry-v34.json` has ZERO references anywhere outside
reports/*.md. All six integrations in it are NOT_CONFIGURED, read-only, and
require approval. Nothing in this file changes that status.

16.5. [v34] Open deployment blockers (rule 12.8) restated as endpoint status:
no connected production LinkedIn API adapter, live analytics readback,
persistent job queue, real scheduler, authenticated research pipeline,
complete 50-competitor dataset, confirmed brand assets, render inspection or
live E2E verification. Production readiness is NOT VERIFIED.

16.6. [v35] Scheduler and Social OS handoff not configured; analytics is not
connected (rule 6.5). [v43] No persistent unattended runtime is promised
(rule 15.3).

## 17. Independent quality rubric

17.1. [gates] Independent quality rubric: Brand fidelity 20; buyer relevance
20; workflow/factual correctness 20; hierarchy 15; mobile readability 10;
CTA 10; technical export 5. Critical blocker overrides score.

17.2. [v6-gate] Comparison rubric (same weights, different labels): Brand
identity 20; Buyer relevance 20; Workflow accuracy 20; Visual hierarchy 15;
Mobile readability 10; CTA 10; Technical quality 5 (total 100). See rule
11.3. The two rubrics agree on weights; the labels differ. No conflict on
scores; label wording is preserved per source.

17.3. [gates] Claim of Social OS superiority requires side-by-side audited
original and new output plus meaningful real-world outcome data (rule 11.4).

## 18. What is NOT verified — never claim

18.1. [v41] The plugin must not report production ready until adapters are
registered and one real content-to-poster run passes, with independent visual
review and real source evidence (rule 16.1).

18.2. [v34] Production readiness is NOT VERIFIED (rule 12.8).

18.3. [v35] Existing v3.4 modules remain, but live external automation
remains unverified (rule 6.4). Do not claim real visual QA if using a
fixture.

18.4. [v43] A real end-to-end run is not established by local tests (rule
15.3). A model-generated receipt alone does not prove independent review
(rule 6.2).

18.5. [v48] Never call a mock fixture a live integration test (rule 2.4).
Legacy scripts are not independently authoritative (rule 13.3).

18.6. [v49] No promise of active integration for every historical script
(rule 13.4). One-content command without external integration configured is
a draft, not fully validated 17-stage production approval (rule 13.6).

18.7. [v6-gate] Never claim a path exists until the file is written and
checked (rule 10.3). Mark every unperformed verification as NOT VERIFIED
(rule 10.7). Do not claim that a system command has been installed or a task
has been completed without evidence (rule 7.5).

18.8. [gates] Missing data not imputed (G13, rule 4.14). No '100%' badge if
any mandatory check is NOT_VERIFIED (rule 3.3).

## 19. Conflicts register — owner decides

19.1. CONFLICT C1 — Fonts (Sora vs Inter/DM Sans): [v41] Sora only (verified
live erudience.com 2026-11-24; old Inter/DM Sans/#10B981 historical only)
vs [v6-gate] Inter + DM Sans mandatory, Sora excluded, vs [gates] G06 and
[v43] "verified Inter/DM Sans font files". Carried with STALE notes at rules
1.4, 4.7, 9.3–9.4, 10.4, 15.5. Verified tokens (Sora only) govern until owner
decides.

19.2. CONFLICT C2 — Gate system count: [v41]/[v43] 17-stage chain vs [gates]
14-gate matrix G00–G13. See rule 4.15.

19.3. CONFLICT C3 — Deep Green: [v41] #0C8D62 (verified) vs [v6-gate]
#0A6E3E. See rule 9.6. Emerald likewise: [v41] #10B77F (verified) vs
[v6-gate] #10B981 (STALE, rule 9.5).

19.4. CONFLICT C4 — Logo required vs logo optional: [v6-gate] missing logo =
critical blocker / brand approval BLOCKED vs [v41]/[v48] logo optional, only
the original owner-approved logo if used. See rule 9.8. (The brand target
file separately records owner-approved-brand-v46, which requires the bundled
logo on new posters.)

19.5. CONFLICT C5 — Endpoint liveness vs registry: [v41] "NO live API
endpoints" vs the existence of `references/endpoint-registry.json` listing
documented provider APIs (OpenAI, Anthropic, Google Search Console) as
DOCUMENTED_PROVIDER_API_NOT_CONNECTED. No contradiction on fact (documented
is not connected), but the registry must never be read as proof of
connectivity. Recorded at rule 16.4.

19.6. No other conflicts were found among the eight merged sources. Where
sources agree (fail-closed gates, max three repairs, receipt/hash binding,
reviewer independence, no auto-publish, no silent bypass, read-only default),
the merged rule is stated once with all agreeing source tags.

## Appendix — sources merged (Worker C scope only)

- gate-contract-v41.md — fully merged (sections 2, 3, 5, 9, 16, 18).
- gates-and-handoff.md — fully merged (sections 3, 4, 7, 8, 17).
- release-audit-v34.md — fully merged (section 12).
- release-compatibility-v48.md — fully merged (sections 5, 9, 13, 14, 16).
- runtime-and-compatibility-v49.md — fully merged (sections 5, 13, 14, 16).
- chatgpt-runtime-v43.md — fully merged (sections 2, 3, 5, 6, 8, 15, 16).
- chat-vision-audit-v35.md — fully merged (sections 2, 6, 8, 9, 16, 18).
- master-command-v6.md — gate/auth/validation sections ONLY merged
  (permissions/read-only, source priority, font lock, logo provenance, visual
  QA blockers, technical QA file proof, comparison rubric, failure handling,
  delivery/status, execution order). Its creative, copy-lock, layout,
  research, buyer-positioning and market-research sections belong to the
  content/image/brand targets and were NOT merged here.
- endpoint-registry.json — NOT merged; stays as JSON (rule 16.4).
- integration-registry-v34.json — NOT merged; stays as JSON (rule 16.4).
- brief-schema-example.json — NOT merged here; see reference-merge-inventory.md.
