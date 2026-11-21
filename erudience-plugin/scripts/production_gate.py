"""Fail-closed production acceptance. Receipts cannot self-certify; no external writes."""
import hashlib,json,re
from pathlib import Path
STAGES=('RESEARCH','KEYWORDS','STRATEGY','DRAFT','FACT_QA','SEO_QA','BRAND_QA','CREATIVE','VISUAL_QA')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def validate(job,receipts,brand,root):
    root=Path(root).resolve();errors=[]; cid=job.get('content_id')
    if not cid:errors.append('CONTENT_ID_REQUIRED')
    for stage in STAGES:
        rec=receipts.get(stage)
        if not isinstance(rec,dict) or rec.get('content_id')!=cid or rec.get('stage')!=stage or rec.get('status')!='PASS':
            errors.append('MISSING_VERIFIED_STAGE:'+stage);continue
        path=rec.get('artifact_path'); expected=rec.get('artifact_sha256')
        try:
            candidate=(root/path).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file() or not re.fullmatch('[0-9a-f]{64}',str(expected)) or digest(candidate)!=expected:
                errors.append('INVALID_STAGE_ARTIFACT:'+stage)
        except (TypeError,ValueError,OSError):errors.append('INVALID_STAGE_ARTIFACT:'+stage)
        if not rec.get('reviewer') or rec['reviewer']==rec.get('producer') or not rec.get('reviewed_at'):
            errors.append('INDEPENDENT_REVIEW_MISSING:'+stage)
    for label in ('logo','font_heading','font_body'):
        item=brand.get(label)
        if not isinstance(item,dict) or not item.get('approved_source') or not item.get('sha256') or not item.get('path'):
            errors.append('BRAND_ASSET_UNVERIFIED:'+label);continue
        try:
            path=(root/item['path']).resolve()
            if not path.is_relative_to(root) or not path.is_file() or digest(path)!=item['sha256']:
                errors.append('BRAND_ASSET_HASH_MISMATCH:'+label)
        except (TypeError,ValueError,OSError):errors.append('BRAND_ASSET_HASH_MISMATCH:'+label)
    if not brand.get('palette_approved') or not brand.get('brand_voice_approved'):
        errors.append('BRAND_POLICY_UNVERIFIED')
    if job.get('image_generated') and not job.get('image_inspection_receipt'):
        errors.append('IMAGE_INSPECTION_MISSING')
    if job.get('external_write') or job.get('publish'):
        errors.append('EXTERNAL_WRITE_DISABLED')
    return {'status':'BLOCKED' if errors else 'READY_FOR_OWNER_REVIEW','errors':sorted(set(errors)),'external_writes':0}
