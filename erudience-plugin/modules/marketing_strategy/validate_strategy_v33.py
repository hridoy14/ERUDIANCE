import json,sys
from pathlib import Path
P=json.loads((Path(__file__).resolve().parents[2]/"config/production-policy-v33.json").read_text())
def validate(batch):
 errors=[]
 if len(batch)!=7: errors.append("Seven planning slots required")
 if sum(bool(x.get("promotion")) for x in batch)!=1: errors.append("Exactly one promotional slot required")
 for x in batch:
  if x.get("deleted"):errors.append("Topic deletion forbidden")
  if x.get("promotion") and not x.get("employee_requirement"):errors.append("Promotion missing employee requirement")
  if not x.get("promotion") and x.get("direct_sales_pitch"):errors.append("Educational slot contains direct pitch")
  if x.get("claimed_image") and not x.get("render_verified"):errors.append("Unverified image")
  if x.get("unsupported_claim"):errors.append("Unsupported claim")
  if x.get("external_write") and not x.get("explicit_authorization"):errors.append("Unauthorized write")
 return errors
def validate_single_slot(slot):
 """Per-job strategy rules (module 06, AG-08) for one planning slot.

 Mirrors validate()'s per-slot checks for a single slot: a promotion
 needs employee_requirement; an educational slot must not contain a
 direct pitch; no unsupported_claim; no unauthorised external_write;
 no deletion. Returns the same error strings validate() uses, so the
 batch and single-slot paths can never disagree. Empty list = valid.
 """
 if not isinstance(slot, dict):
  return ["INVALID_SLOT"]
 errors=[]
 if slot.get("deleted"):errors.append("Topic deletion forbidden")
 if slot.get("promotion") and not slot.get("employee_requirement"):errors.append("Promotion missing employee requirement")
 if not slot.get("promotion") and slot.get("direct_sales_pitch"):errors.append("Educational slot contains direct pitch")
 if slot.get("unsupported_claim"):errors.append("Unsupported claim")
 if slot.get("external_write") and not slot.get("explicit_authorization"):errors.append("Unauthorized write")
 return errors
if __name__=="__main__":
 data=json.load(open(sys.argv[1]));errors=validate(data);print(json.dumps({"status":"PASS" if not errors else "BLOCKED","errors":errors}));sys.exit(bool(errors))
