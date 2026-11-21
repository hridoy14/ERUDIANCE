# Erudience v4.3 ChatGPT-native runtime contract

## Execution architecture
ChatGPT is the external tool orchestrator. `scripts/chatgpt_bridge_v43.py` is the durable local checkpoint/state machine, and `scripts/gate_chain_v41.py` is the authoritative gate validator. ChatGPT tool calls are not callable directly from installed Python scripts. Never imply that installing a plugin ZIP creates a permanent service, autonomous background process, or API credentials.

1. Start job with `python scripts/chatgpt_bridge_v43.py start --state JOB.json --job JOB_INPUT.json`.
2. Call `next --state JOB.json`; inspect the stage and its hashes.
3. Execute the actual stage with ChatGPT tools: web/research for SOURCES; reasoning/writing for strategy/content/plan; image_gen or deterministic renderer for IMAGE_BUILD; independent actual pixel inspection for visual QA. A model-generated receipt alone does not prove independent review.
4. Save tool output with real evidence/provenance to RECEIPT.json. Submit `submit --state JOB.json --stage STAGE --adapter NAME --role producer|reviewer --receipt RECEIPT.json`.
5. Repeat until READY_FOR_OWNER_REVIEW, TEST_FIXTURE_PASS or BLOCKED. A failed gate rewinds, invalidates downstream records, and demands re-execution. Never bypass failure by editing receipt text.
6. Do not auto-publish. Later Supabase/Social OS integration is a separate authorized adapter project.

## Evidence requirements
Live SOURCES require actual URL, verified_at, source_sha256. Every reviewer requires separate inspected evidence file and its real SHA256. IMAGE_BUILD needs real 1080x1350 PNG hash, exact plan and poster ledger hash, and verified Inter/DM Sans font files. Visual reviewer must inspect image pixels at full and mobile scale. Image plan must match locked caption exactly and website brand spec. All gates are fail-closed. Do not fabricate a source, tool execution, review, or image metadata.

## Boundaries
This update implements the checkpoint bridge and tests, not automatic invocation of ChatGPT tools from Python. Connected providers must be used through ChatGPT's supported tool calls in the live session. A real end-to-end run is not established by local tests. No persistent unattended runtime is promised.
