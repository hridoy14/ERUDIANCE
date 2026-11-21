---
name: erudience
description: "One-command Erudience LinkedIn content and image production with a single fail-closed controller."
---
# Erudience v4.9.1 — One controller, one policy

Start by reading `references/brand-policy-current.md` and `references/runtime-and-compatibility-v49.md`. They supersede any conflicting historical logo-required or DM Sans-required documents. Older references are archival and must never override current policy.

Command `erudiance_linkdin` runs seven independent jobs; `erudiance_linkdin --test --single-content ER-001` runs exactly one. Plan content and lock approved caption and poster copy BEFORE generating imagery. Every content job follows the 17 stages defined in `scripts/gate_chain_v41.py`; this is the ONE canonical validation engine, updated in place. `scripts/chatgpt_bridge_v43.py` and `scripts/batch_guard_v45.py` are orchestration adapters, not competing validators. Older production_controller_v39.py and workflow_engine.py are legacy only: do not invoke as independent execution paths. No new versioned controller files in future releases.

Brand: read the only machine-readable brand settings from `references/production-policy-v33.json`. Sora is required for heading and body; current emerald is #10B77F. The approved original logo is optional; never generate, redraw or replace any logo. The footer must contain Erudience and erudience.com. Content topics cover verified Erudience AI voice, automation, SaaS and AI development, products, industries, customer value and use cases; do not force voice agents into every post. On the first weekly workflow run, verify Erudience offerings and public competitor content/image patterns with dated source evidence, recording previous/current values and review status; reuse within the week. Do not claim autonomous weekly research if execution or persistence is not configured.

Poster: one standalone PNG exactly 1080x1350 per content ID, no collages, exact approved poster text rendered deterministically after illustration generation. Image planning includes content hash, poster text, brand, template, funnel and positioning. The brand review must explicitly confirm the authentic logo when present, or confirm absence when omitted. Evidence and independent reviews are mandatory for production approval. Missing evidence = BLOCKED. Fixture tests never imply live success.

External integration registry may remain NOT_CONFIGURED. This does NOT block manual ChatGPT-based draft production. Do not publish, schedule, send messages or perform external writes. Preserve existing file paths and release compatibility; run regression tests before updates.
