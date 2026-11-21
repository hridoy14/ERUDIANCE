"""Local structural batch gate; NOT a substitute for remote Social OS readback."""
import hashlib, json, sys

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def validate_batch(batch):
    errors=[]
    items=batch.get('items', [])
    expected=batch.get('expected_count', 7)
    if len(items)!=expected: errors.append('COUNT_MISMATCH')
    ids=[x.get('content_id') for x in items]
    if len(set(ids))!=len(ids) or any(not x for x in ids): errors.append('INVALID_OR_DUPLICATE_IDS')
    for x in items:
        cid=x.get('content_id','unknown')
        for k in ('copy','creative_brief_hash','prompt_hash','image_sha256','qa_receipt'):
            if not x.get(k): errors.append(f'{cid}:MISSING_{k.upper()}')
        if x.get('controller_decision')!='PASS': errors.append(f'{cid}:CONTROLLER_NOT_PASS')
    return {'decision':'PASS' if not errors else 'BLOCK','errors':errors,'manifest_sha256':digest(batch)}

if __name__=='__main__':
    with open(sys.argv[1],encoding='utf-8') as f: payload=json.load(f)
    result=validate_batch(payload)
    print(json.dumps(result,indent=2))
    sys.exit(0 if result['decision']=='PASS' else 2)
