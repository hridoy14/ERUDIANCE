# Erudience v3.7 production runtime contract

Source of truth: Social OS `BRAND.md` locked v1.1. Social creative uses Sora, not website UI Inter/DM Sans. Brand assets must be retrieved from the connected authenticated GitHub repository, decoded and pinned to content hashes. `scripts/brand_render_v37.py` is the only accepted local deterministic final-image renderer. Old `scripts/render_poster.py` is legacy draft-only and cannot produce approved brand output.

`@Erudience` executes research, keyword research, planning, writing, fact checks, SEO checks, brand voice checks, brief, renderer, independent visual inspection, acceptance. When external research tools or runtime capabilities are absent, stop with BLOCKED/NOT_TESTED. Never substitute a direct image generation call and claim orchestrator approval.

The renderer's output status is RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA, never PASS. Final acceptance additionally requires independently checked asset hashes, visual inspection of rendered pixels, original content claims and source provenance, and a verified stage-by-stage runtime receipt. A path or user-supplied PASS string is insufficient. The production gate from v3.5 remains required, but its reviewer fields are not cryptographic proof of independent execution. Do not claim a security guarantee beyond tests actually run.

The user has deferred all Social OS database/approval integration, LinkedIn publishing and scheduling. No external writes are authorized. The local image generation experiment cannot be represented as a deployed always-on autonomous pipeline. Existing content engine and historical references are retained, with this contract superseding conflicting render/font guidance.
