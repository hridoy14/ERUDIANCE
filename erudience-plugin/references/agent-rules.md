# agent-rules.md — the 18 agent roles and how agents run

Consolidated from the agent sources for the Erudiance plugin. Every rule below
is tagged with its source. No rule was invented.

## 0. How to read this file — and an honest note on sources

- Primary source: `erudience-plugin/agents/roles-v34.md` (NOT moved, modified,
  or deleted; it stays where it is). It is the ONLY source that defines the 18
  roles in detail (input, output, gate per role). All of §1 and §2 comes from
  it, tagged `[source: agents/roles-v34.md]`.
- Secondary sources: the agent sections of `references/master-command-v6.md`
  (tagged `[v6]`) and `references/orchestrator-v2.md` (tagged `[v2]`).
- Agent-adjacent rules also appear in the references files and are collected
  in §6, tagged with their file (e.g. `[v34]`, `[v42]`, `[v40]`, `[v31]`,
  `[v35]`). These are reviewer-separation, controller-independence, and
  role-listing rules — they do not define any additional agent role.
- Honest finding: apart from the role list in [v34] and the reviewer/controller
  rules in §6, the references/ files contain NO agent rule beyond what is in
  `agents/roles-v34.md`, `master-command-v6.md`, and `orchestrator-v2.md`. No
  per-agent prompt, agent-to-agent messaging protocol, or agent staffing rule
  exists in any source read for this file, so none is written here.
- Scope: agent roles and how agents run. Execution stages, gates, rendering,
  and delivery mechanics live in automation-rules.md; this file states only the
  agent rules that govern them (e.g. "reviewers cannot be their immediate
  producer").
- Brand tokens referenced by agent rules: Sora only, emerald #10B77F, logo
  optional (verified website tokens 2026-11-24). Where a source text says
  Inter / DM Sans / #10B981 it is carried with a
  `[STALE — superseded by verified website tokens 2026-11-24]` note, not
  silently rewritten.

## 1. The 18 specialist roles

[source: agents/roles-v34.md] Logical roles, not claimed as deployed autonomous
services [v34]. Logical roles can run in one orchestrator or as separate
agents [v34].

| # | Role | Input | Output | Gate |
|---|---|---|---|---|
| 1 | Business intelligence | verified portfolio | service map | no invented offer |
| 2 | Competitor research | public sources | 50-record target dataset | provenance and coverage |
| 3 | Buyer research | permitted buyer signals | persona and pain clusters | hypothesis separated from evidence |
| 4 | Market research | dated sources | trend brief | freshness and geography |
| 5 | Keyword research | topic and source data | typed keyword cluster | primary uniqueness and evidence |
| 6 | Search intent | cluster and buyer question | intent/funnel map | relevance |
| 7 | Topic intelligence | existing library and new ideas | scored, versioned topics | no destructive delete |
| 8 | Content strategist | topics and constraints | 7-slot weekly plan | one promotion |
| 9 | Funnel planner | personas and plan | TOFU/MOFU/BOFU allocation | stage/CTA consistency |
| 10 | Content writer | approved brief | original caption | no unsupported claims |
| 11 | SEO optimizer | draft and cluster | natural-language revision | no keyword stuffing |
| 12 | Editorial reviewer | draft and target audience | clarity verdict | actionable and understandable |
| 13 | Fact checker | source registry and claims | evidence verdict | independent source checks |
| 14 | Creative director | verified copy and brand | creative brief | brand constraints |
| 15 | Image producer | brief and permitted assets | actual render file | file existence |
| 16 | Brand QA | render and manifest | inspection receipt | verified logo/fonts/readability |
| 17 | Delivery controller | approvals and receipts | review package or authorized handoff | explicit scope, readback |
| 18 | Analytics | observed permitted metrics | descriptive report | no invented attribution |

## 2. Per-role rules

All entries in this section are [source: agents/roles-v34.md] unless tagged
otherwise.

2.1. Business intelligence — input: verified portfolio; output: service map;
gate: no invented offer.
2.2. Competitor research — input: public sources; output: 50-record target
dataset; gate: provenance and coverage.
2.3. Buyer research — input: permitted buyer signals; output: persona and pain
clusters; gate: hypothesis separated from evidence.
2.4. Market research — input: dated sources; output: trend brief; gate:
freshness and geography.
2.5. Keyword research — input: topic and source data; output: typed keyword
cluster; gate: primary uniqueness and evidence.
2.6. Search intent — input: cluster and buyer question; output: intent/funnel
map; gate: relevance.
2.7. Topic intelligence — input: existing library and new ideas; output:
scored, versioned topics; gate: no destructive delete.
2.8. Content strategist — input: topics and constraints; output: 7-slot weekly
plan; gate: one promotion.
2.9. Funnel planner — input: personas and plan; output: TOFU/MOFU/BOFU
allocation; gate: stage/CTA consistency.
2.10. Content writer — input: approved brief; output: original caption; gate:
no unsupported claims.
2.11. SEO optimizer — input: draft and cluster; output: natural-language
revision; gate: no keyword stuffing.
2.12. Editorial reviewer — input: draft and target audience; output: clarity
verdict; gate: actionable and understandable.
2.13. Fact checker — input: source registry and claims; output: evidence
verdict; gate: independent source checks.
2.14. Creative director — input: verified copy and brand; output: creative
brief; gate: brand constraints.
2.15. Image producer — input: brief and permitted assets; output: actual render
file; gate: file existence.
2.16. Brand QA — input: render and manifest; output: inspection receipt; gate:
verified logo/fonts/readability. (The "verified fonts" in this gate refers to
the fonts in the source text. [STALE — superseded by verified website tokens
2026-11-24: Sora only.])
2.17. Delivery controller — input: approvals and receipts; output: review
package or authorized handoff; gate: explicit scope, readback.
2.18. Analytics — input: observed permitted metrics; output: descriptive
report; gate: no invented attribution.

## 3. Non-negotiable instructions for all agents

[source: agents/roles-v34.md]

3.1. No fabricated competitor metrics, buyer quotes, rankings, testimonials,
ROI, service capability or client results.
3.2. No claims of successful remote action without readback.
3.3. Never store secrets in files or logs.
3.4. Block unsupported external writes.
3.5. Each agent records its source IDs, output hash and uncertainty; the
controller validates rather than trusting agent self-certification.

## 4. Agent rules from master-command-v6.md [v6]

4.1. `/SYSTEM /ROLE /EXECUTE_NOT_JUST_PLAN`: act as a B2B Buyer Researcher,
LinkedIn Content Strategist, Brand Art Director, Editorial Infographic
Designer, Asset Engineer, Visual QA Reviewer, and Delivery Operator. Produce
ONE real, legible, premium LinkedIn PNG using the supplied topic. Execute all
feasible steps. Never substitute a description, mock link, or generated prompt
for an actual image. Mark every unperformed verification as NOT VERIFIED.
4.2. The seven acting roles in §4.1 are a single-agent execution instruction in
[v6]; they are NOT seven additional roles beyond the 18 in §1. The 18-role
table in `agents/roles-v34.md` remains the role definition. (No conflict:
[v34] states logical roles can run in one orchestrator.)
4.3. Do not claim that a system command has been installed or a task has been
completed without evidence. [v6]
4.4. [v6] The Visual QA Reviewer role: verify exact words against the exported
image, not only source code. For every issue record defect, severity,
correction, and reinspection result.

## 5. Agent rules from orchestrator-v2.md [v2]

5.1. The controller must approve the plan before render.
5.2. The controller issues APPROVE_FOR_OWNER_REVIEW, REVISE or BLOCK with gate
receipts.
5.3. Owner reviews preview; record explicit APPROVE or REJECT with timestamp
and content hash. On rejection, collect reason, repair, rerun gates, and
request approval again. Owner approval is never assumed.
5.4. If REVISE: identify the failed stage, revise that stage, invalidate all
downstream gate receipts and rerun downstream stages; max three render
attempts per item. If BLOCK: stop and state the required remedy. No gate
bypass by manual "force pass".
5.5. Social OS handoff: prepare an idempotent payload and read-only
compatibility check first. After separate explicit permission, write only
authorised draft record(s) using connected official tools/API; verify the
resulting record ID and read-after-write. Never auto-publish, auto-schedule,
mutate approval flags, or change live workflows.
5.6. Analytics after actual publishing by an authorised user/system: pull
LinkedIn impressions, unique reach if available, saves, meaningful comments,
website/profile clicks, qualified enquiries, meetings and conversions where
permitted. Tag by post and UTM; compare like-for-like time windows; report
missing fields, confounders and no guaranteed growth.
5.7. Input contract roles: if a topic is missing, propose a topic grounded in
research and label it PROPOSED, not approved. Do not silently invent claims or
customer cases.

## 6. Agent-adjacent rules from the references files

These rules govern how agents/reviewers relate to each other and to the
controller. They do not define additional roles.

6.1. [v34] The 18 roles are listed as: business intelligence; competitor
research; buyer research; market research; keyword research; search intent;
topic intelligence; content strategist; funnel planner; content writer; SEO
optimizer; editorial reviewer; fact checker; creative director; image
producer; brand QA; delivery controller; analytics. See
`agents/roles-v34.md` for detailed ownership and handoffs. Logical roles can
run in one orchestrator or separate agents. Deterministic validators must not
be replaced by model self-assessment.
6.2. [v42] Gate ownership: reviewers cannot be their immediate producer.
6.3. [v39] Reviewers must inspect actual rendered pixels and mobile-size
legibility; record observations, exact poster topic, brand assessment and
reviewer identity. A reviewer PASS without real independent inspection is
prohibited; a missing runtime reviewer means BLOCKED.
6.4. [v40] Independent reviewer code paths are provided for content matching
and brand token checks. They are deterministic validators, not human inspection
and not cryptographically authenticated identities. Visual QA requires a real
registered adapter that opens the actual poster at full and mobile sizes. A
human or separately trusted review service must be configured for real visual
sign-off. Passing a `reviewer_id` string alone is not proof of independence.
Do not claim real visual QA if using a fixture.
6.5. [v39] The controller validates receipt structure and binding but cannot
cryptographically authenticate reviewer identity or establish semantic
correctness.
6.6. [v31] The controller is independent from the generator and must check
actual artifacts, not self-reported success.
6.7. [v34] No stage self-certification.
6.8. [v35] Do not treat a tool-generated image or LLM-written caption as
evidence of plugin execution. Report each adapter as CONFIGURED/NOT_CONFIGURED
and real tests as PASS/BLOCKED/NOT_TESTED.
6.9. [v39] A revision must actually be executed by the producer; the controller
does not invent revised content or call an AI model by itself.
6.10. [v42] All artifacts bind upstream hash; image reviews bind image hash and
plan hash. (Binding detail lives in automation-rules.md §5.)

## 7. How agents run together

7.1. [v34] Workflow graph the roles operate across: RESEARCH → KEYWORDS →
STRATEGY → DRAFT → FACT_QA → SEO_QA → CREATIVE → VISUAL_QA → OWNER_APPROVAL
→ DELIVERY → ANALYTICS. Each transition requires an independently recorded
receipt. (Full stage rules: automation-rules.md §3.4.)
7.2. [v31] For each content_id in the ordered calendar: run dependency actions;
for each failed repairable stage retry up to 3 with fresh validation and
hashes; stop the item after 3 and mark BLOCKED. Never auto-retry authorization,
authentication, legal approval, or unavailable evidence.
7.3. [v34] Preserve topic history and prior approved artifacts; revisions
create new versions.
7.4. [v2] The controller must approve the plan before render (also §5.1).
7.5. [v6] Execution order the acting roles follow: verify owner instruction →
verify website fonts → verify Social OS brand → fetch official logo → fetch
approved benchmark → verify LinkedIn specs → research market → define buyer
job → select style → lock copy → load fonts → layout → render real PNG →
verify file bytes → visual inspection → mobile QA → correct and re-render →
compare with benchmark → show image in chat → attach verified PNG → QA report
→ request owner approval. (The font step name is carried verbatim from [v6].
[STALE — superseded by verified website tokens 2026-11-24: Sora only.])

## 8. What is NOT defined in any source (honest gaps)

8.1. No source read for this file gives a per-agent prompt, a per-agent tool
allowance beyond the role table, an agent-to-agent messaging protocol, or a
staffing rule for when roles run as one agent versus separate agents — beyond
[v34] "logical roles can run in one orchestrator or separate agents".
8.2. No source names a human owner for any individual role, a role-level
escalation path, or a per-role retry limit beyond the stage-level caps in
automation-rules.md §6.
8.3. Nothing above was invented to fill these gaps.

## 9. Conflicts register

- C-A1 — Single-agent acting vs 18 roles: [v6] instructs one agent to act as
  seven roles at once; [v34]/[roles-v34] define 18 logical specialist roles.
  Not a contradiction: [v34] states logical roles can run in one orchestrator
  or separate agents. Recorded for clarity.
- C-A2 — Brand QA gate fonts: [roles-v34] requires Brand QA to verify
  "logo/fonts/readability"; the font value in the older sources is Inter/DM
  Sans, superseded by verified website tokens 2026-11-24 (Sora only). The gate
  itself is unchanged; only the font value is stale. See §2.16.
- C-A3 — Reviewer identity: [v39] requires reviewer identity to be recorded,
  while [v39]/[v40] state the controller cannot cryptographically authenticate
  reviewer identity and a `reviewer_id` string alone is not proof of
  independence. Both are kept: record the identity, but do not treat the
  string as proof.

## 10. Source map

- agents/roles-v34.md → §1 (table), §2 (per-role rules), §3 (non-negotiables).
- references/master-command-v6.md (agent sections only) → §4, §7.5.
- references/orchestrator-v2.md (agent sections) → §5, §7.4.
- references/system-architecture-v34.md (role list, self-certification) →
  §6.1, §6.7, §7.1, §7.3.
- references/unified-system-v42.md (gate ownership) → §6.2.
- references/execution-state-machine-v39.md (reviewer rules) → §6.3, §6.5,
  §6.9.
- references/autonomous-execution-v40.md (reviewer trust boundary) → §6.4.
- references/master-action-v31.md (controller independence, retry) → §6.6,
  §7.2.
- references/production-execution-v35.md (adapter honesty) → §6.8.
- Note: references/batch-production-v45.md, references/one-command-v44.md,
  and references/one-action-production-contract.md contain no agent rule beyond
  the reviewer-inspection rules already covered via §6.3–6.4 (actual-pixel
  inspection, evidence-backed review); no additional agent role or rule was
  found in them.
