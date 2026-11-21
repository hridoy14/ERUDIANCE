# Erudience LinkedIn Content & Image Plugin — v4.9.1 source snapshot

## Status
89 text source files migrated to this public repository. Original owner-approved JPG logo will be supplied separately by the owner. This GitHub copy is a source backup, not a published v4.9.2 release.

## Canonical runtime
`skills/erudience/SKILL.md` is the entrypoint. `scripts/gate_chain_v41.py` implements the 17-stage review gate. `scripts/chatgpt_bridge_v43.py` and `scripts/batch_guard_v45.py` support durable handoffs and seven independent 1080×1350 creatives, exactly one promotion. Historical 10-stage and 13-stage controllers remain for compatibility.

## Brand
`references/production-policy-v33.json` is authoritative: Sora typography, emerald `#10B77F`, optional authentic original logo only. Historical Inter/DM Sans and `#10B981` values are not current brand authority.

## Operational safety
External integrations remain NOT_CONFIGURED. No automatic publishing, account changes, fabricated sources, fabricated logos, or claims of production readiness. Owner approval is required before delivery/publication.

## Historical README consolidation
v3.3 core modules and evidence-first policy; v3.4 research/editorial validation; v3.5 SHA-256 receipts and independent review; v3.6–v3.8 brand experiments; v3.9–v4.0 legacy persisted state controller; v4.1 17-stage gate; v4.2 unified entrypoint; v4.9.1 manifest/brand alignment. Historical README-v*.md files are retained until complete source-specific regression checks and review establish they can be safely deleted.

## Testing
GitHub workflow: `.github/workflows/erudience-regression.yml`. Local subset tests: 27 passed, compilation passed on 2026-11-22; this is not a full GitHub checkout verification. Full integration tests and legacy renderers must pass before cleanup and release.
