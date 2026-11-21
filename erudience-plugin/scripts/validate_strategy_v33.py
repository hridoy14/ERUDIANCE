import json,sys
from pathlib import Path
P=json.loads((Path(__file__).resolve().parents[1]/"references/production-policy-v33.json").read_text())
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
if __name__=="__main__":
 data=json.load(open(sys.argv[1]));errors=validate(data);print(json.dumps({"status":"PASS" if not errors else "BLOCKED","errors":errors}));sys.exit(bool(errors))
