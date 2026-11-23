# automation-rules.md — execution, batch, state machine, orchestration

Consolidated from the automation/execution sources in `erudience-plugin/references/`.
Every rule below is tagged with its source. No rule was invented; where sources
conflict, the conflict is named and left for the owner to decide.

## 0. How to read this file

- Tags such as `[v40]` mean the rule comes from that source file:
  `[v40]` autonomous-execution-v40.md, `[v45]` batch-production-v45.md,
  `[v39]` execution-state-machine-v39.md, `[one-action]`
  one-action-production-contract.md, `[v44]` one-command-v44.md,
  `[v31]` master-action-v31.md, `[v2]` orchestrator-v2.md,
  `[v35]` production-execution-v35.md, `[v34]` system-architecture-v34.md,
  `[v42]` unified-system-v42.md, `[v6]` master-command-v6.md (automation /
  execution sections only).
- `[STALE — superseded by verified website tokens 2026-11-24]` means the source
  text is carried verbatim but its brand value is superseded by the verified
  tokens: Sora only, emerald #10B77F, logo optional. The stale text was NOT
  silently rewritten.
- `[CONFLICT]` marks rules that disagree across sources. All conflicting rules
  are kept; the owner decides. See §20 for the conflicts register.
- Scope: execution, batch, state machines, orchestration, rendering, QA gates,
  delivery, and prohibitions. Brand values, content copy, and strategy detail
  live in their own consolidated files; this file states only the automation
  rules that reference them (e.g. "verify the palette", "lock the copy").
- "READY_FOR_OWNER_REVIEW" / "APPROVE" never means permission to publish.

## 1. Triggers and entry points

1.1. Public trigger: `@Erudience`. Legacy `@Erudience linkedin image` is also
accepted. [v31]
1.2. Public trigger for the one-action contract: `@Erudience linkedin image`.
All slash directives in the V6 reference are internal phases, not user input.
[v6, one-action]
1.3. Canonical one-command trigger: `erudiance_linkdin` (canonical user
spelling); alias `erudience_linkdin`. [v44, v45]
1.4. Default intent when `@Erudience` is given with no other words: produce
the next 7-day LinkedIn B2B research-backed content plan and drafts; no
remote writes. Never ask the user to paste a long command. Optional inputs:
topic, category, platform, count, start_date, timezone, formats, model, brand,
approval. Interpret user natural language. [v31]
1.5. One-action autonomy: proceed autonomously through every phase, without
asking the user to select tools or paste already-known assets. Ask one
question only if indispensable topic/copy is absent and no default applies.
This is an on-demand skill, not an always-running service. [one-action]
1.6. One-command runtime: start immediately on trigger. There is no scheduled
background execution. [v44]
1.7. The trigger is manual unless an actual scheduler is connected and
separately authorized. [v34]
1.8. `@Erudience` must not call an image generator directly as a final
delivery shortcut. [v40]
1.9. [v6] Execute the complete workflow when ordered (`/START_NOW`); do not
ask the user again to choose between font systems. [STALE — superseded by
verified website tokens 2026-11-24: the v6 text orders website fonts
Inter + DM Sans; the verified tokens are Sora only.]

## 2. Authoritative controller — [CONFLICT]

2.1. [v39] Authoritative controller: `scripts/production_controller_v39.py`.
All new content-to-image requests MUST use this controller, not the legacy
seven-slot `workflow_engine.py`, legacy `production_gate.py`, or direct
`image_gen` as a delivery path.
2.2. [v40] `autonomous_pipeline_v40.Controller(job, adapters).run()` is the
only supported new content-to-poster controller API.
2.3. [v42] Orchestration and all 17 reviewer gates: `scripts/gate_chain_v41.py`
ONLY. `workflow_engine.py`, `production_gate.py`,
`production_controller_v39.py`, `autonomous_pipeline_v40.py`,
`render_poster.py`, `brand_render_v37.py`, `brief_prompt_gate.py`,
`verify_output.py` and older reference contracts are retained for
regression/traceability, not entrypoints, and MUST NOT override website-first
brand or v4.1 gate order.
2.4. [CONFLICT — controller authority] v39 names `production_controller_v39.py`
as authoritative, v40 names `autonomous_pipeline_v40.Controller` as the only
supported new controller API, and v42 names `gate_chain_v41.py` as the ONLY
orchestration path and demotes the v39 and v40 controllers to historical. All
three claims are kept here; the owner decides which controller is live.
2.5. [v40] An adapter must be executable and registered for each stage. Missing
adapters BLOCK the run. A missing adapter BLOCKS immediately rather than
looping. [v42] Missing real adapter BLOCKED immediately.
2.6. [v31] This plugin's packaged Python scripts do not execute automatically
merely because a ChatGPT prompt mentions them: call the actual runtime/tool
when available; report capability gaps.
2.7. [v45] ChatGPT tools are not automatically callable from Python; the host
assistant must execute tools and submit receipts to the checkpoint bridge.
Without executable tool integration or independent inspection, return
BLOCKED/NOT_APPROVED, never simulated success.
2.8. [v31] Internal action names are logical interfaces, not publicly reachable
HTTP routes. Read `references/endpoint-registry.json` for known provider
contracts. No made-up external endpoints. Before calling any provider,
discover the actual connected tool and verify scope, schema, credential,
response and read-back. Local Python scripts are helper programs, not
automatic cloud endpoints.

## 3. Stage machines and gate enumerations

The sources define different stage enumerations. All are carried below; [v42]
declares the v4.1 gate chain canonical. No stage may be skipped. [v39]

3.1. [v42 — canonical per v42] 17 gates: SOURCES / SOURCE_REVIEW; RESEARCH /
RESEARCH_REVIEW; STRATEGY / STRATEGY_REVIEW; CONTENT / CONTENT_REVIEW;
IMAGE_PLAN / PLAN_REVIEW; IMAGE_BUILD / TECH_REVIEW / VISUAL_REVIEW /
CONTENT_IMAGE_REVIEW / BRAND_REVIEW / FINAL_REVIEW; DELIVERY.
3.2. [v39, v40] 13 stages, in order: SOURCES → RESEARCH → STRATEGY → CONTENT
→ CONTENT_QA → BRIEF → BRIEF_QA → RENDER → TECH_QA → VISUAL_QA →
CONTENT_MATCH_QA → BRAND_QA → DELIVERY. The controller accepts one content
item and requires stages in order.
3.3. [one-action] 15-stage internal state machine: INIT → SOURCES → REFERENCE
→ RESEARCH → COPY_LOCK → DESIGN → RENDER → PIXEL_INSPECTION → CONTENT_QA →
BRAND_QA → MOBILE_QA → TECH_QA → BENCHMARK_QA → DECISION → DELIVERY. Each
stage outputs `PASS`, `FAIL`, or `NOT_VERIFIED`, with evidence/source and
next action.
3.4. [v34] Workflow graph: RESEARCH → KEYWORDS → STRATEGY → DRAFT → FACT_QA →
SEO_QA → CREATIVE → VISUAL_QA → OWNER_APPROVAL → DELIVERY → ANALYTICS. Each
transition requires an independently recorded receipt with content ID, input
hash, evidence references, output artifact path, reviewer, timestamp, and
PASS/BLOCKED/NOT_VERIFIED. No stage self-certification.
3.5. [v31] Action registry (internal only), in dependency order:
research.collect → buyer.extract → evidence.verify → calendar.plan →
calendar.review → content.write → content.review → creative.brief →
creative.review → prompt.build → prompt.review → format.route →
assets.verify → render.execute → visual.verify → batch.reconcile →
owner.review → social_os.authorize → social_os.upload → social_os.readback →
analytics.feedback.
3.6. [v2] 14-step build-and-controller sequence: (1) verify brand/business
source hierarchy; (2) research buyer pains; (3) build buyer map, positioning,
offer, funnel and tracking; (4) build calendar; (5) pick visual treatment;
(6) produce locked copy and 1080×1350 creative brief, controller approves the
plan before render; (7) obtain original logo bytes and approved fonts;
(8) render PNG with manifest; (9) technical + visual QA; (10) benchmark and
controller verdict; (11) REVISE path; (12) owner review; (13) Social OS
handoff; (14) analytics after actual publishing.
3.7. [v6] Execution order (slash commands): `/VERIFY_OWNER_INSTRUCTION` →
`/VERIFY_WEBSITE_FONTS` → `/VERIFY_SOCIAL_OS_BRAND` →
`/FETCH_OFFICIAL_LOGO` → `/FETCH_APPROVED_BENCHMARK` →
`/VERIFY_LINKEDIN_SPECS` → `/RESEARCH_MARKET` → `/DEFINE_BUYER_JOB` →
`/SELECT_STYLE` → `/LOCK_COPY` → `/LOAD_INTER_DM_SANS` → `/LAYOUT` →
`/RENDER_REAL_PNG` → `/VERIFY_FILE_BYTES` → `/VISUAL_INSPECTION` →
`/MOBILE_QA` → `/CORRECT_AND_RERENDER` → `/COMPARE_WITH_BENCHMARK` →
`/SHOW_IMAGE_IN_CHAT` → `/ATTACH_VERIFIED_PNG` → `/QA_REPORT` →
`/REQUEST_OWNER_APPROVAL`. (The `/LOAD_INTER_DM_SANS` step name is carried
verbatim. [STALE — superseded by verified website tokens 2026-11-24: Sora
only.])
3.8. [v39] `CONTENT` locks topic and caption; `BRIEF` must bind to the content
artifact hash and include the exact poster text; `RENDER` must bind to the
brief hash and real image bytes; all image reviewers must bind to both the
image hash and brief hash.
3.9. [v42] Gate ownership: reviewers cannot be their immediate producer. All
artifacts bind upstream hash; content-to-plan binds full caption; plan-to-build
binds full poster copy ledger; image reviews bind image hash and plan hash.
3.10. [v31] Each action contract carries: action_id, input_schema,
output_schema, dependencies, guard, status, evidence_refs, content_id,
input_hash, output_hash, timestamp, attempts. Status is one of PASS, BLOCKED,
NOT_VERIFIED, NOT_APPLICABLE. The guard forbids the next action when the
prerequisite is not PASS, except for an explicit NOT_APPLICABLE branch.
Missing external capability is NOT_VERIFIED, never PASS.
3.11. [v34] Preserve topic history and prior approved artifacts; revisions
create new versions.
3.12. [v2] Allowed terminal states: `DRAFT`, `RESEARCH_BLOCKED`,
`PLAN_REJECTED`, `RENDERED_UNVERIFIED`, `QA_REVISE`, `QA_BLOCKED`,
`READY_FOR_OWNER_REVIEW`, `OWNER_REJECTED`, `OWNER_APPROVED`,
`SOCIAL_OS_STAGED`, `SOCIAL_OS_WRITE_AUTHORISED`, `SOCIAL_OS_DRAFT_CREATED`,
`MEASUREMENT_PENDING`. No status implies publishing.

## 4. Per-stage rules

### 4.1 Sources and research

4.1.1. [v40] SOURCES and RESEARCH need live read-only evidence providers with
provenance. The orchestrator never guesses credentials, bypasses external
tools, or invents research.
4.1.2. [v35] Research gate: source IDs, URLs, retrieval date, quotes/claim
mapping; independent verification is required. A URL field alone is not
verification.
4.1.3. [v2] Verify brand and business source hierarchy, website CSS, official
logo, current LinkedIn documentation and approved reference (read-only).
Record fetched URL, timestamp, source version/commit if available, hash for
binaries, and evidence status. Recheck at each run; cached copies are not
"current".
4.1.4. [v6] Read, if accessible: `bishal-paul-git/erudience-main`
(`src/index.css`, `tailwind.config.ts`, real logo assets) and
`bishal-paul-git/erudience-social-os` (`BRAND.md`, `BUSINESS.md`, `AGENTS.md`,
`agents/12-visual-creative-director.md`, `agents/13-image-carousel.md`,
`agents/21-brand-quality-reviewer.md`, `video/registry/brand-profile.json`
as a historical snapshot, not current approval). Record file paths,
branch/commit or retrieval time where available. Never claim live source
inspection if only past notes are available.
4.1.5. [v6] Research current public LinkedIn B2B examples from automation
consultancies, sales-ops educators, RevOps teams, and service-business
operations creators. For each useful example record publisher, URL, date,
audience, content hook, design format, CTA, and visible metrics if any.
Differentiate observation, hypothesis, and measured result. Do not infer lead
conversion from likes or claim algorithm preference without credible evidence.
If access is unavailable, label MARKET DEMAND UNVERIFIED and proceed with a
clearly identified hypothesis.
4.1.6. [v2] Research current buyer pains, service-business sales operations,
RevOps, response accountability; use public competitor examples with URL,
date, format, hook, visible metrics and limitations. Trend classification must
distinguish observed from hypothesised; never infer conversions from likes.
4.1.7. [v35] Keywords gate: primary, secondary, semantic, intent, ICP, funnel
and platform; do not invent search volume, difficulty or ranking guarantees.
4.1.8. [v34] Keyword taxonomy: primary, secondary, semantic, long_tail,
problem, question, informational, commercial, transactional, branded,
competitor, industry, geographic, entity, negative. Each entry stores term,
type, intent, source (if externally measured), locale, platform, ICP, funnel,
validation status, date. Do not infer search volume or keyword difficulty
without an identified tool and source. LinkedIn search is not equivalent to
Google SEO.
4.1.9. [v34] `scripts/competitor_monitor.py` accepts source-backed records;
never scrapes or schedules itself. Output feeds research and strategy.
`scripts/keyword_research.py` validates typed keyword clusters and provenance
for any asserted volumes. Output feeds `scripts/linkedin_seo_validator.py`
and copywriting. `scripts/linkedin_seo_validator.py` checks natural keyword
inclusion, funnel and claim evidence. It does not predict LinkedIn rankings.

### 4.2 Strategy, calendar, and buyer map

4.2.1. [v2] Build buyer map (ICP, buying role, pain, trigger, objection,
desired outcome), positioning, educational offer, conversion path, lead
qualification, funnel stages and tracking design. Verify any factual claim.
4.2.2. [v2] Build calendar: 30-day rolling plan with day, theme, awareness
stage, hook, evidence, visual style, CTA, target buyer, funnel step, owner,
status and experiment hypothesis. No posting cadence claimed optimal without
data. User-supplied content plan → produce one image per content item after
each gate.
4.2.3. [v2] 30-day planning schema: `day | publish_window_hypothesis | buyer |
funnel_stage | pillar | verified_source | hook | format | CTA | content_id |
status | image_file | gate_receipt | performance_id`. Content pillars: lead
response, sales handoff, CRM hygiene, service operations, AI automation
governance, implementation checklists, case studies ONLY with approved proof,
buyer objections, diagnostic audits.
4.2.4. [v2] Pick visual treatment: process, audit checklist, comparison,
decision tree, diagnostic, myth-vs-fact, or research explainer. Check brand
fit and current observed examples. Avoid copying protected layouts verbatim;
use original compositions.
4.2.5. [v6] Compare three candidate directions on buyer comprehension, brand
fidelity, mobile readability, and benchmark weaknesses: (A) editorial
six-stage process infographic, (B) problem-to-process diagnostic graphic,
(C) practical six-check audit card. Select ONE. Default to A only if evidence
and legibility do not favour B or C. Avoid generic AI art, glossy gradients,
blue circuitry, robots, mock CRM dashboards, decorative icons without meaning,
and excessive text.
4.2.6. [v34] Content formula router: Problem-Cause-Fix for TOFU education;
Question-Answer-Evidence for intent-led education; checklist and framework for
actionable posts; Comparison-Tradeoff-Decision for MOFU;
Objection-Explanation-Next Step for BOFU; PAS and AIDA only where genuinely
helpful. Every output includes target role, buyer problem, primary keyword,
semantic support, angle, evidence, limitations, CTA, format, version and
status. Never force a formula at the cost of clarity.
4.2.7. [v35] Content gate: distinct buyer problem, service relevance, original
insight, useful steps, suitable CTA, human oversight, no unsubstantiated
metrics. Education-first; one planned service promotion per seven slots, hold
if service readiness unverified.

### 4.3 Content, copy lock, and brief

4.3.1. [v40] Never silently replace approved content with another topic.
4.3.2. [v6] Copy lock, UK English, no unapproved rewrite: use exact stage
names and order. Do not place an entire article or lengthy research citations
inside the poster. (The full locked copy text for the Warm Enquiry Response
Workflow poster lives in [v6]; this file carries only the lock rule.)
4.3.3. [one-action] Locked topic fallback: when the user says only
`@Erudience linkedin image`, default to the V6 Warm Enquiry Response Workflow
copy. Six stages exactly: CAPTURE, ACKNOWLEDGE, QUALIFY, ROUTE, NEXT ACTION,
OUTCOME. Do not invent case studies, ROI or research claims. UK English.
4.3.4. [v2] Produce locked copy and a 1080×1350 creative brief. Review for
truthful claims, buyer utility, legibility and CTA. The controller must approve
the plan before render.
4.3.5. [v35] Creative gate: enforce matching caption and creative brief;
verified assets, exact copy, readable mobile typography, actual render file,
inspection receipt, independent brand QA. If logo/fonts absent, block branded
final and label any exploratory draft UNVERIFIED_DRAFT.
4.3.6. [v39] Six-step content must use a renderer that can display all six
steps or the brief must be deliberately restructured and reapproved; silently
dropping a step is forbidden.
4.3.7. [v42] Website-first image renderer `scripts/website_render_v38.py`
renders only 3–5 cards; use another validated renderer for six-card content;
do not truncate.
4.3.8. [v6] Render pipeline: (1) audit sources and collect genuine logo/font
assets; (2) download and inspect the original approved poster if accessible;
(3) research current public B2B design patterns, marking limits; (4) choose
one design hypothesis; lock copy and layout; (5) render with a deterministic
design engine for exact text and original assets; (6) load actual font files,
measure line lengths and adjust text boxes, not the copy; (7) export an
independent PNG to a verified actual path — never claim a path exists until
the file is written and checked; (8) inspect the exported image visually and
programmatically, re-render as needed; (9) never mutate Social OS or publish.
4.3.9. [v6] An image-generation model may propose a decorative visual
direction but MUST NOT be trusted to spell the workflow, reproduce the logo,
or match exact fonts.

### 4.4 Brand-first and asset rules (automation side only)

4.4.1. [v35] Brand-first gate: load actual current website and Social OS brand
rules; validate original logo bytes, font paths/rights, palette, brand voice
and service claims before creative work. A brand name rendered as text is not
a verified logo. No fake assets.
4.4.2. [v2] Obtain original logo bytes (approved asset only) and approved
fonts available locally or downloaded from authorised official sources. Do not
redistribute fonts in the plugin archive. Verify image/logo dimensions, alpha,
file hash, permitted use. If no logo bytes, block brand-approved final; a draft
without logo may still be made and labelled.
4.4.3. [v6] Read genuine website repository assets at
`src/assets/logo-horizontal.png`, `src/assets/erudience-icon.png`, and verify
`src/assets/logo-icon.jpg` before assuming it exists. Download/inspect the
binary and preserve aspect ratio, colour, transparency, sharpness, clear
space. Use the official horizontal logo in the footer only if accessible. Do
not regenerate, redraw, approximate, recolour, distort, or invent a brand
logo. If genuine binary is unavailable, create a clearly labelled REVIEW DRAFT
without a fake logo; final brand approval BLOCKED.
4.4.4. [one-action] For logo use the unmodified original binary from
`bishal-paul-git/erudience-main/src/assets/logo-horizontal.png`, or verify the
alternate `src/assets/erudience-icon.png` when appropriate.
`src/assets/logo-icon.jpg` is only a candidate until verified. If the binary
cannot be retrieved or decoded, brand approval is BLOCKED; do not invent a
logo.
4.4.5. [one-action] Read Social OS `BRAND.md`, `BUSINESS.md`, `AGENTS.md`,
`agents/12-visual-creative-director.md`, `agents/13-image-carousel.md`,
`agents/21-brand-quality-reviewer.md`; snapshot
`video/registry/brand-profile.json` is not live authority. Read-only.
4.4.6. [v39] Owner's current website-first brand profile v3.8 overrides legacy
Sora-only and logo-required rules [STALE — superseded by verified website
tokens 2026-11-24: Sora only, emerald #10B77F, logo optional; the v39 text
describes the website-first profile as overriding Sora-only, which conflicts
with the verified Sora-only tokens — owner decides]. Logo optional. An
authentic logo may be used only if verified. Educational content uses a subtle
CTA, no unsupported performance claims.
4.4.7. [v40] Owner policy (carried verbatim): website-first branding, Inter
headings, DM Sans body, approved emerald/cream palette, Erudience
identity/footer, logo OPTIONAL. [STALE — superseded by verified website tokens
2026-11-24: Sora only, emerald #10B77F.]
4.4.8. [v40] RENDER needs an approved website renderer with genuine Inter and
DM Sans binaries. [STALE — superseded by verified website tokens 2026-11-24:
Sora only.]
4.4.9. [v6] Font lock (carried verbatim): primary headline and emerald emphasis
Inter ExtraBold 800; section headings and numbered stage names Inter Bold 700;
CTA label Inter SemiBold 600; support line, workflow descriptions, diagnostic
sentence, footer microcopy DM Sans 400–500; category label DM Sans 600 with
letterspacing appropriate for uppercase. No Sora on the website-matched poster.
[STALE — superseded by verified website tokens 2026-11-24: Sora only.]
4.4.10. [v6] If exact DM Sans is unavailable locally, obtain a legitimately
served font from the official Google Fonts CSS endpoint or another trusted
authorised source; if retrieval fails, use Inter temporarily and label FONT
FIDELITY BLOCKED, not final. Inspect font metadata; don't infer the font from
appearance or filename alone. No font substitution, synthetic italic, text
raster artefacts, stretched letters, or unsupported glyphs. [STALE — superseded
by verified website tokens 2026-11-24: Sora only.]
4.4.11. [one-action] Website typography (carried verbatim): Inter for headings
and CTA, DM Sans for descriptions and supporting copy. If exact fonts cannot
be rendered, disclose the fallback and mark font fidelity NOT VERIFIED.
[STALE — superseded by verified website tokens 2026-11-24: Sora only.]
4.4.12. [v6] Brand palette lock (carried verbatim): Paper `#F6F1E9`; Ink
`#14120E`; Emerald `#10B981`; Deep Green `#0A6E3E`; Ink Soft `#615B4C`;
Near-Black Green `#0A100E`; Mint `hsl(158 64% 72%)`. [STALE — superseded by
verified website tokens 2026-11-24: emerald #10B77F. The `#10B981` value is
carried verbatim and tagged stale; do not silently replace it.]
4.4.13. [one-action] Palette for Social OS editorial image (carried verbatim,
subject to fresh owner-approved brand verification): Paper #F6F1E9, Ink
#14120E, Emerald #10B981, Deep Green #0A6E3E, Ink Soft #615B4C, Near-Black
Green #0A100E, Mint hsl(158 64% 72%). Do not mistake website dark-theme
tokens for automatic poster surface colours. [STALE — superseded by verified
website tokens 2026-11-24: emerald #10B77F.]
4.4.14. [v6] Do not automatically replace the Social OS paper palette with the
website's dark hero styling: the user requested website fonts, not a wholesale
visual redesign. [STALE in its font premise — superseded by verified website
tokens 2026-11-24: Sora only.]
4.4.15. [one-action] Source-of-truth conflict note (carried verbatim): for
website-matched typography use the actual current CSS from
`bishal-paul-git/erudience-main/src/index.css` and `tailwind.config.ts`. Last
verified website: headings Inter, body DM Sans with Inter fallback. Social OS
`BRAND.md` documents Sora, but this skill intentionally follows the owner's
website-font preference; disclose conflict, never silently blend. [STALE —
superseded by verified website tokens 2026-11-24: Sora only.]
4.4.16. [v6] Website CSS previously inspected from
`erudience-main/src/index.css` contains Google Fonts imports for DM Sans and
Inter; the body uses `font-family: 'DM Sans', 'Inter', sans-serif`; headings
`h1`–`h6` use `font-family: 'Inter', sans-serif`. `tailwind.config.ts`
similarly defines `sans: ['DM Sans','Inter','sans-serif']` and `heading:
['Inter','sans-serif']`. Recheck current files before claiming this is still
live. [STALE — superseded by verified website tokens 2026-11-24: Sora only.]

### 4.5 Render

4.5.1. [v40] CONTENT needs a research-grounded writer; RENDER needs an
approved website renderer with genuine font binaries; VISUAL_QA needs actual
image inspection; DELIVERY is only a verified local file. These are not
included as live provider connections.
4.5.2. [v2] Render PNG with deterministic text/layout; optionally use image
generation for an authorised illustrative element, never for exact logo or
copy. Save source manifest, dimensions, colour mode, checksum and copy ledger.
4.5.3. [one-action] Produce exactly one 1080×1350 sRGB PNG, unless revision
requires rerendering. Warm paper editorial grid, six cards, dark takeaway,
diagnostic question, CTA, authentic footer logo only. Exact text must be
typeset deterministically if possible; image generation can support decorative
visual composition but must not be trusted for spelling, original logo or
exact typography. Preserve clear margins and mobile legibility.
4.5.4. [v6] Layout grid (carried verbatim): canvas 1080×1350; maintain the
prior draft's overall structure unless a concrete legibility defect requires
correction: category pill; large two-part headline; concise support; six
numbered workflow cards in clear reading order; dark takeaway; diagnostic
question; CTA; thin footer rule; genuine logo bottom-left; `erudience.com`
bottom-right. Suggested outer margins 64–80 px; ensure no text clipping,
orphaned words, or overlapping elements. Check full-size and ~360 px
mobile-width previews. Exact card geometry may be adjusted for text fit.
4.5.5. [v45] Do not generate a seven-panel collage as seven deliverables.
Image-generation tools must be called for one approved content item at a time;
request a standalone 4:5 portrait poster. Each output must be a distinct PNG
file at exactly 1080×1350. If an image-generation tool produces another size,
treat it as a draft and do not approve it; a verified local resampling step is
permitted only if the image remains legible and uncut, and must undergo
independent visual re-review. No cropping, stretching, or poster-copy
truncation to force dimensions. Never copy the same image to multiple IDs.
4.5.6. [v39] Direct image generation is allowed only for explicitly labelled
exploration, never as an approved output without running all stages.
4.5.7. [v34] Existing `scripts/content_engine.py`, `scripts/render_poster.py`,
evidence and brand gates remain available; their functionality must be tested
with real assets before a production claim.

## 5. Binding, lineage, and receipts

5.1. [v40] Every stage must produce an artifact and controller-validated
lineage. The immutable job SHA, research source receipt, content→strategy
binding, brief→content binding, render→brief binding, rendered copy ledger,
actual PNG SHA and dimensions, QA→image/brief binding and delivery→render SHA
are enforced.
5.2. [v39] All image reviewers must bind to both the image hash and brief hash.
5.3. [v45] For each content_id, lock exact caption/topic/keywords. The image
plan carries that ID, full caption and content hash. The image builder carries
the same ID and plan hash.
5.4. [v42] All artifacts bind upstream hash, content-to-plan binds full
caption, plan-to-build binds full poster copy ledger, image reviews bind image
hash and plan hash.
5.5. [v35] Receipts: stage, content_id, artifact path and SHA256, producer,
independent reviewer, timestamp; `production_gate.py` validates file integrity
and missing approvals. A PASS string alone never passes.
5.6. [v34] Each transition requires an independently recorded receipt with
content ID, input hash, evidence references, output artifact path, reviewer,
timestamp, and PASS/BLOCKED/NOT_VERIFIED.
5.7. [v31] The controller is independent from the generator and must check
actual artifacts, not self-reported success.
5.8. [v45] A reviewer must inspect actual pixels at native and mobile size,
compare rendered words to the approved poster text and verify the footer,
colour and actual font files. A passing boolean without independently stored
evidence is not sufficient.
5.9. [v40] A test fixture's terminal status is `TEST_FIXTURE_PASS`, never
production approval.
5.10. [v39] Run via CLI: `python scripts/production_controller_v39.py init
--state job.json --content-id <id> --topic <topic>`; for each stage create a
JSON artifact and call `pass --state job.json --stage STAGE --artifact
artifact.json` with `--reviewer` and `--producer` for reviewer stages, and
`--source-verified` for source/research. On failure use `fail --state job.json
--stage STAGE --reason 'reason'`; inspect with `status --state job.json`. Use
file persistence per job; concurrent writers require an external
lock/transactional store not provided here.
5.11. [v2] Owner reviews preview; record explicit APPROVE or REJECT with
timestamp and content hash. On rejection, collect reason, repair, rerun gates,
and request approval again. Owner approval is never assumed.

## 6. Failure, retry, and invalidation

6.1. [v40] A failure returns to the responsible stage, removes all downstream
receipts, reruns registered adapters, and BLOCKS after the fourth failure
(maximum three retries).
6.2. [v39] Failure transition map: SOURCES→SOURCES, RESEARCH→RESEARCH,
STRATEGY→STRATEGY, CONTENT/CONTENT_QA→CONTENT, BRIEF/BRIEF_QA→BRIEF,
RENDER/TECH_QA/VISUAL_QA→RENDER, CONTENT_MATCH_QA/BRAND_QA→BRIEF,
DELIVERY→DELIVERY. On failure, all receipts from the repair target onward are
invalidated. Revision cap 3; fourth failure yields BLOCKED. A revision must
actually be executed by the producer; the controller does not invent revised
content or call an AI model by itself.
6.3. [v42] Failure paths: CONTENT_REVIEW → CONTENT; PLAN_REVIEW →
IMAGE_PLAN; TECH_REVIEW or VISUAL_REVIEW or FINAL_REVIEW → IMAGE_BUILD;
CONTENT_IMAGE_REVIEW or BRAND_REVIEW → IMAGE_PLAN. All dependent receipts
invalidated and rerun. Maximum 3 repairs, fourth failure BLOCKED.
6.4. [v45] Failed reviews invalidate downstream receipts and return to the
owning stage; maximum three corrections.
6.5. [v44] Per-item 17 gates, exact content-to-image binding, fail-closed
review, three repairs.
6.6. [v31] For each failed repairable stage retry up to 3 with fresh validation
and hashes; stop the item after 3 and mark BLOCKED. Never auto-retry
authorization, authentication, legal approval, or unavailable evidence.
Reconcile the batch, list each failed item, never imply complete if assets are
missing. Source changes invalidate downstream gates.
6.7. [v2] If REVISE: identify the failed stage, revise that stage, invalidate
all downstream gate receipts and rerun downstream stages; max three render
attempts per item. If BLOCK: stop and state the required remedy. No gate
bypass by manual "force pass".
6.8. [one-action] Up to 3 render/review iterations; after the third, stop with
a precise failure report. Do not repeatedly fetch the same inaccessible
resource without a changed retrieval method. Critical missing source ⇒ BLOCKED
final approval, but a labelled REVIEW DRAFT may be rendered. Tool failure ⇒
name the tool and failure, use a safe fallback, do not fabricate verification.
6.9. [v6] Failure handling, no blind retries: GitHub inaccessible → identify
repository/path and continue with verified known instructions; mark the
current-source audit incomplete. Original logo inaccessible → no invented
logo; review draft only; brand approval BLOCKED. DM Sans unavailable → seek
an authorised source; if still missing, render a labelled fallback and block
exact-font approval. [STALE — font premise superseded by verified website
tokens 2026-11-24: Sora only.] Benchmark download fails → report the precise
HTTP/tool error; do not pretend a visual comparison. Image generator
unavailable → use a deterministic renderer if possible; do not stop at a
prompt. Text overflows → reflow, resize within readability thresholds, or
adjust layout; do not omit stages. CTA verification fails → retain the
user-supplied URL but mark link verification pending. Market research blocked
→ use a labelled hypothesis, no fabricated demand claims. Export/inspection
fails → do not provide a fabricated attachment or dimensions.
6.10. [v39] Any non-PASS is reported with failure reason and exact return
stage.
6.11. [v2] On Social OS handoff failure, stop and reconcile rather than
blindly retry.

## 7. Reviewer independence and trust boundary

7.1. [v42] Reviewers cannot be their immediate producer.
7.2. [v39] Reviewers must inspect actual rendered pixels and mobile-size
legibility; record observations, exact poster topic, brand assessment and
reviewer identity. The controller validates receipt structure and binding but
cannot cryptographically authenticate reviewer identity or establish semantic
correctness. A reviewer PASS without real independent inspection is prohibited;
a missing runtime reviewer means BLOCKED. Do not claim automatic end-to-end
success from unit tests alone.
7.3. [v40] Independent reviewer code paths are provided for content matching
and brand token checks. They are deterministic validators, not human inspection
and not cryptographically authenticated identities. Visual QA requires a real
registered adapter that opens the actual poster at full and mobile sizes. A
human or separately trusted review service must be configured for real visual
sign-off. Passing a `reviewer_id` string alone is not proof of independence.
Do not claim real visual QA if using a fixture.
7.4. [v31] The controller is independent from the generator and must check
actual artifacts, not self-reported success. (Also §5.7.)
7.5. [v34] No stage self-certification. Deterministic validators must not be
replaced by model self-assessment.
7.6. [v35] Do not treat a tool-generated image or LLM-written caption as
evidence of plugin execution.

## 8. Batch production and weekly/monthly governance

8.1. [v45] Trigger `erudiance_linkdin` (alias `erudience_linkdin`). On demand,
create seven distinct topics and initialize seven independent jobs via
`scripts/batch_guard_v45.py`. Each job must traverse the existing 17-stage
ChatGPT checkpoint bridge, which delegates to the canonical
`gate_chain_v41.py` validator. There is no autonomous background scheduling.
8.2. [v45] The batch is READY_FOR_OWNER_REVIEW only if all seven distinct
jobs pass all 17 gates and produce seven distinct individually verified PNGs.
8.3. [v44] Seven distinct weekly content/image pairs. Per-item 17 gates, exact
content-to-image binding, fail-closed review, three repairs. No scheduled
background execution. No publishing, scheduling, DB writes. Never fabricate
image/research/reviewer evidence. If tools are unavailable, deliver partial
results and an explicit BLOCKED status.
8.4. [v44] Asia/Dhaka 21st monthly anchor.
8.5. [v34] Seven editorial planning slots, exactly one direct-service
promotional slot; if readiness fails, hold the promotional slot and do not
publish it. Four approved posts per week is the prior default publishing
cadence, not a scheduled job. Monthly planning boundary Asia/Dhaka on the
21st. No topic deletion. No automatic external writes, scheduling or
publication. Three repair cycles max per stage; block and report otherwise.
8.6. [v35] Education-first; one planned service promotion per seven slots,
hold if service readiness unverified.
8.7. [v42] Monthly planning and weekly refresh: `references/monthly-weekly-social-os.md` (owner's 21st start).
8.8. [v31] Dispatcher branches: `plan` / `week` / default → collect research
→ buyer pain → evidence → seven-item calendar → 7 original drafts → content
QA → format-appropriate creative briefs and prompts → actual assets if
supported → final report. `month` → 30-day calendar, schedule only explicitly
chosen cadence; create weekly drafts only if requested. `text` → skip image
stages with NOT_APPLICABLE. `image`, `flowchart`, `campaign_poster`,
`market_research_poster`, `trend_poster` → require verified brand assets and
real render+QA. `carousel`, `document` → require true multipage output and
per-page QA, not a single image substitute. `case_study` → demand explicit
client approval and verified results; otherwise block case-study claims.
`trend` → current dated research required; otherwise do not claim trend status.
`social_os` → read-only by default; write only after explicit owner approval
for exact records and operation; schedule/publish separate approval. `claude`
→ only claim Claude use when an authenticated provider was actually invoked;
otherwise use the available model with disclosure.
8.9. [v31] Preserve and apply previous research, branding, source policy,
controller, image production, monthly/weekly, Social OS and analytics
reference files. This file supersedes only trigger ergonomics and action
dispatch. Do not delete previous features.

## 9. Orchestrator steps (detail) [v2]

9.1. Step 1–6: verify sources; research buyer pains; build buyer map,
positioning, offer, funnel, tracking; build the 30-day calendar; pick the
visual treatment; produce locked copy and brief; controller approves the plan
before render. (Detail in §4.1–§4.3.)
9.2. Step 7–8: obtain original logo bytes and approved fonts (see §4.4); render
the PNG with manifest, dimensions, colour mode, checksum and copy ledger.
9.3. Step 9: technical QA — decode PNG, exact dimensions, RGB/RGBA, file size,
margins, OCR or direct text-layout audit, asset hashes, colour tokens, missing
fields. Visual QA — inspect actual pixels at native size and mobile downsample,
contrast, clipped text, grid and spacing. Automated checks supplement but do
not replace human visual inspection.
9.4. Step 10: benchmark with a real Social OS approved image only if downloaded
and inspected. Use identical criteria; no invented scores. Controller issues
APPROVE_FOR_OWNER_REVIEW, REVISE or BLOCK with gate receipts.
9.5. Step 12: owner review (see §5.11).
9.6. Step 13: Social OS handoff — prepare an idempotent payload and a
read-only compatibility check first. After separate explicit permission, write
only authorised draft record(s) using connected official tools/API; verify the
resulting record ID and read-after-write. Never auto-publish, auto-schedule,
mutate approval flags, or change live workflows.
9.7. Step 14: analytics after actual publishing by an authorised user/system —
pull LinkedIn impressions, unique reach if available, saves, meaningful
comments, website/profile clicks, qualified enquiries, meetings and
conversions where permitted. Tag by post and UTM; compare like-for-like time
windows; report missing fields, confounders and no guaranteed growth.

## 10. QA gates (technical, visual, content-match, brand, mobile, benchmark)

10.1. [one-action] Hard verification gates — ALL must pass for APPROVE:
source documents accessible, versions recorded, instruction conflicts
disclosed; real official logo asset binary retrieved, decoded, not distorted
or recoloured, positioned with clear space; poster copy exact and readable, no
misspellings, clipping, missing or duplicate workflow stages; Inter + DM Sans
actually applied or explicitly authorized fallback, fonts verified from
rendered output where feasible [STALE — superseded by verified website tokens
2026-11-24: Sora only]; palette, hierarchy, CTA and destination correct, no
fake facts; output bytes inspected — PNG, 1080×1350, RGB/RGBA
sRGB-compatible, size within current verified LinkedIn spec; full image
visually opened, including mobile-size inspection, contrast and layout check;
approved benchmark visually inspected and comparative score supported by
observed evidence — if inaccessible, comparison NOT VERIFIED and no claim of
superiority; market evidence dated and cited when available, no invented
demand or performance claims. Lack of research does not stop an educational
REVIEW DRAFT but prevents claims of market validation. Explicit owner approval
required for any publishing (no publishing action is in scope).
10.2. [v6] Critical visual-QA blockers: missing or fabricated logo presented as
final; wrong website font without disclosure [STALE — font premise superseded
by verified website tokens 2026-11-24: Sora only]; wrong brand colours;
missing/duplicate/out-of-order stages; text misspelling; clipped/overlapping
text; illegible mobile copy; broken CTA; fake performance claim; wrong file
dimensions/format. Verify exact words against the exported image, not only
source code. For every issue record defect, severity, correction, and
reinspection result. If blocked, provide a usable review draft and transparent
status; never falsely mark APPROVED.
10.3. [v6] Technical QA / file proof: inspect real output bytes — PNG
signature, width=1080, height=1350, RGB/RGBA, sRGB profile if available, file
size, transparent/opaque background as intended, safe margins, logo fidelity,
font metadata, visual hierarchy, mobile-width screenshot. Provide only actual
measurements. Do not call an uninspected render "pixel-perfect".
10.4. [v6] LinkedIn platform specs: verify current official LinkedIn image
requirements at
https://www.linkedin.com/help/linkedin/answer/a527229/share-photos-or-videos?lang=en
. Target 1080×1350, PNG, sRGB/RGB, 4:5; aim under 5MB if appropriate but don't
claim this is the only allowable format or size. Validate export dimensions,
file signature, profile, file size, crop, safe margins, and mobile preview.
10.5. [v6] Approved benchmark: original approved Social OS poster URL
https://itauumqzqgewrfkoishh.supabase.co/storage/v1/object/public/os-media/social/e90d2103-bd8b-4c92-a6e5-96340a92b11c/2026-11-12/1794496473945-warm-enquiry-workflow-capture-acknow.png
— recorded source `os_image_jobs`, content item
`d6c1486e-6039-4070-b901-baedfb27c6dc`, recorded approved variant `v1`,
1080×1350 size. Metadata does not prove visual quality. Attempt download,
inspect actual bytes, dimensions and image contents; if blocked, mark
BENCHMARK VISUAL COMPARISON UNVERIFIED, without inventing scores.
10.6. [one-action] Approved benchmark reference URL (same as §10.5): retrieve,
decode and inspect before scoring; metadata alone is insufficient.
10.7. [one-action] Independent comparison rubric (same rubric for Social OS
original and candidate; total 100): brand accuracy 20; buyer relevance 20;
workflow/factual accuracy 20; visual hierarchy 15; mobile legibility 10;
CTA 10; technical quality 5. Record evidence for each scored criterion;
uninspected = NOT VERIFIED, never 0 by assumption. A higher score is an
editorial assessment, not a proven conversion uplift.
10.8. [v6] Comparison, same rubric, no false winner: brand identity 20; buyer
relevance 20; workflow accuracy 20; visual hierarchy 15; mobile readability
10; CTA 10; technical quality 5 (total 100). Score only what was inspected
and explain each criterion with visible evidence. If the benchmark is
inaccessible, mark the original NOT VERIFIED and do not invent a comparative
total. A higher subjective design score does not prove better impressions,
qualified leads, or conversions.
10.9. [v2] Benchmark with a real Social OS approved image only if downloaded
and inspected; use identical criteria; no invented scores. (Also §9.4.)
10.10. [v34] `scripts/workflow_engine.py` enforces batch IDs, promotion limit,
human oversight and stage receipts; it does not write remotely.
`scripts/linkedin_analytics.py` computes descriptive metrics only from
observed authorized exports; no synthetic reach or leads.
`scripts/integration_tests.py` tests the local contracts and negative cases.

## 11. Delivery and output

11.1. [v39] `DELIVERY` status READY_FOR_OWNER_REVIEW does not imply
publishing.
11.2. [v40] Delivery does not publish.
11.3. [v35] Handoff: deliver local files and audit report only; no Social OS,
LinkedIn, Supabase or GitHub writes without new explicit permission.
11.4. [v40] DELIVERY is only a verified local file.
11.5. [one-action] Output: first display the actual image (if generated), then
provide a verified PNG link (if present), evidence checklist, iterations
attempted, original-versus-new table where evidence permits, remaining defects,
final status `APPROVE / REVISE / BLOCK`. `APPROVE` means ready for the owner's
review, not permission to publish. No claim of 100% market success.
11.6. [v6] Delivery: show the actual generated image directly in chat first,
then provide a clickable link to the verified local PNG when file support
permits. After the image provide: selected design direction; verified
filename/dimensions/format/file size; website font evidence and exact
installed fonts [STALE — font premise superseded by verified website tokens
2026-11-24: Sora only]; genuine logo provenance or blocker; source checks;
six-stage copy check; mobile QA; original-vs-new comparison with NOT VERIFIED
where appropriate; all critical issues; status `APPROVE`, `REVISE`, or
`BLOCK`; request owner approval before any publication. Do not claim that a
system command has been installed or a task has been completed without
evidence.
11.7. [v6] Post-publication test (optional only): suggest a future consent-based
performance evaluation, but do not publish or schedule — compare qualified
enquiries, website clicks, meaningful comments, saves, impressions, and reach
over comparable audiences/time windows, with tracked links where appropriate.
Account for caption, timing, audience, and distribution confounders. Never
invent a benchmark or guarantee results.
11.8. [one-action] Improvement roadmap: P0 — original binary asset retrieval
and deterministic logo/text compositing; source conflict policy; no-fake QA
gates. P1 — screenshot/pixel diff and mobile readability checks, automated OCR
assisted by visual review, repeatable regression test fixture. P2 — competitor
sample library with dated source citations and structured format comparison.
P3 — owner-approved, privacy-conscious post-publication measurement of saves,
meaningful replies, qualified leads and conversions; controlled A/B tests.
P4 — dedicated renderer/asset cache, provider failure telemetry and testable
orchestration service if actual autonomous execution beyond chat is desired.

## 12. Prohibited actions and read-only scope

12.1. [v40] No publishing, Social OS writes, LinkedIn writes, schedules or DB
modifications.
12.2. [v39] No Social OS/LinkedIn/database writes or scheduler actions.
12.3. [v42] No posting, scheduling, Social OS writes or external mutations
without separate owner approval.
12.4. [v44] No publishing, scheduling, DB writes.
12.5. [v45] No posting, scheduling, database writes or external mutations
without separate owner approval. Supabase/Social OS are future integrations.
12.6. [v35] The owner has explicitly deferred Social OS writes, approval portal
integration, scheduling, and LinkedIn publishing. No such actions are
authorized.
12.7. [v6] Permissions / read-only / no side effects: treat GitHub, Supabase,
Social OS workflows, image jobs, content, approval records, and published
assets as READ-ONLY. No commit, push, DB update, deployment, publishing,
scheduling, or approval-state change. Create independent output files only.
Never upload credentials or expose private tokens. No silent side effects.
12.8. [v6] Never mutate Social OS or publish.
12.9. [v2] Never auto-publish, auto-schedule, mutate approval flags, or change
live workflows.
12.10. [v34] No implicit LinkedIn, Supabase, GitHub, image generation, or web
API access. Read-only default.

## 13. Source priority and conflict resolution

13.1. [v6] Source priority: (1) explicit current owner instruction in this
conversation; (2) verified current website font implementation for the
independent website-matched poster [STALE — font premise superseded by
verified website tokens 2026-11-24: Sora only]; (3) owner-approved Social OS
BRAND.md and related agent guidelines for non-font identity rules;
(4) verified genuine assets from the website repository; (5) current
primary-source platform documentation; (6) evidence-based market examples and
design judgment. If a conflict arises, name it and state the applied
precedence. Do not silently blend font systems.
13.2. [one-action] Source-of-truth and conflict resolution: (1) current explicit
owner instructions override historical instructions; (2) for website-matched
typography use the actual current CSS from
`bishal-paul-git/erudience-main/src/index.css` and `tailwind.config.ts`
[STALE — superseded by verified website tokens 2026-11-24: Sora only];
(3) for logo use the unmodified original binary (see §4.4.4); (4) read Social
OS `BRAND.md`, `BUSINESS.md`, `AGENTS.md`, `agents/12-visual-creative-director.md`,
`agents/13-image-carousel.md`, `agents/21-brand-quality-reviewer.md`; snapshot
`video/registry/brand-profile.json` is not live authority; (5) approved
benchmark reference URL (see §10.5); (6) palette for Social OS editorial image
(see §4.4.13).
13.3. [v6] For the website-matched poster, Inter + DM Sans are mandatory when
authentic font files can be loaded. Sora is excluded. If a genuine font file
cannot be accessed, stop exact-font approval and disclose the fallback. Never
label a fallback as exact. [STALE — superseded by verified website tokens
2026-11-24: Sora only.]
13.4. [v42] Historical reference contracts contain incompatible assumptions
(e.g. mandatory logo, six fixed cards, Sora) and MUST NOT override
website-first brand or v4.1 gate order. [CONFLICT — see §20, C3: the v42 text
treats Sora as a superseded historical assumption, while the verified website
tokens 2026-11-24 are Sora only. Both are carried; the owner decides.]

## 14. Adapters, integrations, and honesty about readiness

14.1. [v40] Runtime adapters still needed for genuine production: SOURCES and
RESEARCH — live read-only evidence providers with provenance; CONTENT —
research-grounded writer; RENDER — approved website renderer with genuine
font binaries [STALE — font premise superseded by verified website tokens
2026-11-24: Sora only]; VISUAL_QA — actual image inspection; DELIVERY — only
verified local file. These are not included as live provider connections.
14.2. [v42] Unresolved live dependencies: research endpoint adapter, LLM
planner/writer adapters, verified font assets, real image rendering adapter,
independently executed pixel/mobile reviewer, persistent job state/concurrency
control, and end-to-end live run remain integration requirements. A manifest
merge cannot provide credentials or make an unconnected endpoint operational.
Do not misrepresent readiness.
14.3. [v34] External integration prerequisites: for LinkedIn — approved app
permissions, OAuth, token lifecycle, API endpoint eligibility, rate limits,
posting rights and readback. For Supabase — schema, RLS, least-privilege keys,
migrations, secrets manager, idempotency and audit. For research — approved
public sources and ToS-compliant retrieval. For images — verified logo, font
rights, render engine, actual asset files and visual inspection. For
scheduling — explicit scheduler service, timezone, deduplication and failure
alerts. None of these are provisioned by adding a local file.
14.4. [v34] Every external integration has a separately configured adapter,
credential scope, error handling, rate limit, and readback verification;
absent adapters are BLOCKED, not mocked.
14.5. [v35] No fabricated autonomy: file-based scripts do not equal deployed
agents, connected data providers, scheduler or image generation service.
Report each adapter as CONFIGURED/NOT_CONFIGURED and real tests as
PASS/BLOCKED/NOT_TESTED.
14.6. [v42] Endpoint declarations: `references/endpoint-registry.json` (status
is NOT connected).
14.7. [v40] No live source-to-image test has passed until all real adapters are
connected and the image inspected.
14.8. [v34] `scripts/workflow_engine.py` enforces batch IDs, promotion limit,
human oversight and stage receipts; it does not write remotely. (Also §10.10.)

## 15. Testing and definition of done

15.1. [v40] `python scripts/test_autonomous_pipeline_v40.py` runs 12
fixture-backed tests including full stage traversal, wrong topic, mismatched
brief, wrong render binding, fake reviewer identity, visual failure, brand
mismatch, missing adapters, retry exhaustion and logo omission.
15.2. [v42] QA tests: `scripts/test_gate_chain_v41.py` plus legacy regression
tests.
15.3. [v34] Definition of done: all tests green, source registry verified, real
end-to-end execution through each connected adapter, independent brand review,
explicit approval, observed readback, incident recovery, logs, and documented
operating procedures. Never state 100% readiness until evidence exists for
every gate.
15.4. [v35] Acceptance: for each pilot, prove actual research provenance,
content quality, exact branding, image output, independent QA, negative-path
tests, repeatable execution. Current deployment cannot be called 100%
production-ready until real external connectors and runtime are configured and
end-to-end exercised. Preserve existing historical files and versioned records.
15.5. [v34] `scripts/integration_tests.py` tests the local contracts and
negative cases.

## 16. Legacy and historical paths

16.1. [v40] The v3.9 manual controller and older v3.8 workflow engine are
retained for compatibility but must not be invoked for new production
deliveries. Any prior `PASS` strings are not imported into v4.0.
16.2. [v39] Legacy tools (`workflow_engine.py`, `production_gate.py`, direct
`image_gen`) are historical or draft-only and do not certify production
readiness.
16.3. [v42] Active modules: orchestration and all 17 reviewer gates
`scripts/gate_chain_v41.py` ONLY; website brand contract
`references/website-brand-profile-v38.md` and `scripts/website_brand_v38.py`;
website-first image renderer `scripts/website_render_v38.py` (only 3–5 cards;
use another validated renderer for six-card content; do not truncate); monthly
planning and weekly refresh `references/monthly-weekly-social-os.md` (owner's
21st start); endpoint declarations `references/endpoint-registry.json`
(status is NOT connected); QA tests `scripts/test_gate_chain_v41.py` plus
legacy regression tests.
16.4. [v42] This is a single-plugin merge, not multiple plugin installations.
All pre-existing files remain in the same installed plugin. The merge unifies
manifests, skill entry point, version policy, and authoritative execution path
while retaining old modules for compatibility and auditability.

## 17. Input contract [v2]

17.1. Input fields: `content_id`, `topic`, `source_article_or_brief`,
`audience`, `offer`, `market`, `objective`, `channel=LinkedIn`,
`format=single_image`, `brand=Erudience`, `owner`, `status=DRAFT`,
`requested_batch_size` (default 1). If a content calendar is supplied, each
item is independently versioned and processed. Do not silently invent claims
or customer cases. If a topic is missing, propose a topic grounded in research
and label it PROPOSED, not approved.

## 18. Buyer research and positioning rules (automation side) [v6, v2]

18.1. [v6] Primary audience: B2B service-business founders, Sales Directors,
Operations Managers, and RevOps. Buyer problem: CRM records and alerts can
coexist with missed follow-up, unclear ownership, no deadline, no escalation,
and unrecorded outcome. Buyer job: trace the entire journey of an enquiry and
identify gaps in accountability. Educate first, sell second. No invented ROI,
client outcomes, benchmarks, or customer quotes.
18.2. [v2] Buyer research: permitted buyer signals only; hypothesis separated
from evidence. (Role detail lives in agent-rules.md.)

## 19. Source map

- autonomous-execution-v40.md → §1.5–1.8, §2.2, §2.5, §3.2, §4.1.1, §4.4.7–4.4.8,
  §4.5.1, §5.1, §5.9, §6.1, §7.3, §12.1, §14.1, §14.7, §15.1, §16.1.
- batch-production-v45.md → §1.3, §2.7, §3.1 (via bridge), §4.5.5, §5.3, §5.8,
  §6.4, §8.1–8.2, §12.5.
- execution-state-machine-v39.md → §2.1, §3.2, §3.8, §4.4.6, §4.5.6, §5.2,
  §5.10, §6.2, §6.10, §7.2, §11.1, §12.2, §16.2.
- one-action-production-contract.md → §1.2, §1.5, §3.3, §4.3.3, §4.4.4–4.4.5,
  §4.4.11, §4.4.13, §4.4.15, §4.5.3, §6.8, §10.1, §10.6–10.7, §11.5, §11.8,
  §13.2.
- one-command-v44.md → §1.3, §1.6, §6.5, §8.3–8.4, §12.4.
- master-action-v31.md → §1.1, §1.4, §2.6, §2.8, §3.5, §3.10, §6.6, §7.4,
  §8.8–8.9.
- orchestrator-v2.md → §3.6, §3.12, §4.1.3, §4.1.6, §4.2.1–4.2.4, §4.3.4,
  §4.4.2, §4.5.2, §5.11, §6.7, §6.11, §9, §10.9, §12.9, §17, §18.2.
- production-execution-v35.md → §4.1.2, §4.1.7, §4.2.7, §4.3.5, §4.4.1, §5.5,
  §11.3, §12.6, §14.5, §15.4.
- system-architecture-v34.md → §1.7, §3.4, §3.11, §4.1.8–4.1.9, §4.2.6, §4.5.7,
  §5.6, §7.5, §8.5, §10.10, §12.10, §14.3–14.4, §14.8, §15.3, §15.5.
- unified-system-v42.md → §2.3–2.4, §3.1, §3.9, §6.3, §8.7, §12.3, §13.4,
  §14.2, §14.6, §15.2, §16.3–16.4.
- master-command-v6.md (automation/execution sections only) → §1.2, §1.9,
  §3.7, §4.1.4–4.1.5, §4.2.5, §4.3.2, §4.3.8–4.3.9, §4.4.3, §4.4.9–4.4.10,
  §4.4.12, §4.4.14, §4.4.16, §4.5.4, §6.9, §10.2–10.5, §10.8, §11.6–11.7,
  §12.7–12.8, §13.1, §13.3, §18.1.

## 20. Conflicts register

- C1 — Authoritative controller: [v39] `production_controller_v39.py` vs [v40]
  `autonomous_pipeline_v40.Controller` vs [v42] `gate_chain_v41.py` ONLY.
  Owner decides which controller is live.
- C2 — Stage enumeration: [v39/v40] 13 stages vs [one-action] 15 stages vs
  [v42] 17 gates vs [v34] 11-stage graph vs [v31] 21 actions vs [v2] 14 steps
  vs [v6] 22 slash commands. Return-stage maps also differ ([v39] §6.2 vs
  [v42] §6.3). Owner decides the canonical enumeration; [v42] claims v4.1.
- C3 — Brand font system: [v39/v40/v6/one-action] website-first Inter + DM
  Sans, Sora excluded/overridden, vs [v42] treating Sora as a superseded
  historical assumption, vs verified website tokens 2026-11-24 (Sora only,
  emerald #10B77F, logo optional). All source texts are carried with STALE
  tags; the owner decides. The verified tokens are recorded in §0.
- C4 — Emerald value: [v6/one-action] `#10B981` vs verified emerald `#10B77F`
  (2026-11-24). The `#10B981` text is carried with a STALE tag.
- C5 — Logo requirement: [v39/v40/v42] logo optional on the poster vs
  [one-action §4.4.4 / v6 §4.4.3 / v2 §4.4.2] brand approval BLOCKED if the
  genuine logo binary cannot be retrieved/decoded. These are reconcilable
  (optional to include, but if included it must be the verified original; a
  claimed-but-unverified logo blocks approval) — recorded here so the owner
  can confirm that reading.
- C6 — Renderer card capacity: [v42] website renderer handles only 3–5 cards
  vs [v39/one-action] six-card posters as the default. [v42] resolves it by
  requiring another validated renderer for six-card content; no truncation.
  Recorded, not a live contradiction.
- C7 — "Website-first" vs "Sora-only": [v39 §4.4.6] says the website-first
  profile overrides legacy Sora-only rules, while the verified tokens
  (2026-11-24) are Sora only. Owner decides; both texts are carried.

## 21. What was NOT merged here

- The non-automation sections of master-command-v6.md (buyer persona detail,
  full locked copy text, palette/layout as brand rules, benchmark URL
  provenance beyond §10.5) belong to the brand/content buckets, not this file.
  Only its automation/execution rules were taken, per the task.
- Endpoint, integration, and brief-schema JSON files were not touched, per the
  task.
- No rule was dropped for conflicting. Every unique rule from every listed
  source appears above or is named in the conflicts register.
