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
 return json.loads((Path(__file__).resolve().parent.parent/'references'/'production-policy-v33.json').read_text(encoding='utf-8'))
POLICY=_policy()
BRAND=POLICY['brand']
APPROVED_LOGO=POLICY['brand_assets']['approved_logo_path']

class GateFailure(Exception):
 def __init__(self,code,repair_at=None):super().__init__(code);self.repair_at=repair_at

def digest(o):return sha256(json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def filehash(p):return sha256(Path(p).read_bytes()).hexdigest()
def require(ok,code):
 if not ok:raise GateFailure(code)
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
   if s in REVIEWS:require(out.get('inspection_evidence_path') and Path(out['inspection_evidence_path']).is_file() and out.get('inspection_evidence_sha256')==filehash(out['inspection_evidence_path']),'INDEPENDENT_INSPECTION_EVIDENCE_REQUIRED')
   if s=='SOURCES':require(all(x.get('verified_at')!='fixture-only' and x.get('source_sha256') for x in out['sources']),'LIVE_SOURCE_PROVENANCE_REQUIRED')
   if s=='IMAGE_BUILD':
    for family in (BRAND['heading'],):
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
    target=e.repair_at if isinstance(e,GateFailure) and e.repair_at in STAGES and STAGES.index(e.repair_at)<=i else REPAIR[s]
    self.revisions+=1;self.trace.append({'stage':s,'event':'FAIL','reason':str(e),'return_to':target,'revision':self.revisions})
    if self.revisions>self.limit:self.status='BLOCKED';break
    for k in STAGES[STAGES.index(target):]:self.records.pop(k,None)
    i=STAGES.index(target)
  else:self.status='TEST_FIXTURE_PASS' if self.job.get('mode')=='TEST_FIXTURE' else 'READY_FOR_OWNER_REVIEW'
  return {'status':self.status,'content_id':self.job['content_id'],'repairs':self.revisions,'trace':self.trace,'external_writes':0,'completed_stages':list(self.records)}
