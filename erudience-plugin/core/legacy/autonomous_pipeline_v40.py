"""Erudience deterministic local execution coordinator. No publishing or network writes.

This module invokes supplied stage adapters, verifies immutable lineage and provides
bounded repair routing. It does NOT claim an LLM/human reviewer was run unless a
caller supplies a real adapter; local independent validators are rule-based.
"""
from __future__ import annotations
import hashlib,json,os,re
from pathlib import Path
from dataclasses import dataclass

STAGES=('SOURCES','RESEARCH','STRATEGY','CONTENT','CONTENT_QA','BRIEF','BRIEF_QA','RENDER','TECH_QA','VISUAL_QA','CONTENT_MATCH_QA','BRAND_QA','DELIVERY')
REPAIR={'SOURCES':'SOURCES','RESEARCH':'RESEARCH','STRATEGY':'STRATEGY','CONTENT':'CONTENT','CONTENT_QA':'CONTENT','BRIEF':'BRIEF','BRIEF_QA':'BRIEF','RENDER':'RENDER','TECH_QA':'RENDER','VISUAL_QA':'RENDER','CONTENT_MATCH_QA':'BRIEF','BRAND_QA':'BRIEF','DELIVERY':'DELIVERY'}
REVIEWS={'CONTENT_QA','BRIEF_QA','VISUAL_QA','CONTENT_MATCH_QA','BRAND_QA'}
PALETTE={'paper':'#F6F1E9','ink':'#14120E','soft':'#615B4C','emerald':'#10B981','deep':'#0A6E3E','dark':'#0A100E'}
class PipelineError(RuntimeError):pass
class StageFailure(PipelineError):
 def __init__(self,reason,repair_at=None):super().__init__(reason);self.repair_at=repair_at

def hashobj(o):return hashlib.sha256(json.dumps(o,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def norm(s):return re.sub(r'\W+',' ',str(s).lower()).strip()
def assert_true(cond,reason):
 if not cond:raise StageFailure(reason)

@dataclass
class Adapter:
 name:str
 func:object
 role:str='producer'

class Controller:
 def __init__(self,job,adapters,max_repairs=3):
  assert_true(isinstance(job,dict) and job.get('content_id') and job.get('topic'),'JOB_FIELDS_REQUIRED')
  assert_true(max_repairs>=0,'INVALID_REPAIR_LIMIT')
  self.job=dict(job);self.adapters=adapters;self.max_repairs=max_repairs
  self.records={};self.history=[];self.repairs=0;self.status='ACTIVE'
  self.job_hash=hashobj(self.job)
 def _check(self,stage,value,producer):
  assert_true(isinstance(value,dict) and value,'EMPTY_ARTIFACT')
  if stage in REVIEWS:
   reviewer=value.get('reviewer_id');assert_true(reviewer and reviewer!=producer,'INDEPENDENT_REVIEW_REQUIRED')
   assert_true(value.get('decision')=='PASS' and value.get('observations'),'REVIEW_NOT_PASSED')
   assert_true(value.get('subject_sha256')==self.records[STAGES[STAGES.index(stage)-1]]['hash'],'REVIEW_SUBJECT_MISMATCH')
  if stage=='SOURCES':assert_true(value.get('verified_sources') and isinstance(value['verified_sources'],list),'VERIFIED_SOURCES_REQUIRED')
  if stage=='RESEARCH':assert_true(value.get('evidence') and value.get('source_sha256')==self.records['SOURCES']['hash'],'RESEARCH_EVIDENCE_MISSING')
  if stage=='STRATEGY':assert_true(value.get('topic')==self.job['topic'] and value.get('research_sha256')==self.records['RESEARCH']['hash'],'STRATEGY_TOPIC_OR_SOURCE_MISMATCH')
  if stage=='CONTENT':
   assert_true(value.get('topic')==self.job['topic'] and value.get('strategy_sha256')==self.records['STRATEGY']['hash'],'CONTENT_TOPIC_OR_STRATEGY_MISMATCH')
   assert_true(value.get('caption') and value.get('keywords'),'CONTENT_REQUIRED')
  if stage=='BRIEF':
   assert_true(value.get('topic')==self.job['topic'] and value.get('content_sha256')==self.records['CONTENT']['hash'],'BRIEF_CONTENT_BINDING_FAILED')
   assert_true(value.get('poster_text') and value.get('brand_profile')=='website-v38','BRIEF_OR_BRAND_MISSING')
   assert_true(value.get('heading_font')=='Inter' and value.get('body_font')=='DM Sans' and value.get('palette')==PALETTE,'BRAND_SPEC_MISMATCH')
   assert_true(value.get('footer')=='erudience.com' and value.get('brand_name')=='Erudience','BRAND_IDENTITY_MISSING')
   assert_true(norm(value['poster_text'].get('headline','')) and norm(value['poster_text'].get('headline','')) in norm(value.get('approved_headline',value['poster_text'].get('headline',''))),'POSTER_HEADLINE_MISMATCH')
  if stage=='RENDER':
   assert_true(value.get('brief_sha256')==self.records['BRIEF']['hash'],'RENDER_BRIEF_BINDING_FAILED')
   p=value.get('image_path');assert_true(p and Path(p).is_file() and sha(p)==value.get('image_sha256'),'RENDER_IMAGE_BYTES_INVALID')
   assert_true(value.get('rendered_text_sha256')==hashobj(self.records['BRIEF']['artifact']['poster_text']),'RENDER_COPY_LEDGER_MISMATCH')
  if stage=='TECH_QA':
   from PIL import Image
   p=self.records['RENDER']['artifact']['image_path']
   with Image.open(p) as im:assert_true(im.format=='PNG' and im.size==(1080,1350) and im.mode in ('RGB','RGBA'),'PNG_TECHNICAL_INVALID')
   assert_true(value.get('image_sha256')==sha(p),'TECH_IMAGE_MISMATCH')
  if stage in ('VISUAL_QA','CONTENT_MATCH_QA','BRAND_QA'):
   assert_true(value.get('image_sha256')==self.records['RENDER']['artifact']['image_sha256'],'QA_IMAGE_MISMATCH')
   assert_true(value.get('brief_sha256')==self.records['BRIEF']['hash'],'QA_BRIEF_MISMATCH')
  if stage=='CONTENT_MATCH_QA':
   assert_true(value.get('topic_verified') is True and value.get('copy_ledger_verified') is True,'POSTER_CAPTION_MISMATCH')
  if stage=='BRAND_QA':assert_true(value.get('website_brand_verified') is True,'BRAND_QA_FAILED')
  if stage=='DELIVERY':
   assert_true(value.get('image_sha256')==self.records['RENDER']['artifact']['image_sha256'],'DELIVERY_IMAGE_MISMATCH')
   assert_true(all(s in self.records for s in STAGES[:-1]),'DELIVERY_GATES_MISSING')
 def run(self):
  i=0
  while i<len(STAGES):
   stage=STAGES[i];entry=self.adapters.get(stage)
   if not isinstance(entry,Adapter) or not callable(entry.func):
    self.status='BLOCKED';self.history.append({'stage':stage,'status':'BLOCKED','reason':'EXECUTABLE_ADAPTER_MISSING'});break
   try:
    prior=self.records.get(STAGES[i-1]) if i else None
    value=entry.func(self.job,self.records,prior)
    self._check(stage,value,entry.name)
    self.records[stage]={'artifact':value,'hash':hashobj(value),'adapter':entry.name,'role':entry.role,'job_sha256':self.job_hash}
    self.history.append({'stage':stage,'status':'PASS','artifact_sha256':self.records[stage]['hash']});i+=1
   except Exception as exc:
    reason=str(exc)
    target=exc.repair_at if isinstance(exc,StageFailure) and exc.repair_at else REPAIR[stage]
    if target not in STAGES or STAGES.index(target)>i:target=REPAIR[stage]
    self.repairs+=1
    self.history.append({'stage':stage,'status':'FAIL','reason':reason,'return_to':target,'attempt':self.repairs})
    if self.repairs>self.max_repairs:
     self.status='BLOCKED';break
    j=STAGES.index(target)
    for s in STAGES[j:]:self.records.pop(s,None)
    i=j
  else:self.status='TEST_FIXTURE_PASS' if self.job.get('mode')=='TEST_FIXTURE' else 'READY_FOR_OWNER_REVIEW'
  return {'status':self.status,'job_sha256':self.job_hash,'content_id':self.job['content_id'],'repairs':self.repairs,'history':self.history,'records':self.records,'external_writes':0}

# These validators are independent code paths, not human or model reviewer attestations.
def deterministic_content_match(job,records,prior):
 brief=records['BRIEF']['artifact'];render=records['RENDER']['artifact'];caption=records['CONTENT']['artifact']['caption']
 headline=brief['poster_text']['headline'];topic=brief['topic']
 assert_true(norm(topic)==norm(job['topic']),'TOPIC_MISMATCH')
 assert_true(all(w in norm(caption) for w in norm(topic).split() if len(w)>3),'CAPTION_TOPIC_MISMATCH')
 assert_true(render['rendered_text_sha256']==hashobj(brief['poster_text']),'RENDERED_COPY_MISMATCH')
 return {'decision':'PASS','reviewer_id':'deterministic-content-matcher-v40','observations':'Topic, caption and rendered text ledger matched','subject_sha256':prior['hash'],'image_sha256':render['image_sha256'],'brief_sha256':records['BRIEF']['hash'],'topic_verified':True,'copy_ledger_verified':True}

def deterministic_brand_check(job,records,prior):
 brief=records['BRIEF']['artifact'];render=records['RENDER']['artifact']
 assert_true(brief['palette']==PALETTE and brief['heading_font']=='Inter' and brief['body_font']=='DM Sans','BRAND_TOKENS_MISMATCH')
 assert_true(brief['brand_name']=='Erudience' and brief['footer']=='erudience.com','BRAND_IDENTITY_MISSING')
 assert_true(render.get('font_provenance_verified') is True,'RENDER_FONT_NOT_VERIFIED')
 return {'decision':'PASS','reviewer_id':'deterministic-brand-validator-v40','observations':'Verified website brand tokens and font provenance metadata; visual human inspection is separate','subject_sha256':prior['hash'],'image_sha256':render['image_sha256'],'brief_sha256':records['BRIEF']['hash'],'website_brand_verified':True}
