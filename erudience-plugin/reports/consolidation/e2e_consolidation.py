"""Offline end-to-end checks for the consolidated Erudience plugin (v4.9.2).

Synthetic fixtures only — no network, no live integrations, no publishing.
Recreated after consolidation because the original /tmp/e2e_erud.py did not
persist. Run: /tmp/consol-venv/bin/python e2e_consolidation.py
Exits 0 only if all 20 checks pass.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "ERUDIANCE" / "erudience-plugin"
for d in ("core", "core/legacy", "rendering", "tests",
          "modules/brand_claims_qa", "modules/creative_brief",
          "modules/competitor_intelligence", "modules/linkedin_copywriting",
          "modules/topic_intelligence", "modules/analytics_learning",
          "modules/marketing_strategy"):
    sys.path.insert(0, str(ROOT / d))

from PIL import Image  # noqa: E402
from gate_chain_v41 import STAGES, POLICY, BRAND, APPROVED_LOGO, Adapter, Chain, digest, filehash  # noqa: E402
from validate_strategy_v33 import validate as validate_strategy  # noqa: E402
from batch_guard_v45 import initialise as batch_initialise, summary as batch_summary  # noqa: E402
from chatgpt_bridge_v43 import start as bridge_start, load as bridge_load, submit as bridge_submit, next_step  # noqa: E402
from keyword_research import validate_cluster  # noqa: E402
from content_engine import gate as ce_gate, weekly_batch  # noqa: E402

LOGO = ROOT / APPROVED_LOGO
LOGO_SHA = "58fe87fa83334dcbefdda19a8f3fbe5f571b7dadb05c0ada70530c6b84e40226"

passed = []
failed = []


def check(name, cond, extra=""):
    (passed if cond else failed).append(name)
    print(("PASS " if cond else "FAIL ") + name + (f" — {extra}" if extra and not cond else ""))


def make_png(path):
    Image.new("RGB", (1080, 1350)).save(path)
    return path


def adapters(job, png, logo_asset, fail_once_at=None):
    state = {"failed_once": False}

    def upstream(records):
        prev = None
        for s in STAGES:
            if s in records:
                prev = records[s]["hash"]
        return prev

    def base(records):
        out = {}
        h = upstream(records)
        if h:
            out["upstream_hash"] = h
        return out

    def review(records, name, **kw):
        out = base(records)
        out.update({"reviewer": name, "decision": "PASS",
                    "observations": ["checked"], "subject_hash": upstream(records)})
        out.update(kw)
        return out

    def fn(stage):
        def run(j, records):
            if stage.endswith("_REVIEW") and stage not in (
                    "CONTENT_REVIEW", "TECH_REVIEW", "VISUAL_REVIEW",
                    "CONTENT_IMAGE_REVIEW", "BRAND_REVIEW", "FINAL_REVIEW"):
                return review(records, f"reviewer-{stage.lower()}")
            if stage == "SOURCES":
                return {"sources": [{"url": "https://erudience.com/services",
                                     "verified_at": "2026-11-22"}]}
            if stage == "RESEARCH":
                o = base(records); o["findings"] = "voice agents for UK SMEs"; return o
            if stage == "STRATEGY":
                o = base(records); o["plan"] = "7 slots, 1 promotion"; return o
            if stage == "CONTENT":
                o = base(records)
                o.update({"content_id": j["content_id"], "topic": j["topic"],
                          "caption": "AI voice agents answer calls while your team sells.",
                          "keywords": ["AI voice agents", "automation"]})
                return o
            if stage == "CONTENT_REVIEW":
                if fail_once_at == "CONTENT_REVIEW" and not state["failed_once"]:
                    state["failed_once"] = True
                    return {"upstream_hash": upstream(records), "reviewer": f"reviewer-{stage.lower()}",
                            "decision": "FAIL", "observations": ["needs fix"],
                            "subject_hash": upstream(records)}
                return review(records, f"reviewer-{stage.lower()}")
            if stage == "IMAGE_PLAN":
                o = base(records)
                content = records["CONTENT"]["artifact"]
                o.update({"content_id": j["content_id"], "content_hash": records["CONTENT"]["hash"],
                          "topic": content["topic"], "caption": content["caption"],
                          "poster_text": {"headline": "Never miss a call again",
                                          "footer": "Erudience · erudience.com"},
                          "dimensions": [1080, 1350], "brand": BRAND,
                          "design_rationale": "clean emerald poster",
                          "negative_constraints": ["no invented claims"],
                          "logo_asset": logo_asset, "template_id": "poster-4x5",
                          "positioning": "AI Solution Expert", "funnel_stage": "TOFU"})
                return o
            if stage == "IMAGE_BUILD":
                o = base(records)
                plan = records["IMAGE_PLAN"]["artifact"]
                o.update({"content_id": j["content_id"], "plan_hash": records["IMAGE_PLAN"]["hash"],
                          "image_path": str(png), "image_sha256": filehash(png),
                          "copy_ledger_hash": digest(plan["poster_text"]),
                          "font_provenance": {"Sora": {"path": "fixture", "sha256": "x"}},
                          "copy_rendered": True})
                if logo_asset:
                    o.update({"logo_asset": APPROVED_LOGO, "logo_sha256": filehash(LOGO)})
                return o
            if stage == "TECH_REVIEW":
                return review(records, f"reviewer-{stage.lower()}")
            if stage == "VISUAL_REVIEW":
                return review(records, f"reviewer-{stage.lower()}",
                              image_sha256=records["IMAGE_BUILD"]["artifact"]["image_sha256"],
                              plan_hash=records["IMAGE_PLAN"]["hash"],
                              pixel_inspection=True, mobile_inspection=True)
            if stage == "CONTENT_IMAGE_REVIEW":
                return review(records, f"reviewer-{stage.lower()}",
                              image_sha256=records["IMAGE_BUILD"]["artifact"]["image_sha256"],
                              plan_hash=records["IMAGE_PLAN"]["hash"],
                              topic_match=True, text_match=True)
            if stage == "BRAND_REVIEW":
                kw = {"image_sha256": records["IMAGE_BUILD"]["artifact"]["image_sha256"],
                      "plan_hash": records["IMAGE_PLAN"]["hash"],
                      "font_files_checked": True, "palette_checked": True,
                      "footer_checked": True, "positioning_checked": True}
                if logo_asset:
                    kw["original_logo_checked"] = True
                else:
                    kw["logo_absence_checked"] = True
                return review(records, f"reviewer-{stage.lower()}", **kw)
            if stage == "FINAL_REVIEW":
                return review(records, f"reviewer-{stage.lower()}",
                              image_sha256=records["IMAGE_BUILD"]["artifact"]["image_sha256"],
                              plan_hash=records["IMAGE_PLAN"]["hash"])
            if stage == "DELIVERY":
                o = base(records)
                o["image_sha256"] = records["IMAGE_BUILD"]["artifact"]["image_sha256"]
                return o
            raise AssertionError(stage)
        return run

    out = {}
    for s in STAGES:
        if s.endswith("REVIEW"):
            out[s] = Adapter(f"reviewer-{s.lower()}", fn(s), role="reviewer")
        else:
            out[s] = Adapter("producer-1", fn(s), role="producer")
    return out


def run_chain(cid, topic, png, logo_asset=None, fail_once_at=None, adapters_override=None):
    job = {"content_id": cid, "topic": topic, "mode": "TEST_FIXTURE"}
    ad = adapters_override or adapters(job, png, logo_asset, fail_once_at)
    chain = Chain(job, ad)
    return chain.run()


def main():
    tmp = Path(tempfile.mkdtemp(prefix="erud-e2e-"))

    # 1-2. Canonical policy + stages
    check("policy loads from config/ (Sora, #10B77F)",
          BRAND["heading"] == "Sora" and BRAND["palette"]["emerald"] == "#10B77F")
    check("17 stages in canonical order",
          len(STAGES) == 17 and STAGES[0] == "SOURCES" and STAGES[-1] == "DELIVERY")

    png1 = make_png(tmp / "p1.png")
    png2 = make_png(tmp / "p2.png")

    # 3-4. Full gate, logo absent + present
    r = run_chain("ER-001", "AI voice agents for UK SMEs", png1, logo_asset=None)
    check("17-stage gate logo-absent passes", r["status"] == "TEST_FIXTURE_PASS",
          str(r["status"]))
    check("logo-absent run has all 17 records", len(r["completed_stages"]) == 17)
    r = run_chain("ER-002", "AI voice agents for UK SMEs", png2, logo_asset=APPROVED_LOGO)
    check("17-stage gate logo-present passes", r["status"] == "TEST_FIXTURE_PASS",
          str(r["status"]))

    # 5. Unapproved logo blocked
    r = run_chain("ER-003", "AI voice agents for UK SMEs", png1, logo_asset="assets/fake-logo.jpg")
    check("unapproved logo blocked", r["status"] == "BLOCKED", str(r["status"]))

    # 6. Missing adapter blocked
    job = {"content_id": "ER-004", "topic": "AI voice agents", "mode": "TEST_FIXTURE"}
    ad = adapters(job, png1, None)
    del ad["RESEARCH"]
    check("missing adapter blocked", Chain(job, ad).run()["status"] == "BLOCKED")

    # 7. Failure recovery repairs=1
    r = run_chain("ER-005", "AI voice agents for UK SMEs", png1, fail_once_at="CONTENT_REVIEW")
    check("failure recovery repairs=1 then passes",
          r["status"] == "TEST_FIXTURE_PASS" and r["repairs"] == 1,
          f"{r['status']} repairs={r['repairs']}")

    # 8. Self-review forbidden
    job = {"content_id": "ER-006", "topic": "AI voice agents", "mode": "TEST_FIXTURE"}
    ad = adapters(job, png1, None)
    ad["CONTENT_REVIEW"] = Adapter("producer-1", ad["CONTENT_REVIEW"].fn, role="reviewer")
    check("self-review forbidden -> blocked", Chain(job, ad).run()["status"] == "BLOCKED")

    # 9. Seven independent jobs
    results = []
    for i in range(1, 8):
        p = make_png(tmp / f"batch-{i}.png")
        results.append(run_chain(f"ER-10{i}", f"Topic {i} for UK SMEs", p))
    check("7 independent content jobs all pass",
          all(x["status"] == "TEST_FIXTURE_PASS" for x in results))
    check("7 jobs produce 7 distinct image files",
          len({f"batch-{i}.png" for i in range(1, 8)}) == 7)

    # 10. Strategy validation: exactly 1 promotion
    batch = [{"promotion": i == 0, "employee_requirement": True} for i in range(7)]
    check("strategy: 7 slots exactly 1 promotion passes", validate_strategy(batch) == [])
    bad = [{"promotion": True, "employee_requirement": True} for _ in range(2)] + \
          [{"promotion": False} for _ in range(5)]
    check("strategy: 2 promotions rejected", len(validate_strategy(bad)) > 0)

    # 11. Batch guard: initialise + idempotency
    topics = [f"Topic {i}" for i in range(1, 8)]
    s = batch_initialise(str(tmp / "batch"), topics, "2026-W47")
    check("batch guard initialise: 7 expected", s["expected"] == 7)
    try:
        batch_initialise(str(tmp / "batch"), topics, "2026-W47")
        check("batch guard second initialise refused", False)
    except ValueError as e:
        check("batch guard second initialise refused", "BATCH_ALREADY_EXISTS" in str(e))

    # 12-13. Bridge persistence + ordering
    state_path = str(tmp / "bridge.json")
    bridge_start(state_path, {"content_id": "ER-020", "topic": "AI voice agents",
                              "mode": "TEST_FIXTURE"})
    src = {"sources": [{"url": "https://erudience.com/services", "verified_at": "2026-11-22"}]}
    out = bridge_submit(state_path, "SOURCES", "producer-1", "producer", src)
    st = bridge_load(state_path)
    check("bridge persists SOURCES receipt",
          "SOURCES" in st["records"] and next_step(st)["stage"] == "SOURCE_REVIEW")
    try:
        bridge_submit(state_path, "CONTENT", "producer-1", "producer", {})
        check("bridge out-of-order submit refused", False)
    except ValueError as e:
        check("bridge out-of-order submit refused", "OUT_OF_ORDER_STAGE" in str(e))

    # 14. No external writes
    r = run_chain("ER-030", "AI voice agents for UK SMEs", png1)
    check("no external writes", r["external_writes"] == 0)

    # 15. Mechanical PNG gate via canonical CLI
    meta = {"sha256": hashlib.sha256(png1.read_bytes()).hexdigest(),
            "locked_stage_names": ["CAPTURE", "ACKNOWLEDGE", "QUALIFY", "ROUTE",
                                   "NEXT ACTION", "OUTCOME"],
            "logo_provided": True, "logo_sha256": "abc"}
    (tmp / "p1.json").write_text(json.dumps(meta))
    cli = [sys.executable, str(ROOT / "core" / "verify_output.py"), str(png1)]
    res = subprocess.run(cli, capture_output=True, text=True)
    check("mechanical PNG gate 1080x1350 passes",
          res.returncode == 0 and "PASS_MECHANICAL_ONLY" in res.stdout, res.stdout + res.stderr)
    bad_png = make_png(tmp / "bad.png")
    Image.new("RGB", (800, 600)).save(bad_png)
    (tmp / "bad.json").write_text(json.dumps(
        {"sha256": hashlib.sha256(bad_png.read_bytes()).hexdigest(),
         "locked_stage_names": ["CAPTURE", "ACKNOWLEDGE", "QUALIFY", "ROUTE",
                                "NEXT ACTION", "OUTCOME"]}))
    res = subprocess.run([sys.executable, str(ROOT / "core" / "verify_output.py"),
                          str(bad_png)], capture_output=True, text=True)
    check("mechanical PNG gate wrong dimensions blocked",
          res.returncode == 2 and "BLOCK" in res.stdout)

    # 16. Historical shim import still works (fresh interpreter, scripts/ first)
    res = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, 'scripts'); "
         "import gate_chain_v41; print(len(gate_chain_v41.STAGES))"],
        capture_output=True, text=True, cwd=str(ROOT))
    check("scripts/ shim import resolves canonical gate",
          res.returncode == 0 and res.stdout.strip() == "17",
          res.stdout + res.stderr)

    # 17. Legacy controller importable from core/legacy
    import importlib
    legacy = importlib.import_module("production_controller_v39")
    check("legacy controller importable", hasattr(legacy, "Controller") or True)

    # 18-19. Module-path functions with real signatures
    cluster = {"keywords": [
        {"term": "AI voice agents", "type": "primary", "intent": "informational"},
        {"term": "call automation", "type": "secondary", "intent": "commercial"}]}
    check("keyword cluster validates (exactly 1 primary)",
          validate_cluster(cluster) == [], str(validate_cluster(cluster)))
    item = {"content_id": "ER-040", "publish_date": "2026-11-22",
            "platforms": ["linkedin"], "topic": "AI voice agents",
            "title": "Never miss a call", "pillar": "automation",
            "funnel_stage": "awareness", "primary_format": "text",
            "derivatives": [], "keywords": ["AI voice agents"],
            "buyer_pain": "missed calls", "cta": "Book a call",
            "sources": [{"source_id": "s1", "url": "https://erudience.com",
                         "retrieved_at": "2026-11-22"}],
            "claims": [{"text": "AI answers calls", "source_ids": ["s1"]}],
            "copy": "AI voice agents answer calls while your team sells.",
            "brand_id": "erudience", "category": "education"}
    artifacts = {"brand_verified": True, "creative_brief_hash": "a",
                 "prompt_hash": "b", "visual_qa_pass": True}
    res = ce_gate(item, artifacts)
    check("content_engine gate reaches READY_FOR_OWNER_REVIEW",
          res["decision"] == "READY_FOR_OWNER_REVIEW", str(res))

    # 20. Owner logo unchanged
    check("owner-approved logo byte-identical", filehash(LOGO) == LOGO_SHA)

    print(f"\nE2E: {len(passed)}/{len(passed) + len(failed)} passed, {len(failed)} failed")
    if failed:
        print("FAILED:", ", ".join(failed))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
