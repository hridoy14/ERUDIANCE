# Erudience Plugin — Policy Conflicts (Consolidation)

- Baseline: `main` `9e320fa6` (v4.9.2). Full C1–C22 record: `~/workspace/erudiance-plugin-work/consolidation-staging/policy-conflicts-draft.md`.
- Rule applied: **no conflict is resolved by version number alone.** A higher version number does not override a lower one, and a "current policy" file does not by itself settle a claim another file presents as an explicit owner override. **All conflicts below are UNRESOLVED** unless stated otherwise; none has a recorded owner decision in the files read.
- Owner-approved current policy as stated in `brand-policy-current.md` + `production-policy-v33.json` + SKILL.md: **Sora heading+body, emerald `#10B77F`, logo optional** (original logo only). This is itself contested (C3/C5) — that contest is the conflict.

| # | Conflict | Side A (current-policy files) | Side B | Status |
|---|---|---|---|---|
| C1 | Fonts | Sora (JSON, current-policy, SKILL, gate chain) | Inter + DM Sans (v46/v47/v38, master-command-v6, website renderers, v39/v40) | UNRESOLVED |
| C2 | Emerald | `#10B77F` (JSON, current-policy, SKILL) | `#10B981` (v46/v47/v38/v36, master-command-v6, all renderers except gate chain) | UNRESOLVED |
| C3 | Logo optional vs required | Optional (JSON, current-policy, SKILL, gate chain) | Required for new posters (v46/v47/v38); mandatory in code (v36/v37/render_poster/brief_prompt_gate/production_gate) | UNRESOLVED |
| C4 | Logo source | Bundled JPG (JSON, manifest, v46/v47) | Website-repo PNGs (v36, master-command-v6, asset-and-font-policy) | UNRESOLVED in scope; asset itself settled |
| C5 | Brand authority | JSON + current-policy (SKILL) | v46 (manifest) / v47 / Social OS BRAND.md v1.1 (v36) | UNRESOLVED |
| C6 | Canonical controller | gate_chain v41 (SKILL, runtime-v49, unified-v42) | production_controller v39 (v39 doc) / autonomous v40 (v40 doc) | UNRESOLVED (Claim A followed operationally) |
| C7 | Stage counts/names | 17 (v41) | 13 (v39/v40) / 10 (workflow) / 9 (production_gate) / 10 (content_engine) | UNRESOLVED |
| C8 | Repair targets | v41 map (brand/content-image → IMAGE_PLAN) | v39/v40 map (brand/content-match → BRIEF) | UNRESOLVED (follows C7) |
| C9 | Renderer | — (none named canonical) | brand_render v37 / website_render v38 / render_poster | UNRESOLVED |
| C10 | gate-contract-v41 brand paragraph vs gate code | Code: Sora / `#10B77F` | Document: Inter/DM Sans / `#10B981` | UNRESOLVED |
| C11 | release-compat-v48 vs gate code | Code: logo-optional, Sora-only font check | Document: gate enforces v4.7 logo rules + DM Sans block | UNRESOLVED |
| C12 | brand_policy_v36 mixed profile | Sora font check | `#10B981` palette + mandatory logo | UNRESOLVED |
| C13 | Website-first vs Sora-only scope | Sora-only active (SKILL, current-policy) | Website-first active (unified-v42, v39/v40 docs, master-command-v6) | UNRESOLVED |
| C14 | Owner approval recording | No engine records it | evidence_store model (unwired); OWNER_APPROVAL stages (unenforced) | UNRESOLVED |
| C15 | Weekly research mechanism | Required (current-policy, SKILL) | No scheduler/endpoints (runtime-v49, gate-contract-v41) | UNRESOLVED (delivery decision) |
| C16 | Promotion extra conditions | 1 slot, HOLD if unverified (JSON) | + `employee_requirement` (workflow_engine only) | UNRESOLVED |
| C17 | Font verification scope | Heading family only, live mode (gate chain) | Both families + SHA256 (website_brand/render) / 4 files (render_poster) / boolean (brief_prompt_gate) | UNRESOLVED |
| C18 | `social-os/BRAND.md:v1.1` pin | Pin required (brand_render_v37) | File does not exist in repo | UNRESOLVED |
| C19 | Step count | 3–5 steps (brand/website renderers) | Exactly 6 steps (render_poster; verify_output manifest) | UNRESOLVED |
| C20 | Command spelling | `erudiance_linkdin` (SKILL, one-command-v44, codex manifest) | `erudience_linkdin` alias (one-command-v44, batch-production-v45) | UNRESOLVED |
| C21 | Policy vs plugin version | 3.3.0 = policy version; 4.9.2 = plugin version | — | NOT A CONFLICT |
| C22 | "Supersede" claims (meta) | Newest file wins (each file's own claim) | Newest files disagree with each other | UNRESOLVED (structural) |

## Notes that matter for the owner decision
- C1: master-command-v6 records an explicit owner choice of website fonts, but expressly scoped to "this independent draft" / "THIS poster"; whether it generalises is not decided. Its "Do not ask the user again" line is written without that scope limit — the two readings conflict inside the same file.
- C3: v46 is dated 2026-11-21 and presents itself as an owner override; the current-policy file is v4.9.2 (2026-11-22). Both claim owner authority. Scope also differs inside Side B: v46/v47 require the logo for *new branded posters*, while v36/v37/render_poster/brief_prompt_gate/production_gate require it for *any* branded final.
- C5: the assertions are circular (v46 points at itself as authoritative via the manifest; v47 claims priority over "legacy logo-optional, Sora-only" — exactly what the current-policy files are; SKILL.md claims the reverse).
- C2: only the emerald token conflicts; all other palette tokens agree (paper #F6F1E9, ink #14120E, soft #615B4C, deep #0A6E3E, dark #0A100E).
- C22: the repo's conflict-resolution mechanism is "the newest file says it supersedes the old ones", but the newest files disagree with each other. The only durable resolution is an explicit owner decision per conflict (C1–C20), recorded in `config/brand-policy-current.md` with a date and a scope (all posters vs new posters vs one draft).
- The 8-item correction list for adopting the Sora/`#10B77F`/logo-optional profile is in `reports/cleanup-evidence.md` — **not applied** in v4.9.2 and not applied here.

## Post-consolidation update (2026-11-22)
- Conflicts C1-C22 remain UNRESOLVED (owner decision pending): Sora/#10B77F/logo-optional vs Inter/DM Sans/#10B981/logo-required; canonical controller v41 vs v39 vs v40; 17 vs 13 vs 10 vs 9 stages; 3 renderers; gate-contract doc contradicts its own code; `social-os/BRAND.md` v1.1 pinned but absent; owner approval recorded nowhere.
- Consolidation did NOT resolve any conflict by rewriting a renderer or a policy file. Only C21 is a non-conflict (policy version 3.3.0 vs plugin 4.9.2).
