"""Fail-closed, single-item content-to-poster controller. No external writes.

Persist state to JSON using atomic replace. Stage evidence must be committed through
this controller; claims of real external research or visual inspection are not inferred.
"""
import argparse, hashlib, json, os, tempfile
from pathlib import Path

STAGES=('SOURCES','RESEARCH','STRATEGY','CONTENT','CONTENT_QA','BRIEF','BRIEF_QA','RENDER','TECH_QA','VISUAL_QA','CONTENT_MATCH_QA','BRAND_QA','DELIVERY')
REVIEW_STAGES={'CONTENT_QA','BRIEF_QA','VISUAL_QA','CONTENT_MATCH_QA','BRAND_QA'}
REPAIR_TARGET={'SOURCES':'SOURCES','RESEARCH':'RESEARCH','STRATEGY':'STRATEGY','CONTENT':'CONTENT','CONTENT_QA':'CONTENT','BRIEF':'BRIEF','BRIEF_QA':'BRIEF','RENDER':'RENDER','TECH_QA':'RENDER','VISUAL_QA':'RENDER','CONTENT_MATCH_QA':'BRIEF','BRAND_QA':'BRIEF','DELIVERY':'DELIVERY'}
MAX_REVISIONS=3
class GateError(ValueError):pass

def canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(data):return hashlib.sha256(canonical(data)).hexdigest()
def initial(content_id,topic):
 if not content_id or not topic:raise GateError('CONTENT_ID_AND_TOPIC_REQUIRED')
 return {'schema':'erudience.controller.v3.9','content_id':content_id,'topic':topic,'stage':STAGES[0], 'status':'ACTIVE','revision_count':0,'records':{},'history':[],'external_writes':0}
def _index(stage):
 if stage not in STAGES:raise GateError('UNKNOWN_STAGE')
 return STAGES.index(stage)
def commit(state,stage,artifact,*,reviewer=None,producer=None,source_verified=False):
 if state['status']!='ACTIVE' or state['stage']!=stage:raise GateError('OUT_OF_ORDER_OR_BLOCKED')
 if not isinstance(artifact,dict) or not artifact:raise GateError('ARTIFACT_REQUIRED')
 if stage in REVIEW_STAGES and (not reviewer or reviewer==producer):raise GateError('INDEPENDENT_REVIEW_REQUIRED')
 if stage in ('SOURCES','RESEARCH') and not source_verified:raise GateError('SOURCE_EVIDENCE_REQUIRED')
 if stage=='CONTENT' and (not artifact.get('caption') or not artifact.get('topic')):raise GateError('CONTENT_FIELDS_REQUIRED')
 if stage=='CONTENT' and artifact['topic']!=state['topic']:raise GateError('TOPIC_MISMATCH')
 if stage=='BRIEF':
  content=state['records'].get('CONTENT',{}).get('artifact',{})
  if artifact.get('topic')!=state['topic'] or artifact.get('caption_sha256')!=digest(content):raise GateError('BRIEF_CONTENT_BINDING_FAILED')
  if not artifact.get('poster_text') or not artifact.get('brand_profile_version'):raise GateError('BRIEF_FIELDS_REQUIRED')
 if stage=='RENDER':
  brief=state['records'].get('BRIEF',{}).get('artifact',{})
  if artifact.get('brief_sha256')!=digest(brief):raise GateError('RENDER_BRIEF_BINDING_FAILED')
  if not artifact.get('image_sha256') or not artifact.get('image_path'):raise GateError('IMAGE_ARTIFACT_REQUIRED')
 if stage=='TECH_QA':
  render=state['records']['RENDER']['artifact']
  p=Path(render['image_path'])
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=render['image_sha256']:raise GateError('IMAGE_BYTES_MISMATCH')
  from PIL import Image
  with Image.open(p) as im:
   if im.format!='PNG' or im.size!=(1080,1350):raise GateError('IMAGE_TECHNICAL_MISMATCH')
 if stage in ('VISUAL_QA','CONTENT_MATCH_QA','BRAND_QA'):
  if artifact.get('decision')!='PASS' or not artifact.get('observations'):raise GateError('REVIEW_EVIDENCE_REQUIRED')
  render=state['records']['RENDER']['artifact'];brief=state['records']['BRIEF']['artifact']
  if artifact.get('image_sha256')!=render['image_sha256'] or artifact.get('brief_sha256')!=digest(brief):raise GateError('REVIEW_WRONG_ARTIFACT')
  if stage=='CONTENT_MATCH_QA' and artifact.get('topic_verified') is not True:raise GateError('POSTER_TOPIC_NOT_VERIFIED')
  if stage=='BRAND_QA' and artifact.get('website_brand_verified') is not True:raise GateError('BRAND_NOT_VERIFIED')
 if stage=='DELIVERY':
  if not all(s in state['records'] for s in STAGES[:-1]):raise GateError('UNVERIFIED_DELIVERY')
  if artifact.get('image_sha256')!=state['records']['RENDER']['artifact']['image_sha256']:raise GateError('DELIVERY_IMAGE_MISMATCH')
 rec={'artifact':artifact,'artifact_sha256':digest(artifact),'producer':producer,'reviewer':reviewer,'source_verified':source_verified}
 state['records'][stage]=rec;state['history'].append({'event':'PASS','stage':stage,'sha256':rec['artifact_sha256']})
 idx=_index(stage)
 if idx==len(STAGES)-1:state['status']='READY_FOR_OWNER_REVIEW';state['stage']=None
 else:state['stage']=STAGES[idx+1]
 return state

def fail(state,stage,reason):
 if state['status']!='ACTIVE' or state['stage']!=stage:raise GateError('OUT_OF_ORDER_OR_BLOCKED')
 if not reason:raise GateError('FAIL_REASON_REQUIRED')
 target=REPAIR_TARGET[stage];state['revision_count']+=1
 state['history'].append({'event':'FAIL','stage':stage,'reason':reason,'return_to':target,'revision':state['revision_count']})
 for s in STAGES[_index(target):]:state['records'].pop(s,None)
 if state['revision_count']>MAX_REVISIONS:state['status']='BLOCKED';state['stage']=None
 else:state['stage']=target
 return state

def save(path,state):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.erudience-',suffix='.tmp')
 try:
  with os.fdopen(fd,'w') as f:json.dump(state,f,indent=2,ensure_ascii=False);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['init','status','pass','fail']);ap.add_argument('--state',required=True);ap.add_argument('--content-id');ap.add_argument('--topic');ap.add_argument('--stage');ap.add_argument('--artifact');ap.add_argument('--reviewer');ap.add_argument('--producer');ap.add_argument('--source-verified',action='store_true');ap.add_argument('--reason');args=ap.parse_args()
 if args.action=='init':state=initial(args.content_id,args.topic)
 else:state=json.loads(Path(args.state).read_text())
 if args.action=='pass':state=commit(state,args.stage,json.loads(Path(args.artifact).read_text()),reviewer=args.reviewer,producer=args.producer,source_verified=args.source_verified)
 elif args.action=='fail':state=fail(state,args.stage,args.reason)
 if args.action!='status':save(args.state,state)
 print(json.dumps({'status':state['status'],'next_stage':state['stage'],'revisions':state['revision_count'],'history':state['history'][-1:]},indent=2))
if __name__=='__main__':main()
