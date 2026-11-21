# Erudience v4.0 — executable controller and acceptance boundary

Owner policy: website-first branding, Inter headings, DM Sans body, approved emerald/cream palette, Erudience identity/footer, logo OPTIONAL. Never silently replace approved content with another topic.

## Execution contract
`autonomous_pipeline_v40.Controller(job, adapters).run()` is the only supported new content-to-poster controller API. An adapter must be executable and registered for each stage. Missing adapters BLOCK the run. Stages: SOURCES, RESEARCH, STRATEGY, CONTENT, CONTENT_QA, BRIEF, BRIEF_QA, RENDER, TECH_QA, VISUAL_QA, CONTENT_MATCH_QA, BRAND_QA, DELIVERY.

Every stage must produce an artifact and controller-validated lineage. The immutable job SHA, research source receipt, content→strategy binding, brief→content binding, render→brief binding, rendered copy ledger, actual PNG SHA and dimensions, QA→image/brief binding and delivery→render SHA are enforced. A failure returns to the responsible stage, removes all downstream receipts, reruns registered adapters, and BLOCKS after the fourth failure (maximum three retries). A missing adapter BLOCKS immediately rather than looping. Delivery does not publish.

## Reviewer trust boundary
Independent reviewer *code paths* are provided for content matching and brand token checks. They are deterministic validators, not human inspection and not cryptographically authenticated identities. Visual QA requires a real registered adapter that opens the actual poster at full and mobile sizes. A human or separately trusted review service must be configured for real visual sign-off. Passing a `reviewer_id` string alone is not proof of independence. Do not claim real visual QA if using a fixture.

## Runtime adapters still needed for genuine production
SOURCES and RESEARCH: live read-only evidence providers with provenance; CONTENT: research-grounded writer; RENDER: approved website renderer with genuine Inter and DM Sans binaries; VISUAL_QA: actual image inspection; DELIVERY: only verified local file. These are not included as live provider connections. The orchestrator never guesses credentials, bypasses external tools or invents research. No publishing, Social OS writes, LinkedIn writes, schedules or DB modifications.

## Testing
`python scripts/test_autonomous_pipeline_v40.py` runs 12 fixture-backed tests including full stage traversal, wrong topic, mismatched brief, wrong render binding, fake reviewer identity, visual failure, brand mismatch, missing adapters, retry exhaustion and logo omission. A test fixture's terminal status is `TEST_FIXTURE_PASS`, never production approval. No live source-to-image test has passed until all real adapters are connected and the image inspected.

## Legacy isolation
The v3.9 manual controller and older v3.8 workflow engine are retained for compatibility but must not be invoked for new production deliveries. Any prior `PASS` strings are not imported into v4.0. `@Erudience` must not call an image generator directly as a final delivery shortcut.
