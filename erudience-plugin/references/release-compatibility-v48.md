# v4.8 Compatibility and no-silent-bypass policy

Preserve all legacy files and original binary assets during overlay updates. File preservation is NOT runtime compatibility: older scripts may still import or call legacy validators. The canonical gate_chain_v41.py now enforces the v4.7 logo and content-to-poster requirements; chatgpt_bridge_v43.py imports it directly, so the same checks apply at bridge submission. batch_guard_v45.py imports chatgpt_bridge_v43.py, preserving the single controller path.

Every update must: (1) list prior file paths and compare with post-update inventory, (2) execute tests for bridge, gate, batch guard and current brand, (3) reject incomplete poster_text or logo provenance, (4) verify real source and font evidence, (5) perform one live content-to-image review before production approval. Legacy scripts may remain for compatibility but are not independently authoritative. Do not delete or rename their import paths without a migration and tests. A ZIP overlay cannot itself create background automation or persistent connectors.

The exact original logo must be composited after illustration generation. If DM Sans font binary is missing, final rendering and production approval are BLOCKED; a fallback preview must be explicitly labelled DRAFT. Never call a mock fixture a live integration test.
