"""Erudience canonical controller (stable import path; policy v4.9). Inject REAL adapters; no mock evidence in live mode.
No publishing, network calls or side effects. A reviewer must be an independently registered adapter.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256
from PIL import Image
import json, re

STAGES=('SOURCES','SOURCE_REVIEW','RESEARCH','RESEARCH_REVIEW','STRATEGY','STRATEGY_REVIEW','CONTENT','CONTENT_REVIEW','IMAGE_PLAN','PLAN_REVIEW','IMAGE_BUILD','TECH_REVIEW','VISUAL_REVIEW','CONTENT_IMAGE_REVIEW','BRAND_REVIEW','FINAL_REVIEW','DELIVERY')
REVIEWS={s for s in STAGES if s.endswith('REVIEW')}
REPAIR={'SOURCE_REVIEW':'SOURCES','RESEARCH_REVIEW':'RESEARCH','STRATEGY_REVIEW':'STRATEGY','CONTENT_REVIEW':'CONTENT','PLAN_REVIEW':'IMAGE_PLAN','TECH_REVIEW':'IMAGE_BUILD','VISUAL_REVIEW':'IMAGE_BUILD','CONTENT_IMAGE_REVIEW':'IMAGE_PLAN','BRAND_REVIEW':'IMAGE_PLAN','FINAL_REVIEW':'IMAGE_BUILD'}
REPAIR.update({s:s for s in STAGES if s not in REPAIR})
def _policy():
 return json.loads((Path(__file__).resolve().parent.parent/'config'/'production-policy-v33.json').read_text(encoding='utf-8'))
POLICY=_policy()
BRAND=POLICY['brand']
APPROVED_LOGO=POLICY['brand_assets']['approved_logo_path']

class GateFailure(Exception):
 def __init__(self,code,repair_at=None):super().__init__(code);self.repair_at=repair_at

def digest(o):return sha256(json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def filehash(p):return sha256(Path(p).read_bytes()).hexdigest()
def require(ok,code):
 if not ok:raise GateFailure(code)

# Live-mode evidence labels for RESEARCH (D-14). Fixture mode never sees these.
EVIDENCE_LABELS={'LIVE_VERIFIED','CACHED_VERIFIED','USER_SUPPLIED','MODEL_INFERENCE','NOT_VERIFIED'}
# D-22: recognised kinds of inspection evidence. A kind only proves the file was
# produced by a named route; it cannot prove a human actually looked.
INSPECTION_EVIDENCE_KINDS={'human_review','independent_service','pixel_report'}

def _allowed_roots(job):
 roots=[Path.cwd().resolve(),Path(__file__).resolve().parent.parent]
 if isinstance(job,dict):
  for key in ('state_dir','evidence_dir'):
   v=job.get(key)
   if v:
    try:roots.append(Path(v).resolve())
    except (TypeError,ValueError,OSError):pass
 return roots

def _confine(path,allowed_roots):
 """D-15: mirror core/legacy/production_gate.py — a path must resolve under an allowed root."""
 try:candidate=Path(path).resolve()
 except (TypeError,ValueError,OSError):return False
 return any(candidate.is_relative_to(root) for root in allowed_roots)
@dataclass
class Adapter:
 name:str
 fn:object
 role:str='producer'

class Chain:
 def __init__(self,job,adapters,limit=3):
  require(job.get('content_id') and job.get('topic'),'JOB_REQUIRED')
  self.job=job;self.adapters=adapters;self.limit=limit;self.records={};self.trace=[];self.revisions=0;self.status='ACTIVE'
 def verify(self,s,out,a):
  require(isinstance(out,dict) and bool(out),'EMPTY_OUTPUT')
  prev=STAGES[STAGES.index(s)-1] if s!=STAGES[0] else None
  if prev:require(out.get('upstream_hash')==self.records[prev]['hash'],'UPSTREAM_HASH_MISMATCH')
  if s in REVIEWS:
   require(a.role=='reviewer' and out.get('reviewer')==a.name,'REVIEWER_ADAPTER_REQUIRED')
   require(out.get('decision')=='PASS' and isinstance(out.get('observations'),list) and out['observations'],'REVIEW_NOT_EVIDENCED')
   require(out.get('subject_hash')==self.records[prev]['hash'],'REVIEW_WRONG_SUBJECT')
   require(a.name!=self.records[prev]['adapter'],'SELF_REVIEW_FORBIDDEN')
  if s=='SOURCES':require(out.get('sources') and all(x.get('url') and x.get('verified_at') for x in out['sources']),'SOURCE_PROVENANCE_REQUIRED')
  if self.job.get('mode')!='TEST_FIXTURE':
   # D-15 path confinement (live mode only): every file path the gate reads must
   # resolve under cwd, the plugin root, or the job's state/evidence dir.
   _roots=_allowed_roots(self.job)
   _paths=[]
   if out.get('image_path'):_paths.append(out['image_path'])
   if out.get('inspection_evidence_path'):_paths.append(out['inspection_evidence_path'])
   _fp=out.get('font_provenance')
   if isinstance(_fp,dict):
    for _entry in _fp.values():
     if isinstance(_entry,dict) and _entry.get('path'):_paths.append(_entry['path'])
   for _p in _paths:require(_confine(_p,_roots),'PATH_OUTSIDE_ALLOWED_ROOT')
   if s in REVIEWS:
    require(out.get('inspection_evidence_path') and Path(out['inspection_evidence_path']).is_file() and out.get('inspection_evidence_sha256')==filehash(out['inspection_evidence_path']),'INDEPENDENT_INSPECTION_EVIDENCE_REQUIRED')
    # D-22 (partial): the inspection file must be non-empty, and a declared kind
    # must be a recognised one. Content-substance verification (that a human
    # actually looked) remains a host responsibility — the gate cannot prove it.
    require(Path(out['inspection_evidence_path']).stat().st_size>0,'INDEPENDENT_INSPECTION_EVIDENCE_REQUIRED')
    if out.get('inspection_evidence_kind') is not None:require(out['inspection_evidence_kind'] in INSPECTION_EVIDENCE_KINDS,'INSPECTION_EVIDENCE_KIND_INVALID')
   if s=='SOURCES':require(all(x.get('verified_at')!='fixture-only' and x.get('source_sha256') for x in out['sources']),'LIVE_SOURCE_PROVENANCE_REQUIRED')
   if s=='RESEARCH':
    _ev=out.get('research_evidence')
    require(isinstance(_ev,list) and len(_ev)>0,'RESEARCH_EVIDENCE_REQUIRED')
    for _item in _ev:
     require(isinstance(_item,dict) and _item.get('url') and _item.get('verified_at') and _item.get('evidence_label') in EVIDENCE_LABELS,'RESEARCH_EVIDENCE_INVALID')
     if _item.get('evidence_label')=='LIVE_VERIFIED':require(_item.get('provider') and _item.get('retrieved_at') and _item.get('source_sha256'),'RESEARCH_EVIDENCE_INVALID')
   if s=='STRATEGY':
    _st=out.get('strategy')
    require(isinstance(_st,dict),'STRATEGY_EVIDENCE_REQUIRED')
    require(_st.get('slots')==7 and _st.get('promotion_count')==1 and not _st.get('unsupported_claim') and not _st.get('unauthorised_write'),'STRATEGY_PROMOTION_INVALID')
    if _st.get('promotion'):require(isinstance(_st['promotion'],dict) and bool(_st['promotion'].get('employee_requirement')),'STRATEGY_PROMOTION_INVALID')
   if s=='FINAL_REVIEW':
    _fc=out.get('final_checklist')
    require(isinstance(_fc,dict) and all(_fc.get(_k) is True for _k in ('content_locked','image_verified','brand_checked','approval_pending')),'FINAL_CHECKLIST_INCOMPLETE')
   if s=='IMAGE_BUILD':
    for family in {BRAND['heading'],BRAND['body']}:
     entry=out.get('font_provenance',{}).get(family)
     require(isinstance(entry,dict) and entry.get('path') and Path(entry['path']).is_file() and entry.get('sha256')==filehash(entry['path']),'LIVE_FONT_BINARY_NOT_VERIFIED')
  if s=='CONTENT':require(out.get('content_id')==self.job['content_id'],'CONTENT_ID_MISMATCH')
  if s=='CONTENT':require(out.get('topic')==self.job['topic'] and out.get('caption') and out.get('keywords'),'CONTENT_NOT_LOCKED')
  if s=='IMAGE_PLAN':
   require(out.get('content_id')==self.job['content_id'],'PLAN_CONTENT_ID_MISMATCH')
   content=self.records['CONTENT']['artifact'];require(out.get('content_hash')==self.records['CONTENT']['hash'],'PLAN_CONTENT_MISMATCH')
   require(out.get('topic')==content['topic'] and out.get('caption')==content['caption'],'PLAN_CAPTION_MISMATCH')
   require(out.get('poster_text') and out.get('dimensions')==[1080,1350],'PLAN_COPY_OR_DIMENSIONS')
   require(out.get('brand')==BRAND,'PLAN_BRAND_MISMATCH')
   require(out.get('design_rationale') and out.get('negative_constraints'),'PLAN_REVIEW_INPUTS_MISSING')
   require(out.get('logo_asset') in (None, APPROVED_LOGO),'UNAPPROVED_LOGO_FORBIDDEN')
   require(out.get('template_id') and out.get('positioning') and out.get('funnel_stage'),'BRAND_STRATEGY_PLAN_REQUIRED')
   require(out.get('poster_text',{}).get('headline') and out.get('poster_text',{}).get('footer'),'POSTER_COPY_INCOMPLETE')
  if s=='IMAGE_BUILD':
   require(out.get('content_id')==self.job['content_id'],'IMAGE_CONTENT_ID_MISMATCH')
   plan=self.records['IMAGE_PLAN'];require(out.get('plan_hash')==plan['hash'],'BUILDER_PLAN_MISMATCH')
   p=out.get('image_path');require(p and Path(p).is_file() and filehash(p)==out.get('image_sha256'),'IMAGE_BYTES_MISMATCH')
   with Image.open(p) as im:require(im.format=='PNG' and im.size==(1080,1350) and im.mode in ('RGB','RGBA'),'INDIVIDUAL_PORTRAIT_PNG_REQUIRED')
   require(out.get('copy_ledger_hash')==digest(plan['artifact']['poster_text']),'IMAGE_COPY_LEDGER_MISMATCH')
   require(out.get('font_provenance',{}).get(BRAND['heading']),'FONT_PROVENANCE_REQUIRED')
   
   if plan['artifact'].get('logo_asset'):
    require(out.get('logo_asset')==APPROVED_LOGO and out.get('logo_sha256')==filehash(Path(__file__).resolve().parent.parent/APPROVED_LOGO),'ORIGINAL_LOGO_PROVENANCE_REQUIRED')
   else:
    require(not out.get('logo_asset') and not out.get('logo_sha256'),'UNPLANNED_LOGO_FORBIDDEN')
   require(out.get('copy_rendered') is True,'COPY_RENDER_NOT_CONFIRMED')
  if s=='TECH_REVIEW':
   p=self.records['IMAGE_BUILD']['artifact']['image_path']
   with Image.open(p) as im:require(im.format=='PNG' and im.size==(1080,1350) and im.mode in ('RGB','RGBA'),'TECH_PNG_INVALID')
  if s in ('VISUAL_REVIEW','CONTENT_IMAGE_REVIEW','BRAND_REVIEW','FINAL_REVIEW'):
   build=self.records['IMAGE_BUILD']['artifact'];require(out.get('image_sha256')==build['image_sha256'],'REVIEW_IMAGE_MISMATCH')
   require(out.get('plan_hash')==self.records['IMAGE_PLAN']['hash'],'REVIEW_PLAN_MISMATCH')
  if s=='VISUAL_REVIEW':require(out.get('pixel_inspection') is True and out.get('mobile_inspection') is True,'PIXEL_INSPECTION_REQUIRED')
  if s=='CONTENT_IMAGE_REVIEW':require(out.get('topic_match') is True and out.get('text_match') is True,'CONTENT_IMAGE_MISMATCH')
  if s=='BRAND_REVIEW':require(out.get('font_files_checked') is True and out.get('palette_checked') is True and out.get('footer_checked') is True and (out.get('original_logo_checked') is True if self.records['IMAGE_PLAN']['artifact'].get('logo_asset') else out.get('logo_absence_checked') is True) and out.get('positioning_checked') is True,'BRAND_VISUAL_CHECK_MISSING')
  if s=='DELIVERY':require(out.get('image_sha256')==self.records['IMAGE_BUILD']['artifact']['image_sha256'] and all(x in self.records for x in STAGES[:-1]),'DELIVERY_NOT_VERIFIED')
 def run(self):
  i=0
  while i<len(STAGES):
   s=STAGES[i];a=self.adapters.get(s)
   if not isinstance(a,Adapter) or not callable(a.fn):
    self.status='BLOCKED';self.trace.append({'stage':s,'event':'BLOCKED','reason':'ADAPTER_MISSING'});break
   try:
    out=a.fn(self.job,self.records)
    self.verify(s,out,a)
    self.records[s]={'artifact':out,'hash':digest(out),'adapter':a.name}
    self.trace.append({'stage':s,'event':'PASS','artifact_sha256':digest(out)});i+=1
   except Exception as e:
    # D-23: a repair_at naming a stage AFTER the current stage is silently
    # ignored by the old code; record it in the trace, then fall back to the
    # REPAIR map exactly as before.
    if isinstance(e,GateFailure) and e.repair_at in STAGES and STAGES.index(e.repair_at)>i:
     self.trace.append({'stage':s,'event':'REPAIR_AT_IGNORED','reason':'REPAIR_AT_FORWARD'})
    target=e.repair_at if isinstance(e,GateFailure) and e.repair_at in STAGES and STAGES.index(e.repair_at)<=i else REPAIR[s]
    self.revisions+=1;self.trace.append({'stage':s,'event':'FAIL','reason':str(e),'return_to':target,'revision':self.revisions})
    if self.revisions>self.limit:self.status='BLOCKED';break
    for k in STAGES[STAGES.index(target):]:self.records.pop(k,None)
    i=STAGES.index(target)
  else:self.status='TEST_FIXTURE_PASS' if self.job.get('mode')=='TEST_FIXTURE' else 'READY_FOR_OWNER_REVIEW'
  return {'status':self.status,'content_id':self.job['content_id'],'repairs':self.revisions,'trace':self.trace,'external_writes':0,'completed_stages':list(self.records)}
