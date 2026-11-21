# Erudience One-Action Production Contract — v1.1

## Action and autonomy
Public trigger: `@Erudience linkedin image`. All slash directives in the V6 reference are internal phases. Proceed autonomously through every phase, without asking the user to select tools or paste already-known assets. Ask one question only if indispensable topic/copy is absent and no default applies. This is an on-demand skill, not an always-running service.

## Source-of-truth and conflict resolution
1. Current explicit owner instructions override historical instructions.
2. For website-matched typography use the actual current CSS from `bishal-paul-git/erudience-main/src/index.css` and `tailwind.config.ts`. Last verified website: headings Inter, body DM Sans with Inter fallback. Social OS `BRAND.md` documents Sora, but this skill intentionally follows the owner's website-font preference; disclose conflict, never silently blend.
3. For logo use **unmodified original binary** from `bishal-paul-git/erudience-main/src/assets/logo-horizontal.png`, or verify the alternate `src/assets/erudience-icon.png` when appropriate. `src/assets/logo-icon.jpg` is only a candidate until verified. If binary cannot be retrieved or decoded, brand approval is BLOCKED; do not invent a logo.
4. Read Social OS `BRAND.md`, `BUSINESS.md`, `AGENTS.md`, `agents/12-visual-creative-director.md`, `agents/13-image-carousel.md`, `agents/21-brand-quality-reviewer.md`; snapshot `video/registry/brand-profile.json` is not live authority. Read-only.
5. Approved benchmark reference URL: `https://itauumqzqgewrfkoishh.supabase.co/storage/v1/object/public/os-media/social/e90d2103-bd8b-4c92-a6e5-96340a92b11c/2026-11-12/1794496473945-warm-enquiry-workflow-capture-acknow.png`. Retrieve, decode and inspect before scoring; metadata alone is insufficient.
6. Palette for Social OS editorial image (subject to fresh owner-approved brand verification): Paper #F6F1E9, Ink #14120E, Emerald #10B981, Deep Green #0A6E3E, Ink Soft #615B4C, Near-Black Green #0A100E, Mint hsl(158 64% 72%). Do not mistake website dark-theme tokens for automatic poster surface colours.

## Internal execution state machine
`INIT → SOURCES → REFERENCE → RESEARCH → COPY_LOCK → DESIGN → RENDER → PIXEL_INSPECTION → CONTENT_QA → BRAND_QA → MOBILE_QA → TECH_QA → BENCHMARK_QA → DECISION → DELIVERY`

Each stage outputs `PASS`, `FAIL`, or `NOT_VERIFIED`, with evidence/source and next action. Critical missing source => BLOCKED final approval, but a labelled REVIEW DRAFT may be rendered. Tool failure => name tool and failure, use safe fallback, do not fabricate verification. Up to 3 render/review iterations; after third, stop with precise failure report. Do not repeatedly fetch the same inaccessible resource without a changed retrieval method.

## Locked topic fallback
When the user says only `@Erudience linkedin image`, default to the V6 Warm Enquiry Response Workflow copy. Six stages exactly: CAPTURE, ACKNOWLEDGE, QUALIFY, ROUTE, NEXT ACTION, OUTCOME. Do not invent case studies, ROI or research claims. UK English. Website typography: Inter for headings and CTA, DM Sans for descriptions and supporting copy. If exact fonts cannot be rendered, disclose fallback and mark font fidelity NOT VERIFIED.

## Rendering constraints
Produce exactly one 1080×1350 sRGB PNG, unless revision requires rerendering. Warm paper editorial grid, six cards, dark takeaway, diagnostic question, CTA, authentic footer logo only. Exact text must be typeset deterministically if possible; image generation can support decorative visual composition but must not be trusted for spelling, original logo or exact typography. Preserve clear margins and mobile legibility.

## Hard verification gates (ALL must pass for APPROVE)
- Source documents accessible, versions recorded, instruction conflicts disclosed.
- Real official logo asset binary retrieved, decoded, not distorted or recoloured, positioned with clear space.
- Poster copy exact and readable; no misspellings, clipping, missing or duplicate workflow stages.
- Inter + DM Sans actually applied or explicitly authorized fallback; fonts verified from rendered output where feasible.
- Palette, hierarchy, CTA and destination correct; no fake facts.
- Output bytes inspected: PNG, 1080×1350, RGB/RGBA sRGB-compatible, size within current verified LinkedIn spec.
- Full image visually opened, including mobile-size inspection, contrast and layout check.
- Approved benchmark visually inspected and comparative score supported by observed evidence; if inaccessible, comparison NOT VERIFIED and no claim of superiority.
- Market evidence dated and cited when available; no invented demand or performance claims. Lack of research does not stop an educational REVIEW DRAFT but prevents claims of market validation.
- Explicit owner approval required for any publishing (no publishing action is in scope).

## Independent comparison rubric
Brand accuracy 20; buyer relevance 20; workflow/factual accuracy 20; visual hierarchy 15; mobile legibility 10; CTA 10; technical quality 5. Same rubric for Social OS original and candidate. Record evidence for each scored criterion; uninspected = NOT VERIFIED, never 0 by assumption. Higher score is an editorial assessment, not a proven conversion uplift.

## Output
First display the actual image (if generated), then provide a verified PNG link (if present), evidence checklist, iterations attempted, original-versus-new table where evidence permits, remaining defects, final status `APPROVE / REVISE / BLOCK`. `APPROVE` means ready for owner's review, not permission to publish. No claim of 100% market success.

## Improvement roadmap
P0: Original binary asset retrieval and deterministic logo/text compositing; source conflict policy; no-fake QA gates. P1: Screenshot/pixel diff and mobile readability checks, automated OCR assisted by visual review, repeatable regression test fixture. P2: Competitor sample library with dated source citations and structured format comparison. P3: Owner-approved, privacy-conscious post-publication measurement of saves, meaningful replies, qualified leads and conversions; controlled A/B tests. P4: Dedicated renderer/asset cache, provider failure telemetry and testable orchestration service if actual autonomous execution beyond chat is desired.
