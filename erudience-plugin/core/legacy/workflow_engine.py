"""Local deterministic orchestrator; explicit side-effect approvals required."""
import hashlib,json
STAGES=['RESEARCH','KEYWORDS','STRATEGY','DRAFT','FACT_QA','SEO_QA','CREATIVE','VISUAL_QA','OWNER_APPROVAL','DELIVERY']
class WorkflowError(ValueError):pass
def run(batch,receipts,approval=None,external_write=False):
    if not isinstance(batch,list) or len(batch)!=7:raise WorkflowError('SEVEN_SLOTS_REQUIRED')
    ids=[i.get('content_id') for i in batch]
    if any(not x for x in ids) or len(set(ids))!=7:raise WorkflowError('INVALID_CONTENT_IDS')
    promos=[x for x in batch if x.get('promotion')]
    if len(promos)!=1:raise WorkflowError('EXACTLY_ONE_PROMOTION')
    if not promos[0].get('employee_requirement'):raise WorkflowError('EMPLOYEE_OVERSIGHT_REQUIRED')
    if any(x.get('deleted') or x.get('unsupported_claim') for x in batch):raise WorkflowError('CONTENT_POLICY_FAILED')
    digest=hashlib.sha256(json.dumps(batch,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    result=[]
    for item in batch:
        rec=receipts.get(item['content_id'],{})
        missing=[s for s in STAGES[:8] if rec.get(s)!='PASS']
        result.append({'content_id':item['content_id'],'status':'BLOCKED' if missing else 'READY_FOR_OWNER_REVIEW','missing':missing})
    if external_write:
        if not approval or approval.get('batch_sha256')!=digest or approval.get('scope')!='external_write' or approval.get('approved') is not True:
            raise WorkflowError('EXPLICIT_SCOPED_APPROVAL_REQUIRED')
        if any(x['status']!='READY_FOR_OWNER_REVIEW' for x in result):raise WorkflowError('UNVERIFIED_BATCH_CANNOT_WRITE')
        # Never simulate success; actual adapter must perform and read back writes.
        return {'status':'BLOCKED','reason':'NO_VERIFIED_WRITE_ADAPTER','batch_sha256':digest,'items':result}
    return {'status':'READY_FOR_OWNER_REVIEW' if all(x['status']=='READY_FOR_OWNER_REVIEW' for x in result) else 'BLOCKED','batch_sha256':digest,'items':result,'external_writes':0}
