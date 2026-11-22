# Erudience Plugin — Release Verification (v4.9.2)

- Release candidate branch: `maintenance/erudience-v4.9.2` (from `main@c54e5b0`)
- Plugin ID (per task): `plugins_6b00c86652c0819193d3aa590c3fd8d3`
- Previous Plugin Creator release (per task): `v4.9.1`, release ID `pluginrel_6b02013bf5b081918f297be6d12ce6db` — **preserved; not overwritten**
- Date: 2026-11-22

## Version synchronisation — verified

| Manifest | Version |
|---|---|
| `plugin.json` | 4.9.2 |
| `.agent-plugin/plugin.json` | 4.9.2 |
| `.claude-plugin/plugin.json` | 4.9.2 |
| `.codex-plugin/plugin.json` | 4.9.2 |
| `plugin.yaml` | 4.9.2 (was 4.6.0) |
| `.app.json` | 4.9.2 (was 4.6.0) |
| `skills/erudience/SKILL.md` heading | v4.9.2 |
| `references/brand-policy-current.md` heading | v4.9.2 |
| `README.md` | v4.9.2 |

All six manifests parse (JSON/YAML validated by the version-sync check and by the test runs that load `production-policy-v33.json`). Plugin identity/name/description/entrypoint unchanged except the version bump: name `erudience`, entrypoint `skills/erudience/SKILL.md`, description "Erudience seven-post LinkedIn content and image workflow with Sora typography, verified brand policy and optional authentic logo."

## What v4.9.2 contains

- **Added:** owner-approved logo `assets/erudience-owner-approved-logo-2026-11-21.jpg` (JPEG 1536×1536, 55,210 bytes, SHA-256 `58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226`; copied byte-identical from the owner upload `workspace/user/files/1000167983_0_1tk2.jpg`, visually verified against `owner-approved-brand-v46.md`). This unblocks the logo-present path in `gate_chain_v41.py`.
- **Fixed:** `scripts/verify_output.py` import safety (top-level argparse/`sys.exit()` moved into `main()`); new `scripts/test_verify_output.py` (5 tests).
- **Added reports:** `reports/source-inventory.md`, `reports/architecture-audit.md`, `reports/dependency-map.md`, `reports/regression-results.md`, `reports/cleanup-evidence.md`, `reports/release-verification.md` (this file).
- **Modified:** 6 manifests (version only), `README.md` (v4.9.2 status, counts, test results, preserved historical notes), `skills/erudience/SKILL.md` (heading only), `references/brand-policy-current.md` (heading only), `scripts/verify_output.py` (import guard only).
- **Deleted:** 9 historical README stubs (`README-v33/34/35/36/37/39/40/41/42.md`) — unique info preserved in `README.md` (see `reports/cleanup-evidence.md`); zero active references; regression 112/112 before and after.
- **Not changed:** no legacy controller, renderer, reference doc, or test assertion was rewritten; no brand tokens were rewritten (see Known limitations).

## Verification evidence

- Compile: `python -m compileall -q scripts tests_content_engine.py` — OK.
- Full regression: **112 tests passed / 0 failed** (88 scripts + 10 content-engine + 14 integration), Python 3.12.3 / Pillow 13.0.0, isolated venv. Baseline on `main` was 107/107; +5 are the new `verify_output` tests.
- Offline E2E (synthetic fixtures, `/tmp/e2e_erud.py`): **20/20 passed** — 17-stage gate logo-absent + logo-present, failure recovery (repairs == 1), unapproved-logo block, missing-adapter block, 7-content batch with exactly 1 promotion, batch idempotency, bridge persistence, strategy validation, external-write refusal, mechanical PNG gate.
- No external writes during tests; no network calls in `scripts/`; no secrets in the plugin tree; `__pycache__` removed before commit.
- Release candidate artifact: `~/workspace/erudiance-plugin-work/erudience-plugin-v4.9.2-rc.zip` (plugin directory only, no credentials, no temp files, no `__pycache__`).

## GitHub delivery

- Branch URL (intended — branch exists locally; **not yet live on GitHub** because push is blocked, see below): https://github.com/hridoy14/ERUDIANCE/tree/maintenance/erudience-v4.9.2
- Commit SHA: `0fd2853e99a76a8a435ab2aea6006e437ffb1d3e` ("Erudiance plugin v4.9.2 release candidate", 27 files changed, +556/−47, on local branch `maintenance/erudience-v4.9.2`; commit identity used: `hridoy14 <contact@erudience.com>` — repo-local config only, handle + author email already public in the repo manifest)
- Pull request URL: **not created — blocked by the push blocker below**
- **Push blocker (exact):** `git push -u origin maintenance/erudience-v4.9.2` fails with `fatal: could not read Username for 'https://github.com': terminal prompts disabled` (exit 128). Cause: this environment has no GitHub credentials — `gh auth status` reports "You are not logged into any GitHub hosts", no credential helper is configured, and the SSH route fails (`kex_exchange_identification: read: Connection reset by peer`). HTTPS read works (public repo) but write needs authentication, which this agent does not have and must not request as raw credentials.
- **Unblock path (for the parent agent / owner):** push the already-committed local branch from a session with GitHub access (browser-signed-in as hridoy14, or `gh auth login`), e.g. `git push -u origin maintenance/erudience-v4.9.2` from `~/workspace/erudiance-plugin-work/ERUDIANCE`, then create the PR to `main` with the summary in this file. Nothing was force-pushed, no history was rewritten, and nothing was committed to `main`.
- Merge: only if permissions + owner authorisation permit AND all checks pass; otherwise the PR is left ready for review.

## Plugin Creator release (v4.9.2 publish)

- **Status: BLOCKED — no authorised Plugin Creator integration is available to this agent.** No Plugin Creator connector, API credential, or publishing flow exists in this environment, and the task's Plugin ID / current release ID could not be read back from any live Plugin Creator system. **No v4.9.2 publish was performed and none is claimed.**
- What is provided instead: the validated release candidate artifact above (`erudience-plugin-v4.9.2-rc.zip`) + this branch/PR for review. To publish, the owner (or an agent with Plugin Creator access) must: (1) verify Plugin ID `plugins_6b00c86652c0819193d3aa590c3fd8d3` and confirm the current release is still v4.9.1 (`pluginrel_6b02013bf5b081918f297be6d12ce6db`); (2) upload the RC zip; (3) publish as v4.9.2; (4) read back the published version + file inventory and record the new release ID here.
- The v4.9.1 release is preserved until v4.9.2 is verified after publishing.

## Known limitations (honest, not resolved in v4.9.2)

1. **Brand dual-profile conflict (owner decision required):** canonical JSON profile (Sora / `#10B77F` / logo optional) vs website-first profile (Inter/DM Sans / `#10B981` / logo required for new posters, per v46/v47/v48 + `master-command-v6.md`'s recorded owner choice). The 8-file correction list for adopting the JSON profile is recorded in `reports/cleanup-evidence.md`; applying it would delete the website-first renderers' unique functionality and require re-encoding 4 test files, so it was not applied. `brand_render_v37` also pins `brand_policy == 'social-os/BRAND.md:v1.1'`, a file that does not exist in this repo.
2. **No live integrations:** all external integrations remain NOT_CONFIGURED (OpenAI/Anthropic/Google Search Console); no live research, font rendering, human visual QA, or publishing was performed or claimed. `evidence_store.py` (the only owner-approval model) is unwired.
3. **Workflow gaps in `gate_chain_v41`:** `RESEARCH`/`STRATEGY` have no stage-specific checks; `FINAL_REVIEW` has none beyond image/plan binding; live-mode font verification covers the heading family only; no owner-approval field exists — terminal status is `READY_FOR_OWNER_REVIEW`.
4. **No font binaries in the repo:** Sora/Inter/DM Sans must be supplied as installed paths; renderers fail closed without them. No dependency manifest (`requirements.txt`/`pyproject.toml`); Pillow is declared only in CI.
5. **No tests for:** `evidence_store`, `batch_gate`, `brief_prompt_gate`, `website_render_v38`, `render_poster` (unchanged from baseline).
6. **Production readiness is NOT claimed:** this is a verified source release candidate (code + tests + docs + logo), not a live production approval.
