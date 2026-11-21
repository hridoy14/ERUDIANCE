# Runtime / compatibility contract v4.9

Single canonical validator: `scripts/gate_chain_v41.py` (stable import path). Do not create versioned replacement controllers. `scripts/chatgpt_bridge_v43.py` imports `gate_chain_v41`; `scripts/batch_guard_v45.py` imports `chatgpt_bridge_v43`. Old `production_controller_v39.py` and `workflow_engine.py` are archived compatibility code, NOT active paths. Do not remove them without checking all callers; no promise of active integration for every historical script.

Release process: list plugin files before/after, preserve omitted assets, assert canonical import edges, run bridge, batch and brand-policy regression tests, test both logo-present and logo-absent plans, check mandatory poster copy, and test missing fonts/reviewer evidence blocks. Use guarded expected_release_id. Live production approval requires real research, actual poster and independent visual evidence. The ZIP update does not provision scheduler, API credentials, persistence or runtime automation.

One-content command may run without any external integration configured, using available ChatGPT tools and local rendering. It must still distinguish a draft from fully validated 17-stage production approval.
